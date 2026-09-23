"""Scrive i prompt per generare le immagini delle 78 carte.

    python -m tarot_core.tools.prompt_immagini
    # → frontend/public/cards/prompts.json

**Ogni prompt è autonomo.** Il generatore di immagini riceve una carta alla
volta e non sa nulla delle altre: per questo il blocco di stile, le regole del
testo e il font si ripetono per intero in ogni prompt, identici. È ciò che
tiene uniforme il mazzo.

Un prompt si compone di quattro parti:

1. lo **stile** comune (tecnica, cornice, luce, formato);
2. la **carta**: nome, attribuzioni esoteriche lette da `deck.json`;
3. la **scena**: il contenuto, scritto a mano per ogni carta in
   `knowledge/immagini/scene_*.py`, con i simboli spiegati;
4. il **testo** da scrivere sulla carta, con posizione e font.

Il file prodotto è `{id}.webp`: lo stesso nome che il frontend carica con
`NEXT_PUBLIC_CARD_EXT=webp`.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any, Dict, List

from ..knowledge.immagini import scene_bastoni, scene_coppe, scene_dischi, scene_maggiori, scene_spade
from ..paths import KNOWLEDGE_DIR, PROJECT_ROOT

USCITA = PROJECT_ROOT.parent / "frontend" / "public" / "cards" / "prompts.json"

LARGHEZZA, ALTEZZA = 1200, 2000

SEMI = {"bastoni": "Wands", "coppe": "Cups", "spade": "Swords", "dischi": "Disks"}
ELEMENTI = {"fuoco": "Fire", "acqua": "Water", "aria": "Air", "terra": "Earth", "spirito": "Spirit"}
ELEMENTO_SEME = {"bastoni": "fuoco", "coppe": "acqua", "spade": "aria", "dischi": "terra"}
NUMERI = {
    1: "Ace", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six",
    7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten",
}
CORTI = {"cavaliere": "Knight", "regina": "Queen", "principe": "Prince", "principessa": "Princess"}
SEPHIROTH = {
    "Kether": "Kether (the Crown, 1st sephira: pure unity, brilliant white)",
    "Chokmah": "Chokmah (Wisdom, 2nd sephira: the dynamic father force, soft grey)",
    "Binah": "Binah (Understanding, 3rd sephira: the great dark mother, black and deep indigo)",
    "Chesed": "Chesed (Mercy, 4th sephira: order and benevolent rule, blue)",
    "Geburah": "Geburah (Severity, 5th sephira: strength and conflict, scarlet red)",
    "Tiphareth": "Tiphareth (Beauty, 6th sephira: harmony, the solar heart, golden yellow)",
    "Netzach": "Netzach (Victory, 7th sephira: emotion and nature, emerald green)",
    "Hod": "Hod (Splendour, 8th sephira: intellect and form, orange)",
    "Yesod": "Yesod (Foundation, 9th sephira: the astral, the Moon, violet)",
    "Malkuth": "Malkuth (the Kingdom, 10th sephira: the material world, citrine, olive, russet and black)",
}
TRADUZIONI_ASTRO = {
    "Ariete": "Aries", "Toro": "Taurus", "Gemelli": "Gemini", "Cancro": "Cancer", "Leone": "Leo",
    "Vergine": "Virgo", "Bilancia": "Libra", "Scorpione": "Scorpio", "Sagittario": "Sagittarius",
    "Capricorno": "Capricorn", "Acquario": "Aquarius", "Pesci": "Pisces",
    "Sole": "the Sun", "Luna": "the Moon", "Mercurio": "Mercury", "Venere": "Venus",
    "Marte": "Mars", "Giove": "Jupiter", "Saturno": "Saturn",
    "Aria": "Air", "Acqua": "Water", "Fuoco": "Fire", "Terra": "Earth", "Spirito": "Spirit",
    # Le chiavi più lunghe prima: «Radice del» mangerebbe «Radice dell'».
    "Radice dell'": "Root of ", "Radice della": "Root of", "Radice del": "Root of",
    "Quadrante celeste di": "celestial quadrant of", "trono dell'Asso": "throne of the Ace",
    " in ": " in ", " e ": " and ",
}

STILE = (
    "STYLE (identical for every card of this deck, follow it exactly): a full-colour esoteric tarot card "
    "illustration, portrait format with a 3:5 aspect ratio ({w}x{h} px), the whole card visible edge to edge. "
    "Original artwork inspired by the symbolism of the Thoth Tarot tradition of Aleister Crowley and the "
    "Golden Dawn, not a copy of any existing deck or painting. Painted in opaque gouache and tempera with a "
    "visionary, early-20th-century occult art-deco sensibility: projective geometry, interpenetrating "
    "translucent planes, sweeping curved lines of force, prismatic rays of light, crystalline facets, sacred "
    "geometry underlying the composition. Rich, saturated, luminous colour with jewel tones and subtle "
    "gradients, soft inner glow, fine visible brush texture, crisp clean outlines on symbols; no photographic "
    "realism, no 3D render look. Every card has the SAME border: a thin double gold frame (outer line 1.5% of "
    "the width, inner hairline) on a very dark indigo margin (#0d0a1a) about 4% of the card width all around, "
    "with small eight-pointed gold stars in the four corners. Inside the frame the painting fills the space. "
    "At the top, inside the frame, a narrow dark indigo band (about 6% of the card height) for the upper text; "
    "at the bottom a slightly taller dark indigo title banner (about 9% of the card height) with a thin gold "
    "rule above it, for the card name. Consistent lighting from within the image, harmonious and balanced, "
    "sharp details, high resolution, print quality."
).format(w=LARGHEZZA, h=ALTEZZA)

TESTO = (
    "TEXT ON THE CARD (render it exactly, correctly spelled, perfectly legible, and write nothing else): "
    "in the top band, centred: \"{alto}\". In the bottom title banner, centred: \"{basso}\". "
    "Font for all lettering: Cinzel (a classical Roman inscriptional serif), ALL CAPITALS, generous letter "
    "spacing, warm metallic gold colour (#d8b45a to #f1d68e) with a very subtle engraved look, on the dark "
    "indigo bands; the top text slightly smaller than the bottom title. Apart from these two lines, the only "
    "other marks allowed are the esoteric glyphs described in the scene (Hebrew letters, astrological and "
    "alchemical symbols), drawn as symbols inside the painting and not as captions."
)

NEGATIVO = (
    "photograph, photorealistic, 3D render, CGI, anime, cartoon, comic style, flat vector clip art, "
    "watermark, signature, logo, extra text, captions, misspelled text, garbled letters, random letters, "
    "wrong card name, modern objects, cropped frame, missing border, different border style, "
    "border without stars, low resolution, blurry, jpeg artifacts, deformed anatomy, extra limbs, "
    "extra fingers, nudity, gore, horror"
)


def _traduci(testo: str) -> str:
    out = testo or ""
    for it, en in TRADUZIONI_ASTRO.items():
        out = out.replace(it, en)
    return out


def _testi(c: Dict[str, Any]) -> tuple[str, str, str]:
    """Il testo in alto, quello in basso e il nome completo, in inglese."""
    if c["arcano"] == "maggiore":
        alto = c["numero_romano"] or "0"
        basso = c["nome_thoth"].upper()
        return alto, basso, f"{alto} — {c['nome_thoth']}"
    seme = SEMI[c["seme"]]
    if c.get("corte"):
        figura = CORTI[c["rango"]]
        alto = (
            f"{ELEMENTI[c['sottoelemento']]} of {ELEMENTI[ELEMENTO_SEME[c['seme']]]}".upper()
        )
        basso = f"{figura} of {seme}".upper()
        return alto, basso, f"{figura} of {seme}"
    numero = NUMERI[c["numero"]]
    alto = f"{numero} of {seme}".upper()
    basso = (c.get("titolo_thoth") or "").upper()
    return alto, basso, f"{numero} of {seme} — {c.get('titolo_thoth')}"


def _identita(c: Dict[str, Any]) -> str:
    """Chi è la carta, in termini esoterici: ripetuto in ogni prompt."""
    elemento = ELEMENTI.get(c["elemento"], c["elemento"])
    astro = _traduci(c.get("astrologia") or "")
    colori = ", ".join(c.get("colori") or [])
    if c["arcano"] == "maggiore":
        lettera = c.get("lettera_ebraica") or {}
        collega = " and ".join(c.get("collega") or [])
        return (
            f"THE CARD: Major Arcanum {c['numero_romano']}, \"{c['nome_thoth']}\", of the Thoth tradition. "
            f"Hebrew letter {lettera.get('nome')} ({lettera.get('glifo')}, numerical value "
            f"{lettera.get('valore')}); path {c.get('percorso')} on the Kabbalistic Tree of Life, joining the "
            f"sephiroth {collega}; attribution: {astro}; element: {elemento}. Key colours: {colori}."
        )
    seme = SEMI[c["seme"]]
    sefira = SEPHIROTH.get(c.get("sefira") or "", c.get("sefira") or "")
    if c.get("corte"):
        return (
            f"THE CARD: {CORTI[c['rango']]} of {seme} of the Thoth tradition, the "
            f"{ELEMENTI[c['sottoelemento']]} of {ELEMENTI[ELEMENTO_SEME[c['seme']]]}; associated with "
            f"{sefira}; zodiacal attribution: {astro}. Key colours: {colori}."
        )
    titolo = c.get("titolo_thoth") or ""
    return (
        f"THE CARD: {NUMERI[c['numero']]} of {seme}, titled \"{titolo}\", of the Thoth tradition; element "
        f"{elemento}; sephira {sefira}; astrological attribution: {astro}. Key colours: {colori}."
    )


def scene() -> Dict[str, str]:
    tutte: Dict[str, str] = {}
    for modulo in (scene_maggiori, scene_bastoni, scene_coppe, scene_spade, scene_dischi):
        tutte.update(modulo.SCENE)
    return tutte


def costruisci() -> Dict[str, Any]:
    mazzo = json.loads((KNOWLEDGE_DIR / "deck.json").read_text(encoding="utf-8"))
    descrizioni = scene()
    mancanti = [c["id"] for c in mazzo if c["id"] not in descrizioni]
    if mancanti:
        raise SystemExit(f"scene mancanti per: {', '.join(mancanti)}")

    carte: List[Dict[str, Any]] = []
    for c in mazzo:
        alto, basso, nome = _testi(c)
        prompt = "\n\n".join([
            STILE,
            _identita(c),
            "SCENE (what is painted inside the frame): " + descrizioni[c["id"]].strip(),
            TESTO.format(alto=alto, basso=basso),
        ])
        carte.append({
            "id": c["id"],
            "file": f"{c['id']}.webp",
            "name": nome,
            "top_text": alto,
            "bottom_text": basso,
            "font": "Cinzel",
            "width": LARGHEZZA,
            "height": ALTEZZA,
            "prompt": prompt,
            "negative_prompt": NEGATIVO,
        })
    return {
        "deck": "T-AI-rots — Thoth-inspired tarot",
        "count": len(carte),
        "note": (
            "Each prompt is self-contained: style, card identity, scene and text rules are repeated in full. "
            "Save each image in frontend/public/cards/ with the name in 'file', then set NEXT_PUBLIC_CARD_EXT=webp."
        ),
        "cards": carte,
    }


def main() -> int:
    parser = argparse.ArgumentParser(prog="tarot_core.tools.prompt_immagini")
    parser.add_argument("--uscita", type=pathlib.Path, default=USCITA)
    args = parser.parse_args()
    dati = costruisci()
    args.uscita.parent.mkdir(parents=True, exist_ok=True)
    args.uscita.write_text(json.dumps(dati, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{dati['count']} prompt scritti in {args.uscita}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
