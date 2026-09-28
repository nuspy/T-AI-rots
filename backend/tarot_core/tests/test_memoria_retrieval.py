"""Il ranking delle memorie (v6, Fase A): pura, nessun database — sul modello di `calcola_carrello()`."""
from __future__ import annotations

import uuid

from tarot_core.tarot.memoria_retrieval import CandidatoMemoria, rilevanti, similarita_coseno


def _candidato(campo: str, embedding, contenuto: str = "x") -> CandidatoMemoria:
    return CandidatoMemoria(id=uuid.uuid4(), contenuto=contenuto, tipo="stabile", campo_attinenza=campo, embedding=embedding)


def test_lista_vuota_non_esplode():
    assert rilevanti([], [1.0, 0.0]) == []


def test_similarita_coseno_di_vettori_identici_e_uno():
    assert similarita_coseno([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]) == 1.0


def test_similarita_coseno_di_vettori_ortogonali_e_zero():
    assert similarita_coseno([1.0, 0.0], [0.0, 1.0]) == 0.0


def test_vettore_nullo_non_solleva_divisione_per_zero():
    assert similarita_coseno([0.0, 0.0], [1.0, 2.0]) == 0.0


def test_il_campo_di_attinenza_corrente_vince_su_una_similarita_piu_alta():
    # "lavoro" è testualmente/numericamente più vicino alla query, ma la domanda riguarda "amore":
    # deve comunque vincere la memoria in tema, anche se meno simile in valore assoluto.
    fuori_tema = _candidato("lavoro", [1.0, 0.0, 0.0], contenuto="fuori tema")
    in_tema = _candidato("amore", [0.9, 0.1, 0.0], contenuto="in tema")

    esito = rilevanti([fuori_tema, in_tema], [1.0, 0.0, 0.0], campo_corrente="amore")

    assert [m.contenuto for m in esito] == ["in tema", "fuori tema"]


def test_top_n_limita_il_risultato():
    candidati = [_candidato("amore", [1.0, float(i)]) for i in range(10)]
    esito = rilevanti(candidati, [1.0, 0.0], campo_corrente="amore", top_n=3)
    assert len(esito) == 3


def test_dimensioni_diverse_sollevano_value_error():
    import pytest

    with pytest.raises(ValueError):
        similarita_coseno([1.0, 2.0], [1.0])
