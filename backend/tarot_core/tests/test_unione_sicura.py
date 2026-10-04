"""L'unione con un account dall'email mai verificata: la domanda «era tuo?», la password facoltativa, la separazione.

Il collegamento e la rimozione dei vecchi accessi li fa Keycloak (passo `tarots-unione-sicura`, provato su un
Keycloak vero a parte); qui arriva solo la nota nel token (claim `tarots_unione`). Keycloak per la password è il finto
di `test_admin_accesso_social.py`.
"""
from __future__ import annotations

import pytest
from sqlalchemy import select

from tarot_core.api.routers import profile
from tarot_core.auth.keycloak import Principal
from tarot_core.billing.credits import RegistroCrediti
from tarot_core.domain.models import AuditLog, User
from tarot_core.tarot import unione_account

from .conftest import richiede_database
from .test_admin_accesso_social import keycloak  # noqa: F401 - fixture riusata

#: Collegato adesso (1760000000), account creato prima (1750000000), tolte password e OTP e il collegamento con X.
NOTA = "1760000000|1750000000|password,otp|twitter"


def test_la_nota_si_legge_o_si_ignora():
    nota = unione_account.leggi_nota({unione_account.CLAIM: NOTA})
    assert nota == {
        "id": "1760000000", "il": "2025-10-09T08:53:20+00:00", "creato_il": "2025-06-15T15:06:40+00:00",
        "credenziali": ["password", "otp"], "social": ["twitter"],
    }
    assert unione_account.leggi_nota({}) is None
    assert unione_account.leggi_nota({unione_account.CLAIM: "rotto"}) is None
    assert unione_account.leggi_nota({unione_account.CLAIM: "x|1|password|"}) is None
    solo_social = unione_account.leggi_nota({unione_account.CLAIM: "1760000000||| microsoft".replace(" ", "")})
    assert solo_social["creato_il"] is None and solo_social["credenziali"] == []


@pytest.fixture
def unito(client, keycloak, monkeypatch):  # noqa: F811
    """Una persona appena entrata con Google su un account che c'era, con l'email mai verificata."""
    monkeypatch.setattr(profile, "KeycloakAdmin", keycloak.fabbrica)
    client.identita.principal = Principal(
        subject="sub-unito", email="vera@example.com", display_name="Vera", roles={"user"},
        raw_claims={"sub": "sub-unito", "email": "vera@example.com", unione_account.CLAIM: NOTA},
    )
    return client


pytestmark = richiede_database


async def test_senza_nota_non_si_chiede_niente(client):
    r = await client.get("/me/unione")
    assert r.status_code == 200 and r.json() == {"unione": None}
    assert (await client.post("/me/unione", json={"scelta": "mia"})).status_code == 409


async def test_e_mia_con_una_password_nuova(unito, keycloak, session):  # noqa: F811
    r = await unito.get("/me/unione")
    assert r.status_code == 200, r.text
    domanda = r.json()["unione"]
    assert domanda["credenziali"] == ["password", "otp"] and domanda["social"] == ["twitter"]
    assert domanda["contenuto"]["vuoto"] is True and domanda["contenuto"]["letture"] == 0

    # La politica del realm rifiuta: la domanda resta aperta, e la password non torna mai indietro.
    r = await unito.post("/me/unione", json={"scelta": "mia", "password": "corta"})
    assert r.status_code == 422 and r.json()["detail"] == {"password": "invalidPasswordMinLengthMessage"}
    assert (await unito.get("/me/unione")).json()["unione"] is not None

    r = await unito.post("/me/unione", json={"scelta": "mia", "password": "una-password-lunga"})
    assert r.status_code == 200, r.text
    assert r.json() == {"scelta": "mia", "password": True, "nuovo_account": False}
    assert keycloak.password == {"sub-unito": "una-password-lunga"}
    # Il token porta ancora la nota (tutta la sessione): la domanda non si riapre.
    assert (await unito.get("/me/unione")).json() == {"unione": None}

    voce = (await session.execute(select(AuditLog).where(AuditLog.action == "profilo.unione"))).scalar_one()
    assert voce.after["scelta"] == "mia" and voce.after["tolti"] == ["password", "otp", "twitter"]
    assert "una-password-lunga" not in str(voce.after)


async def test_non_e_mia_si_separa_e_si_riparte(unito, session):
    await unito.get("/me/unione")
    vecchio = (await session.execute(select(User).where(User.keycloak_sub == "sub-unito"))).scalar_one()
    await RegistroCrediti(session).accredita(vecchio.id, 50, reason="acquisto", note="di chi l'aveva creato")
    await session.commit()

    domanda = (await unito.get("/me/unione")).json()["unione"]
    assert domanda["contenuto"]["vuoto"] is False and domanda["contenuto"]["acquisti"] == 1

    r = await unito.post("/me/unione", json={"scelta": "non_mia"})
    assert r.status_code == 200, r.text
    assert r.json()["nuovo_account"] is True

    separato = await session.get(User, vecchio.id, populate_existing=True)
    assert separato.keycloak_sub.startswith(unione_account.PREFISSO_SEPARATO) and separato.deleted_at is not None
    assert await RegistroCrediti(session).saldo(separato.id) >= 50  # gli acquisti restano, sulla riga separata

    nuovo = (await session.execute(select(User).where(User.keycloak_sub == "sub-unito"))).scalar_one()
    assert nuovo.id != vecchio.id and nuovo.unione_risolta == "1760000000"
    # Il nuovo account nasce come a una prima iscrizione, senza ciò che era di altri.
    assert await RegistroCrediti(session).saldo(nuovo.id) < 50
    assert (await unito.get("/me/unione")).json() == {"unione": None}
    assert (await unito.get("/me/profile")).status_code == 200
