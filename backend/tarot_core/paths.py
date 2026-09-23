"""Percorsi canonici del pacchetto.

Si ricavano dalla posizione di questo file, che è l'unica cosa che non
dipende da chi ha avviato il processo: un test lanciato da una sottocartella o
un container con un `WORKDIR` diverso trovano gli stessi file.
"""
from __future__ import annotations

import os
import pathlib

#: La cartella del pacchetto `tarot_core`.
PACKAGE_DIR = pathlib.Path(__file__).resolve().parent

#: La radice del backend.
PROJECT_ROOT = PACKAGE_DIR.parent

#: Dati di configurazione versionati insieme al codice: i guardrail.
DATA_DIR = pathlib.Path(
    os.getenv("TAROT_DATA_DIR", str(PROJECT_ROOT / "data"))
).resolve()

#: La base di conoscenza esoterica: mazzo, stese, dottrina. È ciò che il CAG
#: carica nel contesto, e per questo sta col codice e non nel database: cambia
#: con una revisione, non con un clic.
KNOWLEDGE_DIR = PACKAGE_DIR / "knowledge"
