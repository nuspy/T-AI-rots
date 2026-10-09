"""I conti delle sezioni del Diario sono di tutto il ramo, e coincidono con quello che la pagina della sezione mostra.

L'albero è quello del sito: «Tarot» (contenitore) con gli arcani maggiori, i minori (contenitore con i semi), «Learn
tarot» (articoli, con le stese dentro); «Articles» (contenitore) con le sezioni a tema. Un contenitore conta gli
articoli delle sotto-sezioni; il filtro `sezione` di un contenitore restituisce il suo ramo, non tutto il diario; le
pagine di sezione e di etichetta (`/blog/nove` con `completa=false`) non pescano articoli da fuori."""
from __future__ import annotations

import pytest

from .conftest import richiede_database

pytestmark = richiede_database


@pytest.fixture
def admin(client, principal_admin):
    client.identita.principal = principal_admin
    return client


async def _sezione(c, nome, **campi):
    r = await c.post("/admin/blog/sections", json={"nome": nome, **campi})
    assert r.status_code == 201, r.text
    return r.json()


async def _articolo(c, titolo, pubblica=True, **campi):
    corpo = {"titolo": titolo, "testo": "Un testo di prova.", "lang": "en", **campi}
    if pubblica:
        corpo["stato"] = "pubblicato"
    r = await c.post("/admin/blog/posts", json=corpo)
    assert r.status_code == 201, r.text
    return r.json()


async def _sito(c):
    """L'albero del sito, con gli articoli: 3 in «Learn tarot», 1 in «Love», 4 in «Spirituality», più una bozza e un
    articolo senza sezione (che non contano in nessuna sezione)."""
    tarot = await _sezione(c, "Tarot", tipo="contenitore", ordine=1)
    await _sezione(c, "Major Arcana", tipo="carte", filtro={"arcano": "maggiore"}, parent_id=tarot["id"], ordine=1)
    minori = await _sezione(c, "Minor Arcana", tipo="contenitore", parent_id=tarot["id"], ordine=2)
    await _sezione(c, "Wands", tipo="carte", filtro={"seme": "bastoni"}, parent_id=minori["id"], ordine=1)
    await _sezione(c, "Cups", tipo="carte", filtro={"seme": "coppe"}, parent_id=minori["id"], ordine=2)
    learn = await _sezione(c, "Learn Tarot", parent_id=tarot["id"], ordine=3)
    await _sezione(c, "Tarot Spreads", tipo="stese", parent_id=learn["id"])
    articles = await _sezione(c, "Articles", tipo="contenitore", ordine=2)
    love = await _sezione(c, "Love", parent_id=articles["id"], ordine=1)
    spirito = await _sezione(c, "Spirituality", parent_id=articles["id"], ordine=2)
    await _sezione(c, "Career", parent_id=articles["id"], ordine=3)              # vuota
    for i in range(3):
        await _articolo(c, f"Learn {i}", sezione_id=learn["id"], tags=["Basics"])
    await _articolo(c, "Love 0", sezione_id=love["id"], tags=["Basics"])
    for i in range(4):
        await _articolo(c, f"Spirit {i}", sezione_id=spirito["id"])
    await _articolo(c, "Spirit bozza", pubblica=False, sezione_id=spirito["id"], tags=["Basics"])
    await _articolo(c, "Senza sezione", tags=["Basics"])


def _per_slug(nodi, risultato=None):
    risultato = {} if risultato is None else risultato
    for n in nodi:
        risultato[n["slug"]] = n
        _per_slug(n["figli"], risultato)
    return risultato


async def test_una_sezione_conta_gli_articoli_di_tutto_il_ramo(admin):
    await _sito(admin)
    nodi = _per_slug((await admin.get("/blog/sections")).json())

    # «Articles» non ha articoli suoi: conta quelli delle sotto-sezioni (1 + 4), senza la bozza.
    assert nodi["articles"]["n_articoli"] == 5 and nodi["articles"]["n_articoli_diretti"] == 0
    assert nodi["spirituality"]["n_articoli"] == nodi["spirituality"]["n_articoli_diretti"] == 4
    assert nodi["career"]["n_articoli"] == 0
    # «Tarot» conta «Learn tarot» (3) e nient'altro: le sezioni di carte e stese non hanno articoli.
    assert nodi["tarot"]["n_articoli"] == 3 and nodi["tarot"]["n_articoli_diretti"] == 0
    assert nodi["learn-tarot"]["n_articoli"] == 3
    assert nodi["minor-arcana"]["n_articoli"] == 0

    # Carte e stese del ramo, senza doppioni: i maggiori (22) e due semi (14 + 14); le stese del catalogo.
    assert nodi["major-arcana"]["n_elementi"] == nodi["major-arcana"]["n_carte"] == 22
    assert nodi["minor-arcana"]["n_carte"] == 28 and nodi["minor-arcana"]["n_elementi"] is None
    assert nodi["tarot"]["n_carte"] == 50
    stese = nodi["tarot-spreads"]["n_elementi"]
    assert stese and nodi["tarot-spreads"]["n_stese"] == stese
    assert nodi["learn-tarot"]["n_stese"] == nodi["tarot"]["n_stese"] == stese
    assert nodi["articles"]["n_carte"] == nodi["articles"]["n_stese"] == 0

    # Il dettaglio di una sezione ha gli stessi conti dell'albero.
    dettaglio = (await admin.get("/blog/sections/tarot")).json()
    assert (dettaglio["n_articoli"], dettaglio["n_carte"], dettaglio["n_stese"]) == (3, 50, stese)


async def test_una_carta_in_due_sotto_sezioni_conta_una_volta(admin):
    await _sito(admin)
    tarot = (await admin.get("/blog/sections/tarot")).json()
    # Una sezione con tutto il mazzo, accanto ai maggiori e ai semi: le carte del ramo restano 78, non 78 + 50.
    await _sezione(admin, "All cards", tipo="carte", parent_id=tarot["id"])
    nodi = _per_slug((await admin.get("/blog/sections")).json())
    assert nodi["all-cards"]["n_elementi"] == 78
    assert nodi["tarot"]["n_carte"] == 78


async def test_il_filtro_di_un_contenitore_da_il_suo_ramo_e_non_tutto_il_diario(admin):
    await _sito(admin)
    articles = (await admin.get("/blog/posts", params={"sezione": "articles", "per_pagina": 50})).json()
    assert articles["totale"] == 5
    assert {a["sezione"]["slug"] for a in articles["articoli"]} == {"love", "spirituality"}
    # Un contenitore senza articoli nel ramo non ne mostra nessuno.
    assert (await admin.get("/blog/posts", params={"sezione": "minor-arcana"})).json()["totale"] == 0
    assert (await admin.get("/blog/posts", params={"sezione": "major-arcana"})).json()["totale"] == 0
    tarot = (await admin.get("/blog/posts", params={"sezione": "tarot", "per_pagina": 50})).json()
    assert {a["sezione"]["slug"] for a in tarot["articoli"]} == {"learn-tarot"}


async def test_il_numero_dell_albero_e_quello_degli_articoli_della_pagina(admin):
    """Per ogni sezione: il numero dell'albero = il totale dell'elenco filtrato = gli articoli diversi che la pagina
    della sezione mostra (la prima pagina dell'elenco più i «scelti a caso», che non escono dalla sezione)."""
    await _sito(admin)
    nodi = _per_slug((await admin.get("/blog/sections")).json())
    for slug, nodo in nodi.items():
        elenco = (await admin.get("/blog/posts", params={"sezione": slug, "per_pagina": 50})).json()
        assert elenco["totale"] == nodo["n_articoli"], slug
        nove = (await admin.get("/blog/nove", params={
            "sezione": slug, "recenti": 6, "scelti": 10, "completa": "false",
        })).json()
        mostrati = {a["slug"] for a in nove["recenti"] + nove["scelti"]}
        assert mostrati <= {a["slug"] for a in elenco["articoli"]}, slug
        assert len(mostrati) == min(nodo["n_articoli"], 16), slug


async def test_la_pagina_di_un_etichetta_non_pesca_fuori_dall_etichetta(admin):
    await _sito(admin)
    basics = next(t for t in (await admin.get("/blog/tags")).json() if t["slug"] == "basics")
    assert basics["n"] == 5                                     # 3 + 1 + quello senza sezione; non la bozza
    elenco = (await admin.get("/blog/posts", params={"tag": "basics", "per_pagina": 50})).json()
    assert elenco["totale"] == basics["n"]
    nove = (await admin.get("/blog/nove", params={"tag": "basics", "recenti": 6, "scelti": 10, "completa": "false"})).json()
    assert {a["slug"] for a in nove["recenti"] + nove["scelti"]} == {a["slug"] for a in elenco["articoli"]}
    # Dal 9/10/2026 `completa` non cambia nulla: con un'etichetta si pesca solo lì, sempre.
    tutti = (await admin.get("/blog/nove", params={"tag": "basics", "recenti": 6, "scelti": 10})).json()
    assert {a["slug"] for a in tutti["recenti"] + tutti["scelti"]} == {a["slug"] for a in elenco["articoli"]}


async def test_una_sezione_che_non_ce_non_da_le_recenti_di_tutto_il_diario(admin):
    await _sito(admin)
    nove = (await admin.get("/blog/nove", params={"sezione": "non-esiste", "completa": "false"})).json()
    assert nove == {"recenti": [], "scelti": []}


async def test_la_mappa_conta_i_cataloghi_del_ramo(admin):
    await _sito(admin)
    mappa = (await admin.get("/blog/mappa")).json()
    lingue = mappa["sezioni_lingue"]
    assert lingue["major-arcana"] == ["en", "it"]
    # Un contenitore di soli cataloghi non è vuoto: è l'indice dei semi, nella lingua canonica.
    assert lingue["minor-arcana"] == ["en"]
    assert lingue["articles"] == ["en"] and lingue["career"] == []
    assert set(mappa["sezioni_tradotte"]) == {"major-arcana", "wands", "cups", "tarot-spreads"}
