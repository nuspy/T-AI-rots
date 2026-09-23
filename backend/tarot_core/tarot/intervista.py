"""L'intervista: capire il contesto senza chiedere la risposta.

**La regola che conta.** L'oracolo fa domande che chiariscono il quadro —
la situazione, i tempi, le persone, cosa è già successo, come si sente chi
consulta — ma **non chiede mai all'utente la risposta al quesito**, né una
previsione. A «il mio ragazzo mi ama?» non si risponde con «secondo te ti
ama?»: la previsione la danno le carte, non chi consulta.

La regola è difesa in tre punti, perché un prompt da solo non basta:

1. il prompt dell'intervista la dichiara, con esempi;
2. un controllo deterministico scarta le domande che ricalcano il quesito o
   che chiedono una previsione con le formule tipiche;
3. un modello di validazione, separato, giudica ogni domanda candidata.

Una domanda scartata si rigenera (fino a due volte); se il modello insiste, si
usa una domanda di contesto di riserva.
"""
from __future__ import annotations

import logging
import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

from ..llm.base import GenerationError
from .llm import genera_json, richiesta
from .testi import DOMANDE_DI_RISERVA, lingua

logger = logging.getLogger(__name__)

TENTATIVI_RIGENERAZIONE = 2

PROMPT_INTERVISTA = """# Compito: intervista

Sei l'oracolo di T-AI-rots, lettore esperto del Tarocco di Thoth. Prima di
disporre le carte conduci un breve colloquio per capire il contesto della
domanda di chi consulta.

Regole inviolabili:
- Fai UNA sola domanda per volta, breve, calda e rispettosa.
- Le domande servono a chiarire il CONTESTO: la situazione concreta, da quanto
  dura, le persone coinvolte e il loro ruolo, cosa è già successo, i tempi, lo
  stato d'animo, cosa chi consulta desidera o teme.
- NON chiedere MAI all'utente la risposta al suo quesito, nemmeno riformulata.
  Esempio: se il quesito è «il mio ragazzo mi ama?», NON chiedere «pensi che ti
  ami?», «senti che ti ama?», «secondo te prova qualcosa?».
- NON chiedere MAI previsioni o valutazioni sul futuro («come pensi che andrà?»,
  «credi che succederà?»): le previsioni le danno le carte, non chi consulta.
- Non ripetere domande già poste e non chiedere ciò che è già stato detto.
- Non chiedere dati sensibili superflui (indirizzi, nomi completi, dati sanitari
  dettagliati).
- Quando il quadro è sufficiente per una lettura sensata, oppure hai già fatto
  il numero massimo di domande, chiudi l'intervista.

Rispondi SOLO con un oggetto JSON:
{"completo": false, "domanda": "<la prossima domanda>"}
oppure, quando il quadro è sufficiente:
{"completo": true, "riassunto": "<il quadro emerso, 3-6 frasi in terza persona, senza anticipare alcuna previsione>"}
"""

PROMPT_VALIDAZIONE = """# Compito: validazione

Sei il controllore delle domande di un'intervista che precede una lettura dei
tarocchi. Ricevi il quesito di chi consulta e una domanda candidata che
l'oracolo vorrebbe porre.

La domanda NON è valida se:
1. chiede all'utente, direttamente o riformulata, la risposta al suo stesso
   quesito (es. quesito «il mio ragazzo mi ama?» → «secondo te ti ama?»,
   «senti il suo amore?», «credi che tenga a te?»);
2. chiede all'utente una previsione o una valutazione sul futuro («come
   pensi che finirà?», «credi che otterrai il lavoro?»);
3. non è una domanda, o contiene più domande insieme.

È valida se chiede contesto: fatti, tempi, persone, emozioni, desideri, cosa è
già successo.

Rispondi SOLO con JSON: {"valida": true|false, "motivo": "<breve>"}
"""

#: Le formule con cui si chiede a qualcuno di prevedere o di rispondersi da sé.
_FORMULE_PREVISIONE = re.compile(
    r"\b(pensi|credi|ritieni|senti|immagini|secondo te|a tuo parere|a tuo avviso|"
    r"do you think|do you believe|do you feel|in your opinion)\b"
    r".{0,60}\b(succeder|accadr|andr[aà]|finir|funzioner|torner|arriver|otterr|"
    r"ti am|ama\b|amer|vorr[aà]|lascer|cambier|riuscir|avverr|will|going to|loves? you)",
    re.IGNORECASE,
)

_PAROLE_VUOTE = {
    "il", "lo", "la", "i", "gli", "le", "un", "uno", "una", "di", "a", "da", "in",
    "con", "su", "per", "tra", "fra", "e", "o", "che", "mi", "ti", "si", "ci",
    "vi", "è", "sono", "mio", "mia", "miei", "mie", "tuo", "tua", "suo", "sua",
    "del", "della", "dei", "delle", "al", "alla", "non", "ma", "se", "come",
    "cosa", "quando", "the", "a", "an", "of", "to", "my", "your", "is", "are",
    "do", "does", "will", "me", "you", "and", "or",
}


def _parole(testo: str) -> set:
    testo = unicodedata.normalize("NFKD", testo.lower())
    testo = "".join(c for c in testo if not unicodedata.combining(c))
    return {p for p in re.findall(r"[a-z]+", testo) if p not in _PAROLE_VUOTE and len(p) > 2}


def ricalca_il_quesito(quesito: str, domanda: str, *, soglia: float = 0.6) -> bool:
    """Vero se la domanda ripete il quesito con altre parole.

    Misura quanta parte delle parole di contenuto del quesito ricompare nella
    domanda. Grezzo, ma cattura il caso peggiore — il quesito rigirato
    all'utente — senza chiamare nessun modello.
    """
    q = _parole(quesito)
    d = _parole(domanda)
    if not q or not d:
        return False
    return len(q & d) / len(q) >= soglia


def viola_le_regole(quesito: str, domanda: str) -> Optional[str]:
    """Il controllo deterministico. Restituisce il motivo, o `None`."""
    if not domanda.strip():
        return "domanda vuota"
    if domanda.count("?") > 1:
        return "più domande insieme"
    if _FORMULE_PREVISIONE.search(domanda):
        return "chiede una previsione o la risposta al quesito"
    if ricalca_il_quesito(quesito, domanda):
        return "ricalca il quesito"
    return None


@dataclass
class Passo:
    """L'esito di un turno d'intervista."""

    completo: bool
    domanda: Optional[str] = None
    riassunto: Optional[str] = None
    #: Quante domande candidate sono state scartate prima di questa.
    scartate: int = 0


def _trascrizione(turni: Sequence[Tuple[str, str]]) -> str:
    righe = []
    for ruolo, testo in turni:
        chi = "Oracolo" if ruolo == "oracolo" else "Chi consulta"
        righe.append(f"{chi}: {testo}")
    return "\n".join(righe) or "(nessun turno ancora)"


def _istruzione_lingua(lang: str) -> str:
    return "Scrivi in inglese." if lingua(lang) == "en" else "Scrivi in italiano."


async def prossimo_passo(
    *,
    provider_intervista,
    provider_validazione,
    quesito: str,
    stesa_nome: str,
    turni: Sequence[Tuple[str, str]],
    max_domande: int,
    lang: str = "it",
    profilo: str = "",
) -> Passo:
    """Decide la prossima domanda, o chiude l'intervista col riassunto."""
    poste = sum(1 for r, _ in turni if r == "oracolo")
    obbligo_chiusura = poste >= max_domande

    utente = (
        f"Quesito: {quesito}\n"
        f"Stesa scelta: {stesa_nome}\n"
        f"{profilo}"
        f"Domande già poste: {poste} (massimo {max_domande})\n\n"
        f"Colloquio finora:\n{_trascrizione(turni)}\n\n"
        + (
            "Hai raggiunto il numero massimo di domande: chiudi l'intervista con il riassunto.\n"
            if obbligo_chiusura else ""
        )
        + _istruzione_lingua(lang)
    )
    sistema = [PROMPT_INTERVISTA]

    scartate: List[str] = []
    for tentativo in range(TENTATIVI_RIGENERAZIONE + 1):
        extra = ""
        if scartate:
            extra = (
                "\n\nQueste domande sono state scartate perché violano le regole "
                "(chiedono la risposta al quesito o una previsione), non riproporle:\n- "
                + "\n- ".join(scartate)
            )
        try:
            dati = await genera_json(
                provider_intervista, richiesta(sistema, utente + extra, temperatura=0.6),
            )
        except GenerationError as exc:
            logger.warning("Intervista: il modello non ha risposto (%s)", exc)
            dati = {}

        if dati.get("completo") or obbligo_chiusura:
            riassunto = str(dati.get("riassunto") or "").strip()
            if not riassunto:
                riassunto = await riassumi(
                    provider_intervista, quesito=quesito, turni=turni, lang=lang,
                )
            return Passo(completo=True, riassunto=riassunto, scartate=len(scartate))

        domanda = str(dati.get("domanda") or "").strip()
        if not domanda:
            break

        motivo = viola_le_regole(quesito, domanda)
        if motivo is None:
            motivo = await _giudica(provider_validazione, quesito, domanda)
        if motivo is None:
            return Passo(completo=False, domanda=domanda, scartate=len(scartate))

        logger.info("Domanda scartata (%s): %s", motivo, domanda)
        scartate.append(domanda)

    return Passo(
        completo=False,
        domanda=domanda_di_riserva(turni, lang=lang),
        scartate=len(scartate),
    )


async def _giudica(provider, quesito: str, domanda: str) -> Optional[str]:
    """Il validatore LLM. Un validatore che non risponde non blocca: il
    controllo deterministico è già passato."""
    try:
        dati = await genera_json(provider, richiesta(
            [PROMPT_VALIDAZIONE],
            f"Quesito: {quesito}\nDomanda candidata: {domanda}",
            temperatura=0.0, max_tokens=200,
        ))
    except GenerationError as exc:
        logger.warning("Validatore non disponibile (%s): la domanda passa", exc)
        return None
    if dati.get("valida") is False:
        return str(dati.get("motivo") or "giudicata non valida")
    return None


def domanda_di_riserva(turni: Sequence[Tuple[str, str]], *, lang: str = "it") -> str:
    gia = {t for r, t in turni if r == "oracolo"}
    for d in DOMANDE_DI_RISERVA[lingua(lang)]:
        if d not in gia:
            return d
    return DOMANDE_DI_RISERVA[lingua(lang)][-1]


async def riassumi(
    provider, *, quesito: str, turni: Sequence[Tuple[str, str]], lang: str = "it",
) -> str:
    """Il quadro emerso, quando il modello ha chiuso senza riassumere."""
    try:
        dati = await genera_json(provider, richiesta(
            [PROMPT_INTERVISTA],
            f"Quesito: {quesito}\n\nColloquio:\n{_trascrizione(turni)}\n\n"
            f"L'intervista è conclusa: restituisci solo "
            f'{{"completo": true, "riassunto": "..."}}. {_istruzione_lingua(lang)}',
            temperatura=0.3,
        ))
        testo = str(dati.get("riassunto") or "").strip()
        if testo:
            return testo
    except GenerationError as exc:
        logger.warning("Riassunto dell'intervista non generato (%s)", exc)
    risposte = [t for r, t in turni if r == "utente"]
    return f"Quesito: {quesito}. " + " ".join(risposte)


def turni_da(righe: Sequence[Any]) -> List[Tuple[str, str]]:
    return [(r.ruolo, r.testo) for r in righe]


def profilo_da(dati: Dict[str, Any]) -> str:
    """Il profilo esoterico di chi consulta, se l'ha dato."""
    if not dati:
        return ""
    return "".join(f"{k}: {v}\n" for k, v in dati.items() if v)
