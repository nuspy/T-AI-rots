"""Validazione dei nomi file di un upload di artwork carte (v7, Fasi I e K).

Stessa convenzione già usata da `tools/crea_mazzo.py`/`tools/resize_cards.py`: il nome del file,
senza estensione, È l'id della carta (`maj-00`, `bastoni-06`, `dorso`) — l'attribuzione è quindi
"automatica per convenzione", non una mappa scritta a mano da mantenere in sincronia altrove.
"""
from __future__ import annotations

import io
import zipfile
from typing import Iterable, Set, Tuple


class ZipArtworkNonValido(ValueError):
    """Lo ZIP caricato non è leggibile."""


def nomi_attesi(id_carte: Iterable[str], estensione: str = "webp", *, dorso: bool = True) -> Set[str]:
    attesi = {f"{cid}.{estensione}" for cid in id_carte}
    if dorso:
        attesi.add(f"dorso.{estensione}")
    return attesi


def valida_zip(corpo: bytes, attesi: Set[str]) -> Tuple[Set[str], Set[str]]:
    """`(presenti, mancanti)` fra i nomi attesi. Solleva `ZipArtworkNonValido` se `corpo` non è
    uno ZIP leggibile — non convalida il contenuto delle immagini stesse, solo i nomi: chi carica
    file corrotti se ne accorge comunque aprendo l'anteprima prima di estrarli nel repository."""
    try:
        archivio = zipfile.ZipFile(io.BytesIO(corpo))
    except zipfile.BadZipFile as exc:
        raise ZipArtworkNonValido("Il file caricato non è uno ZIP valido") from exc
    presenti = {nome.rsplit("/", 1)[-1] for nome in archivio.namelist() if not nome.endswith("/")}
    return presenti, attesi - presenti
