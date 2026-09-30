"""Gli eventi di business di TAROTS chat (v8), emessi lato server con `lanterna`.

Si chiamano **prima** del `commit` di chi li emette: l'evento sta nella stessa transazione del fatto
che racconta (un acquisto annullato da un rollback non lascia un evento «acquisto» orfano). Non
sollevano mai: `lanterna` li scrive in un savepoint e, se qualcosa va storto, li perde con un avviso
nel log invece di far fallire la richiesta.

Mai contenuti nelle proprietà: né il testo della domanda, né il responso, né nomi. Solo categorie
(stesa, tipo di lettura, lingua, piano).
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from lanterna.eventi import emetti_evento, segna_registrazione

from ..domain.analytics_models import TABELLE
from ..settings import get_settings

# I nomi, in un posto solo: la console e il catalogo delle interrogazioni li leggono da qui.
REGISTRAZIONE = "registrazione"
LETTURA_APERTA = "lettura_aperta"
LETTURA_COMPLETATA = "lettura_completata"
LETTURA_CRISI = "lettura_crisi"
LETTURA_CANCELLATA = "lettura_cancellata"
LETTURA_FEEDBACK = "lettura_feedback"
LETTURA_CONDIVISA = "lettura_condivisa"
CHECKOUT_AVVIATO = "checkout_avviato"
ACQUISTO = "acquisto"
COUPON_RISCATTATO = "coupon_riscattato"
INVITO_RISCATTATO = "invito_riscattato"
VOTO_MAZZO = "voto_mazzo"
CARTA_DEL_GIORNO = "carta_del_giorno"


async def evento(
    session,
    nome: str,
    *,
    utente_id: Optional[int] = None,
    valore_centesimi: Optional[int] = None,
    valuta: Optional[str] = None,
    proprieta: Optional[Dict[str, Any]] = None,
) -> None:
    if not get_settings().analytics_attivi:
        return
    await emetti_evento(
        session, TABELLE, nome,
        utente_id=utente_id, valore_centesimi=valore_centesimi, valuta=valuta, proprieta=proprieta,
    )


async def registrazione(session, utente_id: int) -> None:
    """Il nuovo iscritto: la riga di attribuzione e l'evento."""
    if not get_settings().analytics_attivi:
        return
    await segna_registrazione(session, TABELLE, utente_id)
    await evento(session, REGISTRAZIONE, utente_id=utente_id)
