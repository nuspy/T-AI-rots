"""L'icona dell'app (proposta C, scelta dall'operatore il 6/10/2026): due carte a ventaglio con la stella del marchio,
ottone su prugna, i colori del sito (`Token.plum`, `plumDeep`, `brass`, `brassPale`).

Disegnata qui in vettoriale (Pillow, a 2048 px e poi ridotta, così i bordi sono morbidi) e salvata in
`assets/icona/`; poi `dart run flutter_launcher_icons` ne fa tutte le misure di Android e iOS (configurazione in
`pubspec.yaml`):

  - `icona.png`       1024, piena e senza trasparenza: iOS (che arrotonda da sé) e Android prima della 8;
  - `primo_piano.png` 1024, trasparente: le carte dell'icona adattiva di Android, dentro la zona sicura (66%);
  - `sfondo.png`      1024: il fondo dell'icona adattiva (l'alone prugna);
  - `monocromo.png`   1024: la sagoma per le icone a tema di Android 13 (conta solo l'alfa);
  - `play_512.png`    512: l'icona da caricare a mano nella scheda di Google Play.

    python tool/icona.py        (dalla cartella mobile)
"""
import math
import pathlib

from PIL import Image, ImageDraw

QUI = pathlib.Path(__file__).resolve().parent.parent / "assets" / "icona"
G = 2048  # lato di lavoro (poi ridotto a 1024)
PRUGNA = (60, 24, 70)
PRUGNA_SCURA = (32, 16, 38)
OTTONE = (178, 131, 54)
OTTONE_CHIARO = (214, 182, 109)


def sfondo() -> Image.Image:
    """L'alone: prugna al centro, prugna scura ai bordi."""
    im = Image.new("RGB", (G, G), PRUGNA_SCURA)
    d = ImageDraw.Draw(im)
    raggio = int(G * 0.72)
    for r in range(raggio, 0, -4):
        t = r / raggio
        c = tuple(int(PRUGNA[i] * (1 - t) + PRUGNA_SCURA[i] * t) for i in range(3))
        d.ellipse([G / 2 - r, G / 2 - r, G / 2 + r, G / 2 + r], fill=c)
    return im


def stella(d: ImageDraw.ImageDraw, cx: float, cy: float, r: float, colore, interno: float = 0.22) -> None:
    """La stella a quattro punte del marchio («✦»)."""
    punti = []
    for k in range(8):
        ang = math.pi / 2 + k * math.pi / 4
        rr = r if k % 2 == 0 else r * interno
        punti.append((cx + rr * math.cos(ang), cy - rr * math.sin(ang)))
    d.polygon(punti, fill=colore)


def carta(w: float, h: float, stella_r: float, colore_stella) -> Image.Image:
    """Una carta: fondo prugna, bordo d'ottone chiaro, cornice interna, la stella al centro."""
    c = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    r = w * 0.09
    d.rounded_rectangle([0, 0, w - 1, h - 1], r, fill=PRUGNA + (255,), outline=OTTONE_CHIARO, width=int(w * 0.06))
    m = w * 0.12
    d.rounded_rectangle([m, m, w - m - 1, h - m - 1], r * 0.5, outline=OTTONE + (255,), width=max(2, int(w * 0.02)))
    stella(d, w / 2, h / 2, w * stella_r, colore_stella + (255,))
    return c


def carte(scala: float) -> Image.Image:
    """Le due carte a ventaglio su trasparente; [scala] è la loro misura rispetto al lato."""
    im = Image.new("RGBA", (G, G), (0, 0, 0, 0))
    w, h = G * 0.40 * scala, G * 0.64 * scala
    for ang, dx, r, colore in [(14, G * 0.10 * scala, 0.20, OTTONE), (-8, -G * 0.06 * scala, 0.30, OTTONE_CHIARO)]:
        c = carta(w, h, r, colore).rotate(ang, expand=True, resample=Image.BICUBIC)
        im.alpha_composite(c, (int(G / 2 - c.width / 2 + dx), int(G / 2 - c.height / 2)))
    return im


def riduci(im: Image.Image, lato: int = 1024) -> Image.Image:
    return im.resize((lato, lato), Image.LANCZOS)


def monocromo(primo: Image.Image) -> Image.Image:
    """La sagoma: l'ottone resta (bianco), il prugna delle carte diventa trasparente."""
    rgba = primo.convert("RGBA")
    fuori = Image.new("RGBA", rgba.size, (255, 255, 255, 0))
    px, po = rgba.load(), fuori.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, a = px[x, y]
            luce = 0.299 * r + 0.587 * g + 0.114 * b
            alfa = max(0.0, min(1.0, (luce - 70) / 60)) * a
            po[x, y] = (255, 255, 255, int(alfa))
    return fuori


def main() -> None:
    QUI.mkdir(parents=True, exist_ok=True)
    fondo = sfondo()
    piena = fondo.convert("RGBA")
    piena.alpha_composite(carte(1.0))
    icona = riduci(piena.convert("RGB"))
    icona.save(QUI / "icona.png")
    icona.resize((512, 512), Image.LANCZOS).save(QUI / "play_512.png")
    riduci(fondo).save(QUI / "sfondo.png")
    # L'icona adattiva: flutter_launcher_icons mette già un margine del 16% per lato (zona sicura); qui le carte stanno
    # in un cerchio dell'86% dell'immagine, perché la maschera del telefono può essere un cerchio.
    primo = riduci(carte(0.95))
    primo.save(QUI / "primo_piano.png")
    monocromo(primo).save(QUI / "monocromo.png")
    print(f"ok: {QUI}")


if __name__ == "__main__":
    main()
