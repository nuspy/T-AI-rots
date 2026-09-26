"""Il blog: sezioni ad albero, articoli, etichette, collegamenti interni, immagini.

**Un solo albero.** Le carte, le stese e gli articoli non sono siti separati: stanno in
un'unica struttura (Tarocchi › Arcani maggiori · Impara i tarocchi › Le stese · Articoli ›
Amore…). Una sezione ha un `tipo`:

- `articoli`: contiene articoli;
- `carte`: elenca da sola le carte del catalogo che soddisfano `filtro` (per esempio
  `{"arcano": "maggiore"}` o `{"seme": "bastoni"}`), che restano pagine `/carte/{id}`;
- `stese`: elenca da sola le stese (`{"categoria": "coppia"}`), pagine `/stese/{id}`;
- `contenitore`: raggruppa altre sezioni.

**Collegamenti interni.** Ogni articolo può citare carte, stese e altri articoli: le citazioni
si estraggono dal testo quando si salva (`tarot/blog.estrai_collegamenti`) e stanno in
`blog_post_links`, così la pagina di una carta sa quali articoli la nominano.

**Immagini nel database.** Come le immagini di condivisione: niente volumi né servizi in più.
Si ricomprimono in WebP e si ridimensionano al caricamento (`tarot/blog.prepara_*`).
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, LargeBinary, String, Text,
    UniqueConstraint, Uuid, false, func, true,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

TIPI_SEZIONE = ("articoli", "carte", "stese", "contenitore")
STATI_ARTICOLO = ("bozza", "pubblicato", "archiviato")
TIPI_COLLEGAMENTO = ("carta", "stesa", "articolo")
USI_IMMAGINE = ("blog", "avatar")


class MediaImage(Base):
    """Un'immagine caricata: di un articolo, di una sezione o l'avatar di un utente."""

    __tablename__ = "media_images"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    uso: Mapped[str] = mapped_column(String(10), nullable=False)
    webp: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    larghezza: Mapped[int] = mapped_column(Integer, nullable=False)
    altezza: Mapped[int] = mapped_column(Integer, nullable=False)
    #: Chi l'ha caricata (per gli avatar, il proprietario).
    owner_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (CheckConstraint("uso in ('blog', 'avatar')", name="ck_media_images_uso"),)


class BlogSection(Base, TimestampMixin):
    __tablename__ = "blog_sections"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("blog_sections.id", ondelete="SET NULL"), index=True,
    )
    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    descrizione: Mapped[Optional[str]] = mapped_column(Text)
    tipo: Mapped[str] = mapped_column(String(20), default="articoli", nullable=False)
    #: Per `carte` e `stese`: quali elementi del catalogo elencare.
    filtro: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    ordine: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    visibile: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true(), nullable=False)
    immagine_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("media_images.id", ondelete="SET NULL"))
    seo_titolo: Mapped[Optional[str]] = mapped_column(String(200))
    seo_descrizione: Mapped[Optional[str]] = mapped_column(String(320))

    __table_args__ = (
        CheckConstraint("tipo in ('articoli', 'carte', 'stese', 'contenitore')", name="ck_blog_sections_tipo"),
        CheckConstraint("parent_id is null or parent_id <> id", name="ck_blog_sections_non_padre_di_se"),
    )


class BlogTag(Base):
    __tablename__ = "blog_tags"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(80), nullable=False)


class BlogPostTag(Base):
    __tablename__ = "blog_post_tags"

    post_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("blog_posts.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("blog_tags.id", ondelete="CASCADE"), primary_key=True)


class BlogPost(Base, TimestampMixin):
    __tablename__ = "blog_posts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    titolo: Mapped[str] = mapped_column(String(200), nullable=False)
    sottotitolo: Mapped[Optional[str]] = mapped_column(String(300))
    #: Markdown. Non si esegue HTML: il renderer lo ignora.
    testo: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    lang: Mapped[str] = mapped_column(String(5), default="it", server_default="it", nullable=False)
    immagine_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("media_images.id", ondelete="SET NULL"))
    immagine_alt: Mapped[Optional[str]] = mapped_column(String(200))
    sezione_id: Mapped[Optional[int]] = mapped_column(ForeignKey("blog_sections.id", ondelete="SET NULL"), index=True)
    autore_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    stato: Mapped[str] = mapped_column(String(12), default="bozza", server_default="bozza", nullable=False)
    #: Un articolo `pubblicato` con questa data nel futuro è **programmato**: compare da quel momento.
    pubblicato_il: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    in_evidenza: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false(), nullable=False)
    commenti_aperti: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true(), nullable=False)
    seo_titolo: Mapped[Optional[str]] = mapped_column(String(200))
    seo_descrizione: Mapped[Optional[str]] = mapped_column(String(320))
    #: Minuti di lettura, calcolati dal testo a ogni salvataggio.
    tempo_lettura: Mapped[int] = mapped_column(Integer, default=1, server_default="1", nullable=False)

    tags: Mapped[list[BlogTag]] = relationship(secondary="blog_post_tags", lazy="selectin", order_by="BlogTag.nome")

    __table_args__ = (
        CheckConstraint("stato in ('bozza', 'pubblicato', 'archiviato')", name="ck_blog_posts_stato"),
        Index("ix_blog_posts_stato_data", "stato", "pubblicato_il"),
    )


class BlogPostLink(Base):
    """Una citazione interna: questo articolo parla di quella carta, stesa o altro articolo."""

    __tablename__ = "blog_post_links"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    post_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("blog_posts.id", ondelete="CASCADE"), nullable=False)
    tipo: Mapped[str] = mapped_column(String(10), nullable=False)
    riferimento: Mapped[str] = mapped_column(String(160), nullable=False)

    __table_args__ = (
        UniqueConstraint("post_id", "tipo", "riferimento", name="uq_blog_post_links"),
        CheckConstraint("tipo in ('carta', 'stesa', 'articolo')", name="ck_blog_post_links_tipo"),
        Index("ix_blog_post_links_riferimento", "tipo", "riferimento"),
    )


class BlogPostRevision(Base):
    """Una versione precedente del testo: si può tornare indietro."""

    __tablename__ = "blog_post_revisions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    post_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("blog_posts.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    titolo: Mapped[str] = mapped_column(String(200), nullable=False)
    sottotitolo: Mapped[Optional[str]] = mapped_column(String(300))
    testo: Mapped[str] = mapped_column(Text, nullable=False)
    autore_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
