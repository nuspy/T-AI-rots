"""Il giro notturno degli analytics (v8): riepilogo giornaliero e pulizia del dettaglio scaduto.

    python -m tarot_core.tools.analytics_notte [--giorni N]

Lo lancia il CronJob `tarots-analytics-notte` (vedi `deploy/k8s/tarots.yaml`). Riepiloga gli ultimi
tre giorni conclusi (idempotente: un giro saltato si recupera la notte dopo), poi cancella sessioni ed
eventi oltre la conservazione e i sali giornalieri scaduti.
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys

from lanterna.giornaliero import notte

from ..analytics.configurazione import configurazione
from ..domain.analytics_models import TABELLE
from ..domain.session import dispose_engine, get_session_factory


async def _giro(giorni: int) -> None:
    try:
        async with get_session_factory()() as sessione:
            resoconto = await notte(sessione, TABELLE, configurazione(), giorni=giorni)
        for chiave, valore in resoconto.items():
            print(f"{chiave}: {valore}")
    finally:
        await dispose_engine()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--giorni", type=int, default=3, help="quanti giorni conclusi riepilogare (predefinito 3)")
    asyncio.run(_giro(max(1, parser.parse_args().giorni)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
