"""Il flusso di una lettura attraverso l'API, col modello finto e un database vero."""
from __future__ import annotations

import pytest

from tarot_core.auth.keycloak import Principal
from tarot_core.billing.credits import RegistroCrediti
from tarot_core.domain.repositories import UserRepository
from tarot_core.tarot.shuffle import verifica

from .conftest import eventi_sse, richiede_database

pytestmark = richiede_database

STESE = {
    "tre-carte": 3,
    "croce-semplice": 4,
    "ferro-di-cavallo": 7,
    "croce-celtica": 10,
    "ruota-astrologica": 13,
}


async def _accredita(session, principal, quanti=1000):
    utente = await UserRepository(session).ensure(principal)
    await RegistroCrediti(session).rettifica(utente.id, quanti, note="crediti di prova")
    await session.commit()
    return utente


async def _lettura_completa(client, spread_id: str, da_scegliere: int) -> dict:
    r = await client.post("/readings", json={"spread_id": spread_id, "question": "Cosa mi riserva il lavoro nei prossimi mesi?"})
    assert r.status_code == 201, r.text
    lettura = r.json()
    assert "scientifica" in lettura["disclaimer"]
    rid = lettura["id"]

    # Intervista: il modello finto chiude dopo due domande.
    r = await client.post(f"/readings/{rid}/interview", json={})
    domande = 0
    while not r.json().get("completa"):
        domande += 1
        assert r.json()["domanda"]
        r = await client.post(f"/readings/{rid}/interview", json={"risposta": "Da qualche mese, con alti e bassi."})
    assert domande == 2 and r.json()["riassunto"]

    r = await client.post(f"/readings/{rid}/fan")
    ventaglio = r.json()
    assert ventaglio["slot_count"] == (22 if spread_id in ("tre-carte", "croce-semplice") else 78)
    assert ventaglio["da_scegliere"] == da_scegliere

    # Prima della rivelazione nessuna carta è visibile.
    dettaglio = (await client.get(f"/me/readings/{rid}")).json()
    assert "deck_state" not in dettaglio or dettaglio["deck_state"] is None

    for i in range(da_scegliere):
        r = await client.post(f"/readings/{rid}/pick", json={"slot": i * 2})
        assert r.status_code == 200, r.text
        assert "carta" not in r.json()
    assert r.json()["tutte_scelte"]

    dettaglio = (await client.get(f"/me/readings/{rid}")).json()
    assert all("carta" not in c for c in dettaglio["cards"])
    posizioni = [c["posizione"] for c in dettaglio["cards"]]

    for pos in sorted(posizioni):
        r = await client.post(f"/readings/{rid}/reveal/{pos}")
        eventi = eventi_sse(r.text)
        nomi = [e for e, _ in eventi]
        assert nomi[0] == "carta" and nomi[-1] == "fine"
        assert eventi[-1][1]["interpretazione"]

    r = await client.post(f"/readings/{rid}/synthesis")
    eventi = eventi_sse(r.text)
    testo = "".join(d["testo"] for e, d in eventi if e == "token")
    assert "## Il quadro" in testo
    fine = eventi[-1][1]
    assert eventi[-1][0] == "fine" and fine["guardia"] == "ok"
    # A lettura conclusa il mazzo si può verificare contro il commitment.
    assert verifica(fine["deck_state"], fine["deck_salt"], fine["commitment"])
    return fine


@pytest.mark.parametrize("spread_id", list(STESE))
async def test_una_lettura_completa_per_ogni_stesa(client, session, catalogo, spread_id):
    await _accredita(session, client.identita.principal)
    fine = await _lettura_completa(client, spread_id, STESE[spread_id])
    assert fine["saldo"] == 999


async def test_cinque_letture_consumano_cinque_crediti(client, session, catalogo):
    await _accredita(session, client.identita.principal)
    for spread_id, n in STESE.items():
        fine = await _lettura_completa(client, spread_id, n)
    assert fine["saldo"] == 995


async def test_senza_crediti_si_riceve_402(client, catalogo):
    r = await client.post("/readings", json={"spread_id": "tre-carte", "question": "Andrà bene?"})
    assert r.status_code == 402
    assert r.json()["detail"]["motivo"] == "crediti"
    assert (await client.get("/me/readings")).json()["totale"] == 0


async def test_la_croce_semplice_calcola_la_sintesi_di_wirth(client, session, catalogo):
    await _accredita(session, client.identita.principal)
    await _lettura_completa(client, "croce-semplice", 4)
    rid = (await client.get("/me/readings")).json()["letture"][0]["id"]
    carte = (await client.get(f"/me/readings/{rid}")).json()["cards"]
    assert len(carte) == 5
    scelte = [c for c in carte if not c["calcolata"]]
    sintesi = next(c for c in carte if c["calcolata"])
    somma = sum(c["carta"]["numero"] for c in scelte)
    while somma > 22:
        somma = sum(int(x) for x in str(somma))
    assert sintesi["carta"]["numero"] == (0 if somma in (0, 22) else somma)
    assert sintesi["posizione"] == 5 and sintesi["rovescio"] is False


async def test_le_carte_si_rivelano_in_ordine(client, session, catalogo):
    await _accredita(session, client.identita.principal)
    rid = (await client.post("/readings", json={"spread_id": "tre-carte", "question": "Una domanda?"})).json()["id"]
    r = await client.post(f"/readings/{rid}/interview", json={})
    while not r.json().get("completa"):
        r = await client.post(f"/readings/{rid}/interview", json={"risposta": "Risposta"})
    await client.post(f"/readings/{rid}/fan")
    # Lo stesso slot non si sceglie due volte.
    assert (await client.post(f"/readings/{rid}/pick", json={"slot": 3})).status_code == 200
    assert (await client.post(f"/readings/{rid}/pick", json={"slot": 3})).status_code == 409
    for s in (4, 5):
        await client.post(f"/readings/{rid}/pick", json={"slot": s})
    assert (await client.post(f"/readings/{rid}/reveal/2")).status_code == 409
    assert (await client.post(f"/readings/{rid}/synthesis")).status_code == 409


async def test_una_crisi_ferma_la_lettura_e_restituisce_il_credito(client, session, catalogo):
    await _accredita(session, client.identita.principal, 1)
    rid = (await client.post("/readings", json={"spread_id": "tre-carte", "question": "Cosa succederà?"})).json()["id"]
    await client.post(f"/readings/{rid}/interview", json={})
    r = await client.post(f"/readings/{rid}/interview", json={"risposta": "Non voglio più vivere"})
    assert r.json()["crisi"] and "112" in r.json()["messaggio"]
    assert (await client.get("/me/billing")).json()["saldo"] == 1
    assert (await client.get(f"/me/readings/{rid}")).json()["status"] == "annullata"


async def test_una_domanda_di_crisi_non_apre_la_lettura(client, session, catalogo):
    await _accredita(session, client.identita.principal, 1)
    r = await client.post("/readings", json={"spread_id": "tre-carte", "question": "Voglio farla finita"})
    assert r.json()["crisi"]
    assert (await client.get("/me/billing")).json()["saldo"] == 1


async def test_le_letture_di_un_altro_non_si_vedono_ne_si_cancellano(client, session, catalogo, principal_altro):
    await _accredita(session, client.identita.principal)
    rid = (await client.post("/readings", json={"spread_id": "tre-carte", "question": "La mia domanda?"})).json()["id"]
    client.identita.principal = principal_altro
    assert (await client.get(f"/me/readings/{rid}")).status_code == 404
    assert (await client.delete(f"/me/readings/{rid}")).status_code == 404
    assert (await client.post(f"/readings/{rid}/interview", json={})).status_code == 404


async def test_la_cancellazione_e_vera(client, session, catalogo):
    await _accredita(session, client.identita.principal)
    rid = (await client.post("/readings", json={"spread_id": "tre-carte", "question": "Da cancellare?"})).json()["id"]
    assert (await client.delete(f"/me/readings/{rid}")).status_code == 204
    assert (await client.get(f"/me/readings/{rid}")).status_code == 404
    # Il movimento di credito resta, senza riferimento alla lettura.
    movimenti = (await client.get("/me/credits")).json()["movimenti"]
    assert any(m["reason"] == "consumo" and m["reading_id"] is None for m in movimenti)


async def test_l_abbonamento_usa_la_quota_prima_dei_crediti(client, session, catalogo):
    from tarot_core.billing.plans import GestoreAbbonamenti

    utente = await _accredita(session, client.identita.principal, 5)
    gestore = GestoreAbbonamenti(session)
    await gestore.sottoscrivi(utente.id, await gestore.piano_per_slug("mensile-base"))
    await session.commit()
    consumi = []
    for _ in range(4):
        r = await client.post("/readings", json={"spread_id": "tre-carte", "question": "Oggi?"})
        consumi.append(r.json()["consumo"])
    assert consumi == ["quota", "quota", "quota", "credito"]
    assert (await client.get("/me/billing")).json()["saldo"] == 4


async def test_un_pacchetto_pagato_accredita_i_crediti(client, catalogo):
    r = await client.post("/me/checkout", json={"piano": "pacchetto-15", "ritorno": "/leggi"})
    assert r.status_code == 201, r.text
    checkout = r.json()["checkout_id"]
    r = await client.post(f"/billing/mock/checkout/{checkout}/esito", data={"esito": "paga", "ritorno": "http://localhost:3000/leggi"})
    assert r.status_code == 303
    assert (await client.get(f"/me/checkout/{checkout}")).json()["stato"] == "pagato"
    assert (await client.get("/me/billing")).json()["saldo"] == 15


async def test_il_ritorno_del_checkout_non_esce_dal_sito(client, catalogo):
    r = await client.post("/me/checkout", json={"piano": "pacchetto-5", "ritorno": "//evil.example"})
    assert r.status_code == 400


async def test_condivisione_e_diario(client, session, catalogo):
    await _accredita(session, client.identita.principal)
    await _lettura_completa(client, "tre-carte", 3)
    rid = (await client.get("/me/readings")).json()["letture"][0]["id"]
    r = await client.post(f"/me/readings/{rid}/share", json={"attiva": True})
    assert r.status_code == 200, r.text
    token = r.json()["share_token"]
    pubblica = (await client.get(f"/shared/{token}")).json()
    assert pubblica["synthesis"] and "interview" not in pubblica
    await client.post(f"/me/readings/{rid}/share", json={"attiva": False})
    assert (await client.get(f"/shared/{token}")).status_code == 404
    assert (await client.post(f"/me/readings/{rid}/feedback", json={"esito": "in_parte"})).status_code == 200


async def test_inviti_e_carta_del_giorno(client, session, catalogo, principal_altro):
    codice = (await client.get("/me/profile")).json()["referral_code"]
    client.identita.principal = principal_altro
    r = await client.post("/me/referral", json={"codice": codice})
    assert r.status_code == 200 and r.json()["saldo"] == 3
    assert (await client.post("/me/referral", json={"codice": codice})).status_code == 409
    prima = (await client.get("/me/daily-card")).json()
    seconda = (await client.get("/me/daily-card")).json()
    assert prima["carta"]["id"] == seconda["carta"]["id"] and prima["serie"] == 1


async def test_la_console_richiede_il_ruolo_admin(client, catalogo, principal_admin):
    assert (await client.get("/admin/stats")).status_code == 403
    client.identita.principal = principal_admin
    stats = (await client.get("/admin/stats?giorni=7")).json()
    assert "attuale" in stats and "per_stesa" in stats
    assert (await client.get("/admin/users")).status_code == 200
    r = await client.get("/admin/reports/letture.csv")
    assert r.status_code == 200 and r.text.lstrip("﻿").startswith("id,")


def test_principal_admin_ha_il_ruolo(principal_admin: Principal):
    assert principal_admin.is_admin
