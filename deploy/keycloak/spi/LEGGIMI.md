# Provider Keycloak di TAROTS

Un solo passo di autenticazione, `tarots-unione-sicura` (`src/chat/tarots/keycloak/`), usato nel flusso «primo accesso
con unione degli account» al posto di «Automatically set existing user» (`idp-auto-link`).

Collega l'identità social all'utente che ha già la stessa email. Se quell'utente **non** aveva l'email verificata
(chiunque poteva averlo creato scrivendo l'email di un altro), prima di collegare gli toglie password, OTP e chiavi di
sicurezza, i collegamenti con i social che non garantiscono l'email, le sessioni (anche offline) e i token già emessi;
mette nome e cognome del social e segna l'email come verificata. Cosa ha tolto lo mette in una nota della sessione
(`tarots_unione` = `istante|creato|credenziali|social`), che il mapper «unione da confermare» del client
`tarot-frontend` copia nel token d'accesso: il sito chiede alla persona se l'account era suo
(`backend/tarot_core/tarot/unione_account.py`).

## Compilazione

Dentro `deploy/keycloak/Dockerfile` (stadio `spi`): `javac` contro i jar della stessa immagine Keycloak, niente Maven.
Il jar finisce in `/opt/keycloak/providers/` prima di `kc.sh build`.

A mano, per un Keycloak portatile di prova (stessa versione):

```bash
KC=/percorso/keycloak-26.0.8
mkdir -p out && javac -proc:none --release 17 -d out -cp "$KC/lib/lib/main/*:$KC/lib/lib/boot/*" \
  src/chat/tarots/keycloak/*.java && cp -r src/META-INF out/ && jar cf "$KC/providers/tarots-keycloak-spi.jar" -C out .
```

(`-proc:none`: i jar di Keycloak contengono processori di annotazioni che, senza, falliscono la compilazione.)

## Aggiornare Keycloak

Il passo usa API interne (`AbstractIdpAuthenticator`, `UserSessionProvider`): a ogni cambio di versione di Keycloak va
ricompilato e riprovato (il Dockerfile lo ricompila da sé; un errore di compilazione ferma la build dell'immagine, ed è
voluto).
