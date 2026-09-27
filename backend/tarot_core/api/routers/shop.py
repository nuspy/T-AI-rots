"""Il negozio mazzi: il carrello, l'apertura dell'ordine, lo storico (v5, Fase B3).

L'ordine non nasce pagato: nasce quando il fornitore conferma il pagamento (stesso principio di
`POST /me/checkout` per i piani) — chi apre la pagina e la chiude non ha comprato niente.
"""
from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response
from pydantic import BaseModel, Field

from ...auth.dependencies import CurrentUser, DbSession
from ...billing.ordini import CarrelloNonValido, GestoreOrdini, VoceCarrello
from ...billing.pagamenti import PagamentiNonDisponibili
from ...domain import deck_repositories, indirizzi_repositories
from ...domain.ordini_models import Ordine
from ...settings import get_settings
from ...tarot.stampa_mazzo import pdf_per_mazzo
from ..deps import get_conoscenza

router = APIRouter(tags=["negozio"])


class VoceIn(BaseModel):
    deck_id: int = Field(gt=0)
    tipo: str = Field(pattern="^(digitale|pdf|fisico)$")
    quantita: int = Field(default=1, ge=1, le=20)


class CarrelloIn(BaseModel):
    voci: List[VoceIn] = Field(min_length=1, max_length=20)
    ritorno: str = ""
    #: Obbligatorio solo se il carrello contiene una riga «fisico»: `GestoreOrdini.apri()` lo verifica.
    indirizzo_id: Optional[uuid.UUID] = None


def _riga_json(r: Any) -> Dict[str, Any]:
    return {
        "tipo": r.tipo, "deck_id": r.deck_id, "quantita": r.quantita,
        "prezzo_pieno_unitario": r.prezzo_pieno_unitario, "prezzo_finale_unitario": r.prezzo_finale_unitario,
        "stato_evasione": r.stato_evasione,
    }


def _ordine_json(o: Ordine) -> Dict[str, Any]:
    return {
        "id": str(o.id), "status": o.status, "importo_totale": o.importo_totale,
        "sconto_scaglioni": o.sconto_scaglioni, "valuta": o.valuta,
        "righe": [_riga_json(r) for r in o.righe],
        "indirizzo_spedizione": o.indirizzo_spedizione,
        "creato": o.created_at.isoformat() if o.created_at else None,
        "completato": o.completed_at.isoformat() if o.completed_at else None,
    }


@router.get("/me/decks")
async def i_miei_mazzi(user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    """Quali mazzi `user` può già leggere — il negozio lo usa per proporre «Aggiungi al carrello»
    solo per ciò che non si possiede ancora."""
    return {"deck_ids": sorted(await deck_repositories.posseduti_ids(session, user.id))}


@router.post("/orders", status_code=status.HTTP_201_CREATED)
async def apri_ordine(payload: CarrelloIn, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    base = get_settings().web_public_url.rstrip("/")
    ritorno = f"{base}/mazzo"
    if payload.ritorno:
        if not payload.ritorno.startswith("/") or payload.ritorno.startswith("//"):
            raise HTTPException(status_code=400, detail="Ritorno non valido")
        ritorno = f"{base}{payload.ritorno}"

    indirizzo = None
    if payload.indirizzo_id is not None:
        indirizzo = await indirizzi_repositories.per_id(session, user.id, payload.indirizzo_id)
        if indirizzo is None:
            raise HTTPException(status_code=404, detail="Indirizzo non trovato")

    voci = [VoceCarrello(deck_id=v.deck_id, tipo=v.tipo, quantita=v.quantita) for v in payload.voci]
    try:
        async with session.begin_nested():
            ordine, url = await GestoreOrdini(session).apri(user.id, voci, ritorno=ritorno, indirizzo=indirizzo)
    except CarrelloNonValido as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except PagamentiNonDisponibili as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    await session.commit()
    return {"url": url, **_ordine_json(ordine)}


@router.get("/me/orders")
async def i_miei_ordini(user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    from sqlalchemy import select

    righe = (
        await session.execute(
            select(Ordine).where(Ordine.user_id == user.id).order_by(Ordine.created_at.desc()),
        )
    ).scalars()
    return {"ordini": [_ordine_json(o) for o in righe]}


@router.get("/me/orders/{ordine_id}")
async def un_mio_ordine(ordine_id: uuid.UUID, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    ordine = await session.get(Ordine, ordine_id)
    if ordine is None or ordine.user_id != user.id:
        raise HTTPException(status_code=404, detail="Ordine non trovato")
    return _ordine_json(ordine)


@router.get("/me/orders/{ordine_id}/pdf/{deck_id}")
async def pdf_ordine(ordine_id: uuid.UUID, deck_id: int, user: CurrentUser, session: DbSession) -> Response:
    """Il PDF di un mazzo comprato (Fase B4): serve un ordine pagato, proprio, con una riga «pdf» per
    questo mazzo — nessuno sblocco persistente, il download riparte da qui ogni volta che serve."""
    ordine = await session.get(Ordine, ordine_id)
    if ordine is None or ordine.user_id != user.id:
        raise HTTPException(status_code=404, detail="Ordine non trovato")
    if ordine.status != "pagato":
        raise HTTPException(status_code=403, detail="L'ordine non risulta pagato")
    if not any(r.tipo == "pdf" and r.deck_id == deck_id for r in ordine.righe):
        raise HTTPException(status_code=404, detail="Questo ordine non contiene il PDF di questo mazzo")

    mazzo = await deck_repositories.per_id(session, deck_id)
    if mazzo is None:
        raise HTTPException(status_code=404, detail="Mazzo non trovato")

    conoscenza = get_conoscenza()
    corpo = await pdf_per_mazzo(
        mazzo.slug, list(conoscenza.ordine), gratuito=False, web_public_url=get_settings().web_public_url,
    )
    return Response(
        content=corpo, media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{mazzo.slug}-tarots-chat.pdf"'},
    )
