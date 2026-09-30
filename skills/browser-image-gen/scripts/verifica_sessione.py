"""Verifica rapida (headless) che la sessione salvata sia effettivamente autenticata su litmedia.ai."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

STATO_FILE = Path(__file__).parent.parent / "sessione_litmedia.json"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=str(STATO_FILE))
        page = context.new_page()
        page.goto("https://litmedia.ai/app/litvideo/ai-image/", wait_until="networkidle")
        page.wait_for_timeout(2000)

        html = page.content()
        testo = page.inner_text("body")

        # Indizi di login: crediti, avatar, "sign in"/"log in" assente
        indizi_loggato = any(k in testo.lower() for k in ["credit", "crediti", "upgrade", "my library", "account"])
        indizi_non_loggato = any(k in testo.lower() for k in ["sign in", "log in", "sign up", "create account"])

        print("Titolo pagina:", page.title())
        print("Contiene indizi di sessione autenticata (credit/account/library):", indizi_loggato)
        print("Contiene inviti al login (sign in/sign up):", indizi_non_loggato)
        print()
        print("--- primi 800 caratteri del testo visibile ---")
        print(testo[:800])

        page.screenshot(path=str(Path(__file__).parent.parent / "verifica_screenshot.png"), full_page=False)
        print("\nScreenshot salvato in verifica_screenshot.png")

        browser.close()


if __name__ == "__main__":
    sys.exit(main())
