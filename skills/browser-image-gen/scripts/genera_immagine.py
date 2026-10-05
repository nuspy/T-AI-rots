"""Genera un'immagine su litmedia.ai (Text to Image) via browser automatizzato e la scarica
su disco. Ripiego gratuito/economico usato da crea-mazzo-tarocchi (illustrazioni dei mazzi) o su
richiesta esplicita dell'operatore; mai per il blog di TAROTS chat, le cui immagini passano solo da
tarots-blog-images (litmedia-skill).

Richiede una sessione gia' salvata: esegui prima login_una_tantum.py una volta sola.

Uso:
    python genera_immagine.py --model nano-banana --prompt "..." --output immagine.png
    python genera_immagine.py --model flux --prompt "..." --aspect 16:9 --resolution 1K --output img.png

Modelli supportati (nome esatto come appare nel selettore del sito):
    gpt-image, nano-banana, seedream, wan, flux, stable-diffusion
"""
import argparse
import json
import sys
import time
import urllib.request
from pathlib import Path
from typing import Optional

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

BASE_DIR = Path(__file__).parent.parent
STATO_FILE = BASE_DIR / "sessione_litmedia.json"
URL_GENERAZIONE = "https://www.litmedia.ai/app/litvideo/text-to-image/"
#: Ogni URL di immagine gia' scaricata con successo, di QUALUNQUE esecuzione passata di questo
#: script (persistente fra processi separati). Bug costoso osservato: una richiesta di rete per
#: una miniatura GIA' ESISTENTE nella cronologia (un refresh in background non collegato al nuovo
#: Create, causa esatta non nota) puo' arrivare subito dopo il click, prima della vera risposta
#: nuova - "la prima risposta mai vista in QUESTO processo" non basta, serve "mai vista in nessuna
#: esecuzione precedente".
URL_VISTI_FILE = BASE_DIR / "url_immagini_scaricate.json"

NOMI_MODELLO = {
    "gpt-image": "GPT Image",
    "nano-banana": "Nano Banana",
    "seedream": "Seedream",
    "wan": "Wan",
    "flux": "Flux",
    "stable-diffusion": "Stable Diffusion",
}

ASPETTI_VALIDI = {"1:1", "4:3", "3:4", "3:2", "2:3", "16:9", "9:16"}
RISOLUZIONI_VALIDE = {"1K", "2K", "4K"}
QUALITA_VALIDE = {"Low", "Medium", "High"}


def errore(msg: str) -> "NoReturn":
    print(f"errore: {msg}", file=sys.stderr)
    sys.exit(1)


def genera(model: str, prompt: str, aspect: str, resolution: str, quality: Optional[str], output: Path, timeout_s: int) -> None:
    if not STATO_FILE.exists():
        errore(f"nessuna sessione salvata ({STATO_FILE}). Esegui prima login_una_tantum.py")
    if model not in NOMI_MODELLO:
        errore(f"modello sconosciuto {model!r}. Validi: {', '.join(NOMI_MODELLO)}")
    if aspect not in ASPETTI_VALIDI:
        errore(f"aspect ratio sconosciuto {aspect!r}. Validi: {', '.join(sorted(ASPETTI_VALIDI))}")
    if resolution not in RISOLUZIONI_VALIDE:
        errore(f"risoluzione sconosciuta {resolution!r}. Valide: {', '.join(sorted(RISOLUZIONI_VALIDE))}")
    if quality is not None and quality not in QUALITA_VALIDE:
        errore(f"qualita' sconosciuta {quality!r}. Valide: {', '.join(sorted(QUALITA_VALIDE))}")

    nome_atteso = NOMI_MODELLO[model]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=str(STATO_FILE))
        page = context.new_page()
        page.goto(URL_GENERAZIONE, wait_until="networkidle")
        page.wait_for_timeout(1500)

        # --- Chiudi il banner promozionale in alto, SEMPRE, prima di qualunque altra cosa. ---
        # Il suo testo ("GPT Image 2.5 Flare Included", ecc.) condivide parole con i nomi dei
        # modelli veri nel selettore sottostante: se resta aperto, un get_by_text sul nome del
        # modello puo' cliccare QUESTO invece del vero elemento del menu (bug osservato: apriva la
        # pagina prezzi invece di selezionare il modello). Posizione fissa in alto a destra.
        try:
            page.mouse.click(1256, 22)
            page.wait_for_timeout(500)
        except Exception:
            pass  # banner assente in questa sessione: nessun problema

        # --- Assicurati di essere sul tab "Record" (cronologia personale), MAI "Inspiration" ---
        # Bug osservato: se il pannello e' rimasto su "Inspiration" (galleria pubblica di esempi,
        # a volte vecchia di mesi), il rilevamento del risultato per posizione/dimensione prende
        # un'immagine di ESEMPIO altrui, non il risultato vero - senza errore, solo il file sbagliato.
        try:
            page.get_by_text("Record", exact=True).first.click(timeout=3000)
            page.wait_for_timeout(500)
        except PWTimeout:
            print("nota: tab 'Record' non trovato/non cliccabile - se il risultato finale sembra "
                  "sbagliato, e' probabilmente questo", file=sys.stderr)

        # --- Prompt: riempito PER PRIMO, prima di qualunque click su modello/formato ---
        # Bug costoso osservato: con un prompt molto lungo (4000+ caratteri, tipico di una carta di
        # tarocchi con stile+identita'+scena concatenati), riempire il textarea DOPO aver gia'
        # cliccato modello/aspect/risoluzione/qualita' faceva bloccare lo script per minuti (nessun
        # errore, nessun progresso) - probabile interazione pesante fra il re-render della UI dopo
        # quei click e il re-render dovuto a un input cosi' grande. Riempito qui, da solo, e'
        # istantaneo (verificato: <0.02s anche per 4193 caratteri) e non ha nulla con cui interagire.
        prompt_box = page.locator("textarea").first
        prompt_box.click()
        prompt_box.fill(prompt)
        page.wait_for_timeout(300)

        # --- Selezione modello: SEMPRE esplicita, mai saltata ---
        # Deliberatamente NON si controlla se il modello richiesto sembra gia' quello attivo per
        # decidere di saltare la selezione: se in futuro il default del sito cambia, un salto
        # silenzioso genererebbe con un modello diverso da quello chiesto senza che nessuno se ne
        # accorga. Meglio il piccolo costo di riselezionarlo ogni volta, anche quando e' gia' quello
        # giusto.
        prompt_label = page.get_by_text("Prompt", exact=True).first
        box_prompt = prompt_label.bounding_box()
        if not box_prompt:
            errore("non trovo la label 'Prompt' sulla pagina - il sito potrebbe aver cambiato struttura")
        y_box_modello = box_prompt["y"] - 45

        page.mouse.click(box_prompt["x"] + 50, y_box_modello)
        page.wait_for_timeout(800)
        # Primo click: la FAMIGLIA nella lista di primo livello (GPT Image / Nano Banana /
        # Seedream / Wan / Flux / Stable Diffusion). A questo livello il nome cercato e'
        # ancora univoco (non compaiono "Nano Banana 2"/"Nano Banana Pro"), quindi un match
        # parziale e' sicuro.
        try:
            page.get_by_text(nome_atteso, exact=False).first.click(timeout=3000)
        except PWTimeout:
            errore(f"non trovo la famiglia '{nome_atteso}' nel selettore modello (il sito potrebbe averlo rinominato/rimosso)")
        page.wait_for_timeout(800)

        # Secondo click, SOLO se la famiglia si apre in varianti multiple (es. "Nano Banana"
        # apre un riquadro con "Nano Banana 2", "Nano Banana Pro" e la "Nano Banana" semplice):
        # qui un match parziale sbaglierebbe bersaglio (prenderebbe "Nano Banana 2" perche'
        # contiene la stringa "Nano Banana"), quindi va usato il testo ESATTO. Se dopo il primo
        # click il nome esatto e' gia' l'unico match visibile (famiglie senza sotto-varianti,
        # es. Flux), il secondo click e' semplicemente un altro modo di confermare la stessa
        # scelta e non fa danno.
        try:
            page.get_by_text(nome_atteso, exact=True).first.click(timeout=3000)
        except PWTimeout:
            pass  # famiglia senza flyout di varianti: il primo click aveva gia' selezionato tutto
        page.wait_for_timeout(800)

        if "text-to-image" not in page.url and "ai-image" not in page.url:
            errore(
                f"dopo la selezione del modello la pagina e' navigata via dal generatore (url ora: "
                f"{page.url}) - probabile click sul banner promozionale o su un link sbagliato"
            )

        def _seleziona_e_verifica(etichetta: str, nome_campo: str, obbligatorio: bool) -> None:
            """Clicca un bottone opzione (aspect/risoluzione/qualita') e VERIFICA che sia
            effettivamente selezionato dopo il click (classe 'bg-white', osservata su tutti i
            bottoni attivi di questo pannello), ritentando fino a 3 volte. Bug costoso osservato:
            il click a volte "non prende" senza sollevare nessun errore - il bottone resta
            visivamente non selezionato e la generazione parte con il default del modello invece
            del valore richiesto (es. una carta di tarocchi generata 3:2 invece di 9:16)."""
            elemento = page.get_by_text(etichetta, exact=True).first
            for tentativo in range(3):
                try:
                    elemento.click(timeout=2000)
                except PWTimeout:
                    if obbligatorio and tentativo == 2:
                        errore(f"{nome_campo} '{etichetta}' non trovato/non cliccabile nell'interfaccia")
                    continue
                page.wait_for_timeout(400)
                classe_padre = elemento.locator("xpath=..").get_attribute("class") or ""
                if "bg-white" in classe_padre:
                    return
            if obbligatorio:
                errore(
                    f"{nome_campo} '{etichetta}' cliccato {3} volte ma non risulta mai selezionato "
                    f"(nessuna classe 'bg-white' sul contenitore) - la generazione partirebbe con un "
                    f"valore diverso da quello richiesto, mi fermo invece di procedere con dati sbagliati"
                )
            print(f"nota: {nome_campo} '{etichetta}' non risulta selezionato dopo 3 tentativi, "
                  f"uso il default del modello", file=sys.stderr)

        # --- Aspect ratio (obbligatorio: un formato sbagliato e' un difetto grave del risultato) ---
        _seleziona_e_verifica(aspect, "aspect ratio", obbligatorio=True)

        # --- Risoluzione ---
        _seleziona_e_verifica(resolution, "risoluzione", obbligatorio=False)

        # --- Qualita' (non tutti i modelli la espongono: Low/Medium/High) ---
        if quality is not None:
            _seleziona_e_verifica(quality, "qualita'", obbligatorio=False)

        # --- Credits check (informativo, non blocca) ---
        try:
            crediti_testo = page.get_by_text("Credits Required", exact=False).first.inner_text()
            print(f"nota: {crediti_testo}", file=sys.stderr)
        except Exception:
            pass

        # --- Cattura l'URL del risultato dalla RETE, non dal DOM ---
        # Quattro tentativi precedenti (in ordine) hanno provato a indovinare "qual e' l'immagine
        # giusta" guardando la pagina: dimensione+posizione, frammento del prompt, testo
        # "Processing" (sparisce a fine generazione, rompendo il locator), data odierna (gia'
        # presente in pagina da un test precedente, quindi ".first" post-click non garantisce che
        # sia la voce NUOVA). Tutti fragili per lo stesso motivo di fondo: il DOM di
        # un'interfaccia web non e' pensato per essere interrogato in modo deterministico da uno
        # script. La rete si': il browser stesso deve ricevere l'URL dell'immagine in una risposta
        # HTTP per poterla mostrare, e quella risposta e' univoca per QUESTA richiesta, non
        # condivisa con nessun'altra generazione precedente.
        # Bug costoso osservato ANCHE con l'intercettazione di rete: un URL identico a quello di un
        # test precedente, completamente scollegato dal prompt appena inviato, e' ricomparso come
        # "prima risposta nuova" - quasi certamente un asset statico dell'interfaccia (l'avatar
        # dell'account nella barra di navigazione, un'icona) che condivide dominio ed estensione con
        # le immagini generate ma e' minuscolo rispetto a un vero risultato. Si scartano quindi le
        # risposte sotto una soglia di dimensione plausibile per un'immagine generata reale.
        # Bug costoso osservato ANCHE con l'intercettazione di rete: una risposta per un'immagine
        # GIA' ESISTENTE nella cronologia (causa esatta non nota - forse un refresh in background
        # di una miniatura visibile, scollegato dal Create appena cliccato) puo' arrivare prima
        # della vera risposta nuova. "La prima mai vista in QUESTO processo" non basta: serve "mai
        # vista in NESSUNA esecuzione precedente di questo script" - da qui l'elenco persistente.
        # Il sito ha cambiato il dominio da cui serve le immagini generate almeno una volta
        # (litvid.org -> resource.soulvid.ai, osservato il 2026-09-30, probabile infrastruttura
        # condivisa non documentata): un elenco invece di un singolo dominio assorbe il prossimo
        # cambio senza dover toccare di nuovo lo script — aggiungere qui il nuovo se il messaggio
        # di errore qui sotto si ripete con un dominio non ancora in elenco.
        DOMINI_RISULTATI = ("litvid.org", "resource.soulvid.ai")
        estensioni_immagine = (".png", ".jpg", ".jpeg", ".webp")
        # Bug costoso osservato: una risposta genuinamente MAI VISTA PRIMA, sopra i 50 KB, si e'
        # rivelata comunque sbagliata - probabile miniatura/anteprima di qualcos'altro sulla pagina,
        # non il risultato a piena risoluzione (i risultati reali osservati finora vanno da ~100 KB
        # a ~2 MB). Soglia alzata di conseguenza.
        DIMENSIONE_MINIMA_BYTE = 150_000
        try:
            url_gia_visti = set(json.loads(URL_VISTI_FILE.read_text(encoding="utf-8"))) if URL_VISTI_FILE.exists() else set()
        except (json.JSONDecodeError, OSError):
            url_gia_visti = set()

        url_nuovi: list[str] = []

        def _on_response(risposta):
            u = risposta.url
            if not any(d in u for d in DOMINI_RISULTATI) or not u.lower().split("?")[0].endswith(estensioni_immagine):
                return
            if u in url_gia_visti or u in url_nuovi:
                return  # gia' vista in un'esecuzione passata (o duplicato nella stessa risposta)
            try:
                lunghezza = int(risposta.headers.get("content-length", "0"))
            except (TypeError, ValueError):
                lunghezza = 0
            if lunghezza and lunghezza < DIMENSIONE_MINIMA_BYTE:
                return  # troppo piccola per essere un'immagine generata reale (probabile avatar/icona)
            url_nuovi.append(u)

        page.on("response", _on_response)

        # Bug costoso osservato (2026-09-29): il sito puo' rifiutare la richiesta di generazione
        # SENZA nessun segnale visibile in pagina (nessun toast rimasto a schermo, nessuna card
        # "Processing" mai creata) - la generazione semplicemente non parte mai, e senza questo
        # controllo lo script aspetta l'intero timeout (anche 300s) prima di fallire con un
        # messaggio generico "nessuna immagine trovata", nascondendo la vera causa. L'endpoint
        # `do-image` risponde comunque con HTTP 200 anche per un rifiuto: l'esito vero e' nel
        # campo `code`/`msg` del corpo JSON (osservato: {"code":1005,"msg":"Create failed,
        # contains sensitive prompt"} per un prompt con parole ritenute sensibili, anche solo nel
        # campo "Avoid"/negative prompt).
        rifiuto_server: list[str] = []

        def _on_do_image(risposta):
            if risposta.request.method != "POST" or "do-image" not in risposta.url:
                return
            try:
                corpo = risposta.json()
            except Exception:
                return
            codice = corpo.get("code")
            if codice not in (200, None):
                rifiuto_server.append(str(corpo.get("msg", corpo)))

        page.on("response", _on_do_image)

        page.get_by_role("button", name="Create", exact=True).click()

        # Il rifiuto arriva come risposta HTTP alla richiesta appena inviata: pochi secondi bastano,
        # molto meno del tempo di una generazione vera (30-90s).
        page.wait_for_timeout(4000)
        if rifiuto_server:
            page.remove_listener("response", _on_response)
            page.remove_listener("response", _on_do_image)
            errore(f"il sito ha rifiutato la generazione: {rifiuto_server[0]}")

        # Bug costoso osservato ANCHE cosi': la PRIMA risposta nuova che arriva puo' essere un
        # risultato ORFANO di un tentativo precedente (mai scaricato correttamente allora per un
        # bug gia' risolto, ma rimasto nella cronologia del sito) la cui immagine viene ri-richiesta
        # dalla pagina per qualche motivo subito dopo aver cliccato Create - scollegato dalla vera
        # generazione, che richiede secondi/minuti reali di elaborazione e quindi arriva DOPO.
        # Si aspetta percio' che la scritta "Processing" sparisca dalla pagina (segnale che la
        # generazione vera e' finita) continuando a raccogliere URL nel frattempo, poi si prende
        # l'ULTIMO arrivato fino a quel momento - quello temporalmente piu' vicino al vero
        # completamento, non il primo rumore di fondo.
        attesa = 0
        intervallo = 10
        while attesa < timeout_s:
            page.wait_for_timeout(intervallo * 1000)
            attesa += intervallo
            if page.get_by_text("Processing", exact=False).count() == 0 and url_nuovi:
                break

        page.wait_for_timeout(2000)  # margine per l'ultima risposta di rete in transito
        page.remove_listener("response", _on_response)
        page.remove_listener("response", _on_do_image)

        if not url_nuovi:
            errore(
                f"timeout dopo {timeout_s}s: nessuna risposta di rete con un'immagine MAI VISTA PRIMA da "
                f"{DOMINI_RISULTATI} e' arrivata dopo il click su Create - il sito potrebbe aver "
                f"rifiutato la richiesta (credito insufficiente, prompt non valido, manutenzione) o "
                f"servire le immagini da un dominio diverso ora"
            )

        src = url_nuovi[-1]
        url_gia_visti.add(src)
        try:
            URL_VISTI_FILE.write_text(json.dumps(sorted(url_gia_visti)), encoding="utf-8")
        except OSError:
            pass  # non bloccante: solo un ottimizzazione per le prossime esecuzioni

        if src.startswith("//"):
            src = "https:" + src
        elif src.startswith("/"):
            src = "https://www.litmedia.ai" + src

        print(f"URL immagine generata: {src}", file=sys.stderr)

        # --- Download ---
        output.parent.mkdir(parents=True, exist_ok=True)
        cookies = context.cookies()
        opener = urllib.request.build_opener()
        opener.addheaders = [("User-Agent", "Mozilla/5.0")]
        with opener.open(src, timeout=30) as risposta, open(output, "wb") as f:
            contenuto = risposta.read()
            f.write(contenuto)

        # Verifica minima: e' un'immagine raster vera, non una pagina di errore/icona
        FIRME = {
            b"\x89PNG\r\n\x1a\n": "PNG",
            b"\xff\xd8\xff": "JPEG",
            b"RIFF": "WebP/RIFF",
            b"GIF8": "GIF",
        }
        formato = next((nome for firma, nome in FIRME.items() if contenuto.startswith(firma)), None)
        if not formato or len(contenuto) < 5000:
            errore(
                f"il file scaricato ({len(contenuto)} byte) non sembra un'immagine raster valida "
                f"(nessuna firma PNG/JPEG/WebP/GIF riconosciuta) - probabile placeholder/icona, non il risultato vero"
            )

        print(f"Immagine salvata in: {output} ({formato}, {len(contenuto)} byte)")
        browser.close()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", required=True, choices=list(NOMI_MODELLO))
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--aspect", default="16:9")
    ap.add_argument("--resolution", default="1K")
    ap.add_argument("--quality", default=None, choices=sorted(QUALITA_VALIDE), help="Low/Medium/High, se il modello la espone")
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--timeout", type=int, default=180, help="secondi massimi di attesa del risultato")
    args = ap.parse_args()

    genera(args.model, args.prompt, args.aspect, args.resolution, args.quality, args.output, args.timeout)


if __name__ == "__main__":
    main()
