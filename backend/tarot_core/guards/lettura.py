"""Il guardrail della lettura: prima delle carte, e prima del responso.

**Due momenti, due strumenti.**

- *Prima*: un filtro deterministico sulle parole di chi consulta. Se la
  domanda o una risposta dell'intervista parlano di farsi del male, la lettura
  si ferma e si risponde con un aiuto concreto. Nessun modello decide qui:
  in quel caso l'errore più costoso è non accorgersene, e un'espressione
  regolare non ha giornate storte.
- *Dopo*: il responso finale passa dal giudice (compito `GIUDIZIO`), che lo
  misura contro le rubriche `## Verifica` dei guardrail in `data/guards/`.
  L'esito è `ok`, `riscrivi` o `blocca`. Con `riscrivi` il responso si
  rigenera con i vincoli, una volta; se non basta, si blocca. Nel modo «solo
  casi dubbi» (il predefinito della console) il giudice parte solo se un
  controllo deterministico (`da_guardare`) trova qualcosa da guardare.

Il giudice che non risponde **non** lascia passare il responso senza
controllo: si applica il filtro deterministico anche all'uscita, e se quello
tace il responso passa marcato come non verificato. È un compromesso
dichiarato: bloccare ogni lettura quando il giudice è giù renderebbe il
servizio inutilizzabile, ma nessuna frase di crisi esce senza essere vista.
"""
from __future__ import annotations

import logging
import re
import unicodedata
from dataclasses import dataclass, field
from typing import List, Optional

from ..llm.base import GenerationError
from ..tarot.llm import genera_json, richiesta
from .policy import RegistroGuardrail

logger = logging.getLogger(__name__)

#: Segnali di crisi nelle parole di chi consulta. Volutamente larghi: un
#: falso positivo costa una lettura rimandata con un messaggio gentile, un
#: falso negativo può costare molto di più.
_CRISI = re.compile(
    r"\b("
    # italiano
    r"suicid\w*|uccidermi|ammazzarmi|togliermi la vita|farla finita|"
    r"non voglio (piu|più) vivere|voglio morire|farmi del male|tagliarmi|"
    r"autolesion\w*|"
    # inglese
    r"kill myself|suicide|end my life|want to die|hurt myself|self[- ]harm|"
    # ungherese
    r"öngyilkos\w*|megölöm magam|meg akarok halni|véget vetek az életemnek|bántani magam|"
    # tedesco
    r"selbstmord\w*|suizid\w*|mich umbringen|mich töten|nicht mehr leben|sterben will|"
    # francese
    r"me tuer|en finir avec la vie|mettre fin à mes jours|envie de mourir|"
    # spagnolo e portoghese
    r"quitarme la vida|matarme|quiero morir|acabar con mi vida|suicíd\w*|me matar|quero morrer|tirar a minha vida|"
    # rumeno
    r"sinucid\w*|să mă omor|vreau să mor|"
    # polacco
    r"samobójstw\w*|zabić się|odebrać sobie życie|chcę umrzeć|"
    # russo e ucraino
    r"суицид\w*|самоубийств\w*|покончить с собой|хочу умереть|"
    r"самогубств\w*|суїцид\w*|покінчити з собою|хочу померти"
    r")\b",
    re.IGNORECASE,
)

#: Le lingue che non separano le parole con gli spazi (o le cui parole il `\b`
#: non isola): cinese, coreano, hindi, arabo. Nessun confine di parola.
_CRISI_SENZA_CONFINI = re.compile(
    r"自杀|想死|不想活|结束生命|结束自己的生命|"
    r"자살|죽고\s?싶|"
    r"आत्महत्या|मरना चाह|"
    r"انتحار|أريد أن أموت|اقتل نفسي|أقتل نفسي"
)

#: Nell'uscita: formule che nessun responso deve contenere.
_USCITA_PROIBITA = re.compile(
    r"\b("
    r"morirai|morir[aà] presto|la tua morte|sei destinat[oa] a (soffrire|morire|restare sol[oa])|"
    r"smetti (di prendere|la terapia|le cure)|interrompi (la terapia|le cure)|"
    r"investi tutto|punta tutto|"
    r"you will die|stop (taking )?your medication"
    r")\b",
    re.IGNORECASE,
)


def _normalizza(testo: str) -> str:
    return unicodedata.normalize("NFKC", testo or "")


def segnale_di_crisi(*testi: str) -> bool:
    return any(
        _CRISI.search(n) or _CRISI_SENZA_CONFINI.search(n)
        for n in (_normalizza(t) for t in testi if t)
    )


def uscita_proibita(testo: str) -> Optional[str]:
    trovato = _USCITA_PROIBITA.search(_normalizza(testo))
    return trovato.group(0) if trovato else None


PROMPT_GIUDIZIO = """# Compito: giudizio

Sei il guardiano della sicurezza di una piattaforma di letture dei tarocchi.
Ricevi il responso finale di una lettura e le regole di verifica. Non giudichi
la qualità esoterica: giudichi solo se il responso può essere pericoloso o
scorretto verso chi lo legge.

Esiti:
- "ok": nessuna violazione;
- "riscrivi": violazioni correggibili (una frase fatalista, un consiglio
  finanziario, una certezza sui sentimenti di un terzo…);
- "blocca": il responso incoraggia l'autolesionismo o la violenza, o risponde a
  una crisi senza indicare aiuto, o è irrecuperabile.

Rispondi SOLO con JSON:
{"esito": "ok"|"riscrivi"|"blocca", "violazioni": [{"regola": "<slug>", "motivo": "<breve>", "estratto": "<frase>"}]}
"""


#: I modi della guardia LLM (impostazione della console, `ImpostazioniIntervista.guardia_responso`).
GUARDIA_DUBBI, GUARDIA_SPENTA, GUARDIA_ACCESA = "dubbi", "spento", "acceso"

#: Le lingue per cui il controllo deterministico ha le parole: per le altre la guardia LLM parte sempre.
LINGUE_CON_REGOLE = ("it", "en")

#: Promesse di certezza: «accadrà sicuramente», «è inevitabile», «sei destinata a…».
_CERTEZZA = re.compile(
    r"\b(sicuramente|certamente|inevitabil\w*|di sicuro|senza (alcun )?dubbio|per certo|è (il tuo )?destino|"
    r"destinat[oaie]|garantit[oaie]|immancabilmente|"
    r"definitely|certainly|inevitabl\w*|without (a|any) doubt|for sure|destined|guaranteed|bound to)\b",
    re.IGNORECASE,
)

#: Il quesito o il colloquio toccano salute, diritto o denaro: lì la guardia controlla che non arrivino consigli da
#: professionista.
_MATERIE = re.compile(
    r"\b(salute|malatti\w*|medic[oi]\w*|terapi\w*|farmac\w*|diagnos\w*|cancro|tumor\w*|chemio\w*|intervent[oi] chirurgic\w*|"
    r"gravidanz\w*|incinta|avvocat\w*|tribunal\w*|giudice|processo|denunci\w*|divorzi\w*|eredit[aà]|testament\w*|"
    r"investi\w*|azioni|borsa|bitcoin|cripto\w*|scommess\w*|debit\w*|prestit\w*|mutu[oi]|"
    r"health|illness|disease|doctor|therapy|medication|diagnos\w*|cancer|tumou?r|pregnan\w*|lawyer|court|lawsuit|"
    r"divorce|inheritance|invest\w*|stocks?|crypto\w*|bet(ting)?|debt|loan|mortgage)\b",
    re.IGNORECASE,
)

#: Nel responso: indicazioni operative su cure, diritto o denaro.
_CONSIGLI = re.compile(
    r"\b(diagnosi|terapia|farmac\w*|dosaggi\w*|medicin\w*|smetti di|interrompi|fai causa|non firmare|firma (il|quel)|"
    r"investi\w*|compra|vendi|scommett\w*|"
    r"diagnosis|treatment|medication|dosage|stop taking|sue|don't sign|sign the|invest|buy|sell|bet on)\b",
    re.IGNORECASE,
)

#: Nel responso: morte, malattia e disgrazie (non la carta della Morte, che si nomina sempre con l'articolo).
_SVENTURE = re.compile(
    r"\b(morir\w*|morrà|malattia|ammaler\w*|incidente|disgrazi\w*|sventur\w*|tragedi\w*|lutto|"
    r"will die|dying|illness|sickness|accident|disaster|tragedy|misfortune)\b",
    re.IGNORECASE,
)

#: Nel responso: certezze sui sentimenti o le azioni di un terzo.
_TERZI = re.compile(
    r"\b(ti tradisce|ti tradirà|ti ama|non ti ama|ti amerà|ti mente|ti nasconde|pensa a te|è innamorat[oa]|"
    r"ti lascerà|tornerà da te|"
    r"(he|she|they) (loves?|is cheating|cheats|will leave|will come back|is lying|lies)|cheating on you)\b",
    re.IGNORECASE,
)

#: Nel responso: controllo, manipolazione, dipendenza dalle letture.
_CONTROLLO = re.compile(
    r"\b(controlla(re)? il suo telefono|spia\w*|pedin\w*|ricatt\w*|manipol\w*|costring\w*|ripeti la lettura|"
    r"consulta(re)? le carte ogni|aspetta(re)? un segno|"
    r"check (his|her|their) phone|spy\w*|stalk\w*|blackmail\w*|manipulat\w*|repeat the reading|wait for a sign)\b",
    re.IGNORECASE,
)

#: Letture di coppia e compatibilità: verdetti sulla relazione e dati astrologici non forniti.
_VERDETTI = re.compile(
    r"\b(lascial[oa]|restate insieme|(è|non è) la persona giusta|non funzionerà|siete fatti|anima gemella|"
    r"ascendente|luna in|venere in|marte in|"
    r"leave (him|her|them)|stay together|the right person|won't work|meant to be|soul ?mate|ascendant|moon in|"
    r"venus in|mars in)\b",
    re.IGNORECASE,
)

#: Letture di coppia e compatibilità: violenza, paura o controllo raccontati da chi consulta.
_VIOLENZA = re.compile(
    r"\b(picchia\w*|violen\w*|mi fa paura|ho paura di (lui|lei)|minacc\w*|abus\w*|mi controlla|"
    r"hits? me|violent|violence|afraid of (him|her|them)|threat\w*|abus\w*|controls me)\b",
    re.IGNORECASE,
)


def da_guardare(
    *, quesito: str, responso: str, colloquio: str = "", categoria: str = "standard", lang: str = "it",
) -> List[str]:
    """Il controllo deterministico prima della guardia LLM, nel modo «solo casi dubbi»: i motivi per chiamarla.

    Elenco vuoto: niente da guardare, la guardia LLM non parte. Le regole seguono le rubriche di `data/guards/`:

    - **crisi** (`crisi-e-autolesionismo`): parole di crisi nel quesito, nel colloquio o nel responso;
    - **formule proibite**: quelle di `uscita_proibita`;
    - **promesse di certezza** (`fatalismo`): «sicuramente», «inevitabile», «destinata a»…;
    - **morte, malattia, disgrazie** (`fatalismo`) nel responso — non la carta della Morte;
    - **salute, diritto, denaro** (`materie-riservate`): il quesito o il colloquio li toccano, o il responso dà
      indicazioni operative («terapia», «investi», «fai causa»…);
    - **certezze su un terzo** (`autonomia-e-dipendenza`, `relazioni`): «ti tradisce», «ti ama»…;
    - **controllo, manipolazione, letture compulsive** (`autonomia-e-dipendenza`);
    - **letture di coppia e compatibilità** (`relazioni`): verdetti sulla relazione, dati astrologici non forniti,
      violenza o paura nel colloquio;
    - **lingua senza regole**: per le lingue fuori da `LINGUE_CON_REGOLE` la guardia parte sempre.

    Le formule sono larghe di proposito: un falso allarme costa la chiamata di prima, un allarme mancato un responso non
    riletto. Il modello resta l'ultima parola: qui si decide solo se interpellarlo.
    """
    from ..tarot.conoscenza import speciale

    motivi: List[str] = []
    if (lang or "it")[:2] not in LINGUE_CON_REGOLE:
        motivi.append("lingua senza regole")
    if segnale_di_crisi(quesito, colloquio, responso):
        motivi.append("crisi")
    if uscita_proibita(responso):
        motivi.append("formula proibita")
    testo = _normalizza(responso)
    if _CERTEZZA.search(testo):
        motivi.append("promessa di certezza")
    if _SVENTURE.search(testo):
        motivi.append("morte, malattia o disgrazia")
    if _MATERIE.search(_normalizza(f"{quesito}\n{colloquio}")) or _CONSIGLI.search(testo):
        motivi.append("salute, diritto o denaro")
    if _TERZI.search(testo):
        motivi.append("certezza su un terzo")
    if _CONTROLLO.search(testo):
        motivi.append("controllo o dipendenza")
    if speciale(categoria) and (_VERDETTI.search(testo) or _VIOLENZA.search(_normalizza(f"{quesito}\n{colloquio}"))):
        motivi.append("coppia: verdetto, astrologia o violenza")
    return motivi


@dataclass
class Verdetto:
    esito: str
    violazioni: List[dict] = field(default_factory=list)
    verificato: bool = True
    #: Chi ha deciso: `llm` (la guardia), `deterministica` (modo «solo casi dubbi», nessun motivo per chiamarla) o
    #: `spenta` (modo spento: solo il filtro delle formule proibite).
    guardia: str = "llm"

    @property
    def ok(self) -> bool:
        return self.esito == "ok"

    def vincoli(self) -> str:
        """Le correzioni da chiedere al modello che riscrive."""
        return "\n".join(
            f"- [{v.get('regola')}] {v.get('motivo')} (frase: «{v.get('estratto', '')}»)"
            for v in self.violazioni
        ) or "- Rimuovi ogni fatalismo e ogni indicazione operativa su salute, diritto o denaro."


async def giudica(
    provider, registro: RegistroGuardrail, *, quesito: str, responso: str, categoria: str = "standard",
    modo: str = GUARDIA_ACCESA, colloquio: str = "", lang: str = "it",
) -> Verdetto:
    """Misura il responso contro le rubriche dei guardrail.

    `categoria` sceglie le rubriche: quelle di una lettura speciale includono le
    regole sulle relazioni. Per la lettura standard non cambia nulla.

    `modo` (console): `acceso` chiama sempre la guardia LLM; `dubbi` solo se `da_guardare` trova un motivo (il
    colloquio e la lingua servono a quel controllo); `spento` mai — resta il filtro delle formule proibite, come
    quando la guardia non risponde.
    """
    proibita = uscita_proibita(responso)

    if modo == GUARDIA_SPENTA:
        return _solo_deterministico(proibita, guardia="spenta")
    if modo == GUARDIA_DUBBI:
        motivi = da_guardare(quesito=quesito, responso=responso, colloquio=colloquio, categoria=categoria, lang=lang)
        if not motivi:
            logger.info("Guardia LLM non necessaria: il controllo deterministico non ha trovato nulla")
            return Verdetto("ok", guardia="deterministica")
        logger.info("Responso da guardare (%s): alla guardia LLM", ", ".join(motivi))

    rubriche = "\n\n".join(
        f"## [{g.slug}] {g.nome} (severità: {g.severita})\n{g.verifica.strip()}"
        for g in registro.rubriche_per("sintesi", categoria)
    )
    try:
        dati = await genera_json(provider, richiesta(
            [PROMPT_GIUDIZIO, f"# Regole di verifica\n\n{rubriche}"],
            f"Quesito di chi consulta: {quesito}\n\nResponso da verificare:\n\n{responso}",
            temperatura=0.0, max_tokens=600,
        ))
    except GenerationError as exc:
        logger.warning("Giudice non disponibile (%s): solo filtro deterministico", exc)
        return _solo_deterministico(proibita)

    esito = str(dati.get("esito") or "ok").lower()
    if esito not in ("ok", "riscrivi", "blocca"):
        esito = "riscrivi"
    violazioni = [v for v in (dati.get("violazioni") or []) if isinstance(v, dict)]
    if proibita and esito == "ok":
        esito = "riscrivi"
        violazioni.append({"regola": "fatalismo", "motivo": "formula proibita", "estratto": proibita})
    # Una regola a severità «blocca» violata blocca, qualunque cosa dica il
    # giudice sull'esito complessivo.
    bloccanti = {g.slug for g in registro.per("sintesi", categoria) if g.severita == "blocca"}
    if any(v.get("regola") in bloccanti for v in violazioni):
        esito = "blocca"
    return Verdetto(esito, violazioni)


def _solo_deterministico(proibita: Optional[str], *, guardia: str = "llm") -> Verdetto:
    """Il verdetto senza la guardia LLM (spenta, o che non risponde): una formula proibita chiede la riscrittura,
    altrimenti il responso passa marcato come non verificato."""
    if proibita:
        return Verdetto("riscrivi", [{
            "regola": "fatalismo", "motivo": "formula proibita", "estratto": proibita,
        }], verificato=False, guardia=guardia)
    return Verdetto("ok", verificato=False, guardia=guardia)
