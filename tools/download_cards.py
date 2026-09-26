#!/usr/bin/env python
"""Scarica da LitMedia le immagini generate dal sito e le salva in Cards/ col nome
della chiave "file" di prompts.json. Non genera nulla e non costa crediti.

Abbinamento task -> carta:
  1. prompt identico a quello della carta (dopo aver normalizzato newline e i
     `\\n` / `\\"` che arrivano incollando dal JSON grezzo);
  2. altrimenti si cerca la carta con la stessa riga "THE CARD: ..." e si accetta
     se la somiglianza del prompt è >= --min-ratio (default 0.95).
Per ogni carta vale l'ultimo task riuscito. Le immagini già presenti non vengono
sovrascritte (--force per rifarle).

Esempi:
  python download_cards.py --dry-run
  python download_cards.py --skip spade-05
  python download_cards.py --only maj-00 maj-01 --force
  python download_cards.py --quality 92        # WebP con perdita invece di lossless
"""
import argparse
import difflib
import io
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PROMPTS = ROOT / "frontend" / "public" / "cards" / "prompts.json"
DEFAULT_OUT = ROOT / "Cards"
DEFAULT_SKILL = Path(os.environ.get("LITMEDIA_SKILL_DIR", r"C:\Users\atain\.claude\skills\litmedia-skill"))

HISTORY_ENDPOINT = "/lit-video/get-image-history"
FORMATS = {".webp": "WEBP", ".png": "PNG", ".jpg": "JPEG", ".jpeg": "JPEG"}
CARD_LINE = re.compile(r"THE CARD:[^\n]*")


def norm(text: str) -> str:
    # incollando dal JSON grezzo arrivano `\n` e `\"` scritti letteralmente
    return text.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\r\n", "\n").replace('\\"', '"').strip()


def card_key(text: str):
    m = CARD_LINE.search(text)
    return m.group(0).strip() if m else None


def fetch_history(client, endpoint, size=50, max_pages=40):
    rows, page = [], 1
    while page <= max_pages:
        chunk = client.post(endpoint, json={"page": str(page), "page_size": str(size)})
        if not chunk:
            break
        rows += chunk
        if len(chunk) < size:
            break
        page += 1
    return rows


def image_url(rec):
    urls = rec.get("image_urls")
    if isinstance(urls, list) and urls:
        return urls[0]
    return rec.get("image_url") or rec.get("img_url") or None


def match_task(prompt, exact, by_key, min_ratio):
    """Ritorna (card, ratio) o None. ratio=1.0 se identico."""
    p = norm(prompt)
    if p in exact:
        return exact[p], 1.0
    cands = by_key.get(card_key(p) or "", [])
    if len(cands) != 1:
        return None
    ratio = difflib.SequenceMatcher(None, p, norm(cands[0]["prompt"]), autojunk=False).ratio()
    return (cands[0], ratio) if ratio >= min_ratio else None


def save_image(data: bytes, dest: Path, quality):
    from PIL import Image

    fmt = FORMATS.get(dest.suffix.lower())
    if not fmt:
        raise ValueError(f"estensione non supportata: {dest.suffix}")
    img = Image.open(io.BytesIO(data))
    opts = {}
    if fmt == "WEBP":
        opts = {"lossless": True} if quality is None else {"quality": quality, "method": 6}
    elif fmt == "JPEG":
        img = img.convert("RGB")
        opts = {"quality": quality or 95}
    tmp = dest.with_name(dest.name + ".part")
    img.save(tmp, format=fmt, **opts)
    os.replace(tmp, dest)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prompts", type=Path, default=DEFAULT_PROMPTS)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--model", default="14", help='image_model dei task da considerare (14 = GPT Image 2), "any" per tutti')
    ap.add_argument("--skip", nargs="*", default=[], metavar="ID", help="id di carte da saltare")
    ap.add_argument("--only", nargs="*", default=[], metavar="ID", help="scarica solo queste carte")
    ap.add_argument("--min-ratio", type=float, default=0.95)
    ap.add_argument("--quality", type=int, default=None, help="qualità WebP/JPEG; senza, WebP lossless")
    ap.add_argument("--force", action="store_true", help="sovrascrive i file già presenti")
    ap.add_argument("--dry-run", action="store_true", help="mostra cosa farebbe senza scaricare")
    ap.add_argument("--missing", action="store_true", help="elenca anche le carte senza immagine")
    ap.add_argument("--skill-dir", type=Path, default=DEFAULT_SKILL)
    args = ap.parse_args()

    sys.path.insert(0, str(args.skill_dir / "scripts"))
    from shared.client import LitMediaClient

    cards = json.loads(args.prompts.read_text(encoding="utf-8"))["cards"]
    exact = {norm(c["prompt"]): c for c in cards}
    by_key = {}
    for c in cards:
        by_key.setdefault(card_key(norm(c["prompt"])) or "", []).append(c)

    client = LitMediaClient()
    rows = fetch_history(client, HISTORY_ENDPOINT)
    if args.model != "any":
        rows = [r for r in rows if str(r["user_params"].get("image_model")) == args.model]

    best, other = {}, 0  # id carta -> (create_at, task, card, ratio, url)
    for r in rows:
        hit = match_task(r["user_params"].get("prompt", ""), exact, by_key, args.min_ratio)
        if not hit:
            other += 1
            continue
        card, ratio = hit
        url = image_url(r) if r["status"] == 1 else None
        if url and (card["id"] not in best or r["create_at"] > best[card["id"]][0]):
            best[card["id"]] = (r["create_at"], r["create_id"], card, ratio, url)

    args.out.mkdir(parents=True, exist_ok=True)
    saved = skipped = errors = 0
    for cid in sorted(best):
        created, task, card, ratio, url = best[cid]
        if cid in args.skip or (args.only and cid not in args.only):
            continue
        dest = args.out / card["file"]
        when = datetime.fromtimestamp(created).strftime("%d/%m %H:%M")
        how = "identico" if ratio == 1.0 else f"~{ratio:.3f}"
        if dest.exists() and not args.force:
            print(f"= {cid:<10} già presente ({dest.name})")
            skipped += 1
            continue
        if args.dry_run:
            print(f"? {cid:<10} <- task {task} ({when}, {how}) -> {dest.name}")
            continue
        try:
            import requests

            resp = requests.get(url, timeout=120)
            resp.raise_for_status()
            save_image(resp.content, dest, args.quality)
            print(f"+ {cid:<10} <- task {task} ({when}, {how}) -> {dest.name} {dest.stat().st_size / 1e6:.1f} MB")
            saved += 1
        except Exception as exc:  # una carta fallita non ferma le altre
            print(f"! {cid:<10} task {task}: {exc}")
            errors += 1

    missing = [c["id"] for c in cards if c["id"] not in best and c["id"] not in args.skip]
    print(f"\nsalvate {saved} | già presenti {skipped} | errori {errors} | "
          f"carte senza immagine {len(missing)}/{len(cards)} | task non riconducibili a una carta {other}"
          + (" | (dry-run)" if args.dry_run else ""))
    if args.missing and missing:
        print("senza immagine:", " ".join(missing))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
