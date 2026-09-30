"""Vota il prossimo mazzo (v7, Fase K): tornate, candidati, voti e statistiche."""
from __future__ import annotations

import uuid
from typing import Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import utcnow
from .voting_models import DeckCandidate, DeckSuggestion, DeckVote, VotingRound


async def tornata_aperta(session: AsyncSession) -> Optional[VotingRound]:
    return (await session.execute(
        select(VotingRound).where(VotingRound.stato == "aperta").order_by(VotingRound.created_at.desc())
    )).scalars().first()


async def chiudi_tornate_scadute(session: AsyncSession) -> bool:
    """Chiude ogni tornata aperta la cui scadenza è già passata — «tornate elettorali»: nessun
    processo separato la chiude, lo fa la prima lettura pubblica o della console che arriva dopo la
    scadenza (`GET /voto/mazzi`, `GET /voto/home`, `GET /admin/voto/tornate`). Ritorna `True` se ha
    chiuso qualcosa, cosi' il chiamante sa se ricaricare i dati che aveva già letto in questa stessa
    richiesta."""
    ora = utcnow()
    scadute = list((await session.execute(
        select(VotingRound).where(
            VotingRound.stato == "aperta", VotingRound.chiude_il.is_not(None), VotingRound.chiude_il <= ora,
        )
    )).scalars())
    for tornata in scadute:
        tornata.stato = "chiusa"
        tornata.chiusa_il = tornata.chiude_il
    return bool(scadute)


async def proposte_disponibili(session: AsyncSession) -> List[DeckCandidate]:
    """La riserva: candidati non ancora scelti per nessuna tornata (`round_id IS NULL`)."""
    return list((await session.execute(
        select(DeckCandidate).where(DeckCandidate.round_id.is_(None)).order_by(DeckCandidate.created_at)
    )).scalars())


async def suggerimenti_nuovi(session: AsyncSession) -> List[DeckSuggestion]:
    """«Suggerisci tema mazzo»: quelli ancora da rivedere in console (non trasformati né scartati)."""
    return list((await session.execute(
        select(DeckSuggestion).where(DeckSuggestion.stato == "nuovo").order_by(DeckSuggestion.created_at)
    )).scalars())


async def ultima_tornata_chiusa(session: AsyncSession) -> Optional[VotingRound]:
    return (await session.execute(
        select(VotingRound).where(VotingRound.stato == "chiusa").order_by(VotingRound.chiusa_il.desc())
    )).scalars().first()


async def candidati_di(session: AsyncSession, round_id: uuid.UUID) -> List[DeckCandidate]:
    return list((await session.execute(
        select(DeckCandidate).where(DeckCandidate.round_id == round_id).order_by(DeckCandidate.created_at)
    )).scalars())


async def voto_di(session: AsyncSession, round_id: uuid.UUID, user_id: int) -> Optional[DeckVote]:
    return (await session.execute(
        select(DeckVote).where(DeckVote.round_id == round_id, DeckVote.user_id == user_id)
    )).scalar_one_or_none()


async def conteggio_per_candidato(session: AsyncSession, round_id: uuid.UUID) -> Dict[uuid.UUID, int]:
    righe = (await session.execute(
        select(DeckVote.candidate_id, func.count()).where(DeckVote.round_id == round_id).group_by(DeckVote.candidate_id)
    )).all()
    return {candidate_id: n for candidate_id, n in righe}


async def vota(
    session: AsyncSession, *, round_id: uuid.UUID, candidate_id: uuid.UUID, user_id: int,
) -> DeckVote:
    """Registra il voto di `user_id` per `candidate_id` in questa tornata. Un voto precedente
    dello stesso utente nella stessa tornata viene SOSTITUITO (update), mai sommato — la richiesta
    esplicita dell'operatore: "possibilità di rifare la votazione modificando il voto"."""
    esistente = await voto_di(session, round_id, user_id)
    if esistente is None:
        esistente = DeckVote(round_id=round_id, candidate_id=candidate_id, user_id=user_id)
        session.add(esistente)
    else:
        esistente.candidate_id = candidate_id
    return esistente
