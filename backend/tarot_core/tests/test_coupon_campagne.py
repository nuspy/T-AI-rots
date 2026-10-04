"""I coupon della Fase 2d: durata sui rinnovi («per N periodi», «per sempre»), cumulo con il rinnovo automatico e la
prova (il più alto, o la somma al centesimo), lotti monouso con il CSV, il link che applica il codice, il resoconto per
coupon e per campagna, il limite dei tentativi a caso.

Stripe è finto (`httpx.MockTransport`, gli stessi attrezzi di `test_abbonamenti.py`), il simulatore paga da sé, il
modello è finto: nessuna prova parla con un servizio vero.
"""
from __future__ import annotations

import csv
import io
from datetime import timedelta

import pytest
from sqlalchemy import select, update

from tarot_core.billing import offerte
from tarot_core.domain.base import utcnow
from tarot_core.domain.billing_models import Coupon, CouponRedemption, Plan, Subscription
from tarot_core.domain.models import User
from tarot_core.domain.repositories import UserRepository

from .conftest import richiede_database
from .test_abbonamenti import StripeFinto, posta, stripe  # noqa: F401  (gli attrezzi di Stripe e dell'SMTP finti)
from .test_stripe import _evento, _invia

pytestmark = richiede_database

RITORNO = {"esito": "paga", "ritorno": "http://localhost:3000/pricing"}


@pytest.fixture(autouse=True)
def _senza_tentativi():
    from tarot_core.api.routers import billing

    billing._TENTATIVI.clear()
    yield
    billing._TENTATIVI.clear()


@pytest.fixture
def come(client, principal_utente, principal_altro, principal_admin):
    def scegli(chi: str):
        client.identita.principal = {
            "admin": principal_admin, "altro": principal_altro, "anonimo": None,
        }.get(chi, principal_utente)
        return client

    return scegli


async def _utente(session, principal):
    utente = await UserRepository(session).ensure(principal)
    await session.commit()
    return utente


async def _coupon(c, **campi):
    r = await c.post("/admin/coupons", json={"tipo": "percentuale", "valore": 20, **campi})
    assert r.status_code == 201, r.text
    return r.json()


async def _paga_simulato(c, checkout_id):
    r = await c.post(f"/billing/mock/checkout/{checkout_id}/esito", data=RITORNO)
    assert r.status_code in (200, 303), r.text


async def _abbonamento_di(session, user_id) -> Subscription:
    return (await session.execute(
        select(Subscription).where(Subscription.user_id == user_id, Subscription.status.in_(("attivo", "in_prova")))
        .order_by(Subscription.created_at.desc()).limit(1)
    )).scalar_one()


async def _fine_periodo(session, abbonamento):
    abbonamento.period_start = utcnow() - timedelta(days=31)
    abbonamento.period_end = utcnow() - timedelta(minutes=1)
    await session.commit()


async def _completa_stripe(c, checkout_id, sub, invoice="in_1", pagato="paid"):
    r = await _invia(c, _evento("checkout.session.completed", {
        "id": f"cs_{sub}", "mode": "subscription", "payment_status": pagato, "subscription": sub, "invoice": invoice,
        "client_reference_id": checkout_id, "metadata": {"tipo": "piano", "checkout_id": checkout_id},
    }))
    assert r.status_code == 200, r.text
    return r


async def _rinnovo_stripe(c, sub, fattura, importo, giorni=60):
    """L'`invoice.paid` di un ciclo: la fine del periodo nuovo dopo quella di adesso (`giorni`; la stessa per lo
    stesso incasso rimandato)."""
    fine = int((utcnow().replace(microsecond=0, second=0, minute=0) + timedelta(days=giorni)).timestamp())
    r = await _invia(c, _evento("invoice.paid", {
        "id": fattura, "billing_reason": "subscription_cycle", "subscription": sub, "amount_paid": importo,
        "lines": {"data": [{"period": {"end": fine}}]},
    }))
    assert r.status_code == 200, r.text


def _sconti_su(stripe_finto, sub):
    return [r["modulo"].get("discounts[0][coupon]", r["modulo"].get("discounts"))
            for r in stripe_finto.a(f"/v1/subscriptions/{sub}", "POST") if "discounts" in str(r["modulo"])]


# ---- la composizione, a mano ---------------------------------------------------------------------------------------


def _finto(**campi) -> offerte.Sconto:
    c = Coupon(code="X", tipo=campi.pop("tipo", "percentuale"), valore=campi.pop("valore"),
               durata=campi.pop("durata", "una_volta"), periodi=campi.pop("periodi", None),
               cumulabile=campi.pop("cumulabile", False))
    return offerte.Sconto(coupon=c, listino=990, sconto=offerte.sconto_su(c, 990), finale=0)


def test_non_cumulabile_vince_il_piu_alto_e_a_pari_merito_il_rinnovo():
    # 9,90 € col rinnovo (−20% = 1,98): un coupon del 30% (2,97) vince, uno del 10% (0,99) no, uno del 20% nemmeno.
    vince = offerte.componi(990, base=198, valutato=_finto(valore=30))
    assert (vince.applicato, vince.vince, vince.sconto, vince.importo, vince.extra_coupon) == (True, "coupon", 297, 693, 99)
    perde = offerte.componi(990, base=198, valutato=_finto(valore=10))
    assert (perde.applicato, perde.vince, perde.importo, perde.to_dict()["nota"]) == (False, "rinnovo", 792, "coupon_non_cumulabile")
    pari = offerte.componi(990, base=198, valutato=_finto(valore=20))
    assert (pari.applicato, pari.importo) == (False, 792)


def test_cumulabile_somma_al_centesimo_sul_listino():
    # 20% (1,98) + 13% di 9,90 = 1,287 → 1,29: 6,63 €.
    c = offerte.componi(990, base=198, valutato=_finto(valore=13, cumulabile=True))
    assert (c.vince, c.sconto, c.importo, c.extra_coupon) == ("entrambi", 327, 663, 129)
    # Senza rinnovo automatico non c'è niente da sommare né rinnovi da scontare.
    senza = offerte.componi(990, base=0, valutato=_finto(valore=13, cumulabile=True), rinnovo=False)
    assert (senza.vince, senza.importo, senza.sconto_ricorrente) == ("coupon", 861, 0)


def test_la_durata_decide_i_rinnovi_scontati():
    una = offerte.componi(990, base=198, valutato=_finto(valore=30))
    assert (una.rinnovi_coupon, una.sconto_ricorrente) == (0, 198)
    tre = offerte.componi(990, base=198, valutato=_finto(valore=30, durata="periodi", periodi=3))
    assert (tre.rinnovi_coupon, tre.sconto_ricorrente) == (2, 297)
    sempre = offerte.componi(990, base=198, valutato=_finto(valore=30, durata="sempre"))
    assert (sempre.rinnovi_coupon, sempre.sconto_ricorrente) == (None, 297)
    # Con la prova il primo pagamento è la conversione: «una volta» sconta quella.
    prova = offerte.componi(9900, base=4950, valutato=_finto(valore=10, cumulabile=True), prova=True)
    assert (prova.importo, prova.rinnovi_coupon, prova.sconto_ricorrente, prova.extra_coupon) == (0, 1, 5940, 0)


def test_un_abbonamento_non_si_azzera_nemmeno_sommando():
    with pytest.raises(offerte.CouponNonValido):
        offerte.componi(990, base=198, valutato=_finto(valore=90, cumulabile=True))


# ---- durata sui rinnovi ----------------------------------------------------------------------------------------------


async def test_per_n_periodi_sconta_i_primi_rinnovi_poi_torna_al_rinnovo(come, session, catalogo):
    from tarot_core.tools.abbonamenti import giro

    utente = await _utente(session, come("utente").identita.principal)
    await _coupon(come("admin"), code="TRE-MESI", valore=30, durata="periodi", periodi=3)
    r = await come("utente").post("/me/checkout", json={"piano": "mensile-base", "coupon": "tre-mesi"})
    assert r.status_code == 201, r.text
    # Non cumulabile: −30% (2,97) contro −20% del rinnovo (1,98): vale il coupon.
    assert (r.json()["importo"], r.json()["coupon"]["vince"]) == (693, "coupon")
    await _paga_simulato(come("utente"), r.json()["checkout_id"])
    abbonamento = await _abbonamento_di(session, utente.id)
    assert (abbonamento.sconto_ricorrente, abbonamento.sconto_base, abbonamento.coupon_rinnovi_rimasti) == (297, 198, 2)
    profilo = (await come("utente").get("/me/abbonamento")).json()["abbonamento"]
    assert profilo["coupon"]["rinnovi_rimasti"] == 2 and profilo["prossimo_rinnovo"] == 693

    importi = []
    for _ in range(3):
        await _fine_periodo(session, abbonamento)
        assert (await giro(session)).get("rinnovati") == 1
        await session.refresh(abbonamento)
        importi.append(abbonamento.importo_periodo)
    # Secondo e terzo mese col coupon, il quarto col solo rinnovo automatico.
    assert importi == [693, 693, 792]
    assert abbonamento.coupon_rinnovi_rimasti == 0 and abbonamento.sconto_ricorrente == 198
    assert (await come("utente").get("/me/abbonamento")).json()["abbonamento"]["coupon"] is None
    righe = (await session.execute(select(CouponRedemption).where(CouponRedemption.rinnovo.is_(True)))).scalars().all()
    assert len(righe) == 2 and {r.sconto for r in righe} == {99} and {r.importo for r in righe} == {693}
    # I rinnovi scontati non sono usi del codice.
    assert (await session.get(Coupon, righe[0].coupon_id)).riscatti == 1


async def test_per_sempre_con_stripe_il_rinnovo_costa_quanto_mostrato(come, session, catalogo, stripe):
    await _utente(session, come("utente").identita.principal)
    await _coupon(come("admin"), code="SEMPRE10", valore=10, durata="sempre", cumulabile=True)
    r = await come("utente").post("/me/checkout", json={"piano": "mensile-base", "coupon": "SEMPRE10"})
    assert (r.json()["importo"], r.json()["sconto_rinnovo"], r.json()["sconto"]) == (693, 198, 99), r.text
    once = [c for c in stripe.coupon.values() if c.get("duration") == "once"][-1]
    assert once["amount_off"] == "297"                                   # un solo coupon d'una volta, al centesimo
    await _completa_stripe(come("utente"), r.json()["checkout_id"], "sub_s")
    assert _sconti_su(stripe, "sub_s")[-1] == "tarots_sconto_297_eur"    # i rinnovi: rinnovo + coupon, per sempre
    assert stripe.coupon["tarots_sconto_297_eur"]["duration"] == "forever"
    await _rinnovo_stripe(come("utente"), "sub_s", "in_s2", 693)
    abbonamento = (await session.execute(select(Subscription).where(Subscription.external_id == "sub_s"))).scalar_one()
    assert (abbonamento.importo_periodo, abbonamento.sconto_ricorrente, abbonamento.coupon_rinnovi_rimasti) == (693, 297, None)
    assert len(_sconti_su(stripe, "sub_s")) == 1                         # niente da cambiare presso Stripe
    # Lo stesso incasso arrivato due volte non scrive due righe.
    await _rinnovo_stripe(come("utente"), "sub_s", "in_s2", 693)
    assert len((await session.execute(select(CouponRedemption).where(CouponRedemption.rinnovo.is_(True)))).all()) == 1


async def test_per_n_periodi_con_stripe_alla_fine_toglie_lo_sconto_del_coupon(come, session, catalogo, stripe):
    await _utente(session, come("utente").identita.principal)
    await _coupon(come("admin"), code="DUE30", valore=30, durata="periodi", periodi=2)
    r = await come("utente").post("/me/checkout", json={"piano": "mensile-base", "coupon": "DUE30"})
    assert r.json()["importo"] == 693
    await _completa_stripe(come("utente"), r.json()["checkout_id"], "sub_d")
    assert _sconti_su(stripe, "sub_d") == ["tarots_sconto_297_eur"]
    await _rinnovo_stripe(come("utente"), "sub_d", "in_d2", 693)        # il secondo periodo, ancora col coupon
    assert _sconti_su(stripe, "sub_d") == ["tarots_sconto_297_eur", "tarots_rinnovo_198_eur"]
    profilo = (await come("utente").get("/me/abbonamento")).json()["abbonamento"]
    assert profilo["prossimo_rinnovo"] == 792 and profilo["coupon"] is None


# ---- cumulo con il rinnovo e con la prova ----------------------------------------------------------------------------


async def test_non_cumulabile_vale_il_rinnovo_e_il_codice_non_si_consuma(come, session, catalogo):
    await _utente(session, come("utente").identita.principal)
    c = await _coupon(come("admin"), code="DIECI", valore=10)
    utente = come("utente")
    anteprima = (await utente.post("/me/coupon/anteprima", json={"codice": "dieci", "piano": "mensile-base"})).json()
    assert (anteprima["vince"], anteprima["importo"], anteprima["nota"]) == ("rinnovo", 792, "coupon_non_cumulabile")
    r = await utente.post("/me/checkout", json={"piano": "mensile-base", "coupon": "DIECI"})
    assert (r.json()["importo"], r.json()["sconto"]) == (792, 0)
    await _paga_simulato(utente, r.json()["checkout_id"])
    assert (await come("admin").get(f"/admin/coupons/{c['id']}/riscatti")).json()["coupon"]["riscatti"] == 0
    # Senza rinnovo automatico il coupon è l'unico sconto: vale.
    senza = (await come("utente").post("/me/coupon/anteprima", json={
        "codice": "DIECI", "piano": "mensile-base", "rinnovo": False,
    })).json()
    assert (senza["vince"], senza["importo"]) == ("coupon", 891)


async def test_con_la_prova_il_coupon_cumulabile_si_somma_sulla_conversione_poi_resta_la_prova(come, session, catalogo, stripe):
    await _utente(session, come("utente").identita.principal)
    c = await _coupon(come("admin"), code="EXTRA10", valore=10, cumulabile=True, campagna="influencer-x")
    r = await come("utente").post("/me/prova", json={"piano": "mensile-base", "coupon": "extra10"})
    assert r.status_code == 201, r.text
    modulo = stripe.a("/v1/checkout/sessions")[-1]["modulo"]
    # 99 € l'anno: −50% della prova (49,50) + 10% (9,90) = 59,40 € sulla conversione.
    assert modulo["discounts[0][coupon]"] == "tarots_sconto_5940_eur"
    stripe.impronte["sub_pc"] = "fp_pc"
    await _completa_stripe(come("utente"), r.json()["checkout_id"], "sub_pc", invoice=None, pagato="no_payment_required")
    abbonamento = (await session.execute(select(Subscription).where(Subscription.external_id == "sub_pc"))).scalar_one()
    assert (abbonamento.status, abbonamento.sconto_ricorrente, abbonamento.sconto_base, abbonamento.coupon_rinnovi_rimasti) == (
        "in_prova", 5940, 4950, 1)
    # La conversione (il primo incasso): col coupon; dopo, la sola prova per sempre.
    await _rinnovo_stripe(come("utente"), "sub_pc", "in_conv", 3960)
    assert _sconti_su(stripe, "sub_pc")[-1] == "tarots_prova_4950_eur"
    await session.refresh(abbonamento)
    assert (abbonamento.status, abbonamento.importo_periodo, abbonamento.sconto_ricorrente) == ("attivo", 3960, 4950)
    resoconto = (await come("admin").get(f"/admin/coupons/{c['id']}/riscatti")).json()["resoconto"]
    assert (resoconto["riscatti"], resoconto["prove"], resoconto["conversioni_da_prova"]) == (1, 1, 1)
    assert (resoconto["incasso_lordo"], resoconto["sconto_concesso"]) == (3960, 990)


async def test_con_la_prova_un_coupon_non_cumulabile_piu_basso_non_si_usa(come, session, catalogo, stripe):
    await _utente(session, come("utente").identita.principal)
    await _coupon(come("admin"), code="TRENTA", valore=30)
    r = await come("utente").post("/me/prova", json={"piano": "mensile-base", "coupon": "TRENTA"})
    assert r.json()["coupon"]["vince"] == "prova" and r.json()["coupon"]["applicato"] is False
    assert stripe.a("/v1/checkout/sessions")[-1]["modulo"]["discounts[0][coupon]"] == "tarots_prova_4950_eur"


# ---- il link e l'anteprima pubblica ---------------------------------------------------------------------------------


async def test_il_link_applica_il_coupon_anche_senza_account(come, session, catalogo):
    c = await _coupon(come("admin"), code="NEWS-OTT", valore=30, durata="periodi", periodi=3,
                      valido_fino=(utcnow() + timedelta(days=2)).isoformat())
    assert c["link"]["en"].endswith("/pricing?coupon=NEWS-OTT") and c["link"]["it"].endswith("/it/piano?coupon=NEWS-OTT")
    r = await come("anonimo").post("/coupon/anteprima", json={"codice": "news-ott"})
    assert r.status_code == 200, r.text
    corpo = r.json()
    assert corpo["coupon"]["codice"] == "NEWS-OTT" and corpo["coupon"]["periodi"] == 3 and corpo["coupon"]["valido_fino"]
    offerta = {(o["piano"], o["annuale"], o["rinnovo"], o["prova"]): o for o in corpo["offerte"]}
    pacchetto = offerta[("pacchetto-15", False, False, False)]
    assert (pacchetto["listino"], pacchetto["importo"], pacchetto["risparmio"]) == (1290, 903, 387)
    mese = offerta[("mensile-base", False, True, False)]
    assert (mese["importo"], mese["risparmio"], mese["vince"], mese["rinnovi_coupon"]) == (693, 297, "coupon", 2)


async def test_errori_chiari_per_il_link(come, session, catalogo):
    admin = come("admin")
    await _coupon(admin, code="SCADUTO", valido_fino=(utcnow() - timedelta(days=1)).isoformat())
    await _coupon(admin, code="FINITO", max_riscatti=1)
    await session.execute(update(Coupon).where(Coupon.code == "FINITO").values(riscatti=1))
    await session.commit()
    await _coupon(admin, code="SOLOPACK", piani=["pacchetto-5"])
    anonimo = come("anonimo")
    assert (await anonimo.post("/coupon/anteprima", json={"codice": "scaduto"})).json()["detail"]["motivo"] == "coupon_scaduto"
    assert (await anonimo.post("/coupon/anteprima", json={"codice": "FINITO"})).json()["detail"]["motivo"] == "coupon_esaurito"
    offerte_ = (await anonimo.post("/coupon/anteprima", json={"codice": "solopack"})).json()["offerte"]
    motivi = {o["piano"]: o.get("motivo") for o in offerte_}
    assert motivi["pacchetto-5"] is None and motivi["pacchetto-15"] == "coupon_non_per_questo_piano"


async def test_chi_prova_codici_a_caso_si_ferma_per_ip_anche_senza_account(come, session, catalogo):
    anonimo = come("anonimo")
    for i in range(10):
        assert (await anonimo.post("/coupon/anteprima", json={"codice": f"ACASO{i}"})).status_code == 422
    r = await anonimo.post("/coupon/anteprima", json={"codice": "ANCORA"})
    assert r.status_code == 429 and r.json()["detail"]["motivo"] == "troppi_tentativi" and r.headers["retry-after"]
    # Lo stesso indirizzo, entrato con un account: fermo anche lui (il limite vale per persona o per IP).
    r = await come("utente").post("/me/coupon/riscatta", json={"codice": "ALTRO"})
    assert r.status_code == 429
    # Un codice che esiste ma non vale non è un tentativo a caso: non conta.
    from tarot_core.api.routers import billing

    billing._TENTATIVI.clear()
    await _coupon(come("admin"), code="SPENTO", attivo=False)
    for _ in range(12):
        assert (await come("anonimo").post("/coupon/anteprima", json={"codice": "spento"})).status_code == 422


# ---- lotti monouso, campagne e resoconto ----------------------------------------------------------------------------


async def test_un_lotto_genera_codici_monouso_con_la_campagna_e_si_esporta(come, session, catalogo):
    admin = come("admin")
    r = await admin.post("/admin/coupon-lotti", json={
        "prefisso": "news", "quantita": 5, "campagna": "newsletter-ottobre", "tipo": "importo", "valore": 200,
    })
    assert r.status_code == 201, r.text
    lotto = r.json()
    assert lotto["prefisso"] == "NEWS" and lotto["quantita"] == 5 and lotto["attivi"] == 5
    # L'elenco dei coupon non si riempie dei codici del lotto: stanno sotto il lotto.
    assert all(c["lotto_id"] is None for c in (await admin.get("/admin/coupons")).json())
    codici = (await admin.get(f"/admin/coupons?lotto={lotto['id']}")).json()
    assert len(codici) == 5 and len({c["codice"] for c in codici}) == 5
    assert all(c["codice"].startswith("NEWS-") and c["max_riscatti"] == 1 and c["campagna"] == "newsletter-ottobre"
               for c in codici)

    await _utente(session, come("utente").identita.principal)
    await _utente(session, come("altro").identita.principal)
    primo = codici[0]["codice"]
    r = await come("utente").post("/me/checkout", json={"piano": "pacchetto-15", "coupon": primo.lower()})
    assert r.json()["importo"] == 1090
    await _paga_simulato(come("utente"), r.json()["checkout_id"])
    r = await come("altro").post("/me/coupon/anteprima", json={"codice": primo, "piano": "pacchetto-15"})
    assert r.status_code == 422 and r.json()["detail"]["motivo"] == "coupon_esaurito"

    r = await come("admin").get(f"/admin/coupon-lotti/{lotto['id']}/csv")
    assert r.status_code == 200 and r.headers["content-type"].startswith("text/csv")
    righe = list(csv.reader(io.StringIO(r.text.lstrip("﻿"))))
    assert righe[0] == ["codice", "campagna", "stato", "usato_il", "link"] and len(righe) == 6
    stati = {riga[0]: riga[2] for riga in righe[1:]}
    assert stati[primo] == "usato" and list(stati.values()).count("attivo") == 4
    assert all("/pricing?coupon=NEWS-" in riga[4] for riga in righe[1:])

    r = await come("admin").patch(f"/admin/coupon-lotti/{lotto['id']}", json={"attivo": False})
    assert r.json()["attivi"] == 0
    elenco = (await come("admin").get("/admin/coupon-lotti")).json()
    assert elenco[0]["usati"] == 1 and elenco[0]["regole"]["valore"] == 200


async def test_un_lotto_incoerente_si_rifiuta(come, catalogo):
    admin = come("admin")
    base = {"prefisso": "OK", "quantita": 2, "campagna": "x", "valore": 10}
    assert (await admin.post("/admin/coupon-lotti", json={**base, "prefisso": "con spazio!"})).status_code == 422
    assert (await admin.post("/admin/coupon-lotti", json={**base, "quantita": 0})).status_code == 422
    assert (await admin.post("/admin/coupon-lotti", json={**base, "quantita": offerte.MAX_LOTTO + 1})).status_code == 422
    assert (await admin.post("/admin/coupon-lotti", json={**base, "durata": "periodi"})).status_code == 422


async def test_il_resoconto_per_campagna(come, session, catalogo):
    admin = come("admin")
    await _coupon(admin, code="NEWS-A", tipo="importo", valore=100, campagna="newsletter")
    await _coupon(admin, code="NEWS-B", tipo="percentuale", valore=10, campagna="newsletter")
    await _coupon(admin, code="SOLO", tipo="importo", valore=100)
    await _coupon(admin, code="REGALO", tipo="crediti", valore=5, campagna="newsletter")
    utente = await _utente(session, come("utente").identita.principal)
    vecchio = await _utente(session, come("altro").identita.principal)
    # Un account nato prima della campagna non è un «nuovo utente».
    await session.execute(update(User).where(User.id == vecchio.id).values(created_at=utcnow() - timedelta(days=90)))
    await session.commit()
    for chi, codice in (("utente", "NEWS-A"), ("altro", "NEWS-B")):
        r = await come(chi).post("/me/checkout", json={"piano": "pacchetto-15", "coupon": codice})
        await _paga_simulato(come(chi), r.json()["checkout_id"])
    assert (await come("utente").post("/me/coupon/riscatta", json={"codice": "regalo"})).status_code == 200

    corpo = (await come("admin").get("/admin/coupon-campagne")).json()
    campagne = {c["campagna"]: c for c in corpo["campagne"]}
    news = campagne["newsletter"]
    assert (news["coupon"], news["riscatti"], news["crediti_regalati"]) == (3, 3, 5)
    assert news["incasso_lordo"] == (1290 - 100) + (1290 - 129)
    assert news["sconto_concesso"] == 100 + 129
    assert news["nuovi_utenti"] == 1 and utente.id
    assert campagne[None]["coupon"] == 1 and campagne[None]["riscatti"] == 0
    assert corpo["totale"]["riscatti"] == 3
    # Anche nell'elenco, coupon per coupon.
    elenco = {c["codice"]: c for c in (await come("admin").get("/admin/coupons?resoconto=true")).json()}
    assert elenco["NEWS-A"]["resoconto"]["incasso_lordo"] == 1190


# ---- regole che non cambiano dopo il primo uso ----------------------------------------------------------------------


async def test_durata_e_cumulo_si_fissano_al_primo_uso(come, session, catalogo):
    admin = come("admin")
    c = await _coupon(admin, code="FISSO", tipo="importo", valore=100)
    r = await admin.patch(f"/admin/coupons/{c['id']}", json={"durata": "periodi", "periodi": 3, "cumulabile": True,
                                                             "campagna": " estate "})
    assert r.status_code == 200 and (r.json()["durata"], r.json()["periodi"], r.json()["cumulabile"], r.json()["campagna"]) == (
        "periodi", 3, True, "estate")
    await _utente(session, come("utente").identita.principal)
    r = await come("utente").post("/me/checkout", json={"piano": "pacchetto-5", "coupon": "FISSO"})
    await _paga_simulato(come("utente"), r.json()["checkout_id"])
    admin = come("admin")
    assert (await admin.patch(f"/admin/coupons/{c['id']}", json={"cumulabile": False})).status_code == 409
    assert (await admin.patch(f"/admin/coupons/{c['id']}", json={"campagna": "autunno"})).status_code == 200
    assert (await admin.post("/admin/coupons", json={"tipo": "crediti", "valore": 5, "durata": "sempre"})).status_code == 422
    assert (await admin.post("/admin/coupons", json={"tipo": "percentuale", "valore": 5, "durata": "periodi"})).status_code == 422
