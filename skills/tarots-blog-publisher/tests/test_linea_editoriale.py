"""The editorial line, offline: titles that are titles, the section, --no-cover only after a failed generation,
drafts unless --publish, the RESULT line and `run-report`, the series (plan, next, new --series, post) and the record
of ideas and research.

    backend/.venv/Scripts/python.exe -m pytest skills/tarots-blog-publisher/tests -q -p no:cacheprovider

Each test fixes what a small local model did on the night of 7/10/2026: «Scorpio Kabalah Correspondences Tarot
Spread» as a title, no section, --no-cover «since we can't generate the cover» without ever generating it, five
articles reported as posted when two were, and topics «da riviste femminili».
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


tb = _load("tarots_blog_linea", SKILLS / "tarots-blog-publisher" / "scripts" / "tarots_blog.py")
ti = _load("tarots_images_linea", SKILLS / "tarots-blog-images" / "scripts" / "tarots_images.py")

TODAY = datetime.date.today().isoformat()
NOW = datetime.datetime.now(datetime.timezone.utc)


def report(score=90):
    return {"punteggio": score, "giudizio": "ottimo", "controlli": [],
            "statistiche": {"parole": 1800, "titoli_h2": 4, "collegamenti_interni": 2, "collegamenti_esterni": 2}}


def row(n, slug, title, *, mine=False, section="kabbalah", when=None):
    when = when or NOW.isoformat()
    return {"id": f"id-{n}", "slug": slug, "titolo": title, "estratto": "", "parola_chiave": "", "sezione": section,
            "lang": "en", "stato": "bozza", "pubblicato_il": None, "aggiornato": when, "mio": mine,
            "tradotto_da_id": None}


class FakeBlog:
    def __init__(self):
        self.calls = []
        self.saved = []
        self.titles = [row(1, "the-tower-thoth", "The Tower in the Thoth Tarot")]

    def __call__(self, method, path, body=None, query=None, **kwargs):
        self.calls.append((method, path, body))
        if path == "/seo-check":
            return report()
        if path == "/titles":
            return {"totale": len(self.titles), "pagina": 1, "per_pagina": 1000, "adesso": NOW.isoformat(),
                    "articoli": self.titles}
        if path == "/media":
            return {"id": "img-1", "url": "/blog/media/img-1.webp"}
        if path == "/posts" and (body or {}).get("dry_run"):
            return {"seo": report()}
        if path == "/posts":
            self.saved.append(body)
            return {"articolo": {"id": f"post-{len(self.saved)}", "slug": body.get("slug"), "stato": body.get("stato", "bozza"),
                                 "lang": "en"}, "url": f"https://tarots.chat/blog/{body.get('slug')}", "avvisi": []}
        if path.startswith("/posts/"):
            return {"articolo": {"id": path.rsplit("/", 1)[1], "immagine_id": "img-1" if path.endswith("id-2") else None}}
        raise AssertionError(f"unexpected call {method} {path}")


@pytest.fixture
def blog(tmp_path, monkeypatch):
    fake = FakeBlog()
    monkeypatch.setattr(tb, "call", fake)
    monkeypatch.setattr(tb, "_identity", lambda: "https://tarots.test/api|tk_live_abcd")
    monkeypatch.setattr(tb, "TITLES_CACHE_PATH", tmp_path / "titles-cache.json")
    monkeypatch.setattr(tb, "PROGRESS_PATH", tmp_path / "images-progress.json")
    monkeypatch.setattr(tb, "EDITORIAL_PATH", tmp_path / "editorial.json")
    monkeypatch.setenv("TAROTS_WORK_DIR", str(tmp_path / "work"))
    return fake


BODY = ("The Sefer Yetzirah tarot question begins with three mother letters and the air between them.\n\n"
        "## Why three mothers\n\nText.\n\n## The letters and the trumps\n\nText.\n")


def make_article(slug="three-mothers", *, body=BODY, **fields):
    assert tb.main(["new", slug]) == tb.EXIT_OK
    folder = tb.work_root() / f"{TODAY}-{slug}"
    data = {**tb.skeleton(slug), "title": "Three Mothers and the Breath Between Them",
            "focus_keyword": "sefer yetzirah tarot", "seo_title": "Sefer Yetzirah Tarot: The Three Mother Letters",
            "section": "kabbalah", **fields}
    (folder / "article.json").write_text(json.dumps(data), encoding="utf-8")
    (folder / "article.md").write_text(body, encoding="utf-8")
    return folder


def generated_cover(folder, slug="three-mothers"):
    cover = folder / "foto" / "cover-20261007-200000.jpg"
    cover.write_bytes(b"\xff\xd8 a quiet garden " + slug.encode())
    data = json.loads(tb.PROGRESS_PATH.read_text(encoding="utf-8")) if tb.PROGRESS_PATH.exists() else {}
    data.setdefault("_generated", []).append({"prompt": "A walled garden at dawn, mist over a fountain, no text",
                                              "file": str(cover), "sha256": tb.sha256_of(cover), "role": "cover",
                                              "article": slug, "when": NOW.isoformat()})
    tb.PROGRESS_PATH.write_text(json.dumps(data), encoding="utf-8")
    return cover


# ---- titles --------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("title, keyword", [
    ("Scorpio Kabalah Correspondences Tarot Spread", "scorpio kabalah correspondences tarot spread"),
    ("Libra Season Autumn Equinox Tarot Spread", "libra season tarot spread"),
    ("Libra Season Balance Tarot Meditation Guide", "libra season balance tarot"),
    ("Sefer Yetzirah Tarot Guide", "sefer yetzirah tarot"),                # the keyword plus filler
])
def test_keyword_strings_are_not_titles(title, keyword):
    assert tb.title_problem(title, keyword)


@pytest.mark.parametrize("title", [
    "Why the Golden Dawn Swapped Strength and Justice",
    "The Thirty-Two Paths Before the Tarot",
    "Teth and the Serpent: Reading Lust Through the Sefer Yetzirah",
    "Sefer Yetzirah Tarot",                                                  # three words: a name, allowed
    "Tarot and String Theory",
    "Atziluth: The World of Emanation in the Thoth Deck",
])
def test_real_titles_pass(title):
    assert tb.title_problem(title, "sefer yetzirah tarot") is None


def test_check_refuses_a_keyword_title_before_the_api(blog, capsys):
    make_article(title="Scorpio Kabalah Correspondences Tarot Spread")
    assert tb.main(["check", "three-mothers"]) == tb.EXIT_TITLE
    err = capsys.readouterr().err
    assert "string of keywords" in err and "Golden Dawn Swapped Strength" in err
    assert not any(p == "/seo-check" for _, p, _ in blog.calls)


def test_the_seo_title_must_read_as_a_title_too(blog, capsys):
    make_article(seo_title="Sefer Yetzirah Tarot Mother Letters Guide")
    assert tb.main(["check", "three-mothers"]) == tb.EXIT_TITLE
    assert "seo_title" in capsys.readouterr().err


def test_next_no_longer_asks_for_the_keyword_first():
    steps = tb.next_steps({"controlli": [{"id": "chiave_nel_titolo", "esito": "avviso", "peso": 3}]},
                          {"seo_parola_chiave": "sefer yetzirah tarot", "seo_titolo": "Three Mothers", "testo": "x"})
    text = steps[0][1]
    assert "where it reads naturally" in text and "starts with" not in text


# ---- the section ---------------------------------------------------------------------------------------------------


def test_an_article_without_a_section_is_refused(blog, capsys):
    make_article(section="")
    assert tb.main(["check", "three-mothers"]) == tb.EXIT_SECTION
    assert "`tarots_blog.py sections`" in capsys.readouterr().err


def test_an_article_about_a_card_may_leave_the_section_to_the_server(blog):
    make_article(section="", subject={"type": "card", "ref": "maj-16"})
    assert tb.main(["check", "three-mothers"]) == tb.EXIT_OK


# ---- --no-cover, --publish, RESULT ---------------------------------------------------------------------------------


def test_no_cover_is_refused_when_generate_never_ran(blog, capsys):
    make_article()
    assert tb.main(["post", "three-mothers", "--no-cover"]) == tb.EXIT_NO_COVER
    assert "no failed generation of the cover is recorded" in capsys.readouterr().err and not blog.saved


def test_no_cover_is_accepted_after_a_failed_generation(blog, capsys):
    make_article()
    tb.PROGRESS_PATH.write_text(json.dumps({"_failed": [{"role": "cover", "article": "three-mothers",
                                                          "reason": "no credits", "when": NOW.isoformat()}]}),
                                encoding="utf-8")
    assert tb.main(["post", "three-mothers", "--no-cover"]) == tb.EXIT_OK
    assert "RESULT saved three-mothers | status=bozza | section=kabbalah | cover=NO" in capsys.readouterr().out


def test_a_failure_before_the_last_cover_does_not_count(blog):
    folder = make_article()
    tb.PROGRESS_PATH.write_text(json.dumps({"_failed": [{"role": "cover", "article": "three-mothers",
                                                          "reason": "timeout", "when": "2026-01-01T00:00:00+00:00"}]}),
                                encoding="utf-8")
    generated_cover(folder)
    assert tb.failed_cover_attempts(folder / "article.json", "three-mothers") == []


def test_published_is_kept_only_with_publish(blog, capsys):
    folder = make_article(status="published")
    generated_cover(folder)
    assert tb.main(["post", "three-mothers"]) == tb.EXIT_OK
    assert blog.saved[-1]["stato"] == "bozza" and "needs --publish" in capsys.readouterr().err
    folder = make_article("three-mothers-two", status="published")
    generated_cover(folder, "three-mothers-two")
    assert tb.main(["post", "three-mothers-two", "--publish"]) == tb.EXIT_OK
    assert blog.saved[-1]["stato"] == "pubblicato"


def test_post_ends_with_the_result_line(blog, capsys):
    folder = make_article()
    generated_cover(folder)
    assert tb.main(["post", "three-mothers"]) == tb.EXIT_OK
    assert "RESULT saved three-mothers | status=bozza | section=kabbalah | cover=yes | id=post-1" in capsys.readouterr().out


def test_run_report_reads_back_what_this_key_saved(blog, capsys):
    old = (NOW - datetime.timedelta(days=3)).isoformat()
    blog.titles = [row(1, "old-one", "An Older Essay", mine=True, when=old),
                   row(2, "with-cover", "The Letter Teth", mine=True),
                   row(3, "no-section", "Another Essay", mine=True, section=None),
                   row(4, "someone-else", "Not Mine")]
    assert tb.main(["run-report", "--hours", "12"]) == tb.EXIT_OK
    out = capsys.readouterr().out
    assert "SAVED with-cover | The Letter Teth | status=bozza | section=kabbalah | cover=yes" in out
    assert "SAVED no-section | Another Essay | status=bozza | section=NONE | cover=NO" in out
    assert "old-one" not in out and "someone-else" not in out


# ---- the series ----------------------------------------------------------------------------------------------------


def plan_file(tmp_path, **changes):
    parts = [{"title": t, "question": f"What does {t.lower()} change for a reader of the Thoth deck?",
              "sources": ["Sefer Yetzirah, Kaplan tr. 1990", "Crowley, The Book of Thoth, 1944"],
              "keyword": "sefer yetzirah tarot"}
             for t in ["Three Mothers and the Breath Between Them", "The Seven Doubles and the Planets of the Trumps",
                       "Twelve Simple Letters and the Zodiac", "Why Tzaddi Is Not the Star",
                       "The Cube of Space and the Order of the Trumps", "From Kircher to the Golden Dawn",
                       "Thirty-Two Paths, Twenty-Two Doors", "What the Sefer Yetzirah Does Not Say"]]
    plan = {"title": "The Letters Before the Cards: The Sefer Yetzirah and the Tarot",
            "thesis": "The letter attributions of the Thoth deck are a reading of a 3rd-6th century text.",
            "why": "Experts know the attributions; few know their sources and their disputes.",
            "section": "kabbalah", "sources": ["Kaplan 1990", "Scholem, Kabbalah, 1974"], "parts": parts}
    plan.update(changes)
    file = tmp_path / "series.json"
    file.write_text(json.dumps(plan), encoding="utf-8")
    return file


def test_a_series_is_recorded_and_its_next_part_briefed(blog, tmp_path, capsys):
    assert tb.main(["series", "plan", str(plan_file(tmp_path))]) == tb.EXIT_OK
    data = json.loads(tb.EDITORIAL_PATH.read_text(encoding="utf-8"))
    series = data["series"][0]
    assert series["status"] == "open" and len(series["parts"]) == 8 and series["tag"].startswith("series-")
    assert data["ideas"][0]["status"] == "used"
    capsys.readouterr()
    assert tb.main(["series", "next"]) == tb.EXIT_OK
    out = capsys.readouterr().out
    assert "part 1 of 8: Three Mothers and the Breath Between Them" in out and f"--series {series['id']} --part 1" in out


@pytest.mark.parametrize("change, words", [
    ({"title": "Libra Season Tarot Spreads"}, "«<sign> season» article"),
    ({"parts": [{"title": "Three Mothers and the Breath", "question": "q", "sources": ["s"]}]}, "a series has 6-12"),
    ({"sources": []}, "at least two real sources"),
    ({"section": ""}, '"section" is empty'),
])
def test_a_poor_series_is_not_recorded(blog, tmp_path, capsys, change, words):
    assert tb.main(["series", "plan", str(plan_file(tmp_path, **change))]) == tb.EXIT_RULE
    assert words in capsys.readouterr().err and not tb.EDITORIAL_PATH.exists()


def test_a_part_already_on_the_blog_is_refused(blog, tmp_path, capsys):
    blog.titles.append(row(9, "why-tzaddi-is-not-the-star", "Why Tzaddi Is Not the Star"))
    assert tb.main(["series", "plan", str(plan_file(tmp_path))]) == tb.EXIT_RULE
    assert "is TAKEN by" in capsys.readouterr().err


def test_only_one_open_series_at_a_time(blog, tmp_path, capsys):
    assert tb.main(["series", "plan", str(plan_file(tmp_path))]) == tb.EXIT_OK
    other = plan_file(tmp_path, title="Decans in the Minor Arcana: Thirty-Six Faces of the Year")
    assert tb.main(["series", "plan", str(other)]) == tb.EXIT_RULE
    assert "is still open" in capsys.readouterr().err


def test_new_with_series_fills_the_article_and_post_marks_the_part(blog, tmp_path, capsys):
    assert tb.main(["series", "plan", str(plan_file(tmp_path))]) == tb.EXIT_OK
    sid = json.loads(tb.EDITORIAL_PATH.read_text(encoding="utf-8"))["series"][0]["id"]
    assert tb.main(["new", "three-mothers", "--series", sid, "--part", "1"]) == tb.EXIT_OK
    folder = tb.work_root() / f"{TODAY}-three-mothers"
    data = json.loads((folder / "article.json").read_text(encoding="utf-8"))
    assert data["title"] == "Three Mothers and the Breath Between Them" and data["section"] == "kabbalah"
    assert data["series"] == {"id": sid, "part": 1} and data["tags"] == [f"series-{sid}"[:60]]
    data.update(focus_keyword="sefer yetzirah tarot", seo_title="Sefer Yetzirah Tarot: The Three Mother Letters")
    (folder / "article.json").write_text(json.dumps(data), encoding="utf-8")
    (folder / "article.md").write_text(BODY, encoding="utf-8")
    generated_cover(folder)
    assert tb.main(["post", "three-mothers"]) == tb.EXIT_OK
    assert "series" not in blog.saved[-1]                                   # never sent to the API
    part = json.loads(tb.EDITORIAL_PATH.read_text(encoding="utf-8"))["series"][0]["parts"][0]
    assert part["status"] == "written" and part["slug"] == "three-mothers" and part["url"].endswith("three-mothers")
    assert "part 1 of «The Letters Before the Cards" in capsys.readouterr().out


def test_the_second_part_must_link_the_first(blog, tmp_path, capsys):
    assert tb.main(["series", "plan", str(plan_file(tmp_path))]) == tb.EXIT_OK
    data = json.loads(tb.EDITORIAL_PATH.read_text(encoding="utf-8"))
    sid = data["series"][0]["id"]
    data["series"][0]["parts"][0].update(status="written", slug="three-mothers")
    tb.EDITORIAL_PATH.write_text(json.dumps(data), encoding="utf-8")
    assert tb.main(["new", "seven-doubles", "--series", sid, "--part", "2"]) == tb.EXIT_OK
    folder = tb.work_root() / f"{TODAY}-seven-doubles"
    art = json.loads((folder / "article.json").read_text(encoding="utf-8"))
    art.update(focus_keyword="sefer yetzirah planets", seo_title="Sefer Yetzirah Planets: The Seven Doubles")
    (folder / "article.json").write_text(json.dumps(art), encoding="utf-8")
    (folder / "article.md").write_text(BODY, encoding="utf-8")
    generated_cover(folder, "seven-doubles")
    assert tb.main(["post", "seven-doubles"]) == tb.EXIT_RULE
    assert "[[post:three-mothers]]" in capsys.readouterr().err and not blog.saved
    (folder / "article.md").write_text(BODY + "\nAs the first part showed ([[post:three-mothers]]), air mediates.\n",
                                       encoding="utf-8")
    assert tb.main(["post", "seven-doubles"]) == tb.EXIT_OK


def test_the_last_part_closes_the_series(blog, tmp_path):
    assert tb.main(["series", "plan", str(plan_file(tmp_path))]) == tb.EXIT_OK
    data = json.loads(tb.EDITORIAL_PATH.read_text(encoding="utf-8"))
    series = data["series"][0]
    for p in series["parts"][:-1]:
        p["status"] = "written"
    tb.EDITORIAL_PATH.write_text(json.dumps(data), encoding="utf-8")
    note = tb.mark_series_part({"id": series["id"], "part": 8}, {"slug": "last", "id": "p8"}, "https://x/last")
    assert "the series is complete" in note
    assert json.loads(tb.EDITORIAL_PATH.read_text(encoding="utf-8"))["series"][0]["status"] == "closed"


# ---- ideas and research --------------------------------------------------------------------------------------------


def test_ideas_keep_what_was_proposed_rejected_and_researched(blog, capsys):
    assert tb.main(["ideas", "add", "Decans", "in", "the", "Minor", "Arcana", "--why", "Picatrix and Agrippa"]) == tb.EXIT_OK
    assert tb.main(["ideas", "add", "A", "Full", "Moon", "Tarot", "Spread"]) == tb.EXIT_OK
    assert tb.main(["ideas", "research", "Kircher Oedipus Aegyptiacus tree", "--why", "1652, 22 paths",
                    "--source", "https://archive.org/details/oedipusaegyptiac"]) == tb.EXIT_OK
    capsys.readouterr()
    assert tb.main(["ideas", "list"]) == tb.EXIT_OK
    out = capsys.readouterr().out
    assert "[proposed] Decans in the Minor Arcana" in out
    assert "[rejected] A Full Moon Tarot Spread — it is a moon-phase or transit reading" in out
    assert "research: Kircher Oedipus Aegyptiacus tree → 1652, 22 paths" in out


def test_status_lists_finished_series_and_rejected_ideas(blog, tmp_path, capsys):
    assert tb.main(["ideas", "reject", "Tarot", "and", "Self-Care", "--why", "lifestyle"]) == tb.EXIT_OK
    capsys.readouterr()
    assert tb.main(["series"]) == tb.EXIT_OK
    out = capsys.readouterr().out
    assert "no open series" in out and "Tarot and Self-Care" in out


# ---- tarots_images: a failed generation is recorded --------------------------------------------------------------


def test_generate_records_a_failure_for_no_cover(tmp_path, monkeypatch):
    monkeypatch.setattr(ti, "PROGRESS_PATH", tmp_path / "images-progress.json")
    monkeypatch.setenv("TAROTS_WORK_DIR", str(tmp_path / "work"))
    monkeypatch.setattr(ti, "balance", lambda: 3)                            # not enough credits
    folder = tmp_path / "work" / f"{TODAY}-three-mothers"
    (folder / "foto").mkdir(parents=True)
    (folder / "article.json").write_text(json.dumps({"slug": "three-mothers"}), encoding="utf-8")
    code = ti.main(["generate", "--article", "three-mothers", "--kind", "landscape", "--shot", "wide",
                    "--light", "blue-hour", "--setting", "walled garden",
                    "--prompt", "A wide view of a walled monastery garden at the blue hour, mist rising over a cracked "
                                "stone fountain, three cypress trees, an open manuscript of Hebrew letters left on a "
                                "bench, lanterns glowing along the cloister arches, no text, no letters"])
    assert code == ti.EXIT_BUDGET
    failed = json.loads((tmp_path / "images-progress.json").read_text(encoding="utf-8"))["_failed"]
    assert failed[0]["article"] == "three-mothers" and failed[0]["role"] == "cover" and "balance" in failed[0]["reason"]
