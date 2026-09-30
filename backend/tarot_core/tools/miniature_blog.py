"""Crea le miniature delle immagini già caricate (v8.3).

    python -m tarot_core.tools.miniature_blog [--lotto N]

Le immagini caricate da adesso in poi hanno già la loro miniatura (`assicura_miniatura`, a ogni caricamento e a
ogni assegnazione); questo strumento la dà a quelle caricate prima. Idempotente: salta chi l'ha già, e si può
fermare e rilanciare. Gli avatar non ne hanno bisogno.
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys

from sqlalchemy import select

from ..domain.blog_models import MediaImage
from ..domain.blog_repositories import assicura_miniatura
from ..domain.session import dispose_engine, get_session_factory


async def crea_miniature(fabbrica, lotto: int = 20) -> int:
    """Dà la miniatura a tutte le immagini che non l'hanno, `lotto` per transazione. Restituisce quante ne ha fatte."""
    fatte = 0
    while True:
        async with fabbrica() as sessione:
            immagini = list((await sessione.execute(
                select(MediaImage).where(MediaImage.mini_webp.is_(None), MediaImage.uso != "avatar").limit(lotto)
            )).scalars())
            if not immagini:
                return fatte
            for img in immagini:
                await assicura_miniatura(img)
            await sessione.commit()
            fatte += len(immagini)
            print(f"miniature create: {fatte}", flush=True)


async def _giro(lotto: int) -> int:
    try:
        return await crea_miniature(get_session_factory(), lotto)
    finally:
        await dispose_engine()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--lotto", type=int, default=20, help="immagini per transazione (default 20)")
    args = parser.parse_args()
    fatte = asyncio.run(_giro(max(1, args.lotto)))
    print(f"fatto: {fatte} miniature nuove")
    return 0


if __name__ == "__main__":
    sys.exit(main())
