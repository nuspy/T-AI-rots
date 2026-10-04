"""L'accesso dalle app (v9, Fase 6): il segreto di «Accedi con Apple» e i codici che spostano un'identità social.

- **`ConfigAccessoApple`** (singleton, `id = 1`): ciò che serve per firmare il `client_secret` dell'identity provider
  `apple` di Keycloak. Apple non accetta un segreto fisso: vuole un JWT ES256 firmato con la chiave «Sign in with
  Apple» (file `.p8`) dell'account sviluppatore, valido al massimo sei mesi. Qui stanno Team ID, Key ID, Services ID
  (il `client_id`, lo stesso per il sito e per le app, che passano da Keycloak nel browser di sistema) e la chiave,
  **cifrata** come le chiavi dei fornitori LLM (`llm/cifratura.py`). Il backend firma il JWT e lo scrive in Keycloak
  (Admin API); il CronJob `tarots-apple-segreto` lo rinnova prima della scadenza. Il JWT non si salva: si rifà dalla
  chiave. Si conservano solo la sua scadenza (la console la mostra) e l'esito dell'ultima scrittura.
- **`CodiceCollegamento`**: il codice monouso (8 caratteri, 10 minuti) con cui un account appena nato nell'app (per
  esempio con «Nascondi la mia email» di Apple, che impedisce la riconciliazione per email) consegna le sue identità
  social all'account che la persona aveva già sul sito (`tarot/collega_identita.py`). Del codice si salva solo
  l'impronta SHA-256: chi legge il database non può usarlo.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Integer, LargeBinary, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class ConfigAccessoApple(Base, TimestampMixin):
    __tablename__ = "config_accesso_apple"
    __table_args__ = (CheckConstraint("id = 1", name="ck_config_accesso_apple_singleton"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    #: L'identificativo del team dell'account sviluppatore (10 caratteri): l'`iss` del JWT.
    team_id: Mapped[str] = mapped_column(String(10), nullable=False, default="", server_default="")
    #: L'identificativo della chiave «Sign in with Apple» (10 caratteri): il `kid` dell'intestazione del JWT.
    key_id: Mapped[str] = mapped_column(String(10), nullable=False, default="", server_default="")
    #: Il Services ID (es. `chat.tarots.web`): il `client_id` del provider in Keycloak e il `sub` del JWT.
    services_id: Mapped[str] = mapped_column(String(150), nullable=False, default="", server_default="")
    #: La chiave privata EC P-256 (PEM PKCS#8, il file `AuthKey_<KeyID>.p8`), cifrata. Nulla: non ancora caricata.
    chiave_cifrata: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    #: Il segreto oggi in Keycloak: quando è stato firmato e quando scade (`exp` del JWT).
    segreto_generato_il: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    segreto_scade_il: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    #: L'ultima scrittura in Keycloak: `{"ok": …, "messaggio": …, "il": …}`.
    esito: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    updated_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))


class CodiceCollegamento(Base):
    __tablename__ = "codici_collegamento"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    #: L'account che consegna le sue identità social (quello nuovo, nato nell'app). Cancellato lui, sparisce il codice.
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    #: SHA-256 esadecimale del codice normalizzato (maiuscole, senza trattini).
    impronta: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    creato_il: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    scade_il: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    #: Usato (una volta sola): quando e da quale account, che ha ricevuto le identità.
    usato_il: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    usato_da: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))
