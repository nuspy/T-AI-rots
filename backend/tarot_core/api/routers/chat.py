"""La chat proattiva (v6, Fase E): solo per utenti loggati, indipendente da qualunque lettura.

Risposta JSON e non SSE: come `readings.py::intervista()`, un turno è un JSON breve (messaggio +
un'eventuale proposta strutturata), non un flusso lungo che ha senso vedere scrivere a macchina —
quello resta della sintesi di una lettura vera.

GDPR, Fase 1: per scrivere nella chat serve la conferma dell'età minima (`privacy.verifica_eta`); i nomi della persona
(i suoi, del partner ricordato, delle ultime letture di coppia) arrivano al fornitore come «Persona_N»
(`tarot/pseudonimi.py::nomi_utente`); la chat si cancella dal profilo, un messaggio alla volta o tutta.
"""
from __future__ import annotations

import random
from datetime import timedelta
from typing import Any, Dict, List, Optional

import uuid

from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import delete

from ...auth.dependencies import CurrentUser, DbSession
from ...domain import chat_repositories, memoria_repositories
from ...domain.chat_models import ChatProattivaTurno
from ...domain.impostazioni_repositories import correnti_chat, pubblico_chat
from ...llm.compiti import Compito
from ...domain.base import utcnow
from ...tarot.chat_proattiva import SPUNTI_APERTURA, genera_turno
from ...tarot.lingue import lingua, rileva_lingua
from ...tarot.memoria_retrieval import formatta_memorie
from ...tarot.pseudonimi import nomi_utente
from ...analytics import eventi as analytics
from ..deps import aggiorna_assegnazioni, provider_per
from .privacy import verifica_eta

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
    query (a differenza dell'apertura di una lettura), quindi il criterio è solo la recenza.

    Con l'interruttore della console acceso è lo stato sintetico (`tarot/stato_memoria.py`), nella stessa forma e
    con un tetto di caratteri: il prompt dell'oracolo non cambia."""
    from datetime import date

    from ...domain.impostazioni_repositories import correnti_intervista
    from ...tarot.stato_memoria import formatta

    if (await correnti_intervista(session)).memoria_stato_nei_prompt:
        return formatta(await memoria_repositories.stato_di(session, owner_id), date.today())
    return formatta_memorie(await memoria_repositories.piu_recenti(session, owner_id))


@router.get("/impostazioni-chat")
async def impostazioni_chat_pubbliche(user: CurrentUser, session: DbSession) -> Dict[str, int]:
    """Il timer di inattività: letto da qualunque utente loggato, non solo dall'amministrazione —
    è il client che deve sapere dopo quanti minuti aprire da solo la conversazione."""
    return pubblico_chat(await correnti_chat(session))


@router.get("/chat/proattiva")
async def storico(user: CurrentUser, session: DbSession) -> Dict[str, List[Dict[str, Any]]]:
    turni = await chat_repositories.recenti(session, user.id)
    # Aperture consecutive senza risposta (quelle impilate prima della v8.5): se ne mostra solo l'ultima.
    visibili = [t for i, t in enumerate(turni) if not (t.ruolo == "ai" and i + 1 < len(turni) and turni[i + 1].ruolo == "ai")]
    return {"turni": [_turno_json(t) for t in visibili]}


@router.post("/chat/proattiva/avvio", status_code=201)
async def avvio(user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    """Il client la chiama quando scatta il timer di inattività, o dopo la fine di una lettura:
    l'AI apre da sola, basandosi sulle memorie dell'utente.

    v8.5: mai aperture impilate. Se l'ultimo turno è già un'apertura dell'oracolo senza risposta, non se ne aggiunge
    un'altra: se ha meno di 12 ore resta quella (nessuna inferenza), se è più vecchia la nuova prende il suo posto.
    Ogni apertura parte da uno spunto a caso e non ripete le aperture recenti."""
    verifica_eta(user)
    turni = await chat_repositories.recenti(session, user.id)
    ultima = turni[-1] if turni else None
    da_sostituire = None
    # La lingua dell'oracolo è quella del profilo: un'apertura recente scritta in un'altra lingua (la persona ha
    # cambiato lingua nel frattempo) non si ripropone, si sostituisce.
    lingua_utente = lingua(user.locale)
    if ultima is not None and ultima.ruolo == "ai":
        stessa_lingua = rileva_lingua(ultima.testo, fallback=lingua_utente) == lingua_utente
        if stessa_lingua and ultima.created_at and utcnow() - ultima.created_at < timedelta(hours=12):
            return {"turno": None, "attuale": _turno_json(ultima)}
        da_sostituire = ultima

    await aggiorna_assegnazioni(session)
    memorie = await _memorie_recenti(session, user.id)
    provider = provider_per(Compito.CHAT_PROATTIVA, await nomi_utente(session, user), riferimento="chat")
    gia_dette = [t.testo for t in turni if t.ruolo == "ai"][-6:]
    esito = await genera_turno(
        provider, memorie=memorie, gia_dette=gia_dette, spunto=random.choice(SPUNTI_APERTURA), lingua=lingua_utente,
    )
    if not esito.messaggio:
        return {"turno": None}

    proposta = (
        {"argomento": esito.proposta.argomento, "categoria": esito.proposta.categoria}
        if esito.proposta else None
    )
    if da_sostituire is not None:
        da_sostituire.testo = esito.messaggio
        da_sostituire.proposta = proposta
        da_sostituire.created_at = utcnow()
        turno = da_sostituire
        await session.flush()
    else:
        turno = await chat_repositories.aggiungi(session, user.id, ruolo="ai", testo=esito.messaggio, proposta=proposta)
    await analytics.evento(session, analytics.CHAT_AVVIO, utente_id=user.id, proprieta={"proposta": proposta is not None})
    await session.commit()
    return {"turno": _turno_json(turno)}


@router.post("/chat/proattiva/messaggio")
async def messaggio(payload: MessaggioIn, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    verifica_eta(user)
    await aggiorna_assegnazioni(session)
    turni_prima = await chat_repositories.recenti(session, user.id)
    await chat_repositories.aggiungi(session, user.id, ruolo="utente", testo=payload.testo.strip())
    await analytics.evento(session, analytics.CHAT_MESSAGGIO, utente_id=user.id)
    await session.commit()

    memorie = await _memorie_recenti(session, user.id)
    provider = provider_per(Compito.CHAT_PROATTIVA, await nomi_utente(session, user), riferimento="chat")
    esito = await genera_turno(
        provider, memorie=memorie, trascrizione=chat_repositories.trascrizione(turni_prima),
        messaggio_utente=payload.testo.strip(), lingua=lingua(user.locale),
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


@router.delete("/chat/proattiva/{turno_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancella_turno(turno_id: uuid.UUID, user: CurrentUser, session: DbSession) -> Response:
    """Cancella un messaggio della chat (tuo o dell'oracolo). Solo del proprietario: un id di un altro è un 404."""
    esito = await session.execute(
        delete(ChatProattivaTurno).where(ChatProattivaTurno.id == turno_id, ChatProattivaTurno.owner_id == user.id)
    )
    if not esito.rowcount:
        raise HTTPException(status_code=404, detail="Messaggio non trovato")
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/chat/proattiva", status_code=status.HTTP_204_NO_CONTENT)
async def cancella_chat(user: CurrentUser, session: DbSession) -> Response:
    """Cancella tutta la chat. Le memorie nate dalla chat restano (si gestiscono a parte, dalla «mia storia»)."""
    await session.execute(delete(ChatProattivaTurno).where(ChatProattivaTurno.owner_id == user.id))
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
