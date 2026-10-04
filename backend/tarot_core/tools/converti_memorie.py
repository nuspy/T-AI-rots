"""Una tantum: le memorie di prima (`user_memories`) diventano voci dello stato sintetico (`memoria_stato`).

    python -m tarot_core.tools.converti_memorie            # converte
    python -m tarot_core.tools.converti_memorie --prova    # conta soltanto, senza scrivere

Per ogni persona con memorie correnti (non sostituite): `stabile` resta stabile, `variabile` diventa volatile con la
data del suo ultimo aggiornamento (se è vecchia, l'oblio dello stato la toglie subito); la salute entra solo con il
consenso `dati_particolari` (art. 9). Le memorie di prima restano nella loro tabella: la persona le vede ancora dal
profilo e le può cancellare. Si può rilanciare: le voci già presenti non si duplicano. Una persona per transazione.
In produzione la tabella era vuota il 4/10/2026: lo strumento serve agli impianti che l'avevano riempita.
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from typing import Dict

from sqlalchemy import distinct, select

from ..domain import consent_repositories, memoria_repositories
from ..domain.memory_models import UserMemory
from ..domain.session import dispose_engine, get_session_factory


async def converti_tutte(fabbrica, *, prova: bool = False) -> Dict[str, int]:
    """Converte le memorie di tutte le persone. Restituisce persone e voci aggiunte."""
    async with fabbrica() as s:
        persone = list((await s.execute(
            select(distinct(UserMemory.owner_id)).where(UserMemory.superseded_by.is_(None))
        )).scalars())
    esito = {"persone": 0, "voci": 0}
    for owner_id in persone:
        async with fabbrica() as s:
            salute = await consent_repositories.accettato(s, owner_id, "dati_particolari")
            aggiunte = await memoria_repositories.converti_in_stato(s, owner_id, salute_ammessa=salute)
            if prova:
                await s.rollback()
            else:
                await s.commit()
        if aggiunte:
            esito["persone"] += 1
            esito["voci"] += aggiunte
    return esito


async def _giro(prova: bool) -> None:
    try:
        esito = await converti_tutte(get_session_factory(), prova=prova)
        print(f"{'(prova) ' if prova else ''}persone convertite: {esito['persone']}; voci aggiunte: {esito['voci']}")
    finally:
        await dispose_engine()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--prova", action="store_true", help="conta soltanto, senza scrivere")
    asyncio.run(_giro(p.parse_args().prova))
    return 0


if __name__ == "__main__":
    sys.exit(main())
