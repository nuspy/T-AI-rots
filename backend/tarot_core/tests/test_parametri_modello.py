"""I `parametri` di un modello: campi che vanno in ogni richiesta (il ragionamento si regola lì, non al caricamento).

Lo stesso modello fisico si dichiara due volte, con e senza ragionamento, e la console assegna l'uno o l'altro a
ciascun compito: le richieste restano sullo stesso modello caricato, quindi nessun ricaricamento a metà lettura."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from tarot_core.llm.base import GenerationError, GenerationRequest, Message
from tarot_core.llm.compiti import AssegnazioneModello, Compito, ModelloConfigurato, RegistroModelli
from tarot_core.llm.openai_compatible import OpenAICompatibleProvider

SPENTO = {"chat_template_kwargs": {"enable_thinking": False}}


def _richiesta(**extra):
    return GenerationRequest(messages=[Message("user", "ciao")], max_tokens=200, temperature=0.0, extra=extra)


async def test_i_parametri_del_modello_entrano_in_ogni_richiesta():
    p = OpenAICompatibleProvider(base_url="http://x/v1", default_model="m", parametri=SPENTO)
    for flusso in (True, False):
        payload = await p._build_payload(_richiesta(), stream=flusso)
        assert payload["chat_template_kwargs"] == {"enable_thinking": False}
        assert payload["model"] == "m" and payload["max_tokens"] == 200 and payload["stream"] is flusso


async def test_senza_parametri_la_richiesta_e_quella_di_prima():
    p = OpenAICompatibleProvider(base_url="http://x/v1", default_model="m")
    payload = await p._build_payload(_richiesta(), stream=False)
    assert set(payload) == {"model", "messages", "temperature", "stream", "max_tokens"}


async def test_i_campi_della_singola_richiesta_prevalgono_sui_parametri_del_modello():
    p = OpenAICompatibleProvider(base_url="http://x/v1", default_model="m", parametri={"reasoning_effort": "low", "top_k": 20})
    payload = await p._build_payload(_richiesta(reasoning_effort="high"), stream=False)
    assert payload["reasoning_effort"] == "high" and payload["top_k"] == 20


async def test_il_ragionamento_acceso_alza_il_budget_lo_spento_no():
    ragiona = OpenAICompatibleProvider(base_url="http://x/v1", default_model="m", ragiona=True)
    diretto = OpenAICompatibleProvider(base_url="http://x/v1", default_model="m", parametri=SPENTO)
    assert (await ragiona._build_payload(_richiesta(), stream=False))["max_tokens"] >= 6144
    assert (await diretto._build_payload(_richiesta(), stream=False))["max_tokens"] == 200


@pytest.mark.parametrize("campo", ["model", "messages", "stream", "stream_options", "stop", "temperature", "max_tokens"])
def test_i_campi_che_scrive_l_applicazione_non_si_possono_toccare(campo):
    with pytest.raises(ValidationError) as e:
        ModelloConfigurato(nome="x", parametri={campo: 1})
    assert campo in str(e.value)


def test_lo_stesso_modello_con_e_senza_ragionamento_si_assegna_per_compito():
    modelli = [
        ModelloConfigurato(nome="qwen-ragiona", base_url="http://x/v1", model="qwen", ragiona=True, motore="lmstudio"),
        ModelloConfigurato(nome="qwen-diretto", base_url="http://x/v1", model="qwen", parametri=SPENTO, motore="lmstudio"),
    ]
    registro = RegistroModelli(modelli, assegnazioni={"interpretazione": "qwen-ragiona", "validazione": "qwen-diretto"})
    ragiona, diretto = registro._fornitore("qwen-ragiona"), registro._fornitore("qwen-diretto")
    assert ragiona.ragiona is True and ragiona._parametri == {}
    assert diretto.ragiona is False and diretto._parametri == SPENTO


def test_override_per_compito_non_si_scambiano_fra_loro_sullo_stesso_fornitore():
    """v7: due compiti sullo stesso fornitore, uno forzato a ragionare e l'altro no — bug reale
    evitato: la cache di `_fornitore()` è per nome di fornitore, un override deve passare da un
    percorso che non la tocca (`_fornitore_override`), altrimenti il secondo `per()` chiamato
    restituirebbe l'oggetto (e il `ragiona`) del primo."""
    modello = ModelloConfigurato(nome="unico", base_url="http://x/v1", model="m", ragiona=False)
    registro = RegistroModelli([modello], assegnazioni={
        Compito.SINTESI: AssegnazioneModello("unico", ragiona_override=True),
        Compito.INTERPRETAZIONE: AssegnazioneModello("unico", ragiona_override=False),
    })
    con_ragionamento = registro.per(Compito.SINTESI)
    senza_ragionamento = registro.per(Compito.INTERPRETAZIONE)
    assert con_ragionamento.ragiona is True
    assert senza_ragionamento.ragiona is False


def test_senza_override_lassegnazione_usa_il_ragiona_del_fornitore():
    modello = ModelloConfigurato(nome="unico", base_url="http://x/v1", model="m", ragiona=True)
    registro = RegistroModelli([modello], assegnazioni={
        Compito.SINTESI: AssegnazioneModello("unico"),
    })
    assert registro.per(Compito.SINTESI).ragiona is True


def test_il_modello_ricavato_dalle_vecchie_impostazioni_porta_i_suoi_parametri(monkeypatch):
    from tarot_core.llm.compiti import modelli_da_impostazioni
    from tarot_core.settings import get_settings

    monkeypatch.setenv("TAROT_LLM_PARAMETRI", '{"reasoning_effort": "low"}')
    get_settings.cache_clear()
    try:
        assert modelli_da_impostazioni()[0].parametri == {"reasoning_effort": "low"}
    finally:
        monkeypatch.delenv("TAROT_LLM_PARAMETRI")
        get_settings.cache_clear()


ACCESO = {"reasoning_budget": 16384, "chat_template_kwargs": {"enable_thinking": True}}


def test_ragiona_spento_per_compito_spegne_davvero_il_ragionamento_del_modello():
    """Bug reale in produzione (2026-09-30): `ragiona_override=False` toglieva solo il margine di
    budget lato app, ma il fornitore continuava a mandare `enable_thinking: true` — il modello
    ragionava sempre (lento) e il ragionamento finiva come testo nelle carte."""
    modello = ModelloConfigurato(nome="n", base_url="http://x/v1", model="m", ragiona=True, parametri=ACCESO)
    registro = RegistroModelli([modello], assegnazioni={
        Compito.INTERPRETAZIONE: AssegnazioneModello("n", ragiona_override=False),
        Compito.SINTESI: AssegnazioneModello("n", ragiona_override=True),
    })
    spento = registro.per(Compito.INTERPRETAZIONE)
    acceso = registro.per(Compito.SINTESI)
    assert spento._parametri["chat_template_kwargs"] == {"enable_thinking": False}
    assert "reasoning_budget" not in spento._parametri
    assert acceso._parametri["chat_template_kwargs"] == {"enable_thinking": True}
    assert acceso._parametri["reasoning_budget"] == 16384


def test_fornitore_senza_override_con_ragiona_falso_non_manda_enable_thinking_vero():
    modello = ModelloConfigurato(nome="n", base_url="http://x/v1", model="m", ragiona=False, parametri=ACCESO)
    registro = RegistroModelli([modello], assegnazioni={Compito.INTERVISTA: AssegnazioneModello("n")})
    assert registro.per(Compito.INTERVISTA)._parametri["chat_template_kwargs"] == {"enable_thinking": False}


def test_il_parametri_override_esplicito_resta_l_ultima_parola():
    modello = ModelloConfigurato(nome="n", base_url="http://x/v1", model="m", ragiona=True, parametri=ACCESO)
    registro = RegistroModelli([modello], assegnazioni={Compito.SINTESI: AssegnazioneModello(
        "n", ragiona_override=False, parametri_override={"chat_template_kwargs": {"enable_thinking": True}},
    )})
    fornitore = registro.per(Compito.SINTESI)
    assert fornitore._parametri["chat_template_kwargs"] == {"enable_thinking": True}
    # Il margine di budget segue il modello: "app spenta, modello acceso" faceva finire il
    # ragionamento nel testo quando il budget si esauriva a metà pensiero.
    assert fornitore.ragiona is True


def test_un_motore_senza_enable_thinking_non_viene_toccato():
    modello = ModelloConfigurato(nome="n", base_url="http://x/v1", model="m", ragiona=True,
                                 parametri={"reasoning_effort": "low"})
    registro = RegistroModelli([modello], assegnazioni={
        Compito.SINTESI: AssegnazioneModello("n", ragiona_override=False),
    })
    assert registro.per(Compito.SINTESI)._parametri == {"reasoning_effort": "low"}


async def test_complete_json_riprova_con_piu_budget_se_non_trova_json(monkeypatch):
    """Bug reale in produzione (2026-09-30): il validatore dell'intervista (`max_tokens=200`)
    riceveva un modello che ragiona in prosa libera, senza tag `<think>` ("Here's a thinking
    process:..."), e falliva con `JsonNonInterpretabile` invece di riprovare con più spazio —
    un `GenerationError` sarebbe stato gestito da chi chiama (`_giudica` in `intervista.py`),
    questo mandava in 500 l'intera intervista, bloccando ogni lettura."""
    p = OpenAICompatibleProvider(base_url="http://x/v1", default_model="m")
    risposte = iter([
        "Here's a thinking process:\n\n1. Analyze the question...",
        '{"valida": false, "motivo": "troppo diretta"}',
    ])
    budget_usati = []

    async def complete_finto(richiesta):
        budget_usati.append(richiesta.max_tokens)
        return next(risposte)

    monkeypatch.setattr(p, "complete", complete_finto)
    richiesta = GenerationRequest(messages=[Message("user", "?")], max_tokens=200, temperature=0.0)
    dati = await p.complete_json(richiesta)

    assert dati == {"valida": False, "motivo": "troppo diretta"}
    assert budget_usati == [200, 600]


async def test_complete_json_riprova_anche_se_il_pensiero_nomina_una_graffa(monkeypatch):
    """Seconda causa dello stesso bug reale: la prima versione del fix cercava solo `{`/`[` nel
    testo (`_contiene_json`), ma il ragionamento in prosa può nominare una graffa descrivendo lo
    schema atteso ("l'output dovrebbe essere {'valida': bool}...") senza mai emettere JSON vero —
    quel controllo diceva "c'è" e lasciava comunque fallire `estrai_json` un attimo dopo, fuori dal
    ripiego. La verifica deve essere il parser stesso (`_contiene_json_valido`)."""
    p = OpenAICompatibleProvider(base_url="http://x/v1", default_model="m")
    risposte = iter([
        "Let me think about the expected shape, something like {'valida': bool, 'motivo': str}, "
        "but I have not produced the real answer yet, still reasoning about the question...",
        '{"valida": false, "motivo": "troppo diretta"}',
    ])

    async def complete_finto(richiesta):
        return next(risposte)

    monkeypatch.setattr(p, "complete", complete_finto)
    richiesta = GenerationRequest(messages=[Message("user", "?")], max_tokens=200, temperature=0.0)
    dati = await p.complete_json(richiesta)

    assert dati == {"valida": False, "motivo": "troppo diretta"}


async def test_complete_json_si_arrende_con_generation_error_non_json_non_interpretabile(monkeypatch):
    """Se il JSON non arriva mai nemmeno al tetto massimo, l'errore dev'essere `GenerationError`
    (che i chiamanti già gestiscono con un ripiego) e non `JsonNonInterpretabile` (non gestito,
    diventava un 500)."""
    p = OpenAICompatibleProvider(base_url="http://x/v1", default_model="m")

    async def complete_finto(richiesta):
        return "Sto ancora pensando e non arrivo mai a una risposta strutturata."

    monkeypatch.setattr(p, "complete", complete_finto)
    richiesta = GenerationRequest(messages=[Message("user", "?")], max_tokens=200, temperature=0.0)
    with pytest.raises(GenerationError):
        await p.complete_json(richiesta)
