"""Il giro delle notifiche push (v9, Fase 5).

    python -m tarot_core.tools.notifiche

Lo lancia il CronJob `tarots-notifiche` ogni 15 minuti (vedi `deploy/k8s/tarots.yaml`). In ordine:

1. le **automatiche** (`notifiche/automatiche.py`): per ogni persona con un dispositivo raggiungibile, quelle la cui
   finestra è aperta all'ora **locale** di chi riceve (la carta del giorno alle 8:30 di Roma per chi sta a Roma,
   alle 8:30 di Buenos Aires per chi sta a Buenos Aires), fuori dalle ore di silenzio;
2. le **campagne** arrivate all'ora e quelle già in invio (`notifiche/campagne.py`).

Senza service account di Firebase le app non ricevono niente (e lo si vede nei conteggi: `nessun_canale` se manca
anche il Web Push); le chiavi VAPID del Web Push si generano da sole al primo giro.

Rieseguirlo è innocuo: ogni invio è prenotato nel registro `invii_notifica` con un indice unico (tipo, persona e
giorno locale; campagna e persona), e un giro ripetuto trova la prenotazione e salta.
"""
from __future__ import annotations

import asyncio
import logging
import sys
from collections import Counter
from datetime import datetime
from typing import Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..notifiche import automatiche, campagne
from ..notifiche.invio import Postino

logger = logging.getLogger(__name__)


async def giro(session: AsyncSession, *, adesso: Optional[datetime] = None) -> Dict[str, int]:
    """Automatiche, poi campagne. Restituisce i conteggi; fa il commit."""
    postino = await Postino.prepara(session, adesso=adesso)
    await session.commit()  # le chiavi VAPID e i segreti appena generati restano anche se il giro si ferma
    conti: Counter = Counter()
    conti.update(await automatiche.giro(session, postino))
    conti.update(await campagne.giro(session, postino))
    await session.commit()
    conti["invii"] = postino.inviati
    return dict(conti)


async def _main() -> None:
    from ..configurazioni.avvio import prepara_strumento
    from ..domain.session import dispose_engine, get_session_factory

    try:
        async with get_session_factory()() as sessione:
            await prepara_strumento(sessione)
            conti = await giro(sessione)
        print(", ".join(f"{k}: {v}" for k, v in sorted(conti.items())) or "niente da fare")
    finally:
        await dispose_engine()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    asyncio.run(_main())
    return 0


if __name__ == "__main__":
    sys.exit(main())
