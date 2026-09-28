"""Estrazione della memoria da una lettura conclusa (v6, Fase B).

Gira **dopo** che la sintesi è stata generata e salvata (`readings.py::sintesi()`), mai prima: la
memoria si scrive da un fatto concluso, non da una lettura ancora in corso. `estrai_memorie()` è solo
il compito LLM (prompt + parsing tollerante); `estrai_e_salva()` è l'orchestrazione fuori dalla
risposta SSE — un compito in background che non deve mai far aspettare l'utente, né farlo fallire se
va storto: un modello che non risponde o un embedding che fallisce non deve intaccare una lettura già
consegnata.
"""
from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional, Sequence

from ..llm.base import GenerationError, supporta_embedding
from .llm import genera_json, richiesta

logger = logging.getLogger(__name__)

#: Deve restare in sincronia con `domain.memory_models.TIPI_MEMORIA` — duplicato qui perché `tarot/`
#: non dipende dal livello dati per la sola validazione di una stringa.
TIPI_MEMORIA = ("stabile", "variabile")

PROMPT_MEMORIA_ESTRAZIONE = """# Compito: memoria_estrazione

Sei l'archivista di TAROTS chat. Ricevi il quesito, il colloquio e la sintesi di una lettura appena
conclusa, e ne estrai i fatti su chi consulta che vale la pena ricordare per le prossime letture.

Due tipi di fatto:
- STABILE: un fatto fisico, anagrafico o di identità che non regredisce naturalmente — una
  condizione fisica permanente, un lutto, uno stato civile duraturo. Esempio: se chi consulta dice
  che gli manca una gamba, è STABILE — non richiederlo mai più, e non ha senso chiedere in futuro se
  "gli è ricresciuta".
- VARIABILE: una situazione che evolve nel tempo — una crisi di coppia, una ricerca di lavoro, uno
  stato d'animo, un progetto in corso. Di questi si può chiedere l'evoluzione la prossima volta.

Non estrarre dettagli di contorno o informazioni già ovvie dal quesito stesso: solo fatti che
cambierebbero il modo in cui una lettura futura va condotta o letta.

Ogni memoria ha un campo di attinenza: amore, lavoro, salute, famiglia, denaro, spirituale, altro.

Rispondi SOLO con un oggetto JSON:
{"memorie": [{"contenuto": "<il fatto, in terza persona, una frase>", "tipo": "stabile|variabile", "campo_attinenza": "<uno dei campi elencati>"}]}
Se non c'è nulla di nuovo da ricordare, rispondi {"memorie": []}.
"""


async def estrai_memorie(provider, *, quesito: str, colloquio: str, sintesi: str) -> List[Dict[str, str]]:
    """Le memorie da questa lettura, o lista vuota se il modello non risponde o non ne trova nessuna."""
    utente = f"Quesito: {quesito}\n\nColloquio:\n{colloquio}\n\nSintesi della lettura:\n{sintesi}"
    try:
        dati = await genera_json(provider, richiesta([PROMPT_MEMORIA_ESTRAZIONE], utente, temperatura=0.2))
    except GenerationError as exc:
        logger.warning("Estrazione memorie non riuscita: %s", exc)
        return []

    grezze = dati.get("memorie")
    if not isinstance(grezze, list):
        return []

    valide: List[Dict[str, str]] = []
    for m in grezze:
        if not isinstance(m, dict):
            continue
        contenuto = str(m.get("contenuto") or "").strip()
        tipo = str(m.get("tipo") or "").strip()
        campo = str(m.get("campo_attinenza") or "").strip() or "altro"
        if not contenuto or tipo not in TIPI_MEMORIA:
            continue
        valide.append({"contenuto": contenuto, "tipo": tipo, "campo_attinenza": campo})
    return valide


async def estrai_e_salva(
    session_factory: Callable[[], Any],
    owner_id: int,
    reading_id: Optional[Any],
    *,
    quesito: str,
    colloquio: str,
    sintesi: str,
    provider_estrazione,
    provider_embedding,
) -> None:
    """Orchestrazione in background: estrae, vettorizza, fonde con le memorie esistenti, salva.

    Va lanciata con `asyncio.create_task()`, mai `await`-ata dal flusso SSE: un errore qui non deve
    mai raggiungere una risposta già inviata all'utente, e per questo ogni eccezione è solo loggata.
    """
    from ..domain.memoria_repositories import scrivi_o_fondi  # import locale: evita un ciclo con readings.py

    try:
        memorie = await estrai_memorie(provider_estrazione, quesito=quesito, colloquio=colloquio, sintesi=sintesi)
        if not memorie:
            return
        if not supporta_embedding(provider_embedding):
            logger.info("Nessun fornitore di embedding disponibile: memorie estratte ma non salvate")
            return

        contenuti = [m["contenuto"] for m in memorie]
        vettori = await provider_embedding.embed(contenuti)

        async with session_factory() as session:
            for memoria, embedding in zip(memorie, vettori):
                await scrivi_o_fondi(
                    session, owner_id,
                    contenuto=memoria["contenuto"], tipo=memoria["tipo"],
                    campo_attinenza=memoria["campo_attinenza"], embedding=embedding,
                    reading_id=reading_id, fonte="lettura",
                )
            await session.commit()
    except Exception:  # noqa: BLE001 - un errore qui non deve mai propagarsi: solo la traccia
        logger.exception("Estrazione/salvataggio della memoria fallito per la lettura %s", reading_id)
