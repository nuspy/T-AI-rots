"""Gli acquisti negli store (v9, Fase 4): Google Play e App Store, con API finte e firme di prova.

Nessuna prova parla con Google o con Apple:

- **Google**: la Play Developer API è un trasporto finto (`GoogleFinto`, al posto di `google_play._client`), il token
  OAuth è finto, e le chiavi con cui «Google» firma il token OIDC del push di Pub/Sub sono una chiave RSA generata qui;
- **Apple**: le transazioni e le notifiche sono JWS firmati da una **CA di test** generata qui (radice, intermedio con
  l'OID di Apple, foglia con l'OID delle firme di StoreKit), iniettata al posto di Apple Root CA G3. La verifica la fa
  la libreria ufficiale di Apple, la stessa che gira in produzione (senza il controllo OCSP).
"""
from __future__ import annotations

import base64
import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import unquote

import httpx
import jwt as pyjwt
import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.x509.oid import NameOID
from sqlalchemy import func, select

from tarot_core.billing import abbonamenti as gestione
from tarot_core.billing.credits import RegistroCrediti
from tarot_core.billing.store import app_store, google_play
from tarot_core.domain import app_mobili_repositories as app_mobili
from tarot_core.domain.abbonamenti_models import InvioEmail, ProvaGratuita
from tarot_core.domain.acquisti_store_models import AcquistoStore
from tarot_core.domain.app_mobili_models import ProdottoStore
from tarot_core.domain.base import utcnow
from tarot_core.domain.billing_models import CreditEntry, PaymentCheckout, PaymentEvent, Plan, Subscription

from .conftest import richiede_database

pytestmark = richiede_database

PACKAGE = "chat.tarots.app"
BUNDLE = "chat.tarots.app"
APPLE_ID = 1234567890
EMAIL_PUSH = "pubsub-push@progetto-prova.iam.gserviceaccount.com"
AUDIENCE = "https://tarots.chat/api/billing/store/google/rtdn"


def _ms(quando: datetime) -> int:
    return int(quando.timestamp() * 1000)


def _iso(quando: datetime) -> str:
    return quando.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


# ---- la CA di test di «Apple» ---------------------------------------------------------------------------------------


def _nome(cn: str) -> x509.Name:
    return x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn), x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Prova")])


def _certificato(soggetto, chiave_pubblica, emittente, chiave_emittente, pubblica_emittente, *, ca: bool, oid=None):
    adesso = datetime.now(timezone.utc)
    costruttore = (
        x509.CertificateBuilder().subject_name(soggetto).issuer_name(emittente).public_key(chiave_pubblica)
        .serial_number(x509.random_serial_number())
        .not_valid_before(adesso - timedelta(days=1)).not_valid_after(adesso + timedelta(days=365))
        .add_extension(x509.BasicConstraints(ca=ca, path_length=None), critical=True)
        .add_extension(x509.KeyUsage(
            digital_signature=not ca, content_commitment=False, key_encipherment=False, data_encipherment=False,
            key_agreement=False, key_cert_sign=ca, crl_sign=ca, encipher_only=False, decipher_only=False,
        ), critical=True)
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(chiave_pubblica), critical=False)
        .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(pubblica_emittente), critical=False)
    )
    if oid:
        costruttore = costruttore.add_extension(x509.UnrecognizedExtension(x509.ObjectIdentifier(oid), b"\x05\x00"),
                                                critical=False)
    return costruttore.sign(chiave_emittente, hashes.SHA256())


class CATest:
    """Radice, intermedio e foglia come quelli di Apple, ma generati qui."""

    def __init__(self) -> None:
        k_radice = ec.generate_private_key(ec.SECP256R1())
        k_intermedio = ec.generate_private_key(ec.SECP256R1())
        self.k_foglia = ec.generate_private_key(ec.SECP256R1())
        radice = _certificato(_nome("Radice di prova"), k_radice.public_key(), _nome("Radice di prova"), k_radice,
                              k_radice.public_key(), ca=True)
        intermedio = _certificato(_nome("Intermedio di prova"), k_intermedio.public_key(), radice.subject, k_radice,
                                  k_radice.public_key(), ca=True, oid="1.2.840.113635.100.6.2.1")
        foglia = _certificato(_nome("Firma StoreKit di prova"), self.k_foglia.public_key(), intermedio.subject,
                              k_intermedio, k_intermedio.public_key(), ca=False, oid="1.2.840.113635.100.6.11.1")
        der = serialization.Encoding.DER
        self.radice = radice.public_bytes(der)
        self.x5c = [base64.b64encode(c.public_bytes(der)).decode() for c in (foglia, intermedio, radice)]

    def firma(self, dati: Dict[str, Any]) -> str:
        return pyjwt.encode(dati, self.k_foglia, algorithm="ES256", headers={"x5c": self.x5c})


def tx_apple(utente, *, ident: str, prodotto: str, tipo: str = "Consumable", originale: Optional[str] = None,
             ambiente: str = "Production", scade: Optional[datetime] = None, prova: bool = False,
             revocata: Optional[datetime] = None, motivo: str = "PURCHASE", account: Optional[str] = None) -> Dict[str, Any]:
    adesso = utcnow()
    dati: Dict[str, Any] = {
        "transactionId": ident, "originalTransactionId": originale or ident, "bundleId": BUNDLE,
        "productId": prodotto, "purchaseDate": _ms(adesso), "originalPurchaseDate": _ms(adesso), "quantity": 1,
        "type": tipo, "appAccountToken": account or str(utente.app_account_token), "inAppOwnershipType": "PURCHASED",
        "signedDate": _ms(adesso), "environment": ambiente, "transactionReason": motivo, "storefront": "ITA",
        "storefrontId": "143450", "price": 4990, "currency": "EUR",
    }
    if scade is not None:
        dati["expiresDate"] = _ms(scade)
    if prova:
        dati.update(offerType=1, offerDiscountType="FREE_TRIAL")
    if revocata is not None:
        dati.update(revocationDate=_ms(revocata), revocationReason=0)
    return dati


def notifica_apple(ca: CATest, tipo: str, *, sotto: Optional[str] = None, tx: Optional[Dict[str, Any]] = None,
                   rinnovo: Optional[Dict[str, Any]] = None, stato: Optional[int] = None,
                   ambiente: str = "Production") -> str:
    data: Dict[str, Any] = {"appAppleId": APPLE_ID, "bundleId": BUNDLE, "bundleVersion": "1", "environment": ambiente}
    if tx is not None:
        data["signedTransactionInfo"] = ca.firma(tx)
    if rinnovo is not None:
        data["signedRenewalInfo"] = ca.firma(rinnovo)
    if stato is not None:
        data["status"] = stato
    corpo: Dict[str, Any] = {
        "notificationType": tipo, "notificationUUID": str(uuid.uuid4()), "data": data, "version": "2.0",
        "signedDate": _ms(utcnow()),
    }
    if sotto:
        corpo["subtype"] = sotto
    return ca.firma(corpo)


def rinnovo_apple(originale: str, prodotto: str, *, attivo: bool = True) -> Dict[str, Any]:
    return {
        "originalTransactionId": originale, "autoRenewProductId": prodotto, "productId": prodotto,
        "autoRenewStatus": 1 if attivo else 0, "signedDate": _ms(utcnow()), "environment": "Production",
    }


# ---- «Google» ------------------------------------------------------------------------------------------------------


class GoogleFinto:
    """La Play Developer API: acquisti e abbonamenti per token, conferme, rimborsi."""

    def __init__(self) -> None:
        self.prodotti: Dict[str, Dict[str, Any]] = {}
        self.abbonamenti: Dict[str, Dict[str, Any]] = {}
        self.annullati: List[Dict[str, Any]] = []
        self.chiamate: List[tuple] = []

    def gestore(self, request: httpx.Request) -> httpx.Response:
        percorso = unquote(request.url.path)
        self.chiamate.append((request.method, percorso))
        assert request.headers["authorization"] == "Bearer token-finto"
        assert f"/applications/{PACKAGE}/" in percorso
        if "/purchases/products/" in percorso:
            token = percorso.split("/tokens/", 1)[1]
            if token.endswith(":consume"):
                self.prodotti[token[:-8]]["consumptionState"] = 1
                return httpx.Response(200)
            if token not in self.prodotti:
                return httpx.Response(404, json={"error": {"message": "not found"}})
            return httpx.Response(200, json=self.prodotti[token])
        if "/purchases/subscriptionsv2/tokens/" in percorso:
            token = percorso.split("/tokens/", 1)[1]
            if token not in self.abbonamenti:
                return httpx.Response(404, json={"error": {"message": "not found"}})
            return httpx.Response(200, json=self.abbonamenti[token])
        if percorso.endswith(":acknowledge"):
            token = percorso.split("/tokens/", 1)[1][:-12]
            self.abbonamenti[token]["acknowledgementState"] = "ACKNOWLEDGEMENT_STATE_ACKNOWLEDGED"
            return httpx.Response(200)
        if percorso.endswith("/purchases/voidedpurchases"):
            return httpx.Response(200, json={"voidedPurchases": self.annullati})
        return httpx.Response(404, json={"error": {"message": "sconosciuto"}})

    def contate(self, fine: str) -> int:
        return sum(1 for _, p in self.chiamate if p.endswith(fine))


def prodotto_google(utente, *, ordine: Optional[str] = "GPA.1111-2222-3333-44444", stato: int = 0, test: bool = False,
                    account: Optional[str] = None) -> Dict[str, Any]:
    dati: Dict[str, Any] = {
        "kind": "androidpublisher#productPurchase", "purchaseTimeMillis": str(_ms(utcnow())), "purchaseState": stato,
        "consumptionState": 0, "acknowledgementState": 0, "regionCode": "IT",
        "obfuscatedExternalAccountId": account or str(utente.app_account_token),
    }
    if ordine:
        dati["orderId"] = ordine
    if test:
        dati["purchaseType"] = 0
    return dati


def abbonamento_google(utente, *, ordine: str, scade: datetime, stato: str = "SUBSCRIPTION_STATE_ACTIVE",
                       base: str = "mensile", rinnovo: bool = True, prova: bool = False,
                       confermato: bool = False) -> Dict[str, Any]:
    return {
        "kind": "androidpublisher#subscriptionPurchaseV2", "regionCode": "IT", "startTime": _iso(utcnow()),
        "subscriptionState": stato,
        "acknowledgementState": "ACKNOWLEDGEMENT_STATE_ACKNOWLEDGED" if confermato else "ACKNOWLEDGEMENT_STATE_PENDING",
        "externalAccountIdentifiers": {"obfuscatedExternalAccountId": str(utente.app_account_token)},
        "lineItems": [{
            "productId": "abbonamento", "expiryTime": _iso(scade), "latestSuccessfulOrderId": ordine,
            "autoRenewingPlan": {"autoRenewEnabled": rinnovo}, "offerDetails": {"basePlanId": base},
            "offerPhase": {"freeTrial": {}} if prova else {"basePrice": {}},
        }],
    }


class FirmaGoogle:
    """La chiave con cui «Google» firma il token OIDC del push, e le sue chiavi pubbliche (JWKS)."""

    def __init__(self) -> None:
        self.chiave = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        numeri = self.chiave.public_key().public_numbers()

        def b64(n: int) -> str:
            return base64.urlsafe_b64encode(n.to_bytes((n.bit_length() + 7) // 8, "big")).rstrip(b"=").decode()

        self.jwks = {"keys": [{"kty": "RSA", "kid": "k1", "alg": "RS256", "use": "sig", "n": b64(numeri.n),
                               "e": b64(numeri.e)}]}

    def token(self, *, audience: str = AUDIENCE, email: str = EMAIL_PUSH, chiave=None) -> str:
        from jose import jwt as jose_jwt

        pem = (chiave or self.chiave).private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption(),
        ).decode()
        adesso = int(utcnow().timestamp())
        return jose_jwt.encode({
            "iss": "https://accounts.google.com", "aud": audience, "email": email, "email_verified": True,
            "sub": "1234567890", "iat": adesso, "exp": adesso + 3600,
        }, pem, algorithm="RS256", headers={"kid": "k1"})


def push(firma: FirmaGoogle, notifica: Dict[str, Any], **kw: Any) -> Dict[str, Any]:
    corpo = {
        "message": {"data": base64.b64encode(json.dumps({"version": "1.0", "packageName": PACKAGE, **notifica}).encode()).decode(),
                    "messageId": uuid.uuid4().hex},
        "subscription": "projects/progetto-prova/subscriptions/rtdn",
    }
    return {"json": corpo, "headers": {"Authorization": f"Bearer {firma.token(**kw)}"}}


# ---- attrezzatura ---------------------------------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _senza_controllo_eta(monkeypatch):
    from tarot_core.tarot import eta_minima

    monkeypatch.setattr(eta_minima, "controllo_attivo", lambda: False, raising=False)


@pytest.fixture
def posta(monkeypatch):
    """L'SMTP finto: le email «partono» in questa lista."""
    from tarot_core.posta import invio
    from tarot_core.settings import get_settings

    inviate: List[Any] = []

    def spedisci(config, messaggi):
        inviate.extend(messaggi)
        return {m["To"]: "ok" for m in messaggi}

    monkeypatch.setattr(invio, "SPEDISCI", spedisci)
    monkeypatch.setenv("TAROT_SMTP_HOST", "smtp.finto.invalid")
    monkeypatch.setenv("TAROT_SMTP_MITTENTE", "noreply@tarots.chat")
    get_settings.cache_clear()
    yield inviate
    get_settings.cache_clear()


async def _piano(session, slug: str) -> Plan:
    return (await session.execute(select(Plan).where(Plan.slug == slug))).scalar_one()


@pytest.fixture
async def prodotti(session, catalogo):
    """I prodotti degli store collegati ai piani del seed, come li scriverebbe la console."""
    voci = [
        ("android", "crediti_5", "pacchetto-5", "consumabile", False, False),
        ("android", "abbonamento:mensile", "mensile-base", "abbonamento", False, False),
        ("android", "abbonamento:annuale-prova", "mensile-oro", "abbonamento", True, True),
        ("ios", "chat.tarots.crediti5", "pacchetto-5", "consumabile", False, False),
        ("ios", "chat.tarots.base.mese", "mensile-base", "abbonamento", False, False),
        ("ios", "chat.tarots.oro.prova", "mensile-oro", "abbonamento", True, True),
    ]
    for piattaforma, product_id, slug, tipo, annuale, prova in voci:
        session.add(ProdottoStore(piattaforma=piattaforma, product_id=product_id, plan_id=(await _piano(session, slug)).id,
                                  tipo=tipo, annuale=annuale, prova=prova))
    await app_mobili.aggiorna(session, "android", parametri={"rtdn_email": EMAIL_PUSH, "rtdn_audience": AUDIENCE},
                              attore_id=None)
    await app_mobili.aggiorna(session, "ios", parametri={"apple_app_id": str(APPLE_ID)}, attore_id=None)
    await session.commit()


@pytest.fixture
def google(monkeypatch):
    finto = GoogleFinto()

    async def token(segreti):
        return "token-finto"

    monkeypatch.setattr(google_play, "_client", lambda: httpx.AsyncClient(transport=httpx.MockTransport(finto.gestore)))
    monkeypatch.setattr(google_play, "_token", token)
    return finto


@pytest.fixture
def firma_google(monkeypatch):
    firma = FirmaGoogle()

    async def chiavi():
        return firma.jwks

    monkeypatch.setattr(google_play, "_chiavi_google", chiavi)
    return firma


@pytest.fixture
def apple(monkeypatch):
    ca = CATest()
    monkeypatch.setattr(app_store, "RADICI", [ca.radice])
    monkeypatch.setattr(app_store, "CONTROLLI_ONLINE", False)
    return ca


async def _abbonamento_store(session, user_id: int) -> Optional[Subscription]:
    """L'abbonamento dello store com'è nel database adesso (l'API scrive con un'altra sessione). `populate_existing` e
    non `expire_all`: quello farebbe scadere anche l'utente della prova, che poi non si rilegge fuori da un await."""
    return (await session.execute(
        select(Subscription).where(Subscription.user_id == user_id, Subscription.provider.in_(("google_play", "app_store")))
        .order_by(Subscription.created_at.desc()).limit(1).execution_options(populate_existing=True)
    )).scalar_one_or_none()


async def _saldo(session, user_id: int) -> int:
    return await RegistroCrediti(session).saldo(user_id)


async def _email(session, tipo: str) -> int:
    return int(await session.scalar(select(func.count()).select_from(InvioEmail).where(InvioEmail.tipo == tipo)) or 0)


def _vicine(a: datetime, b: datetime) -> bool:
    return abs((a - b).total_seconds()) < 2


# ---- Google: pacchetti ------------------------------------------------------------------------------------------------


async def test_google_pacchetto_accreditato_una_volta_fra_verifica_e_notifica(
    client, session, utente, prodotti, google, firma_google,
):
    google.prodotti["tokA"] = prodotto_google(utente)
    r = await client.post("/billing/store/google/verifica", json={"productId": "crediti_5", "purchaseToken": "tokA"})
    assert r.status_code == 200, r.text
    corpo = r.json()
    assert corpo["saldo"] == 5 and corpo["esito"] == "crediti accreditati"
    assert corpo["acquisto"]["stato"] == "accreditato" and corpo["acquisto"]["confermato"] is True
    assert google.contate("tokA:consume") == 1

    # La stessa verifica di nuovo (l'app che riprova) e la notifica dello stesso acquisto: niente di nuovo.
    r = await client.post("/billing/store/google/verifica", json={"productId": "crediti_5", "purchaseToken": "tokA"})
    assert r.status_code == 200 and r.json()["saldo"] == 5
    r = await client.post("/billing/store/google/rtdn", **push(firma_google, {
        "oneTimeProductNotification": {"version": "1.0", "notificationType": 1, "purchaseToken": "tokA", "sku": "crediti_5"},
    }))
    assert r.status_code == 200, r.text
    assert await _saldo(session, utente.id) == 5
    assert google.contate("tokA:consume") == 1

    righe = (await session.execute(select(AcquistoStore))).scalars().all()
    assert len(righe) == 1 and righe[0].transazione == "GPA.1111-2222-3333-44444" and righe[0].confermato
    voce = (await session.execute(select(CreditEntry).where(CreditEntry.reason == "acquisto"))).scalar_one()
    assert (voce.provider, voce.canale, voce.acquisto_id) == ("google_play", "android", righe[0].id)
    checkout = (await session.execute(select(PaymentCheckout))).scalar_one()
    assert (checkout.provider, checkout.status, checkout.importo, checkout.sandbox) == ("google_play", "pagato", 490, False)
    assert await session.get(PaymentEvent, "gp:GPA.1111-2222-3333-44444") is not None

    # La console vede la notifica arrivata.
    riga = await app_mobili.riga(session, "android")
    await session.refresh(riga)
    assert riga.ultima_notifica["tipo"] == "ONE_TIME_PRODUCT_PURCHASED" and riga.ultima_notifica_il is not None


async def test_google_token_di_un_altro_account_rifiutato(client, session, utente, altro_utente, prodotti, google):
    google.prodotti["tokB"] = prodotto_google(altro_utente, ordine="GPA.2")
    r = await client.post("/billing/store/google/verifica", json={"productId": "crediti_5", "purchaseToken": "tokB"})
    assert r.status_code == 403 and r.json()["detail"]["motivo"] == "account_diverso"
    assert await _saldo(session, utente.id) == 0 and await _saldo(session, altro_utente.id) == 0
    assert (await session.execute(select(AcquistoStore))).first() is None
    assert google.contate("tokB:consume") == 0


async def test_google_acquisto_in_attesa_senza_credito_poi_pagato(client, session, utente, prodotti, google, firma_google):
    google.prodotti["tokC"] = prodotto_google(utente, ordine=None, stato=2)
    r = await client.post("/billing/store/google/verifica", json={"productId": "crediti_5", "purchaseToken": "tokC"})
    assert r.status_code == 200, r.text
    assert r.json()["acquisto"]["stato"] == "in_attesa" and r.json()["saldo"] == 0
    assert google.contate("tokC:consume") == 0

    # Il pagamento in contanti arriva: Google lo dice con la notifica, e la riga in attesa prende l'ordine.
    google.prodotti["tokC"] = prodotto_google(utente, ordine="GPA.3", stato=0)
    r = await client.post("/billing/store/google/rtdn", **push(firma_google, {
        "oneTimeProductNotification": {"notificationType": 1, "purchaseToken": "tokC", "sku": "crediti_5"},
    }))
    assert r.status_code == 200, r.text
    assert await _saldo(session, utente.id) == 5
    riga = (await session.execute(select(AcquistoStore))).scalar_one()
    assert (riga.transazione, riga.stato, riga.confermato) == ("GPA.3", "accreditato", True)


async def test_rtdn_con_token_non_valido_401(client, session, prodotti, google, firma_google):
    notifica = {"testNotification": {"version": "1.0"}}
    assert (await client.post("/billing/store/google/rtdn", json=push(firma_google, notifica)["json"])).status_code == 401
    for kw in ({"audience": "https://altro.example/rtdn"}, {"email": "intruso@altro.iam.gserviceaccount.com"},
               {"chiave": rsa.generate_private_key(public_exponent=65537, key_size=2048)}):
        r = await client.post("/billing/store/google/rtdn", **push(firma_google, notifica, **kw))
        assert r.status_code == 401, kw
    r = await client.post("/billing/store/google/rtdn", **push(firma_google, notifica))
    assert r.status_code == 200 and r.json()["esito"] == "notifica di prova"


# ---- Google: abbonamenti --------------------------------------------------------------------------------------------


async def test_google_ciclo_dell_abbonamento(client, session, utente, prodotti, google, firma_google, posta):
    adesso = utcnow()
    google.abbonamenti["sub1"] = abbonamento_google(utente, ordine="GPA.5", scade=adesso + timedelta(days=30))
    r = await client.post("/billing/store/google/verifica", json={"productId": "abbonamento", "purchaseToken": "sub1"})
    assert r.status_code == 200, r.text
    assert r.json()["esito"] == "abbonamento attivato"
    profilo = r.json()["abbonamento"]
    assert profilo["store"] is True and profilo["provider"] == "google_play"
    assert profilo["gestione_store"].startswith("https://play.google.com/")
    a = await _abbonamento_store(session, utente.id)
    assert (a.status, a.plan.slug, a.annuale) == ("attivo", "mensile-base", False)
    assert _vicine(a.period_end, adesso + timedelta(days=30))
    assert google.contate("sub1:acknowledge") == 1

    async def notifica(tipo: int):
        r = await client.post("/billing/store/google/rtdn", **push(firma_google, {
            "subscriptionNotification": {"notificationType": tipo, "purchaseToken": "sub1", "subscriptionId": "abbonamento"},
        }))
        assert r.status_code == 200, r.text
        return await _abbonamento_store(session, utente.id)

    # Rinnovato: un ordine nuovo, la scadenza un mese più in là.
    google.abbonamenti["sub1"] = abbonamento_google(utente, ordine="GPA.5..0", scade=adesso + timedelta(days=60),
                                                    confermato=True)
    a = await notifica(2)
    assert a.status == "attivo" and _vicine(a.period_end, adesso + timedelta(days=60))
    assert len((await session.execute(select(AcquistoStore))).scalars().all()) == 2

    # Il pagamento del rinnovo dopo non riesce: grace period (letture ancora attive), poi account hold.
    google.abbonamenti["sub1"] = abbonamento_google(utente, ordine="GPA.5..0", scade=adesso + timedelta(days=63),
                                                    stato="SUBSCRIPTION_STATE_IN_GRACE_PERIOD", confermato=True)
    a = await notifica(6)
    assert a.status == "in_sospeso" and a.vivo and a.pagamento_fallito_il is not None
    google.abbonamenti["sub1"] = abbonamento_google(utente, ordine="GPA.5..0", scade=adesso - timedelta(days=1),
                                                    stato="SUBSCRIPTION_STATE_ON_HOLD", confermato=True)
    a = await notifica(5)
    assert a.status == "sospeso" and not a.vivo
    # Niente solleciti nostri: li manda lo store.
    assert await _email(session, "pagamento_fallito") == 0

    # Il pagamento arriva (RECOVERED): un ordine nuovo, di nuovo attivo.
    google.abbonamenti["sub1"] = abbonamento_google(utente, ordine="GPA.5..1", scade=adesso + timedelta(days=90),
                                                    confermato=True)
    a = await notifica(1)
    assert a.status == "attivo" and a.pagamento_fallito_il is None and a.cancel_at is None

    # Disdetta nello store: il rinnovo si spegne, l'email di conferma parte una volta sola.
    google.abbonamenti["sub1"] = abbonamento_google(utente, ordine="GPA.5..1", scade=adesso + timedelta(days=90),
                                                    stato="SUBSCRIPTION_STATE_CANCELED", rinnovo=False, confermato=True)
    a = await notifica(3)
    assert a.status == "attivo" and a.cancel_at is not None
    await notifica(3)
    assert await _email(session, "rinnovo_spento") == 1 and len(posta) == 1

    # Scaduto: il piano gratuito torna.
    google.abbonamenti["sub1"] = abbonamento_google(utente, ordine="GPA.5..1", scade=adesso - timedelta(minutes=1),
                                                    stato="SUBSCRIPTION_STATE_EXPIRED", rinnovo=False, confermato=True)
    a = await notifica(13)
    assert a.status == "scaduto"
    vivo = await gestione.ultimo_abbonamento(session, utente.id)
    assert vivo is not None and vivo.plan.slug == "free"
    assert (await session.execute(select(AcquistoStore).where(AcquistoStore.transazione == "GPA.5..1"))).scalar_one().stato == "scaduto"


async def test_un_solo_abbonamento_qualunque_sia_il_canale(client, session, utente, prodotti, google):
    from tarot_core.billing.pagamenti import PagamentiSimulati
    from tarot_core.billing.plans import GestoreAbbonamenti

    oro = await _piano(session, "mensile-oro")
    sito = await GestoreAbbonamenti(session, PagamentiSimulati()).sottoscrivi(utente.id, oro, fornitore="mock",
                                                                               external_id="mock_sub_1")
    await session.commit()
    google.abbonamenti["sub2"] = abbonamento_google(utente, ordine="GPA.6", scade=utcnow() + timedelta(days=30))
    r = await client.post("/billing/store/google/verifica", json={"productId": "abbonamento", "purchaseToken": "sub2"})
    assert r.status_code == 200, r.text
    vecchio = await session.get(Subscription, sito.id, populate_existing=True)
    assert vecchio.status == "disdetto"
    vivi = (await session.execute(select(Subscription).where(
        Subscription.user_id == utente.id, Subscription.status.in_(("attivo", "in_prova", "in_sospeso"))))).scalars().all()
    assert [v.provider for v in vivi] == ["google_play"]


# ---- Apple ----------------------------------------------------------------------------------------------------------


async def test_apple_pacchetto_rimborso_e_rimborso_annullato(client, session, utente, prodotti, apple):
    tx = tx_apple(utente, ident="2000000001", prodotto="chat.tarots.crediti5")
    r = await client.post("/billing/store/apple/verifica", json={"signedTransaction": apple.firma(tx)})
    assert r.status_code == 200, r.text
    assert r.json()["saldo"] == 5
    riga = (await session.execute(select(AcquistoStore))).scalar_one()
    assert (riga.importo, riga.valuta, riga.paese, riga.ambiente) == (499, "EUR", "IT", "production")

    # La stessa transazione dalla notifica (ONE_TIME_CHARGE): niente di nuovo.
    corpo = {"signedPayload": notifica_apple(apple, "ONE_TIME_CHARGE", tx=tx)}
    assert (await client.post("/billing/store/apple/notifiche", json=corpo)).status_code == 200
    assert await _saldo(session, utente.id) == 5

    # I crediti si spendono, poi Apple rimborsa: lo storno porta il saldo sotto zero.
    await RegistroCrediti(session).consuma(utente.id, 3)
    await session.commit()
    rimborsata = {**tx, "revocationDate": _ms(utcnow()), "revocationReason": 0}
    r = await client.post("/billing/store/apple/notifiche", json={"signedPayload": notifica_apple(apple, "REFUND", tx=rimborsata)})
    assert r.status_code == 200 and r.json()["esito"] == "crediti stornati"
    assert await _saldo(session, utente.id) == -3
    # La stessa notifica rimandata da Apple: lo storno non si ripete.
    await client.post("/billing/store/apple/notifiche", json={"signedPayload": notifica_apple(apple, "REFUND", tx=rimborsata)})
    assert await _saldo(session, utente.id) == -3
    assert (await session.execute(select(AcquistoStore).execution_options(populate_existing=True))).scalar_one().stato == "rimborsato"

    r = await client.post("/billing/store/apple/notifiche",
                          json={"signedPayload": notifica_apple(apple, "REFUND_REVERSED", tx=rimborsata)})
    assert r.status_code == 200 and await _saldo(session, utente.id) == 2


async def test_apple_firma_di_un_altra_radice_rifiutata(client, session, utente, prodotti, apple):
    estranea = CATest()
    tx = tx_apple(utente, ident="2000000002", prodotto="chat.tarots.crediti5")
    r = await client.post("/billing/store/apple/verifica", json={"signedTransaction": estranea.firma(tx)})
    assert r.status_code == 401 and r.json()["detail"]["motivo"] == "firma_non_valida"
    r = await client.post("/billing/store/apple/notifiche", json={"signedPayload": notifica_apple(estranea, "TEST")})
    assert r.status_code == 401
    # Un'altra app (bundle diverso), firmata bene: rifiutata.
    altra = {**tx, "bundleId": "com.altra.app"}
    r = await client.post("/billing/store/apple/verifica", json={"signedTransaction": apple.firma(altra)})
    assert r.status_code == 400 and r.json()["detail"]["motivo"] == "altra_app"
    # Il token dell'account di un altro: rifiutato.
    r = await client.post("/billing/store/apple/verifica", json={"signedTransaction": apple.firma(
        tx_apple(utente, ident="2000000003", prodotto="chat.tarots.crediti5", account=str(uuid.uuid4())))})
    assert r.status_code == 403
    assert await _saldo(session, utente.id) == 0


async def test_apple_ciclo_dell_abbonamento_dalle_notifiche(client, session, utente, prodotti, apple, posta):
    adesso = utcnow()
    prodotto = "chat.tarots.base.mese"
    abb = "Auto-Renewable Subscription"

    async def manda(tipo, tx, *, sotto=None, stato=None, rinnovo=None):
        r = await client.post("/billing/store/apple/notifiche", json={"signedPayload": notifica_apple(
            apple, tipo, sotto=sotto, tx=tx, stato=stato, rinnovo=rinnovo)})
        assert r.status_code == 200, r.text
        return await _abbonamento_store(session, utente.id)

    primo = tx_apple(utente, ident="3000000001", prodotto=prodotto, tipo=abb, scade=adesso + timedelta(days=30))
    a = await manda("SUBSCRIBED", primo, sotto="INITIAL_BUY", stato=1)
    assert (a.status, a.provider, a.external_id) == ("attivo", "app_store", "3000000001")

    secondo = tx_apple(utente, ident="3000000002", originale="3000000001", prodotto=prodotto, tipo=abb,
                       scade=adesso + timedelta(days=60), motivo="RENEWAL")
    a = await manda("DID_RENEW", secondo, stato=1)
    assert a.status == "attivo" and _vicine(a.period_end, adesso + timedelta(days=60))

    a = await manda("DID_FAIL_TO_RENEW", secondo, sotto="GRACE_PERIOD", stato=4)
    assert a.status == "in_sospeso" and a.vivo
    a = await manda("GRACE_PERIOD_EXPIRED", secondo, stato=3)
    assert a.status == "sospeso"

    terzo = tx_apple(utente, ident="3000000003", originale="3000000001", prodotto=prodotto, tipo=abb,
                     scade=adesso + timedelta(days=90), motivo="RENEWAL")
    a = await manda("DID_RENEW", terzo, sotto="BILLING_RECOVERY", stato=1)
    assert a.status == "attivo" and a.pagamento_fallito_il is None

    a = await manda("DID_CHANGE_RENEWAL_STATUS", terzo, sotto="AUTO_RENEW_DISABLED", stato=1,
                    rinnovo=rinnovo_apple("3000000001", prodotto, attivo=False))
    assert a.cancel_at is not None and await _email(session, "rinnovo_spento") == 1
    a = await manda("DID_CHANGE_RENEWAL_STATUS", terzo, sotto="AUTO_RENEW_ENABLED", stato=1,
                    rinnovo=rinnovo_apple("3000000001", prodotto))
    assert a.cancel_at is None and await _email(session, "rinnovo_riacceso") == 1

    a = await manda("EXPIRED", terzo, sotto="VOLUNTARY", stato=2)
    assert a.status == "scaduto"
    # Le richieste di consumo si ignorano (motivato in `app_store.py`), e la prova di Apple si registra.
    r = await client.post("/billing/store/apple/notifiche",
                          json={"signedPayload": notifica_apple(apple, "CONSUMPTION_REQUEST", tx=terzo)})
    assert r.status_code == 200 and r.json()["esito"].startswith("richiesta di consumo ignorata")


async def test_apple_rimborso_dell_abbonamento_lo_chiude(client, session, utente, prodotti, apple):
    tx = tx_apple(utente, ident="4000000001", prodotto="chat.tarots.base.mese", tipo="Auto-Renewable Subscription",
                  scade=utcnow() + timedelta(days=30))
    assert (await client.post("/billing/store/apple/verifica", json={"signedTransaction": apple.firma(tx)})).status_code == 200
    rimborsata = {**tx, "revocationDate": _ms(utcnow()), "revocationReason": 1}
    r = await client.post("/billing/store/apple/notifiche", json={"signedPayload": notifica_apple(apple, "REFUND", tx=rimborsata)})
    assert r.status_code == 200, r.text
    a = await _abbonamento_store(session, utente.id)
    assert a.status == "disdetto"
    assert (await session.execute(select(AcquistoStore))).scalar_one().stato == "rimborsato"


async def test_sandbox_accreditato_ma_fuori_dai_ricavi(client, session, utente, prodotti, apple, principal_admin):
    tx = tx_apple(utente, ident="5000000001", prodotto="chat.tarots.crediti5", ambiente="Sandbox")
    r = await client.post("/billing/store/apple/verifica", json={"signedTransaction": apple.firma(tx)})
    assert r.status_code == 200, r.text
    assert r.json()["saldo"] == 5 and r.json()["acquisto"]["ambiente"] == "sandbox"
    checkout = (await session.execute(select(PaymentCheckout))).scalar_one()
    assert checkout.sandbox is True and checkout.status == "pagato"

    client.identita.principal = principal_admin
    r = await client.get("/admin/payments")
    assert r.status_code == 200 and r.json()["incassato"] == 0
    assert r.json()["pagamenti"][0]["sandbox"] is True
    scheda = (await client.get(f"/admin/users/{utente.id}")).json()
    assert [a["ambiente"] for a in scheda["acquisti_store"]] == ["sandbox"]


async def test_prova_dello_store_e_promemoria(client, session, utente, prodotti, apple, posta):
    from tarot_core.billing.abbonamenti import giro_promemoria_prova

    tx = tx_apple(utente, ident="6000000001", prodotto="chat.tarots.oro.prova", tipo="Auto-Renewable Subscription",
                  scade=utcnow() + timedelta(days=1, hours=12), prova=True)
    r = await client.post("/billing/store/apple/verifica", json={"signedTransaction": apple.firma(tx)})
    assert r.status_code == 200, r.text
    assert r.json()["esito"] == "prova attivata"
    a = await _abbonamento_store(session, utente.id)
    assert (a.status, a.prova, a.annuale, a.plan.slug) == ("in_prova", True, True, "mensile-oro")
    # L'annuale «prova» costa la metà, per sempre: 199 € → 99,50 €.
    assert gestione.prossimo_rinnovo(a) == 9950
    assert (await session.execute(select(ProvaGratuita).where(ProvaGratuita.user_id == utente.id))).scalar_one().provider == "app_store"
    checkout = (await session.execute(select(PaymentCheckout))).scalar_one()
    assert checkout.importo == 0 and checkout.prova

    assert await giro_promemoria_prova(session) == 1
    await session.commit()
    assert await giro_promemoria_prova(session) == 0
    assert await _email(session, "promemoria_prova") == 1


async def test_google_prova_anche_se_il_sito_l_aveva_gia_data(client, session, utente, prodotti, google):
    """L'idoneità alla prova la decide lo store: una prova di Google dopo quella del sito non si rifiuta (lo store
    addebiterebbe comunque alla fine), e la riga della prova resta una."""
    session.add(ProvaGratuita(user_id=utente.id, provider="stripe"))
    await session.commit()
    google.abbonamenti["sub3"] = abbonamento_google(utente, ordine="GPA.7", scade=utcnow() + timedelta(days=14),
                                                    base="annuale-prova", prova=True)
    r = await client.post("/billing/store/google/verifica", json={"productId": "abbonamento", "purchaseToken": "sub3"})
    assert r.status_code == 200 and r.json()["esito"] == "prova attivata", r.text
    a = await _abbonamento_store(session, utente.id)
    assert (a.status, a.plan.slug, a.annuale) == ("in_prova", "mensile-oro", True)
    assert len((await session.execute(select(ProvaGratuita))).scalars().all()) == 1


# ---- catalogo -------------------------------------------------------------------------------------------------------


async def test_catalogo_con_la_politica_stripe_per_paese(client, session, utente, prodotti):
    await app_mobili.imposta_politica(session, {"piattaforma": "ios", "paese": "US", "modalita": "link_esterno",
                                                "avviso": "Acquisto fuori dall'App Store"}, attore_id=None)
    await app_mobili.imposta_politica(session, {"piattaforma": "ios", "paese": "IT", "modalita": "entitlement_ue"},
                                      attore_id=None)
    await session.commit()

    r = await client.get("/billing/store/catalogo", params={"piattaforma": "ios", "paese_store": "USA", "lang": "it"})
    assert r.status_code == 200, r.text
    corpo = r.json()
    assert corpo["paese"] == "US" and corpo["stripe"] == {"modalita": "link_esterno", "avviso": "Acquisto fuori dall'App Store",
                                                          "mostra": True}
    assert {p["product_id"] for p in corpo["prodotti"]} == {"chat.tarots.crediti5", "chat.tarots.base.mese", "chat.tarots.oro.prova"}
    assert corpo["app_account_token"] == str(utente.app_account_token)
    prova = next(p for p in corpo["prodotti"] if p["prova"])
    assert prova["annuale"] and prova["piano"]["slug"] == "mensile-oro"

    assert (await client.get("/billing/store/catalogo", params={"piattaforma": "ios", "paese_store": "ITA"})).json()["stripe"]["modalita"] == "entitlement_ue"
    francia = (await client.get("/billing/store/catalogo", params={"piattaforma": "ios", "paese_store": "FR"})).json()
    assert francia["stripe"]["mostra"] is False
    android = (await client.get("/billing/store/catalogo", params={"piattaforma": "android", "paese_store": "US"})).json()
    assert android["stripe"]["mostra"] is False
    assert {(p["product_id"], p["base_plan"]) for p in android["prodotti"]} == {
        ("crediti_5", None), ("abbonamento", "mensile"), ("abbonamento", "annuale-prova")}


# ---- console --------------------------------------------------------------------------------------------------------


async def test_console_filtra_gli_abbonamenti_per_fornitore(client, session, utente, prodotti, google, principal_admin):
    google.abbonamenti["sub4"] = abbonamento_google(utente, ordine="GPA.8", scade=utcnow() + timedelta(days=30))
    assert (await client.post("/billing/store/google/verifica",
                              json={"productId": "abbonamento", "purchaseToken": "sub4"})).status_code == 200
    client.identita.principal = principal_admin
    r = await client.get("/admin/abbonamenti", params={"provider": "google_play"})
    assert r.status_code == 200, r.text
    assert [a["provider"] for a in r.json()["abbonamenti"]] == ["google_play"]
    assert r.json()["per_fornitore"]["google_play"] == 1
    assert (await client.get("/admin/abbonamenti", params={"provider": "stripe"})).json()["abbonamenti"] == []
    assert (await client.get("/admin/abbonamenti", params={"provider": "boh"})).status_code == 422


# ---- riconciliazione notturna ---------------------------------------------------------------------------------------


async def test_riconciliazione_notturna(client, session, utente, prodotti, google, apple, monkeypatch):
    from tarot_core.tools import store_riconcilia

    # Google: un pacchetto accreditato, poi rimborsato senza che la notifica arrivi.
    google.prodotti["tokR"] = prodotto_google(utente, ordine="GPA.9")
    assert (await client.post("/billing/store/google/verifica",
                              json={"productId": "crediti_5", "purchaseToken": "tokR"})).json()["saldo"] == 5
    google.annullati = [{"purchaseToken": "tokR", "orderId": "GPA.9", "voidedTimeMillis": str(_ms(utcnow())),
                         "voidedSource": 0, "voidedReason": 1, "kind": "androidpublisher#voidedPurchase"}]

    # Apple: un abbonamento registrato; il rinnovo arriva solo dalla storia.
    prodotto, abb = "chat.tarots.base.mese", "Auto-Renewable Subscription"
    primo = tx_apple(utente, ident="7000000001", prodotto=prodotto, tipo=abb, scade=utcnow() + timedelta(days=2))
    assert (await client.post("/billing/store/apple/verifica", json={"signedTransaction": apple.firma(primo)})).status_code == 200
    secondo = tx_apple(utente, ident="7000000002", originale="7000000001", prodotto=prodotto, tipo=abb,
                       scade=utcnow() + timedelta(days=32), motivo="RENEWAL")

    async def chiama(session_, percorso, *, ambiente, params=None):
        if percorso.startswith("/inApps/v2/history/"):
            return {"signedTransactions": [apple.firma(secondo), apple.firma(primo)], "hasMore": False, "revision": "r1"}
        if percorso.startswith("/inApps/v1/subscriptions/"):
            return {"data": [{"subscriptionGroupIdentifier": "g", "lastTransactions": [{
                "originalTransactionId": "7000000001", "status": 1, "signedTransactionInfo": apple.firma(secondo),
                "signedRenewalInfo": apple.firma(rinnovo_apple("7000000001", prodotto)),
            }]}]}
        raise AssertionError(percorso)

    async def configurato(session_, piattaforma):
        return True

    monkeypatch.setattr(app_store, "_chiama", chiama)
    monkeypatch.setattr(store_riconcilia, "_configurato", configurato)

    conti = await store_riconcilia.giro(session)
    assert conti.get("google_stornati") == 1 and conti.get("apple_riletti") == 1, conti
    assert await _saldo(session, utente.id) == 0
    a = await _abbonamento_store(session, utente.id)
    assert a.status == "attivo" and _vicine(a.period_end, utcnow() + timedelta(days=32))

    # Rieseguirlo non cambia niente.
    await store_riconcilia.giro(session)
    assert await _saldo(session, utente.id) == 0
    assert len((await session.execute(select(AcquistoStore).where(AcquistoStore.piattaforma == "ios"))).scalars().all()) == 2
