"""Gli indirizzi IP non si conservano in chiaro (GDPR, Fase 1).

Dove serve ricordare «da dove» è arrivata un'azione — il registro (`audit_log`), i consensi (`user_consents`,
`consensi_storico`) — si tengono due cose, mai l'indirizzo intero:

- l'indirizzo **troncato**: IPv4 alla rete /24 (`93.44.12.0`), IPv6 alla /48 (`2001:db8:1::`). Dice ancora la zona e
  il fornitore di rete, quanto basta per capire un abuso o una provenienza strana, ma non indica più un singolo
  abbonato;
- l'**impronta** dell'indirizzo intero: HMAC-SHA256 con un segreto interno. Permette di dire «queste due azioni sono
  partite dallo stesso indirizzo» senza poterlo rileggere. Senza il segreto non si ricalcola nemmeno provando tutti
  gli IPv4.

**Il segreto** (v9, Fase 2c) non lo sceglie nessuno: al primo avvio dell'API se ne genera uno casuale, che si salva
**cifrato** nel database (`segreti_sistema`; la chiave master sta solo sul server, quindi il dump sul NAS porta testo
cifrato) e da lì si usa sempre (`configurazioni/segreti.py`). Se l'ambiente ne dà uno (`TAROT_IP_HASH_SECRET`), vince
quello e si copia nel database: toglierlo un giorno dall'ambiente non cambia le impronte. In console non si vede mai.

Un valore che non è un indirizzo (un proxy che scrive «unknown», un'intestazione malformata) non si conserva affatto:
né troncato né impronta.
"""
from __future__ import annotations

import hashlib
import hmac
import ipaddress
import secrets
from typing import Optional, Tuple

from ..settings import get_settings

#: Le reti a cui si tronca: /24 per IPv4, /48 per IPv6 (un'organizzazione o un sito, non una casa).
PREFISSO_IPV4 = 24
PREFISSO_IPV6 = 48

#: Solo prima che il segreto sia risolto (prove, strumenti che non scrivono IP) e senza ambiente: in un processo
#: dell'API il segreto vero c'è da prima della prima richiesta.
SEGRETO_SVILUPPO = "segreto-ip-di-sviluppo"

_segreto: Optional[str] = None
_generato_in_migrazione: Optional[str] = None


def imposta_segreto(valore: Optional[str]) -> None:
    """Il segreto di questo processo, risolto all'avvio dal database (`configurazioni/segreti.py`)."""
    global _segreto
    _segreto = valore or None


def segreto_corrente() -> str:
    """Quello risolto dal database; prima, quello dell'ambiente; senza nemmeno quello, il valore di sviluppo."""
    return _segreto or get_settings().ip_hash_secret or SEGRETO_SVILUPPO


def segreto_per_migrazione() -> str:
    """Il segreto con cui la migrazione GDPR protegge gli IP già salvati, quando la tabella dei segreti non esiste
    ancora: quello dell'ambiente se c'è, altrimenti uno casuale generato una volta per processo, che la migrazione
    della Fase 2c salva nel database (`generato_in_migrazione`). Mai il valore di sviluppo su dati veri."""
    global _generato_in_migrazione
    ambiente = get_settings().ip_hash_secret
    if ambiente:
        return ambiente
    if _generato_in_migrazione is None:
        _generato_in_migrazione = secrets.token_urlsafe(48)
    return _generato_in_migrazione


def generato_in_migrazione() -> Optional[str]:
    return _generato_in_migrazione


def _indirizzo(ip: Optional[str]) -> Optional[ipaddress._BaseAddress]:
    if not ip:
        return None
    testo = ip.strip()
    # «1.2.3.4:5678» e «[2001:db8::1]:443»: la porta non fa parte dell'indirizzo.
    if testo.startswith("[") and "]" in testo:
        testo = testo[1:testo.index("]")]
    elif testo.count(":") == 1 and "." in testo:
        testo = testo.split(":", 1)[0]
    testo = testo.split("%", 1)[0]  # l'indice di zona IPv6 («fe80::1%eth0»)
    try:
        indirizzo = ipaddress.ip_address(testo)
    except ValueError:
        return None
    # Un IPv4 scritto come IPv6 («::ffff:1.2.3.4») si tratta come IPv4: è lo stesso abbonato.
    if isinstance(indirizzo, ipaddress.IPv6Address) and indirizzo.ipv4_mapped is not None:
        return indirizzo.ipv4_mapped
    return indirizzo


def tronca(ip: Optional[str]) -> Optional[str]:
    """L'indirizzo ridotto alla sua rete (IPv4 /24, IPv6 /48), o None se non è un indirizzo."""
    indirizzo = _indirizzo(ip)
    if indirizzo is None:
        return None
    prefisso = PREFISSO_IPV4 if indirizzo.version == 4 else PREFISSO_IPV6
    return str(ipaddress.ip_network(f"{indirizzo}/{prefisso}", strict=False).network_address)


def impronta(ip: Optional[str], segreto: Optional[str] = None) -> Optional[str]:
    """L'HMAC-SHA256 (esadecimale, 64 caratteri) dell'indirizzo intero normalizzato, o None."""
    indirizzo = _indirizzo(ip)
    if indirizzo is None:
        return None
    chiave = (segreto if segreto is not None else segreto_corrente()).encode("utf-8")
    return hmac.new(chiave, str(indirizzo).encode("ascii"), hashlib.sha256).hexdigest()


def proteggi(ip: Optional[str], segreto: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
    """`(troncato, impronta)`: ciò che si scrive al posto dell'indirizzo."""
    return tronca(ip), impronta(ip, segreto)
