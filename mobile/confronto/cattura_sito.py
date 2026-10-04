"""Le catture del sito per il confronto con l'app (mobile/confronto/).

Fotografa la versione mobile del sito locale (http://localhost:3000, Edge) alle stesse misure dei golden test
dell'app (360×800, 390×844, iPad 1024×1366), schermata per schermata, **con gli stessi dati**: le chiamate del sito
all'API (`--api`, quella che il sito usa) che hanno una fixture nell'elenco `confronto/schermate.json` ricevono la
stessa risposta che ricevono i golden test (Playwright `route.fulfill`); le altre vanno all'API vera. Poi scrive il
rapporto affiancato (`rapporto.html`) con le immagini dell'app (`test/golden/goldens/`).

    python confronto\\cattura_sito.py [--sito http://localhost:3000] [--api http://localhost:8100] [--solo nome,…]

Il banner dei consensi del sito si nasconde nelle catture (l'app li chiede una volta al primo avvio); la barra
dell'oracolo resta (c'è anche nell'app). Misura anche, in tutte le lingue, se la testata del sito sta su una riga da
320 a 430 px (lo stesso controllo del test `testata su una riga` dell'app).

`schermate.json` e `rete/<nome>.json` li scrive `flutter test tool/registra_rete_test.dart` (le risposte che ogni
golden riceve davvero): `{"comuni": {…}, "schermate": [voci]}`, ogni voce
    {"nome": "carte", "titolo": "Le carte", "rotta": "/cards", "golden": "carte_{w}.png",
     "rete": "confronto/rete/carte.json", "misure": [360, 390, 1024], "storage": {chiave: valore}, "note": "…"}
e `rete/<nome>.json` è `{"GET /cards": {"stato": 200, "json": …}, …}` (`METODO /percorso`, senza query; `*` alla
fine vale per un prefisso). Attenzione: le pagine che il sito scrive sul server (carte, stese, diario) leggono l'API
dal server di Next, che Playwright non vede: lì i dati sono quelli dell'API vera, gli stessi da cui vengono le
fixture.
"""
from __future__ import annotations

import argparse
import html
import json
import shutil
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright

QUI = Path(__file__).resolve().parent
MOBILE = QUI.parent
CATTURE = QUI / "catture"
GOLDEN = MOBILE / "test" / "golden" / "goldens"
MISURE = {360: 800, 390: 844, 1024: 1366}
LINGUE_TESTATA = ["en", "it", "hu", "ru", "uk", "es"]
TUTTE = ["it", "hu", "en", "de", "ru", "uk", "fr", "es", "pt", "ro", "pl", "zh", "hi", "ko", "ar"]
NASCONDI = (
    ".cookie, .cookie-categorie, .skip, nextjs-portal { display: none !important; } "
    "* { animation: none !important; transition: none !important; caret-color: transparent !important; }"
)


def percorso_sito(rotta: str) -> str:
    """La rotta dell'app → l'indirizzo inglese del sito (solo la carta del giorno ha un nome diverso)."""
    return rotta.replace("/daily-card", "/card-of-the-day", 1) if rotta.startswith("/daily-card") else rotta


def apri(browser, w: int, h: int, lingua: str, archivio: dict | None = None):
    contesto = browser.new_context(
        viewport={"width": w, "height": h}, device_scale_factor=1, is_mobile=True, has_touch=True,
        locale="it-IT" if lingua == "it" else "en-GB",
    )
    # La lingua scelta, il banner della prova chiuso solo se la voce lo chiede, il tema dell'oracolo fermo (il primo,
    # come nei test dell'app).
    valori = {"lingua": lingua, **(archivio or {})}
    contesto.add_init_script(
        f"try {{ const v = {json.dumps(valori)}; for (const k in v) localStorage.setItem(k, v[k]); }} catch (e) {{}}"
        "Math.random = () => 0;"
    )
    return contesto


def instrada(contesto, api: str, fixture: dict) -> None:
    """Le chiamate all'API con una fixture ricevono la fixture; le altre passano."""
    base = urlsplit(api)

    def gestisci(route):
        u = urlsplit(route.request.url)
        if (u.scheme, u.netloc) != (base.scheme, base.netloc):
            route.continue_()
            return
        chiave = f"{route.request.method} {u.path}"
        voce = fixture.get(chiave)
        if voce is None:
            voce = next((v for k, v in fixture.items() if k.endswith("*") and chiave.startswith(k[:-1])), None)
        if voce is None:
            route.continue_()
            return
        corpo, stato = json.dumps(voce.get("json")), voce.get("stato", 200)
        route.fulfill(status=stato, body=corpo, content_type="application/json",
                      headers={"access-control-allow-origin": route.request.headers.get("origin", "*"),
                               "access-control-allow-credentials": "true"})

    contesto.route("**/*", gestisci)


def vai(pagina, url: str) -> None:
    # Il sito in sviluppo si ricarica da solo quando un file cambia (Fast Refresh): si riprova un paio di volte.
    for tentativo in range(3):
        try:
            _vai(pagina, url)
            return
        except Exception:  # noqa: BLE001 — una navigazione a metà: si ricomincia
            if tentativo == 2:
                raise
            pagina.wait_for_timeout(2000)


def _vai(pagina, url: str) -> None:
    pagina.goto(url, wait_until="networkidle")
    pagina.add_style_tag(content=NASCONDI)
    pagina.evaluate("document.fonts.ready")
    # Le immagini `loading="lazy"` arrivano solo vicino allo schermo: si scorre tutta la pagina e si torna su.
    pagina.evaluate(
        "async () => { for (let y = 0; y < document.body.scrollHeight; y += 400) {"
        " window.scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } window.scrollTo(0, 0); }"
    )
    pagina.wait_for_load_state("networkidle")
    pagina.wait_for_timeout(600)


def carica_schermate() -> list[dict]:
    """Le voci, ciascuna con le fixture comuni (l'oracolo, il banner della prova…) sotto le sue."""
    dati = json.loads((QUI / "schermate.json").read_text(encoding="utf-8"))
    voci = []
    for s in dati["schermate"]:
        rete = json.loads((MOBILE / s["rete"]).read_text(encoding="utf-8")) if s.get("rete") else {}
        voci.append({**s, "fixture": {**dati.get("comuni", {}), **rete}})
    return voci


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sito", default="http://localhost:3000")
    parser.add_argument("--api", default="http://localhost:8100")
    parser.add_argument("--solo", default="", help="solo queste voci (nomi separati da virgole)")
    parser.add_argument("--senza-testata", action="store_true", help="salta la misura della testata in 15 lingue")
    args = parser.parse_args()
    sito = args.sito.rstrip("/")
    solo = {s for s in args.solo.split(",") if s}
    schermate = [s for s in carica_schermate() if not solo or s["nome"] in solo]
    (CATTURE / "sito").mkdir(parents=True, exist_ok=True)
    (CATTURE / "app").mkdir(parents=True, exist_ok=True)
    misure_testata_file = CATTURE / "testata_sito.json"
    misure_testata = json.loads(misure_testata_file.read_text(encoding="utf-8")) if misure_testata_file.exists() else {}
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge")
        for s in schermate:
            for w in s.get("misure", list(MISURE)):
                contesto = apri(browser, w, MISURE[w], s.get("lingua", "en"), s.get("storage"))
                instrada(contesto, args.api, s.get("fixture", {}))
                pagina = contesto.new_page()
                vai(pagina, sito + percorso_sito(s["rotta"]))
                for passo in s.get("passi", []):
                    # Un tocco prima della cattura (aprire un dialogo, l'oracolo…): un selettore CSS o `testo=…`.
                    pagina.locator(passo).first.click()
                    pagina.wait_for_timeout(500)
                destinazione = CATTURE / "sito" / s["golden"].format(w=w)
                if s.get("selettore"):
                    pagina.locator(s["selettore"]).first.screenshot(path=str(destinazione))
                else:
                    pagina.screenshot(path=str(destinazione), full_page=s.get("pagina_intera", True))
                contesto.close()
        if not args.senza_testata:
            for w in (320, 360, 390, 430):
                for lingua in TUTTE:
                    contesto = apri(browser, w, 800, lingua)
                    pagina = contesto.new_page()
                    vai(pagina, sito + "/card-of-the-day")
                    misure_testata[f"{w} {lingua}"] = pagina.evaluate(
                        "() => { const h = document.querySelector('header.site-header');"
                        " return {altezza: h.offsetHeight, contenuto: h.scrollWidth, finestra: h.clientWidth}; }"
                    )
                    contesto.close()
        browser.close()
    misure_testata_file.write_text(json.dumps(misure_testata, indent=1), encoding="utf-8")
    for f in GOLDEN.glob("*.png"):
        shutil.copy(f, CATTURE / "app" / f.name)
    scrivi_rapporto(carica_schermate(), misure_testata)


def scrivi_rapporto(schermate: list[dict], misure_testata: dict) -> None:
    blocchi = []
    for s in schermate:
        for w in s.get("misure", list(MISURE)):
            f = s["golden"].format(w=w)
            titolo = f"{s['titolo']} — {w} px"
            nota = f"<p class=\"nota\">{html.escape(s['note'])}</p>" if s.get("note") else ""
            blocchi.append(
                f"""<section><h2>{html.escape(titolo)}</h2>{nota}<div class="coppia">
<figure><figcaption>Sito (Edge)</figcaption><a href="catture/sito/{f}"><img src="catture/sito/{f}" alt="sito {html.escape(titolo)}" loading="lazy"></a></figure>
<figure><figcaption>App (Flutter)</figcaption><a href="catture/app/{f}"><img src="catture/app/{f}" alt="app {html.escape(titolo)}" loading="lazy"></a></figure>
</div></section>"""
            )
    fuori = [k for k, v in misure_testata.items() if v["contenuto"] > v["finestra"] + 1 or v["altezza"] > 60]
    indice = "".join(f"<li>{html.escape(s['titolo'])}</li>" for s in schermate)
    (QUI / "rapporto.html").write_text(
        f"""<!doctype html>
<html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Confronto sito e app</title>
<style>
:root {{ --carta: #f4efe5; --inchiostro: #20162b; --prugna: #3c1846; --ottone: #b28336; }}
body {{ margin: 0; padding: 16px; background: var(--carta); color: var(--inchiostro); font: 16px/1.6 system-ui, sans-serif; }}
h1 {{ font-family: Georgia, serif; font-weight: 400; color: var(--prugna); }}
section {{ margin: 24px 0; padding-top: 12px; border-top: 2px solid var(--ottone); }}
h2 {{ font-size: 1.1rem; }}
.coppia {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; align-items: start; }}
figure {{ margin: 0; min-width: 0; }} figcaption {{ font-size: .85rem; color: #55455d; }}
img {{ max-width: 100%; height: auto; border: 1px solid rgba(60,24,70,.2); background: #fff; }}
.nota {{ max-width: 70ch; }}
@media (max-width: 560px) {{ .coppia {{ grid-template-columns: 1fr; }} }}
</style></head><body>
<h1>Il sito e l'app, affiancati</h1>
<p class="nota">A sinistra il sito locale in Edge, a destra l'app nei golden test, alle stesse misure (1 px = 1 punto),
con gli stessi dati: le risposte dell'API che i golden leggono dalle fixture il sito le riceve uguali (Playwright).
Nel sito è nascosto il banner dei consensi (l'app li chiede al primo avvio). Le pagine sono intere: la barra
dell'oracolo, ferma in fondo allo schermo, nel sito compare a metà cattura e nell'app in fondo.
Testata del sito che esce dalla riga (320–430 px, 15 lingue): {html.escape(", ".join(fuori) or "nessuna")}.</p>
<ul class="nota">{indice}</ul>
{"".join(blocchi)}
</body></html>
""",
        encoding="utf-8",
    )
    print(f"Rapporto: {QUI / 'rapporto.html'}")


if __name__ == "__main__":
    main()
