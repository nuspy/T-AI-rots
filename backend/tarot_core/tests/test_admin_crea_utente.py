"""La console crea un utente a mano: in Keycloak (email + password) e subito nel database, con il piano gratuito.
Keycloak è finto (`keycloak_finto.py`)."""
from __future__ import annotations

import pytest
from sqlalchemy import select

from tarot_core.api.routers import admin as router_admin
from tarot_core.domain.models import AuditLog, User
from tarot_core.settings import get_settings

from .conftest import richiede_database
from .keycloak_finto import KeycloakFinto

pytestmark = richiede_database


@pytest.fixture
def keycloak(monkeypatch):
    finto = KeycloakFinto()
    monkeypatch.setattr(router_admin, "KeycloakAdmin", finto.fabbrica())
    monkeypatch.setenv("TAROT_KEYCLOAK_CLIENT_SECRET", "segreto-api")
    get_settings.cache_clear()
    yield finto
    get_settings.cache_clear()


@pytest.fixture
def come(client, principal_utente, principal_admin):
    def scegli(chi: str):
        client.identita.principal = principal_admin if chi == "admin" else principal_utente
        return client

    return scegli


NUOVO = {"email": "Nuova.Persona@Example.com", "password": "una-password-lunga", "nome": "Nuova"}


async def test_solo_un_amministratore_crea_utenti(come, keycloak, catalogo):
    assert (await come("utente").post("/admin/users", json=NUOVO)).status_code == 403
    assert keycloak.utenti == {}


async def test_crea_in_keycloak_e_nel_database_col_piano_gratuito(come, keycloak, catalogo, session):
    r = await come("admin").post("/admin/users", json=NUOVO)
    assert r.status_code == 201, r.text
    dati = r.json()
    assert dati["email"] == "nuova.persona@example.com" and dati["display_name"] == "Nuova" and dati["attivo"]

    # In Keycloak: email come nome utente, password definitiva, email verificata.
    (sub, kc), = keycloak.utenti.items()
    assert kc["email"] == "nuova.persona@example.com" and kc["enabled"]
    metodo, percorso, corpo = keycloak.scritture[-1]
    assert (metodo, percorso) == ("POST", "/users")
    assert corpo["username"] == corpo["email"] and corpo["emailVerified"] is True
    assert corpo["credentials"] == [{"type": "password", "value": NUOVO["password"], "temporary": False}]

    # Nel database, agganciato alla `sub` di Keycloak, e visibile nell'elenco con un piano.
    riga = (await session.execute(select(User).where(User.keycloak_sub == sub))).scalar_one()
    assert riga.id == dati["id"]
    elenco = (await come("admin").get("/admin/users", params={"q": "nuova.persona"})).json()["utenti"]
    assert [u["id"] for u in elenco] == [dati["id"]] and elenco[0]["piano"]


async def test_la_creazione_resta_nel_registro_senza_la_password(come, keycloak, catalogo, session):
    await come("admin").post("/admin/users", json=NUOVO)
    voce = (await session.execute(select(AuditLog).where(AuditLog.action == "user.create"))).scalar_one()
    assert voce.after["email"] == "nuova.persona@example.com"
    assert NUOVO["password"] not in str(voce.after) and NUOVO["password"] not in str(voce.before)


async def test_email_gia_usata(come, keycloak, catalogo):
    admin = come("admin")
    assert (await admin.post("/admin/users", json=NUOVO)).status_code == 201
    r = await admin.post("/admin/users", json=NUOVO)
    assert r.status_code == 409 and "già" in r.json()["detail"]


async def test_password_rifiutata_dal_realm(come, keycloak, catalogo):
    r = await come("admin").post("/admin/users", json={**NUOVO, "password": "corta"})
    assert r.status_code == 400 and "invalidPasswordMinLengthMessage" in r.json()["detail"]
    assert keycloak.utenti == {}


async def test_email_non_valida(come, keycloak, catalogo):
    assert (await come("admin").post("/admin/users", json={**NUOVO, "email": "senza-chiocciola"})).status_code == 422


async def test_keycloak_spento(come, keycloak, catalogo):
    keycloak.giu = True
    r = await come("admin").post("/admin/users", json=NUOVO)
    assert r.status_code == 502


async def _database_che_fallisce(monkeypatch):
    from tarot_core.domain.admin_repositories import AdminUserRepository

    async def rotto(self, utente):
        raise RuntimeError("database giù")

    monkeypatch.setattr(AdminUserRepository, "registra_creazione", rotto)


async def test_se_il_database_fallisce_l_utente_sparisce_da_keycloak(come, keycloak, catalogo, session, monkeypatch):
    await _database_che_fallisce(monkeypatch)
    r = await come("admin").post("/admin/users", json=NUOVO)
    assert r.status_code == 500 and "Keycloak" not in r.json()["detail"]
    assert keycloak.utenti == {}
    assert (await session.execute(select(User).where(User.email == "nuova.persona@example.com"))).first() is None
    # Ritentare dopo il guasto funziona: l'email non è rimasta occupata in Keycloak.
    monkeypatch.undo()
    monkeypatch.setattr(router_admin, "KeycloakAdmin", keycloak.fabbrica())
    assert (await come("admin").post("/admin/users", json=NUOVO)).status_code == 201


async def test_se_nemmeno_la_cancellazione_riesce_lo_dice(come, keycloak, catalogo, monkeypatch):
    await _database_che_fallisce(monkeypatch)
    keycloak.cancella_fallisce = True
    r = await come("admin").post("/admin/users", json=NUOVO)
    assert r.status_code == 500 and "rimasto in Keycloak" in r.json()["detail"]
    assert len(keycloak.utenti) == 1
