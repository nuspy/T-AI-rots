"""I prompt delle immagini: 78, autonomi, uniformi."""
from __future__ import annotations

import json

from tarot_core.paths import KNOWLEDGE_DIR
from tarot_core.tools.prompt_immagini import STILE, TESTO, USCITA, costruisci


def test_78_prompt_autonomi_con_stile_testo_e_font():
    dati = costruisci()
    mazzo = json.loads((KNOWLEDGE_DIR / "deck.json").read_text(encoding="utf-8"))
    carte = dati["cards"]
    assert len(carte) == 78 == dati["count"]
    assert [c["id"] for c in carte] == [c["id"] for c in mazzo]
    assert len({c["file"] for c in carte}) == 78
    for c in carte:
        assert c["file"] == f"{c['id']}.webp"
        # Lo stile si ripete intero: ogni prompt deve bastare a sé stesso.
        assert c["prompt"].startswith(STILE)
        assert "Cinzel" in c["prompt"] and c["font"] == "Cinzel"
        assert f'"{c["top_text"]}"' in c["prompt"] and f'"{c["bottom_text"]}"' in c["prompt"]
        assert c["bottom_text"] and c["top_text"]
        assert len(c["prompt"].split("SCENE")[1].split()) > 120


def test_testi_in_inglese():
    carte = {c["id"]: c for c in costruisci()["cards"]}
    assert carte["maj-00"]["bottom_text"] == "THE FOOL"
    assert carte["bastoni-02"]["top_text"] == "TWO OF WANDS"
    assert carte["bastoni-02"]["bottom_text"] == "DOMINION"
    assert carte["coppe-regina"]["bottom_text"] == "QUEEN OF CUPS"
    assert carte["coppe-regina"]["top_text"] == "WATER OF WATER"


def test_il_file_pubblicato_e_aggiornato():
    """Il JSON nel frontend coincide con quello che il generatore produce."""
    assert json.loads(USCITA.read_text(encoding="utf-8")) == costruisci()


def test_il_testo_richiesto_e_unico():
    assert "write nothing else" in TESTO
