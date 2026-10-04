"""App Store (v9, Fase 4): le transazioni firmate di StoreKit 2, le Server Notifications V2, la App Store Server API.

**Tutto ciò che Apple firma è un JWS** (ES256) con la catena dei certificati nell'intestazione (`x5c`): il
certificato che firma, l'intermedio di Apple, la radice. Lo si verifica con la libreria ufficiale di Apple
(`app-store-server-library`, `SignedDataVerifier`), fino alla radice **Apple Root CA - G3** che sta accanto a questo
file (`AppleRootCA-G3.cer`, impronta SHA-256 `63343abf…3e9179`, scaricata da apple.com/certificateauthority). La
libreria controlla anche il bundle ID e, in produzione, l'Apple ID dell'app (dalla console «App mobili» → iOS). In
produzione controlla anche la revoca dei certificati presso Apple (OCSP); in sviluppo e nei test no. I test
iniettano una loro radice (`RADICI`): nessuna chiamata ad Apple.

**L'ambiente.** Un acquisto della sandbox (TestFlight, i tester, la App Review) è firmato come gli altri ma dice
`Sandbox`: si verifica con un verificatore per la sandbox e si accredita lo stesso, segnato `sandbox`.

**L'account.** L'app passa il token dell'account (`users.app_account_token`, un UUID) come `appAccountToken`
all'acquisto; Apple lo rimanda nella transazione firmata. Il resto è `comune.registra`.

**Le notifiche** (V2, un solo `signedPayload`) e la loro traduzione:

| notifica | cosa succede qui |
|---|---|
| `SUBSCRIBED`, `DID_RENEW`, `OFFER_REDEEMED`, `ONE_TIME_CHARGE` | l'incasso si registra (una volta: id `as:<transazione>`) |
| `DID_FAIL_TO_RENEW` con `GRACE_PERIOD` | `in_sospeso`: letture comprese ancora attive (Billing Grace Period) |
| `DID_FAIL_TO_RENEW` senza sottotipo, `GRACE_PERIOD_EXPIRED` | `sospeso`: Apple riprova (billing retry) |
| `EXPIRED` | `scaduto`, e il piano gratuito |
| `DID_CHANGE_RENEWAL_STATUS` | rinnovo spento o riacceso, con l'email di conferma |
| `REFUND` / `REVOKE` | storno dei crediti; il periodo in corso si chiude |
| `REFUND_REVERSED` | lo storno si annulla |
| `CONSUMPTION_REQUEST` | **ignorata**, vedi sotto |
| `TEST` | registrata come ultima notifica |

**`CONSUMPTION_REQUEST`** è Apple che, davanti a una richiesta di rimborso, chiede quanto l'utente ha usato ciò che
ha comprato. Rispondere è facoltativo; la risposta comprende dati sull'account e sull'uso, e Apple vuole che l'utente
abbia acconsentito a mandarli (`customerConsented`). Quel consenso non lo chiediamo, e mandare dati di utilizzo a un
terzo senza bisogno è contrario al principio di minimizzazione del GDPR: si risponde 200 e non si manda niente. Apple
decide il rimborso da sé, e se lo concede arriva `REFUND`.
"""
from __future__ import annotations

import base64
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote

import httpx
from sqlalchemy import distinct, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain import app_mobili_repositories as app_mobili
from ...domain.acquisti_store_models import AcquistoStore
from ...domain.base import utcnow
from ...domain.models import User
from ...settings import get_settings
from ...tarot.store_verifica import API_APPLE, jwt_apple
from .comune import (
    ErroreStore, Transazione, annulla_storno, paese_alpha2, registra, segna_notifica, storna_transazione,
)

logger = logging.getLogger(__name__)

PIATTAFORMA = "ios"
FILE_RADICE = Path(__file__).with_name("AppleRootCA-G3.cer")
#: Le radici di cui fidarsi (DER). I test le sostituiscono con la loro.
RADICI: List[bytes] = [FILE_RADICE.read_bytes()]
#: Il controllo di revoca dei certificati (OCSP) presso Apple: in produzione sì. `None` = secondo l'ambiente.
CONTROLLI_ONLINE: Optional[bool] = None

TIPI = {"Auto-Renewable Subscription": "abbonamento", "Consumable": "consumabile"}
#: `data.status` di una notifica e lo stato di un abbonamento nella App Store Server API.
STATI_APPLE = {1: "attivo", 2: "scaduto", 3: "sospeso", 4: "in_sospeso", 5: "revocato"}


def _client() -> httpx.AsyncClient:
    """Il client HTTP. I test lo sostituiscono con uno su un trasporto finto."""
    return httpx.AsyncClient(timeout=httpx.Timeout(20.0, connect=10.0))


def _ms(valore: Any) -> Optional[datetime]:
    if valore in (None, ""):
        return None
    try:
        return datetime.fromtimestamp(int(valore) / 1000, tz=timezone.utc)
    except (TypeError, ValueError, OverflowError, OSError):
        return None


# ---- la verifica dei JWS --------------------------------------------------------------------------------------------


def contenuto(jws: str) -> Dict[str, Any]:
    """Il contenuto di un JWS **senza verificarlo**: solo per sapere quale verificatore usare (l'ambiente)."""
    try:
        parte = jws.split(".")[1]
        dati = json.loads(base64.urlsafe_b64decode(parte + "=" * (-len(parte) % 4)))
    except (IndexError, ValueError, UnicodeDecodeError) as exc:
        raise ErroreStore("firma_non_valida", "Il dato firmato da Apple non si legge.", 400) from exc
    if not isinstance(dati, dict):
        raise ErroreStore("firma_non_valida", "Il dato firmato da Apple non si legge.", 400)
    return dati


def _verificatore(parametri: Dict[str, Any], ambiente: str):
    from appstoreserverlibrary.models.Environment import Environment
    from appstoreserverlibrary.signed_data_verifier import SignedDataVerifier

    bundle = parametri.get("bundle_id") or ""
    if not bundle:
        raise ErroreStore("non_configurato", "Manca il bundle ID in console → App mobili → iOS.", 503)
    if ambiente == "Sandbox":
        env = Environment.SANDBOX
    elif ambiente == "Production":
        env = Environment.PRODUCTION
    else:
        # Xcode e i test locali di StoreKit firmano con certificati propri: non sono acquisti.
        raise ErroreStore("ambiente_non_valido", f"Ambiente Apple non ammesso: {ambiente or 'sconosciuto'}.", 400)
    app_id = str(parametri.get("apple_app_id") or "")
    if env == Environment.PRODUCTION and not app_id.isdigit():
        raise ErroreStore(
            "non_configurato", "Manca l'Apple ID dell'app in console → App mobili → iOS: serve per le firme di produzione.",
            503,
        )
    online = CONTROLLI_ONLINE if CONTROLLI_ONLINE is not None else get_settings().environment == "prod"
    return SignedDataVerifier(RADICI, online, env, bundle, int(app_id) if app_id.isdigit() else None)


def _verifica(parametri: Dict[str, Any], jws: str, metodo: str, ambiente: str) -> Dict[str, Any]:
    from appstoreserverlibrary.signed_data_verifier import VerificationException, VerificationStatus

    verificatore = _verificatore(parametri, ambiente)
    try:
        getattr(verificatore, metodo)(jws)
    except VerificationException as exc:
        if exc.status == VerificationStatus.RETRYABLE_VERIFICATION_FAILURE:
            raise ErroreStore("store_non_risponde", "Il controllo dei certificati presso Apple non risponde.", 503) from exc
        if exc.status == VerificationStatus.INVALID_APP_IDENTIFIER:
            raise ErroreStore("altra_app", "Il dato firmato è di un'altra app (bundle ID o Apple ID diversi).", 400) from exc
        raise ErroreStore("firma_non_valida", f"La firma di Apple non è valida ({exc.status.name}).", 401) from exc
    # La libreria ha verificato catena, firma, bundle e ambiente dello stesso JWS: il suo contenuto è affidabile.
    return contenuto(jws)


def verifica_transazione(parametri: Dict[str, Any], jws: str) -> Dict[str, Any]:
    return _verifica(parametri, jws, "verify_and_decode_signed_transaction", str(contenuto(jws).get("environment")))


def verifica_rinnovo(parametri: Dict[str, Any], jws: str) -> Dict[str, Any]:
    return _verifica(parametri, jws, "verify_and_decode_renewal_info", str(contenuto(jws).get("environment")))


def verifica_notifica(parametri: Dict[str, Any], jws: str) -> Dict[str, Any]:
    grezzo = contenuto(jws)
    dati = grezzo.get("data") or grezzo.get("summary") or {}
    return _verifica(parametri, jws, "verify_and_decode_notification", str(dati.get("environment")))


# ---- dalla transazione di Apple alla nostra -------------------------------------------------------------------------


def da_transazione(
    tx: Dict[str, Any], rinnovo: Optional[Dict[str, Any]] = None, *, stato_apple: Optional[int] = None,
    stato: Optional[str] = None,
) -> Transazione:
    """Una `JWSTransactionDecodedPayload` (con le informazioni di rinnovo, se ci sono) come transazione.

    Lo stato dell'abbonamento: quello forzato dalla notifica (`stato`), poi `data.status` (`stato_apple`), poi quello
    che si ricava dalla transazione e dal rinnovo (in tolleranza, in billing retry, scaduto)."""
    tipo = TIPI.get(str(tx.get("type")))
    if tipo is None:
        raise ErroreStore("tipo_non_gestito", f"Prodotti «{tx.get('type')}» non in vendita nell'app.")
    adesso = utcnow()
    scade = _ms(tx.get("expiresDate"))
    prova = tx.get("offerType") == 1 and str(tx.get("offerDiscountType") or "") == "FREE_TRIAL"
    if rinnovo is not None and "autoRenewStatus" in rinnovo:
        rinnovo_automatico = rinnovo.get("autoRenewStatus") == 1
    else:
        rinnovo_automatico = True
    if tipo == "abbonamento" and stato is None:
        stato = STATI_APPLE.get(stato_apple) if stato_apple is not None else None
        if stato is None:
            grazia = _ms((rinnovo or {}).get("gracePeriodExpiresDate"))
            if tx.get("revocationDate"):
                stato = "revocato"
            elif scade is not None and scade > adesso:
                stato = "attivo"
            elif (rinnovo or {}).get("isInBillingRetryPeriod"):
                stato = "in_sospeso" if grazia is not None and grazia > adesso else "sospeso"
            else:
                stato = "scaduto"
    if stato == "attivo" and prova:
        stato = "in_prova"
    prezzo = tx.get("price")
    transazione = str(tx.get("transactionId") or "")
    if not transazione:
        raise ErroreStore("firma_non_valida", "La transazione di Apple non ha un identificativo.", 400)
    return Transazione(
        piattaforma=PIATTAFORMA, product_id=str(tx.get("productId") or ""), candidati=[str(tx.get("productId") or "")],
        tipo=tipo, transazione=transazione,
        transazione_originale=str(tx.get("originalTransactionId") or transazione) if tipo == "abbonamento" else None,
        # L'order ID è quello che l'utente vede nella ricevuta di Apple (dal 2023; prima non c'era).
        ordine=str(tx.get("webOrderLineItemId") or "") or None,
        ambiente="sandbox" if tx.get("environment") == "Sandbox" else "production",
        account=str(tx.get("appAccountToken") or "") or None,
        confermato=True,
        acquistato_il=_ms(tx.get("purchaseDate")), scade_il=scade, prova=prova,
        rinnovo_automatico=rinnovo_automatico, stato_abbonamento=stato if tipo == "abbonamento" else None,
        revocato_il=_ms(tx.get("revocationDate")),
        # `price` è in millesimi della valuta (9990 = 9,99): in centesimi è un decimo.
        importo=int(prezzo) // 10 if isinstance(prezzo, (int, float)) else None,
        valuta=str(tx.get("currency") or "")[:3] or None,
        paese=paese_alpha2(tx.get("storefront")),
        payload={"apple": {k: tx.get(k) for k in (
            "type", "transactionReason", "offerType", "offerDiscountType", "storefront", "inAppOwnershipType",
            "revocationReason", "isUpgraded",
        ) if tx.get(k) is not None}},
    )


async def _parametri(session: AsyncSession) -> Tuple[Dict[str, Any], Dict[str, str]]:
    r = await app_mobili.riga(session, PIATTAFORMA)
    return app_mobili.parametri_di(r, PIATTAFORMA), app_mobili.segreti_di(r)


# ---- verifica dall'app ---------------------------------------------------------------------------------------------


async def verifica(
    session: AsyncSession, utente: User, transazione_firmata: str, *, configurato: Any = None,
) -> Dict[str, Any]:
    """Il percorso dell'app dopo un acquisto (`Transaction.jwsRepresentation` di StoreKit 2)."""
    parametri, _ = await _parametri(session)
    tx = verifica_transazione(parametri, transazione_firmata)
    return await registra(session, da_transazione(tx), utente=utente, configurato=configurato)


# ---- le Server Notifications V2 ------------------------------------------------------------------------------------

#: Le notifiche che portano un incasso o un cambio di stato da registrare.
DA_REGISTRARE = (
    "SUBSCRIBED", "DID_RENEW", "OFFER_REDEEMED", "ONE_TIME_CHARGE", "DID_FAIL_TO_RENEW", "GRACE_PERIOD_EXPIRED",
    "EXPIRED", "DID_CHANGE_RENEWAL_STATUS", "DID_CHANGE_RENEWAL_PREF", "RENEWAL_EXTENDED", "PRICE_INCREASE",
    "RENEWAL_EXTENSION",
)


def _stato_della_notifica(tipo: str, sotto: Optional[str]) -> Optional[str]:
    if tipo == "DID_FAIL_TO_RENEW":
        return "in_sospeso" if sotto == "GRACE_PERIOD" else "sospeso"
    if tipo == "GRACE_PERIOD_EXPIRED":
        return "sospeso"
    if tipo == "EXPIRED":
        return "scaduto"
    return None


async def notifica(session: AsyncSession, payload_firmato: str) -> Dict[str, Any]:
    """Una notifica V2: verificata, tradotta, registrata. Restituisce l'esito per i log e la console."""
    parametri, _ = await _parametri(session)
    n = verifica_notifica(parametri, payload_firmato)
    tipo, sotto = str(n.get("notificationType") or ""), n.get("subtype")
    dati = n.get("data") or {}
    ambiente = "sandbox" if dati.get("environment") == "Sandbox" else "production"
    nome = f"{tipo}/{sotto}" if sotto else tipo
    tx: Optional[Dict[str, Any]] = None
    rinnovo: Optional[Dict[str, Any]] = None
    esito = "ignorata"
    try:
        if dati.get("signedTransactionInfo"):
            tx = verifica_transazione(parametri, dati["signedTransactionInfo"])
        if dati.get("signedRenewalInfo"):
            rinnovo = verifica_rinnovo(parametri, dati["signedRenewalInfo"])
        if tipo == "TEST":
            esito = "notifica di prova ricevuta"
        elif tipo == "CONSUMPTION_REQUEST":
            esito = "richiesta di consumo ignorata: non mandiamo ad Apple dati d'uso senza il consenso dell'utente"
        elif tipo in ("REFUND", "REVOKE") and tx is not None:
            esito = await storna_transazione(
                session, PIATTAFORMA, str(tx.get("transactionId")), causa="rimborso" if tipo == "REFUND" else "revoca",
                revoca=tipo == "REVOKE", quando=_ms(tx.get("revocationDate")),
            )
        elif tipo == "REFUND_REVERSED" and tx is not None:
            esito = await annulla_storno(session, PIATTAFORMA, str(tx.get("transactionId")))
        elif tipo in DA_REGISTRARE and tx is not None:
            t = da_transazione(
                tx, rinnovo, stato_apple=dati.get("status") if isinstance(dati.get("status"), int) else None,
                stato=_stato_della_notifica(tipo, sotto),
            )
            if tipo == "DID_CHANGE_RENEWAL_STATUS" and sotto in ("AUTO_RENEW_DISABLED", "AUTO_RENEW_ENABLED"):
                t.rinnovo_automatico = sotto == "AUTO_RENEW_ENABLED"
            esito = (await registra(session, t))["esito"]
    except ErroreStore as exc:
        if exc.http >= 500:
            raise
        esito = f"non registrata: {exc}"
        logger.warning("Notifica Apple %s non registrata: %s", nome, exc)
    await segna_notifica(session, PIATTAFORMA, nome, ambiente=ambiente, esito=esito)
    return {"esito": esito, "tipo": nome}


# ---- la App Store Server API (riconciliazione) ---------------------------------------------------------------------


async def _chiama(session: AsyncSession, percorso: str, *, ambiente: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    parametri, segreti = await _parametri(session)
    if not (segreti.get("chiave_p8") and parametri.get("key_id") and parametri.get("issuer_id") and parametri.get("bundle_id")):
        raise ErroreStore("non_configurato", "La App Store Server API non è configurata (chiave .p8, Key ID, Issuer ID).", 503)
    token = jwt_apple(segreti["chiave_p8"], parametri["key_id"], parametri["issuer_id"], parametri["bundle_id"])
    async with _client() as http:
        try:
            r = await http.get(f"{API_APPLE[ambiente]}{percorso}", headers={"Authorization": f"Bearer {token}"},
                               params=params)
        except httpx.HTTPError as exc:
            raise ErroreStore("store_non_risponde", f"Apple non risponde ({type(exc).__name__}).", 503) from exc
    if r.status_code == 200:
        return r.json()
    if r.status_code == 404:
        raise ErroreStore("acquisto_non_trovato", "Apple non trova questa transazione.", 404)
    raise ErroreStore("store_non_risponde", f"Apple risponde {r.status_code}.", 503)


async def storia(session: AsyncSession, transazione: str, *, ambiente: str) -> List[str]:
    """Le transazioni firmate della storia di un acquisto (`GET /inApps/v2/history/{id}`), tutte le pagine."""
    firmate: List[str] = []
    revisione: Optional[str] = None
    for _ in range(20):
        params: Dict[str, Any] = {"sort": "DESCENDING"}
        if revisione:
            params["revision"] = revisione
        dati = await _chiama(session, f"/inApps/v2/history/{quote(transazione, safe='')}", ambiente=ambiente, params=params)
        firmate.extend(dati.get("signedTransactions") or [])
        revisione = dati.get("revision")
        if not dati.get("hasMore"):
            break
    return firmate


async def stati_abbonamento(session: AsyncSession, transazione: str, *, ambiente: str) -> List[Dict[str, Any]]:
    """Lo stato di ogni abbonamento della famiglia di quella transazione (`GET /inApps/v1/subscriptions/{id}`)."""
    dati = await _chiama(session, f"/inApps/v1/subscriptions/{quote(transazione, safe='')}", ambiente=ambiente)
    voci: List[Dict[str, Any]] = []
    for gruppo in dati.get("data") or []:
        voci.extend(gruppo.get("lastTransactions") or [])
    return voci


async def riconcilia_utente(session: AsyncSession, transazione_originale: str, ambiente: str) -> Dict[str, int]:
    """Rilegge da Apple la storia di un acquisto e lo stato del suo abbonamento, e registra ciò che manca qui
    (rinnovi persi, rimborsi, revoche). Restituisce i conteggi."""
    parametri, _ = await _parametri(session)
    api = "sandbox" if ambiente == "sandbox" else "production"
    conti: Dict[str, int] = {}
    for firmata in await storia(session, transazione_originale, ambiente=api):
        try:
            esito = (await registra(session, da_transazione(verifica_transazione(parametri, firmata))))["esito"]
        except ErroreStore as exc:
            if exc.http >= 500:
                raise
            esito = f"non registrata: {exc.motivo}"
        conti[esito] = conti.get(esito, 0) + 1
    try:
        ultime = await stati_abbonamento(session, transazione_originale, ambiente=api)
    except ErroreStore as exc:
        if exc.http >= 500:
            raise
        ultime = []
    for voce in ultime:
        if not voce.get("signedTransactionInfo"):
            continue
        tx = verifica_transazione(parametri, voce["signedTransactionInfo"])
        rinnovo = verifica_rinnovo(parametri, voce["signedRenewalInfo"]) if voce.get("signedRenewalInfo") else None
        try:
            esito = (await registra(session, da_transazione(
                tx, rinnovo, stato_apple=voce.get("status") if isinstance(voce.get("status"), int) else None,
            )))["esito"]
        except ErroreStore as exc:
            if exc.http >= 500:
                raise
            esito = f"non registrata: {exc.motivo}"
        conti[esito] = conti.get(esito, 0) + 1
    return conti


async def acquisti_recenti(session: AsyncSession, dal: datetime) -> List[Tuple[str, str]]:
    """(transazione originale, ambiente) degli acquisti iOS registrati di recente: chi va riletto stanotte."""
    righe = (await session.execute(
        select(distinct(AcquistoStore.transazione_originale), AcquistoStore.ambiente)
        .where(
            AcquistoStore.piattaforma == PIATTAFORMA, AcquistoStore.created_at >= dal,
            AcquistoStore.transazione_originale.is_not(None),
        )
    )).all()
    singoli = (await session.execute(
        select(AcquistoStore.transazione, AcquistoStore.ambiente).where(
            AcquistoStore.piattaforma == PIATTAFORMA, AcquistoStore.created_at >= dal,
            AcquistoStore.transazione_originale.is_(None),
        )
    )).all()
    return [(str(o), str(a)) for o, a in righe] + [(str(t), str(a)) for t, a in singoli]
