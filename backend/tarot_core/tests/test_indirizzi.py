"""Gli indirizzi di spedizione (v5, Fase B5): CRUD nel profilo, l'unico predefinito, e il loro uso
al checkout del mazzo fisico — con la fotografia che non cambia se l'indirizzo cambia dopo."""
from __future__ import annotations

from tarot_core.domain.deck_models import Deck
from tarot_core.domain.repositories import UserRepository

from .conftest import richiede_database

pytestmark = richiede_database


def _indirizzo(**extra):
    base = {"nome": "Mario Rossi", "via": "Via Roma 1", "citta": "Roma", "cap": "00100", "paese": "IT"}
    base.update(extra)
    return base


# ---- CRUD ------------------------------------------------------------------------------------------


async def test_il_primo_indirizzo_e_predefinito_di_diritto(client):
    r = await client.post("/me/addresses", json=_indirizzo())
    assert r.status_code == 201, r.text
    assert r.json()["predefinito"] is True


async def test_un_secondo_indirizzo_non_predefinito_non_sposta_il_primo(client):
    r1 = await client.post("/me/addresses", json=_indirizzo())
    r2 = await client.post("/me/addresses", json=_indirizzo(nome="Altro"))
    assert r2.json()["predefinito"] is False

    elenco = (await client.get("/me/addresses")).json()["indirizzi"]
    predefiniti = [i for i in elenco if i["predefinito"]]
    assert [i["id"] for i in predefiniti] == [r1.json()["id"]]


async def test_impostare_un_nuovo_predefinito_toglie_l_altro(client):
    r1 = await client.post("/me/addresses", json=_indirizzo())
    r2 = await client.post("/me/addresses", json=_indirizzo(nome="Altro"))
    r3 = await client.patch(f"/me/addresses/{r2.json()['id']}", json={"predefinito": True})
    assert r3.json()["predefinito"] is True

    r1_rivisto = await client.get("/me/addresses")
    per_id = {i["id"]: i["predefinito"] for i in r1_rivisto.json()["indirizzi"]}
    assert per_id[r1.json()["id"]] is False
    assert per_id[r2.json()["id"]] is True


async def test_eliminare_il_predefinito_ne_promuove_un_altro(client):
    r1 = await client.post("/me/addresses", json=_indirizzo())
    r2 = await client.post("/me/addresses", json=_indirizzo(nome="Altro"))
    assert r1.json()["predefinito"] is True

    await client.delete(f"/me/addresses/{r1.json()['id']}")
    rimasti = (await client.get("/me/addresses")).json()["indirizzi"]
    assert len(rimasti) == 1
    assert rimasti[0]["id"] == r2.json()["id"]
    assert rimasti[0]["predefinito"] is True


async def test_un_indirizzo_non_valido_si_respinge(client):
    r = await client.post("/me/addresses", json=_indirizzo(paese="ITALIA"))
    assert r.status_code == 422


async def test_non_si_vede_l_indirizzo_di_un_altro(client, session, principal_admin):
    r = await client.post("/me/addresses", json=_indirizzo())
    indirizzo_id = r.json()["id"]

    client.identita.principal = principal_admin
    r2 = await client.get("/me/addresses")
    assert indirizzo_id not in {i["id"] for i in r2.json()["indirizzi"]}
    r3 = await client.patch(f"/me/addresses/{indirizzo_id}", json={"nome": "Rubato"})
    assert r3.status_code == 404


# ---- il checkout del mazzo fisico -----------------------------------------------------------------


async def test_ordine_fisico_senza_indirizzo_si_respinge(client, session):
    mazzo = Deck(nome="DaSpedire", slug="da-spedire", attivo=True, prezzo_fisico=3000, richiede_spedizione=True)
    session.add(mazzo)
    await session.commit()
    r = await client.post("/orders", json={"voci": [{"deck_id": mazzo.id, "tipo": "fisico"}]})
    assert r.status_code == 422


async def test_ordine_fisico_con_indirizzo_salva_la_fotografia(client, session):
    mazzo = Deck(nome="DaSpedire2", slug="da-spedire-2", attivo=True, prezzo_fisico=3000, richiede_spedizione=True)
    session.add(mazzo)
    await session.commit()
    indirizzo = (await client.post("/me/addresses", json=_indirizzo())).json()

    r = await client.post(
        "/orders", json={"voci": [{"deck_id": mazzo.id, "tipo": "fisico"}], "indirizzo_id": indirizzo["id"]},
    )
    assert r.status_code == 201, r.text
    assert r.json()["indirizzo_spedizione"]["via"] == "Via Roma 1"

    # L'indirizzo cambia dopo: la fotografia dell'ordine già aperto resta quella di prima.
    await client.patch(f"/me/addresses/{indirizzo['id']}", json={"via": "Corso Nuovo 9"})
    dettaglio = await client.get(f"/me/orders/{r.json()['id']}")
    assert dettaglio.json()["indirizzo_spedizione"]["via"] == "Via Roma 1"


async def test_ordine_fisico_pagato_marca_la_riga_in_attesa_di_evasione(client, session):
    mazzo = Deck(nome="DaSpedire3", slug="da-spedire-3", attivo=True, prezzo_fisico=3000, richiede_spedizione=True)
    session.add(mazzo)
    await session.commit()
    indirizzo = (await client.post("/me/addresses", json=_indirizzo())).json()
    r = await client.post(
        "/orders", json={"voci": [{"deck_id": mazzo.id, "tipo": "fisico"}], "indirizzo_id": indirizzo["id"]},
    )
    ordine_id = r.json()["id"]
    await client.post(f"/billing/mock/ordine/{ordine_id}/esito", data={"esito": "paga", "ritorno": "/mazzo"})

    dettaglio = (await client.get(f"/me/orders/{ordine_id}")).json()
    assert dettaglio["righe"][0]["stato_evasione"] == "in_attesa"


async def test_ordine_fisico_con_indirizzo_di_un_altro_utente_si_respinge(client, session, principal_admin):
    mazzo = Deck(nome="DaSpedire4", slug="da-spedire-4", attivo=True, prezzo_fisico=3000, richiede_spedizione=True)
    session.add(mazzo)
    await session.commit()
    indirizzo = (await client.post("/me/addresses", json=_indirizzo())).json()

    client.identita.principal = principal_admin
    await UserRepository(session).ensure(principal_admin)
    await session.commit()
    r = await client.post(
        "/orders", json={"voci": [{"deck_id": mazzo.id, "tipo": "fisico"}], "indirizzo_id": indirizzo["id"]},
    )
    assert r.status_code == 404
