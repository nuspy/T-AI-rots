"""L'estrazione della memoria da una lettura conclusa (v6, Fase B): parsing tollerante, nessun database."""
from __future__ import annotations

import json

import pytest

from tarot_core.llm.base import GenerationError, GenerationRequest, Message
from tarot_core.tarot.memoria import estrai_memorie


class _ProviderFinto:
    def __init__(self, risposta):
        self._risposta = risposta

    async def complete_json(self, req: GenerationRequest):
        if isinstance(self._risposta, Exception):
            raise self._risposta
        return self._risposta


async def test_estrae_una_memoria_stabile_e_una_variabile():
    provider = _ProviderFinto({
        "memorie": [
            {"contenuto": "Gli manca una gamba", "tipo": "stabile", "campo_attinenza": "salute"},
            {"contenuto": "Sta cercando un nuovo lavoro", "tipo": "variabile", "campo_attinenza": "lavoro"},
        ]
    })
    memorie = await estrai_memorie(provider, quesito="q", colloquio="c", sintesi="s")
    assert len(memorie) == 2
    assert memorie[0]["tipo"] == "stabile"
    assert memorie[1]["campo_attinenza"] == "lavoro"


async def test_lista_vuota_se_il_modello_non_trova_nulla():
    provider = _ProviderFinto({"memorie": []})
    assert await estrai_memorie(provider, quesito="q", colloquio="c", sintesi="s") == []


async def test_un_tipo_sconosciuto_viene_scartato():
    provider = _ProviderFinto({"memorie": [{"contenuto": "x", "tipo": "boh", "campo_attinenza": "amore"}]})
    assert await estrai_memorie(provider, quesito="q", colloquio="c", sintesi="s") == []


async def test_un_contenuto_vuoto_viene_scartato():
    provider = _ProviderFinto({"memorie": [{"contenuto": "  ", "tipo": "stabile", "campo_attinenza": "amore"}]})
    assert await estrai_memorie(provider, quesito="q", colloquio="c", sintesi="s") == []


async def test_campo_di_attinenza_mancante_ricade_su_altro():
    provider = _ProviderFinto({"memorie": [{"contenuto": "x", "tipo": "stabile"}]})
    memorie = await estrai_memorie(provider, quesito="q", colloquio="c", sintesi="s")
    assert memorie[0]["campo_attinenza"] == "altro"


async def test_una_risposta_non_json_produce_lista_vuota_senza_sollevare():
    provider = _ProviderFinto({"memorie": "non è una lista"})
    assert await estrai_memorie(provider, quesito="q", colloquio="c", sintesi="s") == []


async def test_il_modello_che_non_risponde_produce_lista_vuota():
    provider = _ProviderFinto(GenerationError("il server non risponde"))
    assert await estrai_memorie(provider, quesito="q", colloquio="c", sintesi="s") == []
