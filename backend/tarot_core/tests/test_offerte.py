"""Le offerte commerciali attraverso l'API: piani (creare, eliminare), coupon di sconto, codici regalo, regali di crediti."""
from __future__ import annotations

from datetime import timedelta

import pytest
from sqlalchemy import select

from tarot_core.billing.credits import RegistroCrediti
from tarot_core.domain.base import utcnow
from tarot_core.domain.models import AuditLog
from tarot_core.domain.repositories import UserRepository

from .conftest import richiede_database

pytestmark = richiede_database

RITORNO = {"esito": "paga", "ritorno": "http://localhost:3000/piano"}


@pytest.fixture(autouse=True)
def _senza_tentativi():
    from tarot_core.api.routers import billing

    billing._TENTATIVI.clear()
    yield
    billing._TENTATIVI.clear()


@pytest.fixture
def come(client, principal_utente, principal_admin):
    """Cambia chi fa le richieste: `come("admin")` o `come("utente")`."""

    def scegli(chi: str):
        client.identita.principal = principal_admin if chi == "admin" else principal_utente
        return client

    return scegli


async def _utente(session, principal):
    utente = await UserRepository(session).ensure(principal)
    await session.commit()
    return utente


async def _piano(c, slug="prova-mese", **campi):
    r = await c.post("/admin/plans", json={"slug": slug, "name": "Prova", **campi})
    assert r.status_code == 201, r.text
    return r.json()


async def _coupon(c, **campi):
    corpo = {"tipo": "percentuale", "valore": 20, **campi}
    r = await c.post("/admin/coupons", json=corpo)
    assert r.status_code == 201, r.text
    return r.json()


async def _anteprima(c, codice, piano="pacchetto-15", annuale=False):
    return await c.post("/me/coupon/anteprima", json={"codice": codice, "piano": piano, "annuale": annuale})


async def _paga(c, checkout_id):
    r = await c.post(f"/billing/mock/checkout/{checkout_id}/esito", data=RITORNO)
    assert r.status_code in (200, 303), r.text


# ---- i piani ---------------------------------------------------------------------------------------------------------


async def test_solo_un_amministratore_gestisce_le_offerte(come, catalogo):
    utente = come("utente")
    assert (await utente.post("/admin/plans", json={"slug": "x-y", "name": "X"})).status_code == 403
    assert (await utente.get("/admin/coupons")).status_code == 403
    assert (await utente.post("/admin/users/1/regalo", json={"crediti": 5})).status_code == 403


async def test_si_crea_un_abbonamento_e_compare_nel_catalogo_pubblico(come, catalogo):
    admin = come("admin")
    p = await _piano(admin, slug="mensile-prova", price_monthly=990, price_yearly=9900, letture_al_giorno=5, rank=15)
    assert p["tipo"] == "abbonamento" and p["limiti"] == {"letture_al_giorno": 5} and p["usi"] == 0
    pubblico = {x["slug"]: x for x in (await admin.get("/plans")).json()}
    assert pubblico["mensile-prova"]["prezzo_mensile"] == 990 and pubblico["mensile-prova"]["limiti"]["letture_al_giorno"] == 5
    # Un piano disattivato sparisce dalla vendita ma resta nella console.
    await admin.patch("/admin/plans/mensile-prova", json={"active": False, "rank": 3})
    assert "mensile-prova" not in {x["slug"] for x in (await admin.get("/plans")).json()}
    piani = {x["slug"]: x for x in (await admin.get("/admin/plans")).json()}
    assert piani["mensile-prova"]["attivo"] is False and piani["mensile-prova"]["rango"] == 3


async def test_si_crea_un_pacchetto_di_crediti(come, catalogo):
    admin = come("admin")
    p = await _piano(admin, slug="pacchetto-100", name="100 letture", tipo="pacchetto", price_monthly=5900, credits_per_period=100)
    assert p["tipo"] == "pacchetto" and p["crediti"] == 100 and p["prezzo_annuale"] == 0 and p["limiti"] == {}


@pytest.mark.parametrize("corpo, quale", [
    ({"slug": "Maiuscole"}, "slug"),
    ({"slug": "-storto-"}, "slug"),
    ({"slug": "a"}, "slug"),
    ({"slug": "senza-crediti", "tipo": "pacchetto", "credits_per_period": 0}, "almeno un credito"),
    ({"slug": "annuale-pack", "tipo": "pacchetto", "credits_per_period": 5, "price_yearly": 100}, "un prezzo solo"),
    ({"slug": "prezzo-negativo", "price_monthly": -1}, "price_monthly"),
    ({"slug": "prezzo-enorme", "price_monthly": 99_999_999}, "price_monthly"),
])
async def test_un_piano_incoerente_si_rifiuta(come, catalogo, corpo, quale):
    r = await come("admin").post("/admin/plans", json={"name": "X", **corpo})
    assert r.status_code == 422 and quale in r.text, r.text


async def test_uno_slug_esistente_si_rifiuta(come, catalogo):
    r = await come("admin").post("/admin/plans", json={"slug": "pacchetto-5", "name": "Doppione"})
    assert r.status_code == 409


async def test_un_piano_mai_usato_si_elimina_uno_usato_no(come, catalogo, session):
    admin = come("admin")
    await _piano(admin, slug="da-eliminare", price_monthly=500)
    assert (await admin.delete("/admin/plans/da-eliminare")).status_code == 204
    assert (await admin.delete("/admin/plans/da-eliminare")).status_code == 404
    # Un pacchetto del catalogo, comprato una volta, non si elimina più.
    utente = come("utente")
    r = await utente.post("/me/checkout", json={"piano": "pacchetto-5"})
    assert r.status_code == 201, r.text
    admin = come("admin")
    r = await admin.delete("/admin/plans/pacchetto-5")
    assert r.status_code == 409 and "disattivalo" in r.json()["detail"]
    piani = {x["slug"]: x for x in (await admin.get("/admin/plans")).json()}
    assert piani["pacchetto-5"]["usi"] == 1


async def test_le_scritture_sui_piani_lasciano_una_traccia(come, catalogo, session):
    admin = come("admin")
    await _piano(admin, slug="tracciato")
    await admin.delete("/admin/plans/tracciato")
    azioni = (await session.execute(select(AuditLog.action).where(AuditLog.target_id == "tracciato"))).scalars().all()
    assert {"plan.create", "plan.delete"} <= set(azioni)


# ---- i coupon: creazione ----------------------------------------------------------------------------------------


async def test_il_codice_si_normalizza_o_si_genera(come, catalogo):
    admin = come("admin")
    c = await _coupon(admin, code=" primavera 10 ")
    assert c["codice"] == "PRIMAVERA10"
    generato = await _coupon(admin)
    assert len(generato["codice"]) == 8 and set(generato["codice"]) <= set("ABCDEFGHJKLMNPQRSTUVWXYZ23456789")
    assert (await admin.post("/admin/coupons", json={"code": "primavera10", "tipo": "importo", "valore": 100})).status_code == 409
    assert {x["codice"] for x in (await admin.get("/admin/coupons")).json()} >= {"PRIMAVERA10", generato["codice"]}


@pytest.mark.parametrize("corpo", [
    {"tipo": "percentuale", "valore": 101},
    {"tipo": "importo", "valore": 0},
    {"tipo": "crediti", "valore": 5, "piani": ["pacchetto-5"]},
    {"tipo": "crediti", "valore": 5, "solo_primo_acquisto": True},
    {"tipo": "percentuale", "valore": 10, "valido_dal": "2030-02-01T00:00:00Z", "valido_fino": "2030-01-01T00:00:00Z"},
    {"tipo": "percentuale", "valore": 10, "piani": ["non-esiste"]},
    {"tipo": "percentuale", "valore": 10, "code": "no"},
    {"tipo": "percentuale", "valore": 10, "code": "con spazio!"},
    {"tipo": "regalo", "valore": 10},
])
async def test_un_coupon_incoerente_si_rifiuta(come, catalogo, corpo):
    assert (await come("admin").post("/admin/coupons", json=corpo)).status_code == 422


# ---- i coupon: quanto valgono ---------------------------------------------------------------------------------------


async def test_lo_sconto_in_percentuale_e_in_importo(come, catalogo):
    admin = come("admin")
    await _coupon(admin, code="VENTI", tipo="percentuale", valore=20)
    await _coupon(admin, code="CINQUE", tipo="importo", valore=500)
    await _coupon(admin, code="ENORME", tipo="importo", valore=99_999)
    utente = come("utente")
    r = (await _anteprima(utente, "venti")).json()                 # 12,90 € - 20 %
    assert (r["listino"], r["sconto"], r["importo"], r["gratis"]) == (1290, 258, 1032, False)
    r = (await _anteprima(utente, " cinque ")).json()
    assert (r["sconto"], r["importo"]) == (500, 790)
    r = (await _anteprima(utente, "ENORME")).json()                # non sconta più del listino
    assert (r["sconto"], r["importo"], r["gratis"]) == (1290, 0, True)


async def test_lo_sconto_arrotonda_al_centesimo(come, catalogo):
    admin = come("admin")
    await _coupon(admin, code="TREDICI", tipo="percentuale", valore=13)
    r = (await _anteprima(come("utente"), "TREDICI", piano="pacchetto-5")).json()   # 490 × 13 % = 63,7 → 64
    assert (r["sconto"], r["importo"]) == (64, 426)


async def test_un_abbonamento_non_si_azzera(come, catalogo):
    admin = come("admin")
    await _coupon(admin, code="TUTTO", tipo="percentuale", valore=100)
    r = await _anteprima(come("utente"), "TUTTO", piano="mensile-base")
    assert r.status_code == 422 and r.json()["detail"]["motivo"] == "coupon_azzera_abbonamento"
    r = await _anteprima(come("utente"), "TUTTO", piano="pacchetto-5")             # un pacchetto sì
    assert r.status_code == 200 and r.json()["gratis"] is True


@pytest.mark.parametrize("campi, motivo", [
    ({"attivo": False}, "coupon_non_attivo"),
    ({"valido_fino": (utcnow() - timedelta(days=1)).isoformat()}, "coupon_scaduto"),
    ({"valido_dal": (utcnow() + timedelta(days=1)).isoformat()}, "coupon_non_ancora_valido"),
    ({"piani": ["pacchetto-50"]}, "coupon_non_per_questo_piano"),
])
async def test_un_coupon_fuori_regola_dice_perche(come, catalogo, campi, motivo):
    await _coupon(come("admin"), code="REGOLA", **campi)
    r = await _anteprima(come("utente"), "REGOLA", piano="pacchetto-15")
    assert r.status_code == 422 and r.json()["detail"]["motivo"] == motivo
    assert r.json()["detail"]["messaggio"]


async def test_un_codice_che_non_esiste_e_un_codice_regalo_non_scontano(come, catalogo):
    admin = come("admin")
    await _coupon(admin, code="REGALO5", tipo="crediti", valore=5)
    utente = come("utente")
    assert (await _anteprima(utente, "NONESISTE")).json()["detail"]["motivo"] == "coupon_sconosciuto"
    assert (await _anteprima(utente, "REGALO5")).json()["detail"]["motivo"] == "coupon_regalo"


async def test_il_coupon_solo_primo_acquisto_non_vale_dopo_un_pagamento(come, catalogo):
    admin = come("admin")
    await _coupon(admin, code="BENVENUTO", solo_primo_acquisto=True, max_per_utente=5)
    utente = come("utente")
    assert (await _anteprima(utente, "BENVENUTO")).status_code == 200
    r = await utente.post("/me/checkout", json={"piano": "pacchetto-5"})
    await _paga(utente, r.json()["checkout_id"])
    r = await _anteprima(utente, "BENVENUTO")
    assert r.status_code == 422 and r.json()["detail"]["motivo"] == "coupon_solo_primo_acquisto"


# ---- il pagamento con lo sconto ------------------------------------------------------------------------------------


async def test_il_checkout_chiede_l_importo_scontato_e_l_uso_si_conta_a_pagamento_avvenuto(come, catalogo):
    admin = come("admin")
    c = await _coupon(admin, code="DIECI", tipo="percentuale", valore=10, max_riscatti=1)
    utente = come("utente")
    r = await utente.post("/me/checkout", json={"piano": "pacchetto-15", "coupon": "dieci"})
    assert r.status_code == 201, r.text
    corpo = r.json()
    assert (corpo["importo"], corpo["sconto"], corpo["gratis"]) == (1161, 129, False)      # 1290 - 10 %

    # Aperto e non pagato: l'uso non è consumato.
    assert come("admin") and (await come("admin").get(f"/admin/coupons/{c['id']}/riscatti")).json()["coupon"]["riscatti"] == 0
    await _paga(come("utente"), corpo["checkout_id"])
    dettaglio = (await come("admin").get(f"/admin/coupons/{c['id']}/riscatti")).json()
    assert dettaglio["coupon"]["riscatti"] == 1
    assert dettaglio["riscatti"][0]["sconto"] == 129 and dettaglio["riscatti"][0]["email"] == "utente@example.com"
    # I crediti del pacchetto sono arrivati per intero, sconto o no.
    assert (await come("utente").get("/me/credits")).json()["saldo"] >= 15
    # Esaurito (max_riscatti=1): un altro non lo usa più.
    r = await _anteprima(come("utente"), "DIECI")
    assert r.status_code == 422 and r.json()["detail"]["motivo"] in ("coupon_esaurito", "coupon_gia_usato")


async def test_un_coupon_non_si_usa_due_volte_dalla_stessa_persona(come, catalogo):
    await _coupon(come("admin"), code="UNAVOLTA", tipo="importo", valore=100)
    utente = come("utente")
    r = await utente.post("/me/checkout", json={"piano": "pacchetto-5", "coupon": "UNAVOLTA"})
    await _paga(utente, r.json()["checkout_id"])
    r = await utente.post("/me/checkout", json={"piano": "pacchetto-5", "coupon": "UNAVOLTA"})
    assert r.status_code == 422 and r.json()["detail"]["motivo"] == "coupon_gia_usato"


async def test_un_coupon_sbagliato_blocca_il_checkout_senza_aprirlo(come, catalogo, session):
    utente = come("utente")
    r = await utente.post("/me/checkout", json={"piano": "pacchetto-5", "coupon": "NONESISTE"})
    assert r.status_code == 422 and r.json()["detail"]["motivo"] == "coupon_sconosciuto"
    from tarot_core.domain.billing_models import PaymentCheckout

    assert (await session.execute(select(PaymentCheckout))).first() is None


async def test_un_pacchetto_azzerato_dal_coupon_si_completa_senza_fornitore(come, catalogo, session):
    admin = come("admin")
    c = await _coupon(admin, code="OMAGGIO100", tipo="percentuale", valore=100)
    utente = come("utente")
    prima = (await utente.get("/me/credits")).json()["saldo"]
    r = await utente.post("/me/checkout", json={"piano": "pacchetto-15", "coupon": "omaggio100", "ritorno": "/piano"})
    assert r.status_code == 201, r.text
    corpo = r.json()
    assert corpo["gratis"] is True and corpo["importo"] == 0 and "checkout=" in corpo["url"]
    assert (await utente.get("/me/credits")).json()["saldo"] == prima + 15
    assert (await utente.get(f"/me/checkout/{corpo['checkout_id']}")).json()["stato"] == "pagato"
    movimenti = (await utente.get("/me/credits")).json()["movimenti"]
    assert movimenti[0]["reason"] == "omaggio" and "OMAGGIO100" in (movimenti[0]["note"] or "")   # non conta come vendita
    assert (await come("admin").get(f"/admin/coupons/{c['id']}/riscatti")).json()["coupon"]["riscatti"] == 1


# ---- i codici regalo -------------------------------------------------------------------------------------------------


async def test_un_codice_regalo_accredita_una_volta(come, catalogo):
    admin = come("admin")
    await _coupon(admin, code="NATALE-25", tipo="crediti", valore=25, max_riscatti=2, description="Natale")
    utente = come("utente")
    prima = (await utente.get("/me/credits")).json()["saldo"]
    r = await utente.post("/me/coupon/riscatta", json={"codice": "natale-25"})
    assert r.status_code == 200 and r.json()["crediti"] == 25 and r.json()["saldo"] == prima + 25
    r = await utente.post("/me/coupon/riscatta", json={"codice": "NATALE-25"})
    assert r.status_code == 422 and r.json()["detail"]["motivo"] == "coupon_gia_usato"
    assert (await utente.get("/me/credits")).json()["saldo"] == prima + 25


async def test_uno_sconto_non_si_riscatta_come_regalo(come, catalogo):
    await _coupon(come("admin"), code="SCONTO", tipo="percentuale", valore=10)
    r = await come("utente").post("/me/coupon/riscatta", json={"codice": "SCONTO"})
    assert r.status_code == 422 and r.json()["detail"]["motivo"] == "coupon_sconto"


async def test_chi_prova_codici_a_caso_viene_fermato(come, catalogo):
    utente = come("utente")
    for i in range(10):
        assert (await utente.post("/me/coupon/riscatta", json={"codice": f"SBAGLIATO{i}"})).status_code == 422
    r = await utente.post("/me/coupon/riscatta", json={"codice": "ANCORA"})
    assert r.status_code == 429


async def test_un_coupon_usato_si_disattiva_non_si_elimina_e_il_valore_non_cambia(come, catalogo):
    admin = come("admin")
    c = await _coupon(admin, code="USATO", tipo="crediti", valore=3)
    await come("utente").post("/me/coupon/riscatta", json={"codice": "USATO"})
    admin = come("admin")
    assert (await admin.delete(f"/admin/coupons/{c['id']}")).status_code == 409
    assert (await admin.patch(f"/admin/coupons/{c['id']}", json={"valore": 9})).status_code == 409
    r = await admin.patch(f"/admin/coupons/{c['id']}", json={"attivo": False, "max_riscatti": 50})
    assert r.status_code == 200 and r.json()["attivo"] is False and r.json()["valore"] == 3
    r = await come("utente").post("/me/coupon/riscatta", json={"codice": "USATO"})
    assert r.json()["detail"]["motivo"] == "coupon_non_attivo"


async def test_un_coupon_mai_usato_si_modifica_e_si_elimina(come, catalogo):
    admin = come("admin")
    c = await _coupon(admin, code="PROVA", tipo="percentuale", valore=10)
    r = await admin.patch(f"/admin/coupons/{c['id']}", json={"valore": 15, "piani": ["pacchetto-5"], "solo_primo_acquisto": True})
    assert r.status_code == 200 and r.json()["valore"] == 15 and r.json()["piani"] == ["pacchetto-5"]
    assert (await admin.patch(f"/admin/coupons/{c['id']}", json={"valore": 200})).status_code == 422       # percentuale > 100
    assert (await admin.patch(f"/admin/coupons/{c['id']}", json={"piani": ["non-esiste"]})).status_code == 422
    assert (await admin.delete(f"/admin/coupons/{c['id']}")).status_code == 204
    assert (await admin.get("/admin/coupons")).json() == []


# ---- regalare crediti --------------------------------------------------------------------------------------------------


async def test_l_amministratore_regala_un_pacchetto_o_una_quantita(come, catalogo, session, principal_utente):
    destinatario = await _utente(session, principal_utente)
    admin = come("admin")
    r = await admin.post(f"/admin/users/{destinatario.id}/regalo", json={"piano": "pacchetto-15", "nota": "grazie del consiglio"})
    assert r.status_code == 200 and r.json()["crediti"] == 15
    r = await admin.post(f"/admin/users/{destinatario.id}/regalo", json={"crediti": 7})
    assert r.json()["saldo"] == 22
    movimenti = (await come("utente").get("/me/credits")).json()["movimenti"]
    assert [m["reason"] for m in movimenti[:2]] == ["omaggio", "omaggio"]
    assert "pacchetto pacchetto-15" in movimenti[1]["note"] and "grazie del consiglio" in movimenti[1]["note"]
    azioni = (await session.execute(select(AuditLog).where(AuditLog.action == "credits.gift"))).scalars().all()
    assert len(azioni) == 2 and azioni[0].after["saldo"] == 15


@pytest.mark.parametrize("corpo, stato", [
    ({}, 422),
    ({"piano": "pacchetto-5", "crediti": 3}, 422),
    ({"crediti": 0}, 422),
    ({"crediti": 10_000_000}, 422),
    ({"piano": "mensile-base"}, 422),           # un abbonamento non è un pacchetto di crediti
    ({"piano": "non-esiste"}, 422),
])
async def test_un_regalo_incoerente_si_rifiuta(come, catalogo, session, principal_utente, corpo, stato):
    destinatario = await _utente(session, principal_utente)
    r = await come("admin").post(f"/admin/users/{destinatario.id}/regalo", json=corpo)
    assert r.status_code == stato, r.text


async def test_non_si_regala_a_chi_non_esiste(come, catalogo):
    assert (await come("admin").post("/admin/users/999999/regalo", json={"crediti": 5})).status_code == 404
