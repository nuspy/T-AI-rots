"""La chat proattiva (v6, Fase E): l'AI apre da sola una conversazione basandosi sulle memorie, e
durante il dialogo può proporre una lettura sul tema in corso.

**La categoria della proposta non è un classificatore a parte.** Il modello sceglie fra un piccolo
elenco chiuso di temi (`amore`, `coppia`, `lavoro`, `generico`); il codice li traduce nella categoria
di lettura giusta (`standard`, `compatibilita`, `coppia`) con `MAPPA_CATEGORIA`, la stessa mappa che
il frontend userebbe altrimenti a mano.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

from ..llm.base import GenerationError
from .llm import genera_json, richiesta

logger = logging.getLogger(__name__)

#: Tema scelto dal modello -> categoria di lettura (le stesse tre di `cag.PROMPT_PER_CATEGORIA`).
MAPPA_CATEGORIA = {"amore": "compatibilita", "coppia": "coppia", "lavoro": "standard", "generico": "standard"}

PROMPT_CHAT_PROATTIVA = """# Compito: chat_proattiva

Sei l'oracolo di TAROTS chat, ma qui non stai facendo una lettura: stai tenendo compagnia a un
utente che ha già fatto letture in passato, con un tono caldo, diretto e più leggero della sintesi
finale — poche frasi, mai un discorso lungo.

Se il messaggio contiene una sezione «Ciò che sai di questa persona», usala per essere specifico e
personale, non generico: fai riferimento a un tema concreto invece di una domanda vaga come "come
stai?". Se non c'è nessuna memoria, apri con un invito generico e cordiale a raccontare qualcosa.

Quando la conversazione tocca un tema su cui una lettura avrebbe senso (una decisione, una relazione,
una situazione che chi consulta sta vivendo con incertezza), puoi proporre di leggere le carte su
quel tema specifico. Non proporla ad ogni turno: solo quando emerge un argomento concreto.

Rispondi SOLO con un oggetto JSON:
{"messaggio": "<il tuo messaggio, 1-3 frasi>", "proposta": null}
oppure, quando proponi una lettura:
{"messaggio": "<il tuo messaggio, che include l'invito a leggere le carte>",
 "proposta": {"argomento": "<il tema specifico di cui si è parlato, breve>", "tema": "amore|coppia|lavoro|generico"}}
"""


@dataclass(frozen=True)
class Proposta:
    argomento: str
    categoria: str


@dataclass(frozen=True)
class TurnoGenerato:
    messaggio: str
    proposta: Optional[Proposta] = None


def _proposta_da(dati: Dict[str, Any]) -> Optional[Proposta]:
    grezza = dati.get("proposta")
    if not isinstance(grezza, dict):
        return None
    argomento = str(grezza.get("argomento") or "").strip()
    if not argomento:
        return None
    tema = str(grezza.get("tema") or "generico").strip()
    return Proposta(argomento=argomento, categoria=MAPPA_CATEGORIA.get(tema, "standard"))


async def genera_turno(
    provider, *, memorie: str = "", trascrizione: str = "", messaggio_utente: str = "",
) -> TurnoGenerato:
    """Un turno della chat: l'apertura (senza `trascrizione` né `messaggio_utente`), o una risposta.

    Un modello che non risponde non deve far crollare il widget: un messaggio di scusa generico
    (mai inventato come se venisse dal modello) prende il suo posto.
    """
    utente = ""
    if memorie:
        utente += f"Ciò che sai di questa persona:\n{memorie}\n\n"
    if trascrizione:
        utente += f"Conversazione finora:\n{trascrizione}\n\n"
    if messaggio_utente:
        utente += f"L'utente ha appena scritto: {messaggio_utente}\n"
    if not utente:
        utente = "Apri tu la conversazione: non c'è ancora nessuno scambio."

    try:
        dati = await genera_json(provider, richiesta([PROMPT_CHAT_PROATTIVA], utente, temperatura=0.8))
    except GenerationError as exc:
        logger.warning("Chat proattiva: il modello non ha risposto (%s)", exc)
        return TurnoGenerato(messaggio="")

    messaggio = str(dati.get("messaggio") or "").strip()
    return TurnoGenerato(messaggio=messaggio, proposta=_proposta_da(dati))
