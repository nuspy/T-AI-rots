"""Le immagini di un mazzo caricate dalla console (ZIP o cartella) e servite dall'API, senza ricostruire il sito;
lo slug valido; le carte d'esempio del voto (al massimo cinque, riordinabili, eliminabili)."""
from __future__ import annotations

import io
import zipfile

import pytest
from PIL import Image

from tarot_core.tarot import immagini_mazzo as im
from tarot_core.tarot.conoscenza import Conoscenza
from tarot_core.tarot.stampa_mazzo import carica_immagini

from .conftest import richiede_database

ATTESI = im.ids_attesi(Conoscenza.carica().ordine)


def _png(larghezza: int = 90, altezza: int = 160, colore=(120, 30, 60)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (larghezza, altezza), colore).save(buf, format="PNG")
    return buf.getvalue()


def _zip(file: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for nome, dati in file.items():
            z.writestr(nome, dati)
    return buf.getvalue()


_UNA = _png()


def _completo(prefisso: str = "", **extra: bytes) -> dict[str, bytes]:
    return {f"{prefisso}{cid}.png": _UNA for cid in ATTESI} | extra


# ---- regole: riconoscere, controllare, convertire --------------------------------------------------


def test_riconosce_le_carte_e_mette_da_parte_il_resto():
    r = im.riconosci(
        ["Lovers/MAJ-00.PNG", "Lovers/_staging/maj-01.png", "Lovers/.nascosta/maj-02.png", "__MACOSX/x.png",
         "Lovers/.DS_Store", "Lovers/note.txt", "Lovers/copertina.png", "Lovers/dorso.webp"],
        set(ATTESI),
    )
    assert r.scelti == {"maj-00": "Lovers/MAJ-00.PNG", "dorso": "Lovers/dorso.webp"}
    assert r.avanzano == ["Lovers/copertina.png"]
    assert "Lovers/_staging/maj-01.png" in r.ignorati and "Lovers/note.txt" in r.ignorati


def test_fra_originale_e_web_vince_la_cartella_web_altrimenti_e_un_doppione():
    r = im.riconosci(["Lovers/maj-00.png", "Lovers/Web/maj-00.webp", "a/maj-01.png", "b/maj-01.png"], set(ATTESI))
    assert r.scelti["maj-00"] == "Lovers/Web/maj-00.webp"
    assert r.doppioni == {"maj-01": ["a/maj-01.png", "b/maj-01.png"]}


def test_il_controllo_elenca_cosa_manca_e_cosa_avanza():
    r = im.riconosci(["maj-00.png", "dorso.png", "extra.png"], set(ATTESI))
    with pytest.raises(im.ImmaginiMazzoNonValide) as e:
        im.controlla(r, ATTESI)
    assert "maj-01" in e.value.dettaglio["mancanti"]
    assert e.value.dettaglio["avanzano"] == ["extra.png"]
    assert len(e.value.dettaglio["mancanti"]) == len(ATTESI) - 2


@pytest.mark.parametrize("cattivo", ["../maj-00.png", "/etc/maj-00.png", "C:/maj-00.png", "a/../../maj-00.png"])
def test_lo_zip_con_percorsi_pericolosi_si_rifiuta(cattivo):
    with pytest.raises(im.ImmaginiMazzoNonValide) as e:
        im.leggi_zip(_zip(_completo() | {cattivo: _UNA}), ATTESI)
    assert e.value.dettaglio["rifiutati"] == [cattivo]


def test_un_file_che_non_e_uno_zip_si_rifiuta():
    with pytest.raises(im.ImmaginiMazzoNonValide):
        im.leggi_zip(b"non sono uno zip", ATTESI)


def test_lo_zip_legge_solo_le_carte_scelte():
    r, dati = im.leggi_zip(_zip(_completo("Set/", **{"Set/stampa.pdf": b"%PDF"})), ATTESI)
    assert set(dati) == set(ATTESI)
    assert r.ignorati == ["Set/stampa.pdf"]


def test_la_carta_diventa_webp_alla_misura_del_sito():
    webp, larghezza, altezza = im.prepara_carta(_png(1440, 2560), "maj-00.png")
    assert (larghezza, altezza) == (360, 640)
    with Image.open(io.BytesIO(webp)) as img:
        assert img.format == "WEBP" and img.size == (360, 640)


def test_un_file_che_non_e_un_immagine_si_rifiuta():
    with pytest.raises(im.ImmaginiMazzoNonValide):
        im.prepara_carta(b"testo qualunque", "maj-00.png")


async def test_il_pdf_usa_le_immagini_gia_lette_senza_scaricarle():
    class Vietato:
        async def get(self, *a, **k):  # pragma: no cover - se lo chiama, il test fallisce
            raise AssertionError("non doveva scaricare niente")

    trovate = await carica_immagini(
        "slug-inesistente", ["maj-00.webp"], web_public_url="http://x", client=Vietato(),
        precaricate={"maj-00.webp": b"byte"},
    )
    assert trovate == {"maj-00.webp": b"byte"}


# ---- l'API --------------------------------------------------------------------------------------


@pytest.fixture
def come(client, principal_utente, principal_admin):
    def scegli(chi: str):
        client.identita.principal = principal_admin if chi == "admin" else principal_utente
        return client
    return scegli


async def _mazzo(admin, slug: str = "notte") -> None:
    r = await admin.post("/admin/decks", json={"slug": slug, "nome": "Notte"})
    assert r.status_code == 201, r.text


@richiede_database
@pytest.mark.parametrize("slug", ["Notte", "notte_2026", "-notte", "notte-", "not--te", "n"])
async def test_lo_slug_non_valido_si_rifiuta(come, slug):
    r = await come("admin").post("/admin/decks", json={"slug": slug, "nome": "Notte"})
    assert r.status_code == 422


@richiede_database
async def test_lo_zip_completo_si_pubblica_e_il_sito_lo_serve_subito(come):
    admin = come("admin")
    await _mazzo(admin)
    corpo = _zip(_completo("Notte/", **{"Notte/copertina.png": _UNA, "Notte/LEGGIMI.md": b"x"}))
    r = await admin.post("/admin/decks/notte/immagini/zip", content=corpo, headers={"Content-Type": "application/zip"})
    assert r.status_code == 200, r.text
    stato = r.json()
    assert stato["pubblicate"] == len(ATTESI) == 79
    assert stato["versione"]
    assert stato["riepilogo"]["avanzano"] == ["Notte/copertina.png"]

    come("utente")
    carta = await admin.get("/decks/notte/cards/maj-00.webp")
    assert carta.status_code == 200
    assert carta.headers["content-type"] == "image/webp"
    assert "max-age" in carta.headers["cache-control"]
    etag = carta.headers["etag"]
    assert (await admin.get("/decks/notte/cards/maj-00.webp", headers={"If-None-Match": etag})).status_code == 304
    versionata = await admin.get(f"/decks/notte/cards/dorso.webp?v={stato['versione']}")
    assert "immutable" in versionata.headers["cache-control"]
    assert (await admin.get("/decks/notte/cards/maj-99.webp")).status_code == 404
    assert (await admin.get("/decks/altro/cards/maj-00.webp")).status_code == 404

    # Il catalogo della console sa che il mazzo ha le sue immagini.
    elenco = (await come("admin").get("/admin/decks")).json()
    assert next(m for m in elenco if m["slug"] == "notte")["immagini_versione"] == stato["versione"]


@richiede_database
async def test_lo_zip_incompleto_non_cambia_niente_e_dice_cosa_manca(come):
    admin = come("admin")
    await _mazzo(admin)
    file = _completo()
    del file["coppe-03.png"]
    file["maj-0.png"] = _UNA
    r = await admin.post("/admin/decks/notte/immagini/zip", content=_zip(file))
    assert r.status_code == 422
    dettaglio = r.json()["detail"]
    assert dettaglio["mancanti"] == ["coppe-03"]
    assert dettaglio["avanzano"] == ["maj-0.png"]
    assert (await admin.get("/admin/decks/notte/immagini")).json()["pubblicate"] == 0


@richiede_database
async def test_la_cartella_si_carica_a_passi_e_si_pubblica_solo_completa(come):
    admin = come("admin")
    await _mazzo(admin)
    for cid in ATTESI[:-1]:
        r = await admin.post(
            "/admin/decks/notte/immagini/file", params={"percorso": f"Notte/Web/{cid}.png"}, content=_UNA,
            headers={"Content-Type": "image/png"},
        )
        assert r.status_code == 200, r.text
    assert r.json()["bozza"] == len(ATTESI) - 1

    incompleta = await admin.post("/admin/decks/notte/immagini/pubblica")
    assert incompleta.status_code == 422
    assert incompleta.json()["detail"]["mancanti"] == ["dorso"]
    assert (await admin.get("/decks/notte/cards/maj-00.webp")).status_code == 404  # la bozza non si vede

    await admin.post("/admin/decks/notte/immagini/file", params={"percorso": "dorso.webp"}, content=_UNA)
    r = await admin.post("/admin/decks/notte/immagini/pubblica")
    assert r.status_code == 200, r.text
    assert r.json()["pubblicate"] == 79 and r.json()["bozza"] == 0
    assert (await admin.get("/decks/notte/cards/maj-00.webp")).status_code == 200

    # Una seconda serie sostituisce la prima in blocco.
    versione = r.json()["versione"]
    altra = _png(colore=(10, 200, 10))
    r = await admin.post("/admin/decks/notte/immagini/zip", content=_zip({f"{c}.png": altra for c in ATTESI}))
    assert r.json()["pubblicate"] == 79 and r.json()["versione"] != versione

    assert (await admin.delete("/admin/decks/notte/immagini")).status_code == 204
    assert (await admin.get("/decks/notte/cards/maj-00.webp")).status_code == 404


@richiede_database
async def test_un_file_che_non_e_una_carta_si_rifiuta(come):
    admin = come("admin")
    await _mazzo(admin)
    r = await admin.post("/admin/decks/notte/immagini/file", params={"percorso": "copertina.png"}, content=_UNA)
    assert r.status_code == 422
    assert "non è una carta" in r.json()["detail"]["messaggio"]
    r = await admin.post("/admin/decks/notte/immagini/file", params={"percorso": "maj-00.png"}, content=b"niente")
    assert r.status_code == 422


@richiede_database
async def test_il_predefinito_e_gli_utenti_normali_no(come, session):
    from tarot_core.domain.deck_models import Deck

    session.add(Deck(nome="Thoth", slug="thoth", predefinito=True, attivo=True))
    await session.commit()
    admin = come("admin")
    assert (await admin.get("/admin/decks/thoth/immagini")).status_code == 409
    await _mazzo(admin)
    utente = come("utente")
    assert (await utente.post("/admin/decks/notte/immagini/zip", content=_zip(_completo()))).status_code == 403


# ---- le carte d'esempio del voto ------------------------------------------------------------------


@richiede_database
async def test_fino_a_cinque_carte_d_esempio_riordinabili_ed_eliminabili(come):
    admin = come("admin")
    cid = (await admin.post("/admin/voto/candidati", json={"nome": "Notte"})).json()["id"]
    caricate = []
    for i in range(5):
        r = await admin.post(
            f"/admin/voto/candidati/{cid}/campioni", content=_png(colore=(i * 40, 0, 0)),
            headers={"Content-Type": "image/png"},
        )
        assert r.status_code == 200, r.text
        caricate.append(r.json()["media_id"])
    assert r.json()["mini"].endswith("-mini.webp")
    sesta = await admin.post(f"/admin/voto/candidati/{cid}/campioni", content=_UNA, headers={"Content-Type": "image/png"})
    assert sesta.status_code == 409

    rovescio = list(reversed(caricate))
    r = await admin.put(f"/admin/voto/candidati/{cid}/campioni", json={"ordine": rovescio})
    assert [c["media_id"] for c in r.json()] == rovescio
    assert (await admin.put(f"/admin/voto/candidati/{cid}/campioni", json={"ordine": rovescio[:2]})).status_code == 409

    assert (await admin.delete(f"/admin/voto/candidati/{cid}/campioni/{caricate[0]}")).status_code == 204
    proposte = (await admin.get("/admin/voto/candidati/disponibili")).json()
    assert [c["media_id"] for c in proposte[0]["campioni"]] == rovescio[:-1]
    assert (await admin.get(f"/blog/media/{caricate[0]}.webp")).status_code == 404
