"""Le miniature delle immagini del blog e il permesso `blog:media` (v8.3), attraverso l'API e un database vero."""
from __future__ import annotations

import base64
import io

import pytest

from tarot_core.auth import chiavi

from .conftest import richiede_database
from .test_blog_rest import ARTICOLO, _chiave, _h, _png

pytestmark = richiede_database


@pytest.fixture(autouse=True)
def _senza_limiti():
    chiavi.azzera_limiti()
    yield
    chiavi.azzera_limiti()


@pytest.fixture
def admin(client, principal_admin):
    client.identita.principal = principal_admin
    return client


def _b64(larghezza=1200, altezza=800, colore=(120, 40, 90)) -> str:
    return base64.b64encode(_png(larghezza, altezza, colore)).decode()


def _dimensioni(webp: bytes):
    from PIL import Image

    return Image.open(io.BytesIO(webp)).size


TESTO = (
    "Primo paragrafo.\n\n"
    "![Una stesa sul tavolo](/blog/media/00000000-0000-0000-0000-000000000001.webp)\n\n"
    "Secondo paragrafo.\n\n"
    "![Un'altra stesa](/blog/media/00000000-0000-0000-0000-000000000002.webp)\n\n"
    "Ultimo paragrafo."
)


async def _pubblicato_da_altri(admin, testo=TESTO, titolo="Di un altro agente"):
    autore, _ = await _chiave(admin, ("blog:write", "blog:publish"))
    r = await admin.post("/v1/blog/posts", json={**ARTICOLO, "titolo": titolo, "testo": testo, "stato": "pubblicato"}, headers=_h(autore))
    assert r.status_code == 201, r.text
    return r.json()["articolo"]


# ---- miniature ------------------------------------------------------------------------------------------------


def test_la_miniatura_e_larga_480_e_non_ingrandisce():
    from tarot_core.tarot import blog as regole

    grande, _, _ = regole.prepara_immagine_articolo(_png(1600, 900))
    mini, larghezza, altezza = regole.miniatura(grande)
    assert (larghezza, altezza) == (480, 270) and _dimensioni(mini) == (480, 270) and len(mini) < len(grande)
    piccola, _, _ = regole.prepara_immagine_articolo(_png(300, 200))
    assert regole.miniatura(piccola)[1:] == (300, 200)


async def test_ogni_caricamento_crea_la_miniatura_e_la_si_serve(admin):
    chiave, _ = await _chiave(admin)
    r = await admin.post("/v1/blog/media", content=_png(1600, 900), headers={**_h(chiave), "content-type": "image/png"})
    assert r.status_code == 201
    j = r.json()
    assert j["mini"] == j["url"].replace(".webp", "-mini.webp")
    mini = await admin.get(j["mini"])
    assert mini.status_code == 200 and mini.headers["content-type"] == "image/webp" and _dimensioni(mini.content) == (480, 270)
    assert _dimensioni((await admin.get(j["url"])).content) == (1600, 900)
    # dalla console
    c = await admin.post("/admin/blog/media", content=_png(1000, 1000), headers={"content-type": "image/png"})
    assert c.status_code == 201 and _dimensioni((await admin.get(c.json()["mini"])).content) == (480, 480)


async def test_gli_elenchi_pubblici_danno_la_miniatura(admin):
    chiave, _ = await _chiave(admin, ("blog:write", "blog:publish"))
    await admin.post("/v1/blog/posts", json={**ARTICOLO, "stato": "pubblicato", "immagine_base64": _b64()}, headers=_h(chiave))
    immagine = (await admin.get("/blog/posts")).json()["articoli"][0]["immagine"]
    assert immagine["mini"].endswith("-mini.webp") and immagine["url"].endswith(".webp") and not immagine["url"].endswith("-mini.webp")


async def test_un_immagine_senza_miniatura_la_riceve_quando_si_assegna_e_con_lo_strumento(admin, session, session_factory):
    from sqlalchemy import select

    from tarot_core.domain.blog_models import MediaImage
    from tarot_core.tarot import blog as regole

    webp, larghezza, altezza = regole.prepara_immagine_articolo(_png(1200, 600))
    vecchie = [MediaImage(uso="blog", webp=webp, larghezza=larghezza, altezza=altezza) for _ in range(3)]
    session.add_all(vecchie)
    await session.commit()
    # la vecchia servita come miniatura, finché non ce l'ha, è la grande
    assert _dimensioni((await admin.get(f"/blog/media/{vecchie[0].id}-mini.webp")).content) == (1200, 600)
    # assegnarla a un articolo le dà la miniatura
    chiave, _ = await _chiave(admin)
    r = await admin.post("/v1/blog/posts", json={**ARTICOLO, "immagine_id": str(vecchie[0].id)}, headers=_h(chiave))
    assert r.status_code == 201
    assert _dimensioni((await admin.get(f"/blog/media/{vecchie[0].id}-mini.webp")).content) == (480, 240)
    # lo strumento dà la miniatura alle altre, e rilanciato non fa niente
    from tarot_core.tools import miniature_blog

    assert await miniature_blog.crea_miniature(session_factory, 1) == 2
    assert await miniature_blog.crea_miniature(session_factory, 1) == 0
    session.expire_all()
    senza = (await session.execute(select(MediaImage).where(MediaImage.mini_webp.is_(None), MediaImage.uso != "avatar"))).scalars().all()
    assert senza == []


# ---- il permesso blog:media ------------------------------------------------------------------------------------


async def test_blog_media_vede_tutti_gli_articoli_ma_non_scrive_testo(admin):
    art = await _pubblicato_da_altri(admin)
    media, _ = await _chiave(admin, ("blog:media",))
    elenco = (await admin.get("/v1/blog/media-posts", headers=_h(media))).json()
    assert elenco["totale"] == 1
    riga = elenco["articoli"][0]
    assert riga["id"] == art["id"] and riga["copertina"] is None and "testo" not in riga
    assert [i["alt"] for i in riga["immagini_nel_testo"]] == ["Una stesa sul tavolo", "Un'altra stesa"]
    dettaglio = (await admin.get(f"/v1/blog/media-posts/{art['id']}", headers=_h(media))).json()
    assert dettaglio["testo"] == TESTO and dettaglio["parola_chiave"] == ARTICOLO["seo_parola_chiave"]
    # niente del resto: né creare, né modificare, né leggere con gli endpoint di scrittura
    assert (await admin.post("/v1/blog/posts", json=ARTICOLO, headers=_h(media))).status_code == 403
    assert (await admin.patch(f"/v1/blog/posts/{art['id']}", json={"testo": "Rubato"}, headers=_h(media))).status_code == 403
    assert (await admin.delete(f"/v1/blog/posts/{art['id']}", headers=_h(media))).status_code == 403
    # ma può leggere la guida e caricare immagini
    assert (await admin.get("/v1/blog/guide", headers=_h(media))).status_code == 200
    assert (await admin.post("/v1/blog/media", content=_png(), headers={**_h(media), "content-type": "image/png"})).status_code == 201


async def test_senza_blog_media_gli_endpoint_delle_immagini_rispondono_403(admin):
    art = await _pubblicato_da_altri(admin)
    scrittore, _ = await _chiave(admin, ("blog:write", "blog:publish"))
    assert (await admin.get("/v1/blog/media-posts", headers=_h(scrittore))).status_code == 403
    r = await admin.put(f"/v1/blog/posts/{art['id']}/cover", json={"immagine_base64": _b64(), "alt": "Una copertina"}, headers=_h(scrittore))
    assert r.status_code == 403


async def test_la_copertina_si_cambia_anche_su_un_articolo_pubblicato_di_altri(admin):
    art = await _pubblicato_da_altri(admin)
    media, _ = await _chiave(admin, ("blog:media",))
    r = await admin.put(
        f"/v1/blog/posts/{art['id']}/cover",
        json={"immagine_base64": _b64(), "alt": "Una donna legge una lettera\nalla finestra"}, headers=_h(media),
    )
    assert r.status_code == 200, r.text
    cop = r.json()["copertina"]
    assert cop["alt"] == "Una donna legge una lettera alla finestra" and cop["mini"].endswith("-mini.webp")
    assert _dimensioni((await admin.get(cop["mini"])).content)[0] == 480
    # il resto non cambia: stato, titolo, testo
    pubblico = (await admin.get(f"/blog/posts/{art['slug']}")).json()
    assert pubblico["titolo"] == "Di un altro agente" and pubblico["immagine"]["url"] == cop["url"]
    # con un'immagine già caricata
    caricata = (await admin.post("/v1/blog/media", content=_png(), headers={**_h(media), "content-type": "image/png"})).json()
    r = await admin.put(f"/v1/blog/posts/{art['id']}/cover", json={"immagine_id": caricata["id"], "alt": "Un giardino"}, headers=_h(media))
    assert r.status_code == 200 and r.json()["copertina"]["id"] == caricata["id"]
    # errori chiari
    assert (await admin.put(f"/v1/blog/posts/{art['id']}/cover", json={"alt": "Senza immagine"}, headers=_h(media))).status_code == 422
    assert (await admin.put(
        "/v1/blog/posts/00000000-0000-0000-0000-000000000000/cover", json={"immagine_base64": _b64(), "alt": "Nessuno"}, headers=_h(media),
    )).status_code == 404


async def test_le_immagini_nel_testo_si_sostituiscono_aggiungono_e_tolgono_senza_toccare_il_resto(admin):
    art = await _pubblicato_da_altri(admin)
    media, _ = await _chiave(admin, ("blog:media",))
    url_2 = "/blog/media/00000000-0000-0000-0000-000000000002.webp"
    r = await admin.put(f"/v1/blog/posts/{art['id']}/inline", json={
        "sostituisci": [
            {"indice": 0, "immagine_base64": _b64(colore=(10, 120, 60)), "alt": "Un sentiero nel bosco d'autunno"},
            {"url_attuale": url_2, "immagine_base64": _b64(colore=(200, 160, 40))},
        ],
        "aggiungi": [{"dopo_paragrafo": 0, "immagine_base64": _b64(colore=(20, 20, 120)), "alt": "Una lanterna accesa"}],
    }, headers=_h(media))
    assert r.status_code == 200, r.text
    j = r.json()
    immagini = j["immagini_nel_testo"]
    assert [i["alt"] for i in immagini] == ["Una lanterna accesa", "Un sentiero nel bosco d'autunno", "Un'altra stesa"]
    assert all("00000000-0000-0000-0000" not in i["url"] for i in immagini)
    paragrafi = j["testo"].split("\n\n")
    assert paragrafi[0] == "Primo paragrafo." and paragrafi[1].startswith("![Una lanterna accesa](")
    assert "Secondo paragrafo." in paragrafi and paragrafi[-1] == "Ultimo paragrafo."
    # ogni immagine nuova ha la sua miniatura
    for i in immagini:
        assert _dimensioni((await admin.get(i["url"].replace(".webp", "-mini.webp"))).content)[0] == 480
    # togliere
    r = await admin.put(f"/v1/blog/posts/{art['id']}/inline", json={"rimuovi": [2]}, headers=_h(media))
    assert r.status_code == 200 and len(r.json()["immagini_nel_testo"]) == 2
    assert "\n\n\n" not in r.json()["testo"] and r.json()["testo"].endswith("Secondo paragrafo.\n\nUltimo paragrafo.")
    # l'articolo resta pubblicato e il pubblico vede il testo nuovo
    pubblico = (await admin.get(f"/blog/posts/{art['slug']}")).json()
    assert "Una lanterna accesa" in pubblico["testo"] and "stesa" not in pubblico["testo"]


async def test_le_richieste_sbagliate_sulle_immagini_nel_testo_non_cambiano_niente(admin):
    art = await _pubblicato_da_altri(admin)
    media, _ = await _chiave(admin, ("blog:media",))
    for corpo in (
        {"sostituisci": [{"indice": 5, "immagine_base64": _b64()}]},
        {"sostituisci": [{"url_attuale": "/blog/media/non-c-e.webp", "immagine_base64": _b64()}]},
        {"sostituisci": [{"immagine_base64": _b64()}]},
        {"aggiungi": [{"dopo_paragrafo": 40, "immagine_base64": _b64(), "alt": "Troppo in là"}]},
        {"rimuovi": [9]},
    ):
        r = await admin.put(f"/v1/blog/posts/{art['id']}/inline", json=corpo, headers=_h(media))
        assert r.status_code == 422, (corpo, r.text)
    dettaglio = (await admin.get(f"/v1/blog/media-posts/{art['id']}", headers=_h(media))).json()
    assert dettaglio["testo"] == TESTO


async def test_la_console_crea_chiavi_con_blog_media_e_la_guida_lo_dice(admin):
    chiave, dati = await _chiave(admin, ("blog:media",))
    assert dati["scopes"] == ["blog:media"]
    guida = (await admin.get("/v1/blog/guide", headers=_h(chiave))).json()
    assert guida["chiave"]["scopes"] == ["blog:media"] and "PUT /v1/blog/posts/{id}/cover" in guida["percorsi"]["immagini_di_tutti_con_blog_media"]
    assert (await admin.post("/admin/blog/api-keys", json={"nome": "x", "scopes": ["blog:tutto"]})).status_code == 422
