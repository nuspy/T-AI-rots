"""Fornitore per gli endpoint in dialetto OpenAI.

Uno solo per LM Studio, vLLM, llama.cpp in modalità server, OpenAI stesso e i
servizi compatibili: parlano tutti lo stesso protocollo, e le differenze che
contano — quali campi rispettano, cosa riportano sul consumo — sono
differenze di comportamento, non di forma.

Le due asprezze gestite qui hanno entrambe una storia:

**Il silenzio del modello che ragiona.** I modelli con ragionamento esplicito
consumano il budget pensando e, se si esaurisce, chiudono con `finish_reason:
length` e contenuto vuoto. Non è un errore di rete: è una risposta valida e
inutile. Senza distinguerla, si conclude che la generazione è riuscita e si
salva una risposta vuota.

**Lo stream che si ferma senza chiudersi.** Una connessione che smette di
emettere token senza mai chiudersi terrebbe la richiesta appesa finché il
client non rinuncia. Il timeout è fra un token e l'altro, non sulla durata
complessiva: una risposta lunga è legittima, un silenzio prolungato no.
"""
from __future__ import annotations

import json
import logging
import time
from dataclasses import replace
from typing import Any, AsyncIterator, Dict, List, Optional

import httpx

from ..settings import Settings, get_settings
from . import consumi
from .base import (
    GenerationError, GenerationRequest, LLMProvider, StreamChunk,
    TruncatedResponse, Usage,
)
from .json_mode import (
    DIALETTI, TENTATIVI_DI_BUDGET, TETTO_TOKEN,
    FiltroPensieroInline, JsonNonInterpretabile, e_rifiuto_del_formato,
    estrai_json, formato_risposta, pavimento_ragionamento, prossimo_budget,
)
from .ragionamento import ragiona_da_livello, tetto_con_ragionamento

logger = logging.getLogger(__name__)

#: Il dialetto JSON già negoziato, per (indirizzo, modello), per tutta la vita del processo.
#:
#: Non basta ricordarlo nell'oggetto: un compito con una sostituzione in console (`ragiona_override`, il livello…) riceve
#: un fornitore nuovo a ogni chiamata (`RegistroModelli.per`, che non lo tiene in cache per non mescolare le
#: sostituzioni di due compiti), e con il ricordo nell'oggetto la negoziazione ripartiva da capo ogni volta — «Modalità
#: JSON negoziata» 199 volte in quattro giorni in produzione. Con un fornitore che rifiuta `json_object` (LM Studio) era
#: una richiesta fallita in più per ogni chiamata JSON. Il dialetto dipende dal server e dal modello, non dal
#: ragionamento né dai parametri: la chiave è quella.
_DIALETTI_NOTI: Dict[tuple, Any] = {}


def dimentica_dialetti_json() -> None:
    """Svuota il ricordo dei dialetti JSON negoziati (per i test, o dopo un cambio di server allo stesso indirizzo)."""
    _DIALETTI_NOTI.clear()


class OpenAICompatibleProvider(LLMProvider):
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        default_model: str = "",
        timeout: Optional[float] = None,
        settings: Optional[Settings] = None,
        name: str = "openai-compatibile",
        motore: Optional[str] = None,
        ragiona: bool = False,
        parametri: Optional[Dict[str, Any]] = None,
        embed_model: str = "",
        json_schema: bool = False,
        livello_ragionamento: str = "",
    ) -> None:
        settings = settings or get_settings()
        self.name = name
        self._base_url = (base_url or settings.llm_base_url).rstrip("/")
        #: Il modello di embedding, se diverso da quello di chat. Vuoto: `embed()` ricade su
        #: `default_model` — un server con un solo modello caricato (LM Studio, vLLM) spesso non
        #: ne ha uno dedicato, ed è comunque in grado di rispondere a `/embeddings`.
        self._embed_model = embed_model
        #: Il motore dietro l'indirizzo: decide quale `ContextStrategy` si usa
        #: e quali campi di cache si possono mandare. Dichiarato qui perché è
        #: il fornitore a sapere a cosa sta parlando.
        self.motore = motore or riconosci_motore(self._base_url, settings.llm_engine)
        #: Se il modello ragiona prima di rispondere. Alza il pavimento del
        #: budget su OGNI richiesta (non solo quelle strutturate): vedi
        #: `pavimento_ragionamento()`.
        self.ragiona = ragiona
        #: Il livello di ragionamento della richiesta (`none` … `max`, `llm/ragionamento.py`): con un livello acceso il
        #: `max_tokens` è il tetto visibile più il margine del livello (`tetto_con_ragionamento`). Vuoto: un fornitore
        #: di prima dei livelli, che segue ancora il pavimento di `pavimento_ragionamento`.
        self.livello_ragionamento = livello_ragionamento
        #: Campi aggiunti a ogni richiesta (per esempio il controllo del ragionamento, che si dà nella richiesta e
        #: non al caricamento del modello). Quelli di una singola richiesta (`request.extra`) prevalgono.
        self._parametri: Dict[str, Any] = dict(parametri or {})
        self._api_key = api_key or settings.llm_api_key
        self._default_model = default_model or settings.llm_model
        self._timeout = timeout or settings.llm_stream_timeout
        self._modello_risolto: Optional[str] = None
        #: Il dialetto JSON che questo server accetta. Si scopre alla prima
        #: richiesta e poi non si ridiscute: rinegoziarlo ogni volta
        #: costerebbe una richiesta fallita per ogni chiamata.
        self._dialetto_json: Optional[str] = None
        self._dialetto_negoziato = False
        #: Provare per prima la risposta vincolata allo schema rigoroso della fase (`llm/schemi_json.py`).
        self._json_schema = json_schema

    # -- interrogazione ----------------------------------------------------

    async def available_models(self) -> List[str]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{self._base_url}/models", headers=self._headers(),
            )
            response.raise_for_status()
            return [m["id"] for m in response.json().get("data", [])]

    async def embed(self, texts: List[str]) -> List[List[float]]:
        """Vettorizza una lista di testi via `POST {base_url}/embeddings`.

        L'ordine del risultato segue `index` dalla risposta, non l'ordine di arrivo: il server
        OpenAI-compatibile non garantisce di rispettare l'ordine di `input` sotto concorrenza, e
        un embedding scambiato con un altro finirebbe silenziosamente sul testo sbagliato.
        """
        if not texts:
            return []
        modello = self._embed_model or self._default_model or await self.resolve_model()
        inizio = time.perf_counter()
        esito, errore, usage = "errore", "", None
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{self._base_url}/embeddings",
                    json={"model": modello, "input": texts},
                    headers=self._headers(),
                )
                if response.status_code >= 400:
                    corpo = response.text
                    raise GenerationError(
                        f"{response.status_code} da {self._base_url}/embeddings: {corpo[:500]}"
                    )
                risposta = response.json()
                if isinstance(risposta.get("usage"), dict):
                    usage = self._parse_usage(risposta["usage"], modello)
                dati = sorted(risposta["data"], key=lambda d: d["index"])
                esito = "ok"
                return [d["embedding"] for d in dati]
        except Exception as exc:
            errore = f"{type(exc).__name__}: {exc}"[:300]
            raise
        finally:
            # Il compito arriva da `ProviderMisurato.embed` (una variabile di contesto: qui non c'è una richiesta).
            consumi.registra(consumi.consumo_da(
                None, fornitore=self.name, modello=modello, usage=usage, esito=esito, errore=errore,
                durata_ms=int((time.perf_counter() - inizio) * 1000),
                etichetta={**consumi.etichetta_embed(), "fase": "embedding", "streaming": False},
                caratteri_ingresso=sum(len(t) for t in texts),
            ))

    async def resolve_model(self) -> str:
        """Il modello da usare, chiedendo al server se non è configurato.

        Con LM Studio è la situazione normale: l'utente carica un modello
        dall'interfaccia e il nome cambia a ogni cambio. Pretendere che sia
        scritto in configurazione significa una modifica al deploy ogni volta.
        """
        if self._default_model:
            return self._default_model
        if self._modello_risolto:
            return self._modello_risolto

        modelli = await self.available_models()
        if not modelli:
            raise GenerationError(
                f"nessun modello caricato su {self._base_url}: "
                f"caricane uno nel motore locale, o imposta TAROT_LLM_MODEL"
            )
        self._modello_risolto = modelli[0]
        logger.info("Modello dedotto dal server: %s", self._modello_risolto)
        return self._modello_risolto

    # -- generazione -------------------------------------------------------

    async def stream(self, request: GenerationRequest) -> AsyncIterator[StreamChunk]:
        """Una chiamata, un frammento per volta; alla fine, comunque finisca, il consumo va al registro.

        Il registro (`llm/consumi.py`) non solleva mai: un errore di scrittura non tocca la risposta, e una chiamata
        fallita o interrotta resta contata (spesso è proprio lì che si spreca). Si annota **prima** di consegnare
        l'ultimo frammento: chi lo riceve di solito smette di leggere (`genera_flusso`), e un generatore abbandonato
        arriva al suo `finally` solo quando il garbage collector se ne ricorda."""
        inizio = time.perf_counter()
        stato: Dict[str, Any] = {
            "esito": "interrotta", "errore": "", "usage": None, "finish_reason": "",
            "testo": 0, "pensiero": 0, "payload": None, "annotato": False,
        }

        def annota() -> None:
            if stato["annotato"]:
                return
            stato["annotato"] = True
            payload = stato["payload"] or {}
            consumi.registra(consumi.consumo_da(
                request, fornitore=self.name, modello=str(payload.get("model") or self._default_model),
                usage=stato["usage"], durata_ms=int((time.perf_counter() - inizio) * 1000),
                esito=stato["esito"], finish_reason=stato["finish_reason"], caratteri_uscita=stato["testo"],
                caratteri_ragionamento=stato["pensiero"], max_tokens=payload.get("max_tokens"),
                errore=stato["errore"],
                extra={k: payload[k] for k in ("chat_template_kwargs", "reasoning_budget", "reasoning_effort")
                       if k in payload},
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
        payload = await self._build_payload(request, stream=True)
        stato["payload"] = payload

        testo_accumulato: List[str] = []
        usage: Optional[Usage] = None
        finish_reason = ""
        filtro_pensiero = FiltroPensieroInline()

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            async with client.stream(
                "POST",
                f"{self._base_url}/chat/completions",
                json=payload,
                headers=self._headers(),
            ) as response:
                if response.status_code >= 400:
                    corpo = (await response.aread()).decode("utf-8", "replace")
                    raise GenerationError(
                        f"{response.status_code} da {self._base_url}: {corpo[:500]}"
                    )

                async for riga in response.aiter_lines():
                    if not riga or not riga.startswith("data:"):
                        continue
                    dato = riga[5:].strip()
                    if dato == "[DONE]":
                        break

                    try:
                        evento = json.loads(dato)
                    except json.JSONDecodeError:
                        # Un frammento malformato non giustifica far cadere
                        # l'intera risposta: si annota e si prosegue.
                        logger.debug("Frammento non interpretabile: %s", dato[:120])
                        continue

                    if (uso := evento.get("usage")):
                        usage = self._parse_usage(uso, payload["model"])
                        stato["usage"] = usage

                    for scelta in evento.get("choices", []):
                        delta = scelta.get("delta") or {}
                        if scelta.get("finish_reason"):
                            finish_reason = scelta["finish_reason"]
                            stato["finish_reason"] = finish_reason

                        # Nome del campo diverso da un motore all'altro: LM
                        # Studio usa `reasoning`, altri `reasoning_content`.
                        pensiero_campo = delta.get("reasoning") or delta.get(
                            "reasoning_content"
                        ) or ""
                        if pensiero_campo:
                            stato["pensiero"] += len(pensiero_campo)
                            yield StreamChunk(reasoning=pensiero_campo)

                        # Alcuni motori non separano affatto il ragionamento: lo scrivono
                        # dentro `content`, tipicamente fra `<think>...</think>`. Senza
                        # questo filtro quel testo attraverserebbe come se fosse la
                        # risposta vera — vedi `FiltroPensieroInline` per la storia del bug.
                        if (grezzo := delta.get("content")):
                            testo, pensiero_inline = filtro_pensiero.filtra(grezzo)
                            if pensiero_inline:
                                stato["pensiero"] += len(pensiero_inline)
                                yield StreamChunk(reasoning=pensiero_inline)
                            if testo:
                                stato["testo"] += len(testo)
                                testo_accumulato.append(testo)
                                yield StreamChunk(text=testo)

        completo = "".join(testo_accumulato)
        if finish_reason == "length" and not completo.strip():
            raise TruncatedResponse(
                "il modello ha esaurito il budget senza produrre testo: "
                "probabilmente ha speso tutti i token a ragionare. "
                "Aumenta max_tokens o usa un modello senza ragionamento esteso.",
                partial=completo,
                usage=usage,
            )

        # Prima dell'ultimo frammento: chi lo riceve spesso chiude il flusso subito dopo (`genera_flusso`), e una
        # chiamata conclusa non va contata come interrotta.
        stato["esito"] = "ok"
        yield StreamChunk(done=True, usage=usage, finish_reason=finish_reason)

    async def complete(self, request: GenerationRequest) -> str:
        pezzi: List[str] = []
        async for chunk in self.stream(request):
            if chunk.text:
                pezzi.append(chunk.text)
        return "".join(pezzi)

    async def complete_json(self, request: GenerationRequest) -> Any:
        """Genera e interpreta una risposta JSON.

        Mette insieme le tre difese di `json_mode`: negozia il dialetto che il
        server accetta, alza il budget se il modello lo esaurisce ragionando, e
        interpreta con tolleranza ciò che torna.

        Non è streaming perché non avrebbe senso: un JSON parziale non si può
        mostrare, e chi chiama aspetta comunque la struttura completa.
        """
        chiave = (self._base_url, request.model or self._default_model)
        if self._json_schema:
            rigoroso = await self._prova_schema_rigoroso(request, chiave)
            if rigoroso is not None:
                return rigoroso
        if not self._dialetto_negoziato and chiave in _DIALETTI_NOTI:
            self._dialetto_json, self._dialetto_negoziato = _DIALETTI_NOTI[chiave], True
        dialetti = [self._dialetto_json] if self._dialetto_negoziato else list(DIALETTI)
        ultimo_errore: Optional[Exception] = None

        for dialetto in dialetti:
            try:
                testo = await self._genera_con_budget(request, dialetto, richiede_json=True)
            except GenerationError as exc:
                if not e_rifiuto_del_formato(exc):
                    raise
                ultimo_errore = exc
                logger.info(
                    "Il server non accetta response_format '%s': provo il successivo",
                    dialetto,
                )
                continue

            if not self._dialetto_negoziato:
                self._dialetto_json = dialetto
                self._dialetto_negoziato = True
                _DIALETTI_NOTI[chiave] = dialetto
                logger.info(
                    "Modalità JSON negoziata: %s",
                    f"response_format '{dialetto}'" if dialetto
                    else "nessun vincolo formale",
                )
            return estrai_json(testo)

        if len(dialetti) == 1 and _DIALETTI_NOTI.get(chiave, "?") == dialetti[0]:
            # Il dialetto ricordato non va più (server aggiornato allo stesso indirizzo): lo si dimentica e si
            # rinegozia una volta, invece di fallire ogni chiamata fino al riavvio.
            _DIALETTI_NOTI.pop(chiave, None)
            self._dialetto_json, self._dialetto_negoziato = None, False
            return await self.complete_json(request)

        raise GenerationError(
            f"nessuna modalità JSON accettata dal server ({ultimo_errore})"
        )

    async def _prova_schema_rigoroso(self, request: GenerationRequest, chiave: tuple) -> Any:
        """La risposta vincolata allo schema rigoroso della fase (`llm/schemi_json.py`), se il compito l'ha acceso,
        la fase ne ha uno e il server non l'ha già rifiutato. `None`: si negozia come sempre (`json_object`, poi
        `json_schema` permissivo, poi testo). Il rifiuto si ricorda per indirizzo e modello come il dialetto."""
        from .consumi import fase_da
        from .schemi_json import formato_rigoroso

        formato = formato_rigoroso(fase_da(request.messages))
        chiave_rigorosa = (*chiave, "rigoroso")
        if formato is None or _DIALETTI_NOTI.get(chiave_rigorosa) is False:
            return None
        try:
            testo = await self._genera_con_budget(request, "rigoroso", richiede_json=True, formato=formato)
        except GenerationError as exc:
            if not e_rifiuto_del_formato(exc):
                raise
            _DIALETTI_NOTI[chiave_rigorosa] = False
            logger.info("Il server non accetta lo schema JSON rigoroso: si negozia il formato come sempre")
            return None
        if _DIALETTI_NOTI.get(chiave_rigorosa) is not True:
            _DIALETTI_NOTI[chiave_rigorosa] = True
            logger.info("Schema JSON rigoroso accettato dal server")
        return estrai_json(testo)

    async def _genera_con_budget(
        self, request: GenerationRequest, dialetto: Optional[str], *, richiede_json: bool = False,
        formato: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Riprova con più spazio quando il modello esaurisce il budget.

        `richiede_json`: chi chiama (`complete_json`) non si accontenta di un testo qualunque — se
        alla fine non c'è traccia di una struttura JSON, non è "il modello ha risposto in prosa"
        (`_sembra_troncato` non lo segnala perché non è un JSON aperto e mai chiuso): è quasi sempre
        un modello che ragiona in prosa libera, senza tag `<think>` — vedi `FiltroPensieroInline`,
        pensato per quelli con i tag — colto a metà pensiero dal budget, prima ancora di iniziare la
        risposta vera. Bug osservato in produzione (2026-09-30): il validatore dell'intervista
        (`max_tokens=200`) falliva con `JsonNonInterpretabile` — non un `GenerationError`, quindi
        nemmeno il ripiego "il validatore non risponde, la domanda passa" scattava — su una risposta
        che iniziava con `"Here's a thinking process:\\n\\n1. **Analyze User Input:**..."` e non
        arrivava mai al JSON. Vale lo stesso rimedio del JSON troncato: più spazio, non un
        fallimento immediato.
        """
        # Il pavimento per i modelli che ragionano lo applica il costruttore
        # del payload, che vale anche per le chiamate non strutturate: qui
        # basta la scala dei tentativi.
        budget = request.max_tokens or 4096

        for tentativo in range(TENTATIVI_DI_BUDGET + 1):
            richiesta = replace(
                request,
                max_tokens=budget,
                extra={**request.extra, **({"response_format": formato} if formato else _formato(dialetto))},
            )
            try:
                testo = await self.complete(richiesta)
            except TruncatedResponse as exc:
                motivo = str(exc)
            else:
                # Una risposta **con** contenuto ma tagliata a metà non
                # solleva `TruncatedResponse`: quella segnala il caso in cui il
                # modello ha speso tutto a ragionare e non ha scritto nulla.
                # Qui il testo c'è, e per il testo libero sarebbe utilizzabile
                # — ma un JSON interrotto a metà graffa non lo è.
                #
                # È il difetto che ha fatto fallire la digestione del primo
                # corpus: quattro lotti su dodici persi, con in log un JSON
                # che cominciava bene e si fermava a metà. Il budget adattivo
                # c'era e non scattava mai.
                if _sembra_troncato(testo):
                    motivo = "JSON incompleto: struttura non chiusa"
                elif richiede_json and not _contiene_json_valido(testo):
                    # Non basta cercare una graffa: il ragionamento in prosa libera può nominarne
                    # una (es. descrivendo lo schema atteso) senza mai emettere JSON vero — la
                    # verifica deve essere il parser stesso, non un'euristica sulla presenza di un
                    # carattere (bug osservato in produzione: `_contiene_json` diceva "c'è" e
                    # `estrai_json` falliva comunque un attimo dopo, uscendo dal ripiego).
                    motivo = "nessun JSON riconoscibile nella risposta (probabile ragionamento non concluso)"
                else:
                    return testo

            if tentativo == TENTATIVI_DI_BUDGET or budget >= TETTO_TOKEN:
                raise GenerationError(
                    f"il modello non produce una risposta utilizzabile nemmeno "
                    f"con {budget} token: {motivo}"
                )
            budget = prossimo_budget(budget)
            logger.info(
                "Risposta inutilizzabile (%s): riprovo con max_tokens=%d",
                motivo, budget,
            )

        raise GenerationError("budget esaurito")  # pragma: no cover

    # -- interni -----------------------------------------------------------

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    async def _build_payload(
        self, request: GenerationRequest, *, stream: bool
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "model": request.model or await self.resolve_model(),
            "messages": [m.to_dict() for m in request.messages],
            "temperature": request.temperature,
            "stream": stream,
        }
        if request.max_tokens:
            # Il pavimento per i modelli che ragionano vale su **ogni**
            # chiamata, non solo su quelle strutturate: il ragionamento
            # consuma lo stesso budget della risposta, e un tetto calcolato
            # sulla lunghezza attesa della risposta lo esaurisce prima che
            # il modello cominci a scrivere. Il risultato è testo vuoto —
            # nessun errore — e chi chiama ricade sul suo ripiego a ogni
            # tentativo, senza che nulla sembri rotto.
            #
            # È un tetto, non un obiettivo: chi ha finito si ferma, e su un
            # modello che non ragiona la riga non fa nulla.
            payload["max_tokens"] = self._tetto(request.max_tokens)
        if request.stop:
            payload["stop"] = request.stop
        if stream:
            # Senza, molti server non riportano affatto il consumo negli
            # eventi di streaming, e la contabilità dei token resta vuota
            # proprio nel percorso che si usa sempre.
            payload["stream_options"] = {"include_usage": True}
        payload.update(self._parametri)
        payload.update(self._campi_di_cache(request))
        payload.update(request.extra)
        # Sempre, ed esplicito, dopo tutto il resto: il fornitore non conserva le risposte (Nebius può tenerle per la
        # distillazione se non glielo si dice). Lo dice anche l'informativa privacy.
        payload["store"] = False
        return payload

    def _tetto(self, visibile: int) -> int:
        """Il `max_tokens` della richiesta. Un modello che non ragiona: il tetto visibile. Con un livello acceso: il
        tetto visibile più il margine del livello (`ragionamento.tetto_con_ragionamento`, configurabile), così il
        ragionamento non si mangia la risposta. Un fornitore di prima dei livelli che ragiona: il pavimento di sempre."""
        if not self.ragiona:
            return visibile
        if ragiona_da_livello(self.livello_ragionamento or None):
            return tetto_con_ragionamento(visibile, self.livello_ragionamento, self._parametri)
        return max(visibile, pavimento_ragionamento(self._parametri))

    def _campi_di_cache(self, request: GenerationRequest) -> Dict[str, Any]:
        """Traduce l'indicazione di cache nei campi che questo motore capisce.

        Solo quelli che il motore conosce, e solo per lui: vLLM rifiuta o
        segnala i campi sconosciuti, e mandare `cache_prompt` a OpenAI o
        `prompt_cache_key` a un llama.cpp sarebbe nel migliore dei casi
        inutile e nel peggiore un 400 su ogni risposta.
        """
        suggerimento = request.cache
        if suggerimento is None or suggerimento.modo == "none":
            return {}

        if self.motore == "llamacpp" and suggerimento.modo == "kv":
            campi: Dict[str, Any] = {"cache_prompt": True}
            if suggerimento.slot is not None:
                campi["id_slot"] = suggerimento.slot
            return campi

        if self.motore == "openai" and suggerimento.modo == "prompt":
            # Il caching di OpenAI è automatico sopra i 1024 token; la chiave
            # instrada le richieste con lo stesso prefisso verso la stessa
            # macchina, dove il prefisso è già in cache.
            return {"prompt_cache_key": suggerimento.chiave}

        # vLLM e LM Studio riusano il prefisso da sé: non serve nessun campo.
        return {}

    @staticmethod
    def _parse_usage(uso: Dict[str, Any], model: str) -> Usage:
        dettagli = uso.get("prompt_tokens_details") or {}
        uscita = uso.get("completion_tokens_details") or {}
        return Usage(
            prompt_tokens=uso.get("prompt_tokens", 0) or 0,
            completion_tokens=uso.get("completion_tokens", 0) or 0,
            cached_tokens=dettagli.get("cached_tokens", 0) or 0,
            total_tokens=uso.get("total_tokens", 0) or 0,
            # `completion_tokens_details.reasoning_tokens` (OpenAI, LM Studio, vLLM); alcuni servizi lo mettono in
            # cima a `usage`.
            reasoning_tokens=uscita.get("reasoning_tokens") or uso.get("reasoning_tokens") or 0,
            model=model,
        )


def riconosci_motore(base_url: str, configurato: str = "auto") -> str:
    """Che motore sta dietro un indirizzo OpenAI-compatibile.

    Dall'indirizzo si riconoscono con sicurezza solo i casi comuni: OpenAI dal
    dominio, LM Studio e llama.cpp dalle loro porte predefinite. Un vLLM o un
    llama.cpp dietro un nome qualunque restano `other` — cioè prezzo pieno —
    finché qualcuno non lo dichiara in `TAROT_LLM_ENGINE`. Indovinare un
    motore con cache e sbagliare manderebbe campi che il server rifiuta.
    """
    if configurato and configurato != "auto":
        return configurato

    indirizzo = base_url.lower()
    if "api.openai.com" in indirizzo:
        return "openai"
    if ":1234" in indirizzo:
        return "lmstudio"
    if ":8080" in indirizzo and ("127.0.0.1" in indirizzo or "localhost" in indirizzo):
        return "llamacpp"
    return "other"


def _formato(dialetto: Optional[str]) -> Dict[str, Any]:
    """Il frammento di payload che impone il formato, o niente."""
    formato = formato_risposta(dialetto)
    return {"response_format": formato} if formato else {}


def _sembra_troncato(testo: str) -> bool:
    """Vero se il testo è un JSON cominciato e mai chiuso.

    Conta le parentesi fuori dalle stringhe: se ne restano di aperte, la
    risposta si è interrotta. Non è un parser — non serve — ma distingue il
    caso che conta da un modello che ha semplicemente risposto in prosa,
    dove riprovare con più spazio non cambierebbe nulla.
    """
    pulito = testo.strip()
    if not pulito.startswith(("{", "[", "```")):
        return False

    aperte = 0
    in_stringa = False
    fuga = False

    for carattere in pulito:
        if fuga:
            fuga = False
            continue
        if carattere == "\\":
            fuga = True
        elif carattere == '"':
            in_stringa = not in_stringa
        elif not in_stringa and carattere in "{[":
            aperte += 1
        elif not in_stringa and carattere in "}]":
            aperte -= 1

    return aperte > 0 or in_stringa


def _contiene_json_valido(testo: str) -> bool:
    """Vero se `estrai_json` riesce davvero a interpretare il testo.

    Deliberatamente il parser stesso, non un'euristica sulla presenza di `{`/`[`: un modello che
    ragiona in prosa libera può nominare una graffa (descrivendo lo schema atteso) senza mai
    emettere JSON vero — un controllo sulla sola presenza del carattere direbbe "c'è" e lascerebbe
    poi fallire `estrai_json` un attimo dopo, fuori da questo ripiego."""
    try:
        estrai_json(testo)
    except JsonNonInterpretabile:
        return False
    return True
