"""Lo strumento offline di traduzione di carte/stese: forma corretta, ripresa, mai una voce a metà."""
from __future__ import annotations

import json

import pytest

from tarot_core.tools.traduci_conoscenza import (
    TraduzioneVoceNonRiuscita,
    esegui,
    traduci_carta,
    traduci_glossario,
    traduci_stesa,
)


class Copione:
    """Un modello che risponde con un copione fisso o in coda, come in test_intervista.py."""

    name = "copione"

    def __init__(self, risposte):
        self.risposte = list(risposte) if isinstance(risposte, list) else risposte
        self.richieste = []

    async def complete_json(self, req):
        self.richieste.append(req)
        if isinstance(self.risposte, list):
            return self.risposte.pop(0)
        return self.risposte(req)


CARTA = {"id": "maj-00", "nome_thoth": "The Fool", "parole_chiave": ["a", "b", "c"]}

STESA = {
    "id": "tre-carte", "nome": "Tre carte", "nome_en": "Three cards",
    "origine": "...", "descrizione": "...", "regole": ["uno", "due"],
    "posizioni": [
        {"n": 1, "nome": "Passato", "significato": "...", "domanda": "..."},
        {"n": 2, "nome": "Presente", "significato": "...", "domanda": "..."},
    ],
}

SCHEDA_CARTA_OK = {
    "astro": "x", "kw": ["1", "2", "3"], "exo": "x", "psy": "x", "ini": "x", "sha": "x",
    "up": "x", "rev": "x", "love": "x", "work": "x", "spirit": "x", "crowley": "x",
}

SCHEDA_STESA_OK = {
    "slug": "three-cards", "nome": "Three cards", "origine": "x", "descrizione": "x",
    "regole": ["one", "two"],
    "pos": {
        "1": {"nome": "Past", "significato": "x", "domanda": "x"},
        "2": {"nome": "Present", "significato": "x", "domanda": "x"},
    },
}


async def test_traduci_carta_ok():
    modello = Copione([SCHEDA_CARTA_OK])
    risultato = await traduci_carta(modello, CARTA, "en")
    assert risultato["astro"] == "x"
    assert len(risultato["kw"]) == 3


async def test_traduci_carta_parole_chiave_spaiate():
    modello = Copione([{**SCHEDA_CARTA_OK, "kw": ["solo-una"]}])
    with pytest.raises(TraduzioneVoceNonRiuscita, match="parole chiave"):
        await traduci_carta(modello, CARTA, "en")


async def test_traduci_carta_campo_mancante():
    rotta = dict(SCHEDA_CARTA_OK)
    del rotta["crowley"]
    modello = Copione([rotta])
    with pytest.raises(TraduzioneVoceNonRiuscita, match="crowley"):
        await traduci_carta(modello, CARTA, "en")


async def test_traduci_stesa_ok():
    modello = Copione([SCHEDA_STESA_OK])
    risultato = await traduci_stesa(modello, STESA, "en")
    assert risultato["slug"] == "three-cards"
    assert risultato["pos"]["2"]["nome"] == "Present"


async def test_traduci_stesa_posizione_incompleta():
    rotta = json.loads(json.dumps(SCHEDA_STESA_OK))
    del rotta["pos"]["2"]["domanda"]
    modello = Copione([rotta])
    with pytest.raises(TraduzioneVoceNonRiuscita, match="posizione 2"):
        await traduci_stesa(modello, STESA, "en")


async def test_traduci_stesa_regole_spaiate():
    modello = Copione([{**SCHEDA_STESA_OK, "regole": ["una-sola"]}])
    with pytest.raises(TraduzioneVoceNonRiuscita, match="regole"):
        await traduci_stesa(modello, STESA, "en")


class ConoscenzaFinta:
    def __init__(self):
        self.carte = {"maj-00": CARTA}


async def test_traduci_glossario_ok():
    modello = Copione([{
        "elemento": {"Aria": "Air"}, "seme": {}, "rango": {}, "arcano": {"maggiore": "major"},
    }])
    CARTA_CON_TERMINI = {**CARTA, "elemento": "Aria", "arcano": "maggiore"}
    conoscenza = ConoscenzaFinta()
    conoscenza.carte = {"maj-00": CARTA_CON_TERMINI}
    risultato = await traduci_glossario(modello, conoscenza, "en")
    assert risultato["elemento"]["Aria"] == "Air"


async def test_traduci_glossario_termine_mancante():
    modello = Copione([{"elemento": {}, "seme": {}, "rango": {}, "arcano": {}}])
    conoscenza = ConoscenzaFinta()
    conoscenza.carte = {"maj-00": {**CARTA, "elemento": "Aria", "arcano": "maggiore"}}
    with pytest.raises(TraduzioneVoceNonRiuscita, match="elemento"):
        await traduci_glossario(modello, conoscenza, "en")


class ConoscenzaDiProva:
    """Un catalogo minimo, per `esegui()`: solo ciò che legge (carte/stese come dict)."""

    def __init__(self):
        self.carte = {
            "maj-00": {**CARTA, "elemento": "Aria", "arcano": "maggiore"},
            "maj-01": {**CARTA, "id": "maj-01", "nome_thoth": "The Magus", "elemento": "Aria", "arcano": "maggiore"},
        }
        self.stese = {"tre-carte": STESA}


async def test_esegui_scrive_una_voce_alla_volta_e_si_ferma_sui_falliti(tmp_path):
    modello = Copione([SCHEDA_CARTA_OK, {**SCHEDA_CARTA_OK, "astro": "y"}, SCHEDA_STESA_OK, {
        "elemento": {}, "seme": {}, "rango": {}, "arcano": {},
    }])
    esito = await esegui(modello, ConoscenzaDiProva(), "en", tmp_path, quieto=True)
    assert "carta:maj-00" in esito["ok"]
    assert "carta:maj-01" in esito["ok"]
    assert "stesa:tre-carte" in esito["ok"]
    assert len(esito["falliti"]) == 1  # il glossario, con termini mancanti
    scritte = json.loads((tmp_path / "cards-bozza.json").read_text(encoding="utf-8"))
    assert set(scritte) == {"maj-00", "maj-01"}


async def test_esegui_con_riprendi_salta_le_voci_gia_scritte(tmp_path):
    (tmp_path / "cards-bozza.json").write_text(json.dumps({"maj-00": SCHEDA_CARTA_OK}), encoding="utf-8")
    modello = Copione([{**SCHEDA_CARTA_OK, "astro": "nuova"}])  # solo per maj-01, l'unica non ancora fatta
    esito = await esegui(
        modello, ConoscenzaDiProva(), "en", tmp_path,
        solo_carte=["maj-00", "maj-01"], solo_stese=[], riprendi=True, quieto=True,
    )
    assert esito["ok"] == ["carta:maj-01"]
    assert len(modello.richieste) == 1  # non ha richiesto di nuovo maj-00, e le stese non erano richieste
