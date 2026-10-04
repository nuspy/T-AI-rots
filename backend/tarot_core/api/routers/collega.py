"""Collegare gli accessi social al proprio account (v9, Fase 6): dal profilo del sito e con il codice dell'app.

- `GET /me/collega`: i social già collegati all'account e quelli che si possono collegare (Google e Apple, se accesi).
- `POST /me/collega/social`: l'indirizzo del collegamento avviato dal sito (`/broker/{alias}/link` di Keycloak) per
  «Collega il tuo Apple ID» / «Collega Google». Il sito ci manda il browser subito dopo un passaggio da Keycloak.
- `POST /me/collega/codice`: dall'app, l'account appena nato chiede un codice monouso (8 caratteri, 10 minuti).
- `POST /me/collega/usa`: dal profilo del sito, l'account vecchio usa il codice e riceve identità e dati del nuovo.

Il perché e i dettagli in `tarot/collega_identita.py`. Ogni passo finisce nel registro di audit (mai il codice).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request
from lanterna.rete import ip_client
from pydantic import BaseModel, Field

from ...auth.dependencies import CurrentPrincipal, CurrentUser, DbSession
from ...auth.keycloak_admin import KeycloakAdmin, KeycloakAdminError
from ...domain.repositories import AuditRepository
from ...settings import get_settings
from ...tarot import collega_identita as collega

router = APIRouter(prefix="/me/collega", tags=["profilo"])


def _errore(exc: collega.ErroreCollegamento) -> HTTPException:
    return HTTPException(status_code=exc.stato, detail={"motivo": exc.motivo, **exc.dettagli})


def _keycloak_giu(exc: KeycloakAdminError) -> HTTPException:
    return HTTPException(status_code=503, detail={"motivo": "keycloak", "errore": str(exc)[:200]})


@router.get("")
async def stato(principal: CurrentPrincipal) -> Dict[str, Any]:
    """I social collegati (solo il nome del provider) e quelli che il profilo propone: Google e Apple, se accesi."""
    kc = KeycloakAdmin()
    try:
        collegati = sorted({str(i.get("identityProvider")) for i in await kc.identita_federate(principal.subject)})
        accesi = {p.get("alias") for p in await kc.provider_identita() if str(p.get("enabled")).lower() == "true"}
    except KeycloakAdminError:
        return {"raggiungibile": False, "collegati": [], "collegabili": []}
    return {
        "raggiungibile": True,
        "collegati": collegati,
        "collegabili": [a for a in collega.COLLEGABILI if a in accesi and a not in collegati],
    }


class CollegaSocial(BaseModel):
    provider: str = Field(pattern="^(google|apple)$")
    #: Dove Keycloak rimanda il browser: una pagina del sito (Keycloak la confronta con gli indirizzi del client).
    ritorno: str = Field(min_length=8, max_length=500, pattern="^https?://")


@router.post("/social")
async def url_social(payload: CollegaSocial, principal: CurrentPrincipal) -> Dict[str, str]:
    claims = principal.raw_claims or {}
    sessione = claims.get("sid") or claims.get("session_state")
    client_id = claims.get("azp")
    if not sessione or client_id not in get_settings().keycloak_accepted_audiences:
        # Un token senza sessione (client-credentials, sviluppo senza Keycloak) non può collegare niente.
        raise HTTPException(status_code=409, detail={"motivo": "sessione_mancante"})
    s = get_settings()
    return {"url": collega.url_collegamento(
        base_keycloak=s.keycloak_issuer_url or s.keycloak_url, realm=s.keycloak_realm, alias=payload.provider,
        client_id=client_id, sessione=str(sessione), ritorno=payload.ritorno,
    )}


@router.post("/codice")
async def crea_codice(request: Request, user: CurrentUser, principal: CurrentPrincipal, session: DbSession) -> Dict[str, Any]:
    try:
        dati = await collega.crea_codice(session, KeycloakAdmin(), user, principal.subject)
    except collega.ErroreCollegamento as exc:
        raise _errore(exc) from exc
    except KeycloakAdminError as exc:
        raise _keycloak_giu(exc) from exc
    await AuditRepository(session).record(
        action="collega.codice_creato", actor_id=user.id, target_type="user", target_id=str(user.id),
        after={"provider": dati["provider"], "scade_il": dati["scade_il"]}, ip=ip_client(request),
    )
    await session.commit()
    return dati


class UsaCodice(BaseModel):
    codice: str = Field(min_length=8, max_length=20)


@router.post("/usa")
async def usa_codice(
    payload: UsaCodice, request: Request, user: CurrentUser, principal: CurrentPrincipal, session: DbSession,
) -> Dict[str, Any]:
    kc = KeycloakAdmin()
    ip = ip_client(request)
    utente_id = user.id
    try:
        esito = await collega.usa_codice(session, kc, user, principal.subject, payload.codice)
    except collega.ErroreCollegamento as exc:
        await session.rollback()
        if exc.motivo == "codice_non_valido":
            # Conta per il limite dei tentativi: va salvato anche se la richiesta fallisce.
            await AuditRepository(session).record(
                action="collega.codice_errato", actor_id=utente_id, target_type="user", target_id=str(utente_id), ip=ip,
            )
            await session.commit()
        raise _errore(exc) from exc
    except KeycloakAdminError as exc:
        await session.rollback()
        raise _keycloak_giu(exc) from exc

    await AuditRepository(session).record(
        action="collega.codice_usato", actor_id=utente_id, target_type="user", target_id=str(utente_id),
        after={"provider": esito["provider"], "spostati": esito["spostati"], "da_utente": esito["donatore_id"],
               "riga_separata": esito["riga_separata"]},
        ip=ip,
    )
    await session.commit()
    problema: Optional[str] = await collega.chiudi_donatore(kc, esito["sub_donatore"])
    if problema:
        await AuditRepository(session).record(
            action="collega.chiusura_incompleta", actor_id=utente_id, target_type="user",
            target_id=str(esito["donatore_id"]), after={"errore": problema},
        )
        await session.commit()
    provider: List[str] = esito["provider"]
    return {"provider": provider, "spostati": esito["spostati"]}
