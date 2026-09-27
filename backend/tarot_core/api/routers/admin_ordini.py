"""La console: il registro degli ordini (v5, Fase B6) — sullo stesso schema di `GET /admin/payments`
(elenco filtrabile, totali) più il seguito della spedizione per le righe fisiche, che qui e solo qui
si aggiorna."""
from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import func, select

from ...auth.dependencies import CurrentUser, DbSession, require_role
from ...domain.ordini_models import Ordine, RigaOrdine
from ...domain.repositories import AuditRepository
from .shop import _ordine_json

router = APIRouter(prefix="/admin", tags=["ordini"], dependencies=[Depends(require_role("admin"))])


def _ip(request: Request) -> Optional[str]:
    return request.client.host if request.client else None


@router.get("/orders")
async def ordini(session: DbSession, status: str = "", limite: int = 100, offset: int = 0) -> Dict[str, Any]:
    filtro = [Ordine.status == status] if status else []
    totale = int(await session.scalar(select(func.count()).select_from(Ordine).where(*filtro)) or 0)
    righe = (
        await session.execute(
            select(Ordine).where(*filtro).order_by(Ordine.created_at.desc()).limit(min(limite, 500)).offset(max(offset, 0)),
        )
    ).scalars().all()
    incassato = int(await session.scalar(
        select(func.coalesce(func.sum(Ordine.importo_totale), 0)).where(Ordine.status == "pagato"),
    ) or 0)
    return {
        "totale": totale, "incassato": incassato,
        "ordini": [{"user_id": o.user_id, **_ordine_json(o)} for o in righe],
    }


@router.get("/orders/{ordine_id}")
async def ordine(ordine_id: str, session: DbSession) -> Dict[str, Any]:
    o = await session.get(Ordine, ordine_id)
    if o is None:
        raise HTTPException(status_code=404, detail="Ordine non trovato")
    return {"user_id": o.user_id, **_ordine_json(o)}


class EvasioneIn(BaseModel):
    stato_evasione: str = Field(pattern="^(in_attesa|spedito|consegnato)$")


@router.patch("/orders/{ordine_id}/righe/{riga_id}")
async def aggiorna_evasione(
    ordine_id: str, riga_id: int, payload: EvasioneIn, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    """Solo per righe «fisico»: le altre non hanno nulla da spedire, un `null` non si aggiorna a mano."""
    riga = await session.get(RigaOrdine, riga_id)
    if riga is None or str(riga.ordine_id) != ordine_id:
        raise HTTPException(status_code=404, detail="Riga non trovata")
    if riga.tipo != "fisico":
        raise HTTPException(status_code=422, detail="Solo una riga «fisico» ha uno stato di evasione da seguire")
    prima = riga.stato_evasione
    riga.stato_evasione = payload.stato_evasione
    await session.flush()
    await AuditRepository(session).record(
        action="ordine.evasione", actor_id=user.id, target_type="riga_ordine", target_id=str(riga_id),
        before={"stato_evasione": prima}, after={"stato_evasione": riga.stato_evasione}, ip=_ip(request),
    )
    await session.commit()
    o = await session.get(Ordine, ordine_id)
    return {"user_id": o.user_id, **_ordine_json(o)}
