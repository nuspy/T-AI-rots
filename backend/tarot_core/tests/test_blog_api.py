"""Il blog, attraverso l'API e un database vero: sezioni, articoli, visibilità, immagini, avatar."""
from __future__ import annotations

import io
from datetime import timedelta

import pytest

from tarot_core.domain.base import utcnow

from .conftest import richiede_database

pytestmark = richiede_database


def _png(larghezza=800, altezza=450, colore=(200, 40, 90)) -> bytes:
    from PIL import Image

    uscita = io.BytesIO()
    Image.new("RGB", (larghezza, altezza), colore).save(uscita, format="PNG")
    return uscita.getvalue()


@pytest.fixture
def admin(client, principal_admin):
    """Il client, da amministratore."""
    client.identita.principal = principal_admin
    return client


async def _sezione(c, nome="Amore", **campi):
    r = await c.post("/admin/blog/sections", json={"nome": nome, **campi})
    assert r.status_code == 201, r.text
    return r.json()


async def _articolo(c, titolo="La Papessa", pubblica=True, **campi):
    corpo = {"titolo": titolo, "testo": "Un testo di prova.", **campi}
    if pubblica and "stato" not in corpo:
        corpo["stato"] = "pubblicato"
    r = await c.post("/admin/blog/posts", json=corpo)
    assert r.status_code == 201, r.text
    return r.json()


async def _pubblici(c, **params):
    r = await c.get("/blog/posts", params=params)
    assert r.status_code == 200, r.text
    return r.json()


# ---- i permessi ---------------------------------------------------------------------------------


async def test_la_console_del_blog_richiede_il_ruolo_admin(client):
    for metodo, percorso in [("get", "/admin/blog/sections"), ("get", "/admin/blog/posts"), ("get", "/admin/blog/tags")]:
        assert (await getattr(client, metodo)(percorso)).status_code == 403
    assert (await client.post("/admin/blog/posts", json={"titolo": "x"})).status_code == 403
    assert (await client.post("/admin/blog/media", content=_png(), headers={"content-type": "image/png"})).status_code == 403


async def test_il_pubblico_legge_senza_account(client):
    assert (await client.get("/blog/sections")).status_code == 200
    assert (await client.get("/blog/posts")).json()["totale"] == 0


# ---- le sezioni ------------------------------------------------------------------------------------


async def test_le_sezioni_formano_un_albero_con_i_conteggi(admin):
    radice = await _sezione(admin, "Tarocchi", tipo="contenitore")
    figlia = await _sezione(admin, "Articoli", tipo="contenitore", parent_id=radice["id"])
    amore = await _sezione(admin, "Amore", parent_id=figlia["id"], ordine=1)
    lavoro = await _sezione(admin, "Lavoro", parent_id=figlia["id"], ordine=2)
    await _articolo(admin, "Uno", sezione_id=amore["id"])
    await _articolo(admin, "Due", sezione_id=amore["id"])
    await _articolo(admin, "Tre", sezione_id=lavoro["id"])
    await _articolo(admin, "Bozza", pubblica=False, sezione_id=lavoro["id"])

    albero = (await admin.get("/blog/sections")).json()
    assert [n["slug"] for n in albero] == ["tarocchi"]
    articoli = albero[0]["figli"][0]
    assert articoli["slug"] == "articoli" and [f["slug"] for f in articoli["figli"]] == ["amore", "lavoro"]
    assert [f["n_articoli"] for f in articoli["figli"]] == [2, 1]        # la bozza non conta

    dettaglio = (await admin.get("/blog/sections/amore")).json()
    assert [b["slug"] for b in dettaglio["briciole"]] == ["tarocchi", "articoli", "amore"]


async def test_una_sezione_di_carte_elenca_da_sola_le_carte_del_catalogo(admin):
    await _sezione(admin, "Arcani maggiori", tipo="carte", filtro={"arcano": "maggiore"})
    await _sezione(admin, "Bastoni", tipo="carte", filtro={"seme": "bastoni"})
    await _sezione(admin, "Stese di coppia", tipo="stese", filtro={"categoria": "coppia"})
    maggiori = (await admin.get("/blog/sections/arcani-maggiori")).json()
    assert maggiori["n_elementi"] == 22 and len(maggiori["elementi"]) == 22
    assert (await admin.get("/blog/sections/bastoni")).json()["n_elementi"] == 14
    coppia = (await admin.get("/blog/sections/stese-di-coppia")).json()
    assert len(coppia["elementi"]) == 5 and all(e["categoria"] == "coppia" for e in coppia["elementi"])


async def test_una_sezione_nascosta_e_le_sue_sotto_sezioni_non_escono(admin):
    padre = await _sezione(admin, "Riservata", visibile=False)
    figlia = await _sezione(admin, "Figlia", parent_id=padre["id"])
    await _articolo(admin, "Segreto", sezione_id=figlia["id"])
    assert (await admin.get("/blog/sections")).json() == []
    assert (await admin.get("/blog/sections/figlia")).status_code == 404
    # La figlia è visibile di per sé, ma sta dentro una nascosta: nemmeno i suoi articoli escono.
    assert (await admin.get("/blog/posts", params={"sezione": "figlia"})).status_code == 404
    assert (await _pubblici(admin))["totale"] == 0
    assert (await admin.get("/blog/posts/segreto")).status_code == 404
    assert (await admin.get("/blog/mappa")).json()["articoli"] == []
    # Nella console si vedono tutte.
    assert len((await admin.get("/admin/blog/sections")).json()) == 2


async def test_gli_slug_delle_sezioni_sono_unici(admin):
    a = await _sezione(admin, "Amore")
    b = await _sezione(admin, "Amore")
    assert a["slug"] == "amore" and b["slug"] == "amore-2"


async def test_una_sezione_non_puo_stare_dentro_una_sua_discendente(admin):
    a = await _sezione(admin, "A")
    b = await _sezione(admin, "B", parent_id=a["id"])
    c = await _sezione(admin, "C", parent_id=b["id"])
    for padre in (a["id"], b["id"], c["id"]):
        r = await admin.patch(f"/admin/blog/sections/{a['id']}", json={"parent_id": padre})
        assert r.status_code == 422, (padre, r.text)
    assert (await admin.patch(f"/admin/blog/sections/{c['id']}", json={"parent_id": a["id"]})).status_code == 200
    assert (await admin.patch(f"/admin/blog/sections/{c['id']}", json={"parent_id": 99999})).status_code == 422


async def test_si_riordinano_e_si_spostano_le_sezioni_in_una_volta(admin):
    a = await _sezione(admin, "A")
    b = await _sezione(admin, "B")
    r = await admin.post("/admin/blog/sections/riordina", json=[
        {"id": a["id"], "parent_id": b["id"], "ordine": 5}, {"id": b["id"], "parent_id": None, "ordine": 1},
    ])
    assert r.status_code == 200 and r.json() == {"aggiornate": 2}
    piatte = {s["slug"]: s for s in (await admin.get("/admin/blog/sections")).json()}
    assert piatte["a"]["parent_id"] == b["id"] and piatte["a"]["ordine"] == 5
    ciclo = await admin.post("/admin/blog/sections/riordina", json=[{"id": b["id"], "parent_id": a["id"], "ordine": 0}])
    assert ciclo.status_code == 422


async def test_una_sezione_non_vuota_si_elimina_solo_con_forza(admin):
    s = await _sezione(admin, "Amore")
    figlia = await _sezione(admin, "Sotto", parent_id=s["id"])
    await _articolo(admin, "Uno", sezione_id=s["id"])
    r = await admin.delete(f"/admin/blog/sections/{s['id']}")
    assert r.status_code == 409 and r.json()["detail"] == {"motivo": "sezione_non_vuota", "articoli": 1, "sotto_sezioni": 1}
    assert (await admin.delete(f"/admin/blog/sections/{s['id']}", params={"forza": True})).status_code == 204
    # L'articolo resta, senza sezione; la figlia sale alla radice.
    assert (await _pubblici(admin))["articoli"][0]["sezione"] is None
    assert next(x for x in (await admin.get("/admin/blog/sections")).json() if x["id"] == figlia["id"])["parent_id"] is None


# ---- gli articoli: ciclo di vita e visibilità -------------------------------------------------------


async def test_una_bozza_non_si_vede_e_si_vede_una_volta_pubblicata(admin):
    a = await _articolo(admin, "Una bozza", pubblica=False)
    assert a["stato"] == "bozza" and a["pubblicato_il"] is None
    assert (await _pubblici(admin))["totale"] == 0
    assert (await admin.get(f"/blog/posts/{a['slug']}")).status_code == 404

    r = await admin.post(f"/admin/blog/posts/{a['id']}/pubblica")
    assert r.status_code == 200 and r.json()["stato"] == "pubblicato" and r.json()["pubblicato_il"]
    assert (await admin.get(f"/blog/posts/{a['slug']}")).status_code == 200
    assert (await _pubblici(admin))["totale"] == 1

    await admin.post(f"/admin/blog/posts/{a['id']}/archivia")
    assert (await admin.get(f"/blog/posts/{a['slug']}")).status_code == 404
    await admin.post(f"/admin/blog/posts/{a['id']}/pubblica")
    assert (await admin.get(f"/blog/posts/{a['slug']}")).status_code == 200
    await admin.post(f"/admin/blog/posts/{a['id']}/bozza")
    assert (await admin.get(f"/blog/posts/{a['slug']}")).status_code == 404


async def test_un_articolo_programmato_compare_solo_dalla_sua_data(admin, session):
    dopo = (utcnow() + timedelta(hours=2)).isoformat()
    a = await _articolo(admin, "Domani", stato="pubblicato", pubblicato_il=dopo)
    assert a["programmato"] is True
    assert (await _pubblici(admin))["totale"] == 0 and (await admin.get(f"/blog/posts/{a['slug']}")).status_code == 404
    assert (await admin.get("/blog/mappa")).json()["articoli"] == []
    # Nella console si vede, e si vede che è programmato.
    assert (await admin.get("/admin/blog/posts")).json()["articoli"][0]["programmato"] is True

    passato = (utcnow() - timedelta(minutes=1)).isoformat()
    await admin.patch(f"/admin/blog/posts/{a['id']}", json={"pubblicato_il": passato})
    assert (await admin.get(f"/blog/posts/{a['slug']}")).status_code == 200


async def test_gli_articoli_stanno_solo_nelle_sezioni_di_articoli(admin):
    carte = await _sezione(admin, "Carte", tipo="carte", filtro={"arcano": "maggiore"})
    r = await admin.post("/admin/blog/posts", json={"titolo": "x", "sezione_id": carte["id"]})
    assert r.status_code == 422 and "articoli" in r.json()["detail"]
    assert (await admin.post("/admin/blog/posts", json={"titolo": "x", "sezione_id": 424242})).status_code == 422
    assert (await admin.post("/admin/blog/posts", json={"titolo": "x", "immagine_id": "0b1c2d3e-0000-4000-8000-000000000000"})).status_code == 422


async def test_gli_slug_degli_articoli_si_generano_e_non_si_ripetono(admin):
    a = await _articolo(admin, "Che cos'è la Papessa?")
    b = await _articolo(admin, "Che cos'è la Papessa?")
    c = await _articolo(admin, "Altro", slug="Che cos'è la Papessa?")
    assert a["slug"] == "che-cos-e-la-papessa" and b["slug"] == "che-cos-e-la-papessa-2" and c["slug"] == "che-cos-e-la-papessa-3"
    r = await admin.patch(f"/admin/blog/posts/{c['id']}", json={"slug": "un-altro-slug"})
    assert r.json()["slug"] == "un-altro-slug"
    assert (await admin.get("/blog/posts/che-cos-e-la-papessa-3")).status_code == 404


async def test_un_articolo_senza_titolo_o_con_campi_troppo_lunghi_si_respinge(admin):
    assert (await admin.post("/admin/blog/posts", json={"titolo": ""})).status_code == 422
    assert (await admin.post("/admin/blog/posts", json={"titolo": "x" * 201})).status_code == 422
    assert (await admin.post("/admin/blog/posts", json={"titolo": "ok", "tags": [str(i) for i in range(11)]})).status_code == 422
    a = await _articolo(admin, "Ok")
    # Un `null` su un campo obbligatorio vuol dire «lascia com'è».
    r = await admin.patch(f"/admin/blog/posts/{a['id']}", json={"titolo": None, "lang": None, "sottotitolo": "Sotto"})
    assert r.status_code == 200 and r.json()["titolo"] == "Ok" and r.json()["lang"] == "it" and r.json()["sottotitolo"] == "Sotto"


async def test_modificare_il_testo_conserva_la_versione_precedente_e_si_puo_ripristinare(admin):
    a = await _articolo(admin, "Versioni", testo="Primo testo.")
    assert (await admin.get(f"/admin/blog/posts/{a['id']}/revisions")).json() == []
    await admin.patch(f"/admin/blog/posts/{a['id']}", json={"testo": "Secondo testo."})
    await admin.patch(f"/admin/blog/posts/{a['id']}", json={"testo": "Secondo testo."})    # uguale: nessuna versione
    await admin.patch(f"/admin/blog/posts/{a['id']}", json={"testo": "Terzo testo.", "titolo": "Nuovo titolo"})
    rev = (await admin.get(f"/admin/blog/posts/{a['id']}/revisions")).json()
    assert [r["testo"] for r in rev] == ["Secondo testo.", "Primo testo."] and rev[0]["titolo"] == "Versioni"
    r = await admin.post(f"/admin/blog/posts/{a['id']}/revisions/{rev[1]['id']}/restore")
    assert r.status_code == 200 and r.json()["testo"] == "Primo testo."
    assert (await admin.post(f"/admin/blog/posts/{a['id']}/revisions/999999/restore")).status_code == 404
    # Le versioni sono al massimo venti.
    for i in range(25):
        await admin.patch(f"/admin/blog/posts/{a['id']}", json={"testo": f"Giro {i}"})
    assert len((await admin.get(f"/admin/blog/posts/{a['id']}/revisions")).json()) == 20


async def test_il_tempo_di_lettura_segue_il_testo(admin):
    a = await _articolo(admin, "Lungo", testo="parola " * 650)
    assert a["tempo_lettura"] == 4
    assert (await admin.patch(f"/admin/blog/posts/{a['id']}", json={"testo": "corto"})).json()["tempo_lettura"] == 1


async def test_eliminare_un_articolo_lo_toglie_dal_pubblico(admin):
    a = await _articolo(admin, "Da togliere")
    assert (await admin.delete(f"/admin/blog/posts/{a['id']}")).status_code == 204
    assert (await admin.get(f"/blog/posts/{a['slug']}")).status_code == 404
    assert (await admin.get(f"/admin/blog/posts/{a['id']}")).status_code == 404


# ---- gli elenchi pubblici ---------------------------------------------------------------------------------


async def test_l_elenco_filtra_per_sezione_con_le_sotto_sezioni_per_etichetta_e_per_testo(admin):
    madre = await _sezione(admin, "Articoli", tipo="contenitore")
    amore = await _sezione(admin, "Amore", parent_id=madre["id"])
    lavoro = await _sezione(admin, "Lavoro", parent_id=madre["id"])
    await _articolo(admin, "Il Sole e l'amore", sezione_id=amore["id"], tags=["Sole", "Amore"], testo="La carta del calore.")
    await _articolo(admin, "La Luna", sezione_id=amore["id"], tags=["Luna"], testo="Le ombre della notte.")
    await _articolo(admin, "Il Carro al lavoro", sezione_id=lavoro["id"], tags=["Sole"], testo="Determinazione.")
    await _articolo(admin, "Senza sezione")

    assert (await _pubblici(admin))["totale"] == 4
    assert {a["titolo"] for a in (await _pubblici(admin, sezione="amore"))["articoli"]} == {"Il Sole e l'amore", "La Luna"}
    assert (await _pubblici(admin, sezione="articoli"))["totale"] == 3          # include le sotto-sezioni
    assert {a["titolo"] for a in (await _pubblici(admin, tag="sole"))["articoli"]} == {"Il Sole e l'amore", "Il Carro al lavoro"}
    assert {a["titolo"] for a in (await _pubblici(admin, q="ombre"))["articoli"]} == {"La Luna"}
    assert {a["titolo"] for a in (await _pubblici(admin, q="il carro"))["articoli"]} == {"Il Carro al lavoro"}
    assert (await _pubblici(admin, q="100%_"))["totale"] == 0                   # i caratteri jolly non sono jolly
    assert (await admin.get("/blog/posts", params={"sezione": "non-esiste"})).status_code == 404
    assert (await admin.get("/blog/posts", params={"sezione": "Maiuscole!"})).status_code == 422


async def test_l_elenco_si_impagina_dal_piu_recente(admin):
    for i in range(5):
        await _articolo(admin, f"Articolo {i}", pubblicato_il=(utcnow() - timedelta(days=5 - i)).isoformat())
    p1 = await _pubblici(admin, per_pagina=2, pagina=1)
    p3 = await _pubblici(admin, per_pagina=2, pagina=3)
    assert p1["totale"] == 5 and p1["pagine"] == 3 and [a["titolo"] for a in p1["articoli"]] == ["Articolo 4", "Articolo 3"]
    assert [a["titolo"] for a in p3["articoli"]] == ["Articolo 0"]
    assert (await admin.get("/blog/posts", params={"per_pagina": 51})).status_code == 422


async def test_l_elenco_filtra_per_lingua_e_per_evidenza(admin):
    await _articolo(admin, "Italiano")
    await _articolo(admin, "English", lang="en", in_evidenza=True)
    assert [a["titolo"] for a in (await _pubblici(admin, lang="en"))["articoli"]] == ["English"]
    assert [a["titolo"] for a in (await _pubblici(admin, evidenza=True))["articoli"]] == ["English"]


async def test_le_etichette_hanno_i_conteggi_e_si_gestiscono_dalla_console(admin):
    await _articolo(admin, "Uno", tags=["Amore", "Sole"])
    await _articolo(admin, "Due", tags=["amore"])
    await _articolo(admin, "Bozza", pubblica=False, tags=["Segreta"])
    pubbliche = (await admin.get("/blog/tags")).json()
    assert pubbliche[0] == {"slug": "amore", "nome": "Amore", "n": 2} and {t["slug"] for t in pubbliche} == {"amore", "sole"}
    tutte = {t["slug"]: t for t in (await admin.get("/admin/blog/tags")).json()}
    assert tutte["segreta"]["n"] == 1
    r = await admin.patch(f"/admin/blog/tags/{tutte['sole']['id']}", json={"nome": "Il Sole"})
    assert r.json()["slug"] == "il-sole"
    assert (await admin.patch(f"/admin/blog/tags/{tutte['sole']['id']}", json={"nome": "Amore"})).status_code == 409
    assert (await admin.delete(f"/admin/blog/tags/{tutte['segreta']['id']}")).status_code == 204
    assert "segreta" not in {t["slug"] for t in (await admin.get("/admin/blog/tags")).json()}


# ---- la pagina di un articolo: collegamenti interni --------------------------------------------------------


async def test_l_articolo_porta_briciole_collegamenti_correlati_e_vicini(admin):
    madre = await _sezione(admin, "Articoli", tipo="contenitore")
    amore = await _sezione(admin, "Amore", parent_id=madre["id"])
    testo = "Parliamo di [[carta:maj-17]], della [[stesa:croce-celtica]] e di [questo](/blog/altro-articolo)."
    primo = await _articolo(admin, "Primo", sezione_id=amore["id"], testo=testo, tags=["stelle"],
                            pubblicato_il=(utcnow() - timedelta(days=3)).isoformat())
    await _articolo(admin, "Altro articolo", sezione_id=amore["id"], testo="[[carta:maj-17]] ancora.", tags=["stelle"],
                    pubblicato_il=(utcnow() - timedelta(days=2)).isoformat())
    await _articolo(admin, "Ultimo", sezione_id=amore["id"], pubblicato_il=(utcnow() - timedelta(days=1)).isoformat())

    p = (await admin.get(f"/blog/posts/{primo['slug']}")).json()
    assert [b["slug"] for b in p["briciole"]] == ["articoli", "amore"]
    # L'articolo è in italiano (`lang` predefinito del modello): nome e slug nella sua lingua, e gli slug in ogni lingua.
    assert p["collegamenti"]["carte"] == [{
        "id": "maj-17", "nome_it": "La Stella", "nome": "La Stella", "slug": "la-stella",
        "slugs": {"it": "la-stella", "en": "the-star"},
    }]
    assert p["collegamenti"]["stese"] == [{
        "id": "croce-celtica", "nome": "Croce Celtica", "slug": "croce-celtica",
        "slugs": {"it": "croce-celtica", "en": "celtic-cross"},
    }]
    assert [a["slug"] for a in p["collegamenti"]["articoli"]] == ["altro-articolo"]
    assert p["correlati"][0]["slug"] == "altro-articolo"            # stessa etichetta, sezione e carta
    assert p["precedente"] is None and p["successivo"]["slug"] == "altro-articolo"
    assert p["testo"] == testo and p["seo_descrizione"] and p["tempo_lettura"] == 1

    # Dalla carta e dalla stesa si risale agli articoli che le citano.
    assert [a["slug"] for a in (await admin.get("/blog/links/carta/maj-17")).json()] == ["altro-articolo", "primo"]
    assert [a["slug"] for a in (await admin.get("/blog/links/stesa/croce-celtica")).json()] == ["primo"]
    assert (await admin.get("/blog/links/carta/maj-00")).json() == []
    assert (await admin.get("/blog/links/altro/x")).status_code == 404


async def test_i_collegamenti_a_carte_inesistenti_non_rompono_la_pagina(admin):
    a = await _articolo(admin, "Strano", testo="[[carta:non-esiste]] [[stesa:nemmeno]] [[articolo:fantasma]]")
    p = (await admin.get(f"/blog/posts/{a['slug']}")).json()
    assert p["collegamenti"] == {"carte": [], "stese": [], "articoli": []}


async def test_un_link_a_una_bozza_non_la_rivela(admin):
    bozza = await _articolo(admin, "Bozza segreta", pubblica=False)
    a = await _articolo(admin, "Pubblico", testo=f"[[articolo:{bozza['slug']}]]")
    p = (await admin.get(f"/blog/posts/{a['slug']}")).json()
    assert p["collegamenti"]["articoli"] == []
    assert (await admin.get("/blog/links/articolo/x")).status_code == 404


async def test_la_mappa_elenca_solo_cio_che_e_pubblico(admin):
    await _articolo(admin, "Pubblico", tags=["uno"])
    await _articolo(admin, "Bozza", pubblica=False, tags=["due"])
    await _sezione(admin, "Visibile")
    await _sezione(admin, "Nascosta", visibile=False)
    m = (await admin.get("/blog/mappa")).json()
    assert [a["slug"] for a in m["articoli"]] == ["pubblico"] and m["sezioni"] == ["visibile"] and m["tags"] == ["uno"]


async def test_la_mappa_dice_in_quali_lingue_una_sezione_o_un_etichetta_ha_articoli(admin):
    amore = await _sezione(admin, "Amore")
    figlia = await _sezione(admin, "Coppie", parent_id=amore["id"])
    await _sezione(admin, "Vuota")
    await _sezione(admin, "Maggiori", tipo="carte", filtro={"arcano": "maggiore"})
    await _articolo(admin, "Love", lang="en", sezione_id=figlia["id"], tags=["love"])
    await _articolo(admin, "Amore in coppia", lang="it", sezione_id=amore["id"], tags=["amore"])
    await _articolo(admin, "Nascosto", lang="it", noindex=True, sezione_id=figlia["id"], tags=["amore", "nascosto"])
    m = (await admin.get("/blog/mappa")).json()
    lingue = m["sezioni_lingue"]
    assert lingue["amore"] == ["en", "it"]                 # l'inglese sta in una sotto-sezione
    assert lingue["coppie"] == ["en"]                      # l'articolo italiano nascosto non conta
    assert lingue["vuota"] == []                           # nessuna pagina da indicare
    assert lingue["maggiori"] == ["en", "it"]              # un catalogo esiste in ogni lingua
    assert m["tags_lingue"] == {"love": ["en"], "amore": ["it"]}


async def test_una_sezione_di_catalogo_parla_la_lingua_richiesta(admin):
    await _sezione(admin, "Maggiori", tipo="carte", filtro={"arcano": "maggiore"})
    await _sezione(admin, "Stese", tipo="stese", filtro={"categoria": "coppia"})
    inglese = (await admin.get("/blog/sections/maggiori", params={"lang": "en"})).json()["elementi"]
    italiano = (await admin.get("/blog/sections/maggiori", params={"lang": "it"})).json()["elementi"]
    stella_en = next(c for c in inglese if c["id"] == "maj-17")
    stella_it = next(c for c in italiano if c["id"] == "maj-17")
    assert stella_en["slug"] == "the-star" and stella_it["slug"] == "la-stella"
    assert stella_en["nome"] != stella_it["nome"]
    stese = (await admin.get("/blog/sections/stese", params={"lang": "en"})).json()["elementi"]
    assert {s["slug"] for s in stese} >= {"mirror-spread", "crossroads-spread"} and all(s["slugs"]["it"] for s in stese)


# ---- le immagini ----------------------------------------------------------------------------------------------


async def test_un_immagine_si_carica_si_riscrive_e_si_serve_con_cache_immutabile(admin):
    r = await admin.post("/admin/blog/media", content=_png(3200, 1800), headers={"content-type": "image/png"})
    assert r.status_code == 201, r.text
    img = r.json()
    assert (img["larghezza"], img["altezza"]) == (1600, 900) and img["url"] == f"/blog/media/{img['id']}.webp"
    servita = await admin.get(img["url"])
    assert servita.status_code == 200 and servita.headers["content-type"] == "image/webp"
    assert "immutable" in servita.headers["cache-control"] and servita.headers["x-content-type-options"] == "nosniff"
    assert servita.content[:4] == b"RIFF" and len(servita.content) == img["byte"]
    assert [i["id"] for i in (await admin.get("/admin/blog/media")).json()] == [img["id"]]


async def test_le_immagini_sbagliate_non_si_caricano(admin):
    assert (await admin.post("/admin/blog/media", content=b"<html>", headers={"content-type": "text/html"})).status_code == 415
    assert (await admin.post("/admin/blog/media", content=b"non un'immagine", headers={"content-type": "image/png"})).status_code == 422
    assert (await admin.post("/admin/blog/media", content=b"x" * 8_000_001, headers={"content-type": "image/png"})).status_code == 413
    for nome in ("non-un-uuid.webp", "0b1c2d3e-0000-4000-8000-000000000000.webp", "0b1c2d3e-0000-4000-8000-000000000000.png"):
        assert (await admin.get(f"/blog/media/{nome}")).status_code == 404


async def test_un_articolo_mostra_la_sua_immagine_e_l_immagine_in_uso_non_si_cancella(admin):
    img = (await admin.post("/admin/blog/media", content=_png(), headers={"content-type": "image/png"})).json()
    a = await _articolo(admin, "Con foto", immagine_id=img["id"], immagine_alt="La foto")
    p = (await admin.get(f"/blog/posts/{a['slug']}")).json()
    assert p["immagine"] == {"url": img["url"], "alt": "La foto", "larghezza": 800, "altezza": 450}
    assert (await admin.get("/blog/posts")).json()["articoli"][0]["immagine"]["url"] == img["url"]
    r = await admin.delete(f"/admin/blog/media/{img['id']}")
    assert r.status_code == 409 and r.json()["detail"]["motivo"] == "immagine_in_uso"
    await admin.patch(f"/admin/blog/posts/{a['id']}", json={"immagine_id": None})
    assert (await admin.delete(f"/admin/blog/media/{img['id']}")).status_code == 204
    assert (await admin.get(img["url"])).status_code == 404


# ---- l'autore, il nome pubblico e l'avatar ----------------------------------------------------------------


async def test_l_avatar_si_carica_si_ritaglia_e_si_sostituisce(client):
    r = await client.put("/me/avatar", content=_png(900, 300), headers={"content-type": "image/png"})
    assert r.status_code == 200, r.text
    url = r.json()["avatar"]
    assert (await client.get("/me/profile")).json()["avatar"] == url
    img = await client.get(url)
    assert img.status_code == 200 and img.headers["content-type"] == "image/webp"
    from PIL import Image

    assert Image.open(io.BytesIO(img.content)).size == (256, 256)

    seconda = (await client.put("/me/avatar", content=_png(500, 500, (1, 2, 3)), headers={"content-type": "image/png"})).json()["avatar"]
    assert seconda != url and (await client.get(url)).status_code == 404          # la vecchia si cancella
    assert (await client.delete("/me/avatar")).status_code == 204
    assert (await client.get("/me/profile")).json()["avatar"] is None and (await client.get(seconda)).status_code == 404
    assert (await client.delete("/me/avatar")).status_code == 204                   # idempotente


async def test_un_avatar_sbagliato_si_respinge(client):
    assert (await client.put("/me/avatar", content=b"<html>", headers={"content-type": "text/html"})).status_code == 415
    assert (await client.put("/me/avatar", content=b"non un'immagine", headers={"content-type": "image/png"})).status_code == 422
    assert (await client.put("/me/avatar", content=_png(32, 32), headers={"content-type": "image/png"})).status_code == 422
    assert (await client.get("/me/profile")).json()["avatar"] is None


async def test_il_nome_pubblico_si_sceglie_si_pulisce_e_non_e_mai_l_email(client):
    p = (await client.get("/me/profile")).json()
    assert p["nome_pubblico"] is None and p["nome_mostrato"] == "Utente"          # «Utente Di Prova»: il primo nome
    r = await client.patch("/me/profile", json={"nome_pubblico": "  Luna <b>Blu</b> \n\"x\" "})
    assert r.json()["nome_pubblico"] == "Luna bBlub x"        # niente simboli: restano lettere, cifre e spazi
    assert "<" not in r.json()["nome_mostrato"] and "@" not in r.json()["nome_mostrato"]
    assert (await client.patch("/me/profile", json={"nome_pubblico": "   "})).json()["nome_pubblico"] is None
    assert (await client.patch("/me/profile", json={"nome_pubblico": "x" * 61})).status_code == 422


async def test_l_autore_di_un_articolo_mostra_nome_e_avatar_mai_l_email(admin):
    await admin.patch("/me/profile", json={"nome_pubblico": "La Redazione"})
    avatar = (await admin.put("/me/avatar", content=_png(), headers={"content-type": "image/png"})).json()["avatar"]
    a = await _articolo(admin, "Firmato")
    p = (await admin.get(f"/blog/posts/{a['slug']}")).json()
    assert p["autore"]["nome"] == "La Redazione" and p["autore"]["avatar"] == avatar
    assert "admin@example.com" not in repr(p) and "Amministratore" not in repr(p)


# ---- l'albero iniziale ----------------------------------------------------------------------------------------


async def test_il_seed_scrive_l_albero_una_volta_e_non_disfa_le_modifiche(admin, session):
    from tarot_core.tools.seed import scrivi_sezioni_blog

    creati = await scrivi_sezioni_blog(session)
    await session.commit()
    assert creati == 17 and await scrivi_sezioni_blog(session) == 0
    albero = (await admin.get("/blog/sections")).json()
    assert [n["slug"] for n in albero] == ["tarot"]
    figli = {f["slug"]: f for f in albero[0]["figli"]}
    assert list(figli) == ["major-arcana", "minor-arcana", "learn-tarot", "tarot-journal", "articles"]
    assert figli["major-arcana"]["n_elementi"] == 22 and figli["major-arcana"]["tipo"] == "carte"
    assert [f["slug"] for f in figli["minor-arcana"]["figli"]] == ["wands", "cups", "swords", "disks"]
    assert [f["slug"] for f in figli["learn-tarot"]["figli"]] == ["tarot-spreads"]
    assert figli["learn-tarot"]["figli"][0]["n_elementi"] == 14
    assert [f["slug"] for f in figli["articles"]["figli"]] == [
        "love", "relationships", "career", "spirituality", "symbolism", "thoth-tarot",
    ]
    # Il seme si sceglie per il suo nome interno («bastoni»); la sezione si chiama come nel mazzo di Thoth.
    assert (await admin.get("/blog/sections/wands")).json()["n_elementi"] == 14
    # La console può rinominare e nascondere: un nuovo seed non lo disfa.
    amore = next(s for s in (await admin.get("/admin/blog/sections")).json() if s["slug"] == "love")
    await admin.patch(f"/admin/blog/sections/{amore['id']}", json={"nome": "Heart", "visibile": False})
    assert await scrivi_sezioni_blog(session) == 0
    await session.commit()
    dopo = {f["slug"]: f for f in (await admin.get("/blog/sections")).json()[0]["figli"]}
    assert "love" not in [f["slug"] for f in dopo["articles"]["figli"]]
    piatte = {s["slug"]: s for s in (await admin.get("/admin/blog/sections")).json()}
    assert piatte["love"]["nome"] == "Heart" and piatte["love"]["visibile"] is False
