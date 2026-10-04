"""La traduzione dei testi di una notifica con l'LLM (v9, Fase 5), sul modello di `tarot/traduzione_blog.py`.

Solo su richiesta dalla console («Traduci»), e il risultato torna nella bozza della campagna (o dell'automatica): una
persona lo rilegge prima di mandarlo. Si usa il compito del modello già assegnato alla traduzione degli articoli
(`Compito.TRADUZIONE_ARTICOLO`): è lo stesso lavoro, più corto. Nelle prove risponde sempre il modello finto.

Le regole per il modello: testo breve (una notifica si legge in due secondi), il «tu» in tutte le lingue (anche in
russo e in ucraino, `ты`/`ти`), i segnaposto `{n}`, `{data}`… intatti, nessuna promessa sul futuro.
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Mapping

from ..llm.base import GenerationError
from ..tarot.lingue import nome_per_prompt
from ..tarot.llm import genera_json, richiesta

PROMPT_SISTEMA = """# Compito: traduzione_notifica

Sei un traduttore professionista per un'app di tarocchi (TAROTS chat). Traduci il titolo e il testo di una notifica
push dalla lingua di partenza ({base}) in ciascuna delle lingue richieste: {lingue}.

Regole:
- breve e naturale come una notifica scritta da una persona di madrelingua: il titolo al massimo 60 caratteri, il
  testo al massimo 180;
- dai del «tu» a chi legge in tutte le lingue (in russo «ты», in ucraino «ти»), con un tono caldo e misurato;
- lascia **intatti** i segnaposto fra graffe ({{n}}, {{data}}, {{piano}}…) e il nome «TAROTS chat»;
- nessuna promessa sul futuro, nessuna parola che metta fretta in modo ingannevole;
- non aggiungere né togliere informazioni.

Rispondi in JSON con una chiave per lingua (il codice ISO), ciascuna con "titolo" e "corpo":
{{"en": {{"titolo": "...", "corpo": "..."}}, ...}}. Nessun testo prima o dopo il JSON."""


class TraduzioneNonRiuscita(RuntimeError):
    """Il modello non ha dato una traduzione utilizzabile: chi chiama lo dice all'operatore."""


def _segnaposto(testo: str) -> List[str]:
    return sorted(re.findall(r"\{\w+\}", testo or ""))


async def traduci(provider: Any, base: str, testo: Mapping[str, str], lingue: List[str]) -> Dict[str, Dict[str, str]]:
    """`{lingua: {"titolo", "corpo"}}` per ciascuna delle `lingue`. Solleva `TraduzioneNonRiuscita`."""
    lingue = [x for x in dict.fromkeys(lingue) if x != base]
    if not lingue:
        return {}
    titolo, corpo = (testo.get("titolo") or "").strip(), (testo.get("corpo") or "").strip()
    if not titolo or not corpo:
        raise TraduzioneNonRiuscita("Scrivi prima titolo e testo nella lingua di partenza.")
    r = richiesta(
        [PROMPT_SISTEMA.format(base=nome_per_prompt(base), lingue=", ".join(f"{x} ({nome_per_prompt(x)})" for x in lingue))],
        json.dumps({"lingua": base, "titolo": titolo, "corpo": corpo, "lingue": lingue}, ensure_ascii=False),
        temperatura=0.3, max_tokens=2048,
    )
    try:
        dati = await genera_json(provider, r)
    except GenerationError as exc:
        raise TraduzioneNonRiuscita(str(exc)) from exc
    attesi = _segnaposto(titolo + " " + corpo)
    risultato: Dict[str, Dict[str, str]] = {}
    for lingua in lingue:
        voce = dati.get(lingua) if isinstance(dati, dict) else None
        if not isinstance(voce, dict) or not str(voce.get("titolo") or "").strip() or not str(voce.get("corpo") or "").strip():
            raise TraduzioneNonRiuscita(f"Manca la traduzione in {lingua}: riprova.")
        t, c = str(voce["titolo"]).strip()[:120], str(voce["corpo"]).strip()[:400]
        if _segnaposto(t + " " + c) != attesi:
            raise TraduzioneNonRiuscita(f"La traduzione in {lingua} ha cambiato i segnaposto fra graffe: riprova.")
        risultato[lingua] = {"titolo": t, "corpo": c}
    return risultato
