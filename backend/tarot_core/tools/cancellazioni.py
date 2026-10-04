"""Le cancellazioni degli account scadute (GDPR, Fase 1).

    python -m tarot_core.tools.cancellazioni

Lo lancia ogni notte il CronJob `tarots-cancellazioni`: ogni account la cui cancellazione è stata chiesta da più di
30 giorni (e non annullata) perde l'utente in Keycloak e i dati personali; la contabilità resta pseudonimizzata
(`tarot/cancellazione.py`). Un account per transazione: uno che fallisce (Keycloak irraggiungibile) si riprova la notte
dopo e non ferma gli altri. Esce con 1 se almeno uno è fallito, così il Job risulta fallito in `kubectl get jobs`.

Serve `TAROT_KEYCLOAK_CLIENT_SECRET` (l'account di servizio di `tarot-api` con `manage-users`): senza, non cancella
niente — cancellare i dati lasciando vivo l'utente in Keycloak gli farebbe ritrovare, rientrando, un account nuovo e
vuoto senza sapere perché.
"""
from __future__ import annotations

import asyncio
import logging
import sys

from ..auth.keycloak_admin import KeycloakAdmin
from ..domain.session import dispose_engine, get_session_factory
from ..settings import get_settings
from ..tarot.cancellazione import esegui_scadute


async def _giro() -> bool:
    if not get_settings().keycloak_client_secret:
        print("TAROT_KEYCLOAK_CLIENT_SECRET non impostato: nessuna cancellazione eseguita")
        return False
    try:
        esito = await esegui_scadute(get_session_factory(), KeycloakAdmin())
        print(f"cancellazioni eseguite: {len(esito['eseguite'])}; fallite: {len(esito['fallite'])}")
        return not esito["fallite"]
    finally:
        await dispose_engine()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    return 0 if asyncio.run(_giro()) else 1


if __name__ == "__main__":
    sys.exit(main())
