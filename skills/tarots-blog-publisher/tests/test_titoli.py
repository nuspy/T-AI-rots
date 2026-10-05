"""`titles` and `topic-check` of tarots_blog.py, offline: the API is replaced by a fake that answers `GET /titles`.

    backend/.venv/Scripts/python.exe -m pytest skills/tarots-blog-publisher/tests skills/tarots-blog-images/tests -q -p no:cacheprovider

The fake honours `dal`, `archiviati`, `pagina` and `per_pagina` like the real endpoint, and remembers every query: the
tests check that a second run asks only for what changed, that a deleted article stays in the local copy until a
full reload, and the verdicts FREE / CLOSE / TAKEN.
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


tb = _load("tarots_blog_titles", SKILLS / "tarots-blog-publisher" / "scripts" / "tarots_blog.py")

T0 = "2026-10-05T10:00:00+00:00"


def _t(value: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(value)


def art(n, slug, title, keyword=None, *, lang="en", status="pubblicato", when="2026-10-01T08:00:00+00:00",
        section=None, mine=False):
    return {
        "id": f"00000000-0000-0000-0000-{n:012d}", "slug": slug, "titolo": title, "estratto": f"About {title.lower()}.",
        "parola_chiave": keyword, "sezione": section, "lang": lang, "stato": status,
        "pubblicato_il": when if status == "pubblicato" else None, "aggiornato": when, "mio": mine,
        "tradotto_da_id": None,
    }


class FakeTitles:
    """`GET /titles` over an in-memory blog. `now` is the server clock returned as `adesso`."""

    def __init__(self, rows, now=T0):
        self.rows = {r["id"]: r for r in rows}
        self.now = now
        self.queries = []
        self.down = False

    def __call__(self, method, path, query=None, **kwargs):
        assert (method, path) == ("GET", "/titles"), (method, path)
        if self.down:
            raise tb.Unreachable("Cannot reach the API (test).")
        query = dict(query or {})
        self.queries.append(query)
        rows = sorted(self.rows.values(), key=lambda r: r["aggiornato"], reverse=True)
        if query.get("archiviati") != "true":
            rows = [r for r in rows if r["stato"] != "archiviato"]
        if "dal" in query:
            rows = [r for r in rows if _t(r["aggiornato"]) >= _t(query["dal"])]
        per, page = query["per_pagina"], query["pagina"]
        return {"totale": len(rows), "pagina": page, "per_pagina": per, "adesso": self.now,
                "articoli": rows[(page - 1) * per: page * per]}

    def touch(self, row, when):
        row = {**row, "aggiornato": when}
        self.rows[row["id"]] = row
        return row


BLOG = [
    art(1, "the-tower-thoth-tarot-meaning", "The Tower in the Thoth Tarot: Meaning and Symbols", "tower tarot meaning",
        when="2026-09-30T08:00:00+00:00", section="cards", mine=True),
    art(2, "celtic-cross-spread-guide", "How to Read the Celtic Cross Spread", "celtic cross spread",
        when="2026-09-20T08:00:00+00:00", section="spreads"),
    art(3, "full-moon-tarot-spread", "A Full Moon Tarot Spread for Release", "full moon tarot spread",
        when="2026-09-25T08:00:00+00:00", section="spreads"),
    art(4, "hermit-card-meaning", "The Hermit Card Meaning", "hermit tarot card meaning", status="bozza",
        when="2026-10-02T08:00:00+00:00"),
    art(5, "la-torre-significato", "La Torre: il significato nei Tarocchi di Thoth", "torre tarocchi thoth", lang="it",
        when="2026-09-28T08:00:00+00:00"),
    art(6, "death-card-meaning", "Death Card Meaning", "death card meaning", status="archiviato",
        when="2026-08-01T08:00:00+00:00"),
]


@pytest.fixture
def api(tmp_path, monkeypatch):
    fake = FakeTitles([dict(r) for r in BLOG])
    monkeypatch.setattr(tb, "call", fake)
    monkeypatch.setattr(tb, "_identity", lambda: "https://tarots.test/api|tk_live_abcd")
    monkeypatch.setattr(tb, "TITLES_CACHE_PATH", tmp_path / "titles-cache.json")
    monkeypatch.setattr(tb, "TITLES_PAGE", 2)  # small pages: every test also pages
    return fake


def _cache():
    return json.loads(tb.TITLES_CACHE_PATH.read_text(encoding="utf-8"))


def _lines(out: str):
    return [line for line in out.splitlines() if line and not line.startswith("#")]


# ---- titles ---------------------------------------------------------------------------------------------------


def test_first_run_loads_every_page_and_prints_one_compact_line_per_article(api, capsys):
    assert tb.main(["titles"]) == tb.EXIT_OK
    assert [q["pagina"] for q in api.queries] == [1, 2, 3] and all("dal" not in q for q in api.queries)
    assert all(q["archiviati"] == "true" and q["per_pagina"] == 2 for q in api.queries)
    out = capsys.readouterr().out
    lines = _lines(out)
    # drafts and published, not archived, newest first
    assert [line.split(" | ")[0] for line in lines] == [
        "hermit-card-meaning", "the-tower-thoth-tarot-meaning", "la-torre-significato", "full-moon-tarot-spread",
        "celtic-cross-spread-guide",
    ]
    assert lines[1] == ("the-tower-thoth-tarot-meaning | The Tower in the Thoth Tarot: Meaning and Symbols | "
                        "tower tarot meaning | en | pubblicato | 2026-09-30")
    assert out.startswith("# 5 of 6 article(s)")
    cache = _cache()
    assert len(cache["articles"]) == 6 and cache["synced_at"] == T0 and cache["identity"].endswith("tk_live_abcd")


def test_second_run_asks_only_for_what_changed_since_the_last_one(api, capsys):
    assert tb.main(["titles"]) == tb.EXIT_OK
    api.queries.clear()
    api.now = "2026-10-05T12:00:00+00:00"
    api.touch({**BLOG[1], "titolo": "The Celtic Cross Spread, Position by Position"}, "2026-10-05T11:00:00+00:00")
    api.rows["new"] = art(7, "shadow-work-tarot", "Shadow Work with Tarot", "shadow work tarot", when="2026-10-05T11:30:00+00:00")
    api.rows["new"]["id"] = "new"
    capsys.readouterr()
    assert tb.main(["titles"]) == tb.EXIT_OK
    # dal = the server clock of the last sync, minus the overlap
    assert len(api.queries) == 1 and _t(api.queries[0]["dal"]) == _t(T0) - tb.TITLES_OVERLAP
    lines = _lines(capsys.readouterr().out)
    assert lines[0].startswith("shadow-work-tarot | Shadow Work with Tarot")
    assert any("The Celtic Cross Spread, Position by Position" in line for line in lines)
    assert not any("How to Read the Celtic Cross Spread" in line for line in lines)
    assert _cache()["synced_at"] == "2026-10-05T12:00:00+00:00" and len(_cache()["articles"]) == 7


def test_a_deleted_article_stays_in_the_copy_until_refresh(api, capsys):
    assert tb.main(["titles"]) == tb.EXIT_OK
    del api.rows[BLOG[2]["id"]]  # deleted on the site
    capsys.readouterr()
    assert tb.main(["titles"]) == tb.EXIT_OK
    assert "full-moon-tarot-spread" in capsys.readouterr().out
    api.queries.clear()
    assert tb.main(["titles", "--refresh"]) == tb.EXIT_OK
    captured = capsys.readouterr()
    assert "full-moon-tarot-spread" not in captured.out and "--refresh" in captured.err
    assert all("dal" not in q for q in api.queries)
    assert BLOG[2]["id"] not in _cache()["articles"]


def test_a_copy_older_than_7_days_is_reloaded_in_full_by_itself(api, capsys, monkeypatch):
    assert tb.main(["titles"]) == tb.EXIT_OK
    cache = _cache()
    cache["full_at"] = (tb._utcnow() - datetime.timedelta(days=8)).isoformat()
    tb.TITLES_CACHE_PATH.write_text(json.dumps(cache), encoding="utf-8")
    del api.rows[BLOG[2]["id"]]
    api.queries.clear()
    capsys.readouterr()
    assert tb.main(["titles"]) == tb.EXIT_OK
    captured = capsys.readouterr()
    assert all("dal" not in q for q in api.queries) and "older than 7 days" in captured.err
    assert "full-moon-tarot-spread" not in captured.out
    # and a copy of another site or key is never reused
    api.queries.clear()
    monkeypatch.setattr(tb, "_identity", lambda: "https://tarots.test/api|tk_live_zzzz")
    assert tb.main(["titles"]) == tb.EXIT_OK
    assert all("dal" not in q for q in api.queries) and _cache()["identity"].endswith("tk_live_zzzz")


def test_filters_limit_all_and_json(api, capsys, monkeypatch):
    assert tb.main(["titles", "--lang", "it"]) == tb.EXIT_OK
    assert [line.split(" | ")[0] for line in _lines(capsys.readouterr().out)] == ["la-torre-significato"]
    assert tb.main(["titles", "--status", "draft"]) == tb.EXIT_OK
    assert [line.split(" | ")[0] for line in _lines(capsys.readouterr().out)] == ["hermit-card-meaning"]
    assert tb.main(["titles", "--status", "archived"]) == tb.EXIT_OK
    assert [line.split(" | ")[0] for line in _lines(capsys.readouterr().out)] == ["death-card-meaning"]
    assert tb.main(["titles", "--section", "spreads"]) == tb.EXIT_OK
    assert len(_lines(capsys.readouterr().out)) == 2
    # grep ignores case, accents and punctuation, and also looks in slug and keyword
    assert tb.main(["titles", "--grep", "CÉLTIC-cross"]) == tb.EXIT_OK
    assert [line.split(" | ")[0] for line in _lines(capsys.readouterr().out)] == ["celtic-cross-spread-guide"]
    assert tb.main(["titles", "--grep", "torre tarocchi"]) == tb.EXIT_OK
    assert len(_lines(capsys.readouterr().out)) == 1
    # without --all only the newest lines, and a footer says how many more
    monkeypatch.setattr(tb, "TITLES_SHOWN", 2)
    assert tb.main(["titles"]) == tb.EXIT_OK
    out = capsys.readouterr().out
    assert len(_lines(out)) == 2 and "3 more" in out
    assert tb.main(["titles", "--all"]) == tb.EXIT_OK
    assert len(_lines(capsys.readouterr().out)) == 5
    assert tb.main(["titles", "--all", "--json"]) == tb.EXIT_OK
    rows = json.loads(capsys.readouterr().out)
    assert len(rows) == 5 and rows[1]["mio"] is True and rows[1]["slug"] == "the-tower-thoth-tarot-meaning"


def test_when_the_api_cannot_be_reached_the_copy_is_used_with_a_warning(api, capsys):
    api.down = True
    assert tb.main(["titles"]) == tb.EXIT_API  # no copy yet: nothing to fall back on
    api.down = False
    assert tb.main(["titles"]) == tb.EXIT_OK
    capsys.readouterr()
    api.down = True
    assert tb.main(["titles"]) == tb.EXIT_OK
    captured = capsys.readouterr()
    assert "Using the local copy" in captured.err and len(_lines(captured.out)) == 5


def test_mine_is_unchanged(api, monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(tb, "call", lambda method, path, **kw: calls.append((method, path, kw)) or
                        {"totale": 0, "pagina": 1, "articoli": []})
    assert tb.main(["mine", "--status", "bozza"]) == tb.EXIT_OK
    assert calls == [("GET", "/posts", {"query": {"stato": "bozza", "pagina": 1, "per_pagina": 25}})]


# ---- topic-check ------------------------------------------------------------------------------------------------


def test_topic_words_normalise_case_accents_stop_words_and_plurals():
    assert tb.topic_words("The Tówer Cards’ meanings in the Thoth deck") == {"tower", "card", "meaning", "thoth", "deck"}
    assert tb.topic_words("Il significato della Torre nei Tarocchi") == {"significato", "torre", "tarocchi"}
    assert tb.topic_words("Mysteries of the Princess and the Magus") == {"mystery", "princess", "magus"}


@pytest.mark.parametrize("topic, verdict, best, exact", [
    ("Tower tarot meaning", "TAKEN", "the-tower-thoth-tarot-meaning", "same keyword"),
    ("THE TÓWER, tarot meaning!", "TAKEN", "the-tower-thoth-tarot-meaning", "same keyword"),
    ("the-tower-thoth-tarot-meaning", "TAKEN", "the-tower-thoth-tarot-meaning", "same slug"),
    ("How to read the Celtic Cross spread", "TAKEN", "celtic-cross-spread-guide", "same title"),
    ("The Tower Thoth card meanings", "TAKEN", "the-tower-thoth-tarot-meaning", None),
    ("Celtic cross spread positions", "CLOSE", "celtic-cross-spread-guide", None),
    ("Tower tarot meaning in love", "CLOSE", "the-tower-thoth-tarot-meaning", None),
    ("New moon tarot spread", "CLOSE", "full-moon-tarot-spread", None),
    ("Death card meaning", "FREE", None, None),          # the archived article does not count
    ("Shadow work journaling prompts", "FREE", None, None),
])
def test_topic_check_verdicts(api, capsys, topic, verdict, best, exact):
    code = tb.main(["topic-check", topic])
    out = capsys.readouterr().out
    assert code == (tb.EXIT_TAKEN if verdict == "TAKEN" else tb.EXIT_OK)
    assert out.strip().splitlines()[-1].startswith(f"{verdict}:")
    first = _lines(out)[0]
    if best:
        assert first.split("  ", 1)[1].startswith(best + " | ")
    if exact:
        assert first.startswith("1.00") and first.endswith(f"[{exact}]")


def test_topic_check_prints_the_5_closest_with_scores_and_json(api, capsys):
    for n, phase in enumerate(["new", "waning", "waxing", "blue", "harvest"], start=20):
        api.rows[str(n)] = {**art(n, f"{phase}-moon-ritual", f"A {phase} moon ritual", f"{phase} moon ritual"), "id": str(n)}
    assert tb.main(["topic-check", "full", "moon", "ritual", "for", "beginners"]) == tb.EXIT_OK  # unquoted words too
    lines = _lines(capsys.readouterr().out)
    assert len(lines) == 6 and lines[-1].startswith("CLOSE:")  # the 5 closest + the verdict
    scores = [float(line.split()[0]) for line in lines[:5]]
    assert scores == sorted(scores, reverse=True) and 0.4 <= scores[0] < tb.TOPIC_TAKEN and min(scores) > 0
    # an unrelated topic prints no line of zeros
    assert tb.main(["topic-check", "shadow work journaling"]) == tb.EXIT_OK
    out = capsys.readouterr().out
    assert "no article shares a topic word" in out and "0.00" not in out
    assert tb.main(["--json", "topic-check", "Tower tarot meaning"]) == tb.EXIT_TAKEN
    data = json.loads(capsys.readouterr().out)
    assert data["verdict"] == "TAKEN" and data["score"] == 1.0 and data["compared"] == 10
    assert data["matches"][0]["exact"] == "same keyword" and data["matches"][0]["slug"] == "the-tower-thoth-tarot-meaning"


def test_topic_check_by_language_and_with_a_fresh_copy(api, capsys):
    assert tb.main(["topic-check", "Tower tarot meaning", "--lang", "it"]) == tb.EXIT_OK
    assert capsys.readouterr().out.strip().splitlines()[-1].startswith("FREE:")
    # an article written a moment ago by someone else is seen: the copy is brought up to date first
    api.now = "2026-10-05T12:00:00+00:00"
    api.rows["x"] = {**art(9, "shadow-work-journaling-prompts", "Shadow Work Journaling Prompts", "shadow work journaling",
                          when="2026-10-05T11:59:00+00:00"), "id": "x"}
    assert tb.main(["topic-check", "Shadow work journaling prompts"]) == tb.EXIT_TAKEN
    assert any("dal" in q for q in api.queries)


def test_topic_check_needs_a_topic(api):
    assert tb.main(["topic-check", "!!!"]) == tb.EXIT_USAGE
