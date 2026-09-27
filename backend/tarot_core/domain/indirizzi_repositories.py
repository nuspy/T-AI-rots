"""Letture e scritture sugli indirizzi di spedizione (v5, Fase B5): solo query e la piccola regola
del "predefinito" — un utente ne ha al più uno."""
from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .ordini_models import IndirizzoSpedizione


async def elenca(session: AsyncSession, user_id: int) -> List[IndirizzoSpedizione]:
    righe = (
        await session.execute(
            select(IndirizzoSpedizione)
            .where(IndirizzoSpedizione.user_id == user_id)
            .order_by(IndirizzoSpedizione.predefinito.desc(), IndirizzoSpedizione.created_at),
        )
    ).scalars()
    return list(righe)


async def per_id(session: AsyncSession, user_id: int, indirizzo_id: uuid.UUID) -> Optional[IndirizzoSpedizione]:
    riga = await session.get(IndirizzoSpedizione, indirizzo_id)
    return riga if riga is not None and riga.user_id == user_id else None


async def azzera_predefinito(session: AsyncSession, user_id: int, *, tranne: Optional[uuid.UUID] = None) -> None:
    """Toglie il flag «predefinito» da ogni altro indirizzo dello stesso utente: ce n'è al più uno."""
    for riga in await elenca(session, user_id):
        if riga.predefinito and riga.id != tranne:
            riga.predefinito = False
