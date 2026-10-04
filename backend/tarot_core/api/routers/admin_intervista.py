"""La console: quante domande fa l'oracolo prima delle carte (v8.5).

Minimo e massimo; fra i due decide il modello, e dopo il minimo chi consulta può fermarsi («No, basta così»). Qui
stanno anche i modi del validatore delle domande e della guardia del responso (solo casi dubbi, spento, acceso) e
l'interruttore dello stato sintetico della memoria nei prompt.
Ogni scrittura finisce nel registro di audit.
"""
from __future__ import annotations

from typing import Any, Dict, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from lanterna.rete import ip_client
from pydantic import BaseModel, Field

from ...auth.dependencies import CurrentUser, DbSession, require_role
from ...domain.impostazioni_repositories import aggiorna_intervista, correnti_intervista, pubblico_intervista

router = APIRouter(prefix="/admin", tags=["impostazioni"], dependencies=[Depends(require_role("admin"))])


class ImpostazioniIntervistaModifica(BaseModel):
    min_domande: Optional[int] = Field(default=None, ge=1, le=12)
    max_domande: Optional[int] = Field(default=None, ge=1, le=12)
    #: dubbi (predefinito): il controllo LLM parte solo sui casi che una regola deterministica segnala; spento: mai;
    #: acceso: sempre.
    validatore_domande: Optional[Literal["dubbi", "spento", "acceso"]] = None
    guardia_responso: Optional[Literal["dubbi", "spento", "acceso"]] = None
    #: Lo stato sintetico della memoria nei prompt di oracolo, intervista e sintesi.
    memoria_stato_nei_prompt: Optional[bool] = None


@router.get("/impostazioni-intervista")
async def leggi_intervista(session: DbSession) -> Dict[str, Any]:
    return pubblico_intervista(await correnti_intervista(session))


@router.put("/impostazioni-intervista")
async def modifica_intervista(
    payload: ImpostazioniIntervistaModifica, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    attuali = pubblico_intervista(await correnti_intervista(session))
    minimo = payload.min_domande if payload.min_domande is not None else attuali["min_domande"]
    massimo = payload.max_domande if payload.max_domande is not None else attuali["max_domande"]
    if minimo > massimo:
        raise HTTPException(status_code=422, detail="Il minimo di domande non può superare il massimo.")
    riga = await aggiorna_intervista(
        session, payload.model_dump(exclude_unset=True), attore_id=user.id, ip=ip_client(request),
    )
    await session.commit()
    return pubblico_intervista(riga)
