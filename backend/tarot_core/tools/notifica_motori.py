"""Annuncia ai motori di ricerca gli articoli del blog nuovi o aggiornati (v8).

    python -m tarot_core.tools.notifica_motori

Lo lancia il CronJob `tarots-notifica-motori` ogni notte a mezzanotte (vedi `deploy/k8s/tarots.yaml`);
dalla console si può fare lo stesso a mano. Esce con 1 se un canale configurato è andato in errore,
così il CronJob risulta fallito e si vede in `kubectl get jobs`.
"""
from __future__ import annotations

import asyncio
import logging
import sys

from ..domain.session import dispose_engine, get_session_factory
from ..tarot.notifiche_motori import esegui


async def _giro() -> bool:
    try:
        async with get_session_factory()() as sessione:
            riga = await esegui(sessione)
        print(f"{len(riga.url)} indirizzi annunciati")
        for canale, esito in riga.esiti.items():
            print(f"  {canale}: {esito['stato']} — {esito['dettaglio']}")
        return riga.riuscita
    finally:
        await dispose_engine()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    return 0 if asyncio.run(_giro()) else 1


if __name__ == "__main__":
    sys.exit(main())
