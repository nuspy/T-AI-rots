"""Quante chiamate al modello fa una lettura, e con quali prompt: la base per contare i token.

Una lettura non è una chiamata: è un'intervista (una domanda, e il controllo di ciascuna), le interpretazioni delle
carte (una chiamata sola), il responso con la dottrina nel contesto e il giudice che lo verifica. Con un modello a pagamento ognuna
costa. Questo test percorre letture intere con il modello finto, registra ogni prompt e, se `TAROT_CATTURA_PROMPT`
indica un file, lo scrive in JSON: `tools/conta_token.py` ne ricava token e costi. Senza la variabile controlla solo
che la forma di una lettura non cambi di nascosto (quante chiamate, di che tipo)."""
from __future__ import annotations

import json
import os
from collections import Counter

import pytest

from .conftest import richiede_database
from .test_flusso import STESE, _accredita, _lettura_completa
from .test_lettura_speciale import PARTNER, _scheda
from .test_lingue import QUESITI

pytestmark = richiede_database

STANDARD = ["tre-carte", "croce-semplice", "ferro-di-cavallo", "croce-celtica", "ruota-astrologica"]
SPECIALI = {"compat-tre": 3, "compat-nove": 9, "coppia-specchio": 8}
QUESITO_COPPIA = {"it": "Compatibilità con Marco", "en": "Compatibility with Marco", "hu": "Kompatibilitás Marcóval"}

_raccolta: dict = {}


def _salva():
    percorso = os.environ.get("TAROT_CATTURA_PROMPT")
    if percorso:
        with open(percorso, "w", encoding="utf-8") as f:
            json.dump(_raccolta, f, ensure_ascii=False)


async def _giro(client, session, prompt_visti, spread_id, carte, lingua, speciale):
    await _accredita(session, client.identita.principal)
    # La forma «piena» di una lettura: validatore e guardia LLM a ogni giro (il modo «acceso» della console). Nel modo
    # predefinito partono solo sui casi dubbi, e quanti siano dipende dalle carte uscite: lo provano
    # `test_controlli_dubbi.py`.
    from ..domain.impostazioni_repositories import correnti_intervista

    regole = await correnti_intervista(session)
    regole.validatore_domande, regole.guardia_responso = "acceso", "acceso"
    await session.flush()
    prompt_visti.clear()
    if speciale:
        await _scheda(client)
        await _lettura_completa(client, spread_id, carte, QUESITO_COPPIA[lingua], extra={"partner": PARTNER})
    else:
        await _lettura_completa(client, spread_id, carte, QUESITI[lingua])
    chiamate = [dict(v) for v in prompt_visti]
    _raccolta[f"{spread_id}/{lingua}"] = {"spread": spread_id, "lingua": lingua, "carte": carte, "chiamate": chiamate}
    _salva()
    return Counter(v["compito"] for v in chiamate)


@pytest.mark.parametrize("lingua", ["it", "en", "hu"])
@pytest.mark.parametrize("spread_id", STANDARD)
async def test_forma_di_una_lettura_standard(client, session, catalogo, prompt_visti, spread_id, lingua):
    n = STESE[spread_id]
    conta = await _giro(client, session, prompt_visti, spread_id, n, lingua, speciale=False)
    # Una chiamata sola per tutte le posizioni (anche una carta calcolata, non scelta, si interpreta): nessuna singola.
    assert conta["interpretazione_unica"] == 1 and conta["interpretazione"] == 0
    assert conta["sintesi"] == 1 and conta["giudizio"] == 1
    assert conta["intervista"] >= 3                 # col modello finto: due domande e la chiusura


@pytest.mark.parametrize("lingua", ["it", "en"])
@pytest.mark.parametrize("spread_id", list(SPECIALI))
async def test_forma_di_una_lettura_speciale(client, session, catalogo, prompt_visti, spread_id, lingua):
    n = SPECIALI[spread_id]
    conta = await _giro(client, session, prompt_visti, spread_id, n, lingua, speciale=True)
    assert conta["interpretazione_unica"] == 1 and conta["interpretazione"] == 0 and conta["sintesi"] == 1
    assert conta["giudizio"] == 1

