"""La riduzione dei costi delle inferenze (ottobre 2026): sempre col modello finto o con fornitori di prova, mai una
chiamata vera.

- il ragionamento **effettivo** di ogni compito (ereditato o scelto), i livelli e il loro dialetto, il tetto
  ragionamento compreso, `store: false`, il servizio;
- i tre modi del validatore delle domande e della guardia del responso, e le regole deterministiche che decidono i
  casi dubbi;
- lo stato sintetico della memoria: aggiornamento, oblio deterministico, tetto, art. 9, esportazione, cancellazione,
  conversione, profilo, e i prompt che non cambiano finché l'interruttore è spento;
- la negoziazione del formato JSON ricordata per tutta la vita del processo.
"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from tarot_core.guards.lettura import da_guardare, giudica
from tarot_core.guards.policy import RegistroGuardrail
from tarot_core.llm.base import GenerationError, GenerationRequest, Message
from tarot_core.llm.compiti import AssegnazioneModello, Compito, ModelloConfigurato, RegistroModelli
from tarot_core.llm.openai_compatible import OpenAICompatibleProvider
from tarot_core.llm.ragionamento import dialetto, livello_da_bool, parametri_per_livello, senza_conflitti
from tarot_core.tarot import stato_memoria as sm
from tarot_core.tarot.intervista import prossimo_passo, sospetta

from .conftest import richiede_database
from .test_intervista import Copione

NEBIUS_DI_OGGI = {"reasoning_budget": 16384, "chat_template_kwargs": {"enable_thinking": True}}


def _richiesta(sistema: str = "", **extra) -> GenerationRequest:
    messaggi = ([Message("system", sistema)] if sistema else []) + [Message("user", "ciao")]
    return GenerationRequest(messages=messaggi, max_tokens=200, temperature=0.0, extra=extra)


# ---- il ragionamento effettivo ------------------------------------------------------------------------------------


def test_un_compito_senza_assegnazione_eredita_il_ragionamento_acceso_e_la_console_lo_dice():
    """Il caso della produzione: l'oracolo e la memoria non sono assegnati e ragionavano col fornitore predefinito,
    mentre la casella della console li mostrava spenti."""
    nebius = ModelloConfigurato(nome="nebius", tipo="nebius", base_url="http://x/v1", model="m", ragiona=True,
                                parametri=NEBIUS_DI_OGGI, livello_ragionamento="medium")
    registro = RegistroModelli([nebius], assegnazioni={
        Compito.INTERVISTA: AssegnazioneModello("nebius", ragiona_override=False, livello="none"),
    })
    stato = {r["compito"]: r for r in registro.stato()}
    assert stato["chat_proattiva"]["ragiona_effettivo"] is True
    assert stato["chat_proattiva"]["ragiona_origine"] == "fornitore"
    assert stato["chat_proattiva"]["livello_effettivo"] == "medium"
    assert stato["chat_proattiva"]["assegnato"] is None
    assert stato["intervista"]["ragiona_effettivo"] is False
    assert stato["intervista"]["ragiona_origine"] == "compito"


def test_un_fornitore_di_prima_dei_livelli_mostra_lo_stato_dal_booleano():
    vecchio = ModelloConfigurato(nome="n", base_url="http://x/v1", model="m", ragiona=True, parametri=NEBIUS_DI_OGGI)
    registro = RegistroModelli([vecchio], assegnazioni={Compito.SINTESI: AssegnazioneModello("n", ragiona_override=False)})
    stato = {r["compito"]: r for r in registro.stato()}
    assert stato["chat_proattiva"]["ragiona_effettivo"] is True and stato["chat_proattiva"]["livello_effettivo"] is None
    assert stato["sintesi"]["ragiona_effettivo"] is False and stato["sintesi"]["ragiona_spegnibile"] is True
    # L'embedding e l'aggiornamento della memoria non ragionano comunque: la console lo dice invece di allarmare.
    assert stato["memoria_estrazione"]["ragiona_effettivo"] is False and stato["memoria_estrazione"]["ragiona_origine"] == "codice"
    assert stato["embedding"]["ragiona_origine"] == "codice"


@pytest.mark.parametrize(("tipo", "atteso"), [("nebius", "effort"), ("lmstudio", "effort"), ("openai_compat", "effort"),
                                               ("nvidia", "thinking")])
def test_il_dialetto_del_ragionamento_dipende_dal_tipo(tipo, atteso):
    assert dialetto(tipo, "openai-compatible", NEBIUS_DI_OGGI) == atteso
    assert dialetto("", "anthropic") == "anthropic"


def test_reasoning_effort_toglie_enable_thinking_e_budget_e_viceversa():
    effort = parametri_per_livello({**NEBIUS_DI_OGGI, "top_k": 20}, "low", "effort")
    assert effort == {"reasoning_effort": "low", "top_k": 20}
    nim = parametri_per_livello({"reasoning_effort": "high"}, "high", "thinking")
    assert nim == {"chat_template_kwargs": {"enable_thinking": True}, "reasoning_budget": 8192}
    spento = parametri_per_livello(NEBIUS_DI_OGGI, "none", "thinking")
    assert spento == {"chat_template_kwargs": {"enable_thinking": False}}
    # Anche dopo un parametri_override scritto a mano: mai i due dialetti insieme.
    assert senza_conflitti({"reasoning_effort": "low", **NEBIUS_DI_OGGI}, "effort") == {"reasoning_effort": "low"}


def test_dal_vecchio_booleano_al_livello():
    assert livello_da_bool(True) == "medium" and livello_da_bool(False) == "none"


def test_il_livello_del_compito_arriva_nella_richiesta_di_nebius_senza_conflitti():
    nebius = ModelloConfigurato(nome="nebius", tipo="nebius", base_url="http://x/v1", model="m", ragiona=True,
                                parametri=NEBIUS_DI_OGGI, livello_ragionamento="medium")
    registro = RegistroModelli([nebius], assegnazioni={
        Compito.VALIDAZIONE: AssegnazioneModello("nebius", livello="none"),
        Compito.SINTESI: AssegnazioneModello("nebius", livello="high"),
    })
    assert registro.per(Compito.VALIDAZIONE)._parametri == {"reasoning_effort": "none"}
    assert registro.per(Compito.SINTESI)._parametri == {"reasoning_effort": "high"}
    # Il compito senza assegnazione eredita «medium» dal fornitore.
    assert registro.per(Compito.CHAT_PROATTIVA)._parametri == {"reasoning_effort": "medium"}


def test_senza_ragionamento_spegne_anche_un_compito_che_eredita_acceso():
    nebius = ModelloConfigurato(nome="nebius", tipo="nebius", base_url="http://x/v1", model="m", ragiona=True,
                                livello_ragionamento="high")
    registro = RegistroModelli([nebius])
    fornitore = registro.per(Compito.MEMORIA_ESTRAZIONE, senza_ragionamento=True)
    assert fornitore._parametri == {"reasoning_effort": "none"} and fornitore.ragiona is False


async def test_store_false_sempre_e_nessun_campo_di_tetto_o_servizio():
    """`store: false` in ogni richiesta, anche se qualcuno prova a mandarlo diverso; niente `max_completion_tokens`
    (conterebbe anche il ragionamento e troncherebbe le risposte) né `service_tier` (decisione dell'operatore)."""
    registro = RegistroModelli([ModelloConfigurato(nome="n", tipo="nebius", base_url="http://x/v1", model="m",
                                                   livello_ragionamento="medium", ragiona=True)])
    for compito in (Compito.MEMORIA_ESTRAZIONE, Compito.INTERVISTA, Compito.SINTESI):
        payload = await registro.per(compito)._build_payload(_richiesta(store=True), stream=False)
        assert payload["store"] is False
        assert "max_completion_tokens" not in payload and "service_tier" not in payload
        assert payload["max_tokens"] >= 200


async def test_il_consumo_legge_cache_e_ragionamento_anche_in_streaming(monkeypatch):
    """L'`usage` di Nebius porta `prompt_tokens_details.cached_tokens` e `completion_tokens_details.reasoning_tokens`
    nell'ultimo evento dello streaming (con `choices` vuoto): il registro dei consumi li legge entrambi."""
    import json as _json

    import httpx

    from tarot_core.llm import consumi
    from tarot_core.tarot.llm import genera_flusso, richiesta

    uso = {"prompt_tokens": 900, "completion_tokens": 300, "total_tokens": 1200,
           "prompt_tokens_details": {"cached_tokens": 640}, "completion_tokens_details": {"reasoning_tokens": 120}}
    eventi = [{"choices": [{"delta": {"content": "Una carta."}}]},
              {"choices": [{"delta": {}, "finish_reason": "stop"}]},
              {"choices": [], "usage": uso}]
    corpo = "".join(f"data: {_json.dumps(e)}\n\n" for e in eventi) + "data: [DONE]\n\n"
    originale = httpx.AsyncClient

    def con_trasporto(*a, **k):
        k["transport"] = httpx.MockTransport(lambda req: httpx.Response(200, text=corpo))
        return originale(*a, **k)

    monkeypatch.setattr(httpx, "AsyncClient", con_trasporto)
    visti = []
    with consumi.ascolta(visti.append):
        fornitore = consumi.misurato(OpenAICompatibleProvider(base_url="http://nebius/v1", default_model="m"),
                                     "interpretazione")
        testo = "".join([p async for p in genera_flusso(fornitore, richiesta(["# Compito: interpretazione"], "x"))])
    assert testo == "Una carta."
    assert visti[-1].token_cache == 640 and visti[-1].token_ragionamento == 120 and visti[-1].token_ingresso == 900


@richiede_database
async def test_la_console_crea_la_sostituzione_anche_per_un_compito_senza_assegnazione(client, principal_admin):
    from tarot_core.api.deps import get_registro_modelli

    client.identita.principal = principal_admin
    get_registro_modelli().aggiorna_modelli(
        [ModelloConfigurato(nome="nebius", tipo="nebius", base_url="http://127.0.0.1:9/v1", model="m",
                            livello_ragionamento="medium", ragiona=True)], reale=True,
    )
    r = await client.put("/admin/models/chat_proattiva", json={"modello": "nebius", "livello": "none"})
    assert r.status_code == 200, r.text
    riga = next(c for c in r.json()["compiti"] if c["compito"] == "chat_proattiva")
    assert riga["assegnato"] == "nebius" and riga["livello"] == "none" and riga["ragiona_override"] is False
    assert riga["ragiona_effettivo"] is False and riga["ragiona_origine"] == "compito"
    # Accendere solo lo schema JSON di un compito senza assegnazione non gli cambia il ragionamento (resta «eredita»).
    r = await client.put("/admin/models/giudizio", json={"modello": "nebius", "livello": None, "json_schema": True})
    riga = next(c for c in r.json()["compiti"] if c["compito"] == "giudizio")
    assert riga["livello"] is None and riga["ragiona_effettivo"] is True and riga["json_schema"] is True


# ---- il validatore delle domande ----------------------------------------------------------------------------------


QUESITO = "Devo accettare la nuova offerta di lavoro?"


@pytest.mark.parametrize("domanda", [
    "Secondo te come ti sentiresti a Milano?",          # opinione
    "Cosa vorresti che succedesse con il tuo capo?",     # futuro
    "Che cosa ti attira dell'offerta di lavoro nuova?",  # somiglia al quesito
])
def test_le_regole_del_sospetto(domanda):
    assert sospetta(QUESITO, domanda) is not None


@pytest.mark.parametrize("domanda", [
    "Da quanto tempo lavori nell'azienda di adesso?",
    "Chi altro è coinvolto nella decisione?",
])
def test_una_domanda_di_contesto_non_e_dubbia(domanda):
    assert sospetta(QUESITO, domanda) is None


def test_nelle_letture_di_coppia_il_mondo_interiore_dell_altro_e_dubbio_e_le_altre_lingue_sempre():
    assert sospetta("Compatibilità con Marco", "Cosa prova Marco quando siete insieme?", categoria="compatibilita",
                    neutre=["Marco"]) is not None
    assert sospetta(QUESITO, "Mióta dolgozol a mostani cégnél?", lang="hu") == "lingua senza regole del sospetto"


async def _un_passo(modo: str, domanda: str):
    intervista = Copione([{"completo": False, "domanda": domanda}])
    validatore = Copione([{"valida": True}])
    passo = await prossimo_passo(
        provider_intervista=intervista, provider_validazione=validatore, quesito=QUESITO, stesa_nome="Tre carte",
        turni=[], max_domande=6, min_domande=2, validatore=modo,
    )
    return passo, validatore.chiamate


@pytest.mark.parametrize(("modo", "domanda", "chiamate"), [
    ("acceso", "Da quanto tempo lavori nell'azienda di adesso?", 1),
    ("dubbi", "Da quanto tempo lavori nell'azienda di adesso?", 0),
    ("dubbi", "Secondo te come ti sentiresti a Milano?", 1),
    ("spento", "Secondo te come ti sentiresti a Milano?", 0),
])
async def test_i_tre_modi_del_validatore(modo, domanda, chiamate):
    passo, fatte = await _un_passo(modo, domanda)
    assert passo.domanda == domanda and fatte == chiamate


async def test_i_controlli_deterministici_valgono_anche_col_validatore_spento():
    intervista = Copione([
        {"completo": False, "domanda": "Pensi che otterrai quel lavoro?"},   # previsione: scartata senza modello
        {"completo": False, "domanda": "Da quanto tempo ci pensi?"},
    ])
    validatore = Copione([])
    passo = await prossimo_passo(
        provider_intervista=intervista, provider_validazione=validatore, quesito=QUESITO, stesa_nome="Tre carte",
        turni=[], max_domande=6, min_domande=2, validatore="spento",
    )
    assert passo.domanda == "Da quanto tempo ci pensi?" and passo.scartate == 1 and validatore.chiamate == 0


# ---- la guardia del responso --------------------------------------------------------------------------------------


class Giudice:
    name = "giudice"

    def __init__(self, esito):
        self.esito = esito
        self.chiamate = 0

    async def complete_json(self, req):
        self.chiamate += 1
        return self.esito


SERENO = "## Il quadro\n\nLa stesa mostra un passaggio che chiede presenza. Le tue scelte possono cambiarne la direzione."


@pytest.mark.parametrize("responso", [
    "Accadrà sicuramente entro l'estate.",
    "Dovresti investire i tuoi risparmi adesso.",
    "Lui ti tradisce, è evidente.",
    "Una malattia potrebbe colpirti.",
    "Le carte dicono che morirai presto.",
])
def test_il_controllo_deterministico_trova_cosa_guardare(responso):
    assert da_guardare(quesito="Come andrà?", responso=responso)


def test_un_responso_sereno_non_ha_nulla_da_guardare_e_la_carta_della_morte_non_allarma():
    assert da_guardare(quesito="Come andrà il lavoro?", responso=SERENO) == []
    assert da_guardare(quesito="Come andrà?", responso="La Morte indica la fine di una fase.") == []


def test_salute_diritto_e_denaro_nel_quesito_e_le_altre_lingue_si_guardano_sempre():
    assert "salute, diritto o denaro" in da_guardare(quesito="Guarirò dalla malattia?", responso=SERENO)
    assert "lingua senza regole" in da_guardare(quesito="?", responso=SERENO, lang="hu")
    assert da_guardare(quesito="Compatibilità con Marco", responso="Lascialo, non è la persona giusta.",
                       categoria="compatibilita")


@pytest.mark.parametrize(("modo", "responso", "chiamate", "guardia"), [
    ("acceso", SERENO, 1, "llm"),
    ("dubbi", SERENO, 0, "deterministica"),
    ("dubbi", "Accadrà sicuramente.", 1, "llm"),
    ("spento", "Accadrà sicuramente.", 0, "spenta"),
])
async def test_i_tre_modi_della_guardia(modo, responso, chiamate, guardia):
    giudice = Giudice({"esito": "ok", "violazioni": []})
    verdetto = await giudica(giudice, RegistroGuardrail(), quesito="q", responso=responso, modo=modo)
    assert verdetto.ok and giudice.chiamate == chiamate and verdetto.guardia == guardia


async def test_con_la_guardia_spenta_una_formula_proibita_chiede_comunque_la_riscrittura():
    giudice = Giudice({"esito": "ok"})
    verdetto = await giudica(giudice, RegistroGuardrail(), quesito="q", responso="Morirai presto.", modo="spento")
    assert verdetto.esito == "riscrivi" and giudice.chiamate == 0


# ---- lo stato sintetico della memoria -----------------------------------------------------------------------------


OGGI = date(2026, 10, 4)


def test_l_aggiornamento_aggiunge_conferma_rimuove_e_scrive_il_tema_dal_quesito():
    voci = [sm.nuova_voce("volatile", "lavoro", "Cerca lavoro a Milano.", oggi=OGGI - timedelta(days=10)),
            sm.nuova_voce("stabile", "famiglia", "Vive con il compagno.", oggi=OGGI - timedelta(days=200))]
    via, tiene = voci[0]["id"], voci[1]["id"]
    nuove = sm.applica(voci, {
        "aggiungi": [{"categoria": "volatile", "campo": "lavoro", "testo": "Ha accettato l'offerta di Milano."},
                     {"categoria": "tema", "campo": "altro", "testo": "Il modello non scrive i temi."}],
        "conferma": [tiene, "sconosciuto"], "rimuovi": [via], "campo_quesito": "lavoro",
    }, oggi=OGGI, quesito="Come andrà il nuovo lavoro?")
    testi = {v["testo"]: v for v in nuove}
    assert "Cerca lavoro a Milano." not in testi
    assert testi["Vive con il compagno."]["visto"] == OGGI.isoformat()
    assert testi["Ha accettato l'offerta di Milano."]["categoria"] == "volatile"
    assert testi["Come andrà il nuovo lavoro?"]["categoria"] == "tema"
    assert "Il modello non scrive i temi." not in testi


def test_un_doppione_conferma_invece_di_aggiungere():
    voci = [sm.nuova_voce("stabile", "famiglia", "Vive con il compagno.", oggi=OGGI - timedelta(days=30))]
    nuove = sm.applica(voci, {"aggiungi": [{"categoria": "stabile", "campo": "famiglia", "testo": "vive con il compagno"}]},
                       oggi=OGGI)
    assert len(nuove) == 1 and nuove[0]["visto"] == OGGI.isoformat()


def test_l_oblio_e_deterministico_per_categoria_e_data():
    stabile = sm.nuova_voce("stabile", "famiglia", "Ha due figli.", oggi=OGGI - timedelta(days=900))
    volatile_vecchia = sm.nuova_voce("volatile", "lavoro", "Aspetta una risposta.", oggi=OGGI - timedelta(days=61))
    volatile_fresca = sm.nuova_voce("volatile", "amore", "Ha conosciuto una persona.", oggi=OGGI - timedelta(days=5))
    tema_vecchio = sm.nuova_voce("tema", "lavoro", "Devo cambiare lavoro?", oggi=OGGI - timedelta(days=121))
    rimaste = sm.dimentica([stabile, volatile_vecchia, volatile_fresca, tema_vecchio], OGGI)
    assert [v["testo"] for v in rimaste] == ["Ha due figli.", "Ha conosciuto una persona."]
    # Il peso scende in linea retta lungo la vita della voce; la stabile pesa sempre 1.
    assert sm.peso(volatile_fresca, OGGI) == pytest.approx(1 - 5 / 60) and sm.peso(stabile, OGGI) == 1.0
    # Al più sei temi: restano i più recenti.
    temi = [sm.nuova_voce("tema", "altro", f"Domanda {i}", oggi=OGGI - timedelta(days=i)) for i in range(9)]
    assert [v["testo"] for v in sm.dimentica(temi, OGGI)] == [f"Domanda {i}" for i in range(6)]


def test_nei_prompt_entra_nella_forma_di_prima_con_un_tetto():
    voci = [sm.nuova_voce("stabile", "famiglia", "Vive a Bologna con il compagno.", oggi=OGGI)]
    voci += [sm.nuova_voce("volatile", "lavoro", "x" * 230, oggi=OGGI - timedelta(days=i)) for i in range(8)]
    istantanea = sm.come_istantanea(voci, OGGI, owner_id=7, limite=5)
    assert istantanea[0]["tipo"] == "stabile" and all(v["tipo"] == "variabile" for v in istantanea[1:])
    assert sum(len(v["contenuto"]) for v in istantanea) <= sm.TETTO_CARATTERI
    blocco = sm.formatta(voci, OGGI)
    assert blocco.startswith("- [STABILE — famiglia] Vive a Bologna")


def test_la_salute_senza_consenso_non_entra_e_se_c_era_esce():
    voci = [sm.nuova_voce("stabile", "salute", "Ha il diabete.", oggi=OGGI)]
    aggiornamento = {"aggiungi": [{"categoria": "volatile", "campo": "salute", "testo": "Aspetta un esame."}],
                     "campo_quesito": "salute"}
    assert sm.applica(voci, aggiornamento, oggi=OGGI, quesito="Guarirò?") == []
    con_consenso = sm.applica(voci, aggiornamento, oggi=OGGI, quesito="Guarirò?", salute_ammessa=True)
    assert len(con_consenso) == 3


def test_il_messaggio_dell_aggiornamento_porta_il_quadro_non_la_trascrizione():
    voci = [sm.nuova_voce("volatile", "lavoro", "Cerca lavoro.", oggi=OGGI),
            sm.nuova_voce("tema", "lavoro", "Devo cambiare lavoro?", oggi=OGGI)]
    testo = sm.messaggio_aggiornamento(voci, quesito="Q", quadro="Il quadro emerso.", oggi=OGGI, lang="it")
    assert "Il quadro emerso." in testo and "Cerca lavoro." in testo
    assert "Devo cambiare lavoro?" not in testo and "Chi consulta:" not in testo


async def test_un_modello_che_non_risponde_non_tocca_lo_stato():
    class Muto:
        name = "muto"

        async def complete_json(self, req):
            raise GenerationError("giù")

    assert await sm.chiedi_aggiornamento(Muto(), [], quesito="q", quadro="", oggi=OGGI) is None


@richiede_database
async def test_stato_profilo_esportazione_cancellazione_e_revoca_del_consenso(client, session, principal_utente):
    from tarot_core.domain import memoria_repositories
    from tarot_core.domain.repositories import UserRepository
    from tarot_core.tarot.consensi import dopo_la_scelta
    from tarot_core.tarot.esportazione import raccogli

    await client.get("/me/addresses")
    io = await UserRepository(session).ensure(principal_utente)
    oggi = date.today()
    await memoria_repositories.salva_stato(session, io.id, [
        sm.nuova_voce("stabile", "famiglia", "Vive con il compagno.", oggi=oggi),
        sm.nuova_voce("volatile", "salute", "Aspetta un esame.", oggi=oggi),
        sm.nuova_voce("tema", "lavoro", "Devo cambiare lavoro?", oggi=oggi),
    ])
    await session.commit()

    elenco = (await client.get("/me/memories")).json()["memorie"]
    assert [m["categoria"] for m in elenco] == ["stabile", "volatile", "tema"]
    assert elenco[0]["scade"] is None and elenco[1]["scade"]
    voce = elenco[0]["id"]
    r = await client.patch(f"/me/memories/{voce}", json={"contenuto": "Vive con il marito."})
    assert r.status_code == 200 and r.json()["contenuto"] == "Vive con il marito."

    assert len((await raccogli(session, io))["stato_memoria.json"]) == 3

    # La revoca del consenso alle categorie particolari toglie la salute anche dallo stato.
    tolti = await dopo_la_scelta(session, io, "dati_particolari", "rifiutato")
    assert tolti.get("stato_memoria_salute") == 1

    r = await client.request("DELETE", "/me/memories", json={"ids": [elenco[2]["id"]]})
    assert r.status_code == 204
    assert [m["contenuto"] for m in (await client.get("/me/memories")).json()["memorie"]] == ["Vive con il marito."]
    assert (await client.request("DELETE", "/me/memories", json={"tutte": True})).status_code == 204
    assert await memoria_repositories.stato_di(session, io.id) == []


@richiede_database
async def test_la_conversione_delle_memorie_di_prima(session, principal_utente):
    from tarot_core.domain import memoria_repositories
    from tarot_core.domain.memory_models import UserMemory
    from tarot_core.domain.repositories import UserRepository

    io = await UserRepository(session).ensure(principal_utente)
    for tipo, campo, testo in [("stabile", "famiglia", "Ha due figli."), ("variabile", "lavoro", "Cerca lavoro."),
                               ("stabile", "salute", "Ha il diabete.")]:
        session.add(UserMemory(owner_id=io.id, contenuto=testo, tipo=tipo, campo_attinenza=campo,
                               embedding=[0.0, 1.0], fonte="lettura"))
    await session.flush()
    assert await memoria_repositories.converti_in_stato(session, io.id) == 2       # senza consenso: niente salute
    assert await memoria_repositories.converti_in_stato(session, io.id) == 0       # rilanciata: nessun doppione
    voci = await memoria_repositories.stato_di(session, io.id)
    assert {(v["categoria"], v["testo"]) for v in voci} == {("stabile", "Ha due figli."), ("volatile", "Cerca lavoro.")}


@richiede_database
async def test_una_lettura_completa_aggiorna_lo_stato_ma_i_prompt_non_cambiano_finche_l_interruttore_e_spento(
    client, session, principal_utente, prompt_visti,
):
    import asyncio

    from tarot_core.domain import memoria_repositories
    from tarot_core.domain.impostazioni_repositories import correnti_intervista
    from tarot_core.domain.repositories import UserRepository

    from .test_flusso import _accredita, _lettura_completa

    await _accredita(session, principal_utente)
    io = await UserRepository(session).ensure(principal_utente)
    await memoria_repositories.salva_stato(session, io.id, [
        sm.nuova_voce("stabile", "famiglia", "Vive con il compagno a Bologna.", oggi=date.today()),
    ])
    await session.commit()

    await _lettura_completa(client, "tre-carte", 3, "Devo accettare il lavoro a Milano?")
    for _ in range(50):
        if any(v["categoria"] == "tema" for v in await memoria_repositories.stato_di(session, io.id)):
            break
        await asyncio.sleep(0.05)
    voci = await memoria_repositories.stato_di(session, io.id)
    assert {"stabile", "tema"} <= {v["categoria"] for v in voci}
    # Spento (il predefinito): nessun prompt della lettura ha visto lo stato (lo vede solo il suo aggiornamento).
    della_lettura = [p for p in prompt_visti if p["compito"] != "memoria_stato"]
    assert della_lettura and not any("Vive con il compagno" in (p.get("utente") or "") for p in della_lettura)

    regole = await correnti_intervista(session)
    regole.memoria_stato_nei_prompt = True
    await session.commit()
    prompt_visti.clear()
    await _lettura_completa(client, "tre-carte", 3, "E con mia sorella come andrà?")
    visti = [p for p in prompt_visti if p["compito"] in ("intervista", "sintesi")]
    assert visti and all("Vive con il compagno" in (p.get("utente") or "") for p in visti)


# ---- la negoziazione del formato JSON -----------------------------------------------------------------------------


async def test_il_dialetto_json_si_negozia_una_volta_per_server_e_modello(monkeypatch):
    tentati = []

    async def finto(self, request, dialetto, *, richiede_json=False, formato=None):
        tentati.append(dialetto)
        if dialetto == "json_object":
            raise GenerationError("400: response_format 'json_object' not supported")
        return '{"valida": true}'

    monkeypatch.setattr(OpenAICompatibleProvider, "_genera_con_budget", finto)
    for _ in range(3):
        # Un fornitore nuovo a ogni chiamata, come per i compiti con una sostituzione in console.
        fornitore = OpenAICompatibleProvider(base_url="http://lmstudio:1234/v1", default_model="m")
        assert await fornitore.complete_json(_richiesta()) == {"valida": True}
    assert tentati == ["json_object", "json_schema", "json_schema", "json_schema"]
    # Un altro modello sullo stesso server si negozia da capo.
    await OpenAICompatibleProvider(base_url="http://lmstudio:1234/v1", default_model="altro").complete_json(_richiesta())
    assert tentati[-2:] == ["json_object", "json_schema"]


async def test_lo_schema_rigoroso_si_prova_e_se_rifiutato_si_ricorda(monkeypatch):
    tentati = []

    async def finto(self, request, dialetto, *, richiede_json=False, formato=None):
        tentati.append(dialetto)
        if dialetto == "rigoroso":
            assert formato["json_schema"]["strict"] is True
            raise GenerationError("400: json_schema strict not supported")
        return '{"valida": true, "motivo": ""}'

    monkeypatch.setattr(OpenAICompatibleProvider, "_genera_con_budget", finto)
    for _ in range(2):
        fornitore = OpenAICompatibleProvider(base_url="http://nebius/v1", default_model="m", json_schema=True)
        await fornitore.complete_json(_richiesta("# Compito: validazione\n\n..."))
    assert tentati == ["rigoroso", "json_object", "json_object"]
    # Una fase senza schema non lo prova nemmeno.
    tentati.clear()
    fornitore = OpenAICompatibleProvider(base_url="http://altro/v1", default_model="m", json_schema=True)
    await fornitore.complete_json(_richiesta("# Compito: analisi_dati\n\n..."))
    assert tentati == ["json_object"]
