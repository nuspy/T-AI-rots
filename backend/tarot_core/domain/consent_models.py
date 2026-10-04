"""Consensi GDPR (v7, Fase G; granulari dalla Fase 1 del GDPR di v9).

**Stato corrente e storia, separati.** `user_consents` ha una riga per (chi consulta, tipo di consenso): un nuovo
consenso dello stesso tipo dalla stessa persona SOVRASCRIVE la riga (vincolo di unicità) — stesso principio di
`ModelAssignment` (stato corrente). La storia sta in `consensi_storico`, **append-only**: ogni scelta, con la versione
del testo mostrato, l'origine (sito, app Android, app iOS) e l'impronta dell'IP. È la prova che l'art. 7.1 chiede
(«dimostrare che l'interessato ha prestato il proprio consenso»), e un registro che si corregge non prova niente.
In più ogni scrittura lascia un evento in `audit_log`, come prima.

**Loggato o anonimo.** Chi non ha ancora un account deve poter accettare o rifiutare prima di essersi mai registrato:
`user_id` e `anon_id` sono entrambi nullable, esattamente uno dei due valorizzato — stesso schema di
`Reading.owner_id`/`Reading.anon_id` (v6, Fase F).

**L'IP non è mai in chiaro**: la rete troncata in `ip` e l'impronta HMAC in `ip_hash` (`tarot/ip_protetto.py`).
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Index, String, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin

#: I consensi che si chiedono oggi, ciascuno a sé (mai uno implicito nell'altro):
#:
#: - `statistiche`: l'identificativo casuale del browser o del dispositivo per le statistiche interne (lanterna), che
#:   riconosce i ritorni nei giorni successivi;
#: - `google_analytics`: Google Analytics 4 e i suoi cookie;
#: - `pubblicita`: gli annunci di Google AdSense negli spazi del sito, chiesto solo quando gli spazi sono accesi;
#: - `testi_statistiche`: i testi scritti dalla persona (quesiti, risposte, chat) usati **anonimi e aggregati** per
#:   statistiche e spunti per il blog (`docs/privacy/testi-statistiche.md`: per ora solo il consenso, nessuna
#:   estrazione);
#: - `dati_particolari`: le categorie particolari dell'art. 9 — la casella «persona trans» e i ricordi sulla salute;
#: - `marketing`: le promozioni via notifica (app e Web Push, Fase 5).
TIPI_CORRENTI = ("statistiche", "google_analytics", "pubblicita", "testi_statistiche", "dati_particolari", "marketing")

#: I tipi che restano ammessi nel database solo per lo storico: `cookie` (sostituito da `statistiche` +
#: `google_analytics`, convertito dalla migrazione `a1c3e5f7b9d2`) e `condivisione_dati_partner` (tolto
#: dall'interfaccia: non c'è nessuna condivisione reale con partner).
TIPI_STORICI = ("cookie", "condivisione_dati_partner")

#: Tutti i tipi ammessi in `user_consents`.
TIPI_CONSENSO = TIPI_CORRENTI + TIPI_STORICI

#: Lo storico registra anche la conferma dell'età minima (`tarot/eta_minima.py`): non è un consenso revocabile, ma la
#: sua prova vive accanto a quella dei consensi, con la stessa forma.
TIPI_STORICO = TIPI_CONSENSO + ("eta_minima",)

VALORI_CONSENSO = ("accettato", "rifiutato")
#: `confermato` solo per `eta_minima`.
VALORI_STORICO = VALORI_CONSENSO + ("confermato",)

#: Da dove arriva la scelta: il sito, le app (Fase 7–9), o il `sistema` (la conversione d'ufficio della migrazione, la
#: pulizia che segue una revoca).
ORIGINI = ("web", "android", "ios", "sistema")


def _in(valori: tuple) -> str:
    return "(" + ", ".join(f"'{v}'" for v in valori) + ")"


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
    #: La rete troncata (IPv4 /24, IPv6 /48), mai l'indirizzo intero.
    ip: Mapped[Optional[str]] = mapped_column(String(64))
    ip_hash: Mapped[Optional[str]] = mapped_column(String(64))
    origine: Mapped[str] = mapped_column(String(10), nullable=False, default="web", server_default="web")

    __table_args__ = (
        UniqueConstraint("user_id", "tipo", name="uq_user_consents_user_tipo"),
        UniqueConstraint("anon_id", "tipo", name="uq_user_consents_anon_tipo"),
        CheckConstraint("(user_id is not null) or (anon_id is not null)", name="ck_user_consents_owner"),
        CheckConstraint(f"tipo in {_in(TIPI_CONSENSO)}", name="ck_user_consents_tipo"),
        CheckConstraint("valore in ('accettato', 'rifiutato')", name="ck_user_consents_valore"),
        CheckConstraint(f"origine in {_in(ORIGINI)}", name="ck_user_consents_origine"),
    )


class ConsensoStorico(Base):
    """Una scelta, così com'è stata fatta. Append-only: l'applicazione non la modifica mai; la sola cancellazione è
    quella manuale della console «Conservazione dati», per le righe più vecchie di N anni che non sono l'ultima scelta
    di quella persona su quel tipo (`api/routers/admin_conservazione.py`)."""

    __tablename__ = "consensi_storico"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    #: `SET NULL` e non `CASCADE`: anche se una riga utente sparisse, la prova delle scelte resta. In pratica la riga
    #: utente non sparisce mai (la cancellazione dell'account la pseudonimizza, `tarot/cancellazione.py`).
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), index=True)
    anon_id: Mapped[Optional[str]] = mapped_column(String(64), index=True)
    tipo: Mapped[str] = mapped_column(String(40), nullable=False)
    valore: Mapped[str] = mapped_column(String(20), nullable=False)
    versione_informativa: Mapped[str] = mapped_column(String(20), nullable=False)
    origine: Mapped[str] = mapped_column(String(10), nullable=False)
    ip: Mapped[Optional[str]] = mapped_column(String(64))
    ip_hash: Mapped[Optional[str]] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint(f"tipo in {_in(TIPI_STORICO)}", name="ck_consensi_storico_tipo"),
        CheckConstraint(f"valore in {_in(VALORI_STORICO)}", name="ck_consensi_storico_valore"),
        CheckConstraint(f"origine in {_in(ORIGINI)}", name="ck_consensi_storico_origine"),
        Index("ix_consensi_storico_creato", "created_at"),
    )
