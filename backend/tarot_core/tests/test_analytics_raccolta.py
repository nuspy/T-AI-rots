"""La raccolta degli analytics (v8, libreria `lanterna`): `POST /e`, sessioni, utenti, eventi di server."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select, text

from lanterna import impronta as impronta_
from lanterna import raccolta
from lanterna.eventi import emetti_evento, imposta_opposizione, segna_registrazione

from ..analytics.configurazione import configurazione
from ..api.routers import analytics as router_analytics
from ..domain.analytics_models import TABELLE
from .conftest import richiede_database

pytestmark = richiede_database

IPHONE = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1"
)
IP = "203.0.113.7"
INTESTAZIONI = {"user-agent": IPHONE, "x-real-ip": IP, "content-type": "text/plain"}


@pytest.fixture(autouse=True)
def stato_pulito():
    router_analytics._ID_PER_SUB.clear()
    raccolta.azzera_limiti()
    impronta_.dimentica_cache()
    yield
    router_analytics._ID_PER_SUB.clear()
    raccolta.azzera_limiti()
    impronta_.dimentica_cache()


def _lotto(*eventi, **altro) -> str:
    return json.dumps({"v": 1, "lingua": "it", "eventi": list(eventi), **altro})


async def _righe(session, tabella):
    return [dict(r) for r in (await session.execute(select(tabella))).mappings().all()]


async def test_visita_anonima_senza_ip_e_senza_query(client, session):
    client.identita.principal = None
    r = await client.post(
        "/e",
        content=_lotto(
            {"n": "page_view", "p": "/leggi?domanda=sposero+mario", "r": "https://www.google.it/",
             "u": {"utm_campaign": "autunno"}},
        ),
        headers=INTESTAZIONI,
    )
    assert r.status_code == 204
    sessioni = await _righe(session, TABELLE.sessioni)
    eventi = await _righe(session, TABELLE.eventi)
    assert len(sessioni) == 1 and len(eventi) == 1
    s = sessioni[0]
    assert s["utente_id"] is None and s["visitatore_esteso"] is None
    assert s["canale"] == "campagna" and s["utm_campagna"] == "autunno"
    assert s["referrer_dominio"] == "google.it"
    assert (s["dispositivo"], s["browser"], s["so"], s["lingua"]) == ("mobile", "Safari", "iOS", "it")
    assert s["ingresso"] == "/leggi" and eventi[0]["percorso"] == "/leggi"
    # L'indirizzo, lo user agent e la domanda non compaiono in nessuna colonna di nessuna tabella.
    tutto = json.dumps([await _righe(session, t) for t in (TABELLE.sessioni, TABELLE.eventi, TABELLE.utenti)], default=str)
    assert IP not in tutto and "iPhone OS" not in tutto and "mario" not in tutto


async def test_stessa_sessione_entro_trenta_minuti_poi_nuova(session):
    cfg = configurazione()
    adesso = datetime.now(timezone.utc)
    for i, percorso in enumerate(("/", "/blog")):
        lotto = raccolta.interpreta(_lotto({"n": "page_view", "p": percorso}).encode(), cfg, adesso)
        await raccolta.registra(session, TABELLE, cfg, lotto, raccolta.Contesto(ip=IP, agente=IPHONE, adesso=adesso + timedelta(minutes=i)))
    sessioni = await _righe(session, TABELLE.sessioni)
    assert len(sessioni) == 1
    assert sessioni[0]["pagine"] == 2 and sessioni[0]["coinvolta"] and sessioni[0]["uscita"] == "/blog"

    dopo = adesso + timedelta(minutes=45)
    lotto = raccolta.interpreta(_lotto({"n": "page_view", "p": "/"}).encode(), cfg, dopo)
    await raccolta.registra(session, TABELLE, cfg, lotto, raccolta.Contesto(ip=IP, agente=IPHONE, adesso=dopo))
    assert len(await _righe(session, TABELLE.sessioni)) == 2


async def test_una_campagna_nuova_apre_una_sessione_nuova(session):
    cfg = configurazione()
    adesso = datetime.now(timezone.utc)
    for campagna in ("a", "b"):
        lotto = raccolta.interpreta(_lotto({"n": "page_view", "p": "/", "u": {"utm_campaign": campagna}}).encode(), cfg, adesso)
        await raccolta.registra(session, TABELLE, cfg, lotto, raccolta.Contesto(ip=IP, agente=IPHONE, adesso=adesso))
    assert sorted(s["utm_campagna"] for s in await _righe(session, TABELLE.sessioni)) == ["a", "b"]


async def test_bot_corpi_malformati_e_percorsi_esclusi_si_scartano_con_204(client, session):
    client.identita.principal = None
    casi = [
        (_lotto({"n": "page_view", "p": "/"}), {**INTESTAZIONI, "user-agent": "Googlebot/2.1 (+http://www.google.com/bot.html)"}),
        ("non json", INTESTAZIONI),
        (json.dumps({"eventi": "no"}), INTESTAZIONI),
        (_lotto({"n": "Nome Non Valido", "p": "/"}), INTESTAZIONI),
        (_lotto({"n": "page_view", "p": "/admin/utenti"}), INTESTAZIONI),
        ("x" * 20_000, INTESTAZIONI),
    ]
    for corpo, intestazioni in casi:
        r = await client.post("/e", content=corpo, headers=intestazioni)
        assert r.status_code == 204
    assert await _righe(session, TABELLE.eventi) == []


async def test_limite_di_frequenza(client, session):
    client.identita.principal = None
    lotto = _lotto(*[{"n": "click", "p": "/"} for _ in range(20)])
    for _ in range(4):
        await client.post("/e", content=lotto, headers=INTESTAZIONI)
    # 60 al minuto: il quarto lotto da 20 supera il limite e si scarta.
    assert len(await _righe(session, TABELLE.eventi)) == 60


async def test_utente_autenticato_ultimo_accesso_e_primo_contatto(client, session):
    r = await client.post(
        "/e",
        content=_lotto({"n": "page_view", "p": "/", "r": "https://chatgpt.com/"}),
        headers=INTESTAZIONI,
    )
    assert r.status_code == 204
    # La raccolta non crea utenti: il primo lotto di un `sub` mai visto resta anonimo.
    assert (await _righe(session, TABELLE.sessioni))[0]["utente_id"] is None

    profilo = await client.get("/me/profile")  # crea l'utente, come al primo accesso vero
    assert profilo.status_code == 200
    utente_id = (await session.execute(text("select id from users where keycloak_sub = 'sub-utente-1'"))).scalar_one()
    await client.post("/e", content=_lotto({"n": "page_view", "p": "/profilo"}), headers=INTESTAZIONI)

    sessioni = await _righe(session, TABELLE.sessioni)
    assert len(sessioni) == 1 and sessioni[0]["utente_id"] == utente_id
    [u] = await _righe(session, TABELLE.utenti)
    assert u["utente_id"] == utente_id and u["giorni_attivi"] == 1 and u["ultimo_accesso"] is not None
    assert u["primo_canale"] == "assistenti_ai" and u["primo_referrer_dominio"] == "chatgpt.com"
    assert u["prima_pagina"] == "/"


async def test_opposizione_toglie_il_legame(client, session):
    await client.get("/me/profile")
    utente_id = (await session.execute(text("select id from users where keycloak_sub = 'sub-utente-1'"))).scalar_one()
    await client.post("/e", content=_lotto({"n": "page_view", "p": "/"}), headers=INTESTAZIONI)
    await imposta_opposizione(session, TABELLE, utente_id, True)
    await session.commit()
    await client.post("/e", content=_lotto({"n": "page_view", "p": "/blog"}), headers=INTESTAZIONI)
    assert all(s["utente_id"] is None for s in await _righe(session, TABELLE.sessioni))
    assert all(e["utente_id"] is None for e in await _righe(session, TABELLE.eventi))
    [u] = await _righe(session, TABELLE.utenti)
    assert u["escluso"] and u["primo_canale"] is None


async def test_livello_esteso_solo_con_id_e_revocabile(client, session):
    client.identita.principal = None
    await client.post("/e", content=_lotto({"n": "page_view", "p": "/"}), headers=INTESTAZIONI)
    assert (await _righe(session, TABELLE.sessioni))[0]["visitatore_esteso"] is None
    await client.post("/e", content=_lotto({"n": "page_view", "p": "/blog"}, id="browser-123"), headers=INTESTAZIONI)
    esteso = (await _righe(session, TABELLE.sessioni))[0]["visitatore_esteso"]
    assert esteso and "browser-123" not in esteso
    r = await client.post("/e/dimentica", content=json.dumps({"id": "browser-123"}), headers=INTESTAZIONI)
    assert r.status_code == 204
    assert (await _righe(session, TABELLE.sessioni))[0]["visitatore_esteso"] is None


async def test_visite_prima_della_registrazione_col_livello_esteso(session, utente):
    cfg = configurazione()
    inizio = datetime.now(timezone.utc) - timedelta(days=3)
    for giorni, ref in ((0, "https://www.instagram.com/"), (1, None)):
        quando = inizio + timedelta(days=giorni)
        lotto = raccolta.interpreta(_lotto({"n": "page_view", "p": "/", "r": ref}, id="b-1").encode(), cfg, quando)
        await raccolta.registra(session, TABELLE, cfg, lotto, raccolta.Contesto(ip=IP, agente=IPHONE, adesso=quando))
    await segna_registrazione(session, TABELLE, utente.id, adesso=datetime.now(timezone.utc) - timedelta(minutes=5))
    adesso = datetime.now(timezone.utc)
    lotto = raccolta.interpreta(_lotto({"n": "page_view", "p": "/profilo"}, id="b-1").encode(), cfg, adesso)
    await raccolta.registra(session, TABELLE, cfg, lotto, raccolta.Contesto(ip=IP, agente=IPHONE, utente_id=utente.id, adesso=adesso))
    [u] = await _righe(session, TABELLE.utenti)
    assert u["visite_prima_registrazione"] == 2
    assert u["primo_canale"] == "social" and u["primo_referrer_dominio"] == "instagram.com"


async def test_evento_di_server_si_lega_alla_sessione_recente(session, utente):
    cfg = configurazione()
    adesso = datetime.now(timezone.utc)
    lotto = raccolta.interpreta(_lotto({"n": "page_view", "p": "/piano", "u": {"utm_source": "newsletter", "utm_medium": "email"}}).encode(), cfg, adesso)
    sessione_id = await raccolta.registra(
        session, TABELLE, cfg, lotto, raccolta.Contesto(ip=IP, agente=IPHONE, utente_id=utente.id, adesso=adesso)
    )
    assert await emetti_evento(session, TABELLE, "acquisto", utente_id=utente.id, valore_centesimi=990, valuta="eur", proprieta={"piano": "mensile"})
    acquisto = [e for e in await _righe(session, TABELLE.eventi) if e["nome"] == "acquisto"][0]
    assert acquisto["sessione_id"] == sessione_id and acquisto["origine"] == "server"
    assert (acquisto["valore_centesimi"], acquisto["valuta"], acquisto["proprieta"]) == (990, "EUR", {"piano": "mensile"})


async def test_un_errore_delle_statistiche_non_rompe_la_transazione(session, utente, monkeypatch):
    from lanterna import eventi as eventi_

    def rotto(*a, **k):
        raise RuntimeError("tabella sparita")

    monkeypatch.setattr(eventi_, "insert", rotto)
    assert await emetti_evento(session, TABELLE, "acquisto", utente_id=utente.id) is False
    # La sessione del chiamante è ancora utilizzabile e il suo lavoro si conferma.
    assert (await session.execute(text("select 1"))).scalar_one() == 1
    await session.commit()
