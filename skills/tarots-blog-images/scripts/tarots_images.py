#!/usr/bin/env python3
"""tarots_images.py: redo the images of TAROTS chat blog articles (cover and inline) through the REST API (v1).

Standard library only (Python 3.8+), plus the separate `litmedia-skill` for generating pictures. Configuration comes
from the environment, or from a small local cache this tool manages — never from a command argument or a prompt:

    TAROTS_API_URL     the API base, e.g. https://tarots.chat/api   (https only; http is accepted for localhost)
    TAROTS_MEDIA_KEY   a `tk_live_...` key with the `blog:media` permission (console: Blog > Keys > "Change images")
    LITMEDIA_SKILL     optional: the litmedia-skill folder (default: ~/.claude/skills/litmedia-skill, then
                       ~/.agents/skills/litmedia-skill, then %LOCALAPPDATA%/hermes/skills/litmedia-skill)

The key is remembered in `~/.tarots-blog/media-credentials.json` (or `TAROTS_MEDIA_KEY_CACHE`), outside any
repository, the same way `tarots_blog.py` remembers its own. A `blog:media` key can touch **only images** — cover
and inline pictures — of any article, published or not; it cannot change text, SEO fields or status.

Commands (run `tarots_images.py <command> -h` for the options):

    key show|save|clear     the saved key: prefix and origin, save the one in TAROTS_MEDIA_KEY, or forget it
    list [--todo]           every article with its cover and inline images (--todo: not redone yet by this tool)
    show ID                 one article with its full text: read it before writing a prompt
    balance                 LitMedia credits left
    generate --prompt P --out FILE [--aspect 3:2] [--resolution 2K] [--budget N] [--dry-run]
                            one picture with Seedream 5.0 (checks the balance first; refuses card-spread prompts)
    cover ID FILE --alt TEXT [--dry-run]
                            replace the cover
    inline ID [--replace N FILE ALT] [--add AFTER_PARAGRAPH FILE ALT] [--remove N] [--dry-run]
                            replace, add or remove pictures inside the text (N = 0 for the first picture)
    progress                what this tool has already redone, with the prompts used

Exit codes: 0 ok · 2 usage · 4 the API or LitMedia refused (message printed) · 5 configuration missing or unsafe
· 6 budget or balance too low (nothing generated).

Every uploaded picture gets its list thumbnail automatically on the server: nothing to do for it here.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

EXIT_OK, EXIT_USAGE, EXIT_API, EXIT_CONFIG, EXIT_BUDGET = 0, 2, 4, 5, 6

MAX_IMAGE_BYTES = 8_000_000
IMAGE_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}

#: Seedream 5.0 on LitMedia: 2K or 4K (there is no 1K), 10 or 20 credits (checked 2026-09-30).
MODEL = "Seedream 5.0"
COST = {"2K": 10, "4K": 20}

HOME = Path.home()
CACHE_PATH = Path(os.environ["TAROTS_MEDIA_KEY_CACHE"]) if os.environ.get("TAROTS_MEDIA_KEY_CACHE") else HOME / ".tarots-blog" / "media-credentials.json"
PROGRESS_PATH = Path(os.environ["TAROTS_IMAGES_PROGRESS"]) if os.environ.get("TAROTS_IMAGES_PROGRESS") else HOME / ".tarots-blog" / "images-progress.json"
_noted = False

#: The problem this skill exists to fix: every cover was "tarot cards laid out on a table". A prompt that asks for
#: that again is refused (a single card as a small detail is fine: say "a single card").
SPREAD_PATTERNS = [
    r"\btarot spread\b", r"\bcard spread\b", r"\bspread of (?:tarot )?cards\b", r"\bcards? (?:laid|spread|arranged) (?:out )?on\b",
    r"\bcards on (?:a|the) (?:wooden )?table\b", r"\btable with (?:a )?(?:thoth-style )?(?:tarot )?(?:cards|spread)\b",
    r"\bcards? face (?:down|up)\b", r"\breading table\b", r"\bfan of cards\b", r"\bceltic cross layout\b",
]


class Failure(Exception):
    def __init__(self, message: str, code: int = EXIT_API):
        super().__init__(message)
        self.code = code


# ---- configuration and HTTP ------------------------------------------------------------------------------------


def _read_cache() -> Optional[Dict[str, str]]:
    try:
        data = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) and str(data.get("key", "")).startswith("tk_live_") else None


def _write_cache(base: str, key: str) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps({"url": base, "key": key}), encoding="utf-8")
    try:
        CACHE_PATH.chmod(0o600)  # best-effort: POSIX only
    except OSError:
        pass


def config() -> Dict[str, str]:
    """Env vars win when present; otherwise the saved key/URL. A different key than the saved one is never swapped in
    silently."""
    global _noted
    env_base = os.environ.get("TAROTS_API_URL", "").strip().rstrip("/")
    env_key = os.environ.get("TAROTS_MEDIA_KEY", "").strip()
    cached = _read_cache()
    if env_key and cached and cached.get("key") != env_key:
        raise Failure(
            f"A different key is already saved (prefix {cached['key'][:12]}...) than the one in TAROTS_MEDIA_KEY "
            f"(prefix {env_key[:12]}...). Run `key show` to compare, `key save` to replace the saved one, or unset "
            "TAROTS_MEDIA_KEY to keep the saved key.", EXIT_CONFIG,
        )
    if env_key:
        base, key = env_base, env_key
        if not cached and base:
            _write_cache(base, key)
            print(f"note: saved this key for reuse (prefix {key[:12]}...) in {CACHE_PATH}.", file=sys.stderr)
    elif cached:
        base, key = env_base or cached.get("url", ""), cached.get("key", "")
        if not _noted:
            print(f"note: using the saved key (prefix {key[:12]}...); set TAROTS_MEDIA_KEY to use another.", file=sys.stderr)
            _noted = True
    else:
        base, key = env_base, env_key
    if not base:
        raise Failure("TAROTS_API_URL is not set (for example https://tarots.chat/api).", EXIT_CONFIG)
    url = urllib.parse.urlparse(base)
    local = url.hostname in ("localhost", "127.0.0.1", "::1")
    if url.scheme != "https" and not (url.scheme == "http" and local):
        raise Failure("TAROTS_API_URL must be https (http only for localhost): the key would travel in clear text.", EXIT_CONFIG)
    if not key.startswith("tk_live_"):
        raise Failure("TAROTS_MEDIA_KEY is not set (and none is saved). Create a key with the «Change images» "
                      "(blog:media) permission in the console: Blog > Keys.", EXIT_CONFIG)
    return {"base": base, "key": key}


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """A redirect would forward the Authorization header to whatever host it points at: never follow one."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D401
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


def call(method: str, path: str, *, body: Any = None, raw: Optional[bytes] = None, content_type: Optional[str] = None,
         query: Optional[Dict[str, Any]] = None, timeout: int = 120) -> Any:
    cfg = config()
    url = f"{cfg['base']}/v1/blog{path}"
    if query:
        url += "?" + urllib.parse.urlencode({k: v for k, v in query.items() if v is not None})
    headers = {"Authorization": f"Bearer {cfg['key']}", "Accept": "application/json", "User-Agent": "tarots-blog-images/1.0"}
    data = None
    if raw is not None:
        data, headers["Content-Type"] = raw, content_type or "application/octet-stream"
    elif body is not None:
        data, headers["Content-Type"] = json.dumps(body).encode("utf-8"), "application/json"
    request = urllib.request.Request(url, data=data, method=method, headers=headers)
    for attempt in range(2 if method == "GET" else 1):
        try:
            with _OPENER.open(request, timeout=timeout) as response:
                payload = response.read()
                return json.loads(payload) if payload else None
        except urllib.error.HTTPError as exc:
            raise Failure(explain(exc)) from None
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            if attempt == 0 and method == "GET":
                time.sleep(2)
                continue
            raise Failure(f"Cannot reach the API ({getattr(exc, 'reason', exc)}). Check TAROTS_API_URL and the network.") from None
    return None  # pragma: no cover


def explain(exc: urllib.error.HTTPError) -> str:
    try:
        detail = json.loads(exc.read().decode("utf-8", "replace")).get("detail")
    except Exception:  # noqa: BLE001
        detail = None
    if isinstance(detail, (dict, list)):
        detail = json.dumps(detail, ensure_ascii=False)
    hints = {
        401: "The key was rejected: wrong or revoked. Create a new one in the console (Blog > Keys).",
        403: "This key lacks the «Change images» (blog:media) permission.",
        404: "Not found: wrong article id.",
        413: "The file is too large (8 MB at most).",
        415: "Unsupported file type: send PNG, JPEG or WebP.",
        429: "Rate limit reached. Wait, and do not retry in a loop.",
    }
    for code in (301, 302, 307, 308):
        hints[code] = "The server redirected the request. Point TAROTS_API_URL at the final address."
    hint = hints.get(exc.code, "")
    return f"HTTP {exc.code}" + (f": {detail}" if detail else "") + (f"\n  {hint}" if hint else "")


# ---- local progress (what was redone, with which prompt) ------------------------------------------------------


def _progress() -> Dict[str, Any]:
    try:
        data = json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _record(post_id: str, kind: str, entry: Dict[str, Any]) -> None:
    data = _progress()
    riga = data.setdefault(post_id, {"cover": None, "inline": []})
    entry = {**entry, "when": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
    if kind == "cover":
        riga["cover"] = entry
    else:
        riga["inline"].append(entry)
    PROGRESS_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROGRESS_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _prompt_of(path: str) -> Optional[str]:
    """`generate` writes the prompt next to the picture (`<file>.prompt.txt`): it goes in the progress record."""
    sidecar = Path(path + ".prompt.txt")
    return sidecar.read_text(encoding="utf-8").strip() if sidecar.exists() else None


# ---- LitMedia ------------------------------------------------------------------------------------------------


def litmedia_dir() -> Path:
    candidates = [os.environ.get("LITMEDIA_SKILL", "")]
    candidates += [str(HOME / ".claude" / "skills" / "litmedia-skill"), str(HOME / ".agents" / "skills" / "litmedia-skill")]
    if os.environ.get("LOCALAPPDATA"):
        candidates.append(str(Path(os.environ["LOCALAPPDATA"]) / "hermes" / "skills" / "litmedia-skill"))
    for c in candidates:
        if c and (Path(c) / "scripts" / "ai_image.py").exists():
            return Path(c)
    raise Failure("litmedia-skill not found. Install it, or set LITMEDIA_SKILL to its folder.", EXIT_CONFIG)


def _litmedia(script: str, args: List[str], timeout: int) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(litmedia_dir() / "scripts" / script), *args]
    try:
        return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired:
        raise Failure(f"LitMedia did not answer within {timeout}s. Run `balance` before trying again: do not resubmit blindly.") from None


def balance() -> int:
    done = _litmedia("user.py", ["--json", "-q", "credit"], timeout=60)
    try:
        return int(json.loads(done.stdout)["credit"])
    except (ValueError, KeyError, TypeError):
        raise Failure("Could not read the LitMedia balance:\n  " + (done.stderr or done.stdout).strip()[-400:]) from None


def spread_problem(prompt: str) -> Optional[str]:
    low = prompt.lower()
    for pattern in SPREAD_PATTERNS:
        m = re.search(pattern, low)
        if m:
            return m.group(0)
    return None


# ---- commands ------------------------------------------------------------------------------------------------


def cmd_key(a) -> int:
    cached = _read_cache()
    env_key = os.environ.get("TAROTS_MEDIA_KEY", "").strip()
    if a.action == "show":
        print(f"saved: {cached['key'][:12]}... for {cached.get('url')} ({CACHE_PATH})" if cached else "saved: none")
        print(f"TAROTS_MEDIA_KEY: {env_key[:12]}..." if env_key else "TAROTS_MEDIA_KEY: not set")
    elif a.action == "save":
        base = os.environ.get("TAROTS_API_URL", "").strip().rstrip("/") or (cached or {}).get("url", "")
        if not env_key.startswith("tk_live_") or not base:
            raise Failure("Set TAROTS_MEDIA_KEY (and TAROTS_API_URL the first time) to the key to save.", EXIT_CONFIG)
        _write_cache(base, env_key)
        print(f"saved {env_key[:12]}... in {CACHE_PATH}")
    else:
        try:
            CACHE_PATH.unlink()
        except FileNotFoundError:
            pass
        print("forgotten")
    return EXIT_OK


def _all_posts(status: Optional[str], lang: Optional[str]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    page = 1
    while True:
        data = call("GET", "/media-posts", query={"stato": status, "lang": lang, "pagina": page, "per_pagina": 100})
        out.extend(data["articoli"])
        if len(out) >= data["totale"] or not data["articoli"]:
            return out
        page += 1


STATUS = {"draft": "bozza", "published": "pubblicato", "archived": "archiviato"}


def cmd_list(a) -> int:
    posts = _all_posts(STATUS.get(a.status) if a.status else None, a.lang)
    done = _progress()
    if a.todo:
        posts = [p for p in posts if not (done.get(p["id"]) or {}).get("cover")]
    if a.json:
        print(json.dumps(posts, indent=2, ensure_ascii=False))
        return EXIT_OK
    for p in posts:
        redone = "redone" if (done.get(p["id"]) or {}).get("cover") else "todo  "
        cover = "cover" if p["copertina"] else "no cover"
        print(f"{p['id']}  {redone}  {p['stato']:<10} {p['lang']}  {cover:<8}  inline:{len(p['immagini_nel_testo'])}  {p['titolo']}")
        if p.get("parola_chiave"):
            print(f"{'':38}keyword: {p['parola_chiave']}")
    print(f"\n{len(posts)} article(s)")
    return EXIT_OK


def cmd_show(a) -> int:
    print(json.dumps(call("GET", f"/media-posts/{a.id}"), indent=2, ensure_ascii=False))
    return EXIT_OK


def cmd_balance(_a) -> int:
    print(f"LitMedia credits: {balance()}")
    return EXIT_OK


def cmd_generate(a) -> int:
    resolution = a.resolution.upper()
    if resolution not in COST:
        raise Failure(f"{MODEL} accepts --resolution 2K or 4K (there is no 1K).", EXIT_USAGE)
    problem = spread_problem(a.prompt)
    if problem and not a.allow_cards:
        raise Failure(
            f"The prompt asks for cards laid out on a table («{problem}»): that is exactly the repetitive picture this "
            "skill replaces. Write a different scene (see references/prompts.md). A single card as a small detail is "
            "fine; --allow-cards only if the operator asked for this very picture.", EXIT_USAGE,
        )
    cost = COST[resolution]
    out = Path(a.out)
    if out.suffix.lower() not in IMAGE_TYPES:
        raise Failure("--out must end in .jpg, .jpeg, .png or .webp", EXIT_USAGE)
    if a.dry_run:
        print(f"dry run: {MODEL}, {a.aspect}, {resolution}, {cost} credits, would be saved to {out}")
        print(f"prompt: {a.prompt}")
        return EXIT_OK
    credits = balance()
    if credits < cost or credits - cost < a.reserve:
        raise Failure(f"LitMedia balance {credits}: not enough for {cost} credits keeping a reserve of {a.reserve}.", EXIT_BUDGET)
    if a.budget is not None and a.budget < cost:
        raise Failure(f"The budget left for this run ({a.budget}) is below the cost of one picture ({cost}).", EXIT_BUDGET)
    with tempfile.TemporaryDirectory(prefix="tarots-img-") as tmp:
        done = _litmedia("ai_image.py", [
            "run", "--type", "text2image", "--model", MODEL, "--prompt", a.prompt, "--aspect-ratio", a.aspect,
            "--resolution", resolution, "--count", "1", "--output-dir", tmp, "--interval", "10",
        ], timeout=900)
        files = sorted(Path(tmp).glob("image_*"))
        if done.returncode != 0 or not files:
            raise Failure("LitMedia did not return a picture:\n  " + (done.stdout + done.stderr).strip()[-600:])
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(files[0]), out)
    Path(str(out) + ".prompt.txt").write_text(a.prompt, encoding="utf-8")
    print(f"saved {out} ({out.stat().st_size // 1024} KB), {cost} credits; balance now about {credits - cost}")
    return EXIT_OK


def _read_image(path: str) -> bytes:
    p = Path(path)
    kind = IMAGE_TYPES.get(p.suffix.lower())
    if not kind:
        raise Failure(f"{path}: send a PNG, JPEG or WebP file.", EXIT_USAGE)
    data = p.read_bytes()
    if len(data) > MAX_IMAGE_BYTES:
        raise Failure(f"{path}: larger than 8 MB.", EXIT_USAGE)
    return data


def upload(path: str) -> Dict[str, Any]:
    data = _read_image(path)
    return call("POST", "/media", raw=data, content_type=IMAGE_TYPES[Path(path).suffix.lower()])


def _check_alt(alt: str) -> str:
    alt = " ".join(alt.split())
    if len(alt) < 8:
        raise Failure("The alt text must describe the picture (8 characters at least).", EXIT_USAGE)
    if problem := spread_problem(alt):
        print(f"warning: the alt text mentions «{problem}»: does it really describe the new picture?", file=sys.stderr)
    return alt[:200]


def cmd_cover(a) -> int:
    alt = _check_alt(a.alt)
    _read_image(a.file)
    if a.dry_run:
        before = call("GET", f"/media-posts/{a.id}")
        print(f"dry run: the cover of «{before['titolo']}» would become {a.file} with alt «{alt}»")
        return EXIT_OK
    image = upload(a.file)
    result = call("PUT", f"/posts/{a.id}/cover", body={"immagine_id": image["id"], "alt": alt})
    _record(a.id, "cover", {"file": a.file, "url": image["url"], "alt": alt, "prompt": _prompt_of(a.file)})
    print(f"cover replaced: {result['copertina']['url']} (thumbnail {result['copertina']['mini']})")
    print(f"article: {result['url']}")
    return EXIT_OK


def cmd_inline(a) -> int:
    replace = a.replace or []
    add = a.add or []
    remove = a.remove or []
    if not (replace or add or remove):
        raise Failure("Nothing to do: give --replace, --add or --remove.", EXIT_USAGE)
    for _, file, alt in replace + add:
        _read_image(file)
        _check_alt(alt)
    if a.dry_run:
        before = call("GET", f"/media-posts/{a.id}")
        current = before["immagini_nel_testo"]
        print(f"«{before['titolo']}»: {len(current)} picture(s) in the text, {len(before['testo'].split(chr(10) * 2))} paragraph(s)")
        for n, file, alt in replace:
            old = current[int(n)]["alt"] if int(n) < len(current) else "(no such picture)"
            print(f"  replace #{n} «{old}» with {file} «{alt}»")
        for n, file, alt in add:
            print(f"  add after paragraph {n}: {file} «{alt}»")
        for n in remove:
            print(f"  remove #{n}")
        return EXIT_OK
    body: Dict[str, Any] = {"sostituisci": [], "aggiungi": [], "rimuovi": [int(n) for n in remove]}
    uploaded: List[Dict[str, Any]] = []
    for n, file, alt in replace:
        image = upload(file)
        uploaded.append({"file": file, "url": image["url"], "alt": _check_alt(alt), "prompt": _prompt_of(file)})
        body["sostituisci"].append({"indice": int(n), "immagine_id": image["id"], "alt": _check_alt(alt)})
    for n, file, alt in add:
        image = upload(file)
        uploaded.append({"file": file, "url": image["url"], "alt": _check_alt(alt), "prompt": _prompt_of(file)})
        body["aggiungi"].append({"dopo_paragrafo": int(n), "immagine_id": image["id"], "alt": _check_alt(alt)})
    result = call("PUT", f"/posts/{a.id}/inline", body=body)
    for entry in uploaded:
        _record(a.id, "inline", entry)
    print(f"text pictures now: {len(result['immagini_nel_testo'])}")
    for img in result["immagini_nel_testo"]:
        print(f"  #{img['indice']} {img['url']}  «{img['alt']}»")
    print(f"article: {result['url']}")
    return EXIT_OK


def cmd_progress(_a) -> int:
    data = _progress()
    if not data:
        print("nothing redone yet")
        return EXIT_OK
    for post_id, riga in data.items():
        cover = riga.get("cover")
        print(f"{post_id}  cover: {'yes' if cover else 'no'}  inline: {len(riga.get('inline', []))}")
        for entry in ([cover] if cover else []) + riga.get("inline", []):
            if entry.get("prompt"):
                print(f"    {entry['prompt'][:140]}")
    return EXIT_OK


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)
    k = sub.add_parser("key", help="the saved key")
    k.add_argument("action", choices=["show", "save", "clear"])
    k.set_defaults(fn=cmd_key)
    ls = sub.add_parser("list", help="every article with its pictures")
    ls.add_argument("--status", choices=list(STATUS))
    ls.add_argument("--lang")
    ls.add_argument("--todo", action="store_true", help="only articles whose cover this tool has not redone yet")
    ls.add_argument("--json", action="store_true")
    ls.set_defaults(fn=cmd_list)
    sh = sub.add_parser("show", help="one article with its full text")
    sh.add_argument("id")
    sh.set_defaults(fn=cmd_show)
    sub.add_parser("balance", help="LitMedia credits left").set_defaults(fn=cmd_balance)
    g = sub.add_parser("generate", help=f"one picture with {MODEL}")
    g.add_argument("--prompt", required=True)
    g.add_argument("--out", required=True, help="where to save the picture (.jpg/.png/.webp)")
    g.add_argument("--aspect", default="3:2", help="3:2 for a cover (default), 4:3 or 1:1 for a picture in the text")
    g.add_argument("--resolution", default="2K", help="2K (10 credits, default) or 4K (20)")
    g.add_argument("--budget", type=int, help="credits still allowed for this run: refuse if one picture costs more")
    g.add_argument("--reserve", type=int, default=0, help="credits that must stay on the account afterwards")
    g.add_argument("--allow-cards", action="store_true", help="accept a card-spread prompt (only if the operator asked)")
    g.add_argument("--dry-run", action="store_true", help="print what would be generated, spend nothing")
    g.set_defaults(fn=cmd_generate)
    c = sub.add_parser("cover", help="replace the cover of an article")
    c.add_argument("id")
    c.add_argument("file")
    c.add_argument("--alt", required=True, help="describes the new picture")
    c.add_argument("--dry-run", action="store_true")
    c.set_defaults(fn=cmd_cover)
    i = sub.add_parser("inline", help="replace, add or remove pictures inside the text")
    i.add_argument("id")
    i.add_argument("--replace", nargs=3, action="append", metavar=("N", "FILE", "ALT"), help="picture number N (0 = first)")
    i.add_argument("--add", nargs=3, action="append", metavar=("AFTER_PARAGRAPH", "FILE", "ALT"), help="0 = after the first paragraph")
    i.add_argument("--remove", action="append", metavar="N")
    i.add_argument("--dry-run", action="store_true")
    i.set_defaults(fn=cmd_inline)
    sub.add_parser("progress", help="what this tool has redone").set_defaults(fn=cmd_progress)
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = parser().parse_args(argv)
    try:
        return args.fn(args)
    except Failure as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exc.code


if __name__ == "__main__":
    sys.exit(main())
