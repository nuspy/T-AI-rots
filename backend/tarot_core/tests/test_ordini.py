"""Il carrello del negozio mazzi (v5, Fase B3): sconto per-mazzo, sconto a scaglioni, e l'acquisto
dall'apertura al pagamento — con il simulatore, come già per i piani."""
from __future__ import annotations

import pytest
from sqlalchemy import func, select

from tarot_core.billing.credits import RegistroCrediti
from tarot_core.billing.ordini import CarrelloNonValido, VoceCarrello, calcola_carrello
from tarot_core.domain.deck_models import Deck, DeckUnlock, OffertaMazzo
from tarot_core.domain.repositories import UserRepository

from .conftest import richiede_database

pytestmark = richiede_database


async def _accredita(session, principal, quanti=1000):
    utente = await UserRepository(session).ensure(principal)
    await RegistroCrediti(session).accredita(utente.id, quanti, reason="omaggio", note="prova")
    await session.commit()
    return utente


# ---- calcola_carrello(), pura --------------------------------------------------------------------


def _mazzo(id_, prezzo_digitale=1000, prezzo_stampa=None, prezzo_fisico=None):
    d = Deck(nome=f"m{id_}", slug=f"m{id_}", prezzo_digitale=prezzo_digitale, prezzo_stampa=prezzo_stampa, prezzo_fisico=prezzo_fisico)
    d.id = id_
    return d


def test_un_solo_mazzo_nessuno_sconto_a_scaglioni():
    decks = {1: _mazzo(1)}
    r = calcola_carrello([VoceCarrello(deck_id=1, tipo="digitale")], decks, {})
    assert r.scaglione_percentuale == 0
    assert r.subtotale == 1000 and r.totale == 1000


@pytest.mark.parametrize(("n_mazzi", "percentuale"), [(1, 0), (2, 10), (3, 20), (4, 30), (5, 40), (6, 50), (10, 50)])
def test_scaglione_cresce_con_i_mazzi_diversi_fino_al_tetto(n_mazzi, percentuale):
    decks = {i: _mazzo(i, prezzo_digitale=1000) for i in range(1, n_mazzi + 1)}
    voci = [VoceCarrello(deck_id=i, tipo="digitale") for i in range(1, n_mazzi + 1)]
    r = calcola_carrello(voci, decks, {})
    assert r.scaglione_percentuale == percentuale
    subtotale = 1000 * n_mazzi
    sconto_atteso = (subtotale * percentuale + 50) // 100
    assert r.sconto_scaglioni == sconto_atteso
    assert r.totale == subtotale - sconto_atteso


def test_piu_copie_dello_stesso_mazzo_non_alzano_lo_scaglione():
    decks = {1: _mazzo(1, prezzo_digitale=1000)}
    r = calcola_carrello([VoceCarrello(deck_id=1, tipo="digitale", quantita=3)], decks, {})
    assert r.scaglione_percentuale == 0
    assert r.subtotale == 3000 and r.totale == 3000


def test_lo_sconto_per_mazzo_si_applica_prima_dello_scaglione():
    decks = {1: _mazzo(1, prezzo_digitale=1000), 2: _mazzo(2, prezzo_digitale=1000)}
    offerte = {1: OffertaMazzo(deck_id=1, tipo="percentuale", valore=50)}  # 1000 -> 500
    r = calcola_carrello(
        [VoceCarrello(deck_id=1, tipo="digitale"), VoceCarrello(deck_id=2, tipo="digitale")], decks, offerte,
    )
    # Subtotale dopo lo sconto per-mazzo: 500 + 1000 = 1500. Poi il 10% di scaglione (2 mazzi diversi).
    assert r.subtotale == 1500
    assert r.scaglione_percentuale == 10
    assert r.sconto_scaglioni == 150
    assert r.totale == 1350


def test_prodotto_non_offerto_si_respinge():
    decks = {1: _mazzo(1, prezzo_digitale=None)}
    with pytest.raises(CarrelloNonValido):
        calcola_carrello([VoceCarrello(deck_id=1, tipo="digitale")], decks, {})


def test_carrello_vuoto_si_respinge():
    with pytest.raises(CarrelloNonValido):
        calcola_carrello([], {}, {})


def test_offerta_non_si_applica_a_pdf_o_fisico():
    decks = {1: _mazzo(1, prezzo_digitale=1000, prezzo_stampa=500)}
    offerte = {1: OffertaMazzo(deck_id=1, tipo="percentuale", valore=50)}
    r = calcola_carrello([VoceCarrello(deck_id=1, tipo="pdf")], decks, offerte)
    assert r.righe[0].prezzo_finale_unitario == 500  # non scontato: l'offerta vale solo sul digitale


# ---- l'ordine, dall'apertura al pagamento (col simulatore) ----------------------------------------


async def test_apertura_respinge_un_mazzo_non_attivo(client, session):
    mazzo = Deck(nome="Spento", slug="spento", attivo=False, prezzo_digitale=1000)
    session.add(mazzo)
    await session.commit()
    r = await client.post("/orders", json={"voci": [{"deck_id": mazzo.id, "tipo": "digitale"}]})
    assert r.status_code == 422


async def test_apertura_respinge_il_fisico_non_ancora_disponibile(client, session):
    mazzo = Deck(nome="Fisico", slug="fisico", attivo=True, prezzo_fisico=3000)
    session.add(mazzo)
    await session.commit()
    r = await client.post("/orders", json={"voci": [{"deck_id": mazzo.id, "tipo": "fisico"}]})
    assert r.status_code == 422


async def test_acquisto_completo_sblocca_il_mazzo(client, session):
    await _accredita(session, client.identita.principal)  # non serve per pagare l'ordine, solo per avere l'utente
    mazzo = Deck(nome="Da comprare", slug="da-comprare", attivo=True, prezzo_digitale=1000)
    session.add(mazzo)
    await session.commit()

    r = await client.post("/orders", json={"voci": [{"deck_id": mazzo.id, "tipo": "digitale"}]})
    assert r.status_code == 201, r.text
    dati = r.json()
    assert dati["status"] == "aperto" and dati["importo_totale"] == 1000
    ordine_id = dati["id"]

    # La pagina simulata esiste ed è raggiungibile.
    pagina = await client.get(f"/billing/mock/ordine/{ordine_id}")
    assert pagina.status_code == 200

    # Il clic su «Paga»: applica l'evento come farebbe il webhook del fornitore vero.
    esito = await client.post(f"/billing/mock/ordine/{ordine_id}/esito", data={"esito": "paga", "ritorno": "/mazzo"})
    assert esito.status_code == 303

    dettaglio = await client.get(f"/me/orders/{ordine_id}")
    assert dettaglio.json()["status"] == "pagato"

    utente = await UserRepository(session).ensure(client.identita.principal)
    riga = (await session.execute(
        select(DeckUnlock).where(DeckUnlock.user_id == utente.id, DeckUnlock.deck_id == mazzo.id),
    )).scalar_one_or_none()
    assert riga is not None

    # Ora la lettura con questo mazzo funziona.
    from tarot_core.tools.seed import scrivi_catalogo
    await scrivi_catalogo(session)
    await session.commit()
    r2 = await client.post("/readings", json={"spread_id": "tre-carte", "question": "Domanda?", "deck_id": mazzo.slug})
    assert r2.status_code == 201, r2.text


async def test_un_evento_ripetuto_non_sblocca_due_volte(client, session):
    mazzo = Deck(nome="Idempotente", slug="idempotente", attivo=True, prezzo_digitale=1000)
    session.add(mazzo)
    await session.commit()
    r = await client.post("/orders", json={"voci": [{"deck_id": mazzo.id, "tipo": "digitale"}]})
    ordine_id = r.json()["id"]
    await client.post(f"/billing/mock/ordine/{ordine_id}/esito", data={"esito": "paga", "ritorno": "/mazzo"})
    await client.post(f"/billing/mock/ordine/{ordine_id}/esito", data={"esito": "paga", "ritorno": "/mazzo"})

    utente = await UserRepository(session).ensure(client.identita.principal)
    n = await session.scalar(
        select(func.count()).select_from(DeckUnlock).where(DeckUnlock.user_id == utente.id, DeckUnlock.deck_id == mazzo.id),
    )
    assert n == 1


async def test_un_ordine_annullato_non_sblocca(client, session):
    mazzo = Deck(nome="Annullato", slug="annullato", attivo=True, prezzo_digitale=1000)
    session.add(mazzo)
    await session.commit()
    r = await client.post("/orders", json={"voci": [{"deck_id": mazzo.id, "tipo": "digitale"}]})
    ordine_id = r.json()["id"]
    await client.post(f"/billing/mock/ordine/{ordine_id}/esito", data={"esito": "annulla", "ritorno": "/mazzo"})
    dettaglio = await client.get(f"/me/orders/{ordine_id}")
    assert dettaglio.json()["status"] == "annullato"


# ---- GET /me/decks: cosa possiede già chi chiede ---------------------------------------------------


async def test_i_miei_mazzi_include_il_predefinito_senza_sblocco(client, session):
    predefinito = Deck(nome="Thoth", slug="thoth-test", predefinito=True, attivo=True)
    altro = Deck(nome="Altro", slug="altro-non-posseduto", attivo=True, prezzo_digitale=1000)
    session.add_all([predefinito, altro])
    await session.commit()

    r = await client.get("/me/decks")
    assert r.status_code == 200
    ids = r.json()["deck_ids"]
    assert predefinito.id in ids
    assert altro.id not in ids


async def test_i_miei_mazzi_include_uno_sbloccato_da_un_ordine_pagato(client, session):
    mazzo = Deck(nome="Da comprare", slug="da-comprare-2", attivo=True, prezzo_digitale=1000)
    session.add(mazzo)
    await session.commit()
    r = await client.post("/orders", json={"voci": [{"deck_id": mazzo.id, "tipo": "digitale"}]})
    ordine_id = r.json()["id"]
    await client.post(f"/billing/mock/ordine/{ordine_id}/esito", data={"esito": "paga", "ritorno": "/mazzo"})

    r2 = await client.get("/me/decks")
    assert mazzo.id in r2.json()["deck_ids"]


# ---- preventivo pubblico e pagamenti disattivati (v8.5) -------------------------------------------------------


async def test_il_preventivo_si_calcola_senza_account_e_non_scrive_niente(client, session):
    from tarot_core.domain.ordini_models import Ordine

    a = Deck(nome="A", slug="prev-a", attivo=True, prezzo_stampa=990, prezzo_fisico=3900)
    b = Deck(nome="B", slug="prev-b", attivo=True, prezzo_stampa=1000)
    session.add_all([a, b])
    await session.commit()
    client.identita.principal = None
    r = await client.post("/shop/quote", json={"voci": [
        {"deck_id": a.id, "tipo": "fisico"}, {"deck_id": a.id, "tipo": "pdf"}, {"deck_id": b.id, "tipo": "pdf", "quantita": 2},
    ]})
    assert r.status_code == 200, r.text
    q = r.json()
    assert q["subtotale"] == 3900 + 990 + 2000 and q["scaglione_percentuale"] == 10
    assert q["totale"] == q["subtotale"] - q["sconto_scaglioni"] and q["richiede_indirizzo"] is True
    assert [x["prezzo_finale_unitario"] for x in q["righe"]] == [3900, 990, 1000]
    assert (await session.execute(select(func.count()).select_from(Ordine))).scalar_one() == 0
    # un formato che il mazzo non offre
    assert (await client.post("/shop/quote", json={"voci": [{"deck_id": b.id, "tipo": "fisico"}]})).status_code == 422


@pytest.fixture
def pagamenti_disattivati(monkeypatch):
    from tarot_core.settings import get_settings

    monkeypatch.setenv("TAROT_BILLING_PROVIDER", "disattivato")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


async def test_con_i_pagamenti_disattivati_l_ordine_si_registra_in_attesa(client, session, pagamenti_disattivati):
    await _accredita(session, client.identita.principal)
    mazzo = Deck(nome="Da stampare", slug="da-stampare", attivo=True, prezzo_stampa=990)
    session.add(mazzo)
    await session.commit()
    q = (await client.post("/shop/quote", json={"voci": [{"deck_id": mazzo.id, "tipo": "pdf"}]})).json()
    assert q["pagamento_attivo"] is False
    r = await client.post("/orders", json={"voci": [{"deck_id": mazzo.id, "tipo": "pdf"}], "ritorno": "/v2/cart"})
    assert r.status_code == 201, r.text
    dati = r.json()
    assert dati["url"] is None and dati["pagamento_attivo"] is False
    assert dati["status"] == "aperto" and dati["importo_totale"] == 990
    elenco = (await client.get("/me/orders")).json()
    assert any(o["id"] == dati["id"] and o["status"] == "aperto" for o in elenco["ordini"])
    # il PDF non si scarica finché l'ordine non è pagato
    assert (await client.get(f"/me/orders/{dati['id']}/pdf/{mazzo.id}")).status_code == 403
