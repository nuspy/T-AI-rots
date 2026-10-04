"""Collegare Apple e Google all'account che la persona ha già (v9, Fase 6): l'indirizzo del collegamento dal
profilo, il codice monouso che sposta le identità da un account nato nell'app, la lingua che va anche in Keycloak.
Keycloak è finto (`keycloak_finto.py`)."""
from __future__ import annotations

import base64
import hashlib
from datetime import timedelta
from urllib.parse import parse_qs, urlparse

import pytest
from sqlalchemy import select

from tarot_core.api.routers import collega as router_collega
from tarot_core.api.routers import profile as router_profilo
from tarot_core.auth.keycloak import Principal
from tarot_core.billing.credits import RegistroCrediti
from tarot_core.domain.accesso_nativo_models import CodiceCollegamento
from tarot_core.domain.models import AuditLog, User
from tarot_core.settings import get_settings
from tarot_core.tarot import collega_identita, unione_account

from .conftest import richiede_database
from .keycloak_finto import KeycloakFinto

pytestmark = richiede_database

APPLE_B = {"identityProvider": "apple", "userId": "001234.abcd.0001", "userName": "x7k2@privaterelay.appleid.com"}


@pytest.fixture
def keycloak(monkeypatch):
    finto = KeycloakFinto()
    finto.aggiungi_utente("sub-utente-1", "utente@example.com")                      # A: l'account del sito
    finto.aggiungi_utente("sub-utente-2", "x7k2@privaterelay.appleid.com", identita=[APPLE_B])  # B: nato su iPhone
    finto.provider = {
        "apple": {"alias": "apple", "enabled": True, "config": {}},
        "google": {"alias": "google", "enabled": True, "config": {}},
        "facebook": {"alias": "facebook", "enabled": True, "config": {}},
    }
    fabbrica = finto.fabbrica()
    monkeypatch.setattr(router_collega, "KeycloakAdmin", fabbrica)
    monkeypatch.setattr(router_profilo, "KeycloakAdmin", fabbrica)
    monkeypatch.setenv("TAROT_KEYCLOAK_CLIENT_SECRET", "segreto-api")
    get_settings.cache_clear()
    yield finto
    get_settings.cache_clear()


async def _codice_di_b(client, principal_altro) -> str:
    client.identita.principal = principal_altro
    r = await client.post("/me/collega/codice")
    assert r.status_code == 200, r.text
    return r.json()["codice"]


# ---- a) dal profilo del sito ---------------------------------------------------------------------------------------


async def test_stato_dei_collegamenti(client, keycloak, principal_altro):
    r = await client.get("/me/collega")
    assert r.json() == {"raggiungibile": True, "collegati": [], "collegabili": ["google", "apple"]}
    client.identita.principal = principal_altro
    r = await client.get("/me/collega")
    assert r.json()["collegati"] == ["apple"] and r.json()["collegabili"] == ["google"]
    keycloak.giu = True
    assert (await client.get("/me/collega")).json()["raggiungibile"] is False


async def test_indirizzo_del_collegamento_avviato_dal_sito(client, keycloak, principal_utente):
    client.identita.principal = Principal(
        subject=principal_utente.subject, email=principal_utente.email, roles={"user"},
        raw_claims={"sid": "sessione-123", "azp": "tarot-frontend"},
    )
    r = await client.post("/me/collega/social", json={"provider": "apple", "ritorno": "https://tarots.chat/profilo?collega=fatto"})
    assert r.status_code == 200, r.text
    url = urlparse(r.json()["url"])
    q = {k: v[0] for k, v in parse_qs(url.query).items()}
    s = get_settings()
    base = (s.keycloak_issuer_url or s.keycloak_url).rstrip("/")
    assert f"{url.scheme}://{url.netloc}{url.path}" == f"{base}/realms/{s.keycloak_realm}/broker/apple/link"
    assert q["client_id"] == "tarot-frontend" and q["redirect_uri"] == "https://tarots.chat/profilo?collega=fatto"
    # Lo stesso hash che Keycloak ricalcola: SHA-256(nonce + sessione + client + alias), base64url senza «=».
    atteso = base64.urlsafe_b64encode(
        hashlib.sha256(f"{q['nonce']}sessione-123tarot-frontendapple".encode()).digest()
    ).rstrip(b"=").decode()
    assert q["hash"] == atteso

    # Senza sessione nel token (o da un client che non è nostro) non si può.
    client.identita.principal = Principal(subject=principal_utente.subject, roles={"user"}, raw_claims={"azp": "tarot-frontend"})
    r = await client.post("/me/collega/social", json={"provider": "apple", "ritorno": "https://tarots.chat/profilo"})
    assert r.status_code == 409
    r = await client.post("/me/collega/social", json={"provider": "facebook", "ritorno": "https://tarots.chat/profilo"})
    assert r.status_code == 422


# ---- b) il codice monouso ------------------------------------------------------------------------------------------


async def test_il_codice_sposta_identita_e_dati_e_separa_il_nuovo(client, keycloak, session, principal_altro, principal_utente):
    codice = await _codice_di_b(client, principal_altro)
    assert len(codice) == 9 and codice[4] == "-" and all(c in collega_identita.ALFABETO for c in codice.replace("-", ""))
    riga = (await session.execute(select(CodiceCollegamento))).scalar_one()
    assert riga.impronta == collega_identita.impronta(codice) and codice.replace("-", "") not in riga.impronta

    b = (await session.execute(select(User).where(User.keycloak_sub == "sub-utente-2"))).scalar_one()
    b_id = b.id
    await RegistroCrediti(session).rettifica(b_id, 7, note="crediti presi nell'app")
    await session.commit()

    client.identita.principal = principal_utente
    r = await client.post("/me/collega/usa", json={"codice": codice.lower().replace("-", " ")})
    assert r.status_code == 200, r.text
    assert r.json()["provider"] == ["apple"] and r.json()["spostati"]["crediti"] >= 1

    # Keycloak: Apple ora è di A; B non ha più niente, è disattivato e le sue sessioni (anche quelle dell'app) chiuse.
    assert keycloak.identita["sub-utente-1"] == [APPLE_B] and keycloak.identita["sub-utente-2"] == []
    assert keycloak.utenti["sub-utente-2"]["enabled"] is False and "sub-utente-2" in keycloak.logout
    assert ("DELETE", "/users/sub-utente-2/consents/tarot-mobile", None) in keycloak.scritture

    # Il database: i crediti di B sono di A, B è separato come in `unione_account.separa()`.
    a_id = (await session.execute(select(User.id).where(User.keycloak_sub == "sub-utente-1"))).scalar_one()
    session.expire_all()
    b = await session.get(User, b_id)
    assert b.deleted_at is not None and b.keycloak_sub.startswith(unione_account.PREFISSO_SEPARATO)
    assert await RegistroCrediti(session).saldo(a_id) >= 7
    voce = (await session.execute(select(AuditLog).where(AuditLog.action == "collega.codice_usato"))).scalar_one()
    assert voce.after["provider"] == ["apple"] and voce.after["da_utente"] == b_id

    # Una volta sola.
    r = await client.post("/me/collega/usa", json={"codice": codice})
    assert r.status_code == 400 and r.json()["detail"]["motivo"] == "codice_non_valido"


async def test_codice_scaduto_e_codice_dello_stesso_account(client, keycloak, session, principal_altro):
    codice = await _codice_di_b(client, principal_altro)
    r = await client.post("/me/collega/usa", json={"codice": codice})  # ancora B: con sé stesso no
    assert r.status_code == 409 and r.json()["detail"]["motivo"] == "stesso_account"

    riga = (await session.execute(select(CodiceCollegamento))).scalar_one()
    riga.scade_il = riga.creato_il - timedelta(seconds=1)
    await session.commit()
    client.identita.principal = Principal(subject="sub-utente-1", email="utente@example.com", roles={"user"})
    r = await client.post("/me/collega/usa", json={"codice": codice})
    assert r.status_code == 400
    assert keycloak.identita["sub-utente-2"] == [APPLE_B]  # niente spostato


async def test_un_codice_nuovo_annulla_il_vecchio(client, keycloak, principal_altro, principal_utente):
    vecchio = await _codice_di_b(client, principal_altro)
    nuovo = await _codice_di_b(client, principal_altro)
    client.identita.principal = principal_utente
    assert (await client.post("/me/collega/usa", json={"codice": vecchio})).status_code == 400
    assert (await client.post("/me/collega/usa", json={"codice": nuovo})).status_code == 200


async def test_senza_identita_social_non_c_e_niente_da_spostare(client, keycloak):
    r = await client.post("/me/collega/codice")  # A non ha social collegati
    assert r.status_code == 409 and r.json()["detail"]["motivo"] == "nessuna_identita"


async def test_un_apple_id_gia_collegato_non_si_sovrascrive(client, keycloak, principal_altro, principal_utente):
    keycloak.identita["sub-utente-1"] = [{"identityProvider": "apple", "userId": "altro-apple", "userName": ""}]
    codice = await _codice_di_b(client, principal_altro)
    client.identita.principal = principal_utente
    r = await client.post("/me/collega/usa", json={"codice": codice})
    assert r.status_code == 409 and r.json()["detail"] == {"motivo": "gia_collegato", "provider": ["apple"]}
    assert keycloak.identita["sub-utente-2"] == [APPLE_B]


async def test_keycloak_che_fallisce_a_meta_rimette_tutto_com_era(client, keycloak, session, principal_altro, principal_utente):
    codice = await _codice_di_b(client, principal_altro)
    keycloak.collega_fallisce_per = "sub-utente-1"
    client.identita.principal = principal_utente
    r = await client.post("/me/collega/usa", json={"codice": codice})
    assert r.status_code == 502 and r.json()["detail"]["motivo"] == "keycloak"
    assert keycloak.identita["sub-utente-2"] == [APPLE_B] and keycloak.identita["sub-utente-1"] == []
    session.expire_all()
    b = (await session.execute(select(User).where(User.keycloak_sub == "sub-utente-2"))).scalar_one()
    assert b.deleted_at is None  # il database è tornato indietro
    riga = (await session.execute(select(CodiceCollegamento))).scalar_one()
    assert riga.usato_il is None
    # Rimesso a posto Keycloak, lo stesso codice funziona.
    keycloak.collega_fallisce_per = None
    assert (await client.post("/me/collega/usa", json={"codice": codice})).status_code == 200


async def test_troppi_tentativi_sbagliati(client, keycloak, monkeypatch):
    monkeypatch.setattr(collega_identita, "TENTATIVI_ORA", 3)
    for _ in range(3):
        r = await client.post("/me/collega/usa", json={"codice": "AAAA-BBBB"})
        assert r.status_code == 400
    r = await client.post("/me/collega/usa", json={"codice": "AAAA-BBBB"})
    assert r.status_code == 429 and r.json()["detail"]["motivo"] == "troppi_tentativi"


# ---- la lingua anche in Keycloak ------------------------------------------------------------------------------------


async def test_la_lingua_del_profilo_va_in_keycloak(client, keycloak):
    r = await client.patch("/me/profile", json={"locale": "hu"})
    assert r.status_code == 200, r.text
    assert keycloak.utenti["sub-utente-1"]["attributes"] == {"locale": ["hu"]}
    # Una lingua del sito che il realm non ha: l'inglese, la predefinita di Keycloak.
    await client.patch("/me/profile", json={"locale": "de"})
    assert keycloak.utenti["sub-utente-1"]["attributes"] == {"locale": ["en"]}
    # La rappresentazione mandata è intera (Keycloak 26 rifiuta un PUT senza email).
    put = [s for s in keycloak.scritture if s[0] == "PUT" and s[1] == "/users/sub-utente-1"]
    assert put and all(s[2]["email"] == "utente@example.com" for s in put)


async def test_keycloak_giu_non_ferma_il_profilo(client, keycloak):
    keycloak.giu = True
    r = await client.patch("/me/profile", json={"locale": "es"})
    assert r.status_code == 200 and r.json()["locale"] == "es"


async def test_senza_cambio_di_lingua_keycloak_non_si_tocca(client, keycloak):
    await client.patch("/me/profile", json={"nome": "Maria"})
    assert not [s for s in keycloak.scritture if s[1] == "/users/sub-utente-1"]
