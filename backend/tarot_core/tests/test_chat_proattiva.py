"""La generazione di un turno della chat proattiva (v6, Fase E): parsing tollerante, nessun database."""
from __future__ import annotations

from tarot_core.llm.base import GenerationError
from tarot_core.tarot.chat_proattiva import MAPPA_CATEGORIA, genera_turno


class _ProviderFinto:
    def __init__(self, risposta):
        self._risposta = risposta

    async def complete_json(self, req):
        if isinstance(self._risposta, Exception):
            raise self._risposta
        return self._risposta


async def test_un_messaggio_senza_proposta():
    provider = _ProviderFinto({"messaggio": "Come va oggi?", "proposta": None})
    esito = await genera_turno(provider)
    assert esito.messaggio == "Come va oggi?"
    assert esito.proposta is None


async def test_una_proposta_valida_mappa_il_tema_sulla_categoria():
    provider = _ProviderFinto({
        "messaggio": "Vuoi leggere le carte sul tuo lavoro?",
        "proposta": {"argomento": "il colloquio di domani", "tema": "lavoro"},
    })
    esito = await genera_turno(provider)
    assert esito.proposta is not None
    assert esito.proposta.argomento == "il colloquio di domani"
    assert esito.proposta.categoria == "standard"


async def test_ogni_tema_della_mappa_produce_una_categoria_nota():
    for tema, categoria_attesa in MAPPA_CATEGORIA.items():
        provider = _ProviderFinto({"messaggio": "x", "proposta": {"argomento": "y", "tema": tema}})
        esito = await genera_turno(provider)
        assert esito.proposta.categoria == categoria_attesa


async def test_una_proposta_senza_argomento_si_scarta():
    provider = _ProviderFinto({"messaggio": "x", "proposta": {"argomento": "", "tema": "amore"}})
    esito = await genera_turno(provider)
    assert esito.proposta is None


async def test_un_tema_sconosciuto_ricade_su_standard():
    provider = _ProviderFinto({"messaggio": "x", "proposta": {"argomento": "y", "tema": "boh"}})
    esito = await genera_turno(provider)
    assert esito.proposta.categoria == "standard"


async def test_il_modello_che_non_risponde_produce_messaggio_vuoto():
    provider = _ProviderFinto(GenerationError("silenzio"))
    esito = await genera_turno(provider)
    assert esito.messaggio == ""
    assert esito.proposta is None
