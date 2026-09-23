"""Le letture giornaliere dell'abbonamento, e da dove si paga una lettura.

**Una finestra mobile di 24 ore, non «oggi».** È la scelta di Personalities, e
vale anche qui: «al giorno» a mezzanotte UTC significherebbe che a Roma il
contatore si azzera all'una di notte, e che chi legge alle 23:50 e alle 00:10
ha usato due giorni in venti minuti. La finestra mobile si spiega da sola:
«hai fatto tre letture nelle ultime 24 ore».

**L'ordine del pagamento.** Prima la quota dell'abbonamento, poi i crediti:
la quota scade col giorno, i crediti comprati no — consumare prima quelli
significherebbe far perdere all'utente ciò che ha già pagato.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta
from typing import Dict, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.base import utcnow
from ..domain.models import Reading
from .entitlements import Diritti

logger = logging.getLogger(__name__)

#: La finestra delle letture «al giorno».
FINESTRA = timedelta(hours=24)

#: Quanto costa una lettura, in crediti. Fisso: un utente che guarda il
#: saldo deve poter dire quante letture gli restano.
COSTO_LETTURA = 1


@dataclass
class Uso:
    letture_24h: int

    def to_dict(self, diritti: Diritti) -> Dict[str, Dict[str, Optional[int]]]:
        limite = diritti.limite("letture_al_giorno")
        return {
            "letture_al_giorno": {
                "usati": self.letture_24h,
                "limite": limite,
                "restanti": None if limite is None else max(0, limite - self.letture_24h),
            },
        }


class ContatoreQuote:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def letture_in_quota_24h(self, user_id: int) -> int:
        """Le letture pagate con la quota nelle ultime 24 ore.

        Solo quelle in quota: le letture pagate con un credito non consumano
        il giorno dell'abbonamento.
        """
        return int(await self._session.scalar(
            select(func.count()).select_from(Reading).where(
                Reading.owner_id == user_id,
                Reading.consumo == "quota",
                Reading.created_at >= utcnow() - FINESTRA,
            )
        ) or 0)

    async def uso(self, user_id: int) -> Uso:
        return Uso(letture_24h=await self.letture_in_quota_24h(user_id))

    async def quota_disponibile(self, user_id: int, diritti: Diritti) -> bool:
        """Se l'abbonamento copre ancora una lettura nelle ultime 24 ore."""
        if diritti.predefiniti:
            return False
        limite = diritti.limite("letture_al_giorno")
        if limite is None:
            return True
        if limite <= 0:
            return False
        return await self.letture_in_quota_24h(user_id) < limite
