"""Le difese di `llm/json_mode.py` per i modelli che ragionano: budget adattivo,
estrazione tollerante, e il filtro del ragionamento scritto dentro `content`."""
from __future__ import annotations

from tarot_core.llm.json_mode import (
    BUDGET_RAGIONAMENTO, MARGINE_RISPOSTA_DOPO_RAGIONAMENTO,
    FiltroPensieroInline, pavimento_ragionamento,
)


def test_pavimento_segue_il_reasoning_budget_del_fornitore():
    """Bug reale: un fornitore con reasoning_budget=16384 nei suoi parametri, ma un
    max_tokens tagliato a 6144 (il vecchio pavimento fisso), garantiva il troncamento
    a meta' pensiero. Il pavimento deve seguire il numero che il fornitore stesso
    dichiara di lasciare pensare al modello."""
    assert pavimento_ragionamento({"reasoning_budget": 16384}) == 16384 + MARGINE_RISPOSTA_DOPO_RAGIONAMENTO


def test_pavimento_ricade_sul_predefinito_senza_reasoning_budget_dichiarato():
    assert pavimento_ragionamento({}) == BUDGET_RAGIONAMENTO
    assert pavimento_ragionamento({"top_p": 0.95}) == BUDGET_RAGIONAMENTO


def test_pavimento_ignora_un_reasoning_budget_non_numerico_o_non_positivo():
    assert pavimento_ragionamento({"reasoning_budget": "alto"}) == BUDGET_RAGIONAMENTO
    assert pavimento_ragionamento({"reasoning_budget": 0}) == BUDGET_RAGIONAMENTO
    assert pavimento_ragionamento({"reasoning_budget": -1}) == BUDGET_RAGIONAMENTO


def test_nessun_tag_passa_come_testo_vero():
    f = FiltroPensieroInline()
    vero, pensiero = f.filtra("ciao mondo")
    assert vero == "ciao mondo"
    assert pensiero == ""


def test_blocco_di_pensiero_isolato_dal_testo():
    f = FiltroPensieroInline()
    vero, pensiero = f.filtra("prima<think>segreto</think>dopo")
    assert vero == "primadopo"
    assert pensiero == "segreto"


def test_tag_spezzato_fra_due_frammenti_dello_stream():
    """Bug reale: un motore può mandare '<thi' in un evento e 'nk>' nel successivo —
    cercare il tag intero in ciascun frammento preso da solo lo lascerebbe passare
    come testo vero."""
    f = FiltroPensieroInline()
    v1, p1 = f.filtra("prima<thi")
    v2, p2 = f.filtra("nk>segreto</th")
    v3, p3 = f.filtra("ink>dopo")
    assert v1 + v2 + v3 == "primadopo"
    assert p1 + p2 + p3 == "segreto"


def test_ragionamento_mai_chiuso_non_diventa_testo():
    """Se il budget finisce a metà del ragionamento (troncamento), il testo vero
    resta vuoto invece di mostrare il pensiero grezzo — così chi chiama vede un
    `TruncatedResponse` invece di una risposta apparentemente riuscita ma sbagliata."""
    f = FiltroPensieroInline()
    vero, pensiero = f.filtra("<think>sto pensando a lungo e non finisco mai")
    assert vero == ""
    assert pensiero == "sto pensando a lungo e non finisco mai"


def test_piu_blocchi_di_pensiero_nello_stesso_stream():
    f = FiltroPensieroInline()
    pezzi = ["<think>uno</think>", "testo1", "<think>due</think>", "testo2"]
    vero_tot, pensiero_tot = "", ""
    for pezzo in pezzi:
        v, p = f.filtra(pezzo)
        vero_tot += v
        pensiero_tot += p
    assert vero_tot == "testo1testo2"
    assert pensiero_tot == "unodue"
