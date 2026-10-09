"""Le interpretazioni delle carte con una chiamata sola.

Fino alla v8.5 ogni carta girata faceva la sua chiamata al modello (`POST /readings/{id}/reveal/{posizione}`), con il
contesto comune (quesito, quadro, colloquio, persone) ripetuto a ogni carta. Ora **la prima richiesta di svelamento di
una lettura** fa una chiamata sola che interpreta tutte le carte ancora da leggere e risponde in JSON
(`{"carte": [{"posizione": 1, "interpretazione": "…"}, …]}`); il codice divide la risposta (`interpretazione.dividi`)
e scrive ogni testo nella sua carta. Le richieste delle altre posizioni lo trovano già pronto e lo mandano subito,
negli stessi eventi di prima (`carta`, `token`, `fine`): sito e app di prima funzionano senza cambiare nulla.

**Le stesse informazioni di prima, carta per carta.** Il blocco di ogni carta è calcolato come se le carte si
girassero una alla volta, in ordine (`dati_carta`): dignità rispetto alle carte già rivelate *prima di lei*, regole di
coppia con quelle, elenco delle carte già rivelate — esattamente ciò che la chiamata singola riceveva girando quella
carta. Il prompt è quello di `PROMPT_INTERPRETAZIONE` (più lavoro, coppia e sicurezza della relazione come prima), con
in fondo la spiegazione dei blocchi e il formato JSON (`interpretazione.PROMPT_INTERPRETAZIONE_UNICA_FORMATO`).

**Una generazione per lettura.** La chiamata unica gira in un task del processo (`_IN_CORSO`), non dentro la
richiesta: due svelamenti insieme aspettano lo stesso task (una chiamata sola), e un client che chiude la connessione
a metà non butta via un'interpretazione già pagata — il task la scrive comunque. Il ricordo è del processo: in
produzione l'API ha una replica (`deploy/k8s/tarots.yaml`); con più repliche, nel caso raro di due svelamenti della
stessa lettura su repliche diverse nello stesso istante, la chiamata unica si farebbe due volte (nessun dato perso: la
seconda non sovrascrive i testi già scritti).

**Ripieghi.** Risposta illeggibile, errore del fornitore, carte mancanti o vuote: per le sole posizioni senza testo si
torna alla chiamata singola di prima, in streaming, quando quella posizione viene svelata. La chiamata unica si tenta
una volta sola per lettura (`_TENTATE`): un ripiego non la ripete. Con una carta sola da leggere si usa direttamente la
chiamata singola.

**In diretta (9/10/2026).** La chiamata unica ora scrive testo con un'intestazione per carta
(`interpretazione.PROMPT_INTERPRETAZIONE_UNICA_FORMATO`) e arriva in streaming: il task aggiorna una `Diretta` a ogni
frammento, e `POST /readings/{id}/reveal-all` manda a chi guarda il testo di ogni carta mentre il modello lo scrive,
invece di aspettare la fine. Il ragionamento non si mostra (`genera_flusso`). Una carta che si rivela sbagliata a metà
(una formula proibita, una carta dritta detta rovesciata) smette di crescere sullo schermo e alla fine si sostituisce.
"""
from __future__ import annotations

import asyncio
import logging
import uuid
from collections import OrderedDict
from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any, Dict, Iterable, List, Optional, Tuple

from sqlalchemy import select

from ..domain.models import DrawnCard, Reading, User
from ..guards.lettura import uscita_proibita
from ..llm.base import GenerationRequest
from ..tarot import interpretazione
from ..tarot.conoscenza import speciale
from ..tarot.intervista import trascrizione, turni_da
from ..tarot.lettura import dignita_di, doppia_valenza, gia_rivelate, note_di_posizione
from ..tarot.llm import genera_flusso, richiesta
from ..tarot.persone import Persone, blocco_persone
from .deps import get_conoscenza, get_guardrail

logger = logging.getLogger(__name__)


class Diretta:
    """Ciò che la chiamata unica ha scritto finora, carta per carta, leggibile da chi aspetta.

    `testi`: posizione → il testo che si può già mostrare (cresce soltanto). Una carta in `fermate` non cresce più sullo
    schermo: il testo scritto fin qui contiene una formula proibita o dice rovesciata una carta dritta; alla fine la si
    sostituisce. `versione` cresce a ogni aggiornamento: chi aspetta (`aspetta`) si sveglia quando cambia."""

    def __init__(self) -> None:
        self.testi: Dict[int, str] = {}
        self.fermate: set = set()
        self.versione = 0
        self._condizione = asyncio.Condition()

    def aggiorna(self, visibili: Dict[int, Tuple[str, bool]]) -> None:
        for n, (testo, valido) in visibili.items():
            if n in self.fermate:
                continue
            if not valido or uscita_proibita(testo):
                self.fermate.add(n)
                continue
            if len(testo) > len(self.testi.get(n, "")):
                self.testi[n] = testo

    async def segnala(self) -> None:
        async with self._condizione:
            self.versione += 1
            self._condizione.notify_all()

    async def aspetta(self, vista: int, timeout: float) -> bool:
        """Vero se c'è qualcosa di nuovo rispetto alla `versione` `vista`, falso se passa `timeout` senza novità."""
        async with self._condizione:
            try:
                await asyncio.wait_for(self._condizione.wait_for(lambda: self.versione != vista), timeout)
                return True
            except asyncio.TimeoutError:
                return False


#: Le chiamate uniche in corso, per lettura: chi arriva mentre una gira la aspetta invece di farne un'altra.
_IN_CORSO: Dict[uuid.UUID, "asyncio.Task[Dict[int, str]]"] = {}
#: La diretta di ogni chiamata unica avviata (anche finita: chi arriva dopo legge da lì). Stesso ricordo di `_TENTATE`.
_DIRETTE: "OrderedDict[uuid.UUID, Diretta]" = OrderedDict()
#: Le letture per cui la chiamata unica è già stata tentata (riuscita o no): dopo, solo chiamate singole. Un ricordo
#: limitato: una lettura si svela in pochi minuti, cinquemila bastano a coprire quelle in corso.
_TENTATE: "OrderedDict[uuid.UUID, None]" = OrderedDict()
_RICORDO_MASSIMO = 5000


def sistema(categoria: str, *, unica: bool) -> List[str]:
    """I messaggi di sistema dell'interpretazione: le regole di sempre, più lavoro, coppia e sicurezza della relazione
    dove servono. Nella chiamata unica il primo è `PROMPT_INTERPRETAZIONE_UNICA` (le stesse regole, «# Compito:
    interpretazione_unica» per il registro dei consumi) e l'ultimo spiega i blocchi e il formato JSON."""
    parti = [interpretazione.PROMPT_INTERPRETAZIONE_UNICA if unica else interpretazione.PROMPT_INTERPRETAZIONE]
    # Le interpretazioni delle carte sono brevi e hanno le loro regole: nelle letture speciali ricevono in più solo
    # ciò che è specifico del tipo di lettura.
    if categoria == "lavoro":
        parti.append(interpretazione.PROMPT_INTERPRETAZIONE_LAVORO)
    if speciale(categoria):
        parti.append(interpretazione.PROMPT_INTERPRETAZIONE_RELAZIONE)
        specifiche = get_guardrail().istruzioni_per("interpretazione", categoria, solo_categoria=True)
        if specifiche:
            parti.append("# Regole di sicurezza della relazione\n\n" + "\n\n".join(specifiche))
    if unica:
        parti.append(interpretazione.PROMPT_INTERPRETAZIONE_UNICA_FORMATO)
    return parti


def contesto_comune(
    lettura: Reading, stesa: Dict[str, Any], persone: Optional[Persone], user: Optional[User],
) -> Dict[str, Any]:
    """Ciò che vale per tutte le carte: si scrive una volta sola nella chiamata unica."""
    return dict(
        stesa=stesa,
        quesito=lettura.question,
        contesto=lettura.context_summary or "",
        colloquio=trascrizione(turni_da(lettura.turns)),
        persone=blocco_persone(persone, get_conoscenza()) if persone else "",
        registro=user.registro_linguistico if user else "",
    )


def _vista(lettura: Reading, fino_a: int) -> SimpleNamespace:
    """La lettura come la vede chi consulta quando gira la carta in posizione `fino_a`: rivelate lei e quelle prima.

    Le carte si rivelano in ordine di posizione (`lettura.prossima_da_rivelare`), quindi è lo stato che la chiamata
    singola trovava girando quella carta, anche quando la chiamata unica le interpreta tutte in anticipo."""
    return SimpleNamespace(cards=[
        SimpleNamespace(
            posizione=c.posizione, card_id=c.card_id, rovescio=c.rovescio, calcolata=c.calcolata,
            rivelata=c.posizione <= fino_a,
        )
        for c in lettura.cards
    ])


def dati_carta(
    lettura: Reading, stesa: Dict[str, Any], carta: DrawnCard, lang: str, soggetti: Optional[Dict[int, str]],
) -> Dict[str, Any]:
    """I valori di una carta per `interpretazione.messaggio` / `messaggio_unico`: gli stessi per le due chiamate."""
    conoscenza = get_conoscenza()
    n = carta.posizione
    vista = _vista(lettura, n)
    return dict(
        carta=conoscenza.carta(carta.card_id),
        rovescio=carta.rovescio,
        posizione=conoscenza.posizione(stesa, n),
        dignita=dignita_di(vista, stesa, conoscenza, solo_rivelate=True).get(n),
        precedenti=gia_rivelate(vista, stesa, conoscenza, n, lang),
        note=note_di_posizione(stesa, n, [c.posizione for c in vista.cards if c.rivelata and c.posizione != n]),
        doppia_valenza=doppia_valenza(lettura, carta),
        nomi=(conoscenza.nome_carta(carta.card_id, lang), conoscenza.nome_posizione(stesa, n, lang)),
        soggetto=(soggetti or {}).get(n, ""),
    )


def prudente(carta: Dict[str, Any], rovescio: bool) -> str:
    """Il significato del mazzo, al posto di un testo che il filtro delle formule proibite ha fermato."""
    return carta.get("rovescio" if rovescio else "dritto") or ""


@dataclass
class Preparata:
    """La chiamata unica pronta da mandare: la richiesta, le posizioni che copre e le carte per il testo prudente."""

    reading_id: uuid.UUID
    posizioni: List[int]
    req: GenerationRequest
    carte: Dict[int, Tuple[Dict[str, Any], bool]] = field(default_factory=dict)
    #: La lingua della risposta: decide le radici con cui si riconosce una carta dritta detta rovesciata.
    lang: str = "it"


def prepara(
    reading_id: uuid.UUID, carte: Iterable[Tuple[DrawnCard, Dict[str, Any]]], *, categoria: str,
    comune: Dict[str, Any], lang: str,
) -> Preparata:
    """La chiamata unica per `carte` (coppie carta, `dati_carta`), in ordine di posizione."""
    ordinate = sorted(carte, key=lambda coppia: coppia[0].posizione)
    domanda = interpretazione.messaggio_unico(carte=[d for _, d in ordinate], lang=lang, **comune)
    return Preparata(
        reading_id=reading_id,
        posizioni=[c.posizione for c, _ in ordinate],
        req=richiesta(
            sistema(categoria, unica=True), domanda, temperatura=0.7,
            max_tokens=interpretazione.tetto_unica(len(ordinate)),
        ),
        carte={c.posizione: (d["carta"], d["rovescio"]) for c, d in ordinate},
        lang=lang,
    )


def avvia(preparata: Preparata, provider: Any, fabbrica: Any) -> "Optional[asyncio.Task[Dict[int, str]]]":
    """Il task della chiamata unica di questa lettura: quello già in corso, o uno nuovo.

    `None` quando non serve: la chiamata unica è già stata tentata (si torna alle singole) o resta una carta sola.
    Nessun `await` fra il controllo e la creazione: due richieste della stessa lettura non ne avviano due."""
    rid = preparata.reading_id
    in_corso = _IN_CORSO.get(rid)
    if in_corso is not None:
        return in_corso
    if rid in _TENTATE or len(preparata.posizioni) < 2:
        return None
    _TENTATE[rid] = None
    while len(_TENTATE) > _RICORDO_MASSIMO:
        _TENTATE.popitem(last=False)
    diretta = _DIRETTE[rid] = Diretta()
    while len(_DIRETTE) > _RICORDO_MASSIMO:
        _DIRETTE.popitem(last=False)
    task = asyncio.create_task(_genera_e_salva(preparata, provider, fabbrica, diretta))
    _IN_CORSO[rid] = task
    task.add_done_callback(lambda _t: _IN_CORSO.pop(rid, None))
    return task


def in_corso(reading_id: uuid.UUID) -> "Optional[asyncio.Task[Dict[int, str]]]":
    return _IN_CORSO.get(reading_id)


def diretta(reading_id: uuid.UUID) -> Optional[Diretta]:
    """La diretta della chiamata unica di questa lettura, se è stata avviata."""
    return _DIRETTE.get(reading_id)


def risultato(task: "Optional[asyncio.Task[Dict[int, str]]]") -> Dict[int, str]:
    """I testi del task finito; vuoto se non c'è, se è stato annullato o è fallito."""
    if task is None or not task.done() or task.cancelled() or task.exception() is not None:
        return {}
    return task.result()


def dimentica() -> None:
    """Svuota i ricordi del processo (per i test)."""
    _IN_CORSO.clear()
    _TENTATE.clear()
    _DIRETTE.clear()


async def _genera_e_salva(
    preparata: Preparata, provider: Any, fabbrica: Any, diretta: Optional[Diretta] = None,
) -> Dict[int, str]:
    """La chiamata unica: genera in streaming (aggiornando la `diretta`), divide, filtra e scrive. Non solleva: un
    errore vuol dire «nessun testo», e le posizioni si leggeranno con la chiamata singola."""
    rid = preparata.reading_id
    diretta = diretta or Diretta()
    orientamenti = {n: rovescio for n, (_carta, rovescio) in preparata.carte.items()}
    grezzo = ""
    try:
        async for pezzo in genera_flusso(provider, preparata.req):
            grezzo += pezzo
            diretta.aggiorna(interpretazione.in_diretta(
                grezzo, preparata.posizioni, orientamenti=orientamenti, lang=preparata.lang,
            ))
            await diretta.segnala()
    except Exception as exc:  # noqa: BLE001 - errori del fornitore e di rete
        logger.warning("Chiamata unica delle interpretazioni non riuscita (lettura %s): %s", rid, exc)
        # Le carte già chiuse prima dell'errore valgono; l'ultima, a metà, no.
        grezzo = interpretazione.senza_ultimo_blocco(grezzo)
    scarti: Dict[int, str] = {}
    divise = interpretazione.dividi_testo(
        grezzo, preparata.posizioni, lang=preparata.lang, scarti=scarti, orientamenti=orientamenti,
    )
    mancanti = [n for n in preparata.posizioni if n not in divise]
    if mancanti:
        logger.warning(
            "Chiamata unica della lettura %s senza le posizioni %s (%s): per quelle si torna alla chiamata singola",
            rid, mancanti, "; ".join(f"{n}: {m}" for n, m in sorted(scarti.items())) or "mancanti o vuote",
        )
    testi: Dict[int, str] = {}
    for n, testo in divise.items():
        if uscita_proibita(testo):
            # Il guardrail leggero delle carte: una formula proibita non arriva allo schermo.
            carta, rovescio = preparata.carte[n]
            testo = prudente(carta, rovescio)
        if testo:
            testi[n] = testo
    if testi:
        try:
            await _salva(fabbrica, rid, testi)
        except Exception:  # noqa: BLE001 - ogni richiesta scrive comunque il testo della sua posizione
            logger.warning("Interpretazioni della lettura %s non salvate", rid, exc_info=True)
    return testi


async def _salva(fabbrica: Any, reading_id: uuid.UUID, testi: Dict[int, str]) -> None:
    """Scrive i testi nelle carte che non ne hanno ancora uno: un ripiego già arrivato non si sovrascrive."""
    async with fabbrica() as s:
        carte = (await s.execute(
            select(DrawnCard)
            .where(DrawnCard.reading_id == reading_id, DrawnCard.posizione.in_(list(testi)))
            .with_for_update()
        )).scalars().all()
        for c in carte:
            if not c.interpretazione:
                c.interpretazione = testi[c.posizione]
        await s.commit()


async def leggi(fabbrica: Any, reading_id: uuid.UUID, posizioni: Iterable[int]) -> Dict[int, str]:
    """Le interpretazioni già scritte per queste posizioni (da un'altra richiesta o da un task finito nel frattempo)."""
    posizioni = list(posizioni)
    if not posizioni:
        return {}
    async with fabbrica() as s:
        righe = (await s.execute(
            select(DrawnCard.posizione, DrawnCard.interpretazione)
            .where(DrawnCard.reading_id == reading_id, DrawnCard.posizione.in_(posizioni))
        )).all()
    return {n: testo for n, testo in righe if testo}
