"""La console «App mobili» (v9, Fase 3): segreti mai in chiaro, appunti dei pagamenti con le sole ultime 4 cifre,
prodotti unici per piattaforma, politica del pulsante Stripe (predefinito «nascosto», risoluzione per paese), versione
minima per le app, e le «Verifica» di Google Play e Apple contro servizi finti (JWT firmati con chiavi generate qui).
Nessuna chiamata vera agli store."""
from __future__ import annotations

import base64
import json
from urllib.parse import parse_qs

import httpx
import pytest
from sqlalchemy import select

from ..domain.models import AuditLog
from ..tarot import google, store_verifica
from .conftest import richiede_database

pytestmark = richiede_database


def _b64d(testo: str) -> bytes:
    return base64.urlsafe_b64decode(testo + "=" * (-len(testo) % 4))


def _service_account() -> tuple[str, str]:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    chiave = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = chiave.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                               serialization.NoEncryption()).decode()
    return json.dumps({
        "type": "service_account", "project_id": "tarots-play", "private_key_id": "0123456789abcdef",
        "private_key": pem, "client_email": "play@tarots-play.iam.gserviceaccount.com", "client_id": "1",
        "token_uri": "https://oauth2.googleapis.com/token",
    }), pem


def _p8():
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ec

    chiave = ec.generate_private_key(ec.SECP256R1())
    pem = chiave.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                               serialization.NoEncryption()).decode()
    return pem, chiave.public_key()


@pytest.fixture
def admin(client, principal_admin):
    client.identita.principal = principal_admin
    return client


@pytest.fixture
def pubblico(client):
    def anonimo():
        client.identita.principal = None
        return client

    return anonimo


async def test_solo_l_amministratore(client):
    assert (await client.get("/admin/app-mobili")).status_code == 403
    assert (await client.put("/admin/app-mobili/android", json={"parametri": {"versione_minima": "1"}})).status_code == 403
    assert (await client.post("/admin/app-mobili/ios/verifica")).status_code == 403


async def test_valori_predefiniti(admin):
    r = await admin.get("/admin/app-mobili")
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["android"]["parametri"]["package_name"] == "chat.tarots.app"
    assert d["ios"]["parametri"]["bundle_id"] == "chat.tarots.app"
    assert d["ios"]["parametri"]["ipad"] is True
    assert d["android"]["url_rtdn"].endswith("/billing/store/google/rtdn")
    assert d["ios"]["url_notifiche"].endswith("/billing/store/apple/notifiche")
    assert d["android"]["segreti"]["service_account"]["presente"] is False
    assert d["ios"]["segreti"]["chiave_p8"]["presente"] is False
    assert d["politica_stripe"] == [] and d["prodotti"] == []


async def test_i_segreti_non_escono_mai(admin, pubblico, session):
    sa_json, pem_rsa = _service_account()
    pem_ec, _ = _p8()
    r = await admin.put("/admin/app-mobili/android", json={"service_account_json": sa_json,
                                                            "parametri": {"id_sviluppatore": "1234567890123456789"}})
    assert r.status_code == 200, r.text
    r = await admin.put("/admin/app-mobili/ios", json={"chiave_p8": pem_ec, "parametri": {
        "team_id": "ABCDE12345", "key_id": "KEY1234567", "issuer_id": "57246542-96fe-1a63-e053-0824d011072a",
        "apple_app_id": "1234567890"}})
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["android"]["segreti"]["service_account"] == {
        "presente": True, "client_email": "play@tarots-play.iam.gserviceaccount.com", "project_id": "tarots-play",
        "chiave_fine": "abcdef",
    }
    assert d["ios"]["segreti"]["chiave_p8"]["presente"] is True
    assert len(d["ios"]["segreti"]["chiave_p8"]["impronta"]) == 12

    corpi = [r.text, (await admin.get("/admin/app-mobili")).text]
    corpi.append((await admin.get("/admin/account-esterni")).text)
    pubblico()
    for piattaforma in ("android", "ios"):
        cfg = await admin.get("/app/config", params={"piattaforma": piattaforma, "versione": "1.0.0"})
        assert cfg.status_code == 200, cfg.text
        corpi.append(cfg.text)
        # L'app non riceve nemmeno gli ID degli account.
        for privato in ("1234567890123456789", "ABCDE12345", "KEY1234567", "57246542"):
            assert privato not in cfg.text
    audit = (await session.execute(select(AuditLog).where(AuditLog.action.like("app_mobili.%")))).scalars().all()
    corpi += [json.dumps(a.before) + json.dumps(a.after) for a in audit]
    for corpo in corpi:
        assert "PRIVATE KEY" not in corpo
        for riga in (pem_rsa.splitlines()[1], pem_ec.splitlines()[1]):
            assert riga not in corpo


async def test_si_toglie_il_segreto_e_si_rifiuta_un_file_sbagliato(admin):
    sa_json, pem_rsa = _service_account()
    await admin.put("/admin/app-mobili/android", json={"service_account_json": sa_json})
    r = await admin.put("/admin/app-mobili/android", json={"service_account_json": ""})
    assert r.json()["android"]["segreti"]["service_account"]["presente"] is False
    r = await admin.put("/admin/app-mobili/android", json={"service_account_json": '{"type": "authorized_user"}'})
    assert r.status_code == 422 and "service account" in r.json()["detail"]
    # Una chiave RSA non è una .p8 di Apple.
    r = await admin.put("/admin/app-mobili/ios", json={"chiave_p8": pem_rsa})
    assert r.status_code == 422 and "P-256" in r.json()["detail"]
    r = await admin.put("/admin/app-mobili/ios", json={"chiave_p8": "non è una chiave"})
    assert r.status_code == 422


async def test_formati_rifiutati(admin):
    for corpo in (
        {"parametri": {"package_name": "senzapunti"}},
        {"parametri": {"pubsub_topic": "tarots-rtdn"}},
        {"parametri": {"versione_minima": "1.x"}},
        {"parametri": {"versione_minima": "2.0", "versione_ultima": "1.9"}},
    ):
        r = await admin.put("/admin/app-mobili/android", json=corpo)
        assert r.status_code == 422, corpo
    for corpo in ({"parametri": {"team_id": "abc"}}, {"parametri": {"issuer_id": "non-un-uuid"}},
                  {"parametri": {"ambiente": "test"}}):
        assert (await admin.put("/admin/app-mobili/ios", json=corpo)).status_code == 422, corpo
    r = await admin.put("/admin/app-mobili/android", json={"parametri": {
        "pubsub_topic": "projects/tarots-play/topics/play-rtdn", "rtdn_email": "Push@Tarots-Play.iam.gserviceaccount.com",
        "tipo_account": "organizzazione", "test_chiuso": "non_richiesto", "test_chiuso_dal": "2026-10-01"}})
    assert r.status_code == 200, r.text
    p = r.json()["android"]["parametri"]
    assert p["rtdn_email"] == "push@tarots-play.iam.gserviceaccount.com"
    assert p["test_chiuso_dal"] == "2026-10-01"


async def test_appunti_pagamenti_solo_ultime_4_cifre(admin):
    for piattaforma in ("android", "ios"):
        url = f"/admin/app-mobili/{piattaforma}"
        r = await admin.put(url, json={"pagamenti": {"conto_ultime4": "IT60X0542811101000000123456"}})
        assert r.status_code == 422, r.text
        r = await admin.put(url, json={"pagamenti": {"note": "IBAN IT60 X054 2811 1010 0000 0123 456"}})
        assert r.status_code == 422 and "IBAN" in r.json()["detail"]
        r = await admin.put(url, json={"pagamenti": {"banca": "carta 4111 1111 1111 1111"}})
        assert r.status_code == 422
        r = await admin.put(url, json={"pagamenti": {"conto_ultime4": "12-34", "banca": "Banca Esempio",
                                                     "valuta": "usd", "paese": "it"}})
        assert r.status_code == 200, r.text
        pag = r.json()[piattaforma]["pagamenti"]
        assert pag["conto_ultime4"] == "1234" and pag["valuta"] == "USD" and pag["paese"] == "IT"
    # L'ID del profilo pagamenti di Google ha il formato del profilo di AdSense.
    r = await admin.put("/admin/app-mobili/android", json={"pagamenti": {"id_profilo": "12345"}})
    assert r.status_code == 422
    r = await admin.put("/admin/app-mobili/android", json={"pagamenti": {"id_profilo": "1234-5678-9012"}})
    assert r.status_code == 200


async def _piani(admin):
    piani = (await admin.get("/admin/app-mobili")).json()["piani"]
    pacchetto = next(p for p in piani if p["tipo"] == "pacchetto")
    abbonamento = next(p for p in piani if p["tipo"] == "abbonamento" and not p["gratuito"])
    return pacchetto, abbonamento, next(p for p in piani if p["gratuito"])


async def test_prodotti_unici_e_coerenti_col_piano(admin, catalogo):
    pacchetto, abbonamento, gratuito = await _piani(admin)
    r = await admin.post("/admin/app-mobili/prodotti", json={
        "piattaforma": "android", "product_id": "crediti_100", "plan_id": pacchetto["id"]})
    assert r.status_code == 201, r.text
    prodotto = r.json()["prodotti"][0]
    assert prodotto["tipo"] == "consumabile" and prodotto["piano"]["slug"] == pacchetto["slug"]

    r = await admin.post("/admin/app-mobili/prodotti", json={
        "piattaforma": "android", "product_id": "crediti_100", "plan_id": pacchetto["id"]})
    assert r.status_code == 422 and "c'è già" in r.json()["detail"]
    # Lo stesso ID su iOS è un altro prodotto.
    r = await admin.post("/admin/app-mobili/prodotti", json={
        "piattaforma": "ios", "product_id": "crediti_100", "plan_id": pacchetto["id"]})
    assert r.status_code == 201
    # Un pacchetto non si vende come abbonamento, e Google vuole le minuscole.
    r = await admin.post("/admin/app-mobili/prodotti", json={
        "piattaforma": "android", "product_id": "mese", "plan_id": pacchetto["id"], "tipo": "abbonamento"})
    assert r.status_code == 422
    r = await admin.post("/admin/app-mobili/prodotti", json={
        "piattaforma": "android", "product_id": "Mese_Plus", "plan_id": abbonamento["id"]})
    assert r.status_code == 422
    r = await admin.post("/admin/app-mobili/prodotti", json={
        "piattaforma": "android", "product_id": "gratis", "plan_id": gratuito["id"]})
    assert r.status_code == 422 and "gratuito" in r.json()["detail"]
    r = await admin.post("/admin/app-mobili/prodotti", json={
        "piattaforma": "ios", "product_id": "chat.tarots.app.Mese", "plan_id": abbonamento["id"]})
    assert r.status_code == 201
    mese = next(p for p in r.json()["prodotti"] if p["product_id"] == "chat.tarots.app.Mese")
    assert mese["tipo"] == "abbonamento"

    r = await admin.put(f"/admin/app-mobili/prodotti/{prodotto['id']}", json={"attivo": False})
    assert next(p for p in r.json()["prodotti"] if p["id"] == prodotto["id"])["attivo"] is False
    r = await admin.put(f"/admin/app-mobili/prodotti/{prodotto['id']}", json={"plan_id": abbonamento["id"]})
    assert r.status_code == 422
    r = await admin.delete(f"/admin/app-mobili/prodotti/{prodotto['id']}")
    assert all(p["id"] != prodotto["id"] for p in r.json()["prodotti"])
    assert (await admin.delete(f"/admin/app-mobili/prodotti/{prodotto['id']}")).status_code == 404


async def _stripe(admin, piattaforma, paese=None):
    params = {"piattaforma": piattaforma, **({"paese": paese} if paese else {})}
    r = await admin.get("/app/config", params=params)
    assert r.status_code == 200, r.text
    return r.json()["pulsante_stripe"]["modalita"]


async def test_pulsante_stripe_nascosto_per_default_e_per_paese(admin):
    assert await _stripe(admin, "ios", "US") == "nascosto"
    assert await _stripe(admin, "android") == "nascosto"

    r = await admin.put("/admin/app-mobili/politica-stripe", json={
        "piattaforma": "ios", "paese": "us", "modalita": "link_esterno", "avviso": "Acquisto sul sito"})
    assert r.status_code == 200, r.text
    assert await _stripe(admin, "ios", "US") == "link_esterno"
    assert await _stripe(admin, "ios", "IT") == "nascosto", "senza una riga del paese né «*»: nascosto"
    assert await _stripe(admin, "android", "US") == "nascosto", "le piattaforme sono separate"

    await admin.put("/admin/app-mobili/politica-stripe", json={
        "piattaforma": "ios", "paese": "IT", "modalita": "entitlement_ue"})
    await admin.put("/admin/app-mobili/politica-stripe", json={"piattaforma": "ios", "paese": "*", "modalita": "nascosto"})
    assert await _stripe(admin, "ios", "IT") == "entitlement_ue"
    assert await _stripe(admin, "ios", "FR") == "nascosto"

    # La regola «*» vale per tutti i paesi senza una riga propria; aggiornarla non ne crea un'altra.
    r = await admin.put("/admin/app-mobili/politica-stripe", json={
        "piattaforma": "android", "paese": "*", "modalita": "scelta_utente"})
    assert await _stripe(admin, "android", "BR") == "scelta_utente"
    r = await admin.put("/admin/app-mobili/politica-stripe", json={
        "piattaforma": "android", "paese": "*", "modalita": "nascosto"})
    assert sum(1 for p in r.json()["politica_stripe"] if p["piattaforma"] == "android") == 1
    assert await _stripe(admin, "android", "BR") == "nascosto"

    for sbagliata in (
        {"piattaforma": "ios", "paese": "*", "modalita": "entitlement_ue"},
        {"piattaforma": "ios", "paese": "US", "modalita": "entitlement_ue"},
        {"piattaforma": "ios", "paese": "US", "modalita": "scelta_utente"},
        {"piattaforma": "ios", "paese": "U1", "modalita": "nascosto"},
    ):
        assert (await admin.put("/admin/app-mobili/politica-stripe", json=sbagliata)).status_code == 422, sbagliata

    regola = next(p for p in r.json()["politica_stripe"] if p["paese"] == "US")
    r = await admin.delete(f"/admin/app-mobili/politica-stripe/{regola['id']}")
    assert r.status_code == 200
    assert await _stripe(admin, "ios", "US") == "nascosto"


async def test_config_per_le_app_e_versione_minima(admin, pubblico):
    await admin.put("/admin/app-mobili/android", json={"parametri": {"versione_minima": "1.2.0", "versione_ultima": "1.3"}})
    await admin.put("/admin/app-mobili/ios", json={"parametri": {"versione_minima": "2", "apple_app_id": "1234567890"}})
    c = pubblico()
    r = await c.get("/app/config", params={"piattaforma": "android", "versione": "1.1.9"})
    d = r.json()
    assert d["aggiornamento_obbligatorio"] is True and d["aggiornamento_disponibile"] is True
    assert d["link_store"] == "https://play.google.com/store/apps/details?id=chat.tarots.app"
    assert r.headers["Cache-Control"].startswith("public")
    d = (await c.get("/app/config", params={"piattaforma": "android", "versione": "1.2"})).json()
    assert d["aggiornamento_obbligatorio"] is False and d["aggiornamento_disponibile"] is True
    d = (await c.get("/app/config", params={"piattaforma": "android", "versione": "1.3.0"})).json()
    assert d["aggiornamento_disponibile"] is False
    d = (await c.get("/app/config", params={"piattaforma": "ios", "versione": "1.9.9"})).json()
    assert d["aggiornamento_obbligatorio"] is True and d["flag"] == {"ipad": True}
    assert d["link_store"] == "https://apps.apple.com/app/id1234567890"
    assert set(d) == {"piattaforma", "versione_minima", "versione_ultima", "aggiornamento_obbligatorio",
                      "aggiornamento_disponibile", "link_store", "pulsante_stripe", "flag"}
    assert (await c.get("/app/config", params={"piattaforma": "ios", "versione": "abc"})).status_code == 422
    assert (await c.get("/app/config", params={"piattaforma": "windows"})).status_code == 422


# ---- Verifica con servizi finti -------------------------------------------------------------------------------------


@pytest.fixture
def play_finto(monkeypatch):
    """Google finto: il token OAuth (JWT RS256 del service account) e la Play Developer API."""
    stato = {"api": 200}
    chiamate: list = []

    def gestore(req: httpx.Request) -> httpx.Response:
        chiamate.append((req.method, str(req.url)))
        if req.url.host == "oauth2.googleapis.com":
            corpo = parse_qs(req.content.decode())
            parti = corpo["assertion"][0].split(".")
            assert json.loads(_b64d(parti[0]))["alg"] == "RS256"
            assert json.loads(_b64d(parti[1]))["scope"] == store_verifica.SCOPE_ANDROIDPUBLISHER
            return httpx.Response(200, json={"access_token": "tok-play", "expires_in": 3600})
        assert req.url.host == "androidpublisher.googleapis.com"
        assert req.headers["Authorization"] == "Bearer tok-play"
        assert req.method == "GET", "la verifica è di sola lettura"
        assert req.url.path == "/androidpublisher/v3/applications/chat.tarots.app/inappproducts"
        if stato["api"] == 200:
            return httpx.Response(200, json={"inappproduct": []})
        return httpx.Response(stato["api"], json={"error": {"code": stato["api"], "message": "The caller does not have permission"}})

    finto = lambda: httpx.AsyncClient(transport=httpx.MockTransport(gestore))  # noqa: E731
    monkeypatch.setattr(google, "_client", finto)
    monkeypatch.setattr(store_verifica, "_client", finto)
    google._TOKEN.clear()
    yield stato, chiamate
    google._TOKEN.clear()


async def test_verifica_play_con_google_finto(admin, play_finto):
    stato, chiamate = play_finto
    r = await admin.post("/admin/app-mobili/android/verifica")
    assert r.json()["android"]["esito_verifica"]["ok"] is False
    assert "Manca il JSON" in r.json()["android"]["esito_verifica"]["messaggio"]
    assert chiamate == [], "senza credenziali non si chiama nessuno"

    sa_json, _ = _service_account()
    await admin.put("/admin/app-mobili/android", json={"service_account_json": sa_json})
    r = await admin.post("/admin/app-mobili/android/verifica")
    esito = r.json()["android"]["esito_verifica"]
    assert esito["ok"] is True, esito
    assert r.json()["android"]["verificato_il"]

    stato["api"] = 403
    esito = (await admin.post("/admin/app-mobili/android/verifica")).json()["android"]["esito_verifica"]
    assert esito["ok"] is False and "Utenti e autorizzazioni" in esito["messaggio"]
    stato["api"] = 404
    esito = (await admin.post("/admin/app-mobili/android/verifica")).json()["android"]["esito_verifica"]
    assert esito["ok"] is False and "non trova l'app" in esito["messaggio"]


@pytest.fixture
def apple_finto(monkeypatch):
    """Apple finta: controlla il JWT ES256 con la chiave pubblica della .p8 generata nel test."""
    stato = {"risposta": 200, "chiave_pubblica": None}
    chiamate: list = []

    def gestore(req: httpx.Request) -> httpx.Response:
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature

        chiamate.append((req.method, str(req.url)))
        token = req.headers["Authorization"].removeprefix("Bearer ")
        intestazione, corpo, firma = token.split(".")
        h, c = json.loads(_b64d(intestazione)), json.loads(_b64d(corpo))
        assert h == {"alg": "ES256", "kid": "KEY1234567", "typ": "JWT"}
        assert c["aud"] == "appstoreconnect-v1" and c["bid"] == "chat.tarots.app"
        assert c["iss"] == "57246542-96fe-1a63-e053-0824d011072a" and c["exp"] - c["iat"] <= 3600
        grezza = _b64d(firma)
        assert len(grezza) == 64, "ES256 in un JWS: r e s affiancati, non DER"
        der = encode_dss_signature(int.from_bytes(grezza[:32], "big"), int.from_bytes(grezza[32:], "big"))
        stato["chiave_pubblica"].verify(der, f"{intestazione}.{corpo}".encode(), ec.ECDSA(hashes.SHA256()))
        if stato["risposta"] == 200:
            return httpx.Response(200, json={"testNotificationToken": "ce3af791-365e-4c60-841b-1674b43c1609"})
        return httpx.Response(stato["risposta"], json={"errorCode": 4040010, "errorMessage": "App not found."})

    monkeypatch.setattr(store_verifica, "_client", lambda: httpx.AsyncClient(transport=httpx.MockTransport(gestore)))
    return stato, chiamate


async def test_verifica_apple_con_apple_finta(admin, apple_finto):
    stato, chiamate = apple_finto
    r = await admin.post("/admin/app-mobili/ios/verifica")
    assert "Mancano la chiave .p8" in r.json()["ios"]["esito_verifica"]["messaggio"]
    assert chiamate == []

    pem, pubblica = _p8()
    stato["chiave_pubblica"] = pubblica
    await admin.put("/admin/app-mobili/ios", json={"chiave_p8": pem, "parametri": {
        "key_id": "KEY1234567", "issuer_id": "57246542-96fe-1a63-e053-0824d011072a"}})
    esito = (await admin.post("/admin/app-mobili/ios/verifica")).json()["ios"]["esito_verifica"]
    assert esito["ok"] is True, esito
    assert chiamate[-1] == ("POST", "https://api.storekit-sandbox.itunes.apple.com/inApps/v1/notifications/test")

    await admin.put("/admin/app-mobili/ios", json={"parametri": {"ambiente": "production"}})
    stato["risposta"] = 401
    esito = (await admin.post("/admin/app-mobili/ios/verifica")).json()["ios"]["esito_verifica"]
    assert esito["ok"] is False and "Key ID" in esito["messaggio"]
    assert chiamate[-1][1].startswith("https://api.storekit.itunes.apple.com/")
    stato["risposta"] = 404
    esito = (await admin.post("/admin/app-mobili/ios/verifica")).json()["ios"]["esito_verifica"]
    assert esito["ok"] is False and "App Store Connect" in esito["messaggio"]


async def test_codemagic_solo_appunti(admin):
    r = await admin.put("/admin/app-mobili/codemagic", json={
        "team": "Tarots", "app_id": "5d85eaa0e941e00019e81bc2", "chiave_asc_caricata": True,
        "chiave_asc_key_id": "ABC123DEFG"})
    assert r.status_code == 200, r.text
    cm = r.json()["codemagic"]
    assert cm["parametri"]["chiave_asc_caricata"] is True
    assert cm["link_console"] == "https://codemagic.io/app/5d85eaa0e941e00019e81bc2"
    assert (await admin.put("/admin/app-mobili/codemagic", json={"chiave_asc_key_id": "corta"})).status_code == 422


# ---- collegamenti verificati (Fase 10) ------------------------------------------------------------------------------

_UPLOAD = "14:6D:E9:83:C5:73:06:50:D8:EE:B9:95:2F:34:FC:64:16:A0:83:42:E6:1D:BE:A8:8A:04:96:B2:3F:CF:44:E5"


async def _anonimo(client, percorso):
    """Una lettura senza account (il sito che chiede i file), poi di nuovo l'amministratore."""
    prima = client.identita.principal
    client.identita.principal = None
    try:
        return await client.get(percorso)
    finally:
        client.identita.principal = prima


async def test_assetlinks_dalle_impronte_della_console(admin):
    # Senza impronte: un elenco vuoto, non un errore (Android non verifica, l'app funziona lo stesso).
    r = await _anonimo(admin, "/app/collegamenti/assetlinks.json")
    assert r.status_code == 200 and r.json() == []
    # Più impronte, in forme diverse: con o senza due punti, minuscole, «SHA256:», doppioni.
    firma = "a" * 64
    r = await admin.put("/admin/app-mobili/android", json={"parametri": {
        "impronte_sha256": [_UPLOAD.lower(), f"SHA256: {firma}", _UPLOAD.replace(":", "")]}})
    assert r.status_code == 200, r.text
    impronte = r.json()["android"]["parametri"]["impronte_sha256"]
    assert impronte == [_UPLOAD, ":".join(["AA"] * 32)]
    r = await _anonimo(admin, "/app/collegamenti/assetlinks.json")
    assert r.headers["content-type"].startswith("application/json")
    assert r.json() == [{
        "relation": ["delegate_permission/common.handle_all_urls"],
        "target": {"namespace": "android_app", "package_name": "chat.tarots.app", "sha256_cert_fingerprints": impronte},
    }]
    # Un'impronta sbagliata non si salva, e quelle di prima restano.
    for sbagliata in (["AB:CD"], ["Z" * 64], [_UPLOAD + ":00"]):
        r = await admin.put("/admin/app-mobili/android", json={"parametri": {"impronte_sha256": sbagliata}})
        assert r.status_code == 422 and "SHA-256" in r.json()["detail"], sbagliata
    assert (await _anonimo(admin, "/app/collegamenti/assetlinks.json")).json()[0]["target"]["sha256_cert_fingerprints"] == impronte
    # Si tolgono tutte con un elenco vuoto.
    r = await admin.put("/admin/app-mobili/android", json={"parametri": {"impronte_sha256": []}})
    assert r.json()["android"]["parametri"]["impronte_sha256"] == []
    assert (await _anonimo(admin, "/app/collegamenti/assetlinks.json")).json() == []


async def test_apple_app_site_association(admin):
    assert (await _anonimo(admin, "/app/collegamenti/apple-app-site-association")).json() == {"applinks": {"details": []}}
    await admin.put("/admin/app-mobili/ios", json={"parametri": {"team_id": "ABCDE12345"}})
    d = (await _anonimo(admin, "/app/collegamenti/apple-app-site-association")).json()
    dettaglio = d["applinks"]["details"][0]
    assert dettaglio["appIDs"] == ["ABCDE12345.chat.tarots.app"]
    assert d["webcredentials"] == {"apps": ["ABCDE12345.chat.tarots.app"]}
    componenti = dettaglio["components"]
    esclusi = [x["/"] for x in componenti if x.get("exclude")]
    # Keycloak e l'API non si aprono mai nell'app (il ritorno dei social, il link di disiscrizione), e le esclusioni
    # vengono prima: iOS si ferma alla prima regola che corrisponde.
    assert {"/auth/*", "/api/*", "/admin/*", "/old/*"} <= set(esclusi)
    assert componenti[: len(esclusi)] == [x for x in componenti if x.get("exclude")]
    inclusi = [x["/"] for x in componenti if not x.get("exclude")]
    for p in ("/", "/it/*", "/daily-card", "/card-of-the-day/*", "/pricing", "/cards/*", "/account/elimina"):
        assert p in inclusi, p
    assert not any(p.startswith(("/auth", "/api")) for p in inclusi)
