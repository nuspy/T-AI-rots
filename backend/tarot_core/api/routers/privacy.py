"""La privacy dell'account (GDPR, Fase 1): età minima, esportazione dei dati, cancellazione dell'account.

| cosa | endpoint |
|---|---|
| lo stato in un colpo solo (profilo, «Privacy e consensi») | `GET /me/privacy` |
| la conferma «ho almeno N anni» | `POST /me/eta` |
| l'archivio dei propri dati (ZIP di JSON, una volta al giorno) | `GET /me/esportazione` |
| la cancellazione dell'account (con riconferma), lo stato, l'annullamento | `POST /me/cancellazione`, `GET /me/cancellazione`, `POST /me/cancellazione/annulla` |

Chi ha chiesto la cancellazione ed è nei 30 giorni di ripensamento passa solo da qui (`UtenteAncheInCancellazione`):
vede la richiesta, la annulla, scarica i suoi dati. Ogni altro endpoint gli risponde 409 `account_in_cancellazione`.
"""
from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import Response
from lanterna.rete import ip_client
from pydantic import BaseModel, Field
from sqlalchemy import desc, select

from ...auth.dependencies import CurrentUser, DbSession, UtenteAncheInCancellazione
from ...domain import consent_repositories
from ...domain.base import utcnow
from ...domain.models import AuditLog, User
from ...domain.repositories import AuditRepository
from ...settings import get_settings
from ...tarot import cancellazione, esportazione
from ...tarot import eta_minima
from ...tarot.lingue import in_lingua

router = APIRouter(prefix="/me", tags=["privacy"])

#: La versione del testo della conferma dell'età: va nello storico con la conferma.
VERSIONE_ETA = "eta-v1"

ETA_DA_CONFERMARE = {
    "it": "Prima di continuare conferma di avere almeno {anni} anni.",
    "en": "Before you continue, please confirm you are at least {anni} years old.",
    "hu": "Mielőtt folytatnád, erősítsd meg, hogy legalább {anni} éves vagy.",
    "ru": "Прежде чем продолжить, подтверди, что тебе не меньше {anni} лет.",
    "uk": "Перш ніж продовжити, підтверди, що тобі щонайменше {anni} років.",
    "es": "Antes de continuar, confirma que tienes al menos {anni} años.",
}
ETA_INSUFFICIENTE = {
    "it": "TAROTS chat è riservato a chi ha almeno {anni} anni.",
    "en": "TAROTS chat is only for people aged {anni} or over.",
    "hu": "A TAROTS chat csak legalább {anni} éveseknek szól.",
    "ru": "TAROTS chat только для тех, кому исполнилось {anni} лет.",
    "uk": "TAROTS chat лише для тих, кому виповнилося {anni} років.",
    "es": "TAROTS chat es solo para personas de {anni} años o más.",
}


def _testo(testi: Dict[str, str], lang: str, anni: int) -> str:
    return in_lingua(testi, lang).replace("{anni}", str(anni))


def verifica_eta(user: User, lang: Optional[str] = None) -> None:
    """403 se la persona non ha confermato l'età minima del suo paese, o se la data di nascita dice che non la
    raggiunge. Si chiama prima di aprire una lettura o di scrivere nella chat."""
    lingua = lang or user.locale or "it"
    anni = eta_minima.anni_minimi(user.posizione_paese)
    if eta_minima.sotto_eta(user.birth_date, user.posizione_paese):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={
            "motivo": "eta_insufficiente", "anni": anni, "messaggio": _testo(ETA_INSUFFICIENTE, lingua, anni),
        })
    if eta_minima.da_confermare(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={
            "motivo": "eta_da_confermare", "anni": anni, "messaggio": _testo(ETA_DA_CONFERMARE, lingua, anni),
        })


def errore_eta_anonima(anni: int, lang: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={
        "motivo": "eta_da_confermare", "anni": anni, "messaggio": _testo(ETA_DA_CONFERMARE, lang, anni),
    })


def keycloak_admin() -> Any:
    """Il client amministrativo di Keycloak, o None se il segreto non c'è (sviluppo senza Keycloak). Una funzione del
    modulo, chiamata a ogni richiesta: i test la sostituiscono con un Keycloak finto."""
    from ...auth.keycloak_admin import KeycloakAdmin

    return KeycloakAdmin() if get_settings().keycloak_client_secret else None


async def _ultima_esportazione(session, user_id: int):
    return (await session.execute(
        select(AuditLog.created_at)
        .where(AuditLog.action == "account.esportazione", AuditLog.actor_id == user_id)
        .order_by(desc(AuditLog.created_at)).limit(1)
    )).scalar_one_or_none()


@router.get("/privacy")
async def stato_privacy(user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    """Età, esportazione e consensi, per la sezione «Privacy e consensi» del profilo."""
    ultima = await _ultima_esportazione(session, user.id)
    correnti = await consent_repositories.correnti_per(session, user_id=user.id, anon_id=None)
    return {
        "eta": eta_minima.stato_json(user),
        "esportazione": {
            "ultima_il": ultima.isoformat() if ultima else None,
            "prossima_dal": (ultima + timedelta(hours=esportazione.LIMITE_ORE)).isoformat() if ultima else None,
        },
        "consensi": {
            tipo: {"valore": c.valore, "versione": c.versione_informativa, "il": c.updated_at.isoformat() if c.updated_at else None}
            for tipo, c in correnti.items()
        },
        "cancellazione": cancellazione.stato_json(user),
    }


class ConfermaEta(BaseModel):
    #: L'età che la persona ha confermato di avere almeno (quella mostrata nella domanda).
    anni: int = Field(ge=13, le=21)
    versione_informativa: str = Field(default=VERSIONE_ETA, min_length=1, max_length=20)
    origine: str = Field(default="web", pattern="^(web|android|ios)$")


@router.post("/eta")
async def conferma_eta(payload: ConfermaEta, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    """«Ho almeno N anni». Vale se N è almeno il minimo del paese della persona, e se la data di nascita del profilo
    (quando c'è) non dice il contrario."""
    anni = eta_minima.anni_minimi(user.posizione_paese)
    if eta_minima.sotto_eta(user.birth_date, user.posizione_paese):
        raise HTTPException(status_code=403, detail={
            "motivo": "eta_insufficiente", "anni": anni, "messaggio": _testo(ETA_INSUFFICIENTE, user.locale, anni),
        })
    if payload.anni < anni:
        raise HTTPException(status_code=422, detail={
            "motivo": "eta_troppo_bassa", "anni": anni, "messaggio": _testo(ETA_DA_CONFERMARE, user.locale, anni),
        })
    user.eta_confermata_il = utcnow()
    user.eta_confermata_anni = payload.anni
    ip = ip_client(request)
    consent_repositories.annota_storico(
        session, user_id=user.id, anon_id=None, tipo="eta_minima", valore="confermato",
        versione_informativa=f"{payload.versione_informativa}:{payload.anni}"[:20], origine=payload.origine, ip=ip,
    )
    await AuditRepository(session).record(
        action="account.eta_confermata", actor_id=user.id, target_type="user", target_id=str(user.id),
        after={"anni": payload.anni, "paese": user.posizione_paese}, ip=ip,
    )
    await session.commit()
    return eta_minima.stato_json(user)


@router.get("/esportazione")
async def esporta(request: Request, user: UtenteAncheInCancellazione, session: DbSession) -> Response:
    """L'archivio ZIP dei propri dati. Una volta ogni 24 ore: prima, 429 con `Retry-After`."""
    adesso = utcnow()
    ultima = await _ultima_esportazione(session, user.id)
    if ultima is not None and adesso - ultima < timedelta(hours=esportazione.LIMITE_ORE):
        attesa = int((ultima + timedelta(hours=esportazione.LIMITE_ORE) - adesso).total_seconds()) + 1
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"motivo": "esportazione_recente", "prossima_dal": (ultima + timedelta(hours=esportazione.LIMITE_ORE)).isoformat()},
            headers={"Retry-After": str(attesa)},
        )
    dati = await esportazione.raccogli(session, user)
    corpo = esportazione.zip_di(dati, adesso)
    await AuditRepository(session).record(
        action="account.esportazione", actor_id=user.id, target_type="user", target_id=str(user.id),
        after={"file": sorted(dati), "byte": len(corpo)}, ip=ip_client(request),
    )
    await session.commit()
    nome = f"tarots-chat-dati-{adesso.date().isoformat()}.zip"
    return Response(
        content=corpo, media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{nome}"', "Cache-Control": "no-store"},
    )


class RichiestaCancellazione(BaseModel):
    #: La riconferma esplicita: il sito la manda solo dopo che la persona ha scritto la parola richiesta e premuto il
    #: secondo pulsante. Senza `true` la richiesta non parte.
    conferma: bool


@router.get("/cancellazione")
async def stato_cancellazione(user: UtenteAncheInCancellazione) -> Dict[str, Any]:
    return cancellazione.stato_json(user)


@router.post("/cancellazione")
async def chiedi_cancellazione(
    payload: RichiestaCancellazione, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    """Chiude l'account adesso; i dati si cancellano dopo 30 giorni, in cui rientrando si può annullare."""
    if not payload.conferma:
        raise HTTPException(status_code=422, detail={"motivo": "conferma_mancante"})
    esito = await cancellazione.richiedi(session, user, ip=ip_client(request), keycloak=keycloak_admin())
    await session.commit()
    return esito


@router.post("/cancellazione/annulla")
async def annulla_cancellazione(request: Request, user: UtenteAncheInCancellazione, session: DbSession) -> Dict[str, Any]:
    try:
        esito = await cancellazione.annulla(session, user, ip=ip_client(request))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail={"motivo": "nessuna_cancellazione"}) from exc
    await session.commit()
    return esito
