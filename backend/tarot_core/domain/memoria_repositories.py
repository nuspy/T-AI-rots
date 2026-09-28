"""Letture e scritture su `user_memories`: ogni funzione filtra per `owner_id`, mai delegato al chiamante
(vedi il vincolo di `OwnedMixin` — qui non ereditato per la non-nullabilità, ma lo stesso principio vale).
"""
from __future__ import annotations

import uuid
from typing import Iterable, List, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..tarot.memoria_retrieval import CandidatoMemoria
from .memory_models import UserMemory


async def candidati_per(session: AsyncSession, owner_id: int) -> List[CandidatoMemoria]:
    """Tutte le memorie correnti dell'utente (non sostituite), pronte per il ranking in `rilevanti()`.

    Niente `LIMIT`/`ORDER BY` per similarità qui: senza un indice vettoriale nativo (vedi
    `memory_models.py`), il filtro utile è solo «di questo utente, non superata» — il ranking vero
    lo fa `rilevanti()` in Python sull'insieme così ottenuto.
    """
    righe = (
        await session.execute(
            select(UserMemory).where(
                UserMemory.owner_id == owner_id,
                UserMemory.superseded_by.is_(None),
            )
        )
    ).scalars()
    return [
        CandidatoMemoria(
            id=r.id, contenuto=r.contenuto, tipo=r.tipo,
            campo_attinenza=r.campo_attinenza, embedding=r.embedding,
        )
        for r in righe
    ]


async def elenca(session: AsyncSession, owner_id: int) -> List[UserMemory]:
    """Le memorie correnti dell'utente, per la sezione "Memoria" del profilo (Fase D)."""
    righe = (
        await session.execute(
            select(UserMemory)
            .where(UserMemory.owner_id == owner_id, UserMemory.superseded_by.is_(None))
            .order_by(UserMemory.updated_at.desc())
        )
    ).scalars()
    return list(righe)


async def per_id(session: AsyncSession, owner_id: int, memoria_id: uuid.UUID) -> Optional[UserMemory]:
    riga = await session.get(UserMemory, memoria_id)
    return riga if riga is not None and riga.owner_id == owner_id else None


async def catena(session: AsyncSession, owner_id: int, memoria_id: uuid.UUID) -> List[UserMemory]:
    """Una memoria variabile e le versioni che ha sostituito, dalla più vecchia alla più recente.

    Serve al confronto prima/dopo della sintesi (Fase C): senza la catena, «la situazione è
    cambiata rispetto all'ultima volta» non avrebbe un "prima" con cui confrontarsi.
    """
    corrente = await per_id(session, owner_id, memoria_id)
    if corrente is None:
        return []
    catena_righe = [corrente]
    righe = (
        await session.execute(
            select(UserMemory).where(UserMemory.owner_id == owner_id, UserMemory.superseded_by.isnot(None))
        )
    ).scalars()
    per_predecessore = {r.superseded_by: r for r in righe}
    # Risale la catena partendo dalla testa: ogni riga sostituita punta a chi l'ha sostituita, non
    # il contrario, quindi si cerca chi ha `superseded_by == id` della riga corrente.
    cursore = corrente
    visitati = {cursore.id}
    while True:
        precedente = next((r for r in per_predecessore.values() if r.superseded_by == cursore.id), None)
        if precedente is None or precedente.id in visitati:
            break
        catena_righe.append(precedente)
        visitati.add(precedente.id)
        cursore = precedente
    return list(reversed(catena_righe))


async def elimina(session: AsyncSession, owner_id: int, memoria_id: uuid.UUID) -> bool:
    riga = await per_id(session, owner_id, memoria_id)
    if riga is None:
        return False
    await session.delete(riga)
    return True


async def elimina_molte(session: AsyncSession, owner_id: int, ids: Sequence[uuid.UUID]) -> int:
    righe = [r for r in await elenca(session, owner_id) if r.id in set(ids)]
    for riga in righe:
        await session.delete(riga)
    return len(righe)


async def elimina_tutte(session: AsyncSession, owner_id: int) -> int:
    righe = (
        await session.execute(select(UserMemory).where(UserMemory.owner_id == owner_id))
    ).scalars().all()
    for riga in righe:
        await session.delete(riga)
    return len(righe)
