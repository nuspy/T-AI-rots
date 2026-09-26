"""L'intervista non chiede mai all'utente la risposta al suo quesito."""
from __future__ import annotations

import json

import pytest

from tarot_core.llm.base import GenerationError, StreamChunk
from tarot_core.tarot.intervista import IntervistaNonRiuscita, prossimo_passo, viola_le_regole


@pytest.mark.parametrize("domanda", [
    "Secondo te, il tuo ragazzo ti ama?",
    "Il tuo ragazzo ti ama?",
    "Pensi che otterrai quel lavoro?",
    "Credi che lui tornerà da te?",
    "Come pensi che andrà a finire?",
    "Da quanto state insieme? E vi vedete spesso?",
])
def test_il_controllo_scarta_le_domande_vietate(domanda):
    assert viola_le_regole("Il mio ragazzo mi ama?", domanda) is not None


@pytest.mark.parametrize("domanda", [
    "Da quanto tempo state insieme?",
    "Cosa è successo di recente fra voi che ti ha fatto nascere questa domanda?",
    "Come ti senti quando siete lontani?",
    "Da quanto tempo conosci il tuo ragazzo?",
])
def test_il_controllo_lascia_passare_le_domande_di_contesto(domanda):
    assert viola_le_regole("Il mio ragazzo mi ama?", domanda) is None


class Copione:
    """Un modello che risponde con un copione, per provare la rigenerazione."""

    name = "copione"

    def __init__(self, risposte):
        self.risposte = list(risposte)
        self.chiamate = 0

    async def complete_json(self, req):
        self.chiamate += 1
        return self.risposte.pop(0)

    async def complete(self, req):
        return json.dumps(await self.complete_json(req))

    async def stream(self, req):
        yield StreamChunk(text=await self.complete(req))
        yield StreamChunk(done=True)


async def test_una_domanda_vietata_viene_rigenerata():
    intervista = Copione([
        {"completo": False, "domanda": "Secondo te lui ti ama?"},
        {"completo": False, "domanda": "Da quanto tempo vi conoscete?"},
    ])
    validatore = Copione([{"valida": True}])
    passo = await prossimo_passo(
        provider_intervista=intervista, provider_validazione=validatore,
        quesito="Il mio ragazzo mi ama?", stesa_nome="Tre carte", turni=[], max_domande=5,
    )
    assert passo.domanda == "Da quanto tempo vi conoscete?"
    assert passo.scartate == 1


async def test_il_validatore_ha_l_ultima_parola():
    intervista = Copione([
        {"completo": False, "domanda": "Hai la sensazione che il suo affetto sia sincero?"},
        {"completo": False, "domanda": "Come vi siete conosciuti?"},
    ])
    validatore = Copione([
        {"valida": False, "motivo": "chiede la risposta al quesito"},
        {"valida": True},
    ])
    passo = await prossimo_passo(
        provider_intervista=intervista, provider_validazione=validatore,
        quesito="Il mio ragazzo mi ama?", stesa_nome="Tre carte", turni=[], max_domande=5,
    )
    assert passo.domanda == "Come vi siete conosciuti?"
    assert passo.scartate == 1


async def test_un_modello_ostinato_non_riceve_domande_di_riserva():
    """Non esistono domande fisse: se il modello insiste con domande vietate
    prima del minimo, l'intervista fallisce invece di porre a tutti lo stesso."""
    intervista = Copione([{"completo": False, "domanda": "Pensi che ti ami?"}] * 3)
    with pytest.raises(IntervistaNonRiuscita):
        await prossimo_passo(
            provider_intervista=intervista, provider_validazione=Copione([]),
            quesito="Il mio ragazzo mi ama?", stesa_nome="Tre carte", turni=[], max_domande=6,
        )


class ModelloMuto:
    """Un modello che non risponde."""

    name = "muto"

    async def complete_json(self, req):
        raise GenerationError("timeout")

    async def complete(self, req):
        raise GenerationError("timeout")

    async def stream(self, req):
        raise GenerationError("timeout")
        yield  # pragma: no cover


async def test_un_modello_che_non_risponde_fa_fallire_l_intervista():
    with pytest.raises(IntervistaNonRiuscita):
        await prossimo_passo(
            provider_intervista=ModelloMuto(), provider_validazione=ModelloMuto(),
            quesito="Cosa mi riserva l'anno?", stesa_nome="Tre carte", turni=[], max_domande=6,
        )


async def test_non_si_chiude_prima_del_minimo():
    """Un modello che chiude alla prima battuta viene richiamato: servono almeno 2 domande."""
    intervista = Copione([
        {"completo": True, "riassunto": "Troppo presto."},
        {"completo": False, "domanda": "Da quanto tempo lavori in quell'azienda?"},
    ])
    passo = await prossimo_passo(
        provider_intervista=intervista, provider_validazione=Copione([{"valida": True}]),
        quesito="Devo cambiare lavoro?", stesa_nome="Tre carte", turni=[],
        min_domande=2, max_domande=6,
    )
    assert not passo.completo and passo.domanda
    assert intervista.chiamate == 2


async def test_dopo_il_minimo_il_modello_puo_chiudere():
    intervista = Copione([{"completo": True, "riassunto": "Il quadro."}])
    turni = [("oracolo", "a?"), ("utente", "x"), ("oracolo", "b?"), ("utente", "y")]
    passo = await prossimo_passo(
        provider_intervista=intervista, provider_validazione=Copione([]),
        quesito="Devo cambiare lavoro?", stesa_nome="Tre carte", turni=turni,
        min_domande=2, max_domande=6,
    )
    assert passo.completo and passo.riassunto == "Il quadro."


async def test_al_massimo_delle_domande_si_chiude():
    intervista = Copione([{"completo": True, "riassunto": "Il quadro."}])
    turni = [("oracolo", "a?"), ("utente", "x"), ("oracolo", "b?"), ("utente", "y")]
    passo = await prossimo_passo(
        provider_intervista=intervista, provider_validazione=Copione([]),
        quesito="Cosa mi riserva l'anno?", stesa_nome="Ruota", turni=turni, max_domande=2,
    )
    assert passo.completo and passo.riassunto == "Il quadro."
