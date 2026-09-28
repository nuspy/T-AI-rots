"""La console: i numeri del regalo d'iscrizione e del referral.

Una riga sola (`ImpostazioniCrediti`): quanti crediti regala l'iscrizione, quanti il riscatto di un codice
d'invito, e la percentuale di commissione che chi ha invitato riceve su ogni acquisto futuro dell'invitato. Ogni
scrittura finisce nel registro di audit (`domain/impostazioni_repositories.py::aggiorna`).
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from ...auth.dependencies import CurrentUser, DbSession, require_role
from ...domain.impostazioni_repositories import (
    aggiorna, aggiorna_chat, correnti, correnti_chat, pubblico, pubblico_chat,
)

router = APIRouter(prefix="/admin", tags=["impostazioni"], dependencies=[Depends(require_role("admin"))])


def _ip(request: Request) -> Optional[str]:
    return request.client.host if request.client else None


class ImpostazioniModifica(BaseModel):
    crediti_iscrizione: Optional[int] = Field(default=None, ge=0, le=1000)
    #: Il totale che l'invitato deve avere dopo il riscatto, non un extra sul regalo d'iscrizione.
    crediti_invito: Optional[int] = Field(default=None, ge=0, le=1000)
    commissione_referral_percentuale: Optional[int] = Field(default=None, ge=0, le=100)


@router.get("/impostazioni-crediti")
async def leggi(session: DbSession) -> Dict[str, Any]:
    return pubblico(await correnti(session))


@router.put("/impostazioni-crediti")
async def modifica(
    payload: ImpostazioniModifica, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    riga = await aggiorna(
        session, payload.model_dump(exclude_unset=True), attore_id=user.id, ip=_ip(request),
    )
    await session.commit()
    return pubblico(riga)


class ImpostazioniChatModifica(BaseModel):
    proattiva_minuti_inattivita: Optional[int] = Field(default=None, ge=1, le=180)


@router.get("/impostazioni-chat")
async def leggi_chat(session: DbSession) -> Dict[str, Any]:
    return pubblico_chat(await correnti_chat(session))


@router.put("/impostazioni-chat")
async def modifica_chat(
    payload: ImpostazioniChatModifica, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    riga = await aggiorna_chat(
        session, payload.model_dump(exclude_unset=True), attore_id=user.id, ip=_ip(request),
    )
    await session.commit()
    return pubblico_chat(riga)
