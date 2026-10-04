"""La pagina «Costi» della console: i consumi per compito, giorno e lettura, e i listini modificabili."""
from __future__ import annotations

import uuid

import pytest

from tarot_core.domain.consumi_models import LlmConsumo, LlmListino
from tarot_core.domain.models import Reading
from tarot_core.llm.listini import Listino, costo

from .conftest import richiede_database

pytestmark = richiede_database


@pytest.fixture
def come(client, principal_utente, principal_admin):
    def scegli(chi: str):
        client.identita.principal = principal_admin if chi == "admin" else principal_utente
        return client

    return scegli


async def _lettura(session, stato: str) -> uuid.UUID:
    r = Reading(anon_id=uuid.uuid4().hex, spread_id="tre-carte", question="Troverò lavoro?", consumo="anonimo",
                lang="it", status=stato)
    session.add(r)
    await session.flush()
    return r.id


def _consumo(compito, fase, *, lettura=None, ingresso=1000, cache=0, uscita=200, ragionamento=0, sistema=0,
             caratteri=4000, riferimento="", esito="ok", usage=True):
    return LlmConsumo(
        compito=compito, fase=fase, fornitore="nebius", modello="nemotron", token_ingresso=ingresso if usage else 0,
        token_cache=cache, token_uscita=uscita if usage else 0, token_ragionamento=ragionamento,
        caratteri_ingresso=caratteri, caratteri_sistema=sistema, caratteri_uscita=700 if not usage else 0,
        esito=esito, usage_riportato=usage, reading_id=lettura, riferimento=riferimento, durata_ms=1000,
    )


@pytest.fixture
async def dati(session):
    completata = await _lettura(session, "completata")
    ferma = await _lettura(session, "intervista")
    session.add_all([
        LlmListino(nome="Nebius (in uso)", prezzo_ingresso=0.06, prezzo_cache=0.06, prezzo_uscita=0.24, attuale=True),
        LlmListino(nome="DeepInfra", prezzo_ingresso=0.06, prezzo_cache=0.03, prezzo_uscita=0.16, cache_hit=0.9),
        # Una lettura completata: intervista, validazione, interpretazione, sintesi (metà ingresso è prefisso stabile).
        _consumo("intervista", "intervista", lettura=completata, ingresso=1500, uscita=300, ragionamento=200),
        _consumo("validazione", "validazione", lettura=completata, ingresso=400, uscita=600, ragionamento=550),
        _consumo("interpretazione", "interpretazione", lettura=completata, ingresso=2000, uscita=150),
        _consumo("sintesi", "sintesi", lettura=completata, ingresso=6000, uscita=900, sistema=2000, caratteri=4000,
                 cache=1000),
        # Una lettura ferma all'intervista.
        _consumo("intervista", "intervista", lettura=ferma, ingresso=1500, uscita=300),
        _consumo("intervista", "intervista", lettura=ferma, esito="errore", ingresso=0, uscita=0),
        # Fuori da una lettura: la chat, senza usage (si stima dai caratteri).
        _consumo("chat_proattiva", "chat_proattiva", riferimento="chat", usage=False, caratteri=3500),
    ])
    await session.commit()
    return {"completata": completata, "ferma": ferma}


async def test_solo_l_amministrazione_vede_i_costi(come):
    risposta = await come("utente").get("/admin/costi")
    assert risposta.status_code == 403


async def test_i_consumi_per_compito_lettura_e_listino(come, dati):
    risposta = await come("admin").get("/admin/costi", params={"giorni": 14})
    assert risposta.status_code == 200, risposta.text
    corpo = risposta.json()

    assert [l["nome"] for l in corpo["listini"]] == ["Nebius (in uso)", "DeepInfra"]
    assert corpo["totali"]["chiamate"] == 7 and corpo["totali"]["errori"] == 1 and corpo["totali"]["stimate"] == 1

    per = {(r["compito"], r["fase"]): r for r in corpo["per_compito"]}
    assert per[("intervista", "intervista")]["chiamate"] == 3
    assert per[("validazione", "validazione")]["ragionamento"] == 550
    # La chat senza usage: 3500 caratteri / 3,5 = 1000 token stimati in ingresso, 700 / 3,5 = 200 in uscita.
    assert per[("chat_proattiva", "chat_proattiva")]["ingresso"] == 1000
    assert per[("chat_proattiva", "chat_proattiva")]["uscita"] == 200

    sintesi = per[("sintesi", "sintesi")]
    assert sintesi["cacheabile"] == 3000            # 6000 token × 2000/4000 caratteri di sistema
    # Il listino in uso conta la cache misurata (1000), quello in valutazione il 90% della parte cacheabile (2700).
    assert sintesi["costi"]["Nebius (in uso)"] == pytest.approx((6000 * 0.06 + 900 * 0.24) / 1e6)
    assert sintesi["costi"]["DeepInfra"] == pytest.approx((3300 * 0.06 + 2700 * 0.03 + 900 * 0.16) / 1e6)

    letture = {r["stato"]: r for r in corpo["letture"]}
    assert letture["completata"]["letture"] == 1 and letture["completata"]["chiamate"] == 4
    assert letture["completata"]["per_lettura"]["ingresso"] == 9900
    assert letture["abbandonata"]["letture"] == 1 and letture["abbandonata"]["errori"] == 1
    assert letture["completata"]["costi_per_lettura"]["DeepInfra"] > 0

    fuori = corpo["fuori_lettura"]
    assert fuori and fuori[0]["riferimento"] == "chat"
    assert {g["giorno"] for g in corpo["per_giorno"]}


async def test_i_listini_si_scrivono_dalla_console(come, dati):
    admin = come("admin")
    nuovo = await admin.post("/admin/costi/listini", json={
        "nome": "Darkbloom", "prezzo_ingresso": 0.039, "prezzo_cache": 0.019, "prezzo_uscita": 0.18,
        "cache_hit": 0.7, "nota": "stima",
    })
    assert nuovo.status_code == 201, nuovo.text
    ident = nuovo.json()["id"]

    doppio = await admin.post("/admin/costi/listini", json={
        "nome": "Darkbloom", "prezzo_ingresso": 1, "prezzo_cache": 1, "prezzo_uscita": 1,
    })
    assert doppio.status_code == 409

    fuori_scala = await admin.post("/admin/costi/listini", json={
        "nome": "X", "prezzo_ingresso": 1, "prezzo_cache": 1, "prezzo_uscita": 1, "cache_hit": 1.5,
    })
    assert fuori_scala.status_code == 422

    # Segnarlo «in uso» toglie il segno a Nebius: uno solo alla volta.
    modificato = await admin.put(f"/admin/costi/listini/{ident}", json={
        "nome": "Darkbloom", "prezzo_ingresso": 0.04, "prezzo_cache": 0.02, "prezzo_uscita": 0.18,
        "cache_hit": 0.7, "attuale": True,
    })
    assert modificato.status_code == 200 and modificato.json()["prezzo_ingresso"] == 0.04
    elenco = (await admin.get("/admin/costi/listini")).json()["listini"]
    assert [l["nome"] for l in elenco if l["attuale"]] == ["Darkbloom"]

    assert (await admin.delete(f"/admin/costi/listini/{ident}")).status_code == 204
    assert (await admin.delete(f"/admin/costi/listini/{ident}")).status_code == 404
    assert (await come("utente").post("/admin/costi/listini", json={
        "nome": "Y", "prezzo_ingresso": 1, "prezzo_cache": 1, "prezzo_uscita": 1,
    })).status_code == 403


def test_il_costo_con_la_cache():
    deepinfra = Listino("DeepInfra", 0.06, 0.03, 0.16, cache_hit=0.9)
    # 10 000 token in ingresso di cui 4 000 cacheabili: 3 600 in cache.
    assert costo(deepinfra, ingresso=10_000, uscita=1_000, cacheabile=4_000) == pytest.approx(
        (6_400 * 0.06 + 3_600 * 0.03 + 1_000 * 0.16) / 1e6)
    in_uso = Listino("Nebius", 0.06, 0.06, 0.24, attuale=True)
    assert costo(in_uso, ingresso=10_000, uscita=0, cacheabile=4_000, cache_misurata=0) == pytest.approx(0.0006)
