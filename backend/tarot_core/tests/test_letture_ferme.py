"""Dove si fermano le letture (v9.5): imbuto e dettaglio dal database delle letture."""
from __future__ import annotations

from datetime import timedelta

import pytest

from tarot_core.domain.base import utcnow
from tarot_core.domain.models import DrawnCard, InterviewTurn, Reading

from .conftest import richiede_database

pytestmark = [richiede_database, pytest.mark.asyncio]


async def _lettura(session, utente, stato: str, *, risposte: int = 0, posate: int = 0, rivelate: int = 0,
                   anonima: bool = False) -> Reading:
    adesso = utcnow()
    r = Reading(owner_id=None if anonima else utente.id, anon_id="anon-x" if anonima else None, spread_id="tre-carte",
                question="?", status=stato, lang="en", consumo="anonimo" if anonima else "credito")
    session.add(r)
    await session.flush()
    for i in range(risposte):
        session.add(InterviewTurn(reading_id=r.id, ordine=2 * i + 1, ruolo="oracolo", testo="d", created_at=adesso))
        session.add(InterviewTurn(reading_id=r.id, ordine=2 * i + 2, ruolo="utente", testo="r", created_at=adesso))
    for p in range(posate):
        session.add(DrawnCard(reading_id=r.id, posizione=p + 1, slot=p, card_id=f"maj-0{p}", rovescio=False,
                              rivelata=p < rivelate, created_at=adesso))
    return r


async def test_imbuto_e_dettaglio(client, utente, principal_admin, session):
    await _lettura(session, utente, "intervista", risposte=0)
    await _lettura(session, utente, "intervista", risposte=2)
    await _lettura(session, utente, "intervista", risposte=2)
    await _lettura(session, utente, "ventaglio", risposte=3)
    await _lettura(session, utente, "scelta", risposte=3, posate=1)
    await _lettura(session, utente, "rivelazione", risposte=3, posate=3, rivelate=1)
    await _lettura(session, utente, "completata", risposte=3, posate=3, rivelate=3)
    await _lettura(session, utente, "annullata")
    await _lettura(session, utente, "completata", anonima=True)
    await session.commit()

    client.identita.principal = principal_admin
    oggi = utcnow().date()
    corpo = {"da": (oggi - timedelta(days=1)).isoformat(), "a": (oggi + timedelta(days=1)).isoformat(), "gruppo": "iscritti"}
    r = await client.post("/admin/analytics/letture-ferme", json=corpo)
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["letture"] == 7 and d["annullate"] == 1
    assert [p["letture"] for p in d["imbuto"]] == [7, 4, 3, 2, 1, 1]
    assert d["imbuto"][1]["perse_dal_passo_prima"] == 3
    ferme = {f["stato"]: f for f in d["ferme"]}
    assert {x["etichetta"]: x["letture"] for x in ferme["intervista"]["dettaglio"]} == {"dopo 0 risposte": 1, "dopo 2 risposte": 2}
    assert ferme["scelta"]["dettaglio"] == [{"etichetta": "con 1 carta già scelta", "letture": 1}]
    assert ferme["rivelazione"]["dettaglio"] == [{"etichetta": "1 carte rivelate su 3", "letture": 1}]

    anonimi = (await client.post("/admin/analytics/letture-ferme", json={**corpo, "gruppo": "anonimi"})).json()
    assert anonimi["letture"] == 1 and anonimi["anteprima"] == {"completate": 1, "passate_a_un_account": 0, "quota": 0.0}


async def test_variante_e_piattaforma(client, utente, principal_admin, session):
    """v9.5: le letture di prima (senza variante) contano come classiche; il filtro della piattaforma separa sito e app."""
    vecchia = await _lettura(session, utente, "completata")
    chat = await _lettura(session, utente, "intervista")
    chat.variante, chat.piattaforma = "chat", "android"
    classica = await _lettura(session, utente, "ventaglio")
    classica.variante, classica.piattaforma = "classica", "web"
    await session.commit()
    client.identita.principal = principal_admin
    oggi = utcnow().date()
    base = {"da": (oggi - timedelta(days=1)).isoformat(), "a": (oggi + timedelta(days=1)).isoformat(), "gruppo": "iscritti"}
    conta = lambda **f: client.post("/admin/analytics/letture-ferme", json={**base, **f})  # noqa: E731
    assert (await conta(variante="classica")).json()["letture"] == 2
    assert (await conta(variante="chat")).json()["letture"] == 1
    assert (await conta(piattaforma="android")).json()["letture"] == 1
    assert (await conta(piattaforma="nd")).json()["letture"] == 1
    assert vecchia.variante is None


async def test_la_lettura_salva_variante_e_piattaforma(client, session):
    import uuid

    r = await client.post("/readings", json={"spread_id": "tre-carte", "question": "Come andrà il lavoro?",
                                             "variante": "chat", "piattaforma": "web"})
    assert r.status_code == 201, r.text
    salvata = await session.get(Reading, uuid.UUID(r.json()["id"]))
    assert (salvata.variante, salvata.piattaforma) == ("chat", "web")
    assert (await client.post("/readings", json={"spread_id": "tre-carte", "question": "Come andrà?",
                                                  "variante": "boh"})).status_code == 422


async def test_le_azioni_numerate_hanno_un_nome_leggibile():
    from tarot_core.analytics.uscite import etichetta

    assert etichetta("interview_answered:2") == "Intervista: ha risposto alla domanda 2"
    assert etichetta("card_revealed:3") == "Ha rivelato la carta in posizione 3"
    assert etichetta("deck_cut") == "Ha tagliato il mazzo"
