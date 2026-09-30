"""La notifica ai motori di ricerca (v8): il registro di ogni invio.

Una riga per esecuzione — quella notturna del CronJob o quella lanciata a mano dalla console — con
gli indirizzi annunciati e l'esito di ciascun canale. Serve a due cose: alla console per mostrare
cosa è partito e cosa no, e all'esecuzione successiva per sapere da quando cercare le novità (la
finestra parte dall'ultima esecuzione, non da "ieri a mezzanotte": un CronJob saltato o in ritardo
non deve far perdere articoli).
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy import Boolean, DateTime, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class NotificaMotori(Base, TimestampMixin):
    __tablename__ = "notifiche_motori"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    #: Da quando si sono cercati articoli nuovi o aggiornati (l'esecuzione precedente).
    finestra_da: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    #: Lanciata dalla console invece che dal CronJob notturno.
    manuale: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    #: Gli indirizzi annunciati (vuota se non c'era nulla di nuovo: in quel caso non parte nulla).
    url: Mapped[List[str]] = mapped_column(JSONB, nullable=False, default=list)
    #: Per canale (`indexnow`, `search_console`, `websub`): `{"stato": "ok"|"errore"|"saltato",
    #: "dettaglio": "..."}`.
    esiti: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    #: Vero se nessun canale configurato è andato in errore.
    riuscita: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
