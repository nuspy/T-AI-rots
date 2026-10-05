"""The pictures of the sections and of the spreads (`sections`, `spreads`, `section-cover`, `spread-cover`) and the
articles without a cover (`list --no-cover`), offline.

    backend/.venv/Scripts/python.exe -m pytest skills/tarots-blog-images/tests -q -p no:cacheprovider

No network, no LitMedia: the API is a fake that answers the contract of 5/10/2026 (GET /media-sections and
/media-spreads, PUT /media-sections/{slug} and /media-spreads/{id}, POST /media, GET /media-posts).
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "tarots_images.py"
_spec = importlib.util.spec_from_file_location("tarots_images_sezioni", SCRIPT)
ti = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ti)

PROMPT = ("A row of old fishing boats drawn up on a pebble beach at first light, nets drying on wooden poles, a heron "
          "standing in the shallows, seen from the dunes, wide view, dawn, " + ti.HOUSE_STYLE)
CARD_PROMPT = ("A row of old fishing boats drawn up on a pebble beach at first light, nets drying on wooden poles, and "
               "on a boat a single small card of the Moon, in the style of the Thoth deck, " + ti.HOUSE_STYLE)


class FakeApi:
    def __init__(self):
        self.calls = []
        self.sections = [
            {"slug": "major-arcana", "nome": "Major Arcana", "tipo": "carte", "descrizione": "The great themes.",
             "immagine": None},
            {"slug": "cups", "nome": "Cups", "tipo": "carte", "descrizione": "Water: emotions.",
             "immagine": {"id": "m1", "url": "/blog/media/m1.webp", "mini": "/blog/media/m1-mini.webp", "alt": "sea"}},
        ]
        self.spreads = {"stese": [
            {"id": "croce-celtica", "nome": "Celtic Cross", "descrizione": "Ten cards.", "tradizione": "Celtic",
             "n_carte": 10, "immagine": None},
        ]}
        self.posts = [
            {"id": "p1", "titolo": "Wheel of Fortune", "stato": "pubblicato", "lang": "en", "copertina": None,
             "immagini_nel_testo": []},
            {"id": "p2", "titolo": "A draft", "stato": "bozza", "lang": "en",
             "copertina": {"id": "c", "url": "/u"}, "immagini_nel_testo": []},
            {"id": "p3", "titolo": "Another draft", "stato": "bozza", "lang": "en", "copertina": None,
             "immagini_nel_testo": []},
        ]

    def __call__(self, method, path, body=None, query=None, **kw):
        self.calls.append((method, path, body))
        if path == "/media-sections":
            return self.sections
        if path == "/media-spreads":
            return self.spreads
        if path == "/media":
            return {"id": "img-9", "url": "/blog/media/img-9.webp", "mini": "/blog/media/img-9-mini.webp"}
        if method == "PUT" and path.startswith(("/media-sections/", "/media-spreads/")):
            return {"slug": path.rsplit("/", 1)[1], "immagine": {"id": body["immagine_id"], "url": "/blog/media/img-9.webp"}}
        if path == "/media-posts":
            rows = [p for p in self.posts if not query.get("stato") or p["stato"] == query["stato"]]
            return {"totale": len(rows), "pagina": 1, "per_pagina": 100, "articoli": rows}
        raise AssertionError(f"unexpected call {method} {path}")


@pytest.fixture
def api(tmp_path, monkeypatch):
    fake = FakeApi()
    monkeypatch.setattr(ti, "PROGRESS_PATH", tmp_path / "images-progress.json")
    monkeypatch.setenv("TAROTS_WORK_DIR", str(tmp_path / "work"))
    monkeypatch.setattr(ti, "call", fake)
    monkeypatch.setattr(ti, "upload", lambda path: fake("POST", "/media"))
    return fake


def _picture(tmp: Path, name: str, content: bytes, prompt: str = PROMPT) -> str:
    path = tmp / name
    path.write_bytes(content)
    Path(str(path) + ".prompt.txt").write_text(prompt, encoding="utf-8")
    ti._record_generated(prompt, path, "3:2", target={"role": "section", "section": "major-arcana"})
    return str(path)


# ---- the lists ----------------------------------------------------------------------------------------------------


def test_sections_and_spreads_list_their_picture_or_its_absence(api, capsys):
    assert ti.main(["sections"]) == ti.EXIT_OK
    out = capsys.readouterr().out
    assert "major-arcana" in out and "no picture" in out and "cups" in out and "2 section(s)" in out
    assert ti.main(["sections", "--missing", "--json"]) == ti.EXIT_OK
    assert [r["slug"] for r in json.loads(capsys.readouterr().out)] == ["major-arcana"]
    assert ti.main(["spreads", "--missing"]) == ti.EXIT_OK                 # an object holding the list: read too
    out = capsys.readouterr().out
    assert "croce-celtica" in out and "10 cards" in out and "Celtic" in out and "1 spread(s)" in out


def test_an_answer_that_is_not_a_list_says_so(api, capsys):
    api.sections = {"detail": "Not Found"}
    assert ti.main(["sections"]) == ti.EXIT_API
    assert "not a list" in capsys.readouterr().err


def test_list_no_cover_takes_every_status(api, capsys):
    assert ti.main(["list", "--no-cover", "--json"]) == ti.EXIT_OK
    assert [p["id"] for p in json.loads(capsys.readouterr().out)] == ["p1", "p3"]   # published and draft
    assert ti.main(["list", "--no-cover", "--status", "draft", "--json"]) == ti.EXIT_OK
    assert [p["id"] for p in json.loads(capsys.readouterr().out)] == ["p3"]


# ---- section-cover and spread-cover ----------------------------------------------------------------------------------


def test_section_cover_uploads_puts_and_records(api, tmp_path, capsys):
    pic = _picture(tmp_path, "section.jpg", b"\xff\xd8 boats")
    assert ti.main(["section-cover", "major-arcana", pic, "--alt", "Fishing boats on a beach at dawn"]) == ti.EXIT_OK
    put = [c for c in api.calls if c[0] == "PUT"]
    assert put == [("PUT", "/media-sections/major-arcana", {"immagine_id": "img-9", "alt": "Fishing boats on a beach at dawn"})]
    assert "section picture set: /blog/media/img-9.webp" in capsys.readouterr().out
    data = json.loads(ti.PROGRESS_PATH.read_text(encoding="utf-8"))
    assert data["_sections"]["major-arcana"]["file"] == pic
    assert data["_used"][ti.sha256_of(pic)]["post"] == "section:major-arcana"
    # the same picture can go on the same section again, never on another section, spread or article
    assert ti.main(["section-cover", "major-arcana", pic, "--alt", "Fishing boats on a beach", "--dry-run"]) == ti.EXIT_OK
    assert ti.main(["section-cover", "cups", pic, "--alt", "Fishing boats on a beach", "--dry-run"]) == ti.EXIT_RULE
    assert "already a picture of the section major-arcana" in capsys.readouterr().err
    assert ti.main(["spread-cover", "croce-celtica", pic, "--alt", "Fishing boats", "--dry-run"]) == ti.EXIT_RULE
    assert ti.main(["cover", "p1", pic, "--alt", "Fishing boats on a beach", "--dry-run"]) == ti.EXIT_RULE


def test_spread_cover_and_its_dry_run(api, tmp_path, capsys):
    pic = _picture(tmp_path, "spread.jpg", b"\xff\xd8 crossing")
    assert ti.main(["spread-cover", "croce-celtica", pic, "--alt", "A crossroads at dawn", "--dry-run"]) == ti.EXIT_OK
    assert "would become" in capsys.readouterr().out and not [c for c in api.calls if c[0] == "PUT"]
    assert ti.main(["spread-cover", "croce-celtica", pic, "--alt", "A crossroads at dawn"]) == ti.EXIT_OK
    assert ("PUT", "/media-spreads/croce-celtica", {"immagine_id": "img-9", "alt": "A crossroads at dawn"}) in api.calls
    assert "croce-celtica" in json.loads(ti.PROGRESS_PATH.read_text(encoding="utf-8"))["_spreads"]


def test_a_picture_of_a_section_with_a_card_or_a_spread_alt_is_refused(api, tmp_path):
    pic = _picture(tmp_path, "moon.jpg", b"\xff\xd8 moon card", prompt=CARD_PROMPT)
    assert ti.main(["section-cover", "major-arcana", pic, "--alt", "Boats on a beach"]) == ti.EXIT_RULE
    ok = _picture(tmp_path, "ok.jpg", b"\xff\xd8 ok")
    assert ti.main(["spread-cover", "croce-celtica", ok, "--alt", "Ten tarot cards laid out on velvet"]) == ti.EXIT_RULE
    assert not [c for c in api.calls if c[0] == "PUT"]
