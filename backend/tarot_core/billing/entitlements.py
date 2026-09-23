"""Cosa un utente può fare, e quanto.

Due domande distinte, e tenerle separate evita di confonderle quando una
lettura viene negata.

**I limiti** (`limits`) dicono *quanto*: letture al giorno comprese
nell'abbonamento. Si esauriscono e si rinnovano.

**I crediti sono un'altra cosa**, e stanno nel registro: sono la moneta, non
il permesso. Chi ha esaurito le letture del giorno può ancora leggere con un
credito comprato; chi non ha né l'una né l'altro va mandato a comprare.

**Senza abbonamento si ricade sul piano gratuito**, non sul nulla: la carta
del giorno resta di tutti.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from ..domain.billing_models import Plan, Subscription

logger = logging.getLogger(__name__)

#: Lo slug del piano che vale per chi non ha abbonamento.
PIANO_PREDEFINITO = "free"

LIMITI_BASE: Dict[str, int] = {
    #: Le letture comprese senza consumare crediti. Il gratuito non ne ha:
    #: ogni lettura costa un credito.
    "letture_al_giorno": 0,
}


@dataclass
class Diritti:
    """Ciò che un utente può fare, risolto."""

    piano: str = PIANO_PREDEFINITO
    nome: str = "Gratuito"
    limiti: Dict[str, int] = field(default_factory=lambda: dict(LIMITI_BASE))
    concessioni: Dict[str, Any] = field(default_factory=dict)
    #: Vero quando si stanno applicando i diritti base per assenza di
    #: abbonamento: «il tuo piano non lo comprende» e «non hai un piano»
    #: richiedono azioni diverse.
    predefiniti: bool = True

    def limite(self, nome: str) -> Optional[int]:
        """Il limite, o `None` se non ce n'è uno (illimitato)."""
        valore = self.limiti.get(nome)
        if valore is None or valore < 0:
            return None
        return valore

    def to_dict(self) -> Dict[str, Any]:
        return {
            "piano": self.piano,
            "nome": self.nome,
            "limiti": self.limiti,
            "concessioni": self.concessioni,
            "predefiniti": self.predefiniti,
        }


def diritti_da(
    abbonamento: Optional[Subscription], *, piano_base: Optional[Plan] = None,
) -> Diritti:
    """Risolve i diritti di un utente dal suo abbonamento.

    Un abbonamento sospeso o scaduto non dà nulla più del piano base.
    """
    if abbonamento is None or not abbonamento.vivo:
        return _dal_piano(piano_base) if piano_base else Diritti()
    return _dal_piano(abbonamento.plan, predefiniti=False)


def _dal_piano(piano: Optional[Plan], *, predefiniti: bool = True) -> Diritti:
    if piano is None:
        return Diritti()
    limiti = dict(LIMITI_BASE)
    limiti.update(piano.limits or {})
    return Diritti(
        piano=piano.slug,
        nome=piano.name,
        limiti=limiti,
        concessioni=dict(piano.entitlements or {}),
        predefiniti=predefiniti,
    )
