"""Il segno solare, l'aspetto fra i segni e la carta della coppia."""
from __future__ import annotations

from datetime import date

import pytest

from tarot_core.tarot.numerologia import carta_dell_anima, carta_della_coppia
from tarot_core.tarot.zodiaco import SEGNI, compatibilita, segno_solare


@pytest.mark.parametrize("nascita, atteso", [
    (date(1990, 3, 14), "pesci"),
    (date(2000, 1, 1), "capricorno"),
    (date(2000, 12, 31), "capricorno"),
    (date(2001, 1, 20), "acquario"),
    (date(2001, 2, 19), "pesci"),
    (date(2001, 4, 25), "toro"),
    (date(2001, 7, 22), "cancro"),
    (date(2001, 7, 23), "leone"),
    (date(1988, 8, 7), "leone"),
    (date(2001, 9, 30), "bilancia"),
    (date(2001, 11, 21), "scorpione"),
    (date(2001, 11, 22), "sagittario"),
])
def test_segno_solare_per_data(nascita, atteso):
    assert segno_solare(nascita).codice == atteso


def test_il_29_febbraio_e_dei_pesci():
    assert segno_solare(date(2000, 2, 29)).codice == "pesci"


@pytest.mark.parametrize("nascita, segno, vicino", [
    (date(2001, 3, 20), "pesci", "ariete"),       # ultimo giorno dei Pesci
    (date(2001, 3, 21), "ariete", "pesci"),       # primo giorno dell'Ariete
    (date(2001, 12, 21), "sagittario", "capricorno"),
    (date(2001, 12, 22), "capricorno", "sagittario"),
    (date(2001, 1, 19), "capricorno", "acquario"),
    (date(2001, 1, 20), "acquario", "capricorno"),
])
def test_la_cuspide_e_segnalata_e_indica_il_segno_vicino(nascita, segno, vicino):
    s = segno_solare(nascita)
    assert s.codice == segno and s.cuspide is True and s.vicino == vicino


def test_a_meta_segno_non_c_e_cuspide():
    for nascita in (date(1990, 3, 14), date(2001, 7, 10), date(2001, 10, 5)):
        s = segno_solare(nascita)
        assert not s.cuspide and s.vicino is None


def test_ogni_giorno_dell_anno_ha_un_segno_e_ogni_segno_compare():
    visti = set()
    for mese, giorni in ((1, 31), (2, 29), (3, 31), (4, 30), (5, 31), (6, 30), (7, 31), (8, 31), (9, 30),
                         (10, 31), (11, 30), (12, 31)):
        for giorno in range(1, giorni + 1):
            visti.add(segno_solare(date(2000, mese, giorno)).codice)
    assert visti == {s[0] for s in SEGNI}


def test_elemento_e_modalita_dei_dodici_segni():
    elementi = {s[0]: s[2] for s in SEGNI}
    assert [elementi[c] for c in ("ariete", "leone", "sagittario")] == ["fuoco"] * 3
    assert [elementi[c] for c in ("toro", "vergine", "capricorno")] == ["terra"] * 3
    assert [elementi[c] for c in ("gemelli", "bilancia", "acquario")] == ["aria"] * 3
    assert [elementi[c] for c in ("cancro", "scorpione", "pesci")] == ["acqua"] * 3
    modalita = [s[3] for s in SEGNI]
    assert modalita.count("cardinale") == modalita.count("fisso") == modalita.count("mutevole") == 4


# Base: Ariete (21 marzo). Ogni segno a una data distanza dallo zodiaco.
_ARIETE = date(2001, 4, 1)


@pytest.mark.parametrize("altra, distanza, aspetto, armonia", [
    (date(2001, 4, 10), 0, "congiunzione", "alta"),        # Ariete
    (date(2001, 5, 10), 1, "semisestile", "mista"),        # Toro
    (date(2001, 6, 10), 2, "sestile", "buona"),            # Gemelli
    (date(2001, 7, 10), 3, "quadrato", "impegnativa"),     # Cancro
    (date(2001, 8, 10), 4, "trigono", "alta"),             # Leone
    (date(2001, 9, 10), 5, "quinconce", "impegnativa"),    # Vergine
    (date(2001, 10, 10), 6, "opposizione", "mista"),       # Bilancia
    (date(2001, 11, 10), 5, "quinconce", "impegnativa"),   # Scorpione (dall'altra parte)
    (date(2001, 12, 10), 4, "trigono", "alta"),            # Sagittario
    (date(2001, 1, 25), 2, "sestile", "buona"),            # Acquario
    (date(2001, 3, 1), 1, "semisestile", "mista"),         # Pesci
])
def test_aspetto_e_armonia_dalla_distanza_fra_i_segni(altra, distanza, aspetto, armonia):
    c = compatibilita(_ARIETE, altra)
    assert (c.distanza, c.aspetto, c.armonia) == (distanza, aspetto, armonia)


def test_la_compatibilita_e_simmetrica():
    a, b = date(1990, 3, 14), date(1988, 8, 7)
    ab, ba = compatibilita(a, b), compatibilita(b, a)
    assert (ab.aspetto, ab.armonia, ab.distanza) == (ba.aspetto, ba.armonia, ba.distanza)
    assert ab.relazione_elementi == ba.relazione_elementi


def test_il_trigono_e_sempre_fra_lo_stesso_elemento():
    fuoco = compatibilita(date(2001, 4, 1), date(2001, 8, 10))     # Ariete-Leone
    assert fuoco.aspetto == "trigono" and fuoco.relazione_elementi == "rafforzata"
    acqua_terra = compatibilita(date(2001, 7, 10), date(2001, 4, 25))  # Cancro-Toro (sestile)
    assert acqua_terra.aspetto == "sestile" and acqua_terra.relazione_elementi == "amica"


def test_l_opposizione_ha_la_stessa_modalita_e_le_note_non_danno_verdetti():
    c = compatibilita(_ARIETE, date(2001, 10, 10))
    assert c.stessa_modalita is True and c.segno_a.modalita == "cardinale"
    for aspetto in ("congiunzione", "semisestile", "sestile", "quadrato", "trigono", "quinconce", "opposizione"):
        from tarot_core.tarot.zodiaco import NOTE_ASPETTO
        nota = NOTE_ASPETTO[aspetto].lower()
        assert "incompatibil" not in nota and "destino" not in nota and "%" not in nota


def test_nessun_punteggio_numerico():
    c = compatibilita(date(1990, 3, 14), date(1988, 8, 7))
    assert isinstance(c.armonia, str) and c.armonia in ("alta", "buona", "mista", "impegnativa")
    assert not any(isinstance(v, float) for v in vars(c).values())


def test_la_carta_della_coppia_e_la_somma_teosofica_delle_due_anime():
    # 14/03/1990 → 27 → 9 ; 07/08/1988 → 41 → 5 ; 9 + 5 = 14
    assert carta_dell_anima(date(1990, 3, 14)) == 9
    assert carta_dell_anima(date(1988, 8, 7)) == 5
    assert carta_della_coppia(date(1990, 3, 14), date(1988, 8, 7)) == 14


def test_la_carta_della_coppia_si_riduce_oltre_22():
    # Due anime da 12 danno 24: si sommano le cifre, 2 + 4 = 6.
    a = date(1973, 9, 19)
    assert carta_dell_anima(a) == 12
    assert carta_della_coppia(a, a) == 6


def test_due_anime_che_sommano_22_sono_il_matto():
    # Due anime da 11 danno 22, cioè il Matto (0).
    a = next(
        date(anno, mese, giorno)
        for anno in range(1970, 2000) for mese in range(1, 13) for giorno in range(1, 29)
        if carta_dell_anima(date(anno, mese, giorno)) == 11
    )
    assert carta_dell_anima(a) == 11
    assert carta_della_coppia(a, a) == 0


def test_la_carta_della_coppia_e_simmetrica():
    a, b = date(1975, 6, 30), date(1982, 11, 2)
    assert carta_della_coppia(a, b) == carta_della_coppia(b, a)
