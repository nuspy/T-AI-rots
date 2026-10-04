"""L'accesso dalle app (v9, Fase 6), lato console: il segreto di Apple firmato qui e scritto in Keycloak, il suo
rinnovo mensile, il client `tarot-mobile` creato sul realm già in produzione. Keycloak è finto (`keycloak_finto.py`);
la chiave .p8 è generata nel test."""
from __future__ import annotations

import json
from datetime import timedelta

import jwt as pyjwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from sqlalchemy import select

from tarot_core.api.routers import admin_accesso_social
from tarot_core.auth import keycloak_admin
from tarot_core.auth.keycloak_admin import CLIENT_MOBILE, REDIRECT_MOBILE
from tarot_core.auth.provider_sociali import FLUSSO_UNIONE
from tarot_core.domain.accesso_nativo_models import ConfigAccessoApple
from tarot_core.domain.base import utcnow
from tarot_core.domain.models import AuditLog
from tarot_core.settings import Settings
from tarot_core.tarot import accesso_apple
from tarot_core.tools import apple_segreto

from .conftest import richiede_database
from .keycloak_finto import KeycloakFinto

DATI = {"team_id": "TEAM123456", "key_id": "KEY9876543", "services_id": "chat.tarots.web"}


def chiave_p8() -> tuple[str, ec.EllipticCurvePublicKey]:
    privata = ec.generate_private_key(ec.SECP256R1())
    pem = privata.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption(),
    ).decode()
    return pem, privata.public_key()


def leggi_segreto(segreto: str, pubblica) -> dict:
    """Come lo leggerebbe Apple: firma ES256 con la chiave pubblica, destinatario appleid.apple.com."""
    return pyjwt.decode(segreto, pubblica, algorithms=["ES256"], audience="https://appleid.apple.com")


# ---- il JWT, senza database ----------------------------------------------------------------------------------------


def test_segreto_apple_firmato_es256_con_le_affermazioni_giuste():
    pem, pubblica = chiave_p8()
    adesso = utcnow().replace(microsecond=0)
    segreto, scade = accesso_apple.firma_segreto(chiave_pem=pem, adesso=adesso, **DATI)
    assert pyjwt.get_unverified_header(segreto) == {"alg": "ES256", "kid": "KEY9876543", "typ": "JWT"}
    corpo = leggi_segreto(segreto, pubblica)
    assert corpo["iss"] == "TEAM123456" and corpo["sub"] == "chat.tarots.web"
    assert corpo["iat"] == int(adesso.timestamp())
    # Apple rifiuta un segreto che vale più di 15 777 000 secondi (circa sei mesi).
    assert corpo["exp"] - corpo["iat"] == 180 * 86_400 < 15_777_000
    assert scade == adesso + timedelta(days=180)


def test_segreto_scaduto_non_vale_piu():
    pem, pubblica = chiave_p8()
    segreto, _ = accesso_apple.firma_segreto(chiave_pem=pem, adesso=utcnow() - timedelta(days=200), **DATI)
    with pytest.raises(pyjwt.ExpiredSignatureError):
        leggi_segreto(segreto, pubblica)


def test_solo_chiavi_p8_ec():
    with pytest.raises(accesso_apple.ErroreAccessoApple, match="non è una chiave .p8"):
        accesso_apple.valida_chiave("ciao")
    rsa_pem = rsa.generate_private_key(public_exponent=65537, key_size=2048).private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption(),
    ).decode()
    with pytest.raises(accesso_apple.ErroreAccessoApple, match="EC P-256"):
        accesso_apple.valida_chiave(rsa_pem)


def test_l_audience_delle_app_e_accettata():
    assert CLIENT_MOBILE in Settings().keycloak_accepted_audiences


# ---- la console ----------------------------------------------------------------------------------------------------

@pytest.fixture
def keycloak(monkeypatch):
    finto = KeycloakFinto()
    monkeypatch.setattr(admin_accesso_social, "KeycloakAdmin", finto.fabbrica())
    return finto


@pytest.fixture
def admin(client, principal_admin):
    client.identita.principal = principal_admin
    return client


@richiede_database
async def test_la_console_salva_firma_e_scrive_il_segreto(admin, keycloak, session):
    pem, pubblica = chiave_p8()
    r = await admin.put("/admin/accesso-social/apple/segreto", json={**DATI, "chiave_p8": pem, "abilitato": True})
    assert r.status_code == 200, r.text
    dati = r.json()
    # La chiave non esce mai: solo che c'è e la sua impronta.
    assert "PRIVATE KEY" not in r.text and dati["chiave"]["presente"] and len(dati["chiave"]["impronta"]) == 12
    assert dati["segreto"]["giorni_rimasti"] in (179, 180) and dati["segreto"]["da_rinnovare"] is False

    apple = keycloak.provider["apple"]
    assert apple["enabled"] is True and apple["providerId"] == "oidc"
    assert apple["config"]["clientId"] == "chat.tarots.web"
    assert apple["firstBrokerLoginFlowAlias"] == FLUSSO_UNIONE  # Apple garantisce l'email: unione degli account
    corpo = leggi_segreto(apple["config"]["clientSecret"], pubblica)
    assert corpo["sub"] == "chat.tarots.web" and corpo["iss"] == "TEAM123456"

    riga = await session.get(ConfigAccessoApple, 1)
    await session.refresh(riga)
    assert b"PRIVATE KEY" not in bytes(riga.chiave_cifrata)  # cifrata a riposo
    voce = (await session.execute(select(AuditLog).where(AuditLog.action == "accesso_social.apple_segreto"))).scalar_one()
    assert "PRIVATE" not in json.dumps(voce.after) and voce.after["scritto_in_keycloak"] is True

    # Un secondo salvataggio senza chiave tiene quella di prima e rifirma.
    r = await admin.put("/admin/accesso-social/apple/segreto", json={"services_id": "chat.tarots.accesso"})
    assert r.status_code == 200, r.text
    assert keycloak.provider["apple"]["config"]["clientId"] == "chat.tarots.accesso"
    assert keycloak.provider["apple"]["enabled"] is True  # `abilitato` assente: resta acceso


@richiede_database
async def test_la_console_rifiuta_dati_sbagliati_e_incompleti(admin, keycloak):
    r = await admin.put("/admin/accesso-social/apple/segreto", json={"team_id": "corto"})
    assert r.status_code == 422 and "Team ID" in r.json()["detail"]
    r = await admin.put("/admin/accesso-social/apple/segreto", json={"chiave_p8": "non una chiave"})
    assert r.status_code == 422 and ".p8" in r.json()["detail"]
    # Incompleto: si salva, ma non si accende e niente va a Keycloak.
    r = await admin.put("/admin/accesso-social/apple/segreto", json={"team_id": "TEAM123456", "abilitato": True})
    assert r.status_code == 422
    r = await admin.put("/admin/accesso-social/apple/segreto", json={"team_id": "TEAM123456"})
    assert r.status_code == 200 and r.json()["completa"] is False and r.json()["applicato"] is None
    assert keycloak.provider == {}
    assert (await admin.post("/admin/accesso-social/apple/segreto/rinnova")).status_code == 422


@richiede_database
async def test_il_team_id_di_app_mobili_si_propone(admin, keycloak):
    r = await admin.put("/admin/app-mobili/ios", json={"parametri": {"team_id": "ABCDE12345"}})
    assert r.status_code == 200, r.text
    r = await admin.get("/admin/accesso-social/apple/segreto")
    assert r.json()["team_id_suggerito"] == "ABCDE12345"


@richiede_database
async def test_il_cronjob_rinnova_solo_vicino_alla_scadenza(admin, keycloak, session_factory, session):
    pem, pubblica = chiave_p8()
    assert (await admin.put("/admin/accesso-social/apple/segreto", json={**DATI, "chiave_p8": pem})).status_code == 200
    kc = keycloak.fabbrica()()
    primo = keycloak.provider["apple"]["config"]["clientSecret"]
    assert keycloak.provider["apple"]["enabled"] is False  # nuovo e senza `abilitato`: nasce spento

    # Lontano dalla scadenza: niente.
    assert await apple_segreto.giro(session_factory, kc) is True
    assert keycloak.provider["apple"]["config"]["clientSecret"] == primo

    # A 60 giorni dalla scadenza: si rinnova.
    async with session_factory() as s:
        riga = await s.get(ConfigAccessoApple, 1)
        riga.segreto_scade_il = utcnow() + timedelta(days=60)
        await s.commit()
    assert await apple_segreto.giro(session_factory, kc) is True
    nuovo = keycloak.provider["apple"]["config"]["clientSecret"]
    assert nuovo != primo and leggi_segreto(nuovo, pubblica)["sub"] == "chat.tarots.web"

    # Keycloak giù: il giro fallisce (Job fallito) e l'esito resta annotato.
    keycloak.giu = True
    assert await apple_segreto.giro(session_factory, kc, forza=True) is False
    async with session_factory() as s:
        riga = await s.get(ConfigAccessoApple, 1)
        assert riga.esito["ok"] is False


@richiede_database
async def test_il_cronjob_senza_configurazione_non_fa_niente(keycloak, session_factory):
    assert await apple_segreto.giro(session_factory, keycloak.fabbrica()()) is True
    assert keycloak.scritture == []


# ---- il client delle app -------------------------------------------------------------------------------------------


@richiede_database
async def test_prepara_l_accesso_dall_app(admin, keycloak, monkeypatch, session):
    monkeypatch.setattr(keycloak_admin, "KeycloakAdmin", keycloak.fabbrica())
    r = await admin.post("/admin/app-mobili/accesso")
    assert r.status_code == 200, r.text
    assert r.json()["creato"] is True and r.json()["redirect"] == REDIRECT_MOBILE
    client = keycloak.client[CLIENT_MOBILE]
    assert client["publicClient"] is True and client["standardFlowEnabled"] is True
    assert client["directAccessGrantsEnabled"] is False and client["implicitFlowEnabled"] is False
    assert client["attributes"]["pkce.code.challenge.method"] == "S256"
    assert client["redirectUris"] == ["chat.tarots.app:/oauth2redirect"]
    assert [m["config"]["claim.name"] for m in client["protocolMappers"]] == ["tarots_unione"]
    # Mai `POST /clients` (403 per l'account di servizio): solo l'importazione parziale, che non tocca un client che c'è.
    assert all(s[1] != "/clients" for s in keycloak.scritture)
    r = await admin.post("/admin/app-mobili/accesso")
    assert r.json()["creato"] is False and "già" in r.json()["messaggio"]
    voci = (await session.execute(select(AuditLog).where(AuditLog.action == "app_mobili.accesso"))).scalars().all()
    assert [v.after["creato"] for v in voci] == [True, False]


def test_il_client_delle_app_e_lo_stesso_dei_realm():
    """`client_mobile()` (creato sul realm vivo) e i due file dei realm dicono la stessa cosa."""
    from pathlib import Path

    radice = Path(__file__).resolve().parents[3] / "deploy" / "keycloak"
    atteso = keycloak_admin.client_mobile()
    for nome in ("realm-tarots.json", "realm-tarots.prod.json"):
        realm = json.loads((radice / nome).read_text(encoding="utf-8"))
        c = next(c for c in realm["clients"] if c["clientId"] == CLIENT_MOBILE)
        for chiave in ("publicClient", "standardFlowEnabled", "implicitFlowEnabled", "directAccessGrantsEnabled",
                       "redirectUris"):
            assert c[chiave] == atteso[chiave], (nome, chiave)
        for chiave in ("pkce.code.challenge.method", "post.logout.redirect.uris"):
            assert c["attributes"][chiave] == atteso["attributes"][chiave], (nome, chiave)
        assert [m["config"] for m in c["protocolMappers"]] == [m["config"] for m in atteso["protocolMappers"]]
        if "optionalClientScopes" in c:
            assert "offline_access" in c["optionalClientScopes"]


@richiede_database
async def test_la_pagina_account_dice_quando_scade_il_segreto(admin, keycloak, session):
    from tarot_core.servizi_esterni import registro

    assert (await registro._sonda_segreto_apple(session))["stato"] == "da_configurare"
    pem, _ = chiave_p8()
    assert (await admin.put("/admin/accesso-social/apple/segreto", json={**DATI, "chiave_p8": pem})).status_code == 200
    session.expire_all()
    esito = await registro._sonda_segreto_apple(session)
    assert esito["stato"] == "configurato" and "valido fino al" in esito["dettaglio"]
