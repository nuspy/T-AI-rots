"""The picture rules of tarots_blog.py (`post --cover`, `upload`), offline: the API is replaced by a fake.

    backend/.venv/Scripts/python.exe -m pytest skills/tarots-blog-publisher/tests skills/tarots-blog-images/tests -q -p no:cacheprovider

The record is the one of the tarots-blog-images skill (`_generated`, `_used`): these tests also write it with
`tarots_images.py` itself, to prove the two scripts read and write the same file the same way.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

SKILLS = Path(__file__).resolve().parents[2]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


tb = _load("tarots_blog", SKILLS / "tarots-blog-publisher" / "scripts" / "tarots_blog.py")
ti = _load("tarots_images_for_blog", SKILLS / "tarots-blog-images" / "scripts" / "tarots_images.py")

GOOD_PROMPT = (
    "A lighthouse on a black basalt cliff in a winter storm, one bolt of lightning splitting the sky, waves breaking "
    "against the rocks, the lamp still burning, seen from a fishing harbour far below, " + ti.HOUSE_STYLE
)
CARD_PROMPT = "Mystical tarot card spread on a velvet tablecloth, golden stars and moon symbols, ethereal lighting"


class FakeApi:
    """Answers the few calls `post` and `upload` make, and remembers them."""

    def __init__(self):
        self.calls = []

    def __call__(self, method, path, **kwargs):
        self.calls.append((method, path))
        if path == "/media":
            return {"id": "img-1", "url": "/blog/media/img-1.webp", "larghezza": 1600, "altezza": 1067, "byte": 1000}
        if path == "/titles":
            return {"totale": 0, "pagina": 1, "per_pagina": 1000, "adesso": "2026-10-06T00:00:00+00:00", "articoli": []}
        if path == "/posts" and (kwargs.get("body") or {}).get("dry_run"):
            return {"seo": {"punteggio": 92, "giudizio": "ottimo", "controlli": [], "statistiche": {}}}
        if path == "/posts":
            return {"articolo": {"id": "post-new", "slug": "the-tower", "stato": "bozza", "lang": "en"},
                    "url": "https://tarots.chat/blog/the-tower", "avvisi": []}
        raise AssertionError(f"unexpected call {method} {path}")

    @property
    def uploads(self):
        return [c for c in self.calls if c[1] == "/media"]


@pytest.fixture
def env(tmp_path, monkeypatch):
    progress = tmp_path / "images-progress.json"
    monkeypatch.setattr(tb, "PROGRESS_PATH", progress)
    monkeypatch.setattr(ti, "PROGRESS_PATH", progress)
    api = FakeApi()
    monkeypatch.setattr(tb, "call", api)
    article = tmp_path / "article.json"
    article.write_text(json.dumps({"title": "The Tower", "body": "text", "status": "draft", "section": "learn-tarot"}), encoding="utf-8")
    return tmp_path, api, str(article)


def _generated(folder: Path, name: str, content: bytes, prompt: str = GOOD_PROMPT) -> str:
    """A picture as `tarots_images.py generate` leaves it: the file, its prompt next to it, the record."""
    path = folder / name
    path.write_bytes(content)
    Path(str(path) + ".prompt.txt").write_text(prompt, encoding="utf-8")
    ti._record_generated(prompt, path, "3:2")
    return str(path)


def _used(env_tmp) -> dict:
    return json.loads((env_tmp / "images-progress.json").read_text(encoding="utf-8")).get("_used", {})


def test_card_patterns_are_the_same_as_in_tarots_images():
    assert tb.CARD_PATTERNS == ti.CARD_PATTERNS
    assert tb.DECK == ti.DECK and tb.NOT_A_CARD_DECK == ti.NOT_A_CARD_DECK
    assert tb.CARD_WORD == ti.CARD_WORD and tb.LEAD_WORDS == ti.LEAD_WORDS and tb.LEAD_SKIP == ti.LEAD_SKIP
    assert tb.SPREAD == ti.SPREAD


def test_the_card_rule_of_the_article_is_the_same_as_in_tarots_images():
    for name in ("MAJOR_ARCANA", "CONTEXT_NAMES", "MINOR_RANKS", "MINOR_SUITS", "CARD_CONTEXT", "NAME_GAP",
                 "NOT_A_CARD_NAME", "COPY_OF_ARTWORK", "CLAUSE_BREAK", "_MINOR_NAME", "_MAJOR_NAMES", "_ARTICLES",
                 "CARD_ID_RANKS", "CARD_ID_SUITS"):
        assert getattr(tb, name) == getattr(ti, name), name
    import inspect
    for name in ("_card_plain", "named_cards", "cards_of_article", "cards_shown", "shows_a_card", "card_rule_problems",
                 "subject_card"):
        assert inspect.getsource(getattr(tb, name)) == inspect.getsource(getattr(ti, name)), name


TOWER_CARD = (GOOD_PROMPT + ", the energy of the Tower, on the harbour wall a single small card of the Tower tucked "
              "under a stone, in the style of the Thoth deck")
NAMELESS_CARD = GOOD_PROMPT + ", on the harbour wall a single card tucked under a stone"
FOOL_CARD = GOOD_PROMPT + ", on the harbour wall a single small card of the Fool, in the style of the Thoth deck"
ARTICLES = [["The Tower tarot card meaning"], ["Tarot Meditation for Libra Season Balance"], ["Full Moon tarot spread"],
            ["The Moon tarot card meaning"], ["Hierophant reversed in love"], ["Asso di Coppe nei tarocchi Thoth"]]


@pytest.mark.parametrize("prompt", [TOWER_CARD, NAMELESS_CARD, FOOL_CARD, GOOD_PROMPT, CARD_PROMPT])
@pytest.mark.parametrize("texts", ARTICLES)
def test_the_copy_judges_the_card_of_the_article_like_tarots_images(prompt, texts):
    assert tb.cards_of_article(texts) == ti.cards_of_article(texts)
    assert tb.cards_shown(prompt) == ti.cards_shown(prompt)
    assert tb.card_rule_problems(prompt, texts, texts[0]) == ti.card_rule_problems(prompt, texts, texts[0])


SAMPLES = [
    CARD_PROMPT, GOOD_PROMPT,
    "a single card tucked between the pages of a notebook on a windowsill",
    "a garden at dawn, a bench, and three cards forgotten on it",
    "a Celtic Cross spread on a wooden floor",
    "a harbour at night, gulls asleep on the posts, a sailor holding a card up to the lantern",
    "Spiritual tarot imagery with sacred geometry, cosmic background",
    "a lighthouse struck by lightning on a black cliff, the energy of the Tower",
    "the Queen of Cups on a throne by the sea",
    "A rain-streaked kitchen window at dawn, a kettle steaming on the stove, a coat on the chair, bread on the "
    "board, and on the windowsill a single card tucked in a notebook",
    "the deck of a sailing ship at dawn", "a heron with its wings spread wide", "an arcane brass astrolabe",
]


@pytest.mark.parametrize("prompt", SAMPLES)
def test_the_copy_judges_every_prompt_like_tarots_images(prompt):
    assert tb.card_problems(prompt) == ti.card_problems(prompt)
    assert tb.card_problem(prompt) == ti.card_problem(prompt)


def test_a_card_name_as_a_symbol_does_not_stop_the_picture(env):
    tmp, api, article = env
    cover = _generated(tmp, "cover.jpg", b"\xff\xd8 lighthouse", prompt=GOOD_PROMPT + ", the energy of the Tower")
    assert tb.main(["post", article, "--cover", cover]) == tb.EXIT_OK


def test_the_card_of_the_article_named_in_the_prompt_is_accepted(env):
    tmp, api, article = env  # article.json: title «The Tower»
    cover = _generated(tmp, "cover.jpg", b"\xff\xd8 lighthouse", prompt=TOWER_CARD)
    assert tb.main(["post", article, "--cover", cover]) == tb.EXIT_OK


@pytest.mark.parametrize("prompt,expected_warnings", [
    # NAMELESS_CARD says "tucked": MARGINAL_WORDS is already satisfied, so only the Thoth warning is left
    (NAMELESS_CARD, ["does not say the cards are in the style of the Thoth deck"]),
    (FOOL_CARD, ["is not the card of"]),
])
def test_post_admits_a_card_that_is_not_the_one_of_the_article(env, prompt, expected_warnings, capsys):
    # `post` no longer refuses this (relaxed 6/10/2026, twice): `check_card_in_picture` now prints the warning
    # itself ("card warning: <file>: <text>"), so it is checked both on stderr and straight from `card_rule_problems`
    # (the function it is built from, kept identical to tarots-blog-images's by a separate test).
    tmp, api, article = env  # article.json: title «The Tower»
    cover = _generated(tmp, "cover.jpg", b"\xff\xd8 lighthouse", prompt=prompt)
    assert tb.main(["post", article, "--cover", cover]) == tb.EXIT_OK
    err = capsys.readouterr().err
    problems, warnings = tb.card_rule_problems(prompt, ["The Tower"], "The Tower")
    assert problems == [] and len(warnings) == len(expected_warnings)
    for text in expected_warnings:
        assert any(text in w for w in warnings)
        assert text in err


def test_the_subject_of_the_article_lets_its_card_in(env, capsys):
    tmp, api, _ = env
    article = tmp / "falls.json"
    article.write_text(json.dumps({"title": "When everything falls at once", "body": "text", "status": "draft", "section": "learn-tarot",
                                   "subject": {"type": "card", "ref": "maj-16"}}), encoding="utf-8")
    cover = _generated(tmp, "cover.jpg", b"\xff\xd8 lighthouse", prompt=TOWER_CARD)
    assert tb.main(["post", str(article), "--cover", cover]) == tb.EXIT_OK
    sent = [c for c in api.calls if c[1] == "/posts"]
    assert len(sent) == 2
    other = _generated(tmp, "cover-2.jpg", b"\xff\xd8 fool", prompt=FOOL_CARD)
    # the subject is the Tower, not the Fool: admitted too now, with a warning (lost by `post`, kept by the function)
    assert tb.main(["post", str(article), "--cover", other]) == tb.EXIT_OK
    _problems, warnings = tb.card_rule_problems(FOOL_CARD, ["When everything falls at once", "the Tower"],
                                                "When everything falls at once")
    assert warnings and "is not the card of" in warnings[0] and "about the Tower" in warnings[0]


def test_post_admits_any_card_for_an_article_about_no_card(env, capsys):
    tmp, api, _ = env
    article = tmp / "libra.json"
    article.write_text(json.dumps({"title": "Tarot Meditation for Libra Season Balance", "body": "text",
                                   "focus_keyword": "libra season tarot", "status": "draft", "section": "learn-tarot"}), encoding="utf-8")
    cover = _generated(tmp, "cover.jpg", b"\xff\xd8 lighthouse", prompt=FOOL_CARD)
    # relaxed 6/10/2026: an article about no card still admits a card as context (nothing of its own to compare it to)
    assert tb.main(["post", str(article), "--cover", cover]) == tb.EXIT_OK
    problems, warnings = tb.card_rule_problems(FOOL_CARD, ["Tarot Meditation for Libra Season Balance",
                                                           "libra season tarot"], "Tarot Meditation for Libra Season Balance")
    assert problems == [] and warnings == []


def test_upload_reads_the_article_of_for_in_its_work_folder_or_the_titles_copy(env, monkeypatch, capsys):
    tmp, api, _ = env
    work = tmp / "work"
    (work / "2026-10-05-the-tower-in-love").mkdir(parents=True)
    (work / "2026-10-05-the-tower-in-love" / "article.json").write_text(
        json.dumps({"title": "The Tower in love", "focus_keyword": "tower tarot card love", "slug": "the-tower-in-love",
                "section": "learn-tarot"}),
        encoding="utf-8")
    monkeypatch.setenv("TAROTS_WORK_DIR", str(work))
    cache = tmp / "titles-cache.json"
    cache.write_text(json.dumps({"articles": {
        "id-libra": {"id": "id-libra", "slug": "libra-season", "titolo": "Tarot Meditation for Libra Season Balance",
                     "parola_chiave": "libra season tarot", "lang": "en"},
        "id-tower": {"id": "id-tower", "slug": "tower-card", "titolo": "The Tower card meaning",
                     "parola_chiave": "tower card meaning", "lang": "en"}}}), encoding="utf-8")
    monkeypatch.setattr(tb, "TITLES_CACHE_PATH", cache)
    pic = _generated(tmp, "inline.jpg", b"\xff\xd8 tower card", prompt=TOWER_CARD)
    assert tb.main(["upload", pic, "--for", "the-tower-in-love"]) == tb.EXIT_OK        # the work folder
    assert tb.main(["upload", pic, "--for", "the-tower-in-love"]) == tb.EXIT_OK
    other = _generated(tmp, "inline-2.jpg", b"\xff\xd8 tower card 2", prompt=TOWER_CARD + ", rain")
    assert tb.main(["upload", other, "--for", "id-tower"]) == tb.EXIT_OK                 # the titles copy, by id
    third = _generated(tmp, "inline-3.jpg", b"\xff\xd8 tower card 3", prompt=TOWER_CARD + ", wind")
    capsys.readouterr()
    # the copy, by slug: the Libra article names no card, so the Tower is admitted too (`upload` shows no warning)
    assert tb.main(["upload", third, "--for", "libra-season"]) == tb.EXIT_OK
    about = tb.article_texts("libra-season")
    assert about is not None and about[1] == "Tarot Meditation for Libra Season Balance"   # the copy was read
    problems, warnings = tb.card_rule_problems(TOWER_CARD + ", wind", *about)
    assert problems == [] and warnings == []
    # relaxed 6/10/2026: a card is admitted even when --for names no known article, or there is no --for at all
    # (the operator's rule now reads "with or without --article"); each needs its own, never-used-before picture
    fourth = _generated(tmp, "inline-4.jpg", b"\xff\xd8 tower card 4", prompt=TOWER_CARD + ", fog")
    assert tb.main(["upload", fourth, "--for", "nowhere"]) == tb.EXIT_OK
    fifth = _generated(tmp, "inline-5.jpg", b"\xff\xd8 tower card 5", prompt=TOWER_CARD + ", snow")
    assert tb.main(["upload", fifth]) == tb.EXIT_OK
    assert len(api.uploads) == 6


def test_a_file_that_is_not_an_image_is_a_usage_error_before_the_record(env, capsys):
    tmp, api, article = env
    gif = tmp / "c.gif"
    gif.write_bytes(b"GIF89a")
    assert tb.main(["upload", str(gif), "--for", "x"]) == tb.EXIT_USAGE
    assert tb.main(["post", article, "--cover", str(gif)]) == tb.EXIT_USAGE
    assert "PNG, JPEG or WebP" in capsys.readouterr().err and api.calls == []


def test_post_with_a_generated_cover_records_it(env):
    tmp, api, article = env
    cover = _generated(tmp, "cover.jpg", b"\xff\xd8 lighthouse")
    assert tb.main(["post", article, "--cover", cover]) == tb.EXIT_OK
    used = _used(tmp)[tb.sha256_of(cover)]
    assert used["post"] == "post-new" and used["slug"] == "the-tower" and used["kind"] == "cover"
    # tarots_images.py sees the same use
    assert ti._used_files(ti._progress())[tb.sha256_of(cover)] == "post-new"


def test_post_refuses_a_cover_used_by_another_article(env):
    tmp, api, article = env
    cover = _generated(tmp, "cover.jpg", b"\xff\xd8 lighthouse")
    ti._record("post-old", "cover", {"file": cover, "sha256": ti.sha256_of(cover), "url": "/m", "alt": "a lighthouse"})
    copy = tmp / "renamed.png"
    copy.write_bytes(b"\xff\xd8 lighthouse")
    assert tb.main(["post", article, "--cover", str(copy), "--operator-image"]) == tb.EXIT_RULE
    assert tb.main(["post", article, "--cover", cover]) == tb.EXIT_RULE
    assert api.calls == []  # refused before anything was sent


def test_post_twice_with_the_same_cover_is_refused_the_second_time(env):
    tmp, api, article = env
    cover = _generated(tmp, "cover.jpg", b"\xff\xd8 lighthouse")
    assert tb.main(["post", article, "--cover", cover]) == tb.EXIT_OK
    api.calls.clear()
    assert tb.main(["post", article, "--cover", cover]) == tb.EXIT_RULE
    assert api.calls == []


def test_post_refuses_a_picture_not_made_by_generate_unless_operator_image(env, capsys):
    tmp, api, article = env
    other = tmp / "from-the-browser.webp"
    other.write_bytes(b"RIFF browser picture")
    assert tb.main(["post", article, "--cover", str(other)]) == tb.EXIT_RULE
    assert "--operator-image" in capsys.readouterr().err
    assert api.calls == []
    assert tb.main(["post", article, "--cover", str(other), "--operator-image"]) == tb.EXIT_OK
    assert "supplied by the operator" in capsys.readouterr().err
    assert _used(tmp)[tb.sha256_of(other)]["post"] == "post-new"


def test_post_refuses_a_picture_generated_from_a_card_prompt(env):
    tmp, api, article = env
    # an older picture: its prompt is only next to the file, never passed the new checks
    old = tmp / "old-cover.jpg"
    old.write_bytes(b"\xff\xd8 cards on velvet")
    Path(str(old) + ".prompt.txt").write_text(CARD_PROMPT, encoding="utf-8")
    assert tb.main(["post", article, "--cover", str(old), "--operator-image"]) == tb.EXIT_RULE
    # and one recorded as generated with a card prompt (as an older tarots_images.py would have allowed)
    rec = _generated(tmp, "rec.jpg", b"\xff\xd8 another", prompt=CARD_PROMPT)
    assert tb.main(["post", article, "--cover", rec]) == tb.EXIT_RULE
    assert api.calls == []


def test_a_cover_is_not_recorded_when_nothing_is_saved(env, monkeypatch):
    tmp, api, article = env
    cover = _generated(tmp, "cover.jpg", b"\xff\xd8 lighthouse")
    assert tb.main(["post", article, "--cover", cover, "--dry-run"]) == tb.EXIT_OK
    assert _used(tmp) == {}


def test_upload_records_the_article_given_with_for(env):
    tmp, api, _ = env
    pic = _generated(tmp, "inline.jpg", b"\xff\xd8 orchard lanterns")
    assert tb.main(["upload", pic, "--for", "celtic-cross-guide"]) == tb.EXIT_OK
    assert _used(tmp)[tb.sha256_of(pic)]["post"] == "celtic-cross-guide"
    # the same picture again for the same article is fine, for another one it is not
    assert tb.main(["upload", pic, "--for", "celtic-cross-guide"]) == tb.EXIT_OK
    assert tb.main(["upload", pic, "--for", "another-article"]) == tb.EXIT_RULE
    assert len(api.uploads) == 2


def test_upload_without_for_ties_the_picture_to_that_upload_only(env):
    tmp, api, _ = env
    pic = _generated(tmp, "inline.jpg", b"\xff\xd8 orchard lanterns")
    assert tb.main(["upload", pic]) == tb.EXIT_OK
    assert _used(tmp)[tb.sha256_of(pic)]["post"].startswith("(upload ")
    assert tb.main(["upload", pic]) == tb.EXIT_RULE
    assert tb.main(["upload", pic, "--for", "some-article"]) == tb.EXIT_RULE


def test_upload_refuses_unknown_pictures_unless_operator_image(env):
    tmp, api, _ = env
    other = tmp / "someone-else.png"
    other.write_bytes(b"\x89PNG operator picture")
    assert tb.main(["upload", str(other), "--for", "x"]) == tb.EXIT_RULE
    assert api.calls == []
    assert tb.main(["upload", str(other), "--for", "x", "--operator-image"]) == tb.EXIT_OK


def test_upload_prints_the_url_for_the_markdown(env, capsys):
    tmp, api, _ = env
    pic = _generated(tmp, "inline.jpg", b"\xff\xd8 orchard lanterns")
    assert tb.main(["upload", pic, "--for", "x"]) == tb.EXIT_OK
    assert "/blog/media/img-1.webp" in capsys.readouterr().out


def test_update_refuses_a_dry_run_patch(env, tmp_path):
    _, api, _ = env
    patch = tmp_path / "patch.json"
    patch.write_text(json.dumps({"title": "New title", "dry_run": True}), encoding="utf-8")
    assert tb.main(["update", "post-1", str(patch)]) == tb.EXIT_USAGE
    assert api.calls == []


def test_older_progress_records_are_read(env):
    tmp, api, article = env
    pic = tmp / "old.jpg"
    pic.write_bytes(b"\xff\xd8 older")
    (tmp / "images-progress.json").write_text(json.dumps(
        {"post-A": {"cover": {"file": str(pic), "url": "/m", "alt": "a bridge", "when": "2026-10-01"}, "inline": []}}
    ), encoding="utf-8")
    assert tb.main(["post", article, "--cover", str(pic), "--operator-image"]) == tb.EXIT_RULE
