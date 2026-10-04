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

**La chiamata unica.** Dalla v8.6 tutte le carte di una lettura si interpretano
in una chiamata sola (`api/rivelazione.py`): stesse regole
(`PROMPT_INTERPRETAZIONE_UNICA` le ricava da `PROMPT_INTERPRETAZIONE`), il
contesto comune una volta e per ogni carta lo stesso blocco del messaggio
singolo (`messaggio_unico`), risposta in JSON divisa dal codice (`dividi`). Il
messaggio singolo (`messaggio`) resta per il ripiego.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple

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


PROMPT_INTERPRETAZIONE_LAVORO = """# Regole aggiuntive: lavoro e affari

Questa lettura riguarda il lavoro, la carriera o un'attività di chi consulta: leggi la
carta su quel piano, con concretezza (il ruolo, il progetto, le persone dell'ambiente di
lavoro, i tempi, le decisioni in arrivo), senza perdere il suo senso simbolico.

- Colleghi, responsabili, clienti e controparti compaiono come energie e tendenze nei loro
  atteggiamenti, mai come certezze su ciò che pensano o decideranno.
- Le carte non dicono se un posto, un contratto o un affare arriveranno: descrivono le forze
  in gioco e ciò che dipende da chi consulta.
- Niente cifre, investimenti, passi legali o contrattuali presentati come indicazione delle
  carte: per quelli serve un professionista.
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
    registro: str = "",
) -> str:
    """Il messaggio utente per una carta: i valori di questa posa, nient'altro.

    `nomi` è (nome della carta, nome della posizione) nella lingua della
    risposta, se non è l'italiano: il modello li usa così come sono. `persone` è
    il blocco «Le persone» e `soggetto` il testo di chi parla la posizione: solo
    nelle letture di compatibilità e di coppia. `registro` (v7, Fase F) è
    `user.registro_linguistico`: vuoto o `"esoterico"` non aggiunge nulla.
    """
    parti = _parti_comuni(stesa=stesa, quesito=quesito, contesto=contesto, colloquio=colloquio, persone=persone)
    parti += _parti_carta(
        carta=carta, rovescio=rovescio, posizione=posizione, dignita=dignita, precedenti=precedenti, note=note,
        doppia_valenza=doppia_valenza, nomi=nomi, lang=lang, soggetto=soggetto,
    )
    parti += _parti_chiusura(lang=lang, registro=registro)
    return "\n".join(parti)


def _parti_comuni(
    *, stesa: Dict[str, Any], quesito: str, contesto: str, colloquio: str, persone: str,
) -> List[str]:
    """Ciò che vale per tutte le carte della lettura: quesito, quadro, colloquio, persone, stesa."""
    parti = [
        f"Quesito: {quesito}",
        f"Contesto emerso dall'intervista: {contesto or 'non disponibile'}",
    ]
    if colloquio:
        parti += ["", "Colloquio (domande dell'oracolo e risposte di chi consulta):", colloquio]
    if persone:
        parti += ["", persone]
    parti += ["", f"Stesa: {stesa['nome']} — {stesa['descrizione']}"]
    return parti


def _parti_carta(
    *,
    carta: Dict[str, Any],
    rovescio: bool,
    posizione: Dict[str, Any],
    dignita: Optional[Dict[str, Any]] = None,
    precedenti: str = "",
    note: Optional[List[str]] = None,
    doppia_valenza: bool = False,
    nomi: Optional[Tuple[str, str]] = None,
    lang: str = "it",
    soggetto: str = "",
) -> List[str]:
    """I valori di una carta in quella posa: posizione, soggetto, orientamento, dignità, regole, scheda, nomi."""
    parti = [f"Posizione {posizione['n']}: {posizione['nome']} — {posizione['significato']}"]
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
    return parti


def _parti_chiusura(*, lang: str, registro: str) -> List[str]:
    """Il registro linguistico e la lingua della risposta: una volta sola, in fondo."""
    parti: List[str] = []
    if registro == "quotidiano":
        parti.append(
            "Registro linguistico richiesto: quotidiano. Evita termini tecnici esoterici non "
            "spiegati (lettera ebraica, sefira, percorso, gradi iniziatici): se un riferimento "
            "serve, traducilo subito in parole comuni invece di darlo per noto."
        )
    parti.append(istruzione_lingua(lang))
    return parti


# ---- la chiamata unica: tutte le carte della lettura in una risposta ------------------------------------------------

#: Il tetto visibile della risposta per una carta (2-3 frasi stanno larghe in 500 token). Nella chiamata unica si
#: moltiplica per le carte e si aggiunge la cornice del JSON. È un tetto, non un obiettivo; il margine per il
#: ragionamento lo aggiunge il fornitore (`llm/ragionamento.tetto_con_ragionamento`).
TETTO_CARTA = 500
TETTO_CORNICE_JSON = 200


def tetto_unica(carte: int) -> int:
    """Il tetto visibile della chiamata unica per `carte` carte."""
    return TETTO_CARTA * max(1, carte) + TETTO_CORNICE_JSON


#: La sola frase del prompt della singola carta che la chiamata unica riformula: le regole restano quelle, parola per
#: parola, e si ricavano da `PROMPT_INTERPRETAZIONE` — cambiare quello cambia anche questo.
_UNA_CARTA = "Interpreti UNA carta appena girata, nella sua posizione della stesa."
_PIU_CARTE = (
    "Interpreti le carte appena girate di una stesa, UNA PER UNA, ciascuna nella sua\n"
    "posizione della stesa."
)
assert _UNA_CARTA in PROMPT_INTERPRETAZIONE

PROMPT_INTERPRETAZIONE_UNICA = "# Compito: interpretazione_unica\n" + PROMPT_INTERPRETAZIONE.split("\n", 1)[1].replace(
    _UNA_CARTA, _PIU_CARTE,
)

#: L'ultimo messaggio di sistema della chiamata unica, dopo le regole di lavoro, di coppia e di sicurezza: che le carte
#: sono più d'una, come leggere i blocchi, e il formato JSON.
PROMPT_INTERPRETAZIONE_UNICA_FORMATO = """# Più carte in una sola risposta

In questo messaggio le carte da interpretare sono più d'una. Ognuna ha il suo blocco («## Carta in posizione N») con
la sua posizione e il suo significato, l'orientamento, la scheda, la dignità, le regole di coppia e le carte già
rivelate prima di lei. Quesito, quadro dell'intervista, colloquio e persone sono scritti una volta sola, in alto, e
valgono per tutte.

- Tutte le regole qui sopra valgono per OGNI carta, separatamente: ogni interpretazione è la lettura di quella sola
  carta, appena girata, nella sua posizione, per questa domanda.
- Per ogni carta usa solo i dati del suo blocco: le carte che nella stesa vengono dopo non sono ancora state girate,
  quindi non anticiparle né nominarle.
- Ogni interpretazione deve reggersi da sola: non rimandare alle altre («come detto sopra») e non ripetere le stesse
  frasi da una carta all'altra.

Formato della risposta: solo un oggetto JSON, senza testo prima o dopo e senza blocchi di codice:
{"carte": [{"posizione": 1, "orientamento": "dritta", "interpretazione": "…"},
           {"posizione": 2, "orientamento": "rovesciata", "interpretazione": "…"}]}
Una voce per ogni blocco del messaggio, nell'ordine delle posizioni, con il numero della posizione scritto nel blocco.
Nel campo «orientamento» ripeti, prima del testo, l'orientamento scritto nella riga «Orientamento:» del blocco di
quella carta: «dritta» o «rovesciata», in italiano, qualunque sia la lingua della risposta.
Nel campo «interpretazione» va solo il testo della lettura di quella carta, senza titoli né elenchi.
"""


def messaggio_unico(
    *,
    carte: List[Dict[str, Any]],
    stesa: Dict[str, Any],
    quesito: str,
    contesto: str,
    colloquio: str = "",
    persone: str = "",
    lang: str = "it",
    registro: str = "",
) -> str:
    """Il messaggio utente della chiamata unica: il contesto comune una volta, poi un blocco per carta.

    Ogni voce di `carte` porta gli stessi valori che `messaggio()` riceve per una carta sola (`carta`, `rovescio`,
    `posizione`, `dignita`, `precedenti`, `note`, `doppia_valenza`, `nomi`, `soggetto`), calcolati come se le carte si
    girassero una alla volta: il blocco di una carta è identico alla parte «carta» del messaggio singolo.
    """
    parti = _parti_comuni(stesa=stesa, quesito=quesito, contesto=contesto, colloquio=colloquio, persone=persone)
    posizioni = ", ".join(str(c["posizione"]["n"]) for c in carte)
    parti += ["", f"Carte da interpretare: {len(carte)}, nelle posizioni {posizioni}. Un'interpretazione per ciascuna."]
    for voce in carte:
        parti += ["", f"## Carta in posizione {voce['posizione']['n']}"]
        parti += _parti_carta(**voce, lang=lang)
    parti += _parti_chiusura(lang=lang, registro=registro)
    return "\n".join(parti)


#: Come il modello può scrivere il campo «orientamento»: le due parole chieste e le loro forme più vicine.
_ORIENTAMENTI = {
    "dritta": False, "dritto": False, "upright": False,
    "rovesciata": True, "rovesciato": True, "reversed": True,
}

#: Le radici con cui un testo dice «rovesciata», per lingua della risposta: una carta dritta il cui testo ne contiene
#: una torna alla chiamata singola. Una lingua che non è qui non si controlla (meglio niente che un falso allarme).
RADICI_ROVESCIATA: Dict[str, Tuple[str, ...]] = {
    "it": ("rovesciat",),
    "en": ("reversed",),
    "es": ("invertid", "al revés"),
    "hu": ("fordított",),
    "ru": ("перевёрнут", "перевернут"),
    "uk": ("перевернут",),
}


def dice_rovesciata(testo: str, lang: str) -> bool:
    """Se il testo, nella lingua della risposta, dice che la carta è rovesciata. `False` per una lingua senza radici."""
    radici = RADICI_ROVESCIATA.get(lingua(lang), ())
    basso = testo.lower()
    return any(r in basso for r in radici)


def dividi(
    dati: Any, attese: Iterable[int], *, orientamenti: Optional[Dict[int, bool]] = None, lang: str = "it",
    scarti: Optional[Dict[int, str]] = None,
) -> Dict[int, str]:
    """Le interpretazioni della risposta unica, per posizione: solo quelle attese, non vuote, la prima se ripetute.

    Accetta `{"carte": [...]}` (il formato chiesto) o direttamente la lista; la posizione può arrivare come numero o
    come stringa di cifre. Ciò che manca non si inventa: chi chiama torna alla chiamata singola per quelle posizioni.

    **L'orientamento non deve scivolare da una carta all'altra.** Con `orientamenti` (posizione → rovesciata, i
    valori veri della lettura) una voce si scarta — e quella posizione torna alla chiamata singola — se il campo
    «orientamento» manca o non coincide con quello vero, o se la carta è dritta e il testo la dice rovesciata
    (`dice_rovesciata`, nella lingua `lang`). In `scarti`, se c'è, il motivo per posizione.
    """
    attese = set(attese)
    voci = dati.get("carte") if isinstance(dati, dict) else dati
    divise: Dict[int, str] = {}
    viste = set()
    for voce in voci if isinstance(voci, list) else []:
        if not isinstance(voce, dict):
            continue
        n, testo = voce.get("posizione"), voce.get("interpretazione")
        if isinstance(n, str) and n.strip().isdigit():
            n = int(n.strip())
        elif isinstance(n, float) and n.is_integer():
            n = int(n)
        if isinstance(n, bool) or not isinstance(n, int) or n not in attese or n in viste:
            continue
        if not (isinstance(testo, str) and testo.strip()):
            continue
        viste.add(n)
        motivo = _orientamento_sbagliato(voce, testo, orientamenti[n], lang) \
            if orientamenti is not None and n in orientamenti else ""
        if motivo:
            if scarti is not None:
                scarti[n] = motivo
            continue
        divise[n] = testo.strip()
    return divise


def _orientamento_sbagliato(voce: Dict[str, Any], testo: str, rovescio: bool, lang: str) -> str:
    """Il motivo per cui la voce non regge l'orientamento vero, o `""`."""
    campo = voce.get("orientamento")
    detto = _ORIENTAMENTI.get(campo.strip().lower()) if isinstance(campo, str) else None
    if detto is None:
        return "orientamento mancante"
    if detto != rovescio:
        return f"orientamento «{campo}» invece di «{'rovesciata' if rovescio else 'dritta'}»"
    if not rovescio and dice_rovesciata(testo, lang):
        return "carta dritta detta rovesciata nel testo"
    return ""
