"""L'API amministrativa di Keycloak: sessione persistente e accesso con i social, dalla console.

Riusa il client `tarot-api` esistente (`serviceAccountsEnabled: true`) invece di crearne uno nuovo: al suo
account di servizio bastano due ruoli client di `realm-management` (vedi `deploy/keycloak/README.md`):

- `manage-realm` — le durate della sessione offline (login persistente, `imposta_sessione_persistente`), il
  flusso che unisce gli account al primo accesso social (`assicura_flusso_unione`) e, con l'importazione parziale,
  il client delle app (`assicura_client_mobile`, v9 Fase 6);
- `manage-identity-providers` — i provider social (`provider_identita`, `salva_provider`), compreso il segreto di
  Apple firmato dal backend (`tarot/accesso_apple.py`);
- `manage-users` — la password che la persona sceglie dopo un'unione con un account mai verificato
  (`imposta_password`, solo per sé stessa: vedi `api/routers/profile.py`); gli account creati a mano dalla console
  (`crea_utente`, `POST /admin/users`, e `cancella_utente` se poi il database fallisce); la lingua dell'utente
  (`imposta_lingua`); le identità social spostate con il codice di collegamento (`identita_federate`,
  `collega_identita`, `scollega_identita`, `disattiva_utente`: `tarot/collega_identita.py`).

Il segreto arriva da `TAROT_KEYCLOAK_CLIENT_SECRET`, che nel cluster viene dalla stessa chiave del Secret
(`tarots-secrets/api-client-secret`) da cui Keycloak legge `KC_API_CLIENT_SECRET` all'import del realm.

**Perché non un client separato.** Un secondo client confidenziale con lo stesso scopo (parlare con
l'API di Keycloak da dentro il backend) sarebbe una credenziale in più da custodire per lo stesso
livello di fiducia — questo processo già ne ha una (`keycloak_client_secret`), e un token ottenuto
con quella non è più privilegiato di quanto lo sia il processo stesso.
"""
from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import httpx

from ..settings import Settings, get_settings

logger = logging.getLogger(__name__)


class KeycloakAdminError(Exception):
    """L'API amministrativa di Keycloak non ha accettato la richiesta, o non è raggiungibile."""

    def __init__(self, messaggio: str, stato: Optional[int] = None) -> None:
        super().__init__(messaggio)
        #: Il codice HTTP di Keycloak, quando c'è stata una risposta: un 403 vuol dire un ruolo che manca
        #: all'account di servizio, e chi chiama lo spiega meglio di un messaggio generico.
        self.stato = stato


class PasswordRifiutata(KeycloakAdminError):
    """La password non rispetta la politica del realm: `chiave` è quella del messaggio di Keycloak."""

    def __init__(self, chiave: str) -> None:
        super().__init__(f"password rifiutata: {chiave}", 400)
        self.chiave = chiave


class UtenteEsistente(KeycloakAdminError):
    """Esiste già un utente con quell'email (o nome utente) in Keycloak."""

    def __init__(self, email: str) -> None:
        super().__init__(f"esiste già un utente con l'email {email}", 409)


#: Il passo del flusso di unione che collega in sicurezza (`deploy/keycloak/spi`, `UnioneSicuraAuthenticatorFactory.ID`).
PASSO_UNIONE_SICURA = "tarots-unione-sicura"

#: Il client pubblico delle app Android e iOS (v9, Fase 6) e l'indirizzo a cui Keycloak le rimanda: lo schema è l'id
#: dell'app (`mobile/lib/auth/configurazione.dart`, AndroidManifest e Info.plist). Gli stessi valori nel realm di
#: sviluppo, in quello di produzione e in `client_mobile()`.
CLIENT_MOBILE = "tarot-mobile"
REDIRECT_MOBILE = "chat.tarots.app:/oauth2redirect"


def client_mobile() -> Dict[str, Any]:
    """`tarot-mobile` come nei realm (`deploy/keycloak/realm-tarots*.json`): pubblico (un'app installata non può
    custodire un segreto), solo il flusso con codice e PKCE S256 obbligatorio, niente password diretta né implicito.
    `offline_access` è fra gli ambiti facoltativi predefiniti del realm, che Keycloak assegna da sé a ogni client
    nuovo: l'app lo chiede e il suo token di rinnovo sopravvive alla chiusura. Il mapper `tarots_unione` porta nel
    token la nota dell'unione da confermare (`tarot/unione_account.py`), come per il sito."""
    return {
        "clientId": CLIENT_MOBILE,
        "name": "App TAROTS chat (Android e iOS)",
        "description": "Client pubblico delle app native: codice + PKCE S256 nel browser di sistema (AppAuth)",
        "enabled": True,
        "protocol": "openid-connect",
        "publicClient": True,
        "standardFlowEnabled": True,
        "implicitFlowEnabled": False,
        "directAccessGrantsEnabled": False,
        "serviceAccountsEnabled": False,
        "frontchannelLogout": False,
        "redirectUris": [REDIRECT_MOBILE],
        "webOrigins": [],
        "attributes": {
            "pkce.code.challenge.method": "S256",
            # Il logout dell'app (`endSession` di AppAuth) torna allo stesso indirizzo.
            "post.logout.redirect.uris": REDIRECT_MOBILE,
        },
        "protocolMappers": [{
            "name": "unione da confermare",
            "protocol": "openid-connect",
            "protocolMapper": "oidc-usersessionmodel-note-mapper",
            "consentRequired": False,
            "config": {
                "user.session.note": "tarots_unione",
                "claim.name": "tarots_unione",
                "jsonType.label": "String",
                "access.token.claim": "true",
                "id.token.claim": "false",
                "userinfo.token.claim": "false",
                "introspection.token.claim": "true",
            },
        }],
    }


class KeycloakAdmin:
    """Un token client-credentials, riusato finché non scade, e le chiamate all'Admin REST API."""

    def __init__(self, settings: Optional[Settings] = None, transport: Optional[httpx.AsyncBaseTransport] = None) -> None:
        self._settings = settings or get_settings()
        self._transport = transport
        self._token: Optional[str] = None
        #: Timestamp Unix oltre il quale il token va considerato scaduto: con un margine, non al
        #: secondo esatto — una richiesta partita un istante prima della scadenza non deve fallire.
        self._scade_a = 0.0

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=10.0, transport=self._transport)

    @property
    def _configurato(self) -> bool:
        return bool(self._settings.keycloak_client_secret)

    @property
    def _realm_admin(self) -> str:
        return f"{self._settings.keycloak_url.rstrip('/')}/admin/realms/{self._settings.keycloak_realm}"

    async def _token_valido(self) -> str:
        if self._token and time.time() < self._scade_a:
            return self._token
        if not self._configurato:
            raise KeycloakAdminError(
                "TAROT_KEYCLOAK_CLIENT_SECRET non impostato: il client-credentials grant non può partire"
            )

        url = f"{self._settings.keycloak_url.rstrip('/')}/realms/{self._settings.keycloak_realm}/protocol/openid-connect/token"
        try:
            async with self._client() as client:
                risposta = await client.post(url, data={
                    "grant_type": "client_credentials",
                    "client_id": self._settings.keycloak_client_id,
                    "client_secret": self._settings.keycloak_client_secret,
                })
        except httpx.HTTPError as exc:
            raise KeycloakAdminError(f"Keycloak non raggiungibile ({type(exc).__name__})") from exc
        if risposta.status_code >= 400:
            raise KeycloakAdminError(
                f"token client-credentials rifiutato ({risposta.status_code}): {risposta.text[:300]}",
                risposta.status_code,
            )

        corpo = risposta.json()
        self._token = corpo["access_token"]
        # Margine di 10 secondi: meglio richiederne uno nuovo un po' presto che
        # rischiare una scrittura sul realm con un token appena scaduto.
        self._scade_a = time.time() + max(int(corpo.get("expires_in", 60)), 0) - 10
        return self._token

    async def _chiama(
        self, metodo: str, percorso: str = "", *, json: Any = None, ammessi: tuple[int, ...] = (),
    ) -> httpx.Response:
        """Una chiamata all'Admin API del realm. `ammessi`: codici d'errore che non sono un errore per chi chiama
        (un 404 su un provider che non esiste ancora)."""
        token = await self._token_valido()
        try:
            async with self._client() as client:
                risposta = await client.request(
                    metodo, f"{self._realm_admin}{percorso}", json=json,
                    headers={"Authorization": f"Bearer {token}"},
                )
        except httpx.HTTPError as exc:
            raise KeycloakAdminError(f"Keycloak non raggiungibile ({type(exc).__name__})") from exc
        if risposta.status_code in ammessi:
            return risposta
        if risposta.status_code >= 400:
            raise KeycloakAdminError(
                f"{metodo} {percorso or '/'} rifiutata ({risposta.status_code}): {risposta.text[:300]}",
                risposta.status_code,
            )
        return risposta

    # ---- realm ------------------------------------------------------------------------------------

    async def leggi_realm(self) -> Dict[str, Any]:
        """La rappresentazione del realm: le durate vere stanno qui, non in una copia nel nostro database."""
        return (await self._chiama("GET")).json()

    async def imposta_sessione_persistente(self, *, inattivita_secondi: int, durata_massima_secondi: int) -> None:
        """Il login persistente è la **sessione offline** del realm (vedi `deploy/keycloak/README.md`).

        Il sito e la console chiedono lo scope `offline_access`: il loro refresh token è un token offline, che
        sopravvive alla chiusura del browser e al riavvio di Keycloak, e scade solo dopo `inattivita_secondi`
        senza alcun uso (ogni rinnovo lo fa ripartire) o, se `durata_massima_secondi` è più di zero, comunque
        dopo quel tempo dall'accesso. Con 0 la durata massima è spenta: si resta dentro fino al logout.

        Proprietà del realm, non di un client: valgono per `tarot-frontend` e `tarot-admin` insieme."""
        corpo: Dict[str, Any] = {
            "offlineSessionIdleTimeout": inattivita_secondi,
            "offlineSessionMaxLifespanEnabled": durata_massima_secondi > 0,
        }
        if durata_massima_secondi > 0:
            corpo["offlineSessionMaxLifespan"] = durata_massima_secondi
        await self._chiama("PUT", json=corpo)

    async def flussi(self) -> List[str]:
        """Gli alias dei flussi di autenticazione del realm (per sapere se esiste quello della 2FA dopo un
        accesso esterno)."""
        return [f.get("alias", "") for f in (await self._chiama("GET", "/authentication/flows")).json()]

    # ---- il flusso che unisce gli account -------------------------------------------------------------

    async def _esecuzioni(self, flusso: str) -> List[Dict[str, Any]]:
        return (await self._chiama("GET", f"/authentication/flows/{quote(flusso)}/executions")).json()

    async def _requisito(self, flusso: str, esecuzione: Dict[str, Any], valore: str) -> None:
        # Tutta la rappresentazione letta, col solo requisito cambiato: Keycloak 26 confronta anche la priorità, e
        # un corpo con il solo id la azzererebbe.
        await self._chiama(
            "PUT", f"/authentication/flows/{quote(flusso)}/executions", json={**esecuzione, "requirement": valore},
        )

    async def _aggiungi_passo(self, flusso: str, provider: str, requisito: str) -> Dict[str, Any]:
        await self._chiama(
            "POST", f"/authentication/flows/{quote(flusso)}/executions/execution", json={"provider": provider},
        )
        passo = [e for e in await self._esecuzioni(flusso) if e.get("providerId") == provider][-1]
        await self._requisito(flusso, passo, requisito)
        return passo

    async def assicura_flusso_unione(self) -> bool:
        """Il flusso del primo accesso social che unisce gli account (`FLUSSO_UNIONE`): lo crea se manca.
        Restituisce vero se l'ha creato adesso.

        È la ricetta di Keycloak «Automatically link existing first login flow», costruita da zero e non copiando
        `first broker login` (i nomi dei sottoflussi copiati cambiano da versione a versione):

        1. *Review Profile* (REQUIRED, solo se manca qualcosa): chi arriva da X senza email la scrive;
        2. un sottoflusso REQUIRED con due alternative: *Create User If Unique* (nessun utente con quell'email →
           lo crea) e, al posto di *Automatically set existing user*, il nostro `tarots-unione-sicura` (c'è già →
           collega a lui l'identità social; se la sua email non era verificata, prima gli toglie i vecchi accessi).
           Serve l'immagine `tarots-keycloak` che lo contiene (`deploy/keycloak/spi`): senza, Keycloak rifiuta il
           passo, il flusso a metà si cancella e l'unione resta spenta.

        Un flusso creato prima, con il collegamento di Keycloak, si aggiorna: il passo nuovo prende il posto del
        vecchio (vero anche allora come valore restituito).

        Crearlo richiede `manage-realm`, che l'account di servizio ha già (il login persistente). Se la costruzione
        si interrompe a metà, il flusso incompleto si cancella: un flusso a metà assegnato a un provider
        bloccherebbe ogni primo accesso."""
        from .provider_sociali import FLUSSO_UNIONE

        if FLUSSO_UNIONE in await self.flussi():
            return await self._aggiorna_collegamento()
        await self._chiama("POST", "/authentication/flows", json={
            "alias": FLUSSO_UNIONE, "providerId": "basic-flow", "topLevel": True, "builtIn": False,
            "description": "Primo accesso con un social: collega l'identità all'utente con la stessa email, o lo crea",
        })
        try:
            rivedi = await self._aggiungi_passo(FLUSSO_UNIONE, "idp-review-profile", "REQUIRED")
            await self._chiama("POST", f"/authentication/executions/{rivedi['id']}/config", json={
                "alias": "unione - rivedi il profilo se manca qualcosa",
                "config": {"update.profile.on.first.login": "missing"},
            })
            sotto = f"{FLUSSO_UNIONE} - crea o collega"
            await self._chiama("POST", f"/authentication/flows/{quote(FLUSSO_UNIONE)}/executions/flow", json={
                "alias": sotto, "type": "basic-flow",
                "description": "Crea l'utente se l'email è nuova, altrimenti collega l'identità a quello che c'è",
            })
            passo = next(e for e in await self._esecuzioni(FLUSSO_UNIONE) if e.get("displayName") == sotto)
            await self._requisito(FLUSSO_UNIONE, passo, "REQUIRED")
            await self._aggiungi_passo(sotto, "idp-create-user-if-unique", "ALTERNATIVE")
            await self._aggiungi_passo(sotto, PASSO_UNIONE_SICURA, "ALTERNATIVE")
        except (KeycloakAdminError, StopIteration, IndexError, KeyError) as exc:
            await self._cancella_flusso(FLUSSO_UNIONE)
            if isinstance(exc, KeycloakAdminError):
                raise
            raise KeycloakAdminError(f"flusso «{FLUSSO_UNIONE}» non costruito: risposta inattesa ({exc!r})") from exc
        logger.info("Creato il flusso «%s»", FLUSSO_UNIONE)
        return True

    async def _aggiorna_collegamento(self) -> bool:
        """Nel flusso che c'è già, il collegamento di Keycloak («idp-auto-link») diventa il nostro. Vero se cambia."""
        from .provider_sociali import FLUSSO_UNIONE

        sotto = f"{FLUSSO_UNIONE} - crea o collega"
        passi = await self._esecuzioni(sotto)
        if any(e.get("providerId") == PASSO_UNIONE_SICURA for e in passi):
            return False
        vecchi = [e for e in passi if e.get("providerId") == "idp-auto-link"]
        await self._aggiungi_passo(sotto, PASSO_UNIONE_SICURA, "ALTERNATIVE")
        for e in vecchi:
            await self._chiama("DELETE", f"/authentication/executions/{e['id']}", ammessi=(404,))
        logger.info("Flusso «%s»: collegamento sicuro al posto di quello di Keycloak", FLUSSO_UNIONE)
        return True

    async def _cancella_flusso(self, alias: str) -> None:
        try:
            for f in (await self._chiama("GET", "/authentication/flows")).json():
                if f.get("alias") == alias and f.get("id"):
                    await self._chiama("DELETE", f"/authentication/flows/{f['id']}", ammessi=(404,))
        except KeycloakAdminError:  # pragma: no cover - si segnala l'errore originale, non questo
            logger.warning("Flusso «%s» incompleto non cancellato: va tolto a mano dalla console di Keycloak", alias)

    # ---- utenti -----------------------------------------------------------------------------------

    async def imposta_password(self, utente_id: str, password: str) -> None:
        """La password di un utente, definitiva (non temporanea). Keycloak applica la sua politica: un rifiuto torna
        come `PasswordRifiutata` con la chiave del messaggio di Keycloak (es. `invalidPasswordMinLengthMessage`).
        La password non si scrive mai nei log né negli errori."""
        token = await self._token_valido()
        try:
            async with self._client() as client:
                risposta = await client.put(
                    f"{self._realm_admin}/users/{quote(utente_id)}/reset-password",
                    json={"type": "password", "value": password, "temporary": False},
                    headers={"Authorization": f"Bearer {token}"},
                )
        except httpx.HTTPError as exc:
            raise KeycloakAdminError(f"Keycloak non raggiungibile ({type(exc).__name__})") from exc
        if risposta.status_code == 400:
            try:
                chiave = str(risposta.json().get("error") or "")
            except ValueError:
                chiave = ""
            raise PasswordRifiutata(chiave or "invalidPasswordGenericMessage")
        if risposta.status_code >= 400:
            raise KeycloakAdminError(
                f"PUT /users/…/reset-password rifiutata ({risposta.status_code})", risposta.status_code,
            )

    async def crea_utente(self, email: str, password: str, *, nome: Optional[str] = None, lingua: str = "it") -> str:
        """Crea un utente a mano (console) con la password già impostata, e ne restituisce l'id (la `sub`).

        Il realm usa l'email come nome utente (`registrationEmailAsUsername`), quindi `username` è l'email. L'email
        si segna come verificata: la persona non l'ha scritta lei, e il messaggio di verifica non servirebbe a
        nessuno. La password è definitiva. Errori: `UtenteEsistente` (409), `PasswordRifiutata` (400 sulla
        password), altrimenti `KeycloakAdminError`. La password non si scrive mai nei log né negli errori."""
        corpo: Dict[str, Any] = {
            "username": email, "email": email, "enabled": True, "emailVerified": True,
            "attributes": {"locale": [lingua]},
            "credentials": [{"type": "password", "value": password, "temporary": False}],
        }
        if nome:
            corpo["firstName"] = nome
        token = await self._token_valido()
        try:
            async with self._client() as client:
                risposta = await client.post(
                    f"{self._realm_admin}/users", json=corpo, headers={"Authorization": f"Bearer {token}"},
                )
        except httpx.HTTPError as exc:
            raise KeycloakAdminError(f"Keycloak non raggiungibile ({type(exc).__name__})") from exc
        if risposta.status_code == 409:
            raise UtenteEsistente(email)
        if risposta.status_code == 400:
            try:
                chiave = str(risposta.json().get("error") or risposta.json().get("errorMessage") or "")
            except ValueError:
                chiave = ""
            # Con la password nel corpo, un 400 con la chiave `invalidPassword…` è la politica del realm.
            if chiave.startswith("invalidPassword"):
                raise PasswordRifiutata(chiave)
            raise KeycloakAdminError(f"POST /users rifiutata (400): {chiave[:200]}", 400)
        if risposta.status_code >= 400:
            raise KeycloakAdminError(f"POST /users rifiutata ({risposta.status_code})", risposta.status_code)
        posizione = risposta.headers.get("location", "")
        sub = posizione.rstrip("/").rsplit("/", 1)[-1]
        if not sub:
            raise KeycloakAdminError("POST /users: Keycloak non ha indicato l'id dell'utente creato")
        return sub

    async def chiudi_sessioni(self, utente_id: str) -> None:
        """Chiude ogni accesso dell'utente (GDPR, Fase 1: la richiesta di cancellazione dell'account).

        - `GET /users/{id}/sessions` e `DELETE /sessions/{sessione}` per ciascuna: le sessioni del browser;
        - `POST /users/{id}/logout`: le stesse in un colpo solo, con l'avviso ai client che hanno un URL
          amministrativo (se una sessione è sparita fra le due chiamate, non è un errore);
        - `DELETE /users/{id}/consents/{client}` per ogni client del sito (`keycloak_accepted_audiences`): revoca i
          token **offline** che il sito e la console tengono per il login persistente, che il logout da solo non
          tocca.

        Bastano i permessi `manage-users` dell'account di servizio. Un utente che non esiste più (404) non è un errore."""
        percorso = f"/users/{quote(utente_id)}"
        risposta = await self._chiama("GET", f"{percorso}/sessions", ammessi=(404,))
        if risposta.status_code == 404:
            return
        for sessione in risposta.json() or []:
            if sessione.get("id"):
                await self._chiama("DELETE", f"/sessions/{quote(str(sessione['id']))}", ammessi=(404,))
        await self._chiama("POST", f"{percorso}/logout", ammessi=(404,))
        for client in self._settings.keycloak_accepted_audiences:
            await self._chiama("DELETE", f"{percorso}/consents/{quote(client)}", ammessi=(404,))

    async def cancella_utente(self, utente_id: str) -> None:
        """Cancella l'utente in Keycloak (credenziali, social collegati, sessioni). Un 404 vuol dire che non c'è già
        più: va bene, la cancellazione è idempotente."""
        await self._chiama("DELETE", f"/users/{quote(utente_id)}", ammessi=(404,))

    async def leggi_utente(self, utente_id: str) -> Optional[Dict[str, Any]]:
        risposta = await self._chiama("GET", f"/users/{quote(utente_id)}", ammessi=(404,))
        return None if risposta.status_code == 404 else risposta.json()

    async def _riscrivi_utente(self, utente_id: str, cambia) -> bool:
        """Legge l'utente, applica `cambia` alla rappresentazione e la rimanda **intera**: in Keycloak 26 (profilo
        utente dichiarativo) un `PUT` parziale viene rifiutato perché mancano i campi obbligatori (l'email),
        verificato su un Keycloak 26.0.8. Vero se qualcosa è cambiato (se `cambia` restituisce falso non scrive)."""
        utente = await self.leggi_utente(utente_id)
        if utente is None:
            raise KeycloakAdminError("utente non trovato in Keycloak", 404)
        if not cambia(utente):
            return False
        # Campi in sola lettura che Keycloak calcola: rimandarli non serve.
        for campo in ("access", "federatedIdentities", "disableableCredentialTypes", "totp", "createdTimestamp"):
            utente.pop(campo, None)
        await self._chiama("PUT", f"/users/{quote(utente_id)}", json=utente)
        return True

    async def imposta_lingua(self, utente_id: str, lingua: str) -> bool:
        """L'attributo `locale` dell'utente (v9, Fase 6): Keycloak lo usa per le email che manda lui (verifica
        dell'indirizzo, password dimenticata) e per le sue pagine quando la richiesta non porta `ui_locales`. Vero se
        è cambiato. Basta `manage-users`."""

        def cambia(utente: Dict[str, Any]) -> bool:
            attributi = utente.get("attributes") or {}
            if attributi.get("locale") == [lingua]:
                return False
            utente["attributes"] = {**attributi, "locale": [lingua]}
            return True

        return await self._riscrivi_utente(utente_id, cambia)

    async def disattiva_utente(self, utente_id: str) -> None:
        """L'utente non può più entrare (resta, per poterlo ritrovare: l'amministratore lo cancella se vuole)."""

        def cambia(utente: Dict[str, Any]) -> bool:
            if utente.get("enabled") is False:
                return False
            utente["enabled"] = False
            return True

        await self._riscrivi_utente(utente_id, cambia)

    # ---- identità social collegate a un utente ------------------------------------------------------------

    async def identita_federate(self, utente_id: str) -> List[Dict[str, Any]]:
        """I social collegati all'utente: `[{"identityProvider": "apple", "userId": "…", "userName": "…"}]`.
        Un utente che non esiste (404) non ne ha."""
        risposta = await self._chiama("GET", f"/users/{quote(utente_id)}/federated-identity", ammessi=(404,))
        return [] if risposta.status_code == 404 else list(risposta.json() or [])

    async def collega_identita(self, utente_id: str, identita: Dict[str, Any]) -> None:
        """Collega all'utente un'identità social già nota (provider, id e nome presso il provider). Keycloak rifiuta
        (409) se l'utente ha già un'identità di quel provider, o se l'identità è di un altro utente."""
        alias = str(identita["identityProvider"])
        await self._chiama("POST", f"/users/{quote(utente_id)}/federated-identity/{quote(alias)}", json={
            "identityProvider": alias, "userId": identita["userId"], "userName": identita.get("userName") or "",
        })

    async def scollega_identita(self, utente_id: str, alias: str) -> None:
        await self._chiama("DELETE", f"/users/{quote(utente_id)}/federated-identity/{quote(alias)}", ammessi=(404,))

    # ---- il client delle app -------------------------------------------------------------------------------

    async def assicura_client_mobile(self) -> bool:
        """Il client pubblico delle app (`tarot-mobile`) sul realm già in produzione, che è stato importato prima
        che il client esistesse. Vero se l'ha creato adesso, falso se c'era già (e allora non lo tocca).

        **Perché l'importazione parziale e non `POST /clients`.** Creare un client vuole il ruolo `manage-clients`,
        che l'account di servizio non ha e non può darsi da solo; l'importazione parziale del realm vuole
        `manage-realm`, che ha già (il login persistente). Verificato su un Keycloak 26.0.8: `POST /clients` → 403,
        `POST /partialImport` con un client → 200. Con `ifResourceExists: SKIP` un client che c'è già resta com'è
        (nessun token delle app già entrate viene invalidato)."""
        risposta = await self._chiama("POST", "/partialImport", json={
            "ifResourceExists": "SKIP", "clients": [client_mobile()],
        })
        esiti = (risposta.json() or {}).get("results") or []
        creato = any(e.get("action") == "ADDED" and e.get("resourceName") == CLIENT_MOBILE for e in esiti)
        if creato:
            logger.info("Creato il client «%s» per le app", CLIENT_MOBILE)
        return creato

    # ---- identity provider ------------------------------------------------------------------------

    async def provider_identita(self) -> List[Dict[str, Any]]:
        """I provider configurati nel realm. Il segreto torna mascherato (`**********`): Keycloak non lo
        restituisce mai in chiaro, ed è giusto così."""
        return (await self._chiama("GET", "/identity-provider/instances")).json()

    async def leggi_provider(self, alias: str) -> Optional[Dict[str, Any]]:
        risposta = await self._chiama("GET", f"/identity-provider/instances/{quote(alias)}", ammessi=(404,))
        return None if risposta.status_code == 404 else risposta.json()

    async def salva_provider(self, rappresentazione: Dict[str, Any], *, esiste: bool) -> None:
        """Crea il provider o lo aggiorna. In aggiornamento, un `clientSecret` lasciato a `**********` (il
        valore mascherato letto da Keycloak) fa tenere a Keycloak il segreto che ha già."""
        alias = rappresentazione["alias"]
        if esiste:
            await self._chiama("PUT", f"/identity-provider/instances/{quote(alias)}", json=rappresentazione)
        else:
            await self._chiama("POST", "/identity-provider/instances", json=rappresentazione)
