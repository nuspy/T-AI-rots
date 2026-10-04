"""Google Play (v9, Fase 4): la verifica degli acquisti con la Play Developer API e le notifiche RTDN.

**Le credenziali** sono quelle della console «App mobili» → Android: il JSON del service account (cifrato) e il
package name. Il token OAuth si ottiene con lo stesso flusso RS256 di `tarot/google.py` (`google.token`), con
l'ambito `androidpublisher`; nessuna libreria di Google.

**Un pacchetto di crediti** è un prodotto a consumo: `purchases.products.get` deve dire `purchaseState = 0`
(acquistato; `2` è in attesa — un pagamento in contanti in un negozio — e non dà niente finché non arriva) e
`obfuscatedExternalAccountId` uguale al token dell'account di chi verifica. Dopo l'accredito (e il commit) lo si
**consuma** (`:consume`, che vale anche come conferma): così si può ricomprare, e Google non lo rimborsa da sé.

**Un abbonamento** si legge con `purchases.subscriptionsv2.get`: stato, scadenza, rinnovo automatico, base plan,
fase di prova, ordine dell'ultimo incasso. Dopo il primo accredito lo si conferma (`:acknowledge`). Il purchase token
resta lo stesso per tutti i rinnovi: è l'abbonamento presso Google (qui ridotto a un'impronta, `gpt_…`, perché un
token può superare i 200 caratteri); ogni rinnovo ha il suo `orderId` (`GPA.…..0`, `..1`), che è la transazione.

**Le notifiche (RTDN)** arrivano da Pub/Sub in push, con un token OIDC firmato da Google nell'intestazione
`Authorization`: si verificano firma (chiavi pubbliche di Google), emittente, audience e l'email del service account
del push, entrambe scritte in console. Una notifica dice solo «qualcosa è cambiato in questo acquisto»: lo stato vero
si rilegge sempre dall'API, così l'ordine in cui arrivano non conta.

I test sostituiscono `_client` (un trasporto finto), `_token` e `_chiavi_google`: nessuna chiamata a Google.
"""
from __future__ import annotations

import base64
import json
import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote

import httpx
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain import app_mobili_repositories as app_mobili
from ...domain.acquisti_store_models import AcquistoStore
from ...domain.app_mobili_models import ProdottoStore
from ...domain.base import utcnow
from ...domain.models import User
from ...tarot import google
from ...tarot.store_verifica import API_ANDROIDPUBLISHER, SCOPE_ANDROIDPUBLISHER
from .comune import ErroreStore, Transazione, impronta, registra, segna_notifica, storna_transazione

logger = logging.getLogger(__name__)

PIATTAFORMA = "android"
#: Le chiavi pubbliche con cui Google firma i token OIDC (anche quelli del push di Pub/Sub).
URL_CHIAVI_GOOGLE = "https://www.googleapis.com/oauth2/v3/certs"
EMITTENTI_GOOGLE = ("accounts.google.com", "https://accounts.google.com")

#: I tipi delle notifiche degli abbonamenti (`subscriptionNotification.notificationType`), per i log e la console.
TIPI_ABBONAMENTO = {
    1: "SUBSCRIPTION_RECOVERED", 2: "SUBSCRIPTION_RENEWED", 3: "SUBSCRIPTION_CANCELED", 4: "SUBSCRIPTION_PURCHASED",
    5: "SUBSCRIPTION_ON_HOLD", 6: "SUBSCRIPTION_IN_GRACE_PERIOD", 7: "SUBSCRIPTION_RESTARTED",
    8: "SUBSCRIPTION_PRICE_CHANGE_CONFIRMED", 9: "SUBSCRIPTION_DEFERRED", 10: "SUBSCRIPTION_PAUSED",
    11: "SUBSCRIPTION_PAUSE_SCHEDULE_CHANGED", 12: "SUBSCRIPTION_REVOKED", 13: "SUBSCRIPTION_EXPIRED",
    17: "SUBSCRIPTION_ITEMS_CHANGED", 18: "SUBSCRIPTION_CANCELLATION_SCHEDULED", 19: "SUBSCRIPTION_PRICE_CHANGE_UPDATED",
    20: "SUBSCRIPTION_PENDING_PURCHASE_CANCELED",
}
TIPI_PRODOTTO = {1: "ONE_TIME_PRODUCT_PURCHASED", 2: "ONE_TIME_PRODUCT_CANCELED"}

#: Lo stato di un abbonamento presso Google (`subscriptionState`) nei nostri. `CANCELED` è il rinnovo spento: vale
#: fino alla scadenza.
STATI_GOOGLE = {
    "SUBSCRIPTION_STATE_ACTIVE": "attivo",
    "SUBSCRIPTION_STATE_CANCELED": "attivo",
    "SUBSCRIPTION_STATE_IN_GRACE_PERIOD": "in_sospeso",
    "SUBSCRIPTION_STATE_ON_HOLD": "sospeso",
    "SUBSCRIPTION_STATE_PAUSED": "sospeso",
    "SUBSCRIPTION_STATE_EXPIRED": "scaduto",
}


def _client() -> httpx.AsyncClient:
    """Il client HTTP. I test lo sostituiscono con uno su un trasporto finto."""
    return httpx.AsyncClient(timeout=httpx.Timeout(20.0, connect=10.0))


# ---- credenziali e chiamate ----------------------------------------------------------------------------------------


async def _parametri(session: AsyncSession) -> Tuple[Dict[str, Any], Dict[str, str]]:
    r = await app_mobili.riga(session, PIATTAFORMA)
    return app_mobili.parametri_di(r, PIATTAFORMA), app_mobili.segreti_di(r)


async def _token(segreti: Dict[str, str]) -> str:
    if not segreti.get("service_account"):
        raise ErroreStore(
            "non_configurato",
            "Google Play non è configurato: manca il JSON del service account in console → App mobili → Android.", 503,
        )
    cred = google.Credenziali(json.loads(segreti["service_account"]), "console")
    try:
        return await google.token(cred, SCOPE_ANDROIDPUBLISHER)
    except google.ErroreGoogle as exc:
        raise ErroreStore("credenziali", str(exc), 503) from exc


async def _chiama(session: AsyncSession, metodo: str, percorso: str, **kw: Any) -> Dict[str, Any]:
    """Una chiamata alla Play Developer API sull'app configurata. Ogni guasto diventa un `ErroreStore` con la
    risposta giusta: 404 per un acquisto che Google non conosce, 503 per ciò che si risolve riprovando."""
    parametri, segreti = await _parametri(session)
    package = parametri.get("package_name") or ""
    if not package:
        raise ErroreStore("non_configurato", "Manca il package name in console → App mobili → Android.", 503)
    t = await _token(segreti)
    url = f"{API_ANDROIDPUBLISHER}/applications/{quote(package, safe='')}{percorso}"
    async with _client() as http:
        try:
            r = await http.request(metodo, url, headers={"Authorization": f"Bearer {t}"}, **kw)
        except httpx.HTTPError as exc:
            raise ErroreStore("store_non_risponde", f"Google Play non risponde ({type(exc).__name__}).", 503) from exc
    if r.status_code in (200, 204):
        try:
            return r.json() if r.content else {}
        except ValueError:
            return {}
    _, motivo, messaggio = google._errore_api(r)
    if r.status_code in (404, 410) or motivo in ("purchaseTokenNotFound", "invalid"):
        raise ErroreStore("acquisto_non_trovato", "Google Play non riconosce questo acquisto.", 404)
    if r.status_code == 400:
        raise ErroreStore("richiesta_rifiutata", f"Google Play rifiuta la richiesta: {messaggio or motivo}", 400)
    if r.status_code in (401, 403):
        raise ErroreStore(
            "non_autorizzato",
            "Il service account non ha accesso agli ordini dell'app in Play Console (Utenti e autorizzazioni).", 503,
        )
    raise ErroreStore("store_non_risponde", f"Google Play risponde {r.status_code}: {messaggio or r.text[:200]}", 503)


# ---- dall'API alla transazione -------------------------------------------------------------------------------------


def _data(valore: Any) -> Optional[datetime]:
    """Una data di Google: RFC 3339 (`2026-10-04T10:00:00.123Z`) o millisecondi dall'epoca in una stringa."""
    if valore in (None, ""):
        return None
    testo = str(valore)
    if testo.isdigit():
        return datetime.fromtimestamp(int(testo) / 1000, tz=timezone.utc)
    try:
        quando = datetime.fromisoformat(testo.replace("Z", "+00:00"))
    except ValueError:
        return None
    return quando if quando.tzinfo else quando.replace(tzinfo=timezone.utc)


def id_abbonamento(purchase_token: str) -> str:
    """L'abbonamento presso Google, come lo si chiama qui: l'impronta del suo purchase token."""
    return f"gpt_{impronta(purchase_token)}"


def da_prodotto(dati: Dict[str, Any], product_id: str, purchase_token: str) -> Transazione:
    """Un `ProductPurchase` (pacchetto di crediti) come transazione."""
    stato = int(dati.get("purchaseState", 0) or 0)
    ordine = dati.get("orderId") or None
    return Transazione(
        piattaforma=PIATTAFORMA, product_id=product_id, candidati=[product_id], tipo="consumabile",
        # Un acquisto in attesa può non avere ancora l'ordine: allora è il token a identificarlo.
        transazione=str(ordine or f"tok_{impronta(purchase_token)}"), ordine=ordine, purchase_token=purchase_token,
        # `purchaseType` 0 è un acquisto di prova (un tester con licenza); 1 promozionale, 2 con premio.
        ambiente="sandbox" if dati.get("purchaseType") == 0 else "production",
        account=dati.get("obfuscatedExternalAccountId") or None,
        in_attesa=stato == 2, annullato=stato == 1,
        confermato=dati.get("consumptionState") == 1,
        acquistato_il=_data(dati.get("purchaseTimeMillis")),
        paese=(dati.get("regionCode") or None),
        payload={"google": {k: dati.get(k) for k in (
            "purchaseState", "consumptionState", "acknowledgementState", "purchaseType", "regionCode", "quantity",
            "orderId",
        ) if k in dati}},
    )


def da_abbonamento(dati: Dict[str, Any], purchase_token: str) -> Transazione:
    """Un `SubscriptionPurchaseV2` come transazione: l'ultimo incasso e lo stato dell'abbonamento."""
    linee = dati.get("lineItems") or [{}]
    linea = linee[0] if isinstance(linee[0], dict) else {}
    prodotto = str(linea.get("productId") or "")
    base = (linea.get("offerDetails") or {}).get("basePlanId")
    stato_google = str(dati.get("subscriptionState") or "")
    ordine = linea.get("latestSuccessfulOrderId") or dati.get("latestOrderId") or None
    scade = _data(linea.get("expiryTime"))
    prova = "freeTrial" in (linea.get("offerPhase") or {})
    stato = STATI_GOOGLE.get(stato_google)
    if stato == "attivo" and prova:
        stato = "in_prova"
    if stato in ("attivo", "in_prova") and scade is not None and scade <= utcnow():
        stato = "scaduto"
    return Transazione(
        piattaforma=PIATTAFORMA, product_id=f"{prodotto}:{base}" if base else prodotto,
        candidati=[f"{prodotto}:{base}", prodotto] if base else [prodotto], tipo="abbonamento",
        transazione=str(ordine or f"tok_{impronta(purchase_token)}"), transazione_originale=id_abbonamento(purchase_token),
        ordine=ordine, purchase_token=purchase_token,
        ambiente="sandbox" if "testPurchase" in dati else "production",
        account=(dati.get("externalAccountIdentifiers") or {}).get("obfuscatedExternalAccountId") or None,
        in_attesa=stato_google == "SUBSCRIPTION_STATE_PENDING",
        annullato=stato_google == "SUBSCRIPTION_STATE_PENDING_PURCHASE_CANCELED",
        confermato=dati.get("acknowledgementState") == "ACKNOWLEDGEMENT_STATE_ACKNOWLEDGED",
        acquistato_il=_data(dati.get("startTime")), scade_il=scade, prova=prova,
        rinnovo_automatico=bool((linea.get("autoRenewingPlan") or {}).get("autoRenewEnabled")),
        stato_abbonamento=stato, paese=dati.get("regionCode") or None,
        payload={"google": {
            "subscriptionState": stato_google, "basePlanId": base, "offerId": (linea.get("offerDetails") or {}).get("offerId"),
            "linkedPurchaseToken": bool(dati.get("linkedPurchaseToken")), "regionCode": dati.get("regionCode"),
        }},
    )


async def leggi_prodotto(session: AsyncSession, product_id: str, purchase_token: str) -> Transazione:
    dati = await _chiama(
        session, "GET", f"/purchases/products/{quote(product_id, safe='')}/tokens/{quote(purchase_token, safe='')}",
    )
    return da_prodotto(dati, product_id, purchase_token)


async def leggi_abbonamento(session: AsyncSession, purchase_token: str) -> Transazione:
    dati = await _chiama(session, "GET", f"/purchases/subscriptionsv2/tokens/{quote(purchase_token, safe='')}")
    return da_abbonamento(dati, purchase_token)


async def tipo_del_prodotto(session: AsyncSession, product_id: str) -> Optional[str]:
    """Consumabile o abbonamento, da ciò che la console sa del prodotto (per Google anche `abbonamento:base_plan`)."""
    return await session.scalar(select(ProdottoStore.tipo).where(
        ProdottoStore.piattaforma == PIATTAFORMA,
        or_(ProdottoStore.product_id == product_id, ProdottoStore.product_id.startswith(f"{product_id}:")),
    ).limit(1))


# ---- conferma a Google ---------------------------------------------------------------------------------------------


async def conferma(session: AsyncSession, riga: AcquistoStore) -> bool:
    """Consuma il pacchetto, o conferma l'abbonamento, dopo il commit dell'accredito. Mai un errore: se non riesce,
    ci riprova la riconciliazione notturna (Google rimborsa da sé ciò che resta non confermato per tre giorni)."""
    if riga.confermato or riga.stato != "accreditato" or not riga.purchase_token:
        return riga.confermato
    token = quote(riga.purchase_token, safe="")
    try:
        if riga.tipo == "consumabile":
            await _chiama(session, "POST", f"/purchases/products/{quote(riga.product_id, safe='')}/tokens/{token}:consume")
        else:
            abbonamento = riga.product_id.split(":", 1)[0]
            await _chiama(
                session, "POST", f"/purchases/subscriptions/{quote(abbonamento, safe='')}/tokens/{token}:acknowledge",
                json={},
            )
    except ErroreStore as exc:
        if exc.motivo == "richiesta_rifiutata" and "already" in str(exc).lower():
            riga.confermato = True          # già consumato o confermato (dall'app, o da un giro di prima)
            return True
        logger.warning("Conferma a Google Play non riuscita per %s: %s", riga.transazione, exc)
        return False
    riga.confermato = True
    return True


# ---- verifica dall'app ---------------------------------------------------------------------------------------------


async def verifica(
    session: AsyncSession, utente: User, product_id: str, purchase_token: str, *, configurato: Any = None,
) -> Dict[str, Any]:
    """Il percorso dell'app dopo un acquisto: rilegge l'acquisto da Google e lo registra per `utente`."""
    tipo = await tipo_del_prodotto(session, product_id)
    if tipo is None:
        raise ErroreStore(
            "prodotto_sconosciuto",
            f"Il prodotto «{product_id}» di Google Play non è collegato a nessun piano: va aggiunto in console → App "
            "mobili → Prodotti.",
        )
    t = await (leggi_prodotto(session, product_id, purchase_token) if tipo == "consumabile"
               else leggi_abbonamento(session, purchase_token))
    return await registra(session, t, utente=utente, configurato=configurato)


# ---- RTDN: il push autenticato di Pub/Sub --------------------------------------------------------------------------

_CHIAVI: Dict[str, Any] = {"jwks": None, "scade": 0.0}


async def _chiavi_google() -> Dict[str, Any]:
    """Le chiavi pubbliche di Google (JWKS), tenute per un'ora."""
    if _CHIAVI["jwks"] and _CHIAVI["scade"] > time.time():
        return _CHIAVI["jwks"]
    async with _client() as http:
        try:
            r = await http.get(URL_CHIAVI_GOOGLE)
            r.raise_for_status()
            jwks = r.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise ErroreStore("store_non_risponde", "Le chiavi di Google non si scaricano: riprova.", 503) from exc
    _CHIAVI.update(jwks=jwks, scade=time.time() + 3600)
    return jwks


class TokenNonValido(Exception):
    """Il push non viene da Pub/Sub con il service account configurato: si risponde 401."""


async def verifica_push(session: AsyncSession, autorizzazione: Optional[str]) -> Dict[str, Any]:
    """Il token OIDC del push: firma di Google, emittente, audience e email del service account del push."""
    from jose import JWTError, jwt

    parametri, _ = await _parametri(session)
    email = (parametri.get("rtdn_email") or "").lower()
    audience = parametri.get("rtdn_audience") or app_mobili.url_api(app_mobili.PERCORSO_RTDN)
    if not email:
        raise TokenNonValido("manca l'email del service account del push in console → App mobili → Android")
    if not autorizzazione or not autorizzazione.lower().startswith("bearer "):
        raise TokenNonValido("intestazione Authorization assente")
    token = autorizzazione.split(" ", 1)[1].strip()
    try:
        dati = jwt.decode(
            token, await _chiavi_google(), algorithms=["RS256"], audience=audience,
            options={"verify_iss": False, "verify_at_hash": False},
        )
    except JWTError as exc:
        raise TokenNonValido(f"token non valido: {exc}") from exc
    if dati.get("iss") not in EMITTENTI_GOOGLE:
        raise TokenNonValido("emittente sconosciuto")
    if str(dati.get("email", "")).lower() != email or not dati.get("email_verified", False):
        raise TokenNonValido("il push non viene dal service account configurato")
    return dati


def leggi_messaggio(corpo: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    """Il messaggio di Pub/Sub: (la notifica dello sviluppatore, l'id del messaggio)."""
    messaggio = corpo.get("message") or {}
    try:
        dati = json.loads(base64.b64decode(messaggio.get("data") or "").decode("utf-8") or "{}")
    except (ValueError, UnicodeDecodeError) as exc:
        raise ErroreStore("messaggio_illeggibile", "Il messaggio di Pub/Sub non si legge.", 400) from exc
    return (dati if isinstance(dati, dict) else {}), str(messaggio.get("messageId") or messaggio.get("message_id") or "")


async def notifica(session: AsyncSession, notifica_dati: Dict[str, Any]) -> Dict[str, Any]:
    """Una notifica RTDN: si rilegge l'acquisto da Google e lo si registra. Restituisce l'esito (per i log e la
    console) e la transazione da confermare a Google dopo il commit (`conferma`). Un errore che riprovando si risolve (Google che non risponde) esce come `ErroreStore` 503: Pub/Sub
    riproverà; gli altri (prodotto sconosciuto, account sconosciuto) si registrano e basta."""
    parametri, _ = await _parametri(session)
    package = notifica_dati.get("packageName")
    if package and parametri.get("package_name") and package != parametri["package_name"]:
        await segna_notifica(session, PIATTAFORMA, "altra_app", esito=f"package {package} ignorato")
        return {"esito": "notifica di un'altra app: ignorata", "tipo": "altra_app", "da_confermare": None}
    if "testNotification" in notifica_dati:
        await segna_notifica(session, PIATTAFORMA, "TEST", esito="notifica di prova ricevuta")
        return {"esito": "notifica di prova", "tipo": "TEST", "da_confermare": None}

    tipo, esito, ambiente = "sconosciuta", "ignorata", None
    da_confermare: Optional[str] = None
    try:
        if "subscriptionNotification" in notifica_dati:
            n = notifica_dati["subscriptionNotification"] or {}
            tipo = TIPI_ABBONAMENTO.get(int(n.get("notificationType") or 0), str(n.get("notificationType")))
            t = await leggi_abbonamento(session, str(n.get("purchaseToken") or ""))
            ambiente = t.ambiente
            esito = (await registra(session, t))["esito"]
            if tipo == "SUBSCRIPTION_REVOKED":
                # Revocato da Google o dalla console di Play (di solito con un rimborso): l'ultimo incasso si storna.
                esito = await storna_transazione(session, PIATTAFORMA, t.transazione, causa="revoca", revoca=True)
            da_confermare = t.transazione
        elif "oneTimeProductNotification" in notifica_dati:
            n = notifica_dati["oneTimeProductNotification"] or {}
            tipo = TIPI_PRODOTTO.get(int(n.get("notificationType") or 0), str(n.get("notificationType")))
            t = await leggi_prodotto(session, str(n.get("sku") or ""), str(n.get("purchaseToken") or ""))
            ambiente = t.ambiente
            esito = (await registra(session, t))["esito"]
            da_confermare = t.transazione
        elif "voidedPurchaseNotification" in notifica_dati:
            n = notifica_dati["voidedPurchaseNotification"] or {}
            tipo = "VOIDED_PURCHASE"
            esito = await storna_voided(session, n)
    except ErroreStore as exc:
        if exc.http >= 500:
            raise
        esito = f"non registrata: {exc}"
        logger.warning("Notifica RTDN %s non registrata: %s", tipo, exc)
    await segna_notifica(session, PIATTAFORMA, tipo, ambiente=ambiente, esito=esito)
    return {"esito": esito, "tipo": tipo, "da_confermare": da_confermare}


#: Perché Google ha annullato un acquisto (`voidedReason`): per la nota dello storno.
MOTIVI_ANNULLO = {
    0: "altro", 1: "rimorso", 2: "non ricevuto", 3: "difettoso", 4: "acquisto accidentale", 5: "frode",
    6: "amichevole", 7: "chargeback", 8: "non riconosciuto",
}


async def storna_voided(session: AsyncSession, voce: Dict[str, Any]) -> str:
    """Un acquisto annullato da Google (rimborso, chargeback, revoca): lo storno dei suoi crediti.

    La voce ha l'`orderId` (la transazione) e il purchase token; un acquisto in attesa mai pagato ha solo il token.
    """
    ordine = str(voce.get("orderId") or "")
    token = str(voce.get("purchaseToken") or "")
    transazione = ordine
    if not transazione and token:
        transazione = f"tok_{impronta(token)}"
    if not transazione:
        return "annullo senza ordine né token: ignorato"
    motivo = MOTIVI_ANNULLO.get(voce.get("voidedReason") if isinstance(voce.get("voidedReason"), int) else -1)
    causa = "chargeback" if voce.get("voidedReason") == 7 else "rimborso"
    return await storna_transazione(
        session, PIATTAFORMA, transazione, causa=f"{causa} ({motivo})" if motivo else causa,
        quando=_data(voce.get("voidedTimeMillis")),
    )


async def annullati(session: AsyncSession, dal: datetime) -> List[Dict[str, Any]]:
    """`voidedpurchases.list` dal giorno dato (abbonamenti compresi), tutte le pagine."""
    voci: List[Dict[str, Any]] = []
    prossima: Optional[str] = None
    for _ in range(50):
        parametri: Dict[str, Any] = {"startTime": str(int(dal.timestamp() * 1000)), "type": 1, "maxResults": 1000}
        if prossima:
            parametri["token"] = prossima
        dati = await _chiama(session, "GET", "/purchases/voidedpurchases", params=parametri)
        voci.extend(dati.get("voidedPurchases") or [])
        prossima = (dati.get("tokenPagination") or {}).get("nextPageToken")
        if not prossima:
            break
    return voci


def finestra_rimborsi(giorni: int = 30) -> datetime:
    """Da quando chiedere i rimborsi: Google li tiene per 30 giorni nell'elenco."""
    return utcnow() - timedelta(days=giorni)
