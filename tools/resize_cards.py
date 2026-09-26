#!/usr/bin/env python
"""Rimpicciolisce le immagini di Cards/ e le salva con lo stesso nome in Cards/web/
come WebP ad alta compressione (con perdita).

Di default ogni lato è ridotto al 25% dell'originale (1440x2560 -> 360x640).
Le immagini già presenti in Cards/web/ vengono rifatte: la cartella è un derivato.

Esempi:
  python resize_cards.py
  python resize_cards.py --scala 50 --quality 70
  python resize_cards.py --only bastoni-01 maj-00
"""
import argparse
import sys
from pathlib import Path

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SRC = ROOT / "Cards"
DEFAULT_DST = DEFAULT_SRC / "web"
EXTENSIONS = {".webp", ".png", ".jpg", ".jpeg"}


def resize_one(src: Path, dst: Path, scale: float, quality: int) -> tuple[tuple[int, int], tuple[int, int]]:
    with Image.open(src) as im:
        im.load()
        old = im.size
        new = (max(1, round(old[0] * scale)), max(1, round(old[1] * scale)))
        mode = "RGBA" if im.mode in ("RGBA", "LA", "P") and "A" in im.getbands() else "RGB"
        out = im.convert(mode).resize(new, Image.LANCZOS)
    # method=6: encoder più lento ma con il file più piccolo a parità di qualità.
    out.save(dst, "WEBP", quality=quality, method=6)
    return old, new


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", type=Path, default=DEFAULT_SRC, help="cartella delle immagini originali")
    ap.add_argument("--dst", type=Path, default=DEFAULT_DST, help="cartella di destinazione")
    ap.add_argument("--scala", type=float, default=25, help="percentuale di ogni lato (default 25)")
    ap.add_argument("--quality", type=int, default=60, help="qualità WebP 0-100, più bassa = più compressa (default 60)")
    ap.add_argument("--only", nargs="+", metavar="NOME", help="solo questi file (nome senza estensione)")
    args = ap.parse_args()

    if not 0 < args.scala <= 100:
        ap.error("--scala deve essere tra 0 (escluso) e 100")
    if not 0 <= args.quality <= 100:
        ap.error("--quality deve essere tra 0 e 100")

    files = sorted(p for p in args.src.iterdir() if p.is_file() and p.suffix.lower() in EXTENSIONS)
    if args.only:
        wanted = set(args.only)
        files = [p for p in files if p.stem in wanted]
    if not files:
        print(f"Nessuna immagine trovata in {args.src}")
        return 1

    args.dst.mkdir(parents=True, exist_ok=True)
    tot_in = tot_out = 0
    for i, src in enumerate(files, 1):
        dst = args.dst / f"{src.stem}.webp"
        old, new = resize_one(src, dst, args.scala / 100, args.quality)
        size_in, size_out = src.stat().st_size, dst.stat().st_size
        tot_in += size_in
        tot_out += size_out
        print(f"[{i:>2}/{len(files)}] {dst.name:<26} {old[0]}x{old[1]} -> {new[0]}x{new[1]}  "
              f"{size_in / 1024:8.0f} KB -> {size_out / 1024:6.1f} KB")

    print(f"\n{len(files)} immagini in {args.dst}")
    print(f"Totale: {tot_in / 1024 / 1024:.1f} MB -> {tot_out / 1024 / 1024:.2f} MB "
          f"({100 * tot_out / tot_in:.2f}% dell'originale)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
