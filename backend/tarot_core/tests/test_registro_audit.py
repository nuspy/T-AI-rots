"""Il Registro in console (`GET /admin/audit`): la lettura, mai testata finora (la scrittura sì, indirettamente,
in `test_offerte.py` e `test_lettura_speciale.py`)."""
from __future__ import annotations

import pytest

from .conftest import richiede_database

pytestmark = richiede_database


@pytest.fixture
def come(client, principal_utente, principal_admin):
    def scegli(chi: str):
        client.identita.principal = principal_admin if chi == "admin" else principal_utente
        return client

    return scegli


async def test_solo_l_amministratore_legge_il_registro(come):
    assert (await come("utente").get("/admin/audit")).status_code == 403


async def test_una_scrittura_amministrativa_si_vede_nel_registro(come):
    admin = come("admin")
    r = await admin.post("/admin/plans", json={"slug": "prova-registro", "name": "Prova"})
    assert r.status_code == 201, r.text

    voci = (await admin.get("/admin/audit?limite=10")).json()
    assert any(v["azione"] == "plan.create" and v["target"] == "prova-registro" for v in voci)
    voce = next(v for v in voci if v["azione"] == "plan.create" and v["target"] == "prova-registro")
    assert voce["tipo"] == "plan" and voce["dopo"]["slug"] == "prova-registro" and voce["prima"] is None
    assert voce["attore"] is not None and "quando" in voce


async def test_il_filtro_per_azione_e_per_tipo_restringe(come):
    admin = come("admin")
    await admin.post("/admin/plans", json={"slug": "filtro-a", "name": "A"})
    await admin.post("/admin/plans", json={"slug": "filtro-b", "name": "B"})
    await admin.delete("/admin/plans/filtro-b")

    solo_creati = (await admin.get("/admin/audit?azione=plan.create&limite=200")).json()
    assert all(v["azione"] == "plan.create" for v in solo_creati)
    assert any(v["target"] == "filtro-a" for v in solo_creati)

    solo_piani = (await admin.get("/admin/audit?target_type=plan&limite=200")).json()
    assert all(v["tipo"] == "plan" for v in solo_piani)
    assert any(v["azione"] == "plan.delete" for v in solo_piani)


async def test_il_limite_e_lo_scarto_paginano(come):
    admin = come("admin")
    for i in range(5):
        await admin.post("/admin/plans", json={"slug": f"pagina-{i}", "name": f"P{i}"})

    prima_pagina = (await admin.get("/admin/audit?azione=plan.create&limite=2&offset=0")).json()
    seconda_pagina = (await admin.get("/admin/audit?azione=plan.create&limite=2&offset=2")).json()
    assert len(prima_pagina) == 2 and len(seconda_pagina) == 2
    assert {v["id"] for v in prima_pagina}.isdisjoint({v["id"] for v in seconda_pagina})
    # Più recenti per prime: la seconda pagina continua da dove la prima si è fermata, non la ripete.
    assert prima_pagina[-1]["quando"] >= seconda_pagina[0]["quando"]


async def test_il_limite_non_supera_500(come):
    voci = (await come("admin").get("/admin/audit?limite=10000")).json()
    assert len(voci) <= 500


async def test_uno_scarto_negativo_non_rompe_la_query(come):
    r = await come("admin").get("/admin/audit?offset=-5")
    assert r.status_code == 200
