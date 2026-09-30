"""Lo sconto a tempo su un mazzo (v5, Fase B2): un solo sconto attivo, sparisce da solo alla scadenza."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from tarot_core.billing.mazzi import prezzo_effettivo
from tarot_core.domain.deck_models import Deck, OffertaMazzo

from .conftest import richiede_database

pytestmark = richiede_database


@pytest.fixture
def come(client, principal_utente, principal_admin):
    def scegli(chi: str):
        client.identita.principal = principal_admin if chi == "admin" else principal_utente
        return client
    return scegli


def _adesso() -> datetime:
    return datetime.now(timezone.utc)


# ---- prezzo_effettivo(), pura -------------------------------------------------------------------


def test_senza_offerta_il_prezzo_e_il_listino():
    d = Deck(nome="x", slug="x", prezzo_digitale=1000)
    p = prezzo_effettivo(d, None)
    assert p.listino == 1000 and p.scontato is None and p.offerta_attiva is False
    assert p.da_mostrare == 1000


def test_senza_prezzo_digitale_niente_da_scontare():
    d = Deck(nome="x", slug="x", prezzo_digitale=None)
    o = OffertaMazzo(deck_id=1, tipo="percentuale", valore=50)
    assert prezzo_effettivo(d, o).listino is None


@pytest.mark.parametrize(("tipo", "valore", "atteso"), [("percentuale", 20, 800), ("percentuale", 100, 0), ("importo", 300, 700), ("importo", 5000, 0)])
def test_sconto_calcolato_correttamente(tipo, valore, atteso):
    d = Deck(nome="x", slug="x", prezzo_digitale=1000)
    o = OffertaMazzo(deck_id=1, tipo=tipo, valore=valore)
    p = prezzo_effettivo(d, o)
    assert p.offerta_attiva is True
    assert p.scontato == atteso
    assert p.da_mostrare == atteso


def test_offerta_prima_della_finestra_non_si_applica():
    d = Deck(nome="x", slug="x", prezzo_digitale=1000)
    o = OffertaMazzo(deck_id=1, tipo="percentuale", valore=50, valido_dal=_adesso() + timedelta(days=1))
    p = prezzo_effettivo(d, o)
    assert p.offerta_attiva is False and p.da_mostrare == 1000


def test_offerta_scaduta_non_si_applica():
    d = Deck(nome="x", slug="x", prezzo_digitale=1000)
    o = OffertaMazzo(deck_id=1, tipo="percentuale", valore=50, valido_fino=_adesso() - timedelta(days=1))
    p = prezzo_effettivo(d, o)
    assert p.offerta_attiva is False and p.da_mostrare == 1000


def test_offerta_dentro_la_finestra_si_applica():
    d = Deck(nome="x", slug="x", prezzo_digitale=1000)
    o = OffertaMazzo(
        deck_id=1, tipo="percentuale", valore=50,
        valido_dal=_adesso() - timedelta(days=1), valido_fino=_adesso() + timedelta(days=1),
    )
    p = prezzo_effettivo(d, o)
    assert p.offerta_attiva is True and p.da_mostrare == 500


# ---- endpoint pubblico e console -----------------------------------------------------------------


async def test_il_negozio_mostra_il_prezzo_scontato(client, session):
    mazzo = Deck(nome="Scontato", slug="scontato", attivo=True, prezzo_digitale=1000)
    session.add(mazzo)
    await session.flush()
    session.add(OffertaMazzo(deck_id=mazzo.id, tipo="percentuale", valore=30))
    await session.commit()
    r = await client.get("/decks/scontato")
    assert r.status_code == 200
    dati = r.json()
    assert dati["offerta_attiva"] is True
    assert dati["prezzo_digitale_scontato"] == 700


async def test_badge_sparisce_alla_scadenza(client, session):
    mazzo = Deck(nome="Scaduto", slug="scaduto", attivo=True, prezzo_digitale=1000)
    session.add(mazzo)
    await session.flush()
    session.add(OffertaMazzo(deck_id=mazzo.id, tipo="percentuale", valore=30, valido_fino=_adesso() - timedelta(minutes=1)))
    await session.commit()
    r = await client.get("/decks/scaduto")
    dati = r.json()
    assert dati["offerta_attiva"] is False
    assert dati["prezzo_digitale_scontato"] is None


async def test_admin_crea_e_sostituisce_l_offerta(come):
    admin = come("admin")
    r0 = await admin.post("/admin/decks", json={"slug": "xx", "nome": "X", "prezzo_digitale": 1000})
    assert r0.status_code == 201, r0.text
    r = await admin.put("/admin/decks/xx/offerta", json={"tipo": "percentuale", "valore": 20})
    assert r.status_code == 200, r.text
    assert r.json()["prezzo_digitale_scontato"] == 800

    # Sostituzione, non accumulo: un secondo PUT rimpiazza, non somma.
    r = await admin.put("/admin/decks/xx/offerta", json={"tipo": "importo", "valore": 100})
    assert r.status_code == 200
    assert r.json()["prezzo_digitale_scontato"] == 900


async def test_admin_non_puo_scontare_un_mazzo_senza_prezzo(come):
    admin = come("admin")
    await admin.post("/admin/decks", json={"slug": "gratis", "nome": "Gratis"})
    r = await admin.put("/admin/decks/gratis/offerta", json={"tipo": "percentuale", "valore": 20})
    assert r.status_code == 422


async def test_admin_sconta_pdf_e_scatola_e_il_negozio_lo_mostra(come, client):
    admin = come("admin")
    await admin.post("/admin/decks", json={"slug": "st", "nome": "Stampa", "prezzo_stampa": 1000, "prezzo_fisico": 4000})
    # senza prezzo digitale, un'offerta sul digitale non ha senso
    assert (await admin.put("/admin/decks/st/offerta", json={"tipo": "percentuale", "valore": 20})).status_code == 422
    r = await admin.put("/admin/decks/st/offerta", json={"tipo": "percentuale", "valore": 20, "formati": ["pdf", "fisico"]})
    assert r.status_code == 200, r.text
    dati = (await admin.get("/decks/st")).json()
    assert dati["offerta_attiva"] is True and dati["offerta_formati"] == ["pdf", "fisico"]
    assert dati["prezzo_stampa_scontato"] == 800 and dati["prezzo_fisico_scontato"] == 3200
    assert dati["prezzo_digitale_scontato"] is None
    q = (await admin.post("/shop/quote", json={"voci": [{"deck_id": dati["id"], "tipo": "pdf"}]})).json()
    assert q["totale"] == 800


async def test_admin_rimuove_l_offerta(come):
    admin = come("admin")
    await admin.post("/admin/decks", json={"slug": "yy", "nome": "Y", "prezzo_digitale": 1000})
    await admin.put("/admin/decks/yy/offerta", json={"tipo": "percentuale", "valore": 20})
    assert (await admin.delete("/admin/decks/yy/offerta")).status_code == 204
    assert (await admin.get("/decks/yy")).json()["offerta_attiva"] is False
    assert (await admin.delete("/admin/decks/yy/offerta")).status_code == 404


async def test_percentuale_oltre_100_si_respinge(come):
    admin = come("admin")
    await admin.post("/admin/decks", json={"slug": "zz", "nome": "Z", "prezzo_digitale": 1000})
    r = await admin.put("/admin/decks/zz/offerta", json={"tipo": "percentuale", "valore": 150})
    assert r.status_code == 422
