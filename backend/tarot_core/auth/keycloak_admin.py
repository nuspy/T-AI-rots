"""L'API amministrativa di Keycloak, per cambiare le impostazioni del realm (v6, Fase G).

Riusa il client `tarot-api` esistente (`serviceAccountsEnabled: true`, mai usato da nessun codice
prima d'ora) invece di crearne uno nuovo: gli basta il ruolo client `manage-realm` di
`realm-management` sul suo account di servizio (vedi `deploy/keycloak/README.md`).

**Perché non un client separato.** Un secondo client confidenziale con lo stesso scopo (parlare con
l'API di Keycloak da dentro il backend) sarebbe una credenziale in più da custodire per lo stesso
livello di fiducia — questo processo già ne ha una (`keycloak_client_secret`), e un token ottenuto
con quella non è più privilegiato di quanto lo sia il processo stesso.
"""
from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional

import httpx

from ..settings import Settings, get_settings

logger = logging.getLogger(__name__)


class KeycloakAdminError(Exception):
    """L'API amministrativa di Keycloak non ha accettato la richiesta, o non è raggiungibile."""


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

    async def _token_valido(self) -> str:
        if self._token and time.time() < self._scade_a:
            return self._token
        if not self._configurato:
            raise KeycloakAdminError(
                "TAROT_KEYCLOAK_CLIENT_SECRET non impostato: il client-credentials grant non può partire"
            )

        url = f"{self._settings.keycloak_url.rstrip('/')}/realms/{self._settings.keycloak_realm}/protocol/openid-connect/token"
        async with self._client() as client:
            risposta = await client.post(url, data={
                "grant_type": "client_credentials",
                "client_id": self._settings.keycloak_client_id,
                "client_secret": self._settings.keycloak_client_secret,
            })
        if risposta.status_code >= 400:
            raise KeycloakAdminError(f"token client-credentials rifiutato ({risposta.status_code}): {risposta.text[:300]}")

        corpo = risposta.json()
        self._token = corpo["access_token"]
        # Margine di 10 secondi: meglio richiederne uno nuovo un po' presto che
        # rischiare una scrittura sul realm con un token appena scaduto.
        self._scade_a = time.time() + max(int(corpo.get("expires_in", 60)), 0) - 10
        return self._token

    async def imposta_durata_sessione(self, secondi: int) -> None:
        """`ssoSessionMaxLifespan` è una proprietà del realm, non di un client: vale per
        `tarot-frontend` e `tarot-admin` insieme, un solo posto da cambiare."""
        token = await self._token_valido()
        url = f"{self._settings.keycloak_url.rstrip('/')}/admin/realms/{self._settings.keycloak_realm}"
        async with self._client() as client:
            risposta = await client.put(
                url, json={"ssoSessionMaxLifespan": secondi},
                headers={"Authorization": f"Bearer {token}"},
            )
        if risposta.status_code >= 400:
            raise KeycloakAdminError(
                f"aggiornamento del realm rifiutato ({risposta.status_code}): {risposta.text[:300]}"
            )

    async def leggi_realm(self) -> Dict[str, Any]:
        """Solo per un controllo manuale o un test: il valore vero è quello su Keycloak, non la
        copia specchiata in `ImpostazioniSessione` (vedi la nota lì sulla deriva realm-JSON/live)."""
        token = await self._token_valido()
        url = f"{self._settings.keycloak_url.rstrip('/')}/admin/realms/{self._settings.keycloak_realm}"
        async with self._client() as client:
            risposta = await client.get(url, headers={"Authorization": f"Bearer {token}"})
        if risposta.status_code >= 400:
            raise KeycloakAdminError(f"lettura del realm rifiutata ({risposta.status_code}): {risposta.text[:300]}")
        return risposta.json()
