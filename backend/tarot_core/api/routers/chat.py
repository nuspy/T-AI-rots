"""La chat proattiva (v6, Fase E): solo per utenti loggati, indipendente da qualunque lettura.

Risposta JSON e non SSE: come `readings.py::intervista()`, un turno è un JSON breve (messaggio +
un'eventuale proposta strutturata), non un flusso lungo che ha senso vedere scrivere a macchina —
quello resta della sintesi di una lettura vera.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ...auth.dependencies import CurrentUser, DbSession
from ...domain import chat_repositories, memoria_repositories
from ...domain.chat_models import ChatProattivaTurno
from ...domain.impostazioni_repositories import correnti_chat, pubblico_chat
from ...llm.compiti import Compito
from ...tarot.chat_proattiva import genera_turno
from ...tarot.memoria_retrieval import formatta_memorie
from ..deps import aggiorna_assegnazioni, provider_per

router = APIRouter(tags=["chat"])


class MessaggioIn(BaseModel):
    testo: str = Field(min_length=1, max_length=2000)


def _turno_json(t: ChatProattivaTurno) -> Dict[str, Any]:
    return {
        "id": str(t.id), "ruolo": t.ruolo, "testo": t.testo, "proposta": t.proposta,
        "creato": t.created_at.isoformat() if t.created_at else None,
    }


async def _memorie_recenti(session: DbSession, owner_id: int) -> str:
    """Le memorie più di recente aggiornate: qui non c'è una domanda specifica da vettorizzare come
    query (a differenza dell'apertura di una lettura), quindi il criterio è solo la recenza."""
    return formatta_memorie(await memoria_repositories.piu_recenti(session, owner_id))


@router.get("/impostazioni-chat")
async def impostazioni_chat_pubbliche(user: CurrentUser, session: DbSession) -> Dict[str, int]:
    """Il timer di inattività: letto da qualunque utente loggato, non solo dall'amministrazione —
    è il client che deve sapere dopo quanti minuti aprire da solo la conversazione."""
    return pubblico_chat(await correnti_chat(session))


@router.get("/chat/proattiva")
async def storico(user: CurrentUser, session: DbSession) -> Dict[str, List[Dict[str, Any]]]:
    turni = await chat_repositories.recenti(session, user.id)
    return {"turni": [_turno_json(t) for t in turni]}


@router.post("/chat/proattiva/avvio", status_code=201)
async def avvio(user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    """Il client la chiama quando scatta il timer di inattività, o dopo la fine di una lettura:
    l'AI apre da sola, basandosi sulle memorie dell'utente."""
    await aggiorna_assegnazioni(session)
    memorie = await _memorie_recenti(session, user.id)
    provider = provider_per(Compito.CHAT_PROATTIVA)
    esito = await genera_turno(provider, memorie=memorie)
    if not esito.messaggio:
        return {"turno": None}

    proposta = (
        {"argomento": esito.proposta.argomento, "categoria": esito.proposta.categoria}
        if esito.proposta else None
    )
    turno = await chat_repositories.aggiungi(session, user.id, ruolo="ai", testo=esito.messaggio, proposta=proposta)
    await session.commit()
    return {"turno": _turno_json(turno)}


@router.post("/chat/proattiva/messaggio")
async def messaggio(payload: MessaggioIn, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    await aggiorna_assegnazioni(session)
    turni_prima = await chat_repositories.recenti(session, user.id)
    await chat_repositories.aggiungi(session, user.id, ruolo="utente", testo=payload.testo.strip())
    await session.commit()

    memorie = await _memorie_recenti(session, user.id)
    provider = provider_per(Compito.CHAT_PROATTIVA)
    esito = await genera_turno(
        provider, memorie=memorie, trascrizione=chat_repositories.trascrizione(turni_prima),
        messaggio_utente=payload.testo.strip(),
    )
    if not esito.messaggio:
        return {"turno": None}

    proposta = (
        {"argomento": esito.proposta.argomento, "categoria": esito.proposta.categoria}
        if esito.proposta else None
    )
    turno = await chat_repositories.aggiungi(session, user.id, ruolo="ai", testo=esito.messaggio, proposta=proposta)
    await session.commit()
    return {"turno": _turno_json(turno)}
