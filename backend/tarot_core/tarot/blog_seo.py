"""Il controllo SEO di un articolo: regole pure, senza database né rete.

Serve a tre cose: la console (un pannello che dice cosa migliorare mentre si scrive), la pubblicazione via REST
(`POST /v1/blog/seo-check` e il campo `seo` nella risposta di ogni salvataggio) e gli agenti che scrivono articoli,
che con quel punteggio sanno quando fermarsi. Ogni controllo ha un `id` stabile, un esito (`ok`, `avviso`, `errore`),
un messaggio in inglese e uno in italiano, e un peso: il punteggio è la somma pesata, da 0 a 100.

**Cosa non fa.** Non misura il posizionamento, la concorrenza né il volume di ricerca: non ha dati. Dice se l'articolo
rispetta le buone pratiche note (titolo e descrizione della giusta lunghezza, la parola chiave dove serve e non
ripetuta a sproposito, struttura a titoli, collegamenti, immagine con testo alternativo, domande frequenti).
Un 100 non promette il primo posto; un 40 dice dove cominciare.

Le soglie stanno in `SOGLIE` e sono le stesse che il sito applica alle sue pagine: titolo 30–60 caratteri,
descrizione 120–160, almeno 800 parole (300 il minimo), almeno due collegamenti interni.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from . import blog as regole

SOGLIE: Dict[str, int] = {
    "titolo_min": 30, "titolo_max": 60,
    "descrizione_min": 120, "descrizione_max": 160,
    "parole_minimo": 300, "parole_buono": 800,
    "slug_max": 75, "slug_parole_max": 9,
    "h2_minimo": 2, "collegamenti_interni_minimo": 2,
    "faq_minimo": 2, "etichette_minimo": 2, "etichette_massimo": 6,
    "densita_max_per_mille": 30,          # 3 %
    "frase_media_max": 24,
    "alt_minimo": 8,
    "primo_paragrafo_parole": 100,
}

#: Quante domande frequenti e quali forme sono accettate (anche nel salvataggio, non solo nel controllo).
FAQ_MAX = 10
FAQ_DOMANDA_MAX = 200
FAQ_RISPOSTA_MAX = 1200
PAROLE_CHIAVE_MAX = 10
PAROLA_CHIAVE_LUNGHEZZA = 60


class DatoSeoNonValido(ValueError):
    """Un campo SEO (FAQ, parole chiave, indirizzo canonico) che non si può salvare."""


# ---- pulizia dei campi (usata dal salvataggio) ----------------------------------------------------------------


def pulisci_parole_chiave(voci: Optional[Sequence[str]]) -> List[str]:
    """Le parole chiave secondarie: senza vuoti né doppioni (ignorando le maiuscole), al massimo dieci."""
    uscita: List[str] = []
    visti = set()
    for v in voci or []:
        testo = " ".join(str(v).split())[:PAROLA_CHIAVE_LUNGHEZZA]
        if testo and testo.lower() not in visti:
            visti.add(testo.lower())
            uscita.append(testo)
    return uscita[:PAROLE_CHIAVE_MAX]


def pulisci_faq(voci: Optional[Sequence[Any]]) -> List[Dict[str, str]]:
    """Le domande frequenti: `[{"domanda": …, "risposta": …}]`, senza voci incomplete, al massimo dieci."""
    uscita: List[Dict[str, str]] = []
    for v in voci or []:
        if isinstance(v, dict):
            d, r = v.get("domanda", v.get("d")), v.get("risposta", v.get("r"))
        else:
            d, r = getattr(v, "domanda", None), getattr(v, "risposta", None)
        d, r = " ".join(str(d or "").split()), " ".join(str(r or "").split())
        if not d or not r:
            continue
        if len(d) > FAQ_DOMANDA_MAX or len(r) > FAQ_RISPOSTA_MAX:
            raise DatoSeoNonValido(f"una domanda frequente è troppo lunga (domanda ≤ {FAQ_DOMANDA_MAX}, risposta ≤ {FAQ_RISPOSTA_MAX})")
        uscita.append({"domanda": d, "risposta": r})
    if len(uscita) > FAQ_MAX:
        raise DatoSeoNonValido(f"al massimo {FAQ_MAX} domande frequenti")
    return uscita


def valida_canonical(url: Optional[str]) -> Optional[str]:
    """L'indirizzo canonico, se c'è, dev'essere un URL `https` assoluto: niente `javascript:`, niente percorsi relativi."""
    if url is None or not url.strip():
        return None
    url = url.strip()
    if len(url) > 500 or not re.fullmatch(r"https://[^\s<>\"']+", url):
        raise DatoSeoNonValido("l'indirizzo canonico dev'essere un URL https assoluto")
    return url


# ---- il controllo ---------------------------------------------------------------------------------------------


@dataclass
class Controllo:
    id: str
    esito: str          # ok | avviso | errore
    peso: int
    en: str
    it: str
    dettaglio: Dict[str, Any] = field(default_factory=dict)

    def come_dizionario(self) -> Dict[str, Any]:
        return {"id": self.id, "esito": self.esito, "peso": self.peso, "messaggio": self.en, "messaggio_it": self.it,
                **({"dettaglio": self.dettaglio} if self.dettaglio else {})}


def _norm(testo: str) -> str:
    """Minuscole, senza accenti né punteggiatura, spazi singoli: per cercare una frase dentro un testo."""
    scomposto = unicodedata.normalize("NFKD", testo or "")
    senza = "".join(c for c in scomposto if not unicodedata.combining(c)).lower()
    return " ".join(re.sub(r"[^\w\s]", " ", senza).split())


def _parole(testo: str) -> List[str]:
    return _norm(testo).split()


def _primo_paragrafo(markdown: str, parole: int) -> str:
    """Le prime `parole` parole del corpo, saltando titoli, immagini e scorciatoie."""
    righe = [r for r in (markdown or "").splitlines() if r.strip() and not r.lstrip().startswith(("#", "!", "[["))]
    return " ".join(" ".join(righe).split()[:parole])


def _titoli_h2(markdown: str) -> List[str]:
    return [m.group(1).strip() for m in re.finditer(r"^##\s+(.+?)\s*$", markdown or "", flags=re.M)]


def _collegamenti(markdown: str, host: Optional[str]) -> Dict[str, int]:
    interni = len(regole.estrai_collegamenti(markdown or "", host=host))
    esterni = 0
    for m in re.finditer(r"(?<!!)\[[^\]]*\]\((https?://[^)\s]+)", markdown or ""):
        url = m.group(1)
        if host and re.match(rf"https?://(www\.)?{re.escape(host)}(/|$)", url):
            continue
        esterni += 1
    return {"interni": interni, "esterni": esterni}


def _frase_media(testo: str) -> float:
    frasi = [f for f in re.split(r"[.!?]+\s+|\n{2,}", regole.testo_semplice(testo)) if len(f.split()) >= 2]
    if not frasi:
        return 0.0
    return sum(len(f.split()) for f in frasi) / len(frasi)


def analizza(
    *, titolo: str, testo: str, slug: str = "", sottotitolo: Optional[str] = None, seo_titolo: Optional[str] = None,
    seo_descrizione: Optional[str] = None, parola_chiave: Optional[str] = None,
    immagine_presente: bool = False, immagine_alt: Optional[str] = None,
    tags: Sequence[str] = (), faq: Sequence[Any] = (), host: Optional[str] = None,
) -> Dict[str, Any]:
    """Il rapporto SEO di un articolo: `{punteggio, giudizio, controlli[], statistiche{}, suggerimenti[]}`."""
    S = SOGLIE
    controlli: List[Controllo] = []

    def aggiungi(id_: str, esito: str, peso: int, en: str, it: str, **dettaglio: Any) -> None:
        controlli.append(Controllo(id_, esito, peso, en, it, dettaglio))

    titolo_seo = (seo_titolo or titolo or "").strip()
    descrizione = (seo_descrizione or "").strip()
    chiave = (parola_chiave or "").strip()
    k = _norm(chiave)
    corpo_parole = regole.testo_semplice(testo).split()
    n_parole = len(corpo_parole)
    primo = _primo_paragrafo(testo, S["primo_paragrafo_parole"])
    h2 = _titoli_h2(testo)
    coll = _collegamenti(testo, host)

    # -- titolo
    n = len(titolo_seo)
    if not n:
        aggiungi("titolo_seo", "errore", 2, "The title is missing.", "Manca il titolo.")
    elif S["titolo_min"] <= n <= S["titolo_max"]:
        aggiungi("titolo_seo", "ok", 2, f"The SEO title is {n} characters: it fits a search result.", f"Il titolo SEO è di {n} caratteri: sta in un risultato di ricerca.", caratteri=n)
    else:
        aggiungi("titolo_seo", "avviso", 2,
                 f"The SEO title is {n} characters; aim for {S['titolo_min']}–{S['titolo_max']} so it is neither thin nor cut off.",
                 f"Il titolo SEO è di {n} caratteri; punta a {S['titolo_min']}–{S['titolo_max']}, così non è povero né tagliato.", caratteri=n)

    # -- descrizione
    n = len(descrizione)
    if not n:
        aggiungi("descrizione_seo", "errore", 2, "There is no SEO description: search engines will invent one from the text.",
                 "Manca la descrizione SEO: i motori di ricerca ne ricaveranno una dal testo.")
    elif S["descrizione_min"] <= n <= S["descrizione_max"]:
        aggiungi("descrizione_seo", "ok", 2, f"The SEO description is {n} characters.", f"La descrizione SEO è di {n} caratteri.", caratteri=n)
    else:
        aggiungi("descrizione_seo", "avviso", 2,
                 f"The SEO description is {n} characters; aim for {S['descrizione_min']}–{S['descrizione_max']}.",
                 f"La descrizione SEO è di {n} caratteri; punta a {S['descrizione_min']}–{S['descrizione_max']}.", caratteri=n)

    # -- parola chiave
    if not k:
        aggiungi("parola_chiave", "errore", 3, "No primary keyword is set: choose one phrase this article should rank for.",
                 "Manca la parola chiave principale: scegli la frase per cui l'articolo deve farsi trovare.")
    else:
        aggiungi("parola_chiave", "ok", 1, f"Primary keyword: “{chiave}”.", f"Parola chiave principale: «{chiave}».")
        for id_, dove, peso, presente, en, it in (
            ("chiave_nel_titolo", "title", 3, k in _norm(titolo_seo), "in the SEO title", "nel titolo SEO"),
            ("chiave_nella_descrizione", "description", 2, k in _norm(descrizione), "in the SEO description", "nella descrizione SEO"),
            ("chiave_nello_slug", "slug", 1, regole.slugify(chiave) in (slug or ""), "in the URL slug", "nello slug"),
            ("chiave_nell_inizio", "start", 2, k in _norm(primo), f"in the first {S['primo_paragrafo_parole']} words", f"nelle prime {S['primo_paragrafo_parole']} parole"),
            ("chiave_in_un_h2", "h2", 1, any(k in _norm(t) for t in h2), "in at least one H2 heading", "in almeno un titolo H2"),
            ("chiave_nell_alt", "alt", 1, k in _norm(immagine_alt or ""), "in the image alt text", "nel testo alternativo dell'immagine"),
        ):
            aggiungi(id_, "ok" if presente else "avviso", peso,
                     f"The keyword appears {en}." if presente else f"The keyword does not appear {en}.",
                     f"La parola chiave compare {it}." if presente else f"La parola chiave non compare {it}.")
        # densità: quante volte, in ogni mille parole (la frase intera; mai più del 3 %)
        conteggio = _norm(regole.testo_semplice(testo)).count(k) if k else 0
        per_mille = round(1000 * conteggio * max(len(k.split()), 1) / max(n_parole, 1), 1)
        if conteggio == 0:
            aggiungi("densita", "avviso", 1, "The keyword never appears in the body text.", "La parola chiave non compare mai nel testo.", per_mille=0)
        elif per_mille > S["densita_max_per_mille"]:
            aggiungi("densita", "avviso", 1, f"The keyword is repeated too often ({per_mille}‰ of the words): it reads as stuffing.",
                     f"La parola chiave è ripetuta troppo ({per_mille}‰ delle parole): sembra forzata.", per_mille=per_mille)
        else:
            aggiungi("densita", "ok", 1, f"Keyword density is natural ({per_mille}‰).", f"La densità della parola chiave è naturale ({per_mille}‰).", per_mille=per_mille)

    # -- lunghezza e struttura
    if n_parole < S["parole_minimo"]:
        aggiungi("lunghezza", "errore", 3, f"The article has {n_parole} words: too thin to rank (aim for {S['parole_buono']}+).",
                 f"L'articolo ha {n_parole} parole: troppo poco per posizionarsi (punta a {S['parole_buono']}+).", parole=n_parole)
    elif n_parole < S["parole_buono"]:
        aggiungi("lunghezza", "avviso", 3, f"The article has {n_parole} words; {S['parole_buono']}+ usually covers a topic in depth.",
                 f"L'articolo ha {n_parole} parole; da {S['parole_buono']} in su di solito un tema è coperto a fondo.", parole=n_parole)
    else:
        aggiungi("lunghezza", "ok", 3, f"The article has {n_parole} words.", f"L'articolo ha {n_parole} parole.", parole=n_parole)

    aggiungi("titoli_h2", "ok" if len(h2) >= S["h2_minimo"] else "avviso", 1,
             f"The text has {len(h2)} H2 heading(s)." + ("" if len(h2) >= S["h2_minimo"] else f" Structure it with at least {S['h2_minimo']}."),
             f"Il testo ha {len(h2)} titolo/i H2." + ("" if len(h2) >= S["h2_minimo"] else f" Strutturalo con almeno {S['h2_minimo']}."), h2=len(h2))
    if re.search(r"^#\s+\S", testo or "", flags=re.M):
        aggiungi("h1_nel_testo", "avviso", 1, "The body has an H1 (`# …`): the page title is already the H1, use `##` for sections.",
                 "Il testo ha un H1 (`# …`): il titolo della pagina è già l'H1, usa `##` per le sezioni.")

    frase = _frase_media(testo)
    aggiungi("frasi", "ok" if 0 < frase <= S["frase_media_max"] else "avviso", 1,
             f"Sentences average {frase:.0f} words." + ("" if frase <= S["frase_media_max"] else f" Shorter sentences (≤ {S['frase_media_max']}) read better."),
             f"Le frasi hanno in media {frase:.0f} parole." + ("" if frase <= S["frase_media_max"] else f" Frasi più corte (≤ {S['frase_media_max']}) si leggono meglio."), parole_per_frase=round(frase, 1))

    # -- collegamenti
    aggiungi("collegamenti_interni", "ok" if coll["interni"] >= S["collegamenti_interni_minimo"] else "avviso", 2,
             f"{coll['interni']} internal link(s) to cards, spreads or other articles." + ("" if coll["interni"] >= S["collegamenti_interni_minimo"] else f" Add at least {S['collegamenti_interni_minimo']} (`[[card:the-star]]`, `[[spread:celtic-cross]]`, `[[post:slug]]`)."),
             f"{coll['interni']} collegamento/i interno/i a carte, stese o altri articoli." + ("" if coll["interni"] >= S["collegamenti_interni_minimo"] else f" Aggiungine almeno {S['collegamenti_interni_minimo']} (`[[carta:maj-17]]`, `[[stesa:croce-celtica]]`, `[[articolo:slug]]`)."), interni=coll["interni"])
    aggiungi("collegamenti_esterni", "ok" if coll["esterni"] >= 1 else "avviso", 1,
             f"{coll['esterni']} external link(s)." + ("" if coll["esterni"] else " Cite at least one reputable source."),
             f"{coll['esterni']} collegamento/i esterno/i." + ("" if coll["esterni"] else " Cita almeno una fonte autorevole."), esterni=coll["esterni"])

    # -- immagine, etichette, domande
    if not immagine_presente:
        aggiungi("immagine", "avviso", 1, "No cover image: articles with an image are shared and clicked more.", "Nessuna immagine di copertina: gli articoli con un'immagine si condividono e si aprono di più.")
    elif len((immagine_alt or "").strip()) < S["alt_minimo"]:
        aggiungi("immagine", "avviso", 1, "The cover image has no useful alt text: describe what it shows.", "L'immagine di copertina non ha un testo alternativo utile: descrivi cosa mostra.")
    else:
        aggiungi("immagine", "ok", 1, "Cover image with alt text.", "Immagine di copertina con testo alternativo.")

    n_tag = len(tags)
    aggiungi("etichette", "ok" if S["etichette_minimo"] <= n_tag <= S["etichette_massimo"] else "avviso", 1,
             f"{n_tag} tag(s)." + ("" if S["etichette_minimo"] <= n_tag <= S["etichette_massimo"] else f" Use {S['etichette_minimo']}–{S['etichette_massimo']}."),
             f"{n_tag} etichetta/e." + ("" if S["etichette_minimo"] <= n_tag <= S["etichette_massimo"] else f" Usane {S['etichette_minimo']}–{S['etichette_massimo']}."), etichette=n_tag)

    n_faq = len(pulisci_faq(faq)) if faq else 0
    aggiungi("faq", "ok" if n_faq >= S["faq_minimo"] else "avviso", 1,
             f"{n_faq} frequently asked question(s): they become FAQ structured data." + ("" if n_faq >= S["faq_minimo"] else " Add 3–5 real questions with short answers."),
             f"{n_faq} domanda/e frequente/i: diventano dati strutturati FAQ." + ("" if n_faq >= S["faq_minimo"] else " Aggiungi 3–5 domande vere con risposte brevi."), faq=n_faq)

    n_slug = len(slug or "")
    parole_slug = len([p for p in (slug or "").split("-") if p])
    if not slug:
        pass  # lo slug non c'è ancora (articolo non salvato): non si giudica
    else:
        buono = n_slug <= S["slug_max"] and parole_slug <= S["slug_parole_max"]
        aggiungi("slug", "ok" if buono else "avviso", 1,
                 f"The slug has {parole_slug} words." + ("" if buono else f" Shorten it (≤ {S['slug_parole_max']} words, ≤ {S['slug_max']} characters)."),
                 f"Lo slug ha {parole_slug} parole." + ("" if buono else f" Accorcialo (≤ {S['slug_parole_max']} parole, ≤ {S['slug_max']} caratteri)."), caratteri=n_slug)

    # -- il punteggio
    totale = sum(c.peso for c in controlli) or 1
    ottenuto = sum(c.peso * (1.0 if c.esito == "ok" else 0.5 if c.esito == "avviso" else 0.0) for c in controlli)
    punteggio = round(100 * ottenuto / totale)
    giudizio = "ottimo" if punteggio >= 85 and not any(c.esito == "errore" for c in controlli) else "buono" if punteggio >= 65 else "da_migliorare"
    return {
        "punteggio": punteggio,
        "giudizio": giudizio,
        "controlli": [c.come_dizionario() for c in controlli],
        "suggerimenti": [c.en for c in controlli if c.esito != "ok"],
        "suggerimenti_it": [c.it for c in controlli if c.esito != "ok"],
        "statistiche": {
            "parole": n_parole, "titoli_h2": len(h2), "collegamenti_interni": coll["interni"],
            "collegamenti_esterni": coll["esterni"], "faq": n_faq, "tempo_lettura": regole.tempo_lettura(testo),
        },
    }
