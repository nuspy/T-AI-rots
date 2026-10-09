"""Il responso in diretta (9/10/2026): chi ha un account legge il testo mentre il modello lo scrive, la guardia giudica
alla fine e, se fa riscrivere o blocca, il testo visto si sostituisce. Un anonimo riceve solo l'anteprima, come prima.

Sempre il modello finto (`tarot/finto.py`), che scrive parola per parola; la guardia si sostituisce dove serve un
verdetto diverso da «ok»."""
from __future__ import annotations

import pytest

from tarot_core.api.routers import readings
from tarot_core.guards.lettura import Verdetto
from tarot_core.tarot.finto import ModelloFinto

from .conftest import eventi_sse, richiede_database
from .test_interpretazione_unica import _fino_alla_rivelazione

pytestmark = richiede_database


async def _fino_alla_sintesi(client, session) -> str:
    rid = await _fino_alla_rivelazione(client, session)
    eventi = eventi_sse((await client.post(f"/readings/{rid}/reveal-all")).text)
    assert eventi[-1][0] == "fine" and eventi[-1][1]["ultima"]
    return rid


def _testo_visto(eventi) -> str:
    """Il testo come lo mostra un client: i `token` si accodano, un `sostituisci` prende il posto di tutto."""
    testo = ""
    for e, d in eventi:
        if e == "token":
            testo += d["testo"]
        elif e == "sostituisci":
            testo = d["testo"]
    return testo


async def test_il_responso_arriva_prima_della_guardia(client, session, catalogo, monkeypatch):
    rid = await _fino_alla_sintesi(client, session)
    monkeypatch.setattr(ModelloFinto, "pausa", 0.001)
    eventi = eventi_sse((await client.post(f"/readings/{rid}/synthesis")).text)
    nomi = [e for e, _ in eventi]
    guardia = nomi.index("fase", 1)
    assert eventi[guardia][1] == {"fase": "guardia"}
    # Molti pezzi, tutti prima della guardia: il testo si legge mentre il modello lo scrive.
    assert nomi[:guardia].count("token") > 5
    assert "sostituisci" not in nomi and nomi[-1] == "fine" and eventi[-1][1]["guardia"] == "ok"
    salvato = (await client.get(f"/me/readings/{rid}")).json()["synthesis"]
    assert _testo_visto(eventi).strip() == salvato and "## Il quadro" in salvato


async def test_se_la_guardia_fa_riscrivere_il_testo_si_sostituisce(client, session, catalogo, monkeypatch):
    rid = await _fino_alla_sintesi(client, session)
    verdetti = iter([
        Verdetto("riscrivi", [{"regola": "fatalismo", "motivo": "prova", "estratto": "quadro"}]),
        Verdetto("ok"),
    ])

    async def guardia_finta(*_a, **_k):
        return next(verdetti)

    async def riscrittura(_autore, _req):
        return "## Il quadro\n\nUn testo riscritto secondo le correzioni della guardia."

    monkeypatch.setattr(readings, "giudica", guardia_finta)
    # La riscrittura (non in diretta) dà un testo diverso dal primo, come farebbe un modello vero.
    monkeypatch.setattr(readings, "genera_testo", riscrittura)
    eventi = eventi_sse((await client.post(f"/readings/{rid}/synthesis")).text)
    nomi = [e for e, _ in eventi]
    assert {"fase": "revisione"} in [d for e, d in eventi if e == "fase"]
    assert "sostituisci" in nomi and nomi.index("sostituisci") > nomi.index("token")
    assert eventi[-1][1]["guardia"] == "riscritto"
    assert _testo_visto(eventi) == "## Il quadro\n\nUn testo riscritto secondo le correzioni della guardia."
    assert _testo_visto(eventi).strip() == (await client.get(f"/me/readings/{rid}")).json()["synthesis"]


async def test_un_responso_bloccato_non_resta_sullo_schermo(client, session, catalogo, monkeypatch):
    rid = await _fino_alla_sintesi(client, session)

    async def blocca(*_a, **_k):
        return Verdetto("blocca", [{"regola": "crisi", "motivo": "prova"}])

    monkeypatch.setattr(readings, "giudica", blocca)
    eventi = eventi_sse((await client.post(f"/readings/{rid}/synthesis")).text)
    assert eventi[-1][1]["guardia"] == "bloccato"
    visto = _testo_visto(eventi)
    assert "## Il quadro" not in visto and visto == (await client.get(f"/me/readings/{rid}")).json()["synthesis"]


@pytest.mark.parametrize("anonimo", [True])
async def test_un_anonimo_vede_solo_l_anteprima(client, session, catalogo, anonimo):
    client.identita.principal = None
    r = await client.post("/readings/anonime", json={"spread_id": "tre-carte", "question": "Cosa mi aspetta?"})
    assert r.status_code == 201, r.text
    rid = r.json()["id"]
    r = await client.post(f"/readings/{rid}/interview", json={})
    while not r.json().get("completa"):
        r = await client.post(f"/readings/{rid}/interview", json={"risposta": "Da qualche mese."})
    await client.post(f"/readings/{rid}/fan")
    for i in range(3):
        await client.post(f"/readings/{rid}/pick", json={"slot": i * 2})
    await client.post(f"/readings/{rid}/reveal-all")
    eventi = eventi_sse((await client.post(f"/readings/{rid}/synthesis")).text)
    nomi = [e for e, _ in eventi]
    # Nessun testo prima della guardia: per un anonimo esce solo l'anteprima, dopo.
    assert "token" not in nomi[:nomi.index("fase", 1)]
    assert "## Il quadro" not in _testo_visto(eventi)
