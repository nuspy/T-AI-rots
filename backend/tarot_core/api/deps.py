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
    from ..settings import get_settings

    return RegistroModelli(modelli_da_impostazioni(), configurato=get_settings().llm_configurato())


@lru_cache(maxsize=1)
def _modello_finto():
    from ..tarot.finto import ModelloFinto

    return ModelloFinto()


async def verifica_modello(session, lang: str = "it") -> None:
    """503 se non c'è un modello vero a cui chiedere la lettura.

    Le domande, le interpretazioni e il responso li scrive un modello: senza,
    il servizio non finge con testi di ripiego uguali per tutti, e non addebita
    nulla. Va chiamata **prima** di aprire (e pagare) una lettura.

    Rilegge prima l'elenco dei fornitori (rispettando la stessa scadenza breve di `aggiorna_assegnazioni`): un
    fornitore aggiunto in console un istante fa deve rendere pronto il servizio senza aspettare la chiamata
    successiva che capiti di rinfrescarlo.
    """
    from fastapi import HTTPException, status

    from ..settings import get_settings
    from ..tarot.lingue import in_lingua
    from ..tarot.testi import MODELLO_NON_CONFIGURATO

    await aggiorna_assegnazioni(session)
    if get_settings().llm_finto or get_registro_modelli().configurato:
        return
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "motivo": "modello_non_configurato",
            "messaggio": in_lingua(MODELLO_NON_CONFIGURATO, lang),
        },
    )


def provider_per(compito, persone=None) -> object:
    """Il fornitore di un compito.

    Con `TAROT_LLM_FINTO=true` tutti i compiti vanno al modello finto: serve
    a provare il flusso intero — e l'interfaccia — senza un modello vero.

    Con `persone` (le persone di una lettura di coppia) il fornitore **non vede i nomi**: gli arriva un segnaposto e le
    risposte tornano col nome vero (`tarot/pseudonimi.py`). Si fa qui, al confine, perché nessun punto di chiamata
    debba ricordarsene.
    """
    from ..settings import get_settings
    from ..tarot.pseudonimi import protetto

    impostazioni = get_settings()
    fornitore = _modello_finto() if impostazioni.llm_finto else get_registro_modelli().per(compito)
    return protetto(fornitore, persone, attivo=impostazioni.anonimizza_nomi)


async def aggiorna_assegnazioni(session, *, forza: bool = False) -> None:
    """Rilegge dal database i fornitori LLM e chi serve quale compito, se è ora.

    Con più repliche dell'API una modifica fatta su una (un fornitore aggiunto in console, un'assegnazione cambiata)
    non arriva alle altre da sola: il registro ha una scadenza breve per ciascuno dei due e si rinfresca da sé. Un
    errore qui non ferma la richiesta — la configurazione di prima è vecchia di mezzo minuto, non sbagliata.
    """
    from ..domain.admin_repositories import assegnazioni_correnti
    from ..llm.compiti import Compito, modelli_da_impostazioni

    registro = get_registro_modelli()

    if forza or registro.da_rileggere_modelli():
        try:
            from ..domain.llm_repositories import modelli_da_db

            forniti = await modelli_da_db(session)
        except Exception:  # noqa: BLE001
            logger.warning(
                "Elenco dei fornitori LLM non riletto: si continua con quello "
                "in memoria", exc_info=True,
            )
        else:
            if forniti:
                registro.aggiorna_modelli(forniti, reale=True)
            else:
                # Tabella vuota (impianto appena installato, nessun fornitore ancora in console): si ricade
                # sull'ambiente, con lo stesso giudizio di «è una configurazione vera?» di sempre.
                from ..settings import get_settings

                registro.aggiorna_modelli(modelli_da_impostazioni(), reale=get_settings().llm_configurato())

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
