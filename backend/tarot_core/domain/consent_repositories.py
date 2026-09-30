"""Lettura e scrittura dei consensi GDPR (v7, Fase G)."""
from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .consent_models import UserConsent
from .repositories import AuditRepository


async def correnti_per(
    session: AsyncSession, *, user_id: Optional[int], anon_id: Optional[str],
) -> dict[str, UserConsent]:
    """I consensi attuali di questa persona (loggata o anonima), per tipo."""
    if user_id is not None:
        condizione = UserConsent.user_id == user_id
    elif anon_id is not None:
        condizione = UserConsent.anon_id == anon_id
    else:
        return {}
    righe = (await session.execute(select(UserConsent).where(condizione))).scalars()
    return {r.tipo: r for r in righe}


async def registra(
    session: AsyncSession, *,
    user_id: Optional[int], anon_id: Optional[str], tipo: str, valore: str,
    versione_informativa: str, ip: Optional[str],
) -> UserConsent:
    """Scrive lo stato corrente del consenso (sovrascrive se già presente) E un evento di audit.

    Esattamente uno fra `user_id`/`anon_id` deve essere valorizzato: lo garantisce il chiamante
    (l'endpoint pubblico), non questa funzione — qui si assume già validato, come per
    `Reading.owner_id`/`Reading.anon_id`.
    """
    if user_id is not None:
        riga = (await session.execute(
            select(UserConsent).where(UserConsent.user_id == user_id, UserConsent.tipo == tipo)
        )).scalar_one_or_none()
    else:
        riga = (await session.execute(
            select(UserConsent).where(UserConsent.anon_id == anon_id, UserConsent.tipo == tipo)
        )).scalar_one_or_none()

    if riga is None:
        riga = UserConsent(user_id=user_id, anon_id=anon_id, tipo=tipo)
        session.add(riga)
    riga.valore = valore
    riga.versione_informativa = versione_informativa
    riga.ip = ip
    # `updated_at` lo calcola il database (`onupdate=func.now()` in TimestampMixin), mai Python:
    # con più repliche dell'API l'orologio del database è l'unico riferimento condiviso.

    await AuditRepository(session).record(
        action=f"consenso.{tipo}", actor_id=user_id,
        target_type="consenso", target_id=str(user_id) if user_id is not None else anon_id,
        after={"valore": valore, "versione_informativa": versione_informativa},
        ip=ip,
    )
    return riga
