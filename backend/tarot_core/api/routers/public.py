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
from ...tarot.giorno import carta_universale, oggi_utc
from ...tarot.lingue import in_lingua
from ...tarot.testi import DISCLAIMER, QUALCUNO_DI_SPECIALE
from ..deps import get_conoscenza

router = APIRouter(tags=["pubblico"])


#: `?lang=` sceglie la lingua dei testi lunghi: `en` (la lingua delle pagine pubbliche) o `it`. Senza,
#: l'italiano di sempre: chi non lo chiede non vede cambiare niente.
Lang = Query(default=None, max_length=10, description="it o en: la lingua dei testi")


@router.get("/spreads")
def stese(
    categoria: Optional[str] = Query(default=None, pattern="^(standard|compatibilita|coppia)$"),
    lang: Optional[str] = Lang,
) -> List[Dict[str, Any]]:
    """Le stese. Con `?categoria=` solo quelle della lettura standard, di
    compatibilità o di coppia; senza, tutte. La home e la scelta della stesa
    standard chiedono `standard`, così le letture speciali non vi compaiono."""
    conoscenza = get_conoscenza()
    scelte = conoscenza.stese_per(categoria) if categoria else conoscenza.stese.values()
    return [conoscenza.stesa_pubblica(s, lang) for s in scelte]


@router.get("/spreads/{spread_id}")
def stesa(spread_id: str, lang: Optional[str] = Lang) -> Dict[str, Any]:
    """Una stesa, per la sua pagina pubblica: posizioni, significati, regole. Si trova per id
    (`croce-celtica`) o per slug (`celtic-cross`)."""
    conoscenza = get_conoscenza()
    trovata = conoscenza.stesa(conoscenza.risolvi_stesa(spread_id) or "")
    if trovata is None:
        raise HTTPException(status_code=404, detail="Stesa sconosciuta")
    return conoscenza.stesa_pubblica(trovata, lang)


@router.get("/cards")
def carte(lang: Optional[str] = Lang) -> List[Dict[str, Any]]:
    conoscenza = get_conoscenza()
    return [conoscenza.carta_pubblica(i, lang=lang) for i in conoscenza.ordine]


@router.get("/cards/{card_id}")
def carta(card_id: str, lang: Optional[str] = Lang) -> Dict[str, Any]:
    """Una carta, per id (`maj-17`) o per slug in qualunque lingua (`the-star`, `la-stella`)."""
    conoscenza = get_conoscenza()
    trovata = conoscenza.risolvi_carta(card_id)
    if trovata is None:
        raise HTTPException(status_code=404, detail="Carta sconosciuta")
    return conoscenza.carta_pubblica(trovata, completa=True, lang=lang)


@router.get("/daily-card/today")
def carta_di_oggi(lang: Optional[str] = Lang) -> Dict[str, Any]:
    """La carta del giorno per tutti, senza account: un Arcano maggiore, la stessa per chiunque per tutto il giorno
    (UTC). Non è la carta personale di `/me/daily-card`, che ha la serie dei giorni di fila."""
    conoscenza = get_conoscenza()
    giorno = oggi_utc()
    carta = conoscenza.carta_pubblica(carta_universale(conoscenza, giorno), completa=True, lang=lang)
    return {"giorno": giorno.isoformat(), "carta": carta, "testo": carta["dritto"]}


@router.get("/disclaimer")
def disclaimer(lang: str = "it") -> Dict[str, str]:
    return {"testo": in_lingua(DISCLAIMER, lang)}


@router.get("/impostazioni-pubbliche")
async def impostazioni_pubbliche(session: DbSession) -> Dict[str, int]:
    """I numeri del regalo d'iscrizione e del referral: niente di sensibile, servono alla home e al profilo per
    mostrare cifre vere invece di un testo fisso che l'amministrazione potrebbe aver cambiato."""
    from ...domain.impostazioni_repositories import correnti, pubblico

    return pubblico(await correnti(session))


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
