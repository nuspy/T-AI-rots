"""L'interpretazione AI degli analytics (v8). Solo modello finto: nessuna chiamata vera."""
from __future__ import annotations

import json

import pytest

from .conftest import richiede_database
from .test_analytics_console import _traffico, stato_pulito  # noqa: F401  (fixture autouse)

pytestmark = richiede_database


@pytest.fixture
def admin(client, principal_admin):
    client.identita.principal = principal_admin
    return client


async def test_analisi_di_una_sezione_verificata_e_salvata(admin, session, prompt_visti):
    await _traffico(session)
    await session.commit()
    r = await admin.post("/admin/analytics/analizza", json={"sezione": "traffico", "giorni": 7})
    assert r.status_code == 200, r.text
    analisi = r.json()
    risposta = analisi["risposta"]
    assert analisi["fatti"] and analisi["fatti"][0]["id"] == "M1"
    assert risposta["verifica"]["voci"] > 0
    assert risposta["verifica"]["verificate"] == risposta["verifica"]["voci"]
    assert risposta["sintesi_verificata"]
    # Una sola chiamata al modello per clic.
    assert [p["compito"] for p in prompt_visti] == ["analisi_dati"]
    # Nel prompt solo aggregati: nessun indirizzo IP, nessuna email.
    assert "198.51.100" not in prompt_visti[0]["utente"] and "@" not in prompt_visti[0]["utente"]
    storico = (await admin.get("/admin/analytics/analisi?sezione=traffico")).json()
    assert [a["id"] for a in storico] == [analisi["id"]]


async def test_numero_inventato_non_verificato(admin, session, monkeypatch):
    from tarot_core.tarot.finto import ModelloFinto

    await _traffico(session)
    await session.commit()

    def inventa(self, req):
        return json.dumps({"sintesi": "Le sessioni sono state 98765.",
                           "osservazioni": [{"titolo": "x", "testo": "Il social vale 4321 sessioni.", "fatti": ["M1"]}]})

    monkeypatch.setattr(ModelloFinto, "_rispondi", inventa)
    risposta = (await admin.post("/admin/analytics/analizza", json={"sezione": "traffico", "giorni": 7})).json()["risposta"]
    assert risposta["sintesi_verificata"] is False
    assert risposta["osservazioni"][0]["verificato"] is False
    assert risposta["osservazioni"][0]["numeri_non_trovati"] == [4321.0]


async def test_modello_che_non_risponde_da_503_e_resta_nello_storico(admin, session, monkeypatch):
    from tarot_core.tarot.finto import ModelloFinto

    await _traffico(session)
    await session.commit()
    monkeypatch.setattr(ModelloFinto, "_rispondi", lambda self, req: "non è JSON")
    r = await admin.post("/admin/analytics/analizza", json={"sezione": "traffico", "giorni": 7})
    assert r.status_code == 503
    [riga] = (await admin.get("/admin/analytics/analisi")).json()
    assert riga["errore"] and riga["risposta"] is None


async def test_contesto_e_azione_adottata_entrano_nell_analisi_successiva(admin, session, prompt_visti):
    await _traffico(session)
    await session.commit()
    r = await admin.put("/admin/analytics/impostazioni", json={"contesto_ai": "Campagna Instagram partita il 20."})
    assert r.json()["contesto_ai"].startswith("Campagna Instagram")
    prima = (await admin.post("/admin/analytics/analizza", json={"sezione": "traffico", "giorni": 7})).json()
    r = await admin.patch(f"/admin/analytics/analisi/{prima['id']}", json={"giudizio": 1, "azione_adottata": "Raddoppiato il budget social"})
    assert r.json()["giudizio"] == 1
    await admin.post("/admin/analytics/analizza", json={"sezione": "traffico", "giorni": 7})
    ultimo = prompt_visti[-1]["utente"]
    assert "Campagna Instagram partita il 20." in ultimo and "Raddoppiato il budget social" in ultimo


@pytest.mark.parametrize("sezione", ["utenti", "ricavi", "letture", "imbuti", "panoramica"])
async def test_ogni_sezione_si_analizza(admin, session, sezione):
    await _traffico(session)
    await session.commit()
    r = await admin.post("/admin/analytics/analizza", json={"sezione": sezione, "giorni": 30})
    assert r.status_code == 200, r.text


async def test_vista_dell_esploratore_e_sezione_sconosciuta(admin, session):
    await _traffico(session)
    await session.commit()
    vista = {"sorgente": "visite", "misure": ["sessioni"], "dimensioni": ["canale"], "da": "2026-01-01", "a": "2026-01-01"}
    r = await admin.post("/admin/analytics/analizza", json={"sezione": "vista", "giorni": 7, "vista": vista})
    assert r.status_code == 200, r.text
    assert any("canale" in f["testo"].lower() for f in r.json()["fatti"])
    assert (await admin.post("/admin/analytics/analizza", json={"sezione": "segreta", "giorni": 7})).status_code == 422


async def test_solo_admin(client):
    assert (await client.post("/admin/analytics/analizza", json={"sezione": "traffico"})).status_code == 403
