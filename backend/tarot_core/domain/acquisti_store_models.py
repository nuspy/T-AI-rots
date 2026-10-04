"""Gli acquisti fatti negli store delle app (v9, Fase 4): Google Play e App Store.

Una riga per **transazione** dello store, cioè per incasso: l'acquisto di un pacchetto di crediti, il primo periodo
di un abbonamento, ogni suo rinnovo. Lo store dà a ognuna un identificativo suo, e la coppia (piattaforma,
transazione) è unica: lo stesso acquisto confermato dall'app, poi da una notifica, poi dalla riconciliazione
notturna, è una riga sola e accredita una volta sola.

- **Google Play**: `transazione` è l'`orderId` (`GPA.1234-…`, che per un abbonamento cambia a ogni rinnovo:
  `…..0`, `…..1`); `purchase_token` è il token dell'acquisto, che per un abbonamento resta lo stesso per tutti i
  rinnovi ed è anche `transazione_originale`. Un acquisto ancora `PENDING` (pagamento in contanti in un negozio,
  per esempio) non ha sempre l'ordine: allora la transazione è il token stesso.
- **App Store**: `transazione` è il `transactionId`, `transazione_originale` l'`originalTransactionId` (lo stesso per
  tutti i rinnovi di un abbonamento: è l'id dell'abbonamento presso Apple).

`stato` dice cosa è successo a quell'incasso **da noi**: `in_attesa` (lo store non l'ha ancora incassato: niente
crediti), `accreditato`, `rimborsato` (storno dei crediti), `revocato` (lo store l'ha tolto: un abbonamento
revocato, un acquisto condiviso in famiglia ritirato), `scaduto` (un acquisto in attesa mai pagato, o il periodo di
un abbonamento finito senza rinnovo).

`ambiente` `sandbox` sono gli acquisti di prova: quelli dei tester e della App Review di Apple. In produzione si
accreditano lo stesso (chi rivede l'app deve vedere i crediti arrivare), ma restano segnati e fuori dai ricavi.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, Uuid,
    false, text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin

STATI_ACQUISTO = ("in_attesa", "accreditato", "rimborsato", "revocato", "scaduto")
AMBIENTI_ACQUISTO = ("sandbox", "production")


class AcquistoStore(Base, TimestampMixin):
    __tablename__ = "acquisti_store"
    __table_args__ = (
        UniqueConstraint("piattaforma", "transazione", name="uq_acquisti_store_transazione"),
        CheckConstraint("piattaforma in ('android', 'ios')", name="ck_acquisti_store_piattaforma"),
        CheckConstraint(
            "stato in ('in_attesa', 'accreditato', 'rimborsato', 'revocato', 'scaduto')", name="ck_acquisti_store_stato",
        ),
        CheckConstraint("ambiente in ('sandbox', 'production')", name="ck_acquisti_store_ambiente"),
        CheckConstraint("tipo in ('consumabile', 'abbonamento')", name="ck_acquisti_store_tipo"),
        Index("ix_acquisti_store_utente", "user_id", "created_at"),
        Index("ix_acquisti_store_originale", "piattaforma", "transazione_originale"),
        # La riconciliazione notturna cerca ciò che è rimasto a metà: in attesa, o non ancora confermato allo store.
        Index("ix_acquisti_store_in_attesa", "stato", postgresql_where=text("stato = 'in_attesa' or not confermato")),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    #: `SET NULL`: un account cancellato (GDPR) lascia l'acquisto, che è contabilità, senza la persona.
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))
    piattaforma: Mapped[str] = mapped_column(String(10), nullable=False)
    #: L'ID del prodotto nello store, come comprato (per Google con il base plan: `abbonamento:annuale`).
    product_id: Mapped[str] = mapped_column(String(150), nullable=False)
    tipo: Mapped[str] = mapped_column(String(12), nullable=False)
    #: Il piano accreditato (da `prodotti_store`). Un piano non si cancella mai: niente cascata.
    plan_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("plans.id"))
    transazione: Mapped[str] = mapped_column(String(200), nullable=False)
    transazione_originale: Mapped[Optional[str]] = mapped_column(String(200))
    #: L'ordine per l'assistenza: quello che l'utente vede nella ricevuta dello store (`GPA.…`, l'order ID di Apple).
    ordine: Mapped[Optional[str]] = mapped_column(String(200))
    purchase_token: Mapped[Optional[str]] = mapped_column(Text)
    stato: Mapped[str] = mapped_column(String(12), nullable=False, default="in_attesa", server_default="in_attesa")
    ambiente: Mapped[str] = mapped_column(String(10), nullable=False, default="production", server_default="production")
    #: L'acquisto è stato confermato allo store (Google: acknowledge/consume; Apple non lo chiede). Google rimborsa da
    #: sé un acquisto non confermato entro tre giorni: la riconciliazione notturna riprova quelli rimasti indietro.
    confermato: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=false())
    #: L'abbonamento locale aperto o rinnovato da questo incasso.
    subscription_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("subscriptions.id", ondelete="SET NULL"))
    #: Il prezzo pagato nello store, quando lo store lo dice (Apple sì, Google no), nella valuta dello store e in
    #: centesimi; il paese dello store (ISO alpha-2). Solo per consultazione: i ricavi del sito usano il listino.
    importo: Mapped[Optional[int]] = mapped_column(Integer)
    valuta: Mapped[Optional[str]] = mapped_column(String(3))
    paese: Mapped[Optional[str]] = mapped_column(String(2))
    #: Un periodo di prova dello store (Google offerta di prova, Apple introductory offer gratuita).
    prova: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=false())
    acquistato_il: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    #: La fine del periodo pagato, per un abbonamento.
    scade_il: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    #: Quando lo store l'ha rimborsato o revocato.
    revocato_il: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    #: Ciò che lo store ha detto, già verificato (senza firme e senza certificati): per l'assistenza.
    payload: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
