"""Il PDF di prova di un mazzo nuovo, dalle immagini locali in `Grafica/Cards/<set>/Web/` (v5, "mazzi
multipli"). Non l'endpoint di produzione (`tarot/stampa_mazzo.py:pdf_per_mazzo`, che scarica dal sito
pubblico): questo legge direttamente da disco, perché il mazzo non è ancora pubblicato da nessuna
parte — è ancora nella cartella dove lo sta componendo chi lo sta creando.

    python -m tarot_core.tools.stampa_bozza_mazzo --set Lovers

Riusa la stessa griglia A4 e lo stesso specchio fronte/retro di `stampa_mazzo.genera_pdf` — nessun
layout nuovo. Il marchio è sempre presente (a differenza del prodotto di produzione, dove compare solo
sul PDF gratuito): qui è un timbro di copyright completo, non il semplice nome del sito, perché questo
PDF di prova non distingue un percorso di acquisto da uno gratuito.
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..tarot.conoscenza import Conoscenza
from ..tarot.stampa_mazzo import ESTENSIONE, genera_pdf
from .crea_mazzo import GRAFICA_DIR


def _carica_locali(cartella_web: Path, nomi_file: List[str]) -> Dict[str, bytes]:
    """Come `stampa_mazzo.carica_immagini`, ma solo da disco: una carta senza immagine ancora pronta
    resta assente (il PDF disegna un segnaposto al suo posto, non fallisce l'intera stampa)."""
    trovate: Dict[str, bytes] = {}
    for nome_file in nomi_file:
        percorso = cartella_web / nome_file
        if percorso.exists():
            trovate[nome_file] = percorso.read_bytes()
    return trovate


def genera(nome_set: str, *, anno: Optional[int] = None) -> Path:
    cartella = GRAFICA_DIR / nome_set
    cartella_web = cartella / "Web"
    if not cartella_web.exists():
        raise SystemExit(f"{cartella_web} non esiste: lanciare prima tools/resize_cards.py su questo mazzo.")

    conoscenza = Conoscenza.carica()
    ordine_carte = conoscenza.ordine
    nomi_file = [f"{card_id}.{ESTENSIONE}" for card_id in ordine_carte] + [f"dorso.{ESTENSIONE}"]
    immagini = _carica_locali(cartella_web, nomi_file)
    mancanti = [n for n in nomi_file if n not in immagini]
    if mancanti:
        print(f"attenzione: {len(mancanti)} immagini mancanti, segnaposto al loro posto: {', '.join(mancanti[:5])}"
              + (", ..." if len(mancanti) > 5 else ""), file=sys.stderr)

    marchio_testo = f"© {anno or datetime.now().year} Copyright https://tarots.chat"
    corpo = genera_pdf(ordine_carte, immagini, gratuito=True, marchio_testo=marchio_testo)

    destinazione = cartella / f"{nome_set}-stampa.pdf"
    destinazione.write_bytes(corpo)
    return destinazione


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(prog="tarot_core.tools.stampa_bozza_mazzo", description=__doc__.split("\n\n")[0])
    p.add_argument("--set", required=True, help="Nome del mazzo, es. 'Lovers' (nome della sua cartella).")
    p.add_argument("--anno", type=int, default=None, help="Anno nel marchio di copyright (default: quello corrente).")
    args = p.parse_args(argv)

    destinazione = genera(args.set, anno=args.anno)
    print(f"PDF scritto in {destinazione}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
