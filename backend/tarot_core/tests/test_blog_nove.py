"""Gli articoli in fondo a ogni pagina: le recenti + quelli scelti a caso dal database (una query), stabili nella
giornata, senza doppioni e senza l'articolo che si sta leggendo. Con una sezione o un'etichetta si pesca solo lì (dal
9/10/2026 niente riempimento con il resto del diario e niente pertinenza: costavano secondi a ogni pagina)."""
from __future__ import annotations

import pytest

from .conftest import richiede_database

pytestmark = richiede_database


@pytest.fixture
def admin(client, principal_admin):
    client.identita.principal = principal_admin
    return client


async def _sezione(c, nome):
    r = await c.post("/admin/blog/sections", json={"nome": nome})
    assert r.status_code == 201, r.text
    return r.json()


async def _articolo(c, titolo, **campi):
    r = await c.post("/admin/blog/posts", json={"titolo": titolo, "testo": "Un testo di prova.", "stato": "pubblicato", **campi})
    assert r.status_code == 201, r.text
    return r.json()


async def test_tre_recenti_e_le_altre_della_sezione_senza_doppioni(admin):
    amore = await _sezione(admin, "Amore")
    lavoro = await _sezione(admin, "Lavoro")
    for i in range(6):
        await _articolo(admin, f"Amore {i}", sezione_id=amore["id"])
    for i in range(6):
        await _articolo(admin, f"Lavoro {i}", sezione_id=lavoro["id"])

    r = await admin.get("/blog/nove", params={"sezione": amore["slug"]})
    assert r.status_code == 200, r.text
    dati = r.json()
    assert len(dati["recenti"]) == 3
    # Con una sezione recenti e scelte sono solo sue: le 3 recenti (Amore 5, 4, 3) e le altre 3, a caso.
    assert len(dati["scelti"]) == 3
    slug = [a["slug"] for a in dati["recenti"] + dati["scelti"]]
    assert len(slug) == len(set(slug))
    assert all((x["sezione"] or {}).get("slug") == amore["slug"] for x in dati["recenti"] + dati["scelti"])

    # Stessa giornata, stesso contesto: stessa scelta.
    assert (await admin.get("/blog/nove", params={"sezione": amore["slug"]})).json() == dati
    # Senza sezione si pesca da tutto il diario.
    tutti = (await admin.get("/blog/nove")).json()
    assert len(tutti["recenti"]) == 3 and len(tutti["scelti"]) == 6


async def test_l_articolo_che_si_legge_non_compare(admin):
    letto = await _articolo(admin, "Quello che leggo")
    for i in range(4):
        await _articolo(admin, f"Altro {i}")
    dati = (await admin.get("/blog/nove", params={"articolo": letto["slug"]})).json()
    slug = [a["slug"] for a in dati["recenti"] + dati["scelti"]]
    assert letto["slug"] not in slug
    assert len(slug) == 4


async def test_le_pagine_del_diario_chiedono_sei_recenti_e_dieci_a_caso(admin):
    for i in range(20):
        await _articolo(admin, f"Articolo {i}")
    dati = (await admin.get("/blog/nove", params={"recenti": 6, "scelti": 10})).json()
    assert len(dati["recenti"]) == 6 and len(dati["scelti"]) == 10
    elenco = (await admin.get("/blog/posts", params={"per_pagina": 6})).json()["articoli"]
    assert [a["slug"] for a in dati["recenti"]] == [a["slug"] for a in elenco]
    assert not {a["slug"] for a in dati["recenti"]} & {a["slug"] for a in dati["scelti"]}
