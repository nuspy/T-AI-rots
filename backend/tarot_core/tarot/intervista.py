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

Una domanda scartata si rigenera (fino a due volte). **Non esistono domande di
riserva**: se il modello non risponde, o insiste con domande vietate prima del
minimo, l'intervista fallisce con `IntervistaNonRiuscita` e il servizio lo dice,
invece di porre a tutti le stesse domande fisse.

**Quante domande.** Le decide il modello in base al quesito, fra un minimo (2) e
un massimo (6) che il codice fa rispettare: prima del minimo una chiusura viene
respinta, al massimo la chiusura è obbligatoria.
"""
from __future__ import annotations

import logging
import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

from ..llm.base import GenerationError
from .llm import genera_json, richiesta
from .lingue import istruzione_lingua

logger = logging.getLogger(__name__)

TENTATIVI_RIGENERAZIONE = 2


class IntervistaNonRiuscita(RuntimeError):
    """Il modello non ha prodotto una domanda utilizzabile.

    Non ha risposto, o ha insistito con domande vietate prima del minimo. Il
    chiamante lo dice a chi consulta: non c'è una domanda di riserva da porre
    al suo posto, perché sarebbe la stessa per tutti.
    """


PROMPT_INTERVISTA = """# Compito: intervista

Sei l'oracolo di T-AI-rots, lettore esperto del Tarocco di Thoth. Prima di
disporre le carte conduci un breve colloquio per capire il contesto della
domanda di chi consulta. Le tue domande servono a leggere meglio le carte, non
a compilare un modulo.

Quante domande: da 2 a 6 in totale, e le decidi TU in base al quesito. Un
quesito circoscritto e chiaro ne richiede poche; uno vago, che coinvolge più
persone o più ambiti della vita, ne richiede di più. Non chiudere prima della
seconda domanda, non superare la sesta, e non allungare il colloquio quando il
quadro è già sufficiente per una lettura sensata.

Come devono essere le domande:
- ATTINENTI: nascono da ciò che chi consulta ha scritto (il quesito e le
  risposte già date) e ne riprendono gli elementi concreti — le persone, la
  situazione, i tempi. Sono vietate le domande generiche, valide per qualunque
  quesito.
- UTILI: chiedi solo ciò che cambierebbe davvero la lettura delle carte: la
  situazione concreta, da quanto dura, chi è coinvolto e che ruolo ha, cosa è
  già successo o è già stato tentato, i tempi e le decisioni in arrivo, cosa chi
  consulta desidera o teme. Guarda le posizioni della stesa scelta (per esempio
  passato, ostacolo, esito) e raccogli il contesto che serve a leggerle.
- COERENTI col colloquio: ogni domanda si aggancia alle risposte precedenti e
  le approfondisce; non ricomincia da capo.
- UNA sola domanda per volta, in una sola frase, breve, calda e rispettosa.

Regole inviolabili:
- NON chiedere MAI all'utente la risposta al suo quesito, nemmeno riformulata.
  Esempio: se il quesito è «il mio ragazzo mi ama?», NON chiedere «pensi che ti
  ami?», «senti che ti ama?», «secondo te prova qualcosa?».
- NON chiedere MAI previsioni o valutazioni sul futuro («come pensi che andrà?»,
  «credi che succederà?»): le previsioni le danno le carte, non chi consulta.
- Non ripetere domande già poste e non chiedere ciò che è già stato detto.
- Non chiedere dati sensibili superflui (indirizzi, nomi completi, dati sanitari
  dettagliati).

Rispondi SOLO con un oggetto JSON:
{"completo": false, "domanda": "<la prossima domanda>"}
oppure, quando il quadro è sufficiente e hai già fatto almeno 2 domande:
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

PROMPT_INTERVISTA_RELAZIONE = """# Regole aggiuntive: compatibilità e coppia

Questa lettura riguarda chi consulta e un'altra persona (il suo nome, se c'è, sta
nel profilo). I dati delle due persone — nomi, generi, date di nascita, segni —
sono già noti: non chiederli.

Le domande servono a capire la relazione e chiedono ciò che chi consulta sa con
certezza:
- FATTI OSSERVABILI: come vi siete conosciuti, da quanto tempo, come e quanto vi
  vedete, cosa è successo di recente, cosa è già stato detto o tentato, quali
  decisioni sono in arrivo;
- IL VISSUTO DI CHI CONSULTA: cosa desidera, cosa teme, come sta nella relazione,
  cosa gli piace e cosa gli manca.

Non chiedere MAI:
- cosa pensa, prova, vuole o nasconde l'altra persona, né se «ti ama» o «tiene a
  te»: chi consulta può raccontare ciò che l'altra persona fa o dice, non il suo
  mondo interiore. Le carte danno la tendenza;
- di valutare la compatibilità o il futuro della coppia;
- dati sensibili superflui: orientamento sessuale, salute, dettagli intimi,
  cognomi o dati di altre persone;
- niente presupposti: non dare per scontati il tipo di relazione, il genere o
  l'orientamento di nessuno.

Se chi consulta accenna a violenza, paura o controllo da parte dell'altra
persona, non indagare i dettagli: rispondi con ascolto e chiedi solo, con
delicatezza, come sta e se si sente al sicuro. Non suggerire di «lavorare sulla
coppia».
"""

PROMPT_VALIDAZIONE_RELAZIONE = """# Regole aggiuntive: compatibilità e coppia

Per una lettura di compatibilità o di coppia la domanda NON è valida anche se:
4. chiede all'utente cosa pensa, prova, vuole o nasconde l'altra persona, o se
   «lo/la ama», come risposta o come previsione (chi consulta può raccontare ciò
   che l'altra persona fa o dice, non il suo mondo interiore);
5. chiede dati sensibili superflui: orientamento sessuale, salute, dettagli
   intimi, cognomi o dati di altre persone.
"""

#: Le formule con cui si chiede a qualcuno di prevedere o di rispondersi da sé.
_FORMULE_PREVISIONE = re.compile(
    r"\b(pensi|credi|ritieni|senti|immagini|secondo te|a tuo parere|a tuo avviso|"
    r"do you think|do you believe|do you feel|in your opinion)\b"
    r".{0,60}\b(succeder|accadr|andr[aà]|finir|funzioner|torner|arriver|otterr|"
    r"ti am|ama\b|amer|vorr[aà]|lascer|cambier|riuscir|avverr|will|going to|loves? you)",
    re.IGNORECASE,
)

#: Nelle letture di relazione: le domande che chiedono all'utente cosa pensa o prova
#: l'altra persona. Descrivere ciò che fa («come si comporta?») va bene; il suo
#: mondo interiore («cosa pensa?», «cosa prova?») no: lo dicono le carte, come tendenza.
_TERZO = r"(lui|lei|l'altra persona|il tuo partner|la tua partner|il partner|la partner|partner|him|her|them)"
_FORMULE_TERZO = re.compile(
    r"\b(cosa|che cosa|quanto|come)\b.{0,25}\b(pensa|prova|sente|vuole|desidera|nasconde|crede|considera|ama|tiene)\b.{0,40}\b" + _TERZO
    + r"|\b(secondo te|a tuo avviso|pensi|credi|ritieni|senti)\b.{0,60}\b" + _TERZO + r"\b.{0,50}\b(ti ama|ti vuole|prov|senta|pens|voglia|tenga|innamorat|desider)"
    + r"|\b(what|how much)\b.{0,20}\b(does|do|is)\b.{0,25}\b(he|she|they|your partner|the other person)\b.{0,25}\b(think|feel|want|hide|believe)"
    + r"|\bdo you think\b.{0,60}\b(he|she|they|your partner|the other person)\b",
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
    return {p for p in re.findall(r"\w+", testo) if p not in _PAROLE_VUOTE and len(p) > 2}


def ricalca_il_quesito(
    quesito: str, domanda: str, *, soglia: float = 0.6, neutre: Sequence[str] = (),
) -> bool:
    """Vero se la domanda ripete il quesito con altre parole.

    Misura quanta parte delle parole di contenuto del quesito ricompare nella
    domanda. Grezzo, ma cattura il caso peggiore — il quesito rigirato
    all'utente — senza chiamare nessun modello.

    `neutre` sono parole che non contano come ripetizione: nelle letture di
    relazione il quesito è spesso «Compatibilità con Marco», e una domanda
    naturale come «Da quanto conoscete Marco?» ne riprenderebbe più della soglia
    solo per il nome e il tipo di lettura.
    """
    q = _parole(quesito) - _parole(" ".join(neutre))
    d = _parole(domanda)
    if not q or not d:
        return False
    return len(q & d) / len(q) >= soglia


def viola_le_regole(
    quesito: str, domanda: str, *, categoria: str = "standard", neutre: Sequence[str] = (),
) -> Optional[str]:
    """Il controllo deterministico. Restituisce il motivo, o `None`."""
    if not domanda.strip():
        return "domanda vuota"
    if domanda.count("?") > 1:
        return "più domande insieme"
    if _FORMULE_PREVISIONE.search(domanda):
        return "chiede una previsione o la risposta al quesito"
    if categoria != "standard" and _FORMULE_TERZO.search(domanda):
        return "chiede cosa pensa o prova l'altra persona"
    if ricalca_il_quesito(quesito, domanda, neutre=neutre):
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


def trascrizione(turni: Sequence[Tuple[str, str]]) -> str:
    righe = []
    for ruolo, testo in turni:
        chi = "Oracolo" if ruolo == "oracolo" else "Chi consulta"
        righe.append(f"{chi}: {testo}")
    return "\n".join(righe) or "(nessun turno ancora)"


async def prossimo_passo(
    *,
    provider_intervista,
    provider_validazione,
    quesito: str,
    stesa_nome: str,
    turni: Sequence[Tuple[str, str]],
    max_domande: int,
    min_domande: int = 2,
    stesa_descrizione: str = "",
    lang: str = "it",
    profilo: str = "",
    categoria: str = "standard",
    nota: str = "",
    parole_neutre: Sequence[str] = (),
) -> Passo:
    """Decide la prossima domanda, o chiude l'intervista col riassunto.

    Per le letture di compatibilità e di coppia (`categoria`) il modello riceve
    anche le regole sulle relazioni; `nota` è l'avvertenza della stesa scelta, e
    `parole_neutre` le parole (il nome del partner) che non contano come
    ripetizione del quesito.

    Le domande sono fra `min_domande` e `max_domande`: quante ne servano lo
    decide il modello. Prima del minimo una chiusura viene respinta; al
    massimo la chiusura è obbligatoria.
    """
    poste = sum(1 for r, _ in turni if r == "oracolo")
    obbligo_chiusura = poste >= max_domande
    prima_del_minimo = poste < min_domande

    utente = (
        f"Quesito: {quesito}\n"
        f"Stesa scelta: {stesa_nome}\n"
        + (f"{stesa_descrizione}\n" if stesa_descrizione else "")
        + f"{profilo}"
        + (f"Nota sulla stesa: {nota}\n" if nota else "")
        + f"Domande già poste: {poste} (minimo {min_domande}, massimo {max_domande})\n\n"
        f"Colloquio finora:\n{trascrizione(turni)}\n\n"
        + (
            "Hai raggiunto il numero massimo di domande: chiudi l'intervista con il riassunto.\n"
            if obbligo_chiusura else ""
        )
        + (
            f"Hai fatto {poste} domande: devi farne ancora almeno {min_domande - poste} "
            "prima di chiudere. NON chiudere l'intervista.\n"
            if prima_del_minimo else ""
        )
        + istruzione_lingua(lang)
    )
    sistema = [PROMPT_INTERVISTA]
    if categoria != "standard":
        sistema.append(PROMPT_INTERVISTA_RELAZIONE)

    scartate: List[str] = []
    for _tentativo in range(TENTATIVI_RIGENERAZIONE + 1):
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
            if obbligo_chiusura:
                # Il colloquio è finito: il riassunto ripiega sulle risposte
                # di chi consulta, che sono sue e non fisse.
                return Passo(
                    completo=True, scartate=len(scartate),
                    riassunto=await riassumi(
                        provider_intervista, quesito=quesito, turni=turni, lang=lang, categoria=categoria,
                    ),
                )
            raise IntervistaNonRiuscita(f"il modello non ha risposto: {exc}") from exc

        if obbligo_chiusura or (dati.get("completo") and not prima_del_minimo):
            riassunto = str(dati.get("riassunto") or "").strip()
            if not riassunto:
                riassunto = await riassumi(
                    provider_intervista, quesito=quesito, turni=turni, lang=lang, categoria=categoria,
                )
            return Passo(completo=True, riassunto=riassunto, scartate=len(scartate))

        domanda = str(dati.get("domanda") or "").strip()
        if not domanda:
            # Ha chiuso troppo presto o non ha scritto nulla: si richiede.
            continue

        motivo = viola_le_regole(quesito, domanda, categoria=categoria, neutre=parole_neutre)
        if motivo is None:
            motivo = await _giudica(provider_validazione, quesito, domanda, categoria)
        if motivo is None:
            return Passo(completo=False, domanda=domanda, scartate=len(scartate))

        logger.info("Domanda scartata (%s): %s", motivo, domanda)
        scartate.append(domanda)

    # Nessuna domanda utilizzabile. Dopo il minimo si può chiudere col quadro
    # che c'è; prima no: servirebbe una domanda fissa, e non ce ne sono.
    if not prima_del_minimo:
        return Passo(
            completo=True, scartate=len(scartate),
            riassunto=await riassumi(
                provider_intervista, quesito=quesito, turni=turni, lang=lang, categoria=categoria,
            ),
        )
    raise IntervistaNonRiuscita("il modello non ha formulato una domanda valida")


async def _giudica(provider, quesito: str, domanda: str, categoria: str = "standard") -> Optional[str]:
    """Il validatore LLM. Un validatore che non risponde non blocca: il
    controllo deterministico è già passato."""
    sistema = [PROMPT_VALIDAZIONE]
    if categoria != "standard":
        sistema.append(PROMPT_VALIDAZIONE_RELAZIONE)
    try:
        dati = await genera_json(provider, richiesta(
            sistema,
            f"Quesito: {quesito}\nDomanda candidata: {domanda}",
            temperatura=0.0, max_tokens=200,
        ))
    except GenerationError as exc:
        logger.warning("Validatore non disponibile (%s): la domanda passa", exc)
        return None
    if dati.get("valida") is False:
        return str(dati.get("motivo") or "giudicata non valida")
    return None


async def riassumi(
    provider, *, quesito: str, turni: Sequence[Tuple[str, str]], lang: str = "it",
    categoria: str = "standard",
) -> str:
    """Il quadro emerso, quando il modello ha chiuso senza riassumere."""
    try:
        dati = await genera_json(provider, richiesta(
            [PROMPT_INTERVISTA] + ([PROMPT_INTERVISTA_RELAZIONE] if categoria != "standard" else []),
            f"Quesito: {quesito}\n\nColloquio:\n{trascrizione(turni)}\n\n"
            f"L'intervista è conclusa: restituisci solo "
            f'{{"completo": true, "riassunto": "..."}}. {istruzione_lingua(lang)}',
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
