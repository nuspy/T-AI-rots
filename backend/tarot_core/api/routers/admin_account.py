"""La console «Account» (v9, Fase 3): tutti i servizi esterni che chiedono un account, con stato, passi, primo link e
dove sta il segreto; «Verifica» dove c'è una prova gratuita.

Il registro è nel codice (`servizi_esterni/registro.py`); le impostazioni restano nelle sezioni competenti. La lettura
non chiama nessun servizio esterno (le sonde leggono database e ambiente); la verifica sì, ma solo con prove gratuite,
le stesse dei pulsanti delle sezioni.
"""
from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException

from ...auth.dependencies import CurrentUser, DbSession, require_role
from ...domain.repositories import AuditRepository
from ...servizi_esterni.registro import CATEGORIE, PER_ID, REGISTRO, STATI, leggi_stato, stato, voce_json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/account-esterni", tags=["account-esterni"], dependencies=[Depends(require_role("admin"))])


@router.get("")
async def elenco(session: DbSession) -> Dict[str, Any]:
    servizi = [voce_json(s, await leggi_stato(session, s)) for s in REGISTRO]
    riepilogo = {nome: sum(1 for v in servizi if v["stato"] == nome) for nome in STATI}
    return {"servizi": servizi, "categorie": list(CATEGORIE), "stati": list(STATI), "riepilogo": riepilogo}


@router.post("/{servizio_id}/verifica")
async def verifica(servizio_id: str, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    servizio = PER_ID.get(servizio_id)
    if servizio is None:
        raise HTTPException(status_code=404, detail="Servizio sconosciuto")
    if servizio.verifica is None:
        raise HTTPException(status_code=422, detail="Per questo servizio non c'è una verifica automatica.")
    try:
        esito = await servizio.verifica(session, user)
    except Exception as exc:  # noqa: BLE001 — una prova che si rompe è un esito da mostrare, non un 500
        logger.warning("Verifica di %s non riuscita: %s", servizio_id, exc)
        await session.rollback()
        esito = stato("errore", f"La verifica non è riuscita ({type(exc).__name__}): riprova dalla sezione competente.")
    await AuditRepository(session).record(
        action="account_esterni.verifica", actor_id=user.id, target_type="servizio_esterno", target_id=servizio_id,
        after={"stato": esito["stato"]},
    )
    await session.commit()
    return {"servizio": voce_json(servizio, await leggi_stato(session, servizio)), "esito": esito}
