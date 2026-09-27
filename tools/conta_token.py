#!/usr/bin/env python
"""Quanti token consuma una lettura, e quanto costerebbe con un modello a pagamento.

Una lettura non è una chiamata al modello: è un'intervista (una domanda e il suo controllo, più la chiusura), una
interpretazione per posizione, il responso con la dottrina nel contesto, e il giudice che lo verifica. Ciascuna chiamata
rimanda il proprio prompt di sistema; alcune ripetono lo stesso prefisso in ogni lettura (il prompt cache dei fornitori
lo sconta).

Due passi:

1. Catturare i prompt veri, percorrendo letture intere con il modello finto (nessun modello, nessun costo):

       cd backend
       TAROT_TEST_DATABASE_URL=postgresql+psycopg://tarot:tarot@localhost:5432/tarot_test \\
       TAROT_CATTURA_PROMPT=../prompt_catturati.json \\
       ./.venv/Scripts/python.exe -m pytest tarot_core/tests/test_costo_token.py

2. Contare e stimare:

       python tools/conta_token.py prompt_catturati.json
       python tools/conta_token.py prompt_catturati.json --domande 4 --risposta-token 60 --stesa croce-celtica

**Cosa è misurato e cosa è stimato.** I token in ingresso sono contati sui prompt reali con il vocabolario `o200k_base`
di tiktoken: un ordine di grandezza corretto per i modelli a pagamento, che però usano altri vocabolari (Claude ne
produce di norma fino a un 20-30 % in più; il fattore `--vocabolario` lo applica). Le risposte del modello finto sono
più brevi di quelle vere, e i token in uscita sono quindi **stimati** da ciò che i prompt chiedono (2-3 frasi per carta,
350-650 parole per il responso), con i rapporti token/parola misurati su un campione parallelo in italiano, inglese e
ungherese. I prezzi sono ipotesi da sostituire con quelli del fornitore scelto.

Tiktoken scarica il vocabolario con `requests`: dove la catena dei certificati non si verifica, si scarica con curl (che
la verifica) nella cartella indicata da `TIKTOKEN_CACHE_DIR`, chiamandolo con lo SHA-1 dell'URL.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")

# ---- il vocabolario -----------------------------------------------------------------------------------------------

try:
    import tiktoken

    _ENC = tiktoken.get_encoding("o200k_base")

    def conta(testo: str) -> int:
        return len(_ENC.encode(testo))

    VOCABOLARIO = "o200k_base (tiktoken)"
except Exception as exc:  # noqa: BLE001
    print(f"! tiktoken non disponibile ({type(exc).__name__}): uso 1 token ogni 3,6 caratteri, molto approssimato", file=sys.stderr)

    def conta(testo: str) -> int:
        return round(len(testo) / 3.6)

    VOCABOLARIO = "approssimazione a caratteri"

# Un campione parallelo (stesso contenuto): dà i token per parola di ciascuna lingua, che serve per stimare le risposte.
CAMPIONE = {
    "it": "La carta ti invita a guardare con lucidità ciò che si muove nella tua situazione, senza fretta di concludere. "
          "È una forza da riconoscere e da orientare, non una sentenza. Fai un piccolo passo questa settimana e osserva "
          "come risponde la situazione, senza chiederle più di quanto può dare.",
    "en": "The card invites you to look clearly at what is moving in your situation, without rushing to conclude. "
          "It is a force to recognise and steer, not a sentence. Take one small step this week and observe how the "
          "situation responds, without asking of it more than it can give.",
    "hu": "A kártya arra hív, hogy tisztán lásd, mi mozog a helyzetedben, anélkül, hogy sietnél a következtetéssel. "
          "Ez egy felismerendő és irányítandó erő, nem ítélet. Tégy meg egy kis lépést ezen a héten, és figyeld meg, "
          "hogyan reagál a helyzet, anélkül, hogy többet kérnél tőle, mint amennyit adhat.",
}
TOKEN_PER_PAROLA = {lg: conta(t) / len(t.split()) for lg, t in CAMPIONE.items()}

# ---- i prezzi (ipotesi: dollari per milione di token) ------------------------------------------------------------------
# `cache` è il prezzo di lettura dal prompt cache in rapporto al prezzo d'ingresso; `cache_min` i token minimi di prefisso
# perché il fornitore lo metta in cache. Sostituire con i numeri del fornitore scelto.
PREZZI = {
    # Riferimenti riportati da comparatori di prezzi terzi a fine settembre 2026: da verificare sul listino del fornitore.
    "A Qwen3.7 Flash": dict(ingresso=0.03, uscita=0.13, cache=0.10, cache_min=1024),
    "B DeepSeek-V4": dict(ingresso=0.14, uscita=0.28, cache=0.02, cache_min=1024),
    "C Gemini 2.5 Flash-Lite": dict(ingresso=0.10, uscita=0.40, cache=0.25, cache_min=1024),
    "D GPT-5.6 Luna": dict(ingresso=0.20, uscita=1.20, cache=0.10, cache_min=1024),
    "E Claude Haiku 4.5": dict(ingresso=1.00, uscita=5.00, cache=0.10, cache_min=4096),
    "F fascia Sonnet": dict(ingresso=3.00, uscita=15.00, cache=0.10, cache_min=1024),
}


# ---- il modello di una lettura ---------------------------------------------------------------------------------------------


def chiamate(scenario: dict, o) -> list[dict]:
    """Le chiamate di una lettura. Per ciascuna: token del prompt di sistema (`stabile`, uguale fra letture), del
    messaggio (`variabile`), della risposta (`uscita`, stimata) e quante volte (`n`, in media)."""
    tpp = TOKEN_PER_PAROLA[scenario["lingua"]]
    per = defaultdict(list)
    for c in scenario["chiamate"]:
        per[c["compito"]].append(c)
    speciale = scenario["spread"].startswith(("compat", "coppia"))
    out: list[dict] = []

    def aggiungi(compito, stabile, variabile, uscita, uscita_max, n=1.0):
        out.append(dict(compito=compito, stabile=stabile, variabile=variabile, uscita=uscita, uscita_max=uscita_max, n=n))

    # Intervista: n domande, ciascuna con il suo controllo, e la chiusura col riassunto. Il colloquio cresce a ogni
    # giro (la domanda e la risposta di chi consulta), e si rimanda per intero.
    iv, val = per["intervista"], per["validazione"]
    stabile_iv, base = conta(iv[0]["sistema"]), conta(iv[0]["utente"])
    passo = max(conta(iv[1]["utente"]) - base, 0) + o.risposta_token if len(iv) > 1 else 30 + o.risposta_token
    stabile_val = conta(val[0]["sistema"])
    variabile_val = sum(conta(x["utente"]) for x in val) / len(val)
    domanda = round(28 * tpp) + 10                      # una domanda di ~28 parole, in un JSON
    for i in range(o.domande + o.rigenerazioni):
        aggiungi("intervista", stabile_iv, base + min(i, o.domande) * passo, domanda, 200)
        aggiungi("validazione", stabile_val, variabile_val, 15, 200)
    aggiungi("intervista", stabile_iv, base + o.domande * passo, round(60 * tpp) + 12, 600)   # la chiusura

    # Interpretazione: una per posizione, in streaming.
    for c in per["interpretazione"]:
        aggiungi("interpretazione", conta(c["sistema"]), conta(c["utente"]), round(o.parole_carta * tpp), 500)

    # Responso e giudice. Una quota di letture (`riscritture_attese`) fa riscrivere il responso: entrambe le chiamate
    # si ripetono, in media, 1 + quota volte.
    s, g = per["sintesi"][0], per["giudizio"][0]
    parole = o.parole_sintesi_speciale if speciale else o.parole_sintesi
    volte = 1 + o.riscritture_attese
    aggiungi("sintesi", conta(s["sistema"]), conta(s["utente"]), round(parole * tpp), 2200 if speciale else 1800, volte)
    # Il giudice legge il responso: quello del modello finto è più corto di quello vero, e lo si sostituisce.
    finto = len(g["utente"].split("Responso da verificare:")[-1].split())
    aggiungi("giudizio", conta(g["sistema"]), conta(g["utente"]) + round((parole - finto) * tpp), 15 + round(105 * o.riscritture_attese), 600, volte)
    return out


def totali(elenco: list[dict], v: float) -> dict:
    f = defaultdict(float)
    for c in elenco:
        f["chiamate"] += c["n"]
        f["stabile"] += c["n"] * c["stabile"] * v
        f["ingresso"] += c["n"] * (c["stabile"] + c["variabile"]) * v
        f["uscita"] += c["n"] * c["uscita"] * v
        f["uscita_max"] += c["n"] * c["uscita_max"]
    return f


def costo(elenco: list[dict], p: dict, v: float, *, con_cache: bool) -> float:
    """Dollari per lettura. Con la cache si sconta il prompt di sistema, ma solo dove è abbastanza lungo perché il
    fornitore lo metta in cache; si suppone traffico abbastanza continuo da trovarla calda."""
    ingresso = uscita = 0.0
    for c in elenco:
        stabile, variabile = c["stabile"] * v, c["variabile"] * v
        if con_cache and stabile >= p["cache_min"]:
            stabile *= p["cache"]
        ingresso += c["n"] * (stabile + variabile)
        uscita += c["n"] * c["uscita"] * v
    return (ingresso * p["ingresso"] + uscita * p["uscita"]) / 1_000_000


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("catturati", help="il JSON scritto da test_costo_token.py")
    ap.add_argument("--stesa", help="solo questa stesa (es. croce-celtica)")
    ap.add_argument("--lingua", help="solo questa lingua (it, en, hu)")
    ap.add_argument("--domande", type=int, default=3, help="domande dell'intervista (2-6, default 3)")
    ap.add_argument("--risposta-token", type=int, default=40, help="token di ogni risposta di chi consulta (default 40)")
    ap.add_argument("--rigenerazioni", type=int, default=0, help="domande scartate e rigenerate, per lettura (default 0)")
    ap.add_argument("--parole-carta", type=int, default=45, help="parole di un'interpretazione (default 45)")
    ap.add_argument("--parole-sintesi", type=int, default=500, help="parole del responso standard (350-650)")
    ap.add_argument("--parole-sintesi-speciale", type=int, default=600, help="parole del responso di coppia (450-750)")
    ap.add_argument("--riscritture-attese", type=float, default=0.05, help="quota di letture che il giudice fa riscrivere")
    ap.add_argument("--vocabolario", type=float, default=1.0, help="moltiplicatore dei token per il vocabolario del fornitore (Claude: ~1,2)")
    o = ap.parse_args()

    dati = json.load(open(o.catturati, encoding="utf-8"))
    print(f"Vocabolario di conteggio: {VOCABOLARIO}; moltiplicatore {o.vocabolario}")
    print("Token per parola (campione): " + ", ".join(f"{lg} {t:.2f}" for lg, t in TOKEN_PER_PAROLA.items()))
    print(f"Ipotesi: {o.domande} domande, risposte di {o.risposta_token} token, carta {o.parole_carta} parole, "
          f"responso {o.parole_sintesi}/{o.parole_sintesi_speciale} parole, {o.riscritture_attese:.0%} riscritture\n")

    v = o.vocabolario
    scelti = [(k, s) for k, s in dati.items() if (not o.stesa or s["spread"] == o.stesa) and (not o.lingua or s["lingua"] == o.lingua)]
    print(f"{'lettura':26} {'chiam.':>6} {'ingresso':>9} {'(fisso)':>8} {'uscita':>7} {'totale':>8}   costo per lettura in centesimi di $ (senza cache → cache calda)")
    riga_prezzi = list(PREZZI)
    for k, s in scelti:
        e = chiamate(s, o)
        t = totali(e, v)
        celle = []
        for nome in riga_prezzi:
            senza, con = costo(e, PREZZI[nome], v, con_cache=False) * 100, costo(e, PREZZI[nome], v, con_cache=True) * 100
            celle.append(f"{nome[0]} {senza:5.3f}→{con:5.3f}")
        print(f"{k:26} {t['chiamate']:6.0f} {t['ingresso']:9,.0f} {t['stabile']:8,.0f} {t['uscita']:7,.0f} {t['ingresso'] + t['uscita']:8,.0f}   " + "  ".join(celle))

    if len(scelti) == 1 or (o.stesa and o.lingua):
        k, s = scelti[0]
        print(f"\nDove vanno i token: {k}")
        per = defaultdict(lambda: defaultdict(float))
        for c in chiamate(s, o):
            n = c["n"]
            d = per[c["compito"]]
            d["chiamate"] += n
            d["fisso"] += c["stabile"] * n * v
            d["variabile"] += c["variabile"] * n * v
            d["uscita"] += c["uscita"] * n * v
        print(f"{'compito':16} {'chiam.':>6} {'sistema':>8} {'messaggio':>10} {'uscita':>7}")
        for compito, d in per.items():
            print(f"{compito:16} {d['chiamate']:6.0f} {d['fisso']:8,.0f} {d['variabile']:10,.0f} {d['uscita']:7,.0f}")
    print("\nLe cifre di ingresso sono contate sui prompt veri; l'uscita è stimata dai limiti che i prompt chiedono; "
          "i prezzi sono ipotesi.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
