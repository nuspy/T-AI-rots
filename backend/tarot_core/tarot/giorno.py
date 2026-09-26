"""La carta del giorno per tutti.

`GET /me/daily-card` dà a ogni utente la sua carta (con la serie dei giorni di fila). Questa è un'altra cosa: **una
sola carta per tutti, uguale per chiunque nello stesso giorno**, senza account. È la pagina pubblica
`/card-of-the-day` — la porta d'ingresso di chi cerca «tarot card of the day» — e ogni giorno cambia contenuto.

Deterministica: si ricava dalla data (UTC) con un hash, senza database né stato; due server, o due richieste nello
stesso istante, scelgono la stessa carta. Solo Arcani maggiori e sempre dritta: il Tarocco di Thoth si legge senza
carte rovesciate, e una carta pubblica non ha il contesto per giudicare la dignità.
"""
from __future__ import annotations

import hashlib
from datetime import date, datetime, timezone
from typing import Optional

from .conoscenza import Conoscenza


def oggi_utc() -> date:
    return datetime.now(timezone.utc).date()


def carta_universale(conoscenza: Conoscenza, giorno: Optional[date] = None) -> str:
    """L'id della carta di questo giorno (per tutti)."""
    giorno = giorno or oggi_utc()
    seme = hashlib.sha256(f"universale:{giorno.isoformat()}".encode()).digest()
    maggiori = [i for i in conoscenza.ordine if conoscenza.carte[i]["arcano"] == "maggiore"]
    return maggiori[int.from_bytes(seme[:4], "big") % len(maggiori)]
