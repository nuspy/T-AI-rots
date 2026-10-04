"""Lo stato sintetico della memoria: poche voci per persona, aggiornate con una chiamata breve, dimenticate dal codice.

**Perché al posto degli embedding.** La memoria di prima (`tarot/memoria.py` + `memoria_retrieval.py`) estraeva i
fatti con un modello che ragionava (4–6 mila token d'uscita a lettura), li vettorizzava e li ritrovava per somiglianza.
In produzione l'embedding non ha mai funzionato e la tabella è rimasta vuota: si pagava l'estrazione per buttarla. Qui
lo stato è piccolo per costruzione — si legge con una chiave primaria e si scrive in poche righe di prompt — e tutto ciò
che può farlo il codice lo fa il codice.

**Tre categorie di voce**:

- `stabile` — un fatto che non cambia da solo (con chi vive, un lutto, una condizione permanente): resta finché chi
  consulta non lo cancella o una lettura non lo smentisce;
- `tema` — una domanda fatta, con la sua data: la scrive il codice dal quesito di ogni lettura, senza chiedere nulla
  al modello;
- `volatile` — una situazione in corso (una scelta da fare, una crisi, un progetto): perde peso col tempo e sparisce
  se nessuna lettura la conferma.

**L'oblio è deterministico** (`dimentica`): ogni categoria ha una vita in giorni dall'ultima conferma (`VITA_GIORNI`)
e un massimo di voci (`MASSIMO`); il peso di una voce volatile scende in linea retta da 1 a 0 lungo la sua vita.
Nessun modello decide cosa dimenticare.

**Dopo ogni lettura completata** (`aggiorna_stato`, in background): una sola chiamata breve **senza ragionamento**
riceve lo stato e il quadro della lettura (il riassunto dell'intervista, non la trascrizione) e risponde con aggiunte,
conferme e rimozioni in JSON. Applicarle (`applica`), scartare la salute senza consenso (art. 9), togliere i doppioni e
dimenticare lo fa il codice. Il prompt è in `docs/proposte-prompt.md`, da approvare con l'operatore.

**Nei prompt** (oracolo, intervista, sintesi) lo stato entra solo con l'interruttore della console
(`ImpostazioniIntervista.memoria_stato_nei_prompt`), spento finché l'operatore non lo approva; entra nella forma delle
memorie di prima (`come_istantanea`, `formatta`), così i prompt non cambiano una parola, con un tetto di caratteri.
"""
from __future__ import annotations

import logging
import re
import secrets
import unicodedata
import uuid
from datetime import date, datetime, timedelta
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence

from ..llm.base import GenerationError
from .llm import genera_json, richiesta

logger = logging.getLogger(__name__)

CATEGORIE = ("stabile", "tema", "volatile")
#: I campi di attinenza, come per le memorie di prima.
CAMPI = ("amore", "lavoro", "salute", "famiglia", "denaro", "spirituale", "altro")

#: Per quanti giorni dall'ultima conferma una voce resta. `None`: finché non la si cancella.
VITA_GIORNI: Dict[str, Optional[int]] = {"stabile": None, "tema": 120, "volatile": 60}
#: Quante voci per categoria, al più: oltre, si tengono quelle confermate più di recente.
MASSIMO: Dict[str, int] = {"stabile": 12, "tema": 6, "volatile": 8}
#: La lunghezza massima del testo di una voce (una frase).
LUNGHEZZA_VOCE = 240
#: Il tetto di caratteri del blocco che entra in un prompt (circa 200 token).
TETTO_CARATTERI = 800

#: Lo spazio dei nomi per gli id UUID che l'istantanea delle memorie richiede (`memoria_retrieval.da_istantanea`).
_SPAZIO_ID = uuid.UUID("6f3c2a5e-1d4b-4e8a-9b7c-0a1d2e3f4a5b")

PROMPT_STATO_MEMORIA = """# Compito: memoria_stato

Aggiorni la memoria breve che TAROTS chat tiene su chi consulta. Ricevi lo stato attuale (voci con un id) e il
quadro di una lettura appena conclusa.
- stabile: un fatto che non cambia da solo (con chi vive, un lutto, una condizione permanente).
- volatile: una situazione in corso che può cambiare (una scelta da fare, una crisi, un progetto).
Aggiungi solo fatti nuovi, detti da chi consulta, utili a una prossima lettura: una frase in terza persona ciascuno.
Conferma gli id ancora veri; rimuovi quelli che la lettura smentisce o dice superati. Non riscrivere il quesito: lo
registra il sistema.
Campi: amore, lavoro, salute, famiglia, denaro, spirituale, altro.

Rispondi SOLO con JSON:
{"aggiungi": [{"categoria": "stabile|volatile", "campo": "<campo>", "testo": "<frase>"}], "conferma": ["<id>"], "rimuovi": ["<id>"], "campo_quesito": "<campo del quesito>"}
"""


# ---- le voci ------------------------------------------------------------------------------------------------------


def _giorno(valore: Any) -> date:
    if isinstance(valore, datetime):
        return valore.date()
    if isinstance(valore, date):
        return valore
    try:
        return date.fromisoformat(str(valore)[:10])
    except ValueError:
        return date.today()


def _normalizza(testo: str) -> str:
    testo = unicodedata.normalize("NFKD", (testo or "").lower())
    testo = "".join(c for c in testo if not unicodedata.combining(c))
    return " ".join(re.findall(r"\w+", testo))


def _campo(valore: Any) -> str:
    campo = str(valore or "").strip().lower()
    return campo if campo in CAMPI else "altro"


def nuova_voce(categoria: str, campo: str, testo: str, *, oggi: date, fonte: str = "lettura") -> Dict[str, Any]:
    """Una voce nuova, con un id breve e casuale (non un UUID: si vede nei prompt dell'aggiornamento)."""
    giorno = oggi.isoformat()
    return {
        "id": secrets.token_hex(3), "categoria": categoria, "campo": _campo(campo),
        "testo": " ".join(str(testo).split())[:LUNGHEZZA_VOCE], "dal": giorno, "visto": giorno, "fonte": fonte,
    }


def valida(voci: Any) -> List[Dict[str, Any]]:
    """Le voci ben formate di un elenco letto dal database o arrivato da un client; il resto si scarta."""
    buone: List[Dict[str, Any]] = []
    for v in voci if isinstance(voci, list) else []:
        if not isinstance(v, dict) or v.get("categoria") not in CATEGORIE or not str(v.get("testo") or "").strip():
            continue
        buone.append({
            "id": str(v.get("id") or secrets.token_hex(3))[:16], "categoria": v["categoria"], "campo": _campo(v.get("campo")),
            "testo": " ".join(str(v["testo"]).split())[:LUNGHEZZA_VOCE],
            "dal": _giorno(v.get("dal")).isoformat(), "visto": _giorno(v.get("visto") or v.get("dal")).isoformat(),
            "fonte": str(v.get("fonte") or "lettura")[:20],
        })
    return buone


def eta_giorni(voce: Dict[str, Any], oggi: date) -> int:
    return max(0, (oggi - _giorno(voce.get("visto"))).days)


def scade_il(voce: Dict[str, Any]) -> Optional[date]:
    """Il giorno in cui la voce si dimentica da sola, se nessuna lettura la conferma prima. `None`: mai."""
    vita = VITA_GIORNI.get(voce.get("categoria", ""))
    if vita is None:
        return None
    return _giorno(voce.get("visto")) + timedelta(days=vita)


def peso(voce: Dict[str, Any], oggi: date) -> float:
    """Da 1 (appena confermata) a 0 (alla fine della sua vita). Una voce senza scadenza pesa sempre 1."""
    vita = VITA_GIORNI.get(voce.get("categoria", ""))
    if vita is None:
        return 1.0
    return max(0.0, 1.0 - eta_giorni(voce, oggi) / vita)


def dimentica(voci: Sequence[Dict[str, Any]], oggi: date) -> List[Dict[str, Any]]:
    """L'oblio, deterministico: via le voci oltre la loro vita, poi al più `MASSIMO` per categoria (restano quelle
    confermate più di recente). L'ordine delle voci rimaste non cambia."""
    vive = [v for v in voci if (scade_il(v) is None or scade_il(v) > oggi)]
    tenute: set = set()
    for categoria, massimo in MASSIMO.items():
        della = sorted((v for v in vive if v["categoria"] == categoria), key=lambda v: (v["visto"], v["dal"]), reverse=True)
        tenute.update(id(v) for v in della[:massimo])
    return [v for v in vive if id(v) in tenute]


def senza_salute(voci: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Le voci senza quelle sulla salute (art. 9 GDPR, senza il consenso `dati_particolari`)."""
    from .consensi import campo_salute

    return [v for v in voci if not campo_salute(v.get("campo", ""))]


def applica(
    voci: Sequence[Dict[str, Any]], aggiornamento: Dict[str, Any], *, oggi: date, quesito: str = "",
    salute_ammessa: bool = False,
) -> List[Dict[str, Any]]:
    """Applica la risposta del modello allo stato: rimozioni, conferme, aggiunte, il quesito come tema, poi l'oblio.

    Tutto ciò che il modello non può decidere lo decide il codice: un id sconosciuto si ignora, una categoria che non
    sia `stabile` o `volatile` si scarta (i temi li scrive il codice), un doppione conferma la voce che c'è invece di
    aggiungerne un'altra, la salute senza consenso non entra (e se c'era, esce).
    """
    stato = [dict(v) for v in valida(list(voci))]
    per_id = {v["id"]: v for v in stato}

    rimuovi = {str(i) for i in (aggiornamento.get("rimuovi") or []) if isinstance(i, (str, int))}
    stato = [v for v in stato if v["id"] not in rimuovi]
    for i in aggiornamento.get("conferma") or []:
        if (v := per_id.get(str(i))) is not None and v["id"] not in rimuovi:
            v["visto"] = oggi.isoformat()

    def aggiungi(categoria: str, campo: str, testo: str) -> None:
        chiave = _normalizza(testo)
        if not chiave:
            return
        for v in stato:
            if v["categoria"] == categoria and _normalizza(v["testo"]) == chiave:
                v["visto"] = oggi.isoformat()
                return
        stato.append(nuova_voce(categoria, campo, testo, oggi=oggi))

    for nuova in aggiornamento.get("aggiungi") or []:
        if not isinstance(nuova, dict) or nuova.get("categoria") not in ("stabile", "volatile"):
            continue
        aggiungi(nuova["categoria"], nuova.get("campo"), str(nuova.get("testo") or ""))

    if quesito.strip():
        aggiungi("tema", aggiornamento.get("campo_quesito"), quesito.strip())

    if not salute_ammessa:
        stato = senza_salute(stato)
    return dimentica(stato, oggi)


# ---- nei prompt ---------------------------------------------------------------------------------------------------


def per_prompt(voci: Sequence[Dict[str, Any]], oggi: date) -> List[Dict[str, Any]]:
    """Le voci nell'ordine in cui entrano in un prompt: le stabili, poi le volatili per peso, poi i temi dal più
    recente. Le voci già scadute non entrano anche se lo stato non è ancora stato ripulito."""
    vive = dimentica(valida(list(voci)), oggi)
    stabili = [v for v in vive if v["categoria"] == "stabile"]
    volatili = sorted((v for v in vive if v["categoria"] == "volatile"), key=lambda v: -peso(v, oggi))
    temi = sorted((v for v in vive if v["categoria"] == "tema"), key=lambda v: v["visto"], reverse=True)
    return stabili + volatili + temi


def _contenuto(voce: Dict[str, Any]) -> str:
    if voce["categoria"] == "tema":
        return f"Ha chiesto: «{voce['testo']}» ({_giorno(voce['visto']).strftime('%d/%m/%Y')})"
    return voce["testo"]


def come_istantanea(
    voci: Sequence[Dict[str, Any]], oggi: date, *, owner_id: int, limite: int = 5, tetto: int = TETTO_CARATTERI,
) -> List[Dict[str, str]]:
    """Lo stato nella forma di `Reading.memorie_recuperate` (`memoria_retrieval.istantanea`): l'intervista e la
    sintesi lo leggono con lo stesso codice e lo stesso prompt delle memorie di prima. `tipo` resta `stabile` o
    `variabile` (le etichette che i prompt conoscono); al più `limite` voci e `tetto` caratteri."""
    risultato: List[Dict[str, str]] = []
    usati = 0
    for v in per_prompt(voci, oggi):
        contenuto = _contenuto(v)
        if len(risultato) >= limite or usati + len(contenuto) > tetto:
            break
        usati += len(contenuto)
        risultato.append({
            "id": str(uuid.uuid5(_SPAZIO_ID, f"{owner_id}:{v['id']}")), "contenuto": contenuto,
            "tipo": "stabile" if v["categoria"] == "stabile" else "variabile", "campo_attinenza": v["campo"],
        })
    return risultato


def formatta(voci: Sequence[Dict[str, Any]], oggi: date, *, limite: int = 5, tetto: int = TETTO_CARATTERI) -> str:
    """Il blocco di testo per l'oracolo, nella forma di `memoria_retrieval.formatta_memorie`."""
    from .memoria_retrieval import da_istantanea, formatta_memorie

    return formatta_memorie(da_istantanea(come_istantanea(voci, oggi, owner_id=0, limite=limite, tetto=tetto)))


# ---- la chiamata al modello ---------------------------------------------------------------------------------------


def messaggio_aggiornamento(voci: Sequence[Dict[str, Any]], *, quesito: str, quadro: str, oggi: date, lang: str) -> str:
    """Il messaggio variabile dell'aggiornamento: data, stato attuale (senza i temi, che il modello non tocca) e il
    quadro della lettura. Mai la trascrizione intera."""
    from .lingue import istruzione_lingua

    righe = [f"- [{v['id']}] {v['categoria']} · {v['campo']}: {v['testo']} (visto il {v['visto']})"
             for v in voci if v["categoria"] != "tema"]
    return (
        f"Data di oggi: {oggi.isoformat()}\n\n"
        f"Stato attuale:\n{chr(10).join(righe) if righe else '(vuoto)'}\n\n"
        f"Nuova lettura\nQuesito: {quesito}\nQuadro emerso dal colloquio: {quadro or '(non disponibile)'}\n\n"
        f"Scrivi i testi delle voci nuove nella lingua di chi consulta. {istruzione_lingua(lang)}"
    )


async def chiedi_aggiornamento(
    provider, voci: Sequence[Dict[str, Any]], *, quesito: str, quadro: str, oggi: date, lang: str = "it",
) -> Optional[Dict[str, Any]]:
    """La risposta del modello, o `None` se non risponde o non manda un oggetto: in quel caso lo stato non si tocca
    (nemmeno il tema, perché senza il campo del quesito non si sa se è salute)."""
    try:
        dati = await genera_json(provider, richiesta(
            [PROMPT_STATO_MEMORIA], messaggio_aggiornamento(voci, quesito=quesito, quadro=quadro, oggi=oggi, lang=lang),
            temperatura=0.2, max_tokens=400,
        ))
    except GenerationError as exc:
        logger.warning("Aggiornamento dello stato della memoria non riuscito: %s", exc)
        return None
    return dati if isinstance(dati, dict) else None


async def aggiorna_stato(
    session_factory: Callable[[], Any], owner_id: int, *, quesito: str, quadro: str, provider, lang: str = "it",
    salute_ammessa: bool = False, oggi: Optional[date] = None,
) -> None:
    """In background dopo una lettura completata: legge lo stato, chiede l'aggiornamento, lo applica e lo salva.

    Va lanciata con `asyncio.create_task()`: un errore qui non deve mai arrivare a una risposta già consegnata.
    """
    from ..domain import memoria_repositories

    oggi = oggi or date.today()
    try:
        async with session_factory() as session:
            voci = await memoria_repositories.stato_di(session, owner_id)
        aggiornamento = await chiedi_aggiornamento(provider, voci, quesito=quesito, quadro=quadro, oggi=oggi, lang=lang)
        if aggiornamento is None:
            return
        async with session_factory() as session:
            # Riletto sotto lock: un'altra lettura finita nel frattempo non deve perdere le sue voci.
            attuali = await memoria_repositories.stato_di(session, owner_id, lock=True)
            await memoria_repositories.salva_stato(session, owner_id, applica(
                attuali, aggiornamento, oggi=oggi, quesito=quesito, salute_ammessa=salute_ammessa,
            ))
            await session.commit()
    except Exception:  # noqa: BLE001 - un errore qui non deve mai propagarsi: solo la traccia
        logger.exception("Aggiornamento dello stato della memoria fallito per l'utente %s", owner_id)


# ---- la conversione delle memorie di prima ------------------------------------------------------------------------


def da_memorie(memorie: Iterable[Any], *, salute_ammessa: bool = False) -> List[Dict[str, Any]]:
    """Le memorie di `user_memories` (le correnti) come voci dello stato: `stabile` resta stabile, `variabile` diventa
    volatile con la data del suo ultimo aggiornamento — se è vecchia, l'oblio la toglie subito, come dev'essere."""
    voci: List[Dict[str, Any]] = []
    for m in memorie:
        giorno = _giorno(getattr(m, "updated_at", None) or getattr(m, "created_at", None) or date.today())
        voce = nuova_voce("stabile" if m.tipo == "stabile" else "volatile", m.campo_attinenza, m.contenuto,
                          oggi=giorno, fonte="conversione")
        voce["dal"] = _giorno(getattr(m, "created_at", None) or giorno).isoformat()
        voci.append(voce)
    return voci if salute_ammessa else senza_salute(voci)
