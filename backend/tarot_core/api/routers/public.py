"""Ciò che si legge senza account: stese, carte, disclaimer, letture condivise.

Le pagine pubbliche delle carte servono anche a chi cerca «significato del
Tre di Spade»: sono la porta d'ingresso organica del servizio.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from ...auth.dependencies import DbSession
from ...domain.repositories import ReadingRepository
from ...domain.share_models import ShareImage
from ...tarot.condivisione import anonimizza, simbolo_partner
from ...tarot.lingue import in_lingua
from ...tarot.testi import DISCLAIMER, QUALCUNO_DI_SPECIALE
from ..deps import get_conoscenza

router = APIRouter(tags=["pubblico"])


@router.get("/spreads")
def stese(
    categoria: Optional[str] = Query(default=None, pattern="^(standard|compatibilita|coppia)$"),
) -> List[Dict[str, Any]]:
    """Le stese. Con `?categoria=` solo quelle della lettura standard, di
    compatibilità o di coppia; senza, tutte. La home e la scelta della stesa
    standard chiedono `standard`, così le letture speciali non vi compaiono."""
    conoscenza = get_conoscenza()
    scelte = conoscenza.stese_per(categoria) if categoria else conoscenza.stese.values()
    return [conoscenza.stesa_pubblica(s) for s in scelte]


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
    return {"testo": in_lingua(DISCLAIMER, lang)}


@router.get("/shared/{token}")
async def condivisa(token: str, session: DbSession) -> Dict[str, Any]:
    """Una lettura condivisa: domanda, carte, responso. Niente intervista,
    niente nome di chi l'ha fatta.

    Nelle letture speciali (compatibilità, coppia) il nome dell'altra persona
    diventa «qualcuno di speciale» in ogni testo, e al suo posto il frontend
    disegna il simbolo del suo genere: escono `partner_simbolo` e `partner_frase`,
    mai nome, cognome, date, intervista o compatibilità zodiacale.
    """
    lettura = await ReadingRepository(session).by_share_token(token)
    if lettura is None or lettura.status != "completata":
        raise HTTPException(status_code=404, detail="Lettura non trovata")
    conoscenza = get_conoscenza()
    stesa = conoscenza.stesa(lettura.spread_id)
    categoria = conoscenza.categoria_di(stesa) if stesa else "standard"
    partner = (lettura.persone or {}).get("partner") or {}
    speciale = categoria != "standard" or lettura.persone is not None
    frase = in_lingua(QUALCUNO_DI_SPECIALE, lettura.lang)

    def anonimo(testo: Optional[str]) -> Optional[str]:
        if not speciale:
            return testo
        for nome in (partner.get("nome"), partner.get("cognome")):
            testo = anonimizza(testo, nome, frase, lang=lettura.lang)
        return testo

    return {
        "question": anonimo(lettura.question),
        "lang": lettura.lang,
        "stesa": conoscenza.stesa_pubblica(stesa) if stesa else None,
        "categoria": categoria,
        "speciale": speciale,
        "partner_simbolo": simbolo_partner(partner.get("genere")) if speciale else None,
        "partner_frase": frase if speciale else None,
        "cards": [
            {
                "posizione": c.posizione,
                "calcolata": c.calcolata,
                "rivelata": True,
                "carta": conoscenza.carta_pubblica(c.card_id),
                "rovescio": c.rovescio,
                "interpretazione": anonimo(c.interpretazione),
            }
            for c in lettura.cards
        ],
        "synthesis": anonimo(lettura.synthesis),
        "share_text": anonimo(lettura.share_text),
        "immagine": await _ha_immagine(session, lettura.id),
        "created_at": lettura.created_at.isoformat(),
        "disclaimer": in_lingua(DISCLAIMER, lettura.lang),
    }


async def _ha_immagine(session, reading_id) -> bool:
    riga = (await session.execute(
        select(ShareImage.reading_id).where(ShareImage.reading_id == reading_id)
    )).first()
    return riga is not None
