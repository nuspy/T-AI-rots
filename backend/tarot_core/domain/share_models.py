"""La condivisione: clic, visite, immagini e iscrizioni dal link.

Le tabelle non hanno dati personali in chiaro: gli indirizzi e gli identificativi
dei browser sono impronte con sale (`tarot/condivisione.anonimo`), buone per
confrontare due eventi, non per risalire a una persona.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, DateTime, ForeignKey, Integer, LargeBinary, String, UniqueConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ShareEvent(Base):
    """Un clic del proprietario su un pulsante di condivisione."""

    __tablename__ = "share_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    reading_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("readings.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    canale: Mapped[str] = mapped_column(String(20), nullable=False)
    #: Impronte del browser e della rete di chi ha premuto: servono a non contare
    #: come «visitatore vero» il proprietario stesso.
    visitor: Mapped[str] = mapped_column(String(64), nullable=False)
    ip: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ShareVisit(Base):
    """Un visitatore vero che ha aperto il link di una lettura condivisa."""

    __tablename__ = "share_visits"
    __table_args__ = (UniqueConstraint("reading_id", "visitor", name="uq_share_visits_reading_visitor"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    reading_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("readings.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    visitor: Mapped[str] = mapped_column(String(64), nullable=False)
    ip: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ShareImage(Base):
    """L'immagine di una lettura condivisa: una sola, WebP 400×300 molto compresso.

    La compone il browser di chi ha condiviso (l'unico che sa scrivere in tutte le
    lingue); il server la ricontrolla e la riscrive (`tarot/condivisione.prepara_immagine`).
    """

    __tablename__ = "share_images"

    reading_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("readings.id", ondelete="CASCADE"), primary_key=True,
    )
    webp: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False,
    )


class ShareSignup(Base):
    """Una persona che si è iscritta partendo dal link condiviso di un'altra."""

    __tablename__ = "share_signups"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    #: Chi ha condiviso, e a cui vanno i crediti.
    sharer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    #: Chi si è iscritto. Una volta sola: un account non può far guadagnare due volte.
    new_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True,
    )
    reading_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("readings.id", ondelete="SET NULL"),
    )
    crediti: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
