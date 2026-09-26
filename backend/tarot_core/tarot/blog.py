"""Il blog: regole pure, senza database né rete.

Slug, tempo di lettura, estratto, collegamenti interni e le due lavorazioni delle
immagini (di un articolo, di un avatar). Tutto ciò che può essere provato senza un
database sta qui.

**Il testo è Markdown e non si fida.** Si salva com'è; il renderer del sito non esegue HTML
(`react-markdown` senza `rehype-raw`), quindi un `<script>` scritto in un articolo resta testo.
Le scorciatoie `[[carta:maj-17]]`, `[[stesa:croce-celtica]]`, `[[articolo:un-titolo]]` sono
collegamenti interni: il sito le rende come schede, e qui le si legge per sapere di cosa parla
ogni articolo.
"""
from __future__ import annotations

import io
import math
import re
import unicodedata
from typing import Callable, Iterable, List, Optional, Set, Tuple

# ---- slug ----------------------------------------------------------------------


def slugify(testo: str, massimo: int = 80) -> str:
    """«Che cos'è la Papessa?» → «che-cos-e-la-papessa». Solo `a-z`, cifre e trattini."""
    scomposto = unicodedata.normalize("NFKD", testo or "")
    ascii_ = "".join(c for c in scomposto if not unicodedata.combining(c))
    ascii_ = ascii_.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_).strip("-")
    return slug[:massimo].strip("-")


def slug_libero(base: str, occupati: Iterable[str], massimo: int = 80) -> str:
    """Il primo slug non occupato: `base`, poi `base-2`, `base-3`…"""
    base = slugify(base, massimo - 6) or "articolo"
    occupati = set(occupati)
    if base not in occupati:
        return base
    n = 2
    while f"{base}-{n}" in occupati:
        n += 1
    return f"{base}-{n}"


def normalizza_etichetta(nome: str) -> Tuple[str, str]:
    """`(slug, nome)` di un'etichetta scritta a mano. Nome vuoto → `("", "")`."""
    nome = " ".join((nome or "").split())[:80]
    return slugify(nome), nome


# ---- testo ---------------------------------------------------------------------

_SCORCIATOIA = re.compile(r"\[\[(carta|stesa|articolo):([a-z0-9-]{1,160})\]\]")
_COLLEGAMENTO_MD = re.compile(r"\]\((?:https?://([^/)\s]+))?/(carte|stese|blog)/([a-z0-9-]+)(?:[/?#][^)\s]*)?\)")
#: Le pagine `/blog/...` che non sono articoli.
_NON_ARTICOLI = {"sezione", "tag", "cerca", "feed", "autore", "media"}
_PAROLE_AL_MINUTO = 200


def tempo_lettura(testo: str) -> int:
    """Minuti di lettura, almeno 1."""
    parole = len(re.findall(r"\w+", _senza_scorciatoie(testo)))
    return max(1, math.ceil(parole / _PAROLE_AL_MINUTO))


def _senza_scorciatoie(testo: str, nomi: Optional[Callable[[str, str], Optional[str]]] = None) -> str:
    """Toglie le scorciatoie; con `nomi(tipo, id)` le sostituisce con il nome («La Stella») invece di lasciare
    un buco («Vedi  e .») negli estratti."""
    if nomi is None:
        return _SCORCIATOIA.sub(" ", testo or "")
    return _SCORCIATOIA.sub(lambda m: nomi(m.group(1), m.group(2)) or " ", testo or "")


def testo_semplice(markdown: str, nomi: Optional[Callable[[str, str], Optional[str]]] = None) -> str:
    """Il testo senza Markdown né scorciatoie: per gli estratti e le descrizioni."""
    t = _senza_scorciatoie(markdown or "", nomi)
    t = re.sub(r"```.*?```", " ", t, flags=re.S)
    t = re.sub(r"`([^`]*)`", r"\1", t)
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", t)
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"^\s{0,3}(#{1,6}|>|[-*+]|\d+\.)\s+", "", t, flags=re.M)
    t = re.sub(r"[*_~]{1,3}", "", t)
    t = re.sub(r"<[^>]+>", " ", t)
    return " ".join(t.split())


def estratto(markdown: str, massimo: int = 200, nomi: Optional[Callable[[str, str], Optional[str]]] = None) -> str:
    """Le prime parole del testo, tagliate a fine parola, con i puntini se resta altro."""
    semplice = testo_semplice(markdown, nomi)
    if len(semplice) <= massimo:
        return semplice
    taglio = semplice[:massimo]
    fine = taglio.rfind(" ")
    return f"{taglio[: fine if fine > massimo * 0.6 else massimo].rstrip(' ,;:.-')}…"


def estrai_collegamenti(testo: str, host: Optional[str] = None) -> List[Tuple[str, str]]:
    """Le citazioni interne di un testo, senza doppioni, nell'ordine in cui compaiono.

    Scorciatoie `[[carta:id]]`, e collegamenti Markdown a `/carte/id`, `/stese/id`, `/blog/slug`:
    relativi, o assoluti verso `host` (il dominio del sito). Un collegamento a un altro sito
    non è una citazione interna.
    """
    trovati: List[Tuple[str, str]] = []
    visti: Set[Tuple[str, str]] = set()

    def aggiungi(tipo: str, riferimento: str) -> None:
        voce = (tipo, riferimento)
        if voce not in visti:
            visti.add(voce)
            trovati.append(voce)

    posizioni = [(m.start(), m.group(1), m.group(2)) for m in _SCORCIATOIA.finditer(testo or "")]
    for m in _COLLEGAMENTO_MD.finditer(testo or ""):
        dominio, parte, rif = m.group(1), m.group(2), m.group(3)
        if dominio is not None and dominio.lower() != (host or "").lower():
            continue
        if parte == "blog" and rif in _NON_ARTICOLI:
            continue
        tipo = {"carte": "carta", "stese": "stesa", "blog": "articolo"}[parte]
        posizioni.append((m.start(), tipo, rif))
    for _, tipo, rif in sorted(posizioni):
        aggiungi(tipo, rif)
    return trovati


# ---- immagini -----------------------------------------------------------------

MAX_CARICO_IMMAGINE = 8_000_000
MAX_PIXEL = 40_000_000
MIN_LATO = 64
LARGHEZZA_MAX_ARTICOLO = 1600
LATO_AVATAR = 256
FORMATI_IMMAGINE = frozenset({"PNG", "JPEG", "WEBP"})


class ImmagineNonValida(ValueError):
    """Il file non è un'immagine che si accetta: il messaggio dice perché."""


def _apri(dati: bytes):
    from PIL import Image, UnidentifiedImageError

    if not dati or len(dati) > MAX_CARICO_IMMAGINE:
        raise ImmagineNonValida("immagine vuota o troppo grande")
    try:
        immagine = Image.open(io.BytesIO(dati))
        formato, (w, h) = immagine.format, immagine.size
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as exc:
        raise ImmagineNonValida("non è un'immagine valida") from exc
    if formato not in FORMATI_IMMAGINE:
        raise ImmagineNonValida("formato non ammesso (solo PNG, JPEG o WebP)")
    if w < MIN_LATO or h < MIN_LATO:
        raise ImmagineNonValida(f"immagine troppo piccola (almeno {MIN_LATO} px per lato)")
    if w * h > MAX_PIXEL:
        raise ImmagineNonValida("immagine troppo grande")
    return immagine


def _decodifica(immagine):
    from PIL import ImageOps

    try:
        immagine.load()                        # qui si scopre un file troncato
        immagine = ImageOps.exif_transpose(immagine)
    except (OSError, ValueError, SyntaxError) as exc:
        raise ImmagineNonValida("immagine danneggiata") from exc
    return immagine


def _in_webp(immagine, qualita: int, metodo: int = 4) -> bytes:
    con_trasparenza = immagine.mode in ("RGBA", "LA") or (immagine.mode == "P" and "transparency" in immagine.info)
    immagine = immagine.convert("RGBA" if con_trasparenza else "RGB")
    uscita = io.BytesIO()
    immagine.save(uscita, format="WEBP", quality=qualita, method=metodo)
    return uscita.getvalue()


def prepara_immagine_articolo(dati: bytes) -> Tuple[bytes, int, int]:
    """Un'immagine di articolo o di sezione: orientata, non oltre 1600 px di larghezza,
    riscritta in WebP (senza metadati). Restituisce `(webp, larghezza, altezza)`."""
    from PIL import Image

    immagine = _decodifica(_apri(dati))
    if immagine.width > LARGHEZZA_MAX_ARTICOLO:
        altezza = round(immagine.height * LARGHEZZA_MAX_ARTICOLO / immagine.width)
        immagine = immagine.resize((LARGHEZZA_MAX_ARTICOLO, max(1, altezza)), Image.Resampling.LANCZOS)
    return _in_webp(immagine, 82), immagine.width, immagine.height


def prepara_avatar(dati: bytes) -> Tuple[bytes, int, int]:
    """Un avatar: ritagliato al centro in un quadrato di 256 px, in WebP."""
    from PIL import Image, ImageOps

    immagine = _decodifica(_apri(dati))
    immagine = ImageOps.fit(immagine, (LATO_AVATAR, LATO_AVATAR), Image.Resampling.LANCZOS, centering=(0.5, 0.4))
    return _in_webp(immagine, 85), LATO_AVATAR, LATO_AVATAR
