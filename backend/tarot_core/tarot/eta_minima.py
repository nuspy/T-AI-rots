"""L'età minima per usare TAROTS chat, per paese (GDPR, Fase 1).

**Da dove vengono i numeri.** L'art. 8 del GDPR fissa a 16 anni l'età sotto la quale, per i servizi della società
dell'informazione offerti direttamente a un minore, serve il consenso di chi ne ha la responsabilità genitoriale, e
lascia agli Stati membri di abbassarla fino a 13. I paesi che l'operatore ha scelto di distinguere:

- **Italia, 14 anni** — art. 2-quinquies del Codice privacy (d.lgs. 196/2003, introdotto dal d.lgs. 101/2018);
- **Spagna, 14 anni** — art. 7 della Ley Orgánica 3/2018 (LOPDGDD);
- **Francia, 15 anni** — art. 45 della loi n° 78-17 «Informatique et Libertés» (modificata dalla loi 2018-493);
- **tutti gli altri, 16 anni** — il valore dell'art. 8.1. Dove la legge nazionale scende sotto i 16 (per esempio 13
  in Belgio, Danimarca, Svezia, Portogallo; 14 in Austria) restare a 16 è più prudente, non meno: si chiede di più,
  mai di meno. Fuori dall'Unione (paese sconosciuto compreso) vale lo stesso 16.

Non è consulenza legale: i valori vanno confermati dal consulente privacy (`docs/privacy/dpia.md`). Il servizio
comprende acquisti e contenuti sulla sfera intima: se il consulente indicasse una soglia più alta (per esempio 18
anni), basta cambiare `PREDEFINITA` e `PER_PAESE` qui; chi ha già confermato un'età più bassa lo rivede chiedere
(`da_confermare`).

**Come si usa.** Il sito chiede al primo accesso «ho almeno N anni» (N per il paese del profilo, o stimato dall'IP);
la conferma si salva sull'utente (`User.eta_confermata_il`, `eta_confermata_anni`) con la prova in
`consensi_storico`. Senza conferma niente letture né chat; una data di nascita nel profilo che dice meno anni del
minimo vale più di una casella spuntata.
"""
from __future__ import annotations

from datetime import date
from typing import Any, Optional

#: Il minimo dove non c'è una regola nazionale più bassa che l'operatore abbia scelto di seguire.
PREDEFINITA = 16

#: Paese ISO 3166-1 alpha-2 → anni.
PER_PAESE = {
    "IT": 14,
    "ES": 14,
    "FR": 15,
}


def controllo_attivo() -> bool:
    """Se la conferma dell'età si pretende. Sempre vero in esercizio: è una funzione solo perché i test che non
    riguardano l'età la spengono in un punto (`tests/conftest.py`), invece di confermare l'età in ognuno."""
    return True


def anni_minimi(paese: Optional[str]) -> int:
    return PER_PAESE.get((paese or "").strip().upper(), PREDEFINITA)


def anni_compiuti(nascita: date, oggi: Optional[date] = None) -> int:
    oggi = oggi or date.today()
    return oggi.year - nascita.year - ((oggi.month, oggi.day) < (nascita.month, nascita.day))


def sotto_eta(nascita: Optional[date], paese: Optional[str], oggi: Optional[date] = None) -> bool:
    """Vero se la data di nascita dice meno anni del minimo del paese. Senza data: falso (decide la conferma)."""
    return controllo_attivo() and nascita is not None and anni_compiuti(nascita, oggi) < anni_minimi(paese)


def da_confermare(utente: Any) -> bool:
    """Vero se la persona non ha ancora confermato l'età minima del suo paese (o ne ha confermata una più bassa)."""
    if not controllo_attivo():
        return False
    if getattr(utente, "eta_confermata_il", None) is None:
        return True
    return (getattr(utente, "eta_confermata_anni", None) or 0) < anni_minimi(getattr(utente, "posizione_paese", None))


def paese_da_ip(ip: Optional[str]) -> Optional[str]:
    """Il paese stimato dall'IP con il database geografico locale (nessun servizio esterno, l'IP non si salva)."""
    if not ip:
        return None
    try:
        from lanterna.geo import luogo

        from ..settings import get_settings

        return luogo(get_settings().analytics_geo or None, ip).paese
    except Exception:  # noqa: BLE001 - senza paese vale il minimo predefinito, che è il più prudente
        return None


def stato_json(utente: Any) -> dict:
    """Ciò che il sito deve sapere: il minimo, se va confermato, e se la data di nascita lo esclude."""
    paese = getattr(utente, "posizione_paese", None)
    eta_il = getattr(utente, "eta_confermata_il", None)
    return {
        "anni": anni_minimi(paese),
        "paese": paese,
        "confermata_il": eta_il.isoformat() if eta_il else None,
        "da_confermare": da_confermare(utente),
        "sotto_eta": sotto_eta(getattr(utente, "birth_date", None), paese),
    }
