"""Vota il prossimo mazzo (v7, Fase K).

**Le carte di prova sono `MediaImage`, non `DeckArtworkUpload`.** Un candidato al voto porta poche
immagini (numero variabile, non 78+1) e devono essere visibili SUBITO sulla pagina pubblica, senza
il ciclo upload→scarica→estrai→rilascio della Fase I (pensato per l'intero mazzo finale, mai
servito pubblicamente da un blob). Si riusa perciò lo stesso schema già in produzione per le
immagini del blog (`MediaImage`, `GET /blog/media/{id}.webp` — l'endpoint non filtra per `uso`,
quindi funziona già così com'è) — `campioni` è un JSONB `[{"etichetta": ..., "media_id": ...}]`
invece di una tabella di giunzione: 2-4 immagini per candidato non giustificano una tabella a
parte.

**Un voto per utente per tornata, mai sommato.** Il vincolo di unicità su (round_id, user_id) rende
impossibile avere due righe: un nuovo voto dello stesso utente nella stessa tornata AGGIORNA quella
esistente (vedi `voting_repositories.py::vota`), implementando esplicitamente "possibilità di
rifare la votazione modificando il voto, non sommandolo" — la richiesta dell'operatore.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint, Uuid, false,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class VotingRound(Base, TimestampMixin):
    __tablename__ = "voting_rounds"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    stato: Mapped[str] = mapped_column(String(20), nullable=False, default="aperta", server_default="aperta")
    #: La scadenza dichiarata alla creazione: oltre questo istante la tornata si chiude da sola (vedi
    #: `voting_repositories.chiudi_tornate_scadute`, chiamata a ogni lettura pubblica). `NULL` per le
    #: tornate create prima di questo campo (si chiudono solo a mano, come prima).
    chiude_il: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    chiusa_il: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint("stato in ('aperta', 'chiusa')", name="ck_voting_rounds_stato"),
    )


class DeckCandidate(Base, TimestampMixin):
    __tablename__ = "deck_candidates"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    #: `NULL` finché il candidato è solo una proposta nella riserva, non ancora scelta per una
    #: tornata: la creazione della tornata seleziona fra le proposte in riserva e assegna qui il suo
    #: id (vedi il commento sul flusso in `api/routers/admin_voto.py::crea_tornata`).
    round_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("voting_rounds.id", ondelete="CASCADE"), nullable=True, index=True,
    )
    nome: Mapped[str] = mapped_column(String(80), nullable=False)
    descrizione: Mapped[Optional[str]] = mapped_column(String(2000))
    #: `[{"etichetta": "The Magus", "media_id": "<uuid>"}, ...]` — vedi il commento in cima al file.
    campioni: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list)
    #: Accettato come vincitore da un amministratore (Fase K, "accetta selezionati"). Un candidato
    #: accettato genera/collega un `Deck` vero (`deck_id`) e non è più votabile.
    accettato: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false(), nullable=False)
    deck_id: Mapped[Optional[int]] = mapped_column(ForeignKey("decks.id", ondelete="SET NULL"))


class DeckVote(Base, TimestampMixin):
    __tablename__ = "deck_votes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    round_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("voting_rounds.id", ondelete="CASCADE"), nullable=False,
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("deck_candidates.id", ondelete="CASCADE"), nullable=False,
    )
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        UniqueConstraint("round_id", "user_id", name="uq_deck_votes_round_user"),
    )


class DeckSuggestion(Base, TimestampMixin):
    """"Suggerisci tema mazzo" (estensione della Fase K): un iscritto propone liberamente un tema, in
    testo libero — non un candidato già rifinito (nome + descrizione + carte di prova) come
    `DeckCandidate`. L'admin la rivede in console e, se le piace, la trasforma in una proposta vera
    nella riserva (`DeckCandidate` con `round_id is None`) — da lì segue lo stesso percorso di ogni
    altra proposta verso una tornata."""
    __tablename__ = "deck_suggestions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    testo: Mapped[str] = mapped_column(String(1000), nullable=False)
    stato: Mapped[str] = mapped_column(String(20), nullable=False, default="nuovo", server_default="nuovo")
    #: Impostato quando l'admin la trasforma in una proposta vera (`stato` diventa `'usato'`).
    candidate_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("deck_candidates.id", ondelete="SET NULL"),
    )

    __table_args__ = (
        CheckConstraint("stato in ('nuovo', 'usato', 'scartato')", name="ck_deck_suggestions_stato"),
    )
