"""Gli abbonamenti dalla console, la prova gratuita e le email agli utenti (v9, Fase 2b).

**Le impostazioni sono una riga sola** (`ImpostazioniAbbonamenti`, id fisso a 1), come le altre della console: gli
sconti, la durata della prova, la tolleranza sui pagamenti falliti, il promemoria, i condoni e il banner. Senza la
riga valgono i default scritti qui, che sono quelli decisi dall'operatore il 3/10.

**Una prova per persona** (`ProvaGratuita`): la riga si scrive quando la prova parte davvero (il fornitore ha
registrato il metodo di pagamento), è unica per utente e porta l'impronta della carta che Stripe dà a ogni carta
(`card.fingerprint`, uguale per la stessa carta anche su account diversi): un secondo account con la stessa carta non
riceve una seconda prova.

**Ogni email agli utenti passa da un registro** (`InvioEmail`): la chiave è unica e dice *che cosa* si è mandato e
*per cosa* (`sollecito_3:<abbonamento>:<fattura>`), così il cron che gira ogni ora, un webhook ripetuto e un secondo
giro concorrente non mandano due volte la stessa email.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin

#: I default dell'operatore (3/10): li usa anche la migrazione, e la console li mostra come punto di partenza.
SCONTO_RINNOVO = 20
SCONTO_PROVA = 50
GIORNI_PROVA = 14
GIORNI_TOLLERANZA = 7
GIORNI_PROMEMORIA_PROVA = 2
CONDONI_PER_PERIODO = 2

#: I tipi di email transazionali (`posta/modelli.py` ha i testi nelle sei lingue).
TIPI_EMAIL = (
    "rinnovo_spento",       # conferma formale della disdetta del rinnovo automatico
    "rinnovo_riacceso",     # il rinnovo automatico è di nuovo attivo
    "promemoria_prova",     # la prova finisce fra due giorni: quando e quanto si paga, come disdire
    "pagamento_fallito",    # il rinnovo non è andato: la fattura aperta e i giorni di tolleranza
    "sollecito",            # al terzo e al sesto giorno della tolleranza
    "sospensione",          # la tolleranza è finita: letture comprese sospese
    "rinnovo_avvenuto",     # il periodo si è allungato
)


class ImpostazioniAbbonamenti(Base, TimestampMixin):
    """I numeri degli abbonamenti decisi dalla console. Singleton."""

    __tablename__ = "impostazioni_abbonamenti"
    __table_args__ = (
        CheckConstraint("id = 1", name="ck_impostazioni_abbonamenti_singleton"),
        CheckConstraint("sconto_rinnovo between 0 and 90", name="ck_impostazioni_abbonamenti_sconto_rinnovo"),
        CheckConstraint("sconto_prova between 0 and 90", name="ck_impostazioni_abbonamenti_sconto_prova"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    #: Lo sconto sul prezzo quando il rinnovo automatico è attivo, in percentuale.
    sconto_rinnovo: Mapped[int] = mapped_column(Integer, nullable=False, default=SCONTO_RINNOVO)
    #: Lo sconto «per sempre» dell'annuale in cui si converte la prova, in percentuale.
    sconto_prova: Mapped[int] = mapped_column(Integer, nullable=False, default=SCONTO_PROVA)
    giorni_prova: Mapped[int] = mapped_column(Integer, nullable=False, default=GIORNI_PROVA)
    #: Quanti giorni dopo un pagamento fallito le letture comprese restano attive (`in_sospeso`).
    giorni_tolleranza: Mapped[int] = mapped_column(Integer, nullable=False, default=GIORNI_TOLLERANZA)
    #: Quanti giorni prima della fine della prova parte il promemoria.
    giorni_promemoria_prova: Mapped[int] = mapped_column(Integer, nullable=False, default=GIORNI_PROMEMORIA_PROVA)
    #: Le letture oltre un limite regalate, per ogni periodo di quel limite.
    condoni_per_periodo: Mapped[int] = mapped_column(Integer, nullable=False, default=CONDONI_PER_PERIODO)
    #: Il banner della prova su tutte le pagine del sito (e nelle app).
    banner_prova: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    updated_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))


class ProvaGratuita(Base):
    """Una prova gratuita partita: una sola per utente, e una sola per carta."""

    __tablename__ = "prove_gratuite"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    #: L'abbonamento nato dalla prova. `SET NULL`: la prova resta «usata» anche se l'abbonamento sparisce.
    subscription_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("subscriptions.id", ondelete="SET NULL"))
    #: L'impronta della carta presso il fornitore (Stripe `card.fingerprint`): non è il numero della carta, ed è
    #: uguale per la stessa carta su account diversi.
    impronta_carta: Mapped[Optional[str]] = mapped_column(String(64))
    provider: Mapped[str] = mapped_column(String(20), nullable=False, default="interno")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (Index("ix_prove_gratuite_impronta", "impronta_carta"),)


class InvioEmail(Base):
    """Un'email transazionale mandata (o tentata) a un utente. Append-only, una per chiave."""

    __tablename__ = "invii_email"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    #: `SET NULL`: chi cancella l'account non lascia il suo indirizzo qui (l'indirizzo non si salva), ma la riga dice
    #: ancora che l'invio c'è stato.
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    #: Che cosa e per cosa: un secondo invio con la stessa chiave non parte.
    chiave: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    lingua: Mapped[str] = mapped_column(String(5), nullable=False, default="en")
    #: `inviata`, `non_configurato` (SMTP assente: si registra lo stesso, l'email non partirà più), `errore`,
    #: `senza_indirizzo`.
    esito: Mapped[str] = mapped_column(String(20), nullable=False)
    dettaglio: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "esito in ('inviata', 'non_configurato', 'errore', 'senza_indirizzo')", name="ck_invii_email_esito",
        ),
        Index("ix_invii_email_utente", "user_id", "created_at"),
    )
