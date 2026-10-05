"""L'elenco compatto di tutti gli articoli (`GET /v1/blog/titles`), attraverso l'API e un database vero.

Serve all'agente che scrive il blog per scegliere un argomento nuovo senza leggere gli articoli interi: deve vedere
**tutti** gli articoli (di qualunque chiave e della console), con pochi campi, a pagine grandi.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import update

from tarot_core.auth import chiavi
from tarot_core.domain.blog_models import BlogPost

from .conftest import richiede_database

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


async def _chiave(admin, scopes=("blog:write",)):
    r = await admin.post("/admin/blog/api-keys", json={"nome": "Agente", "scopes": list(scopes), "limite_minuto": 600})
    assert r.status_code == 201, r.text
    return r.json()["chiave"]


def _h(chiave):
    return {"Authorization": f"Bearer {chiave}"}


async def _dalla_console(admin, titolo, **campi):
    r = await admin.post("/admin/blog/posts", json={"titolo": titolo, "testo": "Un testo della redazione.", **campi})
    assert r.status_code == 201, r.text
    return r.json()


async def _dalla_chiave(admin, chiave, titolo, **campi):
    r = await admin.post("/v1/blog/posts", json={"titolo": titolo, "testo": "Testo di un agente.", **campi}, headers=_h(chiave))
    assert r.status_code == 201, r.text
    return r.json()["articolo"]


async def _titoli(admin, chiave, **params):
    r = await admin.get("/v1/blog/titles", params=params, headers=_h(chiave))
    assert r.status_code == 200, r.text
    return r.json()


# ---- i permessi -----------------------------------------------------------------------------------------------


async def test_servono_blog_write_o_blog_media(admin):
    assert (await admin.get("/v1/blog/titles")).status_code == 401
    solo_publish = await _chiave(admin, ("blog:publish",))
    assert (await admin.get("/v1/blog/titles", headers=_h(solo_publish))).status_code == 403
    for scopes in (("blog:write",), ("blog:media",)):
        assert (await admin.get("/v1/blog/titles", headers=_h(await _chiave(admin, scopes)))).status_code == 200


# ---- il contenuto -------------------------------------------------------------------------------------------------


async def test_ci_sono_gli_articoli_di_tutti_con_i_campi_compatti_e_mio(admin):
    a = await _chiave(admin)
    b = await _chiave(admin, ("blog:write", "blog:publish"))
    sezione = (await admin.post("/admin/blog/sections", json={"nome": "Love", "tipo": "articoli"})).json()
    mio = await _dalla_chiave(admin, a, "The Star Meaning", seo_parola_chiave="star tarot meaning", sezione="love")
    altrui = await _dalla_chiave(admin, b, "The Moon Meaning", stato="pubblicato")
    console = await _dalla_console(admin, "La Papessa", stato="pubblicato", lang="it", sezione_id=sezione["id"])

    dati = await _titoli(admin, a)
    assert dati["totale"] == 3 and dati["pagina"] == 1 and dati["per_pagina"] == 200 and dati["adesso"]
    per_id = {x["id"]: x for x in dati["articoli"]}
    assert set(per_id) == {mio["id"], altrui["id"], console["id"]}
    m = per_id[mio["id"]]
    assert set(m) == {"id", "slug", "titolo", "estratto", "parola_chiave", "sezione", "lang", "stato", "pubblicato_il",
                      "aggiornato", "mio", "tradotto_da_id"}
    assert m["mio"] is True and m["slug"] == "the-star-meaning" and m["parola_chiave"] == "star tarot meaning"
    assert m["sezione"] == "love" and m["lang"] == "en" and m["stato"] == "bozza" and m["pubblicato_il"] is None
    assert m["aggiornato"] and m["tradotto_da_id"] is None
    assert per_id[altrui["id"]]["mio"] is False and per_id[altrui["id"]]["stato"] == "pubblicato"
    assert per_id[altrui["id"]]["pubblicato_il"]
    assert per_id[console["id"]]["mio"] is False and per_id[console["id"]]["sezione"] == "love"
    # per l'altra chiave «mio» è l'altro articolo
    assert [x["id"] for x in (await _titoli(admin, b))["articoli"] if x["mio"]] == [altrui["id"]]


async def test_l_estratto_e_sottotitolo_poi_descrizione_poi_l_inizio_del_testo(admin):
    chiave = await _chiave(admin)
    lungo = "Parola " * 400 + "FINE"
    await _dalla_console(admin, "Con sottotitolo", sottotitolo="Il sottotitolo", seo_descrizione="La descrizione", testo=lungo)
    await _dalla_console(admin, "Con descrizione", seo_descrizione="La descrizione SEO", testo=lungo)
    await _dalla_console(admin, "Solo testo", testo="## Un titolo\n\nVedi [[card:the-star]] e **questo**. " + lungo)
    await _dalla_console(admin, "Descrizione lunga", seo_descrizione="x" * 20 + " " + "parola " * 40)
    per_titolo = {x["titolo"]: x["estratto"] for x in (await _titoli(admin, chiave))["articoli"]}
    assert per_titolo["Con sottotitolo"] == "Il sottotitolo"
    assert per_titolo["Con descrizione"] == "La descrizione SEO"
    solo = per_titolo["Solo testo"]
    # come il blog pubblico: senza Markdown, con il nome della carta, tagliato a fine parola con i puntini
    assert solo.startswith("Un titolo Vedi La Stella e questo. Parola") and solo.endswith("…") and len(solo) <= 161
    assert "FINE" not in solo
    assert len(per_titolo["Descrizione lunga"]) <= 161 and per_titolo["Descrizione lunga"].endswith("…")


async def test_la_traduzione_porta_l_id_dell_originale(admin, session):
    chiave = await _chiave(admin)
    originale = await _dalla_console(admin, "Originale", lang="en")
    traduzione = await _dalla_console(admin, "Traduzione", lang="it")
    await session.execute(
        update(BlogPost).where(BlogPost.id == uuid.UUID(traduzione["id"])).values(tradotto_da_id=uuid.UUID(originale["id"]))
    )
    await session.flush()
    per_id = {x["id"]: x for x in (await _titoli(admin, chiave))["articoli"]}
    assert per_id[traduzione["id"]]["tradotto_da_id"] == originale["id"] and per_id[originale["id"]]["tradotto_da_id"] is None


# ---- i filtri ---------------------------------------------------------------------------------------------------


async def test_filtri_per_lingua_stato_sezione_e_ricerca(admin):
    chiave = await _chiave(admin)
    await admin.post("/admin/blog/sections", json={"nome": "Love", "tipo": "articoli"})
    await admin.post("/admin/blog/sections", json={"nome": "Spreads", "tipo": "articoli"})
    s_love = next(s for s in (await admin.get("/admin/blog/sections")).json() if s["slug"] == "love")
    await _dalla_console(admin, "Tower in love", stato="pubblicato", lang="en", sezione_id=s_love["id"], seo_parola_chiave="tower love")
    await _dalla_console(admin, "La Torre in amore", stato="pubblicato", lang="it")
    await _dalla_console(admin, "Celtic cross guide", stato="bozza", lang="en", slug="celtic-cross-how-to")
    await _dalla_console(admin, "Hidden 50% offer", stato="bozza", lang="en", seo_parola_chiave="ace of wands")

    titoli = lambda d: sorted(x["titolo"] for x in d["articoli"])  # noqa: E731
    assert titoli(await _titoli(admin, chiave, lang="it")) == ["La Torre in amore"]
    assert titoli(await _titoli(admin, chiave, stato="bozza")) == ["Celtic cross guide", "Hidden 50% offer"]
    assert titoli(await _titoli(admin, chiave, sezione="love")) == ["Tower in love"]
    assert (await _titoli(admin, chiave, sezione="nessuna"))["totale"] == 0
    # la ricerca guarda titolo, slug e parola chiave, senza badare alle maiuscole
    assert titoli(await _titoli(admin, chiave, q="TOWER")) == ["Tower in love"]
    assert titoli(await _titoli(admin, chiave, q="how-to")) == ["Celtic cross guide"]
    assert titoli(await _titoli(admin, chiave, q="ace of wands")) == ["Hidden 50% offer"]
    # i caratteri speciali di LIKE si cercano come sono
    assert titoli(await _titoli(admin, chiave, q="50%")) == ["Hidden 50% offer"]
    assert (await _titoli(admin, chiave, q="_"))["totale"] == 0
    assert titoli(await _titoli(admin, chiave, q="torre", lang="en")) == []


async def test_gli_archiviati_solo_se_chiesti(admin):
    chiave = await _chiave(admin)
    vivo = await _dalla_console(admin, "Vivo", stato="pubblicato")
    vecchio = await _dalla_console(admin, "Vecchio", stato="pubblicato")
    assert (await admin.post(f"/admin/blog/posts/{vecchio['id']}/archivia")).status_code == 200
    assert [x["id"] for x in (await _titoli(admin, chiave))["articoli"]] == [vivo["id"]]
    con = await _titoli(admin, chiave, archiviati="true")
    assert {x["id"] for x in con["articoli"]} == {vivo["id"], vecchio["id"]} and con["totale"] == 2
    assert [x["id"] for x in (await _titoli(admin, chiave, stato="archiviato"))["articoli"]] == [vecchio["id"]]


async def test_dal_da_solo_gli_aggiornati_dopo_quel_momento(admin, session):
    chiave = await _chiave(admin)
    fermo = await _dalla_console(admin, "Fermo")
    toccato = await _dalla_console(admin, "Toccato")
    tutti = await _titoli(admin, chiave)
    adesso = datetime.fromisoformat(tutti["adesso"])
    # Nei test tutto avviene in una transazione (now() non cambia): l'aggiornamento successivo si simula.
    await session.execute(
        update(BlogPost).where(BlogPost.id == uuid.UUID(toccato["id"])).values(updated_at=adesso + timedelta(hours=1))
    )
    await session.flush()
    assert {x["id"] for x in (await _titoli(admin, chiave, dal=adesso.isoformat()))["articoli"]} == {fermo["id"], toccato["id"]}
    dopo = await _titoli(admin, chiave, dal=(adesso + timedelta(minutes=30)).isoformat())
    assert [x["id"] for x in dopo["articoli"]] == [toccato["id"]] and dopo["totale"] == 1
    assert (await _titoli(admin, chiave, dal=(adesso + timedelta(hours=2)).isoformat()))["totale"] == 0
    # anche una data senza fuso (si intende UTC)
    senza_fuso = (adesso + timedelta(minutes=30)).astimezone(timezone.utc).replace(tzinfo=None).isoformat()
    assert [x["id"] for x in (await _titoli(admin, chiave, dal=senza_fuso))["articoli"]] == [toccato["id"]]


# ---- pagine e ordine ---------------------------------------------------------------------------------------------


async def test_pagine_fino_a_mille_in_ordine_di_data_decrescente(admin):
    chiave = await _chiave(admin)
    for giorno in range(1, 8):
        await _dalla_console(admin, f"Giorno {giorno}", stato="pubblicato", pubblicato_il=f"2026-01-0{giorno}T08:00:00Z")
    p1 = await _titoli(admin, chiave, per_pagina=3)
    p2 = await _titoli(admin, chiave, per_pagina=3, pagina=2)
    p3 = await _titoli(admin, chiave, per_pagina=3, pagina=3)
    assert [x["titolo"] for x in p1["articoli"]] == ["Giorno 7", "Giorno 6", "Giorno 5"]
    assert [x["titolo"] for x in p2["articoli"]] == ["Giorno 4", "Giorno 3", "Giorno 2"]
    assert [x["titolo"] for x in p3["articoli"]] == ["Giorno 1"]
    assert p1["totale"] == p2["totale"] == p3["totale"] == 7
    # oltre la fine: nessun articolo, ma il totale giusto
    oltre = await _titoli(admin, chiave, per_pagina=3, pagina=9)
    assert oltre["articoli"] == [] and oltre["totale"] == 7
    assert (await _titoli(admin, chiave, per_pagina=1000))["per_pagina"] == 1000
    assert (await admin.get("/v1/blog/titles", params={"per_pagina": 1001}, headers=_h(chiave))).status_code == 422
    assert (await admin.get("/v1/blog/titles", params={"pagina": 0}, headers=_h(chiave))).status_code == 422
