"""Journal v9.4 attraverso l'API e un database vero: sezioni ricche (immagini, «By number», figli con articoli, stese
con tradizione e illustrazione), immagini di sezioni e stese per la skill (`blog:media`) e dalla console, elenchi per
carta e stesa, paginazione, «Chosen for this page» per pertinenza."""
from __future__ import annotations

import pytest

from tarot_core.auth import chiavi

from .conftest import richiede_database
from .test_blog_media import _b64
from .test_blog_rest import _chiave, _h, _png

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


async def _sezione(c, nome, **campi):
    r = await c.post("/admin/blog/sections", json={"nome": nome, **campi})
    assert r.status_code == 201, r.text
    return r.json()


async def _articolo(c, titolo, **campi):
    corpo = {"titolo": titolo, "testo": "Un testo di prova.", "lang": "en", "stato": "pubblicato", **campi}
    r = await c.post("/admin/blog/posts", json=corpo)
    assert r.status_code == 201, r.text
    return r.json()


async def _immagine(c) -> str:
    r = await c.post("/admin/blog/media", content=_png(), headers={"content-type": "image/png"})
    assert r.status_code == 201, r.text
    return r.json()["id"]


# ---- sezioni ricche ---------------------------------------------------------------------------------------------


async def test_il_filtro_rango_raccoglie_le_carte_di_tutti_i_semi_e_la_console_lo_valida(admin):
    assi = await _sezione(admin, "Aces", tipo="carte", filtro={"rango": "ace"})
    assert assi["filtro"] == {"rango": "asso"}            # salvato nella forma di deck.json
    elementi = (await admin.get("/blog/sections/aces")).json()["elementi"]
    assert [e["id"] for e in elementi] == ["bastoni-01", "coppe-01", "spade-01", "dischi-01"]
    # Page = Knave = Princess.
    await _sezione(admin, "Pages", tipo="carte", filtro={"rango": "page"})
    assert {e["rango"] for e in (await admin.get("/blog/sections/pages")).json()["elementi"]} == {"principessa"}
    r = await admin.post("/admin/blog/sections", json={"nome": "Kings", "tipo": "carte", "filtro": {"rango": "re-sole"}})
    assert r.status_code == 422
    r = await admin.patch(f"/admin/blog/sections/{assi['id']}", json={"filtro": {"rango": "10"}})
    assert r.status_code == 200 and r.json()["filtro"] == {"rango": "dieci"}


async def test_l_immagine_di_una_sezione_e_un_oggetto_e_ogni_figlio_porta_tre_articoli_del_suo_ramo(admin):
    img = await _immagine(admin)
    padre = await _sezione(admin, "Articles", tipo="contenitore", immagine_id=img, immagine_alt="A quiet library")
    amore = await _sezione(admin, "Love", parent_id=padre["id"], immagine_id=img, ordine=1)
    lavoro = await _sezione(admin, "Career", parent_id=padre["id"], ordine=2)
    for i in range(5):
        await _articolo(admin, f"Love {i}", sezione_id=amore["id"])
    await _articolo(admin, "Career 0", sezione_id=lavoro["id"])
    await _articolo(admin, "Bozza", stato="bozza", sezione_id=lavoro["id"])

    albero = (await admin.get("/blog/sections")).json()
    assert albero[0]["immagine"] == {"url": f"/blog/media/{img}.webp", "mini": f"/blog/media/{img}-mini.webp", "alt": "A quiet library"}
    assert albero[0]["figli"][0]["immagine"]["alt"] == "Love"        # senza alt: il nome della sezione
    assert albero[0]["figli"][1]["immagine"] is None

    dettaglio = (await admin.get("/blog/sections/articles")).json()
    figli = {f["slug"]: f for f in dettaglio["figli"]}
    assert len(figli["love"]["articoli"]) == 3 and all(a["sezione"]["slug"] == "love" for a in figli["love"]["articoli"])
    assert [a["titolo"] for a in figli["career"]["articoli"]] == ["Career 0"]       # la bozza no
    assert (await admin.get("/blog/sections/articles")).json()["figli"] == dettaglio["figli"]   # stabile nel giorno
    # La console vede l'alt e la miniatura.
    piatte = {s["slug"]: s for s in (await admin.get("/admin/blog/sections")).json()}
    assert piatte["articles"]["immagine_alt"] == "A quiet library" and piatte["articles"]["immagine_mini"].endswith("-mini.webp")


async def test_le_stese_di_una_sezione_hanno_tradizione_schema_e_illustrazione(admin):
    await _sezione(admin, "Tarot Spreads", tipo="stese")
    img = await _immagine(admin)
    r = await admin.put("/admin/blog/catalogo-immagini/stesa/celtic-cross", json={"immagine_id": img, "alt": "A stone circle at dusk"})
    assert r.status_code == 200, r.text
    assert r.json()["riferimento"] == "croce-celtica" and r.json()["immagine"]["alt"] == "A stone circle at dusk"

    elementi = {e["id"]: e for e in (await admin.get("/blog/sections/tarot-spreads", params={"lang": "en"})).json()["elementi"]}
    croce = elementi["croce-celtica"]
    assert croce["tradizione"] == "Celtic tradition" and croce["tradizioni"]["it"] == "tradizione celtica"
    assert croce["n_carte"] == 10 and len(croce["posizioni"]) == 10 and {"x", "y", "rotazione"} <= set(croce["posizioni"][0])
    assert len(croce["descrizione_breve"]) <= 161 and croce["immagine"]["mini"] == f"/blog/media/{img}-mini.webp"
    assert elementi["tre-carte"]["immagine"] is None and elementi["croce-semplice"]["n_carte"] == 5

    # Le pagine pubbliche delle stese la restituiscono.
    assert (await admin.get("/spreads/croce-celtica", params={"lang": "en"})).json()["immagine"]["alt"] == "A stone circle at dusk"
    tutte = {s["id"]: s for s in (await admin.get("/spreads")).json()}
    assert tutte["croce-celtica"]["immagine"]["url"].endswith(".webp") and tutte["tre-carte"]["immagine"] is None

    # L'immagine in uso non si cancella; tolta dal catalogo, sì.
    assert (await admin.delete(f"/admin/blog/media/{img}")).status_code == 409
    assert (await admin.delete("/admin/blog/catalogo-immagini/stesa/croce-celtica")).status_code == 204
    assert (await admin.get("/spreads/croce-celtica")).json()["immagine"] is None
    assert (await admin.delete("/admin/blog/catalogo-immagini/stesa/croce-celtica")).status_code == 404
    assert (await admin.delete(f"/admin/blog/media/{img}")).status_code == 204


async def test_la_console_elenca_e_imposta_le_immagini_di_stese_e_sezioni(admin):
    await _sezione(admin, "Love")
    voci = (await admin.get("/admin/blog/catalogo-immagini")).json()
    stese = [v for v in voci if v["tipo"] == "stesa"]
    assert len(stese) == 19 and all(v["immagine"] is None for v in stese)
    assert [v["riferimento"] for v in voci if v["tipo"] == "sezione"] == ["love"]
    img = await _immagine(admin)
    r = await admin.put("/admin/blog/catalogo-immagini/sezione/love", json={"immagine_id": img, "alt": "Two cups"})
    assert r.status_code == 200 and r.json()["immagine"]["alt"] == "Two cups"
    assert (await admin.get("/blog/sections/love")).json()["immagine"]["url"] == f"/blog/media/{img}.webp"
    assert (await admin.get("/admin/blog/catalogo-immagini", params={"tipo": "sezione"})).json()[0]["immagine_id"] == img
    assert (await admin.put("/admin/blog/catalogo-immagini/stesa/nessuna", json={"immagine_id": img})).status_code == 404
    assert (await admin.put("/admin/blog/catalogo-immagini/sezione/nessuna", json={"immagine_id": img})).status_code == 404
    assert (await admin.put("/admin/blog/catalogo-immagini/carta/maj-00", json={"immagine_id": img})).status_code == 422
    assert (await admin.delete("/admin/blog/catalogo-immagini/sezione/love")).status_code == 204
    assert (await admin.get("/blog/sections/love")).json()["immagine"] is None


# ---- le immagini di sezioni e stese per la skill (`blog:media`) -----------------------------------------------------


async def test_la_skill_vede_cosa_manca_e_imposta_le_immagini_di_sezioni_e_stese(admin):
    await _sezione(admin, "Major Arcana", tipo="carte", filtro={"arcano": "maggiore"})
    media, _ = await _chiave(admin, ("blog:media",))
    scrittore, _ = await _chiave(admin, ("blog:write", "blog:publish"))
    assert (await admin.get("/v1/blog/media-sections", headers=_h(scrittore))).status_code == 403
    assert (await admin.get("/v1/blog/media-spreads", headers=_h(scrittore))).status_code == 403

    sezioni = (await admin.get("/v1/blog/media-sections", headers=_h(media))).json()
    assert [(s["slug"], s["immagine"]) for s in sezioni] == [("major-arcana", None)]
    r = await admin.put("/v1/blog/media-sections/major-arcana", json={"immagine_base64": _b64(), "alt": "A crown of\nstars"}, headers=_h(media))
    assert r.status_code == 200, r.text
    assert r.json()["slug"] == "major-arcana" and r.json()["immagine"]["alt"] == "A crown of stars"
    assert r.json()["immagine"]["mini"].endswith("-mini.webp")
    assert (await admin.get("/v1/blog/media-sections", headers=_h(media))).json()[0]["immagine"] == r.json()["immagine"]
    caricata = (await admin.post("/v1/blog/media", content=_png(), headers={**_h(media), "content-type": "image/png"})).json()
    r = await admin.put("/v1/blog/media-sections/major-arcana", json={"immagine_id": caricata["id"], "alt": "A garden"}, headers=_h(media))
    assert r.status_code == 200 and r.json()["immagine"]["url"] == caricata["url"]
    assert (await admin.put("/v1/blog/media-sections/nessuna", json={"immagine_id": caricata["id"], "alt": "x y z"}, headers=_h(media))).status_code == 404
    assert (await admin.put("/v1/blog/media-sections/major-arcana", json={"alt": "Senza immagine"}, headers=_h(media))).status_code == 422

    stese = (await admin.get("/v1/blog/media-spreads", headers=_h(media))).json()
    assert len(stese) == 19 and all(s["immagine"] is None for s in stese)
    croce = next(s for s in stese if s["id"] == "croce-celtica")
    assert croce["slug"] == "celtic-cross" and croce["tradizione"] == "Celtic tradition" and croce["n_carte"] == 10
    r = await admin.put("/v1/blog/media-spreads/celtic-cross", json={"immagine_base64": _b64(), "alt": "Standing stones"}, headers=_h(media))
    assert r.status_code == 200, r.text
    assert r.json()["id"] == "croce-celtica" and r.json()["slug"] == "celtic-cross" and r.json()["immagine"]["alt"] == "Standing stones"
    # Una seconda volta la sostituisce (una riga sola).
    r2 = await admin.put("/v1/blog/media-spreads/croce-celtica", json={"immagine_id": caricata["id"], "alt": "A garden"}, headers=_h(media))
    assert r2.json()["immagine"]["url"] == caricata["url"]
    stese = {s["id"]: s for s in (await admin.get("/v1/blog/media-spreads", headers=_h(media))).json()}
    assert stese["croce-celtica"]["immagine"]["url"] == caricata["url"]
    assert sum(1 for s in stese.values() if s["immagine"]) == 1
    assert (await admin.put("/v1/blog/media-spreads/nessuna", json={"immagine_id": caricata["id"], "alt": "x y z"}, headers=_h(media))).status_code == 404
    voci = (await admin.get("/admin/audit?azione=blog.rest.spread_image&limite=5")).json()
    assert voci and voci[0]["prima"]["alt"] == "Standing stones"


# ---- elenchi per carta e stesa, paginazione -----------------------------------------------------------------------


async def test_l_elenco_per_carta_da_prima_il_soggetto_poi_le_citazioni(admin):
    soggetto = await _articolo(admin, "Wheel of Fortune Tarot Meaning")
    citante = await _articolo(admin, "Luck and cycles", testo="Think of [[card:fortune]] here.")
    await _articolo(admin, "Something else")
    altro_soggetto = await _articolo(admin, "Fortune tarot card in love readings")
    r = (await admin.get("/blog/posts", params={"carta": "maj-10"})).json()
    assert r["totale"] == 3
    assert [a["slug"] for a in r["articoli"]] == [altro_soggetto["slug"], soggetto["slug"], citante["slug"]]
    assert r["articoli"][0]["soggetto"] == {"tipo": "carta", "ref": "maj-10", "nome": "Fortune", "slug": "fortune"}
    # Per slug, e per stesa; uno sconosciuto è 404.
    assert (await admin.get("/blog/posts", params={"carta": "fortune"})).json()["totale"] == 3
    await _articolo(admin, "Reading the Celtic Cross")
    assert (await admin.get("/blog/posts", params={"stesa": "celtic-cross"})).json()["totale"] == 1
    assert (await admin.get("/blog/posts", params={"carta": "maj-99"})).status_code == 404


@pytest.mark.parametrize("per_pagina", [10, 25, 50])
async def test_per_pagina_ammette_10_25_e_50(admin, per_pagina):
    for i in range(12):
        await _articolo(admin, f"Articolo {i}")
    r = (await admin.get("/blog/posts", params={"per_pagina": per_pagina})).json()
    assert r["per_pagina"] == per_pagina and len(r["articoli"]) == min(12, per_pagina)
    assert r["pagine"] == -(-12 // per_pagina)


async def test_per_pagina_oltre_50_si_rifiuta_e_il_predefinito_resta_12(admin):
    assert (await admin.get("/blog/posts", params={"per_pagina": 51})).status_code == 422
    assert (await admin.get("/blog/posts")).json()["per_pagina"] == 12


# ---- «Chosen for this page» per pertinenza --------------------------------------------------------------------------


async def test_nove_per_una_carta_prima_il_soggetto_poi_le_citazioni_e_niente_a_caso(admin):
    sul_soggetto = [await _articolo(admin, f"Wheel of Fortune tarot {i}") for i in range(2)]
    citanti = [await _articolo(admin, f"Cycles {i}", testo="See [[card:maj-10]].") for i in range(2)]
    for i in range(6):
        await _articolo(admin, f"Unrelated {i}")
    await _articolo(admin, "Ruota della fortuna nei tarocchi", lang="it")

    dati = (await admin.get("/blog/nove", params={"carta": "maj-10", "lang": "en"})).json()
    scelti = [a["slug"] for a in dati["scelti"]]
    # Solo i pertinenti, prima chi ha la carta come soggetto: nessun riempimento con il resto del diario.
    assert len(scelti) == 4
    assert set(scelti[:2]) == {a["slug"] for a in sul_soggetto} and set(scelti[2:]) == {a["slug"] for a in citanti}
    # Le recenti non ripetono le scelte; tutte in inglese.
    assert not set(scelti) & {a["slug"] for a in dati["recenti"]} and len(dati["recenti"]) == 3
    assert all(a["lang"] == "en" for a in dati["scelti"] + dati["recenti"])
    assert (await admin.get("/blog/nove", params={"carta": "maj-10", "lang": "en"})).json() == dati
    # Senza lingua c'è anche l'articolo italiano sul soggetto, fra i primi.
    tutti = (await admin.get("/blog/nove", params={"carta": "fortune"})).json()["scelti"]
    assert "ruota-della-fortuna-nei-tarocchi" in [a["slug"] for a in tutti[:3]]


async def test_nove_per_una_stesa_e_per_un_articolo(admin):
    stesa = await _articolo(admin, "How to read the Celtic Cross")
    citante = await _articolo(admin, "A big reading", testo="Use the [[spread:celtic-cross]].")
    await _articolo(admin, "Unrelated")
    dati = (await admin.get("/blog/nove", params={"stesa": "croce-celtica"})).json()
    assert [a["slug"] for a in dati["scelti"]] == [stesa["slug"], citante["slug"]]

    # Per un articolo: chi ha il suo stesso soggetto, poi chi lo cita, poi i correlati; poi il resto (completa).
    letto = await _articolo(admin, "The Tower tarot card meaning", tags=["Change"])
    stesso = await _articolo(admin, "The Tower in love: a tarot reading")
    correlato = await _articolo(admin, "Sudden change", tags=["Change"])
    cita = await _articolo(admin, "Lightning", testo="Like [[card:the-tower]].")
    dati = (await admin.get("/blog/nove", params={"articolo": letto["slug"], "scelti": 6})).json()
    scelti = [a["slug"] for a in dati["scelti"]]
    assert letto["slug"] not in scelti
    assert scelti[:3] == [stesso["slug"], cita["slug"], correlato["slug"]]
    assert len(scelti) == 6        # completata con il resto del diario
