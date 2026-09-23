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
from typing import Any, AsyncIterator, Dict, Optional

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ...auth.dependencies import CurrentUser, DbSession
from ...billing.credits import CreditiInsufficienti, RegistroCrediti
from ...billing.plans import GestoreAbbonamenti
from ...billing.quote import COSTO_LETTURA, ContatoreQuote
from ...domain.base import utcnow
from ...domain.models import InterviewTurn, Reading, User
from ...domain.repositories import AuditRepository, ReadingRepository
from ...domain.session import SessionFactory
from ...guards.lettura import giudica, segnale_di_crisi, uscita_proibita
from ...llm.base import GenerationError
from ...llm.compiti import Compito
from ...settings import get_settings
from ...tarot import cag, interpretazione
from ...tarot.intervista import prossimo_passo, profilo_da, turni_da
from ...tarot.lettura import (
    StatoNonValido, dignita_di, doppia_valenza, gia_rivelate, posa,
    prevalenze_di, prossima_da_rivelare, wirth,
)
from ...tarot.llm import genera_flusso, genera_testo, richiesta
from ...tarot.numerologia import carta_dell_anima, carta_dell_anno
from ...tarot.shuffle import mescola
from ...tarot.testi import AIUTO, DISCLAIMER, RESPONSO_BLOCCATO, lingua
from ..deps import aggiorna_assegnazioni, get_conoscenza, get_guardrail, provider_per

logger = logging.getLogger(__name__)

router = APIRouter(tags=["letture"])


# ---- modelli di richiesta ---------------------------------------------------


class NuovaLettura(BaseModel):
    spread_id: str = Field(min_length=1, max_length=40)
    question: str = Field(min_length=3, max_length=1000)
    lang: str = Field(default="it", max_length=5)


class RispostaIntervista(BaseModel):
    #: Vuota alla prima chiamata, che chiede la prima domanda.
    risposta: Optional[str] = Field(default=None, max_length=2000)


class Scelta(BaseModel):
    slot: int = Field(ge=0, le=77)


class Diario(BaseModel):
    esito: str = Field(pattern="^(si|in_parte|no)$")
    nota: Optional[str] = Field(default=None, max_length=2000)


class Condivisione(BaseModel):
    attiva: bool = True


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


def carta_json(conoscenza, c, *, completa: bool = False) -> Dict[str, Any]:
    dati: Dict[str, Any] = {
        "posizione": c.posizione,
        "calcolata": c.calcolata,
        "rivelata": c.rivelata,
    }
    if c.rivelata:
        dati.update({
            "carta": conoscenza.carta_pubblica(c.card_id, completa=completa),
            "rovescio": c.rovescio,
            "interpretazione": c.interpretazione,
        })
    return dati


def lettura_json(lettura: Reading, *, dettaglio: bool = True) -> Dict[str, Any]:
    conoscenza = get_conoscenza()
    stesa = conoscenza.stesa(lettura.spread_id) or {}
    dati: Dict[str, Any] = {
        "id": str(lettura.id),
        "spread_id": lettura.spread_id,
        "stesa": stesa.get("nome"),
        "question": lettura.question,
        "status": lettura.status,
        "lang": lettura.lang,
        "consumo": lettura.consumo,
        "created_at": lettura.created_at.isoformat() if lettura.created_at else None,
        "completed_at": lettura.completed_at.isoformat() if lettura.completed_at else None,
        "feedback": lettura.feedback,
        "shared": bool(lettura.share_token),
    }
    if not dettaglio:
        rivelate = [c for c in lettura.cards if c.rivelata]
        dati["carte"] = [conoscenza.carta(c.card_id)["nome_it"] for c in rivelate]
        return dati
    dati.update({
        "context_summary": lettura.context_summary,
        "interview": [
            {"ruolo": t.ruolo, "testo": t.testo, "ordine": t.ordine} for t in lettura.turns
        ],
        "cards": [carta_json(conoscenza, c) for c in lettura.cards],
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
        "feedback_note": lettura.feedback_note,
        "disclaimer": DISCLAIMER[lingua(lettura.lang)],
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
    lang = lingua(payload.lang)

    if segnale_di_crisi(payload.question):
        await AuditRepository(session).record(
            action="reading.crisis", actor_id=user.id, target_type="user", target_id=str(user.id),
        )
        await session.commit()
        return {"crisi": True, "messaggio": AIUTO[lang]}

    gestore = GestoreAbbonamenti(session)
    if not await gestore.tariffe_in_vigore():
        consumo = "omaggio"
    else:
        diritti = await gestore.diritti_di(user.id)
        consumo = "quota" if await ContatoreQuote(session).quota_disponibile(user.id, diritti) else "credito"

    lettura = await ReadingRepository(session).create(
        user, spread_id=stesa["id"], question=payload.question.strip(),
        consumo=consumo, lang=lang, status="intervista",
    )
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
                    "messaggio": "Non hai crediti disponibili per una nuova lettura.",
                    "saldo": exc.disponibili,
                },
            ) from exc
    await session.commit()

    return {
        "id": str(lettura.id),
        "status": lettura.status,
        "consumo": consumo,
        "disclaimer": DISCLAIMER[lang],
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

    await aggiorna_assegnazioni(session)
    stesa = _stesa_o_404(lettura.spread_id)
    passo = await prossimo_passo(
        provider_intervista=provider_per(Compito.INTERVISTA),
        provider_validazione=provider_per(Compito.VALIDAZIONE),
        quesito=lettura.question,
        stesa_nome=stesa["nome"],
        turni=turni_da(lettura.turns),
        max_domande=get_settings().intervista_max_domande,
        lang=lettura.lang,
        profilo=_profilo(user),
    )

    lettura = await _lettura_o_404(repo, user, reading_id, lock=True)
    if passo.completo:
        lettura.context_summary = passo.riassunto
        lettura.status = "ventaglio"
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
    return {"completa": False, "crisi": True, "messaggio": AIUTO[lingua(lettura.lang)]}


# ---- ventaglio e scelta ---------------------------------------------------------


@router.post("/readings/{reading_id}/fan")
async def ventaglio(reading_id: uuid.UUID, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    """Mescola e fissa il mazzo. Al client vanno solo il numero degli slot e
    il commitment: le carte restano sul server finché non si rivelano."""
    repo = ReadingRepository(session)
    lettura = await _lettura_o_404(repo, user, reading_id, lock=True)
    stesa = _stesa_o_404(lettura.spread_id)
    conoscenza = get_conoscenza()

    if lettura.status == "ventaglio":
        fissato = mescola(conoscenza.mazzo_per(stesa))
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

    conoscenza = get_conoscenza()
    stesa = _stesa_o_404(lettura.spread_id)
    carta.rivelata = True
    dignita = dignita_di(lettura, stesa, conoscenza, solo_rivelate=True).get(posizione)
    doppia = doppia_valenza(lettura, carta)
    domanda = interpretazione.messaggio(
        carta=conoscenza.carta(carta.card_id),
        rovescio=carta.rovescio,
        stesa=stesa,
        posizione=conoscenza.posizione(stesa, posizione),
        quesito=lettura.question,
        contesto=lettura.context_summary or "",
        dignita=dignita,
        precedenti=gia_rivelate(lettura, stesa, conoscenza, posizione),
        doppia_valenza=doppia,
        lang=lettura.lang,
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
    provider = provider_per(Compito.INTERPRETAZIONE)

    async def genera() -> AsyncIterator[bytes]:
        yield _sse("carta", evento_carta)
        testo = ""
        try:
            async for pezzo in genera_flusso(provider, richiesta(
                [interpretazione.PROMPT_INTERPRETAZIONE], domanda, temperatura=0.7, max_tokens=500,
            )):
                testo += pezzo
                yield _sse("token", {"testo": pezzo})
        except Exception as exc:  # noqa: BLE001 - errori del fornitore e di rete
            logger.warning("Interpretazione non generata: %s", exc)
            yield _sse("errore", {"messaggio": "L'interpretazione non è disponibile ora: la ritroverai nel responso finale."})

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

    conoscenza = get_conoscenza()
    stesa = _stesa_o_404(lettura.spread_id)
    registro = get_guardrail()
    await aggiorna_assegnazioni(session)
    autore = provider_per(Compito.SINTESI)
    giudice = provider_per(Compito.GIUDIZIO)

    prefisso = cag.prefisso(conoscenza, registro.istruzioni_per("sintesi"))
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
        profilo=_profilo(user), wirth=wirth(lettura, stesa, conoscenza), lang=lang,
    )

    # La transazione della richiesta si chiude prima dello streaming: il
    # responso può richiedere decine di secondi, e tenere aperta una
    # connessione per niente la toglie al pool.
    await session.commit()

    async def scrivi(vincoli: str = "") -> str:
        return await genera_testo(autore, richiesta(
            [prefisso], cag.parte_variabile(**argomenti, vincoli=vincoli),
            temperatura=0.75, max_tokens=1800, cache_dopo=0,
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
            yield _sse("errore", {"messaggio": "Il responso non è stato generato. Puoi riprovare: la lettura resta salvata."})
            return

        yield _sse("fase", {"fase": "guardia"})
        verdetto = await giudica(giudice, registro, quesito=lettura.question, responso=responso)
        esito = "ok"
        if verdetto.esito == "riscrivi":
            yield _sse("fase", {"fase": "revisione"})
            try:
                responso = await scrivi(verdetto.vincoli())
                verdetto = await giudica(giudice, registro, quesito=lettura.question, responso=responso)
                esito = "riscritto" if verdetto.ok else "bloccato"
            except Exception:  # noqa: BLE001
                esito = "bloccato"
        elif verdetto.esito == "blocca":
            esito = "bloccato"
        if esito == "bloccato":
            responso = RESPONSO_BLOCCATO[lang]
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
        "disclaimer": DISCLAIMER[lingua(lettura.lang)],
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
    """Pubblica (o ritira) un link anonimo alla lettura.

    Il link mostra domanda, carte e responso, mai il colloquio né il nome:
    l'intervista contiene dettagli che chi consulta ha dato all'oracolo, non
    al mondo.
    """
    lettura = await _lettura_o_404(ReadingRepository(session), user, reading_id)
    if lettura.status != "completata":
        raise _conflitto("Si condivide solo una lettura conclusa")
    if payload.attiva and not lettura.share_token:
        lettura.share_token = secrets.token_urlsafe(16)[:22]
    elif not payload.attiva:
        lettura.share_token = None
    await session.commit()
    return {"share_token": lettura.share_token}
