"""I mazzi in vendita (v5, Fase B1): finestra di attivazione, possesso, e la loro integrazione
nella pipeline di lettura."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from tarot_core.billing.credits import RegistroCrediti
from tarot_core.domain.deck_models import Deck, DeckUnlock
from tarot_core.domain.repositories import UserRepository

from .conftest import richiede_database

pytestmark = richiede_database


@pytest.fixture
def come(client, principal_utente, principal_admin):
    def scegli(chi: str):
        client.identita.principal = principal_admin if chi == "admin" else principal_utente
        return client
    return scegli


def _adesso() -> datetime:
    return datetime.now(timezone.utc)


async def _accredita(session, principal, quanti=1000):
    utente = await UserRepository(session).ensure(principal)
    await RegistroCrediti(session).accredita(utente.id, quanti, reason="omaggio", note="prova")
    await session.commit()
    return utente


# ---- attivo_ora --------------------------------------------------------------------------------


def test_attivo_ora_senza_finestra():
    d = Deck(nome="x", slug="x", attivo=True, created_at=_adesso())
    assert d.attivo_ora is True


def test_attivo_ora_spento_a_mano():
    d = Deck(nome="x", slug="x", attivo=False, created_at=_adesso())
    assert d.attivo_ora is False


def test_attivo_ora_prima_della_finestra():
    d = Deck(nome="x", slug="x", attivo=True, created_at=_adesso(), attivazione_da=_adesso() + timedelta(days=1))
    assert d.attivo_ora is False


def test_attivo_ora_dopo_la_finestra():
    d = Deck(nome="x", slug="x", attivo=True, created_at=_adesso(), attivazione_fino=_adesso() - timedelta(days=1))
    assert d.attivo_ora is False


def test_attivo_ora_dentro_la_finestra():
    d = Deck(
        nome="x", slug="x", attivo=True, created_at=_adesso(),
        attivazione_da=_adesso() - timedelta(days=1), attivazione_fino=_adesso() + timedelta(days=1),
    )
    assert d.attivo_ora is True


# ---- catalogo pubblico -------------------------------------------------------------------------


async def test_get_decks_mostra_solo_gli_attivi_ora(client, session):
    session.add_all([
        Deck(nome="Visibile", slug="visibile", predefinito=True, attivo=True),
        Deck(nome="Spento", slug="spento", attivo=False),
        Deck(nome="Futuro", slug="futuro", attivo=True, attivazione_da=_adesso() + timedelta(days=30)),
    ])
    await session.commit()
    r = await client.get("/decks")
    assert r.status_code == 200
    slug = {d["slug"] for d in r.json()}
    assert slug == {"visibile"}


async def test_get_deck_slug_sconosciuto_da_404(client):
    assert (await client.get("/decks/non-esiste")).status_code == 404


# ---- possesso nella pipeline di lettura --------------------------------------------------------


async def test_il_predefinito_non_richiede_sblocco(client, session, catalogo):
    await _accredita(session, client.identita.principal)
    session.add(Deck(nome="Thoth", slug="thoth", predefinito=True, attivo=True))
    await session.commit()
    r = await client.post("/readings", json={"spread_id": "tre-carte", "question": "Domanda?", "deck_id": "thoth"})
    assert r.status_code == 201, r.text


async def test_un_mazzo_non_posseduto_si_respinge(client, session, catalogo):
    await _accredita(session, client.identita.principal)
    session.add(Deck(nome="A pagamento", slug="premium", attivo=True, prezzo_digitale=990))
    await session.commit()
    r = await client.post("/readings", json={"spread_id": "tre-carte", "question": "Domanda?", "deck_id": "premium"})
    assert r.status_code == 403
    assert r.json()["detail"]["motivo"] == "mazzo_non_posseduto"
    # Non addebitato: la lettura non è stata creata.
    assert (await client.get("/me/readings")).json()["totale"] == 0


async def test_un_mazzo_sbloccato_si_puo_usare(client, session, catalogo):
    utente = await _accredita(session, client.identita.principal)
    mazzo = Deck(nome="A pagamento", slug="premium", attivo=True, prezzo_digitale=990)
    session.add(mazzo)
    await session.flush()
    session.add(DeckUnlock(user_id=utente.id, deck_id=mazzo.id, acquired_at=_adesso()))
    await session.commit()
    r = await client.post("/readings", json={"spread_id": "tre-carte", "question": "Domanda?", "deck_id": "premium"})
    assert r.status_code == 201, r.text
    # La lettura ricorda il suo mazzo: riaperta e nello storico mostra le sue immagini (v8.5).
    lettura_id = r.json()["reading_id"] if "reading_id" in r.json() else r.json()["id"]
    assert (await client.get(f"/me/readings/{lettura_id}")).json()["mazzo"] == "premium"
    assert (await client.get("/me/readings")).json()["letture"][0]["mazzo"] == "premium"


async def test_con_il_predefinito_o_senza_mazzo_la_lettura_non_ha_cartella(client, session, catalogo):
    await _accredita(session, client.identita.principal)
    session.add(Deck(nome="Thoth", slug="thoth", predefinito=True, attivo=True))
    await session.commit()
    for corpo in ({"deck_id": "thoth"}, {}):
        r = await client.post("/readings", json={"spread_id": "tre-carte", "question": "Domanda?", **corpo})
        assert r.status_code == 201, r.text
    assert {x["mazzo"] for x in (await client.get("/me/readings")).json()["letture"]} == {None}


async def test_un_mazzo_digitale_gratuito_si_usa_senza_ordine(client, session, catalogo):
    await _accredita(session, client.identita.principal)
    session.add(Deck(nome="In regalo", slug="regalo", attivo=True, prezzo_digitale=0, prezzo_stampa=990))
    await session.commit()
    r = await client.post("/readings", json={"spread_id": "tre-carte", "question": "Domanda?", "deck_id": "regalo"})
    assert r.status_code == 201, r.text
    mio = (await client.get("/me/decks")).json()["deck_ids"]
    regalo = (await client.get("/decks/regalo")).json()["id"]
    assert regalo in mio
    # comprarlo non ha senso; il PDF invece si compra
    voci = {"voci": [{"deck_id": regalo, "tipo": "digitale"}]}
    assert (await client.post("/shop/quote", json=voci)).status_code == 422
    assert (await client.post("/shop/quote", json={"voci": [{"deck_id": regalo, "tipo": "pdf"}]})).status_code == 200


async def test_un_mazzo_spento_si_respinge_anche_se_posseduto(client, session, catalogo):
    utente = await _accredita(session, client.identita.principal)
    mazzo = Deck(nome="Ritirato", slug="ritirato", attivo=False)
    session.add(mazzo)
    await session.flush()
    session.add(DeckUnlock(user_id=utente.id, deck_id=mazzo.id, acquired_at=_adesso()))
    await session.commit()
    r = await client.post("/readings", json={"spread_id": "tre-carte", "question": "Domanda?", "deck_id": "ritirato"})
    assert r.status_code == 404


async def test_senza_deck_id_e_come_sempre(client, session, catalogo):
    """Il campo è opzionale: senza, nessuna verifica di possesso — comportamento invariato."""
    await _accredita(session, client.identita.principal)
    r = await client.post("/readings", json={"spread_id": "tre-carte", "question": "Domanda?"})
    assert r.status_code == 201, r.text


# ---- console admin ------------------------------------------------------------------------------


async def test_admin_crea_modifica_ed_elimina_un_mazzo(come):
    admin = come("admin")
    r = await admin.post("/admin/decks", json={"slug": "prova", "nome": "Prova", "prezzo_digitale": 500})
    assert r.status_code == 201, r.text
    assert r.json()["prezzo_digitale"] == 500

    r = await admin.put("/admin/decks/prova", json={"prezzo_digitale": 700})
    assert r.status_code == 200
    assert r.json()["prezzo_digitale"] == 700

    assert (await admin.delete("/admin/decks/prova")).status_code == 204
    assert (await admin.get("/decks/prova")).status_code == 404


async def test_solo_un_predefinito_alla_volta(come):
    admin = come("admin")
    r = await admin.post("/admin/decks", json={"slug": "uno", "nome": "Uno", "predefinito": True})
    assert r.status_code == 201, r.text
    r = await admin.post("/admin/decks", json={"slug": "due", "nome": "Due", "predefinito": True})
    assert r.status_code == 409


async def test_un_mazzo_posseduto_non_si_elimina(come, session):
    admin = come("admin")
    r = await admin.post("/admin/decks", json={"slug": "usato", "nome": "Usato"})
    mazzo_id = r.json()["id"]
    utente = await UserRepository(session).ensure(admin.identita.principal)
    session.add(DeckUnlock(user_id=utente.id, deck_id=mazzo_id, acquired_at=_adesso()))
    await session.commit()
    r = await admin.delete("/admin/decks/usato")
    assert r.status_code == 409


async def test_un_utente_normale_non_accede_alla_console_mazzi(come):
    utente = come("utente")
    assert (await utente.post("/admin/decks", json={"slug": "x", "nome": "X"})).status_code == 403
