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
    r = await admin.post("/v1/blog/posts", json={**ARTICOLO, "sezione": "cards"}, headers=_h(chiave))
    assert r.status_code == 422 and r.json()["detail"]["sezioni_valide"] == ["love"]
    ok = await admin.post("/v1/blog/posts", json={**ARTICOLO, "sezione": "love"}, headers=_h(chiave))
    assert ok.status_code == 201 and ok.json()["articolo"]["sezione_id"] == valida["id"]
    sezioni = (await admin.get("/v1/blog/sections", headers=_h(chiave))).json()
    assert [s["slug"] for s in sezioni] == ["love"]


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


# ---- modificare e cancellare: solo i propri ------------------------------------------------------------------------


async def test_una_chiave_tocca_solo_i_propri_articoli(admin):
    a, _ = await _chiave(admin, ("blog:write", "blog:publish"))
    b, _ = await _chiave(admin, ("blog:write", "blog:publish"))
    creato = (await admin.post("/v1/blog/posts", json={**ARTICOLO, "titolo": "Di A"}, headers=_h(a))).json()["articolo"]
    assert (await admin.get(f"/v1/blog/posts/{creato['id']}", headers=_h(b))).status_code == 404
    assert (await admin.patch(f"/v1/blog/posts/{creato['id']}", json={"titolo": "Rubato"}, headers=_h(b))).status_code == 404
    assert (await admin.delete(f"/v1/blog/posts/{creato['id']}", headers=_h(b))).status_code == 404
    r = await admin.patch(f"/v1/blog/posts/{creato['id']}", json={"testo": "Nuovo testo.", "seo_titolo": "Un titolo SEO"}, headers=_h(a))
    assert r.status_code == 200 and r.json()["articolo"]["testo"] == "Nuovo testo." and r.json()["articolo"]["titolo"] == "Di A"
    assert [x["titolo"] for x in (await admin.get("/v1/blog/posts", headers=_h(a))).json()["articoli"]] == ["Di A"]
    assert (await admin.get("/v1/blog/posts", headers=_h(b))).json()["totale"] == 0


async def test_si_cancellano_solo_le_bozze_e_una_chiave_senza_permesso_non_tocca_il_pubblicato(admin):
    scrittore, _ = await _chiave(admin)
    editor, _ = await _chiave(admin, ("blog:write", "blog:publish"))
    bozza = (await admin.post("/v1/blog/posts", json={**ARTICOLO, "titolo": "Bozza"}, headers=_h(scrittore))).json()["articolo"]
    assert (await admin.delete(f"/v1/blog/posts/{bozza['id']}", headers=_h(scrittore))).status_code == 204
    pubblicato = (await admin.post("/v1/blog/posts", json={**ARTICOLO, "titolo": "Uscito", "stato": "pubblicato"}, headers=_h(editor))).json()["articolo"]
    assert (await admin.delete(f"/v1/blog/posts/{pubblicato['id']}", headers=_h(editor))).status_code == 409
    # La stessa chiave, se poi perde il permesso, non può più modificare ciò che è uscito: qui una chiave a sola scrittura
    # non può nemmeno vederlo (non è sua). E se fosse sua e già pubblicata:
    solo_scrittura, dati = await _chiave(admin)
    mio = (await admin.post("/v1/blog/posts", json={**ARTICOLO, "titolo": "Mio"}, headers=_h(solo_scrittura))).json()["articolo"]
    await admin.post(f"/admin/blog/posts/{mio['id']}/pubblica")
    r = await admin.patch(f"/v1/blog/posts/{mio['id']}", json={"testo": "Cambio"}, headers=_h(solo_scrittura))
    assert r.status_code == 403


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
