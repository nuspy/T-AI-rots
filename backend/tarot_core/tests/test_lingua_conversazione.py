"""La lingua segue chi scrive (9/10/2026), e le domande dell'intervista si possono saltare.

Persone che scrivevano in inglese ricevevano risposte in italiano: la lingua si decideva una volta sola sul quesito, e
la chat dell'oracolo usava quella del profilo («it» d'ufficio). Ora ogni messaggio pieno (almeno tre parole) può
spostare la lingua della conversazione; uno corto («ok», «sì») no. Sempre il modello finto."""
from __future__ import annotations

import uuid

import pytest
from sqlalchemy import select

from tarot_core.domain.models import InterviewTurn, Reading
from tarot_core.tarot.lingue import lingua_del_messaggio
from tarot_core.tarot.testi import DOMANDA_SALTATA

from .conftest import richiede_database
from .test_flusso import QUESITO, _accredita


@pytest.mark.parametrize("testo, attuale, attesa", [
    ("I have been looking for a new job for months", "it", "en"),     # inglese su una lettura italiana
    ("Will I find a new job this year?", "it", "en"),
    ("domani pioverá?", "it", "it"),                                     # il caso dell'8/10: resta italiano
    ("ok", "en", "en"),                                                  # troppo corto per cambiare
    ("sì", "en", "en"),
    ("Marco", "en", "en"),
    ("Da qualche mese, con alti e bassi.", "en", "it"),
    ("Mikor találok végre egy jó munkát?", "it", "hu"),
    ("我今年能找到新工作吗", "it", "zh"),                                   # senza spazi: contano le lettere
    ("工作", "it", "it"),
])
def test_un_messaggio_pieno_sposta_la_lingua_uno_corto_no(testo, attuale, attesa):
    assert lingua_del_messaggio(testo, attuale) == attesa


async def _regole(session, minimo: int, massimo: int) -> None:
    from tarot_core.domain.impostazioni_repositories import correnti_intervista

    riga = await correnti_intervista(session)
    riga.min_domande, riga.max_domande = minimo, massimo
    await session.commit()


async def _apri(client, session, quesito: str = QUESITO, lang: str = "it") -> str:
    await _accredita(session, client.identita.principal)
    r = await client.post("/readings", json={"spread_id": "tre-carte", "question": quesito, "lang": lang})
    assert r.status_code == 201, r.text
    return r.json()["id"]


async def _turni(session, rid: str) -> list:
    righe = (await session.execute(
        select(InterviewTurn).where(InterviewTurn.reading_id == uuid.UUID(rid)).order_by(InterviewTurn.ordine)
    )).scalars().all()
    return [(t.ruolo, t.testo) for t in righe]


@richiede_database
async def test_una_risposta_in_inglese_porta_la_lettura_in_inglese(client, session, catalogo):
    await _regole(session, 1, 3)
    rid = await _apri(client, session)
    r = await client.post(f"/readings/{rid}/interview", json={})
    assert r.json()["lang"] == "it"
    r = await client.post(f"/readings/{rid}/interview", json={"risposta": "ok", "continua": False})
    assert r.json()["lang"] == "it"                        # «ok» non basta
    r = await client.post(f"/readings/{rid}/interview", json={"altra": True})
    r = await client.post(f"/readings/{rid}/interview", json={
        "risposta": "I have been stuck in the same job for years and I want to change", "continua": False,
    })
    assert r.json()["lang"] == "en"
    session.expire_all()
    assert (await session.get(Reading, uuid.UUID(rid))).lang == "en"


@richiede_database
async def test_saltare_una_domanda_e_chiederne_un_altra(client, session, catalogo):
    await _regole(session, 1, 3)
    rid = await _apri(client, session)
    prima = (await client.post(f"/readings/{rid}/interview", json={})).json()["domanda"]
    r = await client.post(f"/readings/{rid}/interview", json={"altra": True})
    assert r.status_code == 200, r.text
    seconda = r.json()["domanda"]
    assert seconda and r.json()["poste"] == 2
    assert (await _turni(session, rid))[:3] == [
        ("oracolo", prima), ("utente", DOMANDA_SALTATA["it"]), ("oracolo", seconda),
    ]


@richiede_database
async def test_saltare_una_domanda_per_dire_un_altra_cosa(client, session, catalogo):
    await _regole(session, 1, 3)
    rid = await _apri(client, session)
    await client.post(f"/readings/{rid}/interview", json={})
    r = await client.post(f"/readings/{rid}/addition", json={"testo": "Vorrei dire che ho paura di sbagliare."})
    assert r.status_code == 200, r.text
    turni = await _turni(session, rid)
    assert turni[1] == ("utente", DOMANDA_SALTATA["it"]) and "ho paura di sbagliare" in turni[2][1]
    # Senza domande in attesa si può chiederne un'altra.
    assert (await client.post(f"/readings/{rid}/interview", json={"altra": True})).json()["domanda"]


@richiede_database
async def test_saltiamo_basta_con_le_domande_anche_sulla_prima(client, session, catalogo):
    await _regole(session, 1, 3)
    rid = await _apri(client, session)
    await client.post(f"/readings/{rid}/interview", json={})
    r = await client.post(f"/readings/{rid}/interview", json={"basta": True})
    assert r.status_code == 200, r.text
    assert r.json()["completa"] and r.json()["lang"] == "it"
    # Il minimo è una domanda: quella saltata resta, con la nota, e conta come posta.
    assert (await _turni(session, rid))[1] == ("utente", DOMANDA_SALTATA["it"])


@richiede_database
async def test_la_chat_risponde_nella_lingua_in_cui_si_scrive(client, session, catalogo, monkeypatch):
    from tarot_core.api.routers import chat
    from tarot_core.tarot.chat_proattiva import TurnoGenerato

    lingue = []

    async def turno_finto(_provider, **argomenti):
        lingue.append(argomenti["lingua"])
        return TurnoGenerato(messaggio="Ciao.")

    monkeypatch.setattr(chat, "genera_turno", turno_finto)
    await _accredita(session, client.identita.principal)                # l'utente nasce col profilo «it» d'ufficio
    for testo in ("Hello, I would like to talk about my job", "ok", "Sono di nuovo io, parliamo d'amore"):
        r = await client.post("/chat/proattiva/messaggio", json={"testo": testo})
        assert r.status_code == 200, r.text
    assert lingue == ["en", "en", "it"]
