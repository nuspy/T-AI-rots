"""Il percorso di una lettura, dall'apertura al responso.

| passo | endpoint | stato dopo |
|---|---|---|
| apertura, pagamento, disclaimer | `POST /readings` | `intervista` |
| una domanda di contesto per volta | `POST /readings/{id}/interview` | `ventaglio` a fine intervista |
| mescolamento e ventaglio | `POST /readings/{id}/fan` | `scelta` |
| una carta per volta | `POST /readings/{id}/pick` | `rivelazione` a carte scelte |
| rivelazione e lettura immediata (SSE) | `POST /readings/{id}/reveal/{pos}` | `sintesi` all'ultima |
| tutte le carte insieme, una chiamata (SSE) | `POST /readings/{id}/reveal-all` | `sintesi` |
| responso finale CAG, col guardrail (SSE) | `POST /readings/{id}/synthesis` | `completata` |

**Il pagamento è all'apertura.** Una lettura consuma un credito o una lettura
giornaliera dell'abbonamento nel momento in cui nasce, nella stessa
transazione: nessuna lettura esiste senza essere stata pagata, e nessun
credito sparisce senza una lettura a cui attribuirlo. Se l'intervista rivela
una crisi, il credito si restituisce.

**Lo streaming apre sessioni proprie.** La sessione della richiesta si chiude
quando l'endpoint restituisce la risposta, mentre il flusso SSE continua: le
scritture finali passano da una sessione nuova (`SessionFactory`), come in
Personalities.
"""
from __future__ import annotations

import asyncio
import json
import logging
import secrets
import uuid
from datetime import date
from typing import Any, AsyncIterator, Dict, List, Literal, Optional

from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi.responses import StreamingResponse
from lanterna.rete import ip_client
from pydantic import BaseModel, Field, field_validator, model_validator
from sqlalchemy import delete, select
from sqlalchemy.orm.attributes import set_committed_value

from ...auth.dependencies import COOKIE_ANONIMO, CurrentUser, DbSession, OptionalUser
from ...billing.credits import CreditiInsufficienti, RegistroCrediti
from ...billing.plans import GestoreAbbonamenti
from ...billing.quote import COSTO_LETTURA
from ...domain import consent_repositories, deck_repositories, memoria_repositories
from ...domain.base import utcnow
from ...domain.models import InterviewTurn, Reading, User
from ...analytics import eventi as analytics
from ...domain.repositories import AuditRepository, ReadingRepository
from ...domain.share_models import ShareImage
from ...domain.session import SessionFactory
from ...guards.lettura import giudica, segnale_di_crisi, uscita_proibita
from ...llm.base import GenerationError, supporta_embedding
from ...llm.compiti import Compito
from ...settings import get_settings
from ...tarot import cag, eta_minima, interpretazione
from ...tarot.condivisione import pulisci_testo
from ...tarot.conoscenza import speciale
from ...domain.impostazioni_repositories import correnti_intervista
from ...tarot.intervista import IntervistaNonRiuscita, prossimo_passo, profilo_da, riassumi, trascrizione, turni_da
from ...tarot.memoria import estrai_e_salva
from ...tarot.stato_memoria import aggiorna_stato, come_istantanea
from ...tarot.teaser import genera_teaser
from ...tarot.memoria_retrieval import da_istantanea, formatta_per_sintesi, istantanea, rilevanti
from ...tarot.lettura import (
    StatoNonValido, dignita_di, posa, posa_manuale, prevalenze_di, prossima_da_rivelare, wirth,
)
from ...tarot.llm import genera_flusso, genera_testo, richiesta
from ...tarot.numerologia import carta_dell_anima, carta_dell_anno
from ...tarot.consensi import trans_ammesso
from ...tarot.persone import (
    LUNGHEZZA_COGNOME, LUNGHEZZA_GENERE_ALTRO, LUNGHEZZA_NOME, Persone, blocco_compatibilita,
    blocco_persone, compatibilita_json, da_json, mancanti, parole_neutre, pulisci, soggetto_testo,
)
from ...tarot.shuffle import mescola
from ...tarot.lingue import in_lingua, lingua, rileva_lingua
from ...tarot.testi import (
    AGGIUNTA_ETICHETTA, AIUTO, CREDITI_ESAURITI, DISCLAIMER, INTERPRETAZIONE_NON_DISPONIBILE,
    SALDO_NEGATIVO,
    MODELLO_NON_DISPONIBILE, PARTNER_MANCANTE, PARTNER_NON_AMMESSO,
    PROFILO_INCOMPLETO, RESPONSO_BLOCCATO, RESPONSO_NON_GENERATO,
)
from .privacy import errore_eta_anonima, verifica_eta
from .. import rivelazione
from ..deps import (
    aggiorna_assegnazioni, get_conoscenza, get_guardrail, provider_per, verifica_modello,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["letture"])


# ---- modelli di richiesta ---------------------------------------------------


class PersonaIn(BaseModel):
    """L'altra persona di una lettura di compatibilità o di coppia.

    Il cognome è facoltativo e resta nella scheda e nello storico: non arriva
    mai ai prompt. Nome e genere libero sono testi che finiscono in un prompt,
    quindi si riducono a ciò che può stare in un nome (`persone.pulisci`).
    """

    nome: str = Field(min_length=1, max_length=LUNGHEZZA_NOME * 2)
    cognome: Optional[str] = Field(default=None, max_length=LUNGHEZZA_COGNOME * 2)
    genere: str = Field(pattern="^(donna|uomo|non_binario|altro|non_dice)$")
    genere_altro: Optional[str] = Field(default=None, max_length=LUNGHEZZA_GENERE_ALTRO * 2)
    trans: bool = False
    nascita: date

    @field_validator("nascita")
    @classmethod
    def _nascita_sensata(cls, valore: date) -> date:
        if valore > date.today() or valore.year < 1900:
            raise ValueError("data di nascita non valida")
        return valore

    @model_validator(mode="after")
    def _testi_utilizzabili(self) -> "PersonaIn":
        if not pulisci(self.nome, LUNGHEZZA_NOME):
            raise ValueError("il nome non è utilizzabile")
        if self.genere == "altro" and not pulisci(self.genere_altro, LUNGHEZZA_GENERE_ALTRO):
            raise ValueError("con «altro» serve un testo")
        return self


class ManualCardIn(BaseModel):
    """Una carta indicata a mano (v5, "Interpreta i miei tarocchi"): il mazzo è fisico, già estratto."""

    posizione: int = Field(ge=1, le=99)
    card_id: str = Field(min_length=1, max_length=40)


class NuovaLettura(BaseModel):
    spread_id: str = Field(min_length=1, max_length=40)
    question: str = Field(min_length=3, max_length=1000)
    lang: str = Field(default="it", max_length=5)
    #: Solo per le letture di compatibilità e di coppia.
    partner: Optional[PersonaIn] = None
    #: «Ricorda»: si salva il partner nel profilo per precompilare il modulo.
    ricorda_partner: bool = False
    #: Presente solo per "Interpreta i miei tarocchi": una carta per ogni posizione non calcolata
    #: della stesa, già estratta a mano. Con questo campo la lettura salta ventaglio/scelta e passa
    #: direttamente alla rivelazione, non appena l'intervista si conclude.
    manual_cards: Optional[List[ManualCardIn]] = None
    #: Il mazzo con cui leggere (v5, Fase B): lo slug di un `Deck`. Assente o nullo: il predefinito
    #: (il Thoth), sempre posseduto, nessuna verifica necessaria.
    deck_id: Optional[str] = Field(default=None, max_length=40)
    #: Oltre un limite dell'abbonamento (v9, Fase 2b) la lettura non parte da sola: il primo tentativo risponde 402
    #: `limite_superato`, e il secondo porta il consenso — `condono` (una delle letture regalate del periodo) o
    #: `credito` (un credito del saldo). Se restano condoni si usa sempre un condono: mai un credito quando c'è il
    #: regalo.
    oltre_limite: Optional[str] = Field(default=None, pattern="^(condono|credito)$")
    #: v9.5: con quale versione della lettura è nata (prova 90/10) e da dove; per confrontare gli abbandoni.
    variante: Optional[Literal["classica", "chat"]] = None
    piattaforma: Optional[Literal["web", "android", "ios"]] = None


class AggiuntaIntervista(BaseModel):
    """v9.5: ciò che chi consulta dice liberamente («Voglio dire qualcosa di libero»), durante l'intervista o dopo,
    prima delle carte."""
    testo: str = Field(min_length=1, max_length=2000)


class RispostaIntervista(BaseModel):
    #: Vuota alla prima chiamata, che chiede la prima domanda.
    risposta: Optional[str] = Field(default=None, max_length=2000)
    #: «No, basta così» (v8.5): dopo il minimo di domande chi consulta chiude l'intervista e passa alle carte.
    #: La domanda facoltativa rimasta senza risposta si toglie dal colloquio.
    basta: bool = False
    #: v9.5: falso = si salva la risposta e NON si chiede subito la domanda successiva: chi consulta sceglie fra
    #: «Passa alla lettura», «Voglio dire qualcosa di libero», «Voglio rispondere a un'altra domanda». Vero (il
    #: predefinito) = come prima, per le app già installate.
    continua: bool = True
    #: v9.5: «Voglio rispondere a un'altra domanda»: l'oracolo DEVE farne una (fino al massimo), non chiudere.
    altra: bool = False


class Scelta(BaseModel):
    slot: int = Field(ge=0, le=77)


class TaglioMazzo(BaseModel):
    #: Dove chi consulta ha tagliato il mazzo: da 0 a 1 lungo il mazzo. Assente
    #: se non ha tagliato.
    taglio: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class Diario(BaseModel):
    esito: str = Field(pattern="^(si|in_parte|no)$")
    nota: Optional[str] = Field(default=None, max_length=2000)


class Condivisione(BaseModel):
    attiva: bool = True
    #: Il testo personalizzato del post. Assente = non toccare quello già scritto;
    #: stringa vuota = toglierlo.
    testo: Optional[str] = Field(default=None, max_length=400)


# ---- utilità ----------------------------------------------------------------


def _sse(evento: str, dati: Dict[str, Any]) -> bytes:
    return f"event: {evento}\ndata: {json.dumps(dati, ensure_ascii=False)}\n\n".encode("utf-8")


def _flusso(generatore: AsyncIterator[bytes]) -> StreamingResponse:
    return StreamingResponse(
        generatore,
        media_type="text/event-stream",
        # Senza, un proxy (nginx, Istio) accumula il flusso e lo consegna
        # tutto alla fine: lo streaming esiste sul server e non nel browser.
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def _stesa_o_404(spread_id: str) -> Dict[str, Any]:
    stesa = get_conoscenza().stesa(spread_id)
    if stesa is None:
        raise HTTPException(status_code=404, detail=f"Stesa «{spread_id}» sconosciuta")
    return stesa


async def _lettura_o_404(
    repo: ReadingRepository, user: Optional[User], reading_id: uuid.UUID, *,
    lock: bool = False, anon_id: Optional[str] = None,
) -> Reading:
    """`anon_id` (v6, Fase F): quando presente, la lettura può anche essere quella di un visitatore
    anonimo (nessun `user`) — vedi `ReadingRepository.get_flex()`. Senza, il comportamento è quello
    di sempre: solo il proprietario autenticato."""
    if anon_id is not None or user is None:
        lettura = await repo.get_flex(reading_id, owner=user, anon_id=anon_id, lock=lock)
    else:
        lettura = await (repo.get_for_update if lock else repo.get)(user, reading_id)
    if lettura is None:
        raise HTTPException(status_code=404, detail="Lettura non trovata")
    return lettura


def _conflitto(msg: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)


def _profilo(user: User) -> str:
    if user.birth_date is None:
        return ""
    conoscenza = get_conoscenza()
    anima = conoscenza.maggiore(carta_dell_anima(user.birth_date))
    anno = conoscenza.maggiore(carta_dell_anno(user.birth_date, date.today().year))
    return profilo_da({
        "Carta dell'anima": anima["nome_it"],
        f"Carta dell'anno {date.today().year}": anno["nome_it"],
    })


def _errore_422(motivo: str, testo: Dict[str, str], lang: str, **extra: Any) -> HTTPException:
    return HTTPException(
        status_code=422,
        detail={"motivo": motivo, "messaggio": in_lingua(testo, lang), **extra},
    )


def _istantanea_persone(user: User, partner: PersonaIn, *, dati_particolari: bool = False) -> Dict[str, Any]:
    """Le due persone come stanno adesso: si salvano con la lettura.

    È una copia: se poi l'utente corregge la scheda, la lettura resta coerente
    con il responso. Il cognome sta qui e non va oltre lo storico.

    La casella «persona trans» (di chi consulta e del partner) è un dato dell'art. 9 GDPR: entra nell'istantanea
    solo con il consenso `dati_particolari` di chi consulta (GDPR, Fase 1). Senza, non si salva nemmeno.
    """
    assert user.birth_date is not None
    return {
        "v": 1,
        "tu": {
            "genere": user.gender, "genere_altro": user.gender_custom,
            "trans": trans_ammesso(dati_particolari, user.is_trans), "nascita": user.birth_date.isoformat(),
        },
        "partner": {
            "nome": pulisci(partner.nome, LUNGHEZZA_NOME),
            "cognome": pulisci(partner.cognome, LUNGHEZZA_COGNOME) or None,
            "genere": partner.genere,
            "genere_altro": pulisci(partner.genere_altro, LUNGHEZZA_GENERE_ALTRO) or None,
            "trans": trans_ammesso(dati_particolari, partner.trans),
            "nascita": partner.nascita.isoformat(),
        },
    }


async def _dati_particolari(session, user: Optional[User]) -> bool:
    """Il consenso alle categorie particolari (art. 9) di chi consulta: senza, niente «persona trans» al modello."""
    return await consent_repositories.accettato(session, user.id if user else None, "dati_particolari")


async def _persone_per_prompt(session, lettura: Reading, user: Optional[User]) -> Optional[Persone]:
    """Le persone della lettura come le vede il modello: la casella «persona trans» solo con il consenso attuale —
    un'istantanea presa prima della Fase 1, o un consenso revocato a metà lettura, non la fanno passare."""
    if not lettura.persone:
        return None
    return da_json(lettura.persone, trans=await _dati_particolari(session, user))


def _persone_dell_apertura(
    user: User, payload: "NuovaLettura", categoria: str, lang: str, *, dati_particolari: bool = False,
) -> Optional[Dict[str, Any]]:
    """Valida partner e scheda per il tipo di lettura e ne fa l'istantanea.

    `None` per la lettura standard e per quella di lavoro. Per le speciali: 422 `partner_mancante`,
    `partner_non_ammesso` o `profilo_incompleto` (con l'elenco di ciò che manca
    nella scheda: il frontend lo chiede e riprova).
    """
    if not speciale(categoria):
        if payload.partner is not None:
            raise _errore_422("partner_non_ammesso", PARTNER_NON_AMMESSO, lang)
        return None
    if payload.partner is None:
        raise _errore_422("partner_mancante", PARTNER_MANCANTE, lang)
    da_completare = mancanti(user)
    if da_completare:
        raise _errore_422("profilo_incompleto", PROFILO_INCOMPLETO, lang, mancanti=da_completare)
    return _istantanea_persone(user, payload.partner, dati_particolari=dati_particolari)


def carta_json(conoscenza, c, *, completa: bool = False, manuale: bool = False) -> Dict[str, Any]:
    dati: Dict[str, Any] = {
        "posizione": c.posizione,
        "calcolata": c.calcolata,
        "rivelata": c.rivelata,
    }
    # In una lettura manuale l'identità è già nota (il mazzo è fisico, in mano a chi consulta): si
    # mostra da subito, indipendentemente da `rivelata` — che resta il ritmo con cui arriva
    # l'interpretazione, invariato rispetto a una lettura normale.
    if c.rivelata or manuale:
        dati.update({
            "carta": conoscenza.carta_pubblica(c.card_id, completa=completa),
            "rovescio": c.rovescio,
            # Solo a carta girata: la chiamata unica scrive in anticipo anche le interpretazioni delle carte ancora
            # coperte (in una lettura manuale la carta si vede da subito, la sua lettura no).
            "interpretazione": c.interpretazione if c.rivelata else None,
        })
    return dati


def _soggetti(stesa: Dict[str, Any], persone: Optional[Persone]) -> Optional[Dict[int, str]]:
    """Di chi parla ogni posizione, in testo: lo decide il codice dai dati della stesa."""
    if persone is None:
        return None
    return {p["n"]: soggetto_testo(p.get("soggetto"), persone) for p in stesa["posizioni"]}


#: Il tetto dei token del responso. Misurato il 4/10/2026 senza ragionamento (Nemotron 3.5 Lightning): la tre carte
#: scrive 950–1 750 token e si fermava a 1 800 una volta su cinque; la compatibilità 1 400–1 730 su 2 200, una volta
#: troncata; la croce celtica si fermava sempre a 1 800, a metà di una sezione. È un tetto, non un obiettivo: chi ha
#: finito si ferma, e i token in più si pagano solo quando prima il responso sarebbe stato tagliato.
TETTO_SINTESI = 2600
#: In più per le letture speciali (una sezione e i nomi dei due) e per le stese lunghe (più di cinque posizioni).
TETTO_SINTESI_SPECIALE = 400
TETTO_SINTESI_STESA_LUNGA = 600


def _tetto_sintesi(stesa: Dict[str, Any], categoria: str) -> int:
    tetto = TETTO_SINTESI
    if speciale(categoria):
        tetto += TETTO_SINTESI_SPECIALE
    if len(stesa.get("posizioni") or []) > 5:
        tetto += TETTO_SINTESI_STESA_LUNGA
    return tetto


async def _memorie_per_sintesi(session: DbSession, owner_id: int, snapshot: List[Dict[str, Any]]) -> str:
    """Il blocco «Memoria» per la sintesi (v6, Fase C): le prime 3 dell'istantanea presa all'apertura,
    con il "prima" di ogni variabile che ha una versione precedente — per il confronto che la sintesi
    fa esplicitamente quando pertinente (vedi `cag._CORPO_SINTESI`)."""
    voci = snapshot[:3]
    if not voci:
        return ""
    precedenti: Dict[str, str] = {}
    for v in voci:
        if v["tipo"] != "variabile":
            continue
        try:
            catena_ = await memoria_repositories.catena(session, owner_id, uuid.UUID(v["id"]))
        except Exception:  # noqa: BLE001 - il confronto prima/dopo è un arricchimento, non un requisito
            continue
        if len(catena_) > 1:
            precedenti[v["id"]] = catena_[-2].contenuto
    return formatta_per_sintesi(voci, precedenti)


def lettura_json(lettura: Reading, *, dettaglio: bool = True) -> Dict[str, Any]:
    conoscenza = get_conoscenza()
    stesa = conoscenza.stesa(lettura.spread_id) or {}
    categoria = conoscenza.categoria_di(stesa) if stesa else "standard"
    dati: Dict[str, Any] = {
        "id": str(lettura.id),
        "spread_id": lettura.spread_id,
        "stesa": stesa.get("nome"),
        # Il nome della stesa in inglese e nelle lingue con nomi propri: lo storico
        # lo mostra nella lingua dell'interfaccia (`nomeStesa` sul frontend).
        "stesa_nomi": conoscenza.stesa_pubblica(stesa)["nomi"] if stesa else {},
        "categoria": categoria,
        "stile": stesa.get("stile"),
        "question": lettura.question,
        "status": lettura.status,
        "lang": lettura.lang,
        "consumo": lettura.consumo,
        "created_at": lettura.created_at.isoformat() if lettura.created_at else None,
        "completed_at": lettura.completed_at.isoformat() if lettura.completed_at else None,
        "feedback": lettura.feedback,
        "shared": bool(lettura.share_token),
        "manuale": lettura.manuale,
        "mazzo": deck_repositories.slug_immagini(lettura.mazzo),
    }
    if not dettaglio:
        rivelate = [c for c in lettura.cards if c.rivelata]
        dati["carte"] = [conoscenza.carta(c.card_id)["nome_it"] for c in rivelate]
        # Nell'elenco basta il nome del partner: il resto è nel dettaglio.
        dati["partner_nome"] = ((lettura.persone or {}).get("partner") or {}).get("nome")
        return dati
    persone = da_json(lettura.persone)
    dati["persone"] = lettura.persone  # col cognome: solo al proprietario
    dati["compatibilita"] = compatibilita_json(persone, conoscenza) if persone else None
    dati.update({
        "context_summary": lettura.context_summary,
        "interview": [
            {"ruolo": t.ruolo, "testo": t.testo, "ordine": t.ordine} for t in lettura.turns
        ],
        "cards": [carta_json(conoscenza, c, manuale=lettura.manuale) for c in lettura.cards],
        "slot_count": len(lettura.deck_state or []) or None,
        "picked_slots": [c.slot for c in lettura.cards if c.slot is not None],
        "commitment": lettura.commitment,
        # Il sale si rivela solo a lettura conclusa: prima permetterebbe di
        # ricostruire il mazzo provando le permutazioni.
        "deck_salt": lettura.deck_salt if lettura.status == "completata" else None,
        "deck_state": lettura.deck_state if lettura.status == "completata" else None,
        "synthesis": lettura.synthesis,
        "guard_outcome": lettura.guard_outcome,
        "share_token": lettura.share_token,
        "share_text": lettura.share_text,
        "feedback_note": lettura.feedback_note,
        "disclaimer": in_lingua(DISCLAIMER, lettura.lang),
        "dignita": (
            dignita_di(lettura, stesa, conoscenza, solo_rivelate=True) if stesa else {}
        ),
    })
    return dati


# ---- apertura ---------------------------------------------------------------


async def _consumo_con_limiti(
    session, gestore: GestoreAbbonamenti, user_id: int, diritti, oltre_limite: Optional[str], lang: str,
) -> tuple[str, Optional[str]]:
    """Da dove si paga la lettura, e quale limite dell'abbonamento ha superato (v9, Fase 2b, `billing/abbonamenti.py`).

    Entro i limiti: `quota`. Oltre, senza consenso: 402 `limite_superato` col limite, le letture fatte nel periodo, i
    condoni rimasti e il saldo — il sito lo mostra e chiede. Col consenso: `condono` finché ce ne sono, poi `credito`.
    """
    from ...billing import abbonamenti as gestione

    abbonamento = await gestore.abbonamento_di(user_id)
    if gestione.ha_letture_comprese(abbonamento, diritti):
        # Il lock sulla riga dell'utente prima di contare: due letture aperte insieme non prendono lo stesso condono.
        await RegistroCrediti(session)._blocca(user_id)
    valutazione = await gestione.valuta_lettura(session, user_id, abbonamento, diritti)
    if valutazione.consumo is not None:
        return valutazione.consumo, None
    superato = valutazione.superato
    assert superato is not None
    if oltre_limite is not None and valutazione.condoni_rimasti > 0:
        return "condono", superato.nome
    if oltre_limite == "credito":
        return "credito", superato.nome
    raise HTTPException(
        status_code=status.HTTP_402_PAYMENT_REQUIRED,
        detail={**valutazione.dettaglio(), "messaggio": in_lingua(gestione.LIMITE_SUPERATO, lang)},
    )


@router.post("/readings", status_code=status.HTTP_201_CREATED)
async def apri(payload: NuovaLettura, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    """Apre una lettura e la paga.

    402 se non c'è né quota né credito: il frontend propone l'acquisto prima
    di cominciare, invece che a metà.
    """
    stesa = _stesa_o_404(payload.spread_id)
    # La lingua della lettura è quella del quesito, non quella dell'interfaccia:
    # si ricava qui, una volta, e si salva. Ogni nuovo quesito la rinnova.
    lang = rileva_lingua(payload.question, fallback=payload.lang)
    # L'età minima (GDPR, Fase 1): senza la conferma, o con una data di nascita sotto il minimo, niente lettura.
    verifica_eta(user, payload.lang)
    conoscenza = get_conoscenza()
    categoria = conoscenza.categoria_di(stesa)
    persone = _persone_dell_apertura(
        user, payload, categoria, lang, dati_particolari=await _dati_particolari(session, user),
    )

    # Il mazzo (v5, Fase B): assente o nullo, il predefinito — nessuna verifica. Indicato, deve
    # esistere ed essere posseduto (il predefinito lo è sempre da chiunque). Si verifica qui, prima
    # di addebitare: un mazzo non posseduto non deve costare un credito prima di fallire.
    mazzo_scelto = None
    if payload.deck_id:
        mazzo_scelto = await deck_repositories.per_slug(session, payload.deck_id)
        if mazzo_scelto is None or not mazzo_scelto.attivo_ora:
            raise HTTPException(status_code=404, detail={"motivo": "mazzo_sconosciuto", "messaggio": "Mazzo non trovato."})
        if not await deck_repositories.possiede(session, user.id, mazzo_scelto):
            raise HTTPException(status_code=403, detail={
                "motivo": "mazzo_non_posseduto", "messaggio": "Non possiedi ancora questo mazzo.",
            })

    # "Interpreta i miei tarocchi" (v5): il mazzo è fisico, già estratto — si valida qui, con un
    # messaggio utile, prima di addebitare qualunque cosa (stesso principio delle altre verifiche
    # sopra: un errore di forma non deve costare un credito).
    assegnazioni_manuali: Optional[Dict[int, str]] = None
    if payload.manual_cards is not None:
        richieste = {p["n"] for p in stesa["posizioni"] if not p.get("calcolata")}
        date_ = {c.posizione for c in payload.manual_cards}
        if date_ != richieste:
            raise HTTPException(status_code=422, detail={
                "motivo": "posizioni_manuali",
                "messaggio": f"Servono esattamente le posizioni {sorted(richieste)}.",
            })
        id_dati = [c.card_id for c in payload.manual_cards]
        if len(set(id_dati)) != len(id_dati):
            raise HTTPException(status_code=422, detail={
                "motivo": "carte_duplicate", "messaggio": "Una carta non può comparire due volte.",
            })
        sconosciute = [i for i in id_dati if i not in conoscenza.carte]
        if sconosciute:
            raise HTTPException(status_code=422, detail={
                "motivo": "carta_sconosciuta", "messaggio": f"Carta sconosciuta: {sconosciute[0]}.",
            })
        assegnazioni_manuali = {c.posizione: c.card_id for c in payload.manual_cards}

    if segnale_di_crisi(payload.question):
        # Un segnale di crisi è un dato sulla salute (art. 9 GDPR): si conta, ma senza legarlo a chi l'ha scritto —
        # né nel registro né nelle statistiche (GDPR, Fase 1).
        await _registra_crisi(session, "apertura")
        await session.commit()
        return {"crisi": True, "messaggio": in_lingua(AIUTO, lang)}

    # Prima di addebitare qualunque cosa: senza un modello vero non c'è lettura.
    await verifica_modello(session, lang)

    gestore = GestoreAbbonamenti(session)
    limite_superato: Optional[str] = None
    if not await gestore.tariffe_in_vigore():
        consumo = "omaggio"
    else:
        # Un saldo sotto zero è il debito lasciato da uno storno (v9): nessuna lettura, nemmeno in quota, finché non
        # torna in pari — altrimenti chi si fa rimborsare continuerebbe a leggere con il piano.
        saldo = await RegistroCrediti(session).saldo(user.id)
        if saldo < 0:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={"motivo": "saldo_negativo", "messaggio": in_lingua(SALDO_NEGATIVO, lang), "saldo": saldo},
            )
        diritti = await gestore.diritti_di(user.id)
        consumo, limite_superato = await _consumo_con_limiti(session, gestore, user.id, diritti, payload.oltre_limite, lang)

    # Il recupero delle memorie (v6, Fase C): un'istantanea presa una volta sola, qui, che vale per
    # tutta l'intervista. Non deve mai impedire l'apertura di una lettura: un fornitore di embedding
    # non configurato o che fallisce lascia solo la lista vuota, non un errore all'utente.
    #
    # Con l'interruttore della console acceso l'istantanea è lo stato sintetico (`tarot/stato_memoria.py`), nella
    # stessa forma: l'intervista e la sintesi la leggono come prima. Spento (il predefinito), resta il recupero di
    # prima — che dalla riduzione dei costi gira solo con `TAROT_MEMORIA_EMBEDDING=true`.
    memorie_recuperate: List[Dict[str, Any]] = []
    try:
        if (await correnti_intervista(session)).memoria_stato_nei_prompt:
            memorie_recuperate = come_istantanea(
                await memoria_repositories.stato_di(session, user.id), date.today(), owner_id=user.id, limite=5,
            )
        elif get_settings().memoria_embedding:
            # Le persone come oggetto, non l'istantanea: il quesito va al fornitore degli embedding senza i nomi.
            provider_embed = provider_per(Compito.EMBEDDING, da_json(persone) if persone else None, riferimento="apertura")
            if supporta_embedding(provider_embed):
                candidati = await memoria_repositories.candidati_per(session, user.id)
                if candidati:
                    vettore = (await provider_embed.embed([payload.question.strip()]))[0]
                    memorie_recuperate = istantanea(rilevanti(candidati, vettore, top_n=5))
    except Exception:  # noqa: BLE001 - il recupero memorie non deve mai bloccare l'apertura
        logger.warning("Recupero memorie non riuscito all'apertura della lettura", exc_info=True)

    lettura = await ReadingRepository(session).create(
        user, spread_id=stesa["id"], question=payload.question.strip(),
        consumo=consumo, lang=lang, status="intervista", persone=persone,
        manuale=assegnazioni_manuali is not None,
        deck_id=mazzo_scelto.id if mazzo_scelto else None,
        memorie_recuperate=memorie_recuperate,
        limite=limite_superato if consumo != "omaggio" else None,
        variante=payload.variante, piattaforma=payload.piattaforma,
    )
    if assegnazioni_manuali is not None:
        # `lettura` è appena stata creata (solo un flush, mai un `select`): la relazione `cards` non è
        # ancora "caricata", e sia leggerla sia assegnarla (`lettura.cards = []`, che deve leggere il
        # valore vecchio per calcolare le rimozioni) proverebbero un lazy-load fuori da un contesto
        # awaitable. Non può avere figlie — `set_committed_value` la segna come caricata, senza query.
        set_committed_value(lettura, "cards", [])
        # Le carte sono già tutte posate: lo stato resta comunque `intervista` (l'intervista non è
        # ancora cominciata) — solo a intervista conclusa si salta `ventaglio` e si va dritti a
        # `rivelazione`, vedi sotto in `intervista()`.
        posa_manuale(lettura, stesa, conoscenza, assegnazioni_manuali)
    if consumo == "credito":
        try:
            await RegistroCrediti(session).consuma(
                user.id, COSTO_LETTURA, reading_id=lettura.id, note=f"lettura {stesa['nome']}",
            )
        except CreditiInsufficienti as exc:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "motivo": "crediti",
                    "messaggio": in_lingua(CREDITI_ESAURITI, lang),
                    "saldo": exc.disponibili,
                },
            ) from exc
    # «Ricorda»: nella stessa transazione della lettura. Se il pagamento fallisce
    # (402, rollback qui sopra) non si ricorda niente; in ramo crisi si è già usciti.
    if persone is not None and payload.ricorda_partner:
        user.partner_ricordato = dict(persone["partner"])
    await analytics.evento(session, analytics.LETTURA_APERTA, utente_id=user.id, proprieta={
        "stesa": stesa["id"], "categoria": categoria, "consumo": consumo, "lingua": lang,
        "manuale": assegnazioni_manuali is not None, "mazzo": payload.deck_id or "predefinito",
    })
    await session.commit()

    return {
        "id": str(lettura.id),
        "status": lettura.status,
        "consumo": consumo,
        "lang": lang,
        "categoria": categoria,
        "disclaimer": in_lingua(DISCLAIMER, lang),
        "stesa": get_conoscenza().stesa_pubblica(stesa),
        "saldo": await RegistroCrediti(session).saldo(user.id),
    }


class NuovaLetturaAnonima(BaseModel):
    """Solo lo standard (v6, Fase F): niente compatibilità/coppia (dati di una seconda persona,
    fuori scope per chi non ha nemmeno un account) né mazzo fisico."""

    spread_id: str = Field(min_length=1, max_length=40)
    question: str = Field(min_length=3, max_length=1000)
    lang: str = Field(default="it", max_length=5)
    #: «Ho almeno N anni» (GDPR, Fase 1): il sito lo chiede prima della lettura gratuita, come al primo accesso.
    eta_confermata: bool = False
    #: L'età confermata (quella mostrata nella domanda, da `GET /eta-minima`).
    eta_anni: Optional[int] = Field(default=None, ge=13, le=21)
    #: v9.5: versione della lettura e piattaforma (vedi `NuovaLettura`).
    variante: Optional[Literal["classica", "chat"]] = None
    piattaforma: Optional[Literal["web", "android", "ios"]] = None


DURATA_COOKIE_ANONIMO = 60 * 60 * 24 * 365  # un anno


@router.post("/readings/anonime", status_code=status.HTTP_201_CREATED)
async def apri_anonima(
    payload: NuovaLetturaAnonima, request: Request, response: Response, session: DbSession,
) -> Dict[str, Any]:
    """L'apertura gratuita per chi non ha un account (v6, Fase F, invito "fammi una domanda").

    Nessun credito, nessuna quota: `consumo="anonimo"`. Un solo colpo per cookie — un secondo
    tentativo con lo stesso `tarots_anon` trova già una lettura sua e viene respinto, non ne apre
    una seconda gratis.
    """
    stesa = _stesa_o_404(payload.spread_id)
    # Ammesse la standard e quella di lavoro: una persona sola, nessun dato di un partner.
    categoria = get_conoscenza().categoria_di(stesa)
    if speciale(categoria):
        raise HTTPException(status_code=422, detail="La lettura gratuita per anonimi è solo standard o di lavoro")
    lang = rileva_lingua(payload.question, fallback=payload.lang)

    # L'età minima vale anche senza account: la conferma arriva con la richiesta, per il paese stimato dall'IP.
    ip = ip_client(request)
    anni = eta_minima.anni_minimi(eta_minima.paese_da_ip(ip))
    if eta_minima.controllo_attivo() and (not payload.eta_confermata or (payload.eta_anni or 0) < anni):
        raise errore_eta_anonima(anni, payload.lang)

    if segnale_di_crisi(payload.question):
        return {"crisi": True, "messaggio": in_lingua(AIUTO, lang)}

    anon_id = request.cookies.get(COOKIE_ANONIMO)
    # `get_flex` cerca per un `reading_id` preciso: qui serve invece "esiste già una lettura con
    # questo anon_id", indipendentemente da quale — una query dedicata.
    esiste_gia = anon_id is not None and (await session.execute(
        select(Reading.id).where(Reading.anon_id == anon_id).limit(1)
    )).first() is not None
    if esiste_gia:
        raise HTTPException(status_code=409, detail={
            "motivo": "lettura_gratuita_gia_usata",
            "messaggio": "Hai già usato la tua lettura gratuita: registrati per continuare.",
        })

    await verifica_modello(session, lang)
    nuovo_anon_id = anon_id or secrets.token_urlsafe(32)
    lettura = Reading(
        owner_id=None, anon_id=nuovo_anon_id, spread_id=stesa["id"], question=payload.question.strip(),
        consumo="anonimo", lang=lang, status="intervista",
        variante=payload.variante, piattaforma=payload.piattaforma,
    )
    session.add(lettura)
    if payload.eta_confermata:
        consent_repositories.annota_storico(
            session, user_id=None, anon_id=nuovo_anon_id, tipo="eta_minima", valore="confermato",
            versione_informativa=f"eta-v1:{payload.eta_anni or anni}", ip=ip,
        )
    await analytics.evento(session, analytics.LETTURA_APERTA, proprieta={
        "stesa": stesa["id"], "categoria": categoria, "consumo": "anonimo", "lingua": lang,
    })
    await session.commit()

    # `SameSite`: in produzione frontend e API sono due domini diversi (tarots.chat, fx.tadamoo.com)
    # — una richiesta genuinamente incrociata fra siti, dove `Lax` non manderebbe mai il cookie su
    # un fetch/XHR. `None` lo richiede `Secure` (solo HTTPS): in sviluppo, dove i due lati girano
    # sullo stesso "sito" (localhost, porte diverse), `Lax` senza `Secure` funziona lo stesso ed
    # evita di dover servire il frontend di sviluppo in HTTPS solo per questo cookie.
    in_produzione = get_settings().environment == "prod"
    response.set_cookie(
        COOKIE_ANONIMO, nuovo_anon_id, max_age=DURATA_COOKIE_ANONIMO,
        httponly=True, secure=in_produzione, samesite="none" if in_produzione else "lax",
    )
    return {
        "id": str(lettura.id),
        "status": lettura.status,
        "consumo": "anonimo",
        "lang": lang,
        "categoria": categoria,
        "disclaimer": in_lingua(DISCLAIMER, lang),
        "stesa": get_conoscenza().stesa_pubblica(stesa),
    }


# ---- intervista ---------------------------------------------------------------


@router.post("/readings/{reading_id}/interview")
async def intervista(
    reading_id: uuid.UUID, payload: RispostaIntervista, user: OptionalUser,
    session: DbSession, request: Request,
) -> Dict[str, Any]:
    """Registra la risposta e restituisce la prossima domanda, o chiude.

    Risposta JSON e non SSE: l'uscita del modello è un JSON che non si può
    mostrare a metà. Il frontend la scrive a macchina.
    """
    anon_id = None if user else request.cookies.get(COOKIE_ANONIMO)
    repo = ReadingRepository(session)
    lettura = await _lettura_o_404(repo, user, reading_id, lock=True, anon_id=anon_id)
    if lettura.status != "intervista":
        raise _conflitto("L'intervista è già conclusa")

    turni = list(lettura.turns)
    attende_risposta = bool(turni) and turni[-1].ruolo == "oracolo"
    regole = await correnti_intervista(session)
    min_domande, max_domande = regole.min_domande, regole.max_domande
    if payload.basta:
        return await _basta_cosi(session, repo, user, lettura, reading_id, anon_id, min_domande)
    if payload.risposta is not None and payload.risposta.strip():
        if not attende_risposta:
            raise _conflitto("Nessuna domanda in attesa di risposta")
        testo = payload.risposta.strip()
        if segnale_di_crisi(testo):
            return await _chiudi_per_crisi(session, user, lettura)
        lettura.turns.append(InterviewTurn(
            ordine=len(turni) + 1, ruolo="utente", testo=testo, created_at=utcnow(),
        ))
        if not payload.continua:
            # v9.5: la risposta è salvata; la prossima domanda arriva solo se chi consulta la chiede.
            await session.commit()
            poste = sum(1 for t in lettura.turns if t.ruolo == "oracolo")
            return {"completa": False, "scelta": True, "poste": poste,
                    "min_domande": min_domande, "max_domande": max_domande}
    elif payload.altra and not attende_risposta:
        if sum(1 for t in turni if t.ruolo == "oracolo") >= max_domande:
            raise _conflitto("Le domande previste sono finite: passa alla lettura")
    elif attende_risposta:
        # Una seconda chiamata vuota (una pagina ricaricata) ripropone la
        # domanda in attesa invece di generarne un'altra.
        poste = sum(1 for t in turni if t.ruolo == "oracolo")
        return {
            "completa": False, "domanda": turni[-1].testo, "ordine": turni[-1].ordine,
            "facoltativa": poste - 1 >= min_domande,
        }
    await session.commit()

    await verifica_modello(session, lettura.lang)          # rilegge già fornitori e assegnazioni
    stesa = _stesa_o_404(lettura.spread_id)
    impostazioni = get_settings()
    conoscenza = get_conoscenza()
    categoria = conoscenza.categoria_di(stesa)
    persone = await _persone_per_prompt(session, lettura, user)
    # Nelle letture speciali il profilo del prompt sono le due persone (col
    # partner senza cognome); nella standard, la carta dell'anima e dell'anno.
    profilo = (_profilo(user) if user else "") if persone is None else blocco_persone(persone, conoscenza) + "\n"
    # v9.5: la prima domanda c'è sempre (anche col minimo a 0, chi vuole passa alle carte da lì), e «un'altra
    # domanda» chiesta da chi consulta va fatta: per il modello il minimo diventa «una in più di quelle già poste».
    poste_ora = sum(1 for t in lettura.turns if t.ruolo == "oracolo")
    minimo_modello = max(min_domande, poste_ora + 1) if (payload.altra or poste_ora == 0) else min_domande
    try:
        passo = await prossimo_passo(
            provider_intervista=provider_per(Compito.INTERVISTA, persone, lettura=reading_id),
            provider_validazione=provider_per(Compito.VALIDAZIONE, persone, lettura=reading_id),
            quesito=lettura.question,
            stesa_nome=stesa["nome"],
            stesa_descrizione=(
                f"{stesa['descrizione']} Posizioni: "
                + "; ".join(f"{p['n']}. {p['nome']}" for p in stesa["posizioni"])
            ),
            turni=turni_da(lettura.turns),
            min_domande=minimo_modello,
            max_domande=max_domande,
            lang=lettura.lang,
            profilo=profilo,
            categoria=categoria,
            nota=stesa.get("nota_intervista", ""),
            parole_neutre=parole_neutre(persone),
            memorie=da_istantanea(lettura.memorie_recuperate or []),
            validatore=regole.validatore_domande or "dubbi",
        )
    except (IntervistaNonRiuscita, RuntimeError) as exc:
        # Nessuna domanda di riserva: si dice che l'oracolo non ha risposto.
        # La lettura resta aperta e chi consulta può riprovare senza pagare
        # un'altra volta.
        logger.warning("Intervista non riuscita (lettura %s): %s", reading_id, exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "motivo": "modello_non_disponibile",
                "messaggio": in_lingua(MODELLO_NON_DISPONIBILE, lettura.lang),
            },
        ) from exc

    lettura = await _lettura_o_404(repo, user, reading_id, lock=True, anon_id=anon_id)
    if passo.completo:
        lettura.context_summary = passo.riassunto
        # Manuale: le carte sono già posate (v5, "Interpreta i miei tarocchi") — niente ventaglio da
        # aprire, si va dritti alla rivelazione.
        lettura.status = "rivelazione" if lettura.manuale else "ventaglio"
        await session.commit()
        return {"completa": True, "riassunto": passo.riassunto}

    ordine = len(lettura.turns) + 1
    lettura.turns.append(InterviewTurn(
        ordine=ordine, ruolo="oracolo", testo=passo.domanda, created_at=utcnow(),
    ))
    await session.commit()
    poste = poste_ora + 1
    return {
        "completa": False, "domanda": passo.domanda, "ordine": ordine, "scartate": passo.scartate,
        # col minimo vero (non quello forzato per il modello): si può smettere se le domande già risposte bastano
        "facoltativa": poste - 1 >= min_domande,
        "poste": poste, "min_domande": min_domande, "max_domande": max_domande,
    }


@router.post("/readings/{reading_id}/addition")
async def aggiunta(
    reading_id: uuid.UUID, payload: AggiuntaIntervista, user: OptionalUser, session: DbSession, request: Request,
) -> Dict[str, Any]:
    """«Voglio dire qualcosa di libero» (v9.5): durante l'intervista (quando nessuna domanda aspetta risposta) o dopo,
    prima delle carte, chi consulta scrive liberamente. Si salva nel colloquio come un intervento di chi consulta,
    con un'etichetta che lo distingue da una risposta: l'intervista e il riassunto finale lo leggono, la sintesi
    rilegge il colloquio. Se l'intervista è già chiusa si aggiunge anche in coda al quadro emerso (che legge
    l'interpretazione di ogni carta). Non conta come domanda. Stesso controllo dei segnali di crisi delle risposte."""
    anon_id = None if user else request.cookies.get(COOKIE_ANONIMO)
    repo = ReadingRepository(session)
    lettura = await _lettura_o_404(repo, user, reading_id, lock=True, anon_id=anon_id)
    turni = list(lettura.turns)
    in_intervista = lettura.status == "intervista"
    prima_delle_carte = lettura.status == "ventaglio" or (
        lettura.manuale and lettura.status == "rivelazione" and not any(c.rivelata for c in lettura.cards)
    )
    if not (in_intervista or prima_delle_carte):
        raise _conflitto("Si può aggiungere qualcosa solo prima delle carte")
    if in_intervista and turni and turni[-1].ruolo == "oracolo":
        raise _conflitto("C'è una domanda che aspetta risposta")
    testo = payload.testo.strip()
    if not testo:
        raise HTTPException(status_code=422, detail="Scrivi qualcosa da aggiungere")
    if segnale_di_crisi(testo):
        return await _chiudi_per_crisi(session, user, lettura)
    etichetta = in_lingua(AGGIUNTA_ETICHETTA, lettura.lang)
    lettura.turns.append(InterviewTurn(ordine=len(turni) + 1, ruolo="utente", testo=f"({etichetta}) {testo}",
                                       created_at=utcnow()))
    if not in_intervista:
        lettura.context_summary = f"{lettura.context_summary or ''}\n\n{etichetta}: {testo}".strip()
    await session.commit()
    return {"aggiunto": True}


async def _basta_cosi(session, repo, user, lettura: Reading, reading_id, anon_id, min_domande: int) -> Dict[str, Any]:
    """«No, basta così»: chiude l'intervista col quadro emerso fin qui e passa alle carte.

    Solo dopo il minimo di domande con risposta; la domanda facoltativa rimasta senza risposta si toglie, così il
    colloquio salvato (e la storia) non mostra una domanda sospesa."""
    turni = list(lettura.turns)
    if turni and turni[-1].ruolo == "oracolo":
        lettura.turns.remove(turni[-1])
        turni = turni[:-1]
    risposte = sum(1 for t in turni if t.ruolo == "oracolo")
    if risposte < min_domande:
        raise _conflitto("Servono ancora alcune risposte prima di passare alle carte")
    await session.commit()
    await verifica_modello(session, lettura.lang)
    persone = await _persone_per_prompt(session, lettura, user)
    categoria = get_conoscenza().categoria_di(_stesa_o_404(lettura.spread_id))
    riassunto = await riassumi(
        provider_per(Compito.INTERVISTA, persone, lettura=reading_id), quesito=lettura.question, turni=turni_da(turni),
        lang=lettura.lang, categoria=categoria,
    )
    lettura = await _lettura_o_404(repo, user, reading_id, lock=True, anon_id=anon_id)
    lettura.context_summary = riassunto
    lettura.status = "rivelazione" if lettura.manuale else "ventaglio"
    await session.commit()
    return {"completa": True, "riassunto": riassunto}


async def _chiudi_per_crisi(session, user: Optional[User], lettura: Reading) -> Dict[str, Any]:
    """Ferma la lettura e restituisce il credito: chi è in crisi riceve aiuto,
    non carte. Una lettura anonima (v6, Fase F) non ha nulla da rimborsare."""
    lettura.status = "annullata"
    if user and lettura.consumo == "credito":
        # La nota del registro dei crediti non dice perché: il registro è contabilità, resta anche dopo la
        # cancellazione dell'account, e un segnale di crisi è un dato sulla salute (art. 9 GDPR).
        await RegistroCrediti(session).rimborsa(
            user.id, COSTO_LETTURA, reading_id=lettura.id, note="lettura sospesa",
        )
    await _registra_crisi(session, "intervista")
    await session.commit()
    return {"completa": False, "crisi": True, "messaggio": in_lingua(AIUTO, lettura.lang)}


async def _registra_crisi(session, fase: str) -> None:
    """Il segnale di crisi si conta e basta (GDPR, Fase 1): nel registro senza chi né quale lettura, nelle
    statistiche senza utente. Quanti segnali, in che fase, quando: abbastanza per capire se il filtro funziona e se
    i numeri di aiuto vanno ripensati, niente che riporti a una persona."""
    await AuditRepository(session).record(action="reading.crisis", after={"fase": fase})
    await analytics.evento(session, analytics.LETTURA_CRISI, proprieta={"fase": fase})


# ---- ventaglio e scelta ---------------------------------------------------------


@router.post("/readings/{reading_id}/fan")
async def ventaglio(
    reading_id: uuid.UUID, user: OptionalUser, session: DbSession, request: Request,
    payload: Optional[TaglioMazzo] = None,
) -> Dict[str, Any]:
    """Mescola, taglia dove ha cliccato chi consulta e fissa il mazzo. Al
    client vanno solo il numero degli slot e il commitment: le carte restano
    sul server finché non si rivelano."""
    anon_id = None if user else request.cookies.get(COOKIE_ANONIMO)
    repo = ReadingRepository(session)
    lettura = await _lettura_o_404(repo, user, reading_id, lock=True, anon_id=anon_id)
    stesa = _stesa_o_404(lettura.spread_id)
    conoscenza = get_conoscenza()

    if lettura.status == "ventaglio":
        fissato = mescola(
            conoscenza.mazzo_per(stesa), taglio=payload.taglio if payload else None,
        )
        lettura.deck_state = fissato.slot
        lettura.deck_salt = fissato.sale
        lettura.commitment = fissato.commitment
        lettura.status = "scelta"
        await session.commit()
    elif lettura.status != "scelta":
        raise _conflitto("Il ventaglio non si può aprire in questo momento")

    return {
        "slot_count": len(lettura.deck_state or []),
        "commitment": lettura.commitment,
        "da_scegliere": stesa["carte_da_scegliere"],
        "picked_slots": [c.slot for c in lettura.cards if c.slot is not None],
    }


@router.post("/readings/{reading_id}/pick")
async def scegli(
    reading_id: uuid.UUID, payload: Scelta, user: OptionalUser, session: DbSession, request: Request,
) -> Dict[str, Any]:
    anon_id = None if user else request.cookies.get(COOKIE_ANONIMO)
    repo = ReadingRepository(session)
    lettura = await _lettura_o_404(repo, user, reading_id, lock=True, anon_id=anon_id)
    stesa = _stesa_o_404(lettura.spread_id)
    try:
        carta = posa(lettura, stesa, payload.slot, get_conoscenza())
    except StatoNonValido as exc:
        raise _conflitto(str(exc)) from exc
    await session.commit()
    return {
        "posizione": carta.posizione,
        "slot": carta.slot,
        "tutte_scelte": lettura.status == "rivelazione",
        "posizioni_calcolate": [c.posizione for c in lettura.cards if c.calcolata],
    }


# ---- rivelazione ------------------------------------------------------------------


@router.post("/readings/{reading_id}/reveal/{posizione}")
async def rivela(
    reading_id: uuid.UUID, posizione: int, user: OptionalUser, session: DbSession,
    fabbrica: SessionFactory, request: Request,
) -> StreamingResponse:
    """Gira la carta e ne dà l'interpretazione, in streaming.

    Le carte si rivelano in ordine di posizione: la lettura è un racconto, e
    l'interpretazione di ciascuna tiene conto di quelle già viste.

    **Una chiamata sola per tutte le carte** (`api/rivelazione.py`): la prima richiesta di svelamento della lettura
    interpreta tutte le carte ancora da leggere; le richieste delle altre posizioni trovano il testo già pronto e lo
    mandano subito (`token` con il testo intero). Gli eventi restano quelli di prima — `carta`, `battito` mentre il
    lettore legge, `token`, `sostituisci`, `errore`, `fine` — così sito e app di prima funzionano come prima. Le
    posizioni che la chiamata unica non copre si leggono con la chiamata singola di prima, in streaming.
    """
    anon_id = None if user else request.cookies.get(COOKIE_ANONIMO)
    repo = ReadingRepository(session)
    lettura = await _lettura_o_404(repo, user, reading_id, lock=True, anon_id=anon_id)
    if lettura.status != "rivelazione":
        raise _conflitto("Non ci sono carte da rivelare")
    carta = prossima_da_rivelare(lettura)
    if carta is None or carta.posizione != posizione:
        raise _conflitto("Le carte si rivelano in ordine")

    await verifica_modello(session, lettura.lang)
    conoscenza = get_conoscenza()
    stesa = _stesa_o_404(lettura.spread_id)
    lang = lingua(lettura.lang)
    categoria = conoscenza.categoria_di(stesa)
    persone_lettura = await _persone_per_prompt(session, lettura, user)
    soggetti = _soggetti(stesa, persone_lettura)
    comune = rivelazione.contesto_comune(lettura, stesa, persone_lettura, user)
    # Questa carta e quelle ancora coperte: la chiamata unica le legge tutte, ciascuna con i dati che avrebbe avuto
    # girandola da sola (`rivelazione.dati_carta`).
    da_leggere = [c for c in lettura.cards if not c.rivelata and not c.interpretazione]
    carta.rivelata = True
    dati = rivelazione.dati_carta(lettura, stesa, carta, lang, soggetti)
    preparata = rivelazione.prepara(
        reading_id, [(c, rivelazione.dati_carta(lettura, stesa, c, lang, soggetti)) for c in da_leggere],
        categoria=categoria, comune=comune, lang=lang,
    )
    pronta = carta.interpretazione or ""
    evento_carta = _evento_carta(conoscenza, carta, dati)
    await session.commit()
    await aggiorna_assegnazioni(session)
    unica = None if pronta else rivelazione.avvia(
        preparata, provider_per(Compito.INTERPRETAZIONE, persone_lettura, lettura=reading_id), fabbrica,
    )

    async def genera() -> AsyncIterator[bytes]:
        yield _sse("carta", evento_carta)
        testo = pronta
        if not testo and unica is not None:
            async for battito in _attendi(unica):
                yield battito
            testo = rivelazione.risultato(unica).get(posizione, "")
        if not testo:
            # Scritta nel frattempo da un'altra richiesta della stessa lettura?
            testo = (await rivelazione.leggi(fabbrica, reading_id, [posizione])).get(posizione, "")
        if testo:
            yield _sse("token", {"testo": testo})
        else:
            esito: List[str] = []
            async for evento in _interpreta_una(
                provider_per(Compito.INTERPRETAZIONE, persone_lettura, lettura=reading_id),
                rivelazione.sistema(categoria, unica=False),
                interpretazione.messaggio(**comune, **dati, lang=lang), dati, lettura.lang, esito,
            ):
                yield evento
            testo = esito[0] if esito else ""

        ultima = await _salva_interpretazione(fabbrica, reading_id, user, anon_id, posizione, testo)
        yield _sse("fine", {"posizione": posizione, "interpretazione": testo, "ultima": ultima})

    return _flusso(genera())


@router.post("/readings/{reading_id}/reveal-all")
async def rivela_tutte(
    reading_id: uuid.UUID, user: OptionalUser, session: DbSession, fabbrica: SessionFactory, request: Request,
) -> StreamingResponse:
    """Gira tutte le carte ancora coperte e le interpreta con una chiamata sola, in streaming.

    Eventi: un `carta` per ogni carta, in ordine (subito: le carte si girano insieme); `fase` `lettura` (il lettore sta
    leggendo le carte) e `battito` finché la chiamata unica lavora; poi per ogni posizione `token` (con `posizione`; il
    testo intero, o a pezzi se quella posizione torna alla chiamata singola), eventualmente `sostituisci` o `errore`
    (con `posizione`), e `fine` (`posizione`, `interpretazione`, `ultima`). Le regole sono quelle di
    `POST /readings/{id}/reveal/{posizione}`, che resta per i client di prima.
    """
    anon_id = None if user else request.cookies.get(COOKIE_ANONIMO)
    repo = ReadingRepository(session)
    lettura = await _lettura_o_404(repo, user, reading_id, lock=True, anon_id=anon_id)
    coperte = sorted((c for c in lettura.cards if not c.rivelata), key=lambda c: c.posizione)
    if lettura.status != "rivelazione" or not coperte:
        raise _conflitto("Non ci sono carte da rivelare")

    await verifica_modello(session, lettura.lang)
    conoscenza = get_conoscenza()
    stesa = _stesa_o_404(lettura.spread_id)
    lang = lingua(lettura.lang)
    categoria = conoscenza.categoria_di(stesa)
    persone_lettura = await _persone_per_prompt(session, lettura, user)
    soggetti = _soggetti(stesa, persone_lettura)
    comune = rivelazione.contesto_comune(lettura, stesa, persone_lettura, user)
    voci = [(c, rivelazione.dati_carta(lettura, stesa, c, lang, soggetti)) for c in coperte]
    pronte = {c.posizione: c.interpretazione for c in coperte if c.interpretazione}
    preparata = rivelazione.prepara(
        reading_id, [(c, d) for c, d in voci if c.posizione not in pronte],
        categoria=categoria, comune=comune, lang=lang,
    )
    for c in coperte:
        c.rivelata = True
    eventi_carta = [_evento_carta(conoscenza, c, d) for c, d in voci]
    await session.commit()
    await aggiorna_assegnazioni(session)
    unica = rivelazione.avvia(
        preparata, provider_per(Compito.INTERPRETAZIONE, persone_lettura, lettura=reading_id), fabbrica,
    ) if len(pronte) < len(coperte) else None

    async def genera() -> AsyncIterator[bytes]:
        for evento in eventi_carta:
            yield _sse("carta", evento)
        yield _sse("fase", {"fase": "lettura"})
        if unica is not None:
            async for battito in _attendi(unica):
                yield battito
        testi = {**rivelazione.risultato(unica), **pronte}
        mancanti = [c.posizione for c in coperte if c.posizione not in testi]
        testi.update(await rivelazione.leggi(fabbrica, reading_id, mancanti))
        for c, dati in voci:
            n = c.posizione
            testo = testi.get(n, "")
            if testo:
                yield _sse("token", {"posizione": n, "testo": testo})
            else:
                esito: List[str] = []
                async for evento in _interpreta_una(
                    provider_per(Compito.INTERPRETAZIONE, persone_lettura, lettura=reading_id),
                    rivelazione.sistema(categoria, unica=False),
                    interpretazione.messaggio(**comune, **dati, lang=lang), dati, lettura.lang, esito, posizione=n,
                ):
                    yield evento
                testo = esito[0] if esito else ""
            ultima = await _salva_interpretazione(fabbrica, reading_id, user, anon_id, n, testo)
            ultima = ultima and n == coperte[-1].posizione
            yield _sse("fine", {"posizione": n, "interpretazione": testo, "ultima": ultima})

    return _flusso(genera())


def _evento_carta(conoscenza, carta, dati: Dict[str, Any]) -> Dict[str, Any]:
    """L'evento `carta`: la carta girata, con la dignità rispetto alle carte già rivelate (come chi consulta la vede)."""
    return {
        "posizione": carta.posizione,
        "carta": conoscenza.carta_pubblica(carta.card_id),
        "rovescio": carta.rovescio,
        "calcolata": carta.calcolata,
        "doppia_valenza": dati["doppia_valenza"],
        "dignita": dati["dignita"],
    }


async def _attendi(task) -> AsyncIterator[bytes]:
    """Un `battito` ogni cinque secondi finché la chiamata unica lavora: la connessione resta viva. Il task non si
    annulla se il client se ne va (`shield`): l'interpretazione si scrive comunque."""
    while not task.done():
        try:
            await asyncio.wait_for(asyncio.shield(task), timeout=5)
        except asyncio.TimeoutError:
            yield _sse("battito", {})
        except Exception:  # noqa: BLE001 - l'esito si legge dal task
            break


async def _interpreta_una(
    provider, sistema: List[str], domanda: str, dati: Dict[str, Any], lang_lettura: str, esito: List[str],
    *, posizione: Optional[int] = None,
) -> AsyncIterator[bytes]:
    """La chiamata singola di prima per una carta, in streaming: il ripiego della chiamata unica. Il testo finale va in
    `esito`. Con `posizione` (svelamento di tutte le carte) gli eventi la portano, per dire a quale carta vanno."""
    dove = {} if posizione is None else {"posizione": posizione}
    testo = ""
    try:
        async for pezzo in genera_flusso(provider, richiesta(
            sistema, domanda, temperatura=0.7, max_tokens=interpretazione.TETTO_CARTA,
        )):
            testo += pezzo
            yield _sse("token", {**dove, "testo": pezzo})
    except Exception as exc:  # noqa: BLE001 - errori del fornitore e di rete
        logger.warning("Interpretazione non generata: %s", exc)
        yield _sse("errore", {**dove, "messaggio": in_lingua(INTERPRETAZIONE_NON_DISPONIBILE, lang_lettura)})

    testo = testo.strip()
    if testo and uscita_proibita(testo):
        # Il guardrail leggero delle carte: una formula proibita non resta sullo schermo.
        testo = rivelazione.prudente(dati["carta"], dati["rovescio"])
        yield _sse("sostituisci", {**dove, "testo": testo})
    esito.append(testo)


async def _salva_interpretazione(
    fabbrica, reading_id: uuid.UUID, user: Optional[User], anon_id: Optional[str], posizione: int, testo: str,
) -> bool:
    """Scrive il testo della posizione e, se non resta niente da girare, passa la lettura alla sintesi. Vero se era
    l'ultima."""
    async with fabbrica() as s:
        r = await ReadingRepository(s).get_flex(reading_id, owner=user, anon_id=anon_id, lock=True)
        if r is None:
            return False
        for c in r.cards:
            if c.posizione == posizione:
                c.interpretazione = testo or None
        if prossima_da_rivelare(r) is None:
            r.status = "sintesi"
        await s.commit()
        return r.status == "sintesi"


def _interpretazione_prudente(carta: Dict[str, Any], rovescio: bool, lang: str) -> str:
    """Il significato del mazzo, al posto di un testo che il filtro ha fermato."""
    return rivelazione.prudente(carta, rovescio)


# ---- sintesi ------------------------------------------------------------------------


@router.post("/readings/{reading_id}/synthesis")
async def sintesi(
    reading_id: uuid.UUID, user: OptionalUser, session: DbSession, fabbrica: SessionFactory,
    request: Request,
) -> StreamingResponse:
    """Il responso finale: CAG, poi guardrail, poi il testo all'utente.

    Il responso **non** si mostra mentre il modello lo scrive: prima passa dal
    giudice, e solo un testo approvato arriva allo schermo. Nel frattempo il
    flusso manda eventi di fase, così la connessione resta viva e l'utente
    vede che la lettura sta prendendo forma.

    **Per un visitatore anonimo (v6, Fase F)**: il responso vero si genera e si salva per intero
    (così il claim alla registrazione non deve ricalcolare nulla), ma ciò che arriva al client è
    un'anteprima breve (`teaser.py`) — mai il testo vero, nemmeno troncato.
    """
    anon_id = None if user else request.cookies.get(COOKIE_ANONIMO)
    is_anonimo = user is None
    repo = ReadingRepository(session)
    lettura = await _lettura_o_404(repo, user, reading_id, anon_id=anon_id)
    lang = lingua(lettura.lang)

    if lettura.status == "completata":
        saldo = await RegistroCrediti(session).saldo(user.id) if user else None
        chiusura = _chiusura(lettura, saldo)
        chiusura["anonimo"] = is_anonimo
        # `teaser` è nullo per una lettura bloccata dal guardrail (non generato apposta): in quel
        # caso `synthesis` contiene già il messaggio generico del blocco, non il responso vero.
        testo_da_servire = (lettura.teaser or lettura.synthesis or "") if is_anonimo else (lettura.synthesis or "")
        await session.commit()

        async def rilegge() -> AsyncIterator[bytes]:
            yield _sse("token", {"testo": testo_da_servire})
            yield _sse("fine", chiusura)
        return _flusso(rilegge())

    if lettura.status == "rivelazione" and lettura.cards and prossima_da_rivelare(lettura) is None:
        # Tutte le carte girate, ma il passaggio alla sintesi non è stato scritto (il client ha chiuso la connessione
        # prima della fine dell'ultima interpretazione): la lettura non resta bloccata.
        lettura.status = "sintesi"
    if lettura.status != "sintesi":
        raise _conflitto("Il responso arriva dopo aver rivelato tutte le carte")

    await verifica_modello(session, lang)
    conoscenza = get_conoscenza()
    stesa = _stesa_o_404(lettura.spread_id)
    registro = get_guardrail()
    await aggiorna_assegnazioni(session)
    persone_lettura = await _persone_per_prompt(session, lettura, user)
    # Le memorie sulla salute (art. 9) si estraggono solo con il consenso alle categorie particolari (GDPR, Fase 1).
    salute_ammessa = await _dati_particolari(session, user)
    regole = await correnti_intervista(session)
    modo_guardia = regole.guardia_responso or "dubbi"
    autore = provider_per(Compito.SINTESI, persone_lettura, lettura=reading_id)
    giudice = provider_per(Compito.GIUDIZIO, persone_lettura, lettura=reading_id)

    categoria = conoscenza.categoria_di(stesa)
    prefisso = cag.prefisso(conoscenza, registro.istruzioni_per("sintesi", categoria), categoria)
    memorie_rilevanti = (
        await _memorie_per_sintesi(session, user.id, lettura.memorie_recuperate or []) if user else ""
    )
    carte = [
        {
            "card_id": c.card_id, "rovescio": c.rovescio, "posizione": c.posizione,
            "calcolata": c.calcolata, "interpretazione": c.interpretazione,
        }
        for c in lettura.cards
    ]
    argomenti = dict(
        conoscenza=conoscenza, stesa=stesa, quesito=lettura.question,
        contesto=lettura.context_summary or "", carte=carte,
        dignita=dignita_di(lettura, stesa, conoscenza, solo_rivelate=False),
        prevalenze=prevalenze_di(lettura, conoscenza),
        profilo=(_profilo(user) if user else "") if persone_lettura is None else "",
        wirth=wirth(lettura, stesa, conoscenza), lang=lang,
        colloquio=trascrizione(turni_da(lettura.turns)),
        persone=blocco_persone(persone_lettura, conoscenza) if persone_lettura else "",
        compatibilita=blocco_compatibilita(persone_lettura, conoscenza) if persone_lettura else "",
        soggetti=_soggetti(stesa, persone_lettura),
        memorie_rilevanti=memorie_rilevanti,
        registro=user.registro_linguistico if user else "",
    )

    # La transazione della richiesta si chiude prima dello streaming: il
    # responso può richiedere decine di secondi, e tenere aperta una
    # connessione per niente la toglie al pool.
    await session.commit()

    tetto = _tetto_sintesi(stesa, categoria)

    async def scrivi(vincoli: str = "") -> str:
        return await genera_testo(autore, richiesta(
            [prefisso], cag.parte_variabile(**argomenti, vincoli=vincoli),
            temperatura=0.75, max_tokens=tetto, cache_dopo=0,
        ))

    async def genera() -> AsyncIterator[bytes]:
        yield _sse("fase", {"fase": "unione"})
        lavoro = asyncio.create_task(scrivi())
        while not lavoro.done():
            try:
                await asyncio.wait_for(asyncio.shield(lavoro), timeout=5)
            except asyncio.TimeoutError:
                yield _sse("battito", {})
            except Exception:  # noqa: BLE001 - l'errore si legge dal task
                break
        try:
            responso = lavoro.result()
            if not responso:
                raise GenerationError("responso vuoto")
        except Exception as exc:  # noqa: BLE001 - errori del fornitore e di rete
            logger.warning("Sintesi non generata: %s", exc)
            # Analytics (v8): gli errori del modello alimentano l'avviso notturno.
            async with fabbrica() as s:
                await analytics.evento(s, analytics.LETTURA_ERRORE, utente_id=user.id if user else None,
                                       proprieta={"stesa": stesa["id"], "categoria": categoria})
                await s.commit()
            yield _sse("errore", {"messaggio": in_lingua(RESPONSO_NON_GENERATO, lang)})
            return

        yield _sse("fase", {"fase": "guardia"})
        # Il modo della guardia (console): nel predefinito «solo casi dubbi» la guardia LLM parte solo se il controllo
        # deterministico trova qualcosa da guardare; la revisione resta legata a ciò che la guardia segnala.
        guardia = dict(
            categoria=categoria, modo=modo_guardia, colloquio=argomenti["colloquio"], lang=lang,
        )
        verdetto = await giudica(giudice, registro, quesito=lettura.question, responso=responso, **guardia)
        esito = "ok"
        if verdetto.esito == "riscrivi":
            yield _sse("fase", {"fase": "revisione"})
            try:
                responso = await scrivi(verdetto.vincoli())
                verdetto = await giudica(giudice, registro, quesito=lettura.question, responso=responso, **guardia)
                esito = "riscritto" if verdetto.ok else "bloccato"
            except Exception:  # noqa: BLE001
                esito = "bloccato"
        elif verdetto.esito == "blocca":
            esito = "bloccato"
        if esito == "bloccato":
            responso = in_lingua(RESPONSO_BLOCCATO, lang)
        elif not verdetto.verificato and verdetto.guardia != "spenta":
            logger.warning("Responso della lettura %s non verificato dal giudice", reading_id)

        # Per un anonimo, l'anteprima si genera qui: sul responso vero, mai su quello bloccato (un
        # rifiuto del guardrail non ha nulla su cui basare un'anteprima sensata).
        teaser_testo = ""
        if is_anonimo and esito != "bloccato":
            # Un compito suo (senza assegnazione: il modello della sintesi, col ragionamento spento).
            teaser_testo = await genera_teaser(
                provider_per(Compito.TEASER, persone_lettura, lettura=reading_id), responso=responso, lang=lang,
            )

        async with fabbrica() as s:
            r = await ReadingRepository(s).get_flex(reading_id, owner=user, anon_id=anon_id, lock=True)
            if r is None:
                return
            r.synthesis = responso
            r.teaser = teaser_testo or None
            r.guard_outcome = esito
            r.status = "completata"
            r.completed_at = utcnow()
            if esito == "bloccato":
                await AuditRepository(s).record(
                    action="reading.guard_block", actor_id=user.id if user else None,
                    target_type="reading", target_id=str(reading_id),
                    after={"violazioni": verdetto.violazioni},
                )
            await analytics.evento(s, analytics.LETTURA_COMPLETATA, utente_id=user.id if user else None, proprieta={
                "stesa": stesa["id"], "categoria": categoria, "guardia": esito, "anonima": is_anonimo,
                "lingua": lang,
            })
            await s.commit()
            saldo = await RegistroCrediti(s).saldo(user.id) if user else None
            chiusura = _chiusura(r, saldo)
            chiusura["anonimo"] = is_anonimo

        if user and esito != "bloccato":
            # In background, mai atteso: un aggiornamento lento o fallito non deve ritardare né
            # rompere una risposta già consegnata all'utente (v6, Fase B). Un anonimo non ha un
            # profilo a cui attaccare memorie: niente da ricordare finché non si registra.
            #
            # Lo stato sintetico: una chiamata breve, sempre senza ragionamento, sul quadro dell'intervista (non sulla
            # trascrizione né sul responso). Si aggiorna anche quando non entra nei prompt (interruttore della console).
            asyncio.create_task(aggiorna_stato(
                fabbrica, user.id, quesito=lettura.question, quadro=lettura.context_summary or "",
                provider=provider_per(
                    Compito.MEMORIA_ESTRAZIONE, persone_lettura, lettura=reading_id, senza_ragionamento=True,
                ),
                lang=lang, salute_ammessa=salute_ammessa,
            ))
            if get_settings().memoria_embedding:
                # La memoria di prima, solo se riaccesa (`TAROT_MEMORIA_EMBEDDING`).
                asyncio.create_task(estrai_e_salva(
                    fabbrica, user.id, reading_id,
                    quesito=lettura.question, colloquio=argomenti["colloquio"], sintesi=responso,
                    provider_estrazione=provider_per(Compito.MEMORIA_ESTRAZIONE, persone_lettura, lettura=reading_id),
                    provider_embedding=provider_per(Compito.EMBEDDING, persone_lettura, lettura=reading_id),
                    salute_ammessa=salute_ammessa,
                ))

        yield _sse("fase", {"fase": "responso", "guardia": esito})
        # Il testo esce a frammenti: già approvato, ma lo si scrive davanti
        # all'utente come si gira una carta — un colpo solo sarebbe un muro. Per un anonimo è
        # l'anteprima che esce così, mai il responso vero.
        testo_da_mostrare = teaser_testo if (is_anonimo and esito != "bloccato") else responso
        for i in range(0, len(testo_da_mostrare), 24):
            yield _sse("token", {"testo": testo_da_mostrare[i:i + 24]})
            await asyncio.sleep(0.012)
        yield _sse("fine", chiusura)

    return _flusso(genera())


def _chiusura(lettura: Reading, saldo: int) -> Dict[str, Any]:
    return {
        "disclaimer": in_lingua(DISCLAIMER, lettura.lang),
        "guardia": lettura.guard_outcome,
        "commitment": lettura.commitment,
        "deck_salt": lettura.deck_salt,
        "deck_state": lettura.deck_state,
        "saldo": saldo,
    }


# ---- storico, diario, condivisione ------------------------------------------------------


@router.get("/me/readings")
async def elenco(user: CurrentUser, session: DbSession, limite: int = 50) -> Dict[str, Any]:
    repo = ReadingRepository(session)
    letture = await repo.list_recent(user, limite=min(limite, 200))
    return {
        "totale": await repo.count(user),
        "letture": [lettura_json(r, dettaglio=False) for r in letture],
    }


@router.get("/me/readings/{reading_id}")
async def dettaglio(reading_id: uuid.UUID, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    lettura = await _lettura_o_404(ReadingRepository(session), user, reading_id)
    dati = lettura_json(lettura)
    dati["stesa_dati"] = get_conoscenza().stesa_pubblica(_stesa_o_404(lettura.spread_id))
    return dati


@router.delete("/me/readings/{reading_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancella(reading_id: uuid.UUID, user: CurrentUser, session: DbSession) -> None:
    """Cancellazione vera: la lettura e tutto ciò che contiene spariscono.

    Il movimento di credito resta, senza riferimento: è contabilità, e dice
    che una lettura c'è stata, non cosa diceva.
    """
    if not await ReadingRepository(session).delete(user, reading_id):
        raise HTTPException(status_code=404, detail="Lettura non trovata")
    await AuditRepository(session).record(
        action="reading.delete", actor_id=user.id, target_type="reading", target_id=str(reading_id),
    )
    await analytics.evento(session, analytics.LETTURA_CANCELLATA, utente_id=user.id)
    await session.commit()


@router.post("/me/readings/{reading_id}/feedback")
async def diario(
    reading_id: uuid.UUID, payload: Diario, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    """«Si è avverato?» Serve a chi consulta per rileggersi, e alla console
    per sapere quanto le letture risultano utili."""
    lettura = await _lettura_o_404(ReadingRepository(session), user, reading_id)
    if lettura.status != "completata":
        raise _conflitto("Si annota solo una lettura conclusa")
    lettura.feedback = payload.esito
    lettura.feedback_note = payload.nota
    lettura.feedback_at = utcnow()
    await analytics.evento(session, analytics.LETTURA_FEEDBACK, utente_id=user.id, proprieta={"esito": payload.esito})
    await session.commit()
    return {"feedback": lettura.feedback}


@router.post("/me/readings/{reading_id}/share")
async def condividi(
    reading_id: uuid.UUID, payload: Condivisione, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    """Pubblica (o ritira) un link anonimo alla lettura, con un testo personalizzato.

    Il link mostra domanda, carte e responso, mai il colloquio né il nome:
    l'intervista contiene dettagli che chi consulta ha dato all'oracolo, non
    al mondo. Nelle letture speciali il nome dell'altra persona non esce (vedi
    `public.condivisa`). Il ritiro cancella anche le immagini caricate: un link
    ritirato non deve lasciare un'anteprima raggiungibile.
    """
    lettura = await _lettura_o_404(ReadingRepository(session), user, reading_id)
    if lettura.status != "completata":
        raise _conflitto("Si condivide solo una lettura conclusa")
    if payload.attiva:
        if not lettura.share_token:
            lettura.share_token = secrets.token_urlsafe(16)[:22]
        if payload.testo is not None:
            lettura.share_text = pulisci_testo(payload.testo) or None
    else:
        lettura.share_token = None
        await session.execute(delete(ShareImage).where(ShareImage.reading_id == lettura.id))
    await analytics.evento(session, analytics.LETTURA_CONDIVISA, utente_id=user.id, proprieta={"attiva": payload.attiva})
    await session.commit()
    return {"share_token": lettura.share_token, "share_text": lettura.share_text}
