"""Le tabelle degli analytics (v8), definite dalla libreria `lanterna`.

Sono SQLAlchemy Core, non modelli ORM: la libreria è riusabile in altri progetti e non conosce la
nostra base dichiarativa. Registrarle nel `MetaData` di `Base` basta perché `create_all` dei test,
l'autogenerate e `test_migrazione` le vedano come tutte le altre. La migrazione chiama le funzioni
congelate della libreria (`lanterna.migrazioni.crea_v1`).
"""
from __future__ import annotations

from lanterna import registra_tabelle

from .base import Base

TABELLE = registra_tabelle(Base.metadata, prefisso="an_", fk_utenti="users.id")
