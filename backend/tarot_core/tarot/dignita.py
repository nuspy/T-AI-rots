"""Le dignità elementali: come Crowley leggeva le carte al posto dei rovesci.

Ogni carta è modulata dalle vicine secondo i loro elementi:

- **Fuoco e Aria** sono amici fra loro (attivi); **Acqua e Terra** pure
  (passivi);
- **Fuoco e Acqua**, **Aria e Terra** sono nemici: si indeboliscono;
- **Fuoco–Terra** e **Aria–Acqua** sono moderatamente amichevoli;
- lo stesso elemento rafforza molto;
- lo Spirito — gli Arcani planetari — è neutro.

Una carta fra due amiche è *ben dignificata*: esprime il lato luminoso. Fra
due nemiche è *mal dignificata*: esprime l'ombra. Qui il calcolo è
deterministico, così che la sintesi non debba indovinarlo e il frontend lo
possa mostrare.
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Set

ELEMENTI = ("fuoco", "acqua", "aria", "terra", "spirito")

_AMICI = {frozenset(("fuoco", "aria")), frozenset(("acqua", "terra"))}
_NEMICI = {frozenset(("fuoco", "acqua")), frozenset(("aria", "terra"))}
_MODERATI = {frozenset(("fuoco", "terra")), frozenset(("aria", "acqua"))}


def relazione(a: str, b: str) -> int:
    """+2 stesso elemento, +1 amici, 0 neutri o moderati, -1 nemici."""
    if "spirito" in (a, b):
        return 0
    if a == b:
        return 2
    coppia = frozenset((a, b))
    if coppia in _AMICI:
        return 1
    if coppia in _NEMICI:
        return -1
    return 0


def nome_relazione(a: str, b: str) -> str:
    if "spirito" in (a, b):
        return "neutra"
    if a == b:
        return "rafforzata"
    coppia = frozenset((a, b))
    if coppia in _AMICI:
        return "amica"
    if coppia in _NEMICI:
        return "ostile"
    if coppia in _MODERATI:
        return "moderata"
    return "neutra"


def vicini(linee: Iterable[List[int]]) -> Dict[int, Set[int]]:
    """Le posizioni adiacenti a ciascuna, lungo tutte le linee della stesa."""
    adiacenza: Dict[int, Set[int]] = {}
    for linea in linee:
        for i, p in enumerate(linea):
            adiacenza.setdefault(p, set())
            if i > 0 and linea[i - 1] != p:
                adiacenza[p].add(linea[i - 1])
            if i + 1 < len(linea) and linea[i + 1] != p:
                adiacenza[p].add(linea[i + 1])
    return adiacenza


def valuta(
    elementi: Dict[int, str], linee: Iterable[List[int]],
) -> Dict[int, Dict[str, object]]:
    """La dignità di ogni posizione, date le carte posate.

    Restituisce per posizione: il punteggio, il giudizio
    (`ben dignificata`, `mal dignificata`, `neutra`, `rafforzata`) e le
    relazioni con le vicine.
    """
    adiacenza = vicini(linee)
    esito: Dict[int, Dict[str, object]] = {}
    for posizione, elemento in elementi.items():
        relazioni = []
        punteggio = 0
        for altra in sorted(adiacenza.get(posizione, ())):
            if altra not in elementi:
                continue
            r = relazione(elemento, elementi[altra])
            punteggio += r
            relazioni.append({
                "posizione": altra,
                "elemento": elementi[altra],
                "relazione": nome_relazione(elemento, elementi[altra]),
            })
        esito[posizione] = {
            "elemento": elemento,
            "punteggio": punteggio,
            "giudizio": giudizio(punteggio, elemento),
            "relazioni": relazioni,
        }
    return esito


def giudizio(punteggio: int, elemento: Optional[str] = None) -> str:
    if elemento == "spirito":
        return "neutra"
    if punteggio >= 3:
        return "rafforzata"
    if punteggio >= 1:
        return "ben dignificata"
    if punteggio <= -1:
        return "mal dignificata"
    return "neutra"


def prevalenze(carte: List[Dict[str, object]]) -> Dict[str, object]:
    """Quanti maggiori, quante corti, quanti per seme ed elemento."""
    semi: Dict[str, int] = {}
    elementi: Dict[str, int] = {}
    numeri: Dict[int, int] = {}
    maggiori = corti = assi = 0
    for c in carte:
        if c.get("arcano") == "maggiore":
            maggiori += 1
        if c.get("corte"):
            corti += 1
        if c.get("rango") == "asso":
            assi += 1
        if c.get("seme"):
            semi[str(c["seme"])] = semi.get(str(c["seme"]), 0) + 1
        elementi[str(c.get("elemento"))] = elementi.get(str(c.get("elemento")), 0) + 1
        if c.get("arcano") == "minore" and isinstance(c.get("numero"), int):
            numeri[int(c["numero"])] = numeri.get(int(c["numero"]), 0) + 1
    ripetuti = {n: q for n, q in numeri.items() if q >= 2}
    return {
        "totale": len(carte),
        "maggiori": maggiori,
        "corti": corti,
        "assi": assi,
        "semi": semi,
        "elementi": elementi,
        "numeri_ripetuti": ripetuti,
    }
