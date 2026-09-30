"""La notifica notturna ai motori di ricerca (v8): cosa si annuncia, con quale finestra, e che un
canale rotto non fermi gli altri. Nessuna chiamata di rete vera: i canali di `seo-notify` sono
sostituiti."""
from __future__ import annotations

from datetime import timedelta

import pytest

from tarot_core.domain.base import utcnow
from tarot_core.domain.seo_models import NotificaMotori
from tarot_core.settings import get_settings
from tarot_core.tarot.notifiche_motori import leggi_sitemap as leggi_sitemap_vera
from tarot_core.tarot.notifiche_motori import url_articolo

from .conftest import richiede_database

pytestmark = richiede_database


def test_url_articolo_inglese_alla_radice_italiano_sotto_it():
    assert url_articolo("https://tarots.chat/", "the-star", "en") == "https://tarots.chat/blog/the-star"
    assert url_articolo("https://tarots.chat", "la-stella", "it") == "https://tarots.chat/it/blog/la-stella"


@pytest.fixture
def admin(client, principal_admin):
    client.identita.principal = principal_admin
    return client


@pytest.fixture
def configura(monkeypatch):
    """Imposta le variabili dei canali per la durata del test."""
    def _configura(**variabili):
        for nome, valore in variabili.items():
            monkeypatch.setenv(f"TAROT_{nome.upper()}", valore)
        get_settings.cache_clear()
    yield _configura
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def sitemap(monkeypatch):
    """La sitemap del sito, finta: nessuna richiesta di rete. Il test ci mette gli indirizzi che vuole."""
    from tarot_core.tarot import notifiche_motori

    indirizzi: list = []
    monkeypatch.setattr(notifiche_motori, "leggi_sitemap", lambda sito: list(indirizzi))
    return indirizzi


@pytest.fixture
def indexnow_finto(monkeypatch):
    """Sostituisce l'invio IndexNow: registra gli indirizzi, risponde 200."""
    import seo_notify
    from seo_notify import RisultatoIndexNow

    inviati: list = []

    def invia(self, urls):
        inviati.extend(urls)
        return RisultatoIndexNow(ok=True, endpoint=self.endpoint, codice_stato=200)

    monkeypatch.setattr(seo_notify.ClientIndexNow, "invia", invia)
    return inviati


async def _articolo(c, titolo, **campi):
    corpo = {"titolo": titolo, "testo": "Un testo.", "stato": "pubblicato", "lang": "en", **campi}
    r = await c.post("/admin/blog/posts", json=corpo)
    assert r.status_code == 201, r.text
    return r.json()


async def test_la_console_seo_richiede_il_ruolo_admin(client):
    assert (await client.get("/admin/seo/notifiche")).status_code == 403
    assert (await client.post("/admin/seo/notifiche")).status_code == 403


async def test_si_annunciano_solo_gli_articoli_pubblici_e_indicizzabili(admin, configura, indexnow_finto):
    configura(indexnow_chiave="abc123", web_public_url="https://tarots.chat")
    pubblico = await _articolo(admin, "La Stella")
    await _articolo(admin, "Bozza", stato="bozza")
    await _articolo(admin, "Nascosto", noindex=True)
    await _articolo(admin, "Programmato", pubblicato_il=(utcnow() + timedelta(days=3)).isoformat())

    r = await admin.post("/admin/seo/notifiche")
    assert r.status_code == 201, r.text
    giro = r.json()

    # l'articolo e l'indice del blog della sua lingua
    atteso = [f"https://tarots.chat/blog/{pubblico['slug']}", "https://tarots.chat/blog"]
    assert giro["url"] == atteso
    assert indexnow_finto == atteso
    assert giro["esiti"]["indexnow"]["stato"] == "ok"
    # Google e WebSub non configurati: si saltano, e il giro resta riuscito.
    assert giro["esiti"]["search_console"]["stato"] == "saltato"
    assert giro["esiti"]["websub"]["stato"] == "saltato"
    assert giro["riuscita"] is True
    assert giro["manuale"] is True


async def test_senza_novita_dall_ultimo_giro_non_parte_nulla(admin, session, configura, indexnow_finto):
    configura(indexnow_chiave="abc123")
    await _articolo(admin, "Già annunciato")
    # Un giro precedente appena fatto: la finestra parte da lì, e l'articolo è più vecchio. Un secondo di
    # margine: le date dell'articolo le scrive in parte il database (`now()`), questa Python, e i due
    # orologi a pari istante possono differire di qualche millisecondo (il test falliva a intermittenza).
    session.add(NotificaMotori(finestra_da=utcnow() - timedelta(days=1), url=[], esiti={},
                               created_at=utcnow() + timedelta(seconds=1)))
    await session.commit()

    giro = (await admin.post("/admin/seo/notifiche")).json()

    assert giro["url"] == []
    assert indexnow_finto == []
    assert {e["stato"] for e in giro["esiti"].values()} == {"saltato"}
    assert giro["riuscita"] is True


async def test_un_canale_che_fallisce_non_ferma_gli_altri(admin, configura, monkeypatch):
    import seo_notify
    from seo_notify import RisultatoWebSub

    configura(indexnow_chiave="abc123", websub_hub="https://hub.example.com/")

    def esplode(self, urls):
        raise RuntimeError("rete giù")

    monkeypatch.setattr(seo_notify.ClientIndexNow, "invia", esplode)
    monkeypatch.setattr(seo_notify, "notifica_hub", lambda url, hub: RisultatoWebSub(ok=True, hub=hub, codice_stato=204))
    await _articolo(admin, "L'Eone")

    giro = (await admin.post("/admin/seo/notifiche")).json()

    assert giro["esiti"]["indexnow"]["stato"] == "errore"
    assert "rete giù" in giro["esiti"]["indexnow"]["dettaglio"]
    assert giro["esiti"]["websub"]["stato"] == "ok"
    assert giro["riuscita"] is False


async def test_l_elenco_mostra_la_configurazione_e_gli_invii(admin, configura, indexnow_finto):
    configura(indexnow_chiave="abc123", web_public_url="https://tarots.chat")
    await _articolo(admin, "Il Sole")
    await admin.post("/admin/seo/notifiche")

    dati = (await admin.get("/admin/seo/notifiche")).json()

    assert dati["canali"]["indexnow"]["configurato"] is True
    assert "https://tarots.chat/abc123.txt" in dati["canali"]["indexnow"]["dettaglio"]
    assert dati["canali"]["search_console"]["configurato"] is False
    assert len(dati["invii"]) == 1


SITO = "https://tarots.chat"
MAPPA = [f"{SITO}/", f"{SITO}/it", f"{SITO}/cards/the-star", f"{SITO}/it/carte/la-stella",
         f"{SITO}/spreads/celtic-cross", f"{SITO}/card-of-the-day", f"{SITO}/it/carta-del-giorno"]


async def test_home_carte_e_stese_si_annunciano_la_prima_volta_poi_solo_le_nuove_e_la_carta_del_giorno(
    admin, configura, indexnow_finto, sitemap,
):
    configura(indexnow_chiave="abc123", web_public_url=SITO)
    sitemap.extend(MAPPA)
    primo = (await admin.post("/admin/seo/notifiche")).json()
    assert primo["url"] == MAPPA and primo["riuscita"] is True

    # il giorno dopo: niente di nuovo, tranne la carta del giorno (cambia ogni giorno)
    secondo = (await admin.post("/admin/seo/notifiche")).json()
    assert secondo["url"] == [f"{SITO}/card-of-the-day", f"{SITO}/it/carta-del-giorno"]

    # una pagina nuova (per esempio una lingua aggiunta) si annuncia da sola
    sitemap.append(f"{SITO}/es/cartas/la-estrella")
    terzo = (await admin.post("/admin/seo/notifiche")).json()
    assert f"{SITO}/es/cartas/la-estrella" in terzo["url"] and f"{SITO}/cards/the-star" not in terzo["url"]


async def test_dalla_console_si_annunciano_tutte_le_pagine(admin, configura, indexnow_finto, sitemap):
    configura(indexnow_chiave="abc123", web_public_url=SITO)
    sitemap.extend(MAPPA)
    await admin.post("/admin/seo/notifiche")
    indexnow_finto.clear()
    tutte = (await admin.post("/admin/seo/notifiche?tutte=true")).json()
    assert tutte["url"] == MAPPA and indexnow_finto == MAPPA


async def test_senza_sitemap_si_annunciano_comunque_gli_articoli(admin, configura, indexnow_finto, monkeypatch):
    from tarot_core.tarot import notifiche_motori

    def giu(sito):
        raise OSError("sito irraggiungibile")

    monkeypatch.setattr(notifiche_motori, "leggi_sitemap", giu)
    configura(indexnow_chiave="abc123", web_public_url=SITO)
    art = await _articolo(admin, "La Luna")
    giro = (await admin.post("/admin/seo/notifiche")).json()
    assert f"{SITO}/blog/{art['slug']}" in giro["url"]
    assert giro["esiti"]["sitemap"]["stato"] == "errore" and "irraggiungibile" in giro["esiti"]["sitemap"]["dettaglio"]
    assert giro["esiti"]["indexnow"]["stato"] == "ok" and giro["riuscita"] is False


def test_la_sitemap_si_legge_solo_per_il_sito_stesso(monkeypatch):
    import httpx

    xml = (b'<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
           b'<url><loc>https://tarots.chat/</loc></url><url><loc>https://altro.example/x</loc></url>'
           b'<url><loc>https://tarots.chat/cards/the-star</loc></url></urlset>')
    monkeypatch.setattr(httpx, "get", lambda url, **k: httpx.Response(200, content=xml, request=httpx.Request("GET", url)))
    assert leggi_sitemap_vera("https://tarots.chat") == ["https://tarots.chat/", "https://tarots.chat/cards/the-star"]
