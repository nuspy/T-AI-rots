"""Il client-credentials grant e la scrittura del realm (v6, Fase G): un server HTTP finto, nessuna rete."""
from __future__ import annotations

import json

import httpx
import pytest

from tarot_core.auth.keycloak_admin import KeycloakAdmin, KeycloakAdminError
from tarot_core.settings import Settings


def _settings(secret: str = "il-segreto") -> Settings:
    return Settings(keycloak_url="http://kc.test", keycloak_realm="tarots", keycloak_client_secret=secret)


def _trasporto(gestore):
    return httpx.MockTransport(gestore)


async def test_imposta_durata_sessione_ottiene_un_token_e_scrive_il_realm():
    chiamate = []

    def gestore(request: httpx.Request) -> httpx.Response:
        chiamate.append(request)
        if request.url.path.endswith("/protocol/openid-connect/token"):
            return httpx.Response(200, json={"access_token": "tok123", "expires_in": 60})
        if request.method == "PUT" and request.url.path == "/admin/realms/tarots":
            corpo = json.loads(request.content)
            assert corpo == {"ssoSessionMaxLifespan": 7200}
            assert request.headers["authorization"] == "Bearer tok123"
            return httpx.Response(204)
        return httpx.Response(404)

    admin = KeycloakAdmin(_settings(), transport=_trasporto(gestore))
    await admin.imposta_durata_sessione(7200)
    assert len(chiamate) == 2


async def test_token_riusato_finche_non_scade():
    conteggio_token = 0

    def gestore(request: httpx.Request) -> httpx.Response:
        nonlocal conteggio_token
        if request.url.path.endswith("/protocol/openid-connect/token"):
            conteggio_token += 1
            return httpx.Response(200, json={"access_token": f"tok{conteggio_token}", "expires_in": 3600})
        return httpx.Response(204)

    admin = KeycloakAdmin(_settings(), transport=_trasporto(gestore))
    await admin.imposta_durata_sessione(3600)
    await admin.imposta_durata_sessione(7200)
    assert conteggio_token == 1  # il secondo giro riusa il token, non ne chiede un altro


async def test_senza_segreto_configurato_solleva_un_errore_chiaro():
    admin = KeycloakAdmin(_settings(secret=""))
    with pytest.raises(KeycloakAdminError):
        await admin.imposta_durata_sessione(3600)


async def test_un_token_rifiutato_solleva_keycloak_admin_error():
    def gestore(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": "invalid_client"})

    admin = KeycloakAdmin(_settings(), transport=_trasporto(gestore))
    with pytest.raises(KeycloakAdminError):
        await admin.imposta_durata_sessione(3600)


async def test_un_realm_che_rifiuta_la_scrittura_solleva_keycloak_admin_error():
    def gestore(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/protocol/openid-connect/token"):
            return httpx.Response(200, json={"access_token": "tok", "expires_in": 60})
        return httpx.Response(403, json={"error": "forbidden"})

    admin = KeycloakAdmin(_settings(), transport=_trasporto(gestore))
    with pytest.raises(KeycloakAdminError):
        await admin.imposta_durata_sessione(3600)
