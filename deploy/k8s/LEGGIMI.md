# Deploy su k3s (tadamoo.com)

`tarots.yaml` mette TAROTS chat nel namespace `tarots` del cluster k3s di
tadamoo.com, sotto **un solo dominio**, `tarots.chat`:

| percorso | servizio | note |
|---|---|---|
| `/` | `tarots-web` | sito Next.js |
| `/api/` | `tarots-api` | FastAPI; il prefisso `/api` si toglie nel gateway |
| `/admin` | `tarots-admin` | console di amministrazione, Next.js costruito con `basePath=/admin`; ci entra solo chi ha il ruolo `admin` |
| `/auth/` | `tarots-keycloak` | Keycloak 26, `KC_HTTP_RELATIVE_PATH=/auth`; console e realm master bloccati (403) |

Un piccolo nginx (`tarots-gateway`, porta 8080) smista i percorsi. Davanti sta
nginx-proxy-manager, che inoltra tutto l'host a `tarots-gateway` (ClusterIP,
porta 8080) e fa TLS con Let's Encrypt. Il database è quello già in cluster
(`postgresql.tadamoo`): ruolo e database `tarots`; Keycloak ha lo schema
`keycloak` dentro lo stesso database.

## Prima volta

```bash
# 1. database (come postgres, nel pod)
kubectl -n tadamoo exec -i deploy/postgresql -- psql -U postgres <<'SQL'
CREATE ROLE tarots LOGIN PASSWORD '<password>';
CREATE DATABASE tarots OWNER tarots;
REVOKE ALL ON DATABASE tarots FROM PUBLIC;
\c tarots
CREATE SCHEMA keycloak AUTHORIZATION tarots;
SQL

# 2. immagini: si costruiscono IN LOCALE con Docker Desktop (mai `docker build` sul server: è carico e condiviso con
#    la produzione) e si importano in containerd, niente registry:
#      docker save tarots-api:vX | ssh root@tadamoo.com "k3s ctr -n k8s.io images import -"
docker build --provenance=false -f deploy/Dockerfile.backend -t tarots-api:v3 .
docker build --provenance=false -f deploy/Dockerfile.next --build-arg APP=frontend \
  --build-arg NEXT_PUBLIC_API_URL=https://tarots.chat/api \
  --build-arg NEXT_PUBLIC_KEYCLOAK_URL=https://tarots.chat/auth \
  --build-arg NEXT_PUBLIC_KEYCLOAK_REALM=tarots \
  --build-arg NEXT_PUBLIC_KEYCLOAK_CLIENT_ID=tarot-frontend \
  --build-arg NEXT_PUBLIC_AUTH_DISABLED=false \
  --build-arg NEXT_PUBLIC_SITE_URL=https://tarots.chat \
  --build-arg NEXT_PUBLIC_CARD_EXT=webp -t tarots-web:v3 .
docker build --provenance=false -f deploy/Dockerfile.next --build-arg APP=admin \
  --build-arg NEXT_PUBLIC_API_URL=https://tarots.chat/api \
  --build-arg NEXT_PUBLIC_KEYCLOAK_URL=https://tarots.chat/auth \
  --build-arg NEXT_PUBLIC_KEYCLOAK_REALM=tarots \
  --build-arg NEXT_PUBLIC_KEYCLOAK_CLIENT_ID=tarot-admin \
  --build-arg NEXT_PUBLIC_AUTH_DISABLED=false \
  --build-arg NEXT_PUBLIC_BASE_PATH=/admin -t tarots-admin:v3 .
docker build -f deploy/keycloak/Dockerfile -t tarots-keycloak:v1 deploy/keycloak
docker save tarots-api:v3 | k3s ctr -n k8s.io images import -   # e così le altre

# 3. segreti e realm (non stanno nel repository)
kubectl create ns tarots
kubectl -n tarots create secret generic tarots-secrets \
  --from-literal=db-password=... \
  --from-literal=database-url='postgresql+psycopg://tarots:...@postgresql.tadamoo.svc.cluster.local:5432/tarots' \
  --from-literal=keycloak-admin-password=... \
  --from-literal=api-client-secret=... \
  --from-literal=llm-provider-key="$(python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"
# v9, Fase 2c: sul server restano SOLO questi tre segreti — la password del database (`db-password`/`database-url`),
# la chiave master di cifratura (`llm-provider-key`) e il segreto del client API↔Keycloak (`api-client-secret`), più
# la password dell'admin di Keycloak. Tutto il resto si imposta dalla console (Stripe, posta, NAS, titolare…).
# `condivisione-sale` e `ip-hash-secret` non servono più: senza, al primo avvio l'API ne genera di casuali e li
# conserva cifrati nel database (tabella `segreti_sistema`). Se il Secret li ha già (installazioni di prima della
# Fase 2c), valgono quelli e si copiano nel database: si possono lasciare, e toglierli dopo non cambia le impronte.
# La migrazione GDPR a1c3e5f7b9d2 senza `ip-hash-secret` usa un segreto casuale che la migrazione a7c9e1b3d5f8 salva
# (stesso `alembic upgrade head`): le impronte degli IP già salvati restano confrontabili con le nuove.
# Il CronJob `tarots-cancellazioni` (ogni notte alle 3:15) esegue le cancellazioni degli account chieste da più di 30
# giorni: usa `api-client-secret` (l'account di servizio di `tarot-api` deve avere `manage-users`). Prova a mano:
#   kubectl -n tarots create job --from=cronjob/tarots-cancellazioni prova-cancellazioni
# `llm-provider-key` è la chiave master: cifra a riposo tutti i segreti salvati dalla console (fornitori LLM, Stripe,
# posta, NAS, Google, Reddit, store, segreti interni): senza, l'API non parte in produzione (vedi
# `Settings.validate_production`). **Cambiarla dopo li rende illeggibili** (tornano «non impostati» e vanno
# reinseriti in console): si genera una volta sola, all'inizio.
kubectl -n tarots create configmap tarots-realm --from-file=realm.json=deploy/keycloak/realm-tarots.prod.json

# 4. tutto il resto
kubectl apply -f deploy/k8s/tarots.yaml

# 5. il seed: piani e utenti di prova, con TAROT_CREDITI_UTENTE_DI_PROVA crediti a testa
kubectl -n tarots exec deploy/tarots-api -- python -m tarot_core.tools.seed
# In un'installazione che ha già utenti veri, sempre senza gli utenti di prova (aggiunge solo piani e sezioni del blog
# che mancano, senza toccare quelli che ci sono):
#   kubectl -n tarots exec deploy/tarots-api -- python -m tarot_core.tools.seed --senza-utenti
```

## Il dominio `tarots.chat`

Il sito vive su **`tarots.chat`** (l'inglese alla radice, l'italiano sotto `/it`). `www.tarots.chat` e il vecchio
`tarots.tadamoo.com` non servono contenuti: reindirizzano con un **301** allo stesso percorso su `https://tarots.chat`.
Il cambio si fa in quest'ordine, e **solo dopo che il DNS risponde** (senza, Let's Encrypt non emette il certificato):

1. **DNS** (dal registrar del dominio): un record `A` per `@` (`tarots.chat`) e uno per `www`, entrambi verso l'IP del
   server (lo stesso di `tarots.tadamoo.com`). Verifica: `nslookup tarots.chat 8.8.8.8`.
2. **NPM**: il proxy host di `tarots.chat` verso `tarots-gateway` con un certificato Let's Encrypt che copre **anche**
   `www.tarots.chat` (passo sopra), Force SSL e HTTP/2. Poi un host di **reindirizzamento** (`POST /nginx/redirection-hosts`,
   `forward_http_code: 301`, `forward_scheme: https`, `forward_domain_name: tarots.chat`, `preserve_path: true`) per
   `www.tarots.chat`, e — solo a cose fatte — lo stesso per `tarots.tadamoo.com` (con il suo certificato già emesso, o
   `ssl_forced: false`). Il vecchio proxy host verso il gateway si sostituisce con il reindirizzamento: non restano due siti.
3. **Immagini**: l'indirizzo è cotto nella build (`NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_KEYCLOAK_URL`,
   `NEXT_PUBLIC_SITE_URL`), quindi `tarots-web` e `tarots-admin` **si ricostruiscono in locale** (Docker Desktop, mai sul server) con i
   `--build-arg` di sopra e un tag nuovo (`v3`), e si importano in containerd, una alla volta. Anche `tarots-api` (nuovo
   codice: SEO, REST del blog, immagini con Pillow) e il tema di Keycloak se cambia.
4. **Realm Keycloak esistente** (l'import parte solo a realm assente, quindi il file non basta): sui due client
   `tarot-frontend` e `tarot-admin` gli indirizzi diventano quelli nuovi. Dal pod di Keycloak:

   ```bash
   KCADM=/opt/keycloak/bin/kcadm.sh
   kubectl -n tarots exec deploy/tarots-keycloak -- $KCADM config credentials --server http://localhost:8080/auth --realm master --user admin
   # per ciascun client (id da: get clients -r tarots -q clientId=<client> --fields id)
   kubectl -n tarots exec deploy/tarots-keycloak -- $KCADM update clients/<id-frontend> -r tarots \
     -s 'redirectUris=["https://tarots.chat/*"]' -s 'webOrigins=["+"]' -s rootUrl=https://tarots.chat
   kubectl -n tarots exec deploy/tarots-keycloak -- $KCADM update clients/<id-admin> -r tarots \
     -s 'redirectUris=["https://tarots.chat/admin/*"]' -s 'webOrigins=["+"]' -s rootUrl=https://tarots.chat/admin
   ```

   Mittente e nome delle email (`smtpServer.from`, `fromDisplayName`) si scrivono all'import del realm: in un realm già
   esistente si aggiornano dalla console (Realm settings → Email) con `noreply@tarots.chat` e «TAROTS chat».
   Attenzione: nel realm di produzione `smtpServer` è **vuoto** (nessun server di posta configurato), quindi recupero
   password e verifica dell'email non partono finché non si imposta un SMTP.
   In uno script passato a `ssh … bash -s` non usare `kubectl exec -i`: si mangia il resto dello script.
5. **Manifest**: `kubectl apply -f deploy/k8s/tarots.yaml` (tag nuovi, `KC_HOSTNAME`, `TAROT_KEYCLOAK_ISSUER_URL`,
   `TAROT_API_PUBLIC_URL`, `TAROT_WEB_PUBLIC_URL`, `TAROT_CORS_ORIGINS`). L'emittente dei token cambia con il dominio: chi
   era connesso deve accedere di nuovo. Il pod dell'API applica le migrazioni (`a41c7e92d3b6`, campi SEO e chiavi).
6. **Prova**: `curl -sI https://tarots.chat/` (200), `https://www.tarots.chat/` e `https://tarots.tadamoo.com/cards`
   (301 verso `https://tarots.chat/cards`), il login dal sito e dalla console, `https://tarots.chat/sitemap.xml`,
   `https://tarots.chat/robots.txt`, `https://tarots.chat/it`.
7. **Dopo il lancio**: registrare il sito in Google Search Console e Bing Webmaster Tools (proprietà di dominio,
   verifica DNS), inviare `https://tarots.chat/sitemap.xml`, e controllare dopo qualche giorno copertura, `hreflang` e
   dati strutturati. Prima del rilascio, `NEXT_PUBLIC_SITE_URL` deve essere `https://tarots.chat` (è nel `Dockerfile.next`):
   canonical, sitemap e Open Graph si scrivono con quello.

**Ritorno indietro**: finché `tarots.tadamoo.com` non è diventato un reindirizzamento si può riportare
`KC_HOSTNAME` e le altre variabili al vecchio indirizzo e ricostruire; dopo, i motori di ricerca hanno già letto i 301.

## Il modello (LLM)

**Senza un modello configurato il servizio non funziona, per scelta.** Le
domande dell'intervista, le letture per posizione e il responso li scrive un
modello; non esistono domande né testi di ripiego. Finché manca, `POST /readings`
risponde `503 modello_non_configurato` e **non addebita nulla**, e la console
mostra un avviso nella pagina Modelli. Il modello finto (`TAROT_LLM_FINTO`) è
solo per sviluppo e test: con `TAROT_ENVIRONMENT=prod` l'API rifiuta di partire
se è attivo.

Il modello si configura nel Secret facoltativo `tarots-llm`, le cui chiavi sono
variabili `TAROT_*`; poi si riavvia l'API:

```bash
kubectl -n tarots create secret generic tarots-llm \
  --from-literal=TAROT_LLM_PROVIDER=anthropic \
  --from-literal=TAROT_ANTHROPIC_API_KEY=... \
  --from-literal=TAROT_ANTHROPIC_MODEL=claude-sonnet-5
kubectl -n tarots rollout restart deploy/tarots-api
```

Per più modelli (uno per compito) si usa invece `TAROT_MODELLI`, un JSON:
`[{"nome":"veloce","provider":"anthropic","model":"claude-haiku-4-5-20251001","api_key":"..."},{"nome":"migliore","provider":"anthropic","model":"claude-sonnet-5","api_key":"..."}]`.
Gli indirizzi e le chiavi restano nel Secret e **non si modificano dalla
console**: un endpoint modificabile dall'interfaccia è traffico dirottabile con
le chiavi appresso. La console (Modelli) sceglie, fra i modelli configurati, chi
serve intervista, validazione, interpretazione, sintesi e giudizio.

## Console di amministrazione

`https://tarots.chat/admin`, con il login Keycloak del client
`tarot-admin` (PKCE). Il collegamento «Admin» compare nella testata del sito
solo a chi ha il ruolo `admin`. Nel realm il client deve avere il redirect
`https://tarots.chat/admin/*` e `webOrigins` `["+"]` (o l'origine
`https://tarots.chat`): un `webOrigins` con il percorso `/admin` non è
un'origine e il CORS del login fallisce. Il generatore del realm ora scrive `+`.

## Instradamento (nginx-proxy-manager)

Serve un proxy host per `tarots.chat` verso il ClusterIP di
`tarots-gateway` (`kubectl -n tarots get svc tarots-gateway`), porta 8080, con
certificato Let's Encrypt e Force SSL. Dall'API di NPM (2.15, sul server:
`http://127.0.0.1:81/api`, login con `POST /tokens`):

1. `POST /nginx/certificates` con `{"provider":"letsencrypt","domain_names":["tarots.chat","www.tarots.chat"],"meta":{"dns_challenge":false}}`
   (in 2.15 l'email non sta nel payload: la prende dall'utente loggato).
2. `POST /nginx/proxy-hosts` con `forward_scheme: http`, `forward_host: <ClusterIP>`,
   `forward_port: 8080`, `certificate_id`, `ssl_forced`, `http2_support`,
   `allow_websocket_upgrade` e in `advanced_config`:

   ```
   proxy_buffering off;
   proxy_read_timeout 300s;
   proxy_send_timeout 300s;
   proxy_buffer_size 128k;
   proxy_buffers 4 256k;
   proxy_busy_buffers_size 256k;
   ```

   `proxy_buffering off` serve allo streaming del responso; i buffer grandi, alle
   intestazioni dei token di Keycloak. Il ClusterIP cambia se il servizio si ricrea.

Nel deploy su tadamoo i due utenti di prova hanno **username `test` e `admin`** con
password uguale al nome (email `test@tarots.local` / `admin@tarots.local`, che
funzionano ancora come login). Sono password volutamente deboli, uguali al nome,
fuori dalla policy del realm (`notUsername`): la policy vale solo quando si
imposta una password, quindi fu sospesa il tempo del cambio (`PUT
/admin/realms/tarots` con `passwordPolicy`). La lunghezza minima delle password
nel realm è **6 caratteri** (`length(6)`, deciso per questo deploy: non serve la
severità dei 12), con `notUsername`, `notEmail` e `passwordHistory(3)`. Nel realm
`registrationEmailAsUsername` è `false` (con `true` l'username torna l'email al
primo aggiornamento del profilo) e `editUsernameAllowed` è stato acceso solo per
rinominarli. L'amministratore ha l'OTP obbligatorio: chi accede per primo lo
configura.

Altri account creati a mano: `andrea` (ruolo `admin`), `martina`, `melanie` e
`adrienn`, ciascuno con 1.000.000 di crediti. In Keycloak con `POST
/admin/realms/tarots/users`; nel database con `python -m tarot_core.tools.utenti -`
(stdin: `[{"sub": "<id Keycloak>", "email": "...", "nome": "...", "crediti": 1000000}]`),
che crea la riga con quel `sub` e i crediti, senza raddoppiarli se rilanciato.

Gli **utenti di prova** vanno creati anche in Keycloak, con lo stesso `id` che
il seed usa come `sub` (`11111111-1111-4111-8111-111111111111` e
`22222222-2222-4222-8222-222222222222`), altrimenti il primo accesso apre un
account nuovo senza i crediti. Il realm di produzione non ha utenti: si
aggiungono con `kcadm.sh create partialImport` dal pod di Keycloak.

## Aggiornare

Nuovo tag nelle `docker build` (in locale, poi `docker save … | ssh … ctr import`) e in `tarots.yaml`, poi
`kubectl apply -f deploy/k8s/tarots.yaml`. Il pod dell'API applica da solo le
migrazioni all'avvio. Il server di tadamoo è carico: build e import in
containerd durano da minuti a un'ora, una immagine alla volta.

**Contesto di build (v8)**: `deploy/Dockerfile.backend` installa `seo-notify` e `lanterna`
(analytics), progetti separati (in locale `E:\Projects\seo-notify` e `E:\Projects\lanterna`, non su
PyPI) che devono stare **accanto a `backend/`** nel contesto di build; `deploy/Dockerfile.next` usa
`lanterna/js` (l'osservatore delle pagine del sito). Il tar dei sorgenti si prepara così:

```bash
tar --exclude=.git --exclude=node_modules --exclude=.venv --exclude=.next --exclude=__pycache__ \
  --exclude='*.mmdb' \
  -czf tarots-src.tar.gz backend frontend admin deploy -C /e/Projects seo-notify lanterna
```

L'immagine dell'API scarica in build DB-IP City Lite (paese e città dall'IP, ~130 MB): passare
`--build-arg GEO_MESE=$(date +%Y-%m)` alla `docker build` dell'API, così il file si aggiorna una volta
al mese e resta in cache per le altre build. Licenza CC BY 4.0: l'attribuzione a DB-IP è
nell'informativa privacy.

## Notifica ai motori di ricerca (v8)

Il CronJob `tarots-notifica-motori` (stessa immagine dell'API) ogni notte a mezzanotte, ora italiana,
annuncia gli articoli del blog pubblicati o modificati dall'ultimo giro. Tre canali indipendenti: uno
non configurato si salta, uno che fallisce non ferma gli altri. Esito e storico nella console, pagina
**SEO**, dove «Invia ora» fa lo stesso giro subito.

- **IndexNow** (Bing, Yandex…): la chiave è pubblica per protocollo. Sta in `tarots.yaml`
  (`TAROT_INDEXNOW_CHIAVE`) e nel file `frontend/public/<chiave>.txt`, che deve contenere la chiave
  stessa: cambiandola, vanno cambiati entrambi e ricostruito il sito.
- **WebSub** (feed RSS): l'hub è `TAROT_WEBSUB_HUB`, e deve coincidere con il `<atom:link rel="hub">`
  scritto in `frontend/app/blog/feed.xml/route.ts`.
- **Search Console** (Google): nessun OAuth interattivo, un *service account*. Una volta sola, dal
  browser: Google Cloud Console → abilitare «Google Search Console API» → creare un account di
  servizio → chiave JSON. In Search Console, sulla proprietà di dominio `tarots.chat` (verificata via
  DNS): Impostazioni → Utenti e autorizzazioni → aggiungere l'email dell'account di servizio come
  **Proprietario**. Poi sul server:

  ```bash
  kubectl -n tarots create secret generic tarots-search-console --from-file=credentials.json=/root/sa.json
  shred -u /root/sa.json
  ```

  Il Secret è montato (facoltativo) sia nell'API sia nel CronJob: dal giro successivo il canale Google
  risulta «configurato». La proprietà è `TAROT_SEARCH_CONSOLE_PROPRIETA` (`sc-domain:tarots.chat`).

Prova a mano del CronJob: `kubectl -n tarots create job --from=cronjob/tarots-notifica-motori prova-notifica`,
poi `kubectl -n tarots logs job/prova-notifica`.

## Analytics (v8, libreria `lanterna`)

Raccolta nostra, nel database dell'API (tabelle `an_*`): il sito manda i lotti a `POST /api/e`, l'API
aggiunge gli eventi di business (iscrizione, letture, acquisti…). Nessun cookie per la misura di base;
l'IP serve solo in memoria (paese/città da DB-IP City Lite, impronta giornaliera) e non si salva mai.
Console: **Analytics** (Traffico, Utenti, Imbuti, Ricavi, Esploratore, Rapporti, Studi, Impostazioni).

- **Spegnere la raccolta** senza ricostruire: `TAROT_ANALYTICS_ATTIVI=false` nel deployment dell'API
  (l'endpoint risponde 204 e scarta tutto; gli eventi di business non si scrivono).
- **Paese e città**: il file `/opt/geo/citta.mmdb` è nell'immagine (build con `GEO_MESE`, vedi
  «Aggiornare»); `TAROT_ANALYTICS_GEO` lo indica. Senza file mancano solo paese e città.
- **Giro notturno** (`tarots-analytics-notte`, 3:30): riepilogo giornaliero anonimo degli ultimi tre
  giorni (idempotente), cancellazione di sessioni ed eventi oltre i 25 mesi, e **avvisi**: se ieri
  visite, iscrizioni, letture, acquisti o errori del modello escono dal normale dei 28 giorni prima,
  un'email ai destinatari del rapporto (si spegne in console → Analytics → Rapporti).
  Prova: `kubectl -n tarots create job --from=cronjob/tarots-analytics-notte prova-analytics`.
- **Rapporto settimanale** (`tarots-rapporto-settimanale`, lunedì 0:30): email a chi è in elenco in
  console → Analytics → Rapporti, via Stalwart (`mail.tadamoo.com:465`, `noreply@tarots.chat`). La posta si
  imposta in console → Impostazioni → **Posta in uscita** (v9, Fase 2c: password cifrata, «Invia un'email di
  prova», stato di SPF/DKIM/DMARC); al primo avvio l'API copia lì da sola i `TAROT_SMTP_*` e la password
  `smtp-password` del Secret, che restano solo come ripiego. Stalwart **solo spedisce**: la posta in arrivo a
  @tarots.chat la riceve e la inoltra Namecheap (console → Account → Namecheap). Un solo tentativo
  (`backoffLimit: 0`): un rapporto rimandato arriverebbe doppio. Esito nella console e in
  `kubectl -n tarots logs job/<nome>`. Prima volta: aggiungere un destinatario e premere «Invia ora»
  per verificare che Stalwart accetti l'invio.
- **Interpretazione AI**: il modello si sceglie in console → Modelli → «Interpretazione dei dati»; il
  contesto del business in Analytics → Impostazioni. Riceve solo aggregati (gruppi di almeno 5 persone).
- **Colab**: i token si creano in Analytics → Studi; nel database resta solo la loro impronta.
  L'export per i notebook è `GET /api/analytics/export/<collezione>`, l'import firmato
  `POST /api/analytics/importa`.
- **Opposizione e consenso**: l'utente si oppone al legame visite-account dal profilo; il consenso
  dei cookie (livello esteso) si cambia dal banner o dalla pagina Privacy. Base giuridica e bilanciamento
  in `docs/privacy/lia-analytics.md`.

## Backup sul NAS (v8.3)

Il CronJob `tarots-backup` (stessa immagine dell'API, che porta `pg_dump`/`pg_restore` 18) ogni notte alle 2:30,
ora italiana, salva il database `tarots` **intero** — l'app, lo schema `keycloak` (utenti, accessi), le immagini
del blog e delle condivisioni (sono nel database) — con `pg_dump -Fc`, e lo carica via SFTP sul NAS di casa
(nella tailnet: il pod raggiunge `100.84.254.116:9222`, verificato il 30/9). Accanto a ogni copia c'è il suo
`.sha256`. Si tengono le **sette** più recenti (si cambia in console); le più vecchie si cancellano solo dopo un
caricamento riuscito e verificato. Se il backup fallisce: Job fallito ed email ai destinatari del rapporto
analytics. Tutto il resto — destinazione, accensione, prova, «Esegui ora», copie, storico, ripristino — dalla
console, pagina **Backup**.

**Prima volta.**

1. Una chiave SSH solo per il backup (non quella personale), con la parte pubblica sul NAS e la privata caricata in
   console (v9, Fase 2c): **Backup → Credenziale del NAS**, scegliendo il file o incollandolo (oppure la password
   dell'utente del NAS). Si salva cifrata con la chiave master che sta solo sul server: il dump che va sul NAS contiene
   solo testo cifrato. La console mostra tipo e impronta della chiave, mai la chiave.

   ```bash
   # su un PC qualunque
   ssh-keygen -t ed25519 -N "" -C tarots-backup -f tarots-backup
   ssh -p 9222 nuspy@100.84.254.116 'mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys' < tarots-backup.pub
   # poi in console: Backup → Credenziale del NAS → scegli il file `tarots-backup`; quindi cancellalo dal PC
   ```

   **Ripiego**: il Secret `tarots-backup` montato in `/etc/tarots-backup` (`ssh-key`, oppure `password`) vale finché la
   console non ha una credenziale; se c'è già (installazioni di prima della Fase 2c), al primo avvio l'API lo copia da
   sola in console, una volta, e lo scrive nell'audit. Da lì vale la console.

2. Console → **Backup**: host `100.84.254.116`, porta `9222`, utente, cartella. **Prova**: collega, crea la
   cartella se manca, scrive e cancella un file di prova e mostra la chiave dell'host (`SHA256:…`). Confrontarla
   con quella del NAS (`ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub` sul NAS) e premere **Fidati di questa
   chiave**: da lì ogni backup controlla che il NAS sia lui, e con un'altra chiave non parte niente.
3. Accendere il backup notturno e premere **Esegui ora**: la copia compare nell'elenco.

**Ripristino dalla console.** Scegliere una copia, scrivere `tarots` per confermare. La console fa prima una
**copia di sicurezza** del database attuale (`tarots-sicurezza-…`, se ne tengono tre; se non riesce, non
ripristina niente), poi scarica la copia, la confronta con il suo `.sha256` e la ripristina con
`pg_restore --clean --if-exists --single-transaction`: o tutto o niente. Alla fine:

```bash
kubectl -n tarots rollout restart deploy/tarots-api deploy/tarots-keycloak
```

**Ripristino a mano** (se la console non è raggiungibile), dal server:

```bash
scp -P 9222 nuspy@100.84.254.116:/Volume1/backup/tarots/tarots-AAAAMMGG-HHMMSS.dump /root/
kubectl -n tarots cp /root/tarots-AAAAMMGG-HHMMSS.dump $(kubectl -n tarots get pod -l component=api -o name | head -1 | cut -d/ -f2):/tmp/r.dump
kubectl -n tarots exec deploy/tarots-api -- sh -c 'python -m tarot_core.tools.backup_db --ora'   # copia di sicurezza prima
kubectl -n tarots exec deploy/tarots-api -- sh -c 'eval $(python -c "from sqlalchemy.engine import make_url; import os; u=make_url(os.environ[\"TAROT_DATABASE_URL\"]); print(f\"export PGHOST={u.host} PGPORT={u.port or 5432} PGUSER={u.username} PGPASSWORD={u.password} PGDATABASE={u.database}\")"); PGOPTIONS="-c lock_timeout=60000" pg_restore --clean --if-exists --single-transaction --no-owner --no-acl -d "$PGDATABASE" /tmp/r.dump && rm /tmp/r.dump'
kubectl -n tarots rollout restart deploy/tarots-api deploy/tarots-keycloak
```

Prova a mano del CronJob: `kubectl -n tarots create job --from=cronjob/tarots-backup prova-backup`, poi
`kubectl -n tarots logs job/prova-backup`.

## La v2 è il sito (v8.5)

La v2 sta alla radice (`app/(v2)`), la v1 sotto `/old` (`app/(old)/old`, `noindex` + `X-Robots-Tag`). Indirizzi
già indicizzati invariati (`/cards/…`, `/it/carte/…`, `/spreads`, `/it/stese`, `/pricing`, `/it/piano`,
`/card-of-the-day`, `/it/carta-del-giorno`, `/blog/…`, `/blog/sezione/…`); pagine nuove coi nomi della v2 (`/read`,
`/my-story`, `/decks`, `/shop`, `/cart`, `/shared/…`, `/physical-reading`, `/explore`, `/vote`, `/profile`, anche
sotto `/it`). Mappa in `frontend/lib/indirizzi.ts`, reindirizzamenti 308 nel proxy. Il ritorno di Keycloak è `/`
per il sito e `/old` per la v1 (il client accetta già `/*`). Prova dopo il rilascio:

```bash
for u in / /it /cards /it/carte /card-of-the-day /leggi /s/x /v2/cards /deck /carte/maj-17 /old; do
  printf "%-16s " "$u"; curl -s -o /dev/null -w "%{http_code} %{redirect_url}\n" "https://tarots.chat$u"; done
curl -sI https://tarots.chat/old | grep -i x-robots   # noindex, nofollow
```

## Le configurazioni stanno in console (v9, Fase 2c)

Richiesta dell'operatore: «Tutte le configurazioni devono essere lì». Sul server restano **solo tre segreti**, nel
Secret `tarots-secrets`: la password del database (`db-password`, `database-url`), la chiave master di cifratura
(`llm-provider-key`) e il segreto del client API↔Keycloak (`api-client-secret`; più `keycloak-admin-password` per la
console di Keycloak). Tutto il resto si imposta dalla console, cifrato con la chiave master dove è un segreto:

| Cosa | Dove in console |
|---|---|
| Stripe: chiavi, webhook, fornitore attivo | Pagamenti → Stripe |
| Posta in uscita (SMTP), prova d'invio, DNS (SPF/DKIM/DMARC) | Impostazioni → Posta in uscita |
| Dati del titolare per l'informativa privacy | Impostazioni → Dati del titolare |
| Credenziale del NAS (chiave SSH o password) | Backup |
| Fornitori LLM, Google, Reddit, store, social | Modelli, SEO/Analytics, Social, App mobili, Accesso con i social |

**Importazione al primo avvio.** Se in console una configurazione è vuota e l'ambiente del server ha il valore
(`TAROT_SMTP_*` con `smtp-password`, la chiave SSH montata in `/etc/tarots-backup`, le chiavi di Stripe,
`TAROT_BILLING_PROVIDER`), l'API la copia nel database **una volta sola** (registro `importazioni_ambiente`, voce
d'audit «importato dall'ambiente»), anche con più repliche che partono insieme (lock di PostgreSQL). Da lì vale la
console, anche se poi la si svuota. In console il campo risulta «impostato».

**Segreti interni.** L'impronta degli IP (`ip-hash-secret`) e il sale delle condivisioni (`condivisione-sale`) non si
impostano più: al primo avvio l'API li genera e li conserva cifrati (`segreti_sistema`); se il Secret li ha, valgono
quelli (copiati nel database). Non si mostrano mai.

**Account.** La pagina Account dice per ogni servizio se si imposta in console (con il collegamento), sul server (solo
i tre segreti), dal fornitore o se è automatico. La voce Namecheap spiega dominio, DNS e inoltro della posta in arrivo.

## Stripe (v9)

La cassa del sito è **Stripe Checkout** (`backend/tarot_core/billing/stripe.py`): pacchetti e ordini del negozio con un
pagamento singolo, abbonamenti come Subscription vere con un Price per piano e intervallo (creato al primo acquisto,
chiave `tarots_<piano>_<mese|anno>`). Il coupon resta interno: a Stripe arriva l'importo (per un abbonamento, uno sconto
d'una volta sul primo pagamento). I crediti nascono solo dall'evento firmato del webhook, mai dal ritorno del browser.

**Tutto dalla console (v9, Fase 2c): Pagamenti → Stripe.** Niente kubectl:

1. **Chiavi.** Due coppie, di prova (`sk_test_…`/`pk_test_…`, dashboard in «modalità test») e reali
   (`sk_live_…`/`pk_live_…`): Dashboard → Sviluppatori → Chiavi API. Si incollano in console scegliendo la modalità
   (la console rifiuta una chiave dell'altra modalità); la chiave segreta si salva **cifrata** nel database (chiave
   master `llm-provider-key`, che sta solo sul server) e non si rilegge più. **Prova la chiave** legge l'account
   (`GET /v1/account`, gratis). Si comincia con quelle di prova anche in produzione, si fa un acquisto con la carta
   `4242 4242 4242 4242`, poi si incollano le reali. Al posto della chiave segreta piena va bene una chiave limitata
   (`rk_…`) con scrittura su Checkout Sessions, Prices, Products, Coupons, Subscriptions, Subscription Schedules (Fase
   2b: downgrade) e Webhook Endpoints (la registrazione dalla console), e lettura su Invoices, Invoice Payments e Payment
   Methods (l'impronta della carta della prova).
2. **Registra il webhook.** La console crea su Stripe l'endpoint `https://tarots.chat/api/billing/webhook` (il gateway
   toglie `/api`: l'API lo serve come `/billing/webhook`) con tutti gli eventi qui sotto, e salva cifrato il segreto
   `whsec_…` che Stripe restituisce. Se l'endpoint esiste già lo aggiorna; se esiste ma il sito non ne ha il segreto
   (Stripe lo rivela solo alla creazione), lo sostituisce: sempre uno solo. Va rifatto dopo il passaggio alle chiavi
   reali (gli endpoint di prova e reali sono separati: cambiando modalità la console dimentica il vecchio segreto).
3. **Fornitore attivo**: Stripe. Vale subito per tutte le repliche (entro mezzo minuto) e per il CronJob
   `tarots-abbonamenti`; in produzione «Simulato» non si può scegliere.

**Ripiego.** `TAROT_BILLING_PROVIDER` e le chiavi `stripe-secret-key`/`stripe-webhook-secret` del Secret valgono
finché la console non ha scelto; se ci sono, al primo avvio l'API le copia in console da sola, una volta (audit
«importato dall'ambiente»). Una chiave mancante non impedisce più l'avvio: la pagina Pagamenti dice cosa manca.

**Eventi abilitati dal webhook** (`billing.stripe.EVENTI`):

`checkout.session.completed`, `checkout.session.async_payment_succeeded`, `checkout.session.async_payment_failed`,
`checkout.session.expired`, `invoice.paid`, `invoice.payment_failed`, `customer.subscription.updated`,
`customer.subscription.deleted`, `customer.subscription.trial_will_end` (Fase 2b), `charge.refunded`,
`charge.dispute.created`, `charge.dispute.closed`.

Il codice legge entrambe le forme degli oggetti (prima e dopo la versione API 2025 «basil»): non serve fissare una
versione, ma conviene che l'endpoint usi quella dell'account. Ogni evento conta una volta (`payment_events`), ogni
incasso accredita una volta e ogni rimborso storna una volta (indice unico su fornitore + riferimento + motivo).

**Rimborsi e contestazioni.** Un rimborso (anche parziale, in proporzione) o una contestazione tolgono i crediti che
quell'incasso aveva dato, anche se già spesi: il saldo può andare sotto zero, e finché è negativo non si aprono letture
(402 «saldo_negativo»: si torna in pari comprando un pacchetto). Una contestazione vinta li restituisce. Un rimborso che
il webhook non riesce a collegare (un incasso di prima del registro multicanale, un ordine del negozio) si registra a
mano dalla scheda dell'utente in console, pulsante «Storna» sul movimento: **non** rimborsa il denaro, quello si fa
nella dashboard di Stripe.

**Rinnovi.** Gli abbonamenti Stripe li rinnova Stripe (`invoice.paid`); il CronJob `tarots-abbonamenti` (ogni ora)
rinnova solo quelli interni e fa scadere quelli Stripe rimasti senza rinnovo da una settimana (webhook persi: vedere
«Eventi» nella dashboard). Prova: `kubectl -n tarots create job --from=cronjob/tarots-abbonamenti prova-abbonamenti`.

**Prove in locale con la Stripe CLI** (chiavi di prova, API su :8100):

```bash
stripe login
stripe listen --forward-to localhost:8100/billing/webhook     # stampa il whsec_… da mettere in TAROT_STRIPE_WEBHOOK_SECRET
stripe trigger checkout.session.completed                      # eventi finti: senza un checkout nostro rispondono «checkout sconosciuto»
stripe trigger charge.refunded
```

Il percorso completo si prova aprendo un checkout dal sito locale con `TAROT_BILLING_PROVIDER=stripe` e la carta 4242.

**Apple Pay e Google Pay sul web** sono già dentro Checkout: si attivano in Dashboard → Impostazioni → Metodi di
pagamento. Google Pay non chiede altro. Per Apple Pay: la pagina di Checkout sta su `checkout.stripe.com`, dominio
già registrato da Stripe, quindi di norma basta attivarlo; conviene comunque registrare `tarots.chat` (Impostazioni →
Domini dei metodi di pagamento → aggiungi), che diventa **obbligatorio** se un giorno il pagamento entra nelle pagine
del sito (Payment Element): allora Stripe chiede di pubblicare il file
`/.well-known/apple-developer-merchantid-domain-association` che fornisce, da mettere in `frontend/public/.well-known/`.
Controllo dopo l'attivazione: aprire un checkout da Safari su iPhone/Mac e vedere il pulsante Apple Pay.

**Ritorno all'app.** Il checkout può tornare al deep link dell'app (`chat.tarots.app://…`, schemi ammessi in
`TAROT_RITORNO_SCHEMI_APP`): Stripe torna solo a indirizzi web, quindi passa da `https://tarots.chat/api/billing/ritorno-app`,
che riconvalida lo schema e rimbalza.

**IVA (da decidere con il commercialista).** Vendendo servizi digitali a consumatori UE, l'IVA è quella del paese
dell'acquirente: o **Stripe Tax** (calcolo e riepiloghi; la dichiarazione OSS resta da fare) o la registrazione
**OSS** con le aliquote gestite a parte. Oggi i prezzi in catalogo sono importi finali e Stripe non aggiunge imposte:
qualunque scelta cambia `billing/stripe.py` (`automatic_tax`, indirizzo di fatturazione) e va fatta prima delle chiavi
reali. Non è consulenza fiscale.

## Abbonamenti: rinnovo automatico, conguaglio, prova, pagamenti falliti (v9, Fase 2b)

Le regole stanno in console → **Abbonamenti → Impostazioni** (sconto del rinnovo automatico 20%, sconto della prova
50%, prova 14 giorni, tolleranza 7 giorni, promemoria 2 giorni, 2 condoni per periodo, banner della prova) e
nell'elenco della stessa voce (abbonamenti per stato, con le azioni). I limiti dei piani (al giorno, alla settimana, al
mese, totali del periodo pagato) sono nel **Catalogo**. Il codice è in `backend/tarot_core/billing/abbonamenti.py`.

**Come si parla con Stripe** (niente da creare a mano: Price e coupon nascono al primo uso).

- *Prezzi*: il Price è sempre il listino (`tarots_<piano>_<mese|anno>`). Il primo pagamento ha **un solo coupon d'una
  volta** pari a tutto lo sconto (rinnovo automatico + codice + conguaglio): Stripe addebita al centesimo il totale
  mostrato sul sito.
- *Rinnovo automatico*: acceso, dal webhook l'abbonamento riceve un coupon `duration=forever` d'**importo fisso**
  (`tarots_rinnovo_<centesimi>_eur`, non una percentuale che Stripe arrotonderebbe a modo suo); spento,
  `cancel_at_period_end=true`, e senza rinnovi lo sconto non si applica più a niente. Riacceso prima della scadenza,
  `cancel_at_period_end=false` (e lo sconto, se era stato comprato senza rinnovo). Ogni spegnimento manda l'email di
  conferma formale.
- *Upgrade col conguaglio*: residuo = pagato del periodo × giorni interi rimasti / giorni del periodo; si paga
  `max(0, prezzo nuovo (scontato col rinnovo) − residuo)` in un Checkout nuovo, e a pagamento avvenuto il vecchio si
  chiude subito **senza rimborso** (`DELETE /subscriptions/…`, `prorate=false`). Non si usa la proration di Stripe:
  calcola al secondo sul listino, non sul pagato, e non coinciderebbe con le tre righe mostrate.
- *Downgrade*: un **subscription schedule** che lascia com'è il periodo in corso e cambia prezzo al rinnovo (funziona
  anche da annuale a mensile).
- *Prova*: Checkout con `trial_period_days` e il coupon «per sempre» dello sconto della prova; il metodo di pagamento
  si registra subito; alla fine Stripe addebita l'annuale scontato (`invoice.paid` → rinnovo). Una prova per utente e
  una per carta (`card.fingerprint`): con una carta già usata l'abbonamento appena nato si chiude subito senza addebito.
  Il promemoria due giorni prima lo manda il CronJob `tarots-abbonamenti` (email, una volta sola);
  `customer.subscription.trial_will_end` allinea solo la data.

**Pagamenti falliti: cosa impostare nel Dashboard di Stripe** (Impostazioni → Fatturazione → Abbonamenti ed e-mail →
«Gestisci pagamenti non riusciti»):

1. **Smart Retries** attivi, con la finestra di tentativi **entro 7 giorni** (o una pianificazione personalizzata, per
   esempio dopo 1, 3 e 5 giorni). Deve stare dentro la tolleranza della console: se si allunga una, si allunga l'altra.
2. Dopo l'ultimo tentativo: **«Annulla l'abbonamento»** (consigliato: arriva `customer.subscription.deleted`, chi aveva
   l'abbonamento torna sul gratuito) oppure **«Segna l'abbonamento come non pagato»** (`unpaid`: resta sospeso, e
   pagando la fattura riparte).
3. Lasciare la fattura aperta (non «contrassegnare come non riscuotibile»): il sito manda a pagare **quella stessa
   fattura** (la sua `hosted_invoice_url`), e pagarla ferma i tentativi automatici. Mentre c'è una fattura aperta il sito
   non apre nessun nuovo checkout di abbonamento: niente doppio addebito.
4. Le email di Stripe ai clienti per i pagamenti non riusciti si possono lasciare spente: le manda il sito, nelle sei
   lingue (fallimento, terzo giorno, sesto giorno, sospensione; e rinnovo avvenuto, disdetta, promemoria della prova).
   Accese, il cliente ne riceverebbe due.
5. Ricevute: Impostazioni → E-mail clienti → «Pagamenti riusciti» acceso (la ricevuta fiscale la manda Stripe).

Le email del sito passano dalla stessa posta del rapporto (console → Impostazioni → Posta in uscita; ripiego
`TAROT_SMTP_*`): senza non partono, e il registro `invii_email` lo dice (`non_configurato`). Ogni email ha una chiave unica: un giro ripetuto del cron non la rimanda.

**Commissione di referral sugli abbonamenti.** L'abbonamento non dà crediti, quindi la commissione di chi ha invitato
è la percentuale della console (Impostazioni → crediti, oggi 20%) **dell'importo pagato davvero** — primo pagamento,
ogni rinnovo, il conguaglio pagato di un upgrade, la conversione di una prova (mai la prova gratuita) — convertita in
crediti al prezzo per credito del pacchetto più economico in vendita, all'unità più vicina. Per i pacchetti resta la
percentuale dei crediti. **Un rimborso non toglie mai la commissione**: è un regalo in crediti a chi ha invitato, non
denaro, e lo storno tocca solo i crediti dell'acquirente.

**Per la Fase 4 (store), da impostare nelle console degli store** — lì il conguaglio e i tentativi li fa lo store, e
nel sito l'abbonamento mostra solo «gestisci nello store»:

- **Google Play Console** → Monetizza → Prodotti → Abbonamenti → (abbonamento) → **Grace period 7 giorni** (le letture
  restano mentre Google riprova) e **Account hold** acceso (dopo la tolleranza l'accesso si sospende finché il metodo di
  pagamento non è sistemato, fino a 30 giorni). Upgrade nello stesso gruppo di base plan con
  `CHARGE_PRORATED_PRICE`. La prova: un base plan annuale «a metà prezzo» con un'offerta di prova di 14 giorni,
  idoneità «mai abbonati».
- **App Store Connect** → App → Abbonamenti → **Billing Grace Period** acceso: Apple ammette **3, 16 o 28 giorni**
  (7 non c'è: il più vicino è 3, oppure 16 per non perdere chi rimedia tardi); il **billing retry** di Apple continua
  fino a 60 giorni. La prova: un prodotto annuale a metà prezzo con introductory offer «free trial 2 weeks» (l'idoneità
  la decide Apple, una per gruppo). Upgrade e downgrade nello stesso gruppo: Apple li applica da sé (upgrade immediato
  con rimborso proporzionale, downgrade al rinnovo).

## Acquisti negli store (v9, Fase 4)

Nelle app si compra con **Google Play** (Android) e con l'**App Store** (iPhone e iPad): pacchetti di crediti e
abbonamenti. Il denaro lo incassa lo store; il sito riceve la prova firmata dell'acquisto e accredita. Tre strade
portano la stessa prova, e l'acquisto conta **una volta sola** qualunque arrivi prima:

1. l'app, subito dopo l'acquisto, la manda al sito (`/billing/store/google/verifica`, `/billing/store/apple/verifica`);
2. lo store manda una **notifica** al sito a ogni acquisto, rinnovo, pagamento fallito, disdetta, rimborso;
3. ogni notte il CronJob `tarots-store-riconcilia` chiede agli store ciò che le notifiche potrebbero aver perso
   (rimborsi di Google degli ultimi 30 giorni, storia degli acquisti su iPhone degli ultimi 40 giorni).

Parole che tornano: un **prodotto** è ciò che si vende nello store (ha un ID, un nome e un prezzo per paese); un
**consumabile** si può comprare più volte (i pacchetti di crediti); un **abbonamento** si rinnova da solo; la
**sandbox** è l'ambiente di prova degli store, dove si «paga» senza addebito.

Le credenziali e gli indirizzi stanno in console → **App mobili** (Android, iOS); i prodotti in **App mobili →
Prodotti**; i rimborsi si fanno **nelle console degli store**, non nel sito (lo storno dei crediti arriva da solo).
Gli abbonamenti comprati negli store si vedono in console → **Abbonamenti** (filtro «Google Play» / «App Store»), e
gli acquisti di ogni persona nella sua scheda (console → Utenti → la persona → «Acquisti nelle app»).

### 1. I prodotti e i prezzi

Si creano prima nello store, poi si collegano in console → App mobili → Prodotti al piano del sito che accreditano.

- **Google Play**: Play Console → l'app → Monetizza → Prodotti → **Prodotti in-app** per i pacchetti (uno per
  pacchetto: `crediti_5`, `crediti_15`, `crediti_50`), **Abbonamenti** per gli abbonamenti. Un abbonamento di Google
  ha uno o più **base plan** (le varianti di durata e prezzo: mensile, annuale): in console si scrive
  `abbonamento:base_plan` (per esempio `oro:annuale`) e si sceglie «mensile», «annuale» o «annuale prova».
  Primo link: https://support.google.com/googleplay/android-developer/answer/1153481
- **Apple**: App Store Connect → l'app → Monetizzazione → **Acquisti in-app** per i pacchetti (tipo «Consumabile»), e
  **Abbonamenti** per gli abbonamenti, tutti nello **stesso gruppo di abbonamenti** (un gruppo è l'insieme fra cui
  l'utente sceglie: Apple gli lascia un solo abbonamento attivo per gruppo e gestisce da sé upgrade e downgrade).
  Ogni durata è un prodotto (`chat.tarots.oro.mese`, `chat.tarots.oro.anno`). Primo link:
  https://developer.apple.com/help/app-store-connect/manage-subscriptions/offer-auto-renewable-subscriptions
- I **prezzi** si decidono nello store, paese per paese: il sito non li cambia. Nei ricavi del sito un acquisto dello
  store vale il listino del piano (Google non dice il prezzo pagato; Apple sì, e la scheda dell'utente lo mostra).
- Su Google lasciare spenta la «quantità multipla» dei prodotti in-app: un acquisto accredita un pacchetto.

### 2. La prova gratuita negli store

Il prodotto «prova» è l'**annuale a metà prezzo** (lo sconto della prova della console, oggi 50%) con 14 giorni
gratis. In console va collegato come «annuale prova».

- **Google**: sull'abbonamento, un base plan annuale a metà prezzo con un'**offerta** di tipo «prova gratuita» di 14
  giorni, idoneità «nuovi clienti» (mai abbonati). Primo link:
  https://support.google.com/googleplay/android-developer/answer/140504
- **Apple**: sul prodotto annuale a metà prezzo, una **introductory offer** (offerta introduttiva) «Prova gratuita, 2
  settimane». L'idoneità la decide Apple (una per gruppo). Primo link:
  https://developer.apple.com/help/app-store-connect/manage-subscriptions/set-up-introductory-offers-for-auto-renewable-subscriptions

Chi ha già fatto la prova sul sito può riceverla dallo store: lo decide lo store, e il sito non la rifiuta (lo store
addebiterebbe comunque alla fine). Il promemoria due giorni prima della fine parte anche per le prove degli store.

### 3. La tolleranza sui pagamenti falliti

È già scritta nella sezione della Fase 2b qui sopra: Google **grace period 7 giorni + account hold**, Apple **Billing
Grace Period** (3, 16 o 28 giorni) + billing retry. Nel sito la tolleranza dello store è «in tolleranza» con le letture
comprese ancora attive; account hold o fine della tolleranza è «sospeso». Gli avvisi di pagamento li manda lo store
(con l'importo vero e il link per sistemare): il sito non manda i suoi solleciti per gli abbonamenti degli store.
Primo link per Apple: https://developer.apple.com/help/app-store-connect/manage-subscriptions/enable-billing-grace-period-for-auto-renewable-subscriptions

### 4. Le notifiche di Google (RTDN, con Pub/Sub e push autenticato)

Google non chiama il sito direttamente: pubblica un messaggio in un **topic** di Google Cloud Pub/Sub (una «casella»
di messaggi), e una **sottoscrizione push** lo consegna al sito. Il push è **autenticato**: ogni consegna porta un
token firmato da Google a nome di un service account, e il sito accetta solo quel service account.

1. Google Cloud (lo stesso progetto del service account della Play Developer API) → Pub/Sub → **Crea topic**
   (`play-rtdn`). Nelle autorizzazioni del topic aggiungi `google-play-developer-notifications@system.gserviceaccount.com`
   con il ruolo **Pub/Sub Publisher**. Primo link: https://developer.android.com/google/play/billing/getting-ready#configure-rtdn
2. Crea un **service account** solo per il push (per esempio `pubsub-push`), senza chiavi da scaricare.
3. Sul topic → **Crea sottoscrizione** di tipo **Push**, endpoint = l'indirizzo «Indirizzo RTDN» copiato da console →
   App mobili → Android (`https://tarots.chat/api/billing/store/google/rtdn`), **Abilita autenticazione** con il
   service account del punto 2; l'audience si può lasciare vuota (allora è l'indirizzo stesso). Primo link:
   https://cloud.google.com/pubsub/docs/authenticate-push-subscriptions
4. In console → App mobili → Android scrivi il **topic**, l'**email del service account del push** e, se l'hai
   scritta, l'**audience**. Senza l'email il sito rifiuta ogni notifica (risponde 401).
5. Play Console → l'app → Monetizza → Impostazioni di monetizzazione → **Notifiche in tempo reale**: incolla il topic
   (`projects/<progetto>/topics/play-rtdn`) e premi **Invia notifica di prova**. In console → App mobili → Android
   «Ultima notifica ricevuta» deve diventare «TEST».

Il service account della Play Developer API (quello caricato in console) deve avere in Play Console → Utenti e
autorizzazioni almeno «Visualizza dati finanziari» e «Gestisci ordini e abbonamenti»: serve a leggere gli acquisti, a
confermarli (Google rimborsa da sé un acquisto non confermato entro 3 giorni) e a leggere i rimborsi.

### 5. Le notifiche di Apple (App Store Server Notifications V2)

App Store Connect → l'app → Informazioni sull'app → **App Store Server Notifications**: in «URL del server di
produzione» e in «URL del server sandbox» incolla l'«Indirizzo delle notifiche» copiato da console → App mobili → iOS
(`https://tarots.chat/api/billing/store/apple/notifiche`), **versione 2**. Primo link:
https://developer.apple.com/help/app-store-connect/configure-in-app-purchase-settings/enter-server-urls-for-app-store-server-notifications

Poi in console → App mobili → iOS «Verifica»: Apple manda una notifica di prova, e «Ultima notifica ricevuta» diventa
«TEST». Servono l'**Apple ID dell'app** (le firme di produzione lo contengono) e la chiave .p8 della App Store Server
API (per la riconciliazione notturna). Le firme di Apple si controllano fino al certificato radice **Apple Root CA -
G3**, che è già nel codice: non c'è niente da caricare.

Le richieste di Apple «quanto è stato usato questo acquisto?» (quando qualcuno chiede un rimborso) **si ignorano**:
rispondere vorrebbe dire mandare ad Apple dati d'uso della persona senza il suo consenso. Apple decide da sola.

### 6. Le prove (sandbox) e la revisione delle app

- Google: Play Console → Impostazioni → **Test delle licenze**: gli account aggiunti comprano senza addebito. Primo
  link: https://support.google.com/googleplay/android-developer/answer/6062777
- Apple: App Store Connect → Utenti e accesso → **Sandbox** → Account di test. Primo link:
  https://developer.apple.com/help/app-store-connect/test-in-app-purchases/create-a-sandbox-apple-account

Gli acquisti di prova **si accreditano anche in produzione** (chi rivede l'app per Apple deve vedere arrivare i
crediti), ma restano segnati «sandbox»: non entrano nei ricavi, nelle statistiche degli acquisti né nelle commissioni
di chi ha invitato. In console si riconoscono dalla scritta «prova (sandbox)».

### 7. La commissione ridotta (15%)

Gli store trattengono il 30%, o il **15%** sul primo milione di dollari l'anno, ma va **chiesto**:

- Apple: **App Store Small Business Program** (si fa domanda una volta, vale dall'anno dopo l'approvazione). Primo
  link: https://developer.apple.com/app-store/small-business-program/
- Google: il 15% sul primo milione si attiva creando il **gruppo di account** in Play Console. Primo link:
  https://support.google.com/googleplay/android-developer/answer/112622

In console → App mobili segna «commissione ridotta» / «Small Business Program» quando è attivo: è un appunto.

### 8. Cosa fa l'app (Fase 9)

- La pagina dei prezzi dell'app mostra i prodotti dello store coi **prezzi dello store**; un prodotto che c'è in
  console ma non nello store (non ancora creato o non attivo) semplicemente non compare.
- Il **pulsante «Paga con carta»** (Stripe, nel browser) compare solo dove App mobili → Politica Stripe lo ammette
  per il **paese dello store** del telefono (senza una regola: nascosto). È l'unico posto dove valgono i **codici
  sconto**: negli store no. Se il telefono non dice il paese (un emulatore senza Play Store), vale la regola `*`.
- Ogni acquisto passa dal sito **prima** di essere chiuso presso lo store; uno che il sito non riesce a registrare
  (per esempio un prodotto non collegato in console) resta aperto e l'app riprova: la persona legge «non siamo ancora
  riusciti a registrare questo acquisto… se non compare entro un giorno, scrivici». Su Google, un acquisto non
  confermato entro 3 giorni viene rimborsato da Google.
- «Ripristina gli acquisti» (Apple lo chiede) e «Gestisci in Google Play / App Store» nel profilo.
- Per provare su Android: un account in **Test delle licenze** (sopra) e l'app caricata almeno nel test interno di
  Play Console. L'emulatore di sviluppo non ha il Play Store: lì l'app dice che gli acquisti non sono disponibili.

### Cosa fa il sito, in breve

- **Un solo abbonamento attivo per persona**, qualunque sia il canale: un abbonamento nuovo nello store chiude quello
  del sito (su Stripe lo disdice a fine periodo). Un abbonamento di un **altro** store non si può disdire da qui: se
  continua a rinnovarsi, la scheda della persona lo segna «doppio» e va detto alla persona di disdirlo nello store.
- **Disdetta**: si fa nello store; il sito riceve la notifica e manda l'email di conferma, come per Stripe.
- **Rimborso** (fatto nella console dello store, o deciso dallo store): i crediti dell'acquisto si stornano (il saldo
  può andare sotto zero); un abbonamento rimborsato nel periodo in corso si chiude e si torna al gratuito.
- Il profilo, per un abbonamento degli store, mostra «Gestisci in Google Play / App Store» con lo stato e niente
  pulsanti di disdetta o di cambio piano.
- Prova a mano della riconciliazione: `kubectl -n tarots create job --from=cronjob/tarots-store-riconcilia prova-store`.

## Notifiche (v9, Fase 5)

Ogni mattina la notifica della **carta del giorno**, e qualche altro promemoria (serie dei giorni in pericolo,
benvenuto, fine della prova, pagamento non riuscito); in più le **campagne** che scrivi dalla console per un gruppo di
utenti. Arrivano nelle app (Android, iPhone, iPad) e nel **browser** di chi usa il sito. Si governa tutto dalla console
→ **Notifications** (Campagne, Automatiche, Consegne e aperture, Impostazioni); il CronJob `tarots-notifiche` manda
ogni 15 minuti, all'ora **locale** di ciascuno, mai nelle ore di silenzio (predefinite 22–8).

**1. Firebase (per le app), una volta.** Firebase è il servizio gratuito di Google che porta le notifiche ai telefoni.

1. Apri https://console.firebase.google.com/ con l'account Google dell'attività → «Crea un progetto» (es. «TAROTS
   chat»; Google Analytics facoltativo).
2. Nel progetto aggiungi l'app **Android** e l'app **Apple** con l'identificativo `chat.tarots.app`: i due file che
   Firebase fa scaricare (`google-services.json`, `GoogleService-Info.plist`) servono all'app (Fase 9).
3. ⚙ Impostazioni progetto → **Account di servizio** → «Genera nuova chiave privata»: si scarica un file `.json`.
4. Console → Notifications → **Impostazioni** → carica il file → «Prova» (Firebase controlla un messaggio senza
   recapitarlo). Il file resta cifrato nel database; non va messo sul server né in Kubernetes.

**2. Apple (iPhone e iPad), una volta, dopo l'Apple Developer Program.** Apple vuole una sua chiave, che si dà a
Firebase (non a noi):

1. Apri https://developer.apple.com/account/resources/authkeys/list → «+» → spunta **Apple Push Notifications service
   (APNs)** → scarica il file `.p8` (si scarica una volta sola: conservalo) e annota **Key ID** e **Team ID**.
2. In Firebase: ⚙ Impostazioni progetto → **Cloud Messaging** → app Apple → «Chiave di autenticazione APNs» → carica
   il `.p8` con Key ID e Team ID. Fatto: le notifiche iOS passano da Firebase.

**3. Il sito (Web Push): nulla da fare.** Le chiavi VAPID le genera il sito da solo al primo uso e le conserva cifrate
(`segreti_sistema`, con la chiave master: per questo non va mai cambiata). Funziona su Chrome, Edge, Firefox e Safari;
**su iPhone e iPad solo dal sito aggiunto alla schermata Home** (Condividi → «Aggiungi alla schermata Home», iOS 16.4
o successivi: serve il manifest `/manifest.webmanifest`, già pubblicato). Il sito lo spiega a chi usa Safari su iOS.
Il permesso non si chiede mai all'apertura: solo dopo aver girato la carta del giorno («vuoi che te la ricordiamo ogni
mattina?») o dal profilo → Notifiche.

**Regole.** Le promozioni partono solo a chi ha acceso «Promozioni» nei consensi, con un tetto settimanale (2, dalla
console) e il pulsante «Niente più promozioni» (link firmato `/notifiche/disiscrivi`, un clic, senza accesso); il
genere e i dati sensibili non sono mai filtri. Il giorno della carta del giorno è quello locale di chi ha un fuso
(rilevato dal browser o dall'app); senza fuso resta quello di Roma.

**Per l'app (Fase 9, fatta: `mobile/lib/notifiche/`).** Finché i due file di Firebase non sono nell'app
(`mobile/LEGGIMI.md`, «Attivare Firebase»), l'app funziona con le notifiche spente e lo dice nel profilo. Con
`firebase_messaging` l'app, dopo l'accesso e dopo il permesso chiesto in due tempi, manda il
token a `POST /me/dispositivi` con `{"canale": "fcm", "piattaforma": "android" | "ios", "token": "<token FCM>",
"lingua": "it", "fuso_orario": "Europe/Rome", "versione_app": "1.0.0"}` (di nuovo a ogni avvio e a ogni
`onTokenRefresh`: la riga è una sola per token), e all'uscita dall'account `DELETE /me/dispositivi` con `{"canale":
"fcm", "token": …}`. Crea i canali Android `servizio` e `promozioni`; al tocco apre il percorso in `data.link` (le rotte
sono quelle del sito) e chiama `POST /notifiche/aperta` con `{"invio": data.invio, "firma": data.firma}`. Le preferenze
sono le stesse del sito: `GET/PUT /me/preferenze-notifica`.

Prova a mano del giro: `kubectl -n tarots create job --from=cronjob/tarots-notifiche prova-notifiche`.

## Collegamenti del sito nelle app (v9, Fase 10: App Links e Universal Links)

Un collegamento a tarots.chat (una carta, la carta del giorno, un articolo, il ritorno da un pagamento con carta) si
apre **direttamente nell'app** se è installata, senza chiedere «apri con». Il telefono lo accetta solo se il sito
dichiara l'app in due file, che il sito scrive da solo coi valori della console:

- `https://tarots.chat/.well-known/assetlinks.json` (Android): package e **impronte SHA-256** dei certificati di firma;
- `https://tarots.chat/.well-known/apple-app-site-association` (iPhone e iPad): Team ID, bundle ID e i percorsi.

**Cosa fare, una volta:**

1. **Android** — Play Console → l'app → Test e rilascio → Configurazione → **Integrità dell'app** → scheda «Firma
   dell'app»: copia l'«Impronta del certificato SHA-256» della **chiave di firma dell'app** e quella della **chiave di
   caricamento**. Incollale in console → App mobili → Android → «Collegamenti del sito nell'app», una per riga, poi
   «Salva». (Per provare un APK di debug si aggiunge anche l'impronta della chiave di debug: è in `mobile/LEGGIMI.md`.)
2. **iOS** (quando si compilerà): console → App mobili → iOS → **Team ID** (developer.apple.com → Account →
   Membership). Il bundle ID è già `chat.tarots.app`.
3. Controllo: `curl -i https://tarots.chat/.well-known/assetlinks.json` deve rispondere **200** con
   `Content-Type: application/json` e il package con le impronte; lo strumento di Google
   https://developers.google.com/digital-asset-links/tools/generator (dominio `tarots.chat`, package
   `chat.tarots.app`, impronta) dice «verificato». Sul telefono: `adb shell pm get-app-links chat.tarots.app`.

**Il percorso dei file.** Li serve il sito Next.js (`frontend/app/.well-known/…/route.ts`), che li legge dall'API
(`/app/collegamenti/…`). Nessun reindirizzamento (Android e Apple non li seguono): nel gateway (`tarots.yaml`)
`/.well-known/` cade in `location /` e va a `tarots-web` così com'è; il proxy del sito lo esclude (niente lingua,
niente 308); NPM non riscrive i percorsi (Force SSL vale solo per http, e i telefoni chiedono già https). Se l'API non
risponde i file danno **503** (non 404, che farebbe credere al telefono che l'associazione non esista più).
`www.tarots.chat` è un reindirizzamento permanente: non va verificato (l'app lo tiene fuori dalla verifica).

**Quali pagine.** Solo quelle che l'app ha (carte, stese, carta del giorno, prezzi, prova, profilo, diario…, in
inglese e sotto `/it`, più i vecchi indirizzi); **mai** `/auth` (il ritorno del login di Google passa di lì: se lo
prendesse l'app, l'accesso si romperebbe), `/api` (il link «niente più promozioni» delle notifiche), `/admin`,
`/old`. L'elenco è `PERCORSI_APP` in `backend/tarot_core/domain/app_mobili_repositories.py`, lo stesso dei filtri di
`mobile/android/app/src/main/AndroidManifest.xml` (un test dell'app controlla che coincidano).

## Accesso dalle app (v9, Fase 6)

Nell'app per **Android** si entra solo con **Google**, in quella per **iPhone e iPad** solo con **Apple**. L'app non
ha un suo login: apre la pagina di accesso di Keycloak nel browser del telefono, già puntata sul social giusto, e torna
all'app da sola. Per Google e Apple è quindi un accesso web come quello del sito: **le credenziali sono le stesse del
sito**, in console → «Accesso con i social». Chi ha già un account con la stessa email lo ritrova (l'unione degli
account, come sul sito).

### Cosa fare, in ordine

1. **Console → App mobili → Android (o iOS) → «Prepara l'accesso dall'app»**, una volta: crea in Keycloak il client
   delle app (`tarot-mobile`). Se c'è già non lo tocca. Non serve kubectl.
2. **Google** (Android): niente di nuovo. Il client OAuth «Applicazione web» già creato per il sito basta, perché il
   telefono passa da Keycloak nel suo browser e Google vede l'indirizzo di ritorno di Keycloak, già registrato. Un
   client «Android» in Google Cloud servirebbe solo con il pulsante nativo di Google dentro l'app, che non usiamo.
   Controllo: Google Cloud → API e servizi → Credenziali, il client del sito ha fra gli «URI di reindirizzamento
   autorizzati» `https://tarots.chat/auth/realms/tarots/broker/google/endpoint`. Primo link:
   https://console.cloud.google.com/apis/credentials
3. **Apple** (iPhone, e anche il sito), in Apple Developer → Certificates, Identifiers & Profiles. Primo link:
   https://developer.apple.com/account/resources/identifiers/list
   1. **App ID** dell'app (`chat.tarots.app`): spunta la capacità «Sign in with Apple» (è l'App ID «primario»).
   2. **Services ID** (Identifiers → «+» → Services IDs), per esempio `chat.tarots.web`: è il «client id» del login con
      Apple, lo stesso per sito e app. Spunta «Sign in with Apple» → Configure: «Primary App ID» = quello del punto 1
      (così la persona ha lo stesso identificativo Apple nell'app e sul sito), «Domains and Subdomains» = `tarots.chat`,
      «Return URLs» = `https://tarots.chat/auth/realms/tarots/broker/apple/endpoint` (la console lo mostra con «Copia»).
   3. **Chiave** (Keys → «+»): spunta «Sign in with Apple», Configure → lo stesso App ID primario. Scarica il file
      `AuthKey_XXXXXXXXXX.p8` (**si scarica una volta sola**: tienine una copia fuori dal computer) e annota il
      **Key ID**. Il **Team ID** è in Account → Membership details.
   4. **Console → Accesso con i social → Apple**: Team ID, Services ID, Key ID, il file .p8, «Acceso» → «Salva e
      firma». Il sito firma il segreto che Apple vuole (scade entro sei mesi), lo scrive in Keycloak e mostra fino a
      quando vale. Il CronJob `tarots-apple-segreto` (il 1° di ogni mese) lo rinnova da solo quando ne mancano meno di
      75 giorni; «Rinnova ora» lo fa subito. Niente estensioni di terzi dentro Keycloak.
   5. Prova: dal sito, «Continua con Apple» nella pagina di accesso.

### Cose da sapere

- **Il nome.** Apple dà nome e cognome solo al primo accesso, e Keycloak non li legge: chi entra con Apple arriva senza
  nome. Il profilo del sito glielo chiede con garbo («Come ti chiami?»), sempre facoltativo.
- **«Nascondi la mia email».** Chi la sceglie dà ad Apple un indirizzo inventato (`…@privaterelay.appleid.com`): il sito
  non può riconoscerlo e nell'app nascerebbe un account nuovo, vuoto. Due rimedi, nel profilo del sito → «Modi di
  accesso»:
  - **«Collega il tuo Apple ID»** (e «Collega Google») prima di usare l'app: da lì in poi Apple porta a questo account;
  - il **codice dell'app**: se l'account nuovo nell'app è già nato, l'app mostra «Hai già un account sul sito?» e un
    codice di 8 caratteri (vale 10 minuti, una volta sola). Scritto nel profilo del sito, l'accesso con Apple passa
    all'account vecchio insieme a ciò che si era fatto nell'app (letture, crediti, acquisti), e l'account nuovo si
    chiude (riga separata, utente Keycloak disattivato). Vale anche per chi passa da iPhone ad Android: l'account nato
    con Google consegna Google a quello nato con Apple. Un abbonamento pagato sull'account nuovo non si sposta da solo:
    il sito lo dice e chiede di scriverci.
- **La lingua.** Quando la persona cambia lingua sul sito, la stessa va anche in Keycloak (attributo `locale`): le email
  di Keycloak (verifica dell'indirizzo, password dimenticata) arrivano nella sua lingua. Keycloak ha sei lingue (en, it,
  hu, ru, uk, es): per le altre usa l'inglese.
- **Revisione Apple.** La regola 4.8 chiede «Sign in with Apple» quando ci sono altri social: nell'app c'è solo quello.
  Il login avviene nel browser di sistema (ASWebAuthenticationSession), che Apple accetta; se un revisore chiedesse il
  pulsante nativo, servirebbe un passo in più (lo scambio del token di Apple con Keycloak).
- Prova a mano del rinnovo: `kubectl -n tarots create job --from=cronjob/tarots-apple-segreto prova-apple` (con
  `--forza` nel comando del Job lo rinnova anche se è lontano dalla scadenza).

## Aggiornare il realm esistente (login persistente, accesso con i social, tema v5)

Il realm di produzione esiste già e `--import-realm` non lo rilegge: le modifiche di `realm-tarots.prod.json` si
portano sul realm vivo con `kcadm`, dal pod di Keycloak. Comandi provati su un Keycloak 26.0.8 locale.

```bash
KC="kubectl -n tarots exec deploy/tarots-keycloak -- /opt/keycloak/bin/kcadm.sh"
PW=$(kubectl -n tarots get secret tarots-secrets -o jsonpath='{.data.keycloak-admin-password}' | base64 -d)
$KC config credentials --server http://localhost:8080/auth --realm master --user admin --password "$PW"

# 1. L'account di servizio dell'API: i due ruoli che usa la console, e solo quelli.
$KC add-roles -r tarots --uusername service-account-tarot-api --cclientid realm-management \
  --rolename manage-realm --rolename manage-identity-providers
$KC get-roles -r tarots --uusername service-account-tarot-api --cclientid realm-management --fields name

# 2. Il segreto del client tarot-api deve essere quello del Secret (`api-client-secret`), che ora riceve anche l'API.
ID_API=$($KC get clients -r tarots -q clientId=tarot-api --fields id --format csv --noquotes)
$KC get clients/$ID_API/client-secret -r tarots          # confrontare con:
kubectl -n tarots get secret tarots-secrets -o jsonpath='{.data.api-client-secret}' | base64 -d; echo
# se diversi, si allinea Keycloak al Secret:
#   $KC update clients/$ID_API -r tarots -s "secret=$(kubectl -n tarots get secret tarots-secrets -o jsonpath='{.data.api-client-secret}' | base64 -d)"

# 3. Login persistente: token offline per 365 giorni d'inattività, nessuna durata massima; «Ricordami» spento
#    (non serve più); le lingue del tema.
$KC update realms/tarots -s offlineSessionIdleTimeout=31536000 -s offlineSessionMaxLifespanEnabled=false \
  -s rememberMe=false -s internationalizationEnabled=true \
  -s 'supportedLocales=["en","it","hu","ru","uk","es"]' -s defaultLocale=en
$KC get roles/default-roles-tarots/composites -r tarots --fields name   # deve esserci offline_access
#   se manca: $KC add-roles -r tarots --rname default-roles-tarots --rolename offline_access

# 3b. IMPORTANTE: chi non ha il ruolo offline_access non riesce più a entrare («Offline tokens not allowed for the
#     user or client»). Gli iscritti dal sito e quelli creati con POST /users hanno default-roles-tarots (che lo
#     contiene); gli utenti creati con partialImport e `realmRoles` espliciti (gli utenti di prova!) no. Si assegna
#     default-roles-tarots a tutti — è idempotente, chi lo ha già resta com'è:
for u in $($KC get users -r tarots --fields username --format csv --noquotes -l 100000); do
  $KC add-roles -r tarots --uusername "$u" --rolename default-roles-tarots
done

# 4. Il tema (immagine tarots-keycloak:v5): già impostato, per controllo.
$KC get realms/tarots --fields loginTheme,accountTheme                    # tarots, tarots
```

**I provider social** non serve crearli a mano: la console («Accesso con i social») li crea al primo salvataggio,
con il flusso della 2FA amministratori dopo l'accesso esterno. Chi preferisse la riga di comando:

```bash
$KC create identity-provider/instances -r tarots -s alias=github -s providerId=github -s displayName=GitHub \
  -s enabled=true -s trustEmail=true -s 'firstBrokerLoginFlowAlias=first broker login' \
  -s 'postBrokerLoginFlowAlias=2FA amministratori dopo accesso esterno' \
  -s config.clientId=<client id> -s config.clientSecret=<segreto> -s config.defaultScope=user:email -s config.syncMode=IMPORT
```

(per i provider già presenti — google, facebook, apple — `update identity-provider/instances/<alias>` con le stesse
`-s`). L'indirizzo di ritorno da registrare presso ciascun provider è
`https://tarots.chat/auth/realms/tarots/broker/<alias>/endpoint` (`google`, `facebook`, `microsoft`, `apple`,
`github`, `linkedin`, `twitter`).

**Ordine del rilascio**: immagine `tarots-keycloak:v5` costruita in locale e importata in containerd; i comandi qui
sopra; `kubectl apply -f deploy/k8s/tarots.yaml` (tag v5 e `TAROT_KEYCLOAK_CLIENT_ID/SECRET` all'API); le immagini
nuove di API, sito e console. Chi è già connesso resta connesso finché il suo token di rinnovo vecchio (non offline)
vale; al primo accesso successivo riceve quello offline.

## Un account per persona e dati dai social (v8.6)

Stessa email = stesso account, comunque si entri: email e password, Google, Facebook, Apple, GitHub, LinkedIn.
L'app lega i suoi utenti al `sub` di Keycloak, e Keycloak collega le identità social all'utente esistente: un solo
`sub`, un solo account anche nell'app. Provato su un Keycloak 26.0.8 locale con un provider OIDC finto:
password → social e social → altro social danno lo stesso `sub` senza domande; social → registrazione con la
stessa email non crea un secondo account e mostra il testo del tema che rimanda al social.

- **Il flusso** «primo accesso con unione degli account» (Review Profile solo se manca qualcosa → Create User If
  Unique | `tarots-unione-sicura`) lo crea il backend (`KeycloakAdmin.assicura_flusso_unione`, serve
  `manage-realm`, che l'account di servizio ha già) e lo assegna ai provider con l'email garantita (`trustEmail`).
  **X e Microsoft restano su `first broker login`** (conferma e nuovo accesso con la password o con un social già
  collegato): X non garantisce l'email, e in Entra ID l'email la scrive l'amministratore del tenant.
- **Account con l'email mai verificata** (il caso del furto preventivo: un intruso registra con una password l'email
  di un altro, senza poterla verificare, e aspetta che il titolare entri col social). Il passo `tarots-unione-sicura`
  (`deploy/keycloak/spi`, nell'immagine Keycloak) collega come quello di Keycloak, ma se l'email dell'utente che c'era
  **non è verificata** prima gli toglie password, OTP e chiavi di sicurezza, i collegamenti con i social non fidati
  (X, Microsoft), tutte le sessioni (anche quelle offline del login persistente) e i token già emessi; nome e cognome
  diventano quelli del social; l'email diventa verificata (niente blocco alla verifica, anche con `verifyEmail`
  acceso). Lo scrive nel token (claim `tarots_unione`, dal mapper «unione da confermare» di `tarot-frontend`) e il
  sito chiede alla persona **«era tuo?»**: sì → resta com'è; no → la riga dell'app si separa (disattivata, non
  cancellata: letture e acquisti dell'altro restano per la contabilità) e la persona riparte con un account nuovo.
  Nella stessa finestra può scegliere una password (anche quella di prima): la imposta il backend con `manage-users`,
  solo per sé stessa e solo mentre la domanda è aperta. Con l'email già verificata non cambia niente.
  Provato su Keycloak 26.0.8 locale (33 controlli, con `verifyEmail` spento e acceso).
- **All'indietro** (prima il social, poi email e password): Keycloak non fonde una registrazione nuova con un account
  esistente senza prova di possesso dell'email — sarebbe un furto d'account. Il tema spiega che l'account esiste e
  rimanda al social; per avere anche una password: «Password dimenticata?» (**serve l'SMTP**) oppure, entrati col
  social, «Account → Accesso → Imposta la password» nella console dell'account (funziona anche senza SMTP). Dalla
  stessa console si vedono e si scollegano i social collegati («Account collegati»).
- **Dati del profilo**: il sito chiama `POST /me/profilo-social` dopo ogni accesso; il backend legge con il token
  della persona i social collegati e il token che Keycloak conserva per ciascuno (`storeToken`, ruolo
  `broker/read-token` nei ruoli predefiniti), chiede al provider nome, cognome, data di nascita, sesso, lingua, foto e
  città, e riempie **solo i campi vuoti** della scheda. La posizione attuale, se il social non la dà, viene dall'IP
  con il DB-IP delle analytics (`TAROT_ANALYTICS_GEO`).

### Sul realm esistente

Dalla console: «Accesso con i social» → **Applica l'unione degli account** (crea il flusso, lo assegna, fa conservare
i token; un flusso creato prima con «idp-auto-link» passa al passo sicuro). Salvare un provider fa lo stesso per quel
provider. **Prima** va installata l'immagine nuova (il passo `tarots-unione-sicura` deve esistere, altrimenti il flusso
non si crea e l'unione resta spenta). Restano a mano, una volta, i ruoli e il mapper:

```bash
# (stesse variabili $KC del paragrafo precedente)
# 1. Chi entra può leggere il token che il suo social gli ha dato (il backend lo usa con il token della persona).
$KC add-roles -r tarots --rname default-roles-tarots --cclientid broker --rolename read-token
$KC get roles/default-roles-tarots/composites -r tarots --fields name     # deve esserci read-token
# 2. In alternativa al pulsante della console, per un provider già presente (es. google):
$KC update identity-provider/instances/google -r tarots \
  -s 'firstBrokerLoginFlowAlias=primo accesso con unione degli account' -s storeToken=true
$KC get identity-provider/instances/google -r tarots --fields alias,firstBrokerLoginFlowAlias,storeToken,trustEmail
#    (il flusso deve già esistere: lo crea il pulsante della console, o un salvataggio di un provider)
# 3. L'API imposta la password scelta dopo un'unione (solo quella della persona stessa).
$KC add-roles -r tarots --uusername service-account-tarot-api --cclientid realm-management --rolename manage-users
# 4. Il claim che dice al sito cosa è stato tolto (nota della sessione → token d'accesso di tarot-frontend). Il
#    mapper è in un file (le virgolette annidate di `-s 'config."…"'` si rompono facilmente); `exec -i` per lo stdin.
ID_WEB=$($KC get clients -r tarots -q clientId=tarot-frontend --fields id --format csv --noquotes)
kubectl -n tarots exec -i deploy/tarots-keycloak -- /opt/keycloak/bin/kcadm.sh create \
  clients/$ID_WEB/protocol-mappers/models -r tarots -f - < deploy/keycloak/strumenti/mapper-unione.json
$KC get clients/$ID_WEB/protocol-mappers/models -r tarots --fields name,protocolMapper   # «unione da confermare»
# 5. Verifica: il passo sicuro nel flusso, e nessun «idp-auto-link» (gli spazi del nome vanno codificati).
$KC get "authentication/flows/primo%20accesso%20con%20unione%20degli%20account/executions" -r tarots \
  --fields providerId,requirement
```

**Immagine**: il tema ha testi nuovi (email già registrata, credenziali non valide, conferma del collegamento) e il
passo `tarots-unione-sicura` (compilato dentro il Dockerfile, senza Maven) → `tarots-keycloak:v6` (manifest e
`deploy/keycloak/Dockerfile`), costruita in locale e importata in containerd come le altre. Nel log di Keycloak
all'avvio c'è un avviso `KC-SERVICES0047 … implementing the internal SPI authenticator`: è normale per ogni passo di
autenticazione aggiunto. **Migrazioni** dell'API: `b1d4f6a8c2e3` (scheda anagrafica, posizione attuale, provenienza)
e `d3f6b8c0e2a5` (unione da confermare), applicate dal pod.

### Prerequisiti presso i provider

- **SMTP del realm**: in produzione `smtpServer` è vuoto. Senza, non partono «Password dimenticata?» né la verifica
  dell'email (chi entra col social su un account mai verificato non resta più fermo: l'email la verifica il passo
  sicuro). Realm settings →
  Email (host `mail.tadamoo.com`, 465 SSL, `noreply@tarots.chat`, password `smtp-password` di `tarots-secrets`).
- **Google, data di nascita e sesso**: Google Cloud → API e servizi → Libreria → **People API** abilitata; schermata
  di consenso con gli ambiti `user.birthday.read` e `user.gender.read`; **verifica dell'app** (ambiti sensibili:
  informativa privacy pubblica, video della schermata di consenso, giorni o settimane). Poi, nella console, «Chiedi
  anche data di nascita e sesso» su Google. Prima della verifica lasciarla spenta: Google mostrerebbe a chi entra
  l'avviso «app non verificata». Nome, cognome, lingua e foto non richiedono niente.
- **Facebook, compleanno, sesso e città**: Meta for Developers → Revisione app → autorizzazioni `user_birthday`,
  `user_gender`, `user_location` (**App Review**, con screencast e motivazione: servono alle letture). Poi la casella
  nella console su Facebook. Finché non sono approvate, chi entra non le concede e si importa solo nome, cognome e foto.
- GitHub, Microsoft, LinkedIn: niente da fare; danno ciò che danno (nome, foto, a volte città o lingua). X: niente
  (OAuth 1.0a, il backend non ha la chiave per firmare). Apple: solo nome ed email del primo accesso.

### Account doppi

Gli account nati **prima** dell'unione (o da X/Microsoft con la stessa email di un altro) restano separati: nessuna
fusione automatica, perché due account sono due storie (letture, crediti, acquisti, memoria). La console li elenca
(«Accesso con i social» → «Account con la stessa email»: id, `sub`, data, letture). Per unirli, deciso quale tenere
(di solito quello con più storia, «A»; l'altro è «B»):

1. **Keycloak**: Utenti → B → Identity provider links: annotare i social collegati e scollegarli; Utenti → A →
   Identity provider links → collegare gli stessi (oppure la persona entra con quel social dopo il passo 2: il flusso
   lo collega da solo ad A). Poi disattivare (non cancellare) B.
2. **App** (`kubectl -n tadamoo exec -it deploy/postgresql -- psql -U postgres tarots`), in una transazione,
   spostare ciò che serve da B ad A e chiudere B:
   ```sql
   begin;
   update readings set owner_id = :A where owner_id = :B;
   update credit_ledger set user_id = :A where user_id = :B;    -- i crediti seguono la persona
   update users set deleted_at = now() where id = :B;
   commit;
   ```
   Le altre tabelle (`user_memories`, `ordini`, gli indirizzi) si spostano allo stesso modo se servono; gli abbonamenti no
   (uno per utente: si tiene quello di A). Annotare nel registro chi ha unito cosa.

## Console di Keycloak

Non è pubblica. Da un terminale sul server:

```bash
kubectl -n tarots port-forward deploy/tarots-keycloak 8081:8080
# poi http://localhost:8081/auth/admin (utente `admin`, password in tarots-secrets)
```
