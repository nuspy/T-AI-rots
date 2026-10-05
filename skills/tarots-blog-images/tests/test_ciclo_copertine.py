"""The loop that redoes many covers one article per agent run (`redo_covers_loop.py`), offline.

    backend/.venv/Scripts/python.exe -m pytest skills/tarots-blog-images/tests -q -p no:cacheprovider

No network, no LitMedia, no Hermes: `tarots_images.py list / show / balance` are a fake blog in memory, and the agent
is a fake too (a function, or a tiny Python script where the test is about the real process). The log and the
progress record are files in a temporary folder.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "redo_covers_loop.py"
_spec = importlib.util.spec_from_file_location("redo_covers_loop", SCRIPT)
rl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rl)


class FakeBlog:
    """The drafts, their covers, the LitMedia balance and the progress record of tarots_images.py."""

    def __init__(self, tmp: Path, n: int = 4, balance: int = 200):
        self.progress = tmp / "images-progress.json"
        self.posts = {f"id-{i}": {"id": f"id-{i}", "slug": f"article-{i}", "titolo": f"Article {i}", "stato": "bozza",
                                  "copertina": {"id": f"old-{i}", "url": f"/blog/media/old-{i}.webp"}}
                      for i in range(1, n + 1)}
        self.balance = balance
        self.calls = []
        self.lists = []
        self.broken_show = set()
        self.sections = [{"slug": "major-arcana", "nome": "Major Arcana", "tipo": "carte",
                          "descrizione": "The great themes.", "immagine": None},
                         {"slug": "cups", "nome": "Cups", "tipo": "carte", "descrizione": "Water.",
                          "immagine": {"id": "s-old", "url": "/m/s-old.webp"}},
                         {"slug": "love", "nome": "Love", "tipo": "articoli", "descrizione": "Love read through the cards.",
                          "immagine": None}]
        self.spreads = [{"id": "croce-celtica", "nome": "Celtic Cross", "descrizione": "Ten cards.",
                         "tradizione": "Celtic tradition", "n_carte": 10, "immagine": None}]

    def set_picture(self, mode: str, key: str, *, record: bool = True, cost: int = 10) -> None:
        """What an agent does with `section-cover` / `spread-cover`."""
        self.balance -= cost
        rows, field = (self.sections, "slug") if mode == "sections" else (self.spreads, "id")
        next(r for r in rows if r[field] == key)["immagine"] = {"id": f"new-{key}", "url": f"/m/new-{key}.webp"}
        if record:
            data = self.record()
            data.setdefault("_sections" if mode == "sections" else "_spreads", {})[key] = {"file": "x.jpg", "sha256": key}
            self.progress.write_text(json.dumps(data), encoding="utf-8")

    def record(self) -> dict:
        return json.loads(self.progress.read_text(encoding="utf-8")) if self.progress.exists() else {}

    def images(self, args, timeout=300):
        self.calls.append(args[0])
        if args[0] == "list":
            self.lists.append(args[1:])
            status = {"draft": "bozza", "published": "pubblicato"}.get(args[2]) if args[1] == "--status" else None
            rows = [p for p in self.posts.values() if status is None or p["stato"] == status]
            if "--no-cover" in args:
                assert args[1:] == ["--no-cover", "--json"]               # in every status
                return json.dumps([p for p in rows if not p["copertina"]])
            assert args[-2:] == ["--todo", "--json"]
            done = self.record()
            return json.dumps([p for p in rows if not (done.get(p["id"]) or {}).get("cover")])
        if args[0] in ("sections", "spreads"):
            rows = self.sections if args[0] == "sections" else self.spreads
            return json.dumps([r for r in rows if "--missing" not in args or not r["immagine"]])
        if args[0] == "show":
            if args[1] in self.broken_show:
                raise rl.LoopError("tarots_images.py show failed (exit 4): HTTP 404", rl.EXIT_IMAGES)
            return json.dumps(self.posts[args[1]])
        if args[0] == "balance":
            assert args[1:] == ["--json"]
            return json.dumps({"credit": self.balance})
        raise AssertionError(f"unexpected tarots_images.py {args}")

    # what an agent can do to an article
    def redo(self, post_id: str, *, record: bool = True, cost: int = 10) -> None:
        self.balance -= cost
        self.posts[post_id]["copertina"] = {"id": f"new-{post_id}", "url": f"/blog/media/new-{post_id}.webp"}
        if record:
            data = self.record()
            data[post_id] = {"cover": {"file": "x.jpg", "sha256": "abc", "when": "2026-10-05T10:00:00+00:00"},
                             "inline": []}
            self.progress.write_text(json.dumps(data), encoding="utf-8")


class FakeAgent:
    """Does to each article what `plan` says (default: redo it), remembers the prompts it received."""

    def __init__(self, blog: FakeBlog, plan=None):
        self.blog, self.plan, self.prompts, self.cmds = blog, plan or {}, [], []

    def __call__(self, cmd, timeout, cwd):
        self.cmds.append(cmd)
        prompt = cmd[-1]
        self.prompts.append(prompt)
        post_id = next(i for i in self.blog.posts if f"(id {i}," in prompt)
        what = self.plan.get(post_id, "ok")
        if what == "ok":
            self.blog.redo(post_id)
            return 0, "done"
        if what == "unrecorded":
            self.blog.redo(post_id, record=False)
            return 0, "done with my own upload"
        if what == "timeout":
            self.blog.balance -= 10
            return None, "still thinking"
        return 1, "I could not do it"                      # "fail": nothing changes


@pytest.fixture
def world(tmp_path, monkeypatch):
    blog = FakeBlog(tmp_path)
    agent = FakeAgent(blog)
    monkeypatch.setattr(rl, "images", blog.images)
    monkeypatch.setattr(rl, "run_agent", agent)
    monkeypatch.setenv("TAROTS_IMAGES_PROGRESS", str(blog.progress))
    log = tmp_path / "loop-covers-log.jsonl"
    base = ["--log", str(log), "--cwd", str(tmp_path / "cwd"), "--agent-cmd", f'"{sys.executable}" -c pass']
    return blog, agent, log, base


def entries(log: Path, event: str = "article") -> list:
    return [e for e in rl.read_log(log) if e.get("event") == event]


# ---- dry run -------------------------------------------------------------------------------------------------------


def test_dry_run_prints_the_list_and_the_first_prompt_and_launches_nothing(world, monkeypatch, capsys):
    blog, agent, log, base = world
    assert rl.main([*base, "--dry-run", "--limit", "2"]) == rl.EXIT_OK
    out = capsys.readouterr().out
    assert "4 article(s) with the cover still to redo (draft); 4 in the queue" in out
    assert " *  1. id-1  Article 1" in out and " *  2. id-2" in out and "    3. id-3" in out  # * = this run
    images = rl.images_command()
    assert "Articolo: «Article 1» (id id-1, slug article-1)" in out
    assert f"{images} show id-1" in out and f"{images} progress" in out and f"{images} catalog" in out
    assert f"{images} generate --article id-1 --aspect 3:2 --resolution 2K" in out
    assert f"{images} cover id-1 <il file stampato da generate> --alt" in out
    assert "nessuna domanda" in out and "nessun altro articolo" in out and "nessuno script tuo" in out
    assert "fermati" in out and "dry run: nothing was launched" in out
    assert agent.cmds == [] and blog.calls == ["list"] and not log.exists()   # no balance, no show, no log


def test_the_default_agent_is_hermes_one_shot_with_the_skill(world, monkeypatch, capsys):
    blog, agent, log, base = world
    monkeypatch.setattr(rl, "find_hermes", lambda: "C:/hermes/hermes.exe")
    cmd = rl.agent_command(None, "the prompt", blog.posts["id-1"])
    assert cmd == ["C:/hermes/hermes.exe", "-z", "the prompt", "--skills", "tarots-blog-images"]
    monkeypatch.setattr(rl, "find_hermes", lambda: None)
    assert rl.main(["--log", str(log), "--cwd", str(log.parent)]) == rl.EXIT_AGENT
    assert "hermes not found" in capsys.readouterr().err and agent.cmds == [] and "balance" not in blog.calls


def test_find_hermes_falls_back_on_the_venv_of_localappdata(monkeypatch, tmp_path):
    exe = tmp_path / "hermes" / "hermes-agent" / "venv" / "Scripts" / "hermes.exe"
    exe.parent.mkdir(parents=True)
    exe.write_bytes(b"")
    monkeypatch.setattr(rl.shutil, "which", lambda name: None)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    assert rl.find_hermes() == str(exe)


def test_agent_cmd_placeholders(world):
    blog, *_ = world
    post = blog.posts["id-2"]
    py = sys.executable
    assert rl.agent_command(f'"{py}" agent.py --task {{prompt}} --for {{slug}}', "P", post) == \
        [py, "agent.py", "--task", "P", "--for", "article-2"]
    assert rl.agent_command(f'"{py}" agent.py --id={{id}}', "P", post) == [py, "agent.py", "--id=id-2", "P"]  # appended
    with pytest.raises(rl.LoopError):
        rl.agent_command("no-such-agent-anywhere --x", "P", post)


# ---- the loop: limit, restart, log ------------------------------------------------------------------------------------


def test_one_agent_run_per_article_up_to_the_limit_then_it_goes_on_from_there(world, capsys):
    blog, agent, log, base = world
    assert rl.main([*base, "--limit", "2"]) == rl.EXIT_OK
    out = capsys.readouterr().out
    assert len(agent.prompts) == 2 and "(id id-1," in agent.prompts[0] and "(id id-2," in agent.prompts[1]
    assert all(p.count("(id ") == 1 for p in agent.prompts)          # each run is about one article only
    assert "Summary: redone 2, failed 0, credits spent 20 (balance 180); still to do 2. Stopped: --limit 2 reached." in out
    assert "Run it again" in out
    first = entries(log)
    assert [(e["id"], e["outcome"]) for e in first] == [("id-1", "ok"), ("id-2", "ok")]
    e = first[0]
    assert e["credits_before"] == 200 and e["credits_after"] == 190 and e["spent"] == 10 and e["seconds"] >= 0
    assert e["cover_before"] == "old-1" and e["cover_after"] == "new-id-1" and e["title"] == "Article 1"
    assert Path(e["output"]).read_text(encoding="utf-8") == "done"   # the agent's output is kept
    assert entries(log, "run")[0]["redone"] == 2
    # run again: it starts from the third
    assert rl.main([*base]) == rl.EXIT_OK
    assert [p.split("(id ")[1].split(",")[0] for p in agent.prompts[2:]] == ["id-3", "id-4"]
    assert "Stopped: no article left" in capsys.readouterr().out
    assert rl.main([*base]) == rl.EXIT_OK and "nothing to do" in capsys.readouterr().out


def test_the_balance_is_read_before_every_article(world):
    blog, agent, log, base = world
    assert rl.main([*base, "--limit", "3"]) == rl.EXIT_OK
    # one before each article (the budget check), one after each (credits spent)
    assert blog.calls.count("balance") == 6 and blog.calls.count("show") == 6


def test_an_article_the_log_has_as_done_is_not_redone_even_if_still_listed(world, capsys):
    blog, agent, log, base = world
    rl.write_log(log, {"event": "article", "id": "id-1", "outcome": "ok"})
    assert rl.main([*base, "--limit", "1"]) == rl.EXIT_OK
    assert "(id id-2," in agent.prompts[0]
    assert "1 done according to the log but still listed (skipped)" in capsys.readouterr().out


# ---- verification: the agent's word is not enough ---------------------------------------------------------------------


@pytest.mark.parametrize("what, reason", [
    ("fail", "the cover on the site did not change (agent exit 1)"),
    ("timeout", "timeout after 15 min"),
    ("unrecorded", "tarots_images.py `cover` did not record it"),
])
def test_a_cover_not_replaced_and_recorded_is_a_failure(world, what, reason):
    blog, agent, log, base = world
    agent.plan = {"id-1": what}
    assert rl.main([*base, "--limit", "2"]) == rl.EXIT_OK
    got = entries(log)
    assert got[0]["outcome"] == "failed" and reason in got[0]["reason"]
    assert got[1]["outcome"] == "ok"


def test_two_failures_in_a_row_stop_the_loop_and_are_skipped_next_time(world, capsys):
    blog, agent, log, base = world
    agent.plan = {"id-1": "fail", "id-2": "timeout"}
    assert rl.main([*base]) == rl.EXIT_FAILURES
    out = capsys.readouterr().out
    assert len(agent.prompts) == 2
    assert "Summary: redone 0, failed 2, credits spent 10" in out and "2 failures in a row" in out
    assert "Failed: id-1, id-2" in out
    # next run: the failed ones are skipped, unless asked
    agent.plan = {}
    assert rl.main([*base, "--limit", "1"]) == rl.EXIT_OK
    assert "(id id-3," in agent.prompts[-1]
    assert "2 failed before (skipped: --retry-failed to include them)" in capsys.readouterr().out
    assert rl.main([*base, "--limit", "1", "--retry-failed"]) == rl.EXIT_OK
    assert "(id id-1," in agent.prompts[-1]


def test_a_failure_between_successes_does_not_stop(world):
    blog, agent, log, base = world
    agent.plan = {"id-1": "fail", "id-3": "fail"}
    assert rl.main([*base]) == rl.EXIT_OK
    assert [e["outcome"] for e in entries(log)] == ["failed", "ok", "failed", "ok"]


def test_an_article_that_cannot_be_read_fails_without_launching_the_agent(world):
    blog, agent, log, base = world
    blog.broken_show = {"id-1"}
    assert rl.main([*base, "--limit", "2"]) == rl.EXIT_OK
    got = entries(log)
    assert got[0]["outcome"] == "failed" and "cannot read the article before the agent" in got[0]["reason"]
    assert len(agent.prompts) == 1 and "(id id-2," in agent.prompts[0]


def test_max_failures_is_configurable(world):
    blog, agent, log, base = world
    agent.plan = {i: "fail" for i in blog.posts}
    assert rl.main([*base, "--max-failures", "3"]) == rl.EXIT_FAILURES
    assert len(entries(log)) == 3


# ---- budget and reserve -------------------------------------------------------------------------------------------------


def test_the_budget_stops_before_an_article_that_could_pass_it(world, capsys):
    blog, agent, log, base = world
    # 20 credits counted per article: 0+20 <= 30 yes, 10+20 <= 30 yes, 20+20 > 30 stop
    assert rl.main([*base, "--budget", "30"]) == rl.EXIT_OK
    out = capsys.readouterr().out
    assert len(agent.prompts) == 2
    assert "Stopped: --budget 30: spent 20, the next article could cost 20." in out and "credits spent 20" in out
    assert rl.main([*base, "--budget", "10", "--cost", "10"]) == rl.EXIT_OK   # a new run counts its own spending
    assert len(agent.prompts) == 3


def test_the_reserve_stays_on_the_account(world, capsys):
    blog, agent, log, base = world
    blog.balance = 35
    assert rl.main([*base, "--reserve", "10"]) == rl.EXIT_OK          # 35-20 >= 10 yes; 25-20 < 10 stop
    assert len(agent.prompts) == 1
    assert "Stopped: --reserve 10: balance 25" in capsys.readouterr().out


def test_an_unreadable_balance_launches_nothing_more(world, monkeypatch, capsys):
    blog, agent, log, base = world
    real = blog.images

    def no_balance(args, timeout=300):
        if args[0] == "balance":
            raise rl.LoopError("tarots_images.py balance failed (exit 4): login expired", rl.EXIT_IMAGES)
        return real(args, timeout)
    monkeypatch.setattr(rl, "images", no_balance)
    assert rl.main([*base]) == rl.EXIT_IMAGES
    assert agent.prompts == [] and "the balance cannot be read" in capsys.readouterr().out


def test_bad_numbers_are_a_usage_error(world):
    *_, base = world
    for bad in (["--limit", "0"], ["--timeout", "0"], ["--budget", "-1"]):
        assert rl.main([*base, *bad]) == rl.EXIT_USAGE


# ---- --status and --missing: the articles with no cover, in every status (5/10/2026) ------------------------------------


def test_missing_adds_the_articles_with_no_cover_in_every_status(world, capsys):
    blog, agent, log, base = world
    blog.posts["id-5"] = {"id": "id-5", "slug": "wheel-of-fortune", "titolo": "Wheel of Fortune", "stato": "pubblicato",
                          "copertina": None}
    blog.posts["id-2"]["copertina"] = None                                  # a draft with no cover: listed once
    assert rl.main([*base, "--dry-run"]) == rl.EXIT_OK
    assert "id-5" not in capsys.readouterr().out                           # drafts only, by default
    assert rl.main([*base, "--missing", "--dry-run"]) == rl.EXIT_OK
    out = capsys.readouterr().out
    assert "5 article(s) with the cover still to redo (draft, and with no cover in every status); 5 in the queue" in out
    assert out.count("id-2 ") == 1 and "  5. id-5  Wheel of Fortune" in out
    assert blog.lists[-2:] == [["--status", "draft", "--todo", "--json"], ["--no-cover", "--json"]]


def test_a_cover_from_none_to_one_is_a_success(world):
    blog, agent, log, base = world
    blog.posts = {"id-5": {"id": "id-5", "slug": "wheel-of-fortune", "titolo": "Wheel of Fortune",
                           "stato": "pubblicato", "copertina": None}}
    assert rl.main([*base, "--missing"]) == rl.EXIT_OK
    got = entries(log)
    assert [(e["id"], e["outcome"]) for e in got] == [("id-5", "ok")]
    assert got[0]["cover_before"] is None and got[0]["cover_after"] == "new-id-5"


@pytest.mark.parametrize("status, expected", [("all", []), ("published", ["--status", "published"])])
def test_status_all_and_published(world, status, expected):
    blog, agent, log, base = world
    assert rl.main([*base, "--status", status, "--dry-run"]) == rl.EXIT_OK
    assert blog.lists[-1] == [*expected, "--todo", "--json"]


def test_status_and_missing_are_for_articles_only(world, capsys):
    *_, base = world
    assert rl.main([*base, "--sections", "--missing"]) == rl.EXIT_USAGE
    assert rl.main([*base, "--spreads", "--status", "all"]) == rl.EXIT_USAGE
    with pytest.raises(SystemExit):
        rl.main([*base, "--sections", "--spreads"])


# ---- --sections and --spreads: one agent per section or spread without a picture -----------------------------------------


class TargetAgent:
    """Sets the picture of the section or spread its prompt names, as `plan` says (default: set and recorded)."""

    def __init__(self, blog: FakeBlog, mode: str, plan=None):
        self.blog, self.mode, self.plan, self.prompts = blog, mode, plan or {}, []

    def __call__(self, cmd, timeout, cwd):
        prompt = cmd[-1]
        self.prompts.append(prompt)
        rows = self.blog.sections if self.mode == "sections" else self.blog.spreads
        key = next(r.get("slug") or r["id"] for r in rows
                   if f"(slug {r.get('slug')}," in prompt or f"(id {r.get('id')}," in prompt)
        what = self.plan.get(key, "ok")
        if what == "ok":
            self.blog.set_picture(self.mode, key)
            return 0, "done"
        if what == "unrecorded":
            self.blog.set_picture(self.mode, key, record=False)
            return 0, "done my way"
        return 1, "failed"


def test_sections_one_agent_per_section_without_a_picture(world, monkeypatch, capsys):
    blog, _agent, log, base = world
    agent = TargetAgent(blog, "sections", {"love": "unrecorded"})
    monkeypatch.setattr(rl, "run_agent", agent)
    assert rl.main([*base, "--sections", "--dry-run"]) == rl.EXIT_OK
    out = capsys.readouterr().out
    assert "2 section(s) with no picture (sections); 2 in the queue" in out and "cups" not in out
    images = rl.images_command()
    assert "Sezione: «Major Arcana» (slug major-arcana, tipo carte)" in out
    assert f"{images} generate --section major-arcana --aspect 3:2 --resolution 2K" in out
    assert f"{images} section-cover major-arcana <il file stampato da generate>" in out
    assert "mostra il MONDO di queste carte" in out and "mai come soggetto" in out
    assert "cost: at most 40 credits for this run (2 × 20; one picture is 10)" in out
    assert rl.main([*base, "--sections"]) == rl.EXIT_OK
    got = entries(log, "section")
    assert [(e["id"], e["outcome"]) for e in got] == [("major-arcana", "ok"), ("love", "failed")]
    assert got[0]["cover_before"] is None and got[0]["cover_after"] == "new-major-arcana"
    assert "`section-cover` did not record it" in got[1]["reason"]
    assert "mostra il tema della sezione" not in agent.prompts[0] and "mostra il tema della sezione" in agent.prompts[1]
    assert entries(log) == []                                             # no article event
    assert "Summary: redone 1, failed 1, credits spent 20" in capsys.readouterr().out
    # run again: the section done is no longer listed, the failed one is skipped
    assert rl.main([*base, "--sections"]) == rl.EXIT_OK
    assert "nothing to do" in capsys.readouterr().out


def test_spreads_with_their_own_prompt_and_the_log_kept_apart(world, monkeypatch, capsys):
    blog, _agent, log, base = world
    rl.write_log(log, {"event": "article", "id": "croce-celtica", "outcome": "ok"})   # an article event: not this
    agent = TargetAgent(blog, "spreads")
    monkeypatch.setattr(rl, "run_agent", agent)
    assert rl.main([*base, "--spreads"]) == rl.EXIT_OK
    prompt = agent.prompts[0]
    assert "Stesa: «Celtic Cross» (id croce-celtica, 10 carte, tradizione: Celtic tradition)" in prompt
    assert "spread-cover croce-celtica" in prompt and "--spread croce-celtica" in prompt
    assert "Lo schema delle posizioni lo disegna il sito" in prompt
    assert [(e["id"], e["outcome"]) for e in entries(log, "spread")] == [("croce-celtica", "ok")]
    assert "Stopped: no spread left" in capsys.readouterr().out


def test_a_section_that_disappears_is_a_failure_not_a_crash(world, monkeypatch):
    blog, _agent, log, base = world

    def vanish(cmd, timeout, cwd):
        blog.sections = [s for s in blog.sections if s["slug"] != "major-arcana"]
        return 0, "deleted it"
    monkeypatch.setattr(rl, "run_agent", vanish)
    assert rl.main([*base, "--sections", "--limit", "1"]) == rl.EXIT_OK
    got = entries(log, "section")[0]
    assert got["outcome"] == "failed" and "cannot read the section after the agent" in got["reason"]


# ---- the real agent process ----------------------------------------------------------------------------------------------


def test_the_agent_gets_the_prompt_as_one_argument_and_runs_in_cwd(tmp_path):
    agent = tmp_path / "agent.py"
    agent.write_text("import json, os, sys\nprint(json.dumps({'argv': sys.argv[1:], 'cwd': os.getcwd()}))\n",
                     encoding="utf-8")
    prompt = rl.make_prompt(rl.DEFAULT_PROMPT, {"id": "id-1", "slug": "s", "titolo": 'A "quoted" title'})
    cmd = rl.agent_command(f'"{sys.executable}" "{agent}" --once {{prompt}}', prompt, {"id": "id-1"})
    code, out = rl.run_agent(cmd, 60, tmp_path)
    got = json.loads(out)
    assert code == 0 and got["argv"] == ["--once", prompt] and Path(got["cwd"]) == tmp_path


def test_an_agent_out_of_time_is_stopped(tmp_path):
    agent = tmp_path / "slow.py"
    agent.write_text("import time\nprint('started', flush=True)\ntime.sleep(60)\n", encoding="utf-8")
    t0 = time.monotonic()
    code, out = rl.run_agent([sys.executable, str(agent)], 2, tmp_path)
    assert code is None and time.monotonic() - t0 < 40
