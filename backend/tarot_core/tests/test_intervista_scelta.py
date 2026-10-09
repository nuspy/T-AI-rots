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
    # (Dal 9/10/2026 «basta» prima del minimo è «Saltiamo, basta con le domande»: chiude con la domanda saltata, vedi
    # `test_lingua_conversazione.py`. Qui si risponde.)

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
async def test_tre_scelte_risposta_senza_domanda_successiva_testo_libero_e_altra_domanda(client, principal_utente):
    """v9.5, i tre pulsanti (predefiniti 0–2): la prima domanda arriva sempre ed è già facoltativa; con `continua`
    falso la risposta si salva senza chiedere la domanda successiva; il testo libero entra nel colloquio (non conta
    come domanda); «un'altra domanda» la ottiene fino al massimo; dopo il massimo si rifiuta; «basta» chiude."""
    lid = (await _apri(client)).json()["id"]
    prima = (await client.post(f"/readings/{lid}/interview", json={})).json()
    assert prima["completa"] is False and prima["facoltativa"] is True
    assert (prima["poste"], prima["min_domande"], prima["max_domande"]) == (1, 0, 2)
    # (Dal 9/10/2026 il testo libero con una domanda in attesa la salta: vedi `test_lingua_conversazione.py`.)

    salvata = (await client.post(f"/readings/{lid}/interview",
                                  json={"risposta": "Da gennaio.", "continua": False})).json()
    assert salvata == {"completa": False, "scelta": True, "poste": 1, "min_domande": 0, "max_domande": 2, "lang": "it"}

    r = await client.post(f"/readings/{lid}/addition", json={"testo": "Ho paura di cambiare città."})
    assert r.status_code == 200, r.text

    seconda = (await client.post(f"/readings/{lid}/interview", json={"altra": True})).json()
    assert seconda["completa"] is False and seconda["domanda"] and seconda["poste"] == 2
    await client.post(f"/readings/{lid}/interview", json={"risposta": "Sì.", "continua": False})
    assert (await client.post(f"/readings/{lid}/interview", json={"altra": True})).status_code == 409

    fine = await client.post(f"/readings/{lid}/interview", json={"basta": True})
    assert fine.status_code == 200 and fine.json()["completa"] is True
    lettura = (await client.get(f"/me/readings/{lid}")).json()
    assert lettura["status"] == "ventaglio"
    assert [t["ruolo"] for t in lettura["interview"]] == ["oracolo", "utente", "utente", "oracolo", "utente"]
    assert lettura["interview"][2]["testo"].endswith("Ho paura di cambiare città.")

    # A intervista chiusa, prima delle carte, il testo libero va anche in coda al quadro emerso.
    assert (await client.post(f"/readings/{lid}/addition", json={"testo": "Anche il lavoro."})).status_code == 200
    lettura = (await client.get(f"/me/readings/{lid}")).json()
    assert lettura["context_summary"].endswith("Anche il lavoro.")


@richiede_database
async def test_minimo_e_massimo_dalla_console(client, principal_admin):
    client.identita.principal = principal_admin
    r = await client.get("/admin/impostazioni-intervista")
    assert r.status_code == 200, r.text
    controlli = {"validatore_domande": "dubbi", "guardia_responso": "dubbi", "memoria_stato_nei_prompt": False,
                 "chat_percentuale": 90}
    # v9.5: predefiniti 0–2 (prima 2–6), e il minimo può essere 0.
    assert r.json() == {"min_domande": 0, "max_domande": 2, **controlli}
    assert (await client.put("/admin/impostazioni-intervista", json={"min_domande": 5, "max_domande": 3})).status_code == 422
    assert (await client.put("/admin/impostazioni-intervista", json={"min_domande": 0, "max_domande": 0})).status_code == 422
    r = await client.put("/admin/impostazioni-intervista", json={"min_domande": 1, "max_domande": 2})
    assert r.json() == {"min_domande": 1, "max_domande": 2, **controlli}
    r = await client.put("/admin/impostazioni-intervista", json={"validatore_domande": "spento", "guardia_responso": "acceso"})
    assert r.json()["validatore_domande"] == "spento" and r.json()["guardia_responso"] == "acceso"
    assert (await client.put("/admin/impostazioni-intervista", json={"guardia_responso": "forse"})).status_code == 422
    # v9.5: la percentuale della lettura in chat, anche nelle impostazioni pubbliche (lo smistatore la legge).
    assert (await client.put("/admin/impostazioni-intervista", json={"chat_percentuale": 101})).status_code == 422
    assert (await client.put("/admin/impostazioni-intervista", json={"chat_percentuale": 50})).json()["chat_percentuale"] == 50
    assert (await client.get("/impostazioni-pubbliche")).json()["lettura_chat_percentuale"] == 50


@richiede_database
async def test_la_prima_variante_diventa_quella_della_persona(client):
    assert (await client.get("/me/profile")).json()["variante_lettura"] is None
    await client.post("/readings", json={"spread_id": "tre-carte", "question": QUESITO, "variante": "chat"})
    await client.post("/readings", json={"spread_id": "tre-carte", "question": QUESITO, "variante": "classica"})
    assert (await client.get("/me/profile")).json()["variante_lettura"] == "chat"
