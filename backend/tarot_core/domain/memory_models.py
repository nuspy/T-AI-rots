"""La memoria per utente (v6, Fase A): fatti stabili e variabili estratti dalle letture e dalla chat.

**Perché non pgvector.** Il piano approvato sceglieva un'estensione vettoriale nativa
(`pgvector`), ma il Postgres condiviso del namespace `tadamoo` (Alpine, senza il pacchetto
`postgresql-pgvector` installato) non la offre, e installarla richiederebbe ricostruire e
riavviare un servizio condiviso con Keycloak — fuori scope per questa release. `embedding` è
quindi un array di float, e la similarità coseno si calcola lato applicazione in
`tarot/memoria_retrieval.py::rilevanti()`, sul modello del ripiego già previsto nel piano
(Open Risk #1): stessa qualità di recupero (embedding reali), solo senza indice ANN nativo —
irrilevante al numero di memorie atteso per utente (poche centinaia, non milioni).

**Perché `owner_id` non usa `OwnedMixin`.** Il mixin lo dichiara nullable per servire anche
tabelle come `Reading`, dove una riga anonima è legittima. Una memoria senza proprietario non
ha senso: qui è dichiarato a mano, non nullable — resta comunque un dato «di proprietà», da
leggere e scrivere solo attraverso `memoria_repositories.py`, filtrato per `owner_id`.

**`superseded_by`.** Sostituire una memoria `variabile` non la cancella: la vecchia riga riceve
`superseded_by = nuova.id` e resta interrogabile per il confronto prima/dopo che la sintesi usa
(Fase C). Il retrieval per il prompt filtra `WHERE superseded_by IS NULL` per default — stesso
spirito append-only di `CreditEntry`.
"""
from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy import ARRAY, BigInteger, CheckConstraint, Float, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin, owner_index

#: `stabile`: fatti fisici/anagrafici/di identità che non regrediscono naturalmente — non si
#: richiedono mai di nuovo (vedi l'esempio nel prompt dell'intervista, Fase C).
#: `variabile`: situazioni che evolvono, di cui si può chiedere l'aggiornamento.
TIPI_MEMORIA = ("stabile", "variabile")

#: Da dove nasce la memoria: una lettura conclusa o un turno della chat proattiva.
FONTI_MEMORIA = ("lettura", "chat")


class UserMemory(Base, TimestampMixin):
    """Un fatto ricordato su un utente, con il proprio vettore per il recupero per pertinenza."""

    __tablename__ = "user_memories"
    __table_args__ = (
        CheckConstraint(f"tipo IN {TIPI_MEMORIA}", name="ck_user_memories_tipo"),
        CheckConstraint(f"fonte IN {FONTI_MEMORIA}", name="ck_user_memories_fonte"),
        owner_index("user_memories", "campo_attinenza"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    contenuto: Mapped[str] = mapped_column(Text, nullable=False)
    tipo: Mapped[str] = mapped_column(String(10), nullable=False)
    #: Es. "amore", "lavoro", "salute", "famiglia", "denaro", "spirituale", "altro" — il modello
    #: classifica liberamente, non è un enum chiuso lato codice (vedi tarot/memoria.py).
    campo_attinenza: Mapped[str] = mapped_column(String(40), nullable=False)
    embedding: Mapped[List[float]] = mapped_column(ARRAY(Float), nullable=False)
    reading_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("readings.id", ondelete="SET NULL"), nullable=True,
    )
    fonte: Mapped[str] = mapped_column(String(20), nullable=False)
    #: Non nullo: questa riga è stata sostituita da una più recente sullo stesso campo. La catena
    #: resta interrogabile; il retrieval per il prompt la esclude per default.
    superseded_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("user_memories.id", ondelete="SET NULL"), nullable=True,
    )
