"""Traduzione automatica di un articolo del blog in un'altra lingua (v5, fase E).

Non gira durante una lettura: solo su richiesta esplicita dalla console (`admin_blog.py`), e il
risultato è **sempre** salvato come bozza — mai pubblicato da solo. L'output di un modello, per quanto
buono, resta un contenuto pubblico: qualcuno deve poterlo rileggere prima che vada online, esattamente
come si tratta ogni altro contenuto scritto in questo progetto.

Solo contenuto, non nuove pagine indicizzate: la traduzione si serve con `?lang=` sulle URL it/en già
esistenti (come i nomi di carte e stese in `knowledge/nomi.json`), non su una nuova route per lingua —
estendere il sito a instradare N lingue è un lavoro molto più grande, volutamente fuori da questa fase.

Il corpo tradotto passa di nuovo da `estrai_collegamenti()` (fuori da questo modulo, a cura di chi
chiama, tramite `BlogRepository.salva()`): le scorciatoie `[[card:...]]`/`[[spread:...]]`/
`[[post:...]]`/`[[video:...]]` non si traducono — il modello ha solo l'istruzione di lasciarle
intatte — ma restano comunque verificate come per un articolo scritto a mano.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List

from ..llm.base import GenerationError
from .lingue import nome_per_prompt
from .llm import genera_json, richiesta

CAMPI_RICHIESTI = ("titolo", "testo", "seo_titolo", "seo_descrizione")

PROMPT_SISTEMA = """# Compito: traduzione di un articolo del blog

Sei un traduttore professionista specializzato in tarocchi, Tarocco di Thoth, Golden Dawn ed
esoterismo. Traduci l'articolo che segue nella sua lingua originale in {lingua}, mantenendo:

- il significato e il tono (riflessivo, non profetico: mai promesse sul futuro, mai un verdetto su una
  persona o una coppia);
- la struttura Markdown esatta (stessi titoli `##`, stesse liste, stessa punteggiatura strutturale);
- le scorciatoie interne `[[card:...]]`, `[[spread:...]]`, `[[post:...]]`, `[[video:...]]` **intatte,
  senza tradurre né la parola chiave prima dei due punti né l'identificatore dopo** — sono riferimenti
  tecnici, non prosa;
- i nomi propri e i termini tecnici (Crowley, Harris, Golden Dawn, Kaph, Netzach…) nella forma con cui
  la tradizione li conosce in {lingua}, se ne esiste una consolidata, altrimenti come nell'originale.

Non aggiungere contenuto, non toglierne, non correggere presunti errori: è una traduzione, non una
riscrittura né una revisione.

Rispondi in JSON con esattamente questi campi, tutti tradotti:
{{"titolo": "...", "sottotitolo": "... oppure null", "testo": "...", "seo_titolo": "...",
"seo_descrizione": "...", "immagine_alt": "... oppure null",
"faq": [{{"domanda": "...", "risposta": "..."}}, ...]}}

Il numero di elementi in "faq" deve restare identico all'originale, tradotti uno a uno nello stesso
ordine. Nessun testo prima o dopo il JSON."""


class TraduzioneNonRiuscita(RuntimeError):
    """Il modello non ha restituito una traduzione utilizzabile (campo mancante, FAQ spaiate, JSON
    non interpretabile). Chi chiama lo dice all'amministratore: non esiste una traduzione di riserva
    da salvare al posto suo."""


def _prompt_utente(post: Any) -> str:
    faq_originale: List[Dict[str, str]] = list(post.faq or [])
    return json.dumps(
        {
            "titolo": post.titolo,
            "sottotitolo": post.sottotitolo,
            "testo": post.testo,
            "seo_titolo": post.seo_titolo,
            "seo_descrizione": post.seo_descrizione,
            "immagine_alt": post.immagine_alt,
            "faq": [{"domanda": f.get("domanda", ""), "risposta": f.get("risposta", "")} for f in faq_originale],
        },
        ensure_ascii=False,
    )


async def traduci_articolo(provider: Any, post: Any, lingua_destinazione: str) -> Dict[str, Any]:
    """Traduce titolo/sottotitolo/corpo/campi SEO/FAQ di `post` in `lingua_destinazione`.

    Non tocca il database: restituisce solo i campi tradotti, pronti per un nuovo `BlogPost` (via
    `BlogRepository.salva(None, {**tradotto, "lang": lingua_destinazione, "tradotto_da_id": post.id,
    "stato": "bozza"}, ...)`). Chi chiama decide se, quando e con quale titolo di sezione/tag salvarlo.
    """
    faq_originale: List[Dict[str, str]] = list(post.faq or [])
    richiesta_llm = richiesta(
        [PROMPT_SISTEMA.format(lingua=nome_per_prompt(lingua_destinazione))],
        _prompt_utente(post),
        temperatura=0.3,
        max_tokens=8192,
    )
    try:
        dati = await genera_json(provider, richiesta_llm)
    except GenerationError as exc:
        raise TraduzioneNonRiuscita(str(exc)) from exc

    mancanti = [c for c in CAMPI_RICHIESTI if not dati.get(c)]
    if mancanti:
        raise TraduzioneNonRiuscita(f"campi mancanti nella traduzione: {', '.join(mancanti)}")
    faq_tradotta = dati.get("faq")
    if not isinstance(faq_tradotta, list) or len(faq_tradotta) != len(faq_originale):
        raise TraduzioneNonRiuscita(
            f"la traduzione ha {len(faq_tradotta) if isinstance(faq_tradotta, list) else 'zero'} "
            f"FAQ, l'originale ne ha {len(faq_originale)}",
        )

    return {
        "titolo": dati["titolo"],
        "sottotitolo": dati.get("sottotitolo") or None,
        "testo": dati["testo"],
        "seo_titolo": dati["seo_titolo"],
        "seo_descrizione": dati["seo_descrizione"],
        "immagine_alt": dati.get("immagine_alt") or None,
        "faq": faq_tradotta,
    }
