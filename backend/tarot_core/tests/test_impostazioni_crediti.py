"""Le impostazioni dei crediti in console: default, lettura pubblica, scrittura con audit, ruolo richiesto."""
from __future__ import annotations

import pytest
from sqlalchemy import select

from tarot_core.domain.models import AuditLog

from .conftest import richiede_database

pytestmark = richiede_database


@pytest.fixture
def come(client, principal_utente, principal_admin):
    def scegli(chi: str):
        client.identita.principal = principal_admin if chi == "admin" else principal_utente
        return client

    return scegli


async def test_i_valori_predefiniti_senza_nessuna_riga_scritta(come):
    r = await come("admin").get("/admin/impostazioni-crediti")
    assert r.status_code == 200
    assert r.json() == {"crediti_iscrizione": 3, "crediti_invito": 5, "commissione_referral_percentuale": 20}


async def test_solo_l_amministratore_scrive_ma_la_lettura_pubblica_e_di_tutti(come, client):
    utente = come("utente")
    assert (await utente.get("/admin/impostazioni-crediti")).status_code == 403
    assert (await utente.put("/admin/impostazioni-crediti", json={"crediti_iscrizione": 1})).status_code == 403
    # La lettura pubblica non passa da `/admin`: non richiede alcun ruolo.
    assert (await client.get("/impostazioni-pubbliche")).status_code == 200


async def test_si_modifica_un_solo_campo_alla_volta(come):
    admin = come("admin")
    r = await admin.put("/admin/impostazioni-crediti", json={"crediti_iscrizione": 10})
    assert r.status_code == 200
    assert r.json() == {"crediti_iscrizione": 10, "crediti_invito": 5, "commissione_referral_percentuale": 20}

    r = await admin.put("/admin/impostazioni-crediti", json={"commissione_referral_percentuale": 30})
    assert r.json() == {"crediti_iscrizione": 10, "crediti_invito": 5, "commissione_referral_percentuale": 30}


async def test_i_limiti_sono_rispettati(come):
    admin = come("admin")
    assert (await admin.put("/admin/impostazioni-crediti", json={"commissione_referral_percentuale": 101})).status_code == 422
    assert (await admin.put("/admin/impostazioni-crediti", json={"crediti_invito": -1})).status_code == 422


async def test_la_lettura_pubblica_riflette_la_scrittura(come, client):
    await come("admin").put("/admin/impostazioni-crediti", json={"crediti_invito": 8})
    assert (await client.get("/impostazioni-pubbliche")).json()["crediti_invito"] == 8


async def test_la_scrittura_lascia_una_traccia_nel_registro(come, session):
    await come("admin").put("/admin/impostazioni-crediti", json={"crediti_iscrizione": 7})
    voce = (await session.execute(
        select(AuditLog).where(AuditLog.action == "impostazioni_credito.modifica")
    )).scalar_one()
    assert voce.after["crediti_iscrizione"] == 7


async def test_una_scrittura_senza_cambiamenti_non_lascia_traccia(come, session):
    admin = come("admin")
    await admin.put("/admin/impostazioni-crediti", json={"crediti_iscrizione": 3})  # è già il default
    righe = (await session.execute(
        select(AuditLog).where(AuditLog.action == "impostazioni_credito.modifica")
    )).scalars().all()
    assert righe == []
