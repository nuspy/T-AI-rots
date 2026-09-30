"""Piani e mazzi nelle lingue del sito (v8.5): la lingua chiesta, poi l'inglese, poi l'originale."""
from __future__ import annotations

import pytest

from tarot_core.billing.lingue import in_lingua, pulisci
from tarot_core.domain.deck_models import Deck

from .conftest import richiede_database


def test_in_lingua_ripiega_sull_inglese_e_poi_sull_originale():
    t = {"en": "Monthly Basic", "hu": "Havi Alap", "ru": "  "}
    assert in_lingua(t, "hu", "Mensile Base") == "Havi Alap"
    assert in_lingua(t, "ru", "Mensile Base") == "Monthly Basic"  # vuota: non conta
    assert in_lingua({}, "de", "Mensile Base") == "Mensile Base"
    assert in_lingua(None, None, "Mensile Base") == "Mensile Base"
    assert in_lingua(t, None, "Mensile Base") == "Mensile Base"  # senza lingua: l'originale


def test_pulisci_tiene_solo_lingue_note_e_testi_veri():
    assert pulisci({"en": " Gold ", "xx": "no", "it": "", "hu": None, "es": "x" * 100}, 10) == {"en": "Gold", "es": "x" * 10}


@pytest.fixture
def admin(client, principal_admin):
    client.identita.principal = principal_admin
    return client


@richiede_database
async def test_il_catalogo_risponde_nella_lingua_chiesta(client, catalogo):
    per = lambda dati: {p["slug"]: p for p in dati}  # noqa: E731
    originale = per((await client.get("/plans")).json())
    assert originale["mensile-base"]["nome"] == "Mensile Base"
    hu = per((await client.get("/plans?lang=hu")).json())
    assert hu["mensile-base"]["nome"] == "Havi Alap" and hu["pacchetto-15"]["descrizione"].startswith("Tizenöt olvasás")
    de = per((await client.get("/plans?lang=de")).json())
    assert de["mensile-oro"]["nome"] == "Monthly Gold"
    ru = per((await client.get("/plans?lang=ru")).json())
    assert ru["free"]["nome"] == "Бесплатный"


@richiede_database
async def test_la_console_scrive_le_traduzioni_di_piani_e_mazzi(admin, catalogo, session):
    r = await admin.patch("/admin/plans/mensile-base", json={"nomi": {"en": "Basic", "de": "Monatlich Basis", "xx": "no"}})
    assert r.status_code == 200, r.text
    assert r.json()["nomi"] == {"en": "Basic", "de": "Monatlich Basis"}
    assert {p["slug"]: p for p in (await admin.get("/plans?lang=de")).json()}["mensile-base"]["nome"] == "Monatlich Basis"

    session.add(Deck(slug="lovers", nome="Lovers", attivo=True, descrizione="Un mazzo preraffaellita."))
    await session.commit()
    r = await admin.put("/admin/decks/lovers", json={"nomi": {"it": "Amanti"}, "descrizioni": {"en": "A Pre-Raphaelite deck."}})
    assert r.status_code == 200, r.text
    en = (await admin.get("/decks/lovers?lang=en")).json()
    it = (await admin.get("/decks/lovers?lang=it")).json()
    assert (en["nome"], en["descrizione"]) == ("Lovers", "A Pre-Raphaelite deck.")
    assert (it["nome"], it["descrizione"]) == ("Amanti", "A Pre-Raphaelite deck.")
