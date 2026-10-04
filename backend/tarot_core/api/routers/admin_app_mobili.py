"""La console «App mobili» (v9, Fase 3): account sviluppatore e pagamenti di Google Play e Apple, i prodotti degli
store collegati ai piani, la politica del pulsante Stripe, gli appunti di Codemagic; dal lato pubblico, `GET
/app/config` per le app.

I segreti (il JSON del service account per la Play Developer API, la chiave `.p8` della App Store Server API)
entrano e non escono: le risposte dicono solo se ci sono e come riconoscerli. Ogni scrittura finisce nel registro di
audit (`domain/app_mobili_repositories.py`), senza i segreti.
"""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from lanterna.rete import ip_client
from pydantic import BaseModel, Field
from sqlalchemy import select

from ...auth.dependencies import CurrentUser, DbSession, require_role
from ...domain import app_mobili_repositories as app_mobili
from ...domain.app_mobili_models import MODALITA_STRIPE
from ...domain.billing_models import Plan
from ...domain.repositories import AuditRepository
from ...tarot import store_verifica

router = APIRouter(prefix="/admin/app-mobili", tags=["app-mobili"], dependencies=[Depends(require_role("admin"))])
#: Pubblico, senza account: l'app chiede all'avvio la versione minima e i flag.
router_pubblico = APIRouter(tags=["app-mobili"])

Piattaforma = Literal["android", "ios"]


def _errore(exc: Exception) -> HTTPException:
    if isinstance(exc, LookupError):
        return HTTPException(status_code=404, detail=str(exc))
    return HTTPException(status_code=422, detail=str(exc))


async def _vista(session) -> Dict[str, Any]:
    piani = (await session.execute(select(Plan).order_by(Plan.rank, Plan.id))).scalars().all()
    return {
        "android": app_mobili.vista(await app_mobili.riga(session, "android"), "android"),
        "ios": app_mobili.vista(await app_mobili.riga(session, "ios"), "ios"),
        "codemagic": app_mobili.vista(await app_mobili.riga(session, "codemagic"), "codemagic"),
        "prodotti": await app_mobili.prodotti(session),
        "politica_stripe": await app_mobili.politiche(session),
        "piani": [{"id": p.id, "slug": p.slug, "nome": p.name, "tipo": p.tipo, "attivo": p.active,
                   "gratuito": app_mobili.gratuito(p)} for p in piani],
        "catalogo": {"modalita_stripe": list(MODALITA_STRIPE), "see": sorted(app_mobili.SEE)},
    }


@router.get("")
async def leggi(session: DbSession) -> Dict[str, Any]:
    vista = await _vista(session)
    await session.commit()
    return vista


class PagamentiIn(BaseModel):
    """Il profilo pagamenti dello store, come appunti: del conto solo le ultime 4 cifre (la validazione vera, anche
    sui testi liberi, è in `app_mobili_repositories`)."""

    id_profilo: Optional[str] = Field(default=None, max_length=40)
    beneficiario: Optional[str] = Field(default=None, max_length=200)
    tipo_profilo: Optional[Literal["individuale", "azienda"]] = None
    paese: Optional[str] = Field(default=None, max_length=2)
    valuta: Optional[str] = Field(default=None, max_length=3)
    banca: Optional[str] = Field(default=None, max_length=120)
    conto_ultime4: Optional[str] = Field(default=None, max_length=9)
    stato_fiscale: Optional[Literal["non_inviate", "inviate", "accettate"]] = None
    note: Optional[str] = Field(default=None, max_length=2000)


class ParametriAndroidIn(BaseModel):
    package_name: Optional[str] = Field(default=None, max_length=150)
    id_sviluppatore: Optional[str] = Field(default=None, max_length=30)
    email_account: Optional[str] = Field(default=None, max_length=200)
    tipo_account: Optional[Literal["personale", "organizzazione"]] = None
    test_chiuso: Optional[Literal["non_iniziato", "in_corso", "completato", "non_richiesto"]] = None
    test_chiuso_dal: Optional[date] = None
    pubsub_topic: Optional[str] = Field(default=None, max_length=300)
    rtdn_audience: Optional[str] = Field(default=None, max_length=300)
    rtdn_email: Optional[str] = Field(default=None, max_length=200)
    versione_minima: Optional[str] = Field(default=None, max_length=30)
    versione_ultima: Optional[str] = Field(default=None, max_length=30)
    commissione_ridotta: Optional[bool] = None
    #: Fase 10: le impronte SHA-256 dei certificati di firma, per `assetlinks.json` (validate nel repository).
    impronte_sha256: Optional[List[str]] = Field(default=None, max_length=20)
    note: Optional[str] = Field(default=None, max_length=2000)


class AndroidIn(BaseModel):
    parametri: Optional[ParametriAndroidIn] = None
    #: Il contenuto del file JSON del service account. `None`: resta quello di prima; stringa vuota: si toglie.
    service_account_json: Optional[str] = Field(default=None, max_length=20_000)
    pagamenti: Optional[PagamentiIn] = None


class ParametriIosIn(BaseModel):
    bundle_id: Optional[str] = Field(default=None, max_length=150)
    team_id: Optional[str] = Field(default=None, max_length=10)
    apple_app_id: Optional[str] = Field(default=None, max_length=12)
    email_account: Optional[str] = Field(default=None, max_length=200)
    tipo_account: Optional[Literal["personale", "organizzazione"]] = None
    key_id: Optional[str] = Field(default=None, max_length=10)
    issuer_id: Optional[str] = Field(default=None, max_length=36)
    ambiente: Optional[Literal["sandbox", "production"]] = None
    versione_minima: Optional[str] = Field(default=None, max_length=30)
    versione_ultima: Optional[str] = Field(default=None, max_length=30)
    ipad: Optional[bool] = None
    accordi_paid_apps: Optional[Literal["non_firmati", "in_attesa", "attivi"]] = None
    small_business: Optional[bool] = None
    note: Optional[str] = Field(default=None, max_length=2000)


class IosIn(BaseModel):
    parametri: Optional[ParametriIosIn] = None
    #: Il contenuto del file .p8. `None`: resta quella di prima; stringa vuota: si toglie.
    chiave_p8: Optional[str] = Field(default=None, max_length=5_000)
    pagamenti: Optional[PagamentiIn] = None


class CodemagicIn(BaseModel):
    team: Optional[str] = Field(default=None, max_length=120)
    app_id: Optional[str] = Field(default=None, max_length=64)
    email_account: Optional[str] = Field(default=None, max_length=200)
    chiave_asc_caricata: Optional[bool] = None
    chiave_asc_key_id: Optional[str] = Field(default=None, max_length=10)
    keystore_caricato: Optional[bool] = None
    note: Optional[str] = Field(default=None, max_length=2000)


async def _aggiorna(session, request: Request, user, piattaforma: str, *, parametri, segreto, pagamenti) -> Dict[str, Any]:
    try:
        await app_mobili.aggiorna(
            session, piattaforma,
            parametri=parametri.model_dump(exclude_unset=True, mode="json") if parametri else None,
            segreto=segreto,
            pagamenti=pagamenti.model_dump(exclude_unset=True) if pagamenti else None,
            attore_id=user.id, ip=ip_client(request),
        )
    except app_mobili.ErroreAppMobili as exc:
        await session.rollback()
        raise _errore(exc) from exc
    await session.commit()
    return await leggi(session)


@router.put("/android")
async def modifica_android(payload: AndroidIn, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    return await _aggiorna(session, request, user, "android", parametri=payload.parametri,
                           segreto=payload.service_account_json, pagamenti=payload.pagamenti)


@router.put("/ios")
async def modifica_ios(payload: IosIn, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    return await _aggiorna(session, request, user, "ios", parametri=payload.parametri,
                           segreto=payload.chiave_p8, pagamenti=payload.pagamenti)


@router.put("/codemagic")
async def modifica_codemagic(payload: CodemagicIn, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    return await _aggiorna(session, request, user, "codemagic", parametri=payload, segreto=None, pagamenti=None)


@router.post("/{piattaforma}/verifica")
async def verifica(piattaforma: Piattaforma, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    """Google: una lettura dalla Play Developer API. Apple: la notifica di prova della App Store Server API."""
    esito = await store_verifica.verifica(session, piattaforma)
    await AuditRepository(session).record(
        action=f"app_mobili.{piattaforma}.verifica", actor_id=user.id, target_type="config_app_mobili",
        target_id=piattaforma, after={"ok": bool(esito.get("ok"))},
    )
    await session.commit()
    return await leggi(session)


# ---- l'accesso dalle app (v9, Fase 6) -----------------------------------------------------------------------------


@router.post("/accesso")
async def prepara_accesso(request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    """«Prepara l'accesso dall'app»: crea in Keycloak il client `tarot-mobile` se manca (il realm in produzione è
    nato prima che esistesse). Idempotente: se c'è già non lo tocca. Vedi `KeycloakAdmin.assicura_client_mobile`."""
    from ...auth.keycloak_admin import CLIENT_MOBILE, REDIRECT_MOBILE, KeycloakAdmin, KeycloakAdminError

    try:
        creato = await KeycloakAdmin().assicura_client_mobile()
    except KeycloakAdminError as exc:
        motivo = (" — all'account di servizio di tarot-api manca il ruolo manage-realm di realm-management"
                  if exc.stato == 403 else "")
        raise HTTPException(status_code=502, detail=f"Keycloak non ha accettato: {exc}{motivo}") from exc
    await AuditRepository(session).record(
        action="app_mobili.accesso", actor_id=user.id, target_type="keycloak_client", target_id=CLIENT_MOBILE,
        after={"creato": creato}, ip=ip_client(request),
    )
    await session.commit()
    return {
        "creato": creato, "client_id": CLIENT_MOBILE, "redirect": REDIRECT_MOBILE,
        "messaggio": ("Fatto: il client dell'app è stato creato in Keycloak." if creato
                      else "Era già pronto: il client dell'app c'è già in Keycloak, non è stato toccato."),
    }


# ---- prodotti -----------------------------------------------------------------------------------------------------


class ProdottoIn(BaseModel):
    piattaforma: Piattaforma
    product_id: str = Field(min_length=1, max_length=150)
    plan_id: int
    #: Assente: si deduce dal piano (pacchetto → consumabile, abbonamento → abbonamento).
    tipo: Optional[Literal["consumabile", "abbonamento"]] = None
    #: Fase 4, solo per un abbonamento: l'annuale (altrimenti il mensile) e il prodotto «prova».
    annuale: bool = False
    prova: bool = False
    attivo: bool = True
    note: str = Field(default="", max_length=500)


class ProdottoMod(BaseModel):
    plan_id: Optional[int] = None
    annuale: Optional[bool] = None
    prova: Optional[bool] = None
    attivo: Optional[bool] = None
    note: Optional[str] = Field(default=None, max_length=500)


@router.post("/prodotti", status_code=201)
async def crea_prodotto(payload: ProdottoIn, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    try:
        await app_mobili.crea_prodotto(session, payload.model_dump(), attore_id=user.id, ip=ip_client(request))
    except app_mobili.ErroreAppMobili as exc:
        await session.rollback()
        raise _errore(exc) from exc
    await session.commit()
    return await leggi(session)


@router.put("/prodotti/{prodotto_id}")
async def modifica_prodotto(
    prodotto_id: int, payload: ProdottoMod, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    try:
        await app_mobili.modifica_prodotto(
            session, prodotto_id, payload.model_dump(exclude_unset=True), attore_id=user.id, ip=ip_client(request),
        )
    except (app_mobili.ErroreAppMobili, LookupError) as exc:
        await session.rollback()
        raise _errore(exc) from exc
    await session.commit()
    return await leggi(session)


@router.delete("/prodotti/{prodotto_id}")
async def elimina_prodotto(prodotto_id: int, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    try:
        await app_mobili.elimina_prodotto(session, prodotto_id, attore_id=user.id, ip=ip_client(request))
    except LookupError as exc:
        raise _errore(exc) from exc
    await session.commit()
    return await leggi(session)


# ---- pulsante Stripe ----------------------------------------------------------------------------------------------


class PoliticaIn(BaseModel):
    piattaforma: Piattaforma
    #: ISO 3166-1 alpha-2 o `*`.
    paese: str = Field(min_length=1, max_length=2)
    modalita: Literal["nascosto", "link_esterno", "entitlement_ue", "scelta_utente"]
    avviso: str = Field(default="", max_length=500)


@router.put("/politica-stripe")
async def imposta_politica(payload: PoliticaIn, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    try:
        await app_mobili.imposta_politica(session, payload.model_dump(), attore_id=user.id, ip=ip_client(request))
    except app_mobili.ErroreAppMobili as exc:
        await session.rollback()
        raise _errore(exc) from exc
    await session.commit()
    return await leggi(session)


@router.delete("/politica-stripe/{politica_id}")
async def elimina_politica(politica_id: int, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    try:
        await app_mobili.elimina_politica(session, politica_id, attore_id=user.id, ip=ip_client(request))
    except LookupError as exc:
        raise _errore(exc) from exc
    await session.commit()
    return await leggi(session)


# ---- per le app -----------------------------------------------------------------------------------------------------


@router_pubblico.get("/app/config")
async def config_app(
    session: DbSession, response: Response,
    piattaforma: Piattaforma = Query(...),
    versione: Optional[str] = Query(default=None, max_length=30),
    paese: Optional[str] = Query(default=None, max_length=2, description="Il paese dello store (ISO 3166-1 alpha-2)."),
) -> Dict[str, Any]:
    """Versione minima e ultima, se l'aggiornamento è obbligatorio, il link alla scheda dello store, il pulsante
    Stripe per il paese e pochi flag. Mai segreti né dati degli account."""
    try:
        dati = await app_mobili.config_pubblica(session, piattaforma, versione, paese)
    except app_mobili.ErroreAppMobili as exc:
        raise _errore(exc) from exc
    response.headers["Cache-Control"] = "public, max-age=300"
    return dati


# ---- i collegamenti verificati (Fase 10): il sito li serve in `/.well-known/` ----------------------------------------


@router_pubblico.get("/app/collegamenti/assetlinks.json")
async def asset_links(session: DbSession, response: Response) -> Any:
    """Il contenuto di `https://tarots.chat/.well-known/assetlinks.json` (lo serve il sito,
    `frontend/app/.well-known/assetlinks.json/route.ts`): package e impronte dei certificati dalla console."""
    dati = await app_mobili.asset_links(session)
    await session.commit()
    response.headers["Cache-Control"] = "public, max-age=300"
    return dati


@router_pubblico.get("/app/collegamenti/apple-app-site-association")
async def apple_app_site_association(session: DbSession, response: Response) -> Dict[str, Any]:
    """Il contenuto di `https://tarots.chat/.well-known/apple-app-site-association`: Team ID, bundle ID e percorsi."""
    dati = await app_mobili.apple_app_site_association(session)
    await session.commit()
    response.headers["Cache-Control"] = "public, max-age=300"
    return dati
