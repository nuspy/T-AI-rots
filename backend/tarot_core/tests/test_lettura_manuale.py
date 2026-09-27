"""'Interpreta i miei tarocchi' (v5): il mazzo è fisico, già estratto — niente ventaglio, l'identità
delle carte è visibile da subito."""
from __future__ import annotations

from tarot_core.billing.credits import RegistroCrediti
from tarot_core.domain.repositories import UserRepository
from tarot_core.tarot.shuffle import verifica

from .conftest import eventi_sse, richiede_database

pytestmark = richiede_database

QUESITO = "Cosa mi dicono queste carte?"


async def _accredita(session, principal, quanti=1000):
    utente = await UserRepository(session).ensure(principal)
    await RegistroCrediti(session).accredita(utente.id, quanti, reason="omaggio", note="prova")
    await session.commit()


async def _concludi_intervista(client, rid):
    r = await client.post(f"/readings/{rid}/interview", json={})
    while not r.json().get("completa"):
        r = await client.post(f"/readings/{rid}/interview", json={"risposta": "Da qualche mese."})
    return r.json()


async def test_tre_carte_manuale_arriva_alla_sintesi(client, session, catalogo):
    await _accredita(session, client.identita.principal)
    manuali = [
        {"posizione": 1, "card_id": "maj-00"},
        {"posizione": 2, "card_id": "maj-01"},
        {"posizione": 3, "card_id": "maj-02"},
    ]
    r = await client.post("/readings", json={"spread_id": "tre-carte", "question": QUESITO, "manual_cards": manuali})
    assert r.status_code == 201, r.text
    rid = r.json()["id"]

    # L'identità è visibile subito, prima ancora che l'intervista cominci — a differenza di una
    # lettura normale, dove nessuna carta è nota prima della rivelazione.
    dettaglio = (await client.get(f"/me/readings/{rid}")).json()
    assert dettaglio["manuale"] is True
    per_posizione = {c["posizione"]: c for c in dettaglio["cards"]}
    assert per_posizione[1]["carta"]["id"] == "maj-00"
    assert per_posizione[1]["rivelata"] is False  # il ritmo dell'interpretazione non cambia

    await _concludi_intervista(client, rid)

    # Niente ventaglio da aprire: si è già in rivelazione.
    dettaglio = (await client.get(f"/me/readings/{rid}")).json()
    assert dettaglio["status"] == "rivelazione"

    for pos in (1, 2, 3):
        r = await client.post(f"/readings/{rid}/reveal/{pos}")
        eventi = eventi_sse(r.text)
        assert eventi[-1][1]["interpretazione"]

    r = await client.post(f"/readings/{rid}/synthesis")
    eventi = eventi_sse(r.text)
    fine = eventi[-1][1]
    assert eventi[-1][0] == "fine" and fine["guardia"] == "ok"
    # Nessun mazzo digitale è stato impegnato: niente da verificare col commitment.
    assert fine["deck_state"] in (None, [])


async def test_croce_semplice_manuale_calcola_la_quinta_carta(client, session, catalogo):
    """La carta di sintesi di Wirth (posizione 5) non si indica a mano: si deriva da sola, come in
    una lettura normale."""
    await _accredita(session, client.identita.principal)
    manuali = [
        {"posizione": 1, "card_id": "maj-00"},
        {"posizione": 2, "card_id": "maj-01"},
        {"posizione": 3, "card_id": "maj-02"},
        {"posizione": 4, "card_id": "maj-03"},
    ]
    r = await client.post("/readings", json={"spread_id": "croce-semplice", "question": QUESITO, "manual_cards": manuali})
    assert r.status_code == 201, r.text
    rid = r.json()["id"]
    dettaglio = (await client.get(f"/me/readings/{rid}")).json()
    per_posizione = {c["posizione"]: c for c in dettaglio["cards"]}
    assert len(per_posizione) == 5
    assert per_posizione[5]["calcolata"] is True
    assert per_posizione[5]["carta"]["id"].startswith("maj-")


async def test_posizione_mancante_si_respinge_e_non_si_addebita(client, session, catalogo):
    await _accredita(session, client.identita.principal)
    manuali = [{"posizione": 1, "card_id": "maj-00"}, {"posizione": 2, "card_id": "maj-01"}]  # manca la 3
    r = await client.post("/readings", json={"spread_id": "tre-carte", "question": QUESITO, "manual_cards": manuali})
    assert r.status_code == 422
    assert r.json()["detail"]["motivo"] == "posizioni_manuali"
    assert (await client.get("/me/readings")).json()["totale"] == 0
    assert await RegistroCrediti(session).saldo((await UserRepository(session).ensure(client.identita.principal)).id) == 1000


async def test_carta_duplicata_si_respinge(client, session, catalogo):
    await _accredita(session, client.identita.principal)
    manuali = [
        {"posizione": 1, "card_id": "maj-00"}, {"posizione": 2, "card_id": "maj-00"}, {"posizione": 3, "card_id": "maj-01"},
    ]
    r = await client.post("/readings", json={"spread_id": "tre-carte", "question": QUESITO, "manual_cards": manuali})
    assert r.status_code == 422
    assert r.json()["detail"]["motivo"] == "carte_duplicate"


async def test_carta_sconosciuta_si_respinge(client, session, catalogo):
    await _accredita(session, client.identita.principal)
    manuali = [
        {"posizione": 1, "card_id": "non-esiste"}, {"posizione": 2, "card_id": "maj-00"}, {"posizione": 3, "card_id": "maj-01"},
    ]
    r = await client.post("/readings", json={"spread_id": "tre-carte", "question": QUESITO, "manual_cards": manuali})
    assert r.status_code == 422
    assert r.json()["detail"]["motivo"] == "carta_sconosciuta"


async def test_senza_manual_cards_la_lettura_e_normale(client, session, catalogo):
    """Il campo è opzionale: senza, tutto resta come prima (ventaglio, non manuale)."""
    await _accredita(session, client.identita.principal)
    r = await client.post("/readings", json={"spread_id": "tre-carte", "question": QUESITO})
    assert r.status_code == 201, r.text
    rid = r.json()["id"]
    dettaglio = (await client.get(f"/me/readings/{rid}")).json()
    assert dettaglio["manuale"] is False
    assert dettaglio["cards"] == []
    await _concludi_intervista(client, rid)
    dettaglio = (await client.get(f"/me/readings/{rid}")).json()
    assert dettaglio["status"] == "ventaglio"
