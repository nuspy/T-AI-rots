"""La lingua suggerita dal paese dell'IP: l'ultimo indizio dopo la scelta salvata e la lingua del browser."""
from __future__ import annotations

import pytest
from lanterna import geo

from tarot_core.tarot.lingue import LINGUE, LINGUA_PER_PAESE, lingua_per_paese

from .conftest import richiede_database


def test_ogni_suggerimento_e_una_lingua_del_sito():
    assert set(LINGUA_PER_PAESE.values()) <= set(LINGUE)
    assert lingua_per_paese("it") == "it" and lingua_per_paese("UA") == "uk" and lingua_per_paese("MX") == "es"
    # Paesi multilingue o sconosciuti: nessun suggerimento, si resta sul ripiego del sito.
    assert lingua_per_paese("CH") is None and lingua_per_paese(None) is None and lingua_per_paese("") is None


@pytest.fixture
def paese(monkeypatch):
    stato = {"paese": "HU"}

    def finto(_db, _ip):
        return geo.Luogo(paese=stato["paese"], regione=None, citta=None)

    monkeypatch.setattr(geo, "luogo", finto)
    return stato


@richiede_database
async def test_endpoint_lingua_suggerita(client, paese):
    r = await client.get("/lingua-suggerita")
    assert r.status_code == 200 and r.json() == {"paese": "HU", "lingua": "hu"}
    paese["paese"] = None
    assert (await client.get("/lingua-suggerita")).json() == {"paese": None, "lingua": None}
