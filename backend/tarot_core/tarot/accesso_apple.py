"""«Accedi con Apple» senza estensioni di Keycloak (v9, Fase 6): il segreto che scade, firmato e rinnovato da qui.

Keycloak 26.0 non ha un provider Apple: `apple` è un OpenID Connect generico (`auth/provider_sociali.py`). Il suo
`client_secret` però non è una stringa fissa: Apple vuole un **JWT ES256** firmato con la chiave «Sign in with Apple»
dell'account sviluppatore (il file `AuthKey_<KeyID>.p8`), con

- intestazione `alg = ES256`, `kid = Key ID`;
- `iss = Team ID`, `sub = Services ID` (il `client_id`), `aud = https://appleid.apple.com`;
- `iat` e `exp`, con `exp` al massimo **sei mesi** dopo (15 777 000 secondi).

Scaduto quello, l'accesso con Apple smette di funzionare per tutti. Invece di un'estensione di terzi dentro
Keycloak (codice altrui nell'immagine che custodisce gli account), lo firma il backend: la console tiene Team ID,
Key ID, Services ID e la chiave **cifrata** (`llm/cifratura.py`); il segreto si scrive nell'identity provider `apple`
di Keycloak via Admin API (`manage-identity-providers`, che l'account di servizio ha già) e il CronJob mensile
`tarots-apple-segreto` (`tools/apple_segreto.py`) lo rifirma quando mancano meno di `RINNOVA_ENTRO` giorni.

**Le app.** Android e iOS entrano passando da Keycloak nel browser di sistema (AppAuth con `kc_idp_hint=apple`):
per Apple è un accesso web come quello del sito, con lo **stesso Services ID**. Il Bundle ID dell'app servirebbe solo
con il pulsante nativo di iOS (AuthenticationServices), il cui token ha come destinatario il Bundle ID e andrebbe
scambiato con Keycloak: qui non si usa. Perché l'identificativo Apple della persona (`sub`) sia lo stesso nell'app e
sul sito, il Services ID va **raggruppato** sotto l'App ID dell'app («Primary App ID» nella sua configurazione).

**Il nome.** Apple manda nome e cognome solo al primo accesso, in un campo `user` del form_post, e l'OIDC generico di
Keycloak lo ignora: chi entra con Apple arriva senza nome. Il profilo del sito lo chiede con garbo (`nome_manca`).
"""
from __future__ import annotations

import base64
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.keycloak_admin import KeycloakAdmin, KeycloakAdminError
from ..auth.provider_sociali import (
    FLUSSO_DOPO_ACCESSO_ESTERNO, FLUSSO_UNIONE, PER_ALIAS, rappresentazione, stato,
)
from ..domain.accesso_nativo_models import ConfigAccessoApple
from ..domain.base import utcnow
from ..llm.cifratura import cifra, decifra

ALIAS = "apple"
AUD = "https://appleid.apple.com"
#: Quanto vale un segreto firmato qui: sei mesi meno un margine (Apple rifiuta oltre 15 777 000 secondi).
DURATA = timedelta(days=180)
#: Il CronJob mensile lo rinnova quando ne mancano meno di questi: con un giro al mese, almeno 45 giorni prima.
RINNOVA_ENTRO = timedelta(days=75)

#: Team ID e Key ID: dieci caratteri maiuscoli o cifre.
DIECI = re.compile(r"^[A-Z0-9]{10}$")
#: Il Services ID ha la forma di un identificativo DNS inverso (`chat.tarots.web`).
SERVICES_ID = re.compile(r"^[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+$")


class ErroreAccessoApple(ValueError):
    """Un valore che la console non può salvare, o una configurazione incompleta: il messaggio si mostra così com'è."""


# ---- il JWT -------------------------------------------------------------------------------------------------------


def _b64(dati: bytes) -> str:
    return base64.urlsafe_b64encode(dati).rstrip(b"=").decode("ascii")


def firma_segreto(
    *, team_id: str, key_id: str, services_id: str, chiave_pem: str, adesso: Optional[datetime] = None,
    durata: timedelta = DURATA,
) -> Tuple[str, datetime]:
    """Il `client_secret` per Apple e la sua scadenza."""
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

    adesso = adesso or datetime.now(timezone.utc)
    iat = int(adesso.timestamp())
    exp = iat + int(durata.total_seconds())
    intestazione = {"alg": "ES256", "kid": key_id, "typ": "JWT"}
    corpo = {"iss": team_id, "iat": iat, "exp": exp, "aud": AUD, "sub": services_id}
    da_firmare = (f"{_b64(json.dumps(intestazione, separators=(',', ':')).encode())}."
                  f"{_b64(json.dumps(corpo, separators=(',', ':')).encode())}")
    chiave = serialization.load_pem_private_key(chiave_pem.encode("utf-8"), password=None)
    # `cryptography` firma in DER; un JWS ES256 vuole r e s affiancati, 32 byte ciascuno (RFC 7518, 3.4).
    r, s = decode_dss_signature(chiave.sign(da_firmare.encode("ascii"), ec.ECDSA(hashes.SHA256())))
    return f"{da_firmare}.{_b64(r.to_bytes(32, 'big') + s.to_bytes(32, 'big'))}", datetime.fromtimestamp(exp, timezone.utc)


def valida_chiave(testo: str) -> str:
    """La chiave «Sign in with Apple»: una chiave privata EC P-256 in PEM (PKCS#8), come la scarica Apple."""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ec

    pem = (testo or "").strip()
    if "BEGIN PRIVATE KEY" not in pem:
        raise ErroreAccessoApple(
            "Il file non è una chiave .p8: in Apple Developer → Certificates, Identifiers & Profiles → Keys crea una "
            "chiave con «Sign in with Apple» e scarica il file AuthKey_XXXXXXXXXX.p8 (si scarica una volta sola).")
    try:
        chiave = serialization.load_pem_private_key(pem.encode("utf-8"), password=None)
    except Exception as exc:  # noqa: BLE001 — qualunque errore di lettura ha lo stesso rimedio
        raise ErroreAccessoApple("La chiave .p8 non si legge: carica il file così come l'hai scaricato.") from exc
    if not isinstance(chiave, ec.EllipticCurvePrivateKey) or chiave.curve.name != "secp256r1":
        raise ErroreAccessoApple("La chiave non è una chiave EC P-256: Apple usa solo chiavi .p8 di questo tipo.")
    return pem + "\n"


def _impronta(pem: str) -> Optional[str]:
    """Le prime 12 cifre esadecimali dello SHA-256 della chiave pubblica: per riconoscere la chiave, non per usarla."""
    try:
        from cryptography.hazmat.primitives import serialization

        chiave = serialization.load_pem_private_key(pem.encode("utf-8"), password=None)
        pubblica = chiave.public_key().public_bytes(
            serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    except Exception:  # noqa: BLE001 — illeggibile: «presente ma illeggibile», non un errore
        return None
    return hashlib.sha256(pubblica).hexdigest()[:12]


# ---- la configurazione --------------------------------------------------------------------------------------------


async def riga(session: AsyncSession) -> ConfigAccessoApple:
    r = await session.get(ConfigAccessoApple, 1)
    if r is None:
        r = ConfigAccessoApple(id=1, team_id="", key_id="", services_id="", esito={})
        session.add(r)
        await session.flush()
    return r


def completa(r: ConfigAccessoApple) -> bool:
    return bool(r.team_id and r.key_id and r.services_id and decifra(r.chiave_cifrata))


def da_rinnovare(r: ConfigAccessoApple, ora: Optional[datetime] = None) -> bool:
    """Il segreto in Keycloak scade entro `RINNOVA_ENTRO` (o non è mai stato scritto da qui)."""
    ora = ora or utcnow()
    return r.segreto_scade_il is None or r.segreto_scade_il - ora < RINNOVA_ENTRO


def vista(r: ConfigAccessoApple, *, team_id_app: str = "", ora: Optional[datetime] = None) -> Dict[str, Any]:
    """Per la console: mai la chiave, solo se c'è e la sua impronta. `team_id_app`: il Team ID già scritto in «App
    mobili → iOS», proposto se qui manca (è lo stesso account sviluppatore)."""
    ora = ora or utcnow()
    pem = decifra(r.chiave_cifrata)
    scade = r.segreto_scade_il
    return {
        "team_id": r.team_id,
        "team_id_suggerito": "" if r.team_id else team_id_app,
        "key_id": r.key_id,
        "services_id": r.services_id,
        "chiave": {"presente": bool(pem), "impronta": _impronta(pem) if pem else None,
                   # Cifrata con una chiave master diversa da quella di oggi: va ricaricata.
                   "illeggibile": bool(r.chiave_cifrata) and not pem},
        "completa": completa(r),
        "segreto": {
            "generato_il": r.segreto_generato_il.isoformat() if r.segreto_generato_il else None,
            "scade_il": scade.isoformat() if scade else None,
            "giorni_rimasti": max((scade - ora).days, 0) if scade else None,
            "scaduto": bool(scade and scade <= ora),
            "da_rinnovare": da_rinnovare(r, ora),
        },
        "esito": r.esito or {},
        "durata_giorni": DURATA.days,
        "rinnova_entro_giorni": RINNOVA_ENTRO.days,
    }


def aggiorna(r: ConfigAccessoApple, campi: Dict[str, Any], chiave_p8: Optional[str]) -> None:
    """I campi presenti. Vuoto è ammesso (non ancora noto), un formato sbagliato no. `chiave_p8`: `None` lascia
    quella di prima, vuota la toglie."""
    for nome, schema, messaggio in (
        ("team_id", DIECI, "Il Team ID ha 10 caratteri, maiuscole e cifre (developer.apple.com → Account → Membership)."),
        ("key_id", DIECI, "Il Key ID ha 10 caratteri, maiuscole e cifre (Apple Developer → Keys → la chiave)."),
        ("services_id", SERVICES_ID, "Il Services ID ha la forma «chat.tarots.web» (Apple Developer → Identifiers "
                                     "→ Services IDs)."),
    ):
        if campi.get(nome) is None:
            continue
        valore = str(campi[nome]).strip()
        if valore and not schema.match(valore):
            raise ErroreAccessoApple(messaggio)
        setattr(r, nome, valore)
    if chiave_p8 is not None:
        r.chiave_cifrata = cifra(valida_chiave(chiave_p8)) if chiave_p8.strip() else None


# ---- in Keycloak --------------------------------------------------------------------------------------------------


async def applica(
    session: AsyncSession, kc: KeycloakAdmin, *, abilitato: Optional[bool] = None, ora: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Firma un segreto nuovo e lo scrive nell'identity provider `apple` (creandolo se manca, con il Services ID
    come `client_id`). `abilitato`: acceso o spento; `None` lascia com'è (un provider nuovo nasce spento). Annota
    scadenza ed esito nella riga; un rifiuto di Keycloak si annota e poi si rilancia. Non fa il commit."""
    r = await riga(session)
    if not completa(r):
        raise ErroreAccessoApple("Per firmare il segreto servono Team ID, Key ID, Services ID e la chiave .p8.")
    ora = ora or utcnow()
    segreto, scade = firma_segreto(
        team_id=r.team_id, key_id=r.key_id, services_id=r.services_id, chiave_pem=decifra(r.chiave_cifrata),
        adesso=ora,
    )
    p = PER_ALIAS[ALIAS]
    avviso: Optional[str] = None
    try:
        esistente = await kc.leggi_provider(ALIAS)
        acceso = stato(p, esistente)["abilitato"] if abilitato is None else abilitato
        flussi = await kc.flussi()
        flusso_dopo = FLUSSO_DOPO_ACCESSO_ESTERNO if FLUSSO_DOPO_ACCESSO_ESTERNO in flussi else None
        # Apple garantisce l'email (anche quella «nascosta», che inoltra a quella vera): unione degli account.
        flusso_unione: Optional[str] = FLUSSO_UNIONE
        try:
            await kc.assicura_flusso_unione()
        except KeycloakAdminError as exc:
            flusso_unione, avviso = None, f"Unione automatica degli account non attiva: {exc}"
        await kc.salva_provider(
            rappresentazione(
                p, esistente, abilitato=acceso, client_id=r.services_id, client_secret=segreto,
                flusso_dopo=flusso_dopo, flusso_unione=flusso_unione,
            ),
            esiste=esistente is not None,
        )
    except KeycloakAdminError as exc:
        r.esito = {"ok": False, "messaggio": str(exc)[:300], "il": ora.isoformat()}
        raise
    r.segreto_generato_il, r.segreto_scade_il = ora, scade
    r.esito = {"ok": True, "messaggio": "Segreto scritto in Keycloak.", "il": ora.isoformat(),
               **({"avviso": avviso} if avviso else {})}
    return {"scade_il": scade.isoformat(), "abilitato": acceso, "avviso": avviso}
