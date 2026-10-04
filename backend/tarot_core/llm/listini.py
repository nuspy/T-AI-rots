"""Quanto costerebbe un consumo con un dato listino: il conto, senza database.

Il prezzo è in dollari per milione di token, come lo pubblicano i fornitori. L'ingresso si divide in tre:

- la parte **in cache**: quella che il fornitore ha detto di aver trovato in cache (`token_cache`, il dato vero) o, per
  un listino che si sta solo valutando, la quota `cache_hit` della parte **cacheabile**;
- la parte **cacheabile** è il prefisso stabile del prompt: i messaggi di sistema in testa, che in questa piattaforma
  non portano mai dati della lettura (`tarot/cag.py`). Il resto — quesito, colloquio, carte, memorie — cambia a ogni
  chiamata e non si trova mai in cache, qualunque cosa prometta il fornitore;
- il resto si paga a prezzo pieno.

L'uscita comprende il ragionamento: i fornitori lo fatturano come uscita.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class Listino:
    nome: str
    prezzo_ingresso: float
    prezzo_cache: float
    prezzo_uscita: float
    cache_hit: float = 0.0
    #: Il listino del fornitore in uso: per lui vale la cache misurata, non quella stimata.
    attuale: bool = False

    @classmethod
    def da(cls, riga: Any) -> "Listino":
        valore = (lambda k: riga[k]) if isinstance(riga, dict) else (lambda k: getattr(riga, k))
        return cls(
            nome=str(valore("nome")), prezzo_ingresso=float(valore("prezzo_ingresso") or 0),
            prezzo_cache=float(valore("prezzo_cache") or 0), prezzo_uscita=float(valore("prezzo_uscita") or 0),
            cache_hit=min(max(float(valore("cache_hit") or 0), 0.0), 1.0), attuale=bool(valore("attuale")),
        )


def in_cache(listino: Listino, *, cacheabile: float, cache_misurata: float) -> float:
    """I token d'ingresso che si pagano a prezzo di cache."""
    if listino.attuale:
        return cache_misurata
    return max(cacheabile, 0.0) * listino.cache_hit


def costo(listino: Listino, *, ingresso: float, uscita: float, cacheabile: float = 0.0,
          cache_misurata: float = 0.0) -> float:
    """Il costo in dollari."""
    cache = min(in_cache(listino, cacheabile=cacheabile, cache_misurata=cache_misurata), ingresso)
    return (
        (ingresso - cache) * listino.prezzo_ingresso
        + cache * listino.prezzo_cache
        + uscita * listino.prezzo_uscita
    ) / 1_000_000


def dettaglio(listino: Listino, **token: float) -> Dict[str, float]:
    """Il costo con le sue tre parti, per le tabelle."""
    ingresso = float(token.get("ingresso", 0))
    cache = min(in_cache(listino, cacheabile=float(token.get("cacheabile", 0)),
                         cache_misurata=float(token.get("cache_misurata", 0))), ingresso)
    uscita = float(token.get("uscita", 0))
    return {
        "ingresso": (ingresso - cache) * listino.prezzo_ingresso / 1_000_000,
        "cache": cache * listino.prezzo_cache / 1_000_000,
        "uscita": uscita * listino.prezzo_uscita / 1_000_000,
        "totale": costo(listino, ingresso=ingresso, uscita=uscita, cacheabile=float(token.get("cacheabile", 0)),
                        cache_misurata=float(token.get("cache_misurata", 0))),
    }
