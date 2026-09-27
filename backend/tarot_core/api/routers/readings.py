"""Il percorso di una lettura, dall'apertura al responso.

| passo | endpoint | stato dopo |
|---|---|---|
| apertura, pagamento, disclaimer | `POST /readings` | `intervista` |
| una domanda di contesto per volta | `POST /readings/{id}/interview` | `ventaglio` a fine intervista |
| mescolamento e ventaglio | `POST /readings/{id}/fan` | `scelta` |
| una carta per volta | `POST /readings/{id}/pick` | `rivelazione` a carte scelte |
| rivelazione e lettura immediata (SSE) | `POST /readings/{id}/reveal/{pos}` | `sintesi` all'ultima |
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
from typing import Any, AsyncIterator, Dict, List, Optional

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator, model_validator
from sqlalchemy import delete
from sqlalchemy.orm.attributes import set_committed_value

from ...auth.dependencies import CurrentUser, DbSession
from ...billing.credits import CreditiInsufficienti, RegistroCrediti
from ...billing.plans import GestoreAbbonamenti
from ...billing.quote import COSTO_LETTURA, ContatoreQuote
from ...domain.base import utcnow
from ...domain.models import InterviewTurn, Reading, User
from ...domain.repositories import AuditRepository, ReadingRepository
from ...domain.share_models import ShareImage
from ...domain.session import SessionFactory
from ...guards.lettura import giudica, segnale_di_crisi, uscita_proibita
from ...llm.base import GenerationError
from ...llm.compiti import Compito
from ...settings import get_settings
from ...tarot import cag, interpretazione
from ...tarot.condivisione import pulisci_testo
from ...tarot.intervista import IntervistaNonRiuscita, prossimo_passo, profilo_da, trascrizione, turni_da
from ...tarot.lettura import (
    StatoNonValido, dignita_di, doppia_valenza, gia_rivelate, note_di_posizione,
    posa, posa_manuale, prevalenze_di, prossima_da_rivelare, wirth,
)
from ...tarot.llm import genera_flusso, genera_testo, richiesta
from ...tarot.numerologia import carta_dell_anima, carta_dell_anno
from ...tarot.persone import (
    LUNGHEZZA_COGNOME, LUNGHEZZA_GENERE_ALTRO, LUNGHEZZA_NOME, Persone, blocco_compatibilita,
    blocco_persone, compatibilita_json, da_json, mancanti, parole_neutre, pulisci, soggetto_testo,
)
from ...tarot.shuffle import mescola
from ...tarot.lingue import in_lingua, lingua, rileva_lingua
from ...tarot.testi import (
    AIUTO, CREDITI_ESAURITI, DISCLAIMER, INTERPRETAZIONE_NON_DISPONIBILE,
    MODELLO_NON_DISPONIBILE, PARTNER_MANCANTE, PARTNER_NON_AMMESSO,
    PROFILO_INCOMPLETO, RESPONSO_BLOCCATO, RESPONSO_NON_GENERATO,
)
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


class RispostaIntervista(BaseModel):
    #: Vuota alla prima chiamata, che chiede la prima domanda.
    risposta: Optional[str] = Field(default=None, max_length=2000)


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


async def _lettura_o_404(repo: ReadingRepository, user: User, reading_id: uuid.UUID, *, lock: bool = False) -> Reading:
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


def _istantanea_persone(user: User, partner: PersonaIn) -> Dict[str, Any]:
    """Le due persone come stanno adesso: si salvano con la lettura.

    È una copia: se poi l'utente corregge la scheda, la lettura resta coerente
    con il responso. Il cognome sta qui e non va oltre lo storico.
    """
    assert user.birth_date is not None
    return {
        "v": 1,
        "tu": {
            "genere": user.gender, "genere_altro": user.gender_custom,
            "trans": bool(user.is_trans), "nascita": user.birth_date.isoformat(),
        },
        "partner": {
            "nome": pulisci(partner.nome, LUNGHEZZA_NOME),
            "cognome": pulisci(partner.cognome, LUNGHEZZA_COGNOME) or None,
            "genere": partner.genere,
            "genere_altro": pulisci(partner.genere_altro, LUNGHEZZA_GENERE_ALTRO) or None,
            "trans": partner.trans,
            "nascita": partner.nascita.isoformat(),
        },
    }


def _persone_dell_apertura(
    user: User, payload: "NuovaLettura", categoria: str, lang: str,
) -> Optional[Dict[str, Any]]:
    """Valida partner e scheda per il tipo di lettura e ne fa l'istantanea.

    `None` per la lettura standard. Per le speciali: 422 `partner_mancante`,
    `partner_non_ammesso` o `profilo_incompleto` (con l'elenco di ciò che manca
    nella scheda: il frontend lo chiede e riprova).
    """
    if categoria == "standard":
        if payload.partner is not None:
            raise _errore_422("partner_non_ammesso", PARTNER_NON_AMMESSO, lang)
        return None
    if payload.partner is None:
        raise _errore_422("partner_mancante", PARTNER_MANCANTE, lang)
    da_completare = mancanti(user)
    if da_completare:
        raise _errore_422("profilo_incompleto", PROFILO_INCOMPLETO, lang, mancanti=da_completare)
    return _istantanea_persone(user, payload.partner)


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
            "interpretazione": c.interpretazione,
        })
    return dati


def _soggetti(stesa: Dict[str, Any], persone: Optional[Persone]) -> Optional[Dict[int, str]]:
    """Di chi parla ogni posizione, in testo: lo decide il codice dai dati della stesa."""
    if persone is None:
        return None
    return {p["n"]: soggetto_testo(p.get("soggetto"), persone) for p in stesa["posizioni"]}


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
    conoscenza = get_conoscenza()
    categoria = conoscenza.categoria_di(stesa)
    persone = _persone_dell_apertura(user, payload, categoria, lang)

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
        await AuditRepository(session).record(
            action="reading.crisis", actor_id=user.id, target_type="user", target_id=str(user.id),
        )
        await session.commit()
        return {"crisi": True, "messaggio": in_lingua(AIUTO, lang)}

    # Prima di addebitare qualunque cosa: senza un modello vero non c'è lettura.
    await verifica_modello(session, lang)

    gestore = GestoreAbbonamenti(session)
    if not await gestore.tariffe_in_vigore():
        consumo = "omaggio"
    else:
        diritti = await gestore.diritti_di(user.id)
        consumo = "quota" if await ContatoreQuote(session).quota_disponibile(user.id, diritti) else "credito"

    lettura = await ReadingRepository(session).create(
        user, spread_id=stesa["id"], question=payload.question.strip(),
        consumo=consumo, lang=lang, status="intervista", persone=persone,
        manuale=assegnazioni_manuali is not None,
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


# ---- intervista ---------------------------------------------------------------


@router.post("/readings/{reading_id}/interview")
async def intervista(
    reading_id: uuid.UUID, payload: RispostaIntervista, user: CurrentUser,
    session: DbSession,
) -> Dict[str, Any]:
    """Registra la risposta e restituisce la prossima domanda, o chiude.

    Risposta JSON e non SSE: l'uscita del modello è un JSON che non si può
    mostrare a metà. Il frontend la scrive a macchina.
    """
    repo = ReadingRepository(session)
    lettura = await _lettura_o_404(repo, user, reading_id, lock=True)
    if lettura.status != "intervista":
        raise _conflitto("L'intervista è già conclusa")

    turni = list(lettura.turns)
    attende_risposta = bool(turni) and turni[-1].ruolo == "oracolo"
    if payload.risposta is not None and payload.risposta.strip():
        if not attende_risposta:
            raise _conflitto("Nessuna domanda in attesa di risposta")
        testo = payload.risposta.strip()
        if segnale_di_crisi(testo):
            return await _chiudi_per_crisi(session, user, lettura)
        lettura.turns.append(InterviewTurn(
            ordine=len(turni) + 1, ruolo="utente", testo=testo, created_at=utcnow(),
        ))
    elif attende_risposta:
        # Una seconda chiamata vuota (una pagina ricaricata) ripropone la
        # domanda in attesa invece di generarne un'altra.
        return {"completa": False, "domanda": turni[-1].testo, "ordine": turni[-1].ordine}
    await session.commit()

    await verifica_modello(session, lettura.lang)          # rilegge già fornitori e assegnazioni
    stesa = _stesa_o_404(lettura.spread_id)
    impostazioni = get_settings()
    conoscenza = get_conoscenza()
    categoria = conoscenza.categoria_di(stesa)
    persone = da_json(lettura.persone)
    # Nelle letture speciali il profilo del prompt sono le due persone (col
    # partner senza cognome); nella standard, la carta dell'anima e dell'anno.
    profilo = _profilo(user) if persone is None else blocco_persone(persone, conoscenza) + "\n"
    try:
        passo = await prossimo_passo(
            provider_intervista=provider_per(Compito.INTERVISTA, persone),
            provider_validazione=provider_per(Compito.VALIDAZIONE, persone),
            quesito=lettura.question,
            stesa_nome=stesa["nome"],
            stesa_descrizione=(
                f"{stesa['descrizione']} Posizioni: "
                + "; ".join(f"{p['n']}. {p['nome']}" for p in stesa["posizioni"])
            ),
            turni=turni_da(lettura.turns),
            min_domande=impostazioni.intervista_min_domande,
            max_domande=impostazioni.intervista_max_domande,
            lang=lettura.lang,
            profilo=profilo,
            categoria=categoria,
            nota=stesa.get("nota_intervista", ""),
            parole_neutre=parole_neutre(persone),
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

    lettura = await _lettura_o_404(repo, user, reading_id, lock=True)
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
    return {"completa": False, "domanda": passo.domanda, "ordine": ordine, "scartate": passo.scartate}


async def _chiudi_per_crisi(session, user: User, lettura: Reading) -> Dict[str, Any]:
    """Ferma la lettura e restituisce il credito: chi è in crisi riceve aiuto,
    non carte."""
    lettura.status = "annullata"
    if lettura.consumo == "credito":
        await RegistroCrediti(session).rimborsa(
            user.id, COSTO_LETTURA, reading_id=lettura.id, note="lettura sospesa: segnale di crisi",
        )
    await AuditRepository(session).record(
        action="reading.crisis", actor_id=user.id, target_type="reading", target_id=str(lettura.id),
    )
    await session.commit()
    return {"completa": False, "crisi": True, "messaggio": in_lingua(AIUTO, lettura.lang)}


# ---- ventaglio e scelta ---------------------------------------------------------


@router.post("/readings/{reading_id}/fan")
async def ventaglio(
    reading_id: uuid.UUID, user: CurrentUser, session: DbSession,
    payload: Optional[TaglioMazzo] = None,
) -> Dict[str, Any]:
    """Mescola, taglia dove ha cliccato chi consulta e fissa il mazzo. Al
    client vanno solo il numero degli slot e il commitment: le carte restano
    sul server finché non si rivelano."""
    repo = ReadingRepository(session)
    lettura = await _lettura_o_404(repo, user, reading_id, lock=True)
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
    reading_id: uuid.UUID, payload: Scelta, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    repo = ReadingRepository(session)
    lettura = await _lettura_o_404(repo, user, reading_id, lock=True)
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
    reading_id: uuid.UUID, posizione: int, user: CurrentUser, session: DbSession,
    fabbrica: SessionFactory,
) -> StreamingResponse:
    """Gira la carta e ne dà l'interpretazione immediata, in streaming.

    Le carte si rivelano in ordine di posizione: la lettura è un racconto, e
    l'interpretazione di ciascuna tiene conto di quelle già viste.
    """
    repo = ReadingRepository(session)
    lettura = await _lettura_o_404(repo, user, reading_id, lock=True)
    if lettura.status != "rivelazione":
        raise _conflitto("Non ci sono carte da rivelare")
    carta = prossima_da_rivelare(lettura)
    if carta is None or carta.posizione != posizione:
        raise _conflitto("Le carte si rivelano in ordine")

    await verifica_modello(session, lettura.lang)
    conoscenza = get_conoscenza()
    stesa = _stesa_o_404(lettura.spread_id)
    carta.rivelata = True
    dignita = dignita_di(lettura, stesa, conoscenza, solo_rivelate=True).get(posizione)
    doppia = doppia_valenza(lettura, carta)
    lang = lingua(lettura.lang)
    categoria = conoscenza.categoria_di(stesa)
    persone_lettura = da_json(lettura.persone)
    soggetti = _soggetti(stesa, persone_lettura)
    # Le interpretazioni delle carte sono brevi e hanno le loro regole: nelle
    # letture speciali ricevono in più solo ciò che è specifico del tipo di lettura.
    sistema_interpretazione = [interpretazione.PROMPT_INTERPRETAZIONE]
    if categoria != "standard":
        sistema_interpretazione.append(interpretazione.PROMPT_INTERPRETAZIONE_RELAZIONE)
        specifiche = get_guardrail().istruzioni_per("interpretazione", categoria, solo_categoria=True)
        if specifiche:
            sistema_interpretazione.append("# Regole di sicurezza della relazione\n\n" + "\n\n".join(specifiche))
    note = note_di_posizione(
        stesa, posizione, [c.posizione for c in lettura.cards if c.rivelata and c.posizione != posizione],
    )
    domanda = interpretazione.messaggio(
        carta=conoscenza.carta(carta.card_id),
        rovescio=carta.rovescio,
        stesa=stesa,
        posizione=conoscenza.posizione(stesa, posizione),
        quesito=lettura.question,
        contesto=lettura.context_summary or "",
        dignita=dignita,
        precedenti=gia_rivelate(lettura, stesa, conoscenza, posizione, lang),
        note=note,
        doppia_valenza=doppia,
        colloquio=trascrizione(turni_da(lettura.turns)),
        nomi=(conoscenza.nome_carta(carta.card_id, lang), conoscenza.nome_posizione(stesa, posizione, lang)),
        lang=lang,
        persone=blocco_persone(persone_lettura, conoscenza) if persone_lettura else "",
        soggetto=(soggetti or {}).get(posizione, ""),
    )
    evento_carta = {
        "posizione": posizione,
        "carta": conoscenza.carta_pubblica(carta.card_id),
        "rovescio": carta.rovescio,
        "calcolata": carta.calcolata,
        "doppia_valenza": doppia,
        "dignita": dignita,
    }
    await session.commit()
    await aggiorna_assegnazioni(session)
    provider = provider_per(Compito.INTERPRETAZIONE, persone_lettura)

    async def genera() -> AsyncIterator[bytes]:
        yield _sse("carta", evento_carta)
        testo = ""
        try:
            async for pezzo in genera_flusso(provider, richiesta(
                sistema_interpretazione, domanda, temperatura=0.7, max_tokens=500,
            )):
                testo += pezzo
                yield _sse("token", {"testo": pezzo})
        except Exception as exc:  # noqa: BLE001 - errori del fornitore e di rete
            logger.warning("Interpretazione non generata: %s", exc)
            yield _sse("errore", {"messaggio": in_lingua(INTERPRETAZIONE_NON_DISPONIBILE, lettura.lang)})

        testo = testo.strip()
        if testo and uscita_proibita(testo):
            # Il guardrail leggero delle carte: una formula proibita non
            # resta sullo schermo.
            testo = _interpretazione_prudente(conoscenza.carta(carta.card_id), carta.rovescio, lettura.lang)
            yield _sse("sostituisci", {"testo": testo})

        async with fabbrica() as s:
            r = await ReadingRepository(s).get_for_update(user, reading_id)
            if r is not None:
                for c in r.cards:
                    if c.posizione == posizione:
                        c.interpretazione = testo or None
                if prossima_da_rivelare(r) is None:
                    r.status = "sintesi"
                await s.commit()
                ultima = r.status == "sintesi"
            else:
                ultima = False
        yield _sse("fine", {"posizione": posizione, "interpretazione": testo, "ultima": ultima})

    return _flusso(genera())


def _interpretazione_prudente(carta: Dict[str, Any], rovescio: bool, lang: str) -> str:
    """Il significato del mazzo, al posto di un testo che il filtro ha fermato."""
    return carta.get("rovescio" if rovescio else "dritto") or ""


# ---- sintesi ------------------------------------------------------------------------


@router.post("/readings/{reading_id}/synthesis")
async def sintesi(
    reading_id: uuid.UUID, user: CurrentUser, session: DbSession, fabbrica: SessionFactory,
) -> StreamingResponse:
    """Il responso finale: CAG, poi guardrail, poi il testo all'utente.

    Il responso **non** si mostra mentre il modello lo scrive: prima passa dal
    giudice, e solo un testo approvato arriva allo schermo. Nel frattempo il
    flusso manda eventi di fase, così la connessione resta viva e l'utente
    vede che la lettura sta prendendo forma.
    """
    repo = ReadingRepository(session)
    lettura = await _lettura_o_404(repo, user, reading_id)
    lang = lingua(lettura.lang)

    if lettura.status == "completata":
        chiusura = _chiusura(lettura, await RegistroCrediti(session).saldo(user.id))
        await session.commit()

        async def rilegge() -> AsyncIterator[bytes]:
            yield _sse("token", {"testo": lettura.synthesis or ""})
            yield _sse("fine", chiusura)
        return _flusso(rilegge())

    if lettura.status != "sintesi":
        raise _conflitto("Il responso arriva dopo aver rivelato tutte le carte")

    await verifica_modello(session, lang)
    conoscenza = get_conoscenza()
    stesa = _stesa_o_404(lettura.spread_id)
    registro = get_guardrail()
    await aggiorna_assegnazioni(session)
    persone_lettura = da_json(lettura.persone)
    autore = provider_per(Compito.SINTESI, persone_lettura)
    giudice = provider_per(Compito.GIUDIZIO, persone_lettura)

    categoria = conoscenza.categoria_di(stesa)
    prefisso = cag.prefisso(conoscenza, registro.istruzioni_per("sintesi", categoria), categoria)
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
        profilo=_profilo(user) if persone_lettura is None else "",
        wirth=wirth(lettura, stesa, conoscenza), lang=lang,
        colloquio=trascrizione(turni_da(lettura.turns)),
        persone=blocco_persone(persone_lettura, conoscenza) if persone_lettura else "",
        compatibilita=blocco_compatibilita(persone_lettura, conoscenza) if persone_lettura else "",
        soggetti=_soggetti(stesa, persone_lettura),
    )

    # La transazione della richiesta si chiude prima dello streaming: il
    # responso può richiedere decine di secondi, e tenere aperta una
    # connessione per niente la toglie al pool.
    await session.commit()

    async def scrivi(vincoli: str = "") -> str:
        return await genera_testo(autore, richiesta(
            [prefisso], cag.parte_variabile(**argomenti, vincoli=vincoli),
            # Le letture speciali hanno una sezione in più e i nomi dei due.
            temperatura=0.75, max_tokens=1800 if categoria == "standard" else 2200, cache_dopo=0,
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
            yield _sse("errore", {"messaggio": in_lingua(RESPONSO_NON_GENERATO, lang)})
            return

        yield _sse("fase", {"fase": "guardia"})
        verdetto = await giudica(
            giudice, registro, quesito=lettura.question, responso=responso, categoria=categoria,
        )
        esito = "ok"
        if verdetto.esito == "riscrivi":
            yield _sse("fase", {"fase": "revisione"})
            try:
                responso = await scrivi(verdetto.vincoli())
                verdetto = await giudica(
                    giudice, registro, quesito=lettura.question, responso=responso, categoria=categoria,
                )
                esito = "riscritto" if verdetto.ok else "bloccato"
            except Exception:  # noqa: BLE001
                esito = "bloccato"
        elif verdetto.esito == "blocca":
            esito = "bloccato"
        if esito == "bloccato":
            responso = in_lingua(RESPONSO_BLOCCATO, lang)
        elif not verdetto.verificato:
            logger.warning("Responso della lettura %s non verificato dal giudice", reading_id)

        async with fabbrica() as s:
            r = await ReadingRepository(s).get_for_update(user, reading_id)
            if r is None:
                return
            r.synthesis = responso
            r.guard_outcome = esito
            r.status = "completata"
            r.completed_at = utcnow()
            if esito == "bloccato":
                await AuditRepository(s).record(
                    action="reading.guard_block", actor_id=user.id,
                    target_type="reading", target_id=str(reading_id),
                    after={"violazioni": verdetto.violazioni},
                )
            await s.commit()
            saldo = await RegistroCrediti(s).saldo(user.id)
            chiusura = _chiusura(r, saldo)

        yield _sse("fase", {"fase": "responso", "guardia": esito})
        # Il testo esce a frammenti: già approvato, ma lo si scrive davanti
        # all'utente come si gira una carta — un colpo solo sarebbe un muro.
        for i in range(0, len(responso), 24):
            yield _sse("token", {"testo": responso[i:i + 24]})
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
    await session.commit()
    return {"share_token": lettura.share_token, "share_text": lettura.share_text}
