"""Where `generate` saves (the article's work folder, foto/) and which Python runs LitMedia, offline.

    backend/.venv/Scripts/python.exe -m pytest skills/tarots-blog-images/tests -q -p no:cacheprovider

No network, no LitMedia, no credit: `balance` and the LitMedia scripts are fakes, and so are the interpreters tried for
LitMedia (no real `python -c` is run except where a test says so).
"""
from __future__ import annotations

import datetime
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "tarots_images.py"
_spec = importlib.util.spec_from_file_location("tarots_images_cartella", SCRIPT)
ti = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ti)

TODAY = datetime.date.today().isoformat()
PROMPTS = [
    "A lone figure in a dark coat on a stone bridge in soft rain, an old river and a distant village at dusk, "
    "lamps coming on in the windows, seen from a distance, wide view, overcast sky, " + ti.HOUSE_STYLE,
    "An orchard of old apple trees at the edge of a Normandy village, lanterns hung in the branches for a harvest "
    "feast, seen from above, aerial view, under a clear starlight sky, " + ti.HOUSE_STYLE,
    "A heron standing in the shallows of a Japanese garden pond at first light, mist on the water, a stone lantern "
    "behind it, close-up, dawn light, " + ti.HOUSE_STYLE,
]
DIMS = [
    ["--kind", "figure-at-distance", "--shot", "wide", "--light", "overcast", "--setting", "river village"],
    ["--kind", "abstract-symbol", "--shot", "aerial", "--light", "starlight", "--setting", "Normandy orchard"],
    ["--kind", "animal", "--shot", "close-up", "--light", "dawn", "--setting", "Japanese garden"],
]


def _fake_litmedia(script, args, timeout):
    out_dir = Path(args[args.index("--output-dir") + 1])
    (out_dir / "image_1.jpg").write_bytes(b"\xff\xd8 fake picture " + args[args.index("--prompt") + 1].encode())

    class Done:
        returncode, stdout, stderr = 0, "", ""
    return Done()


@pytest.fixture
def work(tmp_path, monkeypatch):
    monkeypatch.setattr(ti, "PROGRESS_PATH", tmp_path / "images-progress.json")
    monkeypatch.setenv("TAROTS_WORK_DIR", str(tmp_path / "work"))
    monkeypatch.setattr(ti, "balance", lambda: 100)
    monkeypatch.setattr(ti, "_litmedia", _fake_litmedia)
    monkeypatch.setattr(ti, "call", lambda *a, **k: pytest.fail("the blog API was called"))
    return tmp_path / "work"


def _generate(n, *extra):
    return ti.main(["generate", "--prompt", PROMPTS[n], *DIMS[n], *extra])


# ---- generate saves in <work folder>/foto/ ------------------------------------------------------------------------


def test_generate_with_article_saves_in_its_work_folder(work, capsys):
    folder = work / "2026-10-01-samhain-tarot-spread"
    (folder / "foto").mkdir(parents=True)
    (work / "2026-09-20-samhain-tarot-spread" / "foto").mkdir(parents=True)  # older: not this one
    assert _generate(0, "--article", "samhain-tarot-spread") == ti.EXIT_OK
    assert (folder / "foto" / "cover.jpg").is_file()                     # 3:2 → cover.jpg
    assert str(folder / "foto" / "cover.jpg") in capsys.readouterr().out  # the full path is printed
    assert _generate(1, "--article", "Samhain Tarot Spread", "--aspect", "4:3") == ti.EXIT_OK  # a title is a slug too
    assert (folder / "foto" / "inline-1.jpg").is_file()
    assert _generate(2, "--article", "samhain-tarot-spread", "--out", "heron.jpg", "--aspect", "1:1") == ti.EXIT_OK
    assert (folder / "foto" / "heron.jpg").is_file()
    # the record points at the files in foto/, so tarots_blog.py finds them
    files = [e["file"] for e in json.loads(ti.PROGRESS_PATH.read_text(encoding="utf-8"))["_generated"]]
    assert files == [str(folder / "foto" / n) for n in ("cover.jpg", "inline-1.jpg", "heron.jpg")]


def test_generate_finds_the_folder_by_the_slug_inside_article_json(work):
    folder = work / "2026-10-02-working-title"
    (folder / "foto").mkdir(parents=True)
    (folder / "article.json").write_text(json.dumps({"slug": "samhain-tarot-spread"}), encoding="utf-8")
    assert _generate(0, "--article", "samhain-tarot-spread") == ti.EXIT_OK
    assert (folder / "foto" / "cover.jpg").is_file()


def test_generate_for_an_article_without_a_folder_makes_one_for_today(work, capsys):
    assert _generate(0, "--article", "the-tower-thoth") == ti.EXIT_OK
    assert (work / f"{TODAY}-the-tower-thoth" / "foto" / "cover.jpg").is_file()
    assert "no work folder for the-tower-thoth yet" in capsys.readouterr().err


def test_a_bare_out_name_goes_in_the_newest_work_folder_and_a_path_is_kept(work, tmp_path):
    (work / "2026-10-01-older" / "foto").mkdir(parents=True)
    (work / "2026-10-04-newest" / "foto").mkdir(parents=True)
    assert _generate(0, "--out", "my-cover.jpg") == ti.EXIT_OK
    assert (work / "2026-10-04-newest" / "foto" / "my-cover.jpg").is_file()
    elsewhere = tmp_path / "elsewhere" / "pic.jpg"
    assert _generate(1, "--out", str(elsewhere)) == ti.EXIT_OK
    assert elsewhere.is_file()


def test_generate_never_overwrites_and_needs_a_destination(work, monkeypatch, capsys):
    assert _generate(0, "--article", "x-article") == ti.EXIT_OK
    target = work / f"{TODAY}-x-article" / "foto" / "cover.jpg"
    before = target.read_bytes()
    monkeypatch.setattr(ti, "_litmedia", lambda *a, **k: pytest.fail("LitMedia called for an existing file"))
    assert _generate(1, "--article", "x-article", "--out", "cover.jpg") == ti.EXIT_USAGE
    assert "never overwritten" in capsys.readouterr().err and target.read_bytes() == before
    assert _generate(1) == ti.EXIT_USAGE                                  # neither --article nor --out
    assert "--article" in capsys.readouterr().err


def test_a_bare_name_without_any_work_folder_says_what_to_do(work, capsys):
    assert _generate(0, "--out", "cover.jpg") == ti.EXIT_USAGE
    assert "tarots_blog.py new" in capsys.readouterr().err


# ---- which Python runs LitMedia ----------------------------------------------------------------------------------


@pytest.fixture
def litmedia(tmp_path, monkeypatch):
    """A fake litmedia-skill folder (with the Seedream fix markers) and an empty interpreter cache."""
    folder = tmp_path / "litmedia-skill"
    (folder / "scripts").mkdir(parents=True)
    (folder / "scripts" / "ai_image.py").write_text("\n".join(ti.LITMEDIA_FIX_MARKERS), encoding="utf-8")
    (folder / "scripts" / "requirements.txt").write_text("requests\npython-dotenv\n", encoding="utf-8")
    monkeypatch.setenv("LITMEDIA_SKILL", str(folder))
    monkeypatch.setattr(ti, "_litmedia_python", None)
    return folder


def test_the_first_interpreter_with_the_dependencies_is_used_said_and_kept(litmedia, monkeypatch, capsys):
    candidates = [[sys.executable], ["C:/uv/python.exe"], ["py", "-3.12"], ["C:/Python310/python.exe"]]
    probed = []
    monkeypatch.setattr(ti, "_python_candidates", lambda: candidates)
    monkeypatch.setattr(ti, "_has_litmedia_deps", lambda cmd: probed.append(cmd) or cmd == ["py", "-3.12"])
    ran = []
    monkeypatch.setattr(ti.subprocess, "run", lambda cmd, **kw: ran.append(cmd) or subprocess.CompletedProcess(cmd, 0, '{"credit": 40}', ""))
    assert ti.balance() == 40
    assert probed == candidates[:3]                       # stops at the first that works
    assert ran[0][:2] == ["py", "-3.12"] and ran[0][2] == str(litmedia / "scripts" / "user.py")
    assert "note: LitMedia runs with py -3.12" in capsys.readouterr().err
    assert ti.balance() == 40 and len(probed) == 3        # kept for the process: no second probe
    assert capsys.readouterr().err == ""                  # and said once


def test_this_python_is_used_silently_when_it_has_the_dependencies(litmedia, monkeypatch, capsys):
    monkeypatch.setattr(ti, "_python_candidates", lambda: [[sys.executable], ["other"]])
    monkeypatch.setattr(ti, "_has_litmedia_deps", lambda cmd: True)
    assert ti.litmedia_python() == [sys.executable]
    assert capsys.readouterr().err == ""


def test_no_interpreter_with_the_dependencies_is_a_config_error_with_the_pip_command(litmedia, monkeypatch, capsys):
    monkeypatch.setattr(ti, "_python_candidates", lambda: [["C:/uv/python.exe"], ["py", "-3"]])
    monkeypatch.setattr(ti, "_has_litmedia_deps", lambda cmd: False)
    monkeypatch.setattr(ti.subprocess, "run", lambda *a, **k: pytest.fail("LitMedia ran without its dependencies"))
    assert ti.main(["balance"]) == ti.EXIT_CONFIG
    err = capsys.readouterr().err
    assert f"C:/uv/python.exe -m pip install -r {litmedia / 'scripts' / 'requirements.txt'}" in err
    assert "Tried: C:/uv/python.exe; py -3" in err and "alibabacloud_oss_v2" in err and "pymediainfo" in err
    assert "Nothing was installed" in err


def test_the_candidates_come_in_the_documented_order(monkeypatch, tmp_path):
    monkeypatch.setenv("LITMEDIA_PYTHON", "D:/chosen/python.exe")
    which = {"py": "C:/Windows/py.exe", "python3": None, "python": sys.executable}  # python = this one: listed once
    monkeypatch.setattr(ti.shutil, "which", lambda name: which.get(name))
    local = tmp_path / "local"
    for version in ("Python310", "Python312", "Python39"):
        (local / "Programs" / "Python" / version).mkdir(parents=True)
        (local / "Programs" / "Python" / version / "python.exe").write_bytes(b"")
    monkeypatch.setenv("LOCALAPPDATA", str(local))
    got = ti._python_candidates()
    assert got[:4] == [["D:/chosen/python.exe"], [sys.executable], ["C:/Windows/py.exe", "-3.12"], ["C:/Windows/py.exe", "-3"]]
    rest = [c[0] for c in got[4:]]
    if os.name == "nt":
        base = local / "Programs" / "Python"
        assert rest == [str(base / v / "python.exe") for v in ("Python312", "Python310", "Python39")]
    else:
        assert rest == []


def test_the_import_probe_is_a_real_short_subprocess():
    assert ti._has_litmedia_deps(["a-python-that-does-not-exist-anywhere"]) is False
    ok = subprocess.run([sys.executable, "-c", ti.LITMEDIA_IMPORTS], capture_output=True).returncode == 0
    assert ti._has_litmedia_deps([sys.executable]) is ok
