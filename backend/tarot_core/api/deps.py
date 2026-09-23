"""Dipendenze condivise dagli endpoint.

Tutto ciò che un endpoint riceve dall'esterno passa da qui: i modelli, i
guardrail, la base di conoscenza. Averle in un punto solo è ciò che permette a
un test di sostituirle senza avviare l'infrastruttura.
"""
from __future__ import annotations

import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_registro_modelli():
    """L'elenco dei modelli e chi serve quale compito.

    In cache come i fornitori che contiene: l'oggetto ricorda quale modello
    ciascun server ha caricato, e ricostruirlo a ogni domanda significherebbe
    chiedere di nuovo l'elenco dei modelli prima di ogni singola risposta.
    """
    from ..llm.compiti import RegistroModelli, modelli_da_impostazioni

    return RegistroModelli(modelli_da_impostazioni())


@lru_cache(maxsize=1)
def _modello_finto():
    from ..tarot.finto import ModelloFinto

    return ModelloFinto()


def provider_per(compito) -> object:
    """Il fornitore di un compito.

    Con `TAROT_LLM_FINTO=true` tutti i compiti vanno al modello finto: serve
    a provare il flusso intero — e l'interfaccia — senza un modello vero.
    """
    from ..settings import get_settings

    if get_settings().llm_finto:
        return _modello_finto()
    return get_registro_modelli().per(compito)


async def aggiorna_assegnazioni(session, *, forza: bool = False) -> None:
    """Rilegge dal database chi serve quale compito, se è ora.

    Con più repliche dell'API una modifica fatta su una non arriva alle altre
    da sola: il registro ha una scadenza breve e si rinfresca da sé. Un errore
    qui non ferma la richiesta — l'assegnazione di prima è vecchia di mezzo
    minuto, non sbagliata.
    """
    from ..domain.admin_repositories import assegnazioni_correnti
    from ..llm.compiti import Compito

    registro = get_registro_modelli()
    if not forza and not registro.da_rileggere():
        return

    try:
        righe = await assegnazioni_correnti(session)
    except Exception:  # noqa: BLE001
        logger.warning(
            "Assegnazioni dei modelli non rilette: si continua con quelle "
            "in memoria", exc_info=True,
        )
        return

    registro.aggiorna({
        compito: righe[compito.value] for compito in Compito if righe.get(compito.value)
    })


@lru_cache(maxsize=1)
def get_guardrail():
    """I guardrail, letti una volta dal disco.

    Sono file che non cambiano mentre il processo gira: in produzione
    arrivano con l'immagine.
    """
    from ..guards.policy import RegistroGuardrail

    return RegistroGuardrail()


@lru_cache(maxsize=1)
def get_conoscenza():
    """Mazzo, stese e dottrina, caricati e validati una volta sola."""
    from ..tarot.conoscenza import Conoscenza

    return Conoscenza.carica()


def reset_dependencies() -> None:
    """Dimentica le istanze memorizzate. Solo per i test."""
    get_registro_modelli.cache_clear()
    _modello_finto.cache_clear()
    get_guardrail.cache_clear()
    get_conoscenza.cache_clear()
