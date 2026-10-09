"""Le lingue dell'app, e la lingua in cui chi consulta ha posto il quesito.

**Quale lingua si scrive.** Quella del quesito, non quella dell'interfaccia:
chi apre il sito in italiano e chiede in ungherese riceve domande, letture e
responso in ungherese. La lingua si ricava **una volta**, quando la lettura si
apre, e si salva in `Reading.lang`: da lì la leggono tutte le chiamate al
modello (intervista, interpretazioni, sintesi) e i testi fissi (disclaimer,
messaggio di crisi). Si rinnova a ogni quesito, perché ogni quesito è una
lettura nuova.

**Il rilevamento è deterministico e non chiama nessun modello**: parte dalla
scrittura (hangul, devanagari, arabo, ideogrammi, cirillico) e, per il latino,
pesa le parole più comuni e le lettere che una lingua ha e le altre no. È
volutamente semplice: un quesito è una frase, e su una frase l'alfabeto e una
manciata di parole bastano. Quando non c'è indizio, o due lingue pareggiano, si
tiene la lingua dell'interfaccia.

**Le traduzioni vere** dei testi fissi sono per italiano, inglese e ungherese
(`TRADOTTE`); per le altre lingue i testi fissi ricadono sull'inglese, mentre
le risposte del modello sono comunque nella lingua del quesito.
"""
from __future__ import annotations

import re
from typing import Dict, List

#: codice → (nome nativo, nome in italiano per i prompt).
LINGUE: Dict[str, tuple] = {
    "it": ("Italiano", "italiano"),
    "hu": ("Magyar", "ungherese"),
    "en": ("English", "inglese"),
    "de": ("Deutsch", "tedesco"),
    "ru": ("Русский", "russo"),
    "uk": ("Українська", "ucraino"),
    "fr": ("Français", "francese"),
    "es": ("Español", "spagnolo"),
    "pt": ("Português", "portoghese"),
    "ro": ("Română", "rumeno"),
    "pl": ("Polski", "polacco"),
    "zh": ("中文", "cinese mandarino, in caratteri semplificati"),
    "hi": ("हिन्दी", "hindi"),
    "ko": ("한국어", "coreano"),
    "ar": ("العربية", "arabo"),
}

ORDINE: List[str] = list(LINGUE)

#: Le lingue con testi fissi tradotti davvero. Le altre ricadono sull'inglese.
TRADOTTE = ("it", "en", "hu")

#: Le lingue che si scrivono da destra a sinistra.
DA_DESTRA = ("ar",)

PREDEFINITA = "it"

#: La lingua più probabile per paese (ISO 3166-1 alpha-2): serve solo come ultimo indizio, quando né una scelta
#: salvata né la lingua del browser o del telefono dicono qualcosa di utile. Paese assente = nessun suggerimento.
LINGUA_PER_PAESE: Dict[str, str] = {
    **{p: "it" for p in ("IT", "SM", "VA")},
    "HU": "hu",
    **{p: "de" for p in ("DE", "AT", "LI")},
    **{p: "fr" for p in ("FR", "MC", "LU")},
    **{p: "ru" for p in ("RU", "BY", "KZ", "KG")},
    "UA": "uk",
    **{p: "es" for p in ("ES", "MX", "AR", "CO", "CL", "PE", "VE", "EC", "GT", "CU", "BO", "DO", "HN", "PY",
                         "SV", "NI", "CR", "PA", "UY")},
    **{p: "pt" for p in ("PT", "BR", "AO", "MZ")},
    **{p: "ro" for p in ("RO", "MD")},
    "PL": "pl",
    **{p: "zh" for p in ("CN", "TW", "HK", "MO")},
    "IN": "hi",
    "KR": "ko",
    **{p: "ar" for p in ("SA", "AE", "EG", "MA", "DZ", "TN", "JO", "LB", "IQ", "KW", "QA", "BH", "OM", "YE", "LY",
                         "SY", "SD")},
    **{p: "en" for p in ("GB", "IE", "US", "CA", "AU", "NZ", "ZA")},
}


def lingua_per_paese(paese: str | None) -> str | None:
    """La lingua suggerita per un paese, o None se il paese non dice niente (paesi multilingue non elencati, come
    Svizzera e Belgio, restano senza suggerimento)."""
    return LINGUA_PER_PAESE.get((paese or "").upper())


def lingua(lang: str) -> str:
    """Il codice di una lingua supportata; l'italiano se non lo è."""
    codice = (lang or "").strip().lower().replace("_", "-").split("-")[0]
    return codice if codice in LINGUE else PREDEFINITA


def nome_per_prompt(lang: str) -> str:
    return LINGUE[lingua(lang)][1]


def istruzione_lingua(lang: str) -> str:
    """L'ultima riga di ogni prompt: la lingua in cui il modello deve scrivere."""
    return f"Scrivi in {nome_per_prompt(lang)}, la lingua in cui chi consulta ha posto il quesito."


def in_lingua(per_lingua: Dict[str, str], lang: str) -> str:
    """Il testo fisso nella lingua richiesta; sull'inglese se manca."""
    return per_lingua.get(lingua(lang)) or per_lingua["en"]


# ---- rilevamento ----------------------------------------------------------

_SCRITTURE = {
    "hangul": re.compile(r"[가-힯ᄀ-ᇿ㄰-㆏]"),
    "devanagari": re.compile(r"[ऀ-ॿ]"),
    "arabo": re.compile(r"[؀-ۿݐ-ݿ]"),
    "han": re.compile(r"[一-鿿㐀-䶿]"),
    "cirillico": re.compile(r"[Ѐ-ӿ]"),
    "latino": re.compile(r"[A-Za-zÀ-ɏḀ-ỿ]"),
}
_KANA = re.compile(r"[぀-ヿ]")
_LETTERE_UCRAINE = re.compile(r"[іїєґІЇЄҐ]")

#: Le parole più comuni delle lingue in alfabeto latino. Non sono liste
#: complete: bastano a far vincere la lingua giusta su una frase.
_PAROLE = {
    "it": "il lo la i gli le un uno una di a da in con su per tra fra e o che non è sono ho hai ha come cosa quando dove perché mi ti si ci vi del della dei delle al alla nel nella questo questa mio mia devo posso voglio dovrei sarà lavoro anno",
    "en": "the a an of to in is are was be do does did i you he she it we they my your his her this that what when where why how should will would can could have has not and or for with on at from about",
    "hu": "a az egy és hogy nem is van volt lesz mi ki mit miért hol mikor hogyan én te ő ez meg fel el már még csak vagy de ha mert vele nekem neked",
    "de": "der die das ein eine und ist nicht ich du er sie es wir ihr mit für von zu auf im in den dem des soll werde wird kann muss wie was wann wo warum mein meine dein",
    "fr": "le la les un une des et est ne pas je tu il elle nous vous ils que qui quoi quand où pourquoi comment dois peux vais mon ma mes de du au aux dans pour sur avec suis sont",
    "es": "el la los las un una unos y es no yo tú él ella nosotros que qué quién cuándo dónde por cómo debo puedo voy mi mis de del al en con para sobre soy son está",
    "pt": "o a os as um uma uns e é não eu tu ele ela nós que quem quando onde porquê como devo posso vou meu minha meus de do da dos das no na em com para sobre sou são está você também muito",
    "ro": "un o niște și este nu eu tu el ea noi voi ei ele ce cine când unde de ce cum trebuie pot voi meu mea mei în cu pentru pe sunt să acest această",
    "pl": "i w nie na to jest się z że do jak co kiedy gdzie dlaczego czy ja ty on ona my wy oni mój moja powinienem powinnam mam będzie",
}
_PAROLE_RU = set("и в не на что это как я ты он она мы вы мне мой стоит ли нужно можно почему когда где".split())
_PAROLE_UK = set("і в не на що це як я ти він вона ми ви мені мій чи варто потрібно можна чому коли де".split())

#: Lettere che una lingua ha e le altre (quasi) no, con il loro peso.
_LETTERE = {
    "hu": (("őű", 4.0), ("áéíóöúü", 0.5)),
    "de": (("ß", 4.0), ("äöü", 1.0)),
    "fr": (("œ", 4.0), ("êëîôûùàâè", 0.7)),
    "es": (("ñ¿¡", 4.0),),
    "pt": (("ãõ", 4.0), ("ç", 1.0)),
    "ro": (("ășțşţ", 4.0), ("âî", 1.0)),
    "pl": (("ąęłńśźż", 4.0), ("óć", 1.0)),
    "it": (("ìò", 0.7), ("àèù", 0.4)),
}

_INSIEMI = {codice: set(parole.split()) for codice, parole in _PAROLE.items()}

#: Quanto un'altra lingua deve superare quella dell'interfaccia per prenderne il posto: una parola comune in più.
_SCARTO = 2.0


def _punteggi_latino(testo: str) -> Dict[str, float]:
    return _indizi_latino(testo)[0]


def _indizi_latino(testo: str) -> tuple:
    """(punteggi, parole trovate) per lingua: 2 punti per parola comune, più il peso delle lettere tipiche."""
    minuscolo = testo.lower()
    parole = re.findall(r"[^\W\d_]+", minuscolo)
    punteggi: Dict[str, float] = {}
    trovate: Dict[str, int] = {}
    for codice in _INSIEMI:
        trovate[codice] = sum(1 for p in parole if p in _INSIEMI[codice])
        punti = 2.0 * trovate[codice]
        for lettere, peso in _LETTERE.get(codice, ()):
            punti += peso * sum(minuscolo.count(c) for c in lettere)
        punteggi[codice] = punti
    return punteggi, trovate


def rileva_lingua(testo: str, fallback: str = PREDEFINITA) -> str:
    """La lingua del testo, o `fallback` se non c'è indizio o c'è un pareggio."""
    fallback = lingua(fallback)
    testo = (testo or "").strip()
    if not testo:
        return fallback

    conteggi = {nome: len(rx.findall(testo)) for nome, rx in _SCRITTURE.items()}
    scrittura = max(conteggi, key=conteggi.get)
    if conteggi[scrittura] == 0:
        return fallback

    if scrittura == "hangul":
        return "ko"
    if scrittura == "devanagari":
        return "hi"
    if scrittura == "arabo":
        return "ar"
    if scrittura == "han":
        # Con il kana è giapponese, che non abbiamo: si tiene la lingua dell'interfaccia.
        return fallback if _KANA.search(testo) else "zh"
    if scrittura == "cirillico":
        parole = set(re.findall(r"[^\W\d_]+", testo.lower()))
        if _LETTERE_UCRAINE.search(testo) or len(parole & _PAROLE_UK) > len(parole & _PAROLE_RU):
            return "uk"
        return "ru"

    # Alfabeto latino: la lingua dell'interfaccia resta, salvo prove chiare. Un'altra lingua la sostituisce solo con
    # almeno una sua parola comune e un punteggio più alto di almeno `_SCARTO`: le sole lettere accentate non bastano
    # («Pioverà domani?» non è francese per una «à», e una «é» non fa ungherese una domanda italiana).
    punteggi, trovate = _indizi_latino(testo)
    base = punteggi.get(fallback, 0.0)
    candidate = [c for c in ORDINE if c in punteggi and c != fallback and trovate[c] > 0]
    if not candidate:
        return fallback
    migliore = max(punteggi[c] for c in candidate)
    if migliore < base + _SCARTO:
        return fallback
    return next(c for c in candidate if punteggi[c] == migliore)


#: Quanto deve essere lungo un messaggio per cambiare la lingua di una conversazione già avviata: tre parole, o sei
#: lettere in una scrittura che non separa le parole (cinese).
_PAROLE_PER_CAMBIARE = 3
_LETTERE_SENZA_SPAZI = 6


def lingua_del_messaggio(testo: str, attuale: str) -> str:
    """La lingua in cui rispondere a un messaggio di chi consulta, in una conversazione che finora era in `attuale`.

    Chi scrive in un'altra lingua riceve la risposta nella sua: è la lingua del messaggio che conta, non quella del
    profilo o della pagina (9/10/2026: persone che scrivevano in inglese ricevevano risposte in italiano, la lingua
    d'ufficio dell'account). Ma si cambia solo con prove chiare: un messaggio di almeno tre parole, riconosciuto con
    `rileva_lingua` (che già non si lascia ingannare da un accento). «ok», «sì», un nome, «domani?» lasciano `attuale`."""
    attuale = lingua(attuale)
    testo = (testo or "").strip()
    parole = re.findall(r"[^\W\d_]+", testo)
    senza_spazi = bool(_SCRITTURE["han"].search(testo))
    if len(parole) < _PAROLE_PER_CAMBIARE and not (senza_spazi and sum(map(len, parole)) >= _LETTERE_SENZA_SPAZI):
        return attuale
    return rileva_lingua(testo, fallback=attuale)
