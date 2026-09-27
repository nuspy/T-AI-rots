#!/usr/bin/env python
"""Banco di prova dei modelli sui prompt veri di una lettura: velocità, token, JSON valido, testo da rileggere.

Sceglie fra più modelli con i **numeri**, non con l'impressione: per ciascuno lancia i cinque compiti di una lettura
(intervista, validazione, interpretazione, sintesi, giudizio) con i prompt catturati da `tools/conta_token.py` e misura

- il **primo token** (quanto si aspetta prima che compaia qualcosa) e il tempo totale;
- i **token in uscita** e la velocità (token al secondo), separando quelli di ragionamento se il server li riporta;
- se il compito strutturato torna un **JSON leggibile** (intervista, validazione, giudizio);
- il motivo di chiusura (`length` con testo vuoto = il modello ha finito il budget ragionando).

Il testo generato si salva (`--salva`) per rileggerlo: la qualità non si misura con un numero, e una lettura in
italiano, inglese e ungherese va guardata con i propri occhi almeno una volta per ogni modello candidato.

**Uso** (la chiave sta nell'ambiente, mai nella riga di comando né in un file; il banco non la stampa):

    # PowerShell:  $env:NVIDIA_API_KEY = "nvapi-…"
    python tools/banco_modelli.py prompt_catturati.json --lettura croce-celtica/it \\
        --modelli nvidia/nemotron-nano-3-30b-a3b,nvidia/nemotron-3.5-lightning-30b-a3b,openai/gpt-oss-20b \\
        --salva banco_out

    # Spegnere il ragionamento **nella richiesta** (il modello caricato non ha interruttori), per un modello solo:
    python tools/banco_modelli.py prompt_catturati.json --modelli z-ai/glm-5.3-flash \\
        --parametri-modello 'z-ai/glm-5.3-flash={"chat_template_kwargs":{"enable_thinking":false}}'

Altri endpoint: `--url https://api.studio.nebius.com/v1 --chiave-env NEBIUS_API_KEY`, o LM Studio con
`--url http://100.110.144.5:1234/v1 --chiave-env NIENTE` (senza chiave). Il piano gratuito di NVIDIA ha un limite di
richieste al minuto: `--pausa` (secondi fra una chiamata e l'altra) e i tentativi con attesa su 429 lo rispettano.

I prompt catturati sono di una lettura finta (nessun dato vero). Per rigenerarli vedi la testata di `conta_token.py`.
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from tarot_core.llm.json_mode import estrai_json  # noqa: E402  (dopo il percorso)

#: (temperatura, tetto di token, atteso JSON) come nel codice dell'applicazione.
COMPITI: List[Tuple[str, float, int, bool]] = [
    ("intervista", 0.0, 200, True),
    ("validazione", 0.0, 200, True),
    ("interpretazione", 0.7, 500, False),
    ("sintesi", 0.75, 1800, False),
    ("giudizio", 0.0, 600, True),
]


def _parametri_modello(voci: List[str]) -> Dict[str, Dict[str, Any]]:
    fuori: Dict[str, Dict[str, Any]] = {}
    for voce in voci:
        modello, _, testo = voce.partition("=")
        if not testo:
            raise SystemExit(f"--parametri-modello vuole MODELLO=JSON, non «{voce}»")
        fuori[modello] = json.loads(testo)
    return fuori


def _prima_chiamata(chiamate: List[Dict[str, Any]], compito: str) -> Optional[Dict[str, Any]]:
    return next((c for c in chiamate if c["compito"] == compito), None)


def chiama(
    client: httpx.Client, url: str, chiave: Optional[str], modello: str, chiamata: Dict[str, Any],
    temperatura: float, tetto: int, json_atteso: bool, extra: Dict[str, Any], tentativi: int = 4,
) -> Dict[str, Any]:
    """Una chiamata in streaming; restituisce i numeri misurati. Non lancia: l'errore è un esito."""
    corpo: Dict[str, Any] = {
        "model": modello, "temperature": temperatura, "max_tokens": tetto, "stream": True,
        "stream_options": {"include_usage": True},
        "messages": [
            {"role": "system", "content": chiamata["sistema"]},
            {"role": "user", "content": chiamata["utente"]},
        ],
    }
    corpo.update(extra)
    intestazioni = {"Content-Type": "application/json"}
    if chiave:
        intestazioni["Authorization"] = f"Bearer {chiave}"

    for tentativo in range(1, tentativi + 1):
        t0 = time.perf_counter()
        primo: Optional[float] = None
        primo_testo: Optional[float] = None
        testo: List[str] = []
        pensiero = 0
        uso: Dict[str, Any] = {}
        chiusura = None
        try:
            with client.stream("POST", f"{url}/chat/completions", headers=intestazioni, json=corpo) as r:
                if r.status_code in (429, 500, 502, 503, 504):
                    attesa = float(r.headers.get("retry-after", 0) or 0) or min(60.0, 5.0 * 2 ** (tentativo - 1))
                    r.read()
                    if tentativo < tentativi:
                        print(f"      HTTP {r.status_code}: riprovo fra {attesa:.0f}s", file=sys.stderr)
                        time.sleep(attesa)
                        continue
                    return {"errore": f"HTTP {r.status_code}"}
                if r.status_code >= 400:
                    r.read()
                    return {"errore": f"HTTP {r.status_code}: {r.text[:200]}"}
                for riga in r.iter_lines():
                    if not riga.startswith("data:"):
                        continue
                    dati = riga[5:].strip()
                    if dati == "[DONE]":
                        break
                    try:
                        evento = json.loads(dati)
                    except json.JSONDecodeError:
                        continue
                    if evento.get("usage"):
                        uso = evento["usage"]
                    for scelta in evento.get("choices") or []:
                        delta = scelta.get("delta") or {}
                        pezzo_pensiero = delta.get("reasoning_content") or delta.get("reasoning")
                        if pezzo_pensiero:
                            pensiero += 1
                            primo = primo or time.perf_counter()
                        if delta.get("content"):
                            testo.append(delta["content"])
                            primo = primo or time.perf_counter()
                            primo_testo = primo_testo or time.perf_counter()
                        chiusura = scelta.get("finish_reason") or chiusura
        except httpx.HTTPError as exc:
            return {"errore": f"{type(exc).__name__}: {exc}"}

        fine = time.perf_counter()
        completo = "".join(testo)
        dettagli = uso.get("completion_tokens_details") or {}
        token_out = uso.get("completion_tokens")
        stimato = token_out is None
        if stimato:
            token_out = max(1, round(len(completo) / 3.6)) + pensiero
        json_ok = None
        if json_atteso:
            try:
                estrai_json(completo)
                json_ok = True
            except Exception:
                json_ok = False
        generazione = max(1e-6, fine - (primo or t0))
        return {
            "primo_token": (primo - t0) if primo else None,
            "primo_testo": (primo_testo - t0) if primo_testo else None,
            "totale": fine - t0,
            "token_in": uso.get("prompt_tokens"),
            "token_out": token_out,
            "token_ragionamento": dettagli.get("reasoning_tokens"),
            "pezzi_ragionamento": pensiero,
            "stimato": stimato,
            "vel": token_out / generazione,
            "chiusura": chiusura,
            "json_ok": json_ok,
            "parole": len(completo.split()),
            "testo": completo,
        }
    return {"errore": "tentativi esauriti"}


def _f(x: Optional[float], nd: int = 1) -> str:
    return "-" if x is None else f"{x:.{nd}f}"


def main() -> int:
    ap = argparse.ArgumentParser(prog="banco_modelli", description=__doc__.split("\n\n")[0])
    ap.add_argument("prompt", help="il file di prompt_catturati.json")
    ap.add_argument("--lettura", default="croce-celtica/it", help="quale lettura del file (default croce-celtica/it)")
    ap.add_argument("--modelli", required=True, help="identificativi separati da virgola")
    ap.add_argument("--url", default="https://integrate.api.nvidia.com/v1")
    ap.add_argument("--chiave-env", default="NVIDIA_API_KEY", help="nome della variabile d'ambiente con la chiave")
    ap.add_argument("--parametri", default="{}", help="JSON aggiunto a ogni richiesta (per tutti i modelli)")
    ap.add_argument("--parametri-modello", action="append", default=[], help="MODELLO=JSON, ripetibile")
    ap.add_argument("--pausa", type=float, default=3.0, help="secondi fra una chiamata e la successiva")
    ap.add_argument("--ripeti", type=int, default=1, help="quante volte per ogni compito (mediana dei tempi)")
    ap.add_argument("--salva", help="cartella dove scrivere il testo generato")
    ap.add_argument("--interpretazioni", type=int, default=10, help="interpretazioni per la stima di una lettura intera")
    args = ap.parse_args()

    letture = json.loads(Path(args.prompt).read_text(encoding="utf-8"))
    if args.lettura not in letture:
        raise SystemExit(f"lettura sconosciuta: {args.lettura}. Disponibili: {', '.join(letture)}")
    chiamate = letture[args.lettura]["chiamate"]
    chiave = os.environ.get(args.chiave_env)
    if not chiave and args.chiave_env not in ("NIENTE", ""):
        raise SystemExit(f"manca la chiave: imposta la variabile d'ambiente {args.chiave_env} (non la stampo mai)")
    globali = json.loads(args.parametri)
    per_modello = _parametri_modello(args.parametri_modello)
    modelli = [m.strip() for m in args.modelli.split(",") if m.strip()]
    cartella = Path(args.salva) if args.salva else None

    riepilogo: Dict[str, Dict[str, Any]] = {}
    with httpx.Client(timeout=httpx.Timeout(connect=20, read=180, write=30, pool=30)) as client:
        for modello in modelli:
            print(f"\n=== {modello}")
            print(f"{'compito':<16}{'1° token':>9}{'1° testo':>9}{'totale':>8}{'tok in':>8}{'tok out':>8}{'ragion.':>8}"
                  f"{'tok/s':>7}{'chiude':>8}{'json':>6}{'parole':>8}")
            extra = {**globali, **per_modello.get(modello, {})}
            tempi: Dict[str, float] = {}
            for compito, temperatura, tetto, json_atteso in COMPITI:
                c = _prima_chiamata(chiamate, compito)
                if c is None:
                    print(f"{compito:<16}  (nessuna chiamata catturata)")
                    continue
                prove = []
                for n in range(args.ripeti):
                    time.sleep(args.pausa if (n or tempi or riepilogo.get(modello)) else 0)
                    prove.append(chiama(client, args.url, chiave, modello, c, temperatura, tetto, json_atteso, extra))
                buone = [p for p in prove if "errore" not in p]
                if not buone:
                    print(f"{compito:<16}  ERRORE: {prove[-1]['errore']}")
                    riepilogo.setdefault(modello, {})[compito] = None
                    continue
                r = sorted(buone, key=lambda p: p["totale"])[len(buone) // 2]      # la mediana per durata
                tempi[compito] = r["totale"]
                marca = "~" if r["stimato"] else ""
                print(f"{compito:<16}{_f(r['primo_token']):>9}{_f(r['primo_testo']):>9}{_f(r['totale']):>8}"
                      f"{r['token_in'] if r['token_in'] is not None else '-':>8}{marca + str(r['token_out']):>8}"
                      f"{r['token_ragionamento'] if r['token_ragionamento'] is not None else (r['pezzi_ragionamento'] or '-'):>8}"
                      f"{_f(r['vel']):>7}{str(r['chiusura']):>8}"
                      f"{('sì' if r['json_ok'] else 'NO') if r['json_ok'] is not None else '-':>6}{r['parole']:>8}")
                if r["chiusura"] == "length" and not r["parole"]:
                    print("                  ^ nessun testo e chiusura per lunghezza: ha finito il budget ragionando")
                riepilogo.setdefault(modello, {})[compito] = r
                if cartella:
                    (cartella / modello.replace("/", "__")).mkdir(parents=True, exist_ok=True)
                    (cartella / modello.replace("/", "__") / f"{compito}.txt").write_text(r["testo"], encoding="utf-8")

    print("\n=== attesa stimata per una lettura intera (seriale; l'interpretazione a carta per carta si vede scorrere)")
    n_int = args.interpretazioni
    for modello, dati in riepilogo.items():
        t = {k: (v["totale"] if v else None) for k, v in dati.items()}
        if any(t.get(k) is None for k in ("intervista", "validazione", "interpretazione", "sintesi", "giudizio")):
            print(f"{modello:<44} dati incompleti")
            continue
        intervista = 3 * (t["intervista"] + t["validazione"])
        totale = intervista + n_int * t["interpretazione"] + t["sintesi"] + t["giudizio"]
        print(f"{modello:<44} intervista {intervista:5.0f}s + {n_int}×interpretazione {n_int * t['interpretazione']:5.0f}s"
              f" + sintesi {t['sintesi']:4.0f}s + giudizio {t['giudizio']:3.0f}s = {totale / 60:4.1f} min")
    print("\nIl testo generato è in", cartella if cartella else "(non salvato: usa --salva)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
