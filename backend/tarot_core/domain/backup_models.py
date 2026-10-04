"""Il backup del database sul NAS (v8.3): dove va, e il registro di ogni esecuzione.

La **destinazione** (host, porta, utente, cartella, quante copie tenere, l'impronta della chiave dell'host) si sceglie
dalla console e sta qui; dalla v9 (Fase 2c) anche la **credenziale** (la chiave SSH privata, o una password), ma
**cifrata** con la chiave master che sta solo sul server (`llm/cifratura.py`): un dump del database — che finisce
proprio sul NAS — porta con sé solo testo cifrato, non la chiave per entrare nel NAS. Il Secret montato
(`/etc/tarots-backup`) resta il ripiego, e al primo avvio la sua chiave si copia qui da sola.

Il **registro** tiene ogni esecuzione: il backup notturno, quello lanciato a mano, la copia di sicurezza fatta prima
di un ripristino, il ripristino stesso, le prove di connessione. Dopo un ripristino il registro torna com'era al
momento della copia ripristinata: le righe del ripristino si riscrivono subito dopo (vedi `tarot/backup.py`).
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, LargeBinary, String, Text, Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin

#: Quante copie si tengono sul NAS se la console non dice altro (richiesta dell'operatore: sette).
CONSERVA_PREDEFINITO = 7


class ImpostazioniBackup(Base, TimestampMixin):
    """Una riga sola (id = 1): la destinazione del backup."""

    __tablename__ = "impostazioni_backup"
    __table_args__ = (
        CheckConstraint("id = 1", name="ck_impostazioni_backup_singleton"),
        CheckConstraint("conserva between 1 and 60", name="ck_impostazioni_backup_conserva"),
        CheckConstraint("porta between 1 and 65535", name="ck_impostazioni_backup_porta"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    #: Spento: il CronJob gira ma non fa nulla (e lo registra).
    attivo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    host: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    porta: Mapped[int] = mapped_column(Integer, nullable=False, default=22)
    utente: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    cartella: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    conserva: Mapped[int] = mapped_column(Integer, nullable=False, default=CONSERVA_PREDEFINITO)
    #: L'impronta SHA256 della chiave dell'host, accettata dall'operatore dopo la prima prova («Fidati di questa
    #: chiave»). Senza, nessun backup parte: un NAS impersonato riceverebbe il database intero.
    impronta_host: Mapped[Optional[str]] = mapped_column(String(120))
    #: La credenziale per entrare nel NAS, dalla console (v9, Fase 2c): la chiave SSH privata (testo OpenSSH/PEM) o la
    #: password, **cifrate** con la chiave master che resta sul server. Nulle: il Secret montato, come prima.
    chiave_ssh_cifrata: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    password_cifrata: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    #: Della chiave caricata si mostrano solo tipo e impronta (`ssh-ed25519`, `SHA256:…`), mai la chiave.
    chiave_ssh_tipo: Mapped[Optional[str]] = mapped_column(String(40))
    chiave_ssh_impronta: Mapped[Optional[str]] = mapped_column(String(120))
    updated_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))


class BackupEsecuzione(Base, TimestampMixin):
    """Un'esecuzione: backup, copia di sicurezza, ripristino o prova."""

    __tablename__ = "backup_esecuzioni"
    __table_args__ = (
        CheckConstraint("tipo in ('backup', 'sicurezza', 'ripristino', 'prova')", name="ck_backup_esecuzioni_tipo"),
        CheckConstraint("esito in ('in_corso', 'ok', 'errore', 'saltato')", name="ck_backup_esecuzioni_esito"),
        Index("ix_backup_esecuzioni_created_at", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tipo: Mapped[str] = mapped_column(String(12), nullable=False)
    #: Lanciata dalla console (altrimenti dal CronJob notturno).
    manuale: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    esito: Mapped[str] = mapped_column(String(10), nullable=False, default="in_corso")
    #: Il nome del file sul NAS (creato dal backup, o scelto per il ripristino).
    file: Mapped[Optional[str]] = mapped_column(String(255))
    byte: Mapped[Optional[int]] = mapped_column(BigInteger)
    sha256: Mapped[Optional[str]] = mapped_column(String(64))
    durata_secondi: Mapped[Optional[int]] = mapped_column(Integer)
    #: Le copie vecchie cancellate dopo questo backup (solo dopo un caricamento riuscito).
    eliminati: Mapped[List[str]] = mapped_column(JSONB, nullable=False, default=list)
    dettaglio: Mapped[Optional[str]] = mapped_column(Text)
    finita_il: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    actor_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))
    #: Per il ripristino: l'id della copia di sicurezza fatta prima.
    extra: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
