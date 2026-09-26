"""Operazioni sullo stato di una lettura, indipendenti dal trasporto HTTP.

Il router chiama queste funzioni: qui sta la logica della posa delle carte,
delle dignità e della sintesi di Wirth, provabile senza un server.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from ..domain.base import utcnow
from ..domain.models import DrawnCard, Reading
from .conoscenza import Conoscenza
from .dignita import prevalenze, valuta
from .numerologia import riduci, sintesi_wirth


class StatoNonValido(Exception):
    """L'operazione non è permessa nello stato attuale della lettura."""


def prossima_posizione(stesa: Dict[str, Any], carte: List[DrawnCard]) -> Optional[int]:
    """La prima posizione da scegliere ancora vuota, in ordine di posa."""
    occupate = {c.posizione for c in carte}
    for p in stesa["posizioni"]:
        if not p.get("calcolata") and p["n"] not in occupate:
            return p["n"]
    return None


def posa(
    lettura: Reading, stesa: Dict[str, Any], slot: int, conoscenza: Conoscenza,
) -> DrawnCard:
    """Posa la carta dello slot scelto sulla prossima posizione.

    La carta è quella fissata al mescolamento: qui non si estrae nulla. Una
    posizione `senza_rovescio` (la carta 2 della Croce Celtica, posata di
    traverso: è per natura ciò che si oppone o si aggiunge, e non si legge
    «rovesciata») la riceve **sempre dritta**, qualunque sia l'orientamento
    fissato nello slot. Il mazzo impegnato non cambia: la regola è del codice e
    vale per tutti allo stesso modo.
    """
    if lettura.status != "scelta" or not lettura.deck_state:
        raise StatoNonValido("il ventaglio non è aperto")
    if not 0 <= slot < len(lettura.deck_state):
        raise StatoNonValido("slot inesistente")
    if any(c.slot == slot for c in lettura.cards):
        raise StatoNonValido("carta già scelta")
    posizione = prossima_posizione(stesa, lettura.cards)
    if posizione is None:
        raise StatoNonValido("tutte le carte sono già state scelte")

    fissata = lettura.deck_state[slot]
    senza_rovescio = bool(conoscenza.posizione(stesa, posizione).get("senza_rovescio"))
    carta = DrawnCard(
        posizione=posizione, slot=slot, card_id=fissata["card"],
        rovescio=bool(fissata["rovescio"]) and not senza_rovescio, created_at=utcnow(),
    )
    lettura.cards.append(carta)

    if prossima_posizione(stesa, lettura.cards) is None:
        _aggiungi_calcolate(lettura, stesa, conoscenza)
        lettura.status = "rivelazione"
    return carta


def _aggiungi_calcolate(lettura: Reading, stesa: Dict[str, Any], conoscenza: Conoscenza) -> None:
    """La carta di sintesi della croce semplice: la somma degli Arcani scelti.

    Sempre dritta: non viene dal mazzo, e un orientamento le sarebbe
    attribuito a caso.
    """
    for p in stesa["posizioni"]:
        if not p.get("calcolata"):
            continue
        scelte = [c for c in lettura.cards if not c.calcolata]
        numero = sintesi_wirth(conoscenza.carta(c.card_id)["numero"] or 0 for c in scelte)
        lettura.cards.append(DrawnCard(
            posizione=p["n"], slot=None, card_id=conoscenza.maggiore(numero)["id"],
            rovescio=False, calcolata=True, created_at=utcnow(),
        ))


def wirth(lettura: Reading, stesa: Dict[str, Any], conoscenza: Conoscenza) -> Optional[Dict[str, Any]]:
    if not stesa.get("sintesi_wirth"):
        return None
    scelte = [c for c in lettura.cards if not c.calcolata]
    calcolata = next((c for c in lettura.cards if c.calcolata), None)
    if calcolata is None:
        return None
    somma = sum(conoscenza.carta(c.card_id)["numero"] or 0 for c in scelte)
    return {
        "somma": somma,
        "ridotta": riduci(somma),
        "numero": conoscenza.carta(calcolata.card_id)["numero"],
        "nome": conoscenza.carta(calcolata.card_id)["nome_it"],
        "doppia_valenza": any(c.card_id == calcolata.card_id for c in scelte),
    }


def doppia_valenza(lettura: Reading, carta: DrawnCard) -> bool:
    if not carta.calcolata:
        return False
    return any(c.card_id == carta.card_id and not c.calcolata for c in lettura.cards)


def prossima_da_rivelare(lettura: Reading) -> Optional[DrawnCard]:
    return next((c for c in sorted(lettura.cards, key=lambda c: c.posizione) if not c.rivelata), None)


def dignita_di(
    lettura: Reading, stesa: Dict[str, Any], conoscenza: Conoscenza, *, solo_rivelate: bool,
) -> Dict[int, Dict[str, Any]]:
    elementi = {
        c.posizione: conoscenza.carta(c.card_id)["elemento"]
        for c in lettura.cards
        if c.rivelata or not solo_rivelate
    }
    return valuta(elementi, stesa.get("linee", []))


def prevalenze_di(lettura: Reading, conoscenza: Conoscenza) -> Dict[str, Any]:
    return prevalenze([conoscenza.carta(c.card_id) for c in lettura.cards if not c.calcolata])


def gia_rivelate(
    lettura: Reading, stesa: Dict[str, Any], conoscenza: Conoscenza, prima_di: int, lang: str = "it",
) -> str:
    """Le carte già girate, con i nomi nella lingua della risposta."""
    righe = []
    for c in sorted(lettura.cards, key=lambda c: c.posizione):
        if c.rivelata and c.posizione != prima_di:
            righe.append(
                f"- {conoscenza.nome_posizione(stesa, c.posizione, lang)}: "
                f"{conoscenza.nome_carta(c.card_id, lang)} ({'rovesciata' if c.rovescio else 'dritta'})"
            )
    return "\n".join(righe)


def note_di_posizione(stesa: Dict[str, Any], n: int, rivelate: Iterable[int]) -> List[str]:
    """Le regole della stesa che riguardano *questa* posizione, e solo questa.

    Sono le coppie che la stesa prescrive di leggere insieme, quando l'altra
    carta della coppia è già stata girata (altrimenti si anticiperebbe una carta
    che chi consulta non ha ancora visto), e l'avvertenza di una posizione che
    non si legge rovesciata.
    """
    visibili = set(rivelate)
    nomi = {p["n"]: p["nome"] for p in stesa["posizioni"]}
    note: List[str] = []
    for a, b, testo in stesa.get("coppie", []):
        if n in (a, b):
            altra = b if n == a else a
            if altra in visibili:
                note.append(f"Con la posizione {altra} ({nomi[altra]}): {testo}")
    if stesa["posizioni"][n - 1].get("senza_rovescio"):
        note.append(
            "Questa carta è posata di traverso: si legge sempre come dritta, "
            "è ciò che si oppone o si aggiunge alla carta 1."
        )
    return note
