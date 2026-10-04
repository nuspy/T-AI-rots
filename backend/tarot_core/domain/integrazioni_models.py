"""Le integrazioni con servizi esterni configurate dalla console (v8.6): Google e Reddit.

**Google** (`ConfigGoogle`): il service account che legge Search Console e GA4, l'ID della proprietà GA4 per le
statistiche e l'ID di misurazione (`G-…`) del contatore che il sito carica col consenso. Il JSON del service account
si salva **cifrato** come le chiavi dei fornitori LLM (`llm/cifratura.py`): la console vede solo l'email del service
account e se la chiave c'è, mai la chiave. Il file montato (`TAROT_SEARCH_CONSOLE_CREDENZIALI`) resta il ripiego.

**Reddit** (`ConfigReddit`, `PostReddit`): l'account (app di tipo «script») con cui ogni articolo pubblicato diventa
un post su Reddit, e il registro dei post — uno per articolo, mai due (`uq_post_reddit_articolo`): è il registro, non
la buona volontà del codice, che rende la pubblicazione idempotente anche con più processi o un CronJob in ritardo.

Le due configurazioni sono singleton (`id = 1`), come `ImpostazioniCrediti`.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, LargeBinary, String, UniqueConstraint,
    Uuid, text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin

STATI_POST_REDDIT = ("in_coda", "in_corso", "pubblicato", "errore", "saltato")


class ConfigGoogle(Base, TimestampMixin):
    __tablename__ = "config_google"
    __table_args__ = (CheckConstraint("id = 1", name="ck_config_google_singleton"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    #: Il JSON intero del service account, cifrato (Fernet). Nullo: si usa il file montato, se c'è.
    service_account_cifrato: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    #: In chiaro perché non sono segreti e la console deve mostrarli: l'email da aggiungere come utente in Search
    #: Console e in GA4, il progetto Google Cloud (per i collegamenti «abilita l'API»), l'id della chiave.
    client_email: Mapped[Optional[str]] = mapped_column(String(320))
    project_id: Mapped[Optional[str]] = mapped_column(String(120))
    private_key_id: Mapped[Optional[str]] = mapped_column(String(80))
    #: La proprietà Search Console (`sc-domain:tarots.chat` o `https://tarots.chat/`). Vuota: quella dell'ambiente.
    sc_proprieta: Mapped[Optional[str]] = mapped_column(String(300))
    #: L'ID numerico della proprietà GA4 (Amministrazione → Dettagli proprietà), per la Data API.
    ga4_proprieta_id: Mapped[Optional[str]] = mapped_column(String(20))
    #: L'ID di misurazione del flusso web (`G-XXXXXXX`): pubblico, il sito lo carica solo col consenso ai cookie.
    ga4_misurazione_id: Mapped[Optional[str]] = mapped_column(String(20))
    #: L'ultima «Verifica»: quando e l'esito di ogni passo (`{"search_console": {"ok": …, "messaggio": …}, …}`).
    verificato_il: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    esito_verifica: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    updated_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))


class ConfigReddit(Base, TimestampMixin):
    __tablename__ = "config_reddit"
    __table_args__ = (
        CheckConstraint("id = 1", name="ck_config_reddit_singleton"),
        CheckConstraint("intervallo_minuti >= 0", name="ck_config_reddit_intervallo"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    #: L'app di Reddit di tipo «script» (https://www.reddit.com/prefs/apps): id in chiaro, segreto cifrato.
    client_id: Mapped[Optional[str]] = mapped_column(String(100))
    client_secret_cifrato: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    #: L'account che pubblica (lo stesso che ha creato l'app) e la sua password, cifrata.
    utente: Mapped[Optional[str]] = mapped_column(String(40))
    password_cifrata: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    #: Dove pubblicare, senza `r/`: un subreddit (`tarotschat`) o il proprio profilo (`u_<utente>`).
    subreddit: Mapped[Optional[str]] = mapped_column(String(60))
    #: Il flair obbligatorio in certi subreddit (l'id del modello di flair). Facoltativo.
    flair_id: Mapped[Optional[str]] = mapped_column(String(64))
    attivo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text("false"))
    #: Da quando è acceso: si pubblicano solo gli articoli usciti da quel momento, mai l'archivio intero.
    attivo_dal: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    #: Le lingue degli articoli da portare su Reddit (le traduzioni dello stesso articolo sarebbero doppioni).
    lingue: Mapped[List[str]] = mapped_column(JSONB, nullable=False, default=lambda: ["en"], server_default=text("'[\"en\"]'::jsonb"))
    #: Minuti minimi fra un post e il successivo: venti articoli pubblicati insieme non diventano venti post insieme.
    intervallo_minuti: Mapped[int] = mapped_column(Integer, nullable=False, default=60, server_default="60")
    #: L'esito dell'ultima «Prova» (token e subreddit), per la console.
    ultima_prova_il: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    esito_prova: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    updated_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))


class PostReddit(Base, TimestampMixin):
    """Un articolo portato (o da portare) su Reddit. Una riga per articolo, per sempre: anche un errore resta qui
    finché qualcuno non preme «Riprova», e un articolo già pubblicato non riparte nemmeno se lo si ripubblica."""

    __tablename__ = "post_reddit"
    __table_args__ = (
        UniqueConstraint("articolo_id", name="uq_post_reddit_articolo"),
        CheckConstraint(
            "stato in ('in_coda', 'in_corso', 'pubblicato', 'errore', 'saltato')", name="ck_post_reddit_stato",
        ),
        Index("ix_post_reddit_stato_creato", "stato", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    articolo_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("blog_posts.id", ondelete="CASCADE"), nullable=False)
    stato: Mapped[str] = mapped_column(String(12), nullable=False, default="in_coda", server_default="in_coda")
    #: `galleria` (copertina e immagini del testo) o `link` (il ripiego: l'articolo come collegamento).
    tipo: Mapped[Optional[str]] = mapped_column(String(10))
    subreddit: Mapped[Optional[str]] = mapped_column(String(60))
    #: Il nome completo del post su Reddit (`t3_abc123`) e il suo indirizzo.
    reddit_id: Mapped[Optional[str]] = mapped_column(String(20))
    url: Mapped[Optional[str]] = mapped_column(String(500))
    errore: Mapped[Optional[str]] = mapped_column(String(1000))
    tentativi: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    #: Reddit ha chiesto di aspettare (limite di frequenza): prima di questo istante non si riprova.
    riprova_dopo: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    pubblicato_il: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
