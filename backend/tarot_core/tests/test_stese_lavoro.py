"""Lavoro e affari: le cinque stese della categoria `lavoro`, i `temi` delle stese standard adatte
anche al lavoro, l'elenco per categoria e per tema, e una lettura di lavoro dall'apertura al responso
(col modello finto: nessuna chiamata a un modello vero)."""
from __future__ import annotations

import copy
from dataclasses import replace
from itertools import combinations

import pytest

from tarot_core.tarot import cag
from tarot_core.tarot.conoscenza import Conoscenza, ConoscenzaNonValida, speciale
from tarot_core.tarot.intervista import PROMPT_INTERVISTA_LAVORO, sistema_intervista

from .conftest import eventi_sse, richiede_database
from .test_flusso import _accredita, _lettura_completa
from .test_lettura_speciale import PARTNER

LAVORO = {
    # id: (stile, carte, mazzo)
    "lavoro-trattativa": ("tendenza", 4, "completo"),
    "lavoro-offerta": ("tendenza", 5, "completo"),
    "lavoro-swot": ("moderna", 6, "completo"),
    "lavoro-restare-andare": ("tendenza", 7, "completo"),
    "lavoro-impresa": ("moderna", 9, "completo"),
}

#: Le stese standard che si propongono anche per il lavoro.
ADATTE = ("tre-carte", "croce-semplice", "ferro-di-cavallo", "croce-celtica")

QUESITO = "Devo accettare la nuova offerta di lavoro?"


@pytest.fixture(scope="module")
def conoscenza() -> Conoscenza:
    return Conoscenza.carica()


def _con_stese(conoscenza: Conoscenza, stese) -> Conoscenza:
    return replace(conoscenza, stese={s["id"]: s for s in stese})


# ---- il catalogo -------------------------------------------------------------------------------


def test_le_cinque_stese_di_lavoro_ci_sono_con_stile_carte_e_mazzo(conoscenza):
    assert [s["id"] for s in conoscenza.stese_per("lavoro")] == list(LAVORO)
    for id_, (stile, carte, mazzo) in LAVORO.items():
        stesa = conoscenza.stesa(id_)
        assert conoscenza.categoria_di(stesa) == "lavoro" and not speciale("lavoro")
        assert stesa["stile"] == stile and stesa["mazzo"] == mazzo
        assert stesa["carte_da_scegliere"] == carte == len(stesa["posizioni"])
        assert not stesa.get("sintesi_wirth") and stesa.get("nota_intervista")
        for p in stesa["posizioni"]:
            assert "soggetto" not in p and p["calcolata"] is False and p["rotazione"] == 0
            assert p["nome"] and p["nome_en"] and p["significato"] and p["domanda"].endswith("?")


def test_le_categorie_speciali_restano_due(conoscenza):
    assert [c for c in ("standard", "lavoro", "compatibilita", "coppia") if speciale(c)] == ["compatibilita", "coppia"]


def test_le_stese_di_lavoro_hanno_testi_inglesi_e_nomi_nelle_lingue(conoscenza):
    for id_ in LAVORO:
        stesa = conoscenza.stesa(id_)
        scheda = conoscenza.testi["en"]["stese"][id_]
        assert scheda["slug"].endswith("-spread") and conoscenza.risolvi_stesa(scheda["slug"]) == id_
        assert len(scheda["regole"]) == len(stesa["regole"])
        for codice in ("hu", "ru", "uk", "es"):
            nomi = conoscenza.nomi[codice]["stese"][id_]
            assert nomi["nome"] and set(nomi["posizioni"]) == {str(p["n"]) for p in stesa["posizioni"]}
            assert conoscenza.nome_stesa(stesa, codice) == nomi["nome"]


def test_russo_ucraino_e_spagnolo_hanno_i_nomi_di_tutto_il_catalogo(conoscenza):
    for codice in ("ru", "uk", "es"):
        assert set(conoscenza.nomi[codice]["carte"]) == set(conoscenza.carte)
        assert set(conoscenza.nomi[codice]["stese"]) == set(conoscenza.stese)
    assert conoscenza.nome_carta("dischi-03", "ru") == "Тройка Дисков — Работа"
    assert conoscenza.nome_carta("maj-11", "uk") == "Хіть"
    assert conoscenza.nome_carta("spade-principessa", "es") == "Princesa de Espadas"
    assert conoscenza.nome_posizione(conoscenza.stesa("croce-celtica"), 10, "es") == "El resultado"


def test_le_carte_non_si_sovrappongono_e_restano_sul_tavolo(conoscenza):
    """Il tavolo è 16:12 (1:1 sugli schermi stretti e per le stese quadrate); le carte sono 9:16 e
    larghe `larghezza` × 1,2 del tavolo, centrate sulle coordinate."""
    for id_ in LAVORO:
        stesa = conoscenza.stesa(id_)
        quadrata = stesa.get("forma") == "quadrata"
        casi = [(1.0, stesa["larghezza"])] if quadrata else [
            (0.75, stesa["larghezza"]), (1.0, stesa.get("larghezza_stretto", stesa["larghezza"] * 1.15)),
        ]
        for altezza_tavolo, larghezza in casi:
            w = larghezza * 1.2
            h = w * 16 / 9 / altezza_tavolo
            for a, b in combinations(stesa["posizioni"], 2):
                assert abs(a["x"] - b["x"]) >= w or abs(a["y"] - b["y"]) >= h, (id_, a["n"], b["n"])
            for p in stesa["posizioni"]:
                assert w / 2 <= p["x"] <= 1 - w / 2 and h / 2 <= p["y"] <= 1 - h / 2, (id_, p["n"])


# ---- i temi -------------------------------------------------------------------------------------


def test_le_stese_standard_adatte_al_lavoro_lo_dichiarano(conoscenza):
    assert [s["id"] for s in conoscenza.stese.values() if s.get("temi")] == list(ADATTE)
    assert all(conoscenza.stesa(i)["temi"] == ["lavoro"] for i in ADATTE)
    assert [s["id"] for s in conoscenza.stese_per_tema("lavoro")] == [*LAVORO, *ADATTE]


def test_temi_esposti_nella_stesa_pubblica(conoscenza):
    assert conoscenza.stesa_pubblica(conoscenza.stesa("croce-celtica"))["temi"] == ["lavoro"]
    assert conoscenza.stesa_pubblica(conoscenza.stesa("ruota-astrologica"))["temi"] == []
    inglese = conoscenza.stesa_pubblica(conoscenza.stesa("lavoro-swot"), "en")
    assert inglese["categoria"] == "lavoro" and inglese["categoria_label"] == "Work and business spread"
    assert inglese["nome"] == "SWOT Spread" and inglese["slug"] == "swot-spread" and inglese["temi"] == []


@pytest.mark.parametrize("temi, errore", [
    (["amore"], "temi sconosciuti"),
    (["lavoro", "lavoro"], "temi ripetuti"),
    ("lavoro", "lista"),
    ([], "lista"),
])
def test_temi_non_validi_fermano_l_avvio(conoscenza, temi, errore):
    stese = copy.deepcopy(list(conoscenza.stese.values()))
    stese[0]["temi"] = temi
    with pytest.raises(ConoscenzaNonValida, match=errore):
        _con_stese(conoscenza, stese).valida()


def test_solo_le_stese_standard_hanno_temi(conoscenza):
    for id_ in ("coppia-bivio", "lavoro-swot"):
        stese = copy.deepcopy(list(conoscenza.stese.values()))
        next(s for s in stese if s["id"] == id_)["temi"] = ["lavoro"]
        with pytest.raises(ConoscenzaNonValida, match="solo una stesa standard"):
            _con_stese(conoscenza, stese).valida()


@pytest.mark.parametrize("guasto, errore", [
    (lambda s: s.pop("stile"), "stile"),
    (lambda s: s["posizioni"][0].update(soggetto="tu"), "soggetto"),
    (lambda s: s.update(sintesi_wirth=True), "Wirth"),
    (lambda s: s.update(categoria="affari"), "categoria sconosciuta"),
])
def test_una_stesa_di_lavoro_guasta_ferma_l_avvio(conoscenza, guasto, errore):
    stese = copy.deepcopy(list(conoscenza.stese.values()))
    guasto(next(s for s in stese if s["id"] == "lavoro-offerta"))
    with pytest.raises(ConoscenzaNonValida, match=errore):
        _con_stese(conoscenza, stese).valida()


# ---- i prompt -----------------------------------------------------------------------------------


def test_l_intervista_e_la_sintesi_di_lavoro_hanno_le_loro_regole(conoscenza):
    assert sistema_intervista("standard") == sistema_intervista() and len(sistema_intervista()) == 1
    assert sistema_intervista("lavoro")[1] == PROMPT_INTERVISTA_LAVORO
    assert "compatibilità e coppia" in sistema_intervista("coppia")[1]
    lavoro = cag.prefisso(conoscenza, [], "lavoro")
    assert "Regole per le letture di lavoro e affari" in lavoro and "## La tendenza più probabile" in lavoro
    assert "Regole per le letture di lavoro" not in cag.prefisso(conoscenza, [], "standard")
    assert cag.PROMPT_PER_CATEGORIA["standard"] == cag.PROMPT_SINTESI


# ---- attraverso l'API ---------------------------------------------------------------------------


@richiede_database
async def test_le_stese_si_elencano_per_categoria_e_per_tema(client, catalogo):
    lavoro = (await client.get("/spreads", params={"categoria": "lavoro"})).json()
    assert [s["id"] for s in lavoro] == list(LAVORO) and all(s["categoria"] == "lavoro" for s in lavoro)
    tema = (await client.get("/spreads", params={"tema": "lavoro", "lang": "en"})).json()
    assert [s["id"] for s in tema] == [*LAVORO, *ADATTE]
    assert all(s["categoria"] == "lavoro" or "lavoro" in s["temi"] for s in tema)
    standard = (await client.get("/spreads", params={"categoria": "standard"})).json()
    assert all(s["categoria"] == "standard" for s in standard) and len(standard) == 5
    assert (await client.get("/spreads", params={"tema": "amore"})).status_code == 422
    stesa = (await client.get("/spreads/stay-or-go-spread", params={"lang": "en"})).json()
    assert stesa["id"] == "lavoro-restare-andare" and stesa["temi"] == [] and stesa["stile"] == "tendenza"


@richiede_database
@pytest.mark.parametrize("spread_id", list(LAVORO))
async def test_una_lettura_di_lavoro_completa_per_ogni_stesa(client, session, catalogo, spread_id):
    await _accredita(session, client.identita.principal, 5)
    fine = await _lettura_completa(client, spread_id, LAVORO[spread_id][1], QUESITO)
    assert fine["saldo"] == 4
    lettura = (await client.get("/me/readings")).json()["letture"][0]
    dettaglio = (await client.get(f"/me/readings/{lettura['id']}")).json()
    assert dettaglio["categoria"] == "lavoro" and dettaglio["stile"] == LAVORO[spread_id][0]
    assert dettaglio["persone"] is None and dettaglio["compatibilita"] is None


@richiede_database
async def test_una_lettura_di_lavoro_non_chiede_ne_ammette_il_partner(client, session, catalogo):
    await _accredita(session, client.identita.principal, 5)
    # Nessuna scheda personale (genere, nascita): non serve, come nella standard.
    r = await client.post("/readings", json={"spread_id": "lavoro-swot", "question": QUESITO})
    assert r.status_code == 201, r.text
    r = await client.post("/readings", json={"spread_id": "lavoro-swot", "question": QUESITO, "partner": PARTNER})
    assert r.status_code == 422 and r.json()["detail"]["motivo"] == "partner_non_ammesso"


@richiede_database
async def test_ai_prompt_della_lettura_di_lavoro_arrivano_le_regole_del_lavoro(client, session, catalogo, prompt_visti):
    await _accredita(session, client.identita.principal, 5)
    await _lettura_completa(client, "lavoro-offerta", 5, QUESITO)
    intervista = [v for v in prompt_visti if v["compito"] == "intervista"]
    assert intervista and all("Regole aggiuntive: lavoro e affari" in v["sistema"] for v in intervista)
    assert all("Nota sulla stesa: Chiarisci se si tratta di un colloquio" in v["utente"] for v in intervista)
    interpretazioni = [v for v in prompt_visti if v["compito"] == "interpretazione_unica"]
    assert len(interpretazioni) == 1 and interpretazioni[0]["utente"].count("## Carta in posizione ") == 5
    assert all("Regole aggiuntive: lavoro e affari" in v["sistema"] for v in interpretazioni)
    sintesi = next(v for v in prompt_visti if v["compito"] == "sintesi")
    assert "Regole per le letture di lavoro e affari" in sintesi["sistema"]
    for v in prompt_visti:
        testo = v["sistema"] + "\n" + v["utente"]
        assert "compatibilità e coppia" not in testo and "## Le persone" not in testo and "Riguarda:" not in testo


@richiede_database
async def test_la_lettura_anonima_ammette_il_lavoro(client, session):
    client.identita.principal = None
    r = await client.post("/readings/anonime", json={"spread_id": "lavoro-trattativa", "question": QUESITO})
    assert r.status_code == 201, r.text
    assert r.json()["categoria"] == "lavoro" and r.json()["stesa"]["id"] == "lavoro-trattativa"
    rid = r.json()["id"]

    r = await client.post(f"/readings/{rid}/interview", json={})
    while not r.json().get("completa"):
        r = await client.post(f"/readings/{rid}/interview", json={"risposta": "Un rinnovo di contratto, a fine mese."})
    ventaglio = (await client.post(f"/readings/{rid}/fan")).json()
    assert ventaglio["da_scegliere"] == 4
    for slot in range(4):
        assert (await client.post(f"/readings/{rid}/pick", json={"slot": slot})).status_code == 200
    for n in range(1, 5):
        assert (await client.post(f"/readings/{rid}/reveal/{n}")).status_code == 200
    eventi = eventi_sse((await client.post(f"/readings/{rid}/synthesis")).text)
    assert next(d for e, d in eventi if e == "fine")["anonimo"] is True


@richiede_database
async def test_una_sezione_del_blog_elenca_le_stese_per_il_lavoro(client, principal_admin):
    from .test_blog_api import _sezione

    client.identita.principal = principal_admin
    await _sezione(client, "Stese per il lavoro", tipo="stese", filtro={"tema": "lavoro"})
    await _sezione(client, "Lavoro e affari", tipo="stese", filtro={"categoria": "lavoro"})
    tema = (await client.get("/blog/sections/stese-per-il-lavoro")).json()["elementi"]
    assert [e["id"] for e in tema] == [*LAVORO, *ADATTE]
    categoria = (await client.get("/blog/sections/lavoro-e-affari")).json()["elementi"]
    assert [e["id"] for e in categoria] == list(LAVORO)
