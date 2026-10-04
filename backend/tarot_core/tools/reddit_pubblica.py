"""Porta su Reddit gli articoli del blog in coda (v8.6).

    python -m tarot_core.tools.reddit_pubblica

Lo lancia il CronJob `tarots-reddit` ogni quarto d'ora (vedi `deploy/k8s/tarots.yaml`): prende gli articoli
programmati quando la loro data arriva, quelli rimandati per il limite di frequenza di Reddit e quelli che aspettano
l'intervallo fra un post e l'altro. Le pubblicazioni dalla console e dalla REST partono già da sole, subito. Con la
pubblicazione su Reddit spenta non fa nulla. Esce con 1 se un articolo è finito in errore, così il CronJob risulta
fallito e si vede in `kubectl get jobs`.
"""
from __future__ import annotations

import asyncio
import logging
import sys

from ..domain.session import dispose_engine, get_session_factory
from ..tarot.reddit import lavora


async def _giro() -> bool:
    try:
        esito = await lavora(get_session_factory())
        print(", ".join(f"{k}: {v}" for k, v in esito.items()))
        return esito.get("stato") != "errore" and not esito.get("errori")
    finally:
        await dispose_engine()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    return 0 if asyncio.run(_giro()) else 1


if __name__ == "__main__":
    sys.exit(main())
