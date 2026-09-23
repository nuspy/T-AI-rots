"""Il dominio esoterico, senza database: mazzo, stese, numeri, dignità, mazzo fissato."""
from __future__ import annotations

from datetime import date

import pytest

from tarot_core.tarot.conoscenza import Conoscenza
from tarot_core.tarot.dignita import relazione, valuta, vicini
from tarot_core.tarot.numerologia import (
    arcano_da_numero, carta_dell_anima, riduci, sintesi_wirth,
)
from tarot_core.tarot.shuffle import impegno, mescola, verifica


@pytest.fixture(scope="module")
def conoscenza() -> Conoscenza:
    return Conoscenza.carica()


def test_il_mazzo_ha_78_carte_con_le_attribuzioni_thoth(conoscenza):
    assert len(conoscenza.carte) == 78
    maggiori = [c for c in conoscenza.carte.values() if c["arcano"] == "maggiore"]
    assert len(maggiori) == 22
    corti = [c for c in conoscenza.carte.values() if c.get("corte")]
    assert len(corti) == 16
    # I nomi propri del Thoth, non quelli del Rider-Waite.
    assert conoscenza.maggiore(8)["nome_thoth"] == "Adjustment"
    assert conoscenza.maggiore(11)["nome_thoth"] == "Lust"
    assert conoscenza.maggiore(14)["nome_thoth"] == "Art"
    assert conoscenza.maggiore(20)["nome_thoth"] == "The Aeon"
    # «Tzaddi non è la Stella»: l'Imperatore prende Tzaddi, la Stella He.
    assert conoscenza.maggiore(4)["lettera_ebraica"]["nome"] == "Tzaddi"
    assert conoscenza.maggiore(17)["lettera_ebraica"]["nome"] == "He"


def test_le_cinque_stese(conoscenza):
    attese = {
        "tre-carte": (3, "maggiori"),
        "croce-semplice": (5, "maggiori"),
        "ferro-di-cavallo": (7, "completo"),
        "croce-celtica": (10, "completo"),
        "ruota-astrologica": (13, "completo"),
    }
    for sid, (n, mazzo) in attese.items():
        stesa = conoscenza.stesa(sid)
        assert len(stesa["posizioni"]) == n
        assert stesa["mazzo"] == mazzo
        assert len(conoscenza.mazzo_per(stesa)) == (22 if mazzo == "maggiori" else 78)
    assert conoscenza.stesa("croce-semplice")["carte_da_scegliere"] == 4


@pytest.mark.parametrize("numeri, atteso", [
    ([1, 2, 3, 4], 10),          # 10: Fortuna
    ([21, 20, 19, 18], 15),      # 78 → 7 + 8 = 15: il Diavolo
    ([0, 0, 0, 0], 0),           # tutti Matti: il Matto
    ([5, 6, 5, 6], 0),           # 22 è il Matto
])
def test_sintesi_di_wirth(numeri, atteso):
    assert sintesi_wirth(numeri) == atteso


def test_riduzione_teosofica():
    assert riduci(78) == 15
    assert riduci(22) == 22
    assert riduci(99) == 18
    assert arcano_da_numero(22) == 0


def test_carta_dell_anima():
    # 14/03/1990: 1+4+3+1+9+9+0 = 27 → 9, l'Eremita.
    assert carta_dell_anima(date(1990, 3, 14)) == 9


def test_dignita_elementali():
    assert relazione("fuoco", "aria") == 1
    assert relazione("fuoco", "acqua") == -1
    assert relazione("aria", "terra") == -1
    assert relazione("acqua", "acqua") == 2
    assert relazione("spirito", "acqua") == 0
    # Fuoco fra due Acque: mal dignificato.
    esito = valuta({1: "acqua", 2: "fuoco", 3: "acqua"}, [[1, 2, 3]])
    assert esito[2]["giudizio"] == "mal dignificata"
    # Fuoco fra Aria e Fuoco: ben dignificato, anzi rafforzato.
    esito = valuta({1: "aria", 2: "fuoco", 3: "fuoco"}, [[1, 2, 3]])
    assert esito[2]["punteggio"] == 3


def test_vicini_su_un_anello():
    adiacenza = vicini([[1, 2, 3, 4, 1]])
    assert adiacenza[1] == {2, 4}


def test_il_mazzo_e_fissato_e_verificabile(conoscenza):
    carte = conoscenza.mazzo_per(conoscenza.stesa("croce-celtica"))
    fissato = mescola(carte)
    assert sorted(s["card"] for s in fissato.slot) == sorted(carte)
    assert verifica(fissato.slot, fissato.sale, fissato.commitment)
    # Scambiare due carte dopo il commitment si vede.
    alterato = list(fissato.slot)
    alterato[0], alterato[1] = alterato[1], alterato[0]
    assert impegno(alterato, fissato.sale) != fissato.commitment


def test_i_mescolamenti_differiscono(conoscenza):
    carte = conoscenza.mazzo_per(conoscenza.stesa("tre-carte"))
    assert mescola(carte).slot != mescola(carte).slot
