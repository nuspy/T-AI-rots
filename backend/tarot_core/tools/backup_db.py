"""Il backup notturno del database sul NAS (v8.3), per il CronJob `tarots-backup`.

    python -m tarot_core.tools.backup_db            # il backup notturno (se acceso dalla console)
    python -m tarot_core.tools.backup_db --ora      # subito, anche se spento (come «Esegui ora»)

Destinazione e copie da tenere si scelgono dalla console (Backup); la credenziale sta nel Secret `tarots-backup`.
Esce con 1 se il backup è fallito (il CronJob lo mostra come Job fallito, e parte l'email di avviso).
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys

from ..domain.session import dispose_engine, get_session_factory
from ..tarot.backup import esegui_backup


async def _giro(manuale: bool) -> int:
    try:
        riga = await esegui_backup(get_session_factory(), manuale=manuale)
    finally:
        await dispose_engine()
    print(f"backup: {riga.esito} {riga.file or ''} {riga.dettaglio or ''}".strip())
    return 1 if riga.esito == "errore" else 0


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ora", action="store_true", help="esegue anche se il backup è spento in console")
    return asyncio.run(_giro(manuale=parser.parse_args().ora))


if __name__ == "__main__":
    sys.exit(main())
