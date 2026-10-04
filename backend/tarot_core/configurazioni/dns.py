"""La sonda DNS della posta (v9, Fase 2c): SPF, DKIM e DMARC del dominio del mittente.

Tre record TXT nel DNS dicono ai servizi di posta (Gmail, Outlook…) se fidarsi delle email che dicono di venire da
`tarots.chat`:

- **SPF** (`v=spf1 …` sul dominio): quali server possono spedire per il dominio;
- **DKIM** (`<selettore>._domainkey.<dominio>`): la chiave pubblica con cui il server di posta firma ogni email;
- **DMARC** (`_dmarc.<dominio>`, `v=DMARC1; …`): cosa fare di un'email che non passa SPF e DKIM, e a chi riferirlo.

Senza DKIM e DMARC molte email finiscono nello spam. La sonda legge anche gli MX (dove arriva la posta in entrata:
per tarots.chat l'inoltro di Namecheap, `eforward*.registrar-servers.com`).

La lettura è una query DNS-over-HTTPS al resolver pubblico di Google (`dns.google`, gratis e senza account): niente
dipendenze nuove. Il risultato resta in memoria qualche minuto (la pagina «Account» lo mostra senza rifare la query).
Le prove sostituiscono la rete con `TRASPORTO`.
"""
from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, List, Optional, Tuple

import httpx

RESOLVER = "https://dns.google/resolve"
TIMEOUT = 5.0
#: Quanto vale in memoria l'ultimo controllo.
DURATA_CACHE = 600.0
#: I selettori DKIM più diffusi, provati quando la console non ne indica uno.
SELETTORI_COMUNI = ("default", "mail", "dkim", "stalwart", "s1", "s2", "selector1", "selector2", "google", "k1")
TIPI = {"TXT": 16, "MX": 15}

#: Le prove sostituiscono la rete con un `httpx.MockTransport` qui.
TRASPORTO: Optional[httpx.AsyncBaseTransport] = None

_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}


def dominio_di(mittente: str) -> str:
    """Il dominio dell'indirizzo del mittente (`noreply@tarots.chat` → `tarots.chat`), o `tarots.chat`."""
    if "@" in (mittente or ""):
        return mittente.rsplit("@", 1)[1].strip().lower().rstrip(".") or "tarots.chat"
    return "tarots.chat"


def _testo_txt(dato: str) -> str:
    """Un record TXT arriva fra virgolette e, se lungo, spezzato in più stringhe: `"v=DKIM1; k=rsa; " "p=MIIB…"`."""
    dato = dato.strip()
    if '"' not in dato:
        return dato
    pezzi, dentro, corrente = [], False, []
    i = 0
    while i < len(dato):
        c = dato[i]
        if c == "\\" and i + 1 < len(dato):
            corrente.append(dato[i + 1])
            i += 2
            continue
        if c == '"':
            if dentro:
                pezzi.append("".join(corrente))
                corrente = []
            dentro = not dentro
        elif dentro:
            corrente.append(c)
        i += 1
    return "".join(pezzi)


async def _interroga(client: httpx.AsyncClient, nome: str, tipo: str) -> List[str]:
    risposta = await client.get(RESOLVER, params={"name": nome, "type": tipo}, headers={"accept": "application/dns-json"})
    risposta.raise_for_status()
    dati = risposta.json()
    if dati.get("Status") not in (0, 3):  # 0 = trovato, 3 = il nome non esiste
        raise httpx.HTTPError(f"risposta DNS {dati.get('Status')}")
    valori = []
    for r in dati.get("Answer") or []:
        if r.get("type") != TIPI[tipo]:
            continue
        valore = str(r.get("data") or "")
        valori.append(_testo_txt(valore) if tipo == "TXT" else valore.rstrip("."))
    return valori


async def controlla(dominio: str, selettore: str = "", *, forza: bool = False) -> Dict[str, Any]:
    """SPF, DKIM, DMARC e MX del dominio: `{"spf": {"stato", "valore"}, "dkim": {…, "selettore"}, "dmarc": …, "mx": […]}`.
    Lo stato è `presente`, `assente` o `errore`. Non solleva."""
    chiave = f"{dominio}|{selettore}"
    if not forza and chiave in _cache and time.monotonic() - _cache[chiave][0] < DURATA_CACHE:
        return _cache[chiave][1]
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, transport=TRASPORTO) as client:
            txt, dmarc, mx = await asyncio.gather(
                _interroga(client, dominio, "TXT"),
                _interroga(client, f"_dmarc.{dominio}", "TXT"),
                _interroga(client, dominio, "MX"),
            )
            selettori = [selettore] if selettore else list(SELETTORI_COMUNI)
            dkim = await asyncio.gather(*(_interroga(client, f"{s}._domainkey.{dominio}", "TXT") for s in selettori))
    except (httpx.HTTPError, ValueError) as exc:
        esito = {"dominio": dominio, "errore": f"Il DNS non ha risposto ({type(exc).__name__}): riprova fra poco.",
                 "spf": {"stato": "errore"}, "dkim": {"stato": "errore"}, "dmarc": {"stato": "errore"}, "mx": []}
        return esito
    spf = next((v for v in txt if v.lower().startswith("v=spf1")), None)
    dm = next((v for v in dmarc if v.upper().startswith("V=DMARC1")), None)
    trovato = next(((s, v) for s, valori in zip(selettori, dkim) for v in valori if "p=" in v), None)
    esito = {
        "dominio": dominio,
        "spf": {"stato": "presente" if spf else "assente", "valore": spf},
        "dkim": {
            "stato": "presente" if trovato else "assente",
            "selettore": trovato[0] if trovato else (selettore or None),
            "valore": (trovato[1][:120] + "…") if trovato and len(trovato[1]) > 120 else (trovato[1] if trovato else None),
            "provati": selettori,
        },
        "dmarc": {"stato": "presente" if dm else "assente", "valore": dm},
        "mx": sorted(mx),
        "letto_il": time.time(),
    }
    _cache[chiave] = (time.monotonic(), esito)
    return esito


def ultimo(dominio: str, selettore: str = "") -> Optional[Dict[str, Any]]:
    """L'ultimo controllo ancora in memoria, senza interrogare nessuno (per la pagina «Account»)."""
    voce = _cache.get(f"{dominio}|{selettore}")
    return voce[1] if voce else None


def dimentica() -> None:
    _cache.clear()
