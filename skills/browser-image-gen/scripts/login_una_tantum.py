"""Login interattivo una tantum su litmedia.ai: salva la sessione (cookie + storage) su disco
perche' gli script successivi (headless, automatici) la riusino senza richiedere credenziali.

Niente input() da terminale (non arriverebbe all'utente reale): la finestra resta aperta per un
tempo fisso, poi salva comunque lo stato corrente (che include il login se fatto in tempo)."""
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

STATO_FILE = Path(__file__).parent.parent / "sessione_litmedia.json"
ATTESA_SECONDI = 180


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://litmedia.ai/app/litvideo/ai-image/")
        print(f"Finestra aperta. Hai {ATTESA_SECONDI} secondi per fare login.", flush=True)
        for rimasti in range(ATTESA_SECONDI, 0, -10):
            print(f"  ...{rimasti}s rimasti", flush=True)
            time.sleep(10)
        context.storage_state(path=str(STATO_FILE))
        print(f"Sessione salvata in: {STATO_FILE}", flush=True)
        browser.close()


if __name__ == "__main__":
    sys.exit(main())
