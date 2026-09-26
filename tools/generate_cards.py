#!/usr/bin/env python
"""Genera le carte con GPT Image 2 dal sito LitMedia (9:16, 2K, High) e le scarica in Cards/
col nome della chiave "file" di prompts.json.

Perché dal sito: l'API della skill LitMedia non supporta GPT Image 2 (i task falliscono),
quindi lo script pilota Chrome (Playwright) con un profilo dedicato, separato dal tuo.
Il rilevamento dei task e il download passano dallo storico dell'account (API della skill).

Come lavora:
  * lo storico dell'account è la fonte di verità: all'avvio le carte già generate con i
    parametri giusti ma non scaricate vengono SCARICATE (non rigenerate), quelle ancora in
    elaborazione vengono attese, solo le altre vengono generate;
  * invia carte finché il sito non rifiuta un invio con altre generazioni in corso: quello è
    il limite di generazioni contemporanee, che lo script memorizza. Quando un task finisce lo
    scarica e usa lo slot libero per la carta successiva;
  * se un invio viene rifiutato senza nulla in corso (login scaduto, sito cambiato) si ferma;
  * si può interrompere e rilanciare in qualsiasi momento senza pagare due volte.

Prima volta (una sola):   python generate_cards.py --login     # accedi, poi chiudi la finestra
Verifica del piano:       python generate_cards.py --dry-run
Prova con due carte:      python generate_cards.py --limit 2
Tutte le carte mancanti:  python generate_cards.py

Le carte già presenti in Cards/ (o nella radice del progetto, come spade-05.webp) vengono
saltate. Costo: ~30 crediti a carta.
"""
import argparse
import json
import os
import re
import sys
import time
from collections import Counter, deque
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import download_cards as dc  # noqa: E402  (normalizzazione prompt, storico, salvataggio immagini)

URL = "https://www.litmedia.ai/app/litvideo/text-to-image/"
MODEL, RATIO, RES, QUALITY = "GPT Image 2", "9:16", "2K", "High"
MODEL_ID = "14"  # image_model registrato dal sito per GPT Image 2
CREDITS_PER_CARD = 30
POLL_SECONDS = 10
SUBMIT_WAIT = 40  # secondi per vedere comparire il task nello storico dopo "Create"
WORKDIR = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "t-ai-rots-litmedia"
PROFILE = WORKDIR / "chrome-profile"  # cookie di LitMedia: resta fuori dal repo
ERROR_PNG = WORKDIR / "last-error.png"

STATE_JS = r"""() => {
  const btns = [...document.querySelectorAll('button')];
  const size = btns.filter(b => /^\d+:\d+$/.test(b.textContent.trim()) && /text-black/.test(b.className)).map(b => b.textContent.trim());
  const act = [...document.querySelectorAll('button.option-button-active')].map(b => b.textContent.trim());
  const model = [...document.querySelectorAll('span')].filter(e => e.children.length === 0 && /truncate/.test(e.className) && /^(GPT|Nano|Seedream|Wan|Flux|Stable)/.test(e.textContent.trim())).map(e => e.textContent.trim());
  const cr = [...document.querySelectorAll('body *')].filter(e => /Credits Required/.test(e.textContent) && e.textContent.length < 120).slice(-1)[0];
  return {size, act, model, credits: cr ? cr.textContent.trim() : null};
}"""
MESSAGES_JS = r"""() => [...new Set([...document.querySelectorAll('[role=alert], [class*=toast i], [class*=Toastify], [class*=notif i], [class*=modal i], [class*=dialog i]')]
  .filter(e => e.offsetParent !== null).map(e => e.innerText.trim().replace(/\s+/g, ' ')).filter(t => t && t.length < 300))].slice(0, 3).join(' | ')"""
CLOSE_POPUP_JS = r"""() => {
  const t = [...document.querySelectorAll('*')].find(e => e.children.length === 0 && /Daily Check-in Rewards/.test(e.textContent));
  let n = t;
  for (let i = 0; n && i < 8; i++) {
    n = n.parentElement;
    const c = n && n.querySelector('[class*=close i], [aria-label*=close i]');
    if (c) { c.click(); return true; }
  }
  return false;
}"""


BALANCE_JS = r"""() => {
  const c = [...document.querySelectorAll('body *')].filter(e => e.children.length === 0 && /^\d[\d,]*$/.test(e.textContent.trim()))
    .filter(e => { const r = e.getBoundingClientRect(); return r.y < 90 && r.x > 900; });
  return c.length ? parseInt(c[0].textContent.replace(/,/g, '')) : -1;
}"""
OVERLAYS_JS = r"""() => {
  const out = [];
  for (const e of document.querySelectorAll('body *')) {
    const s = getComputedStyle(e);
    if (s.position !== 'fixed' || s.display === 'none' || s.visibility === 'hidden') continue;
    const r = e.getBoundingClientRect();
    if (r.width < 200 || r.height < 200) continue;
    out.push(`${e.tagName}.${String(e.className).slice(0, 50)} ${Math.round(r.width)}x${Math.round(r.height)} | ${e.innerText.replace(/\s+/g, ' ').slice(0, 60)}`);
  }
  return out.slice(0, 5);
}"""


class Abort(Exception):
    """Errore che deve fermare tutta l'esecuzione, non solo la carta corrente."""


def log(msg):
    print(f"{datetime.now():%H:%M:%S} {msg}", flush=True)


class Site:
    """Chrome con profilo dedicato, aperto solo quando serve."""

    def __init__(self, headless):
        self.headless, self.pw, self.ctx, self.page = headless, None, None, None

    def open(self):
        if self.page:
            return self.page
        from playwright.sync_api import sync_playwright

        self.pw = sync_playwright().start()
        self.ctx = self.pw.chromium.launch_persistent_context(
            str(PROFILE), channel="chrome", headless=self.headless, viewport={"width": 1440, "height": 900})
        self.page = self.ctx.pages[0] if self.ctx.pages else self.ctx.new_page()
        self.page.goto(URL, wait_until="domcontentloaded")
        self.page.locator("textarea").first.wait_for(state="visible", timeout=60000)
        if not self.wait_balance():
            raise RuntimeError("saldo crediti non caricato nella pagina: login scaduto?")
        self.dismiss_popups()
        return self.page

    def wait_balance(self, timeout=30):
        """Senza il saldo caricato il sito crede di avere 0 crediti e mostra il popup di acquisto."""
        end = time.time() + timeout
        while time.time() < end:
            if self.page.evaluate(BALANCE_JS) > 0:
                return True
            self.page.wait_for_timeout(1000)
        return False

    def reload(self):
        self.page.goto(URL, wait_until="domcontentloaded")
        self.page.locator("textarea").first.wait_for(state="visible", timeout=60000)
        if not self.wait_balance():
            raise RuntimeError("saldo crediti non caricato dopo il ricaricamento")
        self.dismiss_popups()

    def overlays(self):
        try:
            return self.page.evaluate(OVERLAYS_JS)
        except Exception:
            return []

    def close(self):
        for closer in (getattr(self.ctx, "close", None), getattr(self.pw, "stop", None)):
            try:
                if closer:
                    closer()
            except Exception:
                pass
        self.page = None

    def dismiss_popups(self):
        self.page.keyboard.press("Escape")
        try:
            self.page.evaluate(CLOSE_POPUP_JS)
        except Exception:
            pass

    def click_button(self, text):
        loc = self.page.locator("button").filter(has_text=re.compile(rf"^\s*{re.escape(text)}\s*$")).first
        loc.scroll_into_view_if_needed()
        loc.click()

    def select_model(self):
        p = self.page
        p.locator("span.truncate", has_text=re.compile(r"^(GPT|Nano|Seedream|Wan|Flux|Stable)")).first.click()
        p.get_by_text("GPT Image", exact=True).first.click()
        p.get_by_text(MODEL, exact=True).last.click()
        p.keyboard.press("Escape")

    def apply_settings(self):
        st = {}
        for _ in range(3):
            st = self.page.evaluate(STATE_JS)
            if st["model"] != [MODEL]:
                self.select_model()
            for text, ok in ((RATIO, st["size"] == [RATIO]), (RES, RES in st["act"]), (QUALITY, QUALITY in st["act"])):
                if not ok:
                    self.click_button(text)
            self.page.wait_for_timeout(700)
            st = self.page.evaluate(STATE_JS)
            if st["model"] == [MODEL] and st["size"] == [RATIO] and RES in st["act"] and QUALITY in st["act"]:
                return st
        raise RuntimeError(f"impostazioni non applicate (serve {MODEL}, {RATIO}, {RES}, {QUALITY}): {st}")

    def submit(self, prompt):
        """Compila il modulo e preme Create. Ritorna (crediti mostrati, messaggi del sito)."""
        p = self.page
        self.dismiss_popups()
        st = self.apply_settings()
        area = p.locator("textarea").first
        area.click()
        area.fill(prompt)
        if area.input_value().replace("\r\n", "\n") != prompt.replace("\r\n", "\n"):
            raise RuntimeError("il testo nel campo prompt non coincide con quello della carta")
        # le schede "Inspiration" hanno pulsanti Create nascosti: quello vero è il grande del pannello
        p.locator("button.x-effect-btn__inner").filter(has_text=re.compile(r"^\s*Create\s*$")).first.click()
        seen = []
        for _ in range(6):  # i messaggi (toast) durano pochi secondi
            p.wait_for_timeout(1000)
            if p.get_by_text("Buy Now", exact=True).first.is_visible():
                overlays = self.overlays()
                p.keyboard.press("Escape")
                raise RuntimeError(f"il sito ha mostrato il popup di acquisto crediti (overlay: {overlays})")
            try:
                m = p.evaluate(MESSAGES_JS)
            except Exception:
                m = ""
            if m and m not in seen:
                seen.append(m)
        return st["credits"], " | ".join(seen)

    def screenshot(self):
        try:
            WORKDIR.mkdir(parents=True, exist_ok=True)
            self.page.screenshot(path=str(ERROR_PNG))
            return str(ERROR_PNG)
        except Exception:
            return None


def login():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        ctx = pw.chromium.launch_persistent_context(
            str(PROFILE), channel="chrome", headless=False, viewport={"width": 1440, "height": 900})
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(URL, wait_until="domcontentloaded")
        print("Accedi a LitMedia nella finestra aperta, poi CHIUDI la finestra per salvare la sessione.")
        ctx.wait_for_event("close", timeout=0)
    print("Sessione salvata.")


def history(client, size=50):
    return dc.fetch_history(client, dc.HISTORY_ENDPOINT, size=size, max_pages=1)


def balance(client):
    b = client.get("/user/credit/detail")
    return b.get("credit", b)


def params_got(rec):
    up = rec["user_params"]
    return (str(up.get("image_model")), up.get("ratio"), str(up.get("quality")).lower(), str(up.get("resolution")).lower())


PARAMS_WANT = (MODEL_ID, RATIO, RES.lower(), QUALITY.lower())


def index_history(rows, by_prompt):
    """Per ogni carta il task migliore con parametri giusti: riuscito > in corso > fallito."""
    rank = lambda r: (r["status"] == 1, r["status"] == 0, r["create_at"])
    best = {}
    for r in rows:
        card = by_prompt.get(dc.norm(r["user_params"].get("prompt", "")))
        if card and params_got(r) == PARAMS_WANT and (card["id"] not in best or rank(r) > rank(best[card["id"]])):
            best[card["id"]] = r
    return best


def find_new_task(client, prompt_norm, known, wait=SUBMIT_WAIT):
    end = time.time() + wait
    while True:
        for r in history(client, 20):
            if r["create_id"] not in known and dc.norm(r["user_params"].get("prompt", "")) == prompt_norm:
                return r
        if time.time() >= end:
            return None
        time.sleep(3)


def store(rec, card, out, quality):
    import io

    import requests
    from PIL import Image

    url = dc.image_url(rec)
    if not url:
        raise RuntimeError("task riuscito ma senza URL immagine")
    resp = requests.get(url, timeout=180)
    resp.raise_for_status()
    w, h = Image.open(io.BytesIO(resp.content)).size
    dest = out / card["file"]
    dc.save_image(resp.content, dest, quality)
    warn = "" if abs(w / h - 9 / 16) < 0.01 else "  ⚠ NON 9:16"
    return f"{w}x{h} {dest.stat().st_size / 1e6:.1f} MB{warn}"


def run(args, client, site, plan):
    """Ciclo principale. Ritorna (salvate, carte con errore)."""
    by_prompt = {dc.norm(c["prompt"]): c for c in plan}
    rows = dc.fetch_history(client, dc.HISTORY_ENDPOINT)
    known = {r["create_id"] for r in rows}
    best = {} if args.force else index_history(rows, by_prompt)

    queue, inflight, ready = deque(), {}, []
    for c in plan:
        r = best.get(c["id"])
        if r and r["status"] == 1:
            ready.append((c, r))
        elif r and r["status"] == 0:
            inflight[c["id"]] = {"card": c, "task": r["create_id"], "t": time.time()}
        else:
            queue.append(c)
    if args.limit:
        queue = deque(list(queue)[: args.limit])
    total = len(ready) + len(inflight) + len(queue)
    log(f"{total} carte: {len(ready)} già generate da scaricare, {len(inflight)} in elaborazione, "
        f"{len(queue)} da generare (~{len(queue) * CREDITS_PER_CARD} crediti)")

    saved, failed, fails, streak = 0, [], Counter(), 0
    cap = args.max_parallel or 10 ** 6
    start_balance = balance(client)

    def download(card, rec):
        nonlocal saved, streak
        info = store(rec, card, args.out, args.quality)
        saved += 1
        streak = 0
        log(f"[{saved}/{total}] {card['id']} -> {card['file']} {info}")

    for card, rec in ready:
        try:
            download(card, rec)
        except Exception as exc:
            failed.append(card["id"])
            log(f"{card['id']}: ERRORE nel download: {exc}")

    while queue or inflight:
        if inflight:
            byid = {r["create_id"]: r for r in history(client)}
            for cid, f in list(inflight.items()):
                r = byid.get(f["task"])
                if not r or r["status"] == 0:
                    if time.time() - f["t"] > args.timeout and not f.get("warned"):
                        f["warned"] = True
                        log(f"{cid}: task {f['task']} in elaborazione da oltre {args.timeout} s, continuo ad attendere")
                    continue
                del inflight[cid]
                if r["status"] == 1:
                    try:
                        download(f["card"], r)
                    except Exception as exc:
                        failed.append(cid)
                        log(f"{cid}: ERRORE nel download: {exc}")
                else:
                    fails[cid] += 1
                    log(f"{cid}: task {f['task']} fallito lato LitMedia (tentativo {fails[cid]})")
                    if fails[cid] < 2:
                        queue.appendleft(f["card"])
                    else:
                        failed.append(cid)

        if queue and len(inflight) < cap:
            card = queue.popleft()
            cid = card["id"]
            try:
                before = balance(client)
                site.open()
                credits, messages = site.submit(card["prompt"])
                rec = find_new_task(client, dc.norm(card["prompt"]), known)
                if rec:
                    if params_got(rec) != PARAMS_WANT:
                        raise Abort(f"il sito ha registrato parametri diversi (modello, formato, qualità, resolution): "
                                    f"{params_got(rec)} invece di {PARAMS_WANT}")
                    known.add(rec["create_id"])
                    inflight[cid] = {"card": card, "task": rec["create_id"], "t": time.time()}
                    streak = 0
                    log(f"{cid}: inviato, task {rec['create_id']} ({credits}); in corso {len(inflight)}")
                    time.sleep(3)
                    continue
                after = balance(client)
                if after != before:
                    raise Abort(f"invio rifiutato ma i crediti sono cambiati ({before} -> {after}): controlla l'account")
                queue.appendleft(card)
                if inflight:
                    cap = len(inflight)
                    log(f"limite raggiunto: {cap} generazioni contemporanee (messaggio del sito: {messages or 'nessuno'})."
                        f" Attendo che se ne liberi una")
                else:
                    streak += 1
                    if streak >= 2:
                        raise Abort(f"invio rifiutato senza nulla in corso: login scaduto o sito cambiato "
                                    f"(messaggio: {messages or 'nessuno'}; overlay: {site.overlays()}). Schermata: {site.screenshot()}")
                    log("invio rifiutato senza nulla in corso: ricarico la pagina e riprovo una volta")
                    site.reload()
            except Abort:
                raise
            except Exception as exc:
                streak += 1
                log(f"{cid}: ERRORE nell'invio: {exc}")
                try:
                    site.reload()
                except Exception:
                    pass
                if streak >= 2:
                    raise Abort(f"due errori di fila nell'invio, mi fermo (schermata: {site.screenshot()})")
                queue.appendleft(card)

        if inflight and (not queue or len(inflight) >= cap):
            time.sleep(POLL_SECONDS)

    log(f"crediti {start_balance} -> {balance(client)}")
    return saved, failed


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--login", action="store_true", help="apre Chrome (profilo dedicato) per accedere a LitMedia")
    ap.add_argument("--dry-run", action="store_true", help="mostra il piano senza generare")
    ap.add_argument("--yes", action="store_true", help="non chiedere conferma")
    ap.add_argument("--limit", type=int, default=0, help="genera al massimo N carte nuove")
    ap.add_argument("--max-parallel", type=int, default=0, help="massimo di generazioni contemporanee (default: quello del sito)")
    ap.add_argument("--only", nargs="*", default=[], metavar="ID")
    ap.add_argument("--skip", nargs="*", default=[], metavar="ID")
    ap.add_argument("--force", action="store_true", help="rigenera anche le carte già presenti (usare con --only)")
    ap.add_argument("--quality", type=int, default=None, help="qualità WebP con perdita; senza, lossless")
    ap.add_argument("--timeout", type=int, default=900, help="dopo quanti secondi segnalare un task lento")
    ap.add_argument("--headless", action="store_true")
    ap.add_argument("--prompts", type=Path, default=dc.DEFAULT_PROMPTS)
    ap.add_argument("--out", type=Path, default=dc.DEFAULT_OUT)
    ap.add_argument("--skill-dir", type=Path, default=dc.DEFAULT_SKILL)
    args = ap.parse_args()

    if args.login:
        return login()

    sys.path.insert(0, str(args.skill_dir / "scripts"))
    from shared.client import LitMediaClient

    cards = json.loads(args.prompts.read_text(encoding="utf-8"))["cards"]
    plan = []
    for c in cards:
        if c["id"] in args.skip or (args.only and c["id"] not in args.only):
            continue
        if not args.force and ((args.out / c["file"]).exists() or (dc.ROOT / c["file"]).exists()):
            continue
        plan.append(c)

    client = LitMediaClient()
    log(f"{len(plan)} carte senza immagine ({MODEL}, {RATIO}, {RES}, {QUALITY}), saldo {balance(client)}")
    if not plan:
        return
    if args.dry_run:
        print("carte:", " ".join(c["id"] for c in plan))
        return
    if not args.yes:
        if not sys.stdin.isatty():
            sys.exit("Serve conferma: rilancia con --yes (o da un terminale interattivo).")
        if input(f"Costo massimo circa {len(plan) * CREDITS_PER_CARD} crediti. Procedo? [s/N] ").strip().lower() not in ("s", "si", "sì", "y", "yes"):
            return

    args.out.mkdir(parents=True, exist_ok=True)
    site, t0 = Site(args.headless), time.time()
    saved, failed = 0, []
    try:
        saved, failed = run(args, client, site, plan)
    except KeyboardInterrupt:
        log("Interrotto: rilancia per riprendere (le generazioni in corso verranno scaricate).")
    except Abort as exc:
        log(f"STOP: {exc}")
        failed.append("stop")
    finally:
        site.close()
    log(f"finito: {saved} salvate, {len(failed)} errori {failed or ''}, {(time.time() - t0) / 60:.0f} min")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
