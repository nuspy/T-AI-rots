"""Le due forme in cui si interroga un modello: JSON o testo in streaming.

I fornitori di `llm/` vengono da Personalities: `OpenAICompatibleProvider` sa
negoziare la modalità JSON, `AnthropicProvider` no. Qui si nasconde la
differenza, così che il dominio chieda «un JSON» senza sapere a chi.
"""
from __future__ import annotations

import logging
from typing import Any, AsyncIterator, Dict, List, Optional

from ..llm.base import GenerationError, GenerationRequest, Message
from ..llm.json_mode import JsonNonInterpretabile, estrai_json

logger = logging.getLogger(__name__)


def richiesta(
    sistema: List[str], utente: str, *, temperatura: float = 0.7,
    max_tokens: Optional[int] = None, cache_dopo: Optional[int] = None,
) -> GenerationRequest:
    messaggi = [Message("system", s) for s in sistema] + [Message("user", utente)]
    return GenerationRequest(
        messages=messaggi, temperature=temperatura, max_tokens=max_tokens,
        cache_breakpoint_after=cache_dopo,
    )


async def genera_json(provider, req: GenerationRequest) -> Dict[str, Any]:
    """Un oggetto JSON dal modello, o `GenerationError`."""
    if hasattr(provider, "complete_json"):
        dati = await provider.complete_json(req)
    else:
        testo = await provider.complete(req)
        try:
            dati = estrai_json(testo)
        except JsonNonInterpretabile as exc:
            raise GenerationError(f"JSON non interpretabile: {exc}") from exc
    if not isinstance(dati, dict):
        raise GenerationError("il modello non ha restituito un oggetto JSON")
    return dati


async def genera_flusso(provider, req: GenerationRequest) -> AsyncIterator[str]:
    """Il testo, un frammento per volta. Il ragionamento non si mostra."""
    async for pezzo in provider.stream(req):
        if pezzo.text:
            yield pezzo.text
        if pezzo.done:
            break


async def genera_testo(provider, req: GenerationRequest) -> str:
    return "".join([p async for p in genera_flusso(provider, req)]).strip()
