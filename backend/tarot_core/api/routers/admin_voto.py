"""La console: tornate di voto, mazzi candidati, statistiche, accettazione dei vincitori (v7, Fase K).

**Riserva e tornate ("tornate elettorali", estensione della Fase K)**: un candidato (`DeckCandidate`)
può esistere prima come proposta in riserva (`round_id is None`) — con nome, descrizione e carte di
prova già caricate — e viene assegnato a una tornata solo quando l'admin la crea scegliendo fra le
proposte in riserva e dichiarando la scadenza (`chiude_il`). La tornata si chiude poi da sola: vedi
`voting_repositories.chiudi_tornate_scadute`, chiamata a ogni lettura (qui e in `voto.py`)."""
from __future__ import annotations

import asyncio
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from lanterna.rete import ip_client
from pydantic import BaseModel, Field
from sqlalchemy import select

from ...auth.dependencies import CurrentUser, DbSession, require_role
from ...domain import deck_repositories, voting_repositories
from ...domain.base import utcnow
from ...domain.blog_models import MediaImage
from ...domain.blog_repositories import assicura_miniatura
from ...domain.deck_models import Deck
from ...domain.repositories import AuditRepository
from ...domain.voting_models import DeckCandidate, DeckSuggestion, VotingRound
from ...tarot import blog as regole
from .blog import url_immagine, url_miniatura

router = APIRouter(prefix="/admin/voto", tags=["voto"], dependencies=[Depends(require_role("admin"))])


def _ip(request: Request) -> Optional[str]:
    return ip_client(request)


#: Le carte d'esempio di un candidato: al massimo cinque, nell'ordine scelto in console.
MAX_CAMPIONI = 5


def _campione_json(camp: Dict[str, Any]) -> Dict[str, Any]:
    media_id = uuid.UUID(camp["media_id"])
    return {
        "media_id": str(media_id), "etichetta": camp.get("etichetta"),
        "url": url_immagine(media_id), "mini": url_miniatura(media_id),
    }


def _candidato_json(c: DeckCandidate, conteggi: Dict[uuid.UUID, int]) -> Dict[str, Any]:
    return {
        "id": str(c.id), "nome": c.nome, "descrizione": c.descrizione,
        "campioni": [_campione_json(camp) for camp in c.campioni if camp.get("media_id")],
        "voti": conteggi.get(c.id, 0),
        "accettato": c.accettato,
        "deck_id": c.deck_id,
        "round_id": str(c.round_id) if c.round_id else None,
    }


def _tornata_json(r: VotingRound) -> Dict[str, Any]:
    return {
        "id": str(r.id), "stato": r.stato, "aperta_il": r.created_at.isoformat(),
        "chiude_il": r.chiude_il.isoformat() if r.chiude_il else None,
        "chiusa_il": r.chiusa_il.isoformat() if r.chiusa_il else None,
    }


# ---- riserva di proposte --------------------------------------------------------------------------


class CandidatoIn(BaseModel):
    nome: str = Field(min_length=1, max_length=80)
    descrizione: Optional[str] = Field(default=None, max_length=2000)


@router.get("/candidati/disponibili")
async def proposte_disponibili(session: DbSession) -> List[Dict[str, Any]]:
    """La riserva: proposte già inserite (con eventuali carte di prova) ma non ancora scelte per
    nessuna tornata — da qui si scelgono i candidati alla creazione di una nuova tornata."""
    lista = await voting_repositories.proposte_disponibili(session)
    return [_candidato_json(c, {}) for c in lista]


@router.post("/candidati", status_code=201)
async def crea_proposta(payload: CandidatoIn, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    """Aggiunge una proposta alla riserva, senza assegnarla a nessuna tornata: le carte di prova si
    caricano subito dopo con `POST /candidati/{id}/campioni`, prima ancora che esista una tornata."""
    candidato = DeckCandidate(round_id=None, nome=payload.nome.strip(), descrizione=(payload.descrizione or "").strip() or None)
    session.add(candidato)
    await session.flush()
    await AuditRepository(session).record(
        action="voto.proposta.crea", actor_id=user.id, target_type="deck_candidate", target_id=str(candidato.id),
        after={"nome": candidato.nome}, ip=_ip(request),
    )
    await session.commit()
    return _candidato_json(candidato, {})


# ---- tornate ------------------------------------------------------------------------------------


@router.get("/tornate")
async def tornate(session: DbSession) -> List[Dict[str, Any]]:
    if await voting_repositories.chiudi_tornate_scadute(session):
        await session.commit()
    righe = (await session.execute(select(VotingRound).order_by(VotingRound.created_at.desc()))).scalars().all()
    return [_tornata_json(r) for r in righe]


class TornataIn(BaseModel):
    candidate_ids: List[uuid.UUID] = Field(min_length=1)
    #: La scadenza dichiarata dall'admin: deve essere nel futuro, la tornata si chiude da sola
    #: quando passa (vedi `voting_repositories.chiudi_tornate_scadute`).
    chiude_il: datetime


@router.post("/tornate", status_code=201)
async def crea_tornata(payload: TornataIn, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    """Crea una tornata scegliendo i candidati fra le proposte in riserva («tornate elettorali»): non
    se ne crea più di nuovi al volo qui — le proposte si preparano prima con `POST /candidati`."""
    if payload.chiude_il <= utcnow():
        raise HTTPException(status_code=400, detail="La scadenza della votazione deve essere nel futuro")

    candidati = list((await session.execute(
        select(DeckCandidate).where(DeckCandidate.id.in_(payload.candidate_ids))
    )).scalars())
    trovati = {c.id: c for c in candidati}
    mancanti = set(payload.candidate_ids) - trovati.keys()
    if mancanti:
        raise HTTPException(status_code=400, detail=f"Proposte non trovate: {sorted(str(m) for m in mancanti)}")
    già_in_una_tornata = [c.nome for c in candidati if c.round_id is not None]
    if già_in_una_tornata:
        raise HTTPException(status_code=400, detail=f"Già assegnate a un'altra tornata: {già_in_una_tornata}")

    tornata = VotingRound(chiude_il=payload.chiude_il)
    session.add(tornata)
    await session.flush()
    for c in candidati:
        c.round_id = tornata.id
    await AuditRepository(session).record(
        action="voto.tornata.crea", actor_id=user.id, target_type="voting_round", target_id=str(tornata.id),
        after={"candidati": [str(c) for c in payload.candidate_ids], "chiude_il": payload.chiude_il.isoformat()},
        ip=_ip(request),
    )
    await session.commit()
    return _tornata_json(tornata)


@router.post("/tornate/{round_id}/chiudi")
async def chiudi_tornata(round_id: uuid.UUID, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    tornata = await session.get(VotingRound, round_id)
    if tornata is None:
        raise HTTPException(status_code=404, detail="Tornata non trovata")
    tornata.stato = "chiusa"
    tornata.chiusa_il = utcnow()
    await AuditRepository(session).record(
        action="voto.tornata.chiudi", actor_id=user.id, target_type="voting_round", target_id=str(round_id),
        ip=_ip(request),
    )
    await session.commit()
    return {"id": str(tornata.id), "stato": tornata.stato}


@router.get("/tornate/{round_id}/candidati")
async def candidati(round_id: uuid.UUID, session: DbSession) -> List[Dict[str, Any]]:
    lista = await voting_repositories.candidati_di(session, round_id)
    conteggi = await voting_repositories.conteggio_per_candidato(session, round_id)
    return [_candidato_json(c, conteggi) for c in lista]


# ---- candidati (già assegnati a una tornata) -----------------------------------------------------


class CandidatoMod(BaseModel):
    nome: Optional[str] = Field(default=None, min_length=1, max_length=80)
    descrizione: Optional[str] = Field(default=None, max_length=2000)


@router.put("/candidati/{candidate_id}")
async def modifica_candidato(
    candidate_id: uuid.UUID, payload: CandidatoMod, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    candidato = await session.get(DeckCandidate, candidate_id)
    if candidato is None:
        raise HTTPException(status_code=404, detail="Candidato non trovato")
    if payload.nome is not None:
        candidato.nome = payload.nome.strip()
    if payload.descrizione is not None:
        candidato.descrizione = payload.descrizione.strip() or None
    await AuditRepository(session).record(
        action="voto.candidato.modifica", actor_id=user.id, target_type="deck_candidate", target_id=str(candidate_id),
        ip=_ip(request),
    )
    await session.commit()
    conteggi = await voting_repositories.conteggio_per_candidato(session, candidato.round_id) if candidato.round_id else {}
    return _candidato_json(candidato, conteggi)


@router.delete("/candidati/{candidate_id}", status_code=204)
async def elimina_candidato(candidate_id: uuid.UUID, request: Request, user: CurrentUser, session: DbSession) -> None:
    candidato = await session.get(DeckCandidate, candidate_id)
    if candidato is None:
        raise HTTPException(status_code=404, detail="Candidato non trovato")
    await session.delete(candidato)
    await AuditRepository(session).record(
        action="voto.candidato.elimina", actor_id=user.id, target_type="deck_candidate", target_id=str(candidate_id),
        ip=_ip(request),
    )
    await session.commit()


@router.post("/candidati/{candidate_id}/campioni")
async def carica_campione(
    candidate_id: uuid.UUID, request: Request, user: CurrentUser, session: DbSession,
    etichetta: Optional[str] = Query(default=None, max_length=80),
) -> Dict[str, Any]:
    """Carica una carta d'esempio (corpo = immagine grezza, stesso pattern di `POST /admin/media`): si elabora e si
    salva come `MediaImage(uso="voto")`, poi si aggiunge in fondo a `campioni`. Al massimo `MAX_CAMPIONI` per
    candidato: la console ne manda più d'una di seguito (selezione multipla), una per richiesta. L'etichetta è
    facoltativa (la console usa il nome del file senza estensione)."""
    candidato = await session.get(DeckCandidate, candidate_id, with_for_update=True)
    if candidato is None:
        raise HTTPException(status_code=404, detail="Candidato non trovato")
    if len(candidato.campioni) >= MAX_CAMPIONI:
        raise HTTPException(status_code=409, detail=f"Al massimo {MAX_CAMPIONI} carte d'esempio per candidato.")
    etichetta = (etichetta or "").strip() or None
    if not request.headers.get("content-type", "").startswith("image/"):
        raise HTTPException(status_code=415, detail="Serve un'immagine")
    if int(request.headers.get("content-length") or 0) > regole.MAX_CARICO_IMMAGINE:
        raise HTTPException(status_code=413, detail="Immagine troppo grande")
    try:
        webp, larghezza, altezza = await asyncio.to_thread(regole.prepara_immagine_articolo, await request.body())
    except regole.ImmagineNonValida as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    img = MediaImage(uso="voto", webp=webp, larghezza=larghezza, altezza=altezza, owner_id=user.id)
    await assicura_miniatura(img)
    session.add(img)
    await session.flush()
    candidato.campioni = [*candidato.campioni, {"etichetta": etichetta, "media_id": str(img.id)}]
    await AuditRepository(session).record(
        action="voto.candidato.campione", actor_id=user.id, target_type="deck_candidate", target_id=str(candidate_id),
        after={"etichetta": etichetta}, ip=_ip(request),
    )
    await session.commit()
    return _campione_json({"etichetta": etichetta, "media_id": str(img.id)})


class OrdineCampioniIn(BaseModel):
    #: Gli id delle immagini (`media_id`) nel nuovo ordine: esattamente quelle che il candidato ha già.
    ordine: List[uuid.UUID] = Field(max_length=MAX_CAMPIONI)


@router.put("/candidati/{candidate_id}/campioni")
async def riordina_campioni(
    candidate_id: uuid.UUID, payload: OrdineCampioniIn, request: Request, user: CurrentUser, session: DbSession,
) -> List[Dict[str, Any]]:
    """Il nuovo ordine delle carte d'esempio (la prima è quella che si vede per prima sul sito)."""
    candidato = await session.get(DeckCandidate, candidate_id, with_for_update=True)
    if candidato is None:
        raise HTTPException(status_code=404, detail="Candidato non trovato")
    per_id = {camp["media_id"]: camp for camp in candidato.campioni if camp.get("media_id")}
    nuovo = [str(m) for m in payload.ordine]
    if sorted(nuovo) != sorted(per_id) or len(set(nuovo)) != len(nuovo):
        raise HTTPException(status_code=409, detail="L'ordine deve contenere esattamente le carte d'esempio del candidato.")
    candidato.campioni = [per_id[m] for m in nuovo]
    await AuditRepository(session).record(
        action="voto.candidato.campioni_ordine", actor_id=user.id, target_type="deck_candidate",
        target_id=str(candidate_id), after={"ordine": nuovo}, ip=_ip(request),
    )
    await session.commit()
    return [_campione_json(camp) for camp in candidato.campioni]


@router.delete("/candidati/{candidate_id}/campioni/{media_id}", status_code=204)
async def elimina_campione(
    candidate_id: uuid.UUID, media_id: uuid.UUID, request: Request, user: CurrentUser, session: DbSession,
) -> None:
    """Toglie una carta d'esempio dal candidato e ne cancella l'immagine (`MediaImage(uso="voto")`: non la usa
    nessun altro)."""
    candidato = await session.get(DeckCandidate, candidate_id, with_for_update=True)
    if candidato is None:
        raise HTTPException(status_code=404, detail="Candidato non trovato")
    resto = [camp for camp in candidato.campioni if camp.get("media_id") != str(media_id)]
    if len(resto) == len(candidato.campioni):
        raise HTTPException(status_code=404, detail="Carta d'esempio non trovata")
    candidato.campioni = resto
    img = await session.get(MediaImage, media_id)
    if img is not None and img.uso == "voto":
        await session.delete(img)
    await AuditRepository(session).record(
        action="voto.candidato.campione_elimina", actor_id=user.id, target_type="deck_candidate",
        target_id=str(candidate_id), after={"media_id": str(media_id)}, ip=_ip(request),
    )
    await session.commit()


# ---- generare un mazzo da un candidato, vincitore o no ---------------------------------------------


async def _deck_per_candidato(session: DbSession, candidato: DeckCandidate) -> Deck:
    """Crea (o recupera, se già fatto) il `Deck` reale collegato a un candidato — indipendente
    dall'esito della votazione: l'ha vinta (`accetta_vincitori`) o no («generare da GUI anche i mazzi
    non vincitori», estensione della Fase K). Senza prezzo/artwork: da completare in console e con la
    pipeline `crea-mazzo-tarocchi` usando lo slug qui assegnato."""
    if candidato.deck_id is not None:
        mazzo = await session.get(Deck, candidato.deck_id)
        if mazzo is not None:
            return mazzo
    slug_base = "".join(ch.lower() if ch.isalnum() else "-" for ch in candidato.nome).strip("-") or "mazzo"
    slug, tentativo = slug_base, 0
    while await deck_repositories.per_slug(session, slug) is not None:
        tentativo += 1
        slug = f"{slug_base}-{tentativo}"
    mazzo = Deck(slug=slug, nome=candidato.nome, descrizione=candidato.descrizione, attivo=False)
    session.add(mazzo)
    await session.flush()
    candidato.deck_id = mazzo.id
    return mazzo


@router.post("/candidati/{candidate_id}/genera-mazzo")
async def genera_mazzo_da_candidato(
    candidate_id: uuid.UUID, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    """Crea il `Deck` di un candidato **senza** accettarlo come vincitore né toccare la tornata:
    l'admin può voler realizzare anche un mazzo che non ha vinto la votazione. Idempotente — un
    candidato con `deck_id` già impostato ritorna lo stesso mazzo."""
    candidato = await session.get(DeckCandidate, candidate_id)
    if candidato is None:
        raise HTTPException(status_code=404, detail="Candidato non trovato")
    mazzo = await _deck_per_candidato(session, candidato)
    await AuditRepository(session).record(
        action="voto.candidato.genera_mazzo", actor_id=user.id, target_type="deck_candidate", target_id=str(candidate_id),
        after={"deck_id": mazzo.id, "slug": mazzo.slug}, ip=_ip(request),
    )
    await session.commit()
    return {"deck_id": mazzo.id, "slug": mazzo.slug}


# ---- accettazione dei vincitori -------------------------------------------------------------------


class AccettaIn(BaseModel):
    candidate_ids: List[uuid.UUID] = Field(min_length=1)


@router.post("/tornate/{round_id}/accetta")
async def accetta_vincitori(
    round_id: uuid.UUID, payload: AccettaIn, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    """Accetta uno o più candidati come vincitori: ciascuno genera un `Deck` reale (senza
    prezzo/artwork — da completare in console e con la pipeline `crea-mazzo-tarocchi`) e chiude la
    tornata. Più candidati possono essere accettati insieme (checkbox multiple in console)."""
    tornata = await session.get(VotingRound, round_id)
    if tornata is None:
        raise HTTPException(status_code=404, detail="Tornata non trovata")
    candidati_tornata = {c.id: c for c in await voting_repositories.candidati_di(session, round_id)}
    mancanti = set(payload.candidate_ids) - candidati_tornata.keys()
    if mancanti:
        raise HTTPException(status_code=400, detail=f"Candidati non in questa tornata: {sorted(str(m) for m in mancanti)}")

    creati: List[str] = []
    for candidate_id in payload.candidate_ids:
        candidato = candidati_tornata[candidate_id]
        mazzo = await _deck_per_candidato(session, candidato)
        candidato.accettato = True
        creati.append(str(mazzo.id))

    tornata.stato = "chiusa"
    tornata.chiusa_il = utcnow()
    await AuditRepository(session).record(
        action="voto.tornata.accetta", actor_id=user.id, target_type="voting_round", target_id=str(round_id),
        after={"candidati": [str(c) for c in payload.candidate_ids]}, ip=_ip(request),
    )
    await session.commit()
    return {"deck_ids": creati, "tornata_chiusa": True}


# ---- suggerimenti degli iscritti (estensione: "suggerisci tema mazzo") ------------------------------


def _suggerimento_json(s: DeckSuggestion) -> Dict[str, Any]:
    return {
        "id": str(s.id), "user_id": s.user_id, "testo": s.testo, "stato": s.stato,
        "candidate_id": str(s.candidate_id) if s.candidate_id else None,
        "creato_il": s.created_at.isoformat(),
    }


@router.get("/suggerimenti")
async def suggerimenti(session: DbSession) -> List[Dict[str, Any]]:
    """Solo quelli ancora da rivedere (`stato == 'nuovo'`): una volta trasformati o scartati escono
    dalla coda di lavoro dell'admin."""
    lista = await voting_repositories.suggerimenti_nuovi(session)
    return [_suggerimento_json(s) for s in lista]


@router.post("/suggerimenti/{suggestion_id}/trasforma", status_code=201)
async def trasforma_suggerimento(
    suggestion_id: uuid.UUID, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    """Trasforma un suggerimento in una proposta vera nella riserva (`DeckCandidate` con
    `round_id is None`): nome e descrizione partono dal testo libero, l'admin li rifinisce dopo con
    `PUT /candidati/{id}` come ogni altra proposta."""
    suggerimento = await session.get(DeckSuggestion, suggestion_id)
    if suggerimento is None:
        raise HTTPException(status_code=404, detail="Suggerimento non trovato")
    if suggerimento.stato != "nuovo":
        raise HTTPException(status_code=409, detail="Suggerimento già rivisto")

    nome = suggerimento.testo.strip()[:80]
    candidato = DeckCandidate(round_id=None, nome=nome, descrizione=suggerimento.testo.strip())
    session.add(candidato)
    await session.flush()
    suggerimento.stato = "usato"
    suggerimento.candidate_id = candidato.id
    await AuditRepository(session).record(
        action="voto.suggerimento.trasforma", actor_id=user.id, target_type="deck_suggestion", target_id=str(suggestion_id),
        after={"candidate_id": str(candidato.id)}, ip=_ip(request),
    )
    await session.commit()
    return _candidato_json(candidato, {})


@router.post("/suggerimenti/{suggestion_id}/scarta")
async def scarta_suggerimento(
    suggestion_id: uuid.UUID, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    suggerimento = await session.get(DeckSuggestion, suggestion_id)
    if suggerimento is None:
        raise HTTPException(status_code=404, detail="Suggerimento non trovato")
    if suggerimento.stato != "nuovo":
        raise HTTPException(status_code=409, detail="Suggerimento già rivisto")
    suggerimento.stato = "scartato"
    await AuditRepository(session).record(
        action="voto.suggerimento.scarta", actor_id=user.id, target_type="deck_suggestion", target_id=str(suggestion_id),
        ip=_ip(request),
    )
    await session.commit()
    return _suggerimento_json(suggerimento)
