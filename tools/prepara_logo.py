"""Prepara il logo di TAROTS chat per il sito: ripulisce i bordi, lo ridimensiona e scrive favicon, icone e anteprima.

I due loghi arrivano da `Grafica/`:

    Grafica/Logo_02_transp.png                          il logo del sito (la maga con la carta), sfondo trasparente
    Grafica/Logo_06.png                                 la seconda versione, per `prova.html`. Ha la «scacchiera
                                                        della trasparenza» disegnata nei pixel: si toglie (`togli_scacchiera`)

    python tools/prepara_logo.py --fonts <cartella con CormorantItalic.ttf e Cinzel.ttf>

**Perché i bordi si ripuliscono.** Il logo è stato ritagliato dallo sfondo con un metodo che ha lasciato, sui pixel
semitrasparenti, il colore dello sfondo (un rosso): su un fondo scuro fa un'aureola rossa attorno agli
scintillii. Qui il colore di quei pixel viene sostituito con quello dei pieni vicini, senza toccare la
trasparenza: l'aureola sparisce e i bagliori restano.

Uscite (tutte in WebP, tranne le icone e l'anteprima, che vogliono il PNG):

    frontend/public/marchio/logo-{128..1347}.webp        il logo, in più larghezze (per `srcset`)
    frontend/public/marchio/logo-b-{...}.webp            la seconda versione
    frontend/public/og/tarots-chat.png                   1200 × 630, anteprima per social e motori di ricerca
    frontend/app/favicon.ico, icon.png, apple-icon.png   le icone del browser e di iOS
    admin/app/favicon.ico, icon.png                      le stesse, per la console
    admin/public/marchio/logo-{128,256}.webp             il logo nella console
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage

RADICE = Path(__file__).resolve().parent.parent
GRAFICA = RADICE / "Grafica"
LOGO = GRAFICA / "Logo_02_transp.png"
LOGO_B = GRAFICA / "Logo_06.png"

#: Da qui in su un pixel si considera pieno: il suo colore è quello vero del logo.
SOLIDO = 235
LARGHEZZE = (128, 192, 256, 384, 512, 768, 1024, 1347)
NOTTE = (11, 8, 24)


def pulisci_bordi(img: Image.Image, anelli: int = 8) -> Image.Image:
    """Ricolora i pixel non pieni con il colore dei pieni vicini (un anello alla volta) e lascia intatta la trasparenza."""
    x = np.asarray(img.convert("RGBA")).astype(np.float32)
    rgb, alfa = x[..., :3], x[..., 3]
    piena = alfa >= SOLIDO
    colore = np.where(piena[..., None], rgb, 0.0)
    peso = piena.astype(np.float32)
    for _ in range(anelli):
        somma = np.zeros_like(colore)
        n = np.zeros_like(peso)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy == 0 and dx == 0:
                    continue
                somma += np.roll(np.roll(colore * peso[..., None], dy, 0), dx, 1)
                n += np.roll(np.roll(peso, dy, 0), dx, 1)
        nuovi = (peso == 0) & (n > 0)
        colore[nuovi] = somma[nuovi] / n[nuovi, None]
        peso[nuovi] = 1.0
    ricolorata = np.where((peso > 0)[..., None] & ~piena[..., None], colore, rgb)
    fuori = np.dstack([ricolorata, alfa]).clip(0, 255).astype(np.uint8)
    return Image.fromarray(fuori, "RGBA")


def togli_scacchiera(img: Image.Image) -> Image.Image:
    """Un'immagine con la scacchiera grigia della «trasparenza» disegnata nei pixel → un'immagine davvero trasparente.

    La scacchiera è fatta di due grigi neutri (uno chiaro, uno scuro). Si tolgono i pixel neutri e grigi che
    toccano il bordo, più le eventuali tasche chiuse dall'illustrazione, purché siano davvero a scacchi (quasi tutti
    i pixel su uno dei due grigi): i riflessi d'argento sono sfumature e non si toccano. Il contorno si restringe di
    un pixel e si ammorbidisce, perché non resti un filo grigio.
    """
    x = np.asarray(img.convert("RGB")).astype(np.int16)
    r, g, b = x[..., 0], x[..., 1], x[..., 2]
    neutro = (abs(r - g) <= 7) & (abs(g - b) <= 7) & (abs(r - b) <= 7) & (r >= 110) & (r <= 215)
    etichette, n = ndimage.label(neutro)
    fondo = np.zeros_like(neutro)
    bordo = set(np.unique(np.concatenate([etichette[0], etichette[-1], etichette[:, 0], etichette[:, -1]]))) - {0}
    chiaro, scuro = (abs(r - 196) <= 9), (abs(r - 136) <= 9)
    for i in range(1, n + 1):
        area = int((etichette == i).sum()) if i not in bordo else 1 << 30
        if i in bordo:
            fondo |= etichette == i
        elif area >= 300:
            comp = etichette == i
            if ((chiaro | scuro) & comp).sum() >= 0.9 * area:
                fondo |= comp
    fondo = ndimage.binary_dilation(fondo, iterations=1)
    alfa = np.where(fondo, 0, 255).astype(np.uint8)
    alfa = ndimage.binary_erosion(alfa > 0, iterations=1)
    morbida = Image.fromarray((alfa * 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(0.8))
    fuori = img.convert("RGBA")
    fuori.putalpha(morbida)
    return fuori


def ritaglia(img: Image.Image, margine: float = 0.02, soglia: int = 6) -> Image.Image:
    """Toglie il margine trasparente e ne lascia un filo (`margine` della dimensione maggiore)."""
    alfa = np.asarray(img.getchannel("A"))
    righe, colonne = np.where(alfa > soglia)
    if not len(righe):
        return img
    x0, x1, y0, y1 = colonne.min(), colonne.max() + 1, righe.min(), righe.max() + 1
    m = round(max(x1 - x0, y1 - y0) * margine)
    return img.crop((max(x0 - m, 0), max(y0 - m, 0), min(x1 + m, img.width), min(y1 + m, img.height)))


def scrivi_webp(img: Image.Image, percorso: Path, larghezza: int, qualita: int = 88) -> int:
    percorso.parent.mkdir(parents=True, exist_ok=True)
    altezza = round(img.height * larghezza / img.width)
    ridotta = img.resize((larghezza, altezza), Image.LANCZOS)
    ridotta.save(percorso, "WEBP", quality=qualita, method=6, alpha_quality=95)
    return percorso.stat().st_size


def quadrato(img: Image.Image, lato: int, riempimento: float = 0.94, sfondo: tuple | None = None) -> Image.Image:
    """Il logo dentro un quadrato: `riempimento` è la parte occupata; senza `sfondo` il quadrato è trasparente."""
    tela = Image.new("RGBA", (lato, lato), (*sfondo, 255) if sfondo else (0, 0, 0, 0))
    scala = lato * riempimento / max(img.width, img.height)
    ridotto = img.resize((round(img.width * scala), round(img.height * scala)), Image.LANCZOS)
    tela.alpha_composite(ridotto, ((lato - ridotto.width) // 2, (lato - ridotto.height) // 2))
    return tela


def icone(logo: Image.Image, cartella_app: Path, apple: bool) -> list[str]:
    scritti = []
    cartella_app.mkdir(parents=True, exist_ok=True)
    grandi = quadrato(logo, 512)
    grandi.save(cartella_app / "icon.png", optimize=True)
    scritti.append(str(cartella_app / "icon.png"))
    ico = [quadrato(logo, s, 0.98) for s in (16, 32, 48)]
    ico[-1].save(cartella_app / "favicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48)], append_images=ico[:-1])
    scritti.append(str(cartella_app / "favicon.ico"))
    if apple:
        # iOS riempie di nero i trasparenti: un fondo notte, con il logo un filo più piccolo.
        quadrato(logo, 180, 0.86, sfondo=NOTTE).convert("RGB").save(cartella_app / "apple-icon.png", optimize=True)
        scritti.append(str(cartella_app / "apple-icon.png"))
    return scritti


def anteprima(logo: Image.Image, percorso: Path, cormorant: Path, cinzel: Path) -> None:
    """1200 × 630: il logo a sinistra su un fondo notte con un alone, il motto e l'indirizzo a destra."""
    W, H = 1200, 630
    fondo = Image.new("RGB", (W, H), NOTTE)
    px = np.zeros((H, W, 3), np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    alone = np.exp(-(((xx - 330) / 380.0) ** 2 + ((yy - 315) / 330.0) ** 2))
    for i, (a, b) in enumerate(zip((20, 12, 45), NOTTE)):
        px[..., i] = b + (a - b) * alone
    fondo = Image.fromarray(px.clip(0, 255).astype(np.uint8), "RGB").convert("RGBA")
    altezza = 560
    segno = logo.resize((round(logo.width * altezza / logo.height), altezza), Image.LANCZOS)
    fondo.alpha_composite(segno, (60, (H - altezza) // 2))
    d = ImageDraw.Draw(fondo)
    motto = ImageFont.truetype(str(cormorant), 54)
    motto.set_variation_by_axes([500])
    piccolo = ImageFont.truetype(str(cinzel), 24)
    piccolo.set_variation_by_axes([600])
    x = 750
    for i, riga in enumerate(("Thoth tarot", "readings,", "guided by AI.")):
        d.text((x, 188 + i * 70), riga, font=motto, fill=(239, 230, 210))
    d.line((x, 432, x + 300, 432), fill=(216, 180, 90, 140), width=2)
    xx0 = x
    for c in "TAROTS.CHAT":
        d.text((xx0, 456), c, font=piccolo, fill=(185, 164, 255))
        xx0 += piccolo.getlength(c) + 6
    percorso.parent.mkdir(parents=True, exist_ok=True)
    fondo.convert("RGB").save(percorso, "PNG", optimize=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fonts", type=Path, required=True)
    args = ap.parse_args()

    logo = ritaglia(pulisci_bordi(Image.open(LOGO)))
    logo_b = ritaglia(pulisci_bordi(togli_scacchiera(Image.open(LOGO_B))), margine=0.01)
    print(f"logo: {logo.size}, logo B: {logo_b.size}")

    pubblico = RADICE / "frontend/public/marchio"
    for larghezza in LARGHEZZE:
        peso = scrivi_webp(logo, pubblico / f"logo-{larghezza}.webp", min(larghezza, logo.width))
        print(f"  logo-{larghezza}.webp  {peso // 1024} KB")
    for larghezza in (256, 512, 768, 1024, 1536):
        peso = scrivi_webp(logo_b, pubblico / f"logo-b-{larghezza}.webp", min(larghezza, logo_b.width))
        print(f"  logo-b-{larghezza}.webp  {peso // 1024} KB")
    for larghezza in (128, 256):
        scrivi_webp(logo, RADICE / f"admin/public/marchio/logo-{larghezza}.webp", larghezza)

    anteprima(logo, RADICE / "frontend/public/og/tarots-chat.png", args.fonts / "CormorantItalic.ttf", args.fonts / "Cinzel.ttf")
    scritti = icone(logo, RADICE / "frontend/app", apple=True) + icone(logo, RADICE / "admin/app", apple=False)
    print("Icone:\n  " + "\n  ".join(scritti))


if __name__ == "__main__":
    main()
