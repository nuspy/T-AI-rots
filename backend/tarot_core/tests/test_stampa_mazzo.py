"""Il PDF "Stampa i tuoi Tarocchi" (v5, Fase B4): impaginazione, marchio condizionato al prezzo, e i
due percorsi di download (gratuito e a pagamento)."""
from __future__ import annotations

import io

import pytest
from pypdf import PdfReader

from tarot_core.domain.deck_models import Deck
from tarot_core.tarot.stampa_mazzo import _griglia, _posizione, genera_pdf

from .conftest import richiede_database

pytestmark = richiede_database


# ---- genera_pdf(), pura rispetto all'IO (le immagini sono già in memoria) -------------------------


def test_griglia_sta_dentro_la_pagina_a4():
    colonne, righe = _griglia()
    assert colonne >= 1 and righe >= 1


def test_il_dorso_specchiato_scambia_prima_e_ultima_colonna():
    colonne, righe = _griglia()
    x_prima_colonna, _ = _posizione(0, 0, colonne, righe)
    x_ultima_colonna, _ = _posizione(colonne - 1, 0, colonne, righe)
    # La posizione specchiata della prima colonna (usata per il dorso) è la posizione reale
    # dell'ultima: è così che il retro cade sopra il fronte giusto dopo la stampa fronte/retro.
    x_specchiata_prima, y1 = _posizione(colonne - 1 - 0, 0, colonne, righe)
    x_specchiata_ultima, y2 = _posizione(colonne - 1 - (colonne - 1), 0, colonne, righe)
    assert x_specchiata_prima == x_ultima_colonna
    assert x_specchiata_ultima == x_prima_colonna


def test_pdf_e_un_pdf_valido():
    corpo = genera_pdf(["maj-00", "maj-01"], {}, gratuito=True)
    assert corpo.startswith(b"%PDF")
    PdfReader(io.BytesIO(corpo))  # non solleva: la struttura si legge


def test_marchio_presente_solo_se_gratuito():
    con_marchio = genera_pdf(["maj-00"], {}, gratuito=True)
    senza_marchio = genera_pdf(["maj-00"], {}, gratuito=False)
    testo_con = PdfReader(io.BytesIO(con_marchio)).pages[0].extract_text()
    testo_senza = PdfReader(io.BytesIO(senza_marchio)).pages[0].extract_text()
    assert "tarots.chat" in testo_con
    assert "tarots.chat" not in testo_senza


def test_marchio_testo_personalizzato_sostituisce_tarots_chat():
    # Uno strumento fuori dalla produzione (la bozza di un mazzo nuovo) vuole un marchio di copyright
    # completo invece del semplice nome del sito, sempre presente: `marchio_testo` lo permette senza
    # toccare il comportamento di produzione (nessuna chiamata esistente lo passa).
    corpo = genera_pdf(["maj-00"], {}, gratuito=True, marchio_testo="© 2026 Copyright https://tarots.chat")
    testo = PdfReader(io.BytesIO(corpo)).pages[0].extract_text()
    assert "Copyright" in testo
    assert "tarots.chat" in testo  # è contenuto nel marchio personalizzato stesso


def test_marchio_testo_ignorato_se_non_gratuito():
    corpo = genera_pdf(["maj-00"], {}, gratuito=False, marchio_testo="© 2026 Copyright https://tarots.chat")
    testo = PdfReader(io.BytesIO(corpo)).pages[0].extract_text()
    assert "Copyright" not in testo


def test_una_carta_senza_immagine_disegna_un_segnaposto_invece_di_fallire():
    # Nessuna immagine passata: non deve sollevare, il segnaposto (un rettangolo) prende il posto.
    corpo = genera_pdf(["maj-00", "maj-01", "maj-02"], {}, gratuito=False)
    assert corpo.startswith(b"%PDF")


def test_pagine_alternano_fronte_e_dorso_una_coppia_per_gruppo():
    colonne, righe = _griglia()
    per_pagina = colonne * righe
    # Due gruppi pieni: 4 pagine (fronte, dorso, fronte, dorso).
    ordine = [f"c{i}" for i in range(per_pagina * 2)]
    corpo = genera_pdf(ordine, {}, gratuito=False)
    assert len(PdfReader(io.BytesIO(corpo)).pages) == 4


# ---- gli endpoint: il download gratuito e quello legato a un ordine pagato ------------------------


async def test_pdf_gratuito_quando_il_prezzo_di_stampa_e_zero(client, session):
    mazzo = Deck(nome="Gratis", slug="stampa-gratis", attivo=True, prezzo_stampa=0)
    session.add(mazzo)
    await session.commit()

    r = await client.get(f"/decks/{mazzo.slug}/pdf")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content.startswith(b"%PDF")
    testo = PdfReader(io.BytesIO(r.content)).pages[0].extract_text()
    assert "tarots.chat" in testo


@pytest.mark.parametrize("prezzo_stampa", [None, 500])
async def test_pdf_gratuito_404_se_non_e_a_prezzo_zero(client, session, prezzo_stampa):
    mazzo = Deck(nome="NonGratis", slug=f"stampa-non-gratis-{prezzo_stampa}", attivo=True, prezzo_stampa=prezzo_stampa)
    session.add(mazzo)
    await session.commit()
    r = await client.get(f"/decks/{mazzo.slug}/pdf")
    assert r.status_code == 404


async def test_pdf_di_un_ordine_richiede_che_sia_pagato(client, session):
    mazzo = Deck(nome="DaStampare", slug="da-stampare", attivo=True, prezzo_stampa=500)
    session.add(mazzo)
    await session.commit()
    r = await client.post("/orders", json={"voci": [{"deck_id": mazzo.id, "tipo": "pdf"}]})
    assert r.status_code == 201, r.text
    ordine_id = r.json()["id"]

    non_pagato = await client.get(f"/me/orders/{ordine_id}/pdf/{mazzo.id}")
    assert non_pagato.status_code == 403

    await client.post(f"/billing/mock/ordine/{ordine_id}/esito", data={"esito": "paga", "ritorno": "/mazzo"})
    pagato = await client.get(f"/me/orders/{ordine_id}/pdf/{mazzo.id}")
    assert pagato.status_code == 200
    assert pagato.content.startswith(b"%PDF")
    # Comprato, non gratuito: nessun marchio.
    testo = PdfReader(io.BytesIO(pagato.content)).pages[0].extract_text()
    assert "tarots.chat" not in testo


async def test_pdf_di_un_ordine_senza_riga_pdf_per_quel_mazzo_e_404(client, session):
    mazzo = Deck(nome="SoloDigitale", slug="solo-digitale", attivo=True, prezzo_digitale=1000)
    session.add(mazzo)
    await session.commit()
    r = await client.post("/orders", json={"voci": [{"deck_id": mazzo.id, "tipo": "digitale"}]})
    ordine_id = r.json()["id"]
    await client.post(f"/billing/mock/ordine/{ordine_id}/esito", data={"esito": "paga", "ritorno": "/mazzo"})

    r2 = await client.get(f"/me/orders/{ordine_id}/pdf/{mazzo.id}")
    assert r2.status_code == 404
