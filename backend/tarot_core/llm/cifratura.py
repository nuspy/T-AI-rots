"""La chiave di un fornitore LLM, cifrata a riposo nel database.

Un endpoint di console che legge e scrive fornitori non deve mai far uscire una chiave in chiaro: la si cifra prima
di scriverla (`cifra`) e la si decifra solo nel momento di usarla (costruire il fornitore, provare la connessione).
`TAROT_LLM_PROVIDER_KEY` è una chiave Fernet (32 byte base64 url-safe, `Fernet.generate_key()`); il valore predefinito
è **solo per lo sviluppo** ed è respinto da `Settings.validate_production()`.

Una chiave persa o cambiata rende illeggibili le righe cifrate con la precedente: `decifra` non solleva, torna una
stringa vuota — un fornitore senza chiave è un guasto visibile subito (la prima richiesta fallisce), un avvio che si
rifiuta di partire per una riga vecchia sarebbe peggio.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Optional


@lru_cache(maxsize=1)
def _fernet():
    from cryptography.fernet import Fernet

    from ..settings import get_settings

    return Fernet(get_settings().llm_provider_key.encode("ascii"))


def cifra(chiaro: str) -> Optional[bytes]:
    """`None` per «nessuna chiave»: un fornitore locale senza autenticazione non ne ha una da cifrare."""
    chiaro = (chiaro or "").strip()
    if not chiaro:
        return None
    return _fernet().encrypt(chiaro.encode("utf-8"))


def decifra(cifrato: Optional[bytes]) -> str:
    if not cifrato:
        return ""
    from cryptography.fernet import InvalidToken

    try:
        return _fernet().decrypt(bytes(cifrato)).decode("utf-8")
    except InvalidToken:
        return ""


def reset_cache() -> None:
    """Solo per i test: dimentica la chiave letta, dopo un `monkeypatch` delle impostazioni."""
    _fernet.cache_clear()
