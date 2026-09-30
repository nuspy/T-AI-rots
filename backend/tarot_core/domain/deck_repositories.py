"""Letture sui mazzi: solo query, il CRUD vero e proprio sta nel router admin (stesso taglio di
`llm_repositories.py`: qui restano solo le funzioni che servono anche fuori da un endpoint di
scrittura)."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .deck_models import Deck, DeckUnlock, OffertaMazzo


async def tutti(session: AsyncSession) -> List[Deck]:
    righe = (await session.execute(select(Deck).order_by(Deck.rank, Deck.id))).scalars().all()
    return list(righe)


async def attivi_ora(session: AsyncSession) -> List[Deck]:
    """Solo quelli visibili nel negozio adesso: il filtro sulla finestra di attivazione è in Python
    (non in SQL) perché `attivo_ora` confronta anche il fuso orario di `created_at`, e sono poche
    righe — un mazzo nuovo non è un evento quotidiano."""
    return [d for d in await tutti(session) if d.attivo_ora]


def slug_immagini(deck) -> Optional[str]:
    """La cartella delle immagini di un mazzo per il frontend: `None` per il predefinito (il Thoth vive nella
    cartella piatta `/cards/`), lo slug per gli altri."""
    return deck.slug if deck is not None and not deck.predefinito else None


async def per_slug(session: AsyncSession, slug: str) -> Optional[Deck]:
    return (await session.execute(select(Deck).where(Deck.slug == slug))).scalar_one_or_none()


async def per_id(session: AsyncSession, deck_id: int) -> Optional[Deck]:
    return await session.get(Deck, deck_id)


async def predefinito(session: AsyncSession) -> Optional[Deck]:
    return (await session.execute(select(Deck).where(Deck.predefinito.is_(True)))).scalar_one_or_none()


async def offerta_per(session: AsyncSession, deck_id: int) -> Optional[OffertaMazzo]:
    return (await session.execute(select(OffertaMazzo).where(OffertaMazzo.deck_id == deck_id))).scalar_one_or_none()


async def offerte_per(session: AsyncSession, deck_ids: List[int]) -> Dict[int, OffertaMazzo]:
    if not deck_ids:
        return {}
    righe = (await session.execute(select(OffertaMazzo).where(OffertaMazzo.deck_id.in_(deck_ids)))).scalars()
    return {o.deck_id: o for o in righe}


def di_tutti(deck: Deck) -> bool:
    """Il predefinito, e un mazzo digitale gratuito (prezzo 0, v8.5): li possiede chiunque, senza ordine."""
    return deck.predefinito or deck.prezzo_digitale == 0


async def possiede(session: AsyncSession, user_id: int, deck: Deck) -> bool:
    """Il predefinito e i gratuiti sono sempre posseduti: nessuna riga in `DeckUnlock` necessaria."""
    if di_tutti(deck):
        return True
    riga = (
        await session.execute(
            select(DeckUnlock.id).where(DeckUnlock.user_id == user_id, DeckUnlock.deck_id == deck.id),
        )
    ).first()
    return riga is not None


async def posseduti_ids(session: AsyncSession, user_id: int) -> set[int]:
    """Gli id dei mazzi che `user_id` può già leggere: ogni predefinito, più ciò che risulta in
    `DeckUnlock` — usato dal negozio per non proporre un secondo acquisto di ciò che si ha già."""
    predefiniti = {d.id for d in await tutti(session) if di_tutti(d)}
    sbloccati = (
        await session.execute(select(DeckUnlock.deck_id).where(DeckUnlock.user_id == user_id))
    ).scalars()
    return predefiniti | set(sbloccati)


def mazzo_json(d: Deck) -> Dict[str, Any]:
    return {
        "id": d.id,
        "slug": d.slug,
        "nome": d.nome,
        "descrizione": d.descrizione,
        "predefinito": d.predefinito,
        "attivo": d.attivo,
        "attivo_ora": d.attivo_ora,
        "attivazione_da": d.attivazione_da.isoformat() if d.attivazione_da else None,
        "attivazione_fino": d.attivazione_fino.isoformat() if d.attivazione_fino else None,
        "prezzo_digitale": d.prezzo_digitale,
        "prezzo_stampa": d.prezzo_stampa,
        "prezzo_fisico": d.prezzo_fisico,
        "richiede_spedizione": d.richiede_spedizione,
        "valuta": d.valuta,
        "rank": d.rank,
    }
