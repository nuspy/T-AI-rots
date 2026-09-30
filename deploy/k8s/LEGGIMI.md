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

# 2. immagini: si costruiscono SUL SERVER (mai sul PC di sviluppo) e si importano
#    in containerd, niente registry. Sorgenti: tar di backend, frontend, admin, deploy.
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
  --from-literal=condivisione-sale="$(openssl rand -hex 24)" \
  --from-literal=llm-provider-key="$(python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"
# Su un Secret che esiste già, la sola chiave nuova (senza, l'API non parte):
#   kubectl -n tarots patch secret tarots-secrets --type merge \
#     -p "{\"stringData\":{\"condivisione-sale\":\"$(openssl rand -hex 24)\"}}"
# `llm-provider-key` cifra a riposo le chiavi dei fornitori LLM aggiunti dalla console («Modelli»): senza, l'API non
# parte in produzione (vedi `Settings.validate_production`). **Cambiarla dopo che dei fornitori sono già stati
# salvati li rende illeggibili** (tornano «nessuna chiave»): si genera una volta sola, all'inizio.
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
   `NEXT_PUBLIC_SITE_URL`), quindi `tarots-web` e `tarots-admin` **si ricostruiscono sul server** (mai in locale) con i
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

Nuovo tag nelle `docker build` (sul server) e in `tarots.yaml`, poi
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
  giorni (idempotente) e cancellazione di sessioni ed eventi oltre i 25 mesi.
  Prova: `kubectl -n tarots create job --from=cronjob/tarots-analytics-notte prova-analytics`.
- **Rapporto settimanale** (`tarots-rapporto-settimanale`, lunedì 0:30): email a chi è in elenco in
  console → Analytics → Rapporti, via Stalwart (`mail.tadamoo.com:465`, `noreply@tarots.chat`, la
  password è `smtp-password` in `tarots-secrets`, la stessa di Keycloak). Un solo tentativo
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

## Console di Keycloak

Non è pubblica. Da un terminale sul server:

```bash
kubectl -n tarots port-forward deploy/tarots-keycloak 8081:8080
# poi http://localhost:8081/auth/admin (utente `admin`, password in tarots-secrets)
```
