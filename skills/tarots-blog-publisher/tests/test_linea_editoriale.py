"""The editorial line, offline: titles that are titles, the section, --no-cover only after a failed generation,
drafts unless --publish, the RESULT line and `run-report`, the plan (series of 3-10 and single articles, the daily
session, failed parts retried and never skipped, requests at once) and the record of ideas and research.

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
        self.fail_post = False
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
            if self.fail_post:
                raise tb.Failure("API 500: the server could not save the article", tb.EXIT_API)
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


# ---- the plan: series and single articles -------------------------------------------------------------------------


def series(title, n=3, section="kabbalah"):
    words = ["Three Mothers and the Breath Between Them", "The Seven Doubles and the Planets of the Trumps",
             "Twelve Simple Letters and the Zodiac", "Why Tzaddi Is Not the Star",
             "The Cube of Space and the Order of the Trumps", "From Kircher to the Golden Dawn",
             "Thirty-Two Paths and Twenty-Two Doors", "What the Book of Formation Does Not Say",
             "Lévi and the Letters of the Trumps", "The Gra and the Order of the Doubles",
             "A Note on the Mother Letters in Saadia"]
    return {"kind": "series", "title": title, "thesis": "The attributions are a reading of a late antique text.",
            "why": "Experts know the attributions, not their sources.", "section": section,
            "sources": ["Kaplan 1990", "Hayman 2004"],
            "parts": [{"title": f"{w} ({title.split(':')[0]})", "question": f"What does {w.lower()} change?",
                       "sources": ["Sefer Yetzirah"], "keyword": "sefer yetzirah tarot"} for w in words[:n]]}


def single(title, section="thoth-tarot"):
    return {"kind": "single", "title": title, "question": "What did the painter change between the drafts?",
            "why": "The letters of Harris are rarely read.", "section": section,
            "sources": ["Kaczynski, Perdurabo 2010", "Harris letters, Warburg Institute"]}


def plan_file(tmp_path, *items, name="plan.json"):
    file = tmp_path / name
    file.write_text(json.dumps({"items": list(items)}), encoding="utf-8")
    return file


def plan():
    return json.loads(tb.EDITORIAL_PATH.read_text(encoding="utf-8"))


def test_the_plan_queues_series_and_single_articles(blog, tmp_path, capsys):
    f = plan_file(tmp_path, series("The Letters Before the Cards: Sefer Yetzirah"),
                  single("What Frieda Harris Changed in the Last Drafts"))
    assert tb.main(["plan", "add", str(f)]) == tb.EXIT_OK
    items = plan()["items"]
    assert [i["kind"] for i in items] == ["series", "single"] and {i["status"] for i in items} == {"queued"}
    assert len(items[0]["parts"]) == 3 and items[0]["tag"].startswith("series-") and items[1]["tag"] == ""
    assert "2 item(s), 4 article(s) added" in capsys.readouterr().out


def test_bad_entries_are_refused_and_the_good_ones_kept(blog, tmp_path, capsys):
    f = plan_file(tmp_path, single("A Full Moon Tarot Spread for Release"),
                  series("Short Series: Two Parts Only", n=2), series("Too Long: Eleven Parts", n=11),
                  series("Decans and Faces: The Minor Arcana as a Calendar", n=10))
    assert tb.main(["plan", "add", str(f)]) == tb.EXIT_OK
    out = capsys.readouterr().out
    assert "a moon-phase or transit reading" in out and "2 parts: a series has 3-10" in out
    assert "11 parts: a series has 3-10" in out
    data = plan()
    assert [i["title"] for i in data["items"]] == ["Decans and Faces: The Minor Arcana as a Calendar"]
    assert sum(1 for i in data["ideas"] if i["status"] == "rejected") == 3


def test_a_part_already_on_the_blog_or_in_the_plan_is_refused(blog, tmp_path, capsys):
    blog.titles.append(row(9, "why-tzaddi-is-not-the-star", "Why Tzaddi Is Not the Star (The Letters)"))
    f = plan_file(tmp_path, series("The Letters: Sefer Yetzirah and the Trumps", n=4))
    assert tb.main(["plan", "add", str(f)]) == tb.EXIT_RULE
    assert "is TAKEN by" in capsys.readouterr().out


def test_a_session_opens_items_in_order_without_splitting_a_series(blog, tmp_path, capsys):
    f = plan_file(tmp_path, single("What Frieda Harris Changed in the Last Drafts"),
                  series("The Letters Before the Cards: Sefer Yetzirah", n=3),
                  single("Why Crowley Renamed Strength as Lust"),
                  series("Decans and Faces: The Minor Arcana as a Calendar", n=4))
    assert tb.main(["plan", "add", str(f)]) == tb.EXIT_OK
    assert tb.main(["plan", "session"]) == tb.EXIT_OK
    status = [i["status"] for i in plan()["items"]]
    assert status == ["open", "open", "open", "queued"]               # 1 + 3 + 1 = 5 articles
    capsys.readouterr()
    assert tb.main(["plan", "session"]) == tb.EXIT_OK                  # 5 left already: nothing more opens
    assert [i["status"] for i in plan()["items"]][-1] == "queued"


def test_a_long_series_is_never_split(blog, tmp_path):
    f = plan_file(tmp_path, series("Decans and Faces: The Minor Arcana as a Calendar", n=8),
                  single("What Frieda Harris Changed in the Last Drafts"))
    assert tb.main(["plan", "add", str(f)]) == tb.EXIT_OK
    assert tb.main(["plan", "session"]) == tb.EXIT_OK
    items = plan()["items"]
    assert items[0]["status"] == "open" and items[1]["status"] == "queued"   # 8 ≥ 5: the series alone


def test_an_empty_plan_asks_for_a_new_one(blog, capsys):
    assert tb.main(["plan", "session"]) == tb.EXIT_PLAN_EMPTY
    assert "PLAN EMPTY" in capsys.readouterr().out


def write_part(blog, item_id, part, slug, body=BODY):
    """`plan next` → `new --series` → write → cover → post, as the daily job does."""
    folder_name = slug
    assert tb.main(["new", folder_name, "--series", item_id, "--part", str(part)]) == tb.EXIT_OK
    folder = tb.work_root() / f"{TODAY}-{folder_name}"
    art = json.loads((folder / "article.json").read_text(encoding="utf-8"))
    art.update(focus_keyword="sefer yetzirah tarot",
               seo_title=f"Sefer Yetzirah Tarot: Part {part} of the Letters")
    (folder / "article.json").write_text(json.dumps(art), encoding="utf-8")
    (folder / "article.md").write_text(body, encoding="utf-8")
    generated_cover(folder, art["slug"])
    return tb.main(["post", folder_name, "--publish"])


def test_a_series_is_written_in_order_and_closed(blog, tmp_path, capsys):
    assert tb.main(["plan", "add", str(plan_file(tmp_path, series("The Letters Before the Cards: Sefer Yetzirah")))]) == tb.EXIT_OK
    assert tb.main(["plan", "session"]) == tb.EXIT_OK
    iid = plan()["items"][0]["id"]
    capsys.readouterr()
    assert tb.main(["plan", "next"]) == tb.EXIT_OK
    out = capsys.readouterr().out
    assert "part 1 of 3" in out and f"--series {iid} --part 1" in out
    assert write_part(blog, iid, 1, "p1") == tb.EXIT_OK
    first = plan()["items"][0]["parts"][0]
    assert first["status"] == "written" and blog.saved[-1]["stato"] == "pubblicato"
    assert blog.saved[-1]["slug"] == first["slug"] and "series" not in blog.saved[-1]
    # part 2 must link part 1
    assert write_part(blog, iid, 2, "p2") == tb.EXIT_RULE
    assert f"[[post:{first['slug']}]]" in capsys.readouterr().err
    link = BODY + f"\nAs the first part showed ([[post:{first['slug']}]]), air mediates.\n"
    assert write_part(blog, iid, 2, "p2b", body=link) == tb.EXIT_OK
    second = plan()["items"][0]["parts"][1]["slug"]
    assert write_part(blog, iid, 3, "p3", body=BODY + f"\nAfter [[post:{second}]], the zodiac.\n") == tb.EXIT_OK
    assert plan()["items"][0]["status"] == "closed"
    capsys.readouterr()
    assert tb.main(["plan", "next"]) == tb.EXIT_OK
    assert "every open item is written" in capsys.readouterr().out


def test_a_failed_part_is_recorded_retried_and_never_skipped(blog, tmp_path, capsys):
    f = plan_file(tmp_path, series("The Letters Before the Cards: Sefer Yetzirah"),
                  single("What Frieda Harris Changed in the Last Drafts"))
    assert tb.main(["plan", "add", str(f)]) == tb.EXIT_OK
    assert tb.main(["plan", "session"]) == tb.EXIT_OK
    iid = plan()["items"][0]["id"]
    blog.fail_post = True                                              # the API refuses the save
    assert write_part(blog, iid, 1, "p1") == tb.EXIT_API
    part = plan()["items"][0]["parts"][0]
    assert part["status"] == "failed" and len(part["attempts"]) == 1
    capsys.readouterr()
    assert tb.main(["plan", "next"]) == tb.EXIT_OK
    out = capsys.readouterr().out
    assert "part 1 of 3" in out and "RETRY: 1 failed attempt(s)" in out and "-retry2" in out
    for k in (2, 3):
        assert write_part(blog, iid, 1, f"p1-retry{k}") == tb.EXIT_API
    capsys.readouterr()
    assert tb.main(["plan", "next"]) == tb.EXIT_OK                     # three today: on to the next item
    assert "single article: What Frieda Harris Changed" in capsys.readouterr().out
    alarms = tb.plan_alarms()
    assert alarms and alarms[0].startswith("STUCK [series] The Letters Before the Cards") and "failed 3 times" in alarms[0]
    blog.fail_post = False
    assert tb.main(["run-report"]) == tb.EXIT_OK
    assert "STUCK [series]" in capsys.readouterr().out


def test_an_item_left_incomplete_yesterday_comes_first(blog, tmp_path, capsys):
    f = plan_file(tmp_path, series("The Letters Before the Cards: Sefer Yetzirah"),
                  single("What Frieda Harris Changed in the Last Drafts"),
                  single("Why Crowley Renamed Strength as Lust"))
    assert tb.main(["plan", "add", str(f)]) == tb.EXIT_OK
    data = plan()
    data["items"][0].update(status="open", opened="2026-01-01T20:00:00+00:00")
    data["items"][0]["parts"][0]["status"] = "written"
    tb.EDITORIAL_PATH.write_text(json.dumps(data), encoding="utf-8")
    capsys.readouterr()
    assert tb.main(["plan", "session"]) == tb.EXIT_OK
    out = capsys.readouterr().out
    assert "FIRST, finish what an earlier session left incomplete" in out and "INCOMPLETE since 2026-01-01" in out
    assert [i["status"] for i in plan()["items"]] == ["open", "open", "open"]   # 2 left + 1 + 1 = 4 < 5
    assert tb.main(["plan", "next"]) == tb.EXIT_OK
    assert "part 2 of 3" in capsys.readouterr().out


def test_a_request_opens_at_once_ahead_of_the_plan(blog, tmp_path, capsys):
    assert tb.main(["plan", "add", str(plan_file(tmp_path, single("What Frieda Harris Changed in the Last Drafts")))]) == tb.EXIT_OK
    assert tb.main(["plan", "session"]) == tb.EXIT_OK
    asked = plan_file(tmp_path, single("Why Crowley Renamed Strength as Lust"), name="asked.json")
    assert tb.main(["plan", "add", str(asked), "--now"]) == tb.EXIT_OK
    capsys.readouterr()
    assert tb.main(["plan", "next"]) == tb.EXIT_OK
    assert "Why Crowley Renamed Strength as Lust" in capsys.readouterr().out


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


def test_status_lists_the_plan_and_rejected_ideas(blog, tmp_path, capsys):
    assert tb.main(["ideas", "reject", "Tarot", "and", "Self-Care", "--why", "lifestyle"]) == tb.EXIT_OK
    capsys.readouterr()
    assert tb.main(["plan"]) == tb.EXIT_OK
    out = capsys.readouterr().out
    assert "queued: 0 item(s), 0 article(s)" in out and "Tarot and Self-Care" in out


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
