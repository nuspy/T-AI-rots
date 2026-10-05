"""One key for both skills: without a media key, tarots_images.py uses the key of tarots_blog.py, offline.

    backend/.venv/Scripts/python.exe -m pytest skills/tarots-blog-images/tests -q -p no:cacheprovider

No network: the HTTP opener is a fake that records the key it receives and answers what the test says (200 or 403).
"""
from __future__ import annotations

import importlib.util
import io
import json
import urllib.error
from pathlib import Path

import pytest

SKILLS = Path(__file__).resolve().parents[2]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ti = _load("tarots_images_una_chiave", SKILLS / "tarots-blog-images" / "scripts" / "tarots_images.py")
tb = _load("tarots_blog_una_chiave", SKILLS / "tarots-blog-publisher" / "scripts" / "tarots_blog.py")

URL = "https://tarots.example/api"
BLOG_KEY = "tk_live_BLOG0000000000000000"
MEDIA_KEY = "tk_live_MEDIA000000000000000"
OTHER_KEY = "tk_live_OTHER000000000000000"


@pytest.fixture
def keys(tmp_path, monkeypatch):
    """No key anywhere, files in tmp: each test saves the ones it needs."""
    monkeypatch.setattr(ti, "CACHE_PATH", tmp_path / "media-credentials.json")
    monkeypatch.setattr(ti, "BLOG_CACHE_PATH", tmp_path / "credentials.json")
    monkeypatch.setattr(tb, "CACHE_PATH", tmp_path / "credentials.json")
    monkeypatch.setattr(ti, "_noted", False)
    for name in ("TAROTS_MEDIA_KEY", "TAROTS_API_KEY", "TAROTS_API_URL"):
        monkeypatch.delenv(name, raising=False)
    return tmp_path


def save_blog_key(monkeypatch, key=BLOG_KEY):
    """As the operator does it: `tarots_blog.py key save` with the variables set once."""
    monkeypatch.setenv("TAROTS_API_URL", URL)
    monkeypatch.setenv("TAROTS_API_KEY", key)
    assert tb.main(["key", "save"]) == tb.EXIT_OK
    monkeypatch.delenv("TAROTS_API_URL")
    monkeypatch.delenv("TAROTS_API_KEY")


class FakeOpener:
    def __init__(self, status=200, body=None):
        self.status, self.body, self.keys = status, body, []

    def open(self, request, timeout=None):
        self.keys.append(request.get_header("Authorization"))
        if self.status != 200:
            raise urllib.error.HTTPError(request.full_url, self.status, "x", {},
                                         io.BytesIO(json.dumps({"detail": "Permesso mancante"}).encode()))
        payload = json.dumps(self.body).encode()

        class Response(io.BytesIO):
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False
        return Response(payload)


def test_without_a_media_key_the_saved_key_of_tarots_blog_is_used_with_a_note(keys, monkeypatch, capsys):
    save_blog_key(monkeypatch)
    capsys.readouterr()
    cfg = ti.config()
    assert cfg == {"base": URL, "key": BLOG_KEY, "source": "blog"}
    err = capsys.readouterr().err
    assert "note: no media key" in err and "using the key of tarots_blog.py (prefix tk_live_BLOG" in err
    assert BLOG_KEY not in err                               # only the prefix
    assert not (keys / "media-credentials.json").exists()   # nothing copied into the media file


def test_the_blog_key_is_sent_to_the_api(keys, monkeypatch, capsys):
    save_blog_key(monkeypatch)
    opener = FakeOpener(body={"articoli": [], "totale": 0})
    monkeypatch.setattr(ti, "_OPENER", opener)
    assert ti.main(["list"]) == ti.EXIT_OK
    assert opener.keys == [f"Bearer {BLOG_KEY}"]


def test_tarots_api_key_in_the_environment_works_too(keys, monkeypatch):
    monkeypatch.setenv("TAROTS_API_URL", URL)
    monkeypatch.setenv("TAROTS_API_KEY", BLOG_KEY)
    assert ti.config()["key"] == BLOG_KEY
    assert not (keys / "credentials.json").exists()          # tarots_images.py never writes the blog's file


def test_a_media_key_wins_over_the_blog_key(keys, monkeypatch, capsys):
    save_blog_key(monkeypatch)
    monkeypatch.setenv("TAROTS_API_URL", URL)
    monkeypatch.setenv("TAROTS_MEDIA_KEY", MEDIA_KEY)
    assert ti.config() == {"base": URL, "key": MEDIA_KEY, "source": "media"}
    monkeypatch.delenv("TAROTS_MEDIA_KEY")
    assert ti.config()["key"] == MEDIA_KEY                  # saved in media-credentials.json on first use
    capsys.readouterr()
    assert ti.main(["key", "show"]) == ti.EXIT_OK
    out = capsys.readouterr().out
    assert "key of tarots_blog.py: tk_live_BLOG... " in out and "not used: a media key wins" in out


def test_an_ambiguous_blog_key_is_refused_as_tarots_blog_refuses_it(keys, monkeypatch):
    save_blog_key(monkeypatch)
    monkeypatch.setenv("TAROTS_API_KEY", OTHER_KEY)
    with pytest.raises(ti.Failure) as exc:
        ti.config()
    assert exc.value.code == ti.EXIT_CONFIG and "tarots_blog.py key save" in str(exc.value)


def test_no_key_at_all_says_how_to_make_the_one_key(keys, monkeypatch, capsys):
    monkeypatch.setenv("TAROTS_API_URL", URL)
    assert ti.main(["list"]) == ti.EXIT_CONFIG
    err = capsys.readouterr().err
    assert "ONE key with the three permissions write + publish + media" in err and "tarots_blog.py key save" in err


def test_a_403_with_the_blog_key_says_to_make_one_key_with_three_permissions(keys, monkeypatch, capsys):
    save_blog_key(monkeypatch)
    monkeypatch.setattr(ti, "_OPENER", FakeOpener(status=403))
    for command in (["list"], ["show", "id-1"]):
        assert ti.main(command) == ti.EXIT_API
        err = capsys.readouterr().err
        assert "HTTP 403" in err and "This key cannot change pictures" in err
        assert ("create in the console (Blog → Keys) ONE key with the three permissions write + publish + media, "
                "and save it with `tarots_blog.py key save`; both skills will use it") in err
        assert BLOG_KEY not in err


def test_a_403_with_a_media_key_gives_the_same_advice(keys, monkeypatch, capsys):
    monkeypatch.setenv("TAROTS_API_URL", URL)
    monkeypatch.setenv("TAROTS_MEDIA_KEY", MEDIA_KEY)
    monkeypatch.setattr(ti, "_OPENER", FakeOpener(status=403))
    assert ti.main(["list"]) == ti.EXIT_API
    err = capsys.readouterr().err
    assert "Permesso mancante" in err and "ONE key with the three permissions" in err


def test_generate_and_prompt_check_still_need_no_key(keys, monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(ti, "PROGRESS_PATH", tmp_path / "images-progress.json")
    prompt = ("A lighthouse on a black basalt cliff in a winter storm, one bolt of lightning splitting the sky, waves "
              "breaking against the rocks, seen from a fishing harbour far below, looking up, " + ti.HOUSE_STYLE)
    assert ti.main(["prompt-check", "--prompt", prompt, "--kind", "architecture", "--shot", "low-angle", "--light",
                    "storm-light", "--setting", "Breton coast"]) == ti.EXIT_OK
