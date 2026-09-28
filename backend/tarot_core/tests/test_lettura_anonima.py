"""La lettura anonima con gate di registrazione (v6, Fase F): apertura senza account, un solo
colpo per cookie, intervista/ventaglio/scelta/rivelazione condivisi con l'utente autenticato,
anteprima invece del responso vero, e il reclamo alla prima registrazione."""
from __future__ import annotations

import uuid

from tarot_core.domain.models import Reading
from tarot_core.domain.repositories import UserRepository

from .conftest import eventi_sse, richiede_database

pytestmark = richiede_database

QUESITO = "Come andrà il mio prossimo anno lavorativo?"


async def _apri_anonima(client, spread_id="tre-carte"):
    client.identita.principal = None
    return await client.post("/readings/anonime", json={"spread_id": spread_id, "question": QUESITO})


async def _conduci_intervista(client, reading_id):
    while True:
        r = await client.post(f"/readings/{reading_id}/interview", json={})
        dati = r.json()
        if dati.get("completa"):
            return dati
        r2 = await client.post(f"/readings/{reading_id}/interview", json={"risposta": "Va tutto come previsto."})
        if r2.json().get("completa"):
            return r2.json()


async def test_apertura_anonima_non_richiede_login(client):
    r = await _apri_anonima(client)
    assert r.status_code == 201, r.text
    assert r.json()["consumo"] == "anonimo"
    assert "tarots_anon" in r.cookies


async def test_apertura_anonima_rifiuta_categorie_speciali(client):
    client.identita.principal = None
    r = await client.post("/readings/anonime", json={"spread_id": "compat-tre", "question": QUESITO})
    assert r.status_code == 422


async def test_un_secondo_tentativo_con_lo_stesso_cookie_e_respinto(client):
    r1 = await _apri_anonima(client)
    assert r1.status_code == 201
    r2 = await _apri_anonima(client)
    assert r2.status_code == 409


async def test_lettura_anonima_procede_fino_alla_sintesi_con_anteprima(client, session):
    apertura = await _apri_anonima(client)
    reading_id = apertura.json()["id"]

    await _conduci_intervista(client, reading_id)
    ventaglio = await client.post(f"/readings/{reading_id}/fan")
    assert ventaglio.status_code == 200, ventaglio.text

    for slot in range(ventaglio.json()["da_scegliere"]):
        r = await client.post(f"/readings/{reading_id}/pick", json={"slot": slot})
        assert r.status_code == 200, r.text
    posizioni_calcolate = set(r.json()["posizioni_calcolate"])

    stesa = (await client.get(f"/spreads/tre-carte")).json()
    for p in stesa["posizioni"]:
        if p["n"] in posizioni_calcolate:
            continue
        rr = await client.post(f"/readings/{reading_id}/reveal/{p['n']}")
        assert rr.status_code == 200, rr.text
        eventi_sse(rr.text)  # solo per verificare che il corpo sia SSE valido

    sintesi = await client.post(f"/readings/{reading_id}/synthesis")
    eventi = eventi_sse(sintesi.text)
    finale = next(dati for nome, dati in eventi if nome == "fine")
    testo = "".join(dati["testo"] for nome, dati in eventi if nome == "token")

    assert finale["anonimo"] is True
    assert testo.strip()

    lettura = await session.get(Reading, uuid.UUID(reading_id))
    assert lettura.synthesis  # il responso vero è salvato per intero
    assert lettura.teaser  # e l'anteprima anche
    assert testo.strip() == lettura.teaser.strip()
    assert lettura.synthesis.strip() not in testo  # mai il responso vero al client anonimo


async def test_un_altro_anonimo_non_vede_la_lettura_di_un_altro_cookie(client):
    apertura = await _apri_anonima(client)
    reading_id = apertura.json()["id"]

    client.cookies.clear()  # un altro visitatore: nessun cookie tarots_anon
    r = await client.post(f"/readings/{reading_id}/interview", json={})
    assert r.status_code == 404


async def test_reclamo_alla_registrazione_trasferisce_la_proprieta(client, session, principal_utente):
    apertura = await _apri_anonima(client)
    reading_id = apertura.json()["id"]
    await _conduci_intervista(client, reading_id)

    # La "registrazione": la stessa identità torna a presentarsi con un token vero, con lo stesso
    # cookie tarots_anon ancora nel client. Una richiesta autenticata qualunque attraversa
    # `current_user()`, che al primo accesso (`appena_creato`) reclama la lettura dal cookie.
    client.identita.principal = principal_utente
    r = await client.get("/me/addresses")
    assert r.status_code == 200

    io = await UserRepository(session).ensure(principal_utente)
    await session.commit()

    lettura = await session.get(Reading, uuid.UUID(reading_id))
    await session.refresh(lettura)
    assert lettura.owner_id == io.id
    assert lettura.anon_id is not None  # resta, per impedire un secondo omaggio con lo stesso cookie
