"""La sintesi finale con Cache-Augmented Generation.

**Perché CAG e non RAG.** La base di conoscenza è piccola, stabile e tutta
rilevante: la dottrina di lettura, le cinque stese, il mazzo. Non serve
cercare i passaggi giusti — servono tutti — e ogni recupero sarebbe un punto
in cui un significato può andare perso. Si carica dunque l'intera conoscenza
nel contesto come **prefisso stabile**, identico byte per byte a ogni lettura,
e la si lascia in cache presso il fornitore: `cache_breakpoint_after`
diventa il `cache_control` di Anthropic, o il prefisso riusato dalla
KV-cache di un motore locale. Si paga una volta, poi costa quasi nulla.

Il prefisso contiene:

1. il ruolo e le regole del responso, compresi i guardrail;
2. la dottrina (`doctrine.md`);
3. le stese (`spreads.json`);
4. il mazzo intero, in forma compatta.

Dopo il confine di cache viene la parte variabile: domanda, quadro
dell'intervista, profilo, stesa, carte con posizione e orientamento, le
interpretazioni immediate già date, le dignità calcolate, le prevalenze e,
nella croce semplice, l'arcano di sintesi di Wirth. È su questa unione che il
modello fa inferenza.
"""
from __future__ import annotations

import json
from functools import lru_cache
from typing import Any, Dict, List, Optional

from .conoscenza import Conoscenza
from .testi import lingua

PROMPT_SINTESI = """# Compito: sintesi

Sei l'oracolo di T-AI-rots, lettore rigoroso e sapiente del Tarocco di Thoth di
Aleister Crowley. Hai davanti a te, qui sotto, tutta la conoscenza della
tradizione che applichi: la dottrina di lettura, le stese e il significato di
ogni carta del mazzo. Il tuo compito è il responso finale di una lettura.

Come costruire il responso:
- Unisci in un'unica inferenza coerente: il quesito, il quadro emerso
  dall'intervista, la stesa e il significato di ciascuna posizione, le carte
  con il loro orientamento, le dignità elementali, le prevalenze (Arcani
  maggiori, figure di corte, semi, numeri ripetuti) e le coppie di posizioni
  che la stesa prescrive di leggere insieme.
- Rispetta le regole della stesa scelta. Nella croce semplice il giudice è la
  risposta e la sintesi calcolata ne è il senso profondo; nella Croce Celtica
  leggi l'esito con corona e atteggiamento; nella ruota leggi il significatore
  e gli assi.
- Resta coerente con le interpretazioni immediate già date: approfondiscile e
  collegale, non contraddirle.
- Rispondi davvero al quesito, con chiarezza: indica la tendenza più probabile
  e perché le carte la mostrano.
- Tono: serio, caldo, rigoroso sul piano esoterico, mai teatrale. Seconda
  persona.
- Il futuro è la tendenza più probabile delle forze attuali, che le scelte di
  chi consulta possono cambiare: niente fatalismo, niente certezze assolute.

Formato (Markdown, 350-650 parole), esattamente queste sezioni:
## Il quadro
## Le forze in gioco
## Il consiglio delle carte
## La tendenza più probabile

Non aggiungere disclaimer: li aggiunge la piattaforma.
"""


def _mazzo_compatto(conoscenza: Conoscenza) -> str:
    righe = []
    for cid in conoscenza.ordine:
        c = conoscenza.carte[cid]
        s = c.get("significati") or {}
        righe.append(
            f"[{cid}] {c['nome_it']} / {c['nome_thoth']} — {c.get('elemento')}, "
            f"{c.get('astrologia')}. Chiavi: {', '.join(c.get('parole_chiave') or [])}. "
            f"Essoterico: {s.get('essoterico', '')} Iniziatico: {s.get('iniziatico', '')} "
            f"Ombra: {s.get('ombra', '')}"
        )
    return "\n".join(righe)


def _stese_compatte(conoscenza: Conoscenza) -> str:
    blocchi = []
    for s in conoscenza.stese.values():
        pos = "\n".join(
            f"  {p['n']}. {p['nome']}: {p['significato']}" for p in s["posizioni"]
        )
        regole = "\n".join(f"  - {r}" for r in s.get("regole", []))
        coppie = "\n".join(f"  - {a}–{b}: {t}" for a, b, t in s.get("coppie", []))
        blocchi.append(
            f"### {s['nome']} ({s['mazzo']})\n{s['descrizione']}\nPosizioni:\n{pos}\n"
            f"Regole:\n{regole}\nCoppie:\n{coppie}"
        )
    return "\n\n".join(blocchi)


@lru_cache(maxsize=4)
def _prefisso_cache(chiave: int, dottrina: str, stese: str, mazzo: str, guardie: str) -> str:
    return (
        f"{PROMPT_SINTESI}\n\n"
        f"# Regole di sicurezza del responso\n\n{guardie}\n\n"
        f"# Dottrina di lettura\n\n{dottrina}\n\n"
        f"# Le stese\n\n{stese}\n\n"
        f"# Il mazzo di Thoth (78 carte)\n\n{mazzo}\n"
    )


def prefisso(conoscenza: Conoscenza, istruzioni_guardrail: List[str]) -> str:
    """Il prefisso stabile. Deve restare byte-identico fra letture: nessun
    dato della lettura, nessuna data, nessun ordine che dipenda dal caso."""
    return _prefisso_cache(
        id(conoscenza),
        conoscenza.dottrina,
        _stese_compatte(conoscenza),
        _mazzo_compatto(conoscenza),
        "\n\n".join(istruzioni_guardrail),
    )


def parte_variabile(
    *,
    conoscenza: Conoscenza,
    stesa: Dict[str, Any],
    quesito: str,
    contesto: str,
    carte: List[Dict[str, Any]],
    dignita: Dict[int, Dict[str, Any]],
    prevalenze: Dict[str, Any],
    profilo: str = "",
    wirth: Optional[Dict[str, Any]] = None,
    vincoli: str = "",
    lang: str = "it",
) -> str:
    """La lettura concreta: tutto ciò che cambia da una consultazione all'altra.

    `carte` è l'elenco ordinato per posizione con `card_id`, `rovescio`,
    `posizione` e l'`interpretazione` immediata già data.
    """
    righe = [
        "# La lettura",
        f"Quesito: {quesito}",
        f"Quadro emerso dall'intervista: {contesto or 'non disponibile'}",
    ]
    if profilo:
        righe.append(f"Profilo di chi consulta:\n{profilo}")
    righe += ["", f"Stesa: {stesa['nome']}", "", "## Le carte"]
    for c in carte:
        carta = conoscenza.carta(c["card_id"])
        pos = conoscenza.posizione(stesa, c["posizione"])
        d = dignita.get(c["posizione"], {})
        righe.append(
            f"- Posizione {pos['n']} «{pos['nome']}» ({pos['significato']}): "
            f"{carta['nome_it']} [{carta['id']}], {'rovesciata' if c['rovescio'] else 'dritta'}"
            + (" — carta di sintesi calcolata" if c.get("calcolata") else "")
            + (f"; dignità: {d.get('giudizio')}" if d else "")
        )
        if c.get("interpretazione"):
            righe.append(f"  Interpretazione immediata già data: {c['interpretazione']}")
    righe += ["", "## Relazioni calcolate", "Dignità elementali per posizione:"]
    for n in sorted(dignita):
        d = dignita[n]
        rel = ", ".join(f"{r['posizione']}:{r['relazione']}" for r in d["relazioni"]) or "nessuna vicina"
        righe.append(f"- {n}: {d['elemento']}, {d['giudizio']} ({rel})")
    righe.append(f"Prevalenze: {json.dumps(prevalenze, ensure_ascii=False)}")
    if wirth:
        righe.append(
            f"Sintesi di Wirth: somma {wirth['somma']} → Arcano {wirth['numero']} "
            f"({wirth['nome']})" + (" — DOPPIA VALENZA: già presente nella stesa" if wirth.get("doppia_valenza") else "")
        )
    if vincoli:
        righe += ["", "## Correzioni richieste", vincoli]
    righe += ["", "Scrivi il responso in inglese." if lingua(lang) == "en" else "Scrivi il responso in italiano."]
    return "\n".join(righe)
