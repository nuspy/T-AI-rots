"""I mazzi in vendita (v5, Fase B).

**Un mazzo nuovo è una risvestizione grafica del Thoth**, non una nuova base di conoscenza: stesso
schema di 78 carte (`maj-NN`, `<seme>-<numero>`, le corti), stessi significati (`Conoscenza` resta
globale e condivisa) — cambia solo l'artwork. Estendere `Conoscenza` a significati diversi per mazzo è
esplicitamente fuori scope per questa fase (vedi il piano).

**La grafica, in due modi.** I mazzi installati come file (il Thoth in `frontend/public/cards/`, gli altri in
`frontend/public/cards/<slug>/`, con `tools/installa_mazzo.py`) richiedono un build+deploy del frontend. Dal
2026-10 un mazzo si carica anche dalla console (uno ZIP o una cartella con le 78 carte e il dorso): le
immagini, già in WebP alla misura web, stanno in `DeckCardImage` e le serve l'API — il sito le mostra
subito, senza ricostruire niente (il frontend chiede `/cards/<slug>/<id>.webp`: se quel file non c'è, la
richiesta passa all'API). `Deck` resta la scheda **commerciale** (prezzo, finestra di attivazione, chi lo
possiede).

**Il mazzo predefinito** (il Thoth) è posseduto da chiunque senza una riga in `DeckUnlock`: non ha
bisogno di essere comprato, e non deve poter essere disattivato per errore (vedi il vincolo sotto).
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, DateTime, ForeignKey, Integer, LargeBinary, String, Text, UniqueConstraint,
    false, text, true,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

#: Come per `Coupon`: percentuale (1-100) o importo fisso in centesimi.
TIPI_OFFERTA_MAZZO = ("percentuale", "importo")


class Deck(Base, TimestampMixin):
    """Un mazzo acquistabile: metadati commerciali, non l'artwork (file statici nel frontend)."""

    __tablename__ = "decks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(80), nullable=False)
    descrizione: Mapped[Optional[str]] = mapped_column(Text)
    #: Nome e descrizione nelle lingue del sito (v8.5, `billing/lingue.py`): lingua → testo. Vuoti: si mostra
    #: l'inglese, poi il nome originale.
    nomi: Mapped[Dict[str, str]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    descrizioni: Mapped[Dict[str, str]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))

    #: Il Thoth: sempre posseduto da tutti, nessuna riga di sblocco necessaria. Non può essere
    #: disattivato (vincolo sotto) — un impianto senza nessun mazzo utilizzabile non deve poter
    #: esistere per un errore di console.
    predefinito: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false(), nullable=False)
    #: Interruttore manuale, indipendente dalla finestra di attivazione sotto.
    attivo: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true(), nullable=False)
    #: Attivazione stagionale (es. un mazzo di Halloween solo in ottobre): entrambe nulle = sempre,
    #: se `attivo`. Un mazzo con la finestra scaduta sparisce dal negozio come un'offerta scaduta —
    #: stesso principio di lettura-a-confronto-con-`now()`, nessun job pianificato.
    attivazione_da: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    attivazione_fino: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    #: Prezzi in centesimi, ciascuno opzionale: nullo = quel prodotto non è offerto per questo mazzo.
    #: Digitale: sblocco per le letture in app. Stampa: il PDF fai-da-te (Fase B4). Fisico: il mazzo
    #: vero, stampato professionalmente e spedito (Fase B5) — oggi annunciato solo per il Thoth
    #: ("cofanetto da collezione" in `MAZZO.description`).
    prezzo_digitale: Mapped[Optional[int]] = mapped_column(Integer)
    prezzo_stampa: Mapped[Optional[int]] = mapped_column(Integer)
    prezzo_fisico: Mapped[Optional[int]] = mapped_column(Integer)
    richiede_spedizione: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false(), nullable=False)
    valuta: Mapped[str] = mapped_column(String(3), default="EUR", server_default="EUR", nullable=False)

    #: Ordine di presentazione nel negozio.
    rank: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    #: L'impronta dell'ultima serie di immagini caricata dalla console e pubblicata (`DeckCardImage`): `None` = il
    #: mazzo usa i file del sito (o non ha ancora immagini).
    immagini_versione: Mapped[Optional[str]] = mapped_column(String(16))

    __table_args__ = (
        CheckConstraint(
            "attivazione_da is null or attivazione_fino is null or attivazione_da < attivazione_fino",
            name="ck_decks_finestra_attivazione",
        ),
    )

    @property
    def attivo_ora(self) -> bool:
        """Visibile nel negozio adesso: acceso a mano E dentro la finestra stagionale, se c'è."""
        if not self.attivo:
            return False
        adesso = datetime.now(self.created_at.tzinfo) if self.created_at.tzinfo else datetime.now()
        if self.attivazione_da and adesso < self.attivazione_da:
            return False
        if self.attivazione_fino and adesso > self.attivazione_fino:
            return False
        return True


class DeckUnlock(Base):
    """Chi possiede quale mazzo digitale. Il mazzo predefinito non ha bisogno di una riga qui."""

    __tablename__ = "deck_unlocks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    deck_id: Mapped[int] = mapped_column(ForeignKey("decks.id", ondelete="CASCADE"), nullable=False)
    acquired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    #: La riga d'ordine che ha originato lo sblocco (Fase B3, `domain/ordini_models.py::RigaOrdine`,
    #: chiave `BigInteger` come le altre righe interne). Nullo per gli sblocchi che non vengono da un
    #: acquisto vero (nessuno, oggi — ma il predefinito non passa mai di qui, quindi resta possibile).
    riga_ordine_id: Mapped[Optional[int]] = mapped_column(BigInteger)

    deck: Mapped[Deck] = relationship()

    __table_args__ = (
        UniqueConstraint("user_id", "deck_id", name="uq_deck_unlocks_utente_mazzo"),
    )


class OffertaMazzo(Base, TimestampMixin):
    """Uno sconto a tempo sul prezzo digitale di un mazzo (v5, Fase B2): non un codice da riscattare
    come `Coupon` — un prezzo mostrato, in vigore da solo. `deck_id` è la chiave primaria: **un solo**
    sconto attivo per mazzo alla volta, sostituito con un `PUT`, non accumulato con un altro.

    Nessun job di scadenza: come per `Coupon.valido_fino`, il confronto con `now()` avviene a ogni
    lettura del prezzo (`prezzo_effettivo()` in `billing/mazzi.py`) — un'offerta scaduta sparisce da
    sola, non richiede che qualcuno la cancelli."""

    __tablename__ = "offerte_mazzo"

    deck_id: Mapped[int] = mapped_column(ForeignKey("decks.id", ondelete="CASCADE"), primary_key=True)
    tipo: Mapped[str] = mapped_column(String(12), nullable=False)
    valore: Mapped[int] = mapped_column(Integer, nullable=False)
    valido_dal: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    valido_fino: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    #: A quali prodotti si applica (v8.5): `digitale`, `pdf`, `fisico`. Le offerte nate prima valevano solo sul
    #: digitale, e così restano.
    formati: Mapped[List[str]] = mapped_column(JSONB, nullable=False, default=lambda: ["digitale"],
                                               server_default=text("'[\"digitale\"]'::jsonb"))

    deck: Mapped[Deck] = relationship()

    __table_args__ = (
        CheckConstraint("tipo in ('percentuale', 'importo')", name="ck_offerte_mazzo_tipo"),
        CheckConstraint("tipo <> 'percentuale' or valore <= 100", name="ck_offerte_mazzo_percentuale"),
        CheckConstraint(
            "valido_dal is null or valido_fino is null or valido_dal < valido_fino",
            name="ck_offerte_mazzo_finestra",
        ),
    )


class DeckCardImage(Base, TimestampMixin):
    """Un'immagine di un mazzo caricato dalla console: una carta (`maj-00`, `bastoni-06`, …) o il dorso (`dorso`),
    già convertita in WebP alla misura web (`tarot/immagini_mazzo.py`). La serve `GET /decks/{slug}/cards/{id}.webp`
    con l'`etag` (l'impronta dei byte) e una cache lunga.

    **Bozza e pubblicate.** Una cartella si carica un file per richiesta: le righe nascono `bozza` e il sito non le
    vede finché la serie non è completa (78 + dorso) e la si pubblica — allora sostituiscono in blocco quelle di
    prima. Uno ZIP arriva tutto insieme e si pubblica nella stessa richiesta, senza passare dalla bozza."""

    __tablename__ = "deck_card_images"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    deck_id: Mapped[int] = mapped_column(ForeignKey("decks.id", ondelete="CASCADE"), nullable=False)
    card_id: Mapped[str] = mapped_column(String(20), nullable=False)
    bozza: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false(), nullable=False)
    webp: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    larghezza: Mapped[int] = mapped_column(Integer, nullable=False)
    altezza: Mapped[int] = mapped_column(Integer, nullable=False)
    etag: Mapped[str] = mapped_column(String(64), nullable=False)

    __table_args__ = (
        UniqueConstraint("deck_id", "card_id", "bozza", name="uq_deck_card_images_carta"),
    )
