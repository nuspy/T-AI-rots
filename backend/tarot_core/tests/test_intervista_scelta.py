"""L'intervista della v8.5: nessuna domanda ripetuta, minimo e massimo dalla console, e «No, basta così» dopo il
minimo (la domanda facoltativa senza risposta si toglie e la lettura passa alle carte)."""
from __future__ import annotations

from tarot_core.tarot.intervista import ripete_una_domanda, viola_le_regole

from .conftest import richiede_database

QUESITO = "Come andrà il mio prossimo anno lavorativo?"


def test_una_domanda_riformulata_da_vicino_e_una_ripetizione():
    fatte = ["Da quanto tempo questa situazione è presente nella tua vita, e cosa l'ha messa in moto?"]
    assert ripete_una_domanda("Da quanto tempo è presente questa situazione nella tua vita?", fatte)
    assert not ripete_una_domanda("Chi sono le persone coinvolte, e che ruolo hanno per te?", fatte)
    assert viola_le_regole(QUESITO, "Da quanto tempo questa situazione è presente nella tua vita?",
                           precedenti=fatte) == "ripete una domanda già posta"


async def _apri(client):
    return await client.post("/readings", json={"spread_id": "tre-carte", "question": QUESITO})


@richiede_database
async def test_dopo_il_minimo_la_domanda_e_facoltativa_e_basta_cosi_chiude(client, principal_admin, principal_utente):
    # Il modello finto chiude appena può: con minimo 1 la seconda domanda è già facoltativa.
    client.identita.principal = principal_admin
    r = await client.put("/admin/impostazioni-intervista", json={"min_domande": 1, "max_domande": 6})
    assert r.status_code == 200, r.text
    client.identita.principal = principal_utente

    r = await _apri(client)
    assert r.status_code == 201, r.text
    lid = r.json()["id"]

    prima = (await client.post(f"/readings/{lid}/interview", json={})).json()
    assert prima["completa"] is False and prima["facoltativa"] is False

    # Prima del minimo «basta così» non vale.
    no = await client.post(f"/readings/{lid}/interview", json={"basta": True})
    assert no.status_code == 409

    seconda = (await client.post(f"/readings/{lid}/interview", json={"risposta": "Da gennaio, col nuovo capo."})).json()
    assert seconda["completa"] is False and seconda["facoltativa"] is True

    fine = await client.post(f"/readings/{lid}/interview", json={"basta": True})
    assert fine.status_code == 200, fine.text
    assert fine.json()["completa"] is True and fine.json()["riassunto"]

    lettura = (await client.get(f"/me/readings/{lid}")).json()
    assert lettura["status"] == "ventaglio"
    # La domanda facoltativa rimasta senza risposta non resta nel colloquio.
    assert [t["ruolo"] for t in lettura["interview"]] == ["oracolo", "utente"]


@richiede_database
async def test_con_minimo_zero_si_passa_alle_carte_dalla_prima_domanda_e_si_puo_aggiungere(client, principal_utente):
    """v9.5: con i predefiniti (0–2) «basta» vale già alla prima domanda; dopo l'intervista ciò che si aggiunge
    liberamente entra nel colloquio e nel quadro emerso, e solo prima delle carte."""
    r = await _apri(client)
    lid = r.json()["id"]
    assert (await client.post(f"/readings/{lid}/addition", json={"testo": "troppo presto"})).status_code == 409
    prima = (await client.post(f"/readings/{lid}/interview", json={})).json()
    assert prima["facoltativa"] is True
    fine = await client.post(f"/readings/{lid}/interview", json={"basta": True})
    assert fine.status_code == 200, fine.text

    r = await client.post(f"/readings/{lid}/addition", json={"testo": "Ho paura di cambiare città."})
    assert r.status_code == 200, r.text
    lettura = (await client.get(f"/me/readings/{lid}")).json()
    assert lettura["interview"][-1] == {"ruolo": "utente", "testo": "Ho paura di cambiare città.", "ordine": 2}
    assert lettura["interview"][-2]["ruolo"] == "oracolo"
    assert lettura["context_summary"].endswith("Ho paura di cambiare città.")
    assert lettura["status"] == "ventaglio"


@richiede_database
async def test_minimo_e_massimo_dalla_console(client, principal_admin):
    client.identita.principal = principal_admin
    r = await client.get("/admin/impostazioni-intervista")
    assert r.status_code == 200, r.text
    controlli = {"validatore_domande": "dubbi", "guardia_responso": "dubbi", "memoria_stato_nei_prompt": False}
    # v9.5: predefiniti 0–2 (prima 2–6), e il minimo può essere 0.
    assert r.json() == {"min_domande": 0, "max_domande": 2, **controlli}
    assert (await client.put("/admin/impostazioni-intervista", json={"min_domande": 5, "max_domande": 3})).status_code == 422
    assert (await client.put("/admin/impostazioni-intervista", json={"min_domande": 0, "max_domande": 0})).status_code == 422
    r = await client.put("/admin/impostazioni-intervista", json={"min_domande": 1, "max_domande": 2})
    assert r.json() == {"min_domande": 1, "max_domande": 2, **controlli}
    r = await client.put("/admin/impostazioni-intervista", json={"validatore_domande": "spento", "guardia_responso": "acceso"})
    assert r.json()["validatore_domande"] == "spento" and r.json()["guardia_responso"] == "acceso"
    assert (await client.put("/admin/impostazioni-intervista", json={"guardia_responso": "forse"})).status_code == 422
