"""La sintesi finale: dottrina in cache, e solo i dati della lettura.

**Cosa sta nel prefisso e cosa no.** Il prefisso stabile — identico byte per
byte a ogni lettura, quindi riusabile dalla cache del fornitore
(`cache_breakpoint_after` diventa il `cache_control` di Anthropic, o il prefisso
riusato dalla KV-cache di un motore locale) — contiene soltanto:

1. il ruolo e le regole del responso;
2. le regole di sicurezza (i guardrail);
3. la dottrina di lettura (`doctrine.md`).

**Non contiene le stese né il mazzo.** Prima ci stavano tutte e cinque le
stese e tutte le 78 carte, di cui una lettura ne usa una e dieci: il resto era
rumore che costava token e dava al modello l'occasione di confondere una
posizione con un'altra. Ora è il codice a scegliere: dopo il confine di cache
il messaggio porta solo

- la stesa scelta, con le sue regole e le sue coppie di posizioni;
- le carte estratte, ciascuna con la sua posizione, l'orientamento e la scheda
  per *quell'orientamento* (`schede.scheda`), la dignità e l'interpretazione
  immediata già data;
- l'**ordine del racconto**: le tappe della stesa nella sequenza in cui si
  leggono, con il valore di ogni carta in quella posa in una frase, perché il
  modello le colleghi in una storia;
- domanda, colloquio, profilo, prevalenze e, nella croce semplice, l'arcano di
  sintesi di Wirth.

Il costo è un prefisso più piccolo e un messaggio più mirato; con il traffico
di un servizio piccolo la cache scade spesso, e scrivere in cache 18 mila token
per ogni lettura costava più di passarne poche migliaia già scelte.
"""
from __future__ import annotations

import json
from functools import lru_cache
from typing import Any, Dict, List, Optional

from .conoscenza import Conoscenza
from .lingue import istruzione_lingua, lingua
from .schede import scheda, valore_sintetico

PROMPT_SINTESI = """# Compito: sintesi

Sei l'oracolo di T-AI-rots, lettore rigoroso e sapiente del Tarocco di Thoth di
Aleister Crowley. Qui sotto hai la dottrina di lettura della tradizione che
applichi. Nel messaggio trovi la lettura da concludere: il sistema ha già scelto
e ti passa solo ciò che serve — la stesa scelta con le sue regole, le sole carte
estratte (ognuna con la sua posizione e con il significato del suo orientamento,
dritta o rovesciata) e l'ordine in cui raccontarle. Usa solo quei dati: non
aggiungere significati di carte che non sono uscite né di posizioni che non
fanno parte della stesa.

Come costruire il responso:
- Costruiscilo come UNA STORIA con un filo. Segui l'«Ordine del racconto» del
  messaggio: ogni tappa è una posizione, con la sua carta e il suo valore in
  quella posa. Collega ogni tappa alla successiva con un nesso esplicito (poi,
  perciò, ma, e così, fino a) in modo che le posizioni si spieghino a vicenda e
  la conclusione discenda dalle carte. Esempio di filo (non copiarlo): «Ora sei
  in una fase di stasi; ciò che ti ostacola può portare alla rovina di un
  assetto, e con essa alla fine di un periodo, ma proprio quella fine apre a un
  nuovo inizio in cui può arrivare il successo.» Mantieni il significato vero
  delle carte e la tua voce.
- Il valore di una carta dipende dalla sua posizione e dal suo orientamento:
  nomina ogni carta con la posizione e l'orientamento (dritta o rovesciata) e
  spiega ciò che l'orientamento cambia. Una carta rovesciata non è un «no»: è la
  stessa energia bloccata, interiorizzata, ritardata o eccessiva.
- Metti le carte in relazione fra loro: le coppie di posizioni che la stesa
  prescrive di leggere insieme, le dignità elementali fra vicine e le
  prevalenze (Arcani maggiori, figure di corte, semi, numeri ripetuti).
- Rispetta le regole della stesa scelta. Nella croce semplice il giudice è la
  risposta e la sintesi calcolata ne è il senso profondo; nella Croce Celtica
  leggi l'esito con corona e atteggiamento; nella ruota leggi il significatore
  e gli assi.
- Richiama il colloquio: accenna alla domanda dell'oracolo e a ciò che chi
  consulta ha risposto («Alla domanda su… hai detto che…») e usalo per
  personalizzare la lettura di ogni forza in gioco. Il responso deve parlare di
  QUESTA persona e di QUESTA situazione, mai di chiunque. Non riportare il
  colloquio come elenco: intrecciane i dettagli nel discorso.
- Resta coerente con le interpretazioni immediate già date: approfondiscile e
  collegale, non contraddirle.
- Rispondi davvero al quesito, con chiarezza: indica la tendenza più probabile
  e perché le carte la mostrano.
- Tono: serio, caldo, rigoroso sul piano esoterico, mai teatrale. Seconda
  persona.
- Il futuro è la tendenza più probabile delle forze attuali, che le scelte di
  chi consulta possono cambiare: niente fatalismo, niente certezze assolute.

Formato (Markdown, 350-650 parole): esattamente queste quattro sezioni, in
questo ordine, con i titoli tradotti nella lingua della risposta:
## Il quadro
## Le forze in gioco   (qui il filo del racconto, tappa dopo tappa)
## Il consiglio delle carte
## La tendenza più probabile

Non aggiungere disclaimer: li aggiunge la piattaforma.
"""


@lru_cache(maxsize=4)
def _prefisso_cache(dottrina: str, guardie: str) -> str:
    return (
        f"{PROMPT_SINTESI}\n\n"
        f"# Regole di sicurezza del responso\n\n{guardie}\n\n"
        f"# Dottrina di lettura\n\n{dottrina}\n"
    )


def prefisso(conoscenza: Conoscenza, istruzioni_guardrail: List[str]) -> str:
    """Il prefisso stabile. Deve restare byte-identico fra letture: nessun
    dato della lettura, nessuna data, nessun ordine che dipenda dal caso.
    Solo ruolo, sicurezza e dottrina: le stese e le carte le sceglie il codice."""
    return _prefisso_cache(conoscenza.dottrina, "\n\n".join(istruzioni_guardrail))


def _con_nome(italiano: str, conoscenza: Conoscenza, nome_lingua: str, lang: str) -> str:
    """Il nome italiano e, se la risposta è in un'altra lingua, quello da usare."""
    if lingua(lang) == "it" or not nome_lingua or nome_lingua == italiano:
        return italiano
    return f"{italiano} (nella risposta: {nome_lingua})"


def blocco_stesa(conoscenza: Conoscenza, stesa: Dict[str, Any], lang: str) -> str:
    """Solo la stesa scelta: descrizione, regole, coppie. Le posizioni sono nelle schede."""
    nome = _con_nome(stesa["nome"], conoscenza, conoscenza.nome_stesa(stesa, lang), lang)
    righe = [f"## La stesa scelta: {nome} (mazzo {stesa['mazzo']})", stesa["descrizione"]]
    if stesa.get("regole"):
        righe += ["Regole della stesa:"] + [f"  - {r}" for r in stesa["regole"]]
    if stesa.get("coppie"):
        righe += ["Coppie di posizioni da leggere insieme:"]
        righe += [f"  - {a}–{b}: {testo}" for a, b, testo in stesa["coppie"]]
    return "\n".join(righe)


def blocco_carte(
    conoscenza: Conoscenza, stesa: Dict[str, Any], carte: List[Dict[str, Any]],
    dignita: Dict[int, Dict[str, Any]], lang: str,
) -> str:
    """Le schede delle sole carte estratte, nell'ordine delle posizioni."""
    righe = [
        "## Le carte estratte",
        "Per ogni posizione: il suo significato, la carta nell'orientamento estratto e la sua scheda.",
    ]
    for c in sorted(carte, key=lambda x: x["posizione"]):
        n = c["posizione"]
        pos = conoscenza.posizione(stesa, n)
        carta = conoscenza.carta(c["card_id"])
        nome_pos = _con_nome(pos["nome"], conoscenza, conoscenza.nome_posizione(stesa, n, lang), lang)
        nome_carta = _con_nome(carta["nome_it"], conoscenza, conoscenza.nome_carta(c["card_id"], lang), lang)
        righe += [
            "",
            f"### Posizione {n} «{nome_pos}» — {pos['significato']}",
            f"Carta estratta: {nome_carta}, {'rovesciata' if c['rovescio'] else 'dritta'}"
            + (" — carta di sintesi calcolata" if c.get("calcolata") else ""),
        ]
        if pos.get("senza_rovescio"):
            righe.append("Posizione di traverso: si legge sempre come dritta.")
        righe.append(scheda(carta, c["rovescio"]))
        d = dignita.get(n)
        if d:
            rel = ", ".join(f"{r['posizione']}:{r['relazione']}" for r in d["relazioni"]) or "nessuna vicina"
            righe.append(f"Dignità elementale: {d['giudizio']} ({rel})")
        if c.get("interpretazione"):
            righe.append(f"Interpretazione immediata già data: {c['interpretazione']}")
    return "\n".join(righe)


def catena(
    conoscenza: Conoscenza, stesa: Dict[str, Any], carte: List[Dict[str, Any]], lang: str,
) -> str:
    """L'ordine del racconto: le tappe nella sequenza in cui la stesa si legge.

    Per ogni tappa la posizione, la carta con l'orientamento e il suo valore in
    quella posa, in una frase. Il modello deve solo collegarle.
    """
    per_posizione = {c["posizione"]: c for c in carte}
    righe = [
        "## Ordine del racconto",
        "Racconta la lettura in quest'ordine, collegando ogni tappa alla successiva:",
    ]
    for k, n in enumerate(stesa["racconto"], start=1):
        c = per_posizione.get(n)
        if c is None:
            continue
        carta = conoscenza.carta(c["card_id"])
        righe.append(
            f"{k}. {conoscenza.nome_posizione(stesa, n, lang)} (posizione {n}) — "
            f"{conoscenza.nome_carta(c['card_id'], lang)}, {'rovesciata' if c['rovescio'] else 'dritta'}: "
            f"{valore_sintetico(carta, c['rovescio'])}"
        )
    return "\n".join(righe)


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
    colloquio: str = "",
    lang: str = "it",
) -> str:
    """La lettura concreta: tutto ciò che cambia da una consultazione all'altra.

    `carte` è l'elenco con `card_id`, `rovescio`, `posizione`, `calcolata` e
    l'`interpretazione` immediata già data. `colloquio` è la trascrizione
    dell'intervista: le domande dell'oracolo e le risposte.
    """
    righe = [
        "# La lettura",
        f"Quesito: {quesito}",
        f"Quadro emerso dall'intervista: {contesto or 'non disponibile'}",
    ]
    if colloquio:
        righe += ["", "Colloquio (domande dell'oracolo e risposte di chi consulta):", colloquio]
    if profilo:
        righe.append(f"Profilo di chi consulta:\n{profilo}")
    righe += [
        "", blocco_stesa(conoscenza, stesa, lang),
        "", blocco_carte(conoscenza, stesa, carte, dignita, lang),
        "", catena(conoscenza, stesa, carte, lang),
        "", "## Prevalenze",
        json.dumps(prevalenze, ensure_ascii=False),
    ]
    if wirth:
        righe.append(
            f"Sintesi di Wirth: somma {wirth['somma']} → Arcano {wirth['numero']} "
            f"({wirth['nome']})" + (" — DOPPIA VALENZA: già presente nella stesa" if wirth.get("doppia_valenza") else "")
        )
    if vincoli:
        righe += ["", "## Correzioni richieste", vincoli]
    righe += ["", istruzione_lingua(lang)]
    return "\n".join(righe)
