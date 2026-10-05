#!/usr/bin/env python3
"""tarots_images.py: redo the images of TAROTS chat blog articles (cover and inline) through the REST API (v1).

Standard library only (Python 3.8+), plus the separate `litmedia-skill` for generating pictures. Configuration comes
from the environment, or from a small local cache this tool manages — never from a command argument or a prompt:

    TAROTS_API_URL     the API base, e.g. https://tarots.chat/api   (https only; http is accepted for localhost)
    TAROTS_MEDIA_KEY   a `tk_live_...` key with the `blog:media` permission (console: Blog > Keys > "Change images")
    LITMEDIA_SKILL     optional: the litmedia-skill folder (default: ~/.claude/skills/litmedia-skill, then
                       ~/.agents/skills/litmedia-skill, then %LOCALAPPDATA%/hermes/skills/litmedia-skill)
    LITMEDIA_PYTHON    optional: the Python that runs LitMedia's scripts. Otherwise the first that can import
                       `requests` and `dotenv` among: this script's Python, `py -3.12`, `py -3`, python3, python and
                       (Windows) %LOCALAPPDATA%/Programs/Python/Python3*/python.exe, newest first. None: exit 5 with
                       the pip command to run; nothing is installed by this script
    TAROTS_WORK_DIR    optional: the root of the articles' work folders (default ~/.tarots-blog/work)

The key is remembered in `~/.tarots-blog/media-credentials.json` (or `TAROTS_MEDIA_KEY_CACHE`), outside any
repository, the same way `tarots_blog.py` remembers its own. A `blog:media` key can touch **only images** — cover
and inline pictures — of any article, published or not; it cannot change text, SEO fields or status.

Commands (run `tarots_images.py <command> -h` for the options):

    key show|save|clear     the saved key: prefix and origin, save the one in TAROTS_MEDIA_KEY, or forget it
    list [--todo]           every article with its cover and inline images (--todo: not redone yet by this tool)
    show ID                 one article with its full text: read it before writing a prompt
    balance                 LitMedia credits left
    catalog                 the values of --kind, --shot and --light, and which ones are free for the next picture
    prompt-check --prompt P --kind K --shot S --light L --setting TEXT [--alt TEXT] [--article SLUG_OR_ID]
                            every check `generate` makes on a prompt, offline: nothing generated, nothing spent
                            (only a prompt that draws a card may ask the API for its article, see below)
    generate --prompt P --kind K --shot S --light L --setting TEXT (--article SLUG_OR_ID | --out FILE) [--aspect 3:2]
             [--resolution 2K] [--budget N] [--dry-run]
                            one picture with Seedream 5.0 through litmedia-skill (checks the prompt, then the balance).
                            With --article, or a bare --out name, it goes in the article's work folder:
                            ~/.tarots-blog/work/<YYYY-MM-DD>-<slug>/foto/ (TAROTS_WORK_DIR moves the root), as
                            cover.jpg (3:2) or inline-N.jpg unless --out names it. An existing file is never overwritten
    cover ID FILE --alt TEXT [--dry-run]
                            replace the cover
    inline ID [--replace N FILE ALT] [--add AFTER_PARAGRAPH FILE ALT] [--remove N] [--dry-run]
                            replace, add or remove pictures inside the text (N = 0 for the first picture)
    progress                the last 20 pictures generated with their four dimensions, what is free next, and what
                            this tool has already redone

The picture rules, checked before anything is generated or sent (`--dry-run` included), with no option to skip them:
    - never a picture OF cards: no card as the subject (at the start of the prompt, in its first clause or its first
      8 content words, a close-up of a card), no two or more cards (cards, a deck, a pile, the arcana), no spread or
      layout (cards on a table, a reading, a fan of cards, cards face down), no hands holding or turning a card.
      Cards may stay in the context: "tarot" as an adjective, the names of cards as a world or a symbol ("the energy
      of the Tower", without the word "card"). An alt text that describes a spread is refused; one that mentions a
      card otherwise gets a warning;
    - a card drawn in the picture (the word "card" later in the scene, one single small card) only for an article
      about that very card: --article is required, its title or focus keyword must name the card (work folder,
      then the titles copy ~/.tarots-blog/titles-cache.json, then the API with the media key), the prompt names
      it in the same phrase ("a single small card of the Tower") and the card is drawn in the style of the Thoth
      deck (a warning when the prompt does not say so; never a copy, never Rider-Waite or Marseille);
    - a concrete scene: at least 12 content words once the house style line and the empty words are taken out;
    - a new form: four dimensions are declared for every picture (--kind, --shot, --light from the catalogs below,
      --setting in free text) and recorded; the kind of the last 3 pictures, a kind+shot pair of the last 20, the
      light of the last 2 (firelight: of the last 10) and a setting of the last 10 are refused. The prompt must show
      the declared light and composition (the setting is recorded, not required in the text);
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
import unicodedata
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
#: made from one fixed prompt per section. The operator's rule: **a blog picture is never a picture of cards**.
#: Cards may stay in the context — the blog is about tarot, and the names of the cards (the Sun, the Tower, the
#: Queen of Cups, the Wands…) are the very world the pictures show — but never as the subject, never more than one,
#: never laid out, never in a hand. Each entry: (pattern, what it names, family). The family "spread" is the only
#: one that also refuses an alt text; the others only warn about it (an alt may carry the article's keyword).
#: `tarots-blog-publisher/scripts/tarots_blog.py` keeps a copy of these patterns, of CARD_WORD, LEAD_WORDS,
#: LEAD_SKIP, DECK and NOT_A_CARD_DECK and of `card_problems()` for the pictures it uploads, and of the card rule
#: of the article (MAJOR_ARCANA… `card_rule_problems()`, below); a test there checks that the two stay identical:
#: change both together.
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
#: A card named as such: in the first clause or among the first LEAD_WORDS content words it is the subject.
CARD_WORD = r"\bcard\b|\barcanum\b|\btarocco\b"
LEAD_WORDS = 8
#: Words that do not count among the first LEAD_WORDS of a prompt: grammar, not content.
LEAD_SKIP = frozenset("""
a an the and or but of in on at to with by for from into onto over under above below behind beside between through
across around along near its it their her his this that these those there is are was were be as while very some one
single just only
""".split())
#: "deck" is a card deck unless it is a ship's, a garden's or a deck chair: those phrases are taken out first.
#: ("wooden deck" stays refused on purpose: it reads as a box of cards as easily as a terrace. Say "terrace".)
DECK = r"\bdecks?\b"
NOT_A_CARD_DECK = (
    r"\b(?:ship's|ships|ship|boat's|boat|ferry|yacht|sailing|sailboat|liner|steamer|barge|vessel|upper|lower|top|main"
    r"|sun|pool|observation|promenade|garden|porch|patio|terrace)\s+decks?\b"
    r"|\bdecks?\s+chairs?\b|\bdeckchairs?\b|\bon\s+deck\b"
    r"|\bdecks?\s+of\s+(?:a|an|the)\s+(?:\w+\s+){0,2}(?:ship|boat|ferry|yacht|sailboat|liner|steamer|vessel|barge)s?\b"
    # the style of the card of an article about it (see card_rule_problems): a style, not a deck in the picture
    r"|\bstyle\s+of\s+(?:the\s+)?thoth\s+(?:tarot\s+)?decks?\b"
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

#: The form of a picture, declared with four options of `generate` and `prompt-check` and kept in `_generated`:
#: what it shows (KINDS), how it is framed (SHOTS), its light (LIGHTS) and where or when it is (--setting, free
#: text). 17 kinds × 12 shots × 10 lights = 2,040 forms before the setting, which has no end. The subject stays
#: what the article is about: the dimensions only keep the form from repeating.
KINDS = {
    "landscape": "open land: a coast, a field, a mountain pass, a valley",
    "sky-and-weather": "the sky and what it does: clouds, rain, wind, a rainbow, snow falling",
    "architecture": "a building or a structure seen from outside: a lighthouse, a bridge, a cloister, a tower",
    "interior": "a room or an inside place: a kitchen, a library, a greenhouse, a stairwell",
    "street-or-market": "public everyday life: a street, a market, a station, a harbour front",
    "figure-from-behind": "one or two people seen from behind, near enough to read the gesture, no face",
    "figure-at-distance": "a person small in a large space, never recognisable",
    "hands-and-gesture": "hands doing something the article speaks of: planting, writing, holding a cup (never cards)",
    "still-life-object": "one object charged with meaning, alone and well lit: a key, a letter, two rings",
    "nature-macro": "a natural detail very close: a seed head, frost on a leaf, bark, a shell",
    "animal": "an animal that carries the article's meaning: a heron, a fox in snow, bees, a horse",
    "water-and-reflection": "a sea, a river, a pool or a puddle, and what it mirrors",
    "celestial": "the moon, the planets, the stars or an eclipse as the subject",
    "ritual-or-craft": "making or rite: weaving, pottery, bread, a procession, a lit offering",
    "abstract-symbol": "a visual metaphor: threads, doors, lights in a pattern, a labyrinth",
    "map-or-diagram": "a drawn map, a sky chart or a plan, with no readable letters or numbers",
    "journey-or-path": "a road, a path, steps, a crossing, a boat leaving",
}
#: Composition: name → (what it is, the words that show it in the prompt; one of them must be there).
SHOTS = {
    "wide": ("the whole place, the subject small in it",
             ("wide", "wide view", "wide shot", "panoramic", "panorama", "vast", "seen from afar", "seen from a distance",
              "far away", "in the distance")),
    "close-up": ("the subject fills the frame",
                 ("close-up", "closeup", "close view", "up close", "tight framing", "detail of", "seen close")),
    "macro": ("closer than the eye: texture, drops, fibres",
              ("macro", "extreme close-up", "magnified", "tiny details", "macro view")),
    "aerial": ("from high above, the land as a pattern",
               ("aerial", "bird's eye", "bird's-eye", "from high above", "from the air", "seen from above",
                "high above", "drone view")),
    "low-angle": ("from below, looking up at the subject",
                  ("low angle", "low-angle", "from below", "looking up", "worm's eye", "from the ground up",
                   "seen from beneath")),
    "silhouette": ("the subject dark against a bright sky or window",
                   ("silhouette", "silhouetted", "backlit", "against the light", "dark outline")),
    "through-a-window-or-doorway": ("seen through a frame in the foreground",
                                    ("through a window", "through the window", "through a doorway", "through the doorway",
                                     "through an open door", "through the open door", "through an arch",
                                     "framed by a window", "framed by a doorway", "framed by an arch", "window frame",
                                     "door frame")),
    "reflection": ("the subject seen in water, glass or a mirror",
                   ("reflection", "reflected", "reflecting", "mirrored", "mirror", "doubled in the water")),
    "symmetrical": ("centred, the two halves answering each other",
                    ("symmetrical", "symmetry", "symmetric", "centred", "centered", "perfectly balanced")),
    "off-centre-negative-space": ("a small subject to one side, much empty space",
                                  ("off-centre", "off-center", "negative space", "empty space", "to one side",
                                   "small in the frame", "open space around")),
    "over-the-shoulder": ("behind a person, seeing what they see",
                          ("over the shoulder", "over her shoulder", "over his shoulder", "over their shoulder",
                           "over-the-shoulder")),
    "top-down": ("straight down on a surface or the ground",
                 ("top-down", "top down", "from directly above", "straight down", "overhead view", "flat lay",
                  "seen from overhead")),
}
#: Light: name → (what it is, the words that show it in the prompt; one of them must be there).
LIGHTS = {
    "dawn": ("first light, cool and clean", ("dawn", "sunrise", "daybreak", "first light", "early morning")),
    "golden-hour": ("low warm sun, long shadows",
                    ("golden hour", "golden light", "late afternoon", "low sun", "sunset", "evening sun", "setting sun")),
    "midday": ("high sun, short shadows, bright colours",
               ("midday", "noon", "high sun", "noonday", "full daylight", "bright daylight", "overhead sun")),
    "overcast": ("soft grey light, no shadows, often rain",
                 ("overcast", "cloudy", "grey sky", "gray sky", "grey light", "diffused light", "soft rain", "drizzle",
                  "rain")),
    "blue-hour": ("after sunset, deep blue sky, first lamps",
                  ("blue hour", "dusk", "twilight", "after sunset", "nightfall", "gloaming")),
    "moonlight": ("night lit by the moon", ("moonlight", "moonlit", "full moon", "crescent moon", "moon")),
    "starlight": ("night under the stars, no moon", ("starlight", "starlit", "starry", "stars", "milky way")),
    "storm-light": ("dark sky and sudden brightness", ("storm", "stormy", "lightning", "thunder", "thunderclouds", "gale")),
    "fog-or-mist": ("the far things fade into white", ("fog", "foggy", "mist", "misty", "haze", "hazy")),
    "firelight": ("candles, lamps, a hearth: rare on this blog",
                  ("firelight", "fire", "candlelight", "candle", "candles", "candlelit", "lamplight", "lantern light",
                   "hearth", "embers", "bonfire", "torchlight")),
}
KIND_GAP = 3         # a kind cannot be the kind of any of the last 3 pictures
PAIR_GAP = 20        # a kind+shot pair cannot repeat within the last 20
LIGHT_GAP = 2        # a light cannot be the light of the last 2
RARE_LIGHTS = {"firelight": 10}  # and these not at all if used within the last N
SETTING_GAP = 10     # a setting (normalized) cannot repeat within the last 10
SHOWN_IN_PROGRESS = 20
MAX_SETTING_CHARS, MAX_SETTING_WORDS = 80, 8


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
#     "_generated": [{"prompt", "file", "sha256", "aspect", "when",          every picture `generate` made, oldest first
#                     "kind", "shot", "light", "setting"}, ...]            (the four dimensions: only in newer entries)
#     "_used":      {sha256: {"post", "kind", "file", "when"}}                every file swapped into an article
# ("kind" in `_used` is cover/inline/upload; in `_generated` it is the kind of picture of KINDS.) Older `_generated`
# entries without dimensions still count for the similarity of prompts, not for the dimension rules.


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


def _record_generated(prompt: str, file: Path, aspect: str, dims: Optional[Dict[str, str]] = None) -> None:
    data = _progress()
    data.setdefault("_generated", []).append(
        {"prompt": prompt, "file": str(file), "sha256": sha256_of(file), "aspect": aspect, "when": _now(), **(dims or {})}
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
            _check_litmedia_version(Path(c))
            return Path(c)
    raise Failure("litmedia-skill not found. Install it, or set LITMEDIA_SKILL to its folder.", EXIT_CONFIG)


#: Seedream 5.0 on the LitMedia API works only with the fix of 2026-09-30 in `ai_image.py`: the model's id (8) and
#: `quality` sent lowercase ("2k"), as the litmedia.ai website does. An older copy creates the task and then fails
#: ("Image generation failed"). These markers are in the fixed script and in no older one.
LITMEDIA_FIX_MARKERS = ("def quality_param(", '"Seedream 5.0":', '"model_id": 8')


def _check_litmedia_version(folder: Path) -> None:
    try:
        source = (folder / "scripts" / "ai_image.py").read_text(encoding="utf-8")
    except OSError as exc:
        raise Failure(f"Cannot read {folder / 'scripts' / 'ai_image.py'}: {exc}", EXIT_CONFIG) from None
    missing = [m for m in LITMEDIA_FIX_MARKERS if m not in source]
    if missing:
        raise Failure(
            f"The litmedia-skill in {folder} is an old version: its scripts/ai_image.py lacks the Seedream 5.0 fix "
            "(model id 8, quality sent lowercase), so the task would be created and then fail. Copy scripts/ai_image.py "
            r"from the up-to-date litmedia-skill (source: E:\Projects\litmedia_skill) and run again; nothing was spent.",
            EXIT_CONFIG,
        )


#: What LitMedia's scripts import on every call (balance, text-to-image). Its requirements.txt also lists
#: alibabacloud_oss_v2 and pymediainfo, needed only to upload a picture (image-to-image): not tested here.
LITMEDIA_IMPORTS = "import requests, dotenv"
_litmedia_python: Optional[List[str]] = None  # the interpreter found, kept for the rest of this process


def _python_candidates() -> List[List[str]]:
    """The interpreters to try for LitMedia, in order. Seen on 5/10/2026: Hermes ran this script with uv's bare
    Python 3.11, without `requests`, while the same PC had three Pythons that had it."""
    found: List[List[str]] = []
    if os.environ.get("LITMEDIA_PYTHON", "").strip():
        found.append([os.environ["LITMEDIA_PYTHON"].strip()])
    if sys.executable:
        found.append([sys.executable])
    launcher = shutil.which("py")
    if launcher:
        found += [[launcher, "-3.12"], [launcher, "-3"]]
    for name in ("python3", "python"):
        path = shutil.which(name)
        if path:
            found.append([path])
    if os.name == "nt" and os.environ.get("LOCALAPPDATA"):
        def minor(folder: Path) -> int:
            m = re.match(r"Python3(\d+)", folder.name)
            return int(m.group(1)) if m else -1
        base = Path(os.environ["LOCALAPPDATA"]) / "Programs" / "Python"
        found += [[str(d / "python.exe")] for d in sorted(base.glob("Python3*"), key=minor, reverse=True)
                  if (d / "python.exe").is_file()]
    unique: List[List[str]] = []
    seen = set()
    for cmd in found:
        key = tuple([os.path.normcase(os.path.abspath(cmd[0]))] + cmd[1:])
        if key not in seen:
            seen.add(key)
            unique.append(cmd)
    return unique


def _has_litmedia_deps(cmd: List[str]) -> bool:
    try:
        return subprocess.run([*cmd, "-c", LITMEDIA_IMPORTS], capture_output=True, timeout=20).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def litmedia_python() -> List[str]:
    """The first candidate that imports LitMedia's dependencies, said in a `note:` when it is not this Python. None:
    EXIT_CONFIG with what to install and with which interpreter. Nothing is ever installed by this script."""
    global _litmedia_python
    if _litmedia_python is not None:
        return _litmedia_python
    candidates = _python_candidates()
    for cmd in candidates:
        if _has_litmedia_deps(cmd):
            if cmd != [sys.executable]:
                print(f"note: LitMedia runs with {' '.join(cmd)}: this script's Python ({sys.executable}) lacks its "
                      "dependencies.", file=sys.stderr)
            _litmedia_python = cmd
            return cmd
    requirements = litmedia_dir() / "scripts" / "requirements.txt"
    first = " ".join(candidates[0]) if candidates else "python"
    raise Failure(
        "No Python with LitMedia's dependencies (requests, python-dotenv) was found. Tried: "
        + ("; ".join(" ".join(c) for c in candidates) or "none")
        + f". Install them for one of these, e.g.: {first} -m pip install -r {requirements} (the complete list, with "
        "alibabacloud_oss_v2 and pymediainfo for image-to-image uploads), or set LITMEDIA_PYTHON to a Python that has "
        "them. Nothing was installed and nothing was spent.", EXIT_CONFIG,
    )


def _litmedia(script: str, args: List[str], timeout: int) -> subprocess.CompletedProcess:
    folder = litmedia_dir()
    cmd = [*litmedia_python(), str(folder / "scripts" / script), *args]
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
            f"it makes cards the picture: {card}. A blog picture is never a picture of cards: no card as the subject "
            f"(at the start, in the first clause or the first {LEAD_WORDS} words), no two or more cards (cards, a "
            "deck, a pile, the arcana), no spread or layout, no hand holding or turning a card. Keep cards as "
            "context: 'tarot' as an adjective, a card's name as a world or a symbol ('a lighthouse struck by "
            "lightning, the energy of the Tower'); one single small card later in the scene only in the picture of "
            "an article about that very card (--article), named ('a single small card of the Tower') and in the "
            "style of the Thoth deck. Show the world the article talks about (see references/prompts.md)."
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


# ---- the four dimensions: kind, shot, light, setting -----------------------------------------------------------


def _flat(text: str) -> str:
    """Lowercase, straight apostrophes, hyphens as spaces, single spaces: how keywords are looked for."""
    return " ".join(text.lower().replace("’", "'").replace("-", " ").split())


def _shows(scene: str, keywords) -> bool:
    flat = _flat(scene)
    return any(re.search(r"(?<![\w'])" + re.escape(_flat(k)) + r"s?(?![\w'])", flat) for k in keywords)


def _scene(prompt: str) -> str:
    """The prompt without the house style line: its words ("soft natural light") never count as a choice."""
    return " ".join(prompt.split()).replace(" ".join(HOUSE_STYLE.split()), " ")


def setting_key(setting: str) -> str:
    """A setting compared without case, accents, punctuation, articles, plurals or word order
    ("The Mediterranean harbours" = "harbour, Mediterranean")."""
    plain = unicodedata.normalize("NFKD", setting)
    plain = "".join(c for c in plain if not unicodedata.combining(c)).lower().replace("’", "'")
    words = {_stem(w) for w in re.findall(r"[a-z0-9]+", plain) if w not in LEAD_SKIP}
    return " ".join(sorted(words))


def _norm_value(value: Optional[str]) -> str:
    return "-".join((value or "").strip().lower().replace("_", " ").replace("-", " ").split())


def dimensions(kind: Optional[str], shot: Optional[str], light: Optional[str], setting: Optional[str]) -> Dict[str, str]:
    """The four options, normalized ("Close up" → close-up) and validated against the catalogs (exit 2 otherwise)."""
    dims = {"kind": _norm_value(kind), "shot": _norm_value(shot), "light": _norm_value(light),
            "setting": " ".join((setting or "").split())}
    wrong = []
    for name, catalog in (("kind", KINDS), ("shot", SHOTS), ("light", LIGHTS)):
        if dims[name] not in catalog:
            wrong.append(f"--{name} «{dims[name] or ''}» is not in the catalog: one of {', '.join(catalog)}")
    if not setting_key(dims["setting"]):
        wrong.append("--setting is missing: a place, a culture or an era in a few words (\"Japanese garden\", "
                     "\"Victorian library\", \"desert at the edge of a salt lake\")")
    elif len(dims["setting"]) > MAX_SETTING_CHARS or len(dims["setting"].split()) > MAX_SETTING_WORDS:
        wrong.append(f"--setting is too long: {MAX_SETTING_WORDS} words and {MAX_SETTING_CHARS} characters at most "
                     "(a place, a culture or an era, not the scene)")
    if wrong:
        raise Failure("the dimensions are not valid, nothing was generated:\n  - " + "\n  - ".join(wrong)
                      + "\n  (`catalog` lists every value and which ones are free now)", EXIT_USAGE)
    return dims


def dimension_history(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """The generated pictures that declared their dimensions, oldest first (older entries have none)."""
    return [e for e in data.get("_generated") or [] if isinstance(e, dict) and e.get("kind")]


def free_values(history: List[Dict[str, Any]], kind: Optional[str] = None) -> Dict[str, Any]:
    """What the next picture may use: kinds, lights, shots (with `kind`: the shots still free for that kind), and
    the settings to avoid."""
    last_kinds = [e.get("kind") for e in history[-KIND_GAP:]]
    last_lights = [e.get("light") for e in history[-LIGHT_GAP:]]
    rare = {l for l, gap in RARE_LIGHTS.items() if any(e.get("light") == l for e in history[-gap:])}
    pairs = {(e.get("kind"), e.get("shot")) for e in history[-PAIR_GAP:]}
    return {
        "kinds": [k for k in KINDS if k not in last_kinds],
        "lights": [l for l in LIGHTS if l not in last_lights and l not in rare],
        "shots": [s for s in SHOTS if (kind, s) not in pairs] if kind else list(SHOTS),
        "settings": [e.get("setting") for e in reversed(history[-SETTING_GAP:]) if e.get("setting")],  # newest first
    }


def dimension_problems(prompt: str, dims: Dict[str, str], history: List[Dict[str, Any]]) -> List[str]:
    """Every dimension rule the picture breaks, each with what to change and what is still free."""
    problems: List[str] = []
    kind, shot, light, setting = dims["kind"], dims["shot"], dims["light"], dims["setting"]
    free = free_values(history, kind)
    last_kinds = [e.get("kind") for e in history[-KIND_GAP:]]
    if kind in last_kinds:
        problems.append(
            f"--kind {kind} is the kind of one of the last {KIND_GAP} pictures ({', '.join(reversed(last_kinds))}, "
            f"newest first): show something else. Kinds free now: {', '.join(free['kinds'])}."
        )
    if any((e.get("kind"), e.get("shot")) == (kind, shot) for e in history[-PAIR_GAP:]):
        problems.append(
            f"--kind {kind} with --shot {shot} was already used in the last {PAIR_GAP} pictures: change the framing. "
            f"Shots still free with {kind}: {', '.join(free['shots']) or 'none, change the kind'}."
        )
    last_lights = [e.get("light") for e in history[-LIGHT_GAP:]]
    if light in last_lights:
        problems.append(
            f"--light {light} is the light of one of the last {LIGHT_GAP} pictures ({', '.join(reversed(last_lights))}, "
            f"newest first): change the hour or the weather. Lights free now: {', '.join(free['lights'])}."
        )
    elif light in RARE_LIGHTS:
        gap = RARE_LIGHTS[light]
        ago = [n for n, e in enumerate(reversed(history[-gap:]), 1) if e.get("light") == light]
        if ago:
            problems.append(
                f"--light {light} stays rare: it was used {ago[0]} picture(s) ago, and never twice in {gap}. "
                f"Lights free now: {', '.join(free['lights'])}."
            )
    key = setting_key(setting)
    earlier = [e.get("setting") for e in history[-SETTING_GAP:] if setting_key(e.get("setting") or "") == key]
    if earlier:
        problems.append(
            f"--setting «{setting}» was already used in the last {SETTING_GAP} pictures (as «{earlier[-1]}»): choose "
            f"another place, culture or era. Settings of the last {SETTING_GAP}, to avoid: "
            f"{'; '.join(free['settings'])}."
        )
    scene = _scene(prompt)
    if not _shows(scene, LIGHTS[light][1]):
        problems.append(
            f"the prompt does not show the light declared with --light {light}: write it into the scene with one of "
            f"{', '.join(repr(k) for k in LIGHTS[light][1])} (the house style line does not count)."
        )
    if not _shows(scene, SHOTS[shot][1]):
        problems.append(
            f"the prompt does not show the composition declared with --shot {shot}: write it into the scene with one "
            f"of {', '.join(repr(k) for k in SHOTS[shot][1])}."
        )
    # Il luogo dichiarato con --setting non deve per forza comparire nel prompt (decisione dell'operatore, 5/10):
    # conta per la varietà, nel registro, non come parola obbligatoria.
    return problems


def check_prompt(prompt: str, dims: Dict[str, str], article: Optional[str] = None) -> List[str]:
    """Refuse the prompt (EXIT_RULE) if it breaks a rule; return the warnings of the card rule."""
    data = _progress()
    cards, warnings = article_card_problems(prompt, article)
    problems = (prompt_problems(prompt, _known_prompts(data)) + cards
                + dimension_problems(prompt, dims, dimension_history(data)))
    if problems:
        raise Failure("the prompt is refused, nothing was generated:\n  - " + "\n  - ".join(problems), EXIT_RULE)
    return warnings


# ---- the article a picture is for: its title and focus keyword name the cards it may show ---------------------
# `--article <slug or id>` is looked for, in this order, in the work folders (article.json: title, focus_keyword,
# slug), in the copy of the titles that `tarots_blog.py titles` keeps (~/.tarots-blog/titles-cache.json, or
# TAROTS_TITLES_CACHE), then, if a media key is set, through the API (GET /media-posts/{id}; a slug is looked for in
# GET /media-posts). Only a prompt that draws a card needs it: every other prompt is checked without looking.

UUID_LIKE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE)
_articles_found: Dict[str, Optional[Dict[str, Any]]] = {}


def titles_cache_path() -> Path:
    """Read at every call, like work_root(): TAROTS_TITLES_CACHE may be set for one run."""
    env = os.environ.get("TAROTS_TITLES_CACHE", "").strip()
    return Path(env).expanduser() if env else Path.home() / ".tarots-blog" / "titles-cache.json"


def _article_entry(title: Any, keyword: Any, slug: Any, post_id: Any, source: str) -> Optional[Dict[str, Any]]:
    texts = [str(t) for t in (title, keyword) if t and str(t).strip()]
    if not texts:
        return None
    return {"title": str(title or keyword), "texts": texts, "slug": slug or None, "id": post_id or None,
            "source": source}


def _from_work_folder(arg: str) -> Optional[Dict[str, Any]]:
    slug = work_slug(arg)
    for folder in work_folders():
        try:
            data = json.loads((folder / "article.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(data, dict):
            continue
        if (WORK_NAME.match(folder.name).group(2) == slug or data.get("slug") == slug
                or (data.get("id") and str(data.get("id")) == arg)):
            found = _article_entry(data.get("title") or data.get("titolo"),
                                   data.get("focus_keyword") or data.get("seo_parola_chiave"),
                                   data.get("slug") or slug, data.get("id"), f"{folder / 'article.json'}")
            if found:
                return found
    return None


def _from_titles_cache(arg: str) -> Optional[Dict[str, Any]]:
    try:
        data = json.loads(titles_cache_path().read_text(encoding="utf-8"))
        rows = list((data.get("articles") or {}).values())
    except (OSError, ValueError, AttributeError):
        return None
    slug = work_slug(arg)
    matches = [r for r in rows if isinstance(r, dict) and (str(r.get("id")) == arg or r.get("slug") in (arg, slug))]
    matches.sort(key=lambda r: r.get("lang") != "en")  # the English original first, then its translations
    found = None
    for row in matches:
        entry = _article_entry(row.get("titolo"), row.get("parola_chiave"), row.get("slug"), row.get("id"),
                               f"the titles copy {titles_cache_path()}")
        if entry and found:
            found["texts"] += [t for t in entry["texts"] if t not in found["texts"]]
        elif entry:
            found = entry
    return found


def _from_api(arg: str) -> Optional[Dict[str, Any]]:
    try:
        config()
    except Failure:
        return None  # no media key: the API is not asked
    try:
        if UUID_LIKE.match(arg):
            post = call("GET", f"/media-posts/{arg}")
        else:
            slug = work_slug(arg)
            post = next((p for p in _all_posts(None, None) if p.get("slug") in (arg, slug)), None)
    except Failure:
        return None
    if not post:
        return None
    return _article_entry(post.get("titolo"), post.get("parola_chiave"), post.get("slug"), post.get("id"), "the API")


def find_article(arg: str) -> Optional[Dict[str, Any]]:
    """The article `arg` (a slug or an id) as {title, texts, slug, id, source}, or None. Kept for this run."""
    arg = (arg or "").strip()
    if arg not in _articles_found:
        _articles_found[arg] = (_from_work_folder(arg) or _from_titles_cache(arg) or _from_api(arg)) if arg else None
    return _articles_found[arg]


def article_card_problems(prompt: str, article: Optional[str]) -> tuple:
    """(problems, warnings) of the card the prompt draws, for `article`; ([], []) when it draws none."""
    if not shows_a_card(prompt):
        return [], []
    if not article:
        return ["it draws a card, and a card may appear only in the picture of an article about that very card: "
                "give --article <slug or id> (its title or focus keyword must name the card), or take the card out "
                "and show the article's world instead"], []
    found = find_article(article)
    if found is None:
        return [f"it draws a card, and the article «{article}» was not found (work folders in {work_root()}, the "
                f"titles copy {titles_cache_path()}, the API if a media key is set): a card may appear only for an "
                "article known to be about it. Check the slug or id (`tarots_blog.py titles` refreshes the copy), "
                "or take the card out"], []
    return card_rule_problems(prompt, found["texts"], found["title"])


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
        raise Failure(f"{path} was generated from a prompt that makes cards the picture ({card}): it cannot go on "
                      "the blog.", EXIT_RULE)
    if prompt and (cards := article_card_problems(prompt, post_id)[0]):
        raise Failure(f"{path} was generated from a prompt that draws a card, and for article {post_id}: "
                      f"{cards[0]}. Generate a new picture for this article.", EXIT_RULE)
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


# ---- the work folder of an article (the same folders as tarots_blog.py `new`) -----------------------------------
# `~/.tarots-blog/work/<YYYY-MM-DD>-<slug>/foto/` holds every picture of one article. An agent saved its files with
# relative paths (`work/<slug>-cover.jpg`) inside the skill's folder and then could not find them: `--article SLUG`,
# or a bare `--out` name, puts the picture there. `work_slug` is a copy of `slugify` in tarots_blog.py (a test there
# keeps the two equal): the two skills install separately.

WORK_NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)$")


def work_root() -> Path:
    """Read at every call, not at import: TAROTS_WORK_DIR may be set for one run."""
    env = os.environ.get("TAROTS_WORK_DIR", "").strip()
    return Path(env).expanduser() if env else Path.home() / ".tarots-blog" / "work"


def work_slug(text: str, limit: int = 60) -> str:
    plain = unicodedata.normalize("NFKD", str(text or "")).replace("æ", "ae").replace("Æ", "ae").replace("œ", "oe")
    plain = "".join(c for c in plain if not unicodedata.combining(c)).lower()
    slug = "-".join(re.sub(r"[^0-9a-z]+", " ", plain).split())
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


def work_folder(article: Optional[str]) -> Path:
    """The work folder of `article` (a slug): the newest with that slug in its name or in its article.json; created
    for today if there is none (pictures for an existing article). Without `article`: the newest work folder."""
    folders = work_folders()
    if not article:
        if not folders:
            raise Failure(f"--out is a bare file name but there is no work folder in {work_root()}: give "
                          "--article <slug> (or run tarots_blog.py new \"<slug>\" first).", EXIT_USAGE)
        return folders[0]
    slug = work_slug(article)
    if not slug:
        raise Failure("--article needs the article's slug.", EXIT_USAGE)
    for folder in folders:
        if WORK_NAME.match(folder.name).group(2) == slug:
            return folder
    for folder in folders:
        try:
            if json.loads((folder / "article.json").read_text(encoding="utf-8")).get("slug") == slug:
                return folder
        except (OSError, ValueError, AttributeError):
            continue
    folder = work_root() / f"{datetime.date.today().isoformat()}-{slug}"
    print(f"note: no work folder for {slug} yet: the picture goes in {folder}", file=sys.stderr)
    return folder


def _next_free(folder: Path, aspect: str) -> Path:
    """The default name in foto/: cover.jpg for a 3:2 picture, inline-1.jpg, inline-2.jpg... for the others."""
    if aspect == "3:2" and not (folder / "cover.jpg").exists():
        return folder / "cover.jpg"
    n = 1
    while (folder / f"inline-{n}.jpg").exists():
        n += 1
    return folder / f"inline-{n}.jpg"


def output_path(out: Optional[str], article: Optional[str], aspect: str) -> Path:
    """Where `generate` saves: in <work folder>/foto/ with --article or a bare --out name; else --out as given."""
    if out and not article and len(Path(out).parts) > 1:
        return Path(out).expanduser()
    if not out and not article:
        raise Failure("Give --article <slug> (the picture goes in its work folder's foto/) or --out FILE.", EXIT_USAGE)
    foto = work_folder(article) / "foto"
    return foto / Path(out).name if out else _next_free(foto, aspect)


def cmd_generate(a) -> int:
    resolution = a.resolution.upper()
    if resolution not in COST:
        raise Failure(f"{MODEL} accepts --resolution 2K or 4K (there is no 1K).", EXIT_USAGE)
    cost = COST[resolution]
    folder_of = a.article
    if a.article and UUID_LIKE.match(a.article.strip()):  # an id: the work folder is named after the slug
        found = find_article(a.article.strip())
        folder_of = (found or {}).get("slug") or a.article
    out = output_path(a.out, folder_of, a.aspect)
    if out.suffix.lower() not in IMAGE_TYPES:
        raise Failure("--out must end in .jpg, .jpeg, .png or .webp", EXIT_USAGE)
    if out.exists():
        raise Failure(f"{out} already exists: a picture already paid for is never overwritten. Give another --out name.", EXIT_USAGE)
    dims = dimensions(a.kind, a.shot, a.light, a.setting)
    for warning in check_prompt(a.prompt, dims, a.article):
        print(f"warning: {warning}", file=sys.stderr)
    if a.dry_run:
        print(f"dry run: the prompt passes every check; {MODEL}, {a.aspect}, {resolution}, {cost} credits, "
              f"would be saved to {out}")
        print(f"form: {_form(dims)}")
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
    _record_generated(a.prompt, out, a.aspect, dims)
    print(f"saved {out} ({out.stat().st_size // 1024} KB), {cost} credits; balance now about {credits - cost}")
    return EXIT_OK


def _form(dims: Dict[str, Any]) -> str:
    if not dims.get("kind"):
        return "(no dimensions: an older record)"
    return f"{dims.get('kind')} · {dims.get('shot')} · {dims.get('light')} · {dims.get('setting')}"


def cmd_prompt_check(a) -> int:
    data = _progress()
    earlier = _known_prompts(data)
    dims = dimensions(a.kind, a.shot, a.light, a.setting)
    history = dimension_history(data)
    cards, card_warnings = article_card_problems(a.prompt, a.article)
    problems = prompt_problems(a.prompt, earlier) + cards + dimension_problems(a.prompt, dims, history)
    for warning in card_warnings:
        print(f"card warning: {warning}")
    if a.alt is not None:
        try:
            _check_alt(a.alt, warn=False)
            if warning := alt_card_warning(a.alt):
                print(f"alt text warning: {warning}")
        except Failure as exc:
            problems.append(str(exc))
    best = most_similar(a.prompt, earlier)
    print(f"form: {_form(dims)}")
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


def alt_card_warning(alt: str) -> Optional[str]:
    """A warning for an alt text that mentions a card without describing a spread (that one is refused)."""
    found = [f for f in card_problems(alt) if f[0] != SPREAD]
    if found:
        return (f"the alt text mentions a card («{found[0][1]}», {found[0][2]}): check that the picture really shows "
                "it, small and in the context; otherwise describe what is there.")
    return None


def _check_alt(alt: str, *, warn: bool = True) -> str:
    alt = " ".join(alt.split())
    if len(alt) < 8:
        raise Failure("The alt text must describe the picture (8 characters at least).", EXIT_USAGE)
    spread = [f for f in card_problems(alt) if f[0] == SPREAD]
    if spread:
        raise Failure(f"The alt text describes a spread («{spread[0][1]}», {spread[0][2]}), and no blog picture "
                      "shows one: describe what is really in the new picture.", EXIT_RULE)
    if warn and (warning := alt_card_warning(alt)):
        print(f"warning: {warning}", file=sys.stderr)
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
        uploaded.append({"file": file, "sha256": hashes[file], "url": image["url"], "alt": _check_alt(alt, warn=False), "prompt": _prompt_of(file)})
        body["sostituisci"].append({"indice": int(n), "immagine_id": image["id"], "alt": _check_alt(alt, warn=False)})
    for n, file, alt in add:
        image = upload(file)
        uploaded.append({"file": file, "sha256": hashes[file], "url": image["url"], "alt": _check_alt(alt, warn=False), "prompt": _prompt_of(file)})
        body["aggiungi"].append({"dopo_paragrafo": int(n), "immagine_id": image["id"], "alt": _check_alt(alt, warn=False)})
    result = call("PUT", f"/posts/{a.id}/inline", body=body)
    for entry in uploaded:
        _record(a.id, "inline", entry)
    print(f"text pictures now: {len(result['immagini_nel_testo'])}")
    for img in result["immagini_nel_testo"]:
        print(f"  #{img['indice']} {img['url']}  «{img['alt']}»")
    print(f"article: {result['url']}")
    return EXIT_OK


def _print_free(history: List[Dict[str, Any]]) -> None:
    free = free_values(history)
    last_kinds = [e.get("kind") for e in reversed(history[-KIND_GAP:])]
    not_lights = [e.get("light") for e in reversed(history[-LIGHT_GAP:])]
    for light, gap in RARE_LIGHTS.items():
        ago = [n for n, e in enumerate(reversed(history[-gap:]), 1) if e.get("light") == light]
        if ago and light not in not_lights:
            not_lights.append(f"{light}: rare, used {ago[0]} picture(s) ago")
    print("Free for the next picture:")
    print(f"  --kind   {', '.join(free['kinds'])}" + (f"   (not: {', '.join(last_kinds)})" if last_kinds else ""))
    print(f"  --light  {', '.join(free['lights'])}" + (f"   (not: {', '.join(not_lights)})" if not_lights else ""))
    print(f"  --shot   any, as long as the kind+shot pair is not one of the last {PAIR_GAP} pictures (see `progress`)")
    if free["settings"]:
        print(f"  --setting not one of the last {SETTING_GAP}: {'; '.join(free['settings'])}")


def cmd_catalog(_a) -> int:
    print(f"--kind: what the picture shows (not the kind of the last {KIND_GAP} pictures)")
    for name, what in KINDS.items():
        print(f"  {name:<28} {what}")
    print(f"\n--shot: the composition (a kind+shot pair not used in the last {PAIR_GAP}); the prompt must contain one "
          "of the words in brackets")
    for name, (what, words) in SHOTS.items():
        print(f"  {name:<28} {what}  [{', '.join(words)}]")
    print(f"\n--light: not the light of the last {LIGHT_GAP} pictures, firelight not twice in "
          f"{RARE_LIGHTS['firelight']}; the prompt must contain one of the words in brackets")
    for name, (what, words) in LIGHTS.items():
        print(f"  {name:<28} {what}  [{', '.join(words)}]")
    print(f"\n--setting: a place, a culture or an era in a few words (\"Mediterranean harbour\", \"Japanese garden\", "
          f"\"Victorian library\"), not one of the last {SETTING_GAP}, named in the prompt too.\n")
    _print_free(dimension_history(_progress()))
    return EXIT_OK


def cmd_progress(_a) -> int:
    data = _progress()
    generated = data.get("_generated") or []
    if generated:
        _print_free(dimension_history(data))
        print(f"\nLast {min(len(generated), SHOWN_IN_PROGRESS)} pictures generated, newest first "
              "(kind · shot · light · setting):")
        for n, entry in enumerate(reversed(generated[-SHOWN_IN_PROGRESS:]), 1):
            print(f"  {n:>2}. {entry.get('when', '')[:10]}  {entry.get('aspect', '')}  {_form(entry)}  {entry.get('file')}")
            print(f"      {_short(entry.get('prompt') or '', 160)}")
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


def _dimension_options(p: argparse.ArgumentParser) -> None:
    """The four dimensions, required: the values are checked by `dimensions()`, which also says which are free."""
    p.add_argument("--kind", required=True, help=f"what the picture shows: {', '.join(KINDS)}")
    p.add_argument("--shot", required=True, help=f"the composition: {', '.join(SHOTS)}")
    p.add_argument("--light", required=True, help=f"the light: {', '.join(LIGHTS)}")
    p.add_argument("--setting", required=True, help="place, culture or era in a few words, e.g. \"Japanese garden\"")


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
    sub.add_parser("catalog", help="the values of --kind, --shot, --light, and which are free now").set_defaults(fn=cmd_catalog)
    pc = sub.add_parser("prompt-check", help="check a prompt (and an alt text) offline, before spending anything")
    pc.add_argument("--prompt", required=True)
    _dimension_options(pc)
    pc.add_argument("--alt", help="also check this alt text")
    pc.add_argument("--article", metavar="SLUG_OR_ID",
                    help="the article the picture is for: needed when the prompt draws a card (only the article's "
                         "own card, named in its title or focus keyword, may appear)")
    pc.set_defaults(fn=cmd_prompt_check)
    g = sub.add_parser("generate", help=f"one picture with {MODEL} through litmedia-skill")
    g.add_argument("--prompt", required=True)
    _dimension_options(g)
    g.add_argument("--article", metavar="SLUG_OR_ID",
                   help="the article's slug (or id): the picture goes in its work folder's foto/ (cover.jpg, "
                        "inline-1.jpg...), and a card may appear only if the article is about that very card")
    g.add_argument("--out", help="the file name (.jpg/.png/.webp). A bare name goes in the work folder's foto/ "
                                 "(of --article, else of the newest work folder); a path with a folder is used as is")
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
