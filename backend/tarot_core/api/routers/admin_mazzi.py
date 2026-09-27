"""La console: i mazzi in vendita (v5, Fase B). Metadati commerciali soltanto — l'artwork è file
statici nel frontend, non passa da qui (vedi il commento in cima a `domain/deck_models.py`).

**Cosa non si cancella.** Un mazzo già posseduto da qualcuno (una riga in `deck_unlocks`) o già usato
in una lettura non si elimina: si disattiva. Lo stesso principio di piani e coupon."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from ...auth.dependencies import CurrentUser, DbSession, require_role
from ...billing import mazzi as mazzi_billing
from ...domain import deck_repositories
from ...domain.deck_models import Deck, DeckUnlock, OffertaMazzo
from ...domain.models import Reading
from ...domain.repositories import AuditRepository

router = APIRouter(prefix="/admin", tags=["mazzi"], dependencies=[Depends(require_role("admin"))])

TETTO_PREZZO = 1_000_000  # centesimi: diecimila euro, oltre è un refuso


def _ip(request: Request) -> Optional[str]:
    return request.client.host if request.client else None


class MazzoNuovo(BaseModel):
    slug: str = Field(min_length=2, max_length=40, pattern="^[a-z0-9-]+$")
    nome: str = Field(min_length=1, max_length=80)
    descrizione: Optional[str] = Field(default=None, max_length=2000)
    predefinito: bool = False
    attivo: bool = True
    attivazione_da: Optional[datetime] = None
    attivazione_fino: Optional[datetime] = None
    prezzo_digitale: Optional[int] = Field(default=None, ge=0, le=TETTO_PREZZO)
    prezzo_stampa: Optional[int] = Field(default=None, ge=0, le=TETTO_PREZZO)
    prezzo_fisico: Optional[int] = Field(default=None, ge=0, le=TETTO_PREZZO)
    richiede_spedizione: bool = False
    valuta: str = Field(default="EUR", min_length=3, max_length=3)
    rank: int = 0

    @model_validator(mode="after")
    def _finestra_sensata(self) -> "MazzoNuovo":
        if self.attivazione_da and self.attivazione_fino and self.attivazione_da >= self.attivazione_fino:
            raise ValueError("la finestra di attivazione deve avere un inizio prima della fine")
        return self


class MazzoMod(BaseModel):
    nome: Optional[str] = Field(default=None, min_length=1, max_length=80)
    descrizione: Optional[str] = Field(default=None, max_length=2000)
    attivo: Optional[bool] = None
    attivazione_da: Optional[datetime] = None
    attivazione_fino: Optional[datetime] = None
    prezzo_digitale: Optional[int] = Field(default=None, ge=0, le=TETTO_PREZZO)
    prezzo_stampa: Optional[int] = Field(default=None, ge=0, le=TETTO_PREZZO)
    prezzo_fisico: Optional[int] = Field(default=None, ge=0, le=TETTO_PREZZO)
    richiede_spedizione: Optional[bool] = None
    rank: Optional[int] = None


@router.get("/decks")
async def mazzi(session: DbSession) -> list[Dict[str, Any]]:
    tutti = await deck_repositories.tutti(session)
    offerte = await deck_repositories.offerte_per(session, [d.id for d in tutti])
    return [mazzi_billing.mazzo_con_prezzo_json(d, offerte.get(d.id)) for d in tutti]


@router.post("/decks", status_code=201)
async def crea_mazzo(payload: MazzoNuovo, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    if payload.predefinito and await deck_repositories.predefinito(session) is not None:
        raise HTTPException(status_code=409, detail="Esiste già un mazzo predefinito.")
    mazzo = Deck(
        slug=payload.slug, nome=payload.nome.strip(), descrizione=(payload.descrizione or "").strip() or None,
        predefinito=payload.predefinito, attivo=payload.attivo,
        attivazione_da=payload.attivazione_da, attivazione_fino=payload.attivazione_fino,
        prezzo_digitale=payload.prezzo_digitale, prezzo_stampa=payload.prezzo_stampa, prezzo_fisico=payload.prezzo_fisico,
        richiede_spedizione=payload.richiede_spedizione, valuta=payload.valuta.upper(), rank=payload.rank,
    )
    session.add(mazzo)
    try:
        await session.flush()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=409, detail=f"Esiste già un mazzo con lo slug «{payload.slug}».") from exc
    await AuditRepository(session).record(
        action="deck.create", actor_id=user.id, target_type="deck", target_id=mazzo.slug,
        after=deck_repositories.mazzo_json(mazzo), ip=_ip(request),
    )
    await session.commit()
    return deck_repositories.mazzo_json(mazzo)


@router.put("/decks/{slug}")
async def modifica_mazzo(slug: str, payload: MazzoMod, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    mazzo = await deck_repositories.per_slug(session, slug)
    if mazzo is None:
        raise HTTPException(status_code=404, detail="Mazzo non trovato")
    prima = deck_repositories.mazzo_json(mazzo)
    dati = payload.model_dump(exclude_unset=True)
    if "attivazione_da" in dati or "attivazione_fino" in dati:
        da_ = dati.get("attivazione_da", mazzo.attivazione_da)
        fino = dati.get("attivazione_fino", mazzo.attivazione_fino)
        if da_ and fino and da_ >= fino:
            raise HTTPException(status_code=422, detail="la finestra di attivazione deve avere un inizio prima della fine")
    for campo, valore in dati.items():
        if campo == "nome" and isinstance(valore, str):
            valore = valore.strip()
        if campo == "descrizione":
            valore = (valore or "").strip() or None
        setattr(mazzo, campo, valore)
    await session.flush()
    await AuditRepository(session).record(
        action="deck.update", actor_id=user.id, target_type="deck", target_id=mazzo.slug,
        before=prima, after=deck_repositories.mazzo_json(mazzo), ip=_ip(request),
    )
    await session.commit()
    return deck_repositories.mazzo_json(mazzo)


@router.delete("/decks/{slug}", status_code=204)
async def elimina_mazzo(slug: str, request: Request, user: CurrentUser, session: DbSession) -> Response:
    mazzo = await deck_repositories.per_slug(session, slug)
    if mazzo is None:
        raise HTTPException(status_code=404, detail="Mazzo non trovato")
    if mazzo.predefinito:
        raise HTTPException(status_code=409, detail="Il mazzo predefinito non si elimina.")
    sblocchi = await session.scalar(select(func.count()).select_from(DeckUnlock).where(DeckUnlock.deck_id == mazzo.id))
    letture = await session.scalar(select(func.count()).select_from(Reading).where(Reading.deck_id == mazzo.id))
    if sblocchi or letture:
        raise HTTPException(status_code=409, detail="Il mazzo è già posseduto o usato: disattivalo, non si elimina.")
    prima = deck_repositories.mazzo_json(mazzo)
    await session.delete(mazzo)
    await AuditRepository(session).record(
        action="deck.delete", actor_id=user.id, target_type="deck", target_id=slug, before=prima, ip=_ip(request),
    )
    await session.commit()
    return Response(status_code=204)


# ---- offerte a tempo (Fase B2) --------------------------------------------------------------------


class OffertaIn(BaseModel):
    tipo: str = Field(pattern="^(percentuale|importo)$")
    valore: int = Field(gt=0, le=TETTO_PREZZO)
    valido_dal: Optional[datetime] = None
    valido_fino: Optional[datetime] = None

    @model_validator(mode="after")
    def _sensata(self) -> "OffertaIn":
        if self.tipo == "percentuale" and self.valore > 100:
            raise ValueError("uno sconto percentuale non può superare 100")
        if self.valido_dal and self.valido_fino and self.valido_dal >= self.valido_fino:
            raise ValueError("la finestra dell'offerta deve avere un inizio prima della fine")
        return self


@router.put("/decks/{slug}/offerta")
async def imposta_offerta(slug: str, payload: OffertaIn, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    """Crea o sostituisce l'offerta del mazzo: **una sola** alla volta, non si accumulano."""
    mazzo = await deck_repositories.per_slug(session, slug)
    if mazzo is None:
        raise HTTPException(status_code=404, detail="Mazzo non trovato")
    if mazzo.prezzo_digitale is None:
        raise HTTPException(status_code=422, detail="Il mazzo non ha un prezzo digitale da scontare.")
    prima_offerta = await deck_repositories.offerta_per(session, mazzo.id)
    prima = mazzi_billing.mazzo_con_prezzo_json(mazzo, prima_offerta)
    if prima_offerta is None:
        session.add(OffertaMazzo(
            deck_id=mazzo.id, tipo=payload.tipo, valore=payload.valore,
            valido_dal=payload.valido_dal, valido_fino=payload.valido_fino,
        ))
    else:
        prima_offerta.tipo = payload.tipo
        prima_offerta.valore = payload.valore
        prima_offerta.valido_dal = payload.valido_dal
        prima_offerta.valido_fino = payload.valido_fino
    await session.flush()
    offerta = await deck_repositories.offerta_per(session, mazzo.id)
    await AuditRepository(session).record(
        action="deck.offerta.imposta", actor_id=user.id, target_type="deck", target_id=mazzo.slug,
        before=prima, after=mazzi_billing.mazzo_con_prezzo_json(mazzo, offerta), ip=_ip(request),
    )
    await session.commit()
    return mazzi_billing.mazzo_con_prezzo_json(mazzo, offerta)


@router.delete("/decks/{slug}/offerta", status_code=204)
async def rimuovi_offerta(slug: str, request: Request, user: CurrentUser, session: DbSession) -> Response:
    mazzo = await deck_repositories.per_slug(session, slug)
    if mazzo is None:
        raise HTTPException(status_code=404, detail="Mazzo non trovato")
    offerta = await deck_repositories.offerta_per(session, mazzo.id)
    if offerta is None:
        raise HTTPException(status_code=404, detail="Questo mazzo non ha un'offerta.")
    prima = mazzi_billing.mazzo_con_prezzo_json(mazzo, offerta)
    await session.delete(offerta)
    await AuditRepository(session).record(
        action="deck.offerta.rimuovi", actor_id=user.id, target_type="deck", target_id=mazzo.slug,
        before=prima, ip=_ip(request),
    )
    await session.commit()
    return Response(status_code=204)
