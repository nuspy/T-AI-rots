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


def mescola(carte: List[str], *, rovesci: bool = True) -> MazzoFissato:
    """Fisher–Yates sul CSPRNG, e un orientamento per ogni carta."""
    mazzo = list(carte)
    _RNG.shuffle(mazzo)
    slot = [
        {"card": c, "rovescio": rovesci and _RNG.random() < PROBABILITA_ROVESCIO}
        for c in mazzo
    ]
    sale = secrets.token_hex(16)
    return MazzoFissato(slot=slot, sale=sale, commitment=impegno(slot, sale))


def verifica(slot: List[Dict[str, Any]], sale: str, commitment: str) -> bool:
    return secrets.compare_digest(impegno(slot, sale), commitment)
