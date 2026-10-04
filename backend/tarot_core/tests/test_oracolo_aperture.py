"""L'oracolo (v8.5): mai aperture impilate senza risposta, una sola domanda in attesa per utente."""
from __future__ import annotations

from datetime import timedelta

from sqlalchemy import select

from tarot_core.domain.base import utcnow
from tarot_core.domain.chat_models import ChatProattivaTurno

from .conftest import richiede_database

pytestmark = richiede_database


async def test_due_aperture_di_seguito_lasciano_una_sola_domanda(client):
    prima = (await client.post("/chat/proattiva/avvio")).json()
    assert prima["turno"] is not None
    seconda = (await client.post("/chat/proattiva/avvio")).json()
    assert seconda["turno"] is None and seconda["attuale"]["id"] == prima["turno"]["id"]
    storico = (await client.get("/chat/proattiva")).json()["turni"]
    assert [t["ruolo"] for t in storico] == ["ai"]


async def test_un_apertura_vecchia_si_sostituisce_e_non_si_aggiunge(client, session):
    prima = (await client.post("/chat/proattiva/avvio")).json()["turno"]
    riga = (await session.execute(select(ChatProattivaTurno))).scalars().one()
    riga.created_at = utcnow() - timedelta(hours=13)
    await session.commit()

    nuova = (await client.post("/chat/proattiva/avvio")).json()["turno"]
    assert nuova is not None and nuova["id"] == prima["id"]
    storico = (await client.get("/chat/proattiva")).json()["turni"]
    assert len(storico) == 1


async def test_dopo_una_risposta_l_oracolo_puo_riaprire(client):
    await client.post("/chat/proattiva/avvio")
    await client.post("/chat/proattiva/messaggio", json={"testo": "Tutto bene, grazie."})
    # L'ultimo turno è la risposta dell'oracolo al messaggio: un'apertura nuova resta in attesa (meno di 12 ore).
    assert (await client.post("/chat/proattiva/avvio")).json()["turno"] is None


def _senza_lingua_nel_token(client, sub):
    # Il token senza claim `locale`: la lingua resta quella scelta nel profilo (come per chi non ha la lingua in
    # Keycloak), invece di tornare a quella del Principal costruito a mano a ogni richiesta.
    from tarot_core.auth.keycloak import Principal

    client.identita.principal = Principal(subject=sub, email=f"{sub}@example.com", roles={"user"}, raw_claims={"sub": sub})


async def test_l_oracolo_scrive_nella_lingua_del_profilo(client):
    """La lingua dell'oracolo è quella del profilo: il prompt la dice (il finto la rispetta come un modello vero)."""
    _senza_lingua_nel_token(client, "sub-oracolo-en")
    assert (await client.patch("/me/profile", json={"locale": "en"})).status_code == 200
    apertura = (await client.post("/chat/proattiva/avvio")).json()["turno"]
    assert apertura["testo"] in (
        "Hi. How are you today? Is something on your mind?",
        "Is there a decision you keep putting off? We can look at it together.",
    )
    risposta = (await client.post("/chat/proattiva/messaggio", json={"testo": "Va tutto bene"})).json()["turno"]
    assert risposta["testo"].startswith("I'm listening.")


async def test_un_apertura_in_un_altra_lingua_non_si_ripropone(client):
    _senza_lingua_nel_token(client, "sub-oracolo-es")
    prima = (await client.post("/chat/proattiva/avvio")).json()["turno"]
    assert (await client.patch("/me/profile", json={"locale": "es"})).status_code == 200
    # Meno di 12 ore, ma scritta in italiano: con il profilo in spagnolo si sostituisce (nessuna seconda domanda).
    nuova = (await client.post("/chat/proattiva/avvio")).json()["turno"]
    assert nuova is not None and nuova["id"] == prima["id"] and nuova["testo"] != prima["testo"]
    assert nuova["testo"].startswith(("Hola", "¿Hay"))
    assert len((await client.get("/chat/proattiva")).json()["turni"]) == 1


def test_il_prompt_porta_la_riga_della_lingua():
    from tarot_core.tarot.chat_proattiva import istruzione_lingua_chat

    assert istruzione_lingua_chat("ru").startswith("Scrivi il messaggio in russo,")
    assert "ungherese" in istruzione_lingua_chat("hu")
