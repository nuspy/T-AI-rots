"""Google dalla console (v8.6): il JSON del service account cifrato, la verifica passo per passo, la sitemap, GA4,
l'ID di misurazione pubblico per il sito. Nessuna chiamata vera a Google: un trasporto HTTP finto."""
from __future__ import annotations

import base64
import json
from urllib.parse import parse_qs, unquote

import httpx
import pytest

from ..domain.integrazioni_models import ConfigGoogle
from ..tarot import google
from .conftest import richiede_database

pytestmark = richiede_database


def _service_account(email="tarots@progetto-x.iam.gserviceaccount.com") -> str:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    chiave = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = chiave.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    return json.dumps({
        "type": "service_account", "project_id": "progetto-x", "private_key_id": "abcdef1234567890",
        "private_key": pem.decode(), "client_email": email, "client_id": "1",
        "token_uri": "https://oauth2.googleapis.com/token",
    })


@pytest.fixture
def admin(client, principal_admin):
    client.identita.principal = principal_admin
    return client


@pytest.fixture
def google_finto(monkeypatch):
    """Un Google finto: token, Search Console e GA4. `stato` decide le risposte; `chiamate` le registra."""
    stato = {"sc": 200, "livello": "siteFullUser", "sitemap": 204, "ga4": 200, "token": 200}
    chiamate: list = []

    def gestore(req: httpx.Request) -> httpx.Response:
        chiamate.append((req.method, str(req.url)))
        host, percorso = req.url.host, unquote(req.url.raw_path.decode())
        if host == "oauth2.googleapis.com":
            corpo = parse_qs(req.content.decode())
            assert corpo["grant_type"] == ["urn:ietf:params:oauth:grant-type:jwt-bearer"]
            intestazione = json.loads(base64.urlsafe_b64decode(corpo["assertion"][0].split(".")[0] + "=="))
            assert intestazione["alg"] == "RS256"
            if stato["token"] != 200:
                return httpx.Response(400, json={"error": "invalid_grant", "error_description": "Invalid JWT Signature."})
            return httpx.Response(200, json={"access_token": "tok", "expires_in": 3600})
        assert req.headers["Authorization"] == "Bearer tok"
        if host == "www.googleapis.com" and "/sitemaps/" in percorso:
            return httpx.Response(stato["sitemap"])
        if host == "www.googleapis.com":
            if stato["sc"] == 200:
                return httpx.Response(200, json={"siteUrl": "sc-domain:tarots.chat", "permissionLevel": stato["livello"]})
            if stato["sc"] == "disabilitata":
                return httpx.Response(403, json={"error": {"code": 403, "message": "Google Search Console API has not been used in project 1 before or it is disabled.",
                                                           "errors": [{"reason": "accessNotConfigured"}]}})
            return httpx.Response(stato["sc"], json={"error": {"code": stato["sc"], "message": "User does not have sufficient permission"}})
        if host == "analyticsdata.googleapis.com":
            if stato["ga4"] != 200:
                return httpx.Response(403, json={"error": {"code": 403, "status": "PERMISSION_DENIED", "message": "no"}})
            if percorso.endswith(":runReport"):
                return httpx.Response(200, json={"rows": [{"metricValues": [{"value": "42"}]}]})
            if percorso.endswith(":batchRunReports"):
                return httpx.Response(200, json={"reports": [
                    {"rows": [{"dimensionValues": [{"value": "date_range_0"}], "metricValues": [{"value": v} for v in ("10", "4", "12", "30", "0.5", "61.2")]},
                              {"dimensionValues": [{"value": "date_range_1"}], "metricValues": [{"value": v} for v in ("5", "2", "6", "11", "0.4", "40")]}]},
                    {"rows": [{"dimensionValues": [{"value": "20261002"}], "metricValues": [{"value": "3"}, {"value": "4"}, {"value": "9"}]}]},
                    {"rows": [{"dimensionValues": [{"value": "/blog"}], "metricValues": [{"value": "20"}, {"value": "7"}]}]},
                    {"rows": [{"dimensionValues": [{"value": "google / organic"}], "metricValues": [{"value": "8"}, {"value": "6"}]}]},
                    {"rows": [{"dimensionValues": [{"value": "Organic Search"}], "metricValues": [{"value": "8"}]}]},
                ]})
        return httpx.Response(404)

    monkeypatch.setattr(google, "_client", lambda: httpx.AsyncClient(transport=httpx.MockTransport(gestore)))
    google._TOKEN.clear()
    google._CACHE.clear()
    yield stato, chiamate
    google._TOKEN.clear()
    google._CACHE.clear()


def test_il_json_deve_essere_un_service_account():
    with pytest.raises(google.ErroreGoogle, match="non è un JSON"):
        google.leggi_service_account("ciao")
    with pytest.raises(google.ErroreGoogle, match="client OAuth"):
        google.leggi_service_account(json.dumps({"installed": {"client_id": "x"}}))
    with pytest.raises(google.ErroreGoogle, match="mancano"):
        google.leggi_service_account(json.dumps({"type": "service_account", "client_email": "a@b"}))
    info = google.leggi_service_account(_service_account())
    assert info["client_email"].endswith("gserviceaccount.com")


def test_asserzione_firmata_rs256():
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding

    info = json.loads(_service_account())
    jwt = google.asserzione(info, google.SCOPE_ANALYTICS, adesso=1_000)
    testa, corpo, firma = jwt.split(".")
    dati = json.loads(base64.urlsafe_b64decode(corpo + "=" * (-len(corpo) % 4)))
    assert dati == {"iss": info["client_email"], "scope": google.SCOPE_ANALYTICS, "aud": "https://oauth2.googleapis.com/token",
                    "iat": 1_000, "exp": 4_600}
    pubblica = serialization.load_pem_private_key(info["private_key"].encode(), password=None).public_key()
    pubblica.verify(base64.urlsafe_b64decode(firma + "=" * (-len(firma) % 4)), f"{testa}.{corpo}".encode(),
                    padding.PKCS1v15(), hashes.SHA256())


async def test_la_chiave_si_salva_cifrata_e_non_esce(admin, session):
    testo = _service_account()
    r = await admin.post("/admin/google/credenziali", json={"json_service_account": testo})
    assert r.status_code == 200, r.text
    corpo = r.json()
    assert corpo["credenziali"] == {"presenti": True, "origine": "console", "project_id": "progetto-x",
                                    "client_email": "tarots@progetto-x.iam.gserviceaccount.com", "chiave_fine": "567890"}
    assert "PRIVATE KEY" not in r.text
    riga = await session.get(ConfigGoogle, 1)
    assert riga.service_account_cifrato and b"PRIVATE KEY" not in bytes(riga.service_account_cifrato)

    stato = (await admin.get("/admin/google")).json()
    assert "PRIVATE KEY" not in json.dumps(stato) and stato["sc_proprieta"] == "sc-domain:tarots.chat"

    r = await admin.post("/admin/google/credenziali", json={"json_service_account": json.dumps({"type": "authorized_user", "x": 1})})
    assert r.status_code == 422 and "service account" in r.json()["detail"]

    assert (await admin.delete("/admin/google/credenziali")).json()["credenziali"]["presenti"] is False


async def test_impostazioni_validate(admin):
    r = await admin.put("/admin/google/impostazioni", json={"ga4_misurazione_id": "UA-123"})
    assert r.status_code == 422 and "G-" in r.json()["detail"]
    r = await admin.put("/admin/google/impostazioni", json={"ga4_proprieta_id": "G-ABC123"})
    assert r.status_code == 422
    r = await admin.put("/admin/google/impostazioni", json={"sc_proprieta": "tarots.chat"})
    assert r.status_code == 422
    r = await admin.put("/admin/google/impostazioni", json={
        "ga4_misurazione_id": "g-abc123xyz", "ga4_proprieta_id": "properties/123456789", "sc_proprieta": "https://tarots.chat/",
    })
    assert r.status_code == 200, r.text
    assert r.json()["ga4_misurazione_id"] == "G-ABC123XYZ" and r.json()["ga4_proprieta_id"] == "123456789"
    assert r.json()["sc_proprieta"] == "https://tarots.chat/"
    # Il sito legge l'ID di misurazione senza account.
    admin.identita.principal = None
    r = await admin.get("/impostazioni-google")
    assert r.json() == {"ga4_misurazione_id": "G-ABC123XYZ"} and "max-age" in r.headers["cache-control"]


async def test_verifica_tutto_a_posto_invia_la_sitemap(admin, google_finto):
    _, chiamate = google_finto
    await admin.post("/admin/google/credenziali", json={"json_service_account": _service_account()})
    await admin.put("/admin/google/impostazioni", json={"ga4_proprieta_id": "123456789", "ga4_misurazione_id": "G-ABC123"})
    r = await admin.post("/admin/google/verifica")
    assert r.status_code == 200, r.text
    esito = r.json()["esito_verifica"]
    assert {k: v["ok"] for k, v in esito.items()} == {"credenziali": True, "search_console": True, "sitemap": True, "ga4": True, "contatore": True}
    assert "42 utenti" in esito["ga4"]["messaggio"]
    assert any(m == "PUT" and "sitemaps" in u for m, u in chiamate)
    assert r.json()["verificato_il"]


async def test_verifica_spiega_cosa_manca(admin, google_finto):
    stato, chiamate = google_finto
    r = await admin.post("/admin/google/verifica")
    esito = r.json()["esito_verifica"]
    assert esito["credenziali"]["ok"] is False and "passo 1" in esito["credenziali"]["messaggio"]
    assert esito["search_console"].get("saltato") and esito["ga4"].get("saltato")
    assert chiamate == []

    await admin.post("/admin/google/credenziali", json={"json_service_account": _service_account()})
    stato["sc"] = 403
    esito = (await admin.post("/admin/google/verifica")).json()["esito_verifica"]
    assert esito["credenziali"]["ok"] is True
    assert esito["search_console"]["ok"] is False and "Aggiungi utente" in esito["search_console"]["messaggio"]
    assert "tarots@progetto-x.iam.gserviceaccount.com" in esito["search_console"]["messaggio"]
    assert esito["sitemap"].get("saltato") and not any("sitemaps" in u for _, u in chiamate)

    stato["sc"] = "disabilitata"
    esito = (await admin.post("/admin/google/verifica")).json()["esito_verifica"]
    assert "searchconsole.googleapis.com" in esito["search_console"]["messaggio"] and "progetto-x" in esito["search_console"]["messaggio"]

    stato["sc"], stato["livello"] = 200, "siteRestrictedUser"
    esito = (await admin.post("/admin/google/verifica")).json()["esito_verifica"]
    assert esito["search_console"]["ok"] is True and "Completo" in esito["search_console"]["messaggio"]
    assert esito["sitemap"].get("saltato")

    stato["livello"] = "siteFullUser"
    await admin.put("/admin/google/impostazioni", json={"ga4_proprieta_id": "123456789"})
    stato["ga4"] = 403
    esito = (await admin.post("/admin/google/verifica")).json()["esito_verifica"]
    assert esito["ga4"]["ok"] is False and "Visualizzatore" in esito["ga4"]["messaggio"]


async def test_chiave_revocata(admin, google_finto):
    stato, _ = google_finto
    stato["token"] = 400
    await admin.post("/admin/google/credenziali", json={"json_service_account": _service_account()})
    esito = (await admin.post("/admin/google/verifica")).json()["esito_verifica"]
    assert esito["credenziali"]["ok"] is False and "nuova chiave" in esito["credenziali"]["messaggio"]


async def test_statistiche_ga4(admin, google_finto):
    r = (await admin.get("/admin/google/statistiche?giorni=7")).json()
    assert r["pronto"] is False and "le credenziali del service account" in r["mancano"]

    await admin.post("/admin/google/credenziali", json={"json_service_account": _service_account()})
    await admin.put("/admin/google/impostazioni", json={"ga4_proprieta_id": "123456789"})
    r = (await admin.get("/admin/google/statistiche?giorni=7")).json()
    assert r["pronto"] is True
    assert r["totali"]["activeUsers"] == 10 and r["precedente"]["activeUsers"] == 5
    assert r["giorni"] == [{"giorno": "2026-10-02", "utenti": 3, "sessioni": 4, "visualizzazioni": 9}]
    assert r["pagine"][0]["pagina"] == "/blog" and r["sorgenti"][0]["sorgente"] == "google / organic"

    stato, _ = google_finto
    stato["ga4"] = 403
    google._CACHE.clear()
    r = (await admin.get("/admin/google/statistiche?giorni=7")).json()
    assert r["pronto"] is False and "Visualizzatore" in r["errore"]


async def test_la_notifica_notturna_usa_le_credenziali_della_console(admin, google_finto, monkeypatch):
    from ..tarot import notifiche_motori

    _, chiamate = google_finto
    await admin.post("/admin/google/credenziali", json={"json_service_account": _service_account()})
    canali = (await admin.get("/admin/seo/notifiche")).json()["canali"]
    assert canali["search_console"]["configurato"] is True and "dalla console" in canali["search_console"]["dettaglio"]

    monkeypatch.setattr(notifiche_motori, "leggi_sitemap", lambda sito: [f"{sito.rstrip('/')}/nuova"])
    giro = (await admin.post("/admin/seo/notifiche")).json()
    assert giro["esiti"]["search_console"]["stato"] == "ok"
    assert any("sitemaps" in u for _, u in chiamate)


async def test_consenso_google_solo_sull_informativa_che_lo_nomina(client):
    # Mai deciso: niente Google, niente da rinnovare (il banner c'è già per la scelta mancante).
    assert (await client.get("/consenso-google")).json() == {"attivo": False, "da_rinnovare": False}
    # Accettato sul testo di prima (v1, che non nominava Google Analytics): da rinnovare, Google spento.
    r = await client.post("/consenso", json={"tipo": "cookie", "valore": "accettato", "versione_informativa": "v1"})
    assert r.status_code == 200, r.text
    r = await client.get("/consenso-google")
    assert r.json() == {"attivo": False, "da_rinnovare": True} and r.headers["cache-control"] == "no-store"
    # Accettato sul testo nuovo: acceso.
    await client.post("/consenso", json={"tipo": "cookie", "valore": "accettato", "versione_informativa": "v2"})
    assert (await client.get("/consenso-google")).json() == {"attivo": True, "da_rinnovare": False}
    await client.post("/consenso", json={"tipo": "cookie", "valore": "rifiutato", "versione_informativa": "v2"})
    assert (await client.get("/consenso-google")).json() == {"attivo": False, "da_rinnovare": False}


async def test_google_solo_admin(client):
    assert (await client.get("/admin/google")).status_code == 403
    assert (await client.post("/admin/google/verifica")).status_code == 403
