"""Stripe e il registro multicanale (v9, Fase 2): firme, checkout, eventi, storni, rinnovi, cron, ritorni.

Stripe è un server finto (`httpx.MockTransport` in `billing.stripe.TRASPORTO`): nessuna prova parla con Stripe, e
le firme dei webhook si calcolano qui con lo stesso segreto finto che riceve l'API.
"""
from __future__ import annotations

import json
import time
import uuid
from datetime import timedelta
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qsl

import httpx
import pytest
from sqlalchemy import select, update

from tarot_core.billing import stripe as modulo_stripe
from tarot_core.billing.credits import RegistroCrediti
from tarot_core.billing.pagamenti import FirmaNonValida
from tarot_core.domain.base import utcnow
from tarot_core.domain.billing_models import CreditEntry, PaymentCheckout, Plan, Subscription
from tarot_core.domain.models import AuditLog
from tarot_core.domain.repositories import UserRepository

from .conftest import richiede_database

pytestmark = richiede_database

SEGRETO = "whsec_prova_finta"
CHIAVE = "sk_test_finta"


class StripeFinto:
    """Le poche risposte dell'API di Stripe che il backend usa, e le richieste ricevute."""

    def __init__(self) -> None:
        self.richieste: List[Dict[str, Any]] = []
        self.fatture_di: Dict[str, str] = {}
        self.prezzi: List[Dict[str, Any]] = []
        self._n = 0

    def gestore(self, request: httpx.Request) -> httpx.Response:
        modulo = dict(parse_qsl(request.content.decode())) if request.content else {}
        self.richieste.append({
            "metodo": request.method, "percorso": request.url.path, "modulo": modulo,
            "parametri": dict(request.url.params), "intestazioni": dict(request.headers),
        })
        assert request.headers["authorization"] == f"Bearer {CHIAVE}"
        self._n += 1
        percorso = request.url.path
        if percorso == "/v1/checkout/sessions":
            sid = f"cs_test_{self._n}"
            return httpx.Response(200, json={"id": sid, "url": f"https://checkout.stripe.com/c/pay/{sid}"})
        if percorso == "/v1/coupons":
            return httpx.Response(200, json={"id": f"co_{self._n}"})
        if percorso == "/v1/prices" and request.method == "GET":
            chiave = request.url.params.get("lookup_keys[0]")
            return httpx.Response(200, json={"data": [p for p in self.prezzi if p["lookup_key"] == chiave]})
        if percorso == "/v1/prices":
            for p in self.prezzi:     # transfer_lookup_key: la chiave passa al Price nuovo
                if p["lookup_key"] == modulo["lookup_key"]:
                    p["lookup_key"] = None
            prezzo = {
                "id": f"price_{self._n}", "lookup_key": modulo["lookup_key"], "currency": modulo["currency"],
                "unit_amount": int(modulo["unit_amount"]), "recurring": {"interval": modulo["recurring[interval]"]},
            }
            self.prezzi.append(prezzo)
            return httpx.Response(200, json=prezzo)
        if percorso.startswith("/v1/invoices/"):
            return httpx.Response(200, json={
                "id": percorso.rsplit("/", 1)[1], "status": "open", "hosted_invoice_url": "https://invoice.stripe.com/i/x",
            })
        if percorso == "/v1/invoice_payments":
            pi = request.url.params.get("payment[payment_intent]")
            fattura = self.fatture_di.get(pi or "")
            return httpx.Response(200, json={"data": [{"invoice": fattura}] if fattura else []})
        if percorso.startswith("/v1/subscriptions/"):
            return httpx.Response(200, json={"id": percorso.rsplit("/", 1)[1], "status": "active"})
        return httpx.Response(404, json={"error": {"message": "sconosciuto"}})

    def ultima(self, percorso: str) -> Dict[str, Any]:
        return [r for r in self.richieste if r["percorso"] == percorso][-1]


@pytest.fixture(autouse=True)
def _senza_controllo_eta(monkeypatch):
    """L'età minima (Fase 1) non è l'oggetto di queste prove."""
    from tarot_core.tarot import eta_minima

    monkeypatch.setattr(eta_minima, "controllo_attivo", lambda: False, raising=False)


@pytest.fixture
def finto(monkeypatch):
    from tarot_core.settings import get_settings

    stripe = StripeFinto()
    monkeypatch.setattr(modulo_stripe, "TRASPORTO", httpx.MockTransport(stripe.gestore))
    monkeypatch.setenv("TAROT_BILLING_PROVIDER", "stripe")
    monkeypatch.setenv("TAROT_STRIPE_SECRET_KEY", CHIAVE)
    monkeypatch.setenv("TAROT_STRIPE_WEBHOOK_SECRET", SEGRETO)
    get_settings.cache_clear()
    yield stripe
    get_settings.cache_clear()


@pytest.fixture
def come(client, principal_utente, principal_admin):
    def scegli(chi: str):
        client.identita.principal = principal_admin if chi == "admin" else principal_utente
        return client

    return scegli


def _evento(tipo: str, oggetto: Dict[str, Any], id_evento: Optional[str] = None) -> bytes:
    return json.dumps({
        "id": id_evento or f"evt_{uuid.uuid4().hex[:20]}", "object": "event", "type": tipo,
        "data": {"object": oggetto},
    }).encode()


async def _invia(client, corpo: bytes, *, segreto: str = SEGRETO, istante: Optional[int] = None):
    return await client.post(
        "/billing/webhook", content=corpo,
        headers={"Stripe-Signature": modulo_stripe.firma(corpo, segreto, istante=istante),
                 "Content-Type": "application/json"},
    )


async def _utente(session, principal):
    utente = await UserRepository(session).ensure(principal)
    await session.commit()
    return utente


async def _piano_stella(session) -> Plan:
    """Un abbonamento che accredita crediti a ogni periodo (quelli del seed non ne danno)."""
    piano = Plan(
        slug="stella", name="Stella", tipo="abbonamento", price_monthly=500, price_yearly=5000,
        credits_per_period=10, limits={"letture_al_giorno": 0}, rank=5,
    )
    session.add(piano)
    await session.commit()
    return piano


async def _compra_pacchetto(client, *, pi: str = "pi_1", piano: str = "pacchetto-15") -> str:
    r = await client.post("/me/checkout", json={"piano": piano, "ritorno": "/pricing"})
    assert r.status_code == 201, r.text
    checkout_id = r.json()["checkout_id"]
    r = await _invia(client, _evento("checkout.session.completed", {
        "id": "cs_x", "object": "checkout.session", "mode": "payment", "payment_status": "paid",
        "payment_intent": pi, "client_reference_id": checkout_id, "amount_total": 1290,
        "metadata": {"tipo": "piano", "checkout_id": checkout_id},
    }))
    assert r.status_code == 200, r.text
    return checkout_id


async def _saldo(session, utente) -> int:
    return await RegistroCrediti(session).saldo(utente.id)


# ---- la firma -----------------------------------------------------------------------------------------------------


def _provider():
    from tarot_core.billing.stripe import PagamentiStripe
    from tarot_core.settings import Settings

    return PagamentiStripe(Settings(stripe_secret_key=CHIAVE, stripe_webhook_secret=SEGRETO))


def test_una_firma_valida_passa_e_l_evento_si_traduce():
    corpo = _evento("customer.subscription.deleted", {"id": "sub_1", "object": "subscription"}, "evt_1")
    evento = _provider().verifica(corpo, {"Stripe-Signature": modulo_stripe.firma(corpo, SEGRETO)})
    assert (evento.id, evento.tipo, evento.dati["subscription_id"]) == ("evt_1", "abbonamento.annullato", "sub_1")


def test_una_firma_scaduta_si_rifiuta():
    corpo = _evento("charge.refunded", {"id": "ch_1"})
    vecchia = modulo_stripe.firma(corpo, SEGRETO, istante=int(time.time()) - 301)
    with pytest.raises(FirmaNonValida, match="vecchio"):
        _provider().verifica(corpo, {"Stripe-Signature": vecchia})


@pytest.mark.parametrize("intestazione", [
    None, "", "t=abc,v1=00", "v1=00", "t=1",
])
def test_una_firma_assente_o_malformata_si_rifiuta(intestazione):
    corpo = _evento("charge.refunded", {"id": "ch_1"})
    with pytest.raises(FirmaNonValida):
        _provider().verifica(corpo, {} if intestazione is None else {"Stripe-Signature": intestazione})


def test_una_firma_sbagliata_o_un_corpo_alterato_si_rifiutano():
    corpo = _evento("charge.refunded", {"id": "ch_1"})
    with pytest.raises(FirmaNonValida, match="non valida"):
        _provider().verifica(corpo, {"Stripe-Signature": modulo_stripe.firma(corpo, "whsec_altro")})
    firma = modulo_stripe.firma(corpo, SEGRETO)
    with pytest.raises(FirmaNonValida, match="non valida"):
        _provider().verifica(corpo.replace(b"ch_1", b"ch_2"), {"Stripe-Signature": firma})


def test_con_due_segreti_in_rotazione_basta_una_firma_giusta():
    corpo = _evento("charge.refunded", {"id": "ch_1", "payment_intent": "pi_1"})
    t = int(time.time())
    buona = modulo_stripe.firma(corpo, SEGRETO, istante=t).split("v1=")[1]
    cattiva = modulo_stripe.firma(corpo, "whsec_vecchio", istante=t).split("v1=")[1]
    evento = _provider().verifica(corpo, {"stripe-signature": f"t={t},v1={cattiva},v1={buona},v0=xyz"})
    assert evento.tipo == "pagamento.stornato" and evento.dati["riferimenti"] == ["pi_1", "ch_1"]


async def test_il_webhook_rifiuta_una_firma_sbagliata(client, finto):
    corpo = _evento("checkout.session.completed", {"id": "cs_1"})
    r = await _invia(client, corpo, segreto="whsec_altro")
    assert r.status_code == 400 and "firma non valida" in r.text
    r = await _invia(client, corpo, istante=int(time.time()) - 3600)
    assert r.status_code == 400 and "vecchio" in r.text


# ---- checkout ------------------------------------------------------------------------------------------------------


async def test_checkout_di_un_pacchetto_con_stripe(client, session, catalogo, finto, principal_utente):
    utente = await _utente(session, principal_utente)
    r = await client.post("/me/checkout", json={"piano": "pacchetto-15", "ritorno": "/pricing"})
    assert r.status_code == 201, r.text
    corpo = r.json()
    assert corpo["url"].startswith("https://checkout.stripe.com/")

    richiesta = finto.ultima("/v1/checkout/sessions")
    modulo = richiesta["modulo"]
    assert modulo["mode"] == "payment"
    assert modulo["line_items[0][price_data][unit_amount]"] == "1290"
    assert modulo["line_items[0][price_data][currency]"] == "eur"
    assert modulo["client_reference_id"] == corpo["checkout_id"] == modulo["metadata[checkout_id]"]
    assert modulo["success_url"] == f"http://localhost:3000/pricing?checkout={corpo['checkout_id']}"
    assert richiesta["intestazioni"]["idempotency-key"] == f"checkout-{corpo['checkout_id']}"
    checkout = await session.get(PaymentCheckout, uuid.UUID(corpo["checkout_id"]))
    await session.refresh(checkout)
    assert checkout.provider == "stripe" and checkout.external_id.startswith("cs_test_")

    r = await _invia(client, _evento("checkout.session.completed", {
        "id": checkout.external_id, "mode": "payment", "payment_status": "paid", "payment_intent": "pi_1",
        "client_reference_id": corpo["checkout_id"], "metadata": {"tipo": "piano", "checkout_id": corpo["checkout_id"]},
    }))
    assert r.json()["esito"] == "crediti accreditati"
    assert (await client.get(f"/me/checkout/{corpo['checkout_id']}")).json()["stato"] == "pagato"
    assert await _saldo(session, utente) == 15
    voce = (await session.execute(
        select(CreditEntry).where(CreditEntry.user_id == utente.id, CreditEntry.reason == "acquisto")
    )).scalar_one()
    assert (voce.canale, voce.provider, voce.riferimento_esterno) == ("web", "stripe", "pi_1")


async def test_un_pagamento_in_attesa_non_accredita_finche_non_arriva(client, session, catalogo, finto, principal_utente):
    utente = await _utente(session, principal_utente)
    checkout_id = (await client.post("/me/checkout", json={"piano": "pacchetto-5"})).json()["checkout_id"]
    sessione = {"id": "cs_a", "mode": "payment", "payment_intent": "pi_sepa", "client_reference_id": checkout_id,
                "metadata": {"tipo": "piano", "checkout_id": checkout_id}}
    r = await _invia(client, _evento("checkout.session.completed", {**sessione, "payment_status": "unpaid"}))
    assert r.json()["esito"] == "ignorato" and await _saldo(session, utente) == 0
    r = await _invia(client, _evento("checkout.session.async_payment_succeeded", {**sessione, "payment_status": "paid"}))
    assert r.json()["esito"] == "crediti accreditati" and await _saldo(session, utente) == 5


async def test_checkout_di_un_abbonamento_con_coupon_sconta_solo_il_primo_pagamento(come, session, catalogo, finto):
    r = await come("admin").post("/admin/coupons", json={"code": "VENTI", "tipo": "percentuale", "valore": 20})
    assert r.status_code == 201, r.text
    # Senza rinnovo automatico (Fase 2b): solo lo sconto del coupon. Con il rinnovo, i due sconti si sommano in un solo
    # coupon d'una volta (`test_abbonamenti.py`).
    r = await come("utente").post("/me/checkout", json={"piano": "mensile-base", "coupon": "venti", "rinnovo": False})
    assert r.status_code == 201, r.text
    assert r.json()["importo"] == 792

    coupon = finto.ultima("/v1/coupons")["modulo"]
    assert (coupon["amount_off"], coupon["duration"], coupon["max_redemptions"]) == ("198", "once", "1")
    modulo = finto.ultima("/v1/checkout/sessions")["modulo"]
    assert modulo["mode"] == "subscription"
    # Un Price vero, al listino: i rinnovi sono a prezzo pieno, lo sconto è lo sconto d'una volta.
    prezzo = finto.prezzi[0]
    assert (prezzo["lookup_key"], prezzo["unit_amount"], prezzo["recurring"]["interval"]) == (
        "tarots_mensile-base_mese", 990, "month",
    )
    assert modulo["line_items[0][price]"] == prezzo["id"]
    assert modulo["discounts[0][coupon]"].startswith("co_")

    # Il secondo abbonato trova lo stesso Price per la sua chiave, non ne crea un altro.
    await come("utente").post("/me/checkout", json={"piano": "mensile-base"})
    assert finto.ultima("/v1/checkout/sessions")["modulo"]["line_items[0][price]"] == prezzo["id"]
    assert len(finto.prezzi) == 1


async def test_un_listino_cambiato_crea_un_price_nuovo_che_prende_la_chiave(come, session, catalogo, finto):
    await come("utente").post("/me/checkout", json={"piano": "mensile-base"})
    piano = (await session.execute(select(Plan).where(Plan.slug == "mensile-base"))).scalar_one()
    piano.price_monthly = 1190
    await session.commit()
    await come("utente").post("/me/checkout", json={"piano": "mensile-base"})
    assert [(p["unit_amount"], p["lookup_key"]) for p in finto.prezzi] == [
        (990, None), (1190, "tarots_mensile-base_mese"),
    ]
    assert finto.ultima("/v1/prices")["modulo"]["transfer_lookup_key"] == "true"


async def test_l_abbonamento_nasce_dal_checkout_completato(client, session, catalogo, finto, principal_utente):
    utente = await _utente(session, principal_utente)
    await _piano_stella(session)
    checkout_id = (await client.post("/me/checkout", json={"piano": "stella"})).json()["checkout_id"]
    r = await _invia(client, _evento("checkout.session.completed", {
        "id": "cs_s", "mode": "subscription", "payment_status": "paid", "subscription": "sub_1", "invoice": "in_1",
        "client_reference_id": checkout_id, "metadata": {"tipo": "piano", "checkout_id": checkout_id},
    }))
    assert r.json()["esito"] == "abbonamento attivato"
    abbonamento = (await session.execute(
        select(Subscription).where(Subscription.user_id == utente.id, Subscription.status == "attivo")
    )).scalar_one()
    assert (abbonamento.provider, abbonamento.external_id) == ("stripe", "sub_1")
    voce = (await session.execute(
        select(CreditEntry).where(CreditEntry.user_id == utente.id, CreditEntry.reason == "accredito_piano")
    )).scalar_one()
    assert (voce.provider, voce.riferimento_esterno, voce.delta) == ("stripe", "in_1", 10)


async def test_lo_stesso_evento_due_volte_conta_una(client, session, catalogo, finto, principal_utente):
    utente = await _utente(session, principal_utente)
    checkout_id = (await client.post("/me/checkout", json={"piano": "pacchetto-15"})).json()["checkout_id"]
    corpo = _evento("checkout.session.completed", {
        "id": "cs_d", "mode": "payment", "payment_status": "paid", "payment_intent": "pi_d",
        "client_reference_id": checkout_id, "metadata": {"tipo": "piano", "checkout_id": checkout_id},
    }, "evt_doppio")
    assert (await _invia(client, corpo)).json()["esito"] == "crediti accreditati"
    assert (await _invia(client, corpo)).json()["esito"] == "già applicato"
    # Un altro evento per lo stesso pagamento (Stripe ne manda due per i metodi asincroni): niente di nuovo.
    altro = _evento("checkout.session.async_payment_succeeded", json.loads(corpo)["data"]["object"])
    assert (await _invia(client, altro)).json()["esito"] == "checkout pagato"
    assert await _saldo(session, utente) == 15


async def test_un_ordine_del_negozio_si_paga_con_stripe(client, session, finto, principal_utente):
    from tarot_core.domain.deck_models import Deck
    from tarot_core.domain.ordini_models import Ordine

    await _utente(session, principal_utente)
    session.add(Deck(slug="lune", nome="Lune", attivo=True, prezzo_digitale=900, rank=1))
    await session.commit()
    deck = (await session.execute(select(Deck).where(Deck.slug == "lune"))).scalar_one()
    r = await client.post("/orders", json={"voci": [{"deck_id": deck.id, "tipo": "digitale"}], "ritorno": "/mazzo"})
    assert r.status_code == 201, r.text
    ordine_id = r.json()["id"]
    modulo = finto.ultima("/v1/checkout/sessions")["modulo"]
    assert modulo["mode"] == "payment" and modulo["metadata[tipo]"] == "ordine"
    assert modulo["line_items[0][price_data][unit_amount]"] == "900"
    r = await _invia(client, _evento("checkout.session.completed", {
        "id": "cs_o", "mode": "payment", "payment_status": "paid", "payment_intent": "pi_o",
        "client_reference_id": ordine_id, "metadata": {"tipo": "ordine", "ordine_id": ordine_id},
    }))
    assert r.json()["esito"] == "ordine pagato"
    ordine = await session.get(Ordine, uuid.UUID(ordine_id))
    await session.refresh(ordine)
    assert ordine.status == "pagato"


# ---- storni ------------------------------------------------------------------------------------------------------


async def test_un_rimborso_storna_i_crediti_una_volta(client, session, catalogo, finto, principal_utente):
    utente = await _utente(session, principal_utente)
    await _compra_pacchetto(client, pi="pi_r")
    rimborso = {"id": "ch_r", "object": "charge", "payment_intent": "pi_r", "amount": 1290, "amount_refunded": 1290}
    r = await _invia(client, _evento("charge.refunded", rimborso))
    assert r.json()["esito"] == "crediti stornati"
    assert await _saldo(session, utente) == 0
    r = await _invia(client, _evento("charge.refunded", rimborso))
    assert r.json()["esito"] == "storno già registrato" and await _saldo(session, utente) == 0
    storno = (await session.execute(select(CreditEntry).where(CreditEntry.reason == "storno"))).scalar_one()
    assert (storno.delta, storno.provider, storno.riferimento_esterno) == (-15, "stripe", "pi_r")


async def test_un_rimborso_parziale_storna_in_proporzione(client, session, catalogo, finto, principal_utente):
    utente = await _utente(session, principal_utente)
    await _compra_pacchetto(client, pi="pi_p")
    await _invia(client, _evento("charge.refunded", {
        "id": "ch_p", "payment_intent": "pi_p", "amount": 1290, "amount_refunded": 645,
    }))
    assert await _saldo(session, utente) == 15 - 8


async def test_il_rimborso_di_una_fattura_si_ritrova_chiedendola_a_stripe(client, session, catalogo, finto, principal_utente):
    """Dal 2025 l'addebito non cita la fattura: il backend la chiede a Stripe (`/v1/invoice_payments`)."""
    utente = await _utente(session, principal_utente)
    await _piano_stella(session)
    checkout_id = (await client.post("/me/checkout", json={"piano": "stella"})).json()["checkout_id"]
    await _invia(client, _evento("checkout.session.completed", {
        "id": "cs_f", "mode": "subscription", "payment_status": "paid", "subscription": "sub_f", "invoice": "in_f",
        "client_reference_id": checkout_id, "metadata": {"tipo": "piano", "checkout_id": checkout_id},
    }))
    finto.fatture_di["pi_f"] = "in_f"
    r = await _invia(client, _evento("charge.refunded", {"id": "ch_f", "payment_intent": "pi_f", "amount": 500,
                                                         "amount_refunded": 500}))
    assert r.json()["esito"] == "crediti stornati" and await _saldo(session, utente) == 0


async def test_con_il_saldo_negativo_non_si_aprono_letture(client, session, catalogo, finto, principal_utente):
    utente = await _utente(session, principal_utente)
    await _compra_pacchetto(client, pi="pi_n")
    await RegistroCrediti(session).consuma(utente.id, 5, note="letture già fatte")
    await session.commit()
    await _invia(client, _evento("charge.dispute.created", {"id": "dp_n", "charge": "ch_n", "payment_intent": "pi_n"}))
    assert await _saldo(session, utente) == -5

    r = await client.post("/readings", json={"spread_id": "tre-carte", "question": "Cosa mi riserva il lavoro?"})
    assert r.status_code == 402, r.text
    assert r.json()["detail"]["motivo"] == "saldo_negativo" and r.json()["detail"]["saldo"] == -5

    # Un pacchetto lo riporta sopra zero: si legge di nuovo.
    await _compra_pacchetto(client, pi="pi_n2", piano="pacchetto-15")
    r = await client.post("/readings", json={"spread_id": "tre-carte", "question": "Cosa mi riserva il lavoro?"})
    assert r.status_code == 201, r.text


async def test_una_contestazione_vinta_restituisce_i_crediti(client, session, catalogo, finto, principal_utente):
    utente = await _utente(session, principal_utente)
    await _compra_pacchetto(client, pi="pi_c")
    contestazione = {"id": "dp_c", "object": "dispute", "charge": "ch_c", "payment_intent": "pi_c"}
    await _invia(client, _evento("charge.dispute.created", {**contestazione, "status": "needs_response"}))
    assert await _saldo(session, utente) == 0
    r = await _invia(client, _evento("charge.dispute.closed", {**contestazione, "status": "won"}))
    assert r.json()["esito"] == "storno annullato" and await _saldo(session, utente) == 15
    r = await _invia(client, _evento("charge.dispute.closed", {**contestazione, "status": "won"}))
    assert r.json()["esito"] == "storno già annullato" and await _saldo(session, utente) == 15


async def test_una_contestazione_persa_lascia_lo_storno(client, session, catalogo, finto, principal_utente):
    utente = await _utente(session, principal_utente)
    await _compra_pacchetto(client, pi="pi_l")
    contestazione = {"id": "dp_l", "charge": "ch_l", "payment_intent": "pi_l"}
    await _invia(client, _evento("charge.dispute.created", contestazione))
    r = await _invia(client, _evento("charge.dispute.closed", {**contestazione, "status": "lost"}))
    assert r.json()["esito"] == "ignorato" and await _saldo(session, utente) == 0


# ---- rinnovi e stati dell'abbonamento ------------------------------------------------------------------------------


async def _abbonato_stripe(client, session, finto) -> Subscription:
    await _piano_stella(session)
    checkout_id = (await client.post("/me/checkout", json={"piano": "stella"})).json()["checkout_id"]
    await _invia(client, _evento("checkout.session.completed", {
        "id": "cs_r", "mode": "subscription", "payment_status": "paid", "subscription": "sub_r", "invoice": "in_1",
        "client_reference_id": checkout_id, "metadata": {"tipo": "piano", "checkout_id": checkout_id},
    }))
    return (await session.execute(select(Subscription).where(Subscription.external_id == "sub_r"))).scalar_one()


async def test_il_rinnovo_arriva_da_invoice_paid(client, session, catalogo, finto, principal_utente):
    utente = await _utente(session, principal_utente)
    abbonamento = await _abbonato_stripe(client, session, finto)
    assert await _saldo(session, utente) == 10

    # La prima fattura non rinnova: il primo periodo l'ha aperto il checkout.
    prima = {"id": "in_1", "object": "invoice", "billing_reason": "subscription_create", "subscription": "sub_r"}
    assert (await _invia(client, _evento("invoice.paid", prima))).json()["esito"] == "ignorato"
    assert await _saldo(session, utente) == 10

    fine = int((utcnow() + timedelta(days=61)).timestamp())
    ciclo = {
        "id": "in_2", "object": "invoice", "billing_reason": "subscription_cycle",
        # La forma dell'API dal 2025: l'abbonamento sta in `parent`.
        "parent": {"subscription_details": {"subscription": "sub_r"}},
        "lines": {"data": [{"period": {"start": 0, "end": fine}}]},
    }
    r = await _invia(client, _evento("invoice.paid", ciclo))
    assert r.json()["esito"] == "abbonamento rinnovato"
    await session.refresh(abbonamento)
    assert abs(abbonamento.period_end.timestamp() - fine) < 1 and abbonamento.status == "attivo"
    assert await _saldo(session, utente) == 20
    # La stessa fattura in un altro evento: già rinnovato.
    assert (await _invia(client, _evento("invoice.paid", ciclo))).json()["esito"] == "già rinnovato"
    assert await _saldo(session, utente) == 20


async def test_pagamento_fallito_apre_la_tolleranza_e_la_chiusura_torna_al_gratuito(client, session, catalogo, finto, principal_utente):
    utente = await _utente(session, principal_utente)
    abbonamento = await _abbonato_stripe(client, session, finto)
    r = await _invia(client, _evento("invoice.payment_failed", {"id": "in_3", "subscription": "sub_r"}))
    # Fase 2b: non si sospende subito, si apre la tolleranza (letture comprese ancora attive).
    assert r.json()["esito"] == "abbonamento in_sospeso"
    r = await _invia(client, _evento("customer.subscription.deleted", {"id": "sub_r", "object": "subscription"}))
    assert r.json()["esito"] == "abbonamento disdetto"
    await session.refresh(abbonamento)
    assert abbonamento.status == "disdetto"
    vivo = (await session.execute(
        select(Subscription).where(Subscription.user_id == utente.id, Subscription.status == "attivo")
    )).scalar_one()
    assert vivo.plan.slug == "free" and vivo.provider == "interno"


async def test_la_fattura_non_pagata_resta_da_pagare_e_si_azzera_al_rinnovo(client, session, catalogo, finto, principal_utente):
    from tarot_core.billing.stripe import PagamentiStripe

    await _utente(session, principal_utente)
    abbonamento = await _abbonato_stripe(client, session, finto)
    await _invia(client, _evento("invoice.payment_failed", {"id": "in_9", "subscription": "sub_r"}))
    await session.refresh(abbonamento)
    assert (abbonamento.status, abbonamento.fattura_aperta) == ("in_sospeso", "in_9")
    # Si torna a pagare quella fattura, non un nuovo checkout.
    assert await PagamentiStripe().url_fattura("in_9") == "https://invoice.stripe.com/i/x"

    await _invia(client, _evento("invoice.paid", {"id": "in_9", "billing_reason": "subscription_cycle",
                                                  "subscription": "sub_r"}))
    await session.refresh(abbonamento)
    assert (abbonamento.status, abbonamento.fattura_aperta) == ("attivo", None)


async def test_lo_stato_locale_segue_quello_di_stripe_senza_accreditare(client, session, catalogo, finto, principal_utente):
    utente = await _utente(session, principal_utente)
    abbonamento = await _abbonato_stripe(client, session, finto)
    fine = int((utcnow() + timedelta(days=20)).timestamp())

    async def aggiorna(**campi):
        oggetto = {"id": "sub_r", "object": "subscription", "status": "active", "cancel_at_period_end": False,
                   "items": {"data": [{"current_period_end": fine}]}, **campi}
        r = await _invia(client, _evento("customer.subscription.updated", oggetto))
        await session.refresh(abbonamento)
        return r.json()["esito"]

    assert await aggiorna(status="past_due") == "abbonamento in_sospeso"       # la tolleranza (Fase 2b)
    assert await aggiorna(status="unpaid") == "abbonamento sospeso"
    assert await aggiorna() == "abbonamento attivo"
    # Il rinnovo automatico spento dal profilo o dalla dashboard: una disdetta a fine periodo, e si toglie riaccendendolo.
    await aggiorna(cancel_at_period_end=True)
    assert abbonamento.cancel_at is not None and abs(abbonamento.cancel_at.timestamp() - fine) < 1
    await aggiorna(cancel_at_period_end=False)
    assert abbonamento.cancel_at is None
    assert await _saldo(session, utente) == 10          # nessun aggiornamento accredita

    assert await aggiorna(status="canceled") == "abbonamento disdetto"
    # Chiuso qui, non torna vivo per un aggiornamento: solo un incasso lo riaprirebbe.
    assert await aggiorna(status="active") == "abbonamento disdetto: invariato"


async def test_la_disdetta_passa_da_stripe(client, session, catalogo, finto, principal_utente):
    await _utente(session, principal_utente)
    await _abbonato_stripe(client, session, finto)
    r = await client.post("/me/subscription/cancel")
    assert r.status_code == 200, r.text
    richiesta = finto.ultima("/v1/subscriptions/sub_r")
    assert richiesta["metodo"] == "POST" and richiesta["modulo"] == {"cancel_at_period_end": "true"}


# ---- il cron degli abbonamenti -------------------------------------------------------------------------------------


async def _abbonamento(session, utente, piano, *, provider: str, fine_giorni: float, stato: str = "attivo",
                       external_id: Optional[str] = None, disdetto: bool = False) -> Subscription:
    fine = utcnow() + timedelta(days=fine_giorni)
    abbonamento = Subscription(
        user_id=utente.id, plan_id=piano.id, status=stato, period_start=fine - timedelta(days=30), period_end=fine,
        provider=provider, external_id=external_id, cancel_at=fine if disdetto else None,
    )
    session.add(abbonamento)
    await session.commit()
    return abbonamento


async def test_il_cron_rinnova_i_piani_interni_una_volta_sola(session, catalogo, principal_utente, principal_altro):
    from tarot_core.tools.abbonamenti import giro

    utente = await _utente(session, principal_utente)
    altro = await _utente(session, principal_altro)
    stella = await _piano_stella(session)
    interno = await _abbonamento(session, utente, stella, provider="interno", fine_giorni=-0.01)
    di_stripe = await _abbonamento(session, altro, stella, provider="stripe", fine_giorni=-1, external_id="sub_x")

    conti = await giro(session)
    assert conti == {"rinnovati": 1, "attesa_fornitore": 1}
    await session.refresh(interno)
    assert interno.period_end > utcnow() and await _saldo(session, utente) == 10
    # Stripe rinnova da sé, con invoice.paid: il cron non accredita niente.
    await session.refresh(di_stripe)
    assert di_stripe.status == "attivo" and await _saldo(session, altro) == 0

    # Un secondo giro non trova più niente da rinnovare.
    assert await giro(session) == {"attesa_fornitore": 1}
    assert await _saldo(session, utente) == 10


async def test_il_rinnovo_interno_non_accredita_due_volte_lo_stesso_periodo(session, catalogo, principal_utente):
    from tarot_core.billing.plans import GestoreAbbonamenti, NienteDaIncassare

    utente = await _utente(session, principal_utente)
    stella = await _piano_stella(session)
    abbonamento = await _abbonamento(session, utente, stella, provider="interno", fine_giorni=-0.01)
    inizio, fine = abbonamento.period_start, abbonamento.period_end
    gestore = GestoreAbbonamenti(session, NienteDaIncassare())
    assert (await gestore.rinnova(abbonamento)).crediti_accreditati == 10
    # Come se una replica avesse letto il periodo di prima: lo stesso periodo non si accredita di nuovo.
    abbonamento.period_start, abbonamento.period_end = inizio, fine
    assert (await gestore.rinnova(abbonamento)).motivo == "già rinnovato"
    assert await _saldo(session, utente) == 10


async def test_il_cron_chiude_scade_e_riporta_al_gratuito(session, catalogo, principal_utente, principal_altro, principal_admin):
    from tarot_core.tools.abbonamenti import giro

    utente = await _utente(session, principal_utente)
    altro = await _utente(session, principal_altro)
    terzo = await _utente(session, principal_admin)
    stella = await _piano_stella(session)
    disdetto = await _abbonamento(session, utente, stella, provider="interno", fine_giorni=-0.01, disdetto=True)
    perso = await _abbonamento(session, altro, stella, provider="stripe", fine_giorni=-8, external_id="sub_p")
    sospeso = await _abbonamento(session, terzo, stella, provider="mock", fine_giorni=-8, stato="sospeso")

    conti = await giro(session)
    assert conti == {"chiusi": 1, "scaduti": 2}
    for abbonamento, stato in ((disdetto, "disdetto"), (perso, "scaduto"), (sospeso, "scaduto")):
        await session.refresh(abbonamento)
        assert abbonamento.status == stato
    for persona in (utente, altro, terzo):
        vivo = (await session.execute(
            select(Subscription).where(Subscription.user_id == persona.id, Subscription.status == "attivo")
        )).scalar_one()
        assert vivo.plan.slug == "free"


async def test_il_cron_apre_la_tolleranza_a_un_rinnovo_del_simulatore_non_pagato(session, catalogo, principal_utente, monkeypatch):
    from tarot_core.settings import get_settings
    from tarot_core.tools.abbonamenti import giro

    monkeypatch.setenv("TAROT_BILLING_MOCK_RENEWAL_FAILS", "true")
    get_settings.cache_clear()
    utente = await _utente(session, principal_utente)
    stella = await _piano_stella(session)
    abbonamento = await _abbonamento(session, utente, stella, provider="mock", fine_giorni=-0.01, external_id="mock_sub_1")
    assert await giro(session) == {"in_tolleranza": 1}
    await session.refresh(abbonamento)
    assert abbonamento.status == "in_sospeso" and await _saldo(session, utente) == 0
    assert abbonamento.fattura_aperta == f"mock_in_{abbonamento.id.hex[:12]}"


# ---- i crediti di piano scadono con i loro consumi -----------------------------------------------------------------


async def test_il_consumo_usa_prima_i_crediti_che_scadono_e_scade_con_loro(session, utente):
    registro = RegistroCrediti(session)
    await registro.accredita(utente.id, 10, reason="accredito_piano", expires_at=utcnow() + timedelta(days=3))
    await registro.accredita(utente.id, 5, reason="acquisto", provider="mock", riferimento_esterno="mock_cs_1")
    await registro.consuma(utente.id, 12)
    assert await registro.saldo(utente.id) == 3
    consumi = (await session.execute(
        select(CreditEntry.delta, CreditEntry.expires_at).where(CreditEntry.reason == "consumo").order_by(CreditEntry.id)
    )).all()
    assert [d for d, _ in consumi] == [-10, -2] and consumi[0][1] is not None and consumi[1][1] is None

    # Il periodo finisce: escono l'accredito e i consumi che l'hanno usato. Restano i 3 comprati non spesi.
    await session.execute(
        update(CreditEntry).where(CreditEntry.expires_at.is_not(None)).values(expires_at=utcnow() - timedelta(seconds=1))
    )
    assert await registro.saldo(utente.id) == 3


async def test_il_rimborso_di_una_lettura_rispecchia_le_scadenze_del_consumo(session, utente):
    from tarot_core.domain.repositories import ReadingRepository

    registro = RegistroCrediti(session)
    scade = utcnow() + timedelta(days=3)
    await registro.accredita(utente.id, 1, reason="accredito_piano", expires_at=scade)
    await registro.accredita(utente.id, 5, reason="omaggio")
    lettura = await ReadingRepository(session).create(
        utente, spread_id="tre-carte", question="Una domanda di prova?", consumo="credito", lang="it", status="intervista",
    )
    await registro.consuma(utente.id, 2, reading_id=lettura.id)
    assert await registro.saldo(utente.id) == 4

    await registro.rimborsa(utente.id, 2, reading_id=lettura.id)
    rimborsi = (await session.execute(
        select(CreditEntry.delta, CreditEntry.expires_at).where(CreditEntry.reason == "rimborso").order_by(CreditEntry.id)
    )).all()
    # Uno torna con la scadenza del piano, uno senza: come erano stati spesi.
    assert [(d, s is not None) for d, s in rimborsi] == [(1, True), (1, False)]
    assert await registro.saldo(utente.id) == 6


async def test_un_accredito_con_lo_stesso_riferimento_non_si_ripete(session, utente):
    registro = RegistroCrediti(session)
    prima = await registro.accredita(utente.id, 5, reason="acquisto", provider="stripe", riferimento_esterno="pi_z")
    dopo = await registro.accredita(utente.id, 5, reason="acquisto", provider="stripe", riferimento_esterno="pi_z")
    assert prima.id == dopo.id and await registro.saldo(utente.id) == 5


# ---- il ritorno del checkout ---------------------------------------------------------------------------------------


async def test_il_ritorno_ammette_il_deep_link_dell_app(client, catalogo):
    r = await client.post("/me/checkout", json={"piano": "pacchetto-5", "ritorno": "chat.tarots.app://pagamento"})
    assert r.status_code == 201, r.text
    assert "chat.tarots.app%3A%2F%2Fpagamento" in r.json()["url"]


@pytest.mark.parametrize("ritorno", [
    "evil.app://pagamento", "javascript:alert(1)", "https://evil.example/x", "//evil.example", "chat.tarots.app://a b",
])
async def test_un_ritorno_con_uno_schema_non_ammesso_si_rifiuta(client, catalogo, ritorno):
    r = await client.post("/me/checkout", json={"piano": "pacchetto-5", "ritorno": ritorno})
    assert r.status_code == 400 and "Ritorno" in r.text


async def test_con_stripe_il_deep_link_passa_dal_rimbalzo_dell_api(client, catalogo, finto):
    r = await client.post("/me/checkout", json={"piano": "pacchetto-5", "ritorno": "chat.tarots.app://pagato"})
    assert r.status_code == 201, r.text
    successo = finto.ultima("/v1/checkout/sessions")["modulo"]["success_url"]
    assert successo.startswith("http://localhost:8100/billing/ritorno-app?verso=chat.tarots.app%3A%2F%2Fpagato")
    r = await client.get("/billing/ritorno-app", params={"verso": f"chat.tarots.app://pagato?checkout={r.json()['checkout_id']}"})
    assert r.status_code == 303 and r.headers["location"].startswith("chat.tarots.app://pagato?checkout=")
    r = await client.get("/billing/ritorno-app", params={"verso": "https://evil.example"})
    assert r.status_code == 400


# ---- la console ----------------------------------------------------------------------------------------------------


async def test_la_console_vede_lo_stato_delle_chiavi_mai_i_valori(come, finto):
    r = await come("admin").get("/admin/payments/config")
    assert r.status_code == 200, r.text
    corpo = r.json()
    assert corpo["provider"] == "stripe"
    assert corpo["stripe"] == {"chiave_segreta": True, "segreto_webhook": True, "modalita": "test"}
    assert corpo["webhook_url"] == "http://localhost:8100/billing/webhook"
    assert "charge.refunded" in corpo["eventi"]
    assert CHIAVE not in r.text and SEGRETO not in r.text
    assert (await come("utente").get("/admin/payments/config")).status_code == 403


async def test_lo_storno_a_mano_dalla_console(come, session, catalogo, principal_utente):
    utente = await _utente(session, principal_utente)
    await RegistroCrediti(session).accredita(
        utente.id, 15, reason="acquisto", canale="web", provider="mock", riferimento_esterno="mock_cs_m",
    )
    await session.commit()
    voce = (await session.execute(select(CreditEntry).where(CreditEntry.riferimento_esterno == "mock_cs_m"))).scalar_one()

    admin = come("admin")
    r = await admin.post(f"/admin/users/{utente.id}/credits/{voce.id}/storno", json={"motivo": "rimborsato a mano"})
    assert r.status_code == 200, r.text
    assert r.json() == {"saldo": 0, "delta": -15}
    r = await admin.post(f"/admin/users/{utente.id}/credits/{voce.id}/storno", json={"motivo": "di nuovo"})
    assert r.status_code == 409

    movimenti = (await admin.get(f"/admin/users/{utente.id}")).json()["movimenti"]
    storno = next(m for m in movimenti if m["reason"] == "storno")
    assert (storno["canale"], storno["provider"], storno["riferimento"]) == ("console", "mock", "mock_cs_m")
    traccia = (await session.execute(select(AuditLog).where(AuditLog.action == "credits.reverse"))).scalar_one()
    assert traccia.after["motivo"] == "rimborsato a mano"

    consumo = await RegistroCrediti(session).accredita(utente.id, 1, reason="omaggio")
    await session.commit()
    r = await admin.post(f"/admin/users/{utente.id}/credits/{consumo.id}/storno", json={"motivo": "non si può"})
    assert r.status_code == 422
