"""Piani, pacchetti, abbonamenti, crediti.

I **limiti** dicono quante letture l'abbonamento comprende al giorno, i
**crediti** sono la moneta per tutte le altre. «Hai finito le letture di oggi»
e «non hai crediti» si risolvono in modi diversi, e vanno detti in modi
diversi.
"""
from .credits import CreditiInsufficienti, Movimento, RegistroCrediti
from .entitlements import Diritti, diritti_da
from .plans import BillingProvider, GestoreAbbonamenti, ProviderDiSviluppo

__all__ = [
    "BillingProvider",
    "CreditiInsufficienti",
    "Diritti",
    "GestoreAbbonamenti",
    "Movimento",
    "ProviderDiSviluppo",
    "RegistroCrediti",
    "diritti_da",
]
