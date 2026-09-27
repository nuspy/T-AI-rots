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
