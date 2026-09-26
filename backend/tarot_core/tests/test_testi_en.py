"""I testi lunghi in inglese: la lingua canonica delle pagine pubbliche.

Senza database né rete: si carica la base di conoscenza e si guardano i dati.
"""
from __future__ import annotations

import re

import pytest

from tarot_core.tarot.conoscenza import Conoscenza, ConoscenzaNonValida

# Parole italiane che in un testo inglese sono il segno di una traduzione dimenticata.
ITALIANO = re.compile(r"\b(della|delle|degli|nella|nelle|nello|quando|perché|sempre|questo|questa|che|una|uno|gli)\b", re.I)


@pytest.fixture(scope="module")
def k() -> Conoscenza:
    return Conoscenza.carica()


def _testi_carta(scheda: dict) -> list:
    return [scheda["astro"], *scheda["kw"], *(scheda[c] for c in ("exo", "psy", "ini", "sha", "up", "rev", "love", "work", "spirit", "crowley"))]


def test_le_78_carte_e_le_14_stese_hanno_il_loro_testo_inglese(k):
    assert set(k.testi["en"]["carte"]) == set(k.carte) and len(k.carte) == 78
    assert set(k.testi["en"]["stese"]) == set(k.stese) and len(k.stese) == 14


def test_nessuna_parola_italiana_nei_testi_inglesi(k):
    trovate = []
    for card_id, scheda in k.testi["en"]["carte"].items():
        for testo in _testi_carta(scheda):
            trovate += [(card_id, m.group(0)) for m in ITALIANO.finditer(testo)]
    for spread_id, scheda in k.testi["en"]["stese"].items():
        testi = [scheda["nome"], scheda["origine"], scheda["descrizione"], *scheda["regole"]]
        for p in scheda["pos"].values():
            testi += [p["nome"], p["significato"], p["domanda"]]
        for testo in testi:
            trovate += [(spread_id, m.group(0)) for m in ITALIANO.finditer(testo)]
    assert not trovate, trovate[:10]


def test_gli_slug_sono_validi_e_non_si_scontrano_fra_lingue(k):
    for id_ in k.carte:
        for lingua in ("it", "en"):
            assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", k.slug_carta(id_, lingua)), (id_, lingua)
    # Ogni slug, in qualunque lingua, porta alla sua carta e a nessun'altra.
    for id_ in k.carte:
        for chiave in (id_, k.slug_carta(id_, "it"), k.slug_carta(id_, "en")):
            assert k.risolvi_carta(chiave) == id_, (id_, chiave)
    for id_ in k.stese:
        for chiave in (id_, k.slug_stesa(id_, "it"), k.slug_stesa(id_, "en")):
            assert k.risolvi_stesa(chiave) == id_, (id_, chiave)


def test_gli_slug_inglesi_sono_quelli_che_si_cercano(k):
    assert k.slug_carta("maj-17", "en") == "the-star"
    assert k.slug_carta("bastoni-02", "en") == "two-of-wands"        # il titolo («Dominion») non entra nell'indirizzo
    assert k.slug_carta("maj-17", "it") == "la-stella"
    assert k.slug_stesa("croce-celtica", "en") == "celtic-cross"
    assert k.slug_stesa("croce-celtica", "it") == "croce-celtica"
    assert k.risolvi_carta("The-Star ") == "maj-17" and k.risolvi_carta("non-esiste") is None


def test_la_carta_in_inglese_e_completa(k):
    c = k.carta_pubblica("maj-17", completa=True, lang="en")
    assert c["lang"] == "en" and c["nome"] == "The Star" and c["slug"] == "the-star"
    assert c["slugs"] == {"it": "la-stella", "en": "the-star"}
    assert c["astrologia"] == "Aquarius" and c["elemento"] == "aria" and c["elemento_label"] == "Air"
    assert set(c["significati"]) == {"essoterico", "psicologico", "iniziatico", "ombra"}
    assert set(c["ambiti"]) == {"amore", "lavoro", "spirito"}
    assert c["dritto"].startswith("Well-founded hope") and c["parole_chiave"][0] == "hope"


def test_una_carta_minore_porta_il_titolo_di_thoth_nel_nome_e_non_nello_slug(k):
    c = k.carta_pubblica("bastoni-02", lang="en")
    assert c["nome"] == "Two of Wands — Dominion" and c["slug"] == "two-of-wands"
    assert (c["seme_label"], c["rango_label"], c["arcano_label"]) == ("Wands", "Two", "Minor Arcana")


def test_senza_lingua_resta_tutto_italiano(k):
    c = k.carta_pubblica("maj-17", completa=True)
    assert c["lang"] == "it" and c["nome"] == "La Stella" and c["slug"] == "la-stella"
    assert c["dritto"].startswith("Speranza fondata") and "elemento_label" not in c
    s = k.stesa_pubblica(k.stesa("croce-celtica"))
    assert s["lang"] == "it" and s["nome"] == "Croce Celtica" and "categoria_label" not in s


def test_ogni_altra_lingua_ricade_sull_inglese(k):
    assert k.lingua_contenuto("hu") == "en" and k.lingua_contenuto("de-DE") == "en"
    assert k.lingua_contenuto("it-IT") == "it" and k.lingua_contenuto(None) == "it" and k.lingua_contenuto("") == "it"


def test_la_stesa_in_inglese(k):
    s = k.stesa_pubblica(k.stesa("croce-celtica"), "en")
    assert s["lang"] == "en" and s["nome"] == "Celtic Cross" and s["slug"] == "celtic-cross"
    assert s["categoria_label"] == "Classic spread" and s["mazzo_label"] == "The full 78-card deck"
    assert [p["nome"] for p in s["posizioni"]][:3] == ["The present", "The challenge", "Recent past"]
    assert len(s["regole"]) == len(k.stesa("croce-celtica")["regole"]) == 4
    # Le coordinate e le linee non si toccano: il tavolo è lo stesso in ogni lingua.
    assert [(p["x"], p["y"]) for p in s["posizioni"]] == [(p["x"], p["y"]) for p in k.stesa("croce-celtica")["posizioni"]]


def test_le_stese_speciali_in_inglese_tengono_il_soggetto(k):
    s = k.stesa_pubblica(k.stesa("coppia-bivio"), "en")
    assert s["categoria_label"] == "Relationship spread" and s["stile_label"] == "Trending"
    assert {p["soggetto"] for p in s["posizioni"]} == {"coppia", "strada-a", "strada-b"}


def test_una_traduzione_mancante_ferma_l_avvio(k):
    import copy
    from dataclasses import replace

    testi = copy.deepcopy(k.testi)
    del testi["en"]["carte"]["maj-17"]
    with pytest.raises(ConoscenzaNonValida, match="mancano le carte"):
        replace(k, testi=testi).valida()
    testi = copy.deepcopy(k.testi)
    testi["en"]["stese"]["croce-celtica"]["slug"] = testi["en"]["stese"]["tre-carte"]["slug"]
    with pytest.raises(ConoscenzaNonValida, match="slug duplicati"):
        replace(k, testi=testi).valida()
    testi = copy.deepcopy(k.testi)
    testi["en"]["carte"]["maj-00"]["kw"] = testi["en"]["carte"]["maj-00"]["kw"][:-1]
    with pytest.raises(ConoscenzaNonValida, match="parole chiave"):
        replace(k, testi=testi).valida()
