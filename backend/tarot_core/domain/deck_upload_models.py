"""L'upload dell'artwork di un mazzo da GUI admin (v7, Fase I) — l'«Archivio ZIP da scaricare» della console.

Dal 2026-10 c'è anche la strada diretta, separata da questa: le «Immagini del mazzo nel sito» (`DeckCardImage` in
`deck_models.py`), convertite e servite dall'API, online senza rilascio. Questo archivio resta per chi vuole
installare il mazzo come file del frontend.

**Perché un blob temporaneo in DB e non un file sul pod.** L'artwork finale resta un file statico
dentro l'immagine Docker del frontend (decisione presa con l'operatore, vedi `deck_models.py`): un
mazzo nuovo richiede comunque un rilascio. Questo modello non cambia quella decisione — automatizza
solo il passo che oggi è manuale (copiare 79 file uno per uno, o con `kubectl cp`): l'amministratore
carica uno ZIP già validato (nomi corretti, tutte le carte presenti) dalla console, lo riscarica con
lo stesso meccanismo già in uso per i report CSV (`admin/lib/api.ts::scaricaReport`, sessione
autenticata del browser), e lo estrae a mano in `frontend/public/cards/<slug>/` prima del build.
Un file sul pod (invece che in DB) sparirebbe al prossimo deploy e non sarebbe replicato su più
repliche dell'API — lo stesso motivo per cui l'artwork finale non vive lì.

**Non permanente.** Una riga qui è un passaggio di transito, non un archivio: l'amministratore la
elimina dopo aver scaricato ed estratto lo ZIP (endpoint `DELETE`), o resta finché qualcuno lo fa —
nessuna pulizia automatica in questa fase, il volume atteso (poche righe, mai a lungo) non la
giustifica.
"""
from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import BigInteger, ForeignKey, Integer, LargeBinary, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class DeckArtworkUpload(Base, TimestampMixin):
    __tablename__ = "deck_artwork_uploads"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    #: Lo slug del mazzo (non una chiave esterna verso `decks`: si può caricare l'artwork di un
    #: mazzo candidato al voto — Fase K — prima ancora che esista una riga `Deck` vera).
    slug: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    zip_bytes: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    file_count: Mapped[int] = mapped_column(Integer, nullable=False)
    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"),
    )
