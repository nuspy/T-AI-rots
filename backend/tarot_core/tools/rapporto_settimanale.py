"""Il rapporto settimanale degli analytics per email (v8).

    python -m tarot_core.tools.rapporto_settimanale

Lo lancia il CronJob `tarots-rapporto-settimanale` ogni lunedì alle 0:30, ora italiana (la notte fra
domenica e lunedì), per la settimana appena conclusa. Esce con 1 se l'invio non è riuscito, così il
Job risulta fallito in `kubectl get jobs`; l'esito resta anche nella console (Analytics → Rapporti).
"""
from __future__ import annotations

import asyncio
import logging
import sys

from ..analytics.rapporto import invia_rapporto
from ..api.deps import aggiorna_assegnazioni, provider_per
from ..domain.session import dispose_engine, get_session_factory
from ..llm.compiti import Compito


async def _giro() -> bool:
    try:
        async with get_session_factory()() as sessione:
            await aggiorna_assegnazioni(sessione)
            esito = await invia_rapporto(sessione, provider=provider_per(Compito.ANALISI_DATI))
        print(f"settimana {esito['da']} – {esito['a']}: {esito['dettaglio']} ({len(esito['destinatari'])} destinatari)")
        return esito["riuscito"]
    finally:
        await dispose_engine()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    return 0 if asyncio.run(_giro()) else 1


if __name__ == "__main__":
    sys.exit(main())
