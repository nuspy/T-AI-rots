"""Il guardrail: crisi prima delle carte, giudice dopo il responso."""
from __future__ import annotations

import pytest

from tarot_core.guards.lettura import giudica, segnale_di_crisi, uscita_proibita
from tarot_core.guards.policy import RegistroGuardrail
from tarot_core.llm.base import GenerationError


@pytest.mark.parametrize("testo", [
    "voglio farla finita",
    "Penso al suicidio da giorni",
    "non voglio più vivere",
    "I want to kill myself",
])
def test_segnali_di_crisi(testo):
    assert segnale_di_crisi(testo)


def test_nessun_falso_allarme_sulla_carta_della_morte():
    assert not segnale_di_crisi("Cosa significa la carta della Morte nel mio lavoro?")


def test_formule_proibite_nell_uscita():
    assert uscita_proibita("Le carte dicono che morirai presto")
    assert uscita_proibita("Smetti di prendere le medicine... anzi, smetti la terapia")
    assert not uscita_proibita("La Morte indica la fine di una fase e l'inizio di un'altra.")


class Giudice:
    name = "giudice"

    def __init__(self, esito=None, errore=False):
        self.esito = esito
        self.errore = errore

    async def complete_json(self, req):
        if self.errore:
            raise GenerationError("giù")
        return self.esito


@pytest.fixture(scope="module")
def registro():
    return RegistroGuardrail()


def test_i_guardrail_si_caricano(registro):
    slug = {g.slug for g in registro.per()}
    assert {"crisi-e-autolesionismo", "materie-riservate", "fatalismo", "autonomia-e-dipendenza"} <= slug


async def test_una_regola_bloccante_blocca(registro):
    verdetto = await giudica(
        Giudice({"esito": "riscrivi", "violazioni": [{"regola": "crisi-e-autolesionismo", "motivo": "x"}]}),
        registro, quesito="q", responso="r",
    )
    assert verdetto.esito == "blocca"


async def test_il_giudice_assente_non_lascia_passare_le_formule_proibite(registro):
    verdetto = await giudica(Giudice(errore=True), registro, quesito="q", responso="Morirai presto.")
    assert verdetto.esito == "riscrivi" and not verdetto.verificato
    verdetto = await giudica(Giudice(errore=True), registro, quesito="q", responso="Un responso sereno.")
    assert verdetto.ok and not verdetto.verificato
