"""Lo schema OpenAPI del backend per il test di contratto dell'app (`test/contratto_test.dart`).

Si genera dall'applicazione FastAPI senza avviarla (niente server, niente database): `app.openapi()` legge solo le
rotte e i modelli. Da lanciare con il Python del backend, dalla cartella `mobile/`:

    ..\\backend\\.venv\\Scripts\\python.exe tool\\genera_openapi.py

Scrive `test/fixtures/openapi.json`. Va rigenerato quando il backend cambia gli endpoint che l'app usa: il test di
contratto dice quali.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

QUI = Path(__file__).resolve().parent
BACKEND = QUI.parent.parent / "backend"
USCITA = QUI.parent / "test" / "fixtures" / "openapi.json"


def main() -> None:
    sys.path.insert(0, str(BACKEND))
    # Le impostazioni di sviluppo bastano: lo schema non dipende da segreti né da servizi esterni.
    os.environ.setdefault("TAROT_ENVIRONMENT", "dev")
    from tarot_core.api.app import create_app  # noqa: E402 (dopo il percorso del backend)

    schema = create_app().openapi()
    USCITA.parent.mkdir(parents=True, exist_ok=True)
    USCITA.write_text(json.dumps(schema, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Scritto {USCITA}: {len(schema.get('paths', {}))} percorsi")


if __name__ == "__main__":
    main()
