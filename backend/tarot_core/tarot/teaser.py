"""L'anteprima per un visitatore anonimo (v6, Fase F).

Non è un troncamento del responso vero: rischierebbe di rivelare comunque la tendenza finale nelle
prime righe (la sintesi apre spesso col quadro d'insieme). È una riscrittura breve, dedicata, che
conferma che la lettura è pronta e ne accenna il tono senza svelarne il contenuto — l'incentivo a
registrarsi è leggere l'analisi vera, non indovinarla dalle prime frasi.
"""
from __future__ import annotations

import logging

from ..llm.base import GenerationError
from .lingue import istruzione_lingua
from .llm import genera_testo, richiesta

logger = logging.getLogger(__name__)

PROMPT_TEASER = """# Compito: teaser

Hai appena scritto il responso completo di una lettura dei tarocchi per una persona che non si è
ancora registrata. Scrivi un'anteprima breve (2-3 frasi) che:
- confermi che le carte hanno parlato e che la lettura è pronta;
- accenni al tono generale delle energie in gioco (per esempio cambiamento, stasi, conflitto,
  crescita, chiarimento) SENZA rivelare la tendenza finale, il consiglio specifico o i nomi delle
  carte;
- crei curiosità per leggere l'analisi completa, con un tono caldo e mai commerciale o insistente.

Non copiare o parafrasare frasi del responso completo. Non anticipare la sezione finale «La tendenza
più probabile». Rispondi solo col testo dell'anteprima, senza titoli né virgolette.
"""

#: Se il modello non risponde: un'anteprima generica, mai finta come se venisse dal modello.
_RIPIEGO = "Le carte hanno parlato: la tua lettura è pronta. Registrati per leggere l'analisi completa."


async def genera_teaser(provider, *, responso: str, lang: str = "it") -> str:
    try:
        testo = await genera_testo(provider, richiesta(
            [PROMPT_TEASER], f"Responso completo:\n{responso}\n\n{istruzione_lingua(lang)}",
            temperatura=0.6, max_tokens=200,
        ))
        if testo.strip():
            return testo.strip()
    except GenerationError as exc:
        logger.warning("Teaser non generato (%s): ripiego sul testo generico", exc)
    return _RIPIEGO
