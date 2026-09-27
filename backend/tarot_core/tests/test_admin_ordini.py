"""Il registro ordini in console (v5, Fase B6): elenco filtrabile, dettaglio, l'evasione della
spedizione per le righe fisiche."""
from __future__ import annotations

from tarot_core.domain.deck_models import Deck

from .conftest import richiede_database

pytestmark = richiede_database


async def _come_admin(client, principal_admin):
    client.identita.principal = principal_admin


async def test_solo_admin_vede_il_registro(client, principal_admin):
    r = await client.get("/admin/orders")
    assert r.status_code == 403
    await _come_admin(client, principal_admin)
    r2 = await client.get("/admin/orders")
    assert r2.status_code == 200


async def test_l_elenco_mostra_l_utente_e_l_incassato(client, session, principal_admin):
    mazzo = Deck(nome="PerRegistro", slug="per-registro", attivo=True, prezzo_digitale=1000)
    session.add(mazzo)
    await session.commit()
    r = await client.post("/orders", json={"voci": [{"deck_id": mazzo.id, "tipo": "digitale"}]})
    ordine_id = r.json()["id"]
    await client.post(f"/billing/mock/ordine/{ordine_id}/esito", data={"esito": "paga", "ritorno": "/mazzo"})

    await _come_admin(client, principal_admin)
    elenco = (await client.get("/admin/orders")).json()
    trovato = next(o for o in elenco["ordini"] if o["id"] == ordine_id)
    assert trovato["status"] == "pagato"
    assert elenco["incassato"] >= 1000


async def test_filtro_per_stato(client, session, principal_admin):
    mazzo = Deck(nome="Filtro", slug="filtro-stato", attivo=True, prezzo_digitale=1000)
    session.add(mazzo)
    await session.commit()
    await client.post("/orders", json={"voci": [{"deck_id": mazzo.id, "tipo": "digitale"}]})

    await _come_admin(client, principal_admin)
    solo_aperti = (await client.get("/admin/orders", params={"status": "aperto"})).json()
    assert all(o["status"] == "aperto" for o in solo_aperti["ordini"])


async def test_aggiorna_evasione_di_una_riga_fisica(client, session, principal_admin):
    mazzo = Deck(nome="DaSpedireRegistro", slug="da-spedire-registro", attivo=True, prezzo_fisico=3000)
    session.add(mazzo)
    await session.commit()
    indirizzo = (await client.post(
        "/me/addresses", json={"nome": "Mario Rossi", "via": "Via Roma 1", "citta": "Roma", "cap": "00100", "paese": "IT"},
    )).json()
    r = await client.post(
        "/orders", json={"voci": [{"deck_id": mazzo.id, "tipo": "fisico"}], "indirizzo_id": indirizzo["id"]},
    )
    ordine_id = r.json()["id"]
    await client.post(f"/billing/mock/ordine/{ordine_id}/esito", data={"esito": "paga", "ritorno": "/mazzo"})
    riga_id = (await client.get(f"/me/orders/{ordine_id}")).json()["righe"][0]["id"]

    await _come_admin(client, principal_admin)
    r2 = await client.patch(f"/admin/orders/{ordine_id}/righe/{riga_id}", json={"stato_evasione": "spedito"})
    assert r2.status_code == 200
    assert r2.json()["righe"][0]["stato_evasione"] == "spedito"


async def test_non_si_aggiorna_l_evasione_di_una_riga_non_fisica(client, session, principal_admin):
    mazzo = Deck(nome="DigitaleRegistro", slug="digitale-registro", attivo=True, prezzo_digitale=1000)
    session.add(mazzo)
    await session.commit()
    r = await client.post("/orders", json={"voci": [{"deck_id": mazzo.id, "tipo": "digitale"}]})
    ordine_id = r.json()["id"]
    riga_id = (await client.get(f"/me/orders/{ordine_id}")).json()["righe"][0]["id"]

    await _come_admin(client, principal_admin)
    r2 = await client.patch(f"/admin/orders/{ordine_id}/righe/{riga_id}", json={"stato_evasione": "spedito"})
    assert r2.status_code == 422
