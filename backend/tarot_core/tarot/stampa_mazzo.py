"""Il PDF "Stampa i tuoi Tarocchi": impaginazione pronta per la stampa fisica (v5, Fase B4).

**Le pagine si alternano fronte/dorso/fronte/dorso**, mai tutti i fronti e poi tutti i dorsi: è così
che una stampante con fronte/retro automatico abbina la pagina N (fronte) alla pagina N+1 (retro).
Sulla pagina dei dorsi le colonne sono specchiate rispetto a quella dei fronti corrispondente — la
stampa duplex ribalta il foglio sul bordo lungo, e senza lo specchio ogni dorso cadrebbe sopra il
fronte della carta vicina, non della propria.

**Il marchio "tarots.chat"**, un piccolo timbro nel margine di ogni carta (fronte e dorso), compare
solo quando `gratuito` è vero — cioè solo per il PDF che si scarica senza pagare
(`Deck.prezzo_stampa == 0`). Un mazzo comprato non lo porta: è il chiamante (l'endpoint) a sapere
quale dei due download è in corso, questo modulo non guarda mai un prezzo.

**Le immagini**: il backend non ha, in produzione, accesso al filesystem del frontend (sono due
immagini Docker distinte) — si leggono da disco solo quando il percorso esiste davvero (sviluppo, e
i test di questo repository), altrimenti si scaricano dal sito pubblico (`TAROT_WEB_PUBLIC_URL`),
una volta sola per carta, con una cache in memoria per la durata della generazione.
"""
from __future__ import annotations

import io
import logging
from typing import Dict, List, Optional

import httpx
from PIL import Image as PILImage
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from ..paths import PROJECT_ROOT

logger = logging.getLogger(__name__)

#: L'estensione delle immagini delle carte — la stessa convenzione del frontend (`NEXT_PUBLIC_CARD_EXT`).
ESTENSIONE = "webp"

#: Dimensione di una carta da tarocchi (più alta del poker): 70×120 mm, con 2 mm di margine di
#: taglio già previsti nel disegno stesso dell'immagine sorgente.
LARGHEZZA_CARTA = 70 * mm
ALTEZZA_CARTA = 120 * mm

MARGINE_PAGINA = 10 * mm
SPAZIO_TAGLIO = 4 * mm  # fra una carta e l'altra, per le forbici

_LARGHEZZA_PAGINA, _ALTEZZA_PAGINA = A4


def _griglia() -> tuple[int, int]:
    """Colonne e righe di carte che stanno su una pagina A4, con margine e spazio di taglio scelti."""
    colonne = int((_LARGHEZZA_PAGINA - 2 * MARGINE_PAGINA + SPAZIO_TAGLIO) // (LARGHEZZA_CARTA + SPAZIO_TAGLIO))
    righe = int((_ALTEZZA_PAGINA - 2 * MARGINE_PAGINA + SPAZIO_TAGLIO) // (ALTEZZA_CARTA + SPAZIO_TAGLIO))
    return max(colonne, 1), max(righe, 1)


def _posizione(colonna: int, riga: int, colonne: int, righe: int) -> tuple[float, float]:
    """L'angolo in basso a sinistra della carta a (riga, colonna) nella griglia, centrata in pagina."""
    larghezza_griglia = colonne * LARGHEZZA_CARTA + (colonne - 1) * SPAZIO_TAGLIO
    altezza_griglia = righe * ALTEZZA_CARTA + (righe - 1) * SPAZIO_TAGLIO
    origine_x = (_LARGHEZZA_PAGINA - larghezza_griglia) / 2
    origine_y = (_ALTEZZA_PAGINA - altezza_griglia) / 2
    x = origine_x + colonna * (LARGHEZZA_CARTA + SPAZIO_TAGLIO)
    y = origine_y + (righe - 1 - riga) * (ALTEZZA_CARTA + SPAZIO_TAGLIO)  # riga 0 = in alto
    return x, y


def _percorso_locale(slug_mazzo: str, nome_file: str) -> Optional[str]:
    """Il file su disco, se questa macchina ha anche il frontend accanto (sviluppo, test):
    prima nella cartella propria del mazzo, poi in quella piatta di oggi (il Thoth predefinito)."""
    base = PROJECT_ROOT.parent / "frontend" / "public" / "cards"
    per_mazzo = base / slug_mazzo / nome_file
    if per_mazzo.exists():
        return str(per_mazzo)
    piatto = base / nome_file
    return str(piatto) if piatto.exists() else None


async def carica_immagini(
    slug_mazzo: str, nomi_file: List[str], *, web_public_url: str, client: Optional[httpx.AsyncClient] = None,
    precaricate: Optional[Dict[str, bytes]] = None,
) -> Dict[str, bytes]:
    """I byte di ogni file in `nomi_file` (carte + dorso): prima fra le `precaricate` (le immagini di un mazzo
    caricato dalla console, lette dal database dal chiamante), poi da disco se c'è, altrimenti dal sito
    pubblico. Un file introvabile in nessuno di questi modi resta assente dal risultato — chi genera il
    PDF disegna un segnaposto al suo posto invece di far fallire l'intera stampa per una carta sola."""
    proprio_client = client is None
    client = client or httpx.AsyncClient(timeout=10.0)
    trovate: Dict[str, bytes] = {}
    try:
        for nome_file in nomi_file:
            if precaricate and nome_file in precaricate:
                trovate[nome_file] = precaricate[nome_file]
                continue
            locale = _percorso_locale(slug_mazzo, nome_file)
            if locale is not None:
                with open(locale, "rb") as f:
                    trovate[nome_file] = f.read()
                continue
            for percorso in (f"/cards/{slug_mazzo}/{nome_file}", f"/cards/{nome_file}"):
                try:
                    r = await client.get(f"{web_public_url.rstrip('/')}{percorso}")
                except httpx.HTTPError:
                    continue
                if r.status_code == 200:
                    trovate[nome_file] = r.content
                    break
            else:
                logger.warning("Immagine non trovata per il PDF del mazzo %s: %s", slug_mazzo, nome_file)
    finally:
        if proprio_client:
            await client.aclose()
    return trovate


def _per_stampa(dati: bytes) -> ImageReader:
    """WebP decodificato è un bitmap RGB come un altro: incorporarlo così nel PDF pesa quanto un
    bitmap grezzo (reportlab non preserva la compressione originale). Ricodificarlo in JPEG a qualità
    alta pesa una frazione ed è indistinguibile in stampa."""
    immagine = PILImage.open(io.BytesIO(dati)).convert("RGB")
    buffer = io.BytesIO()
    immagine.save(buffer, format="JPEG", quality=85)
    buffer.seek(0)
    return ImageReader(buffer)


def _disegna_carta(
    c: canvas.Canvas, x: float, y: float, immagine: Optional[ImageReader], *, marchio: bool,
    marchio_testo: Optional[str] = None,
) -> None:
    if immagine is not None:
        c.drawImage(
            immagine, x, y, width=LARGHEZZA_CARTA, height=ALTEZZA_CARTA,
            preserveAspectRatio=True, anchor="c", mask="auto",
        )
    else:
        c.setStrokeColorRGB(0.6, 0.6, 0.6)
        c.rect(x, y, LARGHEZZA_CARTA, ALTEZZA_CARTA, stroke=1, fill=0)
    if marchio:
        c.saveState()
        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica", 6)
        c.drawCentredString(x + LARGHEZZA_CARTA / 2, y + 2 * mm, marchio_testo or "tarots.chat")
        c.restoreState()


def genera_pdf(
    ordine_carte: List[str], immagini: Dict[str, bytes], *, gratuito: bool,
    marchio_testo: Optional[str] = None,
) -> bytes:
    """Pura rispetto all'IO: `immagini` è già in memoria (da `carica_immagini`), chiavi = nome file
    (`f"{card_id}.{ESTENSIONE}"`, più `f"dorso.{ESTENSIONE}"`).

    `marchio_testo` sostituisce la scritta "tarots.chat" quando `gratuito` è vero — usato da chi
    genera un PDF fuori dal prodotto di produzione (lo strumento di bozza di un mazzo nuovo, che vuole
    un marchio di copyright completo). Senza indicazione il comportamento di produzione non cambia."""
    colonne, righe = _griglia()
    per_pagina = colonne * righe
    # Un solo `ImageReader` per immagine, riusato su tutte le pagine che la mostrano: reportlab lo
    # incorpora una volta sola nel PDF (un form XObject condiviso) invece di ripetere il dorso — la
    # stessa immagine — su ognuna delle decine di pagine che lo portano.
    letture: Dict[str, ImageReader] = {nome: _per_stampa(dati) for nome, dati in immagini.items()}
    dorso = letture.get(f"dorso.{ESTENSIONE}")

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    for inizio in range(0, len(ordine_carte), per_pagina):
        gruppo = ordine_carte[inizio:inizio + per_pagina]

        for indice, card_id in enumerate(gruppo):
            riga, colonna = divmod(indice, colonne)
            x, y = _posizione(colonna, riga, colonne, righe)
            _disegna_carta(c, x, y, letture.get(f"{card_id}.{ESTENSIONE}"), marchio=gratuito, marchio_testo=marchio_testo)
        c.showPage()

        for indice in range(len(gruppo)):
            riga, colonna = divmod(indice, colonne)
            x, y = _posizione(colonne - 1 - colonna, riga, colonne, righe)  # colonne specchiate: v. sopra
            _disegna_carta(c, x, y, dorso, marchio=gratuito, marchio_testo=marchio_testo)
        c.showPage()

    c.save()
    return buffer.getvalue()


async def pdf_per_mazzo(
    slug_mazzo: str, ordine_carte: List[str], *, gratuito: bool, web_public_url: str,
    marchio_testo: Optional[str] = None, precaricate: Optional[Dict[str, bytes]] = None,
) -> bytes:
    """Scarica (o legge) le immagini e genera il PDF: il punto d'ingresso usato dagli endpoint. `precaricate`: le
    immagini del mazzo già in memoria (dal database, `deck_repositories.immagini_per_pdf`)."""
    nomi_file = [f"{card_id}.{ESTENSIONE}" for card_id in ordine_carte] + [f"dorso.{ESTENSIONE}"]
    immagini = await carica_immagini(slug_mazzo, nomi_file, web_public_url=web_public_url, precaricate=precaricate)
    return genera_pdf(ordine_carte, immagini, gratuito=gratuito, marchio_testo=marchio_testo)
