#!/usr/bin/env python3
"""redo_covers_loop.py: redo the covers of many blog articles, ONE article per agent run, each with a clean context.

Standard library only (Python 3.8+). This is the only way allowed to work on many articles: the prompt of every
picture has to be written by an LLM that read that article, and a small model degrades over a long session with many
articles. So this deterministic loop, outside the agent, does the bookkeeping and launches the agent once per
article, with a short prompt about that article alone:

    1. the articles to redo: `tarots_images.py list --status draft --todo --json` (cover not redone yet), minus the
       ones the log already has as done (and, unless --retry-failed, as failed);
    2. before each article: `balance` (LitMedia credits); stop if this article could pass --budget or go below
       --reserve; the cover before (`show ID`) and the progress record of the article (images-progress.json);
    3. the agent, by default `hermes -z "<prompt>" --skills tarots-blog-images`, with a timeout (--timeout);
    4. after: the cover again (`show ID`), the progress record and `balance`. The article is done only if the cover
       on the site changed AND `tarots_images.py cover` recorded it; anything else is a failure;
    5. one line per article in ~/.tarots-blog/loop-covers-log.jsonl (article, outcome, reason, seconds, credits
       before and after) and the agent's output in ~/.tarots-blog/loop-covers/; stop after 2 failures in a row.

Run it again to go on: the articles done leave `--todo` and are in the log. At the end it prints a summary: redone,
failed, credits spent.

    python redo_covers_loop.py --dry-run                  the list and the prompt of the first article; nothing run
    python redo_covers_loop.py --limit 10 --budget 150    ten articles at most, 150 credits at most
    python redo_covers_loop.py --agent-cmd "myagent --once {prompt}"   another agent ({prompt}, {id}, {slug}, {title})

The prompt is a template (--prompt-file to change it) with {id}, {slug}, {title} and {images} (the command that runs
tarots_images.py, absolute paths). The agent runs in ~/.tarots-blog (--cwd), never in a repository.

Exit codes: 0 finished (no article left, or --limit, --budget or --reserve reached) · 2 usage · 3 stopped after
consecutive failures · 4 tarots_images.py could not list the articles or read the balance · 5 the agent command was
not found.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

EXIT_OK, EXIT_USAGE, EXIT_FAILURES, EXIT_IMAGES, EXIT_AGENT = 0, 2, 3, 4, 5

IMAGES = Path(__file__).resolve().with_name("tarots_images.py")
HOME_DIR = Path.home() / ".tarots-blog"
LOG_PATH = HOME_DIR / "loop-covers-log.jsonl"
ARTICLE_COST = 20         # the most one article may cost: a cover (10 credits, Seedream 5.0 2K) and one new try
MAX_FAILURES = 2          # failures in a row that stop the loop
DEFAULT_LIMIT = 10
DEFAULT_TIMEOUT_MIN = 15.0

#: Short and in Italian, as the operator asked: one article, the steps in order, no questions, stop on a failure.
DEFAULT_PROMPT = """\
Rifai SOLO la copertina di UN articolo del blog TAROTS chat, con la skill tarots-blog-images.
Articolo: «{title}» (id {id}, slug {slug}).
1. Leggi tutto l'articolo: {images} show {id}
2. Scegli una forma libera: {images} progress   e   {images} catalog
3. Scrivi il prompt dell'immagine dal contenuto dell'articolo: una scena del suo mondo, mai una foto di carte.
4. Genera: {images} generate --article {id} --aspect 3:2 --resolution 2K --kind <kind> --shot <shot> --light <light> --setting "<luogo>" --prompt "<prompt>"
5. Guarda l'immagine, poi sostituisci la copertina: {images} cover {id} <il file stampato da generate> --alt "<cosa mostra>"
Regole: nessuna domanda, nessun altro articolo, nessuno script tuo, niente immagini nel testo.
Se un passo fallisce, fermati e scrivi quale passo e perché.
"""


class LoopError(Exception):
    def __init__(self, message: str, code: int):
        super().__init__(message)
        self.code = code


# ---- tarots_images.py (the only way this loop reads the blog and the credits) -------------------------------------


def images(args: List[str], timeout: int = 300) -> str:
    """Run `tarots_images.py ARGS` with this Python and return its stdout; a non-zero exit is a LoopError."""
    try:
        done = subprocess.run([sys.executable, str(IMAGES), *args], capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired:
        raise LoopError(f"tarots_images.py {' '.join(args)} did not answer within {timeout}s", EXIT_IMAGES) from None
    if done.returncode != 0:
        tail = (done.stderr or done.stdout).strip()[-600:]
        raise LoopError(f"tarots_images.py {' '.join(args)} failed (exit {done.returncode}): {tail}", EXIT_IMAGES)
    return done.stdout


def articles_todo(status: str) -> List[Dict[str, Any]]:
    """The articles whose cover tarots_images.py has not redone yet (`list --todo`), as the API lists them."""
    out = images(["list", "--status", status, "--todo", "--json"])
    try:
        rows = json.loads(out)
    except ValueError:
        raise LoopError(f"`list --json` did not print JSON: {out.strip()[:300]}", EXIT_IMAGES) from None
    return [r for r in rows if isinstance(r, dict) and r.get("id")]


def credits() -> int:
    out = images(["balance", "--json"], timeout=120)
    try:
        return int(json.loads(out)["credit"])
    except (ValueError, KeyError, TypeError):
        raise LoopError(f"`balance --json` did not print the credits: {out.strip()[:300]}", EXIT_IMAGES) from None


def cover_of(post_id: str) -> Optional[Dict[str, Any]]:
    """The cover on the site (`show ID` → copertina: id, url, mini, alt), or None when the article has none."""
    data = json.loads(images(["show", post_id]))
    return data.get("copertina") or None


def cover_key(cover: Optional[Dict[str, Any]]) -> Optional[str]:
    return str(cover.get("id") or cover.get("url") or "") or None if cover else None


def progress_path() -> Path:
    """The record of tarots_images.py, read at every call (TAROTS_IMAGES_PROGRESS may be set for one run)."""
    env = os.environ.get("TAROTS_IMAGES_PROGRESS", "").strip()
    return Path(env).expanduser() if env else HOME_DIR / "images-progress.json"


def recorded_cover(post_id: str) -> Optional[Dict[str, Any]]:
    """What `tarots_images.py cover` recorded for this article (file, sha256, url, alt, prompt, when), or None."""
    try:
        data = json.loads(progress_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    entry = data.get(post_id) if isinstance(data, dict) else None
    return entry.get("cover") if isinstance(entry, dict) else None


# ---- the log ---------------------------------------------------------------------------------------------------------


def read_log(path: Path) -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return entries
    for line in lines:
        try:
            entry = json.loads(line)
        except ValueError:
            continue  # a line cut by a crash: the rest of the log still counts
        if isinstance(entry, dict):
            entries.append(entry)
    return entries


def write_log(path: Path, entry: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def outcomes(entries: List[Dict[str, Any]]) -> Dict[str, str]:
    """The last outcome of every article in the log: "ok" or "failed"."""
    last: Dict[str, str] = {}
    for e in entries:
        if e.get("event") == "article" and e.get("id"):
            last[str(e["id"])] = str(e.get("outcome"))
    return last


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


# ---- the agent ---------------------------------------------------------------------------------------------------


def find_hermes() -> Optional[str]:
    found = shutil.which("hermes")
    if found:
        return found
    local = os.environ.get("LOCALAPPDATA")
    if local:
        exe = Path(local) / "hermes" / "hermes-agent" / "venv" / "Scripts" / "hermes.exe"
        if exe.is_file():
            return str(exe)
    return None


def split_command(text: str) -> List[str]:
    """A command line as typed in the shell of this system: quotes group words; Windows backslashes stay."""
    if os.name != "nt":
        return shlex.split(text)
    parts = shlex.split(text, posix=False)
    return [p[1:-1] if len(p) >= 2 and p[0] == p[-1] and p[0] in "\"'" else p for p in parts]


def agent_command(template: Optional[str], prompt: str, post: Dict[str, Any]) -> List[str]:
    """The agent's argv for one article. Default: hermes -z PROMPT --skills tarots-blog-images. With --agent-cmd,
    {prompt} (one argument), {id}, {slug} and {title} are replaced; without {prompt} the prompt goes last."""
    if template is None:
        hermes = find_hermes()
        if not hermes:
            raise LoopError("hermes not found: not in the PATH nor in %LOCALAPPDATA%\\hermes\\hermes-agent\\venv\\"
                            "Scripts\\hermes.exe. Install it, or give another agent with --agent-cmd.", EXIT_AGENT)
        return [hermes, "-z", prompt, "--skills", "tarots-blog-images"]
    parts = split_command(template)
    if not parts:
        raise LoopError("--agent-cmd is empty", EXIT_USAGE)
    values = {"id": str(post.get("id", "")), "slug": str(post.get("slug") or ""), "title": str(post.get("titolo") or "")}
    out: List[str] = []
    for part in parts:
        if part == "{prompt}":
            out.append(prompt)
            continue
        out.append(re.sub(r"\{(id|slug|title|prompt)\}", lambda m: prompt if m.group(1) == "prompt" else values[m.group(1)], part))
    if not any("{prompt}" in p for p in parts):
        out.append(prompt)
    if not shutil.which(out[0]) and not Path(out[0]).is_file():
        raise LoopError(f"the agent command {out[0]!r} was not found", EXIT_AGENT)
    return out


def _kill_tree(proc: subprocess.Popen) -> None:
    """The agent may have started its own processes (Python, LitMedia): stop them all."""
    if os.name == "nt":
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)], capture_output=True)
    else:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except OSError:
            pass
    try:
        proc.kill()
    except OSError:
        pass


def run_agent(cmd: List[str], timeout: float, cwd: Path) -> Tuple[Optional[int], str]:
    """(exit code, output); the exit code is None when the agent ran out of time and was stopped. Ctrl+C stops the
    agent too (and then the loop): no agent is ever left running on its own."""
    extra: Dict[str, Any] = {} if os.name == "nt" else {"start_new_session": True}
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                            text=True, encoding="utf-8", errors="replace", cwd=str(cwd), env=env, **extra)
    try:
        out, _ = proc.communicate(timeout=timeout)
        return proc.returncode, out or ""
    except KeyboardInterrupt:
        _kill_tree(proc)
        raise
    except subprocess.TimeoutExpired:
        _kill_tree(proc)
        try:
            out, _ = proc.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            out = ""
        return None, out or ""


def images_command() -> str:
    """This Python and tarots_images.py, absolute, with forward slashes and quotes only around a space: the same text
    works in cmd, PowerShell and bash, whichever shell the agent's tool uses."""
    def one(path: str) -> str:
        text = Path(path).as_posix()
        return f'"{text}"' if " " in text else text
    return f"{one(sys.executable)} {one(str(IMAGES))}"


def make_prompt(template: str, post: Dict[str, Any]) -> str:
    return template.format(id=post.get("id", ""), slug=post.get("slug") or "", title=post.get("titolo") or "",
                           images=images_command())


# ---- one article -------------------------------------------------------------------------------------------------


def do_article(post: Dict[str, Any], a, template: str, log: Path, before_credits: int) -> Dict[str, Any]:
    """Launch the agent for one article and check, without trusting what it says, whether the cover changed."""
    post_id = str(post["id"])
    started = _now()
    base = {"event": "article", "when": started, "id": post_id, "slug": post.get("slug"), "title": post.get("titolo")}
    try:
        before_cover = cover_of(post_id)
    except (LoopError, ValueError) as exc:  # the article cannot be read: no agent, a failure like any other
        entry = {**base, "outcome": "failed", "reason": f"cannot read the article before the agent: {exc}",
                 "seconds": 0, "agent_exit": None, "credits_before": before_credits, "credits_after": before_credits,
                 "spent": 0, "cover_before": None, "cover_after": None, "output": None}
        write_log(log, entry)
        print(f"\n→ {post.get('titolo')} ({post_id})\n  FAILED: {entry['reason']}", flush=True)
        return entry
    before_record = recorded_cover(post_id)
    prompt = make_prompt(template, post)
    cmd = agent_command(a.agent_cmd, prompt, post)
    t0 = time.monotonic()
    print(f"\n→ {post.get('titolo')} ({post_id}): agent started at {started[11:19]} UTC, at most {a.timeout:g} min",
          flush=True)
    code, output = run_agent(cmd, a.timeout * 60, a.cwd)
    seconds = round(time.monotonic() - t0, 1)
    outputs = log.parent / "loop-covers"
    outputs.mkdir(parents=True, exist_ok=True)
    out_file = outputs / f"{started[:19].replace(':', '').replace('-', '')}-{post.get('slug') or post_id}.txt"
    out_file.write_text(output, encoding="utf-8")
    try:
        after_cover = cover_of(post_id)
    except (LoopError, ValueError) as exc:
        after_cover, cover_error = None, str(exc)
    else:
        cover_error = ""
    after_record = recorded_cover(post_id)
    try:
        after_credits: Optional[int] = credits()
    except LoopError:
        after_credits = None
    changed = after_cover is not None and cover_key(after_cover) != cover_key(before_cover)
    recorded = after_record is not None and after_record != before_record
    if changed and recorded:
        outcome, reason = "ok", "cover replaced and recorded" + (f" (agent exit {code})" if code else "")
    elif code is None:
        outcome, reason = "failed", f"timeout after {a.timeout:g} min: the agent was stopped"
    elif cover_error:
        outcome, reason = "failed", f"cannot read the article after the agent: {cover_error}"
    elif not changed:
        outcome, reason = "failed", f"the cover on the site did not change (agent exit {code})"
    else:
        outcome, reason = "failed", ("the cover changed but tarots_images.py `cover` did not record it: not made with "
                                     "the skill's commands")
    entry = {
        **base, "outcome": outcome, "reason": reason, "seconds": seconds, "agent_exit": code,
        "credits_before": before_credits, "credits_after": after_credits,
        "spent": (before_credits - after_credits) if after_credits is not None else None,
        "cover_before": cover_key(before_cover), "cover_after": cover_key(after_cover),
        "output": str(out_file),
    }
    write_log(log, entry)
    print(f"  {outcome.upper()}: {reason}; {seconds:g}s, credits {before_credits} → {after_credits}", flush=True)
    return entry


# ---- the loop ----------------------------------------------------------------------------------------------------


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="redo_covers_loop.py", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help=f"articles in this run (default {DEFAULT_LIMIT})")
    p.add_argument("--budget", type=int, help="credits this run may spend: stop before an article that could pass it")
    p.add_argument("--reserve", type=int, default=0, help="credits that must stay on the LitMedia account")
    p.add_argument("--cost", type=int, default=ARTICLE_COST,
                   help=f"credits counted for the next article in --budget and --reserve (default {ARTICLE_COST}: a "
                        "cover and at most one new try)")
    p.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_MIN,
                   help=f"minutes per article before the agent is stopped (default {DEFAULT_TIMEOUT_MIN:g})")
    p.add_argument("--max-failures", type=int, default=MAX_FAILURES, help=f"failures in a row that stop the loop "
                                                                          f"(default {MAX_FAILURES})")
    p.add_argument("--status", choices=["draft", "published"], default="draft", help="which articles (default draft)")
    p.add_argument("--retry-failed", action="store_true", help="also the articles the log has as failed")
    p.add_argument("--agent-cmd", help="another agent: a command line with {prompt} (else appended), {id}, {slug}, "
                                       "{title}. Default: hermes -z {prompt} --skills tarots-blog-images")
    p.add_argument("--prompt-file", help="a prompt template ({id}, {slug}, {title}, {images}) instead of the default")
    p.add_argument("--log", default=str(LOG_PATH), help=f"the JSONL log (default {LOG_PATH})")
    p.add_argument("--cwd", default=str(HOME_DIR), help=f"the folder the agent runs in (default {HOME_DIR})")
    p.add_argument("--dry-run", action="store_true", help="print the list and the prompt of the first article; run nothing")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass
    a = parser().parse_args(argv)
    if a.limit < 1 or a.timeout <= 0 or a.max_failures < 1 or a.cost < 0 or (a.budget is not None and a.budget < 0):
        print("error: --limit, --timeout and --max-failures must be positive; --budget and --cost not negative",
              file=sys.stderr)
        return EXIT_USAGE
    try:
        return loop(a)
    except LoopError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exc.code
    except KeyboardInterrupt:
        print("\ninterrupted: the agent was stopped; the log has every article finished before", file=sys.stderr)
        return 130


def loop(a) -> int:
    log = Path(a.log).expanduser()
    a.cwd = Path(a.cwd).expanduser()
    template = DEFAULT_PROMPT
    if a.prompt_file:
        try:
            template = Path(a.prompt_file).read_text(encoding="utf-8")
        except OSError as exc:
            raise LoopError(f"cannot read --prompt-file: {exc}", EXIT_USAGE) from None
    last = outcomes(read_log(log))
    todo = articles_todo(a.status)
    done_before = [p for p in todo if last.get(str(p["id"])) == "ok"]
    failed_before = [p for p in todo if last.get(str(p["id"])) == "failed"]
    queue = [p for p in todo if last.get(str(p["id"])) != "ok"
             and (a.retry_failed or last.get(str(p["id"])) != "failed")]
    print(f"{len(todo)} article(s) with the cover still to redo ({a.status}); {len(queue)} in the queue"
          + (f", {len(failed_before)} failed before (skipped: --retry-failed to include them)"
             if failed_before and not a.retry_failed else "")
          + (f", {len(done_before)} done according to the log but still listed (skipped)" if done_before else ""))
    for n, p in enumerate(queue, 1):
        mark = "*" if n <= a.limit else " "
        print(f" {mark}{n:>3}. {p['id']}  {p.get('titolo')}")
    if a.dry_run:
        if queue:
            print(f"\n* = this run (--limit {a.limit}). Prompt of the first article:\n")
            print(make_prompt(template, queue[0]))
            try:
                cmd = agent_command(a.agent_cmd, "<prompt>", queue[0])
            except LoopError as exc:
                print(f"\nagent: {exc}")
            else:
                print("agent: " + subprocess.list2cmdline(cmd) + f"   (in {a.cwd}, at most {a.timeout:g} min)")
        print("\ndry run: nothing was launched")
        return EXIT_OK
    if not queue:
        print("nothing to do")
        return EXIT_OK
    a.cwd.mkdir(parents=True, exist_ok=True)
    agent_command(a.agent_cmd, "", queue[0])  # the agent exists, before spending anything
    first: Optional[int] = None
    current: Optional[int] = None
    done: List[str] = []
    failed: List[str] = []
    in_a_row = 0
    stop = "no article left"
    code = EXIT_OK
    for n, post in enumerate(queue):
        if n >= a.limit:
            stop = f"--limit {a.limit} reached"
            break
        try:
            current = credits()  # before every article: the budget is measured, not estimated
        except LoopError as exc:
            stop, code = f"the balance cannot be read ({exc}): nothing more is launched", EXIT_IMAGES
            break
        first = current if first is None else first
        spent = first - current
        if a.budget is not None and spent + a.cost > a.budget:
            stop = f"--budget {a.budget}: spent {spent}, the next article could cost {a.cost}"
            break
        if current - a.cost < a.reserve:
            stop = f"--reserve {a.reserve}: balance {current}, the next article could cost {a.cost}"
            break
        entry = do_article(post, a, template, log, current)
        if entry["credits_after"] is not None:
            current = entry["credits_after"]
        if entry["outcome"] == "ok":
            done.append(str(post["id"]))
            in_a_row = 0
        else:
            failed.append(str(post["id"]))
            in_a_row += 1
            if in_a_row >= a.max_failures:
                stop = f"{in_a_row} failures in a row: look at the log before running again"
                code = EXIT_FAILURES
                break
    spent_total = (first - current) if first is not None and current is not None else 0
    left = len(queue) - len(done) - len(failed)
    summary = {"event": "run", "when": _now(), "redone": len(done), "failed": len(failed), "spent": spent_total,
               "credits_left": current, "left_in_queue": left, "stop": stop}
    write_log(log, summary)
    print(f"\nSummary: redone {len(done)}, failed {len(failed)}, credits spent {spent_total}"
          + (f" (balance {current})" if current is not None else "") + f"; still to do {left}. Stopped: {stop}.")
    if failed:
        print(f"Failed: {', '.join(failed)} (reasons and agent output in {log})")
    if left and code == EXIT_OK:
        print("Run it again to go on from here.")
    return code


if __name__ == "__main__":
    sys.exit(main())
