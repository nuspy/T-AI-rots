"""Quanto consumano i modelli: una riga per chiamata, e i listini con cui stimarne il costo.

**Una riga per chiamata HTTP, non per compito.** Un compito può costare più chiamate — il budget che si alza quando il
modello ragiona troppo (`_genera_con_budget`), il dialetto JSON che si negozia, la sintesi riscritta dopo il giudizio —
e il conto vero è quello che il fornitore fattura: chiamata per chiamata.

**Niente dati di chi consulta.** Solo numeri, il compito, la fase («# Compito: …» del prompt) e l'id della lettura per
raggruppare: nessun testo dei prompt né delle risposte. L'id della lettura non è una chiave esterna di proposito — la
cancellazione di una lettura non deve fallire né trascinarsi dietro la contabilità, come per il registro dei crediti.

**Il listino è dell'operatore.** I prezzi dei fornitori cambiano e si confrontano: si scrivono dalla console (pagina
«Costi»), non nel codice. `cache_hit` è la quota stimata dell'ingresso **cacheabile** che il fornitore trova davvero
in cache: si applica solo al prefisso stabile (vedi `api/routers/admin_costi.py`).
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, DateTime, Index, Integer, Numeric, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class LlmConsumo(Base):
    """Una chiamata a un modello: chi l'ha chiesta, quanto è costata in token, come è finita."""

    __tablename__ = "llm_consumi"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    #: Il compito di `llm.compiti.Compito` (intervista, sintesi, embedding…). Vuoto: una chiamata fuori dal registro.
    compito: Mapped[str] = mapped_column(String(40), nullable=False, default="")
    #: Cosa si chiedeva davvero: il «# Compito: …» del prompt di sistema (teaser e sintesi condividono il compito),
    #: con un suffisso per i casi che lo stesso prompt non distingue (`intervista.riassunto`, `sintesi.revisione`).
    fase: Mapped[str] = mapped_column(String(40), nullable=False, default="")
    fornitore: Mapped[str] = mapped_column(String(80), nullable=False, default="")
    modello: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    token_ingresso: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    #: La parte dell'ingresso che il fornitore ha trovato in cache (`prompt_tokens_details.cached_tokens`).
    token_cache: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    #: Tutta l'uscita fatturata, ragionamento compreso.
    token_uscita: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    #: La parte dell'uscita spesa a ragionare (già compresa in `token_uscita`).
    token_ragionamento: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    #: I caratteri, per stimare quando il fornitore non riporta il consumo (e per controllarlo quando lo riporta).
    caratteri_ingresso: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    caratteri_uscita: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    caratteri_ragionamento: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    #: I caratteri dei messaggi di sistema iniziali: la parte stabile del prompt, quella che un fornitore con
    #: prompt caching può trovare in cache. Serve a stimare la quota cacheabile dell'ingresso per i listini.
    caratteri_sistema: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    #: Il tetto chiesto (`max_tokens` del payload), per capire quanto spazio si lascia al ragionamento.
    max_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    durata_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    #: `ok`, `troncata` (budget finito senza testo), `errore`, `interrotta` (flusso chiuso prima della fine).
    esito: Mapped[str] = mapped_column(String(20), nullable=False, default="ok")
    finish_reason: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    #: Testo chiesto con `stream()` (interpretazione, sintesi, teaser) invece che JSON con `complete_json()`.
    streaming: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    #: Il fornitore ha riportato il consumo (`usage`): se no, i token sono zero e valgono i caratteri.
    usage_riportato: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    reading_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    #: Un riferimento che non è una lettura: `chat` per la chat dell'oracolo, `misura:<scenario>` per le prove.
    riferimento: Mapped[str] = mapped_column(String(80), nullable=False, default="")
    #: Il primo pezzo del messaggio d'errore, senza dati della richiesta.
    errore: Mapped[str] = mapped_column(String(300), nullable=False, default="")

    __table_args__ = (
        Index("ix_llm_consumi_created_at", "created_at"),
        Index("ix_llm_consumi_reading_id", "reading_id"),
        Index("ix_llm_consumi_compito_created", "compito", "created_at"),
    )


class LlmListino(Base, TimestampMixin):
    """Il prezzo di un fornitore, in dollari per milione di token, con la quota di cache che ci si aspetta."""

    __tablename__ = "llm_listini"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    prezzo_ingresso: Mapped[float] = mapped_column(Numeric(10, 4, asdecimal=False), nullable=False, default=0)
    prezzo_cache: Mapped[float] = mapped_column(Numeric(10, 4, asdecimal=False), nullable=False, default=0)
    prezzo_uscita: Mapped[float] = mapped_column(Numeric(10, 4, asdecimal=False), nullable=False, default=0)
    #: Fra 0 e 1: la quota dell'ingresso cacheabile che si stima trovata in cache.
    cache_hit: Mapped[float] = mapped_column(Numeric(5, 4, asdecimal=False), nullable=False, default=0)
    #: Il listino del fornitore in uso: la pagina «Costi» lo mette per primo.
    attuale: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    nota: Mapped[str] = mapped_column(String(300), nullable=False, default="")
