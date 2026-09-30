"""Consensi GDPR (v7, Fase G): cookie e condivisione dati con i partner.

**Stato corrente, non storia.** Una riga per (chi consulta, tipo di consenso): un nuovo consenso
dello stesso tipo dalla stessa persona SOVRASCRIVE la riga (vincolo di unicità), non se ne
aggiunge un'altra — stesso principio di `ModelAssignment` (stato corrente) accanto ad `AuditLog`
(storia). Ogni scrittura registra ANCHE un evento in `AuditRepository`
(`domain/repositories.py::AuditRepository.record`, già pronto con `ip`/`actor_id`/`created_at`)
per la provenienza completa richiesta esplicitamente dall'operatore: data, IP, ora.

**Loggato o anonimo.** Chi non ha ancora un account deve poter accettare/rifiutare i cookie prima
di essersi mai registrato: `user_id` e `anon_id` sono entrambi nullable, esattamente uno dei due
valorizzato — stesso schema di `Reading.owner_id`/`Reading.anon_id` (v6, Fase F).
"""
from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin

#: I due consensi distinti che l'operatore ha chiesto di tracciare. Il cookie è per forza
#: "prima di tutto" (banner globale); la condivisione dati con i partner è un consenso separato,
#: mai implicito nell'aver accettato i cookie.
TIPI_CONSENSO = ("cookie", "condivisione_dati_partner")
VALORI_CONSENSO = ("accettato", "rifiutato")


class UserConsent(Base, TimestampMixin):
    __tablename__ = "user_consents"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"),
    )
    #: Lo stesso `tarots_anon` delle letture anonime (v6, Fase F): un cookie, un'identità.
    anon_id: Mapped[Optional[str]] = mapped_column(String(64), index=True)
    tipo: Mapped[str] = mapped_column(String(40), nullable=False)
    valore: Mapped[str] = mapped_column(String(20), nullable=False)
    #: La versione del testo informativo mostrato al momento della scelta: cambiare l'informativa
    #: non invalida retroattivamente un consenso già dato, ma la versione resta in chiaro per
    #: sapere COSA esattamente la persona ha accettato o rifiutato.
    versione_informativa: Mapped[str] = mapped_column(String(20), nullable=False)
    ip: Mapped[Optional[str]] = mapped_column(String(64))

    __table_args__ = (
        UniqueConstraint("user_id", "tipo", name="uq_user_consents_user_tipo"),
        UniqueConstraint("anon_id", "tipo", name="uq_user_consents_anon_tipo"),
        CheckConstraint("(user_id is not null) or (anon_id is not null)", name="ck_user_consents_owner"),
        CheckConstraint(
            "tipo in ('cookie', 'condivisione_dati_partner')", name="ck_user_consents_tipo",
        ),
        CheckConstraint("valore in ('accettato', 'rifiutato')", name="ck_user_consents_valore"),
    )
