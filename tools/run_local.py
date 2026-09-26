#!/usr/bin/env python
"""Avvia in locale il backend (FastAPI, :8100) e il frontend (Next.js, :3000).

Prepara da solo ciò che manca — `backend/.venv` con un Python >= 3.11 e
`frontend/node_modules` —, trova un PostgreSQL raggiungibile, applica le
migrazioni e il seed (idempotente), poi lancia i due servizi con i log
affiancati, un prefisso per ciascuno. Ctrl+C ferma entrambi.

Senza Keycloak: il backend gira con TAROT_AUTH_DISABLED (ogni richiesta è
dell'utente di sviluppo, admin) e il frontend con NEXT_PUBLIC_AUTH_DISABLED.
Le risposte dei modelli sono quelle del modello finto, a meno di --llm-reale.

Database, in quest'ordine: --db, TAROT_DATABASE_URL, il valore di
backend/.env o il predefinito (localhost:5433, quello di docker-compose) e la
stessa URL sulla 5432 (PostgreSQL di sistema). Se nessuno risponde e Docker è
attivo parte il servizio `postgres` di docker-compose.

Esempi:
  python run_local.py
  python run_local.py --llm-reale              # il modello di backend/.env
  python run_local.py --db postgresql+psycopg://tarot:tarot@localhost:5432/tarot
  python run_local.py --solo-web               # il backend è già acceso
  python run_local.py --reinstalla             # rifà venv e node_modules
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
os.system("")  # abilita i colori ANSI nella console di Windows

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
VENV = BACKEND / ".venv"
WIN = sys.platform == "win32"
PY_VENV = VENV / ("Scripts/python.exe" if WIN else "bin/python")
# `asyncio.Runner`, che il backend usa per avviarsi su Windows, esiste dal 3.11.
MIN_PY = (3, 11)
DB_COMPOSE = "postgresql+psycopg://tarot:tarot@localhost:5433/tarot"

RESET = "\033[0m"
COLORI = {"avvio": "\033[33m", "api": "\033[36m", "web": "\033[35m"}
_stampa = threading.Lock()


def dice(tag: str, testo: str) -> None:
    with _stampa:
        print(f"{COLORI.get(tag, '')}[{tag}]{RESET} {testo}", flush=True)


def esci(testo: str) -> None:
    dice("avvio", testo)
    sys.exit(1)


def nascondi(url: str) -> str:
    return re.sub(r"(://[^:/@]+:)[^@]*@", r"\1***@", url)


def esegui(tag: str, cmd: list, cwd: Path, env: dict | None = None) -> None:
    cmd = [str(c) for c in cmd]
    dice(tag, "$ " + " ".join(cmd))
    if subprocess.run(cmd, cwd=cwd, env=env).returncode != 0:
        esci(f"Comando fallito: {' '.join(cmd)}")


# ---- Python e dipendenze --------------------------------------------------


def versione(exe: str):
    try:
        out = subprocess.run(
            [exe, "-c", "import sys; print(sys.version_info[0], sys.version_info[1])"],
            capture_output=True, text=True, timeout=30,
        ).stdout.split()
        return int(out[0]), int(out[1])
    except (OSError, subprocess.SubprocessError, ValueError, IndexError):
        return None


def trova_python() -> str:
    candidati = [sys.executable]
    if WIN:
        # `py -0p` elenca gli interpreti installati: " -V:3.12 *   C:\...\python.exe"
        try:
            out = subprocess.run(["py", "-0p"], capture_output=True, text=True, timeout=30).stdout
            candidati += re.findall(r"([A-Za-z]:\\.*python\.exe)\s*$", out, re.M)
        except (OSError, subprocess.SubprocessError):
            pass
    else:
        candidati += [p for n in ("python3.13", "python3.12", "python3.11") if (p := shutil.which(n))]
    for exe in candidati:
        v = versione(exe)
        if v and v >= MIN_PY:
            return exe
    esci(f"Serve Python {MIN_PY[0]}.{MIN_PY[1]} o più recente per il backend: non l'ho trovato.")


def prepara_venv(reinstalla: bool) -> None:
    if VENV.exists() and (reinstalla or not (versione(str(PY_VENV)) or (0, 0)) >= MIN_PY):
        dice("avvio", "Ricreo backend/.venv")
        shutil.rmtree(VENV)
    if not PY_VENV.exists():
        esegui("avvio", [trova_python(), "-m", "venv", VENV], BACKEND)
    richieste = BACKEND / "requirements.txt"
    firma = hashlib.sha256(richieste.read_bytes()).hexdigest()
    marcatore = VENV / ".dipendenze"
    if not marcatore.exists() or marcatore.read_text() != firma:
        esegui("avvio", [PY_VENV, "-m", "pip", "install", "-q", "-r", richieste.name], BACKEND)
        marcatore.write_text(firma)


def npm() -> str:
    exe = shutil.which("npm")
    if not exe:
        esci("npm non è nel PATH: installa Node.js.")
    return exe


def prepara_frontend(reinstalla: bool) -> None:
    if reinstalla or not (FRONTEND / "node_modules").exists():
        esegui("avvio", [npm(), "ci", "--no-audit", "--no-fund"], FRONTEND)


# ---- database -------------------------------------------------------------


def url_del_backend(env: dict) -> str:
    """La URL che il backend userebbe da solo, cioè con backend/.env."""
    r = subprocess.run(
        [str(PY_VENV), "-c", "from tarot_core.settings import get_settings; print(get_settings().database_url)"],
        cwd=BACKEND, env=env, capture_output=True, text=True,
    )
    if r.returncode != 0:
        esci("Non riesco a leggere le impostazioni del backend:\n" + r.stderr)
    return r.stdout.strip().splitlines()[-1]


def prova_connessione(url: str, env: dict):
    """None se il database risponde, altrimenti il motivo."""
    r = subprocess.run(
        [str(PY_VENV), "-c", "import sys, psycopg; psycopg.connect(sys.argv[1], connect_timeout=4).close()",
         url.replace("+psycopg", "", 1)],
        env=env, capture_output=True, text=True,
    )
    if r.returncode == 0:
        return None
    return (r.stderr.strip().splitlines() or ["errore sconosciuto"])[-1]


def docker_attivo() -> bool:
    return bool(shutil.which("docker")) and subprocess.run(
        ["docker", "info"], capture_output=True).returncode == 0


def scegli_database(esplicito: str | None, env: dict) -> str:
    base = esplicito or url_del_backend(env)
    candidati = [base]
    if not esplicito:
        altra = {"5433": "5432", "5432": "5433"}
        variante = re.sub(r":(5432|5433)/", lambda m: f":{altra[m.group(1)]}/", base, count=1)
        if variante != base:
            candidati.append(variante)
    motivi = []
    for url in candidati:
        motivo = prova_connessione(url, env)
        if motivo is None:
            dice("avvio", f"Database: {nascondi(url)}")
            return url
        motivi.append(f"  {nascondi(url)}\n    -> {motivo}")
    if not esplicito and docker_attivo():
        dice("avvio", "Nessun database raggiungibile: avvio quello di docker-compose")
        esegui("avvio", ["docker", "compose", "up", "-d", "--wait", "postgres"], ROOT)
        if prova_connessione(DB_COMPOSE, env) is None:
            return DB_COMPOSE
    esci(
        "Nessun database raggiungibile:\n" + "\n".join(motivi) + "\n\n"
        "Avvia Docker Desktop e rilancia, oppure prepara il PostgreSQL locale:\n"
        "  CREATE USER tarot WITH PASSWORD 'tarot' CREATEDB;  CREATE DATABASE tarot OWNER tarot;\n"
        "oppure indicane uno con --db postgresql+psycopg://utente:password@host:porta/nome"
    )


# ---- servizi --------------------------------------------------------------


def occupata(porta: int) -> bool:
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", porta)) == 0


class Servizio:
    def __init__(self, tag: str, cmd: list, cwd: Path, env: dict, porta: int):
        self.tag, self.porta = tag, porta
        self.proc = subprocess.Popen(
            [str(c) for c in cmd], cwd=cwd, env=env, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace", bufsize=1,
            # Un gruppo a parte: Ctrl+C non arriva ai figli, li ferma `ferma()`.
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if WIN else 0,
            start_new_session=not WIN,
        )
        threading.Thread(target=self._leggi, daemon=True).start()

    def _leggi(self) -> None:
        for riga in iter(self.proc.stdout.readline, ""):
            if riga.strip():
                dice(self.tag, riga.rstrip())

    @property
    def vivo(self) -> bool:
        return self.proc.poll() is None

    def ferma(self) -> None:
        if not self.vivo:
            return
        if WIN:
            subprocess.run(["taskkill", "/PID", str(self.proc.pid), "/T", "/F"], capture_output=True)
        else:
            os.killpg(self.proc.pid, signal.SIGTERM)
        try:
            self.proc.wait(10)
        except subprocess.TimeoutExpired:
            if not WIN:
                os.killpg(self.proc.pid, signal.SIGKILL)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", metavar="URL", help="URL SQLAlchemy del database (postgresql+psycopg://...)")
    ap.add_argument("--llm-reale", action="store_true", help="usa il modello di backend/.env invece di quello finto")
    ap.add_argument("--api-port", type=int, default=8100)
    ap.add_argument("--web-port", type=int, default=3000)
    ap.add_argument("--reinstalla", action="store_true", help="ricrea backend/.venv e frontend/node_modules")
    quale = ap.add_mutually_exclusive_group()
    quale.add_argument("--solo-api", action="store_true", help="solo il backend")
    quale.add_argument("--solo-web", action="store_true", help="solo il frontend")
    args = ap.parse_args()
    con_api, con_web = not args.solo_web, not args.solo_api

    for attivo, porta, nome in ((con_api, args.api_port, "il backend"), (con_web, args.web_port, "il frontend")):
        if attivo and occupata(porta):
            esci(f"La porta {porta} è già occupata: c'è già {nome} acceso? Cambiala con --api-port / --web-port.")

    api_url = f"http://localhost:{args.api_port}"
    web_url = f"http://localhost:{args.web_port}"
    servizi: list[Servizio] = []

    try:
        if con_api:
            prepara_venv(args.reinstalla)
            env = {
                **os.environ,
                "PYTHONUNBUFFERED": "1", "PYTHONIOENCODING": "utf-8",
                "TAROT_AUTH_DISABLED": "true",
                "TAROT_TRACING_ENABLED": "false",   # senza un collettore su :4318 sarebbero solo errori
                "TAROT_LLM_FINTO": "false" if args.llm_reale else "true",
                "TAROT_API_PUBLIC_URL": api_url,
                "TAROT_WEB_PUBLIC_URL": web_url,
                # Anche la console admin (`npm run dev` in admin/, :3001): senza, il browser blocca le sue chiamate.
                "TAROT_CORS_ORIGINS": f'["{web_url}", "http://127.0.0.1:{args.web_port}", "http://localhost:3001", "http://127.0.0.1:3001"]',
            }
            env["TAROT_DATABASE_URL"] = scegli_database(args.db or os.environ.get("TAROT_DATABASE_URL"), env)
            esegui("avvio", [PY_VENV, "-m", "alembic", "upgrade", "head"], BACKEND, env)
            esegui("avvio", [PY_VENV, "-m", "tarot_core.tools.seed"], BACKEND, env)
            servizi.append(Servizio("api", [PY_VENV, "-m", "tarot_core.api", "--port", args.api_port], BACKEND, env, args.api_port))

        if con_web:
            prepara_frontend(args.reinstalla)
            env = {
                **os.environ,
                "NEXT_PUBLIC_AUTH_DISABLED": "true",
                "NEXT_PUBLIC_API_URL": api_url,
                "NEXT_TELEMETRY_DISABLED": "1",
            }
            servizi.append(Servizio("web", [npm(), "run", "dev", "--", "-p", args.web_port], FRONTEND, env, args.web_port))

        in_attesa = list(servizi)
        while in_attesa:
            for s in list(in_attesa):
                if occupata(s.porta):
                    dice("avvio", f"{'API' if s.tag == 'api' else 'Sito'} pronto su "
                                  f"{api_url if s.tag == 'api' else web_url}")
                    in_attesa.remove(s)
            if any(not s.vivo for s in servizi):
                break
            time.sleep(0.5)
        else:
            dice("avvio", "Tutto acceso. Ctrl+C per fermare.")

        while all(s.vivo for s in servizi):
            time.sleep(0.5)
        morto = next(s for s in servizi if not s.vivo)
        dice("avvio", f"Il servizio «{morto.tag}» si è fermato (codice {morto.proc.returncode}): fermo anche gli altri.")
        return 1
    except KeyboardInterrupt:
        dice("avvio", "Fermo tutto…")
        return 0
    finally:
        for s in servizi:
            s.ferma()


if __name__ == "__main__":
    sys.exit(main())
