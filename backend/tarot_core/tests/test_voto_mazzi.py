"""Vota il prossimo mazzo (v7, Fase K) e le sue estensioni "tornate elettorali": riserva di
proposte selezionabili alla creazione, scadenza dichiarata con chiusura automatica, generazione di
un mazzo anche per un candidato non vincitore, suggerimenti di tema dagli iscritti."""
from __future__ import annotations

import uuid
from datetime import timedelta

import pytest
from sqlalchemy import select

from tarot_core.domain.base import utcnow
from tarot_core.domain.deck_models import Deck
from tarot_core.domain.voting_models import DeckCandidate, DeckSuggestion, DeckVote, VotingRound

from .conftest import richiede_database

pytestmark = richiede_database


@pytest.fixture
def come(client, principal_utente, principal_admin):
    def scegli(chi: str):
        client.identita.principal = principal_admin if chi == "admin" else principal_utente
        return client
    return scegli


def _tra_un_ora() -> str:
    return (utcnow() + timedelta(hours=1)).isoformat()


async def _due_proposte_in_riserva(admin) -> tuple[str, str]:
    c1 = (await admin.post("/admin/voto/candidati", json={"nome": "Uno"})).json()
    c2 = (await admin.post("/admin/voto/candidati", json={"nome": "Due"})).json()
    return c1["id"], c2["id"]


async def _tornata_con_due_candidati(admin) -> tuple[str, str, str]:
    c1, c2 = await _due_proposte_in_riserva(admin)
    r = await admin.post("/admin/voto/tornate", json={"candidate_ids": [c1, c2], "chiude_il": _tra_un_ora()})
    return r.json()["id"], c1, c2


async def test_un_secondo_voto_sostituisce_il_primo_non_lo_somma(come, session):
    admin = come("admin")
    round_id, c1, c2 = await _tornata_con_due_candidati(admin)
    utente = come("utente")
    assert (await utente.post(f"/voto/mazzi/{c1}")).status_code == 200
    assert (await utente.post(f"/voto/mazzi/{c2}")).status_code == 200

    voti = (await session.execute(select(DeckVote))).scalars().all()
    assert len(voti) == 1
    assert str(voti[0].candidate_id) == c2


async def test_le_percentuali_sommano_al_100_e_si_vedono_solo_dopo_il_voto(come):
    admin = come("admin")
    round_id, c1, c2 = await _tornata_con_due_candidati(admin)
    utente = come("utente")

    prima = await utente.get("/voto/mazzi")
    assert all(cand["percentuale"] is None for cand in prima.json()["candidati"])

    await utente.post(f"/voto/mazzi/{c1}")
    dopo = await utente.get("/voto/mazzi")
    percentuali = [cand["percentuale"] for cand in dopo.json()["candidati"]]
    assert sum(percentuali) == 100
    assert dopo.json()["mio_voto"] == c1


async def test_accetta_selezionati_crea_piu_mazzi_e_chiude_la_tornata(come, session):
    admin = come("admin")
    round_id, c1, c2 = await _tornata_con_due_candidati(admin)
    r = await admin.post(f"/admin/voto/tornate/{round_id}/accetta", json={"candidate_ids": [c1, c2]})
    assert r.status_code == 200, r.text
    assert len(r.json()["deck_ids"]) == 2

    tornata = await session.get(VotingRound, uuid.UUID(round_id))
    assert tornata.stato == "chiusa"

    mazzi = (await session.execute(select(Deck))).scalars().all()
    assert len(mazzi) == 2
    assert all(not m.attivo for m in mazzi)  # non pronti per la vendita: da completare in console


async def test_un_candidato_non_selezionato_non_viene_accettato(come, session):
    admin = come("admin")
    round_id, c1, c2 = await _tornata_con_due_candidati(admin)
    await admin.post(f"/admin/voto/tornate/{round_id}/accetta", json={"candidate_ids": [c1]})

    candidato_due = await session.get(DeckCandidate, uuid.UUID(c2))
    assert candidato_due.accettato is False
    assert candidato_due.deck_id is None


# ---- riserva di proposte e creazione della tornata ("tornate elettorali") --------------------------


async def test_una_proposta_gia_assegnata_non_si_puo_riusare_in_unaltra_tornata(come):
    admin = come("admin")
    round_id, c1, c2 = await _tornata_con_due_candidati(admin)
    c3 = (await admin.post("/admin/voto/candidati", json={"nome": "Tre"})).json()["id"]

    r = await admin.post("/admin/voto/tornate", json={"candidate_ids": [c1, c3], "chiude_il": _tra_un_ora()})
    assert r.status_code == 400


async def test_una_scadenza_nel_passato_e_rifiutata(come):
    admin = come("admin")
    c1, c2 = await _due_proposte_in_riserva(admin)
    passato = (utcnow() - timedelta(hours=1)).isoformat()
    r = await admin.post("/admin/voto/tornate", json={"candidate_ids": [c1, c2], "chiude_il": passato})
    assert r.status_code == 400


async def test_le_proposte_non_assegnate_restano_in_riserva(come):
    admin = come("admin")
    c1, c2 = await _due_proposte_in_riserva(admin)
    disponibili = (await admin.get("/admin/voto/candidati/disponibili")).json()
    assert {c1, c2} <= {c["id"] for c in disponibili}

    await admin.post("/admin/voto/tornate", json={"candidate_ids": [c1], "chiude_il": _tra_un_ora()})
    dopo = (await admin.get("/admin/voto/candidati/disponibili")).json()
    ids_dopo = {c["id"] for c in dopo}
    assert c1 not in ids_dopo
    assert c2 in ids_dopo


# ---- chiusura automatica alla scadenza --------------------------------------------------------------


async def test_una_tornata_scaduta_si_chiude_da_sola_alla_prima_lettura(come, session):
    admin = come("admin")
    round_id, c1, c2 = await _tornata_con_due_candidati(admin)

    tornata = await session.get(VotingRound, uuid.UUID(round_id))
    tornata.chiude_il = utcnow() - timedelta(minutes=1)
    await session.commit()

    r = await admin.get("/voto/home")
    assert r.json()["voto_aperto"] is False

    await session.refresh(tornata)
    assert tornata.stato == "chiusa"


async def test_il_riepilogo_home_mostra_tutti_i_candidati_della_tornata_chiusa(come, session):
    admin = come("admin")
    round_id, c1, c2 = await _tornata_con_due_candidati(admin)
    utente = come("utente")
    await utente.post(f"/voto/mazzi/{c1}")

    tornata = await session.get(VotingRound, uuid.UUID(round_id))
    tornata.chiude_il = utcnow() - timedelta(minutes=1)
    await session.commit()

    r = await utente.get("/voto/home")
    dati = r.json()
    assert dati["voto_aperto"] is False
    assert dati["risultato_recente"] is not None
    nomi = {c["nome"] for c in dati["risultato_recente"]["candidati"]}
    assert nomi == {"Uno", "Due"}
    assert sum(c["percentuale"] for c in dati["risultato_recente"]["candidati"]) == 100


# ---- generare un mazzo anche per un candidato non vincitore -----------------------------------------


async def test_genera_mazzo_funziona_anche_per_un_candidato_non_accettato(come, session):
    admin = come("admin")
    round_id, c1, c2 = await _tornata_con_due_candidati(admin)

    r = await admin.post(f"/admin/voto/candidati/{c2}/genera-mazzo")
    assert r.status_code == 200, r.text
    deck_id = r.json()["deck_id"]

    candidato = await session.get(DeckCandidate, uuid.UUID(c2))
    assert candidato.deck_id == deck_id
    assert candidato.accettato is False  # generato, ma non ha vinto: resta distinto

    mazzo = await session.get(Deck, deck_id)
    assert mazzo is not None
    assert mazzo.attivo is False


async def test_genera_mazzo_e_idempotente(come):
    admin = come("admin")
    round_id, c1, c2 = await _tornata_con_due_candidati(admin)
    primo = (await admin.post(f"/admin/voto/candidati/{c1}/genera-mazzo")).json()
    secondo = (await admin.post(f"/admin/voto/candidati/{c1}/genera-mazzo")).json()
    assert primo["deck_id"] == secondo["deck_id"]


# ---- suggerisci un tema (per gli iscritti) -----------------------------------------------------------


async def test_un_suggerimento_trasformato_diventa_una_proposta_in_riserva(come, session):
    # `come` riassegna il principal sullo stesso client condiviso: chi lo chiama per ultimo vince,
    # quindi ogni alias va "riattivato" con `come(...)` subito prima di ogni uso, non tenuto da parte.
    utente = come("utente")
    r = await utente.post("/voto/suggerimenti", json={"testo": "Un mazzo ispirato al giardino botanico"})
    assert r.status_code == 201

    admin = come("admin")
    nuovi = (await admin.get("/admin/voto/suggerimenti")).json()
    assert len(nuovi) == 1
    suggestion_id = nuovi[0]["id"]
    assert nuovi[0]["stato"] == "nuovo"

    trasformato = await admin.post(f"/admin/voto/suggerimenti/{suggestion_id}/trasforma")
    assert trasformato.status_code == 201, trasformato.text
    candidate_id = trasformato.json()["id"]

    disponibili = (await admin.get("/admin/voto/candidati/disponibili")).json()
    assert candidate_id in {c["id"] for c in disponibili}

    suggerimento = await session.get(DeckSuggestion, uuid.UUID(suggestion_id))
    assert suggerimento.stato == "usato"
    assert str(suggerimento.candidate_id) == candidate_id

    ancora_nuovi = (await admin.get("/admin/voto/suggerimenti")).json()
    assert ancora_nuovi == []


async def test_un_suggerimento_scartato_non_diventa_una_proposta(come, session):
    utente = come("utente")
    await utente.post("/voto/suggerimenti", json={"testo": "Un tema che non convince"})
    admin = come("admin")
    suggestion_id = (await admin.get("/admin/voto/suggerimenti")).json()[0]["id"]

    r = await admin.post(f"/admin/voto/suggerimenti/{suggestion_id}/scarta")
    assert r.status_code == 200
    assert r.json()["stato"] == "scartato"

    suggerimento = await session.get(DeckSuggestion, uuid.UUID(suggestion_id))
    assert suggerimento.candidate_id is None
    assert (await admin.get("/admin/voto/suggerimenti")).json() == []
