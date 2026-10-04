"""Il rinnovo del segreto di «Accedi con Apple» in Keycloak (v9, Fase 6).

    python -m tarot_core.tools.apple_segreto [--forza]

Lo lancia una volta al mese il CronJob `tarots-apple-segreto`: se il segreto scritto in Keycloak scade fra meno di
`RINNOVA_ENTRO` giorni (o non è mai stato scritto da qui), ne firma uno nuovo con la chiave .p8 caricata in console e
lo scrive nell'identity provider `apple` (`tarot/accesso_apple.py`). Con `--forza` lo rinnova comunque.

Senza la configurazione completa in console (Team ID, Key ID, Services ID, chiave) non fa niente ed esce con 0: Apple
non è ancora acceso, non è un guasto. Esce con 1 se la scrittura in Keycloak fallisce, così il Job risulta fallito in
`kubectl get jobs` (e c'è un mese di margine per accorgersene). Servono la chiave master (`TAROT_LLM_PROVIDER_KEY`,
per decifrare la .p8) e il segreto del client `tarot-api` (`manage-identity-providers`).
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys

from ..auth.keycloak_admin import KeycloakAdmin, KeycloakAdminError
from ..domain.repositories import AuditRepository
from ..domain.session import dispose_engine, get_session_factory
from ..settings import get_settings
from ..tarot import accesso_apple


async def giro(sessioni, kc: KeycloakAdmin, *, forza: bool = False) -> bool:
    """Un giro: vero se tutto è andato bene (anche quando non c'era niente da fare)."""
    async with sessioni() as session:
        r = await accesso_apple.riga(session)
        if not accesso_apple.completa(r):
            print("Accesso con Apple non configurato in console: niente da rinnovare")
            await session.commit()
            return True
        if not forza and not accesso_apple.da_rinnovare(r):
            print(f"Segreto di Apple valido fino al {r.segreto_scade_il:%Y-%m-%d}: nessun rinnovo")
            return True
        try:
            esito = await accesso_apple.applica(session, kc)
        except KeycloakAdminError as exc:
            await AuditRepository(session).record(
                action="accesso_social.apple_rinnovo", target_type="identity_provider", target_id="apple",
                after={"ok": False, "errore": str(exc)[:300]},
            )
            await session.commit()
            print(f"Rinnovo del segreto di Apple fallito: {exc}")
            return False
        await AuditRepository(session).record(
            action="accesso_social.apple_rinnovo", target_type="identity_provider", target_id="apple",
            after={"ok": True, "scade_il": esito["scade_il"]},
        )
        await session.commit()
        print(f"Segreto di Apple rinnovato: scade il {esito['scade_il'][:10]}")
        return True


async def _principale(forza: bool) -> bool:
    if not get_settings().keycloak_client_secret:
        print("TAROT_KEYCLOAK_CLIENT_SECRET non impostato: il segreto di Apple non si può scrivere in Keycloak")
        return False
    try:
        return await giro(get_session_factory(), KeycloakAdmin(), forza=forza)
    finally:
        await dispose_engine()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    argomenti = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    argomenti.add_argument("--forza", action="store_true", help="rinnova anche se il segreto è ancora lontano dalla scadenza")
    return 0 if asyncio.run(_principale(argomenti.parse_args().forza)) else 1


if __name__ == "__main__":
    sys.exit(main())
