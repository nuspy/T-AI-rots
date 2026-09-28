"""Il ranking delle memorie rilevanti per la domanda corrente: pura, come `billing/ordini.py::calcola_carrello()`.

Nessun accesso al database qui: chi chiama porta i candidati già letti (`domain/memoria_repositories.py::
candidati_per()`) insieme al loro embedding, e questa funzione decide solo l'ordine. Separarla rende il
ranking testabile senza Postgres e senza un fornitore LLM vero.

**Perché il coseno si calcola qui e non nel database.** Niente `pgvector` in produzione (vedi
`domain/memory_models.py`): la query porta *tutte* le memorie correnti dell'utente (poche centinaia al
più) già filtrate per `superseded_by IS NULL`, e il coseno si calcola in Python su quell'insieme piccolo.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Sequence
from uuid import UUID


@dataclass(frozen=True)
class CandidatoMemoria:
    """Una memoria con il proprio embedding, pronta per essere ordinata."""

    id: UUID
    contenuto: str
    tipo: str
    campo_attinenza: str
    embedding: Sequence[float]


@dataclass(frozen=True)
class MemoriaRilevante:
    """L'esito del ranking: la memoria, senza il vettore che non serve più a chi la userà nel prompt."""

    id: UUID
    contenuto: str
    tipo: str
    campo_attinenza: str
    distanza: float


def similarita_coseno(a: Sequence[float], b: Sequence[float]) -> float:
    """1 = identici, 0 = ortogonali, -1 = opposti. Zero se un vettore è nullo (evita una divisione per zero)."""
    if len(a) != len(b):
        raise ValueError(f"dimensioni diverse: {len(a)} contro {len(b)}")
    prodotto = sum(x * y for x, y in zip(a, b))
    norma_a = math.sqrt(sum(x * x for x in a))
    norma_b = math.sqrt(sum(y * y for y in b))
    if norma_a == 0.0 or norma_b == 0.0:
        return 0.0
    return prodotto / (norma_a * norma_b)


def rilevanti(
    candidati: List[CandidatoMemoria],
    query_embedding: Sequence[float],
    *,
    campo_corrente: str = "",
    top_n: int = 5,
) -> List[MemoriaRilevante]:
    """Le memorie più pertinenti, ordinate per campo di attinenza corrente prima, poi per similarità.

    Una memoria nel campo che si sta discutendo ora conta più di una fuori tema anche se
    numericamente più vicina: chi chiede di lavoro non deve vedersi ricordato un dettaglio di
    salute solo perché il testo assomiglia di più alla domanda.
    """
    if not candidati:
        return []

    valutate = [
        MemoriaRilevante(
            id=c.id, contenuto=c.contenuto, tipo=c.tipo, campo_attinenza=c.campo_attinenza,
            distanza=similarita_coseno(c.embedding, query_embedding),
        )
        for c in candidati
    ]
    valutate.sort(
        key=lambda m: (m.campo_attinenza != campo_corrente, -m.distanza),
    )
    return valutate[:top_n]
