"""Il registro dei consumi delle chiamate ai modelli (`llm/consumi.py`).

Nessun modello vero: il server OpenAI-compatibile è un trasporto finto di httpx che risponde in SSE, con l'`usage`
nell'ultimo evento come fa un server con `stream_options.include_usage`. Si prova che

- una chiamata JSON e una in streaming finiscono nel registro col compito, la fase, la lettura e i token (compresi
  quelli in cache e di ragionamento);
- un errore di scrittura del registro non rompe la chiamata, e una chiamata fallita resta contata;
- la riga arriva davvero in `llm_consumi`.
"""
from __future__ import annotations

import json
import uuid

import httpx
import pytest

from tarot_core.llm import consumi, openai_compatible
from tarot_core.llm.base import GenerationError, GenerationRequest, Message
from tarot_core.llm.compiti import Compito
from tarot_core.llm.openai_compatible import OpenAICompatibleProvider
from tarot_core.tarot.llm import genera_flusso, genera_json, richiesta

from .conftest import avvisi_di, richiede_database

USO = {
    "prompt_tokens": 812, "completion_tokens": 540, "total_tokens": 1352,
    "prompt_tokens_details": {"cached_tokens": 512},
    "completion_tokens_details": {"reasoning_tokens": 500},
}


def _sse(testo: str, *, pensiero: str = "", usage=USO, finish: str = "stop") -> bytes:
    eventi = []
    if pensiero:
        eventi.append({"choices": [{"delta": {"reasoning": pensiero}}]})
    for i in range(0, len(testo), 7):
        eventi.append({"choices": [{"delta": {"content": testo[i:i + 7]}}]})
    eventi.append({"choices": [{"delta": {}, "finish_reason": finish}]})
    if usage is not None:
        eventi.append({"choices": [], "usage": usage})
    righe = [f"data: {json.dumps(e)}\n\n" for e in eventi] + ["data: [DONE]\n\n"]
    return "".join(righe).encode()


@pytest.fixture
def server(monkeypatch):
    """Un server OpenAI-compatibile finto: `server.risposte` è la coda dei corpi SSE, `server.richieste` i payload."""

    class Server:
        risposte: list = []
        richieste: list = []
        stato = 200

    def gestisci(request: httpx.Request) -> httpx.Response:
        Server.richieste.append(json.loads(request.content))
        if Server.stato >= 400:
            return httpx.Response(Server.stato, text="guasto")
        return httpx.Response(200, content=Server.risposte.pop(0), headers={"content-type": "text/event-stream"})

    originale = httpx.AsyncClient

    class ClientFinto(originale):
        def __init__(self, *a, **k):
            k["transport"] = httpx.MockTransport(gestisci)
            super().__init__(*a, **k)

    monkeypatch.setattr(openai_compatible.httpx, "AsyncClient", ClientFinto)
    Server.risposte, Server.richieste, Server.stato = [], [], 200
    return Server


@pytest.fixture
def registro(monkeypatch):
    """Il registro acceso, con uno scrittore che raccoglie invece di scrivere in tabella."""
    from tarot_core.settings import get_settings

    monkeypatch.setenv("TAROT_CONSUMI_LLM", "true")
    get_settings.cache_clear()
    scritti: list = []

    async def scrivi(consumo):
        scritti.append(consumo)

    precedente = consumi.imposta_scrittore(scrivi)
    yield scritti
    consumi.imposta_scrittore(precedente)
    get_settings.cache_clear()


def _fornitore(**k) -> OpenAICompatibleProvider:
    return OpenAICompatibleProvider(
        base_url="http://finto/v1", api_key="x", default_model="nemotron", name="prova", motore="other",
        ragiona=True, parametri={"reasoning_budget": 1024, "chat_template_kwargs": {"enable_thinking": True}}, **k,
    )


async def test_una_chiamata_json_si_registra_con_compito_lettura_e_token(server, registro):
    lettura = uuid.uuid4()
    server.risposte.append(_sse('{"valida": true, "motivo": "ok"}', pensiero="penso..."))
    fornitore = consumi.misurato(_fornitore(), Compito.VALIDAZIONE, lettura=lettura)

    dati = await genera_json(fornitore, richiesta(["# Compito: validazione\n\nregole"], "Quesito: x", max_tokens=200))
    await consumi.attendi_scritture()

    assert dati == {"valida": True, "motivo": "ok"}
    assert len(registro) == 1
    c = registro[0]
    assert (c.compito, c.fase, c.fornitore, c.modello) == ("validazione", "validazione", "prova", "nemotron")
    assert (c.token_ingresso, c.token_cache, c.token_uscita, c.token_ragionamento) == (812, 512, 540, 500)
    assert c.esito == "ok" and c.finish_reason == "stop" and c.usage_riportato and not c.streaming
    assert c.reading_id == str(lettura)
    assert c.caratteri_ragionamento == len("penso...") and c.caratteri_uscita > 0
    assert c.caratteri_sistema == len("# Compito: validazione\n\nregole")
    # Il pavimento del ragionamento: reasoning_budget + margine, come in produzione.
    assert c.max_tokens == 1024 + 2048
    # L'etichetta non va mai al fornitore.
    assert "etichetta" not in server.richieste[0]
    assert server.richieste[0]["stream_options"] == {"include_usage": True}


async def test_una_chiamata_in_streaming_si_registra_come_tale(server, registro):
    server.risposte.append(_sse("La carta parla di un nuovo inizio."))
    fornitore = consumi.misurato(_fornitore(), "interpretazione", lettura=str(uuid.uuid4()))

    testo = "".join([p async for p in genera_flusso(fornitore, richiesta(
        ["# Compito: interpretazione\n\nregole"], "Carta: il Matto", max_tokens=500,
    ))])
    await consumi.attendi_scritture()

    assert testo == "La carta parla di un nuovo inizio."
    c = registro[-1]
    assert c.streaming and c.compito == "interpretazione" and c.fase == "interpretazione"
    # `genera_flusso` chiude il flusso appena arriva l'ultimo frammento: la chiamata è conclusa, non interrotta.
    assert c.esito == "ok" and c.token_uscita == 540


async def test_senza_usage_restano_i_caratteri(server, registro):
    server.risposte.append(_sse("testo", usage=None))
    await _fornitore().complete(GenerationRequest(messages=[Message("user", "ciao")], max_tokens=50))
    await consumi.attendi_scritture()

    c = registro[-1]
    assert not c.usage_riportato and c.token_uscita == 0 and c.caratteri_uscita == len("testo")
    assert c.compito == ""          # chiamata fuori da `provider_per`: si conta lo stesso, senza compito


async def test_un_errore_di_scrittura_non_rompe_la_chiamata(server, monkeypatch):
    from tarot_core.settings import get_settings

    monkeypatch.setenv("TAROT_CONSUMI_LLM", "true")
    get_settings.cache_clear()

    async def guasto(consumo):
        raise RuntimeError("database giù")

    precedente = consumi.imposta_scrittore(guasto)
    monkeypatch.setattr(consumi, "_errori_scrittura", 0)
    try:
        server.risposte.append(_sse('{"esito": "ok", "violazioni": []}'))
        with avvisi_di(consumi) as avvisi:
            dati = await genera_json(
                consumi.misurato(_fornitore(), Compito.GIUDIZIO), richiesta(["# Compito: giudizio"], "responso"),
            )
            await consumi.attendi_scritture()
    finally:
        consumi.imposta_scrittore(precedente)
        get_settings.cache_clear()

    assert dati["esito"] == "ok"
    assert any("database giù" in a for a in avvisi)


async def test_un_ascoltatore_che_fallisce_non_rompe_la_chiamata(server, registro):
    def rotto(consumo):
        raise ValueError("no")

    server.risposte.append(_sse("ciao"))
    with consumi.ascolta(rotto):
        testo = await _fornitore().complete(GenerationRequest(messages=[Message("user", "x")], max_tokens=20))
    assert testo == "ciao"


async def test_una_chiamata_fallita_resta_contata(server, registro):
    server.stato = 500
    with pytest.raises(GenerationError):
        await consumi.misurato(_fornitore(), Compito.SINTESI).complete(
            GenerationRequest(messages=[Message("system", "# Compito: sintesi"), Message("user", "x")], max_tokens=10),
        )
    await consumi.attendi_scritture()
    c = registro[-1]
    assert c.esito == "errore" and "500" in c.errore and c.compito == "sintesi"


async def test_spento_non_scrive_ma_gli_ascoltatori_ricevono(server):
    visti: list = []
    server.risposte.append(_sse("ciao"))
    with consumi.ascolta(visti.append):
        await _fornitore().complete(GenerationRequest(messages=[Message("user", "x")], max_tokens=20))
    await consumi.attendi_scritture()
    assert len(visti) == 1 and not consumi._in_volo


async def test_embed_si_registra_col_compito(monkeypatch, registro):
    def gestisci(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={
            "data": [{"index": 0, "embedding": [0.1, 0.2]}], "usage": {"prompt_tokens": 9, "total_tokens": 9},
        })

    originale = httpx.AsyncClient

    class ClientFinto(originale):
        def __init__(self, *a, **k):
            k["transport"] = httpx.MockTransport(gestisci)
            super().__init__(*a, **k)

    monkeypatch.setattr(openai_compatible.httpx, "AsyncClient", ClientFinto)
    fornitore = consumi.misurato(_fornitore(embed_model="emb"), Compito.EMBEDDING, riferimento="apertura")
    assert await fornitore.embed(["quesito"]) == [[0.1, 0.2]]
    await consumi.attendi_scritture()
    c = registro[-1]
    assert (c.compito, c.fase, c.riferimento, c.token_ingresso, c.modello) == (
        "embedding", "embedding", "apertura", 9, "emb")


def test_la_fase_viene_dal_prompt():
    def fase(sistema, utente="x"):
        return consumi.fase_da([Message("system", sistema), Message("user", utente)])

    assert fase("# Compito: teaser\n\n...") == "teaser"
    assert fase("# Compito: sintesi\n\n...", "...\n## Correzioni richieste\n- ...") == "sintesi.revisione"
    assert fase("# Compito: intervista\n...", "Colloquio: ...\nL'intervista è conclusa: ...") == "intervista.riassunto"
    assert fase("nessuna intestazione") == ""


def test_provider_per_avvolge_senza_inventare_metodi(monkeypatch):
    """Il fornitore misurato ha `embed` e `complete_json` solo se li ha quello avvolto: `supporta_embedding()` e
    `genera_json` guardano proprio questo."""
    from tarot_core.api import deps
    from tarot_core.llm.base import supporta_embedding
    from tarot_core.settings import get_settings

    monkeypatch.setenv("TAROT_LLM_FINTO", "true")
    get_settings.cache_clear()
    deps.reset_dependencies()
    try:
        fornitore = deps.provider_per(Compito.EMBEDDING, lettura=uuid.uuid4())
        assert isinstance(fornitore, consumi.ProviderMisurato)
        assert not supporta_embedding(fornitore)          # il modello finto non vettorizza
        assert hasattr(fornitore, "complete_json")
    finally:
        deps.reset_dependencies()
        get_settings.cache_clear()


async def test_l_etichetta_attraversa_i_nomi_protetti(registro):
    """Con le persone di una lettura di coppia il fornitore è avvolto due volte (pseudonimi, poi consumi): l'etichetta
    con la lettura arriva comunque a chi registra."""
    from tarot_core.tarot.pseudonimi import Pseudonimi, ProviderProtetto

    viste: list = []

    class Spia:
        async def complete(self, req):
            viste.append(req)
            return "ok"

    lettura = uuid.uuid4()
    fornitore = consumi.misurato(ProviderProtetto(Spia(), Pseudonimi(["Marco"])), Compito.SINTESI, lettura=lettura)
    await fornitore.complete(GenerationRequest(messages=[Message("user", "Marco e io")]))
    assert viste[0].etichetta["lettura"] == str(lettura) and viste[0].etichetta["compito"] == "sintesi"
    assert "Marco" not in viste[0].messages[0].content


@richiede_database
async def test_la_riga_arriva_in_tabella(session_factory, monkeypatch):
    from sqlalchemy import select

    from tarot_core.domain import session as modulo_sessione
    from tarot_core.domain.consumi_models import LlmConsumo

    monkeypatch.setattr(modulo_sessione, "get_session_factory", lambda: session_factory)
    lettura = uuid.uuid4()
    await consumi._scrivi_db(consumi.Consumo(
        compito="sintesi", fase="sintesi", fornitore="prova", modello="m", token_ingresso=3000, token_uscita=900,
        token_ragionamento=400, reading_id=str(lettura), usage_riportato=True, errore="x" * 400,
    ))
    async with session_factory() as s:
        riga = (await s.execute(select(LlmConsumo).where(LlmConsumo.reading_id == lettura))).scalar_one()
    assert (riga.compito, riga.token_ingresso, riga.token_ragionamento) == ("sintesi", 3000, 400)
    assert len(riga.errore) == 300
