"""Il carrello, una volta pagato: ordini e righe (v5, Fase B3).

**Parallelo a `PaymentCheckout`, non innestato**: un checkout di piano è un solo `Plan`; un carrello è
una lista eterogenea (sblocco digitale × N mazzi, PDF × N, fisico × N con quantità) — forzarlo dentro
`PaymentCheckout` (pensato per un `plan_id` solo) avrebbe significato riscriverlo. `payment_events`
resta condiviso fra i due flussi (è già indicizzato per id-evento del fornitore, non per ciò che
paga): l'idempotenza dell'uno non tocca l'altro.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import BigInteger, Boolean, CheckConstraint, DateTime, ForeignKey, Integer, JSON, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class Ordine(Base, TimestampMixin):
    """Un acquisto di uno o più mazzi (o PDF), dal carrello al pagamento."""

    __tablename__ = "ordini"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(12), default="aperto", nullable=False)
    provider: Mapped[str] = mapped_column(String(20), nullable=False)
    external_id: Mapped[Optional[str]] = mapped_column(String(80), unique=True)
    #: Dopo lo sconto per-mazzo (già nelle righe) e lo sconto a scaglioni: è ciò che si è davvero pagato.
    importo_totale: Mapped[int] = mapped_column(Integer, nullable=False)
    #: Solo la parte dello sconto a scaglioni, in centesimi — per il registro (Fase B6): quanto viene
    #: dallo sconto per-mazzo è già visibile confrontando `prezzo_pieno_unitario` e
    #: `prezzo_finale_unitario` di ogni riga, non serve ripeterlo qui.
    sconto_scaglioni: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    valuta: Mapped[str] = mapped_column(String(3), default="EUR", nullable=False)
    #: L'indirizzo scelto al checkout, se il carrello ha una riga fisica (Fase B5). Il riferimento
    #: (senza FK: una riga di `indirizzi_spedizione` cancellata non deve invalidare un ordine passato)
    #: serve solo per un eventuale «modifica il tuo indirizzo salvato partendo da questo»; la verità
    #: storica è `indirizzo_spedizione`, una copia dei campi presa al momento dell'ordine — un
    #: indirizzo poi corretto o cancellato non deve riscrivere silenziosamente la storia dell'ordine.
    indirizzo_spedizione_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    indirizzo_spedizione: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    righe: Mapped[list["RigaOrdine"]] = relationship(
        back_populates="ordine", cascade="all, delete-orphan", order_by="RigaOrdine.id", lazy="selectin",
    )

    __table_args__ = (
        CheckConstraint("status in ('aperto', 'pagato', 'annullato', 'scaduto')", name="ck_ordini_status"),
    )


#: `digitale`: sblocco per le letture in app. `pdf`: il file da stampare in proprio. `fisico`: il mazzo
#: vero, stampato professionalmente e spedito (Fase B5).
TIPI_RIGA_ORDINE = ("digitale", "pdf", "fisico")


class RigaOrdine(Base):
    """Una voce del carrello, con il prezzo pieno e quello davvero pagato (dopo lo sconto per-mazzo:
    lo sconto a scaglioni, che riguarda l'ordine intero, sta solo su `Ordine.sconto_scaglioni`)."""

    __tablename__ = "righe_ordine"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    ordine_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ordini.id", ondelete="CASCADE"), nullable=False, index=True)
    tipo: Mapped[str] = mapped_column(String(10), nullable=False)
    deck_id: Mapped[int] = mapped_column(ForeignKey("decks.id", ondelete="RESTRICT"), nullable=False)
    quantita: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    prezzo_pieno_unitario: Mapped[int] = mapped_column(Integer, nullable=False)
    prezzo_finale_unitario: Mapped[int] = mapped_column(Integer, nullable=False)
    #: Solo per `fisico`: null finché non esiste una spedizione da seguire (Fase B5/B6).
    stato_evasione: Mapped[Optional[str]] = mapped_column(String(12))

    ordine: Mapped[Ordine] = relationship(back_populates="righe")
    deck: Mapped["Deck"] = relationship()  # noqa: F821 — solo per l'annotazione, risolto da SQLAlchemy per nome

    __table_args__ = (
        CheckConstraint("tipo in ('digitale', 'pdf', 'fisico')", name="ck_righe_ordine_tipo"),
        CheckConstraint("quantita > 0", name="ck_righe_ordine_quantita"),
        CheckConstraint(
            "stato_evasione is null or stato_evasione in ('in_attesa', 'spedito', 'consegnato')",
            name="ck_righe_ordine_stato_evasione",
        ),
    )


class IndirizzoSpedizione(Base, TimestampMixin):
    """Un indirizzo salvato nel profilo (Fase B5): il checkout ne sceglie uno quando il carrello
    contiene una riga fisica, e ne copia i campi nell'ordine (`Ordine.indirizzo_spedizione`) — questa
    riga può cambiare dopo, quella copia no."""

    __tablename__ = "indirizzi_spedizione"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    via: Mapped[str] = mapped_column(String(200), nullable=False)
    citta: Mapped[str] = mapped_column(String(120), nullable=False)
    cap: Mapped[str] = mapped_column(String(20), nullable=False)
    provincia: Mapped[Optional[str]] = mapped_column(String(80))
    #: Codice ISO a due lettere ("IT", "HU", …): basta per instradare una spedizione fisica reale.
    paese: Mapped[str] = mapped_column(String(2), nullable=False)
    telefono: Mapped[Optional[str]] = mapped_column(String(30))
    predefinito: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    def campi(self) -> Dict[str, Any]:
        """La fotografia da copiare in un ordine: solo i campi dell'indirizzo, mai l'id o l'utente —
        chi legge lo storico di un ordine non deve poter risalire a una riga viva del profilo."""
        return {
            "nome": self.nome, "via": self.via, "citta": self.citta, "cap": self.cap,
            "provincia": self.provincia, "paese": self.paese, "telefono": self.telefono,
        }
