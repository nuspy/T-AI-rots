"""Le nove stese speciali: struttura, nomi, categorie e geometria del tavolo."""
from __future__ import annotations

import copy
import re
from dataclasses import replace
from itertools import combinations

import pytest

from tarot_core.tarot.conoscenza import Conoscenza, ConoscenzaNonValida

ATTESE = {
    # id: (categoria, stile, carte, mazzo)
    "compat-tre": ("compatibilita", "tradizionale", 3, "maggiori"),
    "compat-sette": ("compatibilita", "tradizionale", 7, "completo"),
    "compat-nove": ("compatibilita", "moderna", 9, "completo"),
    "compat-anime": ("compatibilita", "tendenza", 7, "maggiori"),
    "coppia-croce": ("coppia", "tradizionale", 5, "maggiori"),
    "coppia-stazione": ("coppia", "tradizionale", 7, "completo"),
    "coppia-sette": ("coppia", "moderna", 7, "completo"),
    "coppia-specchio": ("coppia", "moderna", 8, "completo"),
    "coppia-bivio": ("coppia", "tendenza", 8, "completo"),
}

STANDARD = ("tre-carte", "croce-semplice", "ferro-di-cavallo", "croce-celtica", "ruota-astrologica")


@pytest.fixture(scope="module")
def conoscenza() -> Conoscenza:
    return Conoscenza.carica()


def _speciali(conoscenza):
    return [conoscenza.stesa(i) for i in ATTESE]


# ---- il catalogo -------------------------------------------------------------


def test_le_nove_stese_ci_sono_con_categoria_stile_carte_e_mazzo(conoscenza):
    for id_, (categoria, stile, carte, mazzo) in ATTESE.items():
        stesa = conoscenza.stesa(id_)
        assert stesa is not None, id_
        assert conoscenza.categoria_di(stesa) == categoria
        assert stesa["stile"] == stile
        assert stesa["carte_da_scegliere"] == carte == len(stesa["posizioni"])
        assert stesa["mazzo"] == mazzo
        assert len(conoscenza.mazzo_per(stesa)) >= carte


def test_le_categorie_raccolgono_le_stese_giuste(conoscenza):
    assert [s["id"] for s in conoscenza.stese_per("standard")] == list(STANDARD)
    assert [s["id"] for s in conoscenza.stese_per("compatibilita")] == [i for i in ATTESE if i.startswith("compat")]
    assert [s["id"] for s in conoscenza.stese_per("coppia")] == [i for i in ATTESE if i.startswith("coppia")]


def test_le_stese_standard_non_cambiano_e_non_hanno_stile(conoscenza):
    for id_ in STANDARD:
        stesa = conoscenza.stesa(id_)
        assert conoscenza.categoria_di(stesa) == "standard" and not stesa.get("stile")
        assert all("soggetto" not in p for p in stesa["posizioni"])


def test_ogni_lettura_speciale_offre_ogni_stile(conoscenza):
    for categoria in ("compatibilita", "coppia"):
        assert {s["stile"] for s in conoscenza.stese_per(categoria)} == {"tradizionale", "moderna", "tendenza"}


def test_ogni_stesa_speciale_ha_un_soggetto_valido_e_nessuna_carta_calcolata(conoscenza):
    for stesa in _speciali(conoscenza):
        assert not stesa.get("sintesi_wirth")
        for p in stesa["posizioni"]:
            assert p["soggetto"] in ("tu", "partner", "coppia", "strada-a", "strada-b"), (stesa["id"], p["n"])
            assert p["calcolata"] is False and p["rotazione"] == 0
            if p["soggetto"].startswith("strada-"):
                assert stesa["id"] == "coppia-bivio"


def test_il_racconto_tocca_ogni_posizione_e_le_linee_citano_posizioni_esistenti(conoscenza):
    for stesa in _speciali(conoscenza):
        numeri = [p["n"] for p in stesa["posizioni"]]
        assert sorted(stesa["racconto"]) == numeri
        for linea in stesa["linee"]:
            assert set(linea) <= set(numeri), stesa["id"]
        for a, b, testo in stesa["coppie"]:
            assert a in numeri and b in numeri and a != b and testo


def test_la_stazione_scopre_il_centro_per_ultimo(conoscenza):
    stesa = conoscenza.stesa("coppia-stazione")
    centro = next(p for p in stesa["posizioni"] if p["nome"] == "La situazione attuale")
    assert centro["n"] == max(p["n"] for p in stesa["posizioni"]) == stesa["racconto"][-1]
    assert (centro["x"], centro["y"]) == (0.5, 0.5)


def test_il_bivio_racconta_dal_passato_e_ha_le_due_strade_e_la_nota_per_l_intervista(conoscenza):
    stesa = conoscenza.stesa("coppia-bivio")
    assert stesa["racconto"][:2] == [2, 1] and stesa["nota_intervista"]
    soggetti = [p["soggetto"] for p in stesa["posizioni"]]
    assert soggetti.count("strada-a") == soggetti.count("strada-b") == 3


def test_il_triangolo_della_verita_e_dichiarato(conoscenza):
    stesa = conoscenza.stesa("compat-nove")
    assert any("triangolo della verità" in r for r in stesa["regole"])
    assert {1, 5, 7} <= {a for a, _, _ in stesa["coppie"]} | {b for _, b, _ in stesa["coppie"]}


def test_i_nomi_sono_neutri_e_la_regola_anti_stereotipo_c_e(conoscenza):
    vietate = re.compile(r"\b(lei|lui|egli|ella|il partner|la partner|fidanzat[oa]|marito|moglie|ragazz[oa])\b", re.IGNORECASE)
    for stesa in _speciali(conoscenza):
        testi = [stesa["nome"], stesa["descrizione"], stesa["origine"], *stesa["regole"], *(t for _, _, t in stesa["coppie"])]
        for p in stesa["posizioni"]:
            testi += [p["nome"], p["nome_en"], p["significato"], p["domanda"]]
        for testo in testi:
            assert not vietate.search(testo), (stesa["id"], testo)
        assert any("non il genere delle persone" in r for r in stesa["regole"]), stesa["id"]
        assert any("non la lettura del suo pensiero" in r for r in stesa["regole"]), stesa["id"]


def test_i_nomi_ungheresi_delle_nove_stese_ci_sono_e_sono_diversi_dall_italiano(conoscenza):
    for id_ in ATTESE:
        stesa = conoscenza.stesa(id_)
        assert conoscenza.nome_stesa(stesa, "hu") != stesa["nome"]
        for p in stesa["posizioni"]:
            hu = conoscenza.nome_posizione(stesa, p["n"], "hu")
            assert hu and hu != p["nome"] and len(hu) <= 45, (id_, p["n"], hu)


def test_la_stesa_pubblica_espone_i_campi_nuovi_e_non_quelli_interni(conoscenza):
    pubblica = conoscenza.stesa_pubblica(conoscenza.stesa("coppia-bivio"))
    assert pubblica["categoria"] == "coppia" and pubblica["stile"] == "tendenza"
    assert pubblica["larghezza"] == 0.11 and pubblica["larghezza_stretto"] == 0.135 and pubblica["forma"] == "standard"
    assert all("soggetto" in p for p in pubblica["posizioni"])
    assert "nota_intervista" not in pubblica and "linee" not in pubblica and "racconto" not in pubblica
    standard = conoscenza.stesa_pubblica(conoscenza.stesa("tre-carte"))
    assert standard["categoria"] == "standard" and standard["larghezza"] == 0.16 and standard["stile"] is None
    ruota = conoscenza.stesa_pubblica(conoscenza.stesa("ruota-astrologica"))
    assert ruota["forma"] == "quadrata"


# ---- la validazione ---------------------------------------------------------------


def _con(conoscenza, modifica):
    stese = copy.deepcopy(conoscenza.stese)
    modifica(stese)
    return replace(conoscenza, stese=stese)


@pytest.mark.parametrize("modifica, frammento", [
    (lambda s: s["compat-tre"].update(categoria="amicizia"), "categoria sconosciuta"),
    (lambda s: s["compat-tre"].pop("stile"), "stile"),
    (lambda s: s["compat-tre"].update(stile="antica"), "stile"),
    (lambda s: s["tre-carte"].update(stile="moderna"), "standard non ha"),
    (lambda s: s["compat-tre"]["posizioni"][0].pop("soggetto"), "soggetto"),
    (lambda s: s["compat-tre"]["posizioni"][0].update(soggetto="lui"), "soggetto"),
    (lambda s: s["compat-tre"]["posizioni"][0].update(soggetto="strada-a"), "strade sono solo della coppia"),
    (lambda s: s["compat-tre"]["posizioni"][0].update(x=1.2), "fuori dal tavolo"),
    (lambda s: s["compat-tre"]["posizioni"][0].update(y=-0.1), "fuori dal tavolo"),
    (lambda s: s["compat-tre"].update(larghezza=0.5), "larghezza"),
    (lambda s: s["compat-tre"].update(larghezza_stretto=0.01), "larghezza_stretto"),
    (lambda s: s["compat-tre"].update(forma="ovale"), "forma"),
    (lambda s: s["compat-tre"].update(sintesi_wirth=True), "Wirth"),
    # La carta calcolata sballa prima il conto delle carte da scegliere: ferma l'avvio comunque.
    (lambda s: s["compat-tre"]["posizioni"][0].update(calcolata=True), "carte da scegliere incoerenti|calcolat"),
])
def test_la_validazione_respinge_le_stese_speciali_incoerenti(conoscenza, modifica, frammento):
    rotta = _con(conoscenza, modifica)
    with pytest.raises(ConoscenzaNonValida, match=frammento):
        rotta.valida()


def test_senza_uno_stile_la_categoria_non_e_coperta(conoscenza):
    def togli_le_tendenze(stese):
        for id_ in ("compat-anime",):
            del stese[id_]

    rotta = _con(conoscenza, togli_le_tendenze)
    with pytest.raises(ConoscenzaNonValida, match="nessuna stesa di stile"):
        rotta.valida()


# ---- la geometria del tavolo -------------------------------------------------------
#
# Riproduce le formule di `frontend/app/leggi/tavolo.tsx`: la larghezza di una carta
# è `w * larghezza * SCALA_CARTE` sul tavolo 16:12 (e `larghezza_stretto` sul tavolo
# 1:1 dei telefoni), l'altezza è larghezza × 16/9. Se cambia una formula là, va
# cambiata anche qui: il test esiste per accorgersi delle sovrapposizioni PRIMA di
# vedere il tavolo su un telefono.

SCALA_CARTE = 1.2
MOBILE_W = 328   # viewport 360 meno due gutter da 16 px
DESKTOP_W = (600, 800, 1000)


def _carte(stesa, w, h, larghezza):
    cw = w * larghezza * SCALA_CARTE
    ch = cw * 16 / 9
    return [(p["n"], p["x"] * w, p["y"] * h, cw, ch) for p in stesa["posizioni"]], cw, ch


def _spazio_minimo(carte, cw, ch):
    """La distanza minima, in pixel, fra i bordi di due carte (asse più libero)."""
    minimo = float("inf")
    for (_, x1, y1, *_), (_, x2, y2, *_) in combinations(carte, 2):
        minimo = min(minimo, max(abs(x1 - x2) - cw, abs(y1 - y2) - ch))
    return minimo


@pytest.mark.parametrize("id_", list(ATTESE))
def test_sul_telefono_le_carte_non_si_toccano_e_stanno_nel_tavolo(conoscenza, id_):
    stesa = conoscenza.stesa(id_)
    larghezza = stesa.get("larghezza_stretto") or stesa["larghezza"] * 1.15
    carte, cw, ch = _carte(stesa, MOBILE_W, MOBILE_W, larghezza)   # tavolo 1:1
    assert cw >= 48, f"carta di {cw:.0f} px: sotto il minimo di 48"
    for n, x, y, *_ in carte:
        assert cw / 2 <= x <= MOBILE_W - cw / 2 and ch / 2 <= y <= MOBILE_W - ch / 2, (id_, n)
    assert _spazio_minimo(carte, cw, ch) >= 10, id_


@pytest.mark.parametrize("w", DESKTOP_W)
@pytest.mark.parametrize("id_", list(ATTESE))
def test_sul_desktop_le_carte_non_si_toccano_e_stanno_nel_tavolo(conoscenza, id_, w):
    stesa = conoscenza.stesa(id_)
    h = w * 12 / 16                                             # tavolo 16:12
    carte, cw, ch = _carte(stesa, w, h, stesa["larghezza"])
    for n, x, y, *_ in carte:
        assert cw / 2 <= x <= w - cw / 2 and ch / 2 <= y <= h - ch / 2, (id_, n)
    # Fra righe di carte deve restare posto per l'etichetta della posizione (~17 px).
    assert _spazio_minimo(carte, cw, ch) >= 16, (id_, w)


def test_le_cinque_stese_standard_hanno_la_larghezza_di_prima(conoscenza):
    prima = {"tre-carte": 0.16, "croce-semplice": 0.098, "ferro-di-cavallo": 0.1,
             "croce-celtica": 0.074, "ruota-astrologica": 0.075}
    for id_, valore in prima.items():
        assert conoscenza.stesa(id_)["larghezza"] == valore
    assert conoscenza.stesa("ruota-astrologica")["forma"] == "quadrata"
    assert all("forma" not in conoscenza.stesa(i) for i in STANDARD if i != "ruota-astrologica")
