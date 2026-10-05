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
    prompt-check --prompt P [--alt TEXT]
                            every check `generate` makes on a prompt, offline: nothing generated, nothing spent
    generate --prompt P --out FILE [--aspect 3:2] [--resolution 2K] [--budget N] [--dry-run]
                            one picture with Seedream 5.0 through litmedia-skill (checks the prompt, then the balance)
    cover ID FILE --alt TEXT [--dry-run]
                            replace the cover
    inline ID [--replace N FILE ALT] [--add AFTER_PARAGRAPH FILE ALT] [--remove N] [--dry-run]
                            replace, add or remove pictures inside the text (N = 0 for the first picture)
    progress                the last pictures generated, and what this tool has already redone, with the prompts

The picture rules, checked before anything is generated or sent (`--dry-run` included), with no option to skip them:
    - no cards of any kind: no tarot card, deck, spread, arcana, reading table, playing or oracle card, not even one
      as a small detail; the word "tarot" itself is refused (it makes the model paint cards). Alt texts too;
    - a concrete scene: at least 12 content words once the house style line and the empty words are taken out;
    - a new scene: a prompt 45% or more similar (Jaccard, content words) to one already generated is refused;
    - a new file: a picture already used for another article is refused (sha256, kept in the progress file).

Exit codes: 0 ok · 2 usage · 4 the API or LitMedia refused (message printed) · 5 configuration missing or unsafe
· 6 budget or balance too low (nothing generated) · 7 a picture rule refused the prompt, alt text or file.

Every uploaded picture gets its list thumbnail automatically on the server: nothing to do for it here.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
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

EXIT_OK, EXIT_USAGE, EXIT_API, EXIT_CONFIG, EXIT_BUDGET, EXIT_RULE = 0, 2, 4, 5, 6, 7

MAX_IMAGE_BYTES = 8_000_000
IMAGE_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}

#: Seedream 5.0 on LitMedia: 2K or 4K (there is no 1K), 10 or 20 credits (checked 2026-09-30).
MODEL = "Seedream 5.0"
COST = {"2K": 10, "4K": 20}

HOME = Path.home()
CACHE_PATH = Path(os.environ["TAROTS_MEDIA_KEY_CACHE"]) if os.environ.get("TAROTS_MEDIA_KEY_CACHE") else HOME / ".tarots-blog" / "media-credentials.json"
PROGRESS_PATH = Path(os.environ["TAROTS_IMAGES_PROGRESS"]) if os.environ.get("TAROTS_IMAGES_PROGRESS") else HOME / ".tarots-blog" / "images-progress.json"
_noted = False

#: The problem this skill exists to fix: every cover was "tarot cards laid out on a table", then a batch of covers
#: made from one fixed prompt per section. The operator's rule is now absolute: **no card of any kind in any blog
#: picture**, not even one as a small detail. Each entry: (pattern, what it names, checked in alt texts too).
#: The bare word "tarot" and the names of cards are refused in prompts only (they make the model paint the card),
#: while an alt text may still carry the article's keyword ("... the Five of Cups tarot meaning").
#: `tarots-blog-publisher/scripts/tarots_blog.py` keeps a copy of these patterns (and of DECK / NOT_A_CARD_DECK) for
#: the pictures it uploads; a test there checks that the two stay identical: change both together.
CARD_PATTERNS = [
    (r"\btarot\w*|\btarocc\w*", "the word itself makes the model paint cards", False),
    (r"\bcards?\b", "a card", True),
    (r"\b(?:tarot|cards?|reading|oracle|celtic[- ]cross|horseshoe|lenormand)\s+spreads?\b"
     r"|\bspreads?\s+(?:positions?|layout)\b"
     r"|\b(?:a|the|this|that|her|his|their|my|your)\s+spread\s+(?:on|across|over|laid)\b", "a spread", True),
    (r"\barcan(?:a|um)\b", "the arcana", True),
    (r"\breading\s+tables?\b|\btables?\s+(?:set\s+)?for\s+(?:a\s+)?reading\b|\bdivination\s+tables?\b", "a reading table", True),
    (r"\brider[- ]?waite\b|\bwaite[- ]smith\b|\bsmith[- ]waite\b|\bthoth\s+(?:trumps?|atus?)\b|\batus?\s+[ivxlc]+\b",
     "a named tarot deck or its trumps", True),
    (r"\bcartomanc\w*|\blenormand\b", "card reading", True),
    (r"\b(?:ace|two|three|four|five|six|seven|eight|nine|ten|page|knight|queen|king|princess|prince)\s+of\s+"
     r"(?:cups|wands|swords|pentacles|disks|discs|coins)\b"
     r"|\bhigh\s+priestess\b|\bhierophant\b|\bhanged\s+man\b|\bwheel\s+of\s+fortune\b",
     "the name of a card (describe its world instead)", False),
]
#: "deck" is a card deck unless it is a ship's, a garden's or a deck chair: those phrases are taken out first.
#: ("wooden deck" stays refused on purpose: it reads as a box of cards as easily as a terrace. Say "terrace".)
DECK = r"\bdecks?\b"
NOT_A_CARD_DECK = (
    r"\b(?:ship's|ships|ship|boat's|boat|ferry|yacht|sailing|sailboat|liner|steamer|barge|vessel|upper|lower|top|main"
    r"|sun|pool|observation|promenade|garden|porch|patio|terrace)\s+decks?\b"
    r"|\bdecks?\s+chairs?\b|\bdeckchairs?\b|\bon\s+deck\b"
    r"|\bdecks?\s+of\s+(?:a|an|the)\s+(?:\w+\s+){0,2}(?:ship|boat|ferry|yacht|sailboat|liner|steamer|vessel|barge)s?\b"
)

#: The house style of `references/prompts.md`, appended to every prompt. Its words are style, not subject: they do
#: not count as content and do not make two prompts look alike.
HOUSE_STYLE = (
    "editorial painterly illustration, soft natural light, warm paper-cream highlights, deep plum shadows, touches of "
    "brass gold and verdigris green, gentle film grain, calm composition with breathing space, contemplative mood, "
    "no text, no letters, no numbers, no watermark, no logo"
)
#: Words that say nothing about the scene: grammar, and the mood fillers of a prompt written without reading the
#: article ("mystical atmosphere, ethereal lighting, professional photography").
EMPTY_WORDS = set("""
a an the and or but nor of in on at to with without by for from into onto over under above below behind beside
besides between through across around along near far its it their her his him she he they them this that these those
there here is are was were be been being as while very some any one each every all both just only also so then than
too more most much many few such own same other another not no yes up down out off again still
mystical magical mystic mysterious ethereal esoteric divine atmosphere atmospheric mood moody feel feeling feelings
theme themed style styled professional photography photo photograph photographic palette tone tones color colors
colour colours colored coloured energy energies vibe vibes aesthetic beautiful stunning gorgeous symbolic symbol
symbols symbolism spiritual spirituality illustration image picture scene art artwork artistic detailed highly
quality cinematic lighting lit glow glowing render rendering realistic hyperrealistic ultra 4k 8k hd hdr
concept representing represents showing shows featuring motif motifs element elements sense evoking evokes
romantic intimate emotional passionate inspiring inspirational dreamy serene peaceful tranquil radiant majestic epic
dramatic elegant ambient enchanting enchanted
""".split())
#: Fewer content words than this: the prompt does not describe a scene, it decorates a category.
MIN_CONTENT_WORDS = 12
#: Jaccard similarity of content words from which a prompt counts as "the same picture again".
MAX_SIMILARITY = 0.45


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
#
# One JSON object. Article ids map to {"cover": entry, "inline": [entries]} as before; two keys starting with "_"
# were added later and never collide with an id (ids are uuids):
#     "_generated": [{"prompt", "file", "sha256", "aspect", "when"}, ...]   every picture `generate` made, oldest first
#     "_used":      {sha256: {"post", "kind", "file", "when"}}                every file swapped into an article


def _progress() -> Dict[str, Any]:
    try:
        data = json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _save(data: Dict[str, Any]) -> None:
    PROGRESS_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = PROGRESS_PATH.with_name(PROGRESS_PATH.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, PROGRESS_PATH)


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def _articles(data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {k: v for k, v in data.items() if not k.startswith("_") and isinstance(v, dict)}


def _record(post_id: str, kind: str, entry: Dict[str, Any]) -> None:
    data = _progress()
    riga = data.setdefault(post_id, {"cover": None, "inline": []})
    entry = {**entry, "when": _now()}
    if kind == "cover":
        riga["cover"] = entry
    else:
        riga.setdefault("inline", []).append(entry)
    if entry.get("sha256"):
        data.setdefault("_used", {})[entry["sha256"]] = {"post": post_id, "kind": kind, "file": entry.get("file"), "when": entry["when"]}
    _save(data)


def _record_generated(prompt: str, file: Path, aspect: str) -> None:
    data = _progress()
    data.setdefault("_generated", []).append(
        {"prompt": prompt, "file": str(file), "sha256": sha256_of(file), "aspect": aspect, "when": _now()}
    )
    _save(data)


def sha256_of(path: Any) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _used_files(data: Dict[str, Any]) -> Dict[str, str]:
    """sha256 → article id of every picture already swapped in. Entries written before the hashes were kept have
    no sha256: their file is hashed now, if it is still on disk."""
    used = {sha: str(v.get("post")) for sha, v in (data.get("_used") or {}).items() if isinstance(v, dict)}
    for post_id, riga in _articles(data).items():
        for entry in ([riga.get("cover")] if riga.get("cover") else []) + list(riga.get("inline") or []):
            sha = entry.get("sha256")
            if not sha and entry.get("file") and Path(entry["file"]).is_file():
                sha = sha256_of(entry["file"])
            if sha:
                used.setdefault(sha, post_id)
    return used


def _known_prompts(data: Dict[str, Any]) -> List[str]:
    """Every prompt already generated (and the older ones kept only next to an article), without repeats."""
    seen: List[str] = []
    for entry in data.get("_generated") or []:
        if entry.get("prompt") and entry["prompt"] not in seen:
            seen.append(entry["prompt"])
    for riga in _articles(data).values():
        for entry in ([riga.get("cover")] if riga.get("cover") else []) + list(riga.get("inline") or []):
            if entry.get("prompt") and entry["prompt"] not in seen:
                seen.append(entry["prompt"])
    return seen


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


# ---- the picture rules (no network: `prompt-check` runs them alone) -------------------------------------------


def card_problem(text: str, *, alt: bool = False) -> Optional[str]:
    """The first mention of a card in a prompt (or, with alt=True, in an alt text), as «words» (what they name)."""
    low = " ".join(text.lower().split()).replace("’", "'")
    for pattern, what, in_alt in CARD_PATTERNS:
        if alt and not in_alt:
            continue
        m = re.search(pattern, low)
        if m:
            return f"«{m.group(0)}» ({what})"
    m = re.search(DECK, re.sub(NOT_A_CARD_DECK, " ", low))
    return f"«{m.group(0)}» (a deck of cards)" if m else None


def _stem(word: str) -> str:
    if len(word) > 4 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 4 and word.endswith(("ches", "shes", "sses", "xes", "zes")):
        return word[:-2]
    if len(word) > 3 and word.endswith("s") and not word.endswith(("ss", "us", "is")):
        return word[:-1]
    return word


def _words(text: str) -> List[str]:
    return [_stem(w) for w in re.findall(r"[a-z0-9]+(?:'[a-z]+)?", text.lower().replace("’", "'"))]


_STYLE_WORDS = set(_words(HOUSE_STYLE))
_EMPTY = {_stem(w) for w in EMPTY_WORDS}


def content_words(prompt: str) -> set:
    """The words that describe the scene: the house style line, its vocabulary and the empty words taken out."""
    low = " ".join(prompt.lower().split())
    low = low.replace(" ".join(HOUSE_STYLE.lower().split()), " ")
    return {w for w in _words(low) if w not in _STYLE_WORDS and w not in _EMPTY and len(w) > 1}


def similarity(a: str, b: str) -> float:
    wa, wb = content_words(a), content_words(b)
    return len(wa & wb) / len(wa | wb) if wa and wb else 0.0


def most_similar(prompt: str, earlier: List[str]) -> Optional[tuple]:
    best = max(((similarity(prompt, p), p) for p in earlier), default=None, key=lambda t: t[0])
    return best if best and best[0] > 0 else None


def prompt_problems(prompt: str, earlier: List[str]) -> List[str]:
    """Every rule the prompt breaks, as messages for the agent; an empty list means it may be generated."""
    problems: List[str] = []
    card = card_problem(prompt)
    if card:
        problems.append(
            f"it asks for a card: {card}. No blog picture shows cards of any kind — no tarot card, deck, spread, "
            "arcana, reading table, playing or oracle card, not even one small card as a detail. Show the world the "
            "article talks about instead (see references/prompts.md)."
        )
    words = content_words(prompt)
    if len(words) < MIN_CONTENT_WORDS:
        problems.append(
            f"too generic: only {len(words)} content word(s) once the house style and the empty words are out "
            f"(at least {MIN_CONTENT_WORDS}). Describe a concrete scene from this article: who or what, where, when, "
            "which detail from the text."
        )
    best = most_similar(prompt, earlier)
    if best and best[0] >= MAX_SIMILARITY:
        problems.append(
            f"too close to a picture already generated ({best[0]:.0%} of the same content words, the limit is "
            f"{MAX_SIMILARITY:.0%}): «{_short(best[1])}». Choose another kind of picture, setting, light or season."
        )
    return problems


def _short(prompt: str, size: int = 160) -> str:
    text = " ".join(prompt.split())
    style = " ".join(HOUSE_STYLE.split())
    text = text.replace(style, "").rstrip(" ,") or text
    return text if len(text) <= size else text[: size - 1] + "…"


def check_prompt(prompt: str) -> None:
    problems = prompt_problems(prompt, _known_prompts(_progress()))
    if problems:
        raise Failure("the prompt is refused, nothing was generated:\n  - " + "\n  - ".join(problems), EXIT_RULE)


def check_file(post_id: str, path: str, used: Optional[Dict[str, str]] = None) -> str:
    """The file's sha256, after making sure it was never swapped into another article and that the prompt it was
    generated from (if `generate` left it next to the file) obeys today's rules."""
    sha = sha256_of(path)
    data = _progress()
    other = (used if used is not None else _used_files(data)).get(sha)
    if other and other != post_id:
        raise Failure(
            f"{path} is already a picture of article {other}: every article gets its own picture. Generate a new one "
            "for this article.", EXIT_RULE,
        )
    prompt = _prompt_of(path)
    if prompt and (card := card_problem(prompt)):
        raise Failure(f"{path} was generated from a prompt that asks for a card ({card}): it cannot go on the blog.", EXIT_RULE)
    if not any(e.get("sha256") == sha for e in data.get("_generated") or []):
        print(f"warning: {path} was not made by `generate` (litmedia-skill). Use it only if the operator supplied it "
              "and it shows no card.", file=sys.stderr)
    return sha


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
    cost = COST[resolution]
    out = Path(a.out)
    if out.suffix.lower() not in IMAGE_TYPES:
        raise Failure("--out must end in .jpg, .jpeg, .png or .webp", EXIT_USAGE)
    check_prompt(a.prompt)
    if a.dry_run:
        print(f"dry run: the prompt passes every check; {MODEL}, {a.aspect}, {resolution}, {cost} credits, "
              f"would be saved to {out}")
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
    _record_generated(a.prompt, out, a.aspect)
    print(f"saved {out} ({out.stat().st_size // 1024} KB), {cost} credits; balance now about {credits - cost}")
    return EXIT_OK


def cmd_prompt_check(a) -> int:
    earlier = _known_prompts(_progress())
    problems = prompt_problems(a.prompt, earlier)
    if a.alt is not None:
        try:
            _check_alt(a.alt)
        except Failure as exc:
            problems.append(str(exc))
    best = most_similar(a.prompt, earlier)
    print(f"content words: {len(content_words(a.prompt))} (at least {MIN_CONTENT_WORDS})")
    print(f"closest earlier prompt: {best[0]:.0%} (limit {MAX_SIMILARITY:.0%}) «{_short(best[1])}»" if best
          else f"closest earlier prompt: none of the {len(earlier)} on record shares a content word")
    if problems:
        print("REFUSED:\n  - " + "\n  - ".join(problems))
        return EXIT_RULE
    print("ok: `generate` would accept this prompt (nothing was generated, nothing spent)")
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
    if problem := card_problem(alt, alt=True):
        raise Failure(f"The alt text describes a card ({problem}), and no blog picture shows one: describe what is "
                      "really in the new picture.", EXIT_RULE)
    return alt[:200]


def cmd_cover(a) -> int:
    alt = _check_alt(a.alt)
    _read_image(a.file)
    sha = check_file(a.id, a.file)
    if a.dry_run:
        before = call("GET", f"/media-posts/{a.id}")
        print(f"dry run: the cover of «{before['titolo']}» would become {a.file} with alt «{alt}»")
        return EXIT_OK
    image = upload(a.file)
    result = call("PUT", f"/posts/{a.id}/cover", body={"immagine_id": image["id"], "alt": alt})
    _record(a.id, "cover", {"file": a.file, "sha256": sha, "url": image["url"], "alt": alt, "prompt": _prompt_of(a.file)})
    print(f"cover replaced: {result['copertina']['url']} (thumbnail {result['copertina']['mini']})")
    print(f"article: {result['url']}")
    return EXIT_OK


def cmd_inline(a) -> int:
    replace = a.replace or []
    add = a.add or []
    remove = a.remove or []
    if not (replace or add or remove):
        raise Failure("Nothing to do: give --replace, --add or --remove.", EXIT_USAGE)
    used = _used_files(_progress())
    hashes: Dict[str, str] = {}
    for _, file, alt in replace + add:
        _read_image(file)
        _check_alt(alt)
        sha = check_file(a.id, file, used)
        if sha in hashes.values():
            raise Failure(f"{file} is the same picture as another one in this command: each place gets its own.", EXIT_RULE)
        hashes[file] = sha
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
        uploaded.append({"file": file, "sha256": hashes[file], "url": image["url"], "alt": _check_alt(alt), "prompt": _prompt_of(file)})
        body["sostituisci"].append({"indice": int(n), "immagine_id": image["id"], "alt": _check_alt(alt)})
    for n, file, alt in add:
        image = upload(file)
        uploaded.append({"file": file, "sha256": hashes[file], "url": image["url"], "alt": _check_alt(alt), "prompt": _prompt_of(file)})
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
    generated = data.get("_generated") or []
    if generated:
        print("Last pictures generated, newest first (the next one must not be the same kind as the last 3):")
        for n, entry in enumerate(reversed(generated[-6:]), 1):
            print(f"  {n}. {entry.get('when', '')[:10]}  {entry.get('aspect', '')}  {entry.get('file')}")
            print(f"     {_short(entry.get('prompt') or '', 200)}")
        print()
    articles = _articles(data)
    if not articles:
        print("nothing redone yet")
        return EXIT_OK
    for post_id, riga in articles.items():
        cover = riga.get("cover")
        print(f"{post_id}  cover: {'yes' if cover else 'no'}  inline: {len(riga.get('inline', []))}")
        for entry in ([cover] if cover else []) + riga.get("inline", []):
            if entry.get("prompt"):
                print(f"    {_short(entry['prompt'], 140)}")
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
    pc = sub.add_parser("prompt-check", help="check a prompt (and an alt text) offline, before spending anything")
    pc.add_argument("--prompt", required=True)
    pc.add_argument("--alt", help="also check this alt text")
    pc.set_defaults(fn=cmd_prompt_check)
    g = sub.add_parser("generate", help=f"one picture with {MODEL} through litmedia-skill")
    g.add_argument("--prompt", required=True)
    g.add_argument("--out", required=True, help="where to save the picture (.jpg/.png/.webp)")
    g.add_argument("--aspect", default="3:2", help="3:2 for a cover (default), 4:3 or 1:1 for a picture in the text")
    g.add_argument("--resolution", default="2K", help="2K (10 credits, default) or 4K (20)")
    g.add_argument("--budget", type=int, help="credits still allowed for this run: refuse if one picture costs more")
    g.add_argument("--reserve", type=int, default=0, help="credits that must stay on the account afterwards")
    g.add_argument("--dry-run", action="store_true", help="check the prompt and print what would be generated, spend nothing")
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
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]  # «» and … on a Windows console
        except (AttributeError, ValueError):
            pass
    args = parser().parse_args(argv)
    try:
        return args.fn(args)
    except Failure as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exc.code


if __name__ == "__main__":
    sys.exit(main())
