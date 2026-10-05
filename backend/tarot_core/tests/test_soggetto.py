"""Il soggetto di un articolo ricavato da titolo e parola chiave (v9.4, `tarot/soggetto.py`): senza database."""
from __future__ import annotations

import json

import pytest

from tarot_core.paths import KNOWLEDGE_DIR
from tarot_core.tarot import soggetto


@pytest.mark.parametrize("titolo, atteso", [
    # le carte, con i nomi di Thoth, Rider-Waite e italiani
    ("Wheel of Fortune Tarot Meaning", ("carta", "maj-10")),
    ("Fortune in the Thoth Tarot", ("carta", "maj-10")),
    ("Ace of Cups: Love, Feeling and New Beginnings", ("carta", "coppe-01")),
    ("3 of Swords and heartbreak", ("carta", "spade-03")),
    ("Page of Wands", ("carta", "bastoni-principessa")),
    ("Princess of Disks", ("carta", "dischi-principessa")),
    ("King of Swords tarot meaning", ("carta", "spade-cavaliere")),
    ("Prince of Cups", ("carta", "coppe-principe")),
    ("Asso di Coppe: significato", ("carta", "coppe-01")),
    ("The Tower", ("carta", "maj-16")),
    ("Moon tarot card meaning", ("carta", "maj-18")),
    ("Death card: endings", ("carta", "maj-13")),
    ("The Hierophant and tradition", ("carta", "maj-05")),
    ("Justice or Adjustment? A tarot question", ("carta", "maj-08")),
    # le stese
    ("How to Read the Celtic Cross", ("stesa", "croce-celtica")),
    ("Croce celtica: guida", ("stesa", "croce-celtica")),
    ("Three card spread for love", ("stesa", "tre-carte")),
    ("Horseshoe tarot spread", ("stesa", "ferro-di-cavallo")),
    # nessuno: i nomi comuni senza tarocchi vicino, le frasi che non sono carte, le stese che non abbiamo
    ("Full Moon Tarot Spread for Release", None),
    ("New Moon intentions", None),
    ("Sun sign tarot", None),
    ("Star sign compatibility", None),
    ("The art of tarot journaling", None),
    ("Tarot fortune telling for beginners", None),
    ("Tarot Meditation for Libra Season Balance", None),
    ("Three Cards Every Beginner Should Know", None),
    ("A mirror for the soul", None),
])
def test_il_soggetto_dal_titolo(titolo, atteso):
    assert soggetto.calcola(titolo) == atteso


def test_prima_il_titolo_poi_la_parola_chiave_e_vince_il_nome_che_viene_prima():
    assert soggetto.calcola("A practical guide", "wheel of fortune tarot") == ("carta", "maj-10")
    assert soggetto.calcola("The Hermit", "celtic cross") == ("carta", "maj-09")
    assert soggetto.calcola("Celtic Cross and the Hierophant") == ("stesa", "croce-celtica")
    assert soggetto.calcola(None, None) is None and soggetto.calcola("", "  ") is None


def test_un_soggetto_indicato_a_mano_si_porta_agli_id_canonici():
    assert soggetto.normalizza("card", "fortune") == ("carta", "maj-10")
    assert soggetto.normalizza("carta", "la-stella") == ("carta", "maj-17")
    assert soggetto.normalizza("spread", "celtic-cross") == ("stesa", "croce-celtica")
    assert soggetto.normalizza(None, "maj-10") is None
    with pytest.raises(soggetto.SoggettoNonValido):
        soggetto.normalizza("carta", "maj-99")
    with pytest.raises(soggetto.SoggettoNonValido):
        soggetto.normalizza("mazzo", "thoth")


def test_ogni_nome_porta_a_una_carta_del_mazzo():
    """Il catalogo copiato dalla skill delle immagini è portato agli id di deck.json: nessun id inventato."""
    mazzo = {c["id"]: c for c in json.loads((KNOWLEDGE_DIR / "deck.json").read_text(encoding="utf-8"))}
    assert set(soggetto.ARCANI_MAGGIORI) == {i for i, c in mazzo.items() if c["arcano"] == "maggiore"}
    for carta, nomi in soggetto.ARCANI_MAGGIORI.items():
        thoth = soggetto.piano(mazzo[carta]["nome_thoth"]).removeprefix("the ")
        assert thoth in nomi, (carta, thoth)
    for rango in soggetto.RANGHI_MINORI:
        for seme in soggetto.SEMI_MINORI:
            assert soggetto.id_carta_minore(rango, seme) in mazzo


def test_il_json_del_soggetto_ha_nome_e_slug_nella_lingua():
    assert soggetto.soggetto_json("carta", "maj-17", "it") == {"tipo": "carta", "ref": "maj-17", "nome": "La Stella", "slug": "la-stella"}
    assert soggetto.soggetto_json("stesa", "croce-celtica", "en")["slug"] == "celtic-cross"
    assert soggetto.soggetto_json(None, None) is None


def test_le_stese_hanno_la_tradizione_in_ogni_lingua():
    from tarot_core.tarot.conoscenza import condivisa

    conoscenza = condivisa()
    for s in conoscenza.stese.values():
        pubblica = conoscenza.stesa_pubblica(s, "en")
        assert pubblica["tradizione"] and set(pubblica["tradizioni"]) == {"it", "en", "hu", "ru", "uk", "es"}
    assert conoscenza.stesa_pubblica(conoscenza.stesa("croce-celtica"), "en")["tradizione"] == "Celtic tradition"
    assert conoscenza.stesa_pubblica(conoscenza.stesa("croce-celtica"))["tradizione"] == "tradizione celtica"
