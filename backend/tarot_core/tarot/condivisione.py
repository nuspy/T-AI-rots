"""La condivisione di una lettura: regole pure, senza database né rete.

**Cosa si accerta, e cosa no.** Nessun sito può sapere se un utente ha davvero
pubblicato un post su Instagram, TikTok, Facebook o X: le piattaforme non lo
dicono, o lo dicono solo a chi ha permessi che non si ottengono per un servizio
piccolo. Si accerta l'**effetto**: il link della lettura, unico per lettura e
pubblico, viene aperto da un visitatore vero. Una lettura conta come condivisa
quando, **dopo che il proprietario ha usato un pulsante di condivisione** e
entro `GIORNI_FINESTRA` giorni, il suo link è aperto da un visitatore che

- non è il proprietario (visitatore e rete diversi da quelli del clic);
- non è un crawler (le anteprime dei social non contano);
- è distinto: ogni lettura conta una volta sola.

Non prova che il post esista — chi apre il link potrebbe essere un amico a cui
l'utente l'ha mandato in privato — ma prova che il link è uscito dal suo
dispositivo e ha raggiunto qualcuno: è ciò che al servizio serve.

**Anonimato delle letture speciali.** Il responso di una lettura di
compatibilità o di coppia cita il nome dell'altra persona, che non ha dato il
consenso. Nella versione condivisa il nome diventa «qualcuno di speciale» (nella
lingua della lettura) e al suo posto compare un simbolo grafico del suo genere,
in stile tarocchi. Cognome e date non escono mai.
"""
from __future__ import annotations

import hashlib
import io
import re
import unicodedata
from typing import Dict, Optional, Tuple

#: Ogni quante letture conteggiate si regala una lettura.
SOGLIA_PREMIO = 5
#: Entro quanti giorni dal clic di condivisione il link deve essere aperto.
GIORNI_FINESTRA = 7
#: Le letture regalate a chi condivide per ogni persona che si iscrive dal suo link.
CREDITI_ISCRIZIONE = 5
#: Da quanto tempo al massimo un account è «nuovo» per l'attribuzione di un'iscrizione.
ORE_ACCOUNT_NUOVO = 48

CANALI = ("instagram", "facebook", "tiktok", "x", "email", "link", "nativo")

LUNGHEZZA_TESTO = 200


# ---- testo personalizzato -----------------------------------------------------


def pulisci_testo(testo: Optional[str], massimo: int = LUNGHEZZA_TESTO) -> str:
    """Il testo personalizzato del post: una riga, senza caratteri di controllo."""
    if not testo:
        return ""
    puliti = []
    for c in unicodedata.normalize("NFKC", testo):
        categoria = unicodedata.category(c)
        if categoria[0] == "C" and c not in "\n\t":
            continue
        puliti.append(" " if c in "\n\t\r" else c)
    return " ".join("".join(puliti).split())[:massimo].strip()


# ---- simbolo del genere -------------------------------------------------------

#: I simboli astrologici e alchemici di Venere, Marte e Mercurio (e una stella a
#: quattro punte per chi non è né uomo né donna né ha scelto un genere): sono i
#: segni della tradizione dei tarocchi, non i pittogrammi dei servizi igienici.
SIMBOLI: Dict[str, str] = {
    "donna": "venere",
    "uomo": "marte",
    "non_binario": "mercurio",
    "altro": "stella",
    "non_dice": "stella",
}


def simbolo_partner(genere: Optional[str]) -> str:
    return SIMBOLI.get(genere or "", "stella")


# ---- anonimizzazione ----------------------------------------------------------


def _varianti_del_nome(nome: str) -> list:
    """Il nome intero e ciascuna sua parola di almeno 3 lettere, dalla più lunga."""
    parole = [p for p in re.split(r"[\s\-']+", nome) if len(p) >= 3]
    varianti = {nome.strip()} | set(parole)
    return sorted((v for v in varianti if v), key=len, reverse=True)


def anonimizza(testo: Optional[str], nome: Optional[str], frase: str, *, lang: str = "it") -> Optional[str]:
    """Sostituisce il nome dell'altra persona con `frase` («qualcuno di speciale»).

    Parola intera, senza badare alle maiuscole. In ungherese le desinenze si
    attaccano al nome («Marcóval»): lì si prende anche il suffisso, purché il
    nome sia di almeno 4 lettere, per non toccare parole che iniziano allo stesso modo.
    """
    if not testo or not nome or not nome.strip():
        return testo
    risultato = testo
    for variante in _varianti_del_nome(nome):
        coda = r"\w{0,6}" if lang.startswith("hu") and len(variante) >= 4 else ""
        modello = re.compile(rf"(?<!\w){re.escape(variante)}{coda}(?!\w)", re.IGNORECASE | re.UNICODE)
        risultato = modello.sub(lambda _m: frase, risultato)
    return risultato


# ---- chi visita ---------------------------------------------------------------

_BOT = re.compile(
    r"bot|crawl|spider|slurp|preview|facebookexternalhit|facebot|whatsapp|telegram|"
    r"linkedin|discord|pinterest|embed|headless|lighthouse|pagespeed|curl|wget|"
    r"python-requests|httpx|aiohttp|okhttp|java/|go-http|scrapy|monitor|uptime|"
    r"check_http|nagios|zabbix|prometheus",
    re.IGNORECASE,
)


def e_un_bot(user_agent: Optional[str]) -> bool:
    """Un crawler o uno strumento da riga di comando: non conta come visitatore.
    Un'intestazione assente conta come bot: un browser vero la manda sempre."""
    return not user_agent or bool(_BOT.search(user_agent))


_VISITATORE = re.compile(r"^[A-Za-z0-9_-]{16,64}$")


def visitatore_valido(valore: Optional[str]) -> bool:
    return bool(valore) and bool(_VISITATORE.match(valore or ""))


def anonimo(valore: str, sale: str) -> str:
    """Un'impronta non reversibile di un indirizzo o di un identificativo:
    serve a confrontare («stesso visitatore?»), non a ritrovare chi fosse."""
    return hashlib.sha256(f"{sale}:{valore}".encode("utf-8")).hexdigest()[:32]


# ---- immagini ----------------------------------------------------------------

#: L'immagine di una lettura condivisa è **una sola**, WebP 400×300 molto compresso
#: (poche decine di KB): pesa poco nel database, nel link e nelle anteprime dei social.
MISURA_FINALE: Tuple[int, int] = (400, 300)
#: Il browser la compone al doppio (testi più nitidi dopo la riduzione) o già finita.
MISURE_AMMESSE = frozenset({MISURA_FINALE, (800, 600)})
FORMATI_AMMESSI = frozenset({"PNG", "WEBP", "JPEG"})
#: Il file caricato, non l'immagine finale: un PNG 800×600 pieno di dettagli sta sotto.
MAX_CARICO = 3_000_000
QUALITA_WEBP = 55


def prepara_immagine(dati: bytes) -> bytes:
    """Ricontrolla un'immagine caricata e la trasforma in WebP 400×300 molto compresso.

    Solleva `ValueError` con il motivo. Si legge prima l'intestazione e si controllano
    formato e misure, e solo dopo si decodifica: un file che dichiara 60000×60000 pixel
    non arriva mai al decodificatore. Il WebP si riscrive da zero, quindi non porta con
    sé metadati (EXIF, profili, testi) né dati accodati.
    """
    from PIL import Image, UnidentifiedImageError

    if not dati or len(dati) > MAX_CARICO:
        raise ValueError("immagine vuota o troppo grande")
    try:
        immagine = Image.open(io.BytesIO(dati))
        formato, misura = immagine.format, immagine.size
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as exc:
        raise ValueError("non è un'immagine valida") from exc
    if formato not in FORMATI_AMMESSI:
        raise ValueError(f"formato {formato} non ammesso")
    if misura not in MISURE_AMMESSE:
        raise ValueError(f"dimensioni {misura[0]}×{misura[1]} non ammesse")
    try:
        immagine = immagine.convert("RGB")           # decodifica: qui si scopre un file troncato
    except (OSError, ValueError, SyntaxError) as exc:
        raise ValueError("immagine danneggiata") from exc
    if misura != MISURA_FINALE:
        immagine = immagine.resize(MISURA_FINALE, Image.Resampling.LANCZOS)
    uscita = io.BytesIO()
    immagine.save(uscita, format="WEBP", quality=QUALITA_WEBP, method=6)
    return uscita.getvalue()


# ---- premi ----------------------------------------------------------------------


def progresso(verificate: int, premi: int, iscrizioni: int = 0) -> Dict[str, int]:
    """Il contatore della scheda utente."""
    return {
        "verificate": verificate,
        "premi": premi,
        "prossimo_tra": SOGLIA_PREMIO - (verificate % SOGLIA_PREMIO),
        "iscrizioni": iscrizioni,
        "soglia": SOGLIA_PREMIO,
        "crediti_iscrizione": CREDITI_ISCRIZIONE,
    }
