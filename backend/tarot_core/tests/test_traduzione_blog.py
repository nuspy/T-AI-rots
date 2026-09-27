"""La traduzione di un articolo: campi tradotti, FAQ pari in numero, mai una bozza a metà."""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from tarot_core.llm.base import GenerationError
from tarot_core.tarot.traduzione_blog import TraduzioneNonRiuscita, traduci_articolo


class Copione:
    """Un modello che risponde con un copione, come in test_intervista.py."""

    name = "copione"

    def __init__(self, risposte):
        self.risposte = list(risposte)
        self.richieste = []

    async def complete_json(self, req):
        self.richieste.append(req)
        return self.risposte.pop(0)


def _articolo(**extra):
    base = dict(
        id="11111111-1111-1111-1111-111111111111",
        titolo="The Tower Tarot Card Meaning",
        sottotitolo="A moment of clarity, not a curse.",
        testo="## What The Tower shows\n\n[[card:the-tower]] strikes at dawn.",
        seo_titolo="The Tower Tarot Card Meaning",
        seo_descrizione="Meaning of The Tower in the Thoth deck, upright and ill-dignified.",
        immagine_alt="A tower struck by lightning",
        faq=[{"domanda": "Is it bad luck?", "risposta": "No."}, {"domanda": "What letter?", "risposta": "Peh."}],
    )
    base.update(extra)
    return SimpleNamespace(**base)


async def test_traduzione_completa():
    modello = Copione([{
        "titolo": "Il significato della Torre nei tarocchi",
        "sottotitolo": "Un momento di chiarezza, non una maledizione.",
        "testo": "## Cosa mostra la Torre\n\n[[card:the-tower]] colpisce all'alba.",
        "seo_titolo": "Il significato della Torre nei tarocchi",
        "seo_descrizione": "Il significato della Torre nel mazzo di Thoth, dritta e mal dignificata.",
        "immagine_alt": "Una torre colpita da un fulmine",
        "faq": [
            {"domanda": "Porta sfortuna?", "risposta": "No."},
            {"domanda": "Quale lettera?", "risposta": "Peh."},
        ],
    }])
    risultato = await traduci_articolo(modello, _articolo(), "it")
    assert risultato["titolo"] == "Il significato della Torre nei tarocchi"
    assert "[[card:the-tower]]" in risultato["testo"]  # la scorciatoia resta intatta
    assert len(risultato["faq"]) == 2
    assert modello.richieste[0].temperature == 0.3


async def test_scorciatoia_lasciata_intatta_nel_prompt_utente():
    modello = Copione([{
        "titolo": "x", "sottotitolo": None, "testo": "x", "seo_titolo": "x", "seo_descrizione": "x",
        "immagine_alt": None, "faq": [],
    }])
    await traduci_articolo(modello, _articolo(faq=[]), "hu")
    utente = next(m.content for m in modello.richieste[0].messages if m.role == "user")
    assert "[[card:the-tower]]" in utente


@pytest.mark.parametrize("campo", ["titolo", "testo", "seo_titolo", "seo_descrizione"])
async def test_campo_mancante_fallisce(campo):
    risposta = {
        "titolo": "x", "sottotitolo": None, "testo": "x", "seo_titolo": "x", "seo_descrizione": "x",
        "immagine_alt": None, "faq": [],
    }
    risposta[campo] = ""
    modello = Copione([risposta])
    with pytest.raises(TraduzioneNonRiuscita, match=campo):
        await traduci_articolo(modello, _articolo(faq=[]), "hu")


async def test_faq_spaiate_falliscono():
    modello = Copione([{
        "titolo": "x", "sottotitolo": None, "testo": "x", "seo_titolo": "x", "seo_descrizione": "x",
        "immagine_alt": None, "faq": [{"domanda": "una sola", "risposta": "..."}],
    }])
    with pytest.raises(TraduzioneNonRiuscita, match="FAQ"):
        await traduci_articolo(modello, _articolo(), "hu")  # l'originale ne ha 2


async def test_errore_del_modello_diventa_traduzione_non_riuscita():
    class Rotto:
        name = "rotto"

        async def complete_json(self, req):
            raise GenerationError("il modello non risponde")

    with pytest.raises(TraduzioneNonRiuscita):
        await traduci_articolo(Rotto(), _articolo(), "hu")
