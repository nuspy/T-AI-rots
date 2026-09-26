"""L'interpretazione immediata di una carta appena girata.

Si legge **la carta in quella posizione**, non la carta in astratto: lo stesso
Tre di Spade dice cose diverse come «passato recente» e come «esito».

**Cosa entra nel messaggio, deciso dal codice.** Per ogni carta girata il
messaggio porta solo i valori di quella posa esatta:

- il significato di *quella* posizione nella stesa (non delle altre);
- l'orientamento estratto, e la scheda della carta per quell'orientamento
  (`schede.scheda`: il significato dritto *o* quello rovesciato, non entrambi);
- la dignità rispetto alle vicine già rivelate;
- le regole di coppia della stesa che toccano questa posizione, se l'altra
  carta è già visibile;
- il quadro emerso dall'intervista e il colloquio;
- nelle letture di compatibilità e di coppia, di chi parla la posizione (chi
  consulta, l'altra persona, la relazione, una delle due strade) e le due persone
  (`persone.py`): il soggetto lo decide il codice dai dati della stesa, non il
  modello.

Il modello non cerca né sceglie niente: i valori gli arrivano già selezionati,
il che evita gli errori (una carta letta come rovesciata quando è dritta, una
posizione col significato di un'altra) e costa meno token. Le vicine non ancora
rivelate non entrano: la dignità si calcola solo con ciò che chi consulta ha già
visto, altrimenti l'interpretazione anticiperebbe carte ancora coperte.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .lingue import istruzione_lingua, lingua
from .schede import scheda

PROMPT_INTERPRETAZIONE = """# Compito: interpretazione

Sei l'oracolo di TAROTS chat, lettore rigoroso del Tarocco di Thoth di Aleister
Crowley. Interpreti UNA carta appena girata, nella sua posizione della stesa.

I dati sono già scelti dal sistema e stanno nel messaggio: la posizione con il
suo significato, l'orientamento estratto (dritta o rovesciata) e la scheda della
carta per quell'orientamento. Usa solo quelli: non aggiungere significati di
altre carte, di altre posizioni o dell'orientamento che non è uscito.

Come interpretare:
- Leggi la carta IN QUELLA POSIZIONE, non in astratto: parti dal significato
  della posizione («il presente è…», «come ostacolo…», «l'esito tende a…») e
  mostra come la carta lo colora. La stessa carta in un'altra posizione dice
  un'altra cosa.
- Se la carta è rovesciata, dillo e spiega come l'orientamento cambia il
  messaggio: energia bloccata, interiorizzata, ritardata o eccessiva, mai il
  suo contrario banale. Se è dritta, non parlarne.
- Se la dignità è indicata, tienine conto: ben dignificata esprime il lato
  luminoso, mal dignificata il lato d'ombra.
- Se sono indicate regole di coppia con carte già girate, tienine conto: la
  carta si legge anche in relazione a quella.
- Usa i livelli di significato della carta (essoterico, psicologico,
  iniziatico) e i suoi riferimenti (lettera ebraica, percorso, sefira,
  astrologia, elemento) solo quando illuminano il senso, senza fare lezione.
- Collega la lettura al quesito e a un dettaglio concreto che chi consulta ha
  detto nel colloquio, senza citarlo alla lettera.
- Deve essere una lettura SPECIFICA di questa carta, in questa posizione, per
  questa domanda: una frase che andrebbe bene per qualunque carta o posizione è
  un errore.
- 2-3 frasi brevi, in seconda persona, tono serio e caldo. Per il registro,
  questo è un esempio di lettura riuscita (non copiarlo): «Il presente è
  segnato da irrequietezza e instabilità: la carta, rovesciata, ti invita a
  guardare con lucidità ciò che stai progettando, invece di decidere in fretta.»
- Mai fatalismo: parla di tendenze e forze, non di sentenze. Niente diagnosi,
  consigli medici, legali o finanziari. Niente certezze sui sentimenti altrui.
- Non anticipare il responso finale: questa è la lettura di una sola carta.
- Scrivi solo il testo dell'interpretazione, senza titoli né elenchi.
"""


PROMPT_INTERPRETAZIONE_RELAZIONE = """# Regole aggiuntive: compatibilità e coppia

Stai interpretando una carta di una lettura che riguarda chi consulta e un'altra
persona. Nel messaggio trovi «Le persone» e la riga «Questa posizione riguarda:
…»: leggi la carta per QUEL soggetto (chi consulta, l'altra persona, la relazione
fra voi, una delle due strade).

- Le carte parlano di chi consulta e della relazione. Ciò che riguarda l'altra
  persona è una tendenza o un'energia che si mostra nei suoi atteggiamenti, mai
  una certezza su ciò che pensa, prova, vuole o nasconde («sembra», «tende a»,
  «può indicare»).
- Nessun verdetto sulla relazione e nessuna previsione certa sulla sua durata.
- Nessuno stereotipo di genere: Re, Regina, Cavaliere, Fante, Imperatore e
  Imperatrice sono energie, non «l'uomo» o «la donna». Non dare per scontati il
  tipo di relazione né l'orientamento. Usa il genere dichiarato solo per pronomi
  e concordanze, con forme neutre se non è noto o non è binario; una persona
  trans si tratta col suo genere dichiarato, senza commentarlo.
- Chiama l'altra persona per nome, se c'è; non usare il cognome né dati che non ti
  sono stati dati.
- Se conosci il segno solare, usalo solo se illumina la carta: non inventare
  ascendente, luna o pianeti.
"""


def messaggio(
    *,
    carta: Dict[str, Any],
    rovescio: bool,
    stesa: Dict[str, Any],
    posizione: Dict[str, Any],
    quesito: str,
    contesto: str,
    dignita: Optional[Dict[str, Any]] = None,
    precedenti: str = "",
    note: Optional[List[str]] = None,
    doppia_valenza: bool = False,
    colloquio: str = "",
    nomi: Optional[Tuple[str, str]] = None,
    lang: str = "it",
    persone: str = "",
    soggetto: str = "",
) -> str:
    """Il messaggio utente per una carta: i valori di questa posa, nient'altro.

    `nomi` è (nome della carta, nome della posizione) nella lingua della
    risposta, se non è l'italiano: il modello li usa così come sono. `persone` è
    il blocco «Le persone» e `soggetto` il testo di chi parla la posizione: solo
    nelle letture di compatibilità e di coppia.
    """
    parti = [
        f"Quesito: {quesito}",
        f"Contesto emerso dall'intervista: {contesto or 'non disponibile'}",
    ]
    if colloquio:
        parti += ["", "Colloquio (domande dell'oracolo e risposte di chi consulta):", colloquio]
    if persone:
        parti += ["", persone]
    parti += [
        "",
        f"Stesa: {stesa['nome']} — {stesa['descrizione']}",
        f"Posizione {posizione['n']}: {posizione['nome']} — {posizione['significato']}",
    ]
    if soggetto:
        parti.append(f"Questa posizione riguarda: {soggetto}")
    parti.append(f"Orientamento: {'rovesciata' if rovescio else 'dritta'}")
    if posizione.get("calcolata"):
        parti.append(
            "Questa carta non è stata scelta: è la sintesi calcolata (somma "
            "teosofica degli Arcani della stesa)."
        )
    if doppia_valenza:
        parti.append(
            "Doppia valenza: questo Arcano è già presente nella stesa, il suo "
            "messaggio è rafforzato ed è la chiave della lettura."
        )
    if dignita and dignita.get("relazioni"):
        rel = ", ".join(
            f"posizione {r['posizione']} ({r['elemento']}): {r['relazione']}"
            for r in dignita["relazioni"]
        )
        parti.append(f"Dignità elementale rispetto alle carte già rivelate: {dignita['giudizio']} ({rel})")
    for nota in note or []:
        parti.append(f"Regola della stesa — {nota}")
    if precedenti:
        parti.append(f"Carte già rivelate:\n{precedenti}")
    parti += ["", scheda(carta, rovescio), ""]
    if nomi and lingua(lang) != "it":
        parti.append(f"Nomi da usare nella risposta: carta «{nomi[0]}», posizione «{nomi[1]}».")
    parti.append(istruzione_lingua(lang))
    return "\n".join(parti)
