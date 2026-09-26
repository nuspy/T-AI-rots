# Deploy su k3s (tadamoo.com)

`tarots.yaml` mette TAROTS chat nel namespace `tarots` del cluster k3s di
tadamoo.com, sotto **un solo dominio**, `tarots.tadamoo.com`:

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
docker build --provenance=false -f deploy/Dockerfile.backend -t tarots-api:v2 .
docker build --provenance=false -f deploy/Dockerfile.next --build-arg APP=frontend \
  --build-arg NEXT_PUBLIC_API_URL=https://tarots.tadamoo.com/api \
  --build-arg NEXT_PUBLIC_KEYCLOAK_URL=https://tarots.tadamoo.com/auth \
  --build-arg NEXT_PUBLIC_KEYCLOAK_REALM=tarots \
  --build-arg NEXT_PUBLIC_KEYCLOAK_CLIENT_ID=tarot-frontend \
  --build-arg NEXT_PUBLIC_AUTH_DISABLED=false \
  --build-arg NEXT_PUBLIC_SITE_URL=https://tarots.chat \
  --build-arg NEXT_PUBLIC_CARD_EXT=webp -t tarots-web:v2 .
docker build --provenance=false -f deploy/Dockerfile.next --build-arg APP=admin \
  --build-arg NEXT_PUBLIC_API_URL=https://tarots.tadamoo.com/api \
  --build-arg NEXT_PUBLIC_KEYCLOAK_URL=https://tarots.tadamoo.com/auth \
  --build-arg NEXT_PUBLIC_KEYCLOAK_REALM=tarots \
  --build-arg NEXT_PUBLIC_KEYCLOAK_CLIENT_ID=tarot-admin \
  --build-arg NEXT_PUBLIC_AUTH_DISABLED=false \
  --build-arg NEXT_PUBLIC_BASE_PATH=/admin -t tarots-admin:v2 .
docker build -f deploy/keycloak/Dockerfile -t tarots-keycloak:v1 deploy/keycloak
docker save tarots-api:v2 | k3s ctr -n k8s.io images import -   # e così le altre

# 3. segreti e realm (non stanno nel repository)
kubectl create ns tarots
kubectl -n tarots create secret generic tarots-secrets \
  --from-literal=db-password=... \
  --from-literal=database-url='postgresql+psycopg://tarots:...@postgresql.tadamoo.svc.cluster.local:5432/tarots' \
  --from-literal=keycloak-admin-password=... \
  --from-literal=api-client-secret=... \
  --from-literal=condivisione-sale="$(openssl rand -hex 24)"
# Su un Secret che esiste già, la sola chiave nuova (senza, l'API non parte):
#   kubectl -n tarots patch secret tarots-secrets --type merge \
#     -p "{\"stringData\":{\"condivisione-sale\":\"$(openssl rand -hex 24)\"}}"
kubectl -n tarots create configmap tarots-realm --from-file=realm.json=deploy/keycloak/realm-tarots.prod.json

# 4. tutto il resto
kubectl apply -f deploy/k8s/tarots.yaml

# 5. il seed: piani e utenti di prova, con TAROT_CREDITI_UTENTE_DI_PROVA crediti a testa
kubectl -n tarots exec deploy/tarots-api -- python -m tarot_core.tools.seed
```

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

`https://tarots.tadamoo.com/admin`, con il login Keycloak del client
`tarot-admin` (PKCE). Il collegamento «Admin» compare nella testata del sito
solo a chi ha il ruolo `admin`. Nel realm il client deve avere il redirect
`https://tarots.tadamoo.com/admin/*` e `webOrigins` `["+"]` (o l'origine
`https://tarots.tadamoo.com`): un `webOrigins` con il percorso `/admin` non è
un'origine e il CORS del login fallisce. Il generatore del realm ora scrive `+`.

## Instradamento (nginx-proxy-manager)

Serve un proxy host per `tarots.tadamoo.com` verso il ClusterIP di
`tarots-gateway` (`kubectl -n tarots get svc tarots-gateway`), porta 8080, con
certificato Let's Encrypt e Force SSL. Dall'API di NPM (2.15, sul server:
`http://127.0.0.1:81/api`, login con `POST /tokens`):

1. `POST /nginx/certificates` con `{"provider":"letsencrypt","domain_names":["tarots.tadamoo.com"],"meta":{"dns_challenge":false}}`
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

## Console di Keycloak

Non è pubblica. Da un terminale sul server:

```bash
kubectl -n tarots port-forward deploy/tarots-keycloak 8081:8080
# poi http://localhost:8081/auth/admin (utente `admin`, password in tarots-secrets)
```
