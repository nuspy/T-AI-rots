"""Il consenso GDPR (v7, Fase G): stato corrente sovrascritto, storia intatta nell'audit,
IP/data/ora tracciati per ricostruire la paternità della scelta."""
from __future__ import annotations

from sqlalchemy import select

from tarot_core.domain.consent_models import UserConsent
from tarot_core.domain.models import AuditLog

from .conftest import richiede_database

pytestmark = richiede_database

VERSIONE = "v1"


async def test_un_secondo_consenso_sovrascrive_lo_stato_ma_raddoppia_l_audit(client, session, utente):
    r1 = await client.post("/consenso", json={"tipo": "cookie", "valore": "rifiutato", "versione_informativa": VERSIONE})
    assert r1.status_code == 200, r1.text
    r2 = await client.post("/consenso", json={"tipo": "cookie", "valore": "accettato", "versione_informativa": VERSIONE})
    assert r2.status_code == 200, r2.text

    righe = (await session.execute(
        select(UserConsent).where(UserConsent.user_id == utente.id, UserConsent.tipo == "cookie")
    )).scalars().all()
    assert len(righe) == 1
    assert righe[0].valore == "accettato"

    eventi = (await session.execute(
        select(AuditLog).where(AuditLog.action == "consenso.cookie", AuditLog.actor_id == utente.id)
    )).scalars().all()
    assert len(eventi) == 2
    assert eventi[0].ip is not None and eventi[0].created_at is not None


async def test_get_consenso_riporta_none_per_un_tipo_mai_deciso(client):
    r = await client.get("/consenso")
    assert r.status_code == 200
    assert r.json() == {"cookie": None, "condivisione_dati_partner": None}


async def test_get_consenso_dopo_una_scelta(client):
    await client.post("/consenso", json={"tipo": "cookie", "valore": "accettato", "versione_informativa": VERSIONE})
    r = await client.get("/consenso")
    assert r.json()["cookie"] == "accettato"
    assert r.json()["condivisione_dati_partner"] is None


async def test_un_visitatore_anonimo_puo_dare_il_consenso_cookie(client):
    client.identita.principal = None
    r = await client.post("/consenso", json={"tipo": "cookie", "valore": "accettato", "versione_informativa": VERSIONE})
    assert r.status_code == 200, r.text
    assert "tarots_anon" in r.cookies

    r2 = await client.get("/consenso")
    assert r2.json()["cookie"] == "accettato"


async def test_un_secondo_anonimo_non_eredita_il_consenso_del_primo(client):
    client.identita.principal = None
    await client.post("/consenso", json={"tipo": "cookie", "valore": "accettato", "versione_informativa": VERSIONE})
    client.cookies.clear()
    r = await client.get("/consenso")
    assert r.json()["cookie"] is None
