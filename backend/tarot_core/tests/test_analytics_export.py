"""Export degli analytics (v8): CSV e XLSX uguali alla vista, collezioni tutte valide."""
from __future__ import annotations

import io
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from openpyxl import load_workbook

from ..analytics import viste
from ..analytics.catalogo import CATALOGO
from .conftest import richiede_database
from .test_analytics_console import _traffico, stato_pulito  # noqa: F401  (fixture autouse)

pytestmark = richiede_database

OGGI = datetime.now(ZoneInfo("Europe/Rome")).date()
VISTA = {
    "sorgente": "visite", "misure": ["sessioni", "pagine"], "dimensioni": ["canale"],
    "da": OGGI.isoformat(), "a": OGGI.isoformat(),
}


async def test_csv_uguale_alla_vista(client, session, principal_admin):
    await _traffico(session)
    await session.commit()
    client.identita.principal = principal_admin
    vista = (await client.post("/admin/analytics/interroga", json=VISTA)).json()
    r = await client.post("/admin/analytics/esporta?formato=csv", json=VISTA)
    assert r.status_code == 200 and "attachment" in r.headers["content-disposition"]
    righe = r.content.decode("utf-8-sig").strip().split("\r\n")
    assert righe[0] == "Canale;Sessioni;Pagine viste"
    assert len(righe) == len(vista["righe"]) + 2  # intestazione + righe + totale
    assert righe[-1] == f"Totale;{vista['totali']['sessioni']};{vista['totali']['pagine']}"


async def test_xlsx_uguale_alla_vista(client, session, principal_admin):
    await _traffico(session)
    await session.commit()
    client.identita.principal = principal_admin
    vista = (await client.post("/admin/analytics/interroga", json=VISTA)).json()
    r = await client.post("/admin/analytics/esporta?formato=xlsx", json=VISTA)
    assert r.status_code == 200
    foglio = load_workbook(io.BytesIO(r.content)).active
    valori = [[c.value for c in riga] for riga in foglio.iter_rows(min_row=4)]
    assert valori[0] == ["Canale", "Sessioni", "Pagine viste"]
    assert [v[0] for v in valori[1:-1]] == [x["canale"] for x in vista["righe"]]
    assert valori[-1] == ["Totale", vista["totali"]["sessioni"], vista["totali"]["pagine"]]


@pytest.mark.parametrize("nome", list(viste.COLLEZIONI))
async def test_ogni_collezione_si_esporta(client, principal_admin, nome):
    client.identita.principal = principal_admin
    r = await client.get(f"/admin/analytics/collezioni/{nome}.xlsx?giorni=30")
    assert r.status_code == 200, r.text
    libro = load_workbook(io.BytesIO(r.content))
    _, costruisci = viste.COLLEZIONI[nome]
    assert len(libro.worksheets) == len(costruisci(OGGI - timedelta(days=29), OGGI))


def test_le_collezioni_usano_solo_nomi_del_catalogo():
    from lanterna.interroga import valida

    for _, (_, costruisci) in viste.COLLEZIONI.items():
        for _, q, _ in costruisci(OGGI - timedelta(days=6), OGGI):
            valida(CATALOGO, q)
