"""La pubblicazione sul blog via REST con chiave applicativa, attraverso l'API e un database vero."""
from __future__ import annotations

import base64
import io

import pytest

from tarot_core.auth import chiavi

from .conftest import richiede_database

pytestmark = richiede_database


def _png(larghezza=800, altezza=450, colore=(30, 80, 160)) -> bytes:
    from PIL import Image

    uscita = io.BytesIO()
    Image.new("RGB", (larghezza, altezza), colore).save(uscita, format="PNG")
    return uscita.getvalue()


@pytest.fixture(autouse=True)
def _senza_limiti():
    chiavi.azzera_limiti()
    yield
    chiavi.azzera_limiti()


@pytest.fixture
def admin(client, principal_admin):
    client.identita.principal = principal_admin
    return client


async def _chiave(admin, scopes=("blog:write",), **campi):
    r = await admin.post("/admin/blog/api-keys", json={"nome": "Agente di prova", "scopes": list(scopes), **campi})
    assert r.status_code == 201, r.text
    dati = r.json()
    assert dati["chiave"].startswith("tk_live_")
    return dati["chiave"], dati


def _h(chiave):
    return {"Authorization": f"Bearer {chiave}"}


ARTICOLO = {
    "titolo": "The Star Tarot Card Meaning",
    "sottotitolo": "Hope after the Tower",
    "testo": "The Star speaks of hope. See [[card:the-star]] and [[spread:celtic-cross]].\n\n## In love\n\nOpenness.",
    "seo_parola_chiave": "star tarot card meaning",
    "seo_parole_chiave": ["the star", "thoth tarot"],
    "seo_descrizione": "The Star tarot card meaning in the Thoth Tarot.",
    "faq": [{"domanda": "What does the Star mean?", "risposta": "Hope."}],
    "tags": ["Thoth Tarot", "Hope"],
}


# ---- l'accesso ------------------------------------------------------------------------------------------------


async def test_senza_chiave_o_con_una_chiave_sbagliata_si_riceve_401(client):
    assert (await client.get("/v1/blog/guide")).status_code == 401
    assert (await client.get("/v1/blog/guide", headers=_h("tk_live_" + "x" * 43))).status_code == 401
    assert (await client.get("/v1/blog/guide", headers=_h("abc"))).status_code == 401


async def test_la_chiave_funziona_anche_come_x_api_key_e_la_guida_dice_i_permessi(admin):
    chiave, _ = await _chiave(admin)
    r = await admin.get("/v1/blog/guide", headers={"X-API-Key": chiave})
    assert r.status_code == 200
    g = r.json()
    assert g["lingua_predefinita"] == "en" and g["chiave"]["scopes"] == ["blog:write"] and g["soglie_seo"]["titolo_max"] == 60


async def test_una_chiave_revocata_smette_di_funzionare(admin):
    chiave, dati = await _chiave(admin)
    assert (await admin.get("/v1/blog/guide", headers=_h(chiave))).status_code == 200
    assert (await admin.delete(f"/admin/blog/api-keys/{dati['id']}")).status_code == 204
    assert (await admin.get("/v1/blog/guide", headers=_h(chiave))).status_code == 401
    elenco = (await admin.get("/admin/blog/api-keys")).json()
    riga = next(k for k in elenco if k["id"] == dati["id"])
    assert riga["attiva"] is False and riga["revocata"] and "chiave" not in riga and "impronta" not in riga


async def test_la_chiave_si_mostra_una_volta_sola(admin):
    chiave, dati = await _chiave(admin)
    elenco = (await admin.get("/admin/blog/api-keys")).json()
    assert chiave not in str(elenco) and dati["prefisso"] == chiave[:12]


async def test_solo_l_amministratore_gestisce_le_chiavi(client):
    assert (await client.get("/admin/blog/api-keys")).status_code == 403
    assert (await client.post("/admin/blog/api-keys", json={"nome": "x"})).status_code == 403


async def test_il_freno_al_minuto_risponde_429_con_retry_after(admin):
    chiave, _ = await _chiave(admin, limite_minuto=2)
    assert (await admin.get("/v1/blog/guide", headers=_h(chiave))).status_code == 200
    assert (await admin.get("/v1/blog/guide", headers=_h(chiave))).status_code == 200
    r = await admin.get("/v1/blog/guide", headers=_h(chiave))
    assert r.status_code == 429 and int(r.headers["retry-after"]) >= 1


# ---- creare ---------------------------------------------------------------------------------------------------


async def test_una_chiave_di_sola_scrittura_crea_solo_bozze_e_lo_dice(admin):
    chiave, _ = await _chiave(admin)
    r = await admin.post("/v1/blog/posts", json={**ARTICOLO, "stato": "pubblicato", "in_evidenza": True}, headers=_h(chiave))
    assert r.status_code == 201, r.text
    j = r.json()
    assert j["articolo"]["stato"] == "bozza" and j["articolo"]["in_evidenza"] is False
    assert len(j["avvisi"]) == 2 and "blog:publish" in j["avvisi"][0]
    assert (await admin.get("/blog/posts")).json()["totale"] == 0           # il pubblico non lo vede


async def test_con_il_permesso_di_pubblicare_l_articolo_esce_con_tutti_i_campi_seo(admin):
    chiave, _ = await _chiave(admin, ("blog:write", "blog:publish"))
    r = await admin.post("/v1/blog/posts", json={**ARTICOLO, "stato": "pubblicato", "immagine_alt": "The Star card"}, headers=_h(chiave))
    assert r.status_code == 201, r.text
    j = r.json()
    assert j["avvisi"] == [] and j["articolo"]["stato"] == "pubblicato"
    assert j["url"].endswith("/blog/the-star-tarot-card-meaning") and "/it/" not in j["url"]
    assert 0 <= j["seo"]["punteggio"] <= 100 and j["seo"]["controlli"]

    pubblico = (await admin.get("/blog/posts/the-star-tarot-card-meaning")).json()
    assert pubblico["seo_parola_chiave"] == "star tarot card meaning" and pubblico["parole_chiave"] == ["the star", "thoth tarot"]
    assert pubblico["faq"] == [{"domanda": "What does the Star mean?", "risposta": "Hope."}]
    assert pubblico["noindex"] is False and pubblico["canonical_url"] is None and pubblico["lang"] == "en"
    assert pubblico["autore"]["nome"] == "Redazione"


async def test_le_scorciatoie_in_inglese_e_per_slug_si_risolvono_negli_id_canonici(admin):
    chiave, _ = await _chiave(admin, ("blog:write", "blog:publish"))
    await admin.post("/v1/blog/posts", json={**ARTICOLO, "stato": "pubblicato"}, headers=_h(chiave))
    pubblico = (await admin.get("/blog/posts/the-star-tarot-card-meaning")).json()
    carte, stese = pubblico["collegamenti"]["carte"], pubblico["collegamenti"]["stese"]
    assert [c["id"] for c in carte] == ["maj-17"] and carte[0]["nome"] == "The Star" and carte[0]["slug"] == "the-star"
    assert carte[0]["slugs"] == {"it": "la-stella", "en": "the-star"}
    assert [s["id"] for s in stese] == ["croce-celtica"] and stese[0]["slug"] == "celtic-cross"
    # La pagina della carta sa che quest'articolo la nomina (per id, come sempre).
    citato = (await admin.get("/blog/links/carta/maj-17")).json()
    assert [a["slug"] for a in citato] == ["the-star-tarot-card-meaning"]


async def test_l_estratto_usa_il_nome_della_carta_anche_se_citata_per_slug(admin):
    chiave, _ = await _chiave(admin, ("blog:write", "blog:publish"))
    await admin.post("/v1/blog/posts", json={"titolo": "Un articolo", "testo": "Vedi [[card:the-star]] e [[card:la-stella]].", "stato": "pubblicato"}, headers=_h(chiave))
    e = (await admin.get("/blog/posts")).json()["articoli"][0]["estratto"]
    assert e == "Vedi La Stella e La Stella."


async def test_noindex_toglie_l_articolo_dalla_mappa_ma_non_dall_elenco(admin):
    chiave, _ = await _chiave(admin, ("blog:write", "blog:publish"))
    await admin.post("/v1/blog/posts", json={"titolo": "Visibile", "testo": "x", "stato": "pubblicato"}, headers=_h(chiave))
    await admin.post("/v1/blog/posts", json={"titolo": "Nascosto ai motori", "testo": "y", "stato": "pubblicato", "noindex": True}, headers=_h(chiave))
    assert (await admin.get("/blog/posts")).json()["totale"] == 2
    mappa = (await admin.get("/blog/mappa")).json()["articoli"]
    assert [a["slug"] for a in mappa] == ["visibile"] and mappa[0]["lang"] == "en"
    assert (await admin.get("/blog/posts/nascosto-ai-motori")).json()["noindex"] is True


async def test_la_prova_non_salva_niente_e_da_il_rapporto(admin):
    chiave, _ = await _chiave(admin)
    r = await admin.post("/v1/blog/posts", json={**ARTICOLO, "dry_run": True}, headers=_h(chiave))
    assert r.status_code == 201 and r.json()["dry_run"] is True and r.json()["seo"]["punteggio"] >= 0
    assert (await admin.get("/v1/blog/posts", headers=_h(chiave))).json()["totale"] == 0
    r2 = await admin.post("/v1/blog/seo-check", json=ARTICOLO, headers=_h(chiave))
    assert r2.status_code == 200 and r2.json()["punteggio"] == r.json()["seo"]["punteggio"]


async def test_una_sezione_sbagliata_dice_quali_sono_valide(admin):
    chiave, _ = await _chiave(admin)
    valida = (await admin.post("/admin/blog/sections", json={"nome": "Love", "tipo": "articoli"})).json()
    await admin.post("/admin/blog/sections", json={"nome": "Cards", "tipo": "carte"})
    await admin.post("/admin/blog/sections", json={"nome": "Group", "tipo": "contenitore"})
    r = await admin.post("/v1/blog/posts", json={**ARTICOLO, "sezione": "group"}, headers=_h(chiave))
    # v9.4: anche le sezioni di carte e di stese accettano articoli; i contenitori no.
    assert r.status_code == 422 and r.json()["detail"]["sezioni_valide"] == ["cards", "love"]
    ok = await admin.post("/v1/blog/posts", json={**ARTICOLO, "sezione": "love"}, headers=_h(chiave))
    assert ok.status_code == 201 and ok.json()["articolo"]["sezione_id"] == valida["id"]
    sezioni = (await admin.get("/v1/blog/sections", headers=_h(chiave))).json()
    assert sorted((s["slug"], s["tipo"]) for s in sezioni) == [("cards", "carte"), ("love", "articoli")]


async def test_l_immagine_si_carica_come_corpo_o_in_base64_ma_mai_da_un_indirizzo(admin):
    chiave, _ = await _chiave(admin)
    r = await admin.post("/v1/blog/media", content=_png(), headers={**_h(chiave), "content-type": "image/png"})
    assert r.status_code == 201 and r.json()["url"].endswith(".webp") and r.json()["larghezza"] == 800
    a = await admin.post("/v1/blog/posts", json={**ARTICOLO, "immagine_id": r.json()["id"], "immagine_alt": "The Star"}, headers=_h(chiave))
    assert a.status_code == 201 and a.json()["articolo"]["immagine_id"] == r.json()["id"]
    b64 = "data:image/png;base64," + base64.b64encode(_png(1000, 500)).decode()
    b = await admin.post("/v1/blog/posts", json={**ARTICOLO, "titolo": "Con base64", "immagine_base64": b64}, headers=_h(chiave))
    assert b.status_code == 201 and b.json()["articolo"]["immagine"]
    assert (await admin.post("/v1/blog/posts", json={**ARTICOLO, "titolo": "Rotta", "immagine_base64": "non base64!"}, headers=_h(chiave))).status_code == 422
    assert (await admin.post("/v1/blog/posts", json={**ARTICOLO, "titolo": "Falsa", "immagine_base64": base64.b64encode(b"non un'immagine").decode()}, headers=_h(chiave))).status_code == 422
    # Nessun campo accetta un indirizzo da scaricare.
    assert "immagine_url" not in ArticoloRestCampi()


def ArticoloRestCampi():
    from tarot_core.api.routers.rest_blog import ArticoloRest

    return ArticoloRest.model_fields


@pytest.mark.parametrize("campo, valore", [
    ("canonical_url", "http://esempio.it/a"),
    ("canonical_url", "javascript:alert(1)"),
    ("faq", [{"domanda": f"D{i}?", "risposta": "R."} for i in range(11)]),
    ("seo_parole_chiave", [f"k{i}" for i in range(11)]),
    ("lang", "english"),
])
async def test_i_campi_seo_sbagliati_si_rifiutano(admin, campo, valore):
    chiave, _ = await _chiave(admin)
    r = await admin.post("/v1/blog/posts", json={**ARTICOLO, campo: valore}, headers=_h(chiave))
    assert r.status_code == 422, r.text


async def test_un_tetto_di_articoli_al_giorno(admin):
    chiave, _ = await _chiave(admin, limite_giorno=1)
    assert (await admin.post("/v1/blog/posts", json={**ARTICOLO, "titolo": "Primo"}, headers=_h(chiave))).status_code == 201
    r = await admin.post("/v1/blog/posts", json={**ARTICOLO, "titolo": "Secondo"}, headers=_h(chiave))
    assert r.status_code == 429 and "Limite giornaliero" in r.json()["detail"]


# ---- modificare e cancellare: qualunque articolo (v9.4) -------------------------------------------------------------


async def test_una_chiave_legge_e_modifica_anche_gli_articoli_di_altri_e_il_registro_ha_prima_e_dopo(admin):
    a, _ = await _chiave(admin, ("blog:write", "blog:publish"))
    b, _ = await _chiave(admin, ("blog:write",))
    creato = (await admin.post("/v1/blog/posts", json={**ARTICOLO, "titolo": "Di A"}, headers=_h(a))).json()["articolo"]
    # Anche uno scritto dalla console.
    console = (await admin.post("/admin/blog/posts", json={"titolo": "Dalla console", "testo": "x", "lang": "en"})).json()

    letto = await admin.get(f"/v1/blog/posts/{creato['id']}", headers=_h(b))
    assert letto.status_code == 200 and letto.json()["articolo"]["titolo"] == "Di A" and letto.json()["seo"]["controlli"]
    r = await admin.patch(f"/v1/blog/posts/{creato['id']}", json={"titolo": "Di A, rivisto da B", "testo": "Nuovo."}, headers=_h(b))
    assert r.status_code == 200 and r.json()["articolo"]["titolo"] == "Di A, rivisto da B"
    assert (await admin.patch(f"/v1/blog/posts/{console['id']}", json={"sottotitolo": "Da B"}, headers=_h(b))).status_code == 200

    voci = (await admin.get("/admin/audit?azione=blog.rest.update&limite=20")).json()
    di_b = next(v for v in voci if v["target"] == creato["id"])
    assert di_b["dopo"]["autrice"] is False and di_b["dopo"]["campi"]["titolo"] == "Di A, rivisto da B"
    assert di_b["prima"]["titolo"] == "Di A" and set(di_b["prima"]) == set(di_b["dopo"]["campi"]) == {"titolo", "testo"}
    # La chiave autrice non porta il prima e il dopo: è il suo articolo.
    await admin.patch(f"/v1/blog/posts/{creato['id']}", json={"sottotitolo": "Di nuovo A"}, headers=_h(a))
    voci = (await admin.get("/admin/audit?azione=blog.rest.update&limite=20")).json()
    di_a = next(v for v in voci if v["target"] == creato["id"] and v["dopo"]["autrice"])
    assert di_a["prima"] is None and "campi" not in di_a["dopo"]

    # L'elenco: tutti gli articoli, con `mio`; `mine=true` solo quelli della chiave.
    tutti = (await admin.get("/v1/blog/posts", headers=_h(b))).json()
    assert tutti["totale"] == 2 and {x["titolo"]: x["mio"] for x in tutti["articoli"]} == {
        "Di A, rivisto da B": False, "Dalla console": False,
    }
    assert (await admin.get("/v1/blog/posts", params={"mine": "true"}, headers=_h(b))).json()["totale"] == 0
    miei = (await admin.get("/v1/blog/posts", params={"mine": "true"}, headers=_h(a))).json()
    assert [x["titolo"] for x in miei["articoli"]] == ["Di A, rivisto da B"] and miei["articoli"][0]["mio"] is True


async def test_le_bozze_si_cancellano_con_blog_write_i_pubblicati_solo_con_blog_publish(admin):
    scrittore, _ = await _chiave(admin)
    editor, _ = await _chiave(admin, ("blog:write", "blog:publish"))
    # Una bozza di un'altra chiave: la cancella anche lo scrittore, e il registro la conserva.
    bozza = (await admin.post("/v1/blog/posts", json={**ARTICOLO, "titolo": "Bozza"}, headers=_h(editor))).json()["articolo"]
    assert (await admin.delete(f"/v1/blog/posts/{bozza['id']}", headers=_h(scrittore))).status_code == 204
    voce = next(v for v in (await admin.get("/admin/audit?azione=blog.rest.delete&limite=5")).json() if v["target"] == bozza["id"])
    assert voce["prima"]["autrice"] is False and voce["prima"]["articolo"]["titolo"] == "Bozza"

    pubblicato = (await admin.post("/v1/blog/posts", json={**ARTICOLO, "titolo": "Uscito", "stato": "pubblicato"}, headers=_h(editor))).json()["articolo"]
    # Lo scrittore non lo modifica né lo cancella; l'editor sì.
    assert (await admin.patch(f"/v1/blog/posts/{pubblicato['id']}", json={"testo": "Cambio"}, headers=_h(scrittore))).status_code == 403
    assert (await admin.delete(f"/v1/blog/posts/{pubblicato['id']}", headers=_h(scrittore))).status_code == 403
    assert (await admin.get(f"/blog/posts/{pubblicato['slug']}")).status_code == 200
    assert (await admin.delete(f"/v1/blog/posts/{pubblicato['id']}", headers=_h(editor))).status_code == 204
    assert (await admin.get(f"/blog/posts/{pubblicato['slug']}")).status_code == 404
    # Un articolo della console pubblicato: l'editor lo modifica.
    console = (await admin.post("/admin/blog/posts", json={"titolo": "Console", "testo": "x", "stato": "pubblicato"})).json()
    r = await admin.patch(f"/v1/blog/posts/{console['id']}", json={"testo": "Rivisto."}, headers=_h(editor))
    assert r.status_code == 200 and r.json()["articolo"]["stato"] == "pubblicato"
    assert (await admin.get(f"/v1/blog/posts/{'0b1c2d3e-0000-4000-8000-000000000000'}", headers=_h(editor))).status_code == 404


# ---- il soggetto (v9.4) ------------------------------------------------------------------------------------------


async def test_il_soggetto_si_ricava_da_solo_si_indica_e_si_toglie(admin):
    chiave, _ = await _chiave(admin, ("blog:write", "blog:publish"))
    ruota = (await admin.post("/v1/blog/posts", json={"titolo": "Wheel of Fortune Tarot Meaning", "testo": "x"}, headers=_h(chiave))).json()
    assert ruota["articolo"]["subject"] == {"tipo": "carta", "ref": "maj-10", "nome": "Fortune", "slug": "fortune"}
    # Indicato a mano, anche per slug e col tipo in inglese.
    r = await admin.post("/v1/blog/posts", json={"titolo": "A reading for the new year", "testo": "x",
                                                  "subject": {"tipo": "spread", "ref": "celtic-cross"}}, headers=_h(chiave))
    assert r.json()["articolo"]["subject"]["ref"] == "croce-celtica" and r.json()["articolo"]["subject"]["tipo"] == "stesa"
    # `null`: nessuno, anche se il titolo nomina una carta; e un riferimento sconosciuto è un 422.
    r = await admin.post("/v1/blog/posts", json={"titolo": "The Tower and the Star", "testo": "x", "subject": None}, headers=_h(chiave))
    assert r.json()["articolo"]["subject"] is None
    assert (await admin.post("/v1/blog/posts", json={"titolo": "x", "subject": {"tipo": "carta", "ref": "maj-99"}}, headers=_h(chiave))).status_code == 422
    # In modifica: senza soggetto, il titolo nuovo lo dà.
    senza = (await admin.post("/v1/blog/posts", json={"titolo": "Tarot and patience", "testo": "x"}, headers=_h(chiave))).json()["articolo"]
    assert senza["subject"] is None
    m = await admin.patch(f"/v1/blog/posts/{senza['id']}", json={"titolo": "Ace of Cups and patience"}, headers=_h(chiave))
    assert m.json()["articolo"]["subject"]["ref"] == "coppe-01"
    # `titles` lo dice in forma compatta.
    titoli = (await admin.get("/v1/blog/titles", headers=_h(chiave))).json()["articoli"]
    assert {t["titolo"]: t["subject"] for t in titoli}["Wheel of Fortune Tarot Meaning"] == {"tipo": "carta", "ref": "maj-10"}


async def test_un_articolo_su_una_carta_senza_sezione_va_nella_sezione_della_carta(admin):
    chiave, _ = await _chiave(admin, ("blog:write", "blog:publish"))
    maggiori = (await admin.post("/admin/blog/sections", json={"nome": "Major Arcana", "tipo": "carte", "filtro": {"arcano": "maggiore"}})).json()
    coppe = (await admin.post("/admin/blog/sections", json={"nome": "Cups", "tipo": "carte", "filtro": {"seme": "coppe"}})).json()
    love = (await admin.post("/admin/blog/sections", json={"nome": "Love", "tipo": "articoli"})).json()
    r = await admin.post("/v1/blog/posts", json={"titolo": "Wheel of Fortune Tarot Meaning", "testo": "x"}, headers=_h(chiave))
    assert r.json()["articolo"]["sezione_id"] == maggiori["id"]
    r = await admin.post("/v1/blog/posts", json={"titolo": "Ace of Cups in Love", "testo": "x"}, headers=_h(chiave))
    assert r.json()["articolo"]["sezione_id"] == coppe["id"]
    # Con la sezione indicata resta lì; senza soggetto carta nessuna sezione d'ufficio.
    r = await admin.post("/v1/blog/posts", json={"titolo": "The Lovers tarot card in love", "testo": "x", "sezione": "love"}, headers=_h(chiave))
    assert r.json()["articolo"]["sezione_id"] == love["id"]
    r = await admin.post("/v1/blog/posts", json={"titolo": "Full Moon Tarot Spread", "testo": "x"}, headers=_h(chiave))
    assert r.json()["articolo"]["sezione_id"] is None and r.json()["articolo"]["subject"] is None
    # Anche dalla console.
    c = await admin.post("/admin/blog/posts", json={"titolo": "The Tower tarot card", "testo": "x"})
    assert c.json()["sezione_id"] == maggiori["id"] and c.json()["soggetto"]["ref"] == "maj-16"
    m = await admin.patch(f"/admin/blog/posts/{c.json()['id']}", json={"soggetto": None})
    assert m.json()["soggetto"] is None
    m = await admin.patch(f"/admin/blog/posts/{c.json()['id']}", json={"soggetto": {"tipo": "stesa", "ref": "croce-celtica"}})
    assert m.json()["soggetto"]["ref"] == "croce-celtica" and m.json()["sezione_id"] == maggiori["id"]


async def test_il_catalogo_da_le_scorciatoie_pronte_e_le_etichette_esistenti(admin):
    chiave, _ = await _chiave(admin, ("blog:write", "blog:publish"))
    await admin.post("/v1/blog/posts", json={**ARTICOLO, "stato": "pubblicato"}, headers=_h(chiave))
    cat = (await admin.get("/v1/blog/catalog", headers=_h(chiave))).json()
    assert len(cat["carte"]) == 78 and len(cat["stese"]) == 19
    stella = next(c for c in cat["carte"] if c["id"] == "maj-17")
    assert stella["slug"] == "the-star" and stella["scorciatoia"] == "[[card:the-star]]"
    assert next(s for s in cat["stese"] if s["id"] == "croce-celtica")["scorciatoia"] == "[[spread:celtic-cross]]"
    tag = (await admin.get("/v1/blog/tags", headers=_h(chiave))).json()
    assert {"slug": "hope", "nome": "Hope", "n": 1} in tag
