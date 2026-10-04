"""Misura i token veri delle pipeline: letture intere, l'oracolo e la memoria, contro un modello vero.

Non è un test (i test usano sempre il modello finto): è uno strumento da lanciare a mano, contro un modello **gratuito**
— LM Studio sulla macchina dell'operatore, con lo stesso modello della produzione — per sapere quanti token costa
davvero ogni passo, ragionamento compreso, e calcolarne il costo con i listini.

**Come.** L'app vera gira in-process (`httpx.ASGITransport`, come il client dei test) su un database suo, portato a
head con Alembic; il fornitore LLM e le assegnazioni si scrivono nelle tabelle come li scrive la console. Ogni chiamata
al modello passa dal registro dei consumi (`llm/consumi.py`): lo script la raccoglie con un ascoltatore (e la riga
finisce anche in `llm_consumi`, così la pagina «Costi» della console puntata su quel database la mostra).

**Le varianti** (il ragionamento):

- `produzione` — com'è configurata oggi la produzione: i cinque compiti assegnati (intervista, validazione,
  interpretazione, sintesi, giudizio) hanno `ragiona_override=false`, quindi il modello **non** ragiona; quelli non
  assegnati (chat dell'oracolo, estrazione delle memorie, embedding) ricadono sul fornitore predefinito, che ragiona
  con `reasoning_budget: 16384`;
- `acceso` — tutto col ragionamento acceso, come il fornitore è dichiarato (`reasoning_budget: 16384`);
- `spento` — tutto col ragionamento spento.

LM Studio ignora `chat_template_kwargs.enable_thinking` e `reasoning_budget` (verificato il 2026-10-04): il modello
ragiona sempre, senza tetto, finché non lo si spegne con `reasoning_effort: "none"`. Lo script lo aggiunge dove la
produzione manda `enable_thinking: false`. Un budget piccolo (es. 1024) su LM Studio non si può imporre: si può solo
tagliare `max_tokens`, che tronca invece di far ragionare meno — per questo non è fra le varianti.

**Uso** (una chiamata alla volta, mai in parallelo):

    cd backend
    ./.venv/Scripts/python.exe -m tarot_core.tools.misura_costi \\
        --db postgresql+psycopg://tarot:tarot@localhost:5432/tarot_ui_costi \\
        --varianti produzione,acceso,spento --uscita ../misure_costi.json

    # solo il riepilogo da un file già scritto:
    ./.venv/Scripts/python.exe -m tarot_core.tools.misura_costi --riepilogo ../misure_costi.json
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
import uuid
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

BACKEND = Path(__file__).resolve().parents[2]

SCENARI = ("tre-carte", "croce-celtica", "compatibilita", "abbandonata", "anonima", "oracolo")
VARIANTI = ("produzione", "acceso", "spento")
#: I compiti che la produzione assegna (gli altri ricadono sul predefinito).
ASSEGNATI = ("intervista", "validazione", "interpretazione", "sintesi", "giudizio")

PARAMETRI_PRODUZIONE = {"reasoning_budget": 16384, "chat_template_kwargs": {"enable_thinking": True}}
#: Ciò che spegne davvero il ragionamento su LM Studio (vedi la testata).
SPEGNI_LMSTUDIO = {"reasoning_effort": "none"}

QUESITI = {
    "tre-carte": "Devo accettare la nuova offerta di lavoro in un'altra città?",
    "croce-celtica": "Come evolverà il rapporto con mia sorella nei prossimi mesi?",
    "compatibilita": "Compatibilità con Marco",
    "abbandonata": "Riuscirò a finire la tesi entro la primavera?",
    "anonima": "Cosa mi aspetta in amore quest'anno?",
}
STESE = {"tre-carte": "tre-carte", "croce-celtica": "croce-celtica", "compatibilita": "compat-tre",
         "abbandonata": "tre-carte", "anonima": "tre-carte"}
RISPOSTE = [
    "Da circa tre mesi. L'offerta è arrivata da un'azienda di Milano, io vivo a Bologna con il mio compagno.",
    "Mi piace il ruolo, ma temo di perdere le amicizie e la vicinanza ai miei genitori, che stanno invecchiando.",
    "Devo rispondere entro fine mese. Il mio compagno dice che mi seguirebbe, ma lui ha appena aperto uno studio.",
    "Ho già provato a chiedere il lavoro da remoto, mi hanno detto che forse dopo sei mesi si può.",
    "Mi sento divisa: entusiasta e in colpa insieme. Di notte ci penso spesso.",
    "Vorrei soprattutto non pentirmi tra un anno, qualunque cosa scelga.",
]
PARTNER = {"nome": "Marco", "cognome": "Rossi", "genere": "uomo", "trans": False, "nascita": "1988-08-07"}
MEMORIE_PROVA = [
    ("variabile", "lavoro", "Ha ricevuto un'offerta di lavoro a Milano e deve decidere entro fine mese."),
    ("stabile", "famiglia", "Vive a Bologna con il compagno; i genitori sono anziani e abitano vicino."),
    ("variabile", "amore", "Il compagno ha appena aperto uno studio professionale a Bologna."),
    ("variabile", "spirituale", "Di notte pensa spesso alla scelta e si sente divisa fra entusiasmo e colpa."),
    ("stabile", "altro", "Tiene molto alle amicizie di lunga data."),
]


# ---- preparazione ------------------------------------------------------------------------------------------------


def _prepara_ambiente(db: str) -> None:
    os.environ["TAROT_DATABASE_URL"] = db
    os.environ["TAROT_LLM_FINTO"] = "false"
    os.environ["TAROT_CONSUMI_LLM"] = "true"
    os.environ["TAROT_TRACING_ENABLED"] = "false"
    from ..settings import get_settings

    get_settings.cache_clear()


def _crea_e_migra(db: str) -> None:
    import psycopg
    from psycopg import sql

    from alembic import command
    from alembic.config import Config

    base, nome = db.rsplit("/", 1)
    amministrazione = base.replace("postgresql+psycopg://", "postgresql://") + "/postgres"
    with psycopg.connect(amministrazione, autocommit=True) as c:
        if not c.execute("select 1 from pg_database where datname = %s", (nome,)).fetchone():
            c.execute(sql.SQL("create database {}").format(sql.Identifier(nome)))
            print(f"creato il database {nome}")
    cfg = Config(str(BACKEND / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND / "tarot_core" / "migrations"))
    command.upgrade(cfg, "head")


async def _configura(variante: str, url: str, modello: str) -> None:
    """Il fornitore e le assegnazioni, come li scrive la console."""
    from sqlalchemy import delete

    from ..domain.config_models import LlmProvider, ModelAssignment
    from ..domain.session import get_session_factory

    if variante == "spento":
        parametri, ragiona = {**PARAMETRI_PRODUZIONE, **SPEGNI_LMSTUDIO, "chat_template_kwargs": {"enable_thinking": False}}, False
        parametri.pop("reasoning_budget", None)
    else:
        parametri, ragiona = dict(PARAMETRI_PRODUZIONE), True
    # Dalla riduzione dei costi il ragionamento è un livello (`llm/ragionamento.py`): per LM Studio diventa
    # `reasoning_effort`, che è proprio ciò che lo spegne davvero (`none`). «Acceso» è il livello che la migrazione dà
    # a un fornitore che ragionava (`medium`); su LM Studio i livelli diversi da `none` ragionano in modo simile.
    livello = "medium" if ragiona else "none"
    async with get_session_factory()() as s:
        await s.execute(delete(ModelAssignment))
        await s.execute(delete(LlmProvider))
        s.add(LlmProvider(
            nome="lmstudio-nemotron", tipo="lmstudio", provider="openai-compatible", base_url=url, model=modello,
            ragiona=ragiona, livello_ragionamento=livello, parametri=parametri,
            descrizione=f"misura costi: {variante}", attivo=True,
        ))
        if variante == "produzione":
            for compito in ASSEGNATI:
                s.add(ModelAssignment(
                    task=compito, model_name="lmstudio-nemotron", ragiona_override=False, livello_ragionamento="none",
                    parametri_override=dict(SPEGNI_LMSTUDIO),
                ))
        await s.commit()
    from ..api import deps

    deps.reset_dependencies()


# ---- il client sull'app ------------------------------------------------------------------------------------------


class Sessione:
    def __init__(self, client, principal) -> None:
        self.client = client
        self.principal = principal


async def _client(stato: Dict[str, Any]):
    import httpx

    from ..api.app import create_app
    from ..auth.dependencies import current_principal, current_principal_opzionale
    from ..tarot import eta_minima

    eta_minima.controllo_attivo = lambda: False  # la conferma dell'età non è ciò che si misura
    app = create_app()
    app.dependency_overrides[current_principal] = lambda: stato["principal"]
    app.dependency_overrides[current_principal_opzionale] = lambda: stato["principal"]
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://misura", timeout=None)


def _eventi(testo: str) -> List[tuple]:
    eventi = []
    for blocco in testo.split("\n\n"):
        nome, dati = "", ""
        for riga in blocco.splitlines():
            if riga.startswith("event: "):
                nome = riga[7:]
            elif riga.startswith("data: "):
                dati += riga[6:]
        if nome:
            eventi.append((nome, json.loads(dati or "{}")))
    return eventi


async def _attendi_compiti_in_background() -> None:
    """L'estrazione delle memorie parte con `create_task` dopo la sintesi: la si aspetta prima di chiudere."""
    from ..llm import consumi

    corrente = asyncio.current_task()
    for _ in range(600):
        altri = [t for t in asyncio.all_tasks() if t is not corrente and not t.done()]
        if not altri:
            break
        await asyncio.sleep(0.5)
    await consumi.attendi_scritture()


async def _lettura(client, scenario: str, *, fermati_dopo: Optional[int] = None) -> Dict[str, Any]:
    corpo: Dict[str, Any] = {"spread_id": STESE[scenario], "question": QUESITI[scenario], "lang": "it"}
    if scenario == "compatibilita":
        corpo["partner"] = PARTNER
    if scenario == "anonima":
        r = await client.post("/readings/anonime", json={**corpo, "eta_confermata": True, "eta_anni": 18})
    else:
        r = await client.post("/readings", json=corpo)
    assert r.status_code == 201, r.text
    rid = r.json()["id"]
    esito: Dict[str, Any] = {"id": rid, "domande": 0}

    r = await client.post(f"/readings/{rid}/interview", json={})
    while r.status_code == 200 and not r.json().get("completa"):
        esito["domande"] += 1
        if fermati_dopo is not None and esito["domande"] >= fermati_dopo:
            esito["abbandonata"] = True
            return esito
        risposta = RISPOSTE[(esito["domande"] - 1) % len(RISPOSTE)]
        r = await client.post(f"/readings/{rid}/interview", json={"risposta": risposta})
        if esito["domande"] > 8:
            break
    assert r.status_code == 200, r.text

    r = await client.post(f"/readings/{rid}/fan")
    da_scegliere = r.json()["da_scegliere"]
    for i in range(da_scegliere):
        r = await client.post(f"/readings/{rid}/pick", json={"slot": i * 2})
        assert r.status_code == 200, r.text
    posizioni = sorted(c["posizione"] for c in (await client.get(f"/me/readings/{rid}")).json()["cards"]) \
        if scenario != "anonima" else list(range(1, da_scegliere + 1))
    errori = 0
    for pos in posizioni:
        r = await client.post(f"/readings/{rid}/reveal/{pos}")
        errori += sum(1 for nome, _ in _eventi(r.text) if nome == "errore")
    r = await client.post(f"/readings/{rid}/synthesis")
    fasi = [d.get("fase") for nome, d in _eventi(r.text) if nome == "fase"]
    errori += sum(1 for nome, _ in _eventi(r.text) if nome == "errore")
    esito.update({"carte": len(posizioni), "fasi_sintesi": fasi, "errori_sse": errori})
    await _attendi_compiti_in_background()
    return esito


async def _memorie_di_prova(principal) -> None:
    from sqlalchemy import select

    from ..domain.memory_models import UserMemory
    from ..domain.models import User
    from ..domain.session import get_session_factory

    async with get_session_factory()() as s:
        utente = (await s.execute(select(User).where(User.keycloak_sub == principal.subject))).scalar_one()
        for tipo, campo, testo in MEMORIE_PROVA:
            s.add(UserMemory(owner_id=utente.id, contenuto=testo, tipo=tipo, campo_attinenza=campo,
                             embedding=[0.0, 1.0], fonte="lettura"))
        await s.commit()


async def _oracolo(client, principal) -> Dict[str, Any]:
    """Apertura e risposta, prima senza memorie e poi con cinque memorie (il loro peso nel prompt)."""
    esito = {}
    r = await client.post("/chat/proattiva/avvio")
    esito["apertura"] = r.status_code
    r = await client.post("/chat/proattiva/messaggio", json={"testo": "Sono indecisa su un lavoro a Milano."})
    esito["risposta"] = r.status_code
    await _memorie_di_prova(principal)
    # Una seconda apertura subito dopo la prima ripropone quella in attesa (nessuna inferenza): si cancella la chat.
    await client.delete("/chat/proattiva")
    r = await client.post("/chat/proattiva/avvio")
    esito["apertura_con_memorie"] = r.status_code
    r = await client.post("/chat/proattiva/messaggio", json={"testo": "Ho deciso di parlarne con il mio compagno."})
    esito["risposta_con_memorie"] = r.status_code
    return esito


async def misura(args) -> Dict[str, Any]:
    from ..auth.keycloak import Principal
    from ..llm import consumi

    raccolta: List[Dict[str, Any]] = []
    corrente: Dict[str, Any] = {"scenario": "", "variante": "", "fase_oracolo": ""}

    def ascolta(c: consumi.Consumo) -> None:
        riga = {**c.riga(), "extra": c.extra, "scenario": corrente["scenario"], "variante": corrente["variante"]}
        riga["reading_id"] = str(riga["reading_id"]) if riga["reading_id"] else None
        raccolta.append(riga)
        print(f"    {c.compito or '-':16} {c.fase or '-':22} in {c.token_ingresso:6} cache {c.token_cache:5} "
              f"out {c.token_uscita:6} ragion. {c.token_ragionamento:6} {c.durata_ms / 1000:6.1f}s {c.esito}",
              flush=True)

    stato: Dict[str, Any] = {"principal": None}
    client = await _client(stato)
    esiti: Dict[str, Any] = {}
    with consumi.ascolta(ascolta):
        for variante in args.varianti:
            await _configura(variante, args.url, args.modello)
            for scenario in args.scenari:
                corrente.update(scenario=scenario, variante=variante)
                # Un utente nuovo per ogni scenario: nessuna memoria di uno scenario finisce nel prompt di un altro.
                stato["principal"] = None if scenario == "anonima" else Principal(
                    subject=f"misura-{variante}-{scenario}-{uuid.uuid4().hex[:6]}", email=None,
                    display_name="Giulia", roles={"user"},
                )
                if stato["principal"] is not None:
                    await client.patch("/me/profile", json={"gender": "donna", "birth_date": "1990-03-14"})
                else:
                    client.cookies.clear()  # una lettura gratuita per cookie: ogni variante ne vuole una nuova
                print(f"== {variante} / {scenario}", flush=True)
                inizio = time.perf_counter()
                if scenario == "oracolo":
                    esito = await _oracolo(client, stato["principal"])
                elif scenario == "abbandonata":
                    esito = await _lettura(client, scenario, fermati_dopo=2)
                else:
                    esito = await _lettura(client, scenario)
                esito["secondi"] = round(time.perf_counter() - inizio, 1)
                esiti[f"{variante}/{scenario}"] = esito
                print(f"   {esito}", flush=True)
                if args.uscita:
                    _scrivi(args.uscita, raccolta, esiti, args)
    await client.aclose()
    await consumi.attendi_scritture()
    return {"chiamate": raccolta, "esiti": esiti}


def _scrivi(percorso: str, raccolta, esiti, args) -> None:
    Path(percorso).write_text(json.dumps({
        "modello": args.modello, "url": args.url, "quando": time.strftime("%Y-%m-%d %H:%M"),
        "chiamate": raccolta, "esiti": esiti,
    }, ensure_ascii=False, indent=1, default=str), encoding="utf-8")


# ---- riepilogo ---------------------------------------------------------------------------------------------------


LISTINI = {
    "Nebius": dict(prezzo_ingresso=0.06, prezzo_cache=0.06, prezzo_uscita=0.24, cache_hit=0.0),
    "Darkbloom": dict(prezzo_ingresso=0.039, prezzo_cache=0.019, prezzo_uscita=0.18, cache_hit=0.70),
    "DeepInfra": dict(prezzo_ingresso=0.06, prezzo_cache=0.03, prezzo_uscita=0.16, cache_hit=0.90),
}


def _cacheabile(c: Dict[str, Any]) -> float:
    if not c.get("caratteri_ingresso"):
        return 0.0
    return c["token_ingresso"] * c.get("caratteri_sistema", 0) / c["caratteri_ingresso"]


def riepilogo(dati: Dict[str, Any]) -> Dict[str, Any]:
    from ..llm.listini import Listino, costo

    listini = {n: Listino(nome=n, **p) for n, p in LISTINI.items()}
    gruppi: Dict[str, Dict[str, Any]] = defaultdict(lambda: defaultdict(float))
    fasi: Dict[str, Dict[str, Dict[str, float]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    for c in dati["chiamate"]:
        chiave = f"{c['variante']}/{c['scenario']}"
        g = gruppi[chiave]
        g["chiamate"] += 1
        g["errori"] += c["esito"] != "ok"
        for k in ("token_ingresso", "token_cache", "token_uscita", "token_ragionamento", "durata_ms"):
            g[k] += c[k]
        g["cacheabile"] += _cacheabile(c)
        f = fasi[chiave][c["fase"] or c["compito"] or "?"]
        f["chiamate"] += 1
        for k in ("token_ingresso", "token_uscita", "token_ragionamento"):
            f[k] += c[k]
        f["cacheabile"] += _cacheabile(c)
    risultato = {}
    for chiave, g in sorted(gruppi.items()):
        risultato[chiave] = {
            **{k: round(v, 1) for k, v in g.items()},
            "costo": {n: round(costo(l, ingresso=g["token_ingresso"], uscita=g["token_uscita"],
                                     cacheabile=g["cacheabile"]), 6) for n, l in listini.items()},
            "fasi": {fa: {k: round(v, 1) for k, v in valori.items()} for fa, valori in fasi[chiave].items()},
        }
    return risultato


def stampa(r: Dict[str, Any]) -> None:
    print(f"\n{'variante/scenario':34} {'chiam':>5} {'ingresso':>9} {'cacheab':>8} {'uscita':>8} {'ragion':>8} "
          f"{'Nebius $':>9} {'Darkb $':>9} {'DeepI $':>9} {'min':>5}")
    for chiave, g in r.items():
        print(f"{chiave:34} {g['chiamate']:5.0f} {g['token_ingresso']:9.0f} {g['cacheabile']:8.0f} "
              f"{g['token_uscita']:8.0f} {g['token_ragionamento']:8.0f} {g['costo']['Nebius']:9.5f} "
              f"{g['costo']['Darkbloom']:9.5f} {g['costo']['DeepInfra']:9.5f} {g['durata_ms'] / 60000:5.1f}")
        for fase, v in sorted(g["fasi"].items(), key=lambda x: -x[1]["token_uscita"]):
            print(f"    {fase:30} {v['chiamate']:5.0f} {v['token_ingresso']:9.0f} {v['cacheabile']:8.0f} "
                  f"{v['token_uscita']:8.0f} {v['token_ragionamento']:8.0f}")


def main(argv: Optional[List[str]] = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--db", default="postgresql+psycopg://tarot:tarot@localhost:5432/tarot_ui_costi")
    p.add_argument("--url", default="http://127.0.0.1:1234/v1")
    p.add_argument("--modello", default="nvidia-nemotron-3.5-lightning-30b-a3b")
    p.add_argument("--varianti", default=",".join(VARIANTI))
    p.add_argument("--scenari", default=",".join(SCENARI))
    p.add_argument("--uscita", default="")
    p.add_argument("--riepilogo", default="", help="solo il riepilogo di un file di misure già scritto")
    args = p.parse_args(argv)

    if args.riepilogo:
        stampa(riepilogo(json.loads(Path(args.riepilogo).read_text(encoding="utf-8"))))
        return 0

    args.varianti = [v for v in args.varianti.split(",") if v]
    args.scenari = [s for s in args.scenari.split(",") if s]
    for v in args.varianti:
        if v not in VARIANTI:
            p.error(f"variante sconosciuta: {v}")
    for s in args.scenari:
        if s not in SCENARI:
            p.error(f"scenario sconosciuto: {s}")
    _prepara_ambiente(args.db)
    _crea_e_migra(args.db)
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # psycopg asincrono
    dati = asyncio.run(misura(args))
    stampa(riepilogo(dati))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
