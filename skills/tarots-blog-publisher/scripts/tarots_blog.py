#!/usr/bin/env python3
"""tarots_blog.py: publish to the TAROTS chat blog through its REST API (v1).

Standard library only (Python 3.8+). Configuration comes from the environment, or from a small local cache this
tool manages for you — never from a command argument, an article file, or a prompt:

    TAROTS_API_URL   the API base, e.g. https://tarots.chat/api   (https only; http is accepted for localhost)
    TAROTS_API_KEY   a `tk_live_...` key created in the console (Blog > Keys)

Set both once and this tool remembers them for next time, in a file *outside any repository*
(`~/.tarots-blog/credentials.json`, or `TAROTS_KEY_CACHE` if you point it elsewhere): later runs need neither
variable set. Offering a *different* key than the one already saved is never silent — see `key` below.

Commands (run `tarots_blog.py <command> -h` for the options):

    key show|save|clear    the saved key: show its prefix and origin, save the one in TAROTS_API_KEY, or forget it
    guide                  what the blog accepts and the SEO thresholds (read once, before writing)
    new "SLUG OR TITLE"    create the work folder of one article: ~/.tarots-blog/work/<YYYY-MM-DD>-<slug>/ with
                           article.json (empty SEO fields, status draft), article.md (empty) and foto/ (its pictures).
                           TAROTS_WORK_DIR moves the root. Article files live there and nowhere else.
    sections               the sections articles can go in
    tags                   tags already in use (reuse them)
    catalog [--grep TEXT]  cards and spreads with the ready-made internal-link shortcut
    mine                   articles this key created (avoid duplicates, pick an unused keyword)
    titles [--lang en] [--status S] [--section SLUG] [--grep TEXT] [--all] [--refresh]
                           one line per article of the WHOLE blog (any author): slug | title | keyword | lang |
                           status | date. Kept in a local copy (~/.tarots-blog/titles-cache.json, or
                           TAROTS_TITLES_CACHE) updated with only what changed; deleted articles leave it only on a
                           full reload (--refresh, or by itself when the copy is older than 7 days)
    topic-check "TOPIC" [--lang en]
                           the 5 articles closest to a proposed title/keyword and a verdict FREE / CLOSE / TAKEN
    check ARTICLE          SEO report without saving anything, then NEXT: the exact fixes, one per open item.
                           Counts its rounds in the work folder (.checks): a 5th round still below the score is a STOP
    upload IMAGE [--for SLUG_OR_ID] [--operator-image]
                           upload a cover OR an inline image, print its id and reusable url
    post ARTICLE [--cover IMAGE [--operator-image]]
                           check, then create the article (draft unless the JSON says "published")
    update ID PATCH.json   change fields of an article this key created
    delete-draft ID        delete a draft this key created

ARTICLE is the article's slug (the newest work folder with that slug is used), its work folder, or the path of its
article.json. When it is not found the error says where article files live: never search the disk for them. A bare
picture name (`--cover cover.jpg`, `upload inline-1.jpg --for SLUG`) is looked for in that work folder's foto/.

`check` and `post` refuse, before calling the API, a focus_keyword longer than 6 words or with a repeated word
(exit 9), or one already TAKEN by another article according to the same comparison as `topic-check` (exit 8).

Pictures (`post --cover`, `upload`) share the record of the `tarots-blog-images` skill: `~/.tarots-blog/
images-progress.json`, or `TAROTS_IMAGES_PROGRESS`. Before anything is uploaded a picture is refused if it was
not made by `tarots_images.py generate` (unless `--operator-image`: a picture the operator supplied, accepted with a
warning), if it was already used for another article (same sha256, whatever the file name), or if the prompt it
was generated from makes cards the picture (a card as the subject, two or more cards, a spread, a hand holding a
card: the rules of `tarots_images.py`, copied here), or if that prompt draws a card (one single small card) and the
article is not about that very card: its title or focus keyword (article.json for `post`; for `upload --for`, the
work folder or the titles copy) must name the card the prompt names, and `upload` without `--for` refuses it.
After a successful `post` or `upload` its sha256 is recorded with the article.

Exit codes: 0 ok · 2 usage, bad or missing article file · 3 SEO score below the threshold, or an error (FIX) left
(nothing saved) · 4 the API refused (message printed) · 5 configuration missing or unsafe · 7 a picture rule refused
the file (nothing uploaded) · 8 the topic (`topic-check`) or the focus_keyword (`check`, `post`) is TAKEN
· 9 the focus_keyword is not a search phrase (more than 6 words, or a repeated word) · 10 STOP: 4 rounds of `check`
did not reach the score; `check` and `post` refuse this article from now on (the operator can delete its .checks).

The full key is only ever sent to TAROTS_API_URL, never printed (only its 12-character prefix is, to tell keys
apart), and redirects are not followed (a redirect would carry the key to another host): if the server redirects,
fix TAROTS_API_URL. The cache file holds the key in clear text (there is nothing to hash it against, unlike the
server's own copy) — it is `chmod 600` on POSIX and lives outside any repository by default specifically so it can
never be committed; keep it that way if `TAROTS_KEY_CACHE` is set to somewhere else.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

EXIT_OK, EXIT_USAGE, EXIT_SCORE, EXIT_API, EXIT_CONFIG, EXIT_RULE, EXIT_TAKEN = 0, 2, 3, 4, 5, 7, 8
EXIT_KEYWORD, EXIT_STOP = 9, 10

MAX_IMAGE_BYTES = 8_000_000
IMAGE_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}

#: Outside any repository by design: this is the only file this tool ever writes the key to.
CACHE_PATH = Path(os.environ["TAROTS_KEY_CACHE"]) if os.environ.get("TAROTS_KEY_CACHE") else Path.home() / ".tarots-blog" / "credentials.json"
_noted = False  # config() prints its "using saved key" / "key saved" note once per run, not once per API call

#: The picture record of the `tarots-blog-images` skill, shared on purpose (same file, same keys): `_generated`
#: lists what `tarots_images.py generate` made, `_used` maps sha256 → the article that uses the picture.
PROGRESS_PATH = Path(os.environ["TAROTS_IMAGES_PROGRESS"]) if os.environ.get("TAROTS_IMAGES_PROGRESS") else Path.home() / ".tarots-blog" / "images-progress.json"

#: The local copy of every article's title (`titles`, `topic-check`): the compact list of the whole blog, kept up to
#: date with `dal` (only what changed since the last run). Holds no key and no text, only titles, slugs, keywords.
TITLES_CACHE_PATH = Path(os.environ["TAROTS_TITLES_CACHE"]) if os.environ.get("TAROTS_TITLES_CACHE") else Path.home() / ".tarots-blog" / "titles-cache.json"
TITLES_PAGE = 1000                                   # the API's maximum page size
TITLES_FULL_EVERY = datetime.timedelta(days=7)       # older than this: reload everything (deleted articles go away)
TITLES_OVERLAP = datetime.timedelta(minutes=10)      # `dal` starts this much before the last sync (slow transactions)
TITLES_SHOWN = 100                                   # lines `titles` prints without --all

#: A copy of the card rules of `tarots_images.py`: a blog picture is never a picture of cards (no card as the
#: subject, no two or more cards, no spread or layout, no hand holding a card), while cards may stay in the context
#: ("tarot" as an adjective, the names of the cards as a world or a symbol; one single small card only for an
#: article about that very card). CARD_PATTERNS, CARD_WORD, LEAD_WORDS, LEAD_SKIP, DECK, NOT_A_CARD_DECK,
#: `card_problems()` and the card rule of the article (MAJOR_ARCANA… `card_rule_problems()`, after
#: `card_problem()`) are kept identical to the original by a test (`tests/test_immagini.py`); change both together.
SPREAD = "spread"
_W = r"(?:[\w'-]+\s+)"  # one more word, in the patterns below
CARD_PATTERNS = [
    # spreads and layouts
    (r"\b(?:tarot|cards?|reading|oracle|celtic[- ]cross|horseshoe|lenormand)\s+spreads?\b"
     r"|\bspreads?\s+(?:positions?|layouts?)\b"
     r"|\b(?:a|the|this|that|her|his|their|my|your)\s+spread\s+(?:on|across|over|laid)\b"
     r"|\b(?:tarot|cards?|oracle|lenormand|celtic[- ]cross|horseshoe|spread|reading)\s+" + _W + r"{0,2}layouts?\b",
     "a spread or a layout of cards", SPREAD),
    (r"\b(?:tarot|cards?|oracle|lenormand)\s+readings?\b|\breading\s+tables?\b"
     r"|\btables?\s+(?:set\s+)?for\s+(?:a\s+)?reading\b|\bdivination\s+tables?\b|\bcartomanc\w*",
     "a card reading: cards laid out on a table", SPREAD),
    (r"\bcards?\s+(?:laid|spread|arranged|dealt|fanned)\s+out\b"
     r"|\bcards?\s+(?:(?:laid|lying|placed|set|spread|arranged|scattered|dealt|turned)\s+(?:out\s+)?)?"
     r"(?:on|across|over|upon)\s+" + _W + r"{0,3}(?:table|tablecloth|cloth|altar|desk|velvet|silk|floor|rug|board)s?\b",
     "cards laid out on a surface: a spread", SPREAD),
    (r"\bcards?\s+" + _W + r"{0,2}face[- ]?(?:down|up)\b|\bface[- ]?(?:down|up)\s+" + _W + r"{0,2}cards?\b"
     r"|\bfan\s+of\s+" + _W + r"{0,2}cards\b|\bfanned\s+" + _W + r"{0,2}cards\b",
     "cards face down or face up, or fanned out: a spread", SPREAD),
    # hands holding or turning a card
    (r"\b(?:holding|holds|hold|turning|turns|turned|flipping|flips|flipped|drawing|draws|drew|shuffling|shuffles"
     r"|dealing|deals|pulling|pulls|lifting|lifts|picking|picks|clutching|clutches|grasping|grasps|offering)\s+"
     r"(?:up\s+|over\s+)?" + _W + r"{0,3}cards?\b"
     r"|\bcards?\s+" + _W + r"{0,2}(?:in|between|from)\s+" + _W + r"{0,2}(?:hands?|fingers?|palms?)\b",
     "a hand holding or turning a card", "hands"),
    # more than one card
    (r"\bcards\b", "more than one card", "many"),
    (r"\barcana\b|\btarocchi\b|\b(?:thoth|tarot|major|minor)\s+(?:trumps|atus)\b"
     r"|\b(?:pack|pile|stack|heap|hand|handful|box|set)\s+of\s+" + _W + r"{0,2}(?:tarot|tarocchi|oracle|lenormand|playing)\b",
     "a set of cards", "many"),
    # the card as the subject
    (r"\b(?:close[- ]?up|macro(?:\s+shot)?|detail|portrait|still\s+life|study)\s+of\s+" + _W + r"{0,3}cards?\b"
     r"|\bcards?\s+(?:showing|shows|depicting|depicts|bearing|with\s+(?:an?\s+)?(?:image|picture|illustration|painting"
     r"|figure|drawing)\s+of)\b"
     r"|\b(?:large|big|giant|huge|oversized|enormous|floating|levitating|glowing)\s+" + _W + r"?cards?\b"
     r"|\bcards?\s+" + _W + r"{0,2}(?:in\s+the\s+)?(?:foreground|centre|center)\b",
     "a card as the subject of the picture", "subject"),
    (r"\btarot[- ](?:style\s+)?(?:imagery|artwork|art|illustrations?|images?|iconography|designs?|prints?|paintings?"
     r"|style|frames?|borders?)\b|\bcard[- ](?:frames?|borders?)\b|\batus?\s+[ivxlc]+\b",
     "the artwork, frame or numbered title of a card: the model paints the card", "subject"),
    (r"\brider[- ]?waite\b|\bwaite[- ]smith\b|\bsmith[- ]waite\b|\bmarseilles?\s+tarot\b|\btarot\s+de\s+marseilles?\b",
     "a named deck's artwork", "subject"),
]
CARD_WORD = r"\bcard\b|\barcanum\b|\btarocco\b"
LEAD_WORDS = 8
LEAD_SKIP = frozenset("""
a an the and or but of in on at to with by for from into onto over under above below behind beside between through
across around along near its it their her his this that these those there is are was were be as while very some one
single just only
""".split())
DECK = r"\bdecks?\b"
NOT_A_CARD_DECK = (
    r"\b(?:ship's|ships|ship|boat's|boat|ferry|yacht|sailing|sailboat|liner|steamer|barge|vessel|upper|lower|top|main"
    r"|sun|pool|observation|promenade|garden|porch|patio|terrace)\s+decks?\b"
    r"|\bdecks?\s+chairs?\b|\bdeckchairs?\b|\bon\s+deck\b"
    r"|\bdecks?\s+of\s+(?:a|an|the)\s+(?:\w+\s+){0,2}(?:ship|boat|ferry|yacht|sailboat|liner|steamer|vessel|barge)s?\b"
    # the style of the card of an article about it (see card_rule_problems): a style, not a deck in the picture
    r"|\bstyle\s+of\s+(?:the\s+)?thoth\s+(?:tarot\s+)?decks?\b"
)

#: Friendly (English) keys of an article file → the API field. The API's own names are accepted as they are.
FIELDS = {
    "title": "titolo", "subtitle": "sottotitolo", "body": "testo", "markdown": "testo", "language": "lang",
    "section": "sezione", "cover_image_id": "immagine_id", "cover_alt": "immagine_alt", "image_alt": "immagine_alt",
    "seo_title": "seo_titolo", "seo_description": "seo_descrizione", "focus_keyword": "seo_parola_chiave",
    "secondary_keywords": "seo_parole_chiave", "status": "stato", "publish_at": "pubblicato_il",
    "featured": "in_evidenza",
}
#: Fields with the same name in both vocabularies.
SAME = {"lang", "tags", "slug", "canonical_url", "noindex", "faq", "dry_run"}
API_FIELDS = set(FIELDS.values()) | SAME
STATUS = {"draft": "bozza", "published": "pubblicato", "archived": "archiviato"}


class Failure(Exception):
    def __init__(self, message: str, code: int = EXIT_API):
        super().__init__(message)
        self.code = code


class Unreachable(Failure):
    """The API could not be reached at all (network, DNS, timeout): the only failure a local cache may cover for."""


class NotFound(Failure):
    """HTTP 404: the resource, or the whole endpoint on a server older than this script."""


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
        CACHE_PATH.chmod(0o600)  # best-effort: POSIX only, Windows ACLs work differently
    except OSError:
        pass


def _clear_cache() -> None:
    try:
        CACHE_PATH.unlink()
    except FileNotFoundError:
        pass


def config() -> Dict[str, str]:
    """Env vars win when present; otherwise the saved key/URL are used. A key offered via TAROTS_API_KEY that
    differs from an already-saved one is never silently swapped in — see `key show`/`key save` in the docstring."""
    global _noted
    env_base = os.environ.get("TAROTS_API_URL", "").strip().rstrip("/")
    env_key = os.environ.get("TAROTS_API_KEY", "").strip()
    cached = _read_cache()
    if env_key and cached and cached.get("key") != env_key:
        raise Failure(
            f"A different key is already saved (prefix {cached['key'][:12]}...) than the one in TAROTS_API_KEY "
            f"(prefix {env_key[:12]}...). Run `key show` to compare them, `key save` to replace the saved one "
            "with this one, or unset TAROTS_API_KEY to keep using the saved key untouched.", EXIT_CONFIG,
        )
    if env_key:
        base, key = env_base, env_key
        if not cached and base:  # nothing saved yet: nothing to confirm, remember it for next time
            _write_cache(base, key)
            print(f"note: saved this key for reuse (prefix {key[:12]}...) in {CACHE_PATH}; "
                  "omit TAROTS_API_KEY next time, or run `key clear` to forget it.", file=sys.stderr)
    elif cached:
        base, key = env_base or cached.get("url", ""), cached.get("key", "")
        if not _noted:
            print(f"note: using the saved key (prefix {key[:12]}...); set TAROTS_API_KEY to use a different one.", file=sys.stderr)
            _noted = True
    else:
        base, key = env_base, env_key
    if not base:
        raise Failure("TAROTS_API_URL is not set (for example https://tarots.chat/api).", EXIT_CONFIG)
    url = urllib.parse.urlparse(base)
    local = url.hostname in ("localhost", "127.0.0.1", "::1")
    if url.scheme != "https" and not (url.scheme == "http" and local):
        raise Failure("TAROTS_API_URL must be https (http is only accepted for localhost): the key would travel in clear text.", EXIT_CONFIG)
    if not key.startswith("tk_live_"):
        raise Failure("TAROTS_API_KEY is not set (and none is saved), or is not a tk_live_ key. Create one in the console: Blog > Keys.", EXIT_CONFIG)
    return {"base": base, "key": key}


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """A redirect would forward the Authorization header to whatever host it points at: never follow one."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D401
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


def call(
    method: str, path: str, *, body: Optional[Any] = None, raw: Optional[bytes] = None,
    content_type: Optional[str] = None, query: Optional[Dict[str, Any]] = None, timeout: int = 60,
) -> Any:
    """One request to `/v1/blog{path}`. Returns the decoded JSON (or None for 204). Raises `Failure`."""
    cfg = config()
    url = f"{cfg['base']}/v1/blog{path}"
    if query:
        url += "?" + urllib.parse.urlencode({k: v for k, v in query.items() if v is not None})
    headers = {"Authorization": f"Bearer {cfg['key']}", "Accept": "application/json", "User-Agent": "tarots-blog-publisher/1.0"}
    data = None
    if raw is not None:
        data, headers["Content-Type"] = raw, content_type or "application/octet-stream"
    elif body is not None:
        data, headers["Content-Type"] = json.dumps(body).encode("utf-8"), "application/json"
    request = urllib.request.Request(url, data=data, method=method, headers=headers)
    # Only reads are retried: a repeated POST could create a duplicate article.
    for attempt in range(2 if method == "GET" else 1):
        try:
            with _OPENER.open(request, timeout=timeout) as response:
                payload = response.read()
                return json.loads(payload) if payload else None
        except urllib.error.HTTPError as exc:
            raise (NotFound if exc.code == 404 else Failure)(explain(exc)) from None
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            if attempt == 0 and method == "GET":
                time.sleep(2)
                continue
            raise Unreachable(f"Cannot reach the API ({getattr(exc, 'reason', exc)}). Check TAROTS_API_URL and the network.") from None
    return None  # pragma: no cover


def explain(exc: urllib.error.HTTPError) -> str:
    """A short, useful message for an HTTP error. Never includes request headers (the key)."""
    try:
        detail = json.loads(exc.read().decode("utf-8", "replace")).get("detail")
    except Exception:  # noqa: BLE001
        detail = None
    if isinstance(detail, (dict, list)):
        detail = json.dumps(detail, ensure_ascii=False)
    redirect = "The server redirected the request. Point TAROTS_API_URL at the final address; redirects are not followed."
    hints = {
        301: redirect, 302: redirect, 307: redirect, 308: redirect,
        401: "The key was rejected: wrong, revoked or expired. Create a new one in the console (Blog > Keys).",
        403: "This key lacks the permission for that action (or the article is not yours to change).",
        404: "Not found: wrong id, or the article was created by another key.",
        413: "The file is too large (8 MB at most).",
        415: "Unsupported file type: send PNG, JPEG or WebP.",
        429: "Rate limit or daily limit reached. Wait, and do not retry in a loop.",
    }
    hint = hints.get(exc.code, "")
    return f"HTTP {exc.code}" + (f": {detail}" if detail else "") + (f"\n  {hint}" if hint else "")


# ---- reading an article file -----------------------------------------------------------------------------------


def normalize(article: Dict[str, Any], base_dir: Optional[Path] = None) -> Dict[str, Any]:
    """From an article file (friendly or API field names) to the API payload.

    `body_file` (a Markdown path, relative to the JSON file) fills `testo`. FAQ items may be `{question, answer}`.
    `status` may be draft | published | archived. Unknown keys are an error: a typo must not silently vanish."""
    out: Dict[str, Any] = {}
    unknown: List[str] = []
    for key, value in article.items():
        if key == "body_file":
            continue
        target = FIELDS.get(key, key if key in API_FIELDS else None)
        if target is None:
            unknown.append(key)
        else:
            out[target] = value
    if unknown:
        allowed = sorted(set(FIELDS) | SAME | {"body_file"})
        raise Failure(f"Unknown field(s): {', '.join(sorted(unknown))}. Allowed: {', '.join(allowed)}.", EXIT_USAGE)
    if "body_file" in article:
        path = Path(article["body_file"])
        if base_dir is not None and not path.is_absolute():
            path = base_dir / path
        try:
            out["testo"] = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise Failure(f"Cannot read body_file {path}: {exc.strerror}", EXIT_USAGE) from None
    if isinstance(out.get("testo"), str):
        out["testo"] = _without_leading_h1(out["testo"])
    if isinstance(out.get("stato"), str):
        out["stato"] = STATUS.get(out["stato"].lower(), out["stato"])
    if isinstance(out.get("faq"), list):
        out["faq"] = [
            {"domanda": f.get("domanda", f.get("question", "")), "risposta": f.get("risposta", f.get("answer", ""))}
            if isinstance(f, dict) else f
            for f in out["faq"]
        ]
    if isinstance(out.get("seo_parole_chiave"), str):
        out["seo_parole_chiave"] = [p.strip() for p in out["seo_parole_chiave"].split(",") if p.strip()]
    if isinstance(out.get("tags"), str):
        out["tags"] = [p.strip() for p in out["tags"].split(",") if p.strip()]
    return out


def _without_leading_h1(body: str) -> str:
    """The page title is already the H1: a `# …` line at the top of the body is dropped here, deterministically,
    with a note. Agents kept rewriting the whole text around it (5/10/2026) instead of deleting one line."""
    lines = body.lstrip("﻿").splitlines()
    first = next((i for i, line in enumerate(lines) if line.strip()), None)
    if first is None or not re.match(r"#\s+\S", lines[first]) or lines[first].startswith("##"):
        return body
    print(f"note: removed the H1 at the top of the body ({lines[first].strip()[:60]!r}): the article's title is "
          "already the page's H1; sections start at `##`.", file=sys.stderr)
    rest = lines[first + 1:]
    while rest and not rest[0].strip():
        rest = rest[1:]
    return "\n".join(rest) + ("\n" if body.endswith("\n") else "")


def load_article(path: str) -> Dict[str, Any]:
    file = Path(path)
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
    except OSError as exc:
        raise Failure(f"Cannot read {file}: {exc.strerror}", EXIT_USAGE) from None
    except json.JSONDecodeError as exc:
        raise Failure(f"{file} is not valid JSON: {exc}", EXIT_USAGE) from None
    if not isinstance(data, dict):
        raise Failure(f"{file} must contain a JSON object.", EXIT_USAGE)
    return normalize(data, file.parent)


def require_filled(payload: Dict[str, Any], path: Path) -> None:
    """The skeleton written by `new` is not an article yet: say which file to fill, before the API answers a 422."""
    missing = []
    if not str(payload.get("titolo") or "").strip():
        missing.append(f'"title" is empty in {path}')
    if not str(payload.get("testo") or "").strip():
        missing.append(f"the text is empty: write it in {path.parent / 'article.md'} (sections start at `##`)")
    if missing:
        raise Failure("; ".join(missing) + ".", EXIT_USAGE)


# ---- the work folder: where the files of one article live -----------------------------------------------------
# One folder per article, outside any repository and outside the skill: `~/.tarots-blog/work/<YYYY-MM-DD>-<slug>/`
# with article.json, article.md, foto/ (every picture of that article) and .checks (the rounds of `check`).
# An agent (5/10/2026) wrote its files inside the skill's folder, lost them, then searched the whole disk: every
# command now finds the article from its slug, and says where to look when it is not there.
# `tarots_images.py` finds the same folders (its `work_slug` is a copy of `slugify`; a test keeps them equal).

WORK_NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)$")
ROUNDS_FILE = ".checks"
MAX_ROUNDS = 4                       # rounds of `check` below the score; the next one is a STOP
SKILL_DIR = Path(__file__).resolve().parents[1]


def work_root() -> Path:
    """Read at every call, not at import: TAROTS_WORK_DIR may be set for one run."""
    env = os.environ.get("TAROTS_WORK_DIR", "").strip()
    return Path(env).expanduser() if env else Path.home() / ".tarots-blog" / "work"


def slugify(text: str, limit: int = 60) -> str:
    """`Samhain: a Tarot Spread!` → `samhain-a-tarot-spread`, cut at a hyphen within `limit` characters."""
    slug = _plain(text).replace(" ", "-")
    if len(slug) > limit:
        slug = slug[:limit].rsplit("-", 1)[0]
    return slug


def work_folders() -> List[Path]:
    """Every work folder, newest first (the date in its name, then the last change)."""
    try:
        found = [p for p in work_root().iterdir() if p.is_dir() and WORK_NAME.match(p.name)]
    except OSError:
        return []
    return sorted(found, key=lambda p: (p.name[:10], p.stat().st_mtime), reverse=True)


def find_work_folder(slug: str) -> Optional[Path]:
    """The newest work folder of this slug: by the folder's name, else by the `slug` inside its article.json."""
    folders = work_folders()
    for folder in folders:
        if WORK_NAME.match(folder.name).group(2) == slug:
            return folder
    for folder in folders:
        try:
            if json.loads((folder / "article.json").read_text(encoding="utf-8")).get("slug") == slug:
                return folder
        except (OSError, ValueError, AttributeError):
            continue
    return None


def where_articles_live() -> str:
    recent = "".join(f"\n    {p}" for p in work_folders()[:5]) or " (none yet)"
    return (f"Article files live only in the work folder {work_root() / '<YYYY-MM-DD>-<slug>'} (article.json, "
            "article.md, foto/). Start one with `tarots_blog.py new \"<slug>\"`, then pass its slug, its folder or its "
            f"article.json. Do not search the disk for them. Newest work folders:{recent}")


def resolve_article(arg: str, name: str = "article.json") -> Path:
    """ARTICLE as given to `check`, `post` (and `update`, with name="patch.json"): a file, a work folder, or a slug."""
    path = Path(arg).expanduser()
    if path.is_dir():
        path = path / name
    elif not path.exists() and len(path.parts) == 1 and path.suffix.lower() != ".json":
        folder = find_work_folder(slugify(arg))
        if folder is not None:
            path = folder / name
    if not path.is_file():
        looked = f" (looked for {path})" if str(path) != arg else ""
        raise Failure(f"{arg}: not found{looked}. " + where_articles_live(), EXIT_USAGE)
    resolved = path.resolve()
    if SKILL_DIR in resolved.parents and SKILL_DIR / "assets" not in resolved.parents:
        raise Failure(f"{resolved} is inside the skill's folder: article files never go there (they get lost, and "
                      "an update of the skill deletes them). Run `tarots_blog.py new \"<slug>\"` and move them to the "
                      "work folder it prints.", EXIT_USAGE)
    return path


def in_work_folder(path: Path) -> Optional[Path]:
    """The work folder holding this file, if it is in one."""
    parent = path.resolve().parent
    return parent if WORK_NAME.match(parent.name) else None


def resolve_picture(arg: str, folder: Optional[Path]) -> str:
    """A bare file name (`cover.jpg`) that does not exist here is looked for in the work folder's foto/."""
    path = Path(arg).expanduser()
    if not path.exists() and folder is not None and len(path.parts) == 1:
        candidate = folder / "foto" / path.name
        if candidate.is_file():
            return str(candidate)
    return arg


def skeleton(slug: str) -> Dict[str, Any]:
    """The article.json written by `new`: every field to fill, nothing that the API would refuse once filled."""
    return {
        "title": "", "subtitle": "", "slug": slug, "language": "en", "focus_keyword": "", "seo_title": "",
        "seo_description": "", "secondary_keywords": [], "tags": [], "cover_alt": "", "faq": [], "status": "draft",
        "body_file": "article.md",
    }


# ---- rounds of `check` -------------------------------------------------------------------------------------------
# An agent ran `check` more than ten times on one article, rewriting the whole text each time. The rounds are
# counted in the article's folder; the 5th still below the score is a STOP, recorded, so that a later `check` or
# `post` (even with --save-anyway) refuses the article until the operator deletes the file.


def _rounds_path(article: Path) -> Path:
    return article.parent / ROUNDS_FILE


def read_rounds(article: Path) -> Dict[str, Any]:
    try:
        data = json.loads(_rounds_path(article).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"rounds": [], "stopped": False}
    if not isinstance(data, dict) or not isinstance(data.get("rounds"), list):
        return {"rounds": [], "stopped": False}
    return data


def write_rounds(article: Path, data: Dict[str, Any]) -> None:
    _rounds_path(article).write_text(json.dumps(data, indent=2), encoding="utf-8")


def print_stop(article: Path, data: Dict[str, Any], min_score: int) -> None:
    last = data["rounds"][-1]["score"] if data.get("rounds") else "?"
    folder = article.parent
    print(f"\nSTOP: {len(data.get('rounds', []))} rounds of `check` and the score is still {last} (below {min_score}).")
    print("  Do not save this article: no `post`, no `--save-anyway`, no other rewrite.")
    print("  End the run here. Report: the title, the focus keyword, the last score, the items still open, and the")
    print(f"  work folder {folder}")
    print(f"  (only the operator can reopen it, by deleting {_rounds_path(article)})")


# ---- output -----------------------------------------------------------------------------------------------------


def show(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


MARK = {"errore": "FIX ", "avviso": "WARN", "ok": "ok  "}


def report(seo: Dict[str, Any]) -> None:
    s = seo.get("statistiche", {})
    print(f"SEO score: {seo['punteggio']}/100 ({seo['giudizio']})  words={s.get('parole')} h2={s.get('titoli_h2')} "
          f"internal_links={s.get('collegamenti_interni')} external_links={s.get('collegamenti_esterni')} faq={s.get('faq')}")
    todo = [c for c in seo.get("controlli", []) if c["esito"] != "ok"]
    for c in _open_items(seo):
        print(f"  {MARK[c['esito']]} [{c['id']}] {c['messaggio']}")
    if not todo:
        print("  every check passes")


def _open_items(seo: Dict[str, Any]) -> List[Dict[str, Any]]:
    """The checks that are not ok, errors first, then by weight (the order of the report and of NEXT)."""
    todo = [c for c in seo.get("controlli", []) if c["esito"] != "ok"]
    return sorted(todo, key=lambda c: (c["esito"] != "errore", -c["peso"]))


def passes(seo: Dict[str, Any], min_score: int) -> bool:
    """Good enough to save: the score reaches the threshold and no check is an error (FIX)."""
    return seo["punteggio"] >= min_score and not any(c["esito"] == "errore" for c in seo.get("controlli", []))


# The server's thresholds (SOGLIE in backend/tarot_core/tarot/blog_seo.py), to put numbers in the NEXT lines.
TITLE_CHARS, DESCRIPTION_CHARS, GOOD_WORDS, MAX_SENTENCE = (30, 60), (120, 160), 800, 24
MAX_PER_MILLE, SLUG_CHARS, SLUG_WORDS = 30, 75, 9


def _q(text: Any, size: int = 120) -> str:
    text = " ".join(str(text or "").split())
    return json.dumps(text if len(text) <= size else text[: size - 1] + "…", ensure_ascii=False)


def long_sentences(body: str, limit: int = MAX_SENTENCE, n: int = 3) -> List[str]:
    """The `n` longest sentences above `limit` words, links and shortcuts reduced to their words."""
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)|\[\[[^\]]*\]\]", " ", body)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith(("#", "|", ">")))
    sentences = [" ".join(s.split()) for s in re.split(r"(?<=[.!?])\s+|\n\s*\n", text)]
    return sorted((s for s in sentences if len(s.split()) > limit), key=lambda s: -len(s.split()))[:n]


def next_steps(seo: Dict[str, Any], payload: Dict[str, Any]) -> List[tuple]:
    """For every open item of the report, one concrete instruction with the real values: (to do now?, text).
    The ids are those of blog_seo.py; an unknown id gets a generic line, so a newer server never breaks this."""
    kw = str(payload.get("seo_parola_chiave") or "").strip()
    kq = _q(kw)
    kw_slug = slugify(kw, 160)
    body = str(payload.get("testo") or "")
    title = str(payload.get("seo_titolo") or payload.get("titolo") or "")
    description = str(payload.get("seo_descrizione") or "")
    slug = str(payload.get("slug") or "")
    alt = str(payload.get("immagine_alt") or "")
    stats = seo.get("statistiche") or {}
    steps: List[tuple] = []
    for c in _open_items(seo):
        d = c.get("dettaglio") or {}
        cid = c["id"]
        now = True
        if cid == "titolo_seo":
            n = int(d.get("caratteri", len(title)))
            if not n:
                text = f'there is no title: set "seo_title" ({TITLE_CHARS[0]}-{TITLE_CHARS[1]} chars, starting with {kq})'
            elif n > TITLE_CHARS[1]:
                text = f"seo_title is {n} chars: cut it to ≤ {TITLE_CHARS[1]}, keyword first: current = {_q(title)}"
            else:
                text = (f"seo_title is {n} chars: lengthen it to {TITLE_CHARS[0]}-{TITLE_CHARS[1]} (add the benefit or "
                        f"the year), keyword first: current = {_q(title)}")
        elif cid == "descrizione_seo":
            n = int(d.get("caratteri", len(description)))
            lo, hi = DESCRIPTION_CHARS
            if not n:
                text = f"there is no seo_description: write one of {lo}-{hi} chars, with {kq} once, a promise and a reason to click"
            elif n > hi:
                text = f"seo_description is {n} chars: cut it to ≤ {hi} (remove {n - hi}+), keep {kq} once: current = {_q(description, 200)}"
            else:
                text = (f"seo_description is {n} chars: lengthen it to {lo}-{hi} (add {lo - n}+: a concrete promise and "
                        f"a reason to click), keep {kq} once: current = {_q(description, 200)}")
        elif cid == "parola_chiave":
            text = ('there is no focus_keyword: set it to the phrase you checked with `topic-check` (2-5 words a person '
                    "would type in a search engine)")
        elif cid == "chiave_nel_titolo":
            text = f"the keyword {kq} is not in seo_title: rewrite ONLY seo_title so it starts with the exact phrase (≤ {TITLE_CHARS[1]} chars): current = {_q(title)}"
        elif cid == "chiave_nella_descrizione":
            text = f"the keyword {kq} is not in seo_description: put the exact phrase in it once, in a natural sentence: current = {_q(description, 200)}"
        elif cid == "chiave_nello_slug":
            text = f'the slug does not contain "{kw_slug}": set "slug" to "{kw_slug}" (≤ {SLUG_CHARS} chars, ≤ {SLUG_WORDS} words): current = {_q(slug)}'
        elif cid == "chiave_nell_inizio":
            text = f"the keyword {kq} is not in the first 100 words: edit ONLY the first paragraph and put the exact phrase in it"
        elif cid == "chiave_in_un_h2":
            heads = re.findall(r"^##\s+(.+?)\s*$", body, flags=re.M)
            text = (f"keyword not in an H2: rename ONE existing `##` heading to contain {kq}"
                    + (f" (headings now: {' | '.join(_q(h, 60) for h in heads[:6])})" if heads else ""))
        elif cid == "chiave_nell_alt":
            now = False
            text = f"cover_alt does not contain {kq}: add it only if the picture really shows it; otherwise leave this warning"
        elif cid == "densita":
            count = _plain(body).count(_plain(kw)) if kw else 0
            if not count or not d.get("per_mille"):
                text = (f"the keyword {kq} never appears in the body: put the exact phrase once in the first paragraph and "
                        "once in one `##` heading, inside natural sentences (never pasted at the end of a sentence)")
            else:
                words = int(stats.get("parole") or 0)
                keep = max(1, int(MAX_PER_MILLE * words / 1000 / max(len(kw.split()), 1)))
                text = (f"the keyword {kq} appears {count} times ({d['per_mille']}‰ of the words, limit {MAX_PER_MILLE}‰): "
                        f"replace {max(count - keep, 1)} of them with a synonym or a pronoun; keep at most {keep}")
        elif cid == "lunghezza":
            n = int(d.get("parole", stats.get("parole") or 0))
            text = (f"the body has {n} words: add about {max(GOOD_WORDS - n, 50)} words as ONE new `##` section (an example, "
                    "a common misconception or a practical exercise); leave the rest as it is")
        elif cid == "titoli_h2":
            n = int(d.get("h2", stats.get("titoli_h2") or 0))
            text = f"the body has {n} `##` heading(s): add `##` headings above existing paragraphs to make at least 2 sections; do not rewrite the paragraphs"
        elif cid == "h1_nel_testo":
            lines = re.findall(r"^#\s+.+$", body, flags=re.M)
            text = (f"the body has an H1 line ({', '.join(_q(x, 60) for x in lines[:2])}): make it `##`, or delete it "
                    "if it repeats the title")
        elif cid == "frasi":
            longs = long_sentences(body)
            text = (f"sentences average {d.get('parole_per_frase', '?')} words (limit {MAX_SENTENCE}): split ONLY these "
                    "long ones in two: " + ("; ".join(f"{_q(' '.join(s.split()[:10]) + ' …', 90)} ({len(s.split())} words)"
                                                    for s in longs) or "the longest sentences"))
        elif cid == "collegamenti_interni":
            n = int(d.get("interni", stats.get("collegamenti_interni") or 0))
            text = (("no internal links" if not n else f"only {n} internal link") + ": run `tarots_blog.py catalog --grep "
                    f"<word>` with a card or spread the article talks about, and put {max(2 - n, 1)} of the printed "
                    "shortcuts in sentences (e.g. \"… the lightning of [[card:the-tower]] …\"); `titles --grep <word>` "
                    "gives slugs for [[post:slug]]")
        elif cid == "collegamenti_esterni":
            text = ("no external link: add one reputable source, e.g. a museum, library or agency page you actually "
                    "opened, as [a few words](https://…) inside a sentence")
        elif cid == "immagine":
            if len(alt.strip()) < 8:
                text = 'cover_alt is empty or too short: write what the cover shows (8-125 chars) in "cover_alt"'
            else:
                now = False
                text = "no cover yet: normal in `check`; `post <slug> --cover <file in foto/>` adds it"
        elif cid == "etichette":
            n = int(d.get("etichette", len(payload.get("tags") or [])))
            text = (f"there are {n} tags: run `tarots_blog.py tags` and reuse 2-4 existing ones in \"tags\"" if n < 2
                    else f"there are {n} tags: keep the 6 most relevant")
        elif cid == "faq":
            n = int(d.get("faq", stats.get("faq") or 0))
            text = f'there are {n} FAQ items: add {max(3 - n, 1)} real questions with 1-3 sentence answers to "faq" ({{"question": …, "answer": …}})'
        elif cid == "slug":
            words = len([p for p in slug.split("-") if p])
            text = (f"the slug {_q(slug)} is {len(slug)} chars and {words} words: shorten it to ≤ {SLUG_WORDS} words and "
                    f"≤ {SLUG_CHARS} chars" + (f', keeping "{kw_slug}"' if kw_slug else ""))
        else:
            text = f"[{cid}] {c.get('messaggio', '')} Change only what this line names"
        steps.append((now, text))
    return steps


def print_next(steps: List[tuple], round_line: str = "") -> None:
    todo = [text for now, text in steps if now]
    later = [text for now, text in steps if not now]
    if todo:
        print(f"\nNEXT — fix only these, do not rewrite the rest{round_line}:")
        for n, text in enumerate(todo, 1):
            print(f"  {n}. {text}.")
    if later:
        print("No action needed now:")
        for text in later:
            print(f"  - {text}.")


# ---- commands -----------------------------------------------------------------------------------------------------


def cmd_key(a) -> int:
    if a.action == "show":
        cached = _read_cache()
        env_key = os.environ.get("TAROTS_API_KEY", "").strip()
        print(f"cache file:  {CACHE_PATH}")
        print(f"saved key:   {cached['key'][:12] + '...' if cached else '(none)'}"
              + (f"  url={cached.get('url')}" if cached else ""))
        if env_key:
            same = bool(cached) and cached.get("key") == env_key
            print(f"TAROTS_API_KEY: {env_key[:12]}...  ({'same as saved' if same else 'DIFFERENT from saved'})")
        else:
            print("TAROTS_API_KEY: (not set)")
        return EXIT_OK
    if a.action == "save":
        env_base = os.environ.get("TAROTS_API_URL", "").strip().rstrip("/")
        env_key = os.environ.get("TAROTS_API_KEY", "").strip()
        if not env_key.startswith("tk_live_"):
            raise Failure("TAROTS_API_KEY is not set to a tk_live_ key: nothing to save.", EXIT_CONFIG)
        if not env_base:
            raise Failure("TAROTS_API_URL is not set: nothing to pair the key with.", EXIT_CONFIG)
        old = _read_cache()
        _write_cache(env_base, env_key)
        if old and old.get("key") != env_key:
            print(f"replaced the saved key (was prefix {old['key'][:12]}...) with prefix {env_key[:12]}...")
        else:
            print(f"saved (prefix {env_key[:12]}...)")
        return EXIT_OK
    _clear_cache()
    print("saved key cleared")
    return EXIT_OK


def script_paths() -> Dict[str, str]:
    """Absolute paths of this script and of tarots_images.py (the sibling skill), and the Python running them.
    Agents ran `scripts/tarots_blog.py` from the work folder and then walked the whole disk to find it (5/10/2026):
    every command they need is printed with these absolute paths."""
    me = Path(__file__).resolve()
    images = me.parents[2] / "tarots-blog-images" / "scripts" / "tarots_images.py"
    return {"python": sys.executable, "blog": str(me), "images": str(images) if images.exists() else ""}


def print_script_paths() -> None:
    p = script_paths()
    print(f'note: run the scripts by these absolute paths, from any folder:\n  BLOG   = "{p["python"]}" "{p["blog"]}"',
          file=sys.stderr)
    if p["images"]:
        print(f'  IMAGES = "{p["python"]}" "{p["images"]}"', file=sys.stderr)
    else:
        print("  IMAGES = not found next to this skill: tarots-blog-images must sit in the same skills folder.",
              file=sys.stderr)


def cmd_guide(_a) -> int:
    show(call("GET", "/guide"))
    print_script_paths()
    # On stderr, so the JSON above stays parseable. Seen: an «autumn equinox» article written two weeks after it.
    print(f"note: today is {datetime.date.today().isoformat()} (this computer's clock): a timely topic falls in the "
          "next 14 days; a date already past is not timely. Verify every date with a page you open.", file=sys.stderr)
    return EXIT_OK


def cmd_sections(a) -> int:
    rows = call("GET", "/sections")
    if a.json:
        show(rows)
    else:
        for r in rows:
            print(f"{r['slug']:32} {r['percorso']}")
        if not rows:
            print("(no sections: publish without `section`)")
    return EXIT_OK


def cmd_tags(a) -> int:
    rows = call("GET", "/tags")
    if a.json:
        show(rows)
    else:
        for r in rows:
            print(f"{r['nome']} ({r['n']})")
        if not rows:
            print("(no tags yet)")
    return EXIT_OK


def cmd_catalog(a) -> int:
    data = call("GET", "/catalog")
    needle = (a.grep or "").lower()
    keep = lambda r: not needle or needle in r["slug"].lower() or needle in r["nome"].lower()  # noqa: E731
    cards, spreads = [r for r in data["carte"] if keep(r)], [r for r in data["stese"] if keep(r)]
    if a.json:
        show({"cards": cards, "spreads": spreads})
        return EXIT_OK
    for title, rows in (("Cards", cards), ("Spreads", spreads)):
        print(f"{title}:")
        for r in rows:
            print(f"  {r['scorciatoia']:36} {r['nome']}")
    return EXIT_OK


def cmd_mine(a) -> int:
    data = call("GET", "/posts", query={"stato": a.status, "pagina": a.page, "per_pagina": a.per_page})
    if a.json:
        show(data)
        return EXIT_OK
    print(f"{data['totale']} article(s), page {data['pagina']}")
    for p in data["articoli"]:
        print(f"  {p['id']}  {p['stato']:10} {p['lang']}  {p['slug']}  | {p['titolo']}  | keyword: {p.get('seo_parola_chiave') or '-'}")
    return EXIT_OK


# ---- every article of the blog, compact: titles and topic-check --------------------------------------------------
# `GET /titles` lists every article (any key's, the console's too) with a few fields. The list is copied to
# TITLES_CACHE_PATH and refreshed with `dal`: only what changed since the last run travels. An article deleted on the
# site cannot appear in a `dal` answer, so it leaves the copy only on a full reload: `--refresh`, or by itself when
# the copy is older than TITLES_FULL_EVERY (7 days).


def _utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def _parse_time(value: Any) -> Optional[datetime.datetime]:
    if not value:
        return None
    try:
        when = datetime.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return when if when.tzinfo else when.replace(tzinfo=datetime.timezone.utc)


def _identity() -> str:
    """The site and the key the copy belongs to (`mio` depends on the key): a different one means a full reload.
    Only the key's 12-character prefix is stored."""
    cfg = config()
    return f"{cfg['base']}|{cfg['key'][:12]}"


def _read_titles_cache() -> Optional[Dict[str, Any]]:
    try:
        data = json.loads(TITLES_CACHE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) and isinstance(data.get("articles"), dict) else None


def _write_titles_cache(data: Dict[str, Any]) -> None:
    TITLES_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = TITLES_CACHE_PATH.with_name(TITLES_CACHE_PATH.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, TITLES_CACHE_PATH)


def _fetch_titles(since: Optional[datetime.datetime]) -> Any:
    """Every page of `GET /titles`, archived ones included (the filters apply locally, on the copy). Returns the rows
    and the server's clock (`adesso`) at the first page, the starting point of the next `dal`."""
    rows: List[Dict[str, Any]] = []
    server_now = None
    page = 1
    while True:
        query: Dict[str, Any] = {"archiviati": "true", "pagina": page, "per_pagina": TITLES_PAGE}
        if since is not None:
            query["dal"] = since.isoformat()
        try:
            data = call("GET", "/titles", query=query)
        except NotFound:
            if page > 1:
                raise
            return _fetch_own_posts(), None
        if page == 1:
            server_now = data.get("adesso")
        batch = data.get("articoli") or []
        rows.extend(batch)
        if len(batch) < TITLES_PAGE or len(rows) >= int(data.get("totale") or 0):
            return rows, server_now
        page += 1


def _fetch_own_posts() -> List[Dict[str, Any]]:
    """Fallback for a server without `GET /titles` (older than this script): this key's articles from `GET /posts`,
    in the same shape as the rows of `/titles`. Said every time: the other keys' articles are missing. The copy is
    marked partial, so the first run against a newer server reloads it in full."""
    print("warning: this server has no GET /titles yet: topics are checked only against the articles of THIS key "
          "(`mine`), not the whole blog.", file=sys.stderr)
    rows: List[Dict[str, Any]] = []
    page = 1
    while True:
        data = call("GET", "/posts", query={"pagina": page, "per_pagina": 100})
        batch = data.get("articoli") or []
        for p in batch:
            rows.append({
                "id": p["id"], "slug": p.get("slug"), "titolo": p.get("titolo"),
                "estratto": p.get("sottotitolo") or p.get("seo_descrizione") or "",
                "parola_chiave": p.get("seo_parola_chiave"), "sezione": None, "lang": p.get("lang"),
                "stato": p.get("stato"), "pubblicato_il": p.get("pubblicato_il"), "aggiornato": p.get("aggiornato"),
                "mio": True, "tradotto_da_id": p.get("tradotto_da_id"),
            })
        if len(batch) < 100 or len(rows) >= int(data.get("totale") or 0):
            return rows
        page += 1


def sync_titles(*, refresh: bool = False) -> Dict[str, Any]:
    """The up-to-date copy of every article. Incremental (`dal`) when possible; a full reload with `refresh`, when
    there is no copy, when it belongs to another site or key, or when its last full reload is older than 7 days.
    If the API cannot be reached at all, an existing copy is used as it is, with a warning."""
    cache = _read_titles_cache()
    identity = _identity()
    full_at = _parse_time(cache.get("full_at")) if cache else None
    reason = None
    if refresh:
        reason = "--refresh"
    elif cache is None:
        reason = "no local copy yet"
    elif cache.get("identity") != identity:
        reason = "the copy is of another site or key"
    elif cache.get("partial"):
        reason = "the copy came from a server without GET /titles (only this key's articles)"
    elif full_at is None or _utcnow() - full_at > TITLES_FULL_EVERY:
        reason = "the copy is older than 7 days: this also drops deleted articles"
    try:
        if reason:
            rows, server_now = _fetch_titles(None)
            cache = {"version": 1, "identity": identity, "full_at": _utcnow().isoformat(timespec="seconds"), "articles": {}}
            print(f"note: titles reloaded in full ({reason}): {len(rows)} article(s).", file=sys.stderr)
        else:
            assert cache is not None and full_at is not None
            synced = _parse_time(cache.get("synced_at")) or full_at
            rows, server_now = _fetch_titles(synced - TITLES_OVERLAP)
    except Unreachable as exc:
        if cache is None or cache.get("identity") != identity:
            raise
        print(f"warning: {exc} Using the local copy as it is (synced {cache.get('synced_at')}): articles written "
              "since then are missing from it.", file=sys.stderr)
        return cache
    for row in rows:
        cache["articles"][str(row["id"])] = row
    # Only the fallback on `GET /posts` has no server clock: that copy holds this key's articles alone.
    cache["partial"] = server_now is None
    cache["synced_at"] = server_now or _utcnow().isoformat(timespec="seconds")
    _write_titles_cache(cache)
    return cache


def _plain(text: str) -> str:
    """Lowercase, no accents, only letters and digits separated by single spaces (`Crowley’s Æon` → `crowley s aeon`)."""
    text = unicodedata.normalize("NFKD", str(text or "")).replace("æ", "ae").replace("Æ", "ae").replace("œ", "oe")
    text = "".join(c for c in text if not unicodedata.combining(c)).lower()
    return " ".join(re.sub(r"[^0-9a-z]+", " ", text).split())


def _date_of(row: Dict[str, Any]) -> datetime.datetime:
    return _parse_time(row.get("pubblicato_il") or row.get("aggiornato")) or datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)


def _select_titles(cache: Dict[str, Any], *, lang: Optional[str] = None, statuses=("bozza", "pubblicato"),
                   section: Optional[str] = None, grep: Optional[str] = None) -> List[Dict[str, Any]]:
    """The articles of the copy that pass the filters, newest first. `grep` looks in title, slug, keyword and the
    short excerpt, ignoring case, accents and punctuation."""
    needle = _plain(grep) if grep else ""
    rows = []
    for row in cache["articles"].values():
        if lang and row.get("lang") != lang:
            continue
        if statuses and row.get("stato") not in statuses:
            continue
        if section and row.get("sezione") != section:
            continue
        if needle and needle not in _plain(" ".join(str(row.get(k) or "") for k in ("titolo", "slug", "parola_chiave", "estratto"))):
            continue
        rows.append(row)
    rows.sort(key=_date_of, reverse=True)
    return rows


def title_line(row: Dict[str, Any]) -> str:
    when = (row.get("pubblicato_il") or row.get("aggiornato") or "")[:10] or "-"
    return f"{row.get('slug')} | {row.get('titolo')} | {row.get('parola_chiave') or '-'} | {row.get('lang')} | {row.get('stato')} | {when}"


def _statuses(value: Optional[str]):
    return (STATUS.get(value, value),) if value else ("bozza", "pubblicato")


def cmd_titles(a) -> int:
    cache = sync_titles(refresh=a.refresh)
    rows = _select_titles(cache, lang=a.lang, statuses=_statuses(a.status), section=a.section, grep=a.grep)
    shown = rows if a.all else rows[:TITLES_SHOWN]
    if a.json:
        show(shown)
        return EXIT_OK
    print(f"# {len(rows)} of {len(cache['articles'])} article(s), newest first: slug | title | keyword | lang | status | date")
    for row in shown:
        print(title_line(row))
    if len(shown) < len(rows):
        print(f"# ... {len(rows) - len(shown)} more: narrow with --grep/--lang/--section, or add --all.")
    return EXIT_OK


#: Words that say nothing about the topic (English and Italian).
STOPWORDS = frozenset("""
a an the of in on at for to and or but with without by from about into onto over under as is are be been being it its
this that these those your you my our their his her how what why when where which who whom do does vs versus than
then so if not no can will should vs s t
il lo la i gli le un uno una di da con su per tra fra e ed o del della dei degli delle dello al alla ai agli alle
allo nel nella nei negli nelle nello sul sulla sui sugli sulle dal dalla dai dagli dalle che come cosa perche non si
ti mi ci vi sono dell dall nell sull all l d
""".split())
#: Words every article of this blog shares: they count, but much less than the rest («the Tower» is the topic,
#: «tarot card meaning» is not). Compared after the plural is taken off (cards → card).
WEAK_WORDS = frozenset({"tarot", "tarocchi", "tarocco", "thoth", "card", "carta", "carte", "meaning", "significato",
                        "significati", "deck", "mazzo"})
#: topic-check verdicts on the best score (0..1): TAKEN at or above TOPIC_TAKEN, CLOSE at or above TOPIC_CLOSE.
#: With `topic_similarity`: the same topic words (only the generic ones differ) score 0.85–1 → TAKEN from 0.88, i.e.
#: also when the generic words mostly agree («Tower tarot meaning» vs «The Tower Thoth card meanings», 0.91);
#: one extra topic word out of four («Celtic cross spread» + «for love») is 0.86 → CLOSE; half the topic words in
#: common («New moon spread» vs «Full moon spread») about 0.67 → CLOSE; one in three or less → FREE.
TOPIC_TAKEN, TOPIC_CLOSE = 0.88, 0.40


def _stem(word: str) -> str:
    if len(word) > 4 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 3 and word.endswith("s") and not word.endswith(("ss", "us", "is")):
        return word[:-1]
    return word


def topic_words(text: str) -> set:
    return {_stem(w) for w in _plain(text).split() if w not in STOPWORDS and len(w) > 1}


def _dice(a: set, b: set) -> float:
    return 2 * len(a & b) / (len(a) + len(b)) if a and b else 0.0


def topic_similarity(a: set, b: set) -> float:
    """0..1. The topic words (not weak) decide: their Dice overlap, times 0.85–1 depending on how much the weak words
    agree too. With no topic word in common the score is 0 («Death card meaning» is not «Tower card meaning»). When one
    side has only weak words, half their plain overlap."""
    if not a or not b:
        return 0.0
    strong_a, strong_b = a - WEAK_WORDS, b - WEAK_WORDS
    if not strong_a or not strong_b:
        return _dice(a, b) * (1.0 if not strong_a and not strong_b else 0.5)
    strong = _dice(strong_a, strong_b)
    weak_a, weak_b = a & WEAK_WORDS, b & WEAK_WORDS
    weak = _dice(weak_a, weak_b) if (weak_a or weak_b) else 1.0
    return strong * (0.85 + 0.15 * weak)


def topic_matches(topic: str, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Every article with its score against the topic, best first. The same slug, the same keyword or the same title
    (ignoring case, accents, punctuation, stop words and word order) is always 1.0 and marked `exact`."""
    plain = _plain(topic)
    slug = plain.replace(" ", "-")
    words = topic_words(topic)

    def same(text: Any) -> bool:
        return bool(text) and (plain == _plain(text) or (bool(words) and words == topic_words(text)))

    out = []
    for row in rows:
        exact = None
        if slug and slug == row.get("slug"):
            exact = "same slug"
        elif same(row.get("parola_chiave")):
            exact = "same keyword"
        elif same(row.get("titolo")):
            exact = "same title"
        score = 1.0 if exact else max(
            topic_similarity(words, topic_words(row.get(field) or "")) for field in ("titolo", "slug", "parola_chiave")
        )
        out.append({"score": round(score, 2), "exact": exact, "row": row})
    out.sort(key=lambda m: (m["score"], bool(m["exact"]), _date_of(m["row"])), reverse=True)
    return out


def topic_verdict(matches: List[Dict[str, Any]]) -> str:
    best = matches[0] if matches else None
    if best and (best["exact"] or best["score"] >= TOPIC_TAKEN):
        return "TAKEN"
    if best and best["score"] >= TOPIC_CLOSE:
        return "CLOSE"
    return "FREE"


def cmd_topic_check(a) -> int:
    topic = " ".join(a.topic).strip()
    if not _plain(topic):
        raise Failure("Give a proposed title or keyword, e.g. topic-check \"the hermit thoth tarot meaning\".", EXIT_USAGE)
    cache = sync_titles(refresh=a.refresh)
    rows = _select_titles(cache, lang=a.lang)
    matches = topic_matches(topic, rows)
    verdict = topic_verdict(matches)
    top = [m for m in matches[:5] if m["score"] > 0]  # a 0 shares no topic word: not worth a line
    if a.json:
        show({"topic": topic, "verdict": verdict, "score": top[0]["score"] if top else 0.0, "compared": len(rows),
              "matches": [{"score": m["score"], "exact": m["exact"], **m["row"]} for m in top]})
    else:
        print(f"# \"{topic}\" against {len(rows)} article(s) (drafts and published{', ' + a.lang if a.lang else ', every language'})")
        for m in top:
            print(f"{m['score']:.2f}  {title_line(m['row'])}" + (f"  [{m['exact']}]" if m["exact"] else ""))
        if not top:
            print("(no article shares a topic word with it)")
        explanation = {
            "TAKEN": f"an article on this already exists (score >= {TOPIC_TAKEN:.2f}, or the same slug, keyword or title). "
                     "Do not write it: choose another topic, or tell the operator the existing article could be updated.",
            "CLOSE": f"a similar article exists (score {TOPIC_CLOSE:.2f}-{TOPIC_TAKEN:.2f}). Write it only if the search "
                     "intent is really different from the articles above, and say so in the report.",
            "FREE": f"no article close to this (best score below {TOPIC_CLOSE:.2f}).",
        }[verdict]
        print(f"{verdict}: {explanation}")
    return EXIT_TAKEN if verdict == "TAKEN" else EXIT_OK


# ---- the focus keyword ------------------------------------------------------------------------------------------
# Seen on 5/10/2026: «balance tarot meditation autumn», a phrase nobody searches, then pasted into the H1 to make it
# appear. `check` and `post` refuse a keyword that cannot be a search phrase, or that another article already has.

KEYWORD_MAX_WORDS = 6
KEYWORD_RULE = (
    "A focus keyword is the phrase a person would really type into a search engine, in natural order, 2-5 words "
    "(\"samhain tarot spread\", not \"balance tarot meditation autumn\"). Choose it before writing, run "
    "`topic-check \"<keyword>\"`, then use the exact phrase in seo_title, seo_description, slug, the first paragraph "
    "and one `##` heading, inside natural sentences."
)


def keyword_problem(keyword: str) -> Optional[str]:
    """Why this cannot be a search phrase (too long, a word repeated), or None. Stop words may repeat."""
    words = _plain(keyword).split()
    if len(words) > KEYWORD_MAX_WORDS:
        return f"it is {len(words)} words (at most {KEYWORD_MAX_WORDS}, 2-5 is the target)"
    seen = set()
    for word in words:
        if word in STOPWORDS:
            continue
        if _stem(word) in seen:
            return f"it repeats the word \"{word}\""
        seen.add(_stem(word))
    return None


def keyword_taken(keyword: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """The article that already has this keyword (verdict TAKEN of `topic-check`, same language), or None. The
    article itself (same slug) does not count: `check` after `post` must not find its own draft."""
    cache = sync_titles()
    own = payload.get("slug") or slugify(str(payload.get("titolo") or ""), 160)
    rows = [r for r in _select_titles(cache, lang=payload.get("lang")) if r.get("slug") != own]
    matches = topic_matches(keyword, rows)
    return matches[0] if topic_verdict(matches) == "TAKEN" else None


def check_keyword(payload: Dict[str, Any]) -> None:
    keyword = str(payload.get("seo_parola_chiave") or "").strip()
    if not keyword:
        return  # the server reports it (parola_chiave), with its weight
    problem = keyword_problem(keyword)
    if problem:
        raise Failure(f"focus_keyword \"{keyword}\" refused: {problem}. {KEYWORD_RULE}", EXIT_KEYWORD)
    taken = keyword_taken(keyword, payload)
    if taken:
        why = taken["exact"] or f"score {taken['score']:.2f}"
        raise Failure(
            f"focus_keyword \"{keyword}\" is TAKEN ({why}) by: {title_line(taken['row'])}. One page per search intent: "
            "do not write a second one. Choose another topic and keyword with `topic-check`, or report that the "
            "existing article could be updated instead.", EXIT_TAKEN,
        )


def cmd_new(a) -> int:
    name = " ".join(a.name).strip()
    slug = slugify(name)
    if not slug:
        raise Failure("Give a slug or a working title, e.g. new \"samhain tarot spread\".", EXIT_USAGE)
    folder = work_root() / f"{datetime.date.today().isoformat()}-{slug}"
    existed = (folder / "article.json").exists()
    (folder / "foto").mkdir(parents=True, exist_ok=True)
    article, body = folder / "article.json", folder / "article.md"
    if not article.exists():
        article.write_text(json.dumps(skeleton(slug), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if not body.exists():
        body.write_text("", encoding="utf-8")
    paths = {"slug": slug, "folder": str(folder.resolve()), "article": str(article.resolve()),
             "body": str(body.resolve()), "foto": str((folder / "foto").resolve())}
    if a.json:
        show({**paths, "existed": existed})
        return EXIT_OK
    if existed:
        print("note: this work folder already exists: nothing was overwritten.")
    print(f"work folder: {paths['folder']}")
    print(f"article:     {paths['article']}   (fill every empty field)")
    print(f"text:        {paths['body']}   (Markdown, no `# H1`, sections start at `##`)")
    print(f"pictures:    {paths['foto']}   (tarots_images.py generate ... --article {slug})")
    p = script_paths()
    blog = f'"{p["python"]}" "{p["blog"]}"'
    images = f'"{p["python"]}" "{p["images"]}"' if p["images"] else "<tarots-blog-images not found next to this skill>"
    print("next commands (copy them as they are: absolute paths, they work from any folder):")
    print(f"  {blog} catalog --grep <word>")
    print(f"  {blog} check {slug}")
    print(f'  {images} generate --article {slug} --kind <k> --shot <s> --light <l> --setting "<place>" --prompt "<scene>"')
    print(f"  {blog} post {slug} --cover cover.jpg")
    return EXIT_OK


def cmd_check(a) -> int:
    path = resolve_article(a.article)
    rounds = read_rounds(path)
    if rounds.get("stopped"):
        print_stop(path, rounds, a.min_score)
        return EXIT_STOP
    payload = load_article(str(path))
    require_filled(payload, path)
    check_keyword(payload)
    seo = call("POST", "/seo-check", body={k: v for k, v in payload.items() if k != "dry_run"})
    ok = passes(seo, a.min_score)
    rounds["rounds"].append({"when": _utcnow().isoformat(timespec="seconds"), "score": seo["punteggio"]})
    n = len(rounds["rounds"])
    rounds["stopped"] = not ok and n > MAX_ROUNDS
    write_rounds(path, rounds)
    steps = next_steps(seo, payload)
    if a.json:
        show({**seo, "round": n, "max_rounds": MAX_ROUNDS, "pass": ok, "stop": rounds["stopped"],
              "next": [t for now, t in steps if now], "no_action": [t for now, t in steps if not now]})
    else:
        report(seo)
        if rounds["stopped"]:
            print_stop(path, rounds, a.min_score)
        elif ok:
            print(f"\nPASS (round {n}): {seo['punteggio']} ≥ {a.min_score} and no FIX. Do not polish further: go on "
                  "with the pictures and `post`.")
        else:
            last = " This was the last round: if the next check is still below, the article stops." if n == MAX_ROUNDS else ""
            print_next(steps, f" (round {n} of {MAX_ROUNDS})")
            print(f"Then run `tarots_blog.py check {path.parent.name[11:] if in_work_folder(path) else path}` again.{last}")
    if rounds["stopped"]:
        return EXIT_STOP
    return EXIT_OK if ok else EXIT_SCORE


def upload(path: str) -> Dict[str, Any]:
    file = Path(path)
    kind = IMAGE_TYPES.get(file.suffix.lower())
    if kind is None:
        raise Failure("The picture must be a PNG, JPEG or WebP file.", EXIT_USAGE)
    try:
        raw = file.read_bytes()
    except OSError as exc:
        raise Failure(f"Cannot read {file}: {exc.strerror}", EXIT_USAGE) from None
    if len(raw) > MAX_IMAGE_BYTES:
        raise Failure("The image is larger than 8 MB: export it smaller (the site scales it to 1600 px wide anyway).", EXIT_USAGE)
    return call("POST", "/media", raw=raw, content_type=kind)


# ---- the picture record shared with tarots-blog-images ---------------------------------------------------------
# Same file and keys as `tarots_images.py` (duplicated here on purpose: the two skills install separately).


def _progress() -> Dict[str, Any]:
    try:
        data = json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _save_progress(data: Dict[str, Any]) -> None:
    PROGRESS_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = PROGRESS_PATH.with_name(PROGRESS_PATH.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, PROGRESS_PATH)


def sha256_of(path: Any) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _lead(low: str) -> str:
    """The opening of a prompt, where a card is the subject: its first clause, or its first LEAD_WORDS content
    words if they run further."""
    clause = re.split(r"[,;:.!?()]|\s[-–—]\s", low, maxsplit=1)[0]
    end, n = len(low), 0
    for m in re.finditer(r"[a-z0-9]+(?:['-][a-z0-9]+)*", low):
        if m.group(0) not in LEAD_SKIP:
            n += 1
            if n == LEAD_WORDS:
                end = m.end()
                break
    return low[: max(len(clause), end)]


def card_problems(text: str) -> List[tuple]:
    """Every way the text makes cards the picture, as (family, words, what they name); [] when cards are at most
    context. The family SPREAD comes first when there is one."""
    low = " ".join(text.lower().split()).replace("’", "'")
    found = []
    for pattern, what, family in CARD_PATTERNS:
        m = re.search(pattern, low)
        if m:
            found.append((family, m.group(0), what))
    m = re.search(DECK, re.sub(NOT_A_CARD_DECK, " ", low))
    if m:
        found.append(("many", m.group(0), "a deck: many cards"))
    m = re.search(CARD_WORD, _lead(low))
    if m:
        found.append(("subject", m.group(0), f"a card as the subject: in the first clause or the first {LEAD_WORDS} words"))
    return found


def card_problem(text: str) -> Optional[str]:
    """The first way the text makes cards the picture, as «words» (what they name), or None."""
    found = card_problems(text)
    return f"«{found[0][1]}» ({found[0][2]})" if found else None


# ---- a card in the picture: only for an article about that very card ------------------------------------------
# Operator's rule (5/10/2026). In a test run Hermes added "one single small card" to the picture of «Tarot Meditation
# for Libra Season Balance», an article about no card, and out came a large Rider-Waite Fool. A card drawn in the
# picture (CARD_WORD: "card", "arcanum", "tarocco" in a prompt that `card_problems()` lets through) is allowed only
# when the article's title or focus keyword names that very card, when the prompt names it in the same phrase ("a
# single small card of the Tower") and draws it in the style of the Thoth deck, never as a copy of its artwork. The
# names of the cards as a world or a symbol, without the word "card" ("the energy of the Tower"), stay free.
# MAJOR_ARCANA, CONTEXT_NAMES, MINOR_RANKS, MINOR_SUITS, CARD_CONTEXT, NAME_GAP, NOT_A_CARD_NAME, COPY_OF_ARTWORK,
# CLAUSE_BREAK and the functions down to `card_rule_problems()` are the same in tarots_images.py and tarots_blog.py
# (a test in tarots-blog-publisher keeps them identical): change both together.

#: Each major arcanum: its Thoth name → every name it goes by (Thoth, Rider-Waite, Marseille, Italian), written plain
#: (lowercase, no accents, no punctuation). Adjustment = Justice, Lust = Strength, Art = Temperance, Aeon =
#: Judgement, Universe = World, Fortune = Wheel of Fortune, Magus = Magician, Priestess = High Priestess.
MAJOR_ARCANA = {
    "the Fool": ("fool", "matto", "folle"),
    "the Magus": ("magus", "magician", "mago", "bagatto", "bagatella"),
    "the Priestess": ("high priestess", "priestess", "papessa", "gran sacerdotessa", "sacerdotessa"),
    "the Empress": ("empress", "imperatrice"),
    "the Emperor": ("emperor", "imperatore"),
    "the Hierophant": ("hierophant", "pope", "papa", "ierofante"),
    "the Lovers": ("lovers", "amanti", "innamorati"),
    "the Chariot": ("chariot", "carro"),
    "Adjustment": ("adjustment", "justice", "giustizia", "regolazione"),
    "the Hermit": ("hermit", "eremita"),
    "Fortune": ("wheel of fortune", "ruota della fortuna", "fortune", "fortuna"),
    "Lust": ("lust", "strength", "lussuria", "forza"),
    "the Hanged Man": ("hanged man", "appeso", "impiccato"),
    "Death": ("death", "morte"),
    "Art": ("temperance", "temperanza", "art", "arte"),
    "the Devil": ("devil", "diavolo"),
    "the Tower": ("house of god", "maison dieu", "casa di dio", "tower", "torre"),
    "the Star": ("star", "stella"),
    "the Moon": ("moon", "luna"),
    "the Sun": ("sun", "sole"),
    "the Aeon": ("aeon", "eone", "judgement", "judgment", "giudizio"),
    "the Universe": ("universe", "world", "universo", "mondo"),
}
#: The names that are also common words («Full Moon tarot spread», «Sun sign», «the art of…»). They name a card
#: only within NAME_GAP words of a tarot word (CARD_CONTEXT: tarot, card, arcana, Thoth…) or when they are the whole
#: title («The Tower»). Every other name (Hierophant, High Priestess, Hanged Man, Ace of Cups, Knight of Wands…) is
#: unmistakable and counts anywhere.
CONTEXT_NAMES = frozenset("""
fool matto folle mago pope papa lovers amanti innamorati chariot carro adjustment justice giustizia regolazione
fortune fortuna lust strength lussuria forza appeso death morte art arte devil diavolo tower torre star stella moon
luna sun sole judgement judgment giudizio universe world universo mondo
""".split())
#: The minor arcana: rank and suit, each with the names it goes by. "Ace of Cups", "3 of Swords", "Asso di Coppe"…
#: The court cards are compared by name: the Thoth Knight is not the Rider-Waite Knight (the Thoth Prince is), so
#: only Page = Knave = Fante are the same card. A suit alone («the suit of Cups») is not one card.
MINOR_RANKS = {
    "Ace": ("ace", "1", "asso"), "Two": ("two", "2", "due"), "Three": ("three", "3", "tre"),
    "Four": ("four", "4", "quattro"), "Five": ("five", "5", "cinque"), "Six": ("six", "6", "sei"),
    "Seven": ("seven", "7", "sette"), "Eight": ("eight", "8", "otto"), "Nine": ("nine", "9", "nove"),
    "Ten": ("ten", "10", "dieci"), "Knight": ("knight", "cavaliere", "cavallo"), "Queen": ("queen", "regina"),
    "Prince": ("prince", "principe"), "Princess": ("princess", "principessa"), "King": ("king", "re"),
    "Page": ("page", "knave", "fante"),
}
MINOR_SUITS = {
    "Wands": ("wands", "wand", "rods", "staves", "batons", "bastoni"),
    "Cups": ("cups", "cup", "chalices", "coppe"),
    "Swords": ("swords", "sword", "spade"),
    "Disks": ("disks", "disk", "discs", "disc", "pentacles", "pentacle", "coins", "coin", "denari", "dischi", "pentacoli"),
}
#: The tarot words that make a common name («Moon», «Death») the name of a card when they are near it.
CARD_CONTEXT = r"\b(?:tarot\w*|tarocc\w*|cards?|carta|carte|arcan\w*|thoth|atu|trumps?)\b"
NAME_GAP = 4
#: Phrases with a card's name that are not the card (astrology, idioms, "the art of"): taken out before looking,
#: so «Full Moon tarot spread», «Sun sign tarot», «the art of tarot», «tarot fortune telling» name no card.
NOT_A_CARD_NAME = (
    r"\b(?:full|new|half|crescent|gibbous|waxing|waning|harvest|blue|blood|hunter s|hunters|wolf|snow|worm|pink"
    r"|strawberry|buck|sturgeon|corn|beaver|cold|super|dark|black)\s+moons?\b"
    r"|\b(?:moon|sun)\s+(?:signs?|phases?|cycles?|void|water|calendar|salutations?)\b"
    r"|\b(?:moon|sun|venus|mars|mercury)\s+in\s+(?:aries|taurus|gemini|cancer|leo|virgo|libra|scorpio|sagittarius"
    r"|capricorn|aquarius|pisces)\b"
    r"|\bstar\s+(?:signs?|seeds?|charts?|maps?)\b"
    r"|\b(?:shooting|falling|north|pole|morning|evening|lucky|guiding|rising|five pointed|six pointed)\s+stars?\b"
    r"|\b(?:rising|setting|midnight|midsummer)\s+suns?\b"
    r"|\bdeath\s+(?:anniversary|anniversaries|penalty|toll)\b|\bnear\s+death\b"
    r"|\bworld\s+(?:tarot\s+day|war|wide)\b|\b(?:around|across)\s+the\s+world\b"
    r"|\bfortune\s+tell\w*|\bfortunetell\w*|\bgood\s+fortune\b|\bbuona\s+fortuna\b"
    r"|\bart\s+of\b|\b(?:tarot|thoth|deck|card)\s+art\b"
    r"|\bart\s+(?:decks?|journals?|journaling|prints?|therapy|nouveau|deco|history)\b"
    r"|\barte\s+d(?:i|e[il]\w*)\b"
    r"|\bapril\s+fools?\b|\bfor\s+lovers\b"
    r"|\bluna\s+(?:piena|nuova|crescente|calante)\b|\bsegn[oi]\s+(?:del\s+)?sole\b"
)
#: A copy of a deck's artwork: never, not even of the article's own card (a new drawing in the Thoth style).
COPY_OF_ARTWORK = (r"\b(?:reproduc\w*|replicas?|replicating|exact\s+copy|faithful\s+copy|copy\s+of|copied\s+from"
                   r"|facsimile)\b")
#: Where a phrase of a prompt ends: the card shown is named in the same phrase as the word "card".
CLAUSE_BREAK = r"[,;:.!?()]|\s[-–—]\s"

_MAJOR_NAMES = sorted(((alias, card) for card, aliases in MAJOR_ARCANA.items() for alias in aliases),
                      key=lambda t: -len(t[0]))
_RANK_OF = {alias: rank for rank, aliases in MINOR_RANKS.items() for alias in aliases}
_SUIT_OF = {alias: suit for suit, aliases in MINOR_SUITS.items() for alias in aliases}
_MINOR_NAME = (r"\b(" + "|".join(sorted(_RANK_OF, key=len, reverse=True)) + r")\s+(?:of|di)\s+("
               + "|".join(sorted(_SUIT_OF, key=len, reverse=True)) + r")\b")
_ARTICLES = frozenset("the la il lo l le gli i".split())


def _card_plain(text: str) -> str:
    """Lowercase, no accents, only letters and digits separated by single spaces: how card names are looked for."""
    text = unicodedata.normalize("NFKD", str(text or "")).replace("æ", "ae").replace("Æ", "ae").replace("œ", "oe")
    text = "".join(c for c in text if not unicodedata.combining(c)).lower()
    return " ".join(re.sub(r"[^0-9a-z]+", " ", text).split())


def named_cards(text: str, *, need_context: bool = True) -> List[tuple]:
    """The cards named in `text`, as (card, word index), in order. A name that is also a common word (CONTEXT_NAMES)
    counts only near a tarot word or as the whole text, unless `need_context` is False (in a prompt, the word
    "card" next to it is the context). The phrases of NOT_A_CARD_NAME never count."""
    plain = re.sub(NOT_A_CARD_NAME, lambda m: " ".join("-" for _ in m.group(0).split()), _card_plain(text))
    words = plain.split()
    context = [plain[: m.start()].count(" ") for m in re.finditer(CARD_CONTEXT, plain)]
    whole = " ".join(w for n, w in enumerate(words) if not (n == 0 and w in _ARTICLES))
    taken: List[tuple] = []
    found: List[tuple] = []
    for m in re.finditer(_MINOR_NAME, plain):
        taken.append((m.start(), m.end()))
        found.append((plain[: m.start()].count(" "), f"the {_RANK_OF[m.group(1)]} of {_SUIT_OF[m.group(2)]}"))
    for alias, card in _MAJOR_NAMES:  # the longest first: «wheel of fortune» before «fortune»
        for m in re.finditer(r"\b" + re.escape(alias) + r"\b", plain):
            if any(s < m.end() and m.start() < e for s, e in taken):
                continue
            taken.append((m.start(), m.end()))
            first = plain[: m.start()].count(" ")
            last = first + alias.count(" ")
            if need_context and alias in CONTEXT_NAMES and whole != alias and not any(
                    first - NAME_GAP <= c < first or last < c <= last + NAME_GAP for c in context):
                continue
            found.append((first, card))
    return [(card, n) for n, card in sorted(found)]


def cards_of_article(texts: List[str]) -> List[str]:
    """The cards an article is about: those named in its title or its focus keyword, each once."""
    cards: List[str] = []
    for text in texts:
        for card, _n in named_cards(text or ""):
            if card not in cards:
                cards.append(card)
    return cards


def cards_shown(prompt: str) -> Optional[List[Optional[str]]]:
    """None when the prompt draws no card (no CARD_WORD); otherwise, for each "card" in it, the card named nearest
    to it in the same phrase (None when that phrase names none)."""
    low = " ".join(prompt.lower().split()).replace("’", "'")
    shown: List[Optional[str]] = []
    for m in re.finditer(CARD_WORD, low):
        start = max((b.end() for b in re.finditer(CLAUSE_BREAK, low[: m.start()])), default=0)
        stop = re.search(CLAUSE_BREAK, low[m.end():])
        before, after = low[start: m.start()], low[m.end(): m.end() + stop.start() if stop else len(low)]
        size = len(_card_plain(before).split())
        near = [(size - n, card) for card, n in named_cards(before, need_context=False)]
        near += [(n + 1, card) for card, n in named_cards(after, need_context=False)]
        shown.append(min(near)[1] if near else None)
    return shown or None


def shows_a_card(prompt: str) -> bool:
    """The prompt draws a card that `card_problems()` lets through: the card rule of the article applies."""
    return not card_problems(prompt) and cards_shown(prompt) is not None


def card_rule_problems(prompt: str, texts: List[str], title: str = "") -> tuple:
    """(problems, warnings) of the card a prompt draws, for the article whose title and focus keyword are `texts`.
    ([], []) when the prompt draws no card."""
    shown = cards_shown(prompt) if not card_problems(prompt) else None
    if shown is None:
        return [], []
    own = cards_of_article(texts)
    about = f"«{title}»" if title else "this article"
    if not own:
        return [f"this article is not about a specific card: no card in its picture; show its world instead "
                f"({about} names no card in its title or focus keyword; a card's name without the word «card», "
                "as a world or a symbol, stays allowed)"], []
    problems: List[str] = []
    named = []
    for card in shown:
        if card and card not in named:
            named.append(card)
    if None in shown:
        problems.append(f"the prompt draws a card without saying which: name it in the same phrase, e.g. «a single "
                        f"small card of {own[0]}» ({about} is about {', '.join(own)})")
    if len(named) > 1:
        problems.append(f"the prompt draws more than one card ({', '.join(named)}): one single small card at most")
    for card in named:
        if card not in own:
            problems.append(f"the card drawn ({card}) is not a card of this article ({about} is about "
                            f"{', '.join(own)}): only the article's own card may appear; show {card} as a world or "
                            "a symbol, without the word «card», or take it out")
    if re.search(COPY_OF_ARTWORK, _card_plain(prompt)):
        problems.append("it asks for a copy of a deck's artwork: the card is a new drawing in the style of the Thoth "
                        "deck, never a reproduction")
    warnings: List[str] = []
    if not problems and not re.search(r"\bthoth\b", _card_plain(prompt)):
        warnings.append("the prompt does not say the card is in the style of the Thoth deck: add «in the style of "
                        "the Thoth deck» (a new drawing, not a copy; never Rider-Waite or Marseille), or the model "
                        "paints the deck it knows best")
    return problems, warnings


def _used_by(data: Dict[str, Any], sha: str) -> Optional[str]:
    """The article a picture already belongs to: from `_used`, or from the per-article records of
    `tarots_images.py` (older ones without a hash are hashed from their file, if it is still there)."""
    entry = (data.get("_used") or {}).get(sha)
    if isinstance(entry, dict) and entry.get("post"):
        return str(entry["post"])
    for post_id, riga in data.items():
        if post_id.startswith("_") or not isinstance(riga, dict):
            continue
        for e in ([riga.get("cover")] if riga.get("cover") else []) + list(riga.get("inline") or []):
            if e.get("sha256") == sha or (not e.get("sha256") and e.get("file") and Path(e["file"]).is_file()
                                          and sha256_of(e["file"]) == sha):
                return post_id
    return None


def article_texts(arg: str) -> Optional[tuple]:
    """(title and focus keyword, title) of the article `arg` (a slug or an id): from its work folder's article.json,
    else from the titles copy (TITLES_CACHE_PATH). None when neither knows it. Nothing is asked to the API."""
    folder = find_work_folder(slugify(arg))
    if folder is not None:
        try:
            data = json.loads((folder / "article.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            data = {}
        if isinstance(data, dict):
            title = data.get("title") or data.get("titolo") or ""
            texts = [t for t in (title, data.get("focus_keyword") or data.get("seo_parola_chiave")) if t]
            if texts:
                return texts, title
    cache = _read_titles_cache() or {"articles": {}}
    rows = [r for r in cache["articles"].values()
            if isinstance(r, dict) and (str(r.get("id")) == arg or r.get("slug") in (arg, slugify(arg)))]
    texts = [t for r in rows for t in (r.get("titolo"), r.get("parola_chiave")) if t]
    return (texts, rows[0].get("titolo") or "") if texts else None


def check_card_in_picture(path: str, prompt: str, *, article: Optional[str], about: Optional[tuple]) -> None:
    """The card rule of the article (see `card_rule_problems`): a prompt that draws a card is accepted only for an
    article about that very card. `about` is (texts, title) when the article is at hand (`post`)."""
    if not shows_a_card(prompt):
        return
    if about is None and article:
        about = article_texts(article)
    if about is None:
        why = ("no article was given (add --for SLUG_OR_ID)" if not article else
               f"the article {article} was not found in the work folders or in the titles copy (`titles` refreshes it)")
        raise Failure(f"{path} was generated from a prompt that draws a card, and {why}: a card may appear only in "
                      "the picture of an article about that very card.", EXIT_RULE)
    problems, _warnings = card_rule_problems(prompt, about[0], about[1])
    if problems:
        raise Failure(f"{path} was generated from a prompt that draws a card: {problems[0]}. Generate a new one.",
                      EXIT_RULE)


def check_picture(path: str, *, article: Optional[str], operator_image: bool, about: Optional[tuple] = None) -> str:
    """Refuse a picture before it is uploaded; return its sha256. `article` is the slug or id it is for (None for a
    new article: then any earlier use is another article's); `about` is (title and focus keyword, title) of the
    article when it is at hand, for the card rule."""
    if IMAGE_TYPES.get(Path(path).suffix.lower()) is None:  # a usage error first: the record cannot fix a GIF
        raise Failure("The picture must be a PNG, JPEG or WebP file.", EXIT_USAGE)
    if not Path(path).is_file():
        raise Failure(f"Cannot read {path}.", EXIT_USAGE)
    sha = sha256_of(path)
    data = _progress()
    other = _used_by(data, sha)
    if other and other != article:
        raise Failure(f"{path} is already a picture of article {other}: every article gets its own picture. "
                      "Generate a new one with tarots_images.py generate.", EXIT_RULE)
    generated = [e for e in data.get("_generated") or [] if isinstance(e, dict) and e.get("sha256") == sha]
    sidecar = Path(path + ".prompt.txt")
    prompts = [e.get("prompt") or "" for e in generated] + ([sidecar.read_text(encoding="utf-8")] if sidecar.is_file() else [])
    for prompt in prompts:
        if card := card_problem(prompt):
            raise Failure(f"{path} was generated from a prompt that makes cards the picture ({card}): a blog picture "
                          "is never a picture of cards (cards may only be context). Generate a new one.", EXIT_RULE)
        check_card_in_picture(path, prompt, article=article, about=about)
    if not generated:
        if not operator_image:
            raise Failure(
                f"{path} was not made by `tarots_images.py generate` (skill tarots-blog-images, LitMedia): blog "
                "pictures come only from there. If the operator supplied this very picture, add --operator-image.",
                EXIT_RULE,
            )
        print(f"warning: {path} is accepted as a picture supplied by the operator (--operator-image): make sure it "
              "shows no card and is not used by another article.", file=sys.stderr)
    return sha


def record_picture(sha: str, path: str, *, article: str, kind: str, slug: Optional[str] = None) -> None:
    data = _progress()
    entry = {"post": article, "kind": kind, "file": path,
             "when": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
    if slug:
        entry["slug"] = slug
    data.setdefault("_used", {})[sha] = entry
    _save_progress(data)


def cmd_upload(a) -> int:
    folder = find_work_folder(slugify(a.for_article)) if a.for_article else None
    picture = resolve_picture(a.image, folder)
    sha = check_picture(picture, article=a.for_article, operator_image=a.operator_image)
    image = upload(picture)
    record_picture(sha, picture, article=a.for_article or f"(upload {image['id']})", kind="upload")
    if a.json:
        show(image)
    else:
        print(f"uploaded: id={image['id']} {image['larghezza']}x{image['altezza']} ({image['byte']} bytes)")
        print(f"url: {image.get('url')}")
        print(f'as the cover: "cover_image_id": "{image["id"]}"   inside the text: ![what the picture shows]({image.get("url")})')
    return EXIT_OK


def cmd_post(a) -> int:
    path = resolve_article(a.article)
    rounds = read_rounds(path)
    if rounds.get("stopped"):
        print_stop(path, rounds, a.min_score)
        return EXIT_STOP
    payload = load_article(str(path))
    require_filled(payload, path)
    cover = resolve_picture(a.cover, in_work_folder(path)) if a.cover else None
    title = str(payload.get("titolo") or "")
    about = ([t for t in (title, payload.get("seo_parola_chiave")) if t], title)
    sha = check_picture(cover, article=None, operator_image=a.operator_image, about=about) if cover else None
    check_keyword(payload)
    if cover:
        image = upload(cover)
        payload["immagine_id"] = image["id"]
        print(f"cover uploaded: {image['id']}", file=sys.stderr)
    payload.pop("dry_run", None)
    trial = call("POST", "/posts", body={**payload, "dry_run": True})
    seo = trial["seo"]
    report(seo)
    if not passes(seo, a.min_score):
        if not a.save_anyway:
            print_next(next_steps(seo, payload))
            print(f"Not saved: the score is below {a.min_score}, or a FIX is left. Fix only the items above and run "
                  f"`check` again (or use --save-anyway, only if the operator asked it for this article).", file=sys.stderr)
            return EXIT_SCORE
        payload["stato"] = "bozza"
        payload.pop("pubblicato_il", None)
        print("Saving as a draft because of --save-anyway.", file=sys.stderr)
    if a.dry_run:
        print("dry run: nothing saved")
        return EXIT_OK
    result = call("POST", "/posts", body=payload)
    article = result["articolo"]
    if sha:
        record_picture(sha, cover, article=str(article["id"]), kind="cover", slug=article.get("slug"))
    if a.json:
        show(result)
    else:
        print(f"saved: id={article['id']} status={article['stato']} lang={article['lang']}")
        print(f"url:   {result['url']}" + ("" if article["stato"] == "pubblicato" else "   (not public until an editor publishes it)"))
        for warning in result.get("avvisi", []):
            print(f"note:  {warning}")
    return EXIT_OK


def cmd_update(a) -> int:
    payload = load_article(str(resolve_article(a.patch, "patch.json")))
    if "dry_run" in payload:
        # PATCH has no dry run: the server would ignore the field and save the change anyway.
        raise Failure("`update` has no dry run: remove `dry_run` from the patch, and run `check` on the full article "
                      "first if you want the SEO report before saving.", EXIT_USAGE)
    result = call("PATCH", f"/posts/{urllib.parse.quote(a.id)}", body=payload)
    if a.json:
        show(result)
    else:
        article = result["articolo"]
        print(f"updated: id={article['id']} status={article['stato']}  url: {result['url']}")
        report(result["seo"])
        for warning in result.get("avvisi", []):
            print(f"note:  {warning}")
    return EXIT_OK


def cmd_delete(a) -> int:
    call("DELETE", f"/posts/{urllib.parse.quote(a.id)}")
    print("deleted")
    return EXIT_OK


# ---- entry point ----------------------------------------------------------------------------------------------------


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="tarots_blog.py", description=__doc__.split("\n\n")[0])
    p.add_argument("--json", action="store_true", help="print the raw JSON instead of a summary")
    sub = p.add_subparsers(dest="command", required=True)

    ky = sub.add_parser("key", help="the locally saved key: show it (prefix only), save one, or forget it")
    ky.add_argument("action", choices=["show", "save", "clear"])
    ky.set_defaults(run=cmd_key)
    sub.add_parser("guide", help="what the blog accepts and the SEO thresholds").set_defaults(run=cmd_guide)
    sub.add_parser("sections", help="sections articles can go in").set_defaults(run=cmd_sections)
    sub.add_parser("tags", help="tags already in use").set_defaults(run=cmd_tags)
    c = sub.add_parser("catalog", help="cards and spreads with their link shortcuts")
    c.add_argument("--grep", help="only entries whose slug or name contains this text")
    c.set_defaults(run=cmd_catalog)
    m = sub.add_parser("mine", help="articles this key created")
    m.add_argument("--status", choices=["bozza", "pubblicato", "archiviato"])
    m.add_argument("--page", type=int, default=1)
    m.add_argument("--per-page", type=int, default=25)
    m.set_defaults(run=cmd_mine)
    t = sub.add_parser(
        "titles", help="one line per article of the WHOLE blog (any author): slug | title | keyword | lang | status | date",
        description=(
            "Every article of the blog, whoever wrote it, one compact line each, newest first. The list is kept in a "
            f"local copy ({TITLES_CACHE_PATH}) that each run brings up to date with only what changed since the last "
            "one. An article DELETED on the site is not reported by that update: it leaves the copy only on a full "
            "reload, which --refresh forces and which happens by itself when the last one is older than 7 days. "
            "Never download whole articles to find out what exists: use this and topic-check."
        ),
    )
    t.add_argument("--lang", help="only this language (en, it, ...)")
    t.add_argument("--status", choices=["draft", "published", "archived", "bozza", "pubblicato", "archiviato"],
                   help="only this status (default: drafts and published, not archived)")
    t.add_argument("--section", metavar="SLUG", help="only this section (slug, see `sections`)")
    t.add_argument("--grep", metavar="TEXT", help="only articles whose title, slug, keyword or excerpt contain TEXT")
    t.add_argument("--all", action="store_true", help=f"print every matching line (default: the newest {TITLES_SHOWN})")
    t.add_argument("--refresh", action="store_true", help="reload the whole list (drops articles deleted on the site)")
    t.add_argument("--json", action="store_true", default=argparse.SUPPRESS, help="the rows as JSON")
    t.set_defaults(run=cmd_titles)
    tc = sub.add_parser(
        "topic-check", help="is a proposed topic already covered? the 5 closest articles and FREE / CLOSE / TAKEN",
        description=(
            "Compares a proposed title or keyword with the title, slug and keyword of every draft and published "
            "article (from the up-to-date local copy of `titles`), ignoring case, accents, punctuation, English and "
            "Italian stop words; 'tarot', 'thoth', 'card', 'meaning' (and 'deck') weigh little. Prints the 5 closest "
            f"with a score 0-1 and a verdict: TAKEN (score >= {TOPIC_TAKEN:.2f}, or the same slug, keyword or title: "
            f"exit code {EXIT_TAKEN}), CLOSE ({TOPIC_CLOSE:.2f} to {TOPIC_TAKEN:.2f}: write it only for a really "
            f"different search intent, exit 0), FREE (below {TOPIC_CLOSE:.2f}, exit 0)."
        ),
    )
    tc.add_argument("topic", nargs="+", help="the proposed title or focus keyword (quoted or not)")
    tc.add_argument("--lang", help="compare only with articles in this language (default: every language)")
    tc.add_argument("--refresh", action="store_true", help="reload the whole list first")
    tc.add_argument("--json", action="store_true", default=argparse.SUPPRESS, help="the result as JSON")
    tc.set_defaults(run=cmd_topic_check)

    nw = sub.add_parser(
        "new", help="create the work folder of one article (article.json, article.md, foto/) and print its paths",
        description=(
            "Creates <work root>/<YYYY-MM-DD>-<slug>/ with an article.json skeleton (empty SEO fields, status draft, "
            "body_file article.md), an empty article.md and foto/ for every picture of the article. The work root is "
            "~/.tarots-blog/work, or TAROTS_WORK_DIR. An existing folder is never overwritten. Every other command "
            "then accepts the slug instead of a path."
        ),
    )
    nw.add_argument("name", nargs="+", help="the slug or a working title (made into a slug)")
    nw.set_defaults(run=cmd_new)
    k = sub.add_parser(
        "check", help="SEO report without saving, then NEXT: the exact fixes",
        description=(
            "ARTICLE is a slug, a work folder or an article.json. Prints the score, the open items and NEXT (one "
            f"concrete instruction per item). Rounds are counted in the work folder ({ROUNDS_FILE}): the "
            f"{MAX_ROUNDS + 1}th check still below the score prints STOP and exits {EXIT_STOP}; from then on check and "
            "post refuse the article."
        ),
    )
    k.add_argument("article", metavar="ARTICLE")
    k.add_argument("--min-score", type=int, default=85)
    k.set_defaults(run=cmd_check)
    u = sub.add_parser("upload", help="upload a cover or inline image, print its id/url")
    u.add_argument("image")
    u.add_argument("--for", dest="for_article", metavar="SLUG_OR_ID",
                   help="the article this picture is for (recorded, so it is never used for another one)")
    u.add_argument("--operator-image", action="store_true",
                   help="accept a picture the operator supplied, not made by tarots_images.py generate")
    u.set_defaults(run=cmd_upload)
    r = sub.add_parser("post", help="check, then create the article")
    r.add_argument("article", metavar="ARTICLE", help="a slug, a work folder or an article.json")
    r.add_argument("--cover", help="an image file made by tarots_images.py generate (a bare name is looked for in the "
                                   "work folder's foto/), to upload and use as the cover")
    r.add_argument("--operator-image", action="store_true",
                   help="the --cover file was supplied by the operator, not made by tarots_images.py generate")
    r.add_argument("--min-score", type=int, default=85, help="refuse to save below this SEO score (default 85)")
    r.add_argument("--save-anyway", action="store_true", help="below the score, keep it as a draft instead of refusing")
    r.add_argument("--dry-run", action="store_true", help="check only; save nothing")
    r.set_defaults(run=cmd_post)
    x = sub.add_parser("update", help="change fields of an article this key created")
    x.add_argument("id")
    x.add_argument("patch")
    x.set_defaults(run=cmd_update)
    d = sub.add_parser("delete-draft", help="delete a draft this key created")
    d.add_argument("id")
    d.set_defaults(run=cmd_delete)
    return p


def main(argv: Optional[List[str]] = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass
    args = parser().parse_args(argv)
    try:
        return args.run(args)
    except Failure as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exc.code


if __name__ == "__main__":
    sys.exit(main())
