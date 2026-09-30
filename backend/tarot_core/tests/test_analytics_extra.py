"""Annotazioni, obiettivi, avvisi automatici e tempo reale (v8). Modello finto, SMTP finto."""
from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import select

from lanterna import posta

from ..analytics import avvisi
from ..domain.analytics_models import TABELLE
from .conftest import richiede_database
from .test_analytics_console import IPHONE, _visita, stato_pulito  # noqa: F401  (fixture autouse)
from .test_analytics_rapporto import smtp_finto  # noqa: F401  (fixture)

pytestmark = richiede_database

OGGI = datetime.now(ZoneInfo("Europe/Rome")).date()


@pytest.fixture
def admin(client, principal_admin):
    client.identita.principal = principal_admin
    return client


# ---- annotazioni -----------------------------------------------------------------------------------


async def test_annotazioni_in_console_nei_fatti_e_nel_rapporto(admin, session, prompt_visti):
    r = await admin.post("/admin/analytics/annotazioni", json={
        "giorno": (OGGI - timedelta(days=3)).isoformat(), "tipo": "campagna", "titolo": "Campagna Instagram autunno",
    })
    assert r.status_code == 201, r.text
    assert (await admin.post("/admin/analytics/annotazioni", json={
        "giorno": OGGI.isoformat(), "fine": (OGGI - timedelta(days=1)).isoformat(), "titolo": "x",
    })).status_code == 422
    elenco = (await admin.get(f"/admin/analytics/annotazioni?da={(OGGI - timedelta(days=7)).isoformat()}&a={OGGI.isoformat()}")).json()
    assert [a["titolo"] for a in elenco] == ["Campagna Instagram autunno"]

    analisi = (await admin.post("/admin/analytics/analizza", json={"sezione": "traffico", "giorni": 7})).json()
    # Il calendario viene per primo: non cade sotto il tetto dei fatti.
    assert analisi["fatti"][0]["sezione"] == "Calendario" and "Campagna Instagram autunno" in analisi["fatti"][0]["testo"]
    assert "Campagna Instagram autunno" in prompt_visti[-1]["utente"]

    assert (await admin.delete(f"/admin/analytics/annotazioni/{elenco[0]['id']}")).status_code == 204
    assert (await admin.get("/admin/analytics/annotazioni")).json() == []


async def test_annotazione_nel_rapporto_della_settimana(admin, session):
    from ..analytics.rapporto import settimana_conclusa

    da, _ = settimana_conclusa()
    await admin.post("/admin/analytics/annotazioni", json={"giorno": da.isoformat(), "tipo": "rilascio", "titolo": "Nuova home"})
    html = (await admin.get("/admin/analytics/rapporto/anteprima")).text
    assert "In calendario" in html and "Nuova home" in html


# ---- obiettivi -------------------------------------------------------------------------------------


async def test_obiettivi_configurabili(admin, session):
    await _visita(session, "198.51.100.30", IPHONE, {"n": "page_view", "p": "/pricing"}, {"n": "piano_scelto", "p": "/pricing"})
    await _visita(session, "198.51.100.31", IPHONE, {"n": "page_view", "p": "/it/piano"})
    await _visita(session, "198.51.100.32", IPHONE, {"n": "page_view", "p": "/blog"})
    await session.commit()
    for corpo in (
        {"nome": "Vede i prezzi", "tipo": "pagina", "valore": "/pricing,/it/piano"},
        {"nome": "Sceglie un piano", "tipo": "evento", "valore": "piano_scelto"},
    ):
        assert (await admin.post("/admin/analytics/obiettivi", json=corpo)).status_code == 201
    assert (await admin.post("/admin/analytics/obiettivi", json={"nome": "x", "tipo": "pagina", "valore": "pricing"})).status_code == 422
    assert (await admin.post("/admin/analytics/obiettivi", json={"nome": "x", "tipo": "evento", "valore": "drop table"})).status_code == 422
    r = (await admin.get("/admin/analytics/obiettivi?giorni=7")).json()
    per_nome = {o["nome"]: o for o in r["obiettivi"]}
    assert per_nome["Vede i prezzi"]["sessioni"] == 2 and per_nome["Vede i prezzi"]["tasso"] == round(2 / 3, 4)
    assert per_nome["Sceglie un piano"]["sessioni"] == 1
    analisi = (await admin.post("/admin/analytics/analizza", json={"sezione": "traffico", "giorni": 7})).json()
    assert any(f["sezione"] == "Obiettivi" and "Vede i prezzi" in f["testo"] for f in analisi["fatti"])
    assert (await admin.delete(f"/admin/analytics/obiettivi/{per_nome['Vede i prezzi']['id']}")).status_code == 204


# ---- avvisi ----------------------------------------------------------------------------------------


def _serie_finta(crollo: str):
    async def serie(session, sorgente, misura, filtri, da, a):
        giorni = [(da + timedelta(days=i)).isoformat() for i in range((a - da).days + 1)]
        valori = {g: 40.0 + (i % 3) for i, g in enumerate(giorni)}
        if sorgente == "eventi":  # errori del modello: di solito nessuno
            valori = {g: 0.0 for g in giorni}
        if misura == crollo:
            valori[a.isoformat()] = 0.0
        return valori
    return serie


async def test_avviso_quando_ieri_esce_dal_normale(admin, session, smtp_finto, monkeypatch):
    monkeypatch.setattr(avvisi, "serie_giornaliera", _serie_finta("completate"))
    await admin.post("/admin/analytics/rapporto/destinatari", json={"email": "uno@example.test"})
    controllo = (await admin.get("/admin/analytics/avvisi")).json()
    assert [a["metrica"] for a in controllo["avvisi"]] == ["letture_completate"]
    assert not smtp_finto  # il controllo dalla console non invia

    esito = await avvisi.controlla_e_avvisa(session)
    assert esito["inviato"] is True
    [messaggio] = smtp_finto
    assert "avviso" in messaggio["Subject"] and "Letture completate: 0 ieri" in messaggio.get_body(("plain",)).get_content()
    stato = (await admin.get("/admin/analytics/rapporto")).json()
    assert stato["invii"][0]["tipo"] == "avviso"


async def test_nessun_avviso_nel_normale_o_con_avvisi_spenti(admin, session, smtp_finto, monkeypatch):
    monkeypatch.setattr(avvisi, "serie_giornaliera", _serie_finta("nessuna"))
    assert (await avvisi.controlla_e_avvisa(session))["avvisi"] == []
    monkeypatch.setattr(avvisi, "serie_giornaliera", _serie_finta("sessioni"))
    await admin.post("/admin/analytics/rapporto/destinatari", json={"email": "uno@example.test"})
    await admin.put("/admin/analytics/rapporto/opzioni", json={"ai": False, "avvisi": False})
    esito = await avvisi.controlla_e_avvisa(session)
    assert esito["avvisi"] and esito["inviato"] is False and not smtp_finto


async def test_le_serie_vere_si_calcolano(session):
    # Senza finzioni: tutte le metriche si interrogano davvero (anche a database vuoto).
    ieri, trovati = await avvisi.controlla(session)
    assert ieri == OGGI - timedelta(days=1) and trovati == []


async def test_un_responso_non_generato_diventa_un_evento(client, session, catalogo, monkeypatch):
    from tarot_core.tarot.finto import ModelloFinto, _compito

    from .test_flusso import _accredita, _lettura_completa

    await _accredita(session, client.identita.principal)
    originale = ModelloFinto._rispondi
    monkeypatch.setattr(ModelloFinto, "_rispondi", lambda self, req: "" if _compito(req) == "sintesi" else originale(self, req))
    with pytest.raises(AssertionError):  # la lettura non arriva al responso
        await _lettura_completa(client, "tre-carte", 3)
    e = TABELLE.eventi
    righe = (await session.execute(select(e.c.nome, e.c.proprieta).where(e.c.nome == "lettura_errore"))).all()
    assert len(righe) == 1 and righe[0].proprieta["stesa"] == "tre-carte"


# ---- tempo reale -----------------------------------------------------------------------------------


async def test_tempo_reale(admin, session):
    await _visita(session, "198.51.100.40", IPHONE, {"n": "page_view", "p": "/leggi", "r": "https://www.google.com/"})
    await _visita(session, "198.51.100.41", IPHONE, {"n": "page_view", "p": "/blog"},
                  quando=datetime.now(timezone.utc) - timedelta(hours=2))
    await session.commit()
    r = (await admin.get("/admin/analytics/tempo-reale")).json()
    assert r["sessioni_attive"] == 1
    assert r["pagine"] == [{"valore": "/leggi", "sessioni": 1}] and r["canali"][0]["valore"] == "ricerca"
    assert sum(p["pagine"] for p in r["pagine_per_minuto"]) == 1
    assert "198.51.100" not in json.dumps(r)
    assert isinstance(date.fromisoformat(r["pagine_per_minuto"][0]["minuto"][:10]), date)
