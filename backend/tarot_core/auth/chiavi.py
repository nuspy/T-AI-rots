"""Le chiavi applicative: come un agente (Hermes, OpenClaw, uno script) si presenta all'API senza passare da Keycloak.

Una chiave ha la forma `tk_live_<43 caratteri>`. Si presenta come `Authorization: Bearer tk_live_…` oppure come
`X-API-Key: tk_live_…`. Nel database non c'è: c'è l'impronta SHA-256 (una chiave è già casuale e lunga, quindi un
hash veloce basta — una password ne vorrebbe uno lento) e il prefisso, che serve a trovarla e a riconoscerla
nell'elenco. Si mostra **una volta sola**, alla creazione.

Tre difese, in quest'ordine: la chiave dev'essere valida e attiva (401), avere il permesso richiesto (403), e non
superare le richieste al minuto (429, con `Retry-After`). Il limite è in memoria del processo: con più repliche
ciascuna conta per sé, che per un freno a un agente incantato basta e avanza.
"""
from __future__ import annotations

import hashlib
import hmac
import secrets
import time
from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, List, Tuple

from fastapi import Depends, HTTPException, Request
from sqlalchemy import select

from ..domain.base import utcnow
from ..domain.blog_models import ApiKey
from .dependencies import DbSession

PREFISSO_CHIAVE = "tk_live_"
LUNGHEZZA_PREFISSO = 12
SCOPES_VALIDI = ("blog:write", "blog:publish")


def impronta(chiave: str) -> str:
    return hashlib.sha256(chiave.encode()).hexdigest()


def genera_chiave() -> Tuple[str, str, str]:
    """`(chiave, prefisso, impronta)`. La chiave si mostra una volta; il resto si salva."""
    chiave = f"{PREFISSO_CHIAVE}{secrets.token_urlsafe(32)}"
    return chiave, chiave[:LUNGHEZZA_PREFISSO], impronta(chiave)


@dataclass(frozen=True)
class ChiaveVerificata:
    id: int
    nome: str
    prefisso: str
    scopes: Tuple[str, ...]
    limite_giorno: int

    def puo(self, scope: str) -> bool:
        return scope in self.scopes


def _estrai(request: Request) -> str:
    intestazione = request.headers.get("authorization", "")
    if intestazione.lower().startswith("bearer "):
        return intestazione[7:].strip()
    return (request.headers.get("x-api-key") or "").strip()


# ---- il freno alle richieste --------------------------------------------------------------------------------

_FINESTRA_SECONDI = 60.0
_richieste: Dict[int, Deque[float]] = {}


def _entro_il_limite(chiave_id: int, limite: int, adesso: float) -> float:
    """0 se la richiesta passa; altrimenti i secondi da aspettare."""
    coda = _richieste.setdefault(chiave_id, deque())
    while coda and adesso - coda[0] > _FINESTRA_SECONDI:
        coda.popleft()
    if len(coda) >= limite:
        return max(1.0, _FINESTRA_SECONDI - (adesso - coda[0]))
    coda.append(adesso)
    return 0.0


def azzera_limiti() -> None:
    """Solo per i test."""
    _richieste.clear()


def richiede(scope: str):
    """Dipendenza FastAPI: `Depends(richiede("blog:write"))` restituisce la `ChiaveVerificata` o risponde 401/403/429."""

    async def dipendenza(request: Request, session: DbSession) -> ChiaveVerificata:
        chiave = _estrai(request)
        if not chiave.startswith(PREFISSO_CHIAVE) or len(chiave) < LUNGHEZZA_PREFISSO + 16:
            raise HTTPException(
                status_code=401, detail="Serve una chiave applicativa: `Authorization: Bearer tk_live_…` o `X-API-Key`.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        riga = (await session.execute(select(ApiKey).where(ApiKey.prefisso == chiave[:LUNGHEZZA_PREFISSO]))).scalar_one_or_none()
        # Il confronto è a tempo costante anche quando la chiave non esiste (contro un'impronta finta).
        atteso = riga.impronta if riga is not None else "0" * 64
        valida = hmac.compare_digest(impronta(chiave), atteso) and riga is not None and riga.attiva
        if not valida:
            raise HTTPException(status_code=401, detail="Chiave non valida o revocata.", headers={"WWW-Authenticate": "Bearer"})
        assert riga is not None
        scopes: List[str] = list(riga.scopes or [])
        if scope not in scopes:
            raise HTTPException(status_code=403, detail=f"La chiave non ha il permesso «{scope}».")
        attesa = _entro_il_limite(riga.id, riga.limite_minuto, time.monotonic())
        if attesa:
            raise HTTPException(
                status_code=429, detail="Troppe richieste: aspetta un po'.", headers={"Retry-After": str(int(attesa) + 1)},
            )
        riga.ultimo_uso = utcnow()
        riga.usi = (riga.usi or 0) + 1
        return ChiaveVerificata(
            id=riga.id, nome=riga.nome, prefisso=riga.prefisso, scopes=tuple(scopes), limite_giorno=riga.limite_giorno,
        )

    return dipendenza


ChiaveScrittura = Depends(richiede("blog:write"))
