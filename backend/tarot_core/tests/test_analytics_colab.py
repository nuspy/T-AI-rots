"""Colab (v8): token, export per i notebook, import firmato dei risultati, notebook scaricabile."""
from __future__ import annotations

import json

import pytest

from lanterna import colab

from .conftest import richiede_database
from .test_analytics_console import _traffico, stato_pulito  # noqa: F401  (fixture autouse)

pytestmark = richiede_database


@pytest.fixture
def admin(client, principal_admin):
    client.identita.principal = principal_admin
    return client


async def _token(admin, ambiti=("esporta", "importa"), giorni=30):
    r = await admin.post("/admin/analytics/studi/token", json={"nome": "prova", "giorni": giorni, "ambiti": list(ambiti)})
    assert r.status_code == 201, r.text
    return r.json()


async def test_export_con_token_e_senza(admin, session):
    await _traffico(session)
    await session.commit()
    creato = await _token(admin)
    assert creato["token"].startswith("lnt_")
    admin.identita.principal = None  # il notebook non ha una sessione Keycloak
    assert (await admin.get("/analytics/export/traffico")).status_code == 401
    assert (await admin.get("/analytics/export/traffico", headers={"Authorization": "Bearer sbagliato"})).status_code == 401
    r = await admin.get("/analytics/export/traffico?giorni=7", headers={"Authorization": f"Bearer {creato['token']}"})
    assert r.status_code == 200, r.text
    fogli = r.json()["fogli"]
    assert fogli and fogli[0]["colonne"] and "198.51.100" not in r.text
    # Nel database il token non c'è: solo l'impronta.
    from sqlalchemy import select

    from ..domain.analytics_models import TABELLE

    righe = (await session.execute(select(TABELLE.token))).mappings().all()
    assert all(creato["token"] not in json.dumps(dict(x), default=str) for x in righe)


async def test_soglia_k_nell_export(admin, session, utente):
    utente.gender = "donna"
    await session.commit()
    creato = await _token(admin)
    admin.identita.principal = None
    r = await admin.get("/analytics/export/utenti?giorni=7", headers={"Authorization": f"Bearer {creato['token']}"})
    genere = next(f for f in r.json()["fogli"] if f["titolo"] == "Genere")
    # L'utente di prova e l'amministratore: due gruppi da una persona, entrambi nascosti.
    assert genere["righe"] == [] and genere["soppresse"] == 2


async def test_token_revocato_scaduto_o_senza_ambito(admin, session):
    solo_export = await _token(admin, ambiti=("esporta",))
    revocato = await _token(admin)
    assert (await admin.delete(f"/admin/analytics/studi/token/{revocato['id']}")).status_code == 204
    admin.identita.principal = None
    corpo = json.dumps({"titolo": "x", "colonne": ["a"], "righe": [[1]]}).encode()
    for t in (solo_export["token"], revocato["token"]):
        r = await admin.post("/analytics/importa", content=corpo,
                             headers={"Authorization": f"Bearer {t}", "X-Firma": colab.firma(t, corpo)})
        assert r.status_code == 401
    r = await admin.get("/analytics/export/traffico", headers={"Authorization": f"Bearer {revocato['token']}"})
    assert r.status_code == 401


async def test_import_firmato_visibile_in_console(admin, session, principal_admin):
    creato = await _token(admin)
    t = creato["token"]
    admin.identita.principal = None
    corpo = json.dumps({"titolo": "Segmenti RFM", "descrizione": "k-means", "colonne": ["segmento", "clienti"],
                        "righe": [["fedeli", 12], ["a rischio", 7]]}).encode()
    falsa = await admin.post("/analytics/importa", content=corpo, headers={"Authorization": f"Bearer {t}", "X-Firma": "00"})
    assert falsa.status_code == 401
    alterato = corpo.replace(b"12", b"99")
    r = await admin.post("/analytics/importa", content=alterato,
                         headers={"Authorization": f"Bearer {t}", "X-Firma": colab.firma(t, corpo)})
    assert r.status_code == 401
    r = await admin.post("/analytics/importa", content=corpo,
                         headers={"Authorization": f"Bearer {t}", "X-Firma": colab.firma(t, corpo)})
    assert r.status_code == 201 and r.json()["righe"] == 2
    admin.identita.principal = principal_admin
    studi = (await admin.get("/admin/analytics/studi")).json()
    assert studi["risultati"][0]["titolo"] == "Segmenti RFM"
    assert studi["risultati"][0]["righe"] == [["fedeli", 12], ["a rischio", 7]]
    assert studi["token"][0]["ultimo_uso"] is not None


async def test_import_malformato(admin):
    t = (await _token(admin))["token"]
    admin.identita.principal = None
    corpo = json.dumps({"titolo": "x", "colonne": ["a", "b"], "righe": [[1]]}).encode()
    r = await admin.post("/analytics/importa", content=corpo, headers={"Authorization": f"Bearer {t}", "X-Firma": colab.firma(t, corpo)})
    assert r.status_code == 422


async def test_notebook_precompilato_senza_token(admin):
    r = await admin.get("/admin/analytics/studi/notebook.ipynb?collezione=ricavi&giorni=60")
    assert r.status_code == 200
    nb = json.loads(r.text)
    sorgente = "".join("".join(c["source"]) for c in nb["cells"])
    assert 'COLLEZIONE = "ricavi"' in sorgente and "GIORNI = 60" in sorgente and "getpass" in sorgente
    assert "lnt_" not in sorgente
    compile("".join(nb["cells"][1]["source"]), "cella", "exec")  # la cella principale è Python valido
