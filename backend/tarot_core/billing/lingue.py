"""Nomi e descrizioni di piani e mazzi nelle lingue del sito (v8.5).

Ogni piano e ogni mazzo ha il suo nome «originale» (`Plan.name`, `Deck.nome`: quello scritto in console, in
italiano per i piani storici) e, accanto, le traduzioni per lingua (`nomi`, `descrizioni`: JSON lingua → testo).
Si mostra la lingua chiesta; se manca, l'inglese; se manca anche quello, l'originale. Le traduzioni dei piani del
catalogo iniziale stanno qui sotto: le usano il seed (database nuovi) e la migrazione `b2e7c4a19d05` (database già in
uso, solo dove le traduzioni mancano).
"""
from __future__ import annotations

from typing import Dict, Mapping, Optional

#: Le lingue in cui la console chiede le traduzioni (le stesse dell'interfaccia v2).
LINGUE = ("en", "it", "hu", "ru", "uk", "es", "de", "fr", "pt", "ro", "pl", "zh", "hi", "ko", "ar")


def in_lingua(traduzioni: Optional[Mapping[str, str]], lingua: Optional[str], originale: Optional[str]) -> Optional[str]:
    """Il testo nella lingua chiesta, poi l'inglese, poi l'originale. Una traduzione vuota non conta. Senza lingua,
    l'originale: chi non la chiede (la v1) vede ciò che vedeva prima."""
    if not lingua:
        return originale
    t = {k: v for k, v in (traduzioni or {}).items() if isinstance(v, str) and v.strip()}
    if lingua and lingua in t:
        return t[lingua]
    return t.get("en") or originale


def pulisci(traduzioni: Optional[Mapping[str, Optional[str]]], massimo: int) -> Dict[str, str]:
    """Solo lingue conosciute, testi non vuoti, lunghezza massima: quello che arriva dalla console."""
    out: Dict[str, str] = {}
    for lingua, testo in (traduzioni or {}).items():
        if lingua in LINGUE and isinstance(testo, str) and testo.strip():
            out[lingua] = testo.strip()[:massimo]
    return out


TRADUZIONI_PIANI: Dict[str, Dict[str, Dict[str, str]]] = {
    "free": {
        "nomi": {"en": "Free", "it": "Gratuito", "hu": "Ingyenes", "ru": "Бесплатный", "uk": "Безкоштовний", "es": "Gratis"},
        "descrizioni": {
            "en": "The card of the day, every day. Readings are paid with credits.",
            "it": "La carta del giorno ogni giorno. Le letture si pagano con i crediti.",
            "hu": "Minden nap a nap kártyája. Az olvasásokat kreditekkel fizeted.",
            "ru": "Карта дня — каждый день. Чтения оплачиваются кредитами.",
            "uk": "Карта дня — щодня. Читання оплачуються кредитами.",
            "es": "La carta del día, cada día. Las lecturas se pagan con créditos.",
        },
    },
    "mensile-base": {
        "nomi": {"en": "Monthly Basic", "it": "Mensile Base", "hu": "Havi Alap", "ru": "Базовый месячный",
                 "uk": "Базовий місячний", "es": "Mensual Básico"},
        "descrizioni": {
            "en": "Three readings a day, every spread, unlimited history.",
            "it": "Tre letture al giorno, tutte le stese, storico illimitato.",
            "hu": "Napi három olvasás, minden kirakás, korlátlan előzmények.",
            "ru": "Три чтения в день, все расклады, неограниченная история.",
            "uk": "Три читання на день, усі розклади, необмежена історія.",
            "es": "Tres lecturas al día, todas las tiradas, historial ilimitado.",
        },
    },
    "mensile-oro": {
        "nomi": {"en": "Monthly Gold", "it": "Mensile Oro", "hu": "Havi Arany", "ru": "Золотой месячный",
                 "uk": "Золотий місячний", "es": "Mensual Oro"},
        "descrizioni": {
            "en": "Ten readings a day, for those who consult the cards often.",
            "it": "Dieci letture al giorno per chi consulta spesso le carte.",
            "hu": "Napi tíz olvasás azoknak, akik gyakran kérdezik a kártyákat.",
            "ru": "Десять чтений в день — для тех, кто часто обращается к картам.",
            "uk": "Десять читань на день — для тих, хто часто звертається до карт.",
            "es": "Diez lecturas al día para quien consulta a menudo las cartas.",
        },
    },
    "pacchetto-5": {
        "nomi": {"en": "5 readings", "it": "5 letture", "hu": "5 olvasás", "ru": "5 чтений", "uk": "5 читань", "es": "5 lecturas"},
        "descrizioni": {
            "en": "Five readings, no expiry.", "it": "Cinque consulti, senza scadenza.",
            "hu": "Öt olvasás, lejárat nélkül.", "ru": "Пять чтений без срока действия.",
            "uk": "П'ять читань без терміну дії.", "es": "Cinco lecturas, sin caducidad.",
        },
    },
    "pacchetto-15": {
        "nomi": {"en": "15 readings", "it": "15 letture", "hu": "15 olvasás", "ru": "15 чтений", "uk": "15 читань", "es": "15 lecturas"},
        "descrizioni": {
            "en": "Fifteen readings, no expiry. The most chosen.", "it": "Quindici consulti, senza scadenza. Il più scelto.",
            "hu": "Tizenöt olvasás, lejárat nélkül. A legnépszerűbb.", "ru": "Пятнадцать чтений без срока действия. Самый популярный.",
            "uk": "П'ятнадцять читань без терміну дії. Найпопулярніший.", "es": "Quince lecturas, sin caducidad. La más elegida.",
        },
    },
    "pacchetto-50": {
        "nomi": {"en": "50 readings", "it": "50 letture", "hu": "50 olvasás", "ru": "50 чтений", "uk": "50 читань", "es": "50 lecturas"},
        "descrizioni": {
            "en": "Fifty readings, no expiry.", "it": "Cinquanta consulti, senza scadenza.",
            "hu": "Ötven olvasás, lejárat nélkül.", "ru": "Пятьдесят чтений без срока действия.",
            "uk": "П'ятдесят читань без терміну дії.", "es": "Cincuenta lecturas, sin caducidad.",
        },
    },
}

TRADUZIONI_MAZZI: Dict[str, Dict[str, Dict[str, str]]] = {
    "thoth": {
        "nomi": {"en": "Thoth Tarot", "it": "Tarocchi di Thoth", "hu": "Thoth Tarot", "ru": "Таро Тота",
                 "uk": "Таро Тота", "es": "Tarot de Thoth"},
        "descrizioni": {},
    },
}
