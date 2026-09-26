"""Il segno solare e l'aspetto fra due segni: la compatibilità zodiacale.

**Cosa si calcola, e cosa no.** Dalla data di nascita si ricava il segno
solare (zodiaco tropicale, con i confini più diffusi). Non si conoscono ora e
luogo di nascita, quindi non ci sono ascendente, luna né pianeti: la lettura
zodiacale è per forza quella *dei segni solari*, e il prompt lo dice al modello
perché non se ne inventi altri.

**Cuspide.** I confini fra i segni cadono in giorni che cambiano di un anno
con l'altro e dipendono dall'ora e dal luogo. Chi è nato il primo giorno di un
segno, o l'ultimo, può appartenere al segno vicino: la funzione lo segnala
(`cuspide`, `vicino`) e la lettura ne parla, senza scegliere per l'utente.

**Aspetto.** La distanza fra due segni, contata lungo lo zodiaco (da 0 a 6),
è l'aspetto classico: congiunzione (0), semisestile (1), sestile (2), quadrato
(3), trigono (4), quinconce (5), opposizione (6). L'armonia che ne discende è
solo *qualitativa* — alta, buona, mista, impegnativa —, mai un punteggio: una
percentuale darebbe una precisione che l'astrologia dei segni solari non ha. Gli
elementi si confrontano con le stesse relazioni delle dignità di Crowley
(`dignita.nome_relazione`).

Il modulo è puro: nessun I/O, nessun modello. Il risultato è dato deterministico
che il prompt riceve già fatto; il modello lo usa come sfondo, non lo calcola.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple

from .dignita import nome_relazione

#: Nell'ordine dello zodiaco, da Ariete: codice, nome, elemento, modalità.
SEGNI: Tuple[Tuple[str, str, str, str], ...] = (
    ("ariete", "Ariete", "fuoco", "cardinale"),
    ("toro", "Toro", "terra", "fisso"),
    ("gemelli", "Gemelli", "aria", "mutevole"),
    ("cancro", "Cancro", "acqua", "cardinale"),
    ("leone", "Leone", "fuoco", "fisso"),
    ("vergine", "Vergine", "terra", "mutevole"),
    ("bilancia", "Bilancia", "aria", "cardinale"),
    ("scorpione", "Scorpione", "acqua", "fisso"),
    ("sagittario", "Sagittario", "fuoco", "mutevole"),
    ("capricorno", "Capricorno", "terra", "cardinale"),
    ("acquario", "Acquario", "aria", "fisso"),
    ("pesci", "Pesci", "acqua", "mutevole"),
)

#: (mese, giorno) del primo giorno di ciascun segno, nello stesso ordine.
_INIZI: Tuple[Tuple[int, int], ...] = (
    (3, 21), (4, 20), (5, 21), (6, 21), (7, 23), (8, 23),
    (9, 23), (10, 23), (11, 22), (12, 22), (1, 20), (2, 19),
)

_ASPETTI: Dict[int, str] = {
    0: "congiunzione",
    1: "semisestile",
    2: "sestile",
    3: "quadrato",
    4: "trigono",
    5: "quinconce",
    6: "opposizione",
}

_ARMONIA: Dict[str, str] = {
    "congiunzione": "alta",
    "trigono": "alta",
    "sestile": "buona",
    "opposizione": "mista",
    "semisestile": "mista",
    "quadrato": "impegnativa",
    "quinconce": "impegnativa",
}

#: Una frase fissa per aspetto: descrive la dinamica, non emette verdetti.
NOTE_ASPETTO: Dict[str, str] = {
    "congiunzione": "stesso segno: molto in comune, e per questo anche gli stessi punti ciechi",
    "semisestile": "segni contigui: poco in comune, si guardano da vicino senza capirsi subito",
    "sestile": "segni che si sostengono: collaborazione facile se c'è iniziativa da entrambe le parti",
    "quadrato": "segni in tensione: attrito che stimola, richiede impegno e reciproca pazienza",
    "trigono": "stesso elemento: intesa naturale, fluida, quasi senza bisogno di spiegarsi",
    "quinconce": "segni senza affinità evidente: chiedono aggiustamenti continui e curiosità per l'altro",
    "opposizione": "segni opposti e complementari: forte attrazione, la sfida è integrare le differenze",
}


@dataclass(frozen=True)
class Segno:
    codice: str
    nome: str
    elemento: str
    modalita: str
    #: Vero se la data cade il primo o l'ultimo giorno del segno.
    cuspide: bool = False
    #: Il codice del segno vicino con cui la data può confondersi, se `cuspide`.
    vicino: Optional[str] = None


@dataclass(frozen=True)
class Compatibilita:
    segno_a: Segno
    segno_b: Segno
    #: La distanza lungo lo zodiaco, da 0 a 6.
    distanza: int
    aspetto: str
    #: `rafforzata`, `amica`, `moderata`, `ostile` o `neutra` (dignità di Crowley).
    relazione_elementi: str
    stessa_modalita: bool
    #: `alta`, `buona`, `mista` o `impegnativa`. Qualitativa: nessun punteggio.
    armonia: str
    nota: str


def _indice(nascita: date) -> int:
    """L'indice del segno solare (0 = Ariete) di una data."""
    mg = (nascita.month, nascita.day)
    # L'ultimo inizio non successivo alla data; prima del 20 gennaio è Capricorno.
    candidati = [i for i, inizio in enumerate(_INIZI) if inizio <= mg]
    if not candidati:
        return 9
    # Fra gli inizi già passati vince il più tardo nell'anno.
    return max(candidati, key=lambda i: _INIZI[i])


def segno_solare(nascita: date) -> Segno:
    """Il segno solare, con l'avviso di cuspide se la data è al confine."""
    i = _indice(nascita)
    codice, nome, elemento, modalita = SEGNI[i]
    domani = nascita + timedelta(days=1)
    vicino: Optional[str] = None
    if (nascita.month, nascita.day) == _INIZI[i]:
        vicino = SEGNI[(i - 1) % 12][0]  # primo giorno: può ancora essere il precedente
    elif (domani.month, domani.day) == _INIZI[(i + 1) % 12]:
        vicino = SEGNI[(i + 1) % 12][0]  # ultimo giorno: può già essere il successivo
    return Segno(codice, nome, elemento, modalita, cuspide=vicino is not None, vicino=vicino)


def compatibilita(nascita_a: date, nascita_b: date) -> Compatibilita:
    """La compatibilità dei segni solari di due persone."""
    a = segno_solare(nascita_a)
    b = segno_solare(nascita_b)
    ia = next(i for i, s in enumerate(SEGNI) if s[0] == a.codice)
    ib = next(i for i, s in enumerate(SEGNI) if s[0] == b.codice)
    d = (ib - ia) % 12
    distanza = min(d, 12 - d)
    aspetto = _ASPETTI[distanza]
    return Compatibilita(
        segno_a=a,
        segno_b=b,
        distanza=distanza,
        aspetto=aspetto,
        relazione_elementi=nome_relazione(a.elemento, b.elemento),
        stessa_modalita=a.modalita == b.modalita,
        armonia=_ARMONIA[aspetto],
        nota=NOTE_ASPETTO[aspetto],
    )


def codici_segni() -> List[str]:
    return [s[0] for s in SEGNI]
