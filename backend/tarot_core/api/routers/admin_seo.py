"""La console della notifica ai motori di ricerca (v8): cosa è configurato, cosa è partito, e un invio
manuale quando non si vuole aspettare la mezzanotte."""
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select

from ...auth.dependencies import CurrentUser, DbSession, require_role
from ...domain.repositories import AuditRepository
from ...domain.seo_models import NotificaMotori
from ...tarot import notifiche_motori

router = APIRouter(prefix="/admin/seo", tags=["seo"], dependencies=[Depends(require_role("admin"))])


@router.get("/notifiche")
async def elenco(session: DbSession, limite: int = Query(default=30, ge=1, le=200)) -> Dict[str, Any]:
    righe = (await session.execute(
        select(NotificaMotori).order_by(NotificaMotori.created_at.desc()).limit(limite)
    )).scalars().all()
    return {
        "canali": notifiche_motori.stato_configurazione(),
        "invii": [notifiche_motori.riga_json(r) for r in righe],
    }


@router.post("/notifiche", status_code=201)
async def invia_ora(user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    """Lo stesso giro del CronJob notturno, subito: annuncia ciò che è cambiato dall'ultimo invio."""
    riga = await notifiche_motori.esegui(session, manuale=True)
    await AuditRepository(session).record(
        action="seo.notifica_motori", actor_id=user.id, target_type="notifiche_motori", target_id=str(riga.id),
        after={"url": len(riga.url), "riuscita": riga.riuscita},
    )
    await session.commit()
    return notifiche_motori.riga_json(riga)
