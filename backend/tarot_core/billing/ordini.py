"""Il carrello del negozio mazzi: sconto per-mazzo (già in `billing/mazzi.py`) più lo sconto a
scaglioni per mazzi diversi nello stesso ordine, e l'apertura/applicazione dell'ordine (v5, Fase B3).

**Ordine di applicazione degli sconti**, fissato qui e in un punto solo: prima lo sconto per-mazzo
(`OffertaMazzo`, riga per riga, sui formati che l'offerta indica: dalla v8.5 anche PDF e fisico), poi lo sconto a scaglioni
sul subtotale che ne risulta. Comprare due copie dello **stesso** mazzo non fa salire lo scaglione,
solo la quantità: conta `count(distinct deck_id)`, non il numero di righe.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import set_committed_value

from ..domain.base import utcnow
from ..domain.billing_models import PaymentEvent
from ..domain.deck_models import Deck, DeckUnlock, OffertaMazzo
from ..domain.ordini_models import IndirizzoSpedizione, Ordine, RigaOrdine
from .mazzi import listino_di, prezzo_effettivo
from .pagamenti import EventoPagamento, ProviderPagamenti, provider_pagamenti

#: Lo sconto a scaglioni: 10% dal secondo mazzo diverso in poi, fino a un tetto del 50%.
SCAGLIONE_PER_MAZZO = 10
SCAGLIONE_TETTO = 50

#: Gli eventi propri degli ordini — nello stesso `payment_events` dei piani (condiviso, indicizzato
#: per id-evento del fornitore), ma un namespace diverso da `checkout.*` per non essere ambigui nel
#: webhook, che smista sul tipo prima ancora di sapere se è un piano o un ordine.
ORDINE_PAGATO = "ordine.pagato"
ORDINE_ANNULLATO = "ordine.annullato"


class CarrelloNonValido(ValueError):
    """Una voce del carrello non è acquistabile così com'è (prodotto non offerto, mazzo non attivo…)."""


@dataclass(frozen=True)
class VoceCarrello:
    deck_id: int
    tipo: str  # 'digitale' | 'pdf' | 'fisico'
    quantita: int = 1


@dataclass(frozen=True)
class RigaCalcolata:
    voce: VoceCarrello
    prezzo_pieno_unitario: int
    prezzo_finale_unitario: int


@dataclass(frozen=True)
class RisultatoCarrello:
    righe: List[RigaCalcolata]
    subtotale: int              # dopo lo sconto per-mazzo, prima dello scaglione
    scaglione_percentuale: int
    sconto_scaglioni: int
    totale: int


def _prezzo_pieno(deck: Deck, tipo: str) -> Optional[int]:
    return listino_di(deck, tipo)


def calcola_carrello(
    voci: List[VoceCarrello], decks: Dict[int, Deck], offerte: Dict[int, OffertaMazzo],
) -> RisultatoCarrello:
    """Pura: nessun accesso al database, per essere provabile con oggetti costruiti a mano.

    Solleva `CarrelloNonValido` se una voce chiede un prodotto che il mazzo non offre (prezzo nullo)
    o un mazzo sconosciuto — chi chiama ha già caricato `decks`/`offerte` da id verificati, quindi
    l'unico modo per arrivare qui è un carrello costruito con id inventati.
    """
    if not voci:
        raise CarrelloNonValido("il carrello è vuoto")

    righe: List[RigaCalcolata] = []
    for voce in voci:
        deck = decks.get(voce.deck_id)
        if deck is None:
            raise CarrelloNonValido(f"mazzo sconosciuto: {voce.deck_id}")
        listino = _prezzo_pieno(deck, voce.tipo)
        if listino is None:
            raise CarrelloNonValido(f"«{deck.nome}» non offre il prodotto «{voce.tipo}»")
        if voce.tipo == "digitale" and listino == 0:
            raise CarrelloNonValido(f"«{deck.nome}» digitale è gratuito: non serve comprarlo")
        # `is None` e non `or`: uno sconto che porta il prezzo a zero è un prezzo, non un'assenza.
        mostrato = prezzo_effettivo(deck, offerte.get(deck.id), tipo=voce.tipo).da_mostrare
        finale = listino if mostrato is None else mostrato
        righe.append(RigaCalcolata(voce=voce, prezzo_pieno_unitario=listino, prezzo_finale_unitario=finale))

    subtotale = sum(r.prezzo_finale_unitario * r.voce.quantita for r in righe)
    n_distinti = len({r.voce.deck_id for r in righe})
    percentuale = min(SCAGLIONE_TETTO, max(0, (n_distinti - 1) * SCAGLIONE_PER_MAZZO))
    sconto = (subtotale * percentuale + 50) // 100  # mezzi centesimi per eccesso, in interi
    return RisultatoCarrello(
        righe=righe, subtotale=subtotale, scaglione_percentuale=percentuale,
        sconto_scaglioni=sconto, totale=max(subtotale - sconto, 0),
    )


class GestoreOrdini:
    """Apre il carrello e applica gli eventi, una volta sola ciascuno — sorella di `GestorePagamenti`,
    non un ramo al suo interno: un ordine non è un `PaymentCheckout`."""

    def __init__(self, session: AsyncSession, provider: Optional[ProviderPagamenti] = None) -> None:
        self._session = session
        self._provider = provider or provider_pagamenti()

    async def preventivo(self, voci: List[VoceCarrello]) -> RisultatoCarrello:
        """Quanto costa un carrello, con gli stessi controlli e lo stesso calcolo dell'apertura: il negozio lo
        mostra prima di pagare (anche a chi non ha ancora un account). Non scrive niente."""
        decks, offerte = await self._carica(voci)
        return calcola_carrello(voci, decks, offerte)

    async def _carica(self, voci: List[VoceCarrello]) -> tuple[Dict[int, Deck], Dict[int, OffertaMazzo]]:
        deck_ids = list({v.deck_id for v in voci})
        decks = {
            d.id: d for d in (await self._session.execute(select(Deck).where(Deck.id.in_(deck_ids)))).scalars()
        }
        for deck_id in deck_ids:
            if deck_id not in decks or not decks[deck_id].attivo_ora:
                raise CarrelloNonValido(f"mazzo non disponibile: {deck_id}")
        offerte_righe = (
            await self._session.execute(select(OffertaMazzo).where(OffertaMazzo.deck_id.in_(deck_ids)))
        ).scalars()
        offerte = {o.deck_id: o for o in offerte_righe}
        return decks, offerte

    async def apri(
        self, user_id: int, voci: List[VoceCarrello], *, ritorno: str,
        indirizzo: Optional[IndirizzoSpedizione] = None,
    ) -> tuple[Ordine, str]:
        richiede_indirizzo = any(v.tipo == "fisico" for v in voci)
        if richiede_indirizzo and (indirizzo is None or indirizzo.user_id != user_id):
            raise CarrelloNonValido("serve un indirizzo di spedizione per il mazzo fisico")
        if not richiede_indirizzo:
            indirizzo = None  # arrivato per errore col carrello sbagliato: non si registra su un ordine che non spedisce

        decks, offerte = await self._carica(voci)
        risultato = calcola_carrello(voci, decks, offerte)

        ordine = Ordine(
            user_id=user_id, status="aperto", provider=self._provider.name,
            importo_totale=risultato.totale, sconto_scaglioni=risultato.sconto_scaglioni,
            indirizzo_spedizione_id=indirizzo.id if indirizzo else None,
            indirizzo_spedizione=indirizzo.campi() if indirizzo else None,
        )
        self._session.add(ordine)
        await self._session.flush()
        # `ordine` è appena stato creato (solo un flush, mai un `select`): la relazione `righe` non è
        # ancora "caricata", e leggerla più tardi proverebbe un lazy-load fuori da un contesto
        # awaitable (stesso problema già risolto per `Reading.cards` in Fase C). Si segna come
        # caricata a mano, con le righe appena scritte.
        righe_scritte = []
        for riga in risultato.righe:
            nuova = RigaOrdine(
                ordine_id=ordine.id, tipo=riga.voce.tipo, deck_id=riga.voce.deck_id, quantita=riga.voce.quantita,
                prezzo_pieno_unitario=riga.prezzo_pieno_unitario, prezzo_finale_unitario=riga.prezzo_finale_unitario,
            )
            self._session.add(nuova)
            set_committed_value(nuova, "deck", decks[riga.voce.deck_id])  # già caricato: niente accesso pigro
            righe_scritte.append(nuova)
        ordine.external_id = f"{self._provider.name}_ord_{ordine.id.hex[:16]}"
        await self._session.flush()
        set_committed_value(ordine, "righe", righe_scritte)
        return ordine, self._provider.url_di_pagamento_ordine(ordine, ritorno=ritorno)

    async def applica(self, evento: EventoPagamento) -> str:
        """Stessa idempotenza di `GestorePagamenti.applica()`: la riga dell'evento si scrive nella
        stessa transazione dell'effetto, un secondo invio trova la riga già presente."""
        if await self._session.get(PaymentEvent, evento.id) is not None:
            return "già applicato"
        self._session.add(PaymentEvent(
            id=evento.id, provider=self._provider.name, tipo=evento.tipo, payload=evento.dati, received_at=utcnow(),
        ))
        try:
            await self._session.flush()
        except IntegrityError:
            await self._session.rollback()
            return "già applicato"

        if evento.tipo == ORDINE_PAGATO:
            return await self._pagato(evento)
        if evento.tipo == ORDINE_ANNULLATO:
            return await self._chiudi(evento, "annullato")
        return "ignorato"

    async def _ordine(self, evento: EventoPagamento) -> Optional[Ordine]:
        try:
            ordine_id = uuid.UUID(str(evento.dati.get("ordine_id")))
        except ValueError:
            return None
        return await self._session.get(Ordine, ordine_id)

    async def _pagato(self, evento: EventoPagamento) -> str:
        ordine = await self._ordine(evento)
        if ordine is None or ordine.status != "aperto":
            return "ordine sconosciuto o già chiuso"
        ordine.status = "pagato"
        ordine.completed_at = utcnow()
        for riga in ordine.righe:
            if riga.tipo == "digitale":
                # Idempotente da sé: un mazzo già sbloccato (un doppio invio dell'evento, già escluso
                # sopra, o un acquisto ripetuto per errore) non duplica la riga — vincolo unico.
                gia = (await self._session.execute(
                    select(DeckUnlock.id).where(DeckUnlock.user_id == ordine.user_id, DeckUnlock.deck_id == riga.deck_id),
                )).first()
                if gia is None:
                    self._session.add(DeckUnlock(
                        user_id=ordine.user_id, deck_id=riga.deck_id, acquired_at=utcnow(),
                        riga_ordine_id=riga.id,
                    ))
            elif riga.tipo == "fisico":
                # Da qui in poi il registro ordini (Fase B6) segue la spedizione; per ora c'è solo il
                # primo stato, che dice «sì, questa riga va evasa».
                riga.stato_evasione = riga.stato_evasione or "in_attesa"
        from ..analytics import eventi as analytics

        await analytics.evento(
            self._session, analytics.ACQUISTO, utente_id=ordine.user_id,
            valore_centesimi=ordine.importo_totale, valuta=ordine.valuta,
            proprieta={
                "tipo": "ordine",
                "digitali": sum(1 for r in ordine.righe if r.tipo == "digitale"),
                "fisici": sum(1 for r in ordine.righe if r.tipo == "fisico"),
            },
        )
        await self._session.flush()
        return "ordine pagato"

    async def _chiudi(self, evento: EventoPagamento, stato: str) -> str:
        ordine = await self._ordine(evento)
        if ordine is None or ordine.status != "aperto":
            return "ordine sconosciuto o già chiuso"
        ordine.status = stato
        await self._session.flush()
        return f"ordine {stato}"
