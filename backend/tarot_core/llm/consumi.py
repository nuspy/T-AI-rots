"""Il registro dei consumi: quanti token costa ogni chiamata a un modello, e per quale compito.

**Perché qui e non nei router.** Il punto in cui il consumo si conosce davvero è il client del fornitore: lì arriva
l'`usage` della risposta (ingresso, cache, uscita, ragionamento), lì si vede ogni ripetizione — il budget che si alza
quando il modello ragiona troppo, il dialetto JSON negoziato, la sintesi riscritta. Il router sa invece *perché* si
chiama il modello (il compito, la lettura): glielo dice `ProviderMisurato`, che avvolge il fornitore in
`api/deps.provider_per()` e scrive un'`etichetta` sulla richiesta. L'etichetta non va mai al fornitore.

**Mai rallentare, mai rompere.** La scrittura in `llm_consumi` parte in background (`asyncio.create_task`) con una
sessione propria, dopo che la chiamata è finita; ogni errore — database giù, tabella mancante, qualunque cosa — si
annota nel log e si dimentica. Una lettura non aspetta mai il registro e non fallisce mai per colpa sua.

**Cosa si registra.** Solo numeri, il compito, la fase e l'id della lettura: mai il testo dei prompt né delle risposte.
La fase è il «# Compito: …» del primo messaggio di sistema (il teaser, senza assegnazione, gira col fornitore della
sintesi ma ha un compito suo, `teaser`), con due suffissi per i casi che lo stesso prompt non distingue: `intervista.riassunto` e
`sintesi.revisione`.

Gli ascoltatori (`ascolta()`) ricevono ogni consumo anche senza database: servono a `tools/misura_costi.py` e ai test.
"""
from __future__ import annotations

import asyncio
import contextlib
import contextvars
import logging
import re
import uuid
from dataclasses import asdict, dataclass, field, replace
from typing import Any, Awaitable, Callable, Dict, Iterator, List, Optional, Set

from .base import GenerationRequest, Message

logger = logging.getLogger(__name__)


@dataclass
class Consumo:
    """Una chiamata a un modello, come finisce in `llm_consumi` (vedi `domain/consumi_models.LlmConsumo`)."""

    compito: str = ""
    fase: str = ""
    fornitore: str = ""
    modello: str = ""
    token_ingresso: int = 0
    token_cache: int = 0
    token_uscita: int = 0
    token_ragionamento: int = 0
    caratteri_ingresso: int = 0
    caratteri_uscita: int = 0
    caratteri_ragionamento: int = 0
    caratteri_sistema: int = 0
    max_tokens: Optional[int] = None
    durata_ms: int = 0
    esito: str = "ok"
    finish_reason: str = ""
    streaming: bool = False
    usage_riportato: bool = False
    reading_id: Optional[str] = None
    riferimento: str = ""
    errore: str = ""
    #: Solo per gli ascoltatori (non va in tabella): i parametri che hanno deciso il ragionamento.
    extra: Dict[str, Any] = field(default_factory=dict)

    def riga(self) -> Dict[str, Any]:
        """I campi della tabella."""
        dati = asdict(self)
        dati.pop("extra", None)
        dati["reading_id"] = _uuid_o_nulla(self.reading_id)
        for nome, lunghezza in (("compito", 40), ("fase", 40), ("fornitore", 80), ("modello", 160),
                                ("esito", 20), ("finish_reason", 20), ("riferimento", 80), ("errore", 300)):
            dati[nome] = (dati[nome] or "")[:lunghezza]
        return dati


def _uuid_o_nulla(valore: Any) -> Optional[uuid.UUID]:
    if valore is None or valore == "":
        return None
    if isinstance(valore, uuid.UUID):
        return valore
    try:
        return uuid.UUID(str(valore))
    except ValueError:
        return None


# ---- la fase, dal prompt ---------------------------------------------------------------------------------------

_INTESTAZIONE = re.compile(r"^#\s*Compito:\s*([\w.-]+)", re.MULTILINE)


def fase_da(messaggi: List[Message]) -> str:
    """Il «# Compito: …» del primo messaggio di sistema, con i suffissi dei casi che il prompt non distingue."""
    sistema = next((m.content for m in messaggi if m.role == "system"), "")
    trovato = _INTESTAZIONE.search(sistema[:200])
    if not trovato:
        return ""
    fase = trovato.group(1)
    utente = next((m.content for m in reversed(messaggi) if m.role == "user"), "")
    if fase == "intervista" and "L'intervista è conclusa" in utente:
        return "intervista.riassunto"
    if fase == "sintesi" and "## Correzioni richieste" in utente:
        return "sintesi.revisione"
    return fase


# ---- chi ascolta e chi scrive ----------------------------------------------------------------------------------

_ascoltatori: List[Callable[[Consumo], None]] = []
_in_volo: Set[asyncio.Task] = set()
_errori_scrittura = 0


async def _scrivi_db(consumo: Consumo) -> None:
    from ..domain.consumi_models import LlmConsumo
    from ..domain.session import get_session_factory

    async with get_session_factory()() as sessione:
        sessione.add(LlmConsumo(**consumo.riga()))
        await sessione.commit()


_scrittore: Callable[[Consumo], Awaitable[None]] = _scrivi_db


def imposta_scrittore(scrittore: Optional[Callable[[Consumo], Awaitable[None]]]) -> Callable[[Consumo], Awaitable[None]]:
    """Sostituisce chi scrive in tabella (i test, lo script delle misure). `None` rimette quello vero. Restituisce il
    precedente, per rimetterlo."""
    global _scrittore
    precedente = _scrittore
    _scrittore = scrittore or _scrivi_db
    return precedente


@contextlib.contextmanager
def ascolta(funzione: Callable[[Consumo], None]) -> Iterator[None]:
    """Fa ricevere a `funzione` ogni consumo registrato finché il blocco è aperto."""
    _ascoltatori.append(funzione)
    try:
        yield
    finally:
        with contextlib.suppress(ValueError):
            _ascoltatori.remove(funzione)


def _attivo() -> bool:
    try:
        from ..settings import get_settings

        return bool(get_settings().consumi_llm)
    except Exception:  # noqa: BLE001 - impostazioni illeggibili: meglio non scrivere che rompere
        return False


def registra(consumo: Consumo) -> None:
    """Annota un consumo: agli ascoltatori subito, in tabella in background. Non solleva mai."""
    try:
        for funzione in list(_ascoltatori):
            try:
                funzione(consumo)
            except Exception:  # noqa: BLE001
                logger.debug("Ascoltatore dei consumi fallito", exc_info=True)
        if not _attivo():
            return
        try:
            ciclo = asyncio.get_running_loop()
        except RuntimeError:
            return
        compito = ciclo.create_task(_scrivi_sicuro(consumo))
        _in_volo.add(compito)
        compito.add_done_callback(_in_volo.discard)
    except Exception:  # noqa: BLE001 - il registro non deve mai toccare la chiamata
        logger.debug("Consumo non registrato", exc_info=True)


async def _scrivi_sicuro(consumo: Consumo) -> None:
    global _errori_scrittura
    try:
        await _scrittore(consumo)
    except asyncio.CancelledError:
        return
    except Exception as exc:  # noqa: BLE001
        _errori_scrittura += 1
        # Un database giù farebbe una riga di log per chiamata: si dice la prima volta e poi ogni cento.
        if _errori_scrittura == 1 or _errori_scrittura % 100 == 0:
            logger.warning("Consumo LLM non scritto (%d finora): %s", _errori_scrittura, exc)


async def attendi_scritture(timeout: float = 10.0) -> None:
    """Aspetta che le scritture in volo finiscano (lo script delle misure, i test). In produzione non serve."""
    in_corso = [t for t in _in_volo if not t.done()]
    if in_corso:
        await asyncio.wait(in_corso, timeout=timeout)


# ---- l'etichetta: compito e lettura -----------------------------------------------------------------------------

#: Per `embed()`, che non riceve una `GenerationRequest`: l'etichetta passa da qui, solo per la durata della chiamata.
_etichetta_embed: contextvars.ContextVar[Dict[str, Any]] = contextvars.ContextVar("etichetta_embed", default={})


def etichetta_embed() -> Dict[str, Any]:
    return _etichetta_embed.get()


class ProviderMisurato:
    """Un fornitore che dice al registro dei consumi per quale compito e per quale lettura lavora.

    Non cambia nulla della richiesta che arriva al modello: aggiunge solo `etichetta`, che il fornitore legge quando
    registra la chiamata e non manda. `complete_json` ed `embed` esistono solo se il fornitore avvolto li ha (vedi
    `supporta_embedding()` e `tarot/llm.genera_json`, che guardano proprio questo)."""

    def __init__(self, fornitore: Any, compito: str, *, lettura: Any = None, riferimento: str = "") -> None:
        self._fornitore = fornitore
        self._etichetta = {
            "compito": compito,
            "lettura": str(lettura) if lettura else None,
            "riferimento": riferimento,
        }

    def __getattr__(self, nome: str) -> Any:
        valore = getattr(self._fornitore, nome)
        if nome == "complete_json":
            async def complete_json(req: GenerationRequest, *argomenti, **opzioni):
                return await valore(self._richiesta(req, streaming=False), *argomenti, **opzioni)

            return complete_json
        if nome == "embed":
            async def embed(testi, *argomenti, **opzioni):
                segno = _etichetta_embed.set(dict(self._etichetta))
                try:
                    return await valore(testi, *argomenti, **opzioni)
                finally:
                    _etichetta_embed.reset(segno)

            return embed
        return valore

    def _richiesta(self, req: GenerationRequest, *, streaming: bool) -> GenerationRequest:
        return replace(req, etichetta={**req.etichetta, **self._etichetta, "streaming": streaming})

    async def complete(self, req: GenerationRequest) -> str:
        return await self._fornitore.complete(self._richiesta(req, streaming=False))

    async def stream(self, req: GenerationRequest):
        async for pezzo in self._fornitore.stream(self._richiesta(req, streaming=True)):
            yield pezzo


def misurato(fornitore: Any, compito: Any, *, lettura: Any = None, riferimento: str = "") -> Any:
    """Il fornitore avvolto per il registro. `compito` è un `Compito` o il suo valore."""
    valore = getattr(compito, "value", compito) or ""
    return ProviderMisurato(fornitore, str(valore), lettura=lettura, riferimento=riferimento)


def _caratteri_sistema(messaggi: List[Message]) -> int:
    """I caratteri dei messaggi di sistema in testa: il prefisso stabile (in questa piattaforma i prompt di sistema non
    portano mai dati della lettura, vedi `tarot/cag.py`)."""
    totale = 0
    for m in messaggi:
        if m.role != "system":
            break
        totale += len(m.content)
    return totale


def consumo_da(
    req: Optional[GenerationRequest], *, fornitore: str, modello: str, usage: Any = None, durata_ms: int = 0,
    esito: str = "ok", finish_reason: str = "", caratteri_uscita: int = 0, caratteri_ragionamento: int = 0,
    max_tokens: Optional[int] = None, errore: str = "", etichetta: Optional[Dict[str, Any]] = None,
    caratteri_ingresso: Optional[int] = None, extra: Optional[Dict[str, Any]] = None,
) -> Consumo:
    """Mette insieme un `Consumo` da ciò che il fornitore sa alla fine di una chiamata."""
    etichetta = dict(etichetta if etichetta is not None else (req.etichetta if req is not None else {}))
    messaggi = req.messages if req is not None else []
    return Consumo(
        compito=str(etichetta.get("compito") or ""),
        fase=fase_da(messaggi) if messaggi else str(etichetta.get("fase") or ""),
        fornitore=fornitore,
        modello=(getattr(usage, "model", "") or modello) if usage is not None else modello,
        token_ingresso=int(getattr(usage, "prompt_tokens", 0) or 0),
        token_cache=int(getattr(usage, "cached_tokens", 0) or 0),
        token_uscita=int(getattr(usage, "completion_tokens", 0) or 0),
        token_ragionamento=int(getattr(usage, "reasoning_tokens", 0) or 0),
        caratteri_ingresso=(
            caratteri_ingresso if caratteri_ingresso is not None else sum(len(m.content) for m in messaggi)
        ),
        caratteri_uscita=caratteri_uscita,
        caratteri_ragionamento=caratteri_ragionamento,
        caratteri_sistema=_caratteri_sistema(messaggi),
        max_tokens=max_tokens,
        durata_ms=durata_ms,
        esito=esito,
        finish_reason=finish_reason or "",
        streaming=bool(etichetta.get("streaming", False)),
        usage_riportato=usage is not None,
        reading_id=etichetta.get("lettura"),
        riferimento=str(etichetta.get("riferimento") or ""),
        errore=errore,
        extra=dict(extra or {}),
    )
