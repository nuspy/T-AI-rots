"""Le immagini di un mazzo caricate dalla console: riconoscere i file, controllarli, convertirli.

Un mazzo arriva come **ZIP** (tutto in una richiesta) o come **cartella** scelta nel browser (un file per richiesta,
con la sua posizione nella cartella). In entrambi i casi valgono le regole di `tools/installa_mazzo.py`: il nome
del file senza estensione **è** l'id della carta (`maj-00`, `bastoni-06`, `coppe-regina`…), più `dorso`; servono
tutte e 78 le carte e il dorso.

**Quali file contano.** Si accettano PNG, JPEG e WebP (estensione `.png`, `.jpg`, `.jpeg`, `.webp`, maiuscole o
minuscole). Non contano: le cartelle, i file di sistema (`__MACOSX/`, `.DS_Store`, `Thumbs.db`), e tutto ciò che sta
in una cartella che comincia con `_` o `.` — come `_staging/`, dove la pipeline `crea-mazzo-tarocchi` lascia le
prove. Un'immagine con un nome che non è una carta «avanza»: la si elenca, non blocca.

**Doppioni.** La cartella di un set (`Grafica/Cards/Lovers`) può avere gli originali e, in `Web/`, la versione già
ridotta, con gli stessi nomi: se una sola delle copie sta in una cartella `Web`, vince quella; altrimenti è un
doppione e l'operatore deve scegliere (errore con l'elenco).

**Conversione.** Ogni immagine si riscrive in WebP alla misura del sito (dentro 360×640, le proporzioni restano),
qualità 60 come `tools/resize_cards.py`: niente metadati, niente sorprese da un file che dichiara un formato e ne
contiene un altro.

**ZIP.** Non si scrive mai niente su disco: i nomi servono solo a riconoscere la carta (niente zip-slip possibile),
ma un percorso assoluto o con `..` è comunque rifiutato — è il segno di un archivio costruito male o apposta. Tetti
sul numero di voci, sulla dimensione di ciascuna e sul totale decompresso (contro le «bombe» ZIP), e niente voci
cifrate.
"""
from __future__ import annotations

import hashlib
import io
import zipfile
from dataclasses import dataclass, field
from typing import AbstractSet, Dict, Iterable, List, Optional, Tuple

#: La misura web delle carte (`tools/resize_cards.py`: 1440×2560 al 25%).
LARGHEZZA_WEB = 360
ALTEZZA_WEB = 640
QUALITA_WEBP = 60

ESTENSIONI = (".webp", ".png", ".jpg", ".jpeg")
FORMATI = frozenset({"PNG", "JPEG", "WEBP", "MPO"})
DORSO = "dorso"

#: Una carta originale (1440×2560 in PNG) pesa 5-8 MB: il tetto per file lascia margine.
MAX_FILE = 25 * 1024 * 1024
MAX_PIXEL = 40_000_000
MIN_LATO = 64
#: Lo ZIP: le 79 immagini web pesano 5-10 MB; con gli originali si arriva a qualche centinaio. Oltre, la cartella
#: (un file per richiesta) è la strada giusta.
MAX_ZIP = 300 * 1024 * 1024
MAX_VOCI_ZIP = 1000
MAX_TOTALE_ZIP = 1024 * 1024 * 1024

_SISTEMA = frozenset({".ds_store", "thumbs.db", "desktop.ini"})


class ImmaginiMazzoNonValide(ValueError):
    """Il caricamento non va: `dettaglio` porta il messaggio e, quando servono, gli elenchi (cosa manca, cosa
    avanza, i doppioni), pronti per la risposta dell'API."""

    def __init__(self, messaggio: str, **elenchi: List[str]) -> None:
        super().__init__(messaggio)
        self.dettaglio: Dict[str, object] = {"messaggio": messaggio, **elenchi}


@dataclass
class Riconoscimento:
    """Com'è stato letto un insieme di file: la carta → il percorso scelto, e il resto."""

    scelti: Dict[str, str] = field(default_factory=dict)
    avanzano: List[str] = field(default_factory=list)
    ignorati: List[str] = field(default_factory=list)
    doppioni: Dict[str, List[str]] = field(default_factory=dict)

    def mancanti(self, attesi: Iterable[str]) -> List[str]:
        return [cid for cid in attesi if cid not in self.scelti]


def ids_attesi(ordine_carte: Iterable[str]) -> List[str]:
    """Gli id da trovare: le 78 carte nell'ordine del mazzo, poi il dorso."""
    return [*ordine_carte, DORSO]


def _parti(percorso: str) -> List[str]:
    return [p for p in percorso.replace("\\", "/").split("/") if p not in ("", ".")]


def percorso_sicuro(percorso: str) -> bool:
    """Niente percorsi assoluti (anche `C:/…`) né risalite (`..`)."""
    normale = percorso.replace("\\", "/")
    if normale.startswith("/") or (len(normale) > 1 and normale[1] == ":"):
        return False
    return ".." not in normale.split("/")


def id_carta(percorso: str, validi: AbstractSet[str]) -> Tuple[Optional[str], str]:
    """`(id, esito)`: l'id della carta del file, oppure `None` con `esito` = `ignorato` (non è un file del mazzo) o
    `avanza` (un'immagine che non è una carta)."""
    parti = _parti(percorso)
    if not parti:
        return None, "ignorato"
    nome = parti[-1]
    if any(p.startswith((".", "_")) for p in parti[:-1]) or nome.lower() in _SISTEMA or nome.startswith("."):
        return None, "ignorato"
    base, punto, estensione = nome.rpartition(".")
    if not punto or f".{estensione.lower()}" not in ESTENSIONI:
        return None, "ignorato"
    cid = base.strip().lower()
    return (cid, "carta") if cid in validi else (None, "avanza")


def riconosci(percorsi: Iterable[str], validi: AbstractSet[str]) -> Riconoscimento:
    r = Riconoscimento()
    candidati: Dict[str, List[str]] = {}
    for percorso in percorsi:
        cid, esito = id_carta(percorso, validi)
        if cid is None:
            (r.avanzano if esito == "avanza" else r.ignorati).append(percorso)
            continue
        candidati.setdefault(cid, []).append(percorso)
    for cid, lista in candidati.items():
        if len(lista) == 1:
            r.scelti[cid] = lista[0]
            continue
        in_web = [p for p in lista if len(_parti(p)) > 1 and _parti(p)[-2].lower() == "web"]
        if len(in_web) == 1:
            r.scelti[cid] = in_web[0]
        else:
            r.doppioni[cid] = sorted(lista)
    return r


def controlla(r: Riconoscimento, attesi: List[str]) -> None:
    """Solleva se mancano carte o ci sono doppioni; quello che avanza si riporta, non blocca."""
    mancanti = r.mancanti(attesi)
    if mancanti or r.doppioni:
        parti = []
        if mancanti:
            parti.append(f"mancano {len(mancanti)} file su {len(attesi)}")
        if r.doppioni:
            parti.append(f"{len(r.doppioni)} carte compaiono più volte")
        raise ImmaginiMazzoNonValide(
            "Il mazzo non è completo: " + ", ".join(parti) + ".",
            mancanti=mancanti,
            avanzano=sorted(r.avanzano),
            doppioni=[f"{cid}: {', '.join(p)}" for cid, p in sorted(r.doppioni.items())],
        )


def leggi_zip(corpo: bytes, attesi: List[str]) -> Tuple[Riconoscimento, Dict[str, bytes]]:
    """Riconosce le carte dello ZIP, controlla che ci siano tutte (`controlla`) e solo allora ne legge i byte:
    `(riconoscimento, id carta → byte)`. I file che non sono carte non si decomprimono nemmeno."""
    if len(corpo) > MAX_ZIP:
        raise ImmaginiMazzoNonValide(f"Lo ZIP supera {MAX_ZIP // (1024 * 1024)} MB: carica la cartella.")
    try:
        archivio = zipfile.ZipFile(io.BytesIO(corpo))
        voci = archivio.infolist()
    except (zipfile.BadZipFile, OSError, ValueError) as exc:
        raise ImmaginiMazzoNonValide("Il file caricato non è uno ZIP valido.") from exc
    if len(voci) > MAX_VOCI_ZIP:
        raise ImmaginiMazzoNonValide(f"Lo ZIP ha troppi file ({len(voci)}, al massimo {MAX_VOCI_ZIP}).")
    insicuri = [v.filename for v in voci if not percorso_sicuro(v.filename)]
    if insicuri:
        raise ImmaginiMazzoNonValide("Lo ZIP contiene percorsi non ammessi.", rifiutati=insicuri[:20])
    per_nome = {v.filename: v for v in voci if not v.is_dir()}
    r = riconosci(per_nome, set(attesi))
    controlla(r, attesi)
    dati: Dict[str, bytes] = {}
    totale = 0
    for cid, percorso in r.scelti.items():
        voce = per_nome[percorso]
        if voce.flag_bits & 0x1:
            raise ImmaginiMazzoNonValide("Lo ZIP è protetto da password: caricalo senza.")
        if voce.file_size > MAX_FILE:
            raise ImmaginiMazzoNonValide(f"{percorso}: supera {MAX_FILE // (1024 * 1024)} MB.")
        # Al più il tetto più un byte: una voce che mente sulla propria dimensione non passa lo stesso.
        try:
            with archivio.open(voce) as f:
                letti = f.read(MAX_FILE + 1)
        except (zipfile.BadZipFile, OSError, ValueError, RuntimeError, NotImplementedError) as exc:
            raise ImmaginiMazzoNonValide(f"{percorso}: non si legge dallo ZIP.") from exc
        if len(letti) > MAX_FILE:
            raise ImmaginiMazzoNonValide(f"{percorso}: supera {MAX_FILE // (1024 * 1024)} MB.")
        totale += len(letti)
        if totale > MAX_TOTALE_ZIP:
            raise ImmaginiMazzoNonValide("Lo ZIP decompresso è troppo grande.")
        dati[cid] = letti
    return r, dati


def prepara_carta(dati: bytes, nome: str = "immagine") -> Tuple[bytes, int, int]:
    """`(webp, larghezza, altezza)`: l'immagine orientata, dentro 360×640, in WebP senza metadati."""
    from PIL import Image, ImageOps, UnidentifiedImageError

    if not dati:
        raise ImmaginiMazzoNonValide(f"{nome}: il file è vuoto.")
    if len(dati) > MAX_FILE:
        raise ImmaginiMazzoNonValide(f"{nome}: supera {MAX_FILE // (1024 * 1024)} MB.")
    try:
        immagine = Image.open(io.BytesIO(dati))
        formato, (w, h) = immagine.format, immagine.size
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as exc:
        raise ImmaginiMazzoNonValide(f"{nome}: non è un'immagine valida.") from exc
    if formato not in FORMATI:
        raise ImmaginiMazzoNonValide(f"{nome}: formato non ammesso (solo PNG, JPEG o WebP).")
    if w < MIN_LATO or h < MIN_LATO or w * h > MAX_PIXEL:
        raise ImmaginiMazzoNonValide(f"{nome}: dimensioni non ammesse ({w}×{h}).")
    try:
        immagine.load()
        immagine = ImageOps.exif_transpose(immagine)
    except (OSError, ValueError, SyntaxError) as exc:
        raise ImmaginiMazzoNonValide(f"{nome}: immagine danneggiata.") from exc
    scala = min(LARGHEZZA_WEB / immagine.width, ALTEZZA_WEB / immagine.height, 1.0)
    if scala < 1.0:
        nuova = (max(1, round(immagine.width * scala)), max(1, round(immagine.height * scala)))
        immagine = immagine.resize(nuova, Image.Resampling.LANCZOS)
    trasparente = immagine.mode in ("RGBA", "LA") or (immagine.mode == "P" and "transparency" in immagine.info)
    immagine = immagine.convert("RGBA" if trasparente else "RGB")
    uscita = io.BytesIO()
    immagine.save(uscita, format="WEBP", quality=QUALITA_WEBP, method=6)
    return uscita.getvalue(), immagine.width, immagine.height


def impronta(dati: bytes) -> str:
    """L'ETag di un'immagine: le prime 32 cifre dello SHA-256 dei byte."""
    return hashlib.sha256(dati).hexdigest()[:32]


def versione(impronte: Iterable[str]) -> str:
    """L'impronta di una serie intera (16 caratteri): cambia se cambia anche una sola carta."""
    return hashlib.sha256("|".join(sorted(impronte)).encode()).hexdigest()[:16]
