"""The work folder, the H1 at the top, NEXT, the focus keyword rules and the rounds of `check`, offline.

    backend/.venv/Scripts/python.exe -m pytest skills/tarots-blog-publisher/tests skills/tarots-blog-images/tests -q -p no:cacheprovider

Each test fixes one of the mistakes seen on 5/10/2026 (a small local model writing one article with the skill): files
written in the skill's folder and then searched on the whole disk, an `# H1` never removed, a keyword nobody searches
pasted into the title, more than ten rounds of `check` each rewriting the whole text, warnings that did not say what
to do. The API is a fake: `POST /seo-check` answers the report the test sets, `GET /titles` a small blog.
"""
from __future__ import annotations

import datetime
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


tb = _load("tarots_blog_cartella", SKILLS / "tarots-blog-publisher" / "scripts" / "tarots_blog.py")
ti = _load("tarots_images_cartella_blog", SKILLS / "tarots-blog-images" / "scripts" / "tarots_images.py")

TODAY = datetime.date.today().isoformat()
T0 = "2026-10-05T10:00:00+00:00"


def item(cid, esito="avviso", peso=1, messaggio="", **dettaglio):
    return {"id": cid, "esito": esito, "peso": peso, "messaggio": messaggio or f"{cid} message",
            **({"dettaglio": dettaglio} if dettaglio else {})}


def report(score, *items, **stats):
    return {"punteggio": score, "giudizio": "ottimo" if score >= 85 else "buono", "controlli": list(items),
            "statistiche": {"parole": 900, "titoli_h2": 3, "collegamenti_interni": 2, "collegamenti_esterni": 1,
                            "faq": 3, **stats}}


def row(n, slug, title, keyword, lang="en"):
    return {"id": f"id-{n}", "slug": slug, "titolo": title, "estratto": "", "parola_chiave": keyword, "sezione": None,
            "lang": lang, "stato": "pubblicato", "pubblicato_il": "2026-10-01T08:00:00+00:00",
            "aggiornato": "2026-10-01T08:00:00+00:00", "mio": False, "tradotto_da_id": None}


class FakeBlog:
    """`/seo-check`, `/titles`, `/posts` (dry run and save) and `/media`, remembered in `calls`."""

    def __init__(self):
        self.calls = []
        self.seo = report(90)
        self.titles = [row(1, "the-tower-thoth-tarot-meaning", "The Tower in the Thoth Tarot", "tower tarot meaning"),
                       row(2, "full-moon-tarot-spread", "A Full Moon Tarot Spread", "full moon tarot spread")]

    def __call__(self, method, path, body=None, query=None, **kwargs):
        self.calls.append((method, path))
        if path == "/seo-check":
            return self.seo
        if path == "/titles":
            return {"totale": len(self.titles), "pagina": 1, "per_pagina": 1000, "adesso": T0, "articoli": self.titles}
        if path == "/media":
            return {"id": "img-1", "url": "/blog/media/img-1.webp", "larghezza": 1600, "altezza": 1067, "byte": 10}
        if path == "/posts" and (body or {}).get("dry_run"):
            return {"seo": self.seo}
        if path == "/posts":
            return {"articolo": {"id": "post-new", "slug": body.get("slug"), "stato": "bozza", "lang": "en"},
                    "url": "https://tarots.chat/blog/x", "avvisi": []}
        raise AssertionError(f"unexpected call {method} {path}")

    def paths(self):
        return [p for _, p in self.calls]


@pytest.fixture
def blog(tmp_path, monkeypatch):
    fake = FakeBlog()
    monkeypatch.setattr(tb, "call", fake)
    monkeypatch.setattr(tb, "_identity", lambda: "https://tarots.test/api|tk_live_abcd")
    monkeypatch.setattr(tb, "TITLES_CACHE_PATH", tmp_path / "titles-cache.json")
    monkeypatch.setattr(tb, "PROGRESS_PATH", tmp_path / "images-progress.json")
    monkeypatch.setenv("TAROTS_WORK_DIR", str(tmp_path / "work"))
    return fake


BODY = ("A samhain tarot spread is a short reading for the night when the year turns.\n\n"
        "## How the samhain tarot spread works\n\nFive positions, one question each.\n\n## The positions\n\nText.\n")


def make_article(slug="samhain-tarot-spread", *, keyword="samhain tarot spread", body=BODY, **fields):
    """An article as an agent leaves it after `new` and the writing."""
    assert tb.main(["new", slug]) == tb.EXIT_OK
    folder = tb.work_root() / f"{TODAY}-{slug}"
    data = {**tb.skeleton(slug), "title": "A Samhain Tarot Spread for the Turning Year", "focus_keyword": keyword,
            "seo_title": "Samhain Tarot Spread: Five Cards for the Thin Night", **fields}
    (folder / "article.json").write_text(json.dumps(data), encoding="utf-8")
    (folder / "article.md").write_text(body, encoding="utf-8")
    return folder


# ---- the H1 at the top of the body ----------------------------------------------------------------------------------


def test_a_leading_h1_is_removed_with_a_note(capsys):
    p = tb.normalize({"title": "T", "body": "﻿\n# Autumn Balance: balance tarot meditation autumn\n\n\n## One\n\nText.\n"})
    assert p["testo"] == "## One\n\nText.\n"
    assert "removed the H1" in capsys.readouterr().err


@pytest.mark.parametrize("body", ["## One\n\n# Inner title\n\nText.", "Intro first.\n\n# Later\n", "#hashtag at the start", ""])
def test_anything_else_is_left_as_it_is(body, capsys):
    assert tb.normalize({"title": "T", "body": body})["testo"] == body
    assert capsys.readouterr().err == ""


def test_the_h1_goes_also_from_a_body_file(tmp_path):
    (tmp_path / "article.md").write_text("# Title\n## One\n\nText.", encoding="utf-8")
    assert tb.normalize({"title": "T", "body_file": "article.md"}, tmp_path)["testo"] == "## One\n\nText."


# ---- new: the work folder ---------------------------------------------------------------------------------------------


def test_new_creates_the_work_folder_with_a_skeleton_and_prints_absolute_paths(blog, tmp_path, capsys):
    assert tb.main(["new", "Samhain:", "a Tarot Spread!"]) == tb.EXIT_OK
    folder = tmp_path / "work" / f"{TODAY}-samhain-a-tarot-spread"
    data = json.loads((folder / "article.json").read_text(encoding="utf-8"))
    assert data["status"] == "draft" and data["body_file"] == "article.md" and data["slug"] == "samhain-a-tarot-spread"
    assert data["seo_title"] == data["seo_description"] == data["focus_keyword"] == "" and data["faq"] == []
    assert (folder / "article.md").read_text(encoding="utf-8") == "" and (folder / "foto").is_dir()
    out = capsys.readouterr().out
    assert str(folder.resolve()) in out and str((folder / "foto").resolve()) in out
    assert "check samhain-a-tarot-spread" in out
    # every field of the skeleton is one the script knows: once filled it is a valid article file
    assert tb.normalize({**data, "title": "x", "body": "y"}, folder)
    # a second `new` never overwrites
    (folder / "article.json").write_text('{"title": "mine"}', encoding="utf-8")
    assert tb.main(["new", "samhain-a-tarot-spread"]) == tb.EXIT_OK
    assert "already exists" in capsys.readouterr().out
    assert json.loads((folder / "article.json").read_text(encoding="utf-8")) == {"title": "mine"}


def test_new_json_and_a_name_without_letters(blog, capsys):
    assert tb.main(["--json", "new", "shadow work"]) == tb.EXIT_OK
    data = json.loads(capsys.readouterr().out)
    assert data["slug"] == "shadow-work" and data["foto"].endswith("foto") and data["existed"] is False
    assert tb.main(["new", "!!!"]) == tb.EXIT_USAGE


def test_the_slug_is_the_same_in_both_scripts():
    for text in ["Samhain: a Tarot Spread!", "Crowley’s Æon — the Thoth card XX", "  the-tower  ", "x" * 80 + " tail"]:
        assert tb.slugify(text) == ti.work_slug(text)
    assert tb.WORK_NAME.pattern == ti.WORK_NAME.pattern


# ---- ARTICLE: a slug, a folder or a file ------------------------------------------------------------------------------


def test_check_takes_the_slug_the_folder_or_the_file(blog):
    folder = make_article()
    for arg in ("samhain-tarot-spread", "Samhain Tarot Spread", str(folder), str(folder / "article.json")):
        assert tb.main(["check", arg]) == tb.EXIT_OK, arg
    assert blog.paths().count("/seo-check") == 4


def test_the_newest_folder_of_a_slug_wins(blog, tmp_path):
    old = tmp_path / "work" / "2026-09-01-samhain-tarot-spread"
    old.mkdir(parents=True)
    (old / "article.json").write_text(json.dumps({"title": "OLD", "body": "old"}), encoding="utf-8")
    make_article()
    assert tb.resolve_article("samhain-tarot-spread").parent.name == f"{TODAY}-samhain-tarot-spread"
    # a folder found by the slug inside its article.json, when the folder has the working title
    other = tmp_path / "work" / "2026-09-02-working-title"
    other.mkdir()
    (other / "article.json").write_text(json.dumps({"title": "T", "slug": "real-slug"}), encoding="utf-8")
    assert tb.resolve_article("real-slug") == other / "article.json"


def test_a_missing_article_says_where_to_look_and_never_searches(blog, tmp_path, capsys, monkeypatch):
    make_article()
    monkeypatch.chdir(tmp_path)
    for arg in ("no-such-slug", "article.json", str(tmp_path / "nowhere" / "article.json")):
        assert tb.main(["check", arg]) == tb.EXIT_USAGE
        err = capsys.readouterr().err
        assert str(tmp_path / "work") in err and "tarots_blog.py new" in err and "Do not search the disk" in err
        assert f"{TODAY}-samhain-tarot-spread" in err          # the newest work folders are listed
    assert blog.calls == []


def test_an_article_inside_the_skill_folder_is_refused(blog, tmp_path, monkeypatch, capsys):
    skill = tmp_path / "tarots-blog-publisher"
    (skill / "assets").mkdir(parents=True)
    monkeypatch.setattr(tb, "SKILL_DIR", skill)
    (skill / "article.json").write_text(json.dumps({"title": "T", "body": "B"}), encoding="utf-8")
    assert tb.main(["check", str(skill / "article.json")]) == tb.EXIT_USAGE
    assert "inside the skill's folder" in capsys.readouterr().err and blog.calls == []
    (skill / "assets" / "example.json").write_text(json.dumps({"title": "T", "body": "B"}), encoding="utf-8")
    assert tb.main(["check", str(skill / "assets" / "example.json")]) == tb.EXIT_OK  # the example stays usable


def test_an_empty_skeleton_says_which_file_to_fill(blog, capsys):
    tb.main(["new", "empty-one"])
    capsys.readouterr()
    assert tb.main(["check", "empty-one"]) == tb.EXIT_USAGE
    err = capsys.readouterr().err
    assert '"title" is empty' in err and "article.md" in err and blog.calls == []


def test_post_finds_a_bare_cover_name_in_foto(blog):
    folder = make_article()
    cover = folder / "foto" / "cover.jpg"
    cover.write_bytes(b"\xff\xd8 lantern orchard")
    prompt = ("An orchard of old apple trees at the edge of a village, lanterns hung in the branches for a harvest "
              "feast, seen from above, " + ti.HOUSE_STYLE)
    tb.PROGRESS_PATH.write_text(json.dumps({"_generated": [{"prompt": prompt, "file": str(cover),
                                                             "sha256": tb.sha256_of(cover)}]}), encoding="utf-8")
    assert tb.main(["post", "samhain-tarot-spread", "--cover", "cover.jpg"]) == tb.EXIT_OK
    assert "/media" in blog.paths()
    used = json.loads(tb.PROGRESS_PATH.read_text(encoding="utf-8"))["_used"][tb.sha256_of(cover)]
    assert used["file"] == str(cover) and used["post"] == "post-new"


# ---- post without --cover: the cover of foto/, or a stop (seen on 5/10/2026) -------------------------------------------


COVER_PROMPT = ("An orchard of old apple trees at the edge of a village, lanterns hung in the branches for a harvest "
                "feast, seen from above, " + ti.HOUSE_STYLE)


def _generated_cover(folder, name="cover.jpg", content=b"\xff\xd8 lantern orchard", prompt=COVER_PROMPT):
    """foto/<name> as `tarots_images.py generate --article` leaves it: the file and its record in `_generated`."""
    cover = folder / "foto" / name
    cover.write_bytes(content)
    data = json.loads(tb.PROGRESS_PATH.read_text(encoding="utf-8")) if tb.PROGRESS_PATH.exists() else {}
    data.setdefault("_generated", []).append({"prompt": prompt, "file": str(cover), "sha256": tb.sha256_of(cover)})
    tb.PROGRESS_PATH.write_text(json.dumps(data), encoding="utf-8")
    return cover


def test_post_without_cover_uses_the_cover_in_foto_with_a_note(blog, capsys):
    folder = make_article()
    cover = _generated_cover(folder)
    assert tb.main(["post", "samhain-tarot-spread"]) == tb.EXIT_OK
    assert f"no --cover given: using {cover}" in capsys.readouterr().err
    assert "/media" in blog.paths()
    assert json.loads(tb.PROGRESS_PATH.read_text(encoding="utf-8"))["_used"][tb.sha256_of(cover)]["post"] == "post-new"


@pytest.mark.parametrize("name", ["cover.jpeg", "cover.png", "COVER.webp"])
def test_every_cover_extension_is_found(blog, name):
    folder = make_article()
    _generated_cover(folder, name)
    assert tb.main(["post", "samhain-tarot-spread"]) == tb.EXIT_OK
    assert "/media" in blog.paths()


def test_post_without_any_cover_stops_and_says_what_to_do(blog, capsys):
    folder = make_article()
    (folder / "foto" / "inline-1.jpg").write_bytes(b"\xff\xd8 not a cover")
    assert tb.main(["post", "samhain-tarot-spread"]) == tb.EXIT_NO_COVER == 11
    err = capsys.readouterr().err
    assert "no cover" in err and str(folder / "foto") in err and "Nothing was saved" in err
    assert "generate --article samhain-tarot-spread" in err and "--no-cover" in err and "report" in err
    assert "/posts" not in blog.paths() and "/media" not in blog.paths()  # stopped before the check: nothing saved
    assert tb.main(["post", "samhain-tarot-spread", "--dry-run"]) == tb.EXIT_NO_COVER  # the dry run says the same


def test_the_cover_found_in_foto_passes_every_check_of_the_record(blog, capsys):
    folder = make_article()
    # not made by generate: refused, as with --cover
    (folder / "foto" / "cover.jpg").write_bytes(b"\xff\xd8 downloaded from somewhere")
    assert tb.main(["post", "samhain-tarot-spread"]) == tb.EXIT_RULE
    assert "was not made by `tarots_images.py generate`" in capsys.readouterr().err
    (folder / "foto" / "cover.jpg").unlink()
    # already the cover of another article: refused
    cover = _generated_cover(folder)
    data = json.loads(tb.PROGRESS_PATH.read_text(encoding="utf-8"))
    data["_used"] = {tb.sha256_of(cover): {"post": "another-article", "kind": "cover", "file": "x"}}
    tb.PROGRESS_PATH.write_text(json.dumps(data), encoding="utf-8")
    assert tb.main(["post", "samhain-tarot-spread"]) == tb.EXIT_RULE
    assert "already a picture of article another-article" in capsys.readouterr().err
    cover.unlink()
    # a single small card, in the Thoth style, as context: admitted even though this article is about no card
    # (the warning that it is not the article's own card is lost here: `post` discards card warnings)
    _generated_cover(folder, content=b"\xff\xd8 fool", prompt=(
        "A quiet garden at dawn with a stone bench and a cup of tea, and beside it a single small card of the Fool "
        "in the style of the Thoth deck, seen from above, " + ti.HOUSE_STYLE))
    assert tb.main(["post", "samhain-tarot-spread"]) == tb.EXIT_OK
    assert "/posts" in blog.paths() and "/media" in blog.paths()


def test_two_covers_in_foto_ask_to_choose(blog, capsys):
    folder = make_article()
    _generated_cover(folder, "cover.jpg", b"\xff\xd8 one")
    _generated_cover(folder, "cover.png", b"\x89PNG two", prompt=COVER_PROMPT.replace("apple", "pear"))
    assert tb.main(["post", "samhain-tarot-spread"]) == tb.EXIT_USAGE
    assert "more than one cover (cover.jpg, cover.png)" in capsys.readouterr().err and "/posts" not in blog.paths()
    assert tb.main(["post", "samhain-tarot-spread", "--cover", "cover.png"]) == tb.EXIT_OK


def test_no_cover_saves_without_a_picture_and_says_so(blog, capsys):
    make_article()
    assert tb.main(["post", "samhain-tarot-spread", "--no-cover"]) == tb.EXIT_OK
    assert "saved WITHOUT a cover" in capsys.readouterr().err and "/media" not in blog.paths()
    # with a cover still in foto/, --no-cover leaves it out and says so
    folder = make_article("lantern-night", keyword="lantern night tarot")
    _generated_cover(folder)
    assert tb.main(["post", "lantern-night", "--no-cover"]) == tb.EXIT_OK
    assert "foto/ has cover.jpg, NOT used" in capsys.readouterr().err
    with pytest.raises(SystemExit):                          # --cover and --no-cover together: a usage error
        tb.main(["post", "lantern-night", "--no-cover", "--cover", "cover.jpg"])


# ---- covers with names of their own: the LAST one recorded for the slug (5/10/2026) -----------------------------------


def _named_cover(folder, name, content, *, article="samhain-tarot-spread", role="cover", prompt=COVER_PROMPT,
                 when="2026-10-05T10:00:00+00:00"):
    """foto/<name> as `tarots_images.py generate --article` leaves it now: the record says article and role."""
    cover = folder / "foto" / name
    cover.write_bytes(content)
    data = json.loads(tb.PROGRESS_PATH.read_text(encoding="utf-8")) if tb.PROGRESS_PATH.exists() else {}
    data.setdefault("_generated", []).append({"prompt": prompt, "file": str(cover), "sha256": tb.sha256_of(cover),
                                              "role": role, "article": article, "article_id": None, "when": when})
    tb.PROGRESS_PATH.write_text(json.dumps(data), encoding="utf-8")
    return cover


def test_post_takes_the_last_cover_recorded_for_the_slug_and_names_it(blog, capsys):
    folder = make_article()
    _named_cover(folder, "cover-20261005-100000.jpg", b"\xff\xd8 first")
    _named_cover(folder, "inline-20261005-101000.jpg", b"\xff\xd8 inline", role="inline",
                 prompt=COVER_PROMPT.replace("apple", "plum"))
    last = _named_cover(folder, "cover-20261005-102000.jpg", b"\xff\xd8 second",
                        prompt=COVER_PROMPT.replace("apple", "pear"))
    _named_cover(folder, "cover-20261005-103000.jpg", b"\xff\xd8 of another article", article="another-one",
                 prompt=COVER_PROMPT.replace("apple", "cherry"))
    (folder / "foto" / "cover.jpg").write_bytes(b"\xff\xd8 an old-style file, not used")
    assert tb.main(["post", "samhain-tarot-spread"]) == tb.EXIT_OK
    captured = capsys.readouterr()
    assert f"no --cover given: using {last}, the last cover generated for samhain-tarot-spread" in captured.err
    assert "1 older one(s) left aside" in captured.err and "warning" not in captured.err
    assert f"cover: {last}" in captured.out
    assert json.loads(tb.PROGRESS_PATH.read_text(encoding="utf-8"))["_used"][tb.sha256_of(last)]["post"] == "post-new"


def test_a_cover_whose_file_is_gone_is_skipped_and_named_when_none_is_left(blog, capsys):
    folder = make_article()
    first = _named_cover(folder, "cover-20261005-100000.jpg", b"\xff\xd8 first")
    gone = _named_cover(folder, "cover-20261005-102000.jpg", b"\xff\xd8 second", prompt=COVER_PROMPT.replace("apple", "pear"))
    gone.unlink()
    assert tb.main(["post", "samhain-tarot-spread", "--dry-run"]) == tb.EXIT_OK
    assert f"using {first}" in capsys.readouterr().err                    # the last one still on disk
    first.unlink()
    blog.calls.clear()
    assert tb.main(["post", "samhain-tarot-spread"]) == tb.EXIT_NO_COVER
    err = capsys.readouterr().err
    assert f"the cover generated for samhain-tarot-spread is no longer on disk: {gone}" in err
    assert str(first) in err and "Nothing was saved" in err and "/media" not in blog.paths()


def test_the_cover_is_found_also_by_the_slug_in_the_folder_name(blog, capsys):
    folder = make_article("lantern-night", keyword="lantern night tarot")
    data = json.loads((folder / "article.json").read_text(encoding="utf-8"))
    (folder / "article.json").write_text(json.dumps({**data, "slug": "lantern-night-tarot"}), encoding="utf-8")
    # generated with --article lantern-night before article.json had its final slug
    cover = _named_cover(folder, "cover-20261005-100000.jpg", b"\xff\xd8 lanterns", article="lantern-night")
    assert tb.main(["post", "lantern-night"]) == tb.EXIT_OK
    assert f"using {cover}" in capsys.readouterr().err


def test_an_explicit_cover_still_wins(blog, capsys):
    folder = make_article()
    _named_cover(folder, "cover-20261005-100000.jpg", b"\xff\xd8 first")
    chosen = _named_cover(folder, "cover-20261005-090000.jpg", b"\xff\xd8 chosen", prompt=COVER_PROMPT.replace("apple", "fig"))
    assert tb.main(["post", "samhain-tarot-spread", "--cover", chosen.name]) == tb.EXIT_OK
    captured = capsys.readouterr()
    assert "no --cover given" not in captured.err and f"cover: {chosen}" in captured.out


def test_an_old_work_folder_falls_back_on_cover_jpg_with_a_warning(blog, capsys):
    folder = make_article()
    cover = _generated_cover(folder)                    # recorded without article and role, as before 5/10/2026
    assert tb.main(["post", "samhain-tarot-spread"]) == tb.EXIT_OK
    err = capsys.readouterr().err
    assert f"warning: no --cover given: using {cover}" in err and "names of their own" in err


# ---- the subject, the skeleton and the section ----------------------------------------------------------------------


def test_the_skeleton_has_an_empty_subject_and_empty_means_the_server_decides():
    data = tb.skeleton("x")
    assert data["subject"] == {"type": "", "ref": ""} and data["section"] == ""
    data.pop("body_file")
    payload = tb.normalize({**data, "title": "T", "body": "B"})
    assert "subject" not in payload                     # not sent: the server works it out


@pytest.mark.parametrize("subject, sent", [
    ({"type": "card", "ref": "maj-16"}, {"subject": {"tipo": "carta", "ref": "maj-16"}}),
    ({"type": "Spread", "ref": "croce-celtica"}, {"subject": {"tipo": "stesa", "ref": "croce-celtica"}}),
    ({"tipo": "carta", "ref": "the-tower"}, {"subject": {"tipo": "carta", "ref": "the-tower"}}),
    ({"type": "", "ref": ""}, {}), ({}, {}), ("", {}),
    (None, {"subject": None}),                          # null: «about no card or spread», said explicitly
])
def test_the_subject_becomes_the_api_subject(subject, sent):
    payload = tb.normalize({"title": "T", "subject": subject})
    assert {k: v for k, v in payload.items() if k == "subject"} == sent


@pytest.mark.parametrize("subject", [{"type": "card"}, {"type": "deck", "ref": "x"}, {"ref": "maj-16"}, "maj-16",
                                     {"type": "card", "ref": "maj-16", "extra": 1}])
def test_a_half_filled_subject_is_an_error(subject):
    with pytest.raises(tb.Failure) as err:
        tb.normalize({"title": "T", "subject": subject})
    assert err.value.code == tb.EXIT_USAGE and "subject" in str(err.value)


@pytest.mark.parametrize("fields, level, words", [
    ({"subject": {"type": "card", "ref": "maj-16"}, "section": "love"}, "WARN",
     'the subject is the Tower, but "section" is «love»: an article about a card goes in that card\'s section. '
     'Set "section": "major-arcana"'),
    ({"subject": {"type": "card", "ref": "coppe-01"}, "section": "major-arcana"}, "WARN", 'Set "section": "cups"'),
    ({"subject": {"type": "card", "ref": "maj-16"}}, "note", "the server puts the article in «major-arcana»"),
    ({"title": "The Hermit in the Thoth deck", "section": "love"}, "WARN",
     'no "subject" is set, and the title or the focus keyword names the Hermit, but "section" is «love»'),
    ({"subject": {"type": "card", "ref": "maj-99"}}, "WARN", "is not a card the script knows"),
])
def test_check_warns_when_subject_and_section_do_not_match(blog, capsys, fields, level, words):
    make_article(**fields)
    assert tb.main(["check", "samhain-tarot-spread"]) == tb.EXIT_OK          # a warning, not a refusal
    out = capsys.readouterr().out
    assert f"  {level} [subject] " in out and words in out


@pytest.mark.parametrize("fields", [
    {"subject": {"type": "card", "ref": "maj-16"}, "section": "major-arcana"},
    {"subject": {"type": "card", "ref": "dischi-principessa"}, "section": "disks"},
    {},                                                                       # about no card: nothing to say
    {"title": "The Hermit in love readings", "section": "love", "subject": None},   # null: no subject, said so
])
def test_check_says_nothing_when_they_match(blog, capsys, fields):
    make_article(**fields)
    assert tb.main(["check", "samhain-tarot-spread"]) == tb.EXIT_OK
    assert "[subject]" not in capsys.readouterr().out


def test_a_spread_subject_needs_a_section_of_spreads(blog, monkeypatch, capsys):
    sections = [{"slug": "tarot-spreads", "tipo": "stese", "percorso": "Tarot › Spreads"},
                {"slug": "love", "tipo": "articoli", "percorso": "Articles › Love"}]
    real = blog.__call__

    def with_sections(method, path, body=None, query=None, **kw):
        if path == "/sections":
            return sections
        return real(method, path, body=body, query=query, **kw)
    monkeypatch.setattr(tb, "call", with_sections)
    make_article(subject={"type": "spread", "ref": "croce-celtica"}, section="love")
    assert tb.main(["check", "samhain-tarot-spread"]) == tb.EXIT_OK
    assert "WARN [subject] the subject is the spread «croce-celtica»" in capsys.readouterr().out
    make_article(subject={"type": "spread", "ref": "croce-celtica"}, section="tarot-spreads")
    assert tb.main(["check", "samhain-tarot-spread"]) == tb.EXIT_OK
    assert "[subject]" not in capsys.readouterr().out
    assert tb.main(["--json", "check", "samhain-tarot-spread"]) == tb.EXIT_OK
    assert json.loads(capsys.readouterr().out)["subject"] == []


# ---- NEXT: what to do, with the real values --------------------------------------------------------------------------


LONG_TITLE = "Autumn Equinox Tarot Meditation: Finding Balance in the Turning of the Wheel"


def test_next_turns_every_warning_into_one_precise_instruction(blog, capsys):
    long_sentence = " ".join(["word"] * 40) + "."
    make_article(seo_title=LONG_TITLE, seo_description="A short description of the spread, ninety-five characters long or so.",
                 cover_alt="A lantern", body=BODY + "\n" + long_sentence + "\n")
    blog.seo = report(
        72,
        item("titolo_seo", peso=2, caratteri=len(LONG_TITLE)),
        item("descrizione_seo", peso=2, caratteri=68),
        item("chiave_nell_inizio", peso=2),
        item("chiave_in_un_h2"),
        item("collegamenti_interni", peso=2, interni=0),
        item("collegamenti_esterni", esterni=0),
        item("frasi", parole_per_frase=31.0),
        item("faq", faq=1),
        item("chiave_nell_alt"),
        item("immagine"),
        item("a_new_check_from_a_newer_server", messaggio="Something new to improve."),
        collegamenti_interni=0, collegamenti_esterni=0,
    )
    assert tb.main(["check", "samhain-tarot-spread"]) == tb.EXIT_SCORE
    out = capsys.readouterr().out
    assert "NEXT — fix only these, do not rewrite the rest (round 1 of 4):" in out
    assert f'seo_title is {len(LONG_TITLE)} chars: cut it to ≤ 60, keyword first: current = "{LONG_TITLE}"' in out
    assert "seo_description is 68 chars: lengthen it to 120-160 (add 52+" in out
    assert ('the keyword "samhain tarot spread" is not in the first 100 words: edit ONLY the first paragraph and put '
            "the exact phrase in it") in out
    assert 'keyword not in an H2: rename ONE existing `##` heading to contain "samhain tarot spread"' in out
    assert '(headings now: "How the samhain tarot spread works" | "The positions")' in out
    assert "no internal links: run `tarots_blog.py catalog --grep <word>`" in out and "put 2 of the printed shortcuts" in out
    assert "no external link: add one reputable source, e.g. a museum, library or agency page you actually opened" in out
    assert "split ONLY these long ones in two" in out and "(40 words)" in out
    assert "there are 1 FAQ items: add 2 real questions" in out
    assert 'cover_alt is empty or too short' not in out                       # "A lantern" is 9 characters
    assert "[a_new_check_from_a_newer_server] Something new to improve. Change only what this line names" in out
    # not actions now: the cover comes with `post`, the alt only if the picture shows the keyword
    later = out.split("No action needed now:")[1]
    assert "no cover yet" in later and "cover_alt does not contain" in later
    assert "Then run `tarots_blog.py check samhain-tarot-spread` again." in out


@pytest.mark.parametrize("check, expected", [
    (item("titolo_seo", caratteri=22), "seo_title is 22 chars: lengthen it to 30-60"),
    (item("descrizione_seo", caratteri=190), "seo_description is 190 chars: cut it to ≤ 160 (remove 30+)"),
    (item("descrizione_seo", "errore", caratteri=0), "there is no seo_description: write one of 120-160 chars"),
    (item("parola_chiave", "errore", 3), "there is no focus_keyword"),
    (item("chiave_nel_titolo", peso=3), 'the keyword "samhain tarot spread" is not in seo_title: rewrite ONLY seo_title'),
    (item("chiave_nella_descrizione", peso=2), 'is not in seo_description: put the exact phrase in it once'),
    (item("chiave_nello_slug"), 'set "slug" to "samhain-tarot-spread"'),
    (item("densita", per_mille=0), 'the keyword "samhain tarot spread" never appears in the body'),
    (item("densita", per_mille=45.0), "appears 2 times (45.0‰ of the words, limit 30‰)"),
    (item("lunghezza", peso=3, parole=520), "the body has 520 words: add about 280 words as ONE new `##` section"),
    (item("titoli_h2", h2=1), "the body has 1 `##` heading(s): add `##` headings above existing paragraphs"),
    (item("etichette", etichette=0), "there are 0 tags: run `tarots_blog.py tags` and reuse 2-4 existing ones"),
    (item("slug", caratteri=90), "shorten it to ≤ 9 words and ≤ 75 chars"),
    (item("immagine"), "no cover yet"),
])
def test_next_for_each_main_id(check, expected):
    payload = tb.normalize({"title": "A Samhain Tarot Spread", "body": BODY, "focus_keyword": "samhain tarot spread",
                            "seo_title": "Samhain", "slug": "samhain", "cover_alt": "Lanterns in an orchard at night"})
    steps = tb.next_steps(report(70, check), payload)
    assert len(steps) == 1 and expected in steps[0][1], steps


def test_an_empty_alt_is_an_action(blog):
    steps = tb.next_steps(report(70, item("immagine")), {"titolo": "T", "testo": "x", "immagine_alt": ""})
    assert steps == [(True, 'cover_alt is empty or too short: write what the cover shows (8-125 chars) in "cover_alt"')]


def test_post_below_the_score_prints_next_and_saves_nothing(blog, capsys):
    make_article()
    blog.seo = report(70, item("collegamenti_esterni", esterni=0))
    assert tb.main(["post", "samhain-tarot-spread", "--no-cover"]) == tb.EXIT_SCORE
    captured = capsys.readouterr()
    assert "no external link" in captured.out and "Not saved" in captured.err
    assert ("POST", "/posts") in blog.calls and blog.paths().count("/posts") == 1   # the dry run only


def test_a_fix_left_is_not_a_pass_even_above_the_score(blog, capsys):
    make_article()
    blog.seo = report(88, item("descrizione_seo", "errore", 2, caratteri=0))
    assert tb.main(["check", "samhain-tarot-spread"]) == tb.EXIT_SCORE
    assert tb.main(["post", "samhain-tarot-spread", "--no-cover"]) == tb.EXIT_SCORE
    blog.seo = report(88, item("collegamenti_esterni", esterni=0))
    assert tb.main(["check", "samhain-tarot-spread"]) == tb.EXIT_OK
    assert "PASS (round 2)" in capsys.readouterr().out


# ---- the focus keyword ------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("keyword, problem", [
    ("best autumn equinox balance tarot meditation ritual", "it is 7 words"),
    ("tarot spread for tarot beginners", 'it repeats the word "tarot"'),
    ("tarot card cards meaning", 'it repeats the word "cards"'),
])
def test_a_keyword_that_is_not_a_search_phrase_is_refused_before_the_api(blog, capsys, keyword, problem):
    make_article(keyword=keyword)
    for command in ("check", "post"):
        assert tb.main([command, "samhain-tarot-spread"]) == tb.EXIT_KEYWORD
        err = capsys.readouterr().err
        assert problem in err and "2-5 words" in err and "balance tarot meditation autumn" in err
    assert blog.calls == []


@pytest.mark.parametrize("keyword", ["samhain tarot spread", "the queen of the cups", "how to read tarot at samhain"])
def test_natural_phrases_pass(keyword):
    assert tb.keyword_problem(keyword) is None


def test_a_keyword_taken_by_another_article_is_refused(blog, capsys):
    make_article(keyword="full moon tarot spread")
    for command in ("check", "post"):
        assert tb.main([command, "samhain-tarot-spread"]) == tb.EXIT_TAKEN
        err = capsys.readouterr().err
        assert "is TAKEN (same slug)" in err and "full-moon-tarot-spread" in err
    assert "/seo-check" not in blog.paths() and "/posts" not in blog.paths()
    # its own draft (same slug) does not count: `check` after `post` must still work
    blog.titles.append(row(3, "samhain-tarot-spread", "A Samhain Tarot Spread", "samhain tarot spread"))
    make_article(keyword="samhain tarot spread")
    assert tb.main(["check", "samhain-tarot-spread"]) == tb.EXIT_OK
    # an article in another language does not count either
    blog.titles.append(row(4, "stesa-di-samhain", "Stesa di Samhain", "samhain tarot reading", lang="it"))
    make_article(keyword="samhain tarot reading")
    assert tb.main(["check", "samhain-tarot-spread"]) == tb.EXIT_OK


# ---- rounds and STOP ----------------------------------------------------------------------------------------------------


def test_four_rounds_then_stop_and_the_article_stays_stopped(blog, capsys):
    folder = make_article()
    blog.seo = report(72, item("collegamenti_esterni", esterni=0))
    for n in range(1, 5):
        assert tb.main(["check", "samhain-tarot-spread"]) == tb.EXIT_SCORE
        out = capsys.readouterr().out
        assert f"(round {n} of 4)" in out and "STOP" not in out
        assert ("This was the last round" in out) == (n == 4)
    assert tb.main(["check", "samhain-tarot-spread"]) == tb.EXIT_STOP
    out = capsys.readouterr().out
    assert "STOP: 5 rounds of `check` and the score is still 72 (below 85)" in out
    assert "no `post`, no `--save-anyway`" in out and str(folder) in out and "NEXT" not in out
    rounds = json.loads((folder / ".checks").read_text(encoding="utf-8"))
    assert rounds["stopped"] is True and [r["score"] for r in rounds["rounds"]] == [72] * 5
    # from now on: no call to the API, not even with a better text or --save-anyway
    blog.calls.clear()
    blog.seo = report(95)
    assert tb.main(["check", "samhain-tarot-spread"]) == tb.EXIT_STOP
    assert tb.main(["post", "samhain-tarot-spread", "--save-anyway"]) == tb.EXIT_STOP
    assert blog.calls == [] and "STOP" in capsys.readouterr().out
    # the operator reopens it by deleting the file
    (folder / ".checks").unlink()
    assert tb.main(["check", "samhain-tarot-spread"]) == tb.EXIT_OK


def test_a_pass_on_the_fifth_round_is_not_a_stop(blog, capsys):
    make_article()
    blog.seo = report(80, item("faq", faq=1))
    for _ in range(4):
        assert tb.main(["check", "samhain-tarot-spread"]) == tb.EXIT_SCORE
    blog.seo = report(90)
    assert tb.main(["check", "samhain-tarot-spread"]) == tb.EXIT_OK
    assert "PASS (round 5)" in capsys.readouterr().out
    assert tb.main(["post", "samhain-tarot-spread", "--no-cover"]) == tb.EXIT_OK


def test_check_json_carries_round_next_and_stop(blog, capsys):
    make_article(cover_alt="Lanterns in an orchard at night")
    capsys.readouterr()
    blog.seo = report(70, item("collegamenti_esterni", esterni=0), item("immagine"))
    assert tb.main(["--json", "check", "samhain-tarot-spread"]) == tb.EXIT_SCORE
    data = json.loads(capsys.readouterr().out)
    assert data["round"] == 1 and data["max_rounds"] == 4 and data["stop"] is False and data["pass"] is False
    assert data["next"] and data["next"][0].startswith("no external link") and data["no_action"][0].startswith("no cover yet")
