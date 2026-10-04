"""Gli abbonamenti della Fase 2b: limiti e condoni, consenso al credito, conguaglio, rinnovo automatico con le email,
prova gratuita (una per persona e per carta, conversione, promemoria), tolleranza e solleciti, nessun doppio
addebito, console, commissione di referral sugli abbonamenti.

Stripe è finto (`httpx.MockTransport`, come in `test_stripe.py`), l'SMTP è finto (`posta.invio.SPEDISCI`), il
modello è finto: nessuna prova parla con un servizio vero.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qsl

import httpx
import pytest
from sqlalchemy import select, update

from tarot_core.billing import abbonamenti as gestione
from tarot_core.billing import stripe as modulo_stripe
from tarot_core.billing.credits import RegistroCrediti
from tarot_core.billing.plans import GestoreAbbonamenti, NienteDaIncassare
from tarot_core.domain.abbonamenti_models import InvioEmail, ProvaGratuita
from tarot_core.domain.base import utcnow
from tarot_core.domain.billing_models import PaymentCheckout, Plan, Subscription
from tarot_core.domain.models import AuditLog, Reading
from tarot_core.domain.repositories import UserRepository

from .conftest import richiede_database
from .test_stripe import CHIAVE, SEGRETO, _evento, _invia

pytestmark = richiede_database

DOMANDA = {"spread_id": "tre-carte", "question": "Cosa mi riserva il lavoro?"}
RITORNO = {"esito": "paga", "ritorno": "http://localhost:3000/pricing"}


# ---- attrezzi ------------------------------------------------------------------------------------------------------


class StripeFinto:
    """L'API di Stripe che la Fase 2b usa: checkout, coupon (per id), abbonamenti (anche cancellati e con la carta),
    programmi (downgrade), fatture. Raccoglie le richieste."""

    def __init__(self) -> None:
        self.richieste: List[Dict[str, Any]] = []
        self.coupon: Dict[str, Dict[str, Any]] = {}
        self.prezzi: List[Dict[str, Any]] = []
        self.impronte: Dict[str, str] = {}
        self._n = 0

    def gestore(self, request: httpx.Request) -> httpx.Response:
        modulo = dict(parse_qsl(request.content.decode())) if request.content else {}
        self.richieste.append({"metodo": request.method, "percorso": request.url.path, "modulo": modulo,
                               "parametri": dict(request.url.params)})
        assert request.headers["authorization"] == f"Bearer {CHIAVE}"
        self._n += 1
        p = request.url.path
        if p == "/v1/checkout/sessions":
            return httpx.Response(200, json={"id": f"cs_test_{self._n}", "url": f"https://checkout.stripe.com/c/{self._n}"})
        if p == "/v1/coupons" and request.method == "POST":
            ident = modulo.get("id") or f"co_{self._n}"
            self.coupon[ident] = modulo
            return httpx.Response(200, json={"id": ident})
        if p.startswith("/v1/coupons/"):
            ident = p.rsplit("/", 1)[1]
            if ident in self.coupon:
                return httpx.Response(200, json={"id": ident})
            return httpx.Response(404, json={"error": {"message": "No such coupon"}})
        if p == "/v1/prices" and request.method == "GET":
            chiave = request.url.params.get("lookup_keys[0]")
            return httpx.Response(200, json={"data": [x for x in self.prezzi if x["lookup_key"] == chiave]})
        if p == "/v1/prices":
            prezzo = {"id": f"price_{self._n}", "lookup_key": modulo["lookup_key"], "currency": modulo["currency"],
                      "unit_amount": int(modulo["unit_amount"]), "recurring": {"interval": modulo["recurring[interval]"]}}
            self.prezzi.append(prezzo)
            return httpx.Response(200, json=prezzo)
        if p == "/v1/subscription_schedules":
            return httpx.Response(200, json={"id": f"sub_sched_{self._n}", "phases": [{
                "start_date": 1, "end_date": 2, "items": [{"price": "price_vecchio"}],
            }]})
        if p.startswith("/v1/subscription_schedules/"):
            return httpx.Response(200, json={"id": p.split("/")[3]})
        if p.startswith("/v1/subscriptions/"):
            ident = p.rsplit("/", 1)[1]
            corpo: Dict[str, Any] = {"id": ident, "status": "canceled" if request.method == "DELETE" else "active"}
            if ident in self.impronte:
                corpo["default_payment_method"] = {"id": "pm_1", "card": {"fingerprint": self.impronte[ident]}}
            return httpx.Response(200, json=corpo)
        if p.startswith("/v1/invoices/"):
            return httpx.Response(200, json={"id": p.rsplit("/", 1)[1], "status": "open",
                                             "hosted_invoice_url": f"https://invoice.stripe.com/i/{p.rsplit('/', 1)[1]}"})
        return httpx.Response(404, json={"error": {"message": "sconosciuto"}})

    def a(self, percorso: str, metodo: Optional[str] = None) -> List[Dict[str, Any]]:
        return [r for r in self.richieste if r["percorso"] == percorso and (metodo is None or r["metodo"] == metodo)]


@pytest.fixture
def stripe(monkeypatch):
    from tarot_core.settings import get_settings

    finto = StripeFinto()
    monkeypatch.setattr(modulo_stripe, "TRASPORTO", httpx.MockTransport(finto.gestore))
    monkeypatch.setenv("TAROT_BILLING_PROVIDER", "stripe")
    monkeypatch.setenv("TAROT_STRIPE_SECRET_KEY", CHIAVE)
    monkeypatch.setenv("TAROT_STRIPE_WEBHOOK_SECRET", SEGRETO)
    get_settings.cache_clear()
    yield finto
    get_settings.cache_clear()


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


@pytest.fixture
def come(client, principal_utente, principal_altro, principal_admin):
    def scegli(chi: str):
        client.identita.principal = {"admin": principal_admin, "altro": principal_altro}.get(chi, principal_utente)
        return client

    return scegli


async def _utente(session, principal):
    utente = await UserRepository(session).ensure(principal)
    await session.commit()
    return utente


async def _piano(session, slug: str, *, mensile: int, annuale: int = 0, rank: int = 50, limiti=None) -> Plan:
    piano = Plan(slug=slug, name=slug.title(), tipo="abbonamento", price_monthly=mensile, price_yearly=annuale,
                 credits_per_period=0, limits=limiti if limiti is not None else {"letture_al_giorno": 3}, rank=rank)
    session.add(piano)
    await session.commit()
    return piano


async def _abbonamento(
    session, utente, piano: Plan, *, provider: str = "mock", annuale: bool = False, giorni_fa: float = 0,
    durata: int = 30, importo: Optional[int] = None, stato: str = "attivo", external_id: Optional[str] = None,
    sconto: int = 0, prova: bool = False,
) -> Subscription:
    inizio = utcnow() - timedelta(days=giorni_fa)
    listino = piano.price_yearly if annuale else piano.price_monthly
    abbonamento = Subscription(
        user_id=utente.id, plan_id=piano.id, status=stato, period_start=inizio, period_end=inizio + timedelta(days=durata),
        provider=provider, external_id=external_id or f"{provider}_sub_{uuid.uuid4().hex[:8]}", annuale=annuale,
        listino=listino, importo_periodo=listino - sconto if importo is None else importo, sconto_ricorrente=sconto,
        prova=prova,
    )
    session.add(abbonamento)
    await session.commit()
    return abbonamento


async def _azzera_regalo(session):
    from tarot_core.domain.impostazioni_repositories import correnti

    riga = await correnti(session)
    riga.crediti_iscrizione = 0
    await session.commit()


async def _invii(session, tipo: str) -> List[InvioEmail]:
    return list((await session.execute(select(InvioEmail).where(InvioEmail.tipo == tipo))).scalars())


def _oggetti(posta) -> List[str]:
    return [m["Subject"] for m in posta]


# ---- limiti per periodo, condoni, consenso al credito ---------------------------------------------------------------


async def test_oltre_il_limite_del_giorno_due_condoni_poi_il_consenso_a_un_credito(client, session, catalogo):
    await _azzera_regalo(session)
    utente = await _utente(session, client.identita.principal)
    piano = await _piano(session, "limitato", mensile=990, limiti={"letture_al_giorno": 2})
    await _abbonamento(session, utente, piano)
    await RegistroCrediti(session).accredita(utente.id, 1, reason="acquisto", note="un credito")
    await session.commit()

    for _ in range(2):
        r = await client.post("/readings", json=DOMANDA)
        assert r.status_code == 201 and r.json()["consumo"] == "quota", r.text

    r = await client.post("/readings", json=DOMANDA)
    assert r.status_code == 402, r.text
    d = r.json()["detail"]
    assert (d["motivo"], d["limite"], d["valore"], d["usate"], d["letture_fatte"]) == (
        "limite_superato", "letture_al_giorno", 2, 2, 2,
    )
    assert (d["condoni_rimasti"], d["condoni_per_periodo"], d["saldo"], d["scelta"]) == (2, 2, 1, "condono")
    assert d["si_libera"] and d["messaggio"]

    # Col consenso: i primi due oltre il limite sono condonati, e si contano.
    for rimasti in (2, 1):
        r = await client.post("/readings", json={**DOMANDA, "oltre_limite": "condono"})
        assert r.status_code == 201 and r.json()["consumo"] == "condono", r.text
    r = await client.post("/readings", json=DOMANDA)
    d = r.json()["detail"]
    assert (r.status_code, d["condoni_rimasti"], d["letture_fatte"], d["scelta"]) == (402, 0, 4, "credito")
    # Un «condono» quando non ce ne sono più non passa: serve il consenso al credito.
    assert (await client.post("/readings", json={**DOMANDA, "oltre_limite": "condono"})).status_code == 402

    r = await client.post("/readings", json={**DOMANDA, "oltre_limite": "credito"})
    assert r.status_code == 201 and r.json()["consumo"] == "credito" and r.json()["saldo"] == 0, r.text

    # Senza crediti: si va a comprarli.
    r = await client.post("/readings", json=DOMANDA)
    assert r.json()["detail"]["scelta"] == "acquisto"
    r = await client.post("/readings", json={**DOMANDA, "oltre_limite": "credito"})
    assert r.status_code == 402 and r.json()["detail"]["motivo"] == "crediti"

    letture = (await session.execute(select(Reading).where(Reading.owner_id == utente.id))).scalars().all()
    assert sorted((x.consumo, x.limite) for x in letture) == [
        ("condono", "letture_al_giorno"), ("condono", "letture_al_giorno"), ("credito", "letture_al_giorno"),
        ("quota", None), ("quota", None),
    ]


async def test_ogni_limite_ha_i_suoi_condoni_e_la_sua_finestra(client, session, catalogo):
    utente = await _utente(session, client.identita.principal)
    piano = await _piano(session, "settimanale", mensile=990,
                         limiti={"letture_al_giorno": 5, "letture_alla_settimana": 3, "letture_al_mese": 20})
    await _abbonamento(session, utente, piano)
    for _ in range(3):
        assert (await client.post("/readings", json=DOMANDA)).json()["consumo"] == "quota"
    # Due letture di ieri: la settimana è piena, il giorno no. Si dice il limite che dura di più.
    await session.execute(update(Reading).where(Reading.owner_id == utente.id).values(created_at=utcnow() - timedelta(days=1)))
    await session.commit()
    r = await client.post("/readings", json=DOMANDA)
    d = r.json()["detail"]
    assert (r.status_code, d["limite"], d["usate"], d["condoni_rimasti"]) == (402, "letture_alla_settimana", 3, 2)
    assert (await client.post("/readings", json={**DOMANDA, "oltre_limite": "condono"})).json()["consumo"] == "condono"

    # Otto giorni dopo la settimana si libera: di nuovo in quota, e i condoni della settimana tornano due.
    await session.execute(update(Reading).where(Reading.owner_id == utente.id).values(created_at=utcnow() - timedelta(days=8)))
    await session.commit()
    assert (await client.post("/readings", json=DOMANDA)).json()["consumo"] == "quota"
    uso = (await client.get("/me/billing")).json()["uso"]
    assert uso["letture_alla_settimana"] == {"usati": 1, "limite": 3, "restanti": 2}
    assert uso["letture_al_mese"]["usati"] == 4 and uso["letture_al_giorno"]["usati"] == 1


async def test_le_letture_totali_valgono_per_il_periodo_pagato(client, session, catalogo):
    utente = await _utente(session, client.identita.principal)
    piano = await _piano(session, "totali", mensile=990, limiti={"letture_al_giorno": -1, "letture_totali": 2})
    abbonamento = await _abbonamento(session, utente, piano, giorni_fa=10)
    for _ in range(2):
        assert (await client.post("/readings", json=DOMANDA)).json()["consumo"] == "quota"
    r = await client.post("/readings", json=DOMANDA)
    assert r.status_code == 402 and r.json()["detail"]["limite"] == "letture_totali"
    # Si confrontano istanti, non date: l'API legge la fine dal database nel fuso della connessione (Europe/Rome), il
    # test la ha in UTC, e fra mezzanotte italiana e mezzanotte UTC le due date erano diverse (falliva solo di notte).
    si_libera = datetime.fromisoformat(r.json()["detail"]["si_libera"])
    assert abs((si_libera - abbonamento.period_end).total_seconds()) < 1
    # Il rinnovo apre un periodo nuovo: le letture del periodo prima non contano più.
    await session.execute(update(Reading).where(Reading.owner_id == utente.id).values(created_at=utcnow() - timedelta(days=11)))
    await session.commit()
    assert (await client.post("/readings", json=DOMANDA)).json()["consumo"] == "quota"


async def test_senza_abbonamento_a_pagamento_si_paga_col_credito_senza_dialogo(client, session, catalogo):
    utente = await _utente(session, client.identita.principal)
    await RegistroCrediti(session).accredita(utente.id, 2, reason="acquisto", note="due")
    await session.commit()
    r = await client.post("/readings", json=DOMANDA)
    assert r.status_code == 201 and r.json()["consumo"] == "credito"
    assert (await client.get("/me/billing")).json()["letture_comprese"] is False


async def test_la_tolleranza_tiene_le_letture_comprese(client, session, catalogo):
    utente = await _utente(session, client.identita.principal)
    piano = await _piano(session, "tollerante", mensile=990)
    await _abbonamento(session, utente, piano, stato="in_sospeso")
    assert (await client.post("/readings", json=DOMANDA)).json()["consumo"] == "quota"


# ---- il conguaglio --------------------------------------------------------------------------------------------------


def test_il_residuo_al_centesimo():
    inizio = utcnow()
    assert gestione.calcola_residuo(1000, inizio, inizio + timedelta(days=30), inizio + timedelta(days=15)) == (500, 15, 30)
    # Il giorno in corso non conta; fine periodo → zero; dopo la fine → zero.
    assert gestione.calcola_residuo(1000, inizio, inizio + timedelta(days=30), inizio + timedelta(days=15, hours=1))[:2] == (467, 14)
    assert gestione.calcola_residuo(1000, inizio, inizio + timedelta(days=30), inizio + timedelta(days=30))[0] == 0
    assert gestione.calcola_residuo(1000, inizio, inizio + timedelta(days=30), inizio + timedelta(days=40))[0] == 0
    # Mezzo centesimo per eccesso: 999 × 1/2 = 499,5 → 500.
    assert gestione.calcola_residuo(999, inizio, inizio + timedelta(days=2), inizio + timedelta(days=1))[0] == 500


async def test_conguaglio_l_esempio_dell_operatore(come, session, catalogo):
    """Base mensile 10 €, a metà mese passa all'annuale top 100 € con il rinnovo automatico: 80 − 5 = 75 €."""
    utente = await _utente(session, come("utente").identita.principal)
    base = await _piano(session, "base10", mensile=1000, annuale=10000, rank=10)
    await _piano(session, "top100", mensile=1500, annuale=10000, rank=20)
    await _abbonamento(session, utente, base, giorni_fa=14.99, importo=1000)

    r = await come("utente").post("/me/abbonamento/cambio/anteprima", json={"piano": "top100", "annuale": True})
    assert r.status_code == 200, r.text
    c = r.json()
    assert (c["tipo"], c["residuo"], c["listino"], c["sconto_rinnovo"], c["nuovo"], c["totale"]) == (
        "upgrade", 500, 10000, 2000, 8000, 7500,
    )
    assert (c["giorni_rimasti"], c["giorni_periodo"], c["pagato"]) == (15, 30, 1000)
    # Senza rinnovo automatico il nuovo è a listino.
    c = (await come("utente").post("/me/abbonamento/cambio/anteprima",
                                   json={"piano": "top100", "annuale": True, "rinnovo": False})).json()
    assert (c["nuovo"], c["totale"]) == (10000, 9500)


async def test_conguaglio_casi_limite(session, catalogo, principal_utente):
    utente = await _utente(session, principal_utente)
    base = await _piano(session, "basex", mensile=1000, annuale=9900, rank=10)
    top = await _piano(session, "topx", mensile=1500, annuale=14900, rank=20)

    # A fine periodo il residuo è zero: si paga il nuovo intero.
    finito = await _abbonamento(session, utente, base, giorni_fa=29.99, importo=1000)
    c = await gestione.anteprima_cambio(session, finito, top, annuale=False)
    assert (c.residuo, c.totale) == (0, 1200)
    finito.status = "disdetto"

    # Un annuale appena pagato vale più di un mese del piano sopra: il totale non va sotto zero.
    annuale = await _abbonamento(session, utente, base, annuale=True, durata=365, importo=9900, giorni_fa=0.5)
    c = await gestione.anteprima_cambio(session, annuale, top, annuale=False)
    assert c.tipo == "upgrade" and c.residuo == 9873 and c.totale == 0

    # Annuale → annuale a metà anno.
    annuale.period_start = utcnow() - timedelta(days=182, hours=12)
    annuale.period_end = annuale.period_start + timedelta(days=365)
    c = await gestione.anteprima_cambio(session, annuale, top, annuale=True)
    assert (c.giorni_rimasti, c.residuo, c.nuovo, c.totale) == (182, 4936, 11920, 6984)

    # Verso il basso: alla scadenza, senza conguaglio.
    c = await gestione.anteprima_cambio(session, annuale, base, annuale=False)
    assert c.tipo == "downgrade" and c.residuo == 0 and c.decorre == annuale.period_end
    with pytest.raises(gestione.ErroreAbbonamento):
        await gestione.anteprima_cambio(session, annuale, base, annuale=True)


async def test_upgrade_con_stripe_addebita_al_centesimo_e_chiude_il_vecchio_senza_rimborso(come, session, catalogo, stripe):
    utente = await _utente(session, come("utente").identita.principal)
    base = await _piano(session, "base10", mensile=1000, annuale=10000, rank=10)
    await _piano(session, "top100", mensile=1500, annuale=10000, rank=20)
    vecchio = await _abbonamento(session, utente, base, provider="stripe", external_id="sub_vecchio", giorni_fa=14.99,
                                 importo=1000)

    r = await come("utente").post("/me/abbonamento/cambio", json={"piano": "top100", "annuale": True, "ritorno": "/pricing"})
    assert r.status_code == 200, r.text
    assert (r.json()["tipo"], r.json()["importo"]) == ("upgrade", 7500)
    sessione = stripe.a("/v1/checkout/sessions")[-1]["modulo"]
    assert sessione["mode"] == "subscription" and sessione["metadata[sostituisce]"] == str(vecchio.id)
    once = [c for c in stripe.coupon.values() if c.get("duration") == "once"][-1]
    assert int(once["amount_off"]) == 10000 - 7500       # listino − totale: Stripe incassa esattamente 75,00 €

    checkout_id = r.json()["checkout_id"]
    r = await _invia(come("utente"), _evento("checkout.session.completed", {
        "id": "cs_u", "mode": "subscription", "payment_status": "paid", "subscription": "sub_nuovo", "invoice": "in_u",
        "amount_total": 7500, "client_reference_id": checkout_id, "metadata": {"tipo": "piano", "checkout_id": checkout_id},
    }))
    assert r.json()["esito"] == "abbonamento cambiato", r.text
    cancellazione = stripe.a("/v1/subscriptions/sub_vecchio", "DELETE")[-1]["modulo"]
    assert cancellazione == {"prorate": "false", "invoice_now": "false"}
    await session.refresh(vecchio)
    assert vecchio.status == "disdetto"
    nuovo = (await session.execute(select(Subscription).where(Subscription.external_id == "sub_nuovo"))).scalar_one()
    assert (nuovo.annuale, nuovo.listino, nuovo.importo_periodo, nuovo.sconto_ricorrente) == (True, 10000, 7500, 2000)
    # I rinnovi: 100 € − 20 € esatti, con un coupon «per sempre» d'importo fisso.
    assert stripe.coupon["tarots_rinnovo_2000_eur"]["duration"] == "forever"
    assert stripe.a("/v1/subscriptions/sub_nuovo", "POST")[-1]["modulo"] == {"discounts[0][coupon]": "tarots_rinnovo_2000_eur"}


async def test_downgrade_programmato_alla_scadenza(come, session, catalogo, stripe):
    utente = await _utente(session, come("utente").identita.principal)
    base = await _piano(session, "basey", mensile=1000, annuale=10000, rank=10)
    top = await _piano(session, "topy", mensile=1500, annuale=15000, rank=20)
    abbonamento = await _abbonamento(session, utente, top, provider="stripe", external_id="sub_top", giorni_fa=5,
                                     importo=1200, sconto=300)
    r = await come("utente").post("/me/abbonamento/cambio", json={"piano": "basey"})
    assert r.status_code == 200 and r.json()["tipo"] == "downgrade", r.text
    assert r.json()["abbonamento"]["piano_successivo"]["piano"] == "basey"
    await session.refresh(abbonamento)
    assert abbonamento.programma_esterno.startswith("sub_sched_")
    modulo = [x for x in stripe.richieste if x["percorso"].startswith("/v1/subscription_schedules/")][-1]["modulo"]
    assert modulo["end_behavior"] == "release" and modulo["proration_behavior"] == "none"
    assert modulo["phases[0][items][0][price]"] == "price_vecchio" and modulo["phases[1][iterations]"] == "1"
    assert modulo["phases[1][discounts][0][coupon]"] == "tarots_rinnovo_200_eur"

    # Al rinnovo (invoice.paid del ciclo) il piano diventa quello programmato.
    fine = int((utcnow() + timedelta(days=55)).timestamp())
    await _invia(come("utente"), _evento("invoice.paid", {
        "id": "in_r", "billing_reason": "subscription_cycle", "subscription": "sub_top", "amount_paid": 800,
        "lines": {"data": [{"period": {"end": fine}}]},
    }))
    await session.refresh(abbonamento)
    assert (abbonamento.plan_id, abbonamento.listino, abbonamento.importo_periodo) == (base.id, 1000, 800)
    assert abbonamento.piano_successivo_id is None and abbonamento.programma_esterno is None


async def test_gli_abbonamenti_degli_store_si_gestiscono_nello_store(come, session, catalogo):
    utente = await _utente(session, come("utente").identita.principal)
    piano = await _piano(session, "storeplan", mensile=990, annuale=9900)
    await _abbonamento(session, utente, piano, provider="google_play")
    r = await come("utente").post("/me/abbonamento/rinnovo", json={"attivo": False})
    assert r.status_code == 409 and r.json()["detail"]["motivo"] == "store"
    assert r.json()["detail"]["gestione"].startswith("https://play.google.com/")
    r = await come("utente").post("/me/abbonamento/cambio/anteprima", json={"piano": "storeplan", "annuale": True})
    assert r.status_code == 409 and r.json()["detail"]["motivo"] == "store"
    assert (await come("utente").get("/me/abbonamento")).json()["abbonamento"]["store"] is True


# ---- rinnovo automatico ---------------------------------------------------------------------------------------------


async def test_spegnere_il_rinnovo_manda_la_conferma_e_si_riaccende_fino_alla_scadenza(come, session, catalogo, stripe, posta):
    utente = await _utente(session, come("utente").identita.principal)
    piano = await _piano(session, "rinnovabile", mensile=1000)
    abbonamento = await _abbonamento(session, utente, piano, provider="stripe", external_id="sub_r", sconto=200)

    r = await come("utente").post("/me/abbonamento/rinnovo", json={"attivo": False})
    assert r.status_code == 200 and r.json()["abbonamento"]["rinnovo_automatico"] is False, r.text
    assert stripe.a("/v1/subscriptions/sub_r")[-1]["modulo"] == {"cancel_at_period_end": "true"}
    await session.refresh(abbonamento)
    assert abbonamento.cancel_at == abbonamento.period_end and abbonamento.status == "attivo"
    assert _oggetti(posta) == ["Conferma: rinnovo automatico disattivato"]
    assert posta[0]["To"] == "utente@example.com" and "/it/profile#abbonamento" in posta[0].get_body(("plain",)).get_content()
    assert [i.esito for i in await _invii(session, "rinnovo_spento")] == ["inviata"]

    r = await come("utente").post("/me/abbonamento/rinnovo", json={"attivo": True})
    assert r.status_code == 200 and r.json()["abbonamento"]["prossimo_rinnovo"] == 800
    assert stripe.a("/v1/subscriptions/sub_r")[-1]["modulo"] == {"cancel_at_period_end": "false"}
    assert _oggetti(posta)[-1] == "Il rinnovo automatico è di nuovo attivo"

    # Finito il periodo non si riaccende più.
    abbonamento.cancel_at = abbonamento.period_end = utcnow() - timedelta(minutes=1)
    abbonamento.period_start = abbonamento.period_end - timedelta(days=30)
    await session.commit()
    r = await come("utente").post("/me/abbonamento/rinnovo", json={"attivo": True})
    assert r.status_code == 409 and r.json()["detail"]["motivo"] == "scaduto"


async def test_comprato_senza_rinnovo_paga_il_listino_e_riaccendendo_prende_lo_sconto(come, session, catalogo, stripe, posta):
    await _utente(session, come("utente").identita.principal)
    r = await come("utente").post("/me/checkout", json={"piano": "mensile-base", "rinnovo": False})
    assert r.status_code == 201 and r.json()["importo"] == 990 and r.json()["sconto_rinnovo"] == 0, r.text
    assert "discounts[0][coupon]" not in stripe.a("/v1/checkout/sessions")[-1]["modulo"]
    checkout_id = r.json()["checkout_id"]
    await _invia(come("utente"), _evento("checkout.session.completed", {
        "id": "cs_n", "mode": "subscription", "payment_status": "paid", "subscription": "sub_n", "invoice": "in_n",
        "client_reference_id": checkout_id, "metadata": {"tipo": "piano", "checkout_id": checkout_id},
    }))
    assert stripe.a("/v1/subscriptions/sub_n")[-1]["modulo"] == {"cancel_at_period_end": "true"}
    abbonamento = (await session.execute(select(Subscription).where(Subscription.external_id == "sub_n"))).scalar_one()
    assert abbonamento.cancel_at is not None and abbonamento.sconto_ricorrente == 0

    r = await come("utente").post("/me/abbonamento/rinnovo", json={"attivo": True})
    assert r.status_code == 200 and r.json()["abbonamento"]["prossimo_rinnovo"] == 792, r.text
    assert stripe.a("/v1/subscriptions/sub_n")[-1]["modulo"] == {"discounts[0][coupon]": "tarots_rinnovo_198_eur"}


async def test_col_rinnovo_il_primo_pagamento_e_i_rinnovi_sono_scontati_al_centesimo(come, session, catalogo, stripe):
    await _utente(session, come("utente").identita.principal)
    # Cumulabile (Fase 2d): di default un coupon non si somma allo sconto del rinnovo, e qui varrebbe il rinnovo.
    r = await come("admin").post("/admin/coupons", json={"code": "DIECI", "tipo": "percentuale", "valore": 10,
                                                         "cumulabile": True})
    assert r.status_code == 201, r.text
    r = await come("utente").post("/me/checkout", json={"piano": "mensile-base", "coupon": "dieci"})
    # 9,90 € − 20% rinnovo (1,98) − 10% coupon (0,99) = 6,93 €: un solo coupon d'una volta da 2,97 €.
    assert (r.json()["importo"], r.json()["sconto_rinnovo"], r.json()["sconto"]) == (693, 198, 99)
    once = [c for c in stripe.coupon.values() if c.get("duration") == "once"][-1]
    assert (once["amount_off"], once["duration"]) == ("297", "once")
    checkout_id = r.json()["checkout_id"]
    await _invia(come("utente"), _evento("checkout.session.completed", {
        "id": "cs_c", "mode": "subscription", "payment_status": "paid", "subscription": "sub_c", "invoice": "in_c",
        "client_reference_id": checkout_id, "metadata": {"tipo": "piano", "checkout_id": checkout_id},
    }))
    abbonamento = (await session.execute(select(Subscription).where(Subscription.external_id == "sub_c"))).scalar_one()
    assert (abbonamento.importo_periodo, abbonamento.sconto_ricorrente, gestione.prossimo_rinnovo(abbonamento)) == (693, 198, 792)


async def test_l_email_parte_una_volta_e_senza_smtp_si_registra(session, principal_utente, posta, monkeypatch):
    from tarot_core.posta import manda
    from tarot_core.settings import get_settings

    utente = await _utente(session, principal_utente)
    valori = {"piano": "Oro", "data": "1 ottobre 2026", "importo": "9,90 €", "giorni": 7}
    assert await manda(session, utente, "pagamento_fallito", "prova:1", valori) == "inviata"
    assert await manda(session, utente, "pagamento_fallito", "prova:1", valori) == "già inviata"
    assert len(posta) == 1
    monkeypatch.setenv("TAROT_SMTP_HOST", "")
    get_settings.cache_clear()
    assert await manda(session, utente, "sospensione", "prova:2", valori) == "non_configurato"
    assert len(posta) == 1


def test_i_modelli_delle_email_ci_sono_in_sei_lingue_e_si_riempiono():
    from tarot_core.posta import invio, modelli

    valori = {"piano": "Oro", "data": "3 ottobre 2026", "importo": "€9.90", "giorni": 7, "sconto": 50, "oggi": "1"}
    for tipo, lingue in modelli.MODELLI.items():
        assert set(lingue) == set(modelli.LINGUE), tipo
        for lingua in modelli.LINGUE:
            email = invio.componi(tipo, lingua, valori, link="https://tarots.chat/profile")
            assert "{" not in email["oggetto"] + email["testo"], (tipo, lingua)
            assert "https://tarots.chat/profile" in email["html"]
    assert invio.importo_in(7500, "EUR", "it") == "75,00 €" and invio.importo_in(7500, "EUR", "en") == "€75.00"


# ---- la prova gratuita ----------------------------------------------------------------------------------------------


async def test_la_prova_registra_la_carta_dura_14_giorni_ed_e_una_sola(come, session, catalogo, posta):
    utente = await _utente(session, come("utente").identita.principal)
    assert (await come("utente").get("/me/billing")).json()["prova"] == {"idonea": True, "motivo": None}
    r = await come("utente").post("/me/prova", json={"piano": "mensile-oro"})
    assert r.status_code == 201 and r.json()["importo"] == 0, r.text
    await come("utente").post(f"/billing/mock/checkout/{r.json()['checkout_id']}/esito", data=RITORNO)

    abbonamento = await GestoreAbbonamenti(session).abbonamento_di(utente.id)
    assert (abbonamento.status, abbonamento.prova, abbonamento.annuale) == ("in_prova", True, True)
    assert round((abbonamento.period_end - abbonamento.period_start).total_seconds() / 86400) == 14
    # 199 € l'anno, −50% per sempre: il primo addebito (e ogni rinnovo) sarà 99,50 €.
    assert (abbonamento.listino, abbonamento.sconto_ricorrente, gestione.prossimo_rinnovo(abbonamento)) == (19900, 9950, 9950)
    assert (await session.execute(select(ProvaGratuita).where(ProvaGratuita.user_id == utente.id))).scalar_one()

    assert (await come("utente").get("/me/billing")).json()["prova"] == {"idonea": False, "motivo": "prova_gia_usata"}
    r = await come("utente").post("/me/prova", json={"piano": "mensile-base"})
    assert r.status_code == 409 and r.json()["detail"]["motivo"] == "prova_gia_usata"


async def test_con_stripe_la_prova_e_un_checkout_con_trial_e_una_per_carta(come, session, catalogo, stripe):
    await _utente(session, come("utente").identita.principal)
    r = await come("utente").post("/me/prova", json={"piano": "mensile-base", "ritorno": "/trial"})
    assert r.status_code == 201, r.text
    modulo = stripe.a("/v1/checkout/sessions")[-1]["modulo"]
    assert modulo["subscription_data[trial_period_days]"] == "14" and modulo["payment_method_collection"] == "always"
    assert modulo["discounts[0][coupon]"] == "tarots_prova_4950_eur"       # 99 € l'anno, −50% per sempre
    assert stripe.coupon["tarots_prova_4950_eur"]["duration"] == "forever"
    stripe.impronte["sub_p1"] = "fp_carta"
    checkout_id = r.json()["checkout_id"]
    r = await _invia(come("utente"), _evento("checkout.session.completed", {
        "id": "cs_p", "mode": "subscription", "payment_status": "no_payment_required", "subscription": "sub_p1",
        "client_reference_id": checkout_id, "metadata": {"tipo": "piano", "checkout_id": checkout_id},
    }))
    assert r.json()["esito"] == "prova attivata"
    prova = (await session.execute(select(ProvaGratuita))).scalar_one()
    assert prova.impronta_carta == "fp_carta"

    # Un altro account con la stessa carta: niente seconda prova, l'abbonamento appena nato si chiude subito.
    await _utente(session, come("altro").identita.principal)
    r = await come("altro").post("/me/prova", json={"piano": "mensile-base"})
    stripe.impronte["sub_p2"] = "fp_carta"
    checkout_id = r.json()["checkout_id"]
    r = await _invia(come("altro"), _evento("checkout.session.completed", {
        "id": "cs_q", "mode": "subscription", "payment_status": "no_payment_required", "subscription": "sub_p2",
        "client_reference_id": checkout_id, "metadata": {"tipo": "piano", "checkout_id": checkout_id},
    }))
    assert r.json()["esito"] == "prova rifiutata: carta_gia_usata"
    assert stripe.a("/v1/subscriptions/sub_p2", "DELETE")
    assert (await come("altro").get(f"/me/checkout/{checkout_id}")).json()["esito"] == "carta_gia_usata"
    assert (await session.execute(select(Subscription).where(Subscription.external_id == "sub_p2"))).scalar_one_or_none() is None


async def test_la_prova_si_converte_in_annuale_scontato_e_il_promemoria_parte_una_volta(session, catalogo, principal_utente, posta):
    from tarot_core.tools.abbonamenti import giro

    utente = await _utente(session, principal_utente)
    oro = (await session.execute(select(Plan).where(Plan.slug == "mensile-oro"))).scalar_one()
    abbonamento = await _abbonamento(session, utente, oro, annuale=True, durata=14, giorni_fa=12.5, stato="in_prova",
                                     prova=True, sconto=9950, importo=0)
    assert await gestione.giro_promemoria_prova(session) == 1
    assert await gestione.giro_promemoria_prova(session) == 0           # idempotente
    await session.commit()
    assert len(posta) == 1 and _oggetti(posta)[0].startswith("La tua prova gratuita finisce il")
    testo = posta[0].get_body(("plain",)).get_content()
    assert "99,50" in testo and "50%" in testo and "/it/trial" in testo

    # Alla fine della prova il cron la converte: annuale, 99,50 €, attivo.
    abbonamento.period_end = utcnow() - timedelta(minutes=1)
    await session.commit()
    assert (await giro(session)).get("rinnovati") == 1
    await session.refresh(abbonamento)
    assert (abbonamento.status, abbonamento.importo_periodo) == ("attivo", 9950)
    assert round((abbonamento.period_end - abbonamento.period_start).total_seconds() / 86400) == 365
    assert _oggetti(posta)[-1] == "Il tuo abbonamento è stato rinnovato"


async def test_una_prova_disdetta_non_riceve_il_promemoria(session, catalogo, principal_utente, posta):
    utente = await _utente(session, principal_utente)
    oro = (await session.execute(select(Plan).where(Plan.slug == "mensile-oro"))).scalar_one()
    abbonamento = await _abbonamento(session, utente, oro, annuale=True, durata=14, giorni_fa=13, stato="in_prova", prova=True)
    abbonamento.cancel_at = abbonamento.period_end
    await session.commit()
    assert await gestione.giro_promemoria_prova(session) == 0 and posta == []


# ---- tolleranza e solleciti -----------------------------------------------------------------------------------------


async def test_tolleranza_solleciti_al_terzo_e_sesto_giorno_poi_sospensione(come, session, catalogo, stripe, posta):
    utente = await _utente(session, come("utente").identita.principal)
    piano = await _piano(session, "dunning", mensile=1000)
    abbonamento = await _abbonamento(session, utente, piano, provider="stripe", external_id="sub_d", sconto=200)

    r = await _invia(come("utente"), _evento("invoice.payment_failed", {"id": "in_d", "subscription": "sub_d"}))
    assert r.json()["esito"] == "abbonamento in_sospeso"
    # Stripe riprova: un secondo fallimento non riapre la tolleranza e non rimanda l'email.
    await _invia(come("utente"), _evento("invoice.payment_failed", {"id": "in_d", "subscription": "sub_d"}))
    await session.refresh(abbonamento)
    fallito = abbonamento.pagamento_fallito_il
    assert abbonamento.status == "in_sospeso" and abbonamento.fattura_aperta == "in_d"
    assert _oggetti(posta) == ["Non siamo riusciti a rinnovare il tuo abbonamento"]
    pagina = (await come("utente").get("/me/abbonamento/pagamento")).json()
    assert pagina == {"provider": "stripe", "store": False, "url": "https://invoice.stripe.com/i/in_d"}

    async def giorno(n: float) -> Dict[str, int]:
        """Il giro orario come se fossero passati `n` giorni dal primo fallimento."""
        conti = await gestione.giro_tolleranza(session, adesso=fallito + timedelta(days=n))
        await session.commit()
        return conti

    assert await giorno(1) == {}
    assert await giorno(3.1) == {"solleciti_3": 1}
    assert await giorno(3.2) == {}
    assert await giorno(6.1) == {"solleciti_6": 1}
    assert await giorno(7.01) == {"sospesi": 1}
    await session.refresh(abbonamento)
    assert abbonamento.status == "sospeso"
    assert _oggetti(posta)[1:] == [
        "Promemoria: il pagamento del tuo abbonamento è ancora in sospeso",
        "Promemoria: il pagamento del tuo abbonamento è ancora in sospeso",
        "Il tuo abbonamento è sospeso",
    ]
    assert fallito is not None
    # Stripe dice ancora past_due: la tolleranza chiusa qui non si riapre.
    await _invia(come("utente"), _evento("customer.subscription.updated", {
        "id": "sub_d", "status": "past_due", "cancel_at_period_end": False,
    }))
    await session.refresh(abbonamento)
    assert abbonamento.status == "sospeso"

    # Pagata la fattura aperta: di nuovo attivo, niente più tolleranza.
    await _invia(come("utente"), _evento("invoice.paid", {
        "id": "in_d", "billing_reason": "subscription_cycle", "subscription": "sub_d", "amount_paid": 800,
    }))
    await session.refresh(abbonamento)
    assert (abbonamento.status, abbonamento.fattura_aperta, abbonamento.pagamento_fallito_il) == ("attivo", None, None)


async def test_il_simulatore_ha_la_sua_fattura_aperta_e_la_sua_pagina(come, session, catalogo, posta, monkeypatch):
    from tarot_core.settings import get_settings
    from tarot_core.tools.abbonamenti import giro

    monkeypatch.setenv("TAROT_BILLING_MOCK_RENEWAL_FAILS", "true")
    get_settings.cache_clear()
    utente = await _utente(session, come("utente").identita.principal)
    piano = await _piano(session, "simulato", mensile=1000)
    abbonamento = await _abbonamento(session, utente, piano, giorni_fa=30.01)
    assert await giro(session) == {"in_tolleranza": 1}
    pagina = (await come("utente").get("/me/abbonamento/pagamento")).json()
    assert pagina["url"].endswith(f"/billing/mock/fattura/mock_in_{abbonamento.id.hex[:12]}")
    r = await come("utente").post(f"/billing/mock/fattura/mock_in_{abbonamento.id.hex[:12]}/esito",
                                  data={"esito": "paga", "ritorno": "http://localhost:3000/profile"})
    assert r.status_code == 303
    await session.refresh(abbonamento)
    assert (abbonamento.status, abbonamento.fattura_aperta) == ("attivo", None)


# ---- nessun doppio addebito -----------------------------------------------------------------------------------------


async def test_con_una_fattura_aperta_non_si_apre_nessun_nuovo_pagamento_di_abbonamento(come, session, catalogo, stripe):
    utente = await _utente(session, come("utente").identita.principal)
    piano = await _piano(session, "aperta", mensile=1000, rank=5)
    abbonamento = await _abbonamento(session, utente, piano, provider="stripe", external_id="sub_a", stato="in_sospeso")
    abbonamento.fattura_aperta = "in_aperta"
    await session.commit()
    sessioni = len(stripe.a("/v1/checkout/sessions"))

    r = await come("utente").post("/me/checkout", json={"piano": "mensile-oro"})
    assert r.status_code == 409 and r.json()["detail"]["motivo"] == "fattura_aperta"
    r = await come("utente").post("/me/abbonamento/cambio", json={"piano": "mensile-oro"})
    assert r.status_code == 409 and r.json()["detail"]["motivo"] == "fattura_aperta"
    r = await come("utente").post("/me/prova", json={"piano": "mensile-oro"})
    assert r.status_code == 409
    assert len(stripe.a("/v1/checkout/sessions")) == sessioni         # nessun checkout aperto
    # I crediti si comprano lo stesso: non toccano l'abbonamento.
    assert (await come("utente").post("/me/checkout", json={"piano": "pacchetto-5"})).status_code == 201


async def test_con_un_abbonamento_attivo_si_cambia_piano_non_se_ne_apre_un_secondo(come, session, catalogo):
    utente = await _utente(session, come("utente").identita.principal)
    base = (await session.execute(select(Plan).where(Plan.slug == "mensile-base"))).scalar_one()
    await _abbonamento(session, utente, base)
    r = await come("utente").post("/me/checkout", json={"piano": "mensile-oro"})
    assert r.status_code == 409 and r.json()["detail"]["motivo"] == "abbonamento_attivo"


# ---- la console -----------------------------------------------------------------------------------------------------


async def test_la_console_cambia_le_impostazioni_con_audit(come, session, catalogo):
    assert (await come("utente").get("/admin/abbonamenti/impostazioni")).status_code == 403
    r = await come("admin").get("/admin/abbonamenti/impostazioni")
    assert r.json() == {"sconto_rinnovo": 20, "sconto_prova": 50, "giorni_prova": 14, "giorni_tolleranza": 7,
                        "giorni_promemoria_prova": 2, "condoni_per_periodo": 2, "banner_prova": True}
    r = await come("admin").put("/admin/abbonamenti/impostazioni", json={"sconto_rinnovo": 25, "banner_prova": False})
    assert r.status_code == 200 and r.json()["sconto_rinnovo"] == 25
    assert (await come("admin").put("/admin/abbonamenti/impostazioni", json={"sconto_rinnovo": 95})).status_code == 422
    voce = (await session.execute(select(AuditLog).where(AuditLog.action == "abbonamenti.impostazioni"))).scalar_one()
    assert voce.before["sconto_rinnovo"] == 20 and voce.after["sconto_rinnovo"] == 25
    pubblico = (await come("utente").get("/abbonamenti/pubblico")).json()
    assert pubblico["banner_prova"] is False and pubblico["sconto_rinnovo"] == 25
    piani = {p["slug"]: p for p in (await come("utente").get("/plans")).json()}
    assert piani["mensile-base"]["prezzi"]["mensile"] == {"listino": 990, "con_rinnovo": 742, "sconto": 248}


async def test_la_console_elenca_per_stato_e_agisce_con_audit(come, session, catalogo, posta):
    utente = await _utente(session, come("utente").identita.principal)
    altro = await _utente(session, come("altro").identita.principal)
    piano = await _piano(session, "console", mensile=1000)
    in_sospeso = await _abbonamento(session, utente, piano, stato="in_sospeso")
    attivo = await _abbonamento(session, altro, piano)

    r = await come("admin").get("/admin/abbonamenti", params={"stato": "in_sospeso"})
    assert r.status_code == 200
    corpo = r.json()
    assert [a["id"] for a in corpo["abbonamenti"]] == [str(in_sospeso.id)]
    assert corpo["conteggi"]["in_sospeso"] == 1 and corpo["conteggi"]["attivo"] == 1
    assert set(corpo["abbonamenti"][0]["azioni"]) == {"rinnovo_spento", "sospendi", "proroga", "chiudi"}
    assert (await come("admin").get("/admin/abbonamenti", params={"q": "altro@"})).json()["totale"] == 1

    r = await come("admin").post(f"/admin/abbonamenti/{in_sospeso.id}/azione", json={"azione": "sospendi", "motivo": "nessuna risposta"})
    assert r.status_code == 200 and r.json()["stato"] == "sospeso"
    fine = attivo.period_end
    r = await come("admin").post(f"/admin/abbonamenti/{attivo.id}/azione", json={"azione": "proroga", "giorni": 5, "motivo": "disservizio"})
    assert r.status_code == 200
    await session.refresh(attivo)
    assert attivo.period_end - fine == timedelta(days=5)
    r = await come("admin").post(f"/admin/abbonamenti/{attivo.id}/azione", json={"azione": "chiudi", "motivo": "frode"})
    assert r.status_code == 200 and r.json()["stato"] == "disdetto"
    r = await come("admin").post(f"/admin/abbonamenti/{attivo.id}/azione", json={"azione": "proroga", "giorni": 1, "motivo": "x x"})
    assert r.status_code == 409
    azioni = {a.action for a in (await session.execute(select(AuditLog).where(AuditLog.action.like("subscription.admin.%")))).scalars()}
    assert azioni == {"subscription.admin.sospendi", "subscription.admin.proroga", "subscription.admin.chiudi"}


async def test_la_console_scrive_i_limiti_nuovi_dei_piani(come, catalogo):
    r = await come("admin").patch("/admin/plans/mensile-base", json={
        "letture_alla_settimana": 12, "letture_al_mese": 40, "letture_totali": -1,
    })
    assert r.status_code == 200, r.text
    assert r.json()["limiti"] == {"letture_al_giorno": 3, "letture_alla_settimana": 12, "letture_al_mese": 40, "letture_totali": -1}
    r = await come("admin").post("/admin/plans", json={
        "slug": "nuovo-limiti", "name": "Nuovo", "tipo": "abbonamento", "price_monthly": 500, "letture_al_giorno": 2,
        "letture_al_mese": 30,
    })
    assert r.status_code == 201 and r.json()["limiti"] == {"letture_al_giorno": 2, "letture_al_mese": 30}


# ---- la commissione di referral sugli abbonamenti -------------------------------------------------------------------


def test_la_commissione_si_converte_al_prezzo_del_pacchetto_piu_economico():
    from tarot_core.billing.referral import crediti_della_commissione

    assert crediti_della_commissione(8000, 20, 100, 1) == 16          # l'esempio: 80 € → 16 € → 16 crediti da 1 €
    assert crediti_della_commissione(8000, 20, 490, 5) == 16          # 16 € / 0,98 € = 16,33 → 16
    assert crediti_della_commissione(250, 20, 490, 5) == 1            # 0,50 € / 0,98 € = 0,51 → 1
    assert crediti_della_commissione(200, 20, 490, 5) == 0            # 0,40 € / 0,98 € = 0,41 → 0
    assert crediti_della_commissione(0, 20, 490, 5) == 0


async def _invito(session, invitante_p, invitato_p):
    invitante = await _utente(session, invitante_p)
    invitato = await _utente(session, invitato_p)
    invitato.referred_by = invitante.id
    await session.commit()
    return invitante, invitato


async def test_commissione_su_prova_conversione_upgrade_e_mai_stornata(come, session, catalogo, principal_utente, principal_altro):
    from tarot_core.billing.pagamenti import STORNO, EventoPagamento, GestorePagamenti, PagamentiSimulati

    await _azzera_regalo(session)
    invitante, invitato = await _invito(session, principal_utente, principal_altro)
    saldo = RegistroCrediti(session).saldo

    # La prova gratuita non paga: nessuna commissione.
    r = await come("altro").post("/me/prova", json={"piano": "mensile-oro"})
    await come("altro").post(f"/billing/mock/checkout/{r.json()['checkout_id']}/esito", data=RITORNO)
    assert await saldo(invitante.id) == 0

    # La conversione paga 99,50 €: 20% = 19,90 € → 19,90 / 0,98 = 20,3 → 20 crediti.
    abbonamento = await GestoreAbbonamenti(session).abbonamento_di(invitato.id)
    abbonamento.period_start = utcnow() - timedelta(days=14)
    abbonamento.period_end = utcnow() - timedelta(minutes=1)
    await session.commit()
    await GestoreAbbonamenti(session, PagamentiSimulati()).rinnova(abbonamento)
    await session.commit()
    assert abbonamento.importo_periodo == 9950 and await saldo(invitante.id) == 20

    # Un rimborso all'invitato non tocca la commissione di chi l'ha invitato.
    gestore = GestorePagamenti(session, PagamentiSimulati())
    await gestore.applica(EventoPagamento(id=f"evt_{uuid.uuid4().hex}", tipo=STORNO, dati={
        "riferimenti": [f"rinnovo:{abbonamento.id}"], "causa": "rimborso",
    }))
    await session.commit()
    assert await saldo(invitante.id) == 20

    # Un upgrade paga la commissione sul conguaglio pagato davvero.
    top = await _piano(session, "altissimo", mensile=5000, annuale=50000, rank=99)
    r = await come("altro").post("/me/abbonamento/cambio", json={"piano": top.slug, "annuale": True})
    assert r.status_code == 200, r.text
    totale = r.json()["importo"]
    await come("altro").post(f"/billing/mock/checkout/{r.json()['checkout_id']}/esito", data=RITORNO)
    from tarot_core.billing.referral import crediti_della_commissione

    assert await saldo(invitante.id) == 20 + crediti_della_commissione(totale, 20, 490, 5)
    vecchio = await session.get(Subscription, abbonamento.id)
    await session.refresh(vecchio)
    assert vecchio.status == "disdetto"


async def test_una_prova_rifiutata_non_consuma_il_coupon(come, session, catalogo, stripe):
    """Ritocco della Fase 4: la prova rifiutata (carta già usata) non registra l'uso del coupon, così un codice monouso
    resta buono per un acquisto vero. Prima l'uso si registrava prima del controllo e il codice andava perso."""
    from tarot_core.domain.billing_models import Coupon, CouponRedemption

    session.add(Coupon(code="MONOUSO", tipo="percentuale", valore=10, max_riscatti=1, durata="sempre", cumulabile=True))
    await session.commit()
    await _utente(session, come("utente").identita.principal)
    r = await come("utente").post("/me/prova", json={"piano": "mensile-base"})
    stripe.impronte["sub_c1"] = "fp_condivisa"
    checkout_id = r.json()["checkout_id"]
    await _invia(come("utente"), _evento("checkout.session.completed", {
        "id": "cs_c1", "mode": "subscription", "payment_status": "no_payment_required", "subscription": "sub_c1",
        "client_reference_id": checkout_id, "metadata": {"tipo": "piano", "checkout_id": checkout_id},
    }))

    await _utente(session, come("altro").identita.principal)
    r = await come("altro").post("/me/prova", json={"piano": "mensile-base", "coupon": "MONOUSO"})
    assert r.status_code == 201, r.text
    checkout_id = r.json()["checkout_id"]
    assert (await session.get(PaymentCheckout, uuid.UUID(checkout_id))).coupon_id is not None
    stripe.impronte["sub_c2"] = "fp_condivisa"
    r = await _invia(come("altro"), _evento("checkout.session.completed", {
        "id": "cs_c2", "mode": "subscription", "payment_status": "no_payment_required", "subscription": "sub_c2",
        "client_reference_id": checkout_id, "metadata": {"tipo": "piano", "checkout_id": checkout_id},
    }))
    assert r.json()["esito"] == "prova rifiutata: carta_gia_usata"
    coupon = (await session.execute(select(Coupon).where(Coupon.code == "MONOUSO"))).scalar_one()
    await session.refresh(coupon)
    assert coupon.riscatti == 0
    assert (await session.execute(select(CouponRedemption).where(CouponRedemption.coupon_id == coupon.id))).first() is None
