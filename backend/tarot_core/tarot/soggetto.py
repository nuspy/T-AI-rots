"""Il soggetto di un articolo del blog: la carta o la stesa di cui parla (v9.4).

Un articolo «Wheel of Fortune Tarot Meaning» parla di una carta (`maj-10`), «How to Read the Celtic Cross» di una
stesa (`croce-celtica`), «Full Moon Tarot Spread» di nessuna delle due. Il soggetto serve a mettere l'articolo nella
sezione della sua carta e a mostrarlo **per primo** nelle pagine di quella carta o di quella stesa
(`/blog/nove`, `GET /blog/posts?carta=`).

Si ricava da **titolo e parola chiave** (prima il titolo; la parola chiave solo se il titolo non nomina niente):
alla creazione e alla modifica di un articolo che non ce l'ha (`BlogRepository.salva`) e una volta per gli articoli
che c'erano già (migrazione `20261022_1000`). Chi scrive può sempre indicarlo a mano, o toglierlo.

**Le carte.** Il catalogo dei nomi è una copia di quello della regola delle immagini
(`skills/tarots-blog-images/scripts/tarots_images.py`: MAJOR_ARCANA, CONTEXT_NAMES, MINOR_RANKS, MINOR_SUITS,
CARD_CONTEXT, NAME_GAP, NOT_A_CARD_NAME, `named_cards`), **copiato e non importato** (il backend non dipende dalle
skill), con i nomi portati agli id di `knowledge/deck.json`. Ogni carta ha i nomi di Thoth, Rider-Waite, Marsiglia e
italiani; un nome che è anche una parola comune («Moon», «Sun», «Star», «Death», «World», «Art», «Fortune»…) conta
solo vicino a una parola dei tarocchi (tarot, card, arcana, Thoth…) o quando è tutto il titolo; le frasi che
contengono un nome ma non la carta («Full Moon», «Sun sign», «the art of», «fortune telling») non contano mai.
Fra le figure, Page = Knave = Fante = Princess (`principessa`); il King del Rider-Waite è il Knight di Thoth
(`cavaliere`, la corrispondenza della Golden Dawn), il Knight e il Prince si prendono per nome.

**Le stese.** Nomi e slug di `knowledge/spreads.json`, di `knowledge/en/spreads-*.json` e di `knowledge/nomi.json`.
Un nome fatto solo di parole comuni («Three cards», «Simple cross») o di una parola sola («Mirror», «Crossroads»)
conta solo vicino a una parola come «spread», «stesa», «reading», o quando è tutto il titolo; uno distintivo («Celtic
Cross», «Ruota astrologica») conta ovunque.

Se un testo nomina una carta e una stesa vince quella nominata **prima**.
"""
from __future__ import annotations

import re
import unicodedata
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple

TIPI_SOGGETTO = ("carta", "stesa")

# ---- il catalogo dei nomi delle carte (copia di tarots_images.py, con gli id del mazzo) --------------------------

#: Ogni arcano maggiore: il suo id → tutti i nomi con cui si chiama (Thoth, Rider-Waite, Marsiglia, italiano), scritti
#: «piani» (minuscolo, senza accenti né punteggiatura). Adjustment = Justice, Lust = Strength, Art = Temperance,
#: Aeon = Judgement, Universe = World, Fortune = Wheel of Fortune, Magus = Magician, Priestess = High Priestess.
ARCANI_MAGGIORI: Dict[str, Tuple[str, ...]] = {
    "maj-00": ("fool", "matto", "folle"),
    "maj-01": ("magus", "magician", "mago", "bagatto", "bagatella"),
    "maj-02": ("high priestess", "priestess", "papessa", "gran sacerdotessa", "sacerdotessa"),
    "maj-03": ("empress", "imperatrice"),
    "maj-04": ("emperor", "imperatore"),
    "maj-05": ("hierophant", "pope", "papa", "ierofante"),
    "maj-06": ("lovers", "amanti", "innamorati"),
    "maj-07": ("chariot", "carro"),
    "maj-08": ("adjustment", "justice", "giustizia", "regolazione"),
    "maj-09": ("hermit", "eremita"),
    "maj-10": ("wheel of fortune", "ruota della fortuna", "fortune", "fortuna"),
    "maj-11": ("lust", "strength", "lussuria", "forza"),
    "maj-12": ("hanged man", "appeso", "impiccato"),
    "maj-13": ("death", "morte"),
    "maj-14": ("temperance", "temperanza", "art", "arte"),
    "maj-15": ("devil", "diavolo"),
    "maj-16": ("house of god", "maison dieu", "casa di dio", "tower", "torre"),
    "maj-17": ("star", "stella"),
    "maj-18": ("moon", "luna"),
    "maj-19": ("sun", "sole"),
    "maj-20": ("aeon", "eone", "judgement", "judgment", "giudizio"),
    "maj-21": ("universe", "world", "universo", "mondo"),
}
#: I nomi che sono anche parole comuni: contano solo entro NAME_GAP parole da una parola dei tarocchi (CARD_CONTEXT)
#: o quando sono tutto il testo («The Tower»). Gli altri (Hierophant, High Priestess, Hanged Man, Ace of Cups…)
#: sono inconfondibili e contano ovunque.
NOMI_DA_CONTESTO = frozenset("""
fool matto folle mago pope papa lovers amanti innamorati chariot carro adjustment justice giustizia regolazione
fortune fortuna lust strength lussuria forza appeso death morte art arte devil diavolo tower torre star stella moon
luna sun sole judgement judgment giudizio universe world universo mondo
""".split())
#: Gli arcani minori: il grado (`rango` di deck.json) e il seme, ciascuno con i suoi nomi.
RANGHI_MINORI: Dict[str, Tuple[str, ...]] = {
    "asso": ("ace", "1", "asso"), "due": ("two", "2", "due"), "tre": ("three", "3", "tre"),
    "quattro": ("four", "4", "quattro"), "cinque": ("five", "5", "cinque"), "sei": ("six", "6", "sei"),
    "sette": ("seven", "7", "sette"), "otto": ("eight", "8", "otto"), "nove": ("nine", "9", "nove"),
    "dieci": ("ten", "10", "dieci"),
    # Il King del Rider-Waite è il Knight di Thoth (la corrispondenza della Golden Dawn).
    "cavaliere": ("knight", "cavaliere", "cavallo", "king", "re"),
    "regina": ("queen", "regina"),
    "principe": ("prince", "principe"),
    # Page = Knave = Fante = Princess.
    "principessa": ("princess", "principessa", "page", "knave", "fante"),
}
SEMI_MINORI: Dict[str, Tuple[str, ...]] = {
    "bastoni": ("wands", "wand", "rods", "staves", "batons", "bastoni"),
    "coppe": ("cups", "cup", "chalices", "coppe"),
    "spade": ("swords", "sword", "spade"),
    "dischi": ("disks", "disk", "discs", "disc", "pentacles", "pentacle", "coins", "coin", "denari", "dischi", "pentacoli"),
}
#: I numeri dei gradi numerali: `bastoni-01`… `bastoni-10`; le figure hanno l'id col nome (`coppe-principessa`).
NUMERO_DEL_RANGO = {
    "asso": 1, "due": 2, "tre": 3, "quattro": 4, "cinque": 5, "sei": 6, "sette": 7, "otto": 8, "nove": 9, "dieci": 10,
}
#: Le parole dei tarocchi che fanno di un nome comune («Moon», «Death») il nome di una carta, se vicine.
CONTESTO_CARTA = r"\b(?:tarot\w*|tarocc\w*|cards?|carta|carte|arcan\w*|thoth|atu|trumps?)\b"
DISTANZA = 4
#: Le frasi con il nome di una carta che non sono la carta (astrologia, modi di dire, «the art of»): si tolgono prima
#: di cercare, così «Full Moon tarot spread», «Sun sign tarot», «the art of tarot» non nominano carte.
NON_UNA_CARTA = (
    r"\b(?:full|new|half|crescent|gibbous|waxing|waning|harvest|blue|blood|hunter s|hunters|wolf|snow|worm|pink"
    r"|strawberry|buck|sturgeon|corn|beaver|cold|super|dark|black)\s+moons?\b"
    r"|\b(?:moon|sun)\s+(?:signs?|phases?|cycles?|void|water|calendar|salutations?)\b"
    r"|\b(?:moon|sun|venus|mars|mercury)\s+in\s+(?:aries|taurus|gemini|cancer|leo|virgo|libra|scorpio|sagittarius"
    r"|capricorn|aquarius|pisces)\b"
    r"|\bstar\s+(?:signs?|seeds?|charts?|maps?)\b"
    r"|\b(?:shooting|falling|north|pole|morning|evening|lucky|guiding|rising|five pointed|six pointed)\s+stars?\b"
    r"|\b(?:rising|setting|midnight|midsummer)\s+suns?\b"
    r"|\bdeath\s+(?:anniversary|anniversaries|penalty|toll)\b|\bnear\s+death\b"
    r"|\bworld\s+(?:tarot\s+day|war|wide)\b|\b(?:around|across)\s+the\s+world\b"
    r"|\bfortune\s+tell\w*|\bfortunetell\w*|\bgood\s+fortune\b|\bbuona\s+fortuna\b"
    r"|\bart\s+of\b|\b(?:tarot|thoth|deck|card)\s+art\b"
    r"|\bart\s+(?:decks?|journals?|journaling|prints?|therapy|nouveau|deco|history)\b"
    r"|\barte\s+d(?:i|e[il]\w*)\b"
    r"|\bapril\s+fools?\b|\bfor\s+lovers\b"
    r"|\bluna\s+(?:piena|nuova|crescente|calante)\b|\bsegn[oi]\s+(?:del\s+)?sole\b"
)
_ARTICOLI = frozenset("the la il lo l le gli i el los las".split())

_NOMI_MAGGIORI = sorted(((alias, carta) for carta, nomi in ARCANI_MAGGIORI.items() for alias in nomi),
                        key=lambda t: -len(t[0]))
_RANGO_DI = {alias: rango for rango, nomi in RANGHI_MINORI.items() for alias in nomi}
_SEME_DI = {alias: seme for seme, nomi in SEMI_MINORI.items() for alias in nomi}
_NOME_MINORE = (r"\b(" + "|".join(sorted(_RANGO_DI, key=len, reverse=True)) + r")\s+(?:of|di|de)\s+("
                + "|".join(sorted(_SEME_DI, key=len, reverse=True)) + r")\b")


def piano(testo: str) -> str:
    """Minuscolo, senza accenti, solo lettere e cifre separate da uno spazio: come si cercano i nomi. A differenza della
    copia nelle skill tiene anche le lettere non latine (i nomi russi e ucraini delle stese)."""
    testo = unicodedata.normalize("NFKD", str(testo or "")).replace("æ", "ae").replace("Æ", "ae").replace("œ", "oe")
    testo = "".join(c for c in testo if not unicodedata.combining(c)).lower()
    return " ".join(re.sub(r"[\W_]+", " ", testo).split())


def id_carta_minore(rango: str, seme: str) -> str:
    numero = NUMERO_DEL_RANGO.get(rango)
    return f"{seme}-{numero:02d}" if numero else f"{seme}-{rango}"


def _vicino(primo: int, ultimo: int, contesto: List[int]) -> bool:
    return any(primo - DISTANZA <= c < primo or ultimo < c <= ultimo + DISTANZA for c in contesto)


def carte_nominate(testo: str) -> List[Tuple[int, str]]:
    """Le carte nominate in `testo`, come (indice della parola, id), in ordine. Un nome che è anche una parola comune
    conta solo vicino a una parola dei tarocchi o come testo intero; le frasi di NON_UNA_CARTA mai."""
    semplice = re.sub(NON_UNA_CARTA, lambda m: " ".join("-" for _ in m.group(0).split()), piano(testo))
    parole = semplice.split()
    contesto = [semplice[: m.start()].count(" ") for m in re.finditer(CONTESTO_CARTA, semplice)]
    intero = " ".join(p for n, p in enumerate(parole) if not (n == 0 and p in _ARTICOLI))
    presi: List[Tuple[int, int]] = []
    trovate: List[Tuple[int, str]] = []
    for m in re.finditer(_NOME_MINORE, semplice):
        presi.append((m.start(), m.end()))
        trovate.append((semplice[: m.start()].count(" "), id_carta_minore(_RANGO_DI[m.group(1)], _SEME_DI[m.group(2)])))
    for alias, carta in _NOMI_MAGGIORI:  # i più lunghi prima: «wheel of fortune» prima di «fortune»
        for m in re.finditer(r"\b" + re.escape(alias) + r"\b", semplice):
            if any(s < m.end() and m.start() < e for s, e in presi):
                continue
            presi.append((m.start(), m.end()))
            primo = semplice[: m.start()].count(" ")
            ultimo = primo + alias.count(" ")
            if alias in NOMI_DA_CONTESTO and intero != alias and not _vicino(primo, ultimo, contesto):
                continue
            trovate.append((primo, carta))
    return sorted(trovate)


# ---- le stese ------------------------------------------------------------------------------------------------

#: Le parole che fanno di un nome comune («Mirror», «Three cards») il nome di una stesa, se vicine.
CONTESTO_STESA = (
    r"\b(?:spreads?|layouts?|readings?|stes[ae]|disposizion[ei]|letture?|tiradas?|lecturas?|tirages?"
    r"|kirakas\w*|расклад\w*|розклад\w*)\b"
)
#: Le parole troppo comuni per fare da sole il nome di una stesa: un nome fatto solo di queste (o di una parola sola)
#: vuole il contesto. «Celtic Cross» no: «celtic» basta.
PAROLE_COMUNI = frozenset("""
the a an of for to and or in on la il lo le i gli di del della per e o a da in un una el los las de y por
one two three four five six seven eight nine ten uno due tre quattro cinque sei sette otto nove dieci
dos tres cuatro cinco siete ocho nueve diez card cards carta carte cartas simple semplice cross croce cruz
spread spreads stesa stese tirada reading lettura layout
""".split())


def _senza_parentesi(nome: str) -> str:
    return re.sub(r"\([^)]*\)", " ", nome or "")


@lru_cache(maxsize=1)
def _nomi_stese() -> Tuple[Tuple[str, str, bool], ...]:
    """(nome piano, id della stesa, serve il contesto), dai più lunghi: da spreads.json, en/ e nomi.json."""
    from .conoscenza import condivisa

    conoscenza = condivisa()
    voci: Dict[str, Tuple[str, bool]] = {}

    def aggiungi(nome: str, spread_id: str) -> None:
        semplice = piano(_senza_parentesi(nome))
        if not semplice:
            return
        # «three card spread» → anche «three card»: la parola di stesa in fondo fa da contesto, non da nome.
        varianti = {semplice}
        corto = re.sub(CONTESTO_STESA + r"\s*$", "", semplice).strip()
        if corto:
            varianti.add(corto)
        for v in varianti:
            parole = v.split()
            contesto = len(parole) < 2 or all(p in PAROLE_COMUNI for p in parole)
            voci.setdefault(v, (spread_id, contesto))

    for stesa in conoscenza.stese.values():
        sid = stesa["id"]
        aggiungi(sid.replace("-", " "), sid)
        aggiungi(stesa.get("nome") or "", sid)
        aggiungi(stesa.get("nome_en") or "", sid)
        for per_lingua in conoscenza.testi.values():
            scheda = per_lingua.get("stese", {}).get(sid) or {}
            aggiungi(scheda.get("nome") or "", sid)
            aggiungi((scheda.get("slug") or "").replace("-", " "), sid)
        for per_lingua in conoscenza.nomi.values():
            aggiungi((per_lingua.get("stese", {}).get(sid) or {}).get("nome") or "", sid)
    return tuple(sorted(((n, s, c) for n, (s, c) in voci.items()), key=lambda t: -len(t[0])))


def stese_nominate(testo: str) -> List[Tuple[int, str]]:
    """Le stese nominate in `testo`, come (indice della parola, id), in ordine."""
    semplice = piano(testo)
    parole = semplice.split()
    intero = " ".join(p for n, p in enumerate(parole) if not (n == 0 and p in _ARTICOLI))
    contesto = [semplice[: m.start()].count(" ") for m in re.finditer(CONTESTO_STESA, semplice)]
    presi: List[Tuple[int, int]] = []
    trovate: List[Tuple[int, str]] = []
    for nome, spread_id, serve_contesto in _nomi_stese():
        for m in re.finditer(r"\b" + re.escape(nome) + r"\b", semplice):
            if any(s < m.end() and m.start() < e for s, e in presi):
                continue
            primo = semplice[: m.start()].count(" ")
            ultimo = primo + nome.count(" ")
            if serve_contesto and intero != nome and not _vicino(primo, ultimo, contesto):
                continue
            presi.append((m.start(), m.end()))
            trovate.append((primo, spread_id))
    return sorted(trovate)


# ---- il soggetto ----------------------------------------------------------------------------------------------


def soggetto_di(testo: str) -> Optional[Tuple[str, str]]:
    """(tipo, id) della carta o stesa nominata per prima in `testo`, o None."""
    candidati = [(n, "carta", c) for n, c in carte_nominate(testo)] + [(n, "stesa", s) for n, s in stese_nominate(testo)]
    if not candidati:
        return None
    _, tipo, riferimento = min(candidati, key=lambda t: (t[0], t[1]))
    return tipo, riferimento


def calcola(titolo: Optional[str], parola_chiave: Optional[str] = None) -> Optional[Tuple[str, str]]:
    """Il soggetto di un articolo: dal titolo, altrimenti dalla parola chiave. None se nessuno dei due nomina una carta
    o una stesa."""
    for testo in (titolo, parola_chiave):
        if testo and testo.strip():
            trovato = soggetto_di(testo)
            if trovato is not None:
                return trovato
    return None


class SoggettoNonValido(ValueError):
    """Un soggetto indicato a mano che non esiste."""


def normalizza(tipo: Optional[str], riferimento: Optional[str]) -> Optional[Tuple[str, str]]:
    """Un soggetto indicato a mano → (tipo canonico, id canonico). Il tipo si accetta anche in inglese (`card`,
    `spread`); il riferimento per id o per slug in qualunque lingua (`maj-10`, `fortune`, `la-ruota-della-fortuna`;
    `croce-celtica`, `celtic-cross`). `tipo` vuoto: nessun soggetto."""
    from .conoscenza import condivisa

    if not tipo:
        return None
    tipo = {"card": "carta", "spread": "stesa"}.get(tipo.strip().lower(), tipo.strip().lower())
    if tipo not in TIPI_SOGGETTO:
        raise SoggettoNonValido(f"tipo di soggetto sconosciuto «{tipo}»: carta o stesa")
    conoscenza = condivisa()
    ref = (riferimento or "").strip().lower()
    trovato = conoscenza.risolvi_carta(ref) if tipo == "carta" else conoscenza.risolvi_stesa(ref)
    if trovato is None:
        raise SoggettoNonValido(f"{tipo} sconosciuta «{riferimento}»")
    return tipo, trovato


def soggetto_json(tipo: Optional[str], riferimento: Optional[str], lang: Optional[str] = "en") -> Optional[Dict[str, Any]]:
    """`{"tipo", "ref", "nome", "slug"}` per le risposte, nella lingua data (nome e slug); None senza soggetto."""
    from .conoscenza import condivisa

    if not tipo or not riferimento:
        return None
    conoscenza = condivisa()
    if tipo == "carta" and riferimento in conoscenza.carte:
        return {"tipo": tipo, "ref": riferimento, "nome": conoscenza.nome_carta(riferimento, lang or "en"),
                "slug": conoscenza.slug_carta(riferimento, lang or "en")}
    stesa = conoscenza.stesa(riferimento) if tipo == "stesa" else None
    if stesa is not None:
        return {"tipo": tipo, "ref": riferimento, "nome": conoscenza.nome_stesa(stesa, lang or "en"),
                "slug": conoscenza.slug_stesa(riferimento, lang or "en")}
    return {"tipo": tipo, "ref": riferimento, "nome": None, "slug": None}
