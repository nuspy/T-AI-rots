"""Utenti, letture, registro.

`users` e `audit_log` vengono da Personalities così come sono: l'identità vive
in Keycloak e qui se ne tiene il riflesso, il registro è append-only.

Le tabelle della lettura seguono il suo percorso:

- `readings` — la consultazione: domanda, stesa, stato, il mazzo fissato, il
  responso;
- `interview_turns` — le domande di contesto e le risposte dell'utente;
- `drawn_cards` — le carte scelte, una per posizione della stesa.

**Sulle chiavi primarie.** `readings` usa UUID perché finisce in una URL
(`/me/readings/{id}`) e non deve essere indovinabile; le righe che non
compaiono mai in un percorso usano interi.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, Date, DateTime, ForeignKey, Index,
    Integer, String, Text, UniqueConstraint, Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, OwnedMixin, TimestampMixin, owner_index

#: Gli stati di una lettura, nell'ordine in cui si attraversano.
STATI_LETTURA = (
    "intervista", "ventaglio", "scelta", "rivelazione", "sintesi",
    "completata", "annullata",
)


class User(Base, TimestampMixin):
    """Il riflesso locale di un'identità che vive in Keycloak.

    La riga non nasce da una registrazione: nasce la prima volta che un token
    valido arriva con un `sub` mai visto. Qui non si conservano credenziali —
    nemmeno un hash — perché l'unico posto dove una password può stare è il
    servizio che la verifica.

    `deleted_at` invece di una `DELETE`: il registro crediti di un utente
    disattivato serve ancora per la contabilità e per l'audit.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # L'identificativo stabile del soggetto in Keycloak. Non l'email: quella
    # l'utente può cambiarla.
    keycloak_sub: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    email: Mapped[Optional[str]] = mapped_column(String(320), index=True)
    display_name: Mapped[Optional[str]] = mapped_column(String(200))
    locale: Mapped[str] = mapped_column(String(10), default="it", nullable=False)

    #: Facoltativa: serve alla carta dell'anima e dell'anno, e se c'è entra
    #: nel contesto della lettura.
    birth_date: Mapped[Optional[date]] = mapped_column(Date)

    #: Il codice che l'utente condivide per invitare altri. Nasce con l'utente.
    referral_code: Mapped[Optional[str]] = mapped_column(String(16), unique=True)
    #: Chi l'ha invitato. Scritto una volta sola, al primo riscatto.
    referred_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
    )

    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    #: Vero solo sull'istanza che ha appena creato la riga. Non è una colonna:
    #: serve a chi deve fare qualcosa una volta sola alla nascita
    #: dell'account — aprire il piano gratuito.
    appena_creato: bool = False

    readings: Mapped[List["Reading"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan",
        foreign_keys="Reading.owner_id",
    )

    @property
    def is_active(self) -> bool:
        return self.deleted_at is None

    def __repr__(self) -> str:  # pragma: no cover - diagnostica
        return f"<User id={self.id} sub={self.keycloak_sub[:8]}>"


class Reading(Base, TimestampMixin, OwnedMixin):
    """Una consultazione.

    **Il mazzo è fissato prima della scelta.** Quando l'utente apre il
    ventaglio, `deck_state` contiene già carta e orientamento di ogni slot; il
    frontend riceve solo gli indici. `commitment` è l'hash SHA-256 di quello
    stato con un sale: pubblicato insieme alla lettura, dimostra che le carte
    non sono state scelte dopo aver visto cosa l'utente preferiva.

    La cancellazione è vera (`DELETE` in cascata): una lettura è un dato
    intimo, e l'utente che la cancella deve poter contare che non resti.
    """

    __tablename__ = "readings"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    spread_id: Mapped[str] = mapped_column(String(40), nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="intervista", nullable=False)
    lang: Mapped[str] = mapped_column(String(5), default="it", nullable=False)

    #: Da dove è stata pagata: `credito` (un credito del registro) o `quota`
    #: (una delle letture giornaliere dell'abbonamento), oppure `omaggio`
    #: dove l'installazione non fa pagare.
    consumo: Mapped[str] = mapped_column(String(10), nullable=False)

    #: Il quadro emerso dall'intervista, riassunto dal modello.
    context_summary: Mapped[Optional[str]] = mapped_column(Text)

    #: `[{"card": "maj-00", "rovescio": false}, ...]`, uno per slot del
    #: ventaglio. Mai inviato al client prima della rivelazione.
    deck_state: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB)
    deck_salt: Mapped[Optional[str]] = mapped_column(String(64))
    commitment: Mapped[Optional[str]] = mapped_column(String(64))

    synthesis: Mapped[Optional[str]] = mapped_column(Text)
    #: L'esito del guardrail sul responso: `ok`, `riscritto`, `bloccato`.
    guard_outcome: Mapped[Optional[str]] = mapped_column(String(20))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    #: La condivisione pubblica, per scelta esplicita dell'utente.
    share_token: Mapped[Optional[str]] = mapped_column(String(32), unique=True)

    #: Il diario: «si è avverato?». `si`, `in_parte`, `no`.
    feedback: Mapped[Optional[str]] = mapped_column(String(10))
    feedback_note: Mapped[Optional[str]] = mapped_column(Text)
    feedback_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    owner: Mapped[Optional[User]] = relationship(
        back_populates="readings", foreign_keys="Reading.owner_id",
    )
    turns: Mapped[List["InterviewTurn"]] = relationship(
        back_populates="reading", cascade="all, delete-orphan",
        order_by="InterviewTurn.ordine", lazy="selectin",
    )
    cards: Mapped[List["DrawnCard"]] = relationship(
        back_populates="reading", cascade="all, delete-orphan",
        order_by="DrawnCard.posizione", lazy="selectin",
    )

    __table_args__ = (
        CheckConstraint(
            "status in ('intervista', 'ventaglio', 'scelta', 'rivelazione', "
            "'sintesi', 'completata', 'annullata')",
            name="ck_readings_status",
        ),
        CheckConstraint(
            "consumo in ('credito', 'quota', 'omaggio')", name="ck_readings_consumo",
        ),
        CheckConstraint(
            "feedback is null or feedback in ('si', 'in_parte', 'no')",
            name="ck_readings_feedback",
        ),
        owner_index("readings", "created_at"),
    )


class InterviewTurn(Base):
    """Un turno dell'intervista. Immutabile: non si corregge, si aggiunge."""

    __tablename__ = "interview_turns"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    reading_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("readings.id", ondelete="CASCADE"), nullable=False,
    )
    ordine: Mapped[int] = mapped_column(Integer, nullable=False)
    #: `oracolo` per le domande dell'AI, `utente` per le risposte.
    ruolo: Mapped[str] = mapped_column(String(10), nullable=False)
    testo: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    reading: Mapped[Reading] = relationship(back_populates="turns")

    __table_args__ = (
        CheckConstraint("ruolo in ('oracolo', 'utente')", name="ck_interview_ruolo"),
        UniqueConstraint("reading_id", "ordine", name="uq_interview_ordine"),
    )


class DrawnCard(Base):
    """Una carta posata su una posizione della stesa.

    `calcolata` vale per la quinta carta della croce semplice, che non si
    sceglie: è la somma teosofica delle altre quattro.
    """

    __tablename__ = "drawn_cards"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    reading_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("readings.id", ondelete="CASCADE"), nullable=False,
    )
    posizione: Mapped[int] = mapped_column(Integer, nullable=False)
    #: Lo slot del ventaglio da cui è stata scelta. Nullo per le calcolate.
    slot: Mapped[Optional[int]] = mapped_column(Integer)
    card_id: Mapped[str] = mapped_column(String(40), nullable=False)
    rovescio: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    calcolata: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    rivelata: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    interpretazione: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    reading: Mapped[Reading] = relationship(back_populates="cards")

    __table_args__ = (
        UniqueConstraint("reading_id", "posizione", name="uq_drawn_posizione"),
        UniqueConstraint("reading_id", "slot", name="uq_drawn_slot"),
        Index("ix_drawn_cards_card", "card_id"),
    )


class DailyCard(Base):
    """La carta del giorno: gratuita, una per utente al giorno.

    Una riga per giorno e non un calcolo: chi la riapre la sera deve ritrovare
    la stessa carta del mattino.
    """

    __tablename__ = "daily_cards"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
    )
    giorno: Mapped[date] = mapped_column(Date, nullable=False)
    card_id: Mapped[str] = mapped_column(String(40), nullable=False)
    rovescio: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    testo: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "giorno", name="uq_daily_card_giorno"),
    )


class AuditLog(Base):
    """Chi ha fatto cosa, a cosa, e com'era prima.

    Append-only per disciplina: l'applicazione non espone aggiornamenti né
    cancellazioni su questa tabella. Un registro che si può correggere non è un
    registro.
    """

    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Nullo per le azioni di sistema: «non è stato nessuno» è
    # un'informazione, e va distinta da un utente ignoto.
    actor_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True,
    )

    action: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    target_type: Mapped[Optional[str]] = mapped_column(String(50))
    target_id: Mapped[Optional[str]] = mapped_column(String(64))

    before: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    after: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)

    ip: Mapped[Optional[str]] = mapped_column(String(45))  # anche IPv6
    correlation_id: Mapped[Optional[str]] = mapped_column(String(64), index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True,
    )

    __table_args__ = (
        Index("ix_audit_log_target", "target_type", "target_id"),
    )
