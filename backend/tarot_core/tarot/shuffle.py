"""Il mescolamento, e la prova che è avvenuto prima della scelta.

**Le carte sono assegnate agli slot del ventaglio prima che l'utente scelga.**
È ciò che rende la scelta una scelta: se la carta fosse estratta *dopo* il
clic, il clic non conterebbe nulla. Quando il ventaglio si apre, ogni slot ha
già la sua carta e il suo orientamento.

**Il commitment.** Lo stato del mazzo si serializza in forma canonica, gli si
antepone un sale casuale, e se ne pubblica l'hash SHA-256 insieme al ventaglio.
A lettura conclusa si rivela il sale: chiunque può ricalcolare l'hash e
verificare che il mazzo non è cambiato dopo aver visto le scelte. Il sale
impedisce di indovinare lo stato provando le permutazioni possibili.

Il generatore è `secrets.SystemRandom`, cioè il CSPRNG del sistema: un
mescolamento prevedibile sarebbe una lettura truccata.
"""
from __future__ import annotations

import hashlib
import json
import secrets
from dataclasses import dataclass
from typing import Any, Dict, List

_RNG = secrets.SystemRandom()

#: La probabilità di una carta rovesciata. Metà e metà: un mazzo mescolato a
#: mano, girando i due mazzetti, dà questa proporzione.
PROBABILITA_ROVESCIO = 0.5


@dataclass(frozen=True)
class MazzoFissato:
    slot: List[Dict[str, Any]]
    sale: str
    commitment: str


def canonico(slot: List[Dict[str, Any]]) -> bytes:
    return json.dumps(slot, separators=(",", ":"), sort_keys=True).encode("utf-8")


def impegno(slot: List[Dict[str, Any]], sale: str) -> str:
    return hashlib.sha256(sale.encode("utf-8") + b"|" + canonico(slot)).hexdigest()


def taglia(slot: List[Dict[str, Any]], taglio: float) -> List[Dict[str, Any]]:
    """Taglia il mazzo: le carte dopo il punto passano davanti, come a mano.

    `taglio` è la posizione del clic, da 0 a 1 lungo il mazzo. Fuori da un
    intervallo utile (nessuna carta da spostare) il mazzo resta com'è.
    """
    n = len(slot)
    k = round(max(0.0, min(1.0, taglio)) * n)
    if k <= 0 or k >= n:
        return list(slot)
    return slot[k:] + slot[:k]


def mescola(
    carte: List[str], *, rovesci: bool = True, taglio: float | None = None,
) -> MazzoFissato:
    """Fisher–Yates sul CSPRNG, un orientamento per ogni carta, e il taglio.

    Il taglio dell'utente si applica **prima** del commitment: il mazzo che si
    impegna è già quello tagliato, e la verifica a lettura conclusa lo copre.
    """
    mazzo = list(carte)
    _RNG.shuffle(mazzo)
    slot = [
        {"card": c, "rovescio": rovesci and _RNG.random() < PROBABILITA_ROVESCIO}
        for c in mazzo
    ]
    if taglio is not None:
        slot = taglia(slot, taglio)
    sale = secrets.token_hex(16)
    return MazzoFissato(slot=slot, sale=sale, commitment=impegno(slot, sale))


def verifica(slot: List[Dict[str, Any]], sale: str, commitment: str) -> bool:
    return secrets.compare_digest(impegno(slot, sale), commitment)
