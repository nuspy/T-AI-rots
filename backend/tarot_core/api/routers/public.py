"""Ciò che si legge senza account: stese, carte, disclaimer, letture condivise.

Le pagine pubbliche delle carte servono anche a chi cerca «significato del
Tre di Spade»: sono la porta d'ingresso organica del servizio.
"""
from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from ...auth.dependencies import DbSession
from ...domain.repositories import ReadingRepository
from ...tarot.testi import DISCLAIMER, lingua
from ..deps import get_conoscenza

router = APIRouter(tags=["pubblico"])


@router.get("/spreads")
def stese() -> List[Dict[str, Any]]:
    conoscenza = get_conoscenza()
    return [conoscenza.stesa_pubblica(s) for s in conoscenza.stese.values()]


@router.get("/cards")
def carte() -> List[Dict[str, Any]]:
    conoscenza = get_conoscenza()
    return [conoscenza.carta_pubblica(i) for i in conoscenza.ordine]


@router.get("/cards/{card_id}")
def carta(card_id: str) -> Dict[str, Any]:
    conoscenza = get_conoscenza()
    if card_id not in conoscenza.carte:
        raise HTTPException(status_code=404, detail="Carta sconosciuta")
    return conoscenza.carta_pubblica(card_id, completa=True)


@router.get("/disclaimer")
def disclaimer(lang: str = "it") -> Dict[str, str]:
    return {"testo": DISCLAIMER[lingua(lang)]}


@router.get("/shared/{token}")
async def condivisa(token: str, session: DbSession) -> Dict[str, Any]:
    """Una lettura condivisa: domanda, carte, responso. Niente intervista,
    niente nome di chi l'ha fatta."""
    lettura = await ReadingRepository(session).by_share_token(token)
    if lettura is None or lettura.status != "completata":
        raise HTTPException(status_code=404, detail="Lettura non trovata")
    conoscenza = get_conoscenza()
    stesa = conoscenza.stesa(lettura.spread_id)
    return {
        "question": lettura.question,
        "stesa": conoscenza.stesa_pubblica(stesa) if stesa else None,
        "cards": [
            {
                "posizione": c.posizione,
                "calcolata": c.calcolata,
                "rivelata": True,
                "carta": conoscenza.carta_pubblica(c.card_id),
                "rovescio": c.rovescio,
                "interpretazione": c.interpretazione,
            }
            for c in lettura.cards
        ],
        "synthesis": lettura.synthesis,
        "created_at": lettura.created_at.isoformat(),
        "disclaimer": DISCLAIMER[lingua(lettura.lang)],
    }
