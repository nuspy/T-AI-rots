"""Le regole pure del blog: slug, tempo di lettura, estratti, collegamenti, immagini."""
from __future__ import annotations

import io

import pytest

from tarot_core.tarot import blog as b


def _immagine(larghezza=800, altezza=600, formato="PNG", modo="RGB", colore=(200, 40, 90)):
    from PIL import Image

    img = Image.new(modo, (larghezza, altezza), colore)
    uscita = io.BytesIO()
    img.save(uscita, format=formato)
    return uscita.getvalue()


# ---- slug ------------------------------------------------------------------------------------


@pytest.mark.parametrize("titolo, atteso", [
    ("Che cos'è la Papessa?", "che-cos-e-la-papessa"),
    ("  Amore & Relazioni: 7 carte  ", "amore-relazioni-7-carte"),
    ("Città, età, più", "citta-eta-piu"),
    ("Тарот", ""),                       # niente lettere latine: lo slug è vuoto, ci pensa slug_libero
    ("---", ""),
])
def test_slugify(titolo, atteso):
    assert b.slugify(titolo) == atteso


def test_slug_libero_aggiunge_un_numero_e_ha_un_ripiego():
    assert b.slug_libero("La Stella", []) == "la-stella"
    assert b.slug_libero("La Stella", ["la-stella"]) == "la-stella-2"
    assert b.slug_libero("La Stella", ["la-stella", "la-stella-2"]) == "la-stella-3"
    assert b.slug_libero("Тарот", []) == "articolo"
    assert len(b.slug_libero("x" * 500, [], massimo=80)) <= 80


def test_le_etichette_si_normalizzano():
    assert b.normalizza_etichetta("  Arcani   Maggiori ") == ("arcani-maggiori", "Arcani Maggiori")
    assert b.normalizza_etichetta("   ") == ("", "")


# ---- testo -----------------------------------------------------------------------------------


def test_tempo_di_lettura_ha_un_minimo_di_un_minuto():
    assert b.tempo_lettura("") == 1 and b.tempo_lettura("poche parole") == 1
    assert b.tempo_lettura("parola " * 401) == 3
    # Le scorciatoie non sono parole lette.
    assert b.tempo_lettura("[[carta:maj-17]] " * 500) == 1


def test_il_testo_semplice_toglie_markdown_e_scorciatoie():
    md = "## Titolo\n\nUn **testo** con [un link](/carte/maj-17) e `codice`.\n\n[[carta:maj-00]]\n\n- voce uno\n- voce due\n\n![img](/x.png)"
    assert b.testo_semplice(md) == "Titolo Un testo con un link e codice. voce uno voce due"


def test_l_estratto_mette_il_nome_al_posto_delle_scorciatoie():
    testo = "Determinazione e direzione: [[carta:maj-07]]. Guida: [[stesa:croce-celtica]] e [[articolo:x]]."
    nomi = {("carta", "maj-07"): "Il Carro", ("stesa", "croce-celtica"): "Croce Celtica"}
    assert b.estratto(testo, 200, lambda t, i: nomi.get((t, i))) == "Determinazione e direzione: Il Carro. Guida: Croce Celtica e ."
    assert b.estratto(testo, 200) == "Determinazione e direzione: . Guida: e ."


def test_il_testo_ricco_e_i_video_non_finiscono_negli_estratti():
    testo = (
        "Un :testo[titolo in ottone]{colore=ottone dimensione=grande} e :text[plum]{color=plum}, "
        ":sottolineato[sotto] e :underline[under].\n\n[[video:vimeo:123456789]]\n\n[[video:youtube:dQw4w9WgXcQ]]\n\n"
        "![Una carta](/blog/media/x.webp \"La didascalia\") Alle 10:30, :pericolo[resta]."
    )
    assert b.testo_semplice(testo) == (
        "Un titolo in ottone e plum, sotto e under. Alle 10:30, :pericolo[resta]."
    )


def test_l_estratto_taglia_a_fine_parola():
    testo = "Una frase abbastanza lunga da dover essere tagliata prima della fine, senza spezzare le parole a metà."
    e = b.estratto(testo, 40)
    assert e.endswith("…") and len(e) <= 41 and not e[:-1].endswith("se")
    assert b.estratto("Breve", 40) == "Breve"


def test_i_collegamenti_interni_si_estraggono_senza_doppioni_e_in_ordine():
    testo = (
        "Vedi [[carta:maj-17]] e la [[stesa:croce-celtica]].\n"
        "Leggi anche [un articolo](/blog/come-leggere-i-tarocchi) o la [carta](https://tarots.chat/carte/maj-17).\n"
        "Non contano: [sezione](/blog/sezione/amore), [tag](/blog/tag/x), [fuori](https://esempio.it/carte/x) "
        "e [[carta:MAJ 17]].\n"
        "Di nuovo [[carta:maj-17]] e [[articolo:altro-articolo]]."
    )
    assert b.estrai_collegamenti(testo, host="tarots.chat") == [
        ("carta", "maj-17"),
        ("stesa", "croce-celtica"),
        ("articolo", "come-leggere-i-tarocchi"),
        ("articolo", "altro-articolo"),
    ]
    # Senza sapere quale sia il sito, i collegamenti assoluti non sono interni.
    assert ("carta", "x") not in b.estrai_collegamenti(testo) and ("carta", "maj-17") in b.estrai_collegamenti(testo)


def test_un_testo_senza_collegamenti_non_ne_ha():
    assert b.estrai_collegamenti("") == [] and b.estrai_collegamenti("solo testo") == []


# ---- immagini ------------------------------------------------------------------------------------


def _apri(webp):
    from PIL import Image

    return Image.open(io.BytesIO(webp))


@pytest.mark.parametrize("formato", ["PNG", "JPEG", "WEBP"])
def test_un_immagine_di_articolo_diventa_webp(formato):
    webp, w, h = b.prepara_immagine_articolo(_immagine(800, 600, formato))
    img = _apri(webp)
    assert img.format == "WEBP" and (w, h) == (800, 600) == img.size


def test_un_immagine_larga_si_riduce_a_1600_px_mantenendo_le_proporzioni():
    webp, w, h = b.prepara_immagine_articolo(_immagine(3200, 1800))
    assert (w, h) == (1600, 900) and _apri(webp).size == (1600, 900)


def test_la_trasparenza_si_conserva():
    webp, _, _ = b.prepara_immagine_articolo(_immagine(200, 200, "PNG", "RGBA", (10, 20, 30, 0)))
    assert _apri(webp).mode == "RGBA"


def test_l_avatar_e_un_quadrato_di_256_px_ritagliato_al_centro():
    webp, w, h = b.prepara_avatar(_immagine(900, 300))
    assert (w, h) == (256, 256) and _apri(webp).size == (256, 256)


@pytest.mark.parametrize("dati, motivo", [
    pytest.param(b"", "vuota", id="vuoto"),
    pytest.param(b"non un'immagine", "valida", id="testo"),
    pytest.param(_immagine(800, 600, "GIF"), "formato", id="gif"),
    pytest.param(_immagine(32, 32), "piccola", id="piccola"),
    pytest.param(_immagine(800, 600)[:-300], "danneggiata", id="troncata"),
    pytest.param(b"x" * (b.MAX_CARICO_IMMAGINE + 1), "grande", id="troppo-grande"),
])
def test_le_immagini_sbagliate_si_rifiutano(dati, motivo):
    with pytest.raises(b.ImmagineNonValida, match=motivo):
        b.prepara_immagine_articolo(dati)
    with pytest.raises(b.ImmagineNonValida, match=motivo):
        b.prepara_avatar(dati)


def test_i_metadati_non_passano():
    from PIL import Image

    img = Image.new("RGB", (400, 300), (10, 20, 30))
    exif = Image.Exif()
    exif[0x010F] = "Fotocamera segreta"
    uscita = io.BytesIO()
    img.save(uscita, format="JPEG", exif=exif)
    assert b"Fotocamera segreta" in uscita.getvalue()
    webp, _, _ = b.prepara_immagine_articolo(uscita.getvalue())
    assert b"Fotocamera segreta" not in webp
