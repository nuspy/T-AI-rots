"""Quanto ragiona un modello, e come glielo si dice: il **punto unico** in cui un livello diventa parametri.

**I livelli** sono quelli che Nebius Token Factory documenta per `reasoning_effort` (create-chat-completion):
`none`, `minimal`, `low`, `medium`, `high`, `xhigh`, `max`. La console li offre per ogni fornitore (il suo
predefinito) e per ogni compito («eredita dal fornitore», o uno dei sette).

**Il dialetto** dipende dal tipo di fornitore (`llm/catalogo_fornitori.py`), non dal modello:

- `effort` — Nebius, LM Studio, OpenAI e gli OpenAI-compatibili generici: `reasoning_effort: <livello>` (LM Studio
  rispetta `none`, verificato il 4/10/2026; con gli altri livelli ragiona in modo simile);
- `thinking` — NVIDIA NIM: `chat_template_kwargs.enable_thinking` e un `reasoning_budget` proporzionale al livello;
- `anthropic` — il budget del «thinking» di Claude, proporzionale al livello (lo applica `llm/anthropic.py`).

**Mai parametri in conflitto.** Il dialetto `effort` toglie `enable_thinking` e `reasoning_budget` dai parametri del
fornitore; `thinking` toglie `reasoning_effort`. Un fornitore configurato a mano prima dei livelli (con
`enable_thinking` nei parametri) non perde nulla: finché non ha un livello si comporta come prima
(`compiti._parametri_coerenti`).

**Dal vecchio booleano**: `ragiona=true` diventa `medium`, `false` diventa `none` (migrazione `b6d8f0a2c4e7`). Il
booleano resta, allineato al livello, per il margine di budget lato applicazione (`json_mode.pavimento_ragionamento`).
"""
from __future__ import annotations

from typing import Any, Dict, Optional

LIVELLI = ("none", "minimal", "low", "medium", "high", "xhigh", "max")

#: Il budget di ragionamento per i dialetti che vogliono un numero (NIM, Anthropic): raddoppia a ogni livello, da 512
#: a 32 000 (il tetto di `json_mode.TETTO_TOKEN`).
BUDGET_LIVELLO: Dict[str, int] = {
    "none": 0, "minimal": 512, "low": 1024, "medium": 4096, "high": 8192, "xhigh": 16384, "max": 32000,
}

#: Il budget minimo che Anthropic accetta per il thinking.
BUDGET_MINIMO_ANTHROPIC = 1024

DIALETTO_EFFORT, DIALETTO_THINKING, DIALETTO_ANTHROPIC = "effort", "thinking", "anthropic"

#: I tipi del catalogo che vogliono `enable_thinking` + `reasoning_budget` invece di `reasoning_effort`.
TIPI_THINKING = frozenset({"nvidia"})


def valido(livello: Any) -> Optional[str]:
    """Il livello se è uno dei sette, altrimenti `None` (eredita)."""
    return livello if isinstance(livello, str) and livello in LIVELLI else None


def livello_da_bool(ragiona: bool) -> str:
    return "medium" if ragiona else "none"


def ragiona_da_livello(livello: Optional[str]) -> bool:
    return bool(livello) and livello != "none"


def dialetto(tipo: str, provider: str, parametri: Optional[Dict[str, Any]] = None) -> str:
    """Il dialetto del ragionamento per un fornitore. Senza tipo (un modello dall'ambiente), chi dichiara già
    `enable_thinking` nei parametri parla `thinking`, gli altri `effort`."""
    if provider == "anthropic":
        return DIALETTO_ANTHROPIC
    if tipo in TIPI_THINKING:
        return DIALETTO_THINKING
    if not tipo:
        kwargs = (parametri or {}).get("chat_template_kwargs")
        if isinstance(kwargs, dict) and "enable_thinking" in kwargs:
            return DIALETTO_THINKING
    return DIALETTO_EFFORT


def parametri_per_livello(parametri: Dict[str, Any], livello: str, dialetto_: str) -> Dict[str, Any]:
    """I parametri del fornitore con il ragionamento al `livello` scelto, nel dialetto giusto e senza conflitti.

    Si tolgono sempre le chiavi del ragionamento che il fornitore aveva (`reasoning_effort`, `reasoning_budget`,
    `chat_template_kwargs.enable_thinking`) e si scrivono solo quelle del dialetto. Gli altri parametri restano.
    Per Anthropic non si scrive nulla qui: il budget lo applica il fornitore (`budget_anthropic`).
    """
    puliti = {k: v for k, v in parametri.items() if k not in ("reasoning_effort", "reasoning_budget")}
    kwargs = dict(puliti.get("chat_template_kwargs") or {}) if isinstance(puliti.get("chat_template_kwargs"), dict) else {}
    kwargs.pop("enable_thinking", None)
    if kwargs:
        puliti["chat_template_kwargs"] = kwargs
    else:
        puliti.pop("chat_template_kwargs", None)

    if dialetto_ == DIALETTO_EFFORT:
        puliti["reasoning_effort"] = livello
    elif dialetto_ == DIALETTO_THINKING:
        acceso = ragiona_da_livello(livello)
        puliti["chat_template_kwargs"] = {**kwargs, "enable_thinking": acceso}
        if acceso:
            puliti["reasoning_budget"] = BUDGET_LIVELLO[livello]
    return puliti


def senza_conflitti(parametri: Dict[str, Any], dialetto_: str) -> Dict[str, Any]:
    """L'ultima pulizia, dopo i `parametri_override` scritti a mano su un compito: nel dialetto `effort` non restano
    `enable_thinking` né `reasoning_budget`, nel dialetto `thinking` non resta `reasoning_effort`."""
    if dialetto_ == DIALETTO_THINKING:
        return {k: v for k, v in parametri.items() if k != "reasoning_effort"}
    if dialetto_ != DIALETTO_EFFORT or "reasoning_effort" not in parametri:
        return parametri
    puliti = {k: v for k, v in parametri.items() if k != "reasoning_budget"}
    kwargs = puliti.get("chat_template_kwargs")
    if isinstance(kwargs, dict) and "enable_thinking" in kwargs:
        resto = {k: v for k, v in kwargs.items() if k != "enable_thinking"}
        if resto:
            puliti["chat_template_kwargs"] = resto
        else:
            puliti.pop("chat_template_kwargs")
    return puliti


#: **Il margine di ragionamento**: quanti token si aggiungono al tetto visibile di una richiesta (`max_tokens` del
#: chiamante: 500 per carta nella chiamata unica, ~2 600–3 600 per la sintesi) quando il livello non è `none`. Il
#: ragionamento consuma lo stesso `max_tokens` della risposta: senza margine il modello pensa fino al tetto e la
#: risposta resta vuota o tagliata. Misurato su Nebius (Nemotron 3.5 Lightning, ragionamento acceso col budget di
#: allora, 16 384): fino a ~8 000 token di ragionamento sulle interpretazioni e ~14 000 sulla sintesi; il `max_tokens`
#: predefinito di Nebius (8 192) non basta. Si cambia senza toccare il codice con `TAROT_MARGINI_RAGIONAMENTO`, un JSON
#: per livello (es. `{"xhigh": 32768}`); i livelli non indicati tengono questi valori.
MARGINE_LIVELLO: Dict[str, int] = {
    "none": 0, "minimal": 2048, "low": 4096, "medium": 8192, "high": 16384, "xhigh": 24576, "max": 32768,
}


def margine(livello: Optional[str], parametri: Optional[Dict[str, Any]] = None) -> int:
    """Il margine di ragionamento del livello (configurabile, vedi `MARGINE_LIVELLO`); almeno il `reasoning_budget`
    che il fornitore manda al modello (dialetto `thinking`), perché il pensiero dichiarato ci stia tutto."""
    if not ragiona_da_livello(livello):
        return 0
    from ..settings import get_settings

    configurati = get_settings().margini_ragionamento or {}
    valore = configurati.get(livello)
    base = int(valore) if isinstance(valore, (int, float)) and valore >= 0 else MARGINE_LIVELLO[livello]
    dichiarato = (parametri or {}).get("reasoning_budget")
    if isinstance(dichiarato, (int, float)) and not isinstance(dichiarato, bool) and dichiarato > base:
        return int(dichiarato)
    return base


def tetto_con_ragionamento(visibile: int, livello: Optional[str], parametri: Optional[Dict[str, Any]] = None) -> int:
    """Il `max_tokens` da mandare: il tetto visibile più il margine del livello. Con `none` (o senza livello) resta il
    tetto visibile; chi chiama decide se il modello ragiona (`ragiona`)."""
    return visibile + margine(livello, parametri)


def budget_anthropic(livello: Optional[str]) -> Optional[int]:
    """Il budget del thinking di Claude per il livello, o `None` (thinking spento)."""
    if not ragiona_da_livello(livello):
        return None
    return max(BUDGET_MINIMO_ANTHROPIC, BUDGET_LIVELLO[livello])
