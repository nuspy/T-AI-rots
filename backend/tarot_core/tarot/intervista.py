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
3. un modello di validazione, separato, giudica le domande candidate: tutte, solo quelle che una regola
   deterministica leggera trova dubbie (`sospetta`, il modo predefinito) o nessuna, secondo la console.

Una domanda scartata si rigenera (fino a due volte). **Non esistono domande di
riserva**: se il modello non risponde, o insiste con domande vietate prima del
minimo, l'intervista fallisce con `IntervistaNonRiuscita` e il servizio lo dice,
invece di porre a tutti le stesse domande fisse.

**Quante domande.** Le decide il modello in base al quesito, fra un minimo e un
massimo che si scelgono dalla console (2 e 6 se nessuno li ha cambiati) e che il
codice fa rispettare: prima del minimo una chiusura viene respinta, al massimo la
chiusura è obbligatoria. Dopo il minimo ogni domanda è *facoltativa*: il sito
chiede a chi consulta se vuole aggiungere altro o passare alle carte.

**Mai la stessa domanda due volte.** Il controllo deterministico scarta anche le
domande che ripetono, o riformulano da vicino, una domanda già posta.
"""
from __future__ import annotations

import logging
import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

from ..llm.base import GenerationError
from .conoscenza import speciale
from .llm import genera_json, richiesta
from .lingue import istruzione_lingua
from .memoria_retrieval import MemoriaRilevante, formatta_memorie

logger = logging.getLogger(__name__)

TENTATIVI_RIGENERAZIONE = 2


class IntervistaNonRiuscita(RuntimeError):
    """Il modello non ha prodotto una domanda utilizzabile.

    Non ha risposto, o ha insistito con domande vietate prima del minimo. Il
    chiamante lo dice a chi consulta: non c'è una domanda di riserva da porre
    al suo posto, perché sarebbe la stessa per tutti.
    """


PROMPT_INTERVISTA = """# Compito: intervista

Sei l'oracolo di TAROTS chat, lettore esperto del Tarocco di Thoth. Prima di
disporre le carte conduci un breve colloquio per capire il contesto della
domanda di chi consulta. Le tue domande servono a leggere meglio le carte, non
a compilare un modulo.

Quante domande: fra il minimo e il massimo indicati nel messaggio, e le decidi TU
in base al quesito. Un quesito circoscritto e chiaro ne richiede poche; uno vago,
che coinvolge più persone o più ambiti della vita, ne richiede di più. Non chiudere
prima del minimo, non superare il massimo, e non allungare il colloquio quando il
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
- MAI ripetere una domanda già posta, nemmeno con altre parole, e mai chiedere
  ciò che è già stato detto: ogni domanda nuova esplora un aspetto diverso.
- Non chiedere dati sensibili superflui (indirizzi, nomi completi, dati sanitari
  dettagliati).

Se il messaggio contiene una sezione «Cose già note su questa persona»:
- Una memoria STABILE è un fatto acquisito: NON chiederne conferma né un
  eventuale cambiamento, nemmeno in negativo (se sai che gli manca una gamba,
  non chiedere né se ha handicap fisici né se "gli è ricresciuta").
- Una memoria VARIABILE puoi usarla per chiedere se la situazione si è
  evoluta rispetto a quanto già noto, invece di richiedere da capo il
  contesto che già hai.

Rispondi SOLO con un oggetto JSON:
{"completo": false, "domanda": "<la prossima domanda>"}
oppure, quando il quadro è sufficiente e hai già fatto almeno il minimo di domande:
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

PROMPT_INTERVISTA_LAVORO = """# Regole aggiuntive: lavoro e affari

Questa lettura riguarda il lavoro, la carriera o un'attività di chi consulta (un posto, un
colloquio, una trattativa, un progetto, un'impresa da avviare). Le domande raccolgono il
contesto professionale che serve a leggere le carte:
- LA SITUAZIONE CONCRETA: il ruolo o il progetto, da quanto dura, in che fase è;
- LE PERSONE: chi è coinvolto (responsabili, colleghi, soci, clienti, controparti) e che
  ruolo ha, raccontato attraverso ciò che fa o dice, non ciò che pensa;
- I TEMPI E LE DECISIONI: scadenze, colloqui, offerte, scelte in arrivo;
- IL VISSUTO DI CHI CONSULTA: che cosa desidera, che cosa teme, che cosa ha già tentato.

Non chiedere:
- dati riservati o superflui: nomi di aziende o di persone, cifre esatte di stipendi,
  fatturati o contratti, documenti interni;
- che cosa pensano o decideranno un responsabile, un selezionatore o una controparte: le
  carte danno la tendenza.
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


def ripete_una_domanda(domanda: str, precedenti: Sequence[str], *, soglia: float = 0.55) -> bool:
    """Vero se la domanda ripete, o riformula da vicino, una di quelle già poste.

    Confronta le parole di contenuto: quanta parte della domanda più corta ricompare nell'altra. Grezzo come
    `ricalca_il_quesito`, ma basta per i casi che si vedono davvero (la stessa domanda con due parole cambiate)."""
    d = _parole(domanda)
    if not d:
        return False
    for altra in precedenti:
        p = _parole(altra)
        if not p:
            continue
        if len(d & p) / min(len(d), len(p)) >= soglia:
            return True
    return False


def viola_le_regole(
    quesito: str, domanda: str, *, categoria: str = "standard", neutre: Sequence[str] = (),
    precedenti: Sequence[str] = (),
) -> Optional[str]:
    """Il controllo deterministico. Restituisce il motivo, o `None`."""
    if not domanda.strip():
        return "domanda vuota"
    if domanda.count("?") > 1:
        return "più domande insieme"
    if _FORMULE_PREVISIONE.search(domanda):
        return "chiede una previsione o la risposta al quesito"
    if speciale(categoria) and _FORMULE_TERZO.search(domanda):
        return "chiede cosa pensa o prova l'altra persona"
    if ricalca_il_quesito(quesito, domanda, neutre=neutre):
        return "ricalca il quesito"
    if ripete_una_domanda(domanda, precedenti):
        return "ripete una domanda già posta"
    return None


#: I modi del validatore LLM (impostazione della console, `ImpostazioniIntervista.validatore_domande`).
VALIDATORE_DUBBI, VALIDATORE_SPENTO, VALIDATORE_ACCESO = "dubbi", "spento", "acceso"

#: Le lingue per cui le regole del sospetto hanno le parole: per le altre ogni domanda è «dubbia» e va al validatore.
LINGUE_CON_REGOLE = ("it", "en")

#: Sospetto 1 — parole del campo «chiedere la risposta»: si chiede a chi consulta un'opinione, una convinzione o una
#: sensazione su come stanno le cose. Più larga di `_FORMULE_PREVISIONE`, che scarta solo se c'è anche un verbo al
#: futuro: qui basta la formula, perché l'ultima parola la dà il validatore.
_SOSPETTO_OPINIONE = re.compile(
    r"\b(pensi|credi|ritieni|secondo te|a tuo (parere|avviso)|immagini|ti aspetti|prevedi|sei sicur[oa]|"
    r"senti che|hai la sensazione|speri che|sei convint[oa]|"
    r"do you think|do you believe|do you feel|do you expect|in your opinion|would you say|how likely|are you sure)\b",
    re.IGNORECASE,
)

#: Sospetto 2 — il futuro o l'esito: la domanda parla di come andrà, non di com'è.
_SOSPETTO_FUTURO = re.compile(
    r"\b(succed\w*|accadr\w*|andr[aà]|finir[aà]|funzioner\w*|riuscir\w*|otterr\w*|tornerà|cambierà|avverr\w*|"
    r"futuro|esito|will|going to|future|outcome)\b",
    re.IGNORECASE,
)

#: Sospetto 3 (solo letture di coppia e compatibilità) — il mondo interiore dell'altra persona o un dato sensibile.
_SOSPETTO_RELAZIONE = re.compile(
    r"\b(pensa|prova|sente|vuole|ama|desidera|nasconde|innamorat\w*|orientament\w*|sessual\w*|salute|malatti\w*|"
    r"cognome|think|feels?|wants?|loves?|hides?|orientation|sexual\w*|health|surname)\b",
    re.IGNORECASE,
)

#: Sospetto 4 — la domanda somiglia al quesito, anche sotto la soglia che la scarta (`ricalca_il_quesito`, 0,6).
SOGLIA_SOSPETTO_QUESITO = 0.35


def sospetta(
    quesito: str, domanda: str, *, categoria: str = "standard", neutre: Sequence[str] = (), lang: str = "it",
) -> Optional[str]:
    """La regola deterministica leggera del modo «solo casi dubbi»: il motivo del sospetto, o `None`.

    Gira **dopo** `viola_le_regole` (che scarta senza appello) e decide solo se la domanda merita il validatore LLM. Una
    domanda è dubbia se:

    1. usa una formula d'opinione rivolta a chi consulta («pensi», «secondo te», «do you think»…);
    2. parla del futuro o dell'esito («succederà», «andrà», «futuro», «will»…);
    3. nelle letture di coppia e compatibilità, nomina il mondo interiore dell'altra persona («pensa», «prova», «ama»)
       o un dato sensibile («salute», «orientamento», «cognome»);
    4. riprende più di un terzo delle parole del quesito (soglia 0,35, contro lo 0,6 che scarta);
    5. è in una lingua per cui queste parole non ci sono (`LINGUE_CON_REGOLE`): lì ogni domanda va al validatore.

    Un falso sospetto costa la chiamata di prima; un sospetto mancato lascia passare una domanda che il prompt
    dell'intervista e i controlli deterministici non hanno fermato — per questo le formule sono larghe.
    """
    if (lang or "it")[:2] not in LINGUE_CON_REGOLE:
        return "lingua senza regole del sospetto"
    if _SOSPETTO_OPINIONE.search(domanda):
        return "chiede un'opinione a chi consulta"
    if _SOSPETTO_FUTURO.search(domanda):
        return "parla del futuro o dell'esito"
    if speciale(categoria) and _SOSPETTO_RELAZIONE.search(domanda):
        return "tocca il mondo interiore dell'altra persona o un dato sensibile"
    if ricalca_il_quesito(quesito, domanda, soglia=SOGLIA_SOSPETTO_QUESITO, neutre=neutre):
        return "somiglia al quesito"
    return None


@dataclass
class Passo:
    """L'esito di un turno d'intervista."""

    completo: bool
    domanda: Optional[str] = None
    riassunto: Optional[str] = None
    #: Quante domande candidate sono state scartate prima di questa.
    scartate: int = 0
    #: Il minimo di domande è già raggiunto: chi consulta può fermarsi qui e passare alle carte.
    facoltativa: bool = False


def sistema_intervista(categoria: str = "standard") -> List[str]:
    """Il prompt di sistema dell'intervista: quello di sempre e, per le letture di relazione o di
    lavoro, le regole aggiuntive della categoria. La standard resta com'era."""
    sistema = [PROMPT_INTERVISTA]
    if speciale(categoria):
        sistema.append(PROMPT_INTERVISTA_RELAZIONE)
    elif categoria == "lavoro":
        sistema.append(PROMPT_INTERVISTA_LAVORO)
    return sistema


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
    memorie: Sequence[MemoriaRilevante] = (),
    validatore: str = VALIDATORE_ACCESO,
) -> Passo:
    """Decide la prossima domanda, o chiude l'intervista col riassunto.

    Per le letture di compatibilità e di coppia (`categoria`) il modello riceve
    anche le regole sulle relazioni, per quelle di lavoro le regole sul contesto
    professionale; `nota` è l'avvertenza della stesa scelta, e
    `parole_neutre` le parole (il nome del partner) che non contano come
    ripetizione del quesito.

    `memorie` (v6, Fase C) è lo stesso elenco per tutta l'intervista, recuperato
    una sola volta all'apertura della lettura: non si ricalcola a ogni domanda,
    altrimenti una memoria scritta da un'altra lettura in corso cambierebbe le
    regole a metà colloquio.

    Le domande sono fra `min_domande` e `max_domande`: quante ne servano lo
    decide il modello. Prima del minimo una chiusura viene respinta; al
    massimo la chiusura è obbligatoria.

    `validatore` è il modo del controllo LLM delle domande (impostazione della console): `acceso` giudica ogni
    candidata che supera i controlli deterministici, `dubbi` solo quelle che `sospetta()` segnala, `spento` nessuna.
    I controlli deterministici (`viola_le_regole`) valgono sempre, in tutti e tre i modi.
    """
    poste = sum(1 for r, _ in turni if r == "oracolo")
    precedenti = [t for r, t in turni if r == "oracolo"]
    obbligo_chiusura = poste >= max_domande
    prima_del_minimo = poste < min_domande

    blocco_memorie = formatta_memorie(memorie)
    utente = (
        f"Quesito: {quesito}\n"
        f"Stesa scelta: {stesa_nome}\n"
        + (f"{stesa_descrizione}\n" if stesa_descrizione else "")
        + f"{profilo}"
        + (f"Nota sulla stesa: {nota}\n" if nota else "")
        + (f"Cose già note su questa persona:\n{blocco_memorie}\n" if blocco_memorie else "")
        + "\n"
        # Le domande già fatte stanno una volta sola, dentro il colloquio; il contatore sta dopo, così fra un turno e
        # il successivo il messaggio resta identico fino all'ultima risposta (prefisso utile alla cache del fornitore).
        + (
            "Colloquio finora (le domande dell'oracolo sono già fatte: NON ripeterle e non riformularle; "
            "esplora un aspetto diverso):\n"
            if precedenti else "Colloquio finora:\n"
        )
        + f"{trascrizione(turni)}\n\n"
        + f"Domande già poste: {poste} (minimo {min_domande}, massimo {max_domande})\n"
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
    sistema = sistema_intervista(categoria)

    scartate: List[str] = []
    motivi: List[str] = []
    for _tentativo in range(TENTATIVI_RIGENERAZIONE + 1):
        extra = ""
        if scartate:
            extra = (
                "\n\nQueste domande sono state scartate perché violano le regole (il motivo è fra parentesi), "
                "non riproporle e non riformularle:\n- "
                + "\n- ".join(f"{d} ({m})" for d, m in zip(scartate, motivi))
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

        motivo = viola_le_regole(
            quesito, domanda, categoria=categoria, neutre=parole_neutre, precedenti=precedenti,
        )
        if motivo is None and _da_validare(
            validatore, quesito, domanda, categoria=categoria, neutre=parole_neutre, lang=lang,
        ):
            motivo = await _giudica(provider_validazione, quesito, domanda, categoria)
        if motivo is None:
            return Passo(
                completo=False, domanda=domanda, scartate=len(scartate), facoltativa=poste >= min_domande,
            )

        logger.info("Domanda scartata (%s): %s", motivo, domanda)
        scartate.append(domanda)
        motivi.append(motivo)

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


def _da_validare(
    modo: str, quesito: str, domanda: str, *, categoria: str, neutre: Sequence[str], lang: str,
) -> bool:
    """Se la domanda va al validatore LLM, secondo il modo scelto in console. Un modo sconosciuto vale «acceso»: nel
    dubbio si controlla."""
    if modo == VALIDATORE_SPENTO:
        return False
    if modo == VALIDATORE_DUBBI:
        motivo = sospetta(quesito, domanda, categoria=categoria, neutre=neutre, lang=lang)
        if motivo is None:
            logger.debug("Validatore saltato (nessun sospetto): %s", domanda)
            return False
        logger.debug("Domanda dubbia (%s): al validatore", motivo)
    return True


async def _giudica(provider, quesito: str, domanda: str, categoria: str = "standard") -> Optional[str]:
    """Il validatore LLM. Un validatore che non risponde non blocca: il
    controllo deterministico è già passato."""
    sistema = [PROMPT_VALIDAZIONE]
    if speciale(categoria):
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
            sistema_intervista(categoria),
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
