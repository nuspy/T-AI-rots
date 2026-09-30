"""Gli eventi di business emessi lato server (v8): iscrizione, lettura, acquisto. Modello finto."""
from __future__ import annotations

import json

from sqlalchemy import select

from ..domain.analytics_models import TABELLE
from .conftest import richiede_database
from .test_flusso import QUESITO, _azzera_regalo_iscrizione, _lettura_completa

pytestmark = richiede_database


async def _eventi(session, nome=None):
    e = TABELLE.eventi
    q = select(e).order_by(e.c.id)
    if nome:
        q = q.where(e.c.nome == nome)
    return [dict(r) for r in (await session.execute(q)).mappings().all()]


async def test_il_primo_accesso_segna_la_registrazione(client, session):
    assert (await client.get("/me/profile")).status_code == 200
    [evento] = await _eventi(session, "registrazione")
    [riga] = (await session.execute(select(TABELLE.utenti))).mappings().all()
    assert riga["utente_id"] == evento["utente_id"] and riga["registrato_il"] is not None
    # Un secondo accesso non è una seconda iscrizione.
    await client.get("/me/profile")
    assert len(await _eventi(session, "registrazione")) == 1


async def test_la_lettura_emette_apertura_e_completamento_senza_contenuti(client, session, catalogo):
    await _lettura_completa(client, "tre-carte", 3)
    [aperta] = await _eventi(session, "lettura_aperta")
    [completata] = await _eventi(session, "lettura_completata")
    assert aperta["proprieta"]["stesa"] == "tre-carte" and aperta["proprieta"]["consumo"] in {"quota", "credito", "omaggio"}
    assert completata["proprieta"]["anonima"] is False and completata["origine"] == "server"
    # Né la domanda né il responso finiscono negli eventi.
    tutto = json.dumps(await _eventi(session), default=str)
    assert QUESITO not in tutto and "lavoro" not in tutto


async def test_checkout_e_acquisto_con_valore(client, session, catalogo):
    await _azzera_regalo_iscrizione(session)
    r = await client.post("/me/checkout", json={"piano": "pacchetto-15", "ritorno": "/leggi"})
    assert r.status_code == 201, r.text
    importo = r.json()["importo"]
    checkout = r.json()["checkout_id"]
    await client.post(f"/billing/mock/checkout/{checkout}/esito", data={"esito": "paga", "ritorno": "http://localhost:3000/leggi"})
    [avviato] = await _eventi(session, "checkout_avviato")
    [acquisto] = await _eventi(session, "acquisto")
    assert avviato["valore_centesimi"] == importo == acquisto["valore_centesimi"] and importo > 0
    assert acquisto["proprieta"] == {"tipo": "crediti", "piano": "pacchetto-15", "annuale": False, "coupon": False}
    assert acquisto["valuta"] == "EUR" and acquisto["utente_id"] is not None


async def test_analytics_spenti_non_emettono(client, session, catalogo, monkeypatch):
    from tarot_core.settings import get_settings

    monkeypatch.setenv("TAROT_ANALYTICS_ATTIVI", "false")
    get_settings.cache_clear()
    try:
        await client.get("/me/profile")
        await client.post("/e", content=json.dumps({"eventi": [{"n": "page_view", "p": "/"}]}),
                          headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0) Chrome/126.0 Safari/537.36"})
        assert await _eventi(session) == []
    finally:
        monkeypatch.delenv("TAROT_ANALYTICS_ATTIVI")
        get_settings.cache_clear()


async def test_opposizione_dal_profilo(client, session):
    assert (await client.get("/me/statistiche")).json() == {"opposizione": False}
    r = await client.put("/me/statistiche", json={"opposizione": True})
    assert r.status_code == 200 and r.json() == {"opposizione": True}
    assert (await client.get("/me/statistiche")).json() == {"opposizione": True}
    # Da qui gli eventi dell'utente restano anonimi.
    await client.get("/me/profile")
    assert all(e["utente_id"] is None for e in await _eventi(session))
    assert (await client.put("/me/statistiche", json={"opposizione": False})).json() == {"opposizione": False}
