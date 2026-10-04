"""La console: i numeri del regalo d'iscrizione e del referral, la chat proattiva, il login persistente.

Una riga sola (`ImpostazioniCrediti`): quanti crediti regala l'iscrizione, quanti il riscatto di un codice
d'invito, e la percentuale di commissione che chi ha invitato riceve su ogni acquisto futuro dell'invitato. Ogni
scrittura finisce nel registro di audit (`domain/impostazioni_repositories.py::aggiorna`).
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from lanterna.rete import ip_client
from pydantic import BaseModel, Field

from ...auth.dependencies import CurrentUser, DbSession, require_role
from ...auth.keycloak_admin import KeycloakAdmin, KeycloakAdminError
from ...domain.impostazioni_repositories import aggiorna, aggiorna_chat, correnti, correnti_chat, pubblico, pubblico_chat
from ...domain.repositories import AuditRepository

router = APIRouter(prefix="/admin", tags=["impostazioni"], dependencies=[Depends(require_role("admin"))])


def _ip(request: Request) -> Optional[str]:
    return ip_client(request)


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
    #: 0 = l'oracolo non apre mai da solo (solo quando l'utente scrive).
    proattiva_max_per_visita: Optional[int] = Field(default=None, ge=0, le=20)


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


#: Un giorno in secondi: la console ragiona in giorni, Keycloak in secondi.
GIORNO = 86_400


class ImpostazioniSessioneModifica(BaseModel):
    """Il login persistente: la sessione offline di Keycloak (vedi `KeycloakAdmin.imposta_sessione_persistente`).

    `inattivita_giorni`: dopo quanti giorni **senza mai aprire** il sito o la console si deve rifare l'accesso
    (ogni visita li fa ripartire). `durata_massima_giorni`: un tetto assoluto dall'accesso; 0 = nessuno, si resta
    dentro fino al logout."""

    inattivita_giorni: int = Field(ge=1, le=3650)
    durata_massima_giorni: int = Field(default=0, ge=0, le=3650)


def _sessione_da_realm(realm: Dict[str, Any]) -> Dict[str, int]:
    attiva = bool(realm.get("offlineSessionMaxLifespanEnabled"))
    massima = int(realm.get("offlineSessionMaxLifespan") or 0) if attiva else 0
    return {
        "inattivita_giorni": round(int(realm.get("offlineSessionIdleTimeout") or 0) / GIORNO),
        "durata_massima_giorni": round(massima / GIORNO),
    }


@router.get("/impostazioni-sessione")
async def leggi_sessione() -> Dict[str, Any]:
    """I valori veri, letti da Keycloak a ogni apertura: nessuna copia locale che possa smentirli. Se Keycloak
    non risponde lo si dice, con il motivo, invece di mostrare un numero inventato."""
    try:
        valori = _sessione_da_realm(await KeycloakAdmin().leggi_realm())
    except KeycloakAdminError as exc:
        return {
            "keycloak_raggiungibile": False, "errore": str(exc),
            "inattivita_giorni": None, "durata_massima_giorni": None,
        }
    return {"keycloak_raggiungibile": True, "errore": None, **valori}


@router.put("/impostazioni-sessione")
async def modifica_sessione(
    payload: ImpostazioniSessioneModifica, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    """Cambia le durate **su Keycloak**, subito: valgono per il sito e per la console, anche per chi è già
    dentro (la scadenza di un token offline si ricalcola a ogni rinnovo)."""
    if payload.durata_massima_giorni and payload.durata_massima_giorni < payload.inattivita_giorni:
        raise HTTPException(
            status_code=422,
            detail="La durata massima non può essere più breve dell'inattività ammessa (0 = nessun limite).",
        )
    kc = KeycloakAdmin()
    try:
        prima = _sessione_da_realm(await kc.leggi_realm())
        await kc.imposta_sessione_persistente(
            inattivita_secondi=payload.inattivita_giorni * GIORNO,
            durata_massima_secondi=payload.durata_massima_giorni * GIORNO,
        )
        dopo = _sessione_da_realm(await kc.leggi_realm())
    except KeycloakAdminError as exc:
        raise HTTPException(status_code=502, detail=f"Keycloak non ha accettato il cambio: {exc}") from exc

    if prima != dopo:
        await AuditRepository(session).record(
            action="impostazioni_sessione.modifica", actor_id=user.id, target_type="keycloak_realm",
            target_id="sessione_offline", before=prima, after=dopo, ip=_ip(request),
        )
        await session.commit()
    return {"keycloak_raggiungibile": True, "errore": None, **dopo}
