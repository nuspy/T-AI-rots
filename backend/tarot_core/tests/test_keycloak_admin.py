"""Il client-credentials grant e le scritture sul realm: un server HTTP finto, nessuna rete."""
from __future__ import annotations

import json

import httpx
import pytest

from tarot_core.auth.keycloak_admin import KeycloakAdmin, KeycloakAdminError
from tarot_core.auth.provider_sociali import MASCHERA, PER_ALIAS, e_segnaposto, rappresentazione, stato
from tarot_core.settings import Settings


def _settings(secret: str = "il-segreto") -> Settings:
    return Settings(keycloak_url="http://kc.test", keycloak_realm="tarots", keycloak_client_secret=secret)


def _trasporto(gestore):
    return httpx.MockTransport(gestore)


async def test_sessione_persistente_senza_durata_massima():
    chiamate = []

    def gestore(request: httpx.Request) -> httpx.Response:
        chiamate.append(request)
        if request.url.path.endswith("/protocol/openid-connect/token"):
            assert request.content and b"grant_type=client_credentials" in request.content
            return httpx.Response(200, json={"access_token": "tok123", "expires_in": 60})
        if request.method == "PUT" and request.url.path == "/admin/realms/tarots":
            corpo = json.loads(request.content)
            # Nessuna durata massima: il token offline vale finché lo si usa, fino al logout.
            assert corpo == {"offlineSessionIdleTimeout": 31_536_000, "offlineSessionMaxLifespanEnabled": False}
            assert request.headers["authorization"] == "Bearer tok123"
            return httpx.Response(204)
        return httpx.Response(404)

    admin = KeycloakAdmin(_settings(), transport=_trasporto(gestore))
    await admin.imposta_sessione_persistente(inattivita_secondi=31_536_000, durata_massima_secondi=0)
    assert len(chiamate) == 2


async def test_sessione_persistente_con_durata_massima():
    corpi = []

    def gestore(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/protocol/openid-connect/token"):
            return httpx.Response(200, json={"access_token": "tok", "expires_in": 60})
        corpi.append(json.loads(request.content))
        return httpx.Response(204)

    admin = KeycloakAdmin(_settings(), transport=_trasporto(gestore))
    await admin.imposta_sessione_persistente(inattivita_secondi=86_400, durata_massima_secondi=172_800)
    assert corpi == [{
        "offlineSessionIdleTimeout": 86_400, "offlineSessionMaxLifespanEnabled": True,
        "offlineSessionMaxLifespan": 172_800,
    }]


async def test_token_riusato_finche_non_scade():
    conteggio_token = 0

    def gestore(request: httpx.Request) -> httpx.Response:
        nonlocal conteggio_token
        if request.url.path.endswith("/protocol/openid-connect/token"):
            conteggio_token += 1
            return httpx.Response(200, json={"access_token": f"tok{conteggio_token}", "expires_in": 3600})
        return httpx.Response(204)

    admin = KeycloakAdmin(_settings(), transport=_trasporto(gestore))
    await admin.imposta_sessione_persistente(inattivita_secondi=3600, durata_massima_secondi=0)
    await admin.imposta_sessione_persistente(inattivita_secondi=7200, durata_massima_secondi=0)
    assert conteggio_token == 1  # il secondo giro riusa il token, non ne chiede un altro


async def test_senza_segreto_configurato_solleva_un_errore_chiaro():
    admin = KeycloakAdmin(_settings(secret=""))
    with pytest.raises(KeycloakAdminError, match="TAROT_KEYCLOAK_CLIENT_SECRET"):
        await admin.leggi_realm()


async def test_un_token_rifiutato_solleva_keycloak_admin_error():
    def gestore(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": "invalid_client"})

    admin = KeycloakAdmin(_settings(), transport=_trasporto(gestore))
    with pytest.raises(KeycloakAdminError) as errore:
        await admin.imposta_sessione_persistente(inattivita_secondi=3600, durata_massima_secondi=0)
    assert errore.value.stato == 401


async def test_un_realm_che_rifiuta_la_scrittura_solleva_keycloak_admin_error():
    def gestore(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/protocol/openid-connect/token"):
            return httpx.Response(200, json={"access_token": "tok", "expires_in": 60})
        return httpx.Response(403, json={"error": "forbidden"})

    admin = KeycloakAdmin(_settings(), transport=_trasporto(gestore))
    with pytest.raises(KeycloakAdminError) as errore:
        await admin.imposta_sessione_persistente(inattivita_secondi=3600, durata_massima_secondi=0)
    assert errore.value.stato == 403


async def test_keycloak_irraggiungibile_e_un_keycloak_admin_error():
    def gestore(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("rifiutata", request=request)

    admin = KeycloakAdmin(_settings(), transport=_trasporto(gestore))
    with pytest.raises(KeycloakAdminError, match="non raggiungibile"):
        await admin.leggi_realm()


async def test_provider_assente_e_none_e_si_crea_con_post():
    viste = []

    def gestore(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/protocol/openid-connect/token"):
            return httpx.Response(200, json={"access_token": "tok", "expires_in": 60})
        viste.append((request.method, request.url.path))
        if request.method == "GET":
            return httpx.Response(404, json={"error": "Could not find identity provider"})
        return httpx.Response(201)

    admin = KeycloakAdmin(_settings(), transport=_trasporto(gestore))
    assert await admin.leggi_provider("github") is None
    await admin.salva_provider({"alias": "github", "providerId": "github"}, esiste=False)
    await admin.salva_provider({"alias": "github", "providerId": "github"}, esiste=True)
    assert viste == [
        ("GET", "/admin/realms/tarots/identity-provider/instances/github"),
        ("POST", "/admin/realms/tarots/identity-provider/instances"),
        ("PUT", "/admin/realms/tarots/identity-provider/instances/github"),
    ]


# ---- il catalogo dei provider -------------------------------------------------------------------


def test_i_segnaposto_non_sono_credenziali():
    for valore in ("", "  ", "non-usato", "sostituire-google", "${KC_GOOGLE_CLIENT_ID}", None):
        assert e_segnaposto(valore)
    assert not e_segnaposto("1234.apps.googleusercontent.com")


def test_stato_non_rivela_il_segreto_e_ignora_i_segnaposto():
    def credenziali(s):
        return {k: s[k] for k in ("presente", "abilitato", "client_id", "segreto_impostato")}

    esistente = {"alias": "google", "enabled": False, "config": {"clientId": "non-usato", "clientSecret": MASCHERA}}
    assert credenziali(stato(PER_ALIAS["google"], esistente)) == {
        "presente": True, "abilitato": False, "client_id": "", "segreto_impostato": False,
    }
    assert MASCHERA not in json.dumps(stato(PER_ALIAS["google"], esistente))
    esistente = {"alias": "google", "enabled": True, "config": {"clientId": "id-vero", "clientSecret": MASCHERA}}
    assert stato(PER_ALIAS["google"], esistente)["segreto_impostato"] is True
    assert credenziali(stato(PER_ALIAS["google"], None)) == {
        "presente": False, "abilitato": False, "client_id": "", "segreto_impostato": False,
    }
    # L'unione degli account e i dati estesi si leggono da Keycloak, non da una copia.
    nuda = stato(PER_ALIAS["google"], None)
    assert nuda["unione_possibile"] is True and nuda["unione_automatica"] is False and nuda["dati_estesi"] is False
    assert stato(PER_ALIAS["twitter"], None)["unione_possibile"] is False


def test_rappresentazione_tiene_i_campi_di_keycloak_e_il_segreto_mascherato():
    esistente = {
        "alias": "github", "internalId": "abc", "providerId": "github", "enabled": False,
        "config": {"clientId": "vecchio", "clientSecret": MASCHERA, "guiOrder": "3"},
    }
    r = rappresentazione(PER_ALIAS["github"], esistente, abilitato=True, client_id="nuovo", client_secret=None,
                         flusso_dopo="2FA amministratori dopo accesso esterno")
    assert r["internalId"] == "abc" and r["config"]["guiOrder"] == "3"
    assert r["config"]["clientId"] == "nuovo" and r["config"]["clientSecret"] == MASCHERA
    assert r["enabled"] is True and r["postBrokerLoginFlowAlias"] == "2FA amministratori dopo accesso esterno"
    assert esistente["config"]["clientId"] == "vecchio"  # l'originale non si tocca


def test_rappresentazione_nuova_per_apple_e_un_oidc_generico():
    r = rappresentazione(PER_ALIAS["apple"], None, abilitato=True, client_id="chat.tarots.web",
                         client_secret="eyJ...", flusso_dopo=None)
    assert r["providerId"] == "oidc" and r["config"]["issuer"] == "https://appleid.apple.com"
    assert r["config"]["clientSecret"] == "eyJ..." and "postBrokerLoginFlowAlias" not in r


def test_instagram_e_nel_catalogo_ma_non_si_accende():
    assert PER_ALIAS["instagram"].disponibile is False
    assert "Basic Display" in PER_ALIAS["instagram"].nota
