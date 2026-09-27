"""Lo strumento offline di descrizione di un mazzo nuovo: forma della scena, campione, bozza
incrementale che non riparte mai da zero, e la conversione dell'immagine scaricata."""
from __future__ import annotations

import json

import pytest
from PIL import Image

from tarot_core.tools.crea_mazzo import (
    NEGATIVO_BASE,
    SceneNonRiuscita,
    avverti_se_stile_ha_dimensioni,
    costruisci_prompt_carta,
    costruisci_prompt_dorso,
    genera_campione,
    genera_tutte,
    salva_immagine,
    scrivi_scena_carta,
    scrivi_scena_dorso,
)


class Copione:
    """Un modello che risponde con un copione fisso o in coda, come in test_traduci_conoscenza.py."""

    name = "copione"

    def __init__(self, risposte):
        self.risposte = list(risposte) if isinstance(risposte, list) else risposte
        self.richieste = []

    async def complete_json(self, req):
        self.richieste.append(req)
        if isinstance(self.risposte, list):
            return self.risposte.pop(0)
        return self.risposte(req)


STILE = "Acquerello botanico vittoriano, palette pastello, luce di serra."

CARTA_MAJ_00 = {
    "id": "maj-00", "arcano": "maggiore", "numero_romano": "0", "nome_thoth": "The Fool",
    "elemento": "aria", "astrologia": "Aria", "colori": ["#FFF8A6"],
    "lettera_ebraica": {"nome": "Aleph", "glifo": "א", "valore": 1},
    "percorso": 11, "collega": ["Kether", "Chokmah"],
}
CARTA_MAJ_01 = {
    "id": "maj-01", "arcano": "maggiore", "numero_romano": "I", "nome_thoth": "The Magus",
    "elemento": "aria", "astrologia": "Mercurio", "colori": ["#FFE135", "#7B3F9E"],
    "lettera_ebraica": {"nome": "Beth", "glifo": "ב", "valore": 2},
    "percorso": 12, "collega": ["Kether", "Binah"],
}


class ConoscenzaFinta:
    """Solo ciò che `genera_campione`/`genera_tutte` leggono: `.carte` e `.ordine`."""

    def __init__(self, carte, ordine):
        self.carte = carte
        self.ordine = ordine


# ---- validazione della scena ------------------------------------------------------------------


async def test_scrivi_scena_carta_ok():
    modello = Copione([{"scena": "  Una scena dipinta.  "}])
    scena = await scrivi_scena_carta(modello, CARTA_MAJ_01, STILE)
    assert scena == "Una scena dipinta."


async def test_scrivi_scena_carta_vuota_fallisce():
    modello = Copione([{"scena": "   "}])
    with pytest.raises(SceneNonRiuscita, match="vuota"):
        await scrivi_scena_carta(modello, CARTA_MAJ_01, STILE)


async def test_scrivi_scena_carta_con_dimensioni_fallisce():
    modello = Copione([{"scena": "Una scena in formato 1440x2560, molto dettagliata."}])
    with pytest.raises(SceneNonRiuscita, match="dimensione"):
        await scrivi_scena_carta(modello, CARTA_MAJ_01, STILE)


async def test_scrivi_scena_carta_con_aspect_ratio_fallisce():
    modello = Copione([{"scena": "Una scena in formato 9:16, molto dettagliata e ricca di dettagli."}])
    with pytest.raises(SceneNonRiuscita, match="dimensione"):
        await scrivi_scena_carta(modello, CARTA_MAJ_01, STILE)


async def test_scrivi_scena_dorso_ok():
    modello = Copione([{"scena": "Un motivo floreale simmetrico."}])
    scena = await scrivi_scena_dorso(modello, STILE)
    assert scena == "Un motivo floreale simmetrico."


def test_avverti_se_stile_ha_dimensioni_rileva():
    assert avverti_se_stile_ha_dimensioni("formato 1200x2000, stile acquerello") is not None


def test_avverti_se_stile_ha_dimensioni_non_rileva_stile_pulito():
    assert avverti_se_stile_ha_dimensioni(STILE) is None


# ---- assemblaggio dei prompt -------------------------------------------------------------------


def test_costruisci_prompt_carta():
    voce = costruisci_prompt_carta(CARTA_MAJ_01, STILE, "Una scena con Mercurio alato.")
    assert voce["top_text"] == "I"
    assert voce["bottom_text"] == "THE MAGUS"
    assert STILE in voce["prompt"]
    assert "Una scena con Mercurio alato." in voce["prompt"]
    assert "SCENE (what is painted inside the frame):" in voce["prompt"]
    assert voce["negative_prompt"] == NEGATIVO_BASE


def test_costruisci_prompt_dorso():
    voce = costruisci_prompt_dorso(STILE, "Un motivo floreale simmetrico.")
    assert STILE in voce["prompt"]
    assert "Un motivo floreale simmetrico." in voce["prompt"]
    assert "TEXT ON THE CARD: none" in voce["prompt"]


# ---- genera_campione: i due cancelli -------------------------------------------------------------


async def test_genera_campione_scrive_fronte_e_dorso(tmp_path):
    modello = Copione([{"scena": "Scena del Mago."}, {"scena": "Motivo del dorso."}])
    descrizioni = await genera_campione(modello, ConoscenzaFinta({"maj-01": CARTA_MAJ_01}, ["maj-01"]), STILE, "maj-01", tmp_path)

    assert descrizioni["carte"]["maj-01"]["scene"] == "Scena del Mago."
    assert descrizioni["dorso"]["scene"] == "Motivo del dorso."
    scritto = json.loads((tmp_path / "descrizioni.json").read_text(encoding="utf-8"))
    assert scritto["carte"]["maj-01"]["scene"] == "Scena del Mago."

    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["carte"]["maj-01"]["descritta"] is True
    assert manifest["dorso"]["descritta"] is True


async def test_genera_campione_solo_fronte_non_tocca_il_dorso(tmp_path):
    modello = Copione([{"scena": "Scena del Mago."}])
    descrizioni = await genera_campione(
        modello, ConoscenzaFinta({"maj-01": CARTA_MAJ_01}, ["maj-01"]), STILE, "maj-01", tmp_path, solo="fronte",
    )
    assert "dorso" not in descrizioni
    assert len(modello.richieste) == 1


async def test_genera_campione_carta_sconosciuta_solleva():
    with pytest.raises(KeyError):
        await genera_campione(Copione([]), ConoscenzaFinta({}, []), STILE, "maj-99", None)


# ---- genera_tutte: bozza incrementale, mai da zero -----------------------------------------------


async def test_genera_tutte_salta_le_gia_fatte_senza_chiamare_il_modello(tmp_path):
    (tmp_path / "descrizioni.json").write_text(json.dumps({
        "carte": {"maj-00": {"scene": "già fatta"}}, "dorso": {"scene": "già fatto"},
    }), encoding="utf-8")
    modello = Copione([{"scena": "Scena del Mago."}])
    conoscenza = ConoscenzaFinta({"maj-00": CARTA_MAJ_00, "maj-01": CARTA_MAJ_01}, ["maj-00", "maj-01"])

    esito = await genera_tutte(modello, conoscenza, STILE, tmp_path, silenzioso=True)

    assert esito["ok"] == ["maj-01"]
    assert len(modello.richieste) == 1  # maj-00 non richiesta di nuovo
    scritto = json.loads((tmp_path / "descrizioni.json").read_text(encoding="utf-8"))
    assert scritto["carte"]["maj-00"]["scene"] == "già fatta"  # intoccata
    assert scritto["carte"]["maj-01"]["scene"] == "Scena del Mago."


async def test_genera_tutte_con_solo_carte_rigenera_anche_se_gia_presente(tmp_path):
    (tmp_path / "descrizioni.json").write_text(json.dumps({
        "carte": {"maj-00": {"scene": "vecchia scena"}}, "dorso": {"scene": "già fatto"},
    }), encoding="utf-8")
    modello = Copione([{"scena": "scena nuova"}])
    conoscenza = ConoscenzaFinta({"maj-00": CARTA_MAJ_00}, ["maj-00"])

    esito = await genera_tutte(modello, conoscenza, STILE, tmp_path, solo_carte=["maj-00"], silenzioso=True)

    assert esito["ok"] == ["maj-00"]
    scritto = json.loads((tmp_path / "descrizioni.json").read_text(encoding="utf-8"))
    assert scritto["carte"]["maj-00"]["scene"] == "scena nuova"


async def test_genera_tutte_carta_fallita_non_viene_scritta(tmp_path):
    (tmp_path / "descrizioni.json").write_text(json.dumps({"carte": {}, "dorso": {"scene": "x"}}), encoding="utf-8")
    modello = Copione([{"scena": "formato 1440x2560, non valido"}])
    conoscenza = ConoscenzaFinta({"maj-00": CARTA_MAJ_00}, ["maj-00"])

    esito = await genera_tutte(modello, conoscenza, STILE, tmp_path, silenzioso=True)

    assert esito["ok"] == []
    assert len(esito["falliti"]) == 1
    scritto = json.loads((tmp_path / "descrizioni.json").read_text(encoding="utf-8"))
    assert "maj-00" not in scritto["carte"]


# ---- salva_immagine: conversione in WebP ---------------------------------------------------------


def test_salva_immagine_converte_in_webp(tmp_path):
    origine = tmp_path / "scaricata.png"
    Image.new("RGB", (100, 200), color="blue").save(origine, "PNG")

    destinazione = salva_immagine(tmp_path / "Set", "maj-01", origine)

    assert destinazione.name == "maj-01.webp"
    with Image.open(destinazione) as im:
        assert im.size == (100, 200)
    manifest = json.loads((tmp_path / "Set" / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["carte"]["maj-01"]["scaricata"] is True


def test_salva_immagine_dorso_usa_nome_fisso(tmp_path):
    origine = tmp_path / "scaricata.png"
    Image.new("RGB", (50, 50), color="red").save(origine, "PNG")

    destinazione = salva_immagine(tmp_path / "Set", "dorso", origine)

    assert destinazione.name == "dorso.webp"
    manifest = json.loads((tmp_path / "Set" / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["dorso"]["scaricata"] is True


def test_salva_immagine_file_non_trovato(tmp_path):
    with pytest.raises(FileNotFoundError):
        salva_immagine(tmp_path / "Set", "maj-01", tmp_path / "non-esiste.png")
