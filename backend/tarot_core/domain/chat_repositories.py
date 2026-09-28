"""Letture e scritture sui turni della chat proattiva: filtrate per `owner_id`, come ogni tabella di
proprietà (vedi `memoria_repositories.py`, `indirizzi_repositories.py`)."""
from __future__ import annotations

from typing import List, Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .chat_models import ChatProattivaTurno


async def recenti(session: AsyncSession, owner_id: int, *, limite: int = 20) -> List[ChatProattivaTurno]:
    """Gli ultimi turni, in ordine cronologico (non decrescente): è la trascrizione da mostrare e da
    passare al modello, non un elenco da sfogliare a ritroso."""
    righe = (
        await session.execute(
            select(ChatProattivaTurno)
            .where(ChatProattivaTurno.owner_id == owner_id)
            .order_by(ChatProattivaTurno.ordine.desc())
            .limit(limite)
        )
    ).scalars().all()
    return list(reversed(righe))


async def prossimo_ordine(session: AsyncSession, owner_id: int) -> int:
    massimo = (
        await session.execute(
            select(func.max(ChatProattivaTurno.ordine)).where(ChatProattivaTurno.owner_id == owner_id)
        )
    ).scalar_one_or_none()
    return (massimo or 0) + 1


async def aggiungi(
    session: AsyncSession, owner_id: int, *, ruolo: str, testo: str, proposta: Optional[dict] = None,
) -> ChatProattivaTurno:
    turno = ChatProattivaTurno(
        owner_id=owner_id, ordine=await prossimo_ordine(session, owner_id),
        ruolo=ruolo, testo=testo, proposta=proposta,
    )
    session.add(turno)
    await session.flush()
    return turno


def trascrizione(turni: Sequence[ChatProattivaTurno]) -> str:
    righe = [f"{'Oracolo' if t.ruolo == 'ai' else 'Utente'}: {t.testo}" for t in turni]
    return "\n".join(righe) or "(nessun turno ancora)"
