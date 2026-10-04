"""La console: l'accesso con i social (Google, Facebook, Microsoft, Apple, GitHub, LinkedIn, X).

Per ogni provider l'operatore lo accende o lo spegne e inserisce client id e segreto: il backend li applica a
Keycloak come identity provider, via Admin API (`auth/keycloak_admin.py`). **Il segreto non si salva qui**: passa
da questa richiesta a Keycloak e basta (vedi `auth/provider_sociali.py`). Il registro di audit annota chi ha
cambiato cosa, mai il segreto.

La pagina di accesso di Keycloak mostra da sola i pulsanti dei soli provider accesi (tema `tarots`,
`social-providers.ftl`): accenderne uno qui lo fa comparire, senza ricostruire niente.

**Un account per persona.** Salvando un provider con l'email garantita (Google, Facebook, Apple, GitHub, LinkedIn)
il backend crea, se manca, il flusso che unisce gli account (`FLUSSO_UNIONE`) e glielo assegna: chi entra con quel
social e ha già un account con la stessa email ritrova il suo. `POST /admin/accesso-social/unione` fa lo stesso su
tutti i provider già presenti; `GET /admin/accesso-social/doppioni` elenca gli account dell'app con la stessa email
nati prima (da unire a mano: vedi `deploy/k8s/LEGGIMI.md`, «Account doppi»).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Request
from lanterna.rete import ip_client
from pydantic import BaseModel, Field
from sqlalchemy import func, select

from ...auth.dependencies import CurrentUser, DbSession, require_role
from ...auth.keycloak_admin import KeycloakAdmin, KeycloakAdminError
from ...auth.provider_sociali import (
    CATALOGO, FLUSSO_DOPO_ACCESSO_ESTERNO, FLUSSO_UNIONE, PER_ALIAS, ProviderSociale, con_unione, e_segnaposto,
    rappresentazione, stato,
)
from ...domain.models import Reading, User
from ...domain.repositories import AuditRepository
from ...settings import get_settings
from ...tarot import accesso_apple

router = APIRouter(prefix="/admin", tags=["accesso-social"], dependencies=[Depends(require_role("admin"))])


def _uri_reindirizzamento(alias: str) -> str:
    """L'indirizzo che il provider chiama al ritorno: quello pubblico di Keycloak (l'emittente dei token), non
    il servizio interno del cluster da cui l'API gli parla."""
    s = get_settings()
    base = (s.keycloak_issuer_url or s.keycloak_url).rstrip("/")
    return f"{base}/realms/{s.keycloak_realm}/broker/{alias}/endpoint"


def _spiega(exc: KeycloakAdminError, ruolo: str = "manage-identity-providers") -> str:
    if exc.stato == 403:
        return (
            f"{exc} — all'account di servizio di tarot-api manca un ruolo di realm-management "
            f"({ruolo}): vedi deploy/k8s/LEGGIMI.md, «Aggiornare il realm esistente»."
        )
    return str(exc)


async def _flusso_unione(kc: KeycloakAdmin) -> Tuple[Optional[str], Optional[str]]:
    """Il flusso che unisce gli account, creato se manca: `(alias, None)`, o `(None, motivo)` se Keycloak non lo
    lascia creare. Il provider si salva comunque: senza unione funziona come prima (conferma e ri-autenticazione)."""
    try:
        await kc.assicura_flusso_unione()
    except KeycloakAdminError as exc:
        return None, f"Unione automatica degli account non attiva: {_spiega(exc, 'manage-realm')}"
    return FLUSSO_UNIONE, None


def _voce(p: ProviderSociale, esistente: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "alias": p.alias,
        "nome": p.nome,
        "disponibile": p.disponibile,
        "nota": p.nota,
        "guida": p.guida,
        "console": p.console,
        "uri_reindirizzamento": _uri_reindirizzamento(p.alias),
        **stato(p, esistente),
    }


@router.get("/accesso-social")
async def elenco() -> Dict[str, Any]:
    """Il catalogo con lo stato vero, letto da Keycloak. Se Keycloak non risponde la pagina mostra comunque
    guide e indirizzi di ritorno (che non dipendono da lui), e dice perché lo stato manca."""
    errore: Optional[str] = None
    esistenti: Dict[str, Dict[str, Any]] = {}
    flusso_presente: Optional[bool] = None
    kc = KeycloakAdmin()
    try:
        esistenti = {p["alias"]: p for p in await kc.provider_identita()}
        flusso_presente = FLUSSO_UNIONE in await kc.flussi()
    except KeycloakAdminError as exc:
        errore = _spiega(exc)
    provider: List[Dict[str, Any]] = [_voce(p, esistenti.get(p.alias)) for p in CATALOGO]
    presenti = [v for v in provider if v["presente"] and v["unione_possibile"]]
    return {
        "keycloak_raggiungibile": errore is None, "errore": errore, "provider": provider,
        "unione": {
            "flusso": FLUSSO_UNIONE,
            "flusso_presente": flusso_presente,
            # Tutti i provider presenti con l'email garantita usano il flusso? Se no, la console propone di applicarlo.
            "completa": bool(flusso_presente) and all(v["unione_automatica"] for v in presenti),
        },
    }


class ProviderModifica(BaseModel):
    abilitato: bool
    client_id: str = Field(default="", max_length=500)
    #: Vuoto: si tiene il segreto che Keycloak ha già. Lungo abbastanza per il JWT di Apple.
    client_secret: str = Field(default="", max_length=4000)
    #: Chiedere anche gli ambiti sensibili (data di nascita, sesso, città). `None`: lascia com'è.
    dati_estesi: Optional[bool] = None


@router.put("/accesso-social/{alias}")
async def modifica(
    alias: str, payload: ProviderModifica, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    p = PER_ALIAS.get(alias)
    if p is None:
        raise HTTPException(status_code=404, detail="Provider sconosciuto.")
    if not p.disponibile:
        raise HTTPException(status_code=400, detail=p.nota)

    client_id = payload.client_id.strip()
    client_secret = payload.client_secret.strip()
    kc = KeycloakAdmin()
    try:
        esistente = await kc.leggi_provider(alias)
        prima = stato(p, esistente)
        if payload.abilitato:
            if e_segnaposto(client_id):
                raise HTTPException(status_code=422, detail="Per accenderlo serve il client id.")
            if not client_secret and not prima["segreto_impostato"]:
                raise HTTPException(status_code=422, detail="Per accenderlo serve il segreto.")
        if esistente is None and not client_secret:
            # Un provider nuovo, anche spento, nasce con un segreto: Keycloak lo pretende.
            raise HTTPException(status_code=422, detail="Il segreto serve alla prima configurazione.")
        # Il flusso della 2FA amministratori dopo un accesso esterno, se il realm ce l'ha (produzione): un
        # admin che entra con un social deve comunque passare dall'OTP.
        flusso = FLUSSO_DOPO_ACCESSO_ESTERNO if FLUSSO_DOPO_ACCESSO_ESTERNO in await kc.flussi() else None
        # L'unione degli account: solo per un provider con l'email garantita, e solo se il flusso c'è o si riesce
        # a crearlo.
        flusso_unione, avviso = await _flusso_unione(kc) if p.fidati_email else (None, None)
        await kc.salva_provider(
            rappresentazione(
                p, esistente, abilitato=payload.abilitato, client_id=client_id,
                client_secret=client_secret or None, flusso_dopo=flusso,
                flusso_unione=flusso_unione, dati_estesi=payload.dati_estesi,
            ),
            esiste=esistente is not None,
        )
        dopo = await kc.leggi_provider(alias)
    except KeycloakAdminError as exc:
        raise HTTPException(status_code=502, detail=f"Keycloak non ha accettato il cambio: {_spiega(exc)}") from exc

    voce = _voce(p, dopo)
    voce["avviso"] = avviso
    await AuditRepository(session).record(
        action="accesso_social.modifica", actor_id=user.id, target_type="identity_provider", target_id=alias,
        before={"abilitato": prima["abilitato"], "client_id": prima["client_id"]},
        after={
            "abilitato": voce["abilitato"], "client_id": voce["client_id"], "segreto_cambiato": bool(client_secret),
            "unione_automatica": voce["unione_automatica"], "dati_estesi": voce["dati_estesi"],
        },
        ip=ip_client(request),
    )
    await session.commit()
    return voce


@router.post("/accesso-social/unione")
async def applica_unione(request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    """Un account per persona su tutti i provider già presenti: crea il flusso che unisce gli account (se manca),
    lo assegna ai provider con l'email garantita, rimette quello standard (con conferma) agli altri, e fa conservare
    a Keycloak il token dei provider da cui si legge il profilo. Idempotente: un secondo giro non cambia niente."""
    kc = KeycloakAdmin()
    cambiati: List[str] = []
    try:
        await kc.assicura_flusso_unione()
        for esistente in await kc.provider_identita():
            p = PER_ALIAS.get(esistente.get("alias", ""))
            if p is None or not p.disponibile:
                continue
            nuova = con_unione(p, esistente, FLUSSO_UNIONE)
            if nuova is not None:
                await kc.salva_provider(nuova, esiste=True)
                cambiati.append(p.alias)
    except KeycloakAdminError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Keycloak non ha accettato il cambio: {_spiega(exc, 'manage-realm, manage-identity-providers')}",
        ) from exc
    await AuditRepository(session).record(
        action="accesso_social.unione", actor_id=user.id, target_type="realm", target_id="tarots",
        after={"flusso": FLUSSO_UNIONE, "provider": cambiati}, ip=ip_client(request),
    )
    await session.commit()
    return {"provider_aggiornati": cambiati, **(await elenco())}


# ---- Apple: il segreto firmato dal backend (v9, Fase 6) -------------------------------------------------------------


class AppleSegretoIn(BaseModel):
    team_id: Optional[str] = Field(default=None, max_length=10)
    key_id: Optional[str] = Field(default=None, max_length=10)
    services_id: Optional[str] = Field(default=None, max_length=150)
    #: Il contenuto del file .p8. `None`: resta quella di prima; stringa vuota: si toglie.
    chiave_p8: Optional[str] = Field(default=None, max_length=5_000)
    #: Accendere o spegnere «Accedi con Apple» insieme al salvataggio. `None`: com'è.
    abilitato: Optional[bool] = None


async def _vista_apple(session) -> Dict[str, Any]:
    from ...domain import app_mobili_repositories as app_mobili

    team_app = app_mobili.parametri_di(await session.get(app_mobili.ConfigAppMobile, "ios"), "ios").get("team_id") or ""
    return accesso_apple.vista(await accesso_apple.riga(session), team_id_app=team_app)


@router.get("/accesso-social/apple/segreto")
async def leggi_apple(session: DbSession) -> Dict[str, Any]:
    """Team ID, Key ID, Services ID, se la chiave c'è (e la sua impronta), quando scade il segreto in Keycloak."""
    vista = await _vista_apple(session)
    await session.commit()
    return vista


async def _applica_apple(session, abilitato: Optional[bool]) -> Dict[str, Any]:
    try:
        return await accesso_apple.applica(session, KeycloakAdmin(), abilitato=abilitato)
    except KeycloakAdminError as exc:
        await session.commit()  # l'esito negativo resta annotato
        raise HTTPException(status_code=502, detail=f"Keycloak non ha accettato il segreto: {_spiega(exc)}") from exc


@router.put("/accesso-social/apple/segreto")
async def modifica_apple(
    payload: AppleSegretoIn, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    """Salva i dati (la chiave cifrata) e, se sono completi, firma subito un segreto nuovo e lo scrive in Keycloak."""
    r = await accesso_apple.riga(session)
    prima = {"team_id": r.team_id, "key_id": r.key_id, "services_id": r.services_id, "chiave": bool(r.chiave_cifrata)}
    try:
        accesso_apple.aggiorna(r, payload.model_dump(exclude={"chiave_p8", "abilitato"}), payload.chiave_p8)
    except accesso_apple.ErroreAccessoApple as exc:
        await session.rollback()
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    r.updated_by = user.id
    applicato: Optional[Dict[str, Any]] = None
    if accesso_apple.completa(r):
        applicato = await _applica_apple(session, payload.abilitato)
    elif payload.abilitato:
        await session.rollback()
        raise HTTPException(status_code=422, detail="Per accendere Apple servono Team ID, Key ID, Services ID e la chiave .p8.")
    await AuditRepository(session).record(
        action="accesso_social.apple_segreto", actor_id=user.id, target_type="identity_provider", target_id="apple",
        before=prima,
        after={"team_id": r.team_id, "key_id": r.key_id, "services_id": r.services_id, "chiave": bool(r.chiave_cifrata),
               "chiave_cambiata": payload.chiave_p8 is not None, "scritto_in_keycloak": applicato is not None,
               "scade_il": applicato["scade_il"] if applicato else None},
        ip=ip_client(request),
    )
    await session.commit()
    return {**(await _vista_apple(session)), "applicato": applicato}


@router.post("/accesso-social/apple/segreto/rinnova")
async def rinnova_apple(request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    """Firma subito un segreto nuovo (lo fa anche il CronJob mensile, quando mancano meno di 75 giorni)."""
    r = await accesso_apple.riga(session)
    if not accesso_apple.completa(r):
        raise HTTPException(status_code=422, detail="Per firmare il segreto servono Team ID, Key ID, Services ID e la chiave .p8.")
    applicato = await _applica_apple(session, None)
    await AuditRepository(session).record(
        action="accesso_social.apple_rinnovo", actor_id=user.id, target_type="identity_provider", target_id="apple",
        after={"scade_il": applicato["scade_il"]}, ip=ip_client(request),
    )
    await session.commit()
    return {**(await _vista_apple(session)), "applicato": applicato}


@router.get("/accesso-social/doppioni")
async def doppioni(session: DbSession) -> Dict[str, Any]:
    """Gli account dell'app con la stessa email (senza badare alle maiuscole) ma `sub` di Keycloak diversi: nati
    prima dell'unione automatica, o da un provider senza email garantita. **Non si fondono da soli**: due account
    sono due storie (letture, crediti, acquisti), e decidere quale tenere spetta all'amministratore — la procedura
    è in `deploy/k8s/LEGGIMI.md`, «Account doppi»."""
    email = func.lower(User.email)
    ripetute = (await session.execute(
        select(email).where(User.email.is_not(None)).group_by(email).having(func.count() > 1).order_by(email)
    )).scalars().all()
    if not ripetute:
        return {"gruppi": []}
    letture = dict((await session.execute(
        select(Reading.owner_id, func.count()).join(User, User.id == Reading.owner_id)
        .where(email.in_(ripetute)).group_by(Reading.owner_id)
    )).all())
    utenti = (await session.execute(
        select(User).where(email.in_(ripetute)).order_by(email, User.created_at)
    )).scalars().all()
    gruppi: Dict[str, List[Dict[str, Any]]] = {}
    for u in utenti:
        gruppi.setdefault((u.email or "").lower(), []).append({
            "id": u.id, "email": u.email, "display_name": u.display_name, "keycloak_sub": u.keycloak_sub,
            "attivo": u.deleted_at is None, "creato": u.created_at.isoformat() if u.created_at else None,
            "letture": letture.get(u.id, 0),
        })
    return {"gruppi": [{"email": e, "utenti": righe} for e, righe in gruppi.items()]}
