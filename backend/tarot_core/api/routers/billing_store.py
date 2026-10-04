"""Gli acquisti nelle app (v9, Fase 4): verifica dall'app, notifiche degli store, catalogo per l'app.

| | chi chiama | come si fida |
|---|---|---|
| `POST /billing/store/google/verifica` | l'app Android dopo un acquisto | l'utente è autenticato; l'acquisto si rilegge da Google |
| `POST /billing/store/apple/verifica` | l'app iPhone dopo un acquisto | l'utente è autenticato; la transazione è firmata da Apple |
| `POST /billing/store/google/rtdn` | Pub/Sub di Google | il token OIDC del push (audience ed email dalla console) |
| `POST /billing/store/apple/notifiche` | Apple | il `signedPayload` firmato da Apple |
| `GET /billing/store/catalogo` | l'app, all'apertura dei prezzi | pubblico |

**L'ordine conta per Google**: l'accredito si scrive e si conferma nel database (commit) e **solo dopo** si conferma
l'acquisto a Google (consume o acknowledge). Al contrario, un guasto fra i due lascerebbe un acquisto confermato e
mai accreditato; così, al peggio, resta un accredito non confermato che la riconciliazione notturna conferma.

**Le notifiche rispondono 200** anche quando non c'è niente da fare (un prodotto che la console non conosce, un
account cancellato): lo store le rimanderebbe all'infinito. Rispondono 503 solo per ciò che riprovando si risolve
(lo store che non risponde), 401 per una firma o un token non validi.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Literal, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import select

from ...auth.dependencies import CurrentUser, DbSession, OptionalUser
from ...billing import abbonamenti as gestione_abbonamenti
from ...billing.credits import RegistroCrediti
from ...billing.lingue import in_lingua
from ...billing.store import app_store, google_play
from ...billing.store.comune import ErroreStore, paese_alpha2, riga_di
from ...domain import app_mobili_repositories as app_mobili
from ...domain.app_mobili_models import ProdottoStore
from ...domain.billing_models import Plan

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/billing/store", tags=["acquisti negli store"])


class VerificaGoogle(BaseModel):
    productId: str = Field(min_length=1, max_length=150)
    purchaseToken: str = Field(min_length=1, max_length=4096)


class VerificaApple(BaseModel):
    #: `Transaction.jwsRepresentation` di StoreKit 2.
    signedTransaction: str = Field(min_length=20, max_length=20000)


def _http(exc: ErroreStore) -> HTTPException:
    return HTTPException(status_code=exc.http, detail={"motivo": exc.motivo, "messaggio": str(exc)})


async def _risposta(session, user, risultato: Dict[str, Any], lang: Optional[str]) -> Dict[str, Any]:
    """Ciò che l'app mostra dopo la verifica: l'esito, l'acquisto, il saldo e l'abbonamento aggiornati."""
    abbonamento = await gestione_abbonamenti.ultimo_abbonamento(session, user.id)
    return {
        **risultato,
        "saldo": await RegistroCrediti(session).saldo(user.id),
        "abbonamento": gestione_abbonamenti.abbonamento_json(abbonamento, lang),
    }


@router.post("/google/verifica")
async def verifica_google(
    dati: VerificaGoogle, user: CurrentUser, session: DbSession,
    lang: Optional[str] = Query(default=None, pattern="^[a-z]{2}$"),
) -> Dict[str, Any]:
    """L'app Android dopo un acquisto: si rilegge l'acquisto da Google e si accredita (una volta), poi si conferma."""
    try:
        risultato = await google_play.verifica(session, user, dati.productId, dati.purchaseToken)
    except ErroreStore as exc:
        uid = user.id                     # prima del rollback, che fa scadere gli attributi
        await session.rollback()
        logger.warning("Verifica Google Play rifiutata per l'utente %s: %s", uid, exc)
        raise _http(exc) from exc
    await session.commit()
    riga = await riga_di(session, "android", risultato["acquisto"]["transazione"])
    if riga is not None and await google_play.conferma(session, riga):
        risultato["acquisto"]["confermato"] = True
        await session.commit()
    return await _risposta(session, user, risultato, lang)


@router.post("/apple/verifica")
async def verifica_apple(
    dati: VerificaApple, user: CurrentUser, session: DbSession,
    lang: Optional[str] = Query(default=None, pattern="^[a-z]{2}$"),
) -> Dict[str, Any]:
    """L'app iPhone dopo un acquisto: la transazione firmata si verifica fino alla radice di Apple e si accredita."""
    try:
        risultato = await app_store.verifica(session, user, dati.signedTransaction)
    except ErroreStore as exc:
        uid = user.id                     # prima del rollback, che fa scadere gli attributi
        await session.rollback()
        logger.warning("Verifica App Store rifiutata per l'utente %s: %s", uid, exc)
        raise _http(exc) from exc
    await session.commit()
    return await _risposta(session, user, risultato, lang)


@router.post("/google/rtdn")
async def rtdn_google(request: Request, session: DbSession) -> Dict[str, Any]:
    """Le Real-time Developer Notifications di Google Play, spinte da Pub/Sub con il token OIDC."""
    try:
        await google_play.verifica_push(session, request.headers.get("authorization"))
    except google_play.TokenNonValido as exc:
        await session.rollback()
        logger.warning("Push RTDN rifiutato: %s", exc)
        raise HTTPException(status_code=401, detail="push non autenticato") from exc
    try:
        corpo = await request.json()
        notifica, messaggio = google_play.leggi_messaggio(corpo if isinstance(corpo, dict) else {})
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="corpo illeggibile") from exc
    except ErroreStore as exc:
        raise _http(exc) from exc
    try:
        esito = await google_play.notifica(session, notifica)
    except ErroreStore as exc:
        await session.rollback()
        logger.warning("RTDN %s da riprovare: %s", messaggio, exc)
        raise _http(exc) from exc
    await session.commit()
    if esito.get("da_confermare"):
        riga = await riga_di(session, "android", esito["da_confermare"])
        if riga is not None and await google_play.conferma(session, riga):
            await session.commit()
    logger.info("RTDN %s (%s): %s", messaggio, esito.get("tipo"), esito.get("esito"))
    return {"ricevuto": messaggio, "esito": esito.get("esito")}


@router.post("/apple/notifiche")
async def notifiche_apple(request: Request, session: DbSession) -> Dict[str, Any]:
    """Le App Store Server Notifications V2: un `signedPayload` firmato da Apple."""
    try:
        corpo = await request.json()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="corpo illeggibile") from exc
    firmato = corpo.get("signedPayload") if isinstance(corpo, dict) else None
    if not isinstance(firmato, str) or not firmato:
        raise HTTPException(status_code=400, detail="signedPayload mancante")
    try:
        esito = await app_store.notifica(session, firmato)
    except ErroreStore as exc:
        await session.rollback()
        logger.warning("Notifica Apple rifiutata o da riprovare: %s", exc)
        raise _http(exc) from exc
    await session.commit()
    logger.info("Notifica Apple %s: %s", esito.get("tipo"), esito.get("esito"))
    return {"esito": esito.get("esito")}


@router.get("/catalogo")
async def catalogo(
    session: DbSession, user: OptionalUser,
    piattaforma: Literal["android", "ios"] = Query(...),
    paese_store: Optional[str] = Query(default=None, max_length=3),
    lang: Optional[str] = Query(default=None, pattern="^[a-z]{2}$"),
) -> Dict[str, Any]:
    """I prodotti in vendita nello store di quella piattaforma, con il loro piano, e il pulsante Stripe secondo la
    politica della console per il paese dello store (alpha-2 o alpha-3, come lo dà StoreKit). Senza una regola il
    pulsante è nascosto. Con l'utente autenticato c'è anche il token dell'account da passare allo store."""
    paese = paese_alpha2(paese_store)
    righe = (await session.execute(
        select(ProdottoStore, Plan).join(Plan, Plan.id == ProdottoStore.plan_id)
        .where(ProdottoStore.piattaforma == piattaforma, ProdottoStore.attivo.is_(True))
        .order_by(Plan.rank, ProdottoStore.product_id)
    )).all()
    politica = await app_mobili.risolvi_politica(session, piattaforma, paese)
    risposta = {
        "piattaforma": piattaforma,
        "paese": paese,
        "prodotti": [{
            "product_id": p.product_id.split(":", 1)[0],
            "base_plan": p.product_id.split(":", 1)[1] if ":" in p.product_id else None,
            "tipo": p.tipo,
            "annuale": p.annuale,
            "prova": p.prova,
            "piano": {
                "slug": piano.slug, "nome": in_lingua(piano.nomi, lang, piano.name),
                "descrizione": in_lingua(piano.descrizioni, lang, piano.description), "tipo": piano.tipo,
                "crediti": piano.credits_per_period, "limiti": piano.limits or {}, "livello": piano.rank,
            },
        } for p, piano in righe],
        "stripe": {
            "modalita": politica["modalita"], "avviso": politica["avviso"],
            "mostra": politica["modalita"] != "nascosto",
        },
        "app_account_token": str(user.app_account_token) if user is not None else None,
    }
    await session.commit()
    return risposta
