"""Le uscite (v8.6): la pagina d'uscita di ogni visita e, per le pagine di lettura, l'ultima azione."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from ..analytics import uscite
from .conftest import richiede_database
from .test_analytics_console import IPHONE, OGGI, WINDOWS, _visita, stato_pulito  # noqa: F401  (fixture autouse)

pytestmark = richiede_database


@pytest.fixture
def admin(client, principal_admin):
    client.identita.principal = principal_admin
    return client


async def _visite(session):
    # 1. Esce dal blog dopo la home.
    await _visita(session, "198.51.100.1", IPHONE, {"n": "page_view", "p": "/"}, {"n": "page_view", "p": "/blog"})
    # 2. Esce dalla lettura dopo aver tagliato il mazzo (le fasi e i gesti della v2).
    await _visita(session, "198.51.100.2", WINDOWS,
                  {"n": "page_view", "p": "/read"},
                  {"n": "lettura_fase", "p": "/read", "x": {"fase": "preparazione"}},
                  {"n": "shuffle_started", "p": "/read"},
                  {"n": "lettura_fase", "p": "/read", "x": {"fase": "taglio"}},
                  {"n": "engagement", "p": "/read", "d": 4000})
    # 3. Esce dalla lettura senza toccare nulla.
    await _visita(session, "198.51.100.3", WINDOWS, {"n": "page_view", "p": "/it/read"}, {"n": "vista", "p": "/it/read"})
    # 4. Legge, va al blog, torna alla lettura e se ne va: conta solo ciò che fa dopo l'ultimo ingresso.
    prima = datetime.now(timezone.utc) - timedelta(minutes=5)
    await _visita(session, "198.51.100.4", IPHONE,
                  {"n": "page_view", "p": "/read"}, {"n": "card_drawn", "p": "/read"}, {"n": "page_view", "p": "/blog"},
                  quando=prima)
    await _visita(session, "198.51.100.4", IPHONE, {"n": "page_view", "p": "/read"})
    # 5. La lettura col mazzo fisico.
    await _visita(session, "198.51.100.5", IPHONE,
                  {"n": "page_view", "p": "/physical-reading"}, {"n": "physical_reading_started", "p": "/physical-reading"})
    await session.commit()


def test_pagine_di_lettura():
    assert uscite.e_lettura("/read") and uscite.e_lettura("/it/read/") and uscite.e_lettura("/old/leggi")
    assert uscite.e_lettura("/physical-reading") and uscite.e_lettura("/it/physical-reading")
    assert not uscite.e_lettura("/reader") and not uscite.e_lettura("/blog") and not uscite.e_lettura(None)
    assert uscite.etichetta("lettura_fase:taglio") == "Fase: mescola e taglia"
    assert uscite.etichetta("lettura_fase:nuova") == "Fase: nuova"


async def test_pagine_d_uscita_e_ultima_azione_della_lettura(session):
    await _visite(session)
    esito = await uscite.uscite(session, OGGI, OGGI)

    assert esito["sessioni"] == 5
    per_pagina = {p["pagina"]: p for p in esito["pagine"]}
    assert per_pagina["/read"]["uscite"] == 2 and per_pagina["/read"]["lettura"] is True
    assert per_pagina["/blog"]["uscite"] == 1 and per_pagina["/blog"]["lettura"] is False
    # /read: tre pagine viste (la visita 2 una, la 4 due), due uscite.
    assert per_pagina["/read"]["visualizzazioni"] == 3
    assert per_pagina["/read"]["tasso_uscita"] == pytest.approx(2 / 3, abs=1e-3)
    assert per_pagina["/it/read"]["uscite_unica_pagina"] == 1

    letture = esito["letture"]
    assert letture["sessioni"] == 4
    azioni = {a["azione"]: a["sessioni"] for a in letture["azioni"]}
    # la fase, non il tempo attivo; «solo vista» per chi non tocca nulla (la 3 e la 4, che è tornata senza agire)
    assert azioni == {"lettura_fase:taglio": 1, uscite.SOLO_VISTA: 2, "physical_reading_started": 1}
    voci = {p["pagina"]: p for p in letture["per_pagina"]}
    assert voci["/read"]["sessioni"] == 2
    assert {a["azione"] for a in voci["/read"]["azioni"]} == {"lettura_fase:taglio", uscite.SOLO_VISTA}
    assert next(a for a in letture["azioni"] if a["azione"] == "lettura_fase:taglio")["etichetta"] == "Fase: mescola e taglia"


async def test_endpoint_uscite(admin, session):
    await _visite(session)
    r = await admin.post("/admin/analytics/uscite", json={"da": OGGI.isoformat(), "a": OGGI.isoformat()})
    assert r.status_code == 200, r.text
    assert r.json()["letture"]["sessioni"] == 4
    r = await admin.post("/admin/analytics/uscite", json={"da": OGGI.isoformat(), "a": (OGGI - timedelta(days=1)).isoformat()})
    assert r.status_code == 422


async def test_uscite_solo_admin(client):
    r = await client.post("/admin/analytics/uscite", json={"da": OGGI.isoformat(), "a": OGGI.isoformat()})
    assert r.status_code == 403
