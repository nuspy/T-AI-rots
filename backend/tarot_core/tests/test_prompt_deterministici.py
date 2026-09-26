"""Ciò che si passa al modello: solo la carta e la posizione di quella posa.

Il codice sceglie i valori, il modello non li cerca: meno token, meno errori.
Qui si prova che nel messaggio entra ciò che serve e nient'altro, e che la
sintesi finale riceve le carte nell'ordine del racconto.
"""
from __future__ import annotations

import re

import pytest

from tarot_core.domain.models import Reading
from tarot_core.guards.lettura import segnale_di_crisi
from tarot_core.tarot import cag, interpretazione
from tarot_core.tarot.conoscenza import Conoscenza
from tarot_core.tarot.lettura import gia_rivelate, note_di_posizione, posa
from tarot_core.tarot.schede import scheda, valore_sintetico


@pytest.fixture(scope="module")
def conoscenza() -> Conoscenza:
    return Conoscenza.carica()


# ---- la scheda: solo l'orientamento estratto ---------------------------------


def test_la_scheda_di_una_carta_dritta_non_porta_il_rovescio(conoscenza):
    carta = conoscenza.carta("maj-07")
    testo = scheda(carta, rovescio=False)
    assert carta["dritto"] in testo
    assert carta["rovescio"] not in testo
    assert "Lato d'ombra" not in testo


def test_la_scheda_di_una_carta_rovesciata_non_porta_il_dritto(conoscenza):
    carta = conoscenza.carta("maj-07")
    testo = scheda(carta, rovescio=True)
    assert carta["rovescio"] in testo
    assert carta["dritto"] not in testo


def test_il_valore_sintetico_e_una_frase_breve_dell_orientamento(conoscenza):
    for carta in conoscenza.carte.values():
        for rovescio in (False, True):
            valore = valore_sintetico(carta, rovescio)
            assert 0 < len(valore) <= 150, (carta["id"], rovescio)
            origine = carta["rovescio"] if rovescio else carta["dritto"]
            assert valore.rstrip("…").strip()[:20] in origine


# ---- l'interpretazione di una carta: solo quella posizione --------------------


def _messaggio(conoscenza, stesa_id, n, card_id, rovescio, **extra):
    stesa = conoscenza.stesa(stesa_id)
    return interpretazione.messaggio(
        carta=conoscenza.carta(card_id), rovescio=rovescio, stesa=stesa,
        posizione=conoscenza.posizione(stesa, n), quesito="Come andrà il lavoro?",
        contesto="Cambio di lavoro in corso.", **extra,
    )


def test_il_messaggio_porta_il_significato_di_quella_sola_posizione(conoscenza):
    stesa = conoscenza.stesa("croce-celtica")
    testo = _messaggio(conoscenza, "croce-celtica", 5, "maj-07", True)
    assert stesa["posizioni"][4]["significato"] in testo
    for p in stesa["posizioni"]:
        if p["n"] != 5:
            assert p["significato"] not in testo, p["nome"]


def test_il_messaggio_porta_solo_l_orientamento_estratto(conoscenza):
    carta = conoscenza.carta("maj-07")
    dritta = _messaggio(conoscenza, "tre-carte", 2, "maj-07", False)
    rovesciata = _messaggio(conoscenza, "tre-carte", 2, "maj-07", True)
    assert "Orientamento: dritta" in dritta and carta["rovescio"] not in dritta
    assert "Orientamento: rovesciata" in rovesciata and carta["dritto"] not in rovesciata


def test_le_regole_di_coppia_entrano_solo_se_l_altra_carta_e_visibile(conoscenza):
    stesa = conoscenza.stesa("croce-celtica")
    a, b, testo = stesa["coppie"][0]
    assert not any(testo in nota for nota in note_di_posizione(stesa, a, []))
    assert any(testo in nota for nota in note_di_posizione(stesa, a, [b]))
    assert any(testo in nota for nota in note_di_posizione(stesa, b, [a]))
    # Una posizione fuori dalla coppia non le riceve.
    fuori = next(p["n"] for p in stesa["posizioni"] if p["n"] not in (a, b))
    assert not any(testo in nota for nota in note_di_posizione(stesa, fuori, [a, b]))


def test_la_carta_2_della_croce_celtica_porta_l_avvertenza(conoscenza):
    stesa = conoscenza.stesa("croce-celtica")
    assert any("traverso" in nota for nota in note_di_posizione(stesa, 2, []))
    assert not any("traverso" in nota for nota in note_di_posizione(stesa, 1, []))
    testo = _messaggio(
        conoscenza, "croce-celtica", 2, "maj-16", False, note=note_di_posizione(stesa, 2, [1]),
    )
    assert "Regola della stesa — Questa carta è posata di traverso" in testo


def test_in_un_altra_lingua_il_messaggio_porta_i_nomi_da_usare(conoscenza):
    stesa = conoscenza.stesa("tre-carte")
    nomi = (conoscenza.nome_carta("maj-07", "hu"), conoscenza.nome_posizione(stesa, 2, "hu"))
    testo = _messaggio(conoscenza, "tre-carte", 2, "maj-07", False, nomi=nomi, lang="hu")
    assert f"carta «{nomi[0]}», posizione «{nomi[1]}»" in testo
    assert "ungherese" in testo and "Scrivi in italiano" not in testo
    # In italiano i nomi sono già quelli del prompt: non si ripetono.
    assert "Nomi da usare" not in _messaggio(conoscenza, "tre-carte", 2, "maj-07", False, nomi=nomi, lang="it")


# ---- la carta 2 della croce celtica non si legge rovesciata ---------------------


def _lettura(conoscenza, stesa, rovesci):
    """Una lettura in scelta, con gli slot già fissati (carta, orientamento)."""
    ids = conoscenza.mazzo_per(stesa)
    return Reading(
        spread_id=stesa["id"], question="?", status="scelta",
        deck_state=[{"card": ids[i], "rovescio": r} for i, r in enumerate(rovesci)],
    )


def test_la_carta_2_della_croce_celtica_e_sempre_dritta(conoscenza):
    stesa = conoscenza.stesa("croce-celtica")
    lettura = _lettura(conoscenza, stesa, [True] * 78)
    prima = posa(lettura, stesa, 0, conoscenza)
    seconda = posa(lettura, stesa, 1, conoscenza)
    terza = posa(lettura, stesa, 2, conoscenza)
    assert (prima.posizione, seconda.posizione, terza.posizione) == (1, 2, 3)
    assert prima.rovescio is True
    assert seconda.rovescio is False  # di traverso: mai rovesciata
    assert terza.rovescio is True
    # Il mazzo impegnato non cambia: la regola sta nel codice, non nello slot.
    assert lettura.deck_state[1]["rovescio"] is True


def test_nelle_altre_stese_l_orientamento_resta_quello_fissato(conoscenza):
    stesa = conoscenza.stesa("tre-carte")
    lettura = _lettura(conoscenza, stesa, [True] * 22)
    assert [posa(lettura, stesa, i, conoscenza).rovescio for i in range(3)] == [True, True, True]


# ---- la sintesi: prefisso stabile e parte variabile mirata ------------------------


def _carte(conoscenza, stesa, scelte):
    """`scelte`: [(card_id, rovescio)] nell'ordine delle posizioni."""
    return [
        {
            "card_id": cid, "rovescio": rov, "posizione": i, "calcolata": False,
            "interpretazione": f"Lettura immediata {i}.",
        }
        for i, (cid, rov) in enumerate(scelte, start=1)
    ]


def test_il_prefisso_non_porta_ne_le_stese_ne_il_mazzo(conoscenza):
    prefisso = cag.prefisso(conoscenza, ["Regola di sicurezza di prova."])
    assert "Regola di sicurezza di prova." in prefisso
    for stesa in conoscenza.stese.values():
        assert stesa["descrizione"] not in prefisso
    for carta in conoscenza.carte.values():
        assert carta["dritto"] not in prefisso and carta["rovescio"] not in prefisso
    # Byte-identico fra letture: è ciò che lo rende riusabile dalla cache.
    assert prefisso == cag.prefisso(conoscenza, ["Regola di sicurezza di prova."])


def _variabile(conoscenza, stesa_id, scelte, lang="it"):
    stesa = conoscenza.stesa(stesa_id)
    return cag.parte_variabile(
        conoscenza=conoscenza, stesa=stesa, quesito="Come andrà?", contesto="Quadro.",
        carte=_carte(conoscenza, stesa, scelte), dignita={}, prevalenze={"maggiori": 3},
        colloquio="Oracolo: Da quanto?\nChi consulta: Da un mese.", lang=lang,
    )


def test_la_parte_variabile_porta_la_sola_stesa_scelta_e_le_sole_carte_estratte(conoscenza):
    scelte = [("maj-07", True), ("maj-16", False), ("maj-13", False)]
    testo = _variabile(conoscenza, "tre-carte", scelte)
    assert conoscenza.stesa("tre-carte")["descrizione"] in testo
    for altra in ("croce-semplice", "croce-celtica", "ferro-di-cavallo", "ruota-astrologica"):
        assert conoscenza.stesa(altra)["descrizione"] not in testo
    estratte = {cid for cid, _ in scelte}
    for cid, carta in conoscenza.carte.items():
        if cid not in estratte:
            assert carta["dritto"] not in testo and carta["rovescio"] not in testo, cid
    # Le estratte, solo nell'orientamento uscito.
    assert conoscenza.carta("maj-07")["rovescio"] in testo
    assert conoscenza.carta("maj-07")["dritto"] not in testo
    assert conoscenza.carta("maj-16")["dritto"] in testo
    assert conoscenza.carta("maj-16")["rovescio"] not in testo


def _posizioni_del_racconto(testo):
    sezione = testo.split("## Ordine del racconto", 1)[1].split("\n## ", 1)[0]
    return [int(n) for n in re.findall(r"\(posizione (\d+)\)", sezione)]


@pytest.mark.parametrize("stesa_id", ["tre-carte", "croce-semplice", "ferro-di-cavallo", "croce-celtica"])
def test_la_catena_segue_l_ordine_del_racconto_della_stesa(conoscenza, stesa_id):
    stesa = conoscenza.stesa(stesa_id)
    ids = [c for c in conoscenza.mazzo_per(stesa)][: len(stesa["posizioni"])]
    testo = _variabile(conoscenza, stesa_id, [(cid, i % 2 == 0) for i, cid in enumerate(ids)])
    assert _posizioni_del_racconto(testo) == stesa["racconto"]


def test_ogni_tappa_porta_la_carta_l_orientamento_e_il_suo_valore(conoscenza):
    """Il caso della richiesta: presente, ostacolo, futuro prossimo, futuro lontano."""
    stesa = conoscenza.stesa("croce-semplice")
    scelte = [("maj-07", True), ("maj-16", False), ("maj-13", False), ("maj-19", False)]
    testo = cag.catena(conoscenza, stesa, _carte(conoscenza, stesa, scelte), "it")
    righe = [r for r in testo.splitlines() if re.match(r"\d+\. ", r)]
    assert len(righe) == 4
    for riga in righe:
        n = int(re.search(r"\(posizione (\d+)\)", riga).group(1))
        cid, rovescio = scelte[n - 1]
        carta = conoscenza.carta(cid)
        assert conoscenza.nome_carta(cid, "it") in riga
        assert ("rovesciata" if rovescio else "dritta") in riga
        assert valore_sintetico(carta, rovescio) in riga


def test_la_catena_tace_le_posizioni_senza_carta(conoscenza):
    """Nella croce semplice la sintesi (posizione 5) c'è solo a carte scelte."""
    stesa = conoscenza.stesa("croce-semplice")
    scelte = [("maj-07", False), ("maj-16", False), ("maj-13", False), ("maj-19", False)]
    testo = cag.catena(conoscenza, stesa, _carte(conoscenza, stesa, scelte), "it")
    assert sorted(_posizioni_del_racconto(testo)) == [1, 2, 3, 4]


def test_in_ungherese_la_sintesi_porta_i_nomi_tradotti_e_la_lingua(conoscenza):
    scelte = [("maj-07", False), ("maj-16", True), ("maj-13", False)]
    testo = _variabile(conoscenza, "tre-carte", scelte, lang="hu")
    assert conoscenza.nome_carta("maj-07", "hu") in testo
    assert conoscenza.nome_posizione(conoscenza.stesa("tre-carte"), 1, "hu") in testo
    assert "ungherese" in testo and "Scrivi in italiano" not in testo


def test_le_gia_rivelate_usano_i_nomi_della_lingua(conoscenza):
    stesa = conoscenza.stesa("tre-carte")
    lettura = _lettura(conoscenza, stesa, [False] * 22)
    prima = posa(lettura, stesa, 0, conoscenza)
    prima.rivelata = True
    testo = gia_rivelate(lettura, stesa, conoscenza, 2, "hu")
    assert conoscenza.nome_carta(prima.card_id, "hu") in testo
    assert conoscenza.nome_posizione(stesa, 1, "hu") in testo


# ---- i nomi nelle lingue ------------------------------------------------------------


def test_i_nomi_ungheresi_coprono_carte_stese_e_posizioni(conoscenza):
    assert "hu" in conoscenza.nomi
    for cid, carta in conoscenza.carte.items():
        assert conoscenza.nome_carta(cid, "hu")
    for stesa in conoscenza.stese.values():
        assert conoscenza.nome_stesa(stesa, "hu")
        for p in stesa["posizioni"]:
            assert conoscenza.nome_posizione(stesa, p["n"], "hu")


def test_le_lingue_senza_nomi_ricadono_sull_inglese(conoscenza):
    stesa = conoscenza.stesa("tre-carte")
    for codice in ("de", "ru", "zh", "ar"):
        assert conoscenza.nome_carta("maj-07", codice) == conoscenza.nome_carta("maj-07", "en")
        assert conoscenza.nome_posizione(stesa, 1, codice) == conoscenza.nome_posizione(stesa, 1, "en")
    assert conoscenza.nome_carta("maj-07", "it") == conoscenza.carta("maj-07")["nome_it"]


def test_il_racconto_di_ogni_stesa_tocca_ogni_posizione_una_volta(conoscenza):
    for stesa in conoscenza.stese.values():
        assert sorted(stesa["racconto"]) == [p["n"] for p in stesa["posizioni"]]


# ---- il segnale di crisi, in ogni lingua ------------------------------------------------


@pytest.mark.parametrize("frase", [
    "Voglio farla finita",
    "I want to end my life",
    "Meg akarok halni",
    "Ich will mich umbringen",
    "J'ai envie de mourir",
    "Quiero morir",
    "Quero morrer",
    "Vreau să mor",
    "Chcę umrzeć",
    "Хочу умереть",
    "Хочу померти",
    "我想死",
    "मैं आत्महत्या करना चाहता हूँ",
    "자살하고 싶어요",
    "أريد أن أموت",
])
def test_la_crisi_si_riconosce_in_ogni_lingua(frase):
    assert segnale_di_crisi(frase)


@pytest.mark.parametrize("frase", [
    "Devo accettare la nuova offerta di lavoro?",
    "Should I take the new job offer?",
    "El kell fogadnom az új állásajánlatot?",
    "我应该接受新的工作吗？",
    "Стоит ли мне принять предложение?",
])
def test_una_domanda_normale_non_e_una_crisi(frase):
    assert not segnale_di_crisi(frase)
