"""Installare un mazzo nuovo nel sito (v8.5): le immagini nel frontend e la voce nel catalogo.

    python -m tarot_core.tools.installa_mazzo file --set Lovers --slug lovers
    python -m tarot_core.tools.installa_mazzo catalogo --slug lovers --nome "Lovers" [--descrizione "…"] [--attivo]

**`file`** (sul computer di sviluppo, dove sta `Grafica/`): controlla che `Grafica/Cards/<Set>/Web` abbia tutte le 78
carte più il dorso, con i nomi della convenzione (`maj-00.webp`, `bastoni-01.webp`, …, `dorso.webp`), e le copia in
`frontend/public/cards/<slug>/`. Da lì le servono il sito, la lettura, la galleria del negozio e il PDF da stampare
(che le scarica dal sito). Poi si ricostruisce il sito.

**`catalogo`** (dove gira l'API, per esempio con `kubectl exec`): crea o aggiorna la riga del mazzo. Nasce
**spenta** e senza prezzi: prezzi, date di attivazione, spedizione e offerta si decidono dalla console (Mazzi), e
lì la si accende. `--attivo` la accende subito.

Idempotente: rilanciato, non duplica niente. Non tocca mai il mazzo predefinito (il Thoth).

**Senza rilascio**: dalla console (Mazzi → Immagini) si carica lo stesso set come ZIP o come cartella, con le stesse
regole sui nomi; le immagini finiscono nel database e il sito le mostra subito (`tarot/immagini_mazzo.py`). I file
installati da qui, se ci sono, hanno la precedenza.
"""
from __future__ import annotations

import argparse
import asyncio
import re
import shutil
import sys
from pathlib import Path
from typing import List, Optional

RADICE = Path(__file__).resolve().parents[3]
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{1,39}$")


def nomi_attesi() -> List[str]:
    from ..api.deps import get_conoscenza

    return sorted(f"{cid}.webp" for cid in get_conoscenza().carte) + ["dorso.webp"]


def controlla(cartella: Path) -> List[str]:
    """I file mancanti (vuoto se il mazzo è completo)."""
    presenti = {p.name for p in cartella.glob("*.webp")}
    return [n for n in nomi_attesi() if n not in presenti]


def installa_file(nome_set: str, slug: str, *, radice: Path = RADICE) -> int:
    sorgente = radice / "Grafica" / "Cards" / nome_set / "Web"
    if not sorgente.is_dir():
        raise SystemExit(f"manca {sorgente}: prima la versione Web del mazzo (tools/resize_cards.py)")
    mancanti = controlla(sorgente)
    if mancanti:
        raise SystemExit(f"il mazzo {nome_set} è incompleto: mancano {len(mancanti)} file ({', '.join(mancanti[:8])}…)")
    destinazione = radice / "frontend" / "public" / "cards" / slug
    destinazione.mkdir(parents=True, exist_ok=True)
    copiati = 0
    for nome in nomi_attesi():
        da, a = sorgente / nome, destinazione / nome
        if not a.exists() or a.read_bytes() != da.read_bytes():
            shutil.copyfile(da, a)
            copiati += 1
    print(f"{nome_set} → {destinazione.relative_to(radice)}: {copiati} file copiati, {len(nomi_attesi()) - copiati} già uguali")
    return copiati


async def installa_catalogo(slug: str, nome: str, descrizione: Optional[str], attivo: bool) -> str:
    from sqlalchemy import select

    from ..domain.deck_models import Deck
    from ..domain.session import dispose_engine, get_session_factory

    try:
        async with get_session_factory()() as session:
            mazzo = (await session.execute(select(Deck).where(Deck.slug == slug))).scalar_one_or_none()
            if mazzo is not None and mazzo.predefinito:
                raise SystemExit(f"{slug} è il mazzo predefinito: non si tocca da qui")
            if mazzo is None:
                mazzo = Deck(slug=slug, nome=nome, descrizione=descrizione, attivo=attivo, rank=10)
                session.add(mazzo)
                esito = "creato"
            else:
                mazzo.nome = nome
                if descrizione is not None:
                    mazzo.descrizione = descrizione
                if attivo:
                    mazzo.attivo = True
                esito = "aggiornato"
            await session.commit()
            print(f"mazzo {slug}: {esito} ({'acceso' if mazzo.attivo else 'spento: accendilo dalla console, Mazzi'})")
            return esito
    finally:
        await dispose_engine()


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="comando", required=True)
    f = sub.add_parser("file", help="copia le immagini nel frontend, dopo averle controllate")
    f.add_argument("--set", required=True, help="la cartella in Grafica/Cards (per esempio Lovers)")
    f.add_argument("--slug", required=True, help="lo slug del mazzo (per esempio lovers)")
    c = sub.add_parser("catalogo", help="crea o aggiorna la voce del mazzo nel database")
    c.add_argument("--slug", required=True)
    c.add_argument("--nome", required=True)
    c.add_argument("--descrizione")
    c.add_argument("--attivo", action="store_true", help="acceso subito (altrimenti dalla console)")
    a = parser.parse_args(argv)
    if not SLUG.match(a.slug):
        raise SystemExit("slug non valido: minuscole, cifre e trattini, da 2 a 40 caratteri")
    if a.comando == "file":
        installa_file(a.set, a.slug)
    else:
        asyncio.run(installa_catalogo(a.slug, a.nome, a.descrizione, a.attivo))
    return 0


if __name__ == "__main__":
    sys.exit(main())
