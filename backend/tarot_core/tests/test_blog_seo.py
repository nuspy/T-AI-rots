"""Il controllo SEO degli articoli: regole pure, senza database né rete."""
from __future__ import annotations

import pytest

from tarot_core.auth.chiavi import LUNGHEZZA_PREFISSO, PREFISSO_CHIAVE, genera_chiave, impronta
from tarot_core.tarot import blog_seo as s

PARAGRAFO = (
    "The Star tarot card speaks of hope after a crisis. In the Thoth Tarot the Star follows the Tower, and it asks you "
    "to trust the direction you have already chosen. Read it as an invitation to rest, to heal and to look up. "
)


def _testo_lungo(parole=900, chiave="star tarot card meaning") -> str:
    intro = f"The {chiave} is the first thing people search for. " + PARAGRAFO
    corpo = "\n\n".join(
        f"## {t}\n\n{PARAGRAFO * 3}" for t in (f"What is the {chiave}?", "The Star in love", "The Star at work")
    )
    fine = "\n\nSee [[card:the-star]] and [[spread:celtic-cross]], and the [Golden Dawn](https://en.wikipedia.org/wiki/Golden_Dawn)."
    testo = intro + "\n\n" + corpo + fine
    while len(testo.split()) < parole:
        testo += "\n\n" + PARAGRAFO * 3
    return testo


def _analizza(**cambia):
    base = dict(
        titolo="The Star Tarot Card Meaning: Hope and Healing",
        testo=_testo_lungo(),
        slug="the-star-tarot-card-meaning",
        seo_titolo="The Star Tarot Card Meaning: Hope and Healing",
        seo_descrizione="The Star tarot card meaning in the Thoth Tarot: hope, healing and renewal, upright and reversed, in love and at work, with its Hebrew letter.",
        parola_chiave="star tarot card meaning",
        immagine_presente=True,
        immagine_alt="The Star tarot card meaning shown on a dark background",
        tags=["Thoth Tarot", "Major Arcana", "Hope"],
        faq=[{"domanda": "What does the Star mean?", "risposta": "Hope."}, {"domanda": "Is it a good card?", "risposta": "Yes."}],
    )
    base.update(cambia)
    return s.analizza(**base)


def _esito(rapporto, id_):
    return next(c["esito"] for c in rapporto["controlli"] if c["id"] == id_)


def test_un_articolo_curato_prende_un_punteggio_alto():
    r = _analizza()
    assert r["punteggio"] >= 85 and r["giudizio"] == "ottimo", (r["punteggio"], r["suggerimenti"])
    assert r["statistiche"]["parole"] >= 800 and r["statistiche"]["titoli_h2"] == 3
    assert r["statistiche"]["collegamenti_interni"] == 2 and r["statistiche"]["collegamenti_esterni"] == 1


def test_senza_parola_chiave_e_un_errore_e_i_controlli_sulla_parola_chiave_non_ci_sono():
    r = _analizza(parola_chiave=None)
    assert _esito(r, "parola_chiave") == "errore"
    assert not any(c["id"].startswith("chiave_") for c in r["controlli"])
    assert r["giudizio"] != "ottimo"


@pytest.mark.parametrize("titolo, esito", [("Corto", "avviso"), ("x" * 61, "avviso"), ("Un titolo che sta nei sessanta caratteri, ecco", "ok"), ("", "errore")])
def test_il_titolo_seo_ha_la_lunghezza_giusta(titolo, esito):
    assert _esito(_analizza(titolo=titolo, seo_titolo=None), "titolo_seo") == esito


def test_la_descrizione_manca_o_e_fuori_misura():
    assert _esito(_analizza(seo_descrizione=None), "descrizione_seo") == "errore"
    assert _esito(_analizza(seo_descrizione="Troppo breve."), "descrizione_seo") == "avviso"
    assert _esito(_analizza(seo_descrizione="x " * 100), "descrizione_seo") == "avviso"


def test_un_testo_corto_e_un_errore_uno_medio_un_avviso():
    assert _esito(_analizza(testo="Poche parole."), "lunghezza") == "errore"
    assert _esito(_analizza(testo=_testo_lungo(500)[: 500 * 8]), "lunghezza") in ("avviso", "errore")


def test_la_parola_chiave_ripetuta_troppo_sembra_forzata():
    stufo = ("star tarot card meaning " * 200) + "\n\n## star tarot card meaning\n\n" + _testo_lungo()
    assert _esito(_analizza(testo=stufo), "densita") == "avviso"


def test_gli_accenti_e_le_maiuscole_non_contano_nel_confronto():
    r = _analizza(parola_chiave="Più Città", titolo="Più città: guida", seo_titolo="Più città: guida", testo="## piu citta\n\nPiù città qui. " + _testo_lungo())
    assert _esito(r, "chiave_nel_titolo") == "ok" and _esito(r, "chiave_in_un_h2") == "ok"


def test_i_collegamenti_interni_e_esterni_si_contano_una_volta_sola():
    testo = "[[card:the-star]] [[carta:maj-17]] [Stars](/cards/the-star) [Altro](https://tarots.chat/blog/x) [Fonte](https://example.org/a)"
    r = _analizza(testo=testo + "\n\n" + _testo_lungo(), host="tarots.chat")
    # the-star e maj-17 sono due scritture della stessa carta: nel controllo restano due voci grezze (la risoluzione
    # a id canonico avviene al salvataggio); il blog interno assoluto conta come interno, la fonte come esterna.
    assert r["statistiche"]["collegamenti_interni"] >= 3 and r["statistiche"]["collegamenti_esterni"] >= 2


def test_un_h1_nel_testo_e_segnalato():
    assert any(c["id"] == "h1_nel_testo" for c in _analizza(testo="# Titolo\n\n" + _testo_lungo())["controlli"])


def test_senza_slug_non_si_giudica_lo_slug():
    assert not any(c["id"] == "slug" for c in _analizza(slug="")["controlli"])
    assert _esito(_analizza(slug="a-" * 40), "slug") == "avviso"


def test_il_rapporto_ha_i_messaggi_in_due_lingue_e_i_suggerimenti_solo_per_cio_che_non_va():
    r = _analizza(faq=[], tags=[])
    assert r["suggerimenti"] and len(r["suggerimenti"]) == len(r["suggerimenti_it"])
    assert all("messaggio" in c and "messaggio_it" in c for c in r["controlli"])
    assert all(c["esito"] != "ok" for c in r["controlli"] if c["messaggio"] in r["suggerimenti"])


# ---- pulizia dei campi ----------------------------------------------------------------------------------------


def test_le_parole_chiave_secondarie_si_puliscono():
    assert s.pulisci_parole_chiave(["  Thoth  Tarot ", "thoth tarot", "", "a" * 90] + [f"k{i}" for i in range(20)]) == (
        ["Thoth Tarot", "a" * 60] + [f"k{i}" for i in range(8)]
    )
    assert s.pulisci_parole_chiave(None) == []


def test_le_faq_incomplete_si_scartano_e_quelle_troppo_lunghe_o_troppe_no():
    assert s.pulisci_faq([{"domanda": "D?", "risposta": "R."}, {"domanda": "Solo domanda"}, {"d": "Breve?", "r": "Sì."}]) == [
        {"domanda": "D?", "risposta": "R."}, {"domanda": "Breve?", "risposta": "Sì."},
    ]
    with pytest.raises(s.DatoSeoNonValido):
        s.pulisci_faq([{"domanda": "D?", "risposta": "x" * (s.FAQ_RISPOSTA_MAX + 1)}])
    with pytest.raises(s.DatoSeoNonValido):
        s.pulisci_faq([{"domanda": f"D{i}?", "risposta": "R."} for i in range(s.FAQ_MAX + 1)])


@pytest.mark.parametrize("url", ["http://esempio.it/a", "javascript:alert(1)", "/relativo", "https://a b", "https://x/" + "a" * 500])
def test_l_indirizzo_canonico_dev_essere_https_assoluto(url):
    with pytest.raises(s.DatoSeoNonValido):
        s.valida_canonical(url)


def test_l_indirizzo_canonico_valido_passa_e_il_vuoto_e_nessuno():
    assert s.valida_canonical("https://esempio.it/articolo?a=1") == "https://esempio.it/articolo?a=1"
    assert s.valida_canonical("  ") is None and s.valida_canonical(None) is None


# ---- le chiavi -------------------------------------------------------------------------------------------------


def test_una_chiave_ha_prefisso_e_impronta_e_non_si_ripete():
    chiave, prefisso, imp = genera_chiave()
    assert chiave.startswith(PREFISSO_CHIAVE) and len(chiave) >= 40
    assert prefisso == chiave[:LUNGHEZZA_PREFISSO] and imp == impronta(chiave) and len(imp) == 64
    assert chiave not in imp and genera_chiave()[0] != chiave


def test_il_freno_alle_richieste_conta_per_chiave_e_ripulisce_la_finestra():
    from tarot_core.auth import chiavi

    chiavi.azzera_limiti()
    assert [chiavi._entro_il_limite(1, 2, t) for t in (0.0, 1.0)] == [0.0, 0.0]
    attesa = chiavi._entro_il_limite(1, 2, 2.0)
    assert 55 <= attesa <= 60                       # la terza richiesta deve aspettare
    assert chiavi._entro_il_limite(2, 2, 2.0) == 0  # un'altra chiave non c'entra
    assert chiavi._entro_il_limite(1, 2, 62.0) == 0  # passato un minuto si riparte
    chiavi.azzera_limiti()
