"""La raccolta degli analytics dal browser (v8): `POST /e` e `POST /e/dimentica`.

Il router è quello generico di `lanterna`; qui si decide solo come si riconosce l'utente. Un token
valido basta per legare la visita all'account (legittimo interesse, vedi l'informativa), ma la
raccolta **non crea mai un utente**: se il `sub` non ha ancora una riga, la visita resta anonima.
"""
from __future__ import annotations

from typing import Annotated, Dict, Optional

from fastapi import Depends
from lanterna.fastapi import crea_router_raccolta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...analytics.configurazione import configurazione
from ...auth.dependencies import current_principal_opzionale
from ...auth.keycloak import Principal
from ...domain.analytics_models import TABELLE
from ...domain.models import User
from ...domain.session import get_db_session
from ...settings import get_settings

#: `sub` → id, per non interrogare `users` a ogni lotto. Un id non cambia mai per lo stesso `sub`;
#: i `sub` sconosciuti non si ricordano (l'utente può registrarsi un attimo dopo).
_ID_PER_SUB: Dict[str, int] = {}


async def utente_id_opzionale(
    principal: Annotated[Optional[Principal], Depends(current_principal_opzionale)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Optional[int]:
    if principal is None:
        return None
    noto = _ID_PER_SUB.get(principal.subject)
    if noto is not None:
        return noto
    trovato = (
        await session.execute(
            select(User.id).where(User.keycloak_sub == principal.subject, User.deleted_at.is_(None))
        )
    ).scalar()
    if trovato is not None:
        if len(_ID_PER_SUB) > 100_000:
            _ID_PER_SUB.clear()
        _ID_PER_SUB[principal.subject] = trovato
    return trovato


router = crea_router_raccolta(
    config=configurazione,
    tabelle=TABELLE,
    sessione=get_db_session,
    utente=utente_id_opzionale,
    attivi=lambda: get_settings().analytics_attivi,
)
