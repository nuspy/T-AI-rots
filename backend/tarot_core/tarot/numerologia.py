"""Somma teosofica e carte personali.

**La sintesi di Wirth.** Nella croce semplice la quinta carta non si pesca:
si sommano i numeri dei quattro Arcani, e se il totale supera 22 si sommano
le sue cifre, finché non si scende a 22 o meno. Il 22 — e lo 0 — è il Matto.

**La carta dell'anima e dell'anno.** Dalla data di nascita si ricavano due
Arcani: la somma delle cifre della data completa, ridotta a 22 o meno, è la
carta dell'anima (la lezione di una vita); la stessa somma con l'anno in
corso al posto dell'anno di nascita è la carta dell'anno personale.
"""
from __future__ import annotations

from datetime import date
from typing import Iterable


def riduci(n: int, *, massimo: int = 22) -> int:
    """Somma le cifre finché il numero non scende a `massimo` o meno."""
    while n > massimo:
        n = sum(int(c) for c in str(n))
    return n


def arcano_da_numero(n: int) -> int:
    """Da un numero ridotto al numero dell'Arcano: 22 e 0 sono il Matto."""
    n = riduci(n)
    return 0 if n in (0, 22) else n


def sintesi_wirth(numeri: Iterable[int]) -> int:
    return arcano_da_numero(sum(numeri))


def _cifre(*valori: int) -> int:
    return sum(int(c) for v in valori for c in str(v))


def carta_dell_anima(nascita: date) -> int:
    return arcano_da_numero(_cifre(nascita.day, nascita.month, nascita.year))


def carta_dell_anno(nascita: date, anno: int) -> int:
    return arcano_da_numero(_cifre(nascita.day, nascita.month, anno))
