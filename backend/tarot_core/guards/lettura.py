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
  rigenera con i vincoli, una volta; se non basta, si blocca.

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
    r"suicid\w*|uccidermi|ammazzarmi|togliermi la vita|farla finita|"
    r"non voglio (piu|più) vivere|voglio morire|farmi del male|tagliarmi|"
    r"autolesion\w*|"
    r"kill myself|suicide|end my life|want to die|hurt myself|self[- ]harm"
    r")\b",
    re.IGNORECASE,
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
    return any(_CRISI.search(_normalizza(t)) for t in testi if t)


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


@dataclass
class Verdetto:
    esito: str
    violazioni: List[dict] = field(default_factory=list)
    verificato: bool = True

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
    provider, registro: RegistroGuardrail, *, quesito: str, responso: str,
) -> Verdetto:
    """Misura il responso contro le rubriche dei guardrail."""
    proibita = uscita_proibita(responso)

    rubriche = "\n\n".join(
        f"## [{g.slug}] {g.nome} (severità: {g.severita})\n{g.verifica.strip()}"
        for g in registro.rubriche_per("sintesi")
    )
    try:
        dati = await genera_json(provider, richiesta(
            [PROMPT_GIUDIZIO, f"# Regole di verifica\n\n{rubriche}"],
            f"Quesito di chi consulta: {quesito}\n\nResponso da verificare:\n\n{responso}",
            temperatura=0.0, max_tokens=600,
        ))
    except GenerationError as exc:
        logger.warning("Giudice non disponibile (%s): solo filtro deterministico", exc)
        if proibita:
            return Verdetto("riscrivi", [{
                "regola": "fatalismo", "motivo": "formula proibita", "estratto": proibita,
            }], verificato=False)
        return Verdetto("ok", verificato=False)

    esito = str(dati.get("esito") or "ok").lower()
    if esito not in ("ok", "riscrivi", "blocca"):
        esito = "riscrivi"
    violazioni = [v for v in (dati.get("violazioni") or []) if isinstance(v, dict)]
    if proibita and esito == "ok":
        esito = "riscrivi"
        violazioni.append({"regola": "fatalismo", "motivo": "formula proibita", "estratto": proibita})
    # Una regola a severità «blocca» violata blocca, qualunque cosa dica il
    # giudice sull'esito complessivo.
    bloccanti = {g.slug for g in registro.per("sintesi") if g.severita == "blocca"}
    if any(v.get("regola") in bloccanti for v in violazioni):
        esito = "blocca"
    return Verdetto(esito, violazioni)
