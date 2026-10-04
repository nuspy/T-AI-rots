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

_CORPO_SINTESI = """# Compito: sintesi

Sei l'oracolo di TAROTS chat, lettore rigoroso e sapiente del Tarocco di Thoth di
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
- Se il messaggio contiene una sezione «Memoria: letture precedenti», fai un
  confronto esplicito prima/dopo quando pertinente («rispetto a ciò che sapevo
  di te…»), senza inventare continuità che le memorie non supportano: una
  memoria STABILE descrive chi consulta senza mai essere messa in discussione
  di nuovo, una VARIABILE è la situazione a cui si può chiedere se qualcosa è
  cambiato.
"""

_FORMATO_STANDARD = """
Formato (Markdown, 350-650 parole): esattamente queste quattro sezioni, in
questo ordine, con i titoli tradotti nella lingua della risposta:
## Il quadro
## Le forze in gioco   (qui il filo del racconto, tappa dopo tappa)
## Il consiglio delle carte
## La tendenza più probabile

Stile: conciso ma completo, esaustivo e chiaro. Ogni frase aggiunge un'informazione
specifica di questa lettura; nessuna sezione ripete il contenuto di un'altra; niente
frasi generiche che varrebbero per qualunque lettura. Resta nel numero di parole indicato.

Non aggiungere disclaimer: li aggiunge la piattaforma.
"""

#: La lettura standard: identica, lettera per lettera, a com'era prima delle
#: letture speciali (lo prova un test con l'impronta del prefisso).
PROMPT_SINTESI = _CORPO_SINTESI + _FORMATO_STANDARD

_REGOLE_RELAZIONE = """
Regole per le letture di compatibilità e di coppia:
- Il messaggio contiene «Le persone», la «Compatibilità zodiacale» calcolata dal
  sistema e, per ogni carta, di chi parla la posizione («Riguarda:»). Nomina i
  partecipanti per nome (l'altra persona col suo nome, chi consulta con «tu»);
  non usare cognomi né dati che non ti sono stati dati.
- Le carte parlano di chi consulta e della relazione. Ciò che riguarda l'altra
  persona è una tendenza, mai una certezza su ciò che pensa, prova, vuole o
  nasconde. Nessun verdetto («siete compatibili» o «incompatibili», «lascialo»,
  «è la persona giusta»): parla di affinità, punti d'incontro e aree di lavoro, e
  lascia la scelta a chi consulta. Nessuna previsione certa sulla durata.
- La compatibilità zodiacale è calcolata dal sistema sui soli segni solari: usala
  come sfondo, non contraddirla e non inventare ascendente, luna o pianeti. Se una
  data è sulla cuspide, dillo in una frase.
- Nessuno stereotipo di genere: Re, Regina, Cavaliere, Fante, Imperatore e
  Imperatrice sono energie, non «l'uomo» o «la donna»; non dare per scontati il
  tipo di relazione né l'orientamento. Il genere serve solo a pronomi e
  concordanze (forme neutre se non binario, «altro» o non dichiarato); una persona
  trans si tratta col genere dichiarato, senza commentarlo.
- Se chi consulta ha descritto violenza, paura o controllo, non minimizzare e non
  consigliare di «lavorare sulla coppia»: riconosci ciò che vive e indica in modo
  generico i servizi di aiuto del suo paese.
"""

_FORMATO_COMPATIBILITA = """
Formato (Markdown, 450-750 parole): esattamente queste cinque sezioni, in questo
ordine, con i titoli tradotti nella lingua della risposta:
## Il quadro
## L'incontro dei segni   (la compatibilità zodiacale calcolata, letta insieme alle carte: sfondo, non verdetto)
## Le forze in gioco   (qui il filo del racconto, tappa dopo tappa, con i nomi)
## Il consiglio delle carte
## La tendenza più probabile

Stile: conciso ma completo, esaustivo e chiaro. Ogni frase aggiunge un'informazione
specifica di questa lettura; nessuna sezione ripete il contenuto di un'altra; niente
frasi generiche che varrebbero per qualunque lettura. Resta nel numero di parole indicato.

Non aggiungere disclaimer: li aggiunge la piattaforma.
"""

_FORMATO_COPPIA = """
Formato (Markdown, 450-750 parole): esattamente queste cinque sezioni, in questo
ordine, con i titoli tradotti nella lingua della risposta:
## Il quadro
## Ciò che vi lega e ciò che vi mette alla prova   (qui anche la compatibilità zodiacale, come sfondo)
## Le forze in gioco   (qui il filo del racconto, tappa dopo tappa, con i nomi)
## Il consiglio delle carte   (rivolto a chi consulta: cosa può fare chi consulta, non l'altra persona)
## La tendenza più probabile   (con «cosa dipende da voi»)

Stile: conciso ma completo, esaustivo e chiaro. Ogni frase aggiunge un'informazione
specifica di questa lettura; nessuna sezione ripete il contenuto di un'altra; niente
frasi generiche che varrebbero per qualunque lettura. Resta nel numero di parole indicato.

Non aggiungere disclaimer: li aggiunge la piattaforma.
"""

_REGOLE_LAVORO = """
Regole per le letture di lavoro e affari:
- La lettura riguarda il lavoro, la carriera o un'attività di chi consulta: porta
  ogni forza sul piano professionale con concretezza (il ruolo, il progetto, le
  persone dell'ambiente di lavoro, i tempi, le decisioni in arrivo), senza
  perdere il senso simbolico delle carte.
- Colleghi, responsabili, clienti, soci e controparti sono energie e tendenze nei
  loro atteggiamenti, mai certezze su ciò che pensano o decideranno.
- Le carte non dicono se un posto, un contratto o un affare arriveranno: dicono
  le forze in gioco e ciò che dipende da chi consulta. La scelta resta sua.
- Nel consiglio indica passi concreti e alla portata di chi consulta, non cifre,
  investimenti, passi legali o contrattuali: per quelli rimanda a un
  professionista che conosca il caso.
"""

#: Il prompt di sintesi per categoria di lettura. Il prefisso in cache è uno
#: per categoria, e ciascuno è stabile fra letture della stessa categoria.
PROMPT_PER_CATEGORIA = {
    "standard": PROMPT_SINTESI,
    # Lavoro e affari: le stesse quattro sezioni della standard, con le regole del piano professionale.
    "lavoro": _CORPO_SINTESI + _REGOLE_LAVORO + _FORMATO_STANDARD,
    "compatibilita": _CORPO_SINTESI + _REGOLE_RELAZIONE + _FORMATO_COMPATIBILITA,
    "coppia": _CORPO_SINTESI + _REGOLE_RELAZIONE + _FORMATO_COPPIA,
}


@lru_cache(maxsize=8)
def _prefisso_cache(dottrina: str, guardie: str, categoria: str) -> str:
    return (
        f"{PROMPT_PER_CATEGORIA[categoria]}\n\n"
        f"# Regole di sicurezza del responso\n\n{guardie}\n\n"
        f"# Dottrina di lettura\n\n{dottrina}\n"
    )


def prefisso(
    conoscenza: Conoscenza, istruzioni_guardrail: List[str], categoria: str = "standard",
) -> str:
    """Il prefisso stabile. Deve restare byte-identico fra letture: nessun
    dato della lettura, nessuna data, nessun ordine che dipenda dal caso.
    Solo ruolo, sicurezza e dottrina: le stese e le carte le sceglie il codice.

    Ce n'è uno per categoria di lettura (standard, lavoro, compatibilità, coppia): il
    formato del responso e le regole sulle relazioni o sul lavoro cambiano, la dottrina no.
    Quello della lettura standard non è cambiato."""
    return _prefisso_cache(conoscenza.dottrina, "\n\n".join(istruzioni_guardrail), categoria)


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
    dignita: Dict[int, Dict[str, Any]], lang: str, soggetti: Optional[Dict[int, str]] = None,
) -> str:
    """Le schede delle sole carte estratte, nell'ordine delle posizioni.

    Nelle letture speciali `soggetti` dice, per ogni posizione, di chi parla
    (chi consulta, l'altra persona, la relazione): lo decide il codice."""
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
        if soggetti and soggetti.get(n):
            righe.append(f"Riguarda: {soggetti[n]}")
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
    soggetti: Optional[Dict[int, str]] = None,
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
        riga = (
            f"{k}. {conoscenza.nome_posizione(stesa, n, lang)} (posizione {n}) — "
            f"{conoscenza.nome_carta(c['card_id'], lang)}, {'rovesciata' if c['rovescio'] else 'dritta'}: "
            f"{valore_sintetico(carta, c['rovescio'])}"
        )
        # In coda alla riga e dopo «(posizione n)»: chi legge la catena col
        # numero di posizione non deve accorgersi del soggetto.
        if soggetti and soggetti.get(n):
            riga += f" [riguarda: {soggetti[n]}]"
        righe.append(riga)
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
    persone: str = "",
    compatibilita: str = "",
    soggetti: Optional[Dict[int, str]] = None,
    memorie_rilevanti: str = "",
    registro: str = "",
) -> str:
    """La lettura concreta: tutto ciò che cambia da una consultazione all'altra.

    Nelle letture di compatibilità e di coppia: `persone` (il blocco «Le
    persone»), `compatibilita` (il blocco della compatibilità zodiacale
    calcolata) e `soggetti` (di chi parla ogni posizione).

    `carte` è l'elenco con `card_id`, `rovescio`, `posizione`, `calcolata` e
    l'`interpretazione` immediata già data. `colloquio` è la trascrizione
    dell'intervista: le domande dell'oracolo e le risposte. `memorie_rilevanti`
    (v6, Fase C) è già formattato dal chiamante (`readings.py`), come per
    `colloquio`: è per-utente, quindi qui e non nel prefisso stabile. `registro`
    (v7, Fase F) è `user.registro_linguistico`: vuoto o `"esoterico"` non
    aggiunge nulla (comportamento identico a prima di v7); `"quotidiano"`
    aggiunge un'istruzione breve. Per-utente come `memorie_rilevanti`, mai nel
    prefisso stabile.
    """
    righe = [
        "# La lettura",
        f"Quesito: {quesito}",
        f"Quadro emerso dall'intervista: {contesto or 'non disponibile'}",
    ]
    if colloquio:
        righe += ["", "Colloquio (domande dell'oracolo e risposte di chi consulta):", colloquio]
    if memorie_rilevanti:
        righe += ["", "## Memoria: letture precedenti", memorie_rilevanti]
    if profilo:
        righe.append(f"Profilo di chi consulta:\n{profilo}")
    if persone:
        righe += ["", persone]
    if compatibilita:
        righe += ["", compatibilita]
    righe += [
        "", blocco_stesa(conoscenza, stesa, lang),
        "", blocco_carte(conoscenza, stesa, carte, dignita, lang, soggetti),
        "", catena(conoscenza, stesa, carte, lang, soggetti),
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
    if registro == "quotidiano":
        righe += [
            "",
            "Registro linguistico richiesto: quotidiano. Evita termini tecnici esoterici non "
            "spiegati (lettera ebraica, sefira, percorso, gradi iniziatici): se un riferimento "
            "serve, traducilo subito in parole comuni invece di darlo per noto.",
        ]
    righe += ["", istruzione_lingua(lang)]
    return "\n".join(righe)
