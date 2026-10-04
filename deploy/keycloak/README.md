# Realm di sviluppo

Derivato da quello di Personalities: stessi ruoli, stessi flussi, client rinominati.

`realm-tarots.json` viene importato all'avvio di Keycloak (`start-dev
--import-realm`). Contiene i due ruoli della specifica, i client di frontend,
console e API, e due utenti di prova.

**Non usare questo file in produzione.** Le password sono note e il segreto del
client `tarot-api` è un segnaposto.

## Perché non ci sono commenti nel JSON

Keycloak rifiuta le proprietà che non riconosce: una chiave `_commento` fa
fallire l'import con `Unrecognized field`, e il container resta in riavvio
continuo. Le note stanno qui.

## Contenuto

| Elemento | Nota |
|---|---|
| `user`, `admin` | i due ruoli di realm della specifica |
| `default-roles-tarots` | composito, assegna `user` a ogni nuovo iscritto |
| `tarot-frontend` | client pubblico, PKCE S256, redirect su :3000 |
| `tarot-admin` | console di amministrazione, :3001 |
| `tarot-api` | client confidenziale, solo service account |
| `test@tarots.local` / `test` | utente di prova, **1000 crediti** dopo il seed |
| `admin@tarots.local` / `admin` | utente con ruolo `admin`, 1000 crediti |

Gli utenti di prova hanno un `id` fisso (`11111111-…`, `22222222-…`): è il
`sub` dei loro token, e `python -m tarot_core.tools.seed` crea le righe con lo
stesso `sub` e accredita i 1000 crediti. Al primo login l'utente li trova già.

## Tema grafico (login e account)

Il tema `tarots` (`deploy/keycloak/themes/tarots/`) veste le pagine di Keycloak nello stile della **v2** del sito
(`frontend/app/(v2)/v2.css`): carta chiara e prugna, ottone e verderame, Libre Baskerville per i titoli e DM Sans per
l'interfaccia, marchio «✦ TAROTS chat».

- `login/template.ftl` — il guscio di ogni pagina (testata prugna con marchio e lingua, foglio di carta con l'ombra
  d'ottone, quinta prugna col motto solo da 960px, piede). Riscrive il layout di `keycloak.v2` **con la stessa firma**
  (`registrationLayout` e le sezioni `header`, `show-username`, `form`, `info`, `socialProviders`): le pagine di base
  (login, registrazione, password dimenticata/da aggiornare, configurazione e richiesta dell'OTP, scelta del metodo,
  errori, info, pagina scaduta…) restano quelle di Keycloak e vi si inseriscono da sole. **Aggiornando Keycloak a una
  versione maggiore** va riconfrontato con il `template.ftl` di `keycloak.v2` di quella versione.
- `login/social-providers.ftl` — i pulsanti «Continua con …», uno per riga, con l'icona del provider. Keycloak passa
  solo i provider **accesi**: si accendono dalla console («Accesso con i social»), senza ricostruire l'immagine.
- `login/resources/css/tarots-v7.css` — ridisegna il markup PatternFly 5 delle pagine (token globali e variabili dei
  componenti) e il guscio. Mobile-first, verificato a 360, 390 e 1280 px (nessuno scroll orizzontale, bersagli ≥44px).
- `login/resources/fonts/` — i caratteri serviti dal tema (OFL), non da Google Fonts: la pagina d'accesso non manda
  l'IP di chi entra a terzi.
- `login/messages/messages_{en,it,hu,ru,uk,es}.properties` — i testi nuovi del tema (`tarots…`); tutti gli altri sono
  quelli di Keycloak, già tradotti. Il realm offre le stesse lingue (`internationalizationEnabled`,
  `supportedLocales`), e il sito passa la sua con `ui_locales`: chi naviga in ungherese trova il login in ungherese.
- `account/` — la console dell'account (`{realm}/account/`, dove si gestisce la 2FA): `parent=keycloak.v3`, solo i
  colori. Prima era `parent=keycloak.v2`, che per l'account in Keycloak 26 **non esiste**: il tema falliva e Keycloak
  usava in silenzio quello di serie.
- `Dockerfile` — `COPY themes/tarots ...` avviene **prima** di `kc.sh build`: Keycloak 26 ottimizzato include i temi
  nella fase di build. Un tema cambiato vuol dire **un'immagine nuova** (tag nel manifest: `tarots-keycloak:v6`, per i testi dell'account unico).

**Verifica**: il tema è stato provato su un Keycloak 26.0.8 locale (`kc.sh start-dev` con la cartella del tema
collegata e il realm di sviluppo): login, errore di credenziali, registrazione, password dimenticata, configurazione
dell'OTP, pagina d'errore, in it/hu/ru/es, a 360/390/1280 px.

## Identity provider (accesso con i social)

Google, Facebook, Microsoft, GitHub, LinkedIn (OpenID Connect) e X/Twitter sono provider integrati di Keycloak 26.0;
Apple no (OIDC generico, vedi sotto). Nel realm sono tutti **spenti**, con credenziali segnaposto. Si configurano
dalla console del sito, **Accesso con i social**: per ogni provider client id, segreto e acceso/spento; il backend
(`backend/tarot_core/auth/provider_sociali.py`, `api/routers/admin_accesso_social.py`) li scrive in Keycloak via
Admin API. I segreti **non** passano dal nostro database: restano solo in Keycloak. La pagina mostra l'indirizzo di
ritorno da registrare presso il provider:

    https://tarots.chat/auth/realms/tarots/broker/<alias>/endpoint

**Instagram** non c'è: Keycloak 26.0 ha ancora un provider `instagram`, ma usa la Instagram Basic Display API, che Meta
ha chiuso il 4 dicembre 2024. Chi usa Instagram entra con Facebook.

`trustEmail` è spento per Microsoft (un account personale può avere un'email non verificata) e per X (che l'email la
dà solo se l'app la chiede): chi entra da lì conferma l'email da noi.

## Riapplicare il realm dopo una modifica

L'import avviene solo alla prima creazione del database interno. Per rileggerlo:

    docker compose down keycloak
    docker volume rm tarots_keycloak_data 2>/dev/null || true
    docker compose up -d keycloak

## `tarot-test` e il pubblico del token

Il client dei test automatici porta un mappatore di *audience* verso
`tarot-api`. Senza, l'API rifiuta i suoi token con «token emesso per
['tarot-test']»: la verifica del pubblico è voluta — un token buono per
un client non deve valere per un altro — ma un client di prova che non
riesce a parlare con ciò che deve provare non serve a niente.

## Login persistente (fino al logout)

Chi entra nel sito o nella console resta dentro — anche chiudendo il browser e riavviando la macchina — finché non fa
logout. Il meccanismo è il **token offline** di Keycloak:

1. il sito e la console chiedono lo scope `offline_access` (`SCOPE_PERSISTENTE` in `frontend/lib/sessione.tsx` e
   `admin/lib/sessione.tsx`): il token di rinnovo che ricevono è *offline*, cioè non legato alla sessione del browser
   (il cookie SSO, che continua a scadere dopo 30 minuti di inattività o 10 ore);
2. i token stanno in `localStorage`; all'apertura, se il token d'accesso è scaduto ma c'è il token offline, lo si usa
   una volta (`useRipresaSessione`) e si è di nuovo dentro senza vedere Keycloak; a pagina aperta il rinnovo
   automatico fa il resto;
3. il token offline scade solo dopo `offlineSessionIdleTimeout` **senza alcun uso** — 365 giorni, e ogni rinnovo
   lo fa ripartire — mentre `offlineSessionMaxLifespanEnabled` è spento (nessuna scadenza assoluta). Le due durate si
   cambiano dalla console, «Impostazioni → Login persistente», che le scrive su Keycloak e le rilegge da lì;
4. **logout**: prima la revoca del token offline (`revokeTokens(["refresh_token"])`: chiudere la sessione del
   browser in Keycloak non lo invalida), poi il logout normale. Un amministratore può revocare le sessioni offline di
   un utente dalla console di Keycloak (Users → utente → Sessions).

**Perché non «Ricordami»** (`rememberMe` con durate lunghe): dipende da una casella che l'utente deve spuntare, lega
la durata al cookie SSO del browser e alle sessioni online; il token offline è il meccanismo che Keycloak prevede per
«resta connesso finché non esci», e si revoca per utente. `rememberMe` è spento: una casella che non cambia nulla
confonderebbe. Il costo accettato: il token offline è in `localStorage`, e uno script che lo rubasse (XSS) resterebbe
dentro finché non viene revocato.

Il ruolo `offline_access` è fra i ruoli predefiniti (`default-roles-tarots`) e lo scope `offline_access` è opzionale
per i client: niente consenso da chiedere (`consentRequired` è spento). **Chi non ha il ruolo non entra più**
(«Offline tokens not allowed for the user or client»): gli utenti importati con `realmRoles` espliciti non ricevono
i ruoli predefiniti, per questo gli utenti di prova qui hanno `default-roles-tarots` scritto a mano. Per il realm di
produzione c'è il ciclo `kcadm` in `deploy/k8s/LEGGIMI.md`. Provato su Keycloak 26.0.8 locale: token di rinnovo di
tipo `Offline`, che rinnova anche dopo la fine della sessione del browser, e che dopo la revoca è rifiutato
(`invalid_grant`); la revoca dal browser ha il CORS giusto.

# Realm di produzione

`realm-tarots.prod.json` è lo stesso realm senza utenti di prova, senza
il client `tarot-test` e senza indirizzi `localhost`, con in più:

| | |
|---|---|
| 2FA per gli amministratori | OTP obbligatorio per chi ha il ruolo `admin`, anche quando entra con un provider esterno |
| 2FA per gli utenti | facoltativa: chi la attiva dal proprio account la usa, gli altri no |
| provider social | Google, Facebook, Microsoft, Apple, GitHub, LinkedIn, X — **spenti**: si accendono dalla console (o, a un import nuovo, dall'ambiente) |
| protezione brute force | blocco progressivo dopo 8 tentativi, fino a 15 minuti |
| password | almeno 6 caratteri, diversa da nome ed email, non una delle ultime 3 |
| email verificata | obbligatoria alla registrazione: serve l'SMTP |
| HTTPS | richiesto per le richieste esterne (`sslRequired: external`) |

## Variabili d'ambiente

Keycloak sostituisce i segnaposto `${...}` all'import (`--import-realm`); il
file non contiene segreti.

| Variabile | A cosa serve |
|---|---|
| `KC_URL_WEB`, `KC_URL_ADMIN` | gli indirizzi del sito e della console, per il ritorno dal login (in Kubernetes li mette l'overlay) |
| `KC_API_CLIENT_SECRET` | segreto del client confidenziale `tarot-api` |
| `KC_SMTP_HOST`, `KC_SMTP_PORT`, `KC_SMTP_FROM`, `KC_SMTP_USER`, `KC_SMTP_PASSWORD` | invio delle email di verifica e di recupero |
| `KC_GOOGLE_ENABLED`, `KC_GOOGLE_CLIENT_ID`, `KC_GOOGLE_CLIENT_SECRET` | accesso con Google |
| `KC_FACEBOOK_ENABLED`, `KC_FACEBOOK_CLIENT_ID`, `KC_FACEBOOK_CLIENT_SECRET` | accesso con Facebook |
| `KC_APPLE_ENABLED`, `KC_APPLE_CLIENT_ID`, `KC_APPLE_CLIENT_SECRET` | accesso con Apple |
| `KC_MICROSOFT_*`, `KC_GITHUB_*`, `KC_LINKEDIN_*`, `KC_TWITTER_*` | gli altri provider, stessi tre nomi |

`KC_<PROVIDER>_ENABLED` vale `false` se manca: un provider senza credenziali
non compare nella pagina di accesso. Per accenderlo si impostano le tre
variabili e si registra presso il provider l'indirizzo di ritorno:

    https://<dominio di Keycloak>/realms/tarots/broker/<google|facebook|apple>/endpoint

## Come funziona la 2FA

Il flusso del browser è `browser con 2FA amministratori`, copia di quello
predefinito con due modifiche:

1. il sottoflusso *Conditional OTP* — l'OTP per chi l'ha attivato — esclude
   gli amministratori, o a loro verrebbe chiesto due volte;
2. un sottoflusso nuovo, condizionato al ruolo `admin`, chiede sempre l'OTP.
   Un amministratore che non l'ha ancora configurato viene portato a farlo al
   primo accesso, con il QR code da leggere con un'app (Google Authenticator,
   Microsoft Authenticator, FreeOTP).

### La 2FA facoltativa degli utenti, dal sito

Il realm non cambia: chi ha configurato l'OTP lo usa (sottoflusso *Conditional OTP*), gli altri
no. Il sito la **propone** (`frontend/lib/sicurezza.ts`, `app/componenti/promemoria-2fa.tsx`, sezione
«Sicurezza dell'account» del profilo):

- **Attivarla**: `Sessione.attiva2fa()` rifà la richiesta di accesso con `kc_action=CONFIGURE_TOTP`
  (*application initiated action* di Keycloak): compare il QR code, si inserisce il primo codice e si
  torna al profilo. Richiede che l'azione richiesta *Configure OTP* sia abilitata nel realm (lo è).
- **Sapere se è attiva**: `GET {realm}/account/credentials` col token dell'utente (API dell'account:
  il token ha l'audience `account` perché i ruoli predefiniti del realm includono `account`). Se non
  risponde lo stato è «non disponibile» e il sito lo dice, senza indovinare. Il client `tarot-frontend`
  ha già i `webOrigins` necessari per la richiesta dal browser.
- **Il promemoria**: una volta per sessione del browser, a chi non l'ha attivata; «Più tardi» lo
  chiude fino al prossimo ingresso, la casella «Non mostrare più» salva `users.promemoria_2fa = false`
  (vale su ogni dispositivo) e si riaccende dal profilo. Non compare sulle pagine condivise.
- **Gestirla** (togliere un dispositivo, aggiungerne un altro): la console dell'account di Keycloak,
  `{realm}/account/`.

Non è provata contro un Keycloak vero (niente Docker in locale): il sito è stato provato con un realm
finto che risponde a discovery, accesso, token e `/account/credentials`. Da verificare sul server: (1) dal
profilo, «Attiva» porta alla configurazione dell'OTP e torna a `/profilo`; (2) dopo, lo stato diventa
«Attiva» e il promemoria non compare più; (3) con l'OTP attivo l'accesso chiede il codice.

Il flusso `2FA amministratori dopo accesso esterno` è il *post login* di tutti i
provider: senza, un amministratore che entra con Google salterebbe il secondo
fattore, perché il flusso del browser finisce al reindirizzamento. La console lo
assegna anche ai provider che crea («Accesso con i social»), se il realm lo ha.

## Apple

Apple non ha un provider integrato in Keycloak ed è configurato come OIDC
generico. Il suo `client_secret` non è una stringa fissa ma un JWT firmato
(ES256) con la chiave privata dell'account sviluppatore, valido **al più sei
mesi**: va rigenerato prima della scadenza, o l'accesso con Apple smette di
funzionare senza preavviso.

**Dalla v9 (Fase 6) lo firma il backend**, senza estensioni di terzi nell'immagine:
la console («Accesso con i social» → Apple) tiene Team ID, Key ID, Services ID e
la chiave `.p8` cifrata, firma il JWT e lo scrive nell'identity provider `apple`
via Admin API (`backend/tarot_core/tarot/accesso_apple.py`); il CronJob
`tarots-apple-segreto` lo rinnova ogni mese quando ne mancano meno di 75 giorni.
`KC_APPLE_CLIENT_SECRET` serve solo a un import nuovo del realm. Le app passano
da Keycloak nel browser di sistema: per Apple è un accesso web con lo stesso
Services ID (non serve il Bundle ID). Apple manda il nome solo al primo accesso
(`user` del form_post) e l'OIDC generico lo ignora: lo chiede il profilo del sito.

## Il client delle app (`tarot-mobile`)

Pubblico (un'app non custodisce segreti), solo codice + **PKCE S256 obbligatorio**,
ritorno `chat.tarots.app:/oauth2redirect` (anche dopo il logout), niente password
diretta né flusso implicito, il mapper `tarots_unione` come `tarot-frontend`;
`offline_access` arriva dagli ambiti facoltativi predefiniti del realm. L'app
sceglie il social con `kc_idp_hint=google` (Android) o `apple` (iOS). Sul realm
già vivo lo crea la console (App mobili → «Prepara l'accesso dall'app») con
l'**importazione parziale** del realm: `POST /clients` vorrebbe `manage-clients`,
che l'account di servizio non ha; `partialImport` basta `manage-realm` (provato
su Keycloak 26.0.8).

Il collegamento di un social a un account esistente dal profilo del sito usa il
*client-initiated account linking* (`/realms/tarots/broker/{alias}/link`), che
26.0 supporta; l'azione `kc_action=idp_link` arriva solo nelle versioni
successive (26.0.8 risponde 400). Un social già collegato a un altro utente si
ferma sulla pagina d'errore di Keycloak: il tema ridefinisce il messaggio
`identityProviderAlreadyLinkedMessage` con il rimedio (il codice dell'app).

## Rigenerare il file

Il file si genera, non si scrive a mano: se un realm dichiara flussi di
autenticazione Keycloak non crea più quelli predefiniti, e un file con il solo
flusso 2FA importerebbe un realm senza recupero della password né
registrazione. Lo script costruisce i flussi su un'istanza usa-e-getta ed
esporta il realm intero:

    docker run -d --name kc-genera -p 8181:8080 -e KC_BOOTSTRAP_ADMIN_USERNAME=admin \
        -e KC_BOOTSTRAP_ADMIN_PASSWORD=genera -e KC_DB=dev-mem \
        quay.io/keycloak/keycloak:26.0 start-dev
    python deploy/keycloak/strumenti/genera_realm_prod.py --password genera
    docker rm -f kc-genera

Va rifatto dopo ogni modifica al realm di sviluppo che debba arrivare in
produzione.

### L'account di servizio di `tarot-api`

L'utente di servizio `service-account-tarot-api` ha tre ruoli client di `realm-management`, e solo quelli:

```json
"clientRoles": { "realm-management": ["manage-realm", "manage-identity-providers", "manage-users"] }
```

- `manage-realm` — la console cambia le durate della sessione offline (login persistente) e crea il flusso che unisce
  gli account;
- `manage-identity-providers` — la console configura l'accesso con i social;
- `manage-users` — dopo l'unione con un account dall'email mai verificata, la persona sceglie una password nuova
  (`PUT /users/{id}/reset-password`, solo per sé stessa: `api/routers/profile.py`, `POST /me/unione`).

L'API li usa col grant client-credentials (`backend/tarot_core/auth/keycloak_admin.py`): le servono
`TAROT_KEYCLOAK_CLIENT_SECRET` (nel manifest dal Secret `tarots-secrets`, chiave `api-client-secret`, la stessa di
`KC_API_CLIENT_SECRET`). L'esportazione parziale non contiene utenti: lo script (`account_di_servizio()`) aggiunge
quest'unico utente, preso dal realm di sviluppo, al file di produzione. **Verificato** su Keycloak 26.0.8 locale:
il file si importa, il token client-credentials legge e scrive realm e provider, e non legge gli utenti (403).
In un realm **già importato** i ruoli si aggiungono con `kcadm` (vedi `deploy/k8s/LEGGIMI.md`).

## Verifica manuale prima del primo avvio

1. Importato il file su un'istanza di prova, entrare nella console come
   amministratore: al primo accesso compare la configurazione dell'OTP.
2. Entrare come utente senza OTP: nessun secondo fattore richiesto.
3. Con `KC_GOOGLE_ENABLED=true` e le credenziali, la pagina di accesso mostra
   Google; senza, non lo mostra.
