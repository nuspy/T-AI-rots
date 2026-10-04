"""Le app native dalla console «App mobili»: lettura, validazione e scrittura con audit, e la vista per le app.

Tre gruppi, come le tabelle di `app_mobili_models`:

- **la configurazione per piattaforma** (`android`, `ios`) e gli appunti di **Codemagic**: campi in chiaro, segreti
  cifrati (il JSON del service account per la Play Developer API, la chiave `.p8` della App Store Server API), appunti
  del profilo pagamenti. I segreti entrano e non escono: la vista per la console dice se ci sono e come riconoscerli
  (email del service account, impronta della chiave), mai il contenuto;
- **i prodotti degli store** collegati ai piani del sito;
- **la politica del pulsante Stripe** per piattaforma e paese, con `*` per «tutti gli altri» e, senza nessuna riga,
  «nascosto».

**Cosa esce verso le app** (`config_pubblica`, per `GET /app/config`): versione minima e ultima, se l'aggiornamento è
obbligatorio, il link alla scheda dello store, il pulsante Stripe per il paese chiesto e pochi flag. Mai i segreti,
mai gli appunti, mai gli ID degli account.

Gli appunti dei pagamenti seguono le regole di quelli di AdSense (`pubblicita_repositories`): del conto si tengono
solo le ultime 4 cifre, e un IBAN o un numero di carta interi si rifiutano anche nei testi liberi. La validazione è la
stessa, riusata da là.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..llm.cifratura import cifra, decifra
from ..settings import get_settings
from . import pubblicita_repositories as pubblicita
from .app_mobili_models import (
    MODALITA_STRIPE, PIATTAFORME, RIGHE_CONFIG, TIPI_PRODOTTO, ConfigAppMobile, PoliticaStripe, ProdottoStore,
)
from .billing_models import Plan
from .repositories import AuditRepository


class ErroreAppMobili(ValueError):
    """Un valore che la console non può salvare, con il messaggio da mostrare così com'è."""


# ---- formati ----------------------------------------------------------------------------------------------------

#: Il package name Android: almeno due segmenti, ognuno comincia con una lettera.
PACKAGE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*(\.[A-Za-z][A-Za-z0-9_]*)+$")
#: Il bundle ID iOS (notazione DNS inversa: lettere, cifre, trattini e punti).
BUNDLE = re.compile(r"^[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+$")
#: L'ID dell'account sviluppatore Google Play: le cifre nell'indirizzo di Play Console (`/developers/<id>`).
ID_SVILUPPATORE = re.compile(r"^\d{8,25}$")
#: Team ID, Key ID: dieci caratteri maiuscoli o cifre.
DIECI = re.compile(r"^[A-Z0-9]{10}$")
#: L'Apple ID dell'app (App Store Connect → Informazioni sull'app): un numero.
APPLE_APP_ID = re.compile(r"^\d{6,12}$")
ISSUER = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
#: Un topic Pub/Sub: `projects/<progetto>/topics/<nome>`.
TOPIC = re.compile(r"^projects/[a-z][a-z0-9-]{4,28}[a-z0-9]/topics/[A-Za-z][A-Za-z0-9_.~+%-]{2,254}$")
#: Una versione dell'app (`1`, `1.2`, `1.2.3`, `1.2.3.4`).
VERSIONE = re.compile(r"^\d{1,5}(\.\d{1,5}){0,3}$")
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
#: L'ID di un'app o di un team in Codemagic (nell'indirizzo della pagina dell'app).
ID_CODEMAGIC = re.compile(r"^[A-Za-z0-9_-]{4,64}$")
#: L'ID di un prodotto: Google vuole minuscole, cifre, `_` e `.` (comincia con lettera o cifra); Apple ammette anche
#: le maiuscole.
#: Su Google un abbonamento può avere il base plan dopo i due punti (`abbonamento:annuale`, Fase 4): l'ID del base
#: plan ha minuscole, cifre e trattini. Così lo stesso abbonamento di Play si collega a piani diversi per base plan.
PRODOTTO = {
    "android": re.compile(r"^[a-z0-9][a-z0-9._]{0,138}(:[a-z0-9][a-z0-9-]{0,62})?$"),
    "ios": re.compile(r"^[A-Za-z0-9][A-Za-z0-9._]{0,149}$"),
}
PAESE = re.compile(r"^[A-Z]{2}$")
#: Lo Spazio economico europeo (UE + Islanda, Liechtenstein, Norvegia): dove valgono il DMA e i programmi
#: di pagamento alternativo degli store.
SEE = frozenset(
    "AT BE BG CY CZ DE DK EE ES FI FR GR HR HU IE IT LT LU LV MT NL PL PT RO SE SI SK IS LI NO".split()
)

TIPI_ACCOUNT = ("personale", "organizzazione")
STATI_TEST_CHIUSO = ("non_iniziato", "in_corso", "completato", "non_richiesto")
AMBIENTI = ("sandbox", "production")
STATI_ACCORDI = ("non_firmati", "in_attesa", "attivi")

#: Gli endpoint delle notifiche degli store (Fase 4, `api/routers/billing_store.py`): l'indirizzo da incollare
#: negli store.
PERCORSO_RTDN = "/billing/store/google/rtdn"
PERCORSO_NOTIFICHE_APPLE = "/billing/store/apple/notifiche"


def parametri_predefiniti(piattaforma: str) -> Dict[str, Any]:
    if piattaforma == "android":
        return {
            #: La proposta del piano (Fase 7): lo stesso identificativo su Android e iOS.
            "package_name": "chat.tarots.app",
            "id_sviluppatore": "",
            "email_account": "",
            "tipo_account": "personale",
            #: Gli account personali nuovi devono fare un test chiuso (12 tester per 14 giorni) prima della produzione.
            "test_chiuso": "non_iniziato",
            "test_chiuso_dal": None,
            "pubsub_topic": "",
            #: Il push autenticato di Pub/Sub: l'audience del token OIDC e l'email del service account che lo firma.
            "rtdn_audience": "",
            "rtdn_email": "",
            "versione_minima": "",
            "versione_ultima": "",
            #: La commissione al 15% sul primo milione di dollari l'anno (va chiesta in Play Console, gruppo di account).
            "commissione_ridotta": False,
            #: Fase 10: le impronte SHA-256 dei certificati che firmano l'app (`AA:BB:…`), per `assetlinks.json`: la
            #: chiave di firma dell'app di Play (Play Console → Integrità dell'app) e quella di caricamento, più quella
            #: di debug per le prove. Senza, Android non verifica i collegamenti a tarots.chat e chiede con cosa aprirli.
            "impronte_sha256": [],
            "note": "",
        }
    if piattaforma == "ios":
        return {
            "bundle_id": "chat.tarots.app",
            "team_id": "",
            "apple_app_id": "",
            "email_account": "",
            "tipo_account": "personale",
            "key_id": "",
            "issuer_id": "",
            "ambiente": "sandbox",
            "versione_minima": "",
            "versione_ultima": "",
            #: L'app gira anche su iPad (decisione del piano): con `false` resterebbe solo per iPhone.
            "ipad": True,
            "accordi_paid_apps": "non_firmati",
            #: App Store Small Business Program: commissione al 15% sotto il milione di dollari l'anno (va chiesto).
            "small_business": False,
            "note": "",
        }
    return {
        "team": "",
        "app_id": "",
        "email_account": "",
        #: La chiave API di App Store Connect per la firma e il caricamento su TestFlight si carica **in Codemagic**
        #: (Team settings → Integrations → Developer Portal), non qui: qui solo se c'è e il suo Key ID.
        "chiave_asc_caricata": False,
        "chiave_asc_key_id": "",
        #: Il keystore di upload Android, caricato in Codemagic (Code signing identities); una copia fuori dal repo.
        "keystore_caricato": False,
        "note": "",
    }


def pagamenti_predefiniti() -> Dict[str, Any]:
    return {
        #: Google: l'ID del profilo pagamenti (12 cifre a gruppi di 4). Apple: vuoto, o il riferimento che si vuole.
        "id_profilo": "",
        "beneficiario": "",
        "tipo_profilo": "individuale",
        "paese": "",
        "valuta": "EUR",
        "banca": "",
        "conto_ultime4": "",
        "stato_fiscale": "non_inviate",
        "note": "",
    }


# ---- lettura ----------------------------------------------------------------------------------------------------


async def riga(session: AsyncSession, piattaforma: str) -> ConfigAppMobile:
    """La riga di una piattaforma (o di Codemagic), creata coi valori predefiniti se manca."""
    if piattaforma not in RIGHE_CONFIG:
        raise ErroreAppMobili(f"Piattaforma sconosciuta: {piattaforma}")
    r = await session.get(ConfigAppMobile, piattaforma)
    if r is None:
        r = ConfigAppMobile(
            piattaforma=piattaforma, parametri=parametri_predefiniti(piattaforma),
            appunti_pagamenti=pagamenti_predefiniti(), esito_verifica={},
        )
        session.add(r)
        await session.flush()
    return r


def parametri_di(r: Optional[ConfigAppMobile], piattaforma: str) -> Dict[str, Any]:
    """I parametri completi: quelli salvati sopra i predefiniti (una chiave nuova non rompe una riga vecchia)."""
    base = parametri_predefiniti(piattaforma)
    base.update({k: v for k, v in ((r.parametri if r else None) or {}).items() if k in base})
    return base


def pagamenti_di(r: Optional[ConfigAppMobile]) -> Dict[str, Any]:
    base = pagamenti_predefiniti()
    base.update({k: v for k, v in ((r.appunti_pagamenti if r else None) or {}).items() if k in base})
    return base


def segreti_di(r: Optional[ConfigAppMobile]) -> Dict[str, str]:
    """I segreti in chiaro, **solo per usarli** (la verifica, la Fase 4). Mai in una risposta."""
    if r is None or not r.segreti:
        return {}
    chiaro = decifra(r.segreti)
    if not chiaro:
        return {}
    try:
        dati = json.loads(chiaro)
    except ValueError:
        return {}
    return {k: str(v) for k, v in dati.items() if isinstance(v, str)} if isinstance(dati, dict) else {}


def _impronta_p8(pem: str) -> Optional[str]:
    """Le prime 12 cifre esadecimali dello SHA-256 della chiave pubblica: per riconoscere la chiave, non per usarla."""
    try:
        from cryptography.hazmat.primitives import serialization

        chiave = serialization.load_pem_private_key(pem.encode("utf-8"), password=None)
        pubblica = chiave.public_key().public_bytes(
            serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    except Exception:  # noqa: BLE001 — una chiave illeggibile si dice «presente ma illeggibile», non esplode
        return None
    return hashlib.sha256(pubblica).hexdigest()[:12]


def vista_segreti(r: Optional[ConfigAppMobile], piattaforma: str) -> Dict[str, Any]:
    """Cosa la console sa dei segreti: che ci sono e come riconoscerli."""
    s = segreti_di(r)
    if piattaforma == "android":
        info: Dict[str, Any] = {}
        if s.get("service_account"):
            try:
                info = json.loads(s["service_account"])
            except ValueError:
                info = {}
        return {"service_account": {
            "presente": bool(s.get("service_account")),
            "client_email": info.get("client_email"),
            "project_id": info.get("project_id"),
            "chiave_fine": str(info.get("private_key_id", ""))[-6:] or None,
        }}
    if piattaforma == "ios":
        return {"chiave_p8": {
            "presente": bool(s.get("chiave_p8")),
            "impronta": _impronta_p8(s["chiave_p8"]) if s.get("chiave_p8") else None,
        }}
    return {}


def url_api(percorso: str) -> str:
    return f"{get_settings().api_public_url.rstrip('/')}{percorso}"


def link_store(piattaforma: str, parametri: Dict[str, Any]) -> Optional[str]:
    """La scheda pubblica dell'app nello store (per l'aggiornamento obbligatorio), se si può già costruire."""
    if piattaforma == "android" and parametri.get("package_name"):
        return f"https://play.google.com/store/apps/details?id={parametri['package_name']}"
    if piattaforma == "ios" and parametri.get("apple_app_id"):
        return f"https://apps.apple.com/app/id{parametri['apple_app_id']}"
    return None


def vista(r: Optional[ConfigAppMobile], piattaforma: str) -> Dict[str, Any]:
    """Per la console: parametri, appunti, i segreti come «presente», gli indirizzi da copiare negli store."""
    parametri = parametri_di(r, piattaforma)
    risultato: Dict[str, Any] = {
        "piattaforma": piattaforma,
        "parametri": parametri,
        "segreti": vista_segreti(r, piattaforma),
        "verificato_il": r.verificato_il.isoformat() if r and r.verificato_il else None,
        "esito_verifica": (r.esito_verifica if r else {}) or {},
    }
    if piattaforma in PIATTAFORME:
        risultato["pagamenti"] = pagamenti_di(r)
        risultato["link_store"] = link_store(piattaforma, parametri)
        # Fase 4: l'ultima notifica arrivata dallo store (RTDN, Server Notifications V2): la prova che il
        # collegamento funziona.
        risultato["ultima_notifica"] = {
            "il": r.ultima_notifica_il.isoformat() if r and r.ultima_notifica_il else None,
            **((r.ultima_notifica if r else None) or {}),
        }
    if piattaforma == "android":
        risultato["url_rtdn"] = url_api(PERCORSO_RTDN)
        risultato["link_console"] = (
            f"https://play.google.com/console/u/0/developers/{parametri['id_sviluppatore']}/app-list"
            if parametri["id_sviluppatore"] else "https://play.google.com/console/"
        )
    elif piattaforma == "ios":
        risultato["url_notifiche"] = url_api(PERCORSO_NOTIFICHE_APPLE)
        risultato["link_console"] = (
            f"https://appstoreconnect.apple.com/apps/{parametri['apple_app_id']}"
            if parametri["apple_app_id"] else "https://appstoreconnect.apple.com/apps"
        )
    else:
        risultato["link_console"] = (
            f"https://codemagic.io/app/{parametri['app_id']}" if parametri["app_id"] else "https://codemagic.io/apps"
        )
    return risultato


# ---- scrittura: parametri, segreti, appunti ---------------------------------------------------------------------


def _testo(valore: Any, massimo: int) -> str:
    return str(valore or "").strip()[:massimo]


def _formato(valore: Any, schema: re.Pattern, messaggio: str, *, massimo: int = 300) -> str:
    """Il valore ripulito; vuoto è sempre ammesso (un campo non ancora noto), un formato sbagliato no."""
    testo = _testo(valore, massimo)
    if testo and not schema.match(testo):
        raise ErroreAppMobili(messaggio)
    return testo


def _scelta(valore: Any, ammessi: Tuple[str, ...], nome: str) -> str:
    if valore not in ammessi:
        raise ErroreAppMobili(f"{nome} sconosciuto: {valore}")
    return valore


def _senza_numeri_di_conto(campo: str, testo: str) -> str:
    """La stessa regola degli appunti di AdSense: niente IBAN o numeri di carta interi nei testi liberi."""
    try:
        return pubblicita._senza_numeri_di_conto(campo, testo)
    except pubblicita.ErrorePubblicita as exc:
        raise ErroreAppMobili(str(exc)) from exc


_MESSAGGI = {
    "package_name": (PACKAGE, "Il package name ha la forma «chat.tarots.app»: segmenti separati da punti, ognuno "
                              "comincia con una lettera. Non si cambia dopo la prima pubblicazione."),
    "bundle_id": (BUNDLE, "Il bundle ID ha la forma «chat.tarots.app» (lettere, cifre, trattini e punti)."),
    "id_sviluppatore": (ID_SVILUPPATORE, "L'ID dell'account sviluppatore è il numero nell'indirizzo di Play Console "
                                         "(…/developers/<numero>/…)."),
    "team_id": (DIECI, "Il Team ID ha 10 caratteri, maiuscole e cifre (developer.apple.com → Account → Membership)."),
    "key_id": (DIECI, "Il Key ID ha 10 caratteri, maiuscole e cifre (App Store Connect → Utenti e accesso → "
                      "Integrazioni → Acquisti in-app)."),
    "apple_app_id": (APPLE_APP_ID, "L'Apple ID dell'app è un numero (App Store Connect → l'app → Informazioni "
                                   "sull'app → Apple ID)."),
    "issuer_id": (ISSUER, "L'Issuer ID è un UUID (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx), in App Store Connect → "
                          "Utenti e accesso → Integrazioni."),
    "pubsub_topic": (TOPIC, "Il topic Pub/Sub ha la forma «projects/<progetto>/topics/<nome>»."),
    "versione_minima": (VERSIONE, "La versione ha la forma «1.2.3» (da uno a quattro numeri separati da punti)."),
    "versione_ultima": (VERSIONE, "La versione ha la forma «1.2.3» (da uno a quattro numeri separati da punti)."),
    "email_account": (EMAIL, "Indirizzo email non valido."),
    "rtdn_email": (EMAIL, "L'email del service account del push ha la forma «nome@progetto.iam.gserviceaccount.com»."),
    "app_id": (ID_CODEMAGIC, "L'ID dell'app in Codemagic è la parte finale dell'indirizzo della sua pagina."),
    "team": (re.compile(r"^.{1,120}$"), "Nome del team troppo lungo."),
    "chiave_asc_key_id": (DIECI, "Il Key ID ha 10 caratteri, maiuscole e cifre."),
}


#: Un'impronta SHA-256 di un certificato: 32 byte in esadecimale, con o senza i due punti (`keytool` e Play Console la
#: scrivono `AB:CD:…`, `signingReport` di Gradle anche così).
IMPRONTA = re.compile(r"^[0-9A-F]{64}$")
#: Quante impronte al massimo: chiave di firma di Play, chiave di caricamento, debug, e qualche avanzo.
MAX_IMPRONTE = 10


def impronte_sha256(valore: Any) -> List[str]:
    """Le impronte SHA-256 dei certificati di firma, nella forma di `assetlinks.json` (`AB:CD:…`, maiuscole). Si
    accetta un elenco o un testo con un'impronta per riga (anche separate da virgole); i doppioni si tolgono."""
    voci = valore if isinstance(valore, list) else re.split(r"[\s,;]+", str(valore or ""))
    risultato: List[str] = []
    for voce in voci:
        testo = re.sub(r"[\s:]", "", str(voce or "")).upper()
        if not testo:
            continue
        if testo.startswith("SHA256"):
            testo = testo[6:]
        if not IMPRONTA.match(testo):
            raise ErroreAppMobili(
                f"«{str(voce).strip()[:40]}» non è un'impronta SHA-256: sono 32 coppie di cifre esadecimali separate da "
                "due punti (Play Console → Test e rilascio → Configurazione → Integrità dell'app → Firma dell'app).")
        forma = ":".join(testo[i:i + 2] for i in range(0, 64, 2))
        if forma not in risultato:
            risultato.append(forma)
    if len(risultato) > MAX_IMPRONTE:
        raise ErroreAppMobili(f"Al massimo {MAX_IMPRONTE} impronte.")
    return risultato


def _valida_parametri(piattaforma: str, campi: Dict[str, Any], attuali: Dict[str, Any]) -> Dict[str, Any]:
    nuovi = copy.deepcopy(attuali)
    for chiave, valore in campi.items():
        if chiave not in nuovi or valore is None and chiave not in ("test_chiuso_dal",):
            continue
        if chiave in _MESSAGGI:
            schema, messaggio = _MESSAGGI[chiave]
            pulito = _formato(valore, schema, messaggio)
            nuovi[chiave] = pulito.lower() if chiave in ("email_account", "rtdn_email") else pulito
        elif chiave == "tipo_account":
            nuovi[chiave] = _scelta(valore, TIPI_ACCOUNT, "Tipo di account")
        elif chiave == "test_chiuso":
            nuovi[chiave] = _scelta(valore, STATI_TEST_CHIUSO, "Stato del test chiuso")
        elif chiave == "ambiente":
            nuovi[chiave] = _scelta(valore, AMBIENTI, "Ambiente")
        elif chiave == "accordi_paid_apps":
            nuovi[chiave] = _scelta(valore, STATI_ACCORDI, "Stato degli accordi")
        elif chiave == "test_chiuso_dal":
            nuovi[chiave] = valore or None
        elif chiave == "impronte_sha256":
            nuovi[chiave] = impronte_sha256(valore)
        elif isinstance(nuovi[chiave], bool):
            nuovi[chiave] = bool(valore)
        elif chiave == "rtdn_audience":
            nuovi[chiave] = _testo(valore, 300)
        elif chiave == "note":
            nuovi[chiave] = _senza_numeri_di_conto("Note", _testo(valore, 2000))
    if piattaforma in PIATTAFORME and nuovi["versione_minima"] and nuovi["versione_ultima"]:
        if versione(nuovi["versione_ultima"]) < versione(nuovi["versione_minima"]):
            raise ErroreAppMobili("L'ultima versione pubblicata non può essere più vecchia della versione minima.")
    return nuovi


def _valida_pagamenti(piattaforma: str, campi: Dict[str, Any], attuali: Dict[str, Any]) -> Dict[str, Any]:
    nuovi = copy.deepcopy(attuali)
    if campi.get("id_profilo") is not None:
        profilo = _testo(campi["id_profilo"], 40)
        if profilo and piattaforma == "android" and not pubblicita.ID_PROFILO.match(profilo):
            raise ErroreAppMobili(
                "L'ID del profilo pagamenti Google ha 12 cifre a gruppi di 4 (Play Console → Configurazione → "
                "Profilo pagamenti).")
        nuovi["id_profilo"] = _senza_numeri_di_conto("ID profilo", profilo) if piattaforma == "ios" else profilo
    for chiave, massimo, nome in (("beneficiario", 200, "Beneficiario"), ("banca", 120, "Banca"), ("note", 2000, "Note")):
        if campi.get(chiave) is not None:
            nuovi[chiave] = _senza_numeri_di_conto(nome, _testo(campi[chiave], massimo))
    if campi.get("conto_ultime4") is not None:
        ultime = re.sub(r"[\s-]", "", str(campi["conto_ultime4"]))
        if ultime and not pubblicita.ULTIME_4.match(ultime):
            raise ErroreAppMobili(
                "Del conto si tengono solo le ultime 4 cifre: un IBAN o un numero di conto interi non si salvano qui.")
        nuovi["conto_ultime4"] = ultime.upper()
    if campi.get("tipo_profilo") is not None:
        nuovi["tipo_profilo"] = _scelta(campi["tipo_profilo"], pubblicita.TIPI_PROFILO, "Tipo di profilo")
    if campi.get("stato_fiscale") is not None:
        nuovi["stato_fiscale"] = _scelta(campi["stato_fiscale"], pubblicita.STATI_FISCALI, "Stato fiscale")
    if campi.get("paese") is not None:
        paese = _testo(campi["paese"], 2).upper()
        if paese and not PAESE.match(paese):
            raise ErroreAppMobili("Il paese è un codice di due lettere (IT, US…).")
        nuovi["paese"] = paese
    if campi.get("valuta") is not None:
        valuta = _testo(campi["valuta"], 3).upper()
        if not pubblicita.VALUTA.match(valuta):
            raise ErroreAppMobili("La valuta è un codice di tre lettere (EUR, USD, GBP…).")
        nuovi["valuta"] = valuta
    return nuovi


def valida_service_account(testo: str) -> Dict[str, Any]:
    """Il JSON del service account per la Play Developer API: lo stesso controllo di quello di Search Console."""
    from ..tarot import google

    try:
        return google.leggi_service_account(testo)
    except google.ErroreGoogle as exc:
        raise ErroreAppMobili(str(exc)) from exc


def valida_p8(testo: str) -> str:
    """La chiave `.p8` della App Store Server API: una chiave privata EC P-256 in PEM (PKCS#8)."""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ec

    pem = (testo or "").strip()
    if "BEGIN PRIVATE KEY" not in pem:
        raise ErroreAppMobili(
            "Il file non è una chiave .p8: in App Store Connect → Utenti e accesso → Integrazioni → Acquisti in-app "
            "genera una chiave e scarica il file AuthKey_XXXXXXXXXX.p8 (si scarica una volta sola).")
    try:
        chiave = serialization.load_pem_private_key(pem.encode("utf-8"), password=None)
    except Exception as exc:  # noqa: BLE001 — qualunque errore di lettura ha lo stesso rimedio
        raise ErroreAppMobili("La chiave .p8 non si legge: carica il file così come l'hai scaricato.") from exc
    if not isinstance(chiave, ec.EllipticCurvePrivateKey) or chiave.curve.name != "secp256r1":
        raise ErroreAppMobili("La chiave non è una chiave EC P-256: la App Store Server API usa solo chiavi .p8 di Apple.")
    return pem + "\n"


def _per_audit(v: Dict[str, Any]) -> Dict[str, Any]:
    """La vista senza nulla che riconosca i segreti oltre a «presente»."""
    return {"parametri": v["parametri"], "pagamenti": v.get("pagamenti"),
            "segreti": {k: bool(s.get("presente")) for k, s in v["segreti"].items()}}


async def aggiorna(
    session: AsyncSession, piattaforma: str, *, parametri: Optional[Dict[str, Any]] = None,
    segreto: Optional[str] = None, pagamenti: Optional[Dict[str, Any]] = None, attore_id: Optional[int],
    ip: Optional[str] = None,
) -> ConfigAppMobile:
    """Aggiorna i campi presenti. `segreto`: `None` lo lascia com'è, una stringa vuota lo toglie, altrimenti è il
    contenuto del file (il JSON del service account per Android, la chiave .p8 per iOS)."""
    r = await riga(session, piattaforma)
    prima = vista(r, piattaforma)

    if parametri:
        r.parametri = _valida_parametri(piattaforma, parametri, parametri_di(r, piattaforma))
    if pagamenti and piattaforma in PIATTAFORME:
        r.appunti_pagamenti = _valida_pagamenti(piattaforma, pagamenti, pagamenti_di(r))
    if segreto is not None and piattaforma in PIATTAFORME:
        nome = "service_account" if piattaforma == "android" else "chiave_p8"
        attuali = segreti_di(r)
        if segreto.strip():
            attuali[nome] = (json.dumps(valida_service_account(segreto)) if piattaforma == "android"
                             else valida_p8(segreto))
        else:
            attuali.pop(nome, None)
        r.segreti = cifra(json.dumps(attuali)) if attuali else None
        # Credenziali nuove: la verifica di prima parlava di un'altra chiave.
        r.verificato_il = None
        r.esito_verifica = {}
    r.updated_by = attore_id

    dopo = vista(r, piattaforma)
    if _per_audit(prima) != _per_audit(dopo) or segreto is not None:
        await AuditRepository(session).record(
            action=f"app_mobili.{piattaforma}", actor_id=attore_id, target_type="config_app_mobili",
            target_id=piattaforma, before=_per_audit(prima),
            after={**_per_audit(dopo), **({"segreto": "cambiato" if segreto else "tolto"} if segreto is not None else {})},
            ip=ip,
        )
    return r


async def salva_esito(session: AsyncSession, piattaforma: str, esito: Dict[str, Any]) -> ConfigAppMobile:
    from .base import utcnow

    r = await riga(session, piattaforma)
    r.verificato_il = utcnow()
    r.esito_verifica = esito
    return r


# ---- prodotti degli store ---------------------------------------------------------------------------------------


def prodotto_json(p: ProdottoStore, piano: Optional[Plan] = None) -> Dict[str, Any]:
    return {
        "id": p.id, "piattaforma": p.piattaforma, "product_id": p.product_id, "plan_id": p.plan_id,
        "piano": ({"slug": piano.slug, "nome": piano.name, "tipo": piano.tipo, "attivo": piano.active}
                  if piano else None),
        "tipo": p.tipo, "annuale": bool(p.annuale), "prova": bool(p.prova), "attivo": p.attivo, "note": p.note,
    }


def _intervallo(piano: Plan, tipo: str, annuale: Any, prova: Any) -> Tuple[bool, bool]:
    """(annuale, prova) di un prodotto (Fase 4): solo un abbonamento li ha; il prodotto «prova» è sempre l'annuale."""
    if tipo != "abbonamento":
        return False, False
    annuale, prova = bool(annuale), bool(prova)
    if prova:
        annuale = True
    if annuale and not piano.price_yearly:
        raise ErroreAppMobili(f"Il piano «{piano.name}» non ha il prezzo annuale: il prodotto annuale non gli corrisponde.")
    return annuale, prova


async def prodotti(session: AsyncSession) -> List[Dict[str, Any]]:
    righe = (await session.execute(
        select(ProdottoStore, Plan).join(Plan, Plan.id == ProdottoStore.plan_id)
        .order_by(ProdottoStore.piattaforma, Plan.rank, ProdottoStore.product_id)
    )).all()
    return [prodotto_json(p, piano) for p, piano in righe]


def _tipo_per_piano(piano: Plan) -> str:
    return "consumabile" if piano.tipo == "pacchetto" else "abbonamento"


def gratuito(piano: Plan) -> bool:
    return not (piano.price_monthly or piano.price_yearly)


async def _piano(session: AsyncSession, plan_id: int) -> Plan:
    piano = await session.get(Plan, plan_id)
    if piano is None:
        raise ErroreAppMobili("Piano inesistente.")
    if gratuito(piano):
        raise ErroreAppMobili(f"Il piano «{piano.name}» è gratuito: negli store si vendono solo piani a pagamento.")
    return piano


async def crea_prodotto(
    session: AsyncSession, dati: Dict[str, Any], *, attore_id: Optional[int], ip: Optional[str] = None,
) -> ProdottoStore:
    piattaforma = _scelta(dati.get("piattaforma"), PIATTAFORME, "Piattaforma")
    product_id = _testo(dati.get("product_id"), 150)
    if not PRODOTTO[piattaforma].match(product_id):
        raise ErroreAppMobili(
            "L'ID del prodotto va copiato dallo store: su Google minuscole, cifre, «_» e «.» (per un abbonamento, "
            "volendo, «:» e l'ID del base plan); su Apple anche le maiuscole. Comincia con una lettera o una cifra.")
    piano = await _piano(session, int(dati["plan_id"]))
    tipo = dati.get("tipo") or _tipo_per_piano(piano)
    _scelta(tipo, TIPI_PRODOTTO, "Tipo di prodotto")
    if tipo != _tipo_per_piano(piano):
        raise ErroreAppMobili(
            f"Il piano «{piano.name}» è un {piano.tipo}: nello store va creato come prodotto "
            f"«{_tipo_per_piano(piano)}».")
    esistente = (await session.execute(select(ProdottoStore).where(
        ProdottoStore.piattaforma == piattaforma, ProdottoStore.product_id == product_id))).scalar_one_or_none()
    if esistente is not None:
        raise ErroreAppMobili(f"Il prodotto «{product_id}» su {piattaforma} c'è già: un ID prodotto vale una volta sola.")
    if ":" in product_id and tipo != "abbonamento":
        raise ErroreAppMobili("Il base plan («:…») esiste solo per gli abbonamenti di Google Play.")
    annuale, prova = _intervallo(piano, tipo, dati.get("annuale"), dati.get("prova"))
    p = ProdottoStore(
        piattaforma=piattaforma, product_id=product_id, plan_id=piano.id, tipo=tipo, annuale=annuale, prova=prova,
        attivo=bool(dati.get("attivo", True)), note=_testo(dati.get("note"), 500), updated_by=attore_id,
    )
    session.add(p)
    try:
        await session.flush()
    except IntegrityError as exc:  # due richieste insieme: il vincolo unico decide
        raise ErroreAppMobili(f"Il prodotto «{product_id}» su {piattaforma} c'è già.") from exc
    await AuditRepository(session).record(
        action="app_mobili.prodotto.crea", actor_id=attore_id, target_type="prodotti_store", target_id=str(p.id),
        after=prodotto_json(p), ip=ip,
    )
    return p


async def modifica_prodotto(
    session: AsyncSession, prodotto_id: int, dati: Dict[str, Any], *, attore_id: Optional[int], ip: Optional[str] = None,
) -> ProdottoStore:
    """Si cambiano piano, stato e note; l'ID del prodotto e la piattaforma no (sono quelli dello store)."""
    p = await session.get(ProdottoStore, prodotto_id)
    if p is None:
        raise LookupError("Prodotto non trovato")
    prima = prodotto_json(p)
    if dati.get("plan_id") is not None:
        piano = await _piano(session, int(dati["plan_id"]))
        if _tipo_per_piano(piano) != p.tipo:
            raise ErroreAppMobili(
                f"Il prodotto è «{p.tipo}» nello store: il piano «{piano.name}» ({piano.tipo}) non gli corrisponde.")
        p.plan_id = piano.id
    if dati.get("annuale") is not None or dati.get("prova") is not None or dati.get("plan_id") is not None:
        piano = await _piano(session, p.plan_id)
        p.annuale, p.prova = _intervallo(
            piano, p.tipo, p.annuale if dati.get("annuale") is None else dati["annuale"],
            p.prova if dati.get("prova") is None else dati["prova"],
        )
    if dati.get("attivo") is not None:
        p.attivo = bool(dati["attivo"])
    if dati.get("note") is not None:
        p.note = _testo(dati["note"], 500)
    p.updated_by = attore_id
    dopo = prodotto_json(p)
    if prima != dopo:
        await AuditRepository(session).record(
            action="app_mobili.prodotto.modifica", actor_id=attore_id, target_type="prodotti_store",
            target_id=str(p.id), before=prima, after=dopo, ip=ip,
        )
    return p


async def elimina_prodotto(
    session: AsyncSession, prodotto_id: int, *, attore_id: Optional[int], ip: Optional[str] = None,
) -> None:
    p = await session.get(ProdottoStore, prodotto_id)
    if p is None:
        raise LookupError("Prodotto non trovato")
    await AuditRepository(session).record(
        action="app_mobili.prodotto.elimina", actor_id=attore_id, target_type="prodotti_store", target_id=str(p.id),
        before=prodotto_json(p), ip=ip,
    )
    await session.delete(p)


# ---- il pulsante Stripe -----------------------------------------------------------------------------------------


def politica_json(p: PoliticaStripe) -> Dict[str, Any]:
    return {"id": p.id, "piattaforma": p.piattaforma, "paese": p.paese, "modalita": p.modalita, "avviso": p.avviso}


async def politiche(session: AsyncSession) -> List[Dict[str, Any]]:
    righe = (await session.execute(
        select(PoliticaStripe).order_by(PoliticaStripe.piattaforma, PoliticaStripe.paese != "*", PoliticaStripe.paese)
    )).scalars().all()
    return [politica_json(p) for p in righe]


def _paese(valore: Any) -> str:
    paese = _testo(valore, 2).upper()
    if paese != "*" and not PAESE.match(paese):
        raise ErroreAppMobili("Il paese è un codice ISO di due lettere (IT, US…) o «*» per tutti gli altri.")
    return paese


async def imposta_politica(
    session: AsyncSession, dati: Dict[str, Any], *, attore_id: Optional[int], ip: Optional[str] = None,
) -> PoliticaStripe:
    """Crea o aggiorna la regola di (piattaforma, paese)."""
    piattaforma = _scelta(dati.get("piattaforma"), PIATTAFORME, "Piattaforma")
    paese = _paese(dati.get("paese"))
    modalita = _scelta(dati.get("modalita"), MODALITA_STRIPE, "Modalità")
    if modalita == "entitlement_ue" and paese not in SEE:
        raise ErroreAppMobili(
            "«Entitlement UE» vale solo per un paese dello Spazio economico europeo (UE, Islanda, Liechtenstein, "
            "Norvegia): scegli il paese, non «*».")
    if modalita == "scelta_utente" and piattaforma != "android":
        raise ErroreAppMobili("La scelta dell'utente fra store e Stripe esiste solo su Google Play (User Choice Billing).")
    avviso = _testo(dati.get("avviso"), 500)
    p = (await session.execute(select(PoliticaStripe).where(
        PoliticaStripe.piattaforma == piattaforma, PoliticaStripe.paese == paese))).scalar_one_or_none()
    prima = politica_json(p) if p else None
    if p is None:
        p = PoliticaStripe(piattaforma=piattaforma, paese=paese)
        session.add(p)
    p.modalita, p.avviso, p.updated_by = modalita, avviso, attore_id
    await session.flush()
    await AuditRepository(session).record(
        action="app_mobili.politica_stripe", actor_id=attore_id, target_type="politica_stripe", target_id=str(p.id),
        before=prima, after=politica_json(p), ip=ip,
    )
    return p


async def elimina_politica(
    session: AsyncSession, politica_id: int, *, attore_id: Optional[int], ip: Optional[str] = None,
) -> None:
    p = await session.get(PoliticaStripe, politica_id)
    if p is None:
        raise LookupError("Regola non trovata")
    await AuditRepository(session).record(
        action="app_mobili.politica_stripe.elimina", actor_id=attore_id, target_type="politica_stripe",
        target_id=str(p.id), before=politica_json(p), ip=ip,
    )
    await session.delete(p)


async def risolvi_politica(session: AsyncSession, piattaforma: str, paese: Optional[str]) -> Dict[str, Any]:
    """La regola che vale per (piattaforma, paese): quella del paese, poi `*`, poi «nascosto»."""
    paese = (paese or "").strip().upper()
    righe = {p.paese: p for p in (await session.execute(select(PoliticaStripe).where(
        PoliticaStripe.piattaforma == piattaforma,
        PoliticaStripe.paese.in_([paese, "*"] if PAESE.match(paese) else ["*"]),
    ))).scalars()}
    regola = righe.get(paese) or righe.get("*")
    if regola is None:
        return {"modalita": "nascosto", "avviso": "", "regola": None}
    return {"modalita": regola.modalita, "avviso": regola.avviso, "regola": regola.paese}


# ---- la vista per le app ----------------------------------------------------------------------------------------


def versione(testo: str) -> Tuple[int, ...]:
    """`1.2` → `(1, 2, 0, 0)`: si confrontano tuple della stessa lunghezza."""
    parti = [int(x) for x in testo.split(".")]
    return tuple(parti + [0] * (4 - len(parti)))


async def config_pubblica(
    session: AsyncSession, piattaforma: str, versione_app: Optional[str], paese: Optional[str],
) -> Dict[str, Any]:
    """Ciò che serve all'app all'avvio, e nient'altro: niente segreti, appunti o ID degli account."""
    if versione_app and not VERSIONE.match(versione_app):
        raise ErroreAppMobili("Versione non valida: la forma è «1.2.3».")
    r = await session.get(ConfigAppMobile, piattaforma)
    parametri = parametri_di(r, piattaforma)
    minima, ultima = parametri["versione_minima"] or None, parametri["versione_ultima"] or None
    obbligatorio = bool(versione_app and minima and versione(versione_app) < versione(minima))
    disponibile = bool(versione_app and ultima and versione(versione_app) < versione(ultima))
    stripe = await risolvi_politica(session, piattaforma, paese)
    return {
        "piattaforma": piattaforma,
        "versione_minima": minima,
        "versione_ultima": ultima,
        "aggiornamento_obbligatorio": obbligatorio,
        "aggiornamento_disponibile": disponibile or obbligatorio,
        "link_store": link_store(piattaforma, parametri),
        "pulsante_stripe": {"modalita": stripe["modalita"], "avviso": stripe["avviso"]},
        "flag": {"ipad": bool(parametri["ipad"])} if piattaforma == "ios" else {},
    }


# ---- i collegamenti verificati fra sito e app (Fase 10) -----------------------------------------------------------

#: Le pagine del sito che si aprono nell'app (Android App Links, iOS Universal Links): le rotte dell'app
#: (`mobile/lib/rotte/percorsi.dart`), gli indirizzi pubblici in inglese e sotto `/it`, i vecchi nomi della v1 che il
#: router dell'app traduce (`mobile/lib/rotte/indirizzi.dart`). **Mai** `/api`, `/auth` (Keycloak: il ritorno dei
#: social passa di lì, e se lo prendesse l'app l'accesso si romperebbe), `/admin`, `/old`. Lo stesso elenco sta nei
#: filtri di `mobile/android/app/src/main/AndroidManifest.xml` (Android non legge i percorsi da `assetlinks.json`).
PERCORSI_APP: Tuple[str, ...] = (
    "/read", "/physical-reading", "/my-story", "/shared", "/daily-card", "/card-of-the-day", "/cards", "/spreads",
    "/decks", "/vote", "/shop", "/cart", "/pricing", "/explore", "/trial", "/blog", "/profile", "/privacy",
    "/account/elimina",
    # i nomi della v1 (e l'italiano senza `/it`), che l'app porta alla pagina nuova come il sito
    "/carte", "/stese", "/piano", "/carta-del-giorno", "/mazzo", "/deck", "/leggi", "/letture", "/profilo", "/s",
    "/interpreta", "/vota-mazzo",
)
#: Ciò che non si apre mai nell'app, anche se un giorno un percorso sopra lo coprisse.
ESCLUSI_APP: Tuple[str, ...] = ("/api/*", "/auth/*", "/admin/*", "/old/*", "/.well-known/*")


async def asset_links(session: AsyncSession) -> List[Dict[str, Any]]:
    """`/.well-known/assetlinks.json`: il package Android e le impronte dei certificati di firma (console → App mobili
    → Android). Senza package o senza impronte è un elenco vuoto: Android non verifica, e l'app funziona lo stesso
    (chiede con cosa aprire i collegamenti)."""
    parametri = parametri_di(await session.get(ConfigAppMobile, "android"), "android")
    pacchetto, impronte = parametri.get("package_name"), parametri.get("impronte_sha256") or []
    if not pacchetto or not impronte:
        return []
    return [{
        "relation": ["delegate_permission/common.handle_all_urls"],
        "target": {"namespace": "android_app", "package_name": pacchetto, "sha256_cert_fingerprints": list(impronte)},
    }]


def componenti_app() -> List[Dict[str, Any]]:
    """I percorsi per `apple-app-site-association` (iOS 13+): prima le esclusioni, poi le pagine dell'app."""
    componenti: List[Dict[str, Any]] = [{"/": p, "exclude": True} for p in ESCLUSI_APP]
    componenti += [{"/": "/"}, {"/": "/it"}, {"/": "/it/*"}]
    for p in PERCORSI_APP:
        componenti += [{"/": p}, {"/": f"{p}/*"}]
    return componenti


async def apple_app_site_association(session: AsyncSession) -> Dict[str, Any]:
    """`/.well-known/apple-app-site-association`: Team ID e bundle ID (console → App mobili → iOS) e i percorsi. Senza
    Team ID non c'è nessuna app associata."""
    parametri = parametri_di(await session.get(ConfigAppMobile, "ios"), "ios")
    team, bundle = parametri.get("team_id"), parametri.get("bundle_id")
    if not team or not bundle:
        return {"applinks": {"details": []}}
    app_id = f"{team}.{bundle}"
    return {
        "applinks": {"details": [{"appIDs": [app_id], "components": componenti_app()}]},
        # Le password salvate per tarots.chat proposte anche nella pagina d'accesso aperta dall'app.
        "webcredentials": {"apps": [app_id]},
    }
