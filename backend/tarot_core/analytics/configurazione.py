"""La configurazione di `lanterna` per TAROTS chat, dalle impostazioni del backend."""
from __future__ import annotations

import hashlib
import hmac

from lanterna import ConfigLanterna

from ..settings import get_settings

SITO = "tarots"


def configurazione() -> ConfigLanterna:
    from ..configurazioni.segreti import sale_condivisione

    s = get_settings()
    # Il segreto dell'identificativo esteso deriva dal sale delle condivisioni (un segreto interno,
    # generato al primo avvio o preso dall'ambiente: `configurazioni/segreti.py`) con una separazione
    # di dominio: nessun segreto nuovo da gestire, e i due usi non producono mai lo stesso valore.
    segreto = hmac.new(sale_condivisione().encode("utf-8"), b"lanterna/esteso", hashlib.sha256).hexdigest()
    return ConfigLanterna(
        sito=SITO,
        dominio=s.analytics_dominio,
        segreto=segreto,
        ritenzione_mesi=s.analytics_ritenzione_mesi,
        percorso_geo=s.analytics_geo or None,
        esclusi=("/admin", "/api"),
    )
