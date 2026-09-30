"""Il rapporto settimanale (v8): composizione, invio con SMTP finto, registro, console."""
from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest

from lanterna import posta

from ..analytics import rapporto
from .conftest import richiede_database
from .test_analytics_console import _traffico, stato_pulito  # noqa: F401  (fixture autouse)

pytestmark = richiede_database


@pytest.fixture
def smtp_finto(monkeypatch):
    """Nessuna connessione vera: i messaggi finiscono in una lista."""
    from tarot_core.settings import get_settings

    inviati = []
    monkeypatch.setattr(posta, "invia", lambda config, messaggi: (inviati.extend(messaggi), {m["To"]: "ok" for m in messaggi})[1])
    monkeypatch.setenv("TAROT_SMTP_HOST", "smtp.example.test")
    monkeypatch.setenv("TAROT_SMTP_MITTENTE", "noreply@example.test")
    get_settings.cache_clear()
    yield inviati
    monkeypatch.delenv("TAROT_SMTP_HOST")
    monkeypatch.delenv("TAROT_SMTP_MITTENTE")
    get_settings.cache_clear()


@pytest.fixture
def admin(client, principal_admin):
    client.identita.principal = principal_admin
    return client


def test_settimana_conclusa():
    lunedi_notte = datetime(2026, 10, 5, 0, 30, tzinfo=ZoneInfo("Europe/Rome"))
    assert rapporto.settimana_conclusa(lunedi_notte) == (date(2026, 9, 28), date(2026, 10, 4))
    mercoledi = datetime(2026, 10, 7, 15, 0, tzinfo=ZoneInfo("Europe/Rome"))
    assert rapporto.settimana_conclusa(mercoledi) == (date(2026, 9, 28), date(2026, 10, 4))


async def test_senza_smtp_o_destinatari_non_parte_e_lo_registra(admin, session):
    esito = await rapporto.invia_rapporto(session)
    assert esito["riuscito"] is False and "SMTP" in esito["dettaglio"]
    stato = (await admin.get("/admin/analytics/rapporto")).json()
    assert stato["smtp_configurato"] is False and stato["invii"][0]["riuscito"] is False


async def test_invio_a_ogni_destinatario_con_allegato(admin, session, smtp_finto):
    await _traffico(session)
    await session.commit()
    for email in ("uno@example.test", "Due@Example.test"):
        assert (await admin.post("/admin/analytics/rapporto/destinatari", json={"email": email})).status_code == 201
    assert (await admin.post("/admin/analytics/rapporto/destinatari", json={"email": "non-valida"})).status_code == 422
    r = await admin.post("/admin/analytics/rapporto/invia")
    assert r.status_code == 200, r.text
    assert r.json()["riuscito"] is True
    assert sorted(m["To"] for m in smtp_finto) == ["due@example.test", "uno@example.test"]
    messaggio = smtp_finto[0]
    assert "rapporto settimanale" in messaggio["Subject"]
    allegati = [p.get_filename() for p in messaggio.iter_attachments()]
    assert allegati and allegati[0].endswith(".xlsx")
    corpo = messaggio.get_body(preferencelist=("html",)).get_content()
    assert "I numeri della settimana" in corpo and "198.51.100" not in corpo
    stato = (await admin.get("/admin/analytics/rapporto")).json()
    assert stato["invii"][0]["manuale"] is True and stato["invii"][0]["riuscito"] is True


async def test_con_ai_solo_voci_verificate(admin, session, smtp_finto, prompt_visti):
    await _traffico(session)
    await session.commit()
    await admin.post("/admin/analytics/rapporto/destinatari", json={"email": "uno@example.test"})
    assert (await admin.put("/admin/analytics/rapporto/opzioni", json={"ai": True})).json()["ai"] is True
    await admin.post("/admin/analytics/rapporto/invia")
    assert [p["compito"] for p in prompt_visti] == ["analisi_dati"]
    corpo = smtp_finto[0].get_body(preferencelist=("html",)).get_content()
    assert "solo voci verificate" in corpo


async def test_anteprima_e_rimozione_destinatario(admin, session):
    assert "I numeri della settimana" in (await admin.get("/admin/analytics/rapporto/anteprima")).text
    await admin.post("/admin/analytics/rapporto/destinatari", json={"email": "uno@example.test"})
    [d] = (await admin.get("/admin/analytics/rapporto")).json()["destinatari"]
    assert (await admin.delete(f"/admin/analytics/rapporto/destinatari/{d['id']}")).status_code == 204
    assert (await admin.get("/admin/analytics/rapporto")).json()["destinatari"] == []
