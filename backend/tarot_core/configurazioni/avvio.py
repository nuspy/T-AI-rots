"""Ciò che l'API fa partendo, per le configurazioni della console (v9, Fase 2c), e il rinfresco periodico.

All'avvio, in una transazione sola e prima della prima richiesta:

1. i segreti interni (impronta degli IP, sale delle condivisioni): presi dall'ambiente o generati, e messi in uso;
2. la copia una tantum dall'ambiente al database (`importa.dall_ambiente`), in fila fra le repliche;
3. l'istantanea dei valori della console (`correnti.carica`).

Poi, finché il processo vive, l'istantanea si rilegge ogni `correnti.ETA_MASSIMA` secondi: una modifica salvata
dalla console su un'altra replica arriva qui senza riavvii.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable

from sqlalchemy.ext.asyncio import AsyncSession

from . import correnti, importa, segreti

logger = logging.getLogger(__name__)


async def prepara(fabbrica: Callable[[], Any]) -> None:
    """Segreti, importazione dall'ambiente, istantanea. Solleva se il database non risponde: chi chiama decide."""
    async with fabbrica() as session:
        await segreti.assicura_tutti(session)
        copiate = await importa.dall_ambiente(session)
        await session.commit()
        await correnti.carica(session)
    if copiate:
        logger.info("Importate dall'ambiente: %s", ", ".join(copiate))


async def prepara_strumento(session: AsyncSession) -> None:
    """Per i CronJob: segreti interni e istantanea, senza importazione (quella la fa l'API)."""
    await segreti.assicura_tutti(session)
    await session.commit()
    await correnti.carica(session)


async def aggiorna_periodicamente(fabbrica: Callable[[], Any], ogni: float = correnti.ETA_MASSIMA) -> None:
    """Rilegge l'istantanea per sempre (si ferma con la cancellazione del compito). Un errore non la ferma."""
    while True:
        await asyncio.sleep(ogni)
        try:
            async with fabbrica() as session:
                await correnti.carica(session)
        except asyncio.CancelledError:
            raise
        except Exception:  # noqa: BLE001 — un database lento per un giro non deve spegnere il rinfresco
            logger.warning("Configurazioni della console non rilette: resta l'istantanea precedente", exc_info=True)
