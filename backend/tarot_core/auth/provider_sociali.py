"""L'accesso con i social: quali provider la console sa configurare, e come diventano un identity provider di
Keycloak.

Keycloak 26.0 (l'immagine di `deploy/keycloak/Dockerfile`) ha provider integrati per Google, Facebook, Microsoft,
GitHub, LinkedIn (OpenID Connect) e X/Twitter: bastano client id e segreto. Apple non ha un provider integrato ed
è un OIDC generico (il suo segreto è un JWT che scade, vedi la guida). Instagram è nel catalogo solo per dire
perché non si può accendere.

**I segreti non passano dal nostro database.** La console li manda, il backend li gira a Keycloak (Admin API) e li
dimentica: restano solo in Keycloak, che non li restituisce più in chiaro (`**********`). Così non serve una
cifratura come per le chiavi dei fornitori LLM: non c'è niente da cifrare, perché niente viene salvato.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

#: Il valore con cui Keycloak maschera un segreto nelle risposte dell'Admin API. Rimandato così in un
#: aggiornamento, Keycloak tiene il segreto che ha già.
MASCHERA = "**********"

#: Il flusso che chiede l'OTP agli amministratori anche dopo un accesso esterno (realm di produzione, creato da
#: `deploy/keycloak/strumenti/genera_realm_prod.py`): senza, un admin che entra con un social salterebbe la 2FA.
FLUSSO_DOPO_ACCESSO_ESTERNO = "2FA amministratori dopo accesso esterno"

#: Il flusso del primo accesso con un social che **unisce gli account**: se esiste già un utente con la stessa email
#: (iscritto con email e password, o entrato prima con un altro social) l'identità social si collega a lui senza
#: chiedere niente; se non esiste, lo crea. Lo costruisce `KeycloakAdmin.assicura_flusso_unione` (e il generatore
#: del realm di produzione) con i passi della ricetta di Keycloak «Automatically link existing first login flow».
#: Solo per i provider che garantiscono un'email verificata (`fidati_email`): con gli altri, collegare in automatico
#: vorrebbe dire consegnare un account a chiunque scriva quell'email nel proprio profilo social.
FLUSSO_UNIONE = "primo accesso con unione degli account"
#: Il flusso predefinito di Keycloak: con un'email già registrata chiede conferma e una prova (rientrare con la
#: password o con un social già collegato) prima di collegare.
FLUSSO_STANDARD = "first broker login"


@dataclass(frozen=True)
class ProviderSociale:
    alias: str
    nome: str
    #: Il `providerId` di Keycloak (il tipo di provider), che non sempre coincide con l'alias.
    tipo: str
    #: Dove l'operatore crea le credenziali.
    console: str
    #: Una guida breve, in passi: cosa creare e dove incollare l'URI di reindirizzamento.
    guida: List[str]
    #: Configurazione fissa del provider oltre a id e segreto (ambiti, endpoint per l'OIDC generico).
    config: Dict[str, str] = field(default_factory=dict)
    #: Le email che arrivano dal provider si possono considerare verificate? Decide anche l'unione automatica
    #: degli account (`FLUSSO_UNIONE`): solo con un'email garantita.
    fidati_email: bool = True
    nota: str = ""
    disponibile: bool = True
    #: Il backend legge il profilo dal provider (nome, data di nascita, sesso, lingua, foto, città) con il token che
    #: Keycloak conserva (`storeToken`): vedi `tarot/profilo_social.py`.
    legge_profilo: bool = False
    #: Gli ambiti in più per i dati «sensibili» (data di nascita, sesso, città), accesi dalla console. Google li
    #: concede solo alle app verificate, Facebook dopo l'App Review: prima, chiederli fa danni (Google mostra «app
    #: non verificata» a chi entra) o non dà niente.
    scope_estesi: str = ""
    nota_estesi: str = ""


CATALOGO: List[ProviderSociale] = [
    ProviderSociale(
        alias="google", nome="Google", tipo="google",
        console="https://console.cloud.google.com/apis/credentials",
        guida=[
            "Google Cloud Console → API e servizi → Schermata consenso OAuth: tipo «Esterno», ambiti openid, email, profile.",
            "Credenziali → Crea credenziali → ID client OAuth → Applicazione web.",
            "In «URI di reindirizzamento autorizzati» incolla l'URI qui sotto.",
            "Copia ID client e Client secret qui.",
            "Per data di nascita e sesso: abilita la «People API» (API e servizi → Libreria), aggiungi gli ambiti "
            "user.birthday.read e user.gender.read alla schermata di consenso e chiedi la verifica dell'app.",
        ],
        config={"defaultScope": "openid profile email"},
        legge_profilo=True,
        scope_estesi=(
            "https://www.googleapis.com/auth/user.birthday.read https://www.googleapis.com/auth/user.gender.read"
        ),
        nota_estesi=(
            "Data di nascita e sesso vengono dalla People API con due ambiti «sensibili»: Google li concede solo "
            "alle app verificate (Google Cloud → Schermata consenso OAuth → Verifica). Accenderli prima della "
            "verifica fa comparire a chi entra l'avviso «Google non ha verificato questa app»."
        ),
    ),
    ProviderSociale(
        alias="facebook", nome="Facebook", tipo="facebook",
        console="https://developers.facebook.com/apps",
        guida=[
            "Meta for Developers → Crea app → caso d'uso «Autenticare e richiedere dati agli utenti con Facebook Login».",
            "Facebook Login → Impostazioni → «URI di reindirizzamento OAuth validi»: incolla l'URI qui sotto.",
            "Impostazioni → Di base: ID app e Chiave segreta; servono anche l'URL dell'informativa privacy e la modalità Live.",
        ],
        config={"defaultScope": "email public_profile"},
        nota="È anche la via d'accesso per chi usa Instagram: gli account Meta passano da qui.",
        legge_profilo=True,
        scope_estesi="user_birthday user_gender user_location",
        nota_estesi=(
            "Compleanno, sesso e città richiedono i permessi user_birthday, user_gender e user_location, che Meta "
            "concede solo dopo l'App Review (Meta for Developers → Revisione app → Autorizzazioni). Finché non sono "
            "approvati, chi entra non li concede e si importa solo nome, cognome e foto."
        ),
    ),
    ProviderSociale(
        alias="microsoft", nome="Microsoft", tipo="microsoft",
        console="https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade",
        guida=[
            "Portale Azure → Microsoft Entra ID → Registrazioni app → Nuova registrazione.",
            "Tipi di account: «Account in qualsiasi directory organizzativa e account Microsoft personali».",
            "URI di reindirizzamento: piattaforma Web, l'URI qui sotto.",
            "Certificati e segreti → Nuovo segreto client: copia il «Valore» (non l'ID). Ha una scadenza: annotala.",
            "ID applicazione (client) e Valore del segreto qui.",
        ],
        config={"defaultScope": "openid profile email"},
        # Un account Microsoft personale può avere un'email non verificata, e in Entra ID l'email è un campo che
        # l'amministratore del tenant scrive a piacere («nOAuth»): niente unione automatica, l'iscritto conferma.
        fidati_email=False,
        legge_profilo=True,
        nota="Il segreto scade (al massimo 24 mesi): rinnovalo dal portale e reinseriscilo qui.",
    ),
    ProviderSociale(
        alias="apple", nome="Apple", tipo="oidc",
        console="https://developer.apple.com/account/resources/identifiers/list/serviceId",
        guida=[
            "Apple Developer → Identifiers: l'App ID dell'app (chat.tarots.app) con «Sign in with Apple», poi un "
            "Services ID (per esempio chat.tarots.web) raggruppato sotto quell'App ID («Primary App ID»).",
            "Nel Services ID: dominio del login (quello di Keycloak) e Return URL = l'URI qui sotto. Il Services ID "
            "è il client id, per il sito e per le app.",
            "Keys: una chiave con «Sign in with Apple» collegata allo stesso App ID; scarica il file .p8 (una volta "
            "sola) e annota il Key ID. Il Team ID è in Account → Membership.",
            "Scrivi Team ID, Key ID, Services ID e carica la .p8 nel riquadro «Segreto di Apple» qui sotto: il "
            "segreto (un JWT che scade entro 6 mesi) lo firma e lo rinnova il sito, da solo.",
        ],
        config={
            "issuer": "https://appleid.apple.com",
            "authorizationUrl": "https://appleid.apple.com/auth/authorize?response_mode=form_post",
            "tokenUrl": "https://appleid.apple.com/auth/token",
            "jwksUrl": "https://appleid.apple.com/auth/keys",
            "useJwksUrl": "true",
            "validateSignature": "true",
            "clientAuthMethod": "client_secret_post",
            "defaultScope": "openid name email",
        },
        nota=(
            "Keycloak 26 non ha un provider Apple integrato: è un OIDC generico, e il segreto (un JWT) scade entro "
            "6 mesi. Lo firma il sito con la chiave .p8 caricata qui e lo rinnova ogni mese il CronJob "
            "tarots-apple-segreto (tarot/accesso_apple.py). Apple manda il nome solo al primo accesso e Keycloak non "
            "lo legge: il profilo del sito lo chiede alla persona."
        ),
    ),
    ProviderSociale(
        alias="github", nome="GitHub", tipo="github",
        console="https://github.com/settings/developers",
        guida=[
            "GitHub → Settings → Developer settings → OAuth Apps → New OAuth App.",
            "Homepage URL https://tarots.chat; «Authorization callback URL» = l'URI qui sotto.",
            "Generate a new client secret: Client ID e segreto qui.",
        ],
        config={"defaultScope": "user:email"},
        legge_profilo=True,
    ),
    ProviderSociale(
        alias="linkedin", nome="LinkedIn", tipo="linkedin-openid-connect",
        console="https://www.linkedin.com/developers/apps",
        guida=[
            "LinkedIn Developers → Create app (serve una pagina aziendale da collegare).",
            "Products → «Sign In with LinkedIn using OpenID Connect».",
            "Auth → «Authorized redirect URLs for your app»: l'URI qui sotto.",
            "Client ID e Primary Client Secret qui.",
        ],
        config={"defaultScope": "openid profile email"},
        legge_profilo=True,
    ),
    ProviderSociale(
        alias="twitter", nome="X (Twitter)", tipo="twitter",
        console="https://developer.x.com/en/portal/dashboard",
        guida=[
            "X Developer Portal → Projects & Apps → la tua app → User authentication settings.",
            "OAuth 1.0a, tipo «Web App»; Callback URI = l'URI qui sotto; Website URL https://tarots.chat.",
            "Attiva «Request email from users» (chiede gli URL di privacy e termini).",
            "Keys and tokens → «API Key and Secret» (le chiavi consumer, non il Client ID OAuth 2.0): sono client id e segreto.",
        ],
        fidati_email=False,
        nota="Keycloak parla con X in OAuth 1.0a. Senza «Request email» X non dà l'email e Keycloak la chiede all'iscritto.",
    ),
    ProviderSociale(
        alias="instagram", nome="Instagram", tipo="instagram",
        console="https://developers.facebook.com/apps",
        guida=[],
        disponibile=False,
        nota=(
            "Non si può accendere. Keycloak 26.0 ha ancora un provider «instagram», ma usa la Instagram Basic Display "
            "API, che Meta ha chiuso il 4 dicembre 2024: il login fallirebbe sempre. Chi usa Instagram entra con "
            "Facebook (gli account Meta sono collegati dall'Account Center)."
        ),
    ),
]

PER_ALIAS: Dict[str, ProviderSociale] = {p.alias: p for p in CATALOGO}


def e_segnaposto(valore: Optional[str]) -> bool:
    """Un client id che non è una credenziale vera: vuoto, il segnaposto del realm di sviluppo (`sostituire-…`),
    quello del manifest (`non-usato`) o un `${…}` non risolto all'import."""
    v = (valore or "").strip()
    return not v or v == "non-usato" or v.startswith("sostituire-") or v.startswith("${")


def dati_estesi_attivi(p: ProviderSociale, esistente: Optional[Dict[str, Any]]) -> bool:
    """Gli ambiti estesi sono già chiesti? Lo stato vero sta in Keycloak (il `defaultScope` del provider), non in
    una copia nel nostro database."""
    if not p.scope_estesi or not esistente:
        return False
    chiesti = set(str(((esistente.get("config") or {}).get("defaultScope")) or "").split())
    return set(p.scope_estesi.split()) <= chiesti


def stato(p: ProviderSociale, esistente: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Ciò che la console mostra di un provider: mai il segreto, solo se c'è."""
    config = (esistente or {}).get("config") or {}
    client_id = config.get("clientId") or ""
    return {
        "presente": esistente is not None,
        "abilitato": bool(esistente and str(esistente.get("enabled")).lower() == "true"),
        "client_id": "" if e_segnaposto(client_id) else client_id,
        # Keycloak maschera qualunque segreto: se l'id è un segnaposto lo è anche il segreto.
        "segreto_impostato": bool(config.get("clientSecret")) and not e_segnaposto(client_id),
        # L'unione automatica degli account: possibile solo con un'email garantita, attiva se il provider usa il
        # flusso che la fa.
        "unione_possibile": p.fidati_email,
        "unione_automatica": bool(esistente and esistente.get("firstBrokerLoginFlowAlias") == FLUSSO_UNIONE),
        "legge_profilo": p.legge_profilo,
        "token_conservato": bool(esistente and str(esistente.get("storeToken")).lower() == "true"),
        "dati_estesi_disponibili": bool(p.scope_estesi),
        "dati_estesi": dati_estesi_attivi(p, esistente),
        "nota_estesi": p.nota_estesi,
    }


def rappresentazione(
    p: ProviderSociale,
    esistente: Optional[Dict[str, Any]],
    *,
    abilitato: bool,
    client_id: str,
    client_secret: Optional[str],
    flusso_dopo: Optional[str],
    flusso_unione: Optional[str] = None,
    dati_estesi: Optional[bool] = None,
) -> Dict[str, Any]:
    """La rappresentazione da mandare a Keycloak. Parte da quella esistente (non si perdono i campi che
    Keycloak aggiunge da sé, né i mapper), e se il segreto non cambia lascia il valore mascherato.

    `flusso_unione`: l'alias del flusso che unisce gli account, se il realm ce l'ha; lo prende solo un provider con
    l'email garantita, gli altri restano (o tornano) al flusso standard con conferma. `dati_estesi`: chiedere anche
    gli ambiti sensibili; `None` lascia com'è."""
    rapp = copy.deepcopy(esistente) if esistente else {
        "alias": p.alias,
        "providerId": p.tipo,
        "firstBrokerLoginFlowAlias": FLUSSO_STANDARD,
        "config": {"syncMode": "IMPORT"},
    }
    if dati_estesi is None:
        dati_estesi = dati_estesi_attivi(p, esistente)
    rapp["displayName"] = p.nome
    rapp["enabled"] = abilitato
    rapp["trustEmail"] = p.fidati_email
    if p.fidati_email and flusso_unione:
        rapp["firstBrokerLoginFlowAlias"] = flusso_unione
    elif not p.fidati_email:
        rapp["firstBrokerLoginFlowAlias"] = FLUSSO_STANDARD
    if p.legge_profilo:
        # Keycloak conserva il token del provider, e chi è entrato lo legge per sé (`broker/<alias>/token`, ruolo
        # `broker/read-token` nei ruoli predefiniti): così il backend chiede al provider i dati del profilo.
        rapp["storeToken"] = True
    config = rapp.setdefault("config", {})
    config.update(p.config)
    if p.scope_estesi and dati_estesi:
        config["defaultScope"] = f"{p.config.get('defaultScope', '')} {p.scope_estesi}".strip()
    config["clientId"] = client_id
    if client_secret:
        config["clientSecret"] = client_secret
    elif esistente:
        config["clientSecret"] = MASCHERA
    if flusso_dopo:
        rapp["postBrokerLoginFlowAlias"] = flusso_dopo
    return rapp


def con_unione(p: ProviderSociale, esistente: Dict[str, Any], flusso_unione: str) -> Optional[Dict[str, Any]]:
    """Il provider così com'è in Keycloak, con il flusso giusto per l'unione degli account e il token conservato se
    il backend legge il profilo. `None` se non c'è niente da cambiare. Il segreto torna mascherato com'è stato letto:
    Keycloak tiene quello che ha."""
    flusso = flusso_unione if p.fidati_email else FLUSSO_STANDARD
    conserva = p.legge_profilo and str(esistente.get("storeToken")).lower() != "true"
    if esistente.get("firstBrokerLoginFlowAlias") == flusso and not conserva:
        return None
    rapp = copy.deepcopy(esistente)
    rapp["firstBrokerLoginFlowAlias"] = flusso
    if p.legge_profilo:
        rapp["storeToken"] = True
    config = rapp.setdefault("config", {})
    if config.get("clientSecret"):
        config["clientSecret"] = MASCHERA
    return rapp
