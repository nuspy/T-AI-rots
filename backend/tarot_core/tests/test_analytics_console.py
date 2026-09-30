"""La console degli analytics (v8): interrogazioni dichiarate, imbuti, coorti, riepilogo notturno."""
from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import func, select

from lanterna import impronta as impronta_
from lanterna import raccolta
from lanterna.giornaliero import notte, pulisci, riepiloga
from lanterna.interroga import ErroreInterrogazione, Interrogazione, esegui

from ..analytics.catalogo import CATALOGO
from ..analytics.configurazione import configurazione
from ..domain.analytics_models import TABELLE
from .conftest import richiede_database
from .test_flusso import _azzera_regalo_iscrizione

pytestmark = richiede_database

IPHONE = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 Version/17.5 Mobile/15E148 Safari/604.1"
WINDOWS = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
OGGI = datetime.now(ZoneInfo("Europe/Rome")).date()


@pytest.fixture(autouse=True)
def stato_pulito():
    raccolta.azzera_limiti()
    impronta_.dimentica_cache()
    yield
    raccolta.azzera_limiti()
    impronta_.dimentica_cache()


async def _visita(session, ip, ua, *eventi, quando=None, utente_id=None, id_browser=None):
    cfg = configurazione()
    quando = quando or datetime.now(timezone.utc)
    corpo = json.dumps({"lingua": "it", "eventi": list(eventi), **({"id": id_browser} if id_browser else {})}).encode()
    lotto = raccolta.interpreta(corpo, cfg, quando)
    return await raccolta.registra(session, TABELLE, cfg, lotto, raccolta.Contesto(ip=ip, agente=ua, utente_id=utente_id, adesso=quando))


async def _traffico(session):
    await _visita(session, "198.51.100.1", IPHONE, {"n": "page_view", "p": "/", "r": "https://www.google.com/"},
                  {"n": "page_view", "p": "/blog"})
    await _visita(session, "198.51.100.2", WINDOWS, {"n": "page_view", "p": "/", "r": "https://www.google.com/"})
    await _visita(session, "198.51.100.3", WINDOWS, {"n": "page_view", "p": "/pricing", "u": {"utm_campaign": "lancio", "utm_source": "ig"}})


def _q(**kw) -> Interrogazione:
    return Interrogazione(**{"da": OGGI, "a": OGGI, **kw})


async def test_visite_per_canale_e_dispositivo(session):
    await _traffico(session)
    r = await esegui(session, CATALOGO, _q(sorgente="visite", misure=["sessioni", "pagine"], dimensioni=["canale"]))
    per_canale = {riga["canale"]: riga for riga in r.righe}
    assert per_canale["ricerca"]["sessioni"] == 2 and per_canale["ricerca"]["pagine"] == 3
    assert per_canale["campagna"]["sessioni"] == 1
    assert r.totali == {"sessioni": 3, "pagine": 4}
    assert [c["tipo"] for c in r.colonne] == ["dimensione", "misura", "misura"]

    r = await esegui(session, CATALOGO, _q(
        sorgente="visite", misure=["sessioni"], dimensioni=["dispositivo"],
        filtri=[{"dimensione": "canale", "operatore": "uguale", "valori": ["ricerca"]}],
    ))
    assert {x["dispositivo"]: x["sessioni"] for x in r.righe} == {"mobile": 1, "desktop": 1}


async def test_granularita_confronto_e_ordine(session):
    await _traffico(session)
    ieri = datetime.now(timezone.utc) - timedelta(days=1)
    await _visita(session, "198.51.100.9", IPHONE, {"n": "page_view", "p": "/"}, quando=ieri)
    r = await esegui(session, CATALOGO, Interrogazione(
        sorgente="visite", misure=["sessioni"], da=OGGI - timedelta(days=1), a=OGGI, granularita="giorno",
    ))
    assert [x["sessioni"] for x in r.righe] == [1, 3]
    assert r.righe[0]["periodo"] < r.righe[1]["periodo"]

    r = await esegui(session, CATALOGO, _q(sorgente="visite", misure=["sessioni"], confronto="precedente"))
    assert r.totali["sessioni"] == 3 and r.confronto["totali"]["sessioni"] == 1
    assert r.confronto["da"] == (OGGI - timedelta(days=1)).isoformat()


async def test_eventi_con_proprieta_come_dimensione(session):
    await _visita(session, "198.51.100.4", IPHONE,
                  {"n": "lettura_fase", "p": "/leggi", "x": {"fase": "stesa"}},
                  {"n": "lettura_fase", "p": "/leggi", "x": {"fase": "intervista"}},
                  {"n": "lettura_fase", "p": "/leggi", "x": {"fase": "intervista"}})
    r = await esegui(session, CATALOGO, _q(
        sorgente="eventi", misure=["eventi"], dimensioni=["prop:fase"],
        filtri=[{"dimensione": "nome", "valori": ["lettura_fase"]}],
    ))
    assert {x["prop:fase"]: x["eventi"] for x in r.righe} == {"intervista": 2, "stesa": 1}


@pytest.mark.parametrize("sbagliata", [
    {"sorgente": "segreti", "misure": ["x"]},
    {"sorgente": "visite", "misure": ["drop table users"]},
    {"sorgente": "visite", "misure": ["sessioni"], "dimensioni": ["email"]},
    {"sorgente": "visite", "misure": ["sessioni"], "filtri": [{"dimensione": "canale", "valori": []}]},
    {"sorgente": "visite", "misure": ["sessioni"], "ordine": {"campo": "canale"}},
    {"sorgente": "eventi", "misure": ["eventi"], "dimensioni": ["prop:x;drop"]},
])
async def test_nomi_fuori_catalogo_rifiutati(session, sbagliata):
    with pytest.raises(ErroreInterrogazione):
        await esegui(session, CATALOGO, _q(**sbagliata))


@pytest.mark.parametrize("nome", list(CATALOGO))
async def test_ogni_misura_e_dimensione_del_catalogo_si_esegue(session, nome):
    """Un'espressione SQL sbagliata nel catalogo (una funzione che non esiste per quel tipo) si vede
    solo eseguendola: qui si eseguono tutte, su tabelle vuote, e con la soglia k attiva."""
    src = CATALOGO[nome]
    await esegui(session, CATALOGO, _q(sorgente=nome, misure=list(src.misure)[:6], confronto="precedente"))
    for misure in (list(src.misure)[i:i + 6] for i in range(0, len(src.misure), 6)):
        await esegui(session, CATALOGO, _q(sorgente=nome, misure=misure, granularita="mese"))
    prima = [next(iter(src.misure))]
    for d in src.dimensioni:
        await esegui(session, CATALOGO, _q(sorgente=nome, misure=prima, dimensioni=[d],
                                           filtri=[{"dimensione": d, "operatore": "contiene", "valori": ["x"]}]), k_minimo=5)


async def test_ritorni_e_giorni_tra_le_visite(session):
    adesso = datetime.now(timezone.utc)
    # Col consenso (id del browser): due visite a due giorni di distanza.
    await _visita(session, "198.51.100.20", IPHONE, {"n": "page_view", "p": "/"}, quando=adesso - timedelta(days=2), id_browser="b-ritorno")
    await _visita(session, "198.51.100.21", IPHONE, {"n": "page_view", "p": "/"}, quando=adesso, id_browser="b-ritorno")
    # Senza consenso né accesso: non si sa se è nuovo.
    await _visita(session, "198.51.100.22", WINDOWS, {"n": "page_view", "p": "/"}, quando=adesso)
    q = Interrogazione(sorgente="visite", misure=["sessioni", "sessioni_di_ritorno", "giorni_tra_visite"],
                       dimensioni=["tipo_visitatore"], da=OGGI - timedelta(days=3), a=OGGI)
    r = await esegui(session, CATALOGO, q)
    per_tipo = {x["tipo_visitatore"]: x for x in r.righe}
    assert per_tipo["di ritorno"]["sessioni"] == 1 and per_tipo["di ritorno"]["giorni_tra_visite"] == 2.0
    assert per_tipo["nuovo"]["sessioni"] == 1
    assert per_tipo["non noto (senza cookie né accesso)"]["sessioni"] == 1
    assert r.totali["sessioni_di_ritorno"] == 1


async def test_paese_e_visite_prima_degli_iscritti(session, utente):
    from lanterna.eventi import segna_registrazione

    adesso = datetime.now(timezone.utc)
    await segna_registrazione(session, TABELLE, utente.id)
    await session.execute(TABELLE.utenti.update().values(visite_prima_registrazione=3))
    s = TABELLE.sessioni
    sessione_id = await _visita(session, "198.51.100.23", IPHONE, {"n": "page_view", "p": "/"}, quando=adesso, utente_id=utente.id)
    await session.execute(s.update().where(s.c.id == sessione_id).values(paese="HU"))
    r = await esegui(session, CATALOGO, _q(sorgente="utenti", misure=["utenti"], dimensioni=["paese", "visite_prima_fascia"]))
    assert r.righe == [{"paese": "HU", "visite_prima_fascia": "2-3", "utenti": 1}]


async def test_intervallo_troppo_lungo(session):
    with pytest.raises(ErroreInterrogazione):
        await esegui(session, CATALOGO, Interrogazione(sorgente="visite", misure=["sessioni"], da=date(2020, 1, 1), a=OGGI))


async def test_soglia_k_sulle_dimensioni_personali(session, utente):
    utente.birth_date = date(1990, 5, 1)
    utente.gender = "donna"
    await session.commit()
    q = _q(sorgente="utenti", misure=["utenti"], dimensioni=["genere"])
    senza = await esegui(session, CATALOGO, q)
    assert senza.righe == [{"genere": "donna", "utenti": 1}]
    con = await esegui(session, CATALOGO, q, k_minimo=5)
    assert con.righe == [] and con.soppresse == 1
    # Una dimensione non personale non si sopprime.
    assert (await esegui(session, CATALOGO, _q(sorgente="utenti", misure=["utenti"], dimensioni=["invitato"]), k_minimo=5)).righe


async def test_console_richiede_admin_e_risponde(client, principal_admin):
    assert (await client.get("/admin/analytics/catalogo")).status_code == 403
    client.identita.principal = principal_admin
    r = await client.get("/admin/analytics/catalogo")
    assert r.status_code == 200
    corpo = r.json()
    assert {"visite", "eventi", "utenti", "letture", "acquisti", "ordini", "riepilogo"} <= set(corpo["sorgenti"])
    assert "sql" not in json.dumps(corpo).lower()
    r = await client.post("/admin/analytics/interroga", json={
        "sorgente": "visite", "misure": ["sessioni"], "da": OGGI.isoformat(), "a": OGGI.isoformat(),
    })
    assert r.status_code == 200 and r.json()["totali"] == {"sessioni": 0}
    r = await client.post("/admin/analytics/interroga", json={
        "sorgente": "visite", "misure": ["password"], "da": OGGI.isoformat(), "a": OGGI.isoformat(),
    })
    assert r.status_code == 422


async def test_acquisti_dalle_tabelle_di_business(client, session, catalogo, principal_admin):
    await _azzera_regalo_iscrizione(session)
    r = await client.post("/me/checkout", json={"piano": "pacchetto-15", "ritorno": "/leggi"})
    importo = r.json()["importo"]
    await client.post(f"/billing/mock/checkout/{r.json()['checkout_id']}/esito", data={"esito": "paga", "ritorno": "http://localhost:3000/leggi"})
    client.identita.principal = principal_admin
    r = await client.post("/admin/analytics/interroga", json={
        "sorgente": "acquisti", "misure": ["acquisti", "ricavi", "clienti"], "dimensioni": ["piano"],
        "da": OGGI.isoformat(), "a": OGGI.isoformat(),
    })
    assert r.status_code == 200, r.text
    assert r.json()["righe"] == [{"piano": "pacchetto-15", "acquisti": 1, "ricavi": importo / 100, "clienti": 1}]


async def test_imbuto_della_lettura(client, session, principal_admin):
    fasi = ["stesa", "intervista", "scelta", "rivelazione", "completata"]
    # Una sessione arriva in fondo, una si ferma all'intervista.
    await _visita(session, "198.51.100.5", IPHONE, {"n": "page_view", "p": "/leggi"},
                  *[{"n": "lettura_fase", "p": "/leggi", "x": {"fase": f}} for f in fasi])
    await _visita(session, "198.51.100.6", WINDOWS, {"n": "page_view", "p": "/leggi"},
                  *[{"n": "lettura_fase", "p": "/leggi", "x": {"fase": f}} for f in fasi[:2]])
    await session.commit()
    client.identita.principal = principal_admin
    r = await client.post("/admin/analytics/imbuto", json={"imbuto": "lettura", "da": OGGI.isoformat(), "a": OGGI.isoformat()})
    assert r.status_code == 200, r.text
    assert [p["n"] for p in r.json()["passi"]] == [2, 2, 2, 1, 1, 1]
    assert r.json()["passi"][3]["dal_precedente"] == 0.5
    r = await client.post("/admin/analytics/imbuto", json={
        "imbuto": "lettura", "da": OGGI.isoformat(), "a": OGGI.isoformat(), "segmento": "dispositivo",
    })
    segmenti = {s["valore"]: [p["n"] for p in s["passi"]] for s in r.json()["segmenti"]}
    assert segmenti == {"mobile": [1, 1, 1, 1, 1, 1], "desktop": [1, 1, 1, 0, 0, 0]}


async def test_imbuto_della_lettura_v2_separato_dal_sito(client, session, principal_admin):
    """La lettura della v2 ha il suo imbuto; i suoi eventi non entrano in quello del sito, e viceversa."""
    fasi_v2 = ["preparazione", "intervista", "taglio", "scelta", "rivelazione", "completata"]
    await _visita(session, "198.51.100.7", IPHONE, {"n": "page_view", "p": "/v2/read"},
                  *[{"n": "lettura_fase", "p": "/v2/read", "x": {"fase": f}} for f in fasi_v2])
    await _visita(session, "198.51.100.8", WINDOWS, {"n": "page_view", "p": "/it/v2/read"},
                  *[{"n": "lettura_fase", "p": "/it/v2/read", "x": {"fase": f}} for f in fasi_v2[:3]])
    await session.commit()
    client.identita.principal = principal_admin
    r = await client.post("/admin/analytics/imbuto", json={"imbuto": "lettura_v2", "da": OGGI.isoformat(), "a": OGGI.isoformat()})
    assert r.status_code == 200, r.text
    assert [p["n"] for p in r.json()["passi"]] == [2, 2, 2, 2, 1, 1, 1]
    r = await client.post("/admin/analytics/imbuto", json={"imbuto": "lettura", "da": OGGI.isoformat(), "a": OGGI.isoformat()})
    assert [p["n"] for p in r.json()["passi"]] == [0, 0, 0, 0, 0, 0]


async def test_imbuto_iscrizione_lega_l_evento_di_server_alla_visita(client, session, principal_admin):
    client.identita.principal = None
    intestazioni = {"user-agent": IPHONE, "x-real-ip": "198.51.100.7"}
    lotto = lambda *ev: json.dumps({"eventi": list(ev)})  # noqa: E731
    await client.post("/e", content=lotto({"n": "page_view", "p": "/"}, {"n": "cta_iscrizione", "p": "/"}), headers=intestazioni)
    from tarot_core.auth.keycloak import Principal

    client.identita.principal = Principal(subject="sub-nuovo", email="n@example.com", display_name="N", roles={"user"})
    await client.get("/me/profile")  # iscrizione: evento di server senza sessione
    await client.post("/e", content=lotto({"n": "page_view", "p": "/profilo"}), headers=intestazioni)
    client.identita.principal = principal_admin
    r = await client.post("/admin/analytics/imbuto", json={"imbuto": "iscrizione", "da": OGGI.isoformat(), "a": OGGI.isoformat()})
    assert [p["n"] for p in r.json()["passi"]] == [1, 1, 1]


async def test_coorti_di_letture(client, session, principal_admin, catalogo):
    from .test_flusso import _lettura_completa

    await _lettura_completa(client, "tre-carte", 3)
    client.identita.principal = principal_admin
    r = await client.post("/admin/analytics/coorti", json={"tipo": "letture", "periodi": 3})
    assert r.status_code == 200, r.text
    coorti = r.json()["coorti"]
    assert sum(c["dimensione"] for c in coorti) >= 1
    assert any(c["valori"][0] >= 1 for c in coorti)


async def test_riepilogo_idempotente_uguale_al_dettaglio_e_pulizia(session):
    await _traffico(session)
    await _visita(session, "198.51.100.8", IPHONE, {"n": "acquisto_finto", "p": "/"})
    assert await riepiloga(session, TABELLE, OGGI) > 0
    await riepiloga(session, TABELLE, OGGI)  # di nuovo: nessun doppione
    g = TABELLE.giornaliero
    eventi = (await session.execute(select(func.sum(g.c.eventi)).where(g.c.giorno == OGGI))).scalar_one()
    grezzi = (await session.execute(select(func.count()).select_from(TABELLE.eventi))).scalar_one()
    assert eventi == grezzi == 5
    r = await esegui(session, CATALOGO, _q(sorgente="riepilogo", misure=["eventi"], dimensioni=["canale"]))
    assert sum(x["eventi"] for x in r.righe) == 5

    # Dettaglio oltre la conservazione: sparisce; il riepilogo resta.
    vecchio = datetime.now(timezone.utc) - timedelta(days=800)
    await _visita(session, "198.51.100.10", IPHONE, {"n": "page_view", "p": "/"}, quando=vecchio)
    esito = await pulisci(session, TABELLE, configurazione())
    assert esito["sessioni"] == 1 and esito["eventi"] == 1
    assert (await session.execute(select(func.count()).select_from(g))).scalar_one() > 0


async def test_giro_notturno(session):
    ieri = datetime.now(timezone.utc) - timedelta(days=1)
    await _visita(session, "198.51.100.11", IPHONE, {"n": "page_view", "p": "/"}, quando=ieri)
    resoconto = await notte(session, TABELLE, configurazione())
    assert any(k.startswith("riepilogo_") and v >= 1 for k, v in resoconto.items())
