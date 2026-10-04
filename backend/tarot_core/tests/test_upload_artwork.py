"""L'upload dell'artwork di un mazzo da GUI admin (v7, Fase I): validazione dei nomi file,
scarico con sessione autenticata, cancellazione dello staging."""
from __future__ import annotations

import io
import zipfile

import pytest

from tarot_core.tarot.conoscenza import Conoscenza

from .conftest import richiede_database

pytestmark = richiede_database


@pytest.fixture
def come(client, principal_utente, principal_admin):
    def scegli(chi: str):
        client.identita.principal = principal_admin if chi == "admin" else principal_utente
        return client
    return scegli


def _zip(nomi) -> bytes:
    """Uno ZIP con una data fissa per ogni file: `writestr` con un nome solo mette l'ora corrente (a passi di due
    secondi), e due ZIP «uguali» costruiti a cavallo di quel passo differivano. Nella suite completa, più lenta, il
    confronto fra lo ZIP caricato e uno ricostruito dopo falliva una volta su due."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for nome in nomi:
            z.writestr(zipfile.ZipInfo(nome, date_time=(2026, 1, 1, 0, 0, 0)), b"finto webp")
    return buf.getvalue()


def _zip_completo() -> bytes:
    conoscenza = Conoscenza.carica()
    nomi = [f"{cid}.webp" for cid in conoscenza.ordine] + ["dorso.webp"]
    return _zip(nomi)


async def test_upload_completo_viene_accettato(come):
    admin = come("admin")
    r = await admin.post("/admin/decks/prova-artwork/artwork", content=_zip_completo())
    assert r.status_code == 201, r.text
    assert r.json()["file_count"] == 79


async def test_upload_con_carte_mancanti_viene_rifiutato(come):
    admin = come("admin")
    r = await admin.post("/admin/decks/prova-artwork/artwork", content=_zip(["maj-00.webp", "dorso.webp"]))
    assert r.status_code == 400
    assert "maj-01.webp" in r.json()["detail"]["mancanti"]


async def test_upload_non_zip_viene_rifiutato(come):
    admin = come("admin")
    r = await admin.post("/admin/decks/prova-artwork/artwork", content=b"non e' uno zip")
    assert r.status_code == 400


async def test_scarico_e_cancellazione(come):
    admin = come("admin")
    caricato = _zip_completo()
    r = await admin.post("/admin/decks/prova-artwork/artwork", content=caricato)
    upload_id = r.json()["id"]

    scaricato = await admin.get(f"/admin/decks/prova-artwork/artwork/{upload_id}")
    assert scaricato.status_code == 200
    assert scaricato.content == caricato

    elenco = await admin.get("/admin/decks/prova-artwork/artwork")
    assert len(elenco.json()) == 1

    assert (await admin.delete(f"/admin/decks/prova-artwork/artwork/{upload_id}")).status_code == 204
    assert (await admin.get("/admin/decks/prova-artwork/artwork")).json() == []


async def test_un_utente_normale_non_puo_caricare(come):
    utente = come("utente")
    r = await utente.post("/admin/decks/prova-artwork/artwork", content=_zip_completo())
    assert r.status_code == 403
