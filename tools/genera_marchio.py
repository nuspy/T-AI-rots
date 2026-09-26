"""Scrive le immagini del marchio di TAROTS chat: favicon, icona per iOS, immagine di anteprima (Open Graph).

Il segno è una carta dei tarocchi con la coda di un fumetto e, dentro, la stella a sette punte di Babalon.
La geometria è **la stessa** di `frontend/lib/marchio.ts` (il componente e il canvas dell'immagine di condivisione
la leggono da lì): qui si ricopiano i numeri, perché uno script Python non può importare TypeScript. Se cambia
uno, cambia l'altro.

    python tools/genera_marchio.py --fonts <cartella con Cinzel.ttf e CormorantItalic.ttf>

I caratteri sono Cinzel e Cormorant Garamond (licenza OFL, come nel sito). Serve Pillow. Le immagini escono in:

    frontend/app/icon.svg              favicon (Next lo serve da solo)
    frontend/app/apple-icon.png        180 × 180, icona per iOS
    admin/app/icon.svg                 favicon della console
    frontend/public/marchio/emblema.svg    il segno, trasparente, per chi lo vuole altrove
    frontend/public/og/tarots-chat.png     1200 × 630, anteprima per social e motori di ricerca
"""
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

RADICE = Path(__file__).resolve().parent.parent

# ---- la geometria (copia di frontend/lib/marchio.ts) ----------------------------------------------------------
LARGHEZZA, ALTEZZA = 68, 105
CONTORNO = "M13 4H55A7 7 0 0 1 62 11V85A7 7 0 0 1 55 92H46V101L36 92H13A7 7 0 0 1 6 85V11A7 7 0 0 1 13 4Z"
CORNICE = (11.5, 9.5, 45, 77, 3.5)  # x, y, larghezza, altezza, raggio
CENTRO = (34.0, 48.0)
RAGGIO = 20.0
ROMBI = ("M34 13.2l1.7 2.3-1.7 2.3-1.7-2.3z", "M34 78.2l1.7 2.3-1.7 2.3-1.7-2.3z")
ORO_CHIARO, ORO, ORO_SCURO = (246, 228, 168), (216, 180, 90), (143, 108, 36)
NOTTE_ALTA, NOTTE, VIOLA = (36, 26, 72), (11, 8, 24), (185, 164, 255)
TESTO = (239, 230, 210)


def punte() -> list[tuple[float, float]]:
    return [
        (round(CENTRO[0] + RAGGIO * math.cos(-math.pi / 2 + k * 2 * math.pi / 7), 2),
         round(CENTRO[1] + RAGGIO * math.sin(-math.pi / 2 + k * 2 * math.pi / 7), 2))
        for k in range(7)
    ]


def percorso_stella() -> str:
    p = punte()
    ordine = [0, 2, 4, 6, 1, 3, 5]
    return "".join(f"{'M' if i == 0 else 'L'}{p[k][0]} {p[k][1]}" for i, k in enumerate(ordine)) + "Z"


def arco(cx: float, cy: float, r: float, da: float, a: float, n: int = 14) -> list[tuple[float, float]]:
    return [
        (cx + r * math.cos(math.radians(da + (a - da) * i / n)), cy + r * math.sin(math.radians(da + (a - da) * i / n)))
        for i in range(n + 1)
    ]


def contorno_punti() -> list[tuple[float, float]]:
    """Lo stesso percorso di CONTORNO, campionato: gli angoli tondi diventano archi."""
    pts: list[tuple[float, float]] = [(13, 4), (55, 4)]
    pts += arco(55, 11, 7, -90, 0)[1:]
    pts += [(62, 85)]
    pts += arco(55, 85, 7, 0, 90)[1:]
    pts += [(46, 92), (46, 101), (36, 92), (13, 92)]
    pts += arco(13, 85, 7, 90, 180)[1:]
    pts += [(6, 11)]
    pts += arco(13, 11, 7, 180, 270)[1:]
    return pts


# ---- disegno a raster --------------------------------------------------------------------------------------------


def gradiente(dim: tuple[int, int], colori: list[tuple[float, tuple[int, int, int]]], diagonale: bool = True) -> Image.Image:
    """Un gradiente lineare (in diagonale o dall'alto in basso) fra i colori dati."""
    w, h = dim
    img = Image.new("RGB", dim)
    px = img.load()
    for y in range(h):
        for x in range(w):
            t = (x / max(w - 1, 1) + y / max(h - 1, 1)) / 2 if diagonale else y / max(h - 1, 1)
            for (t0, c0), (t1, c1) in zip(colori, colori[1:]):
                if t0 <= t <= t1:
                    f = (t - t0) / (t1 - t0) if t1 > t0 else 0
                    px[x, y] = tuple(round(c0[i] + (c1[i] - c0[i]) * f) for i in range(3))
                    break
    return img


def emblema(altezza: int, semplice: bool = False, sfondo: bool = True) -> Image.Image:
    """Il segno come immagine RGBA alta `altezza` px (con 4× di supercampionamento)."""
    s = 4
    k = altezza * s / ALTEZZA
    W, H = round(LARGHEZZA * k), round(ALTEZZA * k)

    def sc(p: tuple[float, float]) -> tuple[float, float]:
        return (p[0] * k, p[1] * k)

    carta = [sc(p) for p in contorno_punti()]
    maschera_carta = Image.new("L", (W, H), 0)
    ImageDraw.Draw(maschera_carta).polygon(carta, fill=255)

    fuori = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if sfondo:
        notte = gradiente((W, H), [(0, NOTTE_ALTA), (1, NOTTE)], diagonale=False)
        fuori.paste(notte, (0, 0), maschera_carta)
        # L'alone viola dietro la stella.
        alone = Image.new("L", (W, H), 0)
        cx, cy = sc(CENTRO)
        ImageDraw.Draw(alone).ellipse((cx - 30 * k, cy - 30 * k, cx + 30 * k, cy + 30 * k), fill=110)
        alone = alone.filter(ImageFilter.GaussianBlur(9 * k))
        viola = Image.new("RGBA", (W, H), VIOLA + (0,))
        viola.putalpha(Image.composite(alone, Image.new("L", (W, H), 0), maschera_carta))
        fuori = Image.alpha_composite(fuori, viola)

    tratti = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(tratti)
    spessore = (3.2 if semplice else 1.9) * k
    d.line(carta + [carta[0]], fill=255, width=round(spessore), joint="curve")
    for p in carta:  # angoli tondi anche nelle giunture
        d.ellipse((p[0] - spessore / 2, p[1] - spessore / 2, p[0] + spessore / 2, p[1] + spessore / 2), fill=255)
    stella = [sc(p) for p in punte()]
    ordine = [0, 2, 4, 6, 1, 3, 5, 0]
    larg_stella = (2.6 if semplice else 1.5) * k
    seg = [stella[i] for i in ordine]
    d.line(seg, fill=255, width=round(larg_stella), joint="curve")
    for p in seg:
        d.ellipse((p[0] - larg_stella / 2, p[1] - larg_stella / 2, p[0] + larg_stella / 2, p[1] + larg_stella / 2), fill=255)
    r = (2.6 if semplice else 2.1) * k
    cx, cy = sc(CENTRO)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    if not semplice:
        for cy0 in (15.5, 80.5):  # i due rombi, sopra e sotto la stella
            rombo = [(34.0, cy0 - 2.3), (35.7, cy0), (34.0, cy0 + 2.3), (32.3, cy0)]
            d.polygon([sc(pt) for pt in rombo], fill=255)
        x, y, w, h, rr = CORNICE
        cornice = Image.new("L", (W, H), 0)
        ImageDraw.Draw(cornice).rounded_rectangle(
            (x * k, y * k, (x + w) * k, (y + h) * k), radius=rr * k, outline=128, width=max(1, round(0.6 * k)),
        )
        tratti = ImageChops.lighter(tratti, cornice)
    oro = gradiente((W, H), [(0, ORO_CHIARO), (0.5, ORO), (1, ORO_SCURO)])
    fuori.paste(oro, (0, 0), tratti)
    return fuori.resize((round(W / s), round(H / s)), Image.LANCZOS)


def testo_spaziato(d: ImageDraw.ImageDraw, xy: tuple[float, float], testo: str, font: ImageFont.FreeTypeFont,
                   spazio: float, fill) -> float:
    """Lettera per lettera, con la spaziatura tra le lettere; ritorna la larghezza."""
    x, y = xy
    for c in testo:
        d.text((x, y), c, font=font, fill=fill)
        x += font.getlength(c) + spazio
    return x - xy[0] - spazio


def oro_su_testo(img: Image.Image, xy: tuple[int, int], testo: str, font: ImageFont.FreeTypeFont, spazio: float) -> float:
    """TAROTS in oro: il testo fa da maschera a un gradiente."""
    w = int(sum(font.getlength(c) + spazio for c in testo)) + 8
    h = int(font.size * 1.5)
    maschera = Image.new("L", (w, h), 0)
    larg = testo_spaziato(ImageDraw.Draw(maschera), (0, 0), testo, font, spazio, 255)
    oro = gradiente((w, h), [(0, ORO_CHIARO), (0.55, ORO), (1, (199, 154, 60))])
    img.paste(oro, xy, maschera)
    return larg


def stelle_di_fondo(img: Image.Image, seme: int = 7) -> None:
    rnd = random.Random(seme)
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(140):
        x, y = rnd.randint(0, img.width), rnd.randint(0, img.height)
        r = rnd.choice((1, 1, 1, 2))
        colore = rnd.choice(((ORO_CHIARO), VIOLA))
        d.ellipse((x - r, y - r, x + r, y + r), fill=colore + (rnd.randint(40, 130),))


def anteprima(percorso: Path, cinzel: Path, cormorant: Path) -> None:
    W, H = 1200, 630
    fondo = gradiente((W, H), [(0, (21, 14, 46)), (0.5, (10, 7, 22)), (1, (7, 5, 15))])
    img = fondo.convert("RGBA")
    # Una grande stella sbiadita a destra: il segno che si ripete come filigrana.
    filigrana = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(filigrana)
    cx, cy, R = 985, 300, 300
    p = [(cx + R * math.cos(-math.pi / 2 + k * 2 * math.pi / 7), cy + R * math.sin(-math.pi / 2 + k * 2 * math.pi / 7)) for k in range(7)]
    fd.line([p[i] for i in [0, 2, 4, 6, 1, 3, 5, 0]], fill=ORO + (26,), width=3, joint="curve")
    fd.ellipse((cx - R * 1.08, cy - R * 1.08, cx + R * 1.08, cy + R * 1.08), outline=ORO + (22,), width=2)
    img = Image.alpha_composite(img, filigrana)
    stelle_di_fondo(img)

    segno = emblema(300)
    bagliore = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(bagliore).ellipse((60, 130, 330, 470), fill=ORO + (48,))
    img = Image.alpha_composite(img, bagliore.filter(ImageFilter.GaussianBlur(60)))
    img.alpha_composite(segno, (110, 165))

    d = ImageDraw.Draw(img)
    f_titolo = ImageFont.truetype(str(cinzel), 122)
    f_titolo.set_variation_by_axes([700])
    f_voce = ImageFont.truetype(str(cormorant), 92)
    f_voce.set_variation_by_axes([500])
    f_motto = ImageFont.truetype(str(cormorant), 44)
    f_motto.set_variation_by_axes([500])
    f_dominio = ImageFont.truetype(str(cinzel), 22)
    f_dominio.set_variation_by_axes([600])

    x0 = 400
    larghezza = oro_su_testo(img, (x0, 196), "TAROTS", f_titolo, 12)
    d.text((x0 + 4, 326), "chat", font=f_voce, fill=VIOLA)
    d.line((x0 + 4, 452, x0 + 4 + min(int(larghezza), 420), 452), fill=ORO + (110,), width=2)
    d.text((x0 + 4, 470), "Thoth tarot readings, guided by AI.", font=f_motto, fill=TESTO)
    testo_spaziato(d, (x0 + 4, 540), "TAROTS.CHAT", f_dominio, 6, VIOLA + (230,))

    percorso.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(percorso, "PNG", optimize=True)


def icona_apple(percorso: Path) -> None:
    lato = 180
    fondo = gradiente((lato, lato), [(0, (30, 21, 62)), (1, (9, 6, 20))]).convert("RGBA")
    segno = emblema(128)
    fondo.alpha_composite(segno, ((lato - segno.width) // 2, (lato - segno.height) // 2))
    percorso.parent.mkdir(parents=True, exist_ok=True)
    fondo.convert("RGB").save(percorso, "PNG", optimize=True)


# ---- SVG ---------------------------------------------------------------------------------------------------------


def svg_emblema(semplice: bool, contenitore: bool = False) -> str:
    """Il segno come SVG. `contenitore`: dentro un quadrato scuro con gli angoli tondi (favicon)."""
    hx = lambda c: "#%02x%02x%02x" % c
    corpo = f"""<defs>
    <linearGradient id="o" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{hx(ORO_CHIARO)}"/><stop offset=".5" stop-color="{hx(ORO)}"/><stop offset="1" stop-color="{hx(ORO_SCURO)}"/></linearGradient>
    <linearGradient id="n" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{hx(NOTTE_ALTA)}"/><stop offset="1" stop-color="{hx(NOTTE)}"/></linearGradient>
  </defs>
  <path d="{CONTORNO}" fill="url(#n)" stroke="url(#o)" stroke-width="{3.2 if semplice else 1.9}" stroke-linejoin="round"/>"""
    if not semplice:
        x, y, w, h, r = CORNICE
        corpo += f"""
  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="none" stroke="url(#o)" stroke-width=".6" opacity=".5"/>
  <path d="{ROMBI[0]}" fill="url(#o)"/><path d="{ROMBI[1]}" fill="url(#o)"/>"""
    corpo += f"""
  <path d="{percorso_stella()}" fill="none" stroke="url(#o)" stroke-width="{2.6 if semplice else 1.5}" stroke-linejoin="round"/>
  <circle cx="{CENTRO[0]}" cy="{CENTRO[1]}" r="{2.6 if semplice else 2.1}" fill="url(#o)"/>"""
    if not contenitore:
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {LARGHEZZA} {ALTEZZA}" width="{LARGHEZZA}" height="{ALTEZZA}">\n  {corpo}\n</svg>\n'
    # Il favicon: un quadrato 96 × 96 scuro, il segno alto 82 al centro.
    k = 82 / ALTEZZA
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96" width="96" height="96">\n'
        f'  <rect width="96" height="96" rx="20" fill="{hx((14, 10, 31))}"/>\n'
        f'  <g transform="translate({(96 - LARGHEZZA * k) / 2:.2f} {(96 - 82) / 2:.2f}) scale({k:.4f})">\n  {corpo}\n  </g>\n</svg>\n'
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fonts", type=Path, required=True, help="cartella con Cinzel.ttf e CormorantItalic.ttf")
    args = ap.parse_args()

    scritti = []

    def scrivi(rel: str, contenuto: str) -> None:
        p = RADICE / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(contenuto, encoding="utf-8")
        scritti.append(rel)

    scrivi("frontend/public/marchio/emblema.svg", svg_emblema(semplice=False))
    scrivi("frontend/app/icon.svg", svg_emblema(semplice=True, contenitore=True))
    scrivi("admin/app/icon.svg", svg_emblema(semplice=True, contenitore=True))

    icona_apple(RADICE / "frontend/app/apple-icon.png")
    scritti.append("frontend/app/apple-icon.png")
    anteprima(RADICE / "frontend/public/og/tarots-chat.png", args.fonts / "Cinzel.ttf", args.fonts / "CormorantItalic.ttf")
    scritti.append("frontend/public/og/tarots-chat.png")
    print("Scritti:\n  " + "\n  ".join(scritti))


if __name__ == "__main__":
    main()
