"""La chat proattiva (v6, Fase E): non lega mai un turno a una lettura specifica — a differenza di
`InterviewTurn` (FK a `readings.id`) — perché la conversazione esiste prima che l'utente scelga di
"leggere le carte per" un argomento, e continua anche quando non lo fa mai. Il proprietario è
l'unico legame: una chat per utente, non una per lettura.
"""
from __future__ import annotations

import uuid
from typing import Any, Dict, Optional

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin, owner_index

RUOLI_CHAT = ("ai", "utente")


class ChatProattivaTurno(Base, TimestampMixin):
    """Un turno della chat proattiva. `proposta` è il campo strutturato che accende il bottone
    "Leggi le carte per: …" nell'interfaccia — nullo per un turno che non ne fa una."""

    __tablename__ = "chat_proattiva_turni"
    __table_args__ = (
        CheckConstraint(f"ruolo IN {RUOLI_CHAT}", name="ck_chat_proattiva_turni_ruolo"),
        owner_index("chat_proattiva_turni", "ordine"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ordine: Mapped[int] = mapped_column(Integer, nullable=False)
    ruolo: Mapped[str] = mapped_column(String(10), nullable=False)
    testo: Mapped[str] = mapped_column(Text, nullable=False)
    #: `{"argomento": "...", "categoria": "amore|lavoro|...", "spread_suggerito": "..."}` — solo sui
    #: turni `ai` che propongono una lettura.
    proposta: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
