"""Fornitore Anthropic, sul Messages API.

Esiste per una ragione precisa: il prompt caching di Anthropic non è
automatico. Serve un `cache_control` esplicito sul blocco dopo il quale finisce
il prefisso da riusare, e senza di esso lo strato stabile — costruito apposta
byte-identico — si paga per intero a ogni risposta. Un endpoint compatibile
OpenAI davanti ad Anthropic funzionerebbe, e perderebbe proprio questo.

**Dove va il prompt.** Il Messages API non accetta messaggi `system` in mezzo
alla conversazione: il sistema è un parametro a parte, fatto di blocchi.
Lo strato stabile diventa il primo blocco, con il `cache_control`; il
materiale volatile che il costruttore del prompt mette in un secondo messaggio
di sistema — memorie e passaggi recuperati — diventa un secondo blocco, senza.
L'ordine dei token resta quello: stabile, poi volatile, poi la conversazione.

**Cosa si conta.** I token letti dalla cache arrivano in `cache_read_input_tokens`
e finiscono in `Usage.cached_tokens`: è l'unico numero che dice se il prefisso
è stato davvero riconosciuto, e senza il risparmio resterebbe una promessa.
"""
from __future__ import annotations

import json
import logging
import time
from typing import Any, AsyncIterator, Dict, List, Optional

import httpx

from ..settings import Settings, get_settings
from . import consumi
from .base import (
    GenerationError, GenerationRequest, Message, StreamChunk, TruncatedResponse,
    Usage,
)

logger = logging.getLogger(__name__)

VERSIONE_API = "2023-06-01"


class AnthropicProvider:
    """Il Messages API, in streaming.

    Non implementa `embed()`: Anthropic non offre un endpoint di embedding. `llm.base.
    supporta_embedding()` lo riconosce per assenza del metodo, senza bisogno di una dichiarazione
    esplicita qui — assegnare `Compito.EMBEDDING` a un fornitore Anthropic va evitato in console.
    """

    name = "anthropic"
    #: Dichiarato per `scegli_strategia`: qui il caching è quello del fornitore.
    motore = "anthropic"

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        default_model: str = "",
        max_tokens: Optional[int] = None,
        timeout: Optional[float] = None,
        settings: Optional[Settings] = None,
        transport: Optional[httpx.AsyncBaseTransport] = None,
        budget_ragionamento: Optional[int] = None,
    ) -> None:
        settings = settings or get_settings()
        #: Il budget del «thinking» di Claude, dal livello di ragionamento del compito (`llm/ragionamento.py`).
        #: `None`: thinking spento, la richiesta resta quella di prima.
        self._budget_ragionamento = budget_ragionamento
        self._api_key = api_key or settings.anthropic_api_key
        self._base_url = (base_url or settings.anthropic_base_url).rstrip("/")
        self._default_model = default_model or settings.anthropic_model
        self._max_tokens = max_tokens or settings.anthropic_max_tokens
        self._timeout = timeout or settings.llm_stream_timeout
        #: Per le prove: permette di intercettare le richieste senza rete.
        self._transport = transport

    # -- interrogazione ----------------------------------------------------

    def _client(self, timeout: float) -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=timeout, transport=self._transport)

    def _headers(self) -> Dict[str, str]:
        if not self._api_key:
            raise GenerationError(
                "nessuna chiave Anthropic configurata: imposta TAROT_ANTHROPIC_API_KEY"
            )
        return {
            "x-api-key": self._api_key,
            "anthropic-version": VERSIONE_API,
            "content-type": "application/json",
        }

    async def available_models(self) -> List[str]:
        async with self._client(10.0) as client:
            risposta = await client.get(f"{self._base_url}/v1/models", headers=self._headers())
            risposta.raise_for_status()
            return [m["id"] for m in risposta.json().get("data", [])]

    # -- richiesta ---------------------------------------------------------

    def costruisci(self, request: GenerationRequest, *, stream: bool = True) -> Dict[str, Any]:
        """Il corpo della richiesta. Pubblico perché è ciò che i test verificano."""
        sistema: List[Dict[str, Any]] = []
        conversazione: List[Message] = []

        # Il punto di cache indica l'ultimo messaggio del prefisso stabile.
        confine = request.cache_breakpoint_after
        usa_cache = request.cache is not None and request.cache.modo == "prompt"

        for indice, messaggio in enumerate(request.messages):
            if messaggio.role == "system":
                blocco: Dict[str, Any] = {"type": "text", "text": messaggio.content}
                if usa_cache and confine is not None and indice == confine:
                    blocco["cache_control"] = {"type": "ephemeral"}
                sistema.append(blocco)
            else:
                conversazione.append(messaggio)

        corpo: Dict[str, Any] = {
            "model": request.model or self._default_model,
            "max_tokens": request.max_tokens or self._max_tokens,
            "temperature": request.temperature,
            "messages": _alterna(conversazione),
            "stream": stream,
        }
        if sistema:
            corpo["system"] = sistema
        if request.stop:
            corpo["stop_sequences"] = request.stop
        if self._budget_ragionamento:
            # Il thinking esteso: il budget sta dentro `max_tokens` (che deve superarlo, con spazio per la risposta), e
            # Claude lo accetta solo con la temperatura predefinita. Il tetto è quello visibile più il budget: il pensiero
            # non si mangia la risposta (come `ragionamento.tetto_con_ragionamento` per gli OpenAI-compatibili).
            corpo["thinking"] = {"type": "enabled", "budget_tokens": self._budget_ragionamento}
            corpo["max_tokens"] = corpo["max_tokens"] + self._budget_ragionamento
            corpo["temperature"] = 1
        corpo.update(request.extra)
        return corpo

    # -- generazione -------------------------------------------------------

    async def stream(self, request: GenerationRequest) -> AsyncIterator[StreamChunk]:
        """Come `OpenAICompatibleProvider.stream`: alla fine, comunque finisca, il consumo va al registro.

        Anthropic non separa i token di ragionamento da quelli di uscita: restano solo i caratteri del pensiero."""
        inizio = time.perf_counter()
        stato: Dict[str, Any] = {"esito": "interrotta", "errore": "", "usage": None, "motivo": "",
                                 "testo": 0, "pensiero": 0, "corpo": None, "annotato": False}

        def annota() -> None:
            if stato["annotato"]:
                return
            stato["annotato"] = True
            corpo = stato["corpo"] or {}
            consumi.registra(consumi.consumo_da(
                request, fornitore="anthropic", modello=str(corpo.get("model") or ""), usage=stato["usage"],
                durata_ms=int((time.perf_counter() - inizio) * 1000), esito=stato["esito"],
                finish_reason=stato["motivo"], caratteri_uscita=stato["testo"],
                caratteri_ragionamento=stato["pensiero"], max_tokens=corpo.get("max_tokens"), errore=stato["errore"],
            ))

        try:
            async for pezzo in self._stream(request, stato):
                if pezzo.done:
                    annota()
                yield pezzo
        except TruncatedResponse as exc:
            stato["esito"], stato["errore"] = "troncata", str(exc)[:300]
            raise
        except Exception as exc:
            stato["esito"], stato["errore"] = "errore", f"{type(exc).__name__}: {exc}"[:300]
            raise
        finally:
            annota()

    async def _stream(self, request: GenerationRequest, stato: Dict[str, Any]) -> AsyncIterator[StreamChunk]:
        corpo = self.costruisci(request, stream=True)
        stato["corpo"] = corpo
        testo: List[str] = []
        uso = Usage(model=corpo["model"])
        motivo = ""

        async with self._client(self._timeout) as client:
            async with client.stream(
                "POST", f"{self._base_url}/v1/messages", json=corpo, headers=self._headers(),
            ) as risposta:
                if risposta.status_code >= 400:
                    errore = (await risposta.aread()).decode("utf-8", "replace")
                    raise GenerationError(f"{risposta.status_code} da Anthropic: {errore[:500]}")

                async for riga in risposta.aiter_lines():
                    if not riga.startswith("data:"):
                        continue
                    try:
                        evento = json.loads(riga[5:].strip())
                    except json.JSONDecodeError:
                        logger.debug("Evento non interpretabile: %s", riga[:120])
                        continue

                    tipo = evento.get("type")
                    if tipo == "message_start":
                        _conta_ingresso(uso, (evento.get("message") or {}).get("usage") or {})
                        stato["usage"] = uso
                    elif tipo == "content_block_delta":
                        delta = evento.get("delta") or {}
                        if delta.get("type") == "text_delta" and delta.get("text"):
                            stato["testo"] += len(delta["text"])
                            testo.append(delta["text"])
                            yield StreamChunk(text=delta["text"])
                        elif delta.get("type") == "thinking_delta" and delta.get("thinking"):
                            stato["pensiero"] += len(delta["thinking"])
                            yield StreamChunk(reasoning=delta["thinking"])
                    elif tipo == "message_delta":
                        motivo = (evento.get("delta") or {}).get("stop_reason") or motivo
                        stato["motivo"] = motivo
                        uscita = (evento.get("usage") or {}).get("output_tokens")
                        if uscita is not None:
                            uso.completion_tokens = int(uscita)
                    elif tipo == "error":
                        dettaglio = (evento.get("error") or {}).get("message", "errore")
                        raise GenerationError(f"Anthropic: {dettaglio}")

        uso.total_tokens = uso.prompt_tokens + uso.completion_tokens
        completo = "".join(testo)
        if motivo == "max_tokens" and not completo.strip():
            raise TruncatedResponse(
                "il modello ha esaurito max_tokens senza produrre testo", partial=completo, usage=uso,
            )
        stato["esito"] = "ok"
        yield StreamChunk(done=True, usage=uso, finish_reason=motivo)

    async def complete(self, request: GenerationRequest) -> str:
        pezzi: List[str] = []
        async for chunk in self.stream(request):
            if chunk.text:
                pezzi.append(chunk.text)
        return "".join(pezzi)


def _conta_ingresso(uso: Usage, dati: Dict[str, Any]) -> None:
    """I token in ingresso, compresi quelli scritti e letti dalla cache.

    Anthropic li riporta separati: `input_tokens` sono solo quelli *fuori*
    cache. Il totale in ingresso è la somma dei tre, ed è quello che va in
    `prompt_tokens` perché il confronto con gli altri fornitori abbia senso.
    """
    base = int(dati.get("input_tokens", 0) or 0)
    scritti = int(dati.get("cache_creation_input_tokens", 0) or 0)
    letti = int(dati.get("cache_read_input_tokens", 0) or 0)
    uso.prompt_tokens = base + scritti + letti
    uso.cached_tokens = letti


def _alterna(messaggi: List[Message]) -> List[Dict[str, Any]]:
    """Messaggi utente e assistente, alternati e che cominciano dall'utente.

    Il Messages API pretende l'alternanza. Due turni consecutivi dello stesso
    ruolo — capita con una risposta interrotta, o con una domanda riproposta —
    si uniscono invece di far fallire la richiesta; un avvio con l'assistente
    riceve un turno utente vuoto davanti, che non cambia il senso e rende la
    richiesta valida.
    """
    uscita: List[Dict[str, Any]] = []
    for m in messaggi:
        if uscita and uscita[-1]["role"] == m.role:
            uscita[-1]["content"] += "\n\n" + m.content
        else:
            uscita.append({"role": m.role, "content": m.content})
    if uscita and uscita[0]["role"] != "user":
        uscita.insert(0, {"role": "user", "content": "…"})
    return uscita
