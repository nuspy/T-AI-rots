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
    article.write_text(json.dumps({"title": "The Tower", "body": "text", "status": "draft"}), encoding="utf-8")
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
    assert tb.CARD_PATTERNS == [pattern for pattern, _what, _alt in ti.CARD_PATTERNS]
    assert tb.DECK == ti.DECK and tb.NOT_A_CARD_DECK == ti.NOT_A_CARD_DECK


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
