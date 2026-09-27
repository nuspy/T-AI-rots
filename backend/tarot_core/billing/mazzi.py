"""Il prezzo di un mazzo, con lo sconto a tempo se ce n'è uno in vigore (v5, Fase B2).

Punto unico: sia l'elenco del negozio sia il calcolo del carrello (Fase B3) chiamano
`prezzo_effettivo()`, così i due non possono mai divergere — lo stesso principio già seguito per gli
sconti sui piani (`billing/offerte.py::valuta()`).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from ..domain.base import utcnow
from ..domain.deck_models import Deck, OffertaMazzo
from ..domain.deck_repositories import mazzo_json


@dataclass(frozen=True)
class PrezzoMazzo:
    listino: Optional[int]      # None: il prodotto (digitale) non è offerto per questo mazzo
    scontato: Optional[int]
    offerta_attiva: bool

    @property
    def da_mostrare(self) -> Optional[int]:
        """Il prezzo su cui basare un acquisto adesso: lo scontato se l'offerta è in vigore, altrimenti il listino."""
        return self.scontato if self.offerta_attiva else self.listino


def _offerta_valida(offerta: Optional[OffertaMazzo], adesso: datetime) -> bool:
    if offerta is None:
        return False
    if offerta.valido_dal and adesso < offerta.valido_dal:
        return False
    if offerta.valido_fino and adesso > offerta.valido_fino:
        return False
    return True


def prezzo_effettivo(
    deck: Deck, offerta: Optional[OffertaMazzo], *, adesso: Optional[datetime] = None,
) -> PrezzoMazzo:
    """Il prezzo digitale di `deck`, con lo sconto di `offerta` se in vigore adesso.

    Non tocca il database, non verifica che `offerta.deck_id == deck.id` (è compito di chi carica
    entrambi, tipicamente con un join): qui c'è solo l'aritmetica, per essere provabile senza sessione."""
    adesso = adesso or utcnow()
    listino = deck.prezzo_digitale
    if listino is None or not _offerta_valida(offerta, adesso):
        return PrezzoMazzo(listino=listino, scontato=None, offerta_attiva=False)

    assert offerta is not None  # per il type-checker: _offerta_valida ha già escluso None
    if offerta.tipo == "percentuale":
        sconto = (listino * offerta.valore + 50) // 100  # mezzi centesimi per eccesso, in interi
    else:
        sconto = min(offerta.valore, listino)
    return PrezzoMazzo(listino=listino, scontato=max(listino - sconto, 0), offerta_attiva=True)


def mazzo_con_prezzo_json(deck: Deck, offerta: Optional[OffertaMazzo]) -> Dict[str, Any]:
    """Il JSON del mazzo (metadati, da `deck_repositories.mazzo_json`) più il prezzo effettivo: il
    negozio e la console mostrano sempre questa forma, mai i due pezzi calcolati separatamente."""
    prezzo = prezzo_effettivo(deck, offerta)
    return mazzo_json(deck) | {
        "prezzo_digitale_scontato": prezzo.scontato if prezzo.offerta_attiva else None,
        "offerta_attiva": prezzo.offerta_attiva,
        "offerta_valido_fino": offerta.valido_fino.isoformat() if offerta and offerta.valido_fino else None,
    }
