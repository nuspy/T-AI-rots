"""Configurazione del backend, letta dall'ambiente.

In un container la configurazione arriva dall'ambiente, non da un file: i
valori cambiano fra sviluppo, staging e produzione mentre l'immagine resta la
stessa. I default qui sono quelli dello sviluppo con Docker Compose, cosi'
`docker compose up` funziona senza predisporre nulla.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict, List, Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .llm.compiti import ModelloConfigurato


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="TAROT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- identita' del processo -------------------------------------------
    service_name: str = "tarot-api"
    environment: Literal["dev", "staging", "prod"] = "dev"

    # --- supporti ----------------------------------------------------------
    #: Il valore predefinito e' quello per un processo avviato **sull'host**,
    #: e punta alla 5433 perche' e' li' che Compose espone il database: la 5432
    #: e' spesso gia' occupata da un PostgreSQL di sistema. I container
    #: ricevono `TAROT_DATABASE_URL` con `postgres:5432` e non usano questo.
    database_url: str = "postgresql+psycopg://tarot:tarot@localhost:5433/tarot"
    # Niente Redis: nessuna parte del codice lo usava (v9, Fase 3). Un `TAROT_REDIS_URL` rimasto
    # nell'ambiente si ignora (`extra="ignore"`).

    # --- identita' degli utenti -------------------------------------------
    keycloak_url: str = "http://localhost:8080"
    keycloak_realm: str = "tarots"
    keycloak_client_id: str = "tarot-api"
    #: Il segreto del client `tarot-api` (confidenziale, `serviceAccountsEnabled`): serve solo al
    #: grant client-credentials di `auth/keycloak_admin.py`, con cui la console cambia su Keycloak il
    #: login persistente (sessione offline) e l'accesso con i social. Nel cluster viene dal Secret
    #: `tarots-secrets`, chiave `api-client-secret` (la stessa che Keycloak legge come
    #: `KC_API_CLIENT_SECRET`). Vuoto: quelle due sezioni della console rispondono con l'errore, non
    #: un errore all'avvio — l'API non deve smettere di partire per questo.
    keycloak_client_secret: str = ""
    #: L'indirizzo pubblico di Keycloak, quello scritto nel campo `iss` dei
    #: token. Vuoto vale `keycloak_url`, come in sviluppo; in un cluster
    #: `keycloak_url` e' il servizio interno da cui si leggono le chiavi, e
    #: questo e' il dominio che vede il browser.
    keycloak_issuer_url: str = ""
    #: Altri client del realm i cui token questa API accetta. Il frontend ne fa
    #: parte: il token che riceve e' emesso per `tarot-frontend`, e se non
    #: fosse elencato qui ogni richiesta dell'interfaccia verrebbe respinta —
    #: con un 401 che sembrerebbe un problema di login. Resta un elenco chiuso
    #: perche' accettare qualunque destinatario significa accettare i token di
    #: qualunque applicazione che usi lo stesso realm. `tarot-mobile` (v9, Fase 6):
    #: il client pubblico delle app Android e iOS.
    keycloak_accepted_audiences: tuple[str, ...] = ("tarot-frontend", "tarot-admin", "tarot-mobile")
    #: In sviluppo l'autenticazione puo' essere disattivata per provare gli
    #: endpoint senza avviare Keycloak. Va negata fuori dallo sviluppo, e il
    #: controllo e' in `validate_production()`: un flag simile lasciato acceso
    #: per errore e' fra i modi piu' comuni di esporre un servizio.
    auth_disabled: bool = False

    # --- pagamenti ---------------------------------------------------------
    #: Chi incassa: `stripe` (v9, `billing/stripe.py`), `mock` (il simulatore,
    #: per lo sviluppo) o `disattivato` (nessuno: i piani a pagamento
    #: rispondono 503). Il flusso — sessione, pagina ospitata, evento firmato —
    #: e' lo stesso per tutti. In produzione `mock` impedisce l'avvio.
    #: Dalla v9 (Fase 2c) si sceglie dalla console (Pagamenti → Stripe, `configurazioni/correnti.py`):
    #: questo è il ripiego finché la console non ha scelto.
    billing_provider: str = "mock"
    #: Il segreto con cui il simulatore firma i suoi eventi (Stripe ha il suo, qui sotto).
    billing_webhook_secret: str = "segreto-di-sviluppo-da-cambiare"
    #: Fa fallire i rinnovi del simulatore, per provare la sospensione.
    billing_mock_renewal_fails: bool = False
    #: Stripe (v9): la chiave segreta dell'API (`sk_test_…`/`sk_live_…`, o una chiave limitata `rk_…`) e il segreto
    #: dell'endpoint del webhook (`whsec_…`). Dalla v9 (Fase 2c) si impostano dalla console (Pagamenti → Stripe,
    #: cifrate nel database, il webhook registrato da lì): questi, dal Secret `tarots-secrets` (`stripe-secret-key`,
    #: `stripe-webhook-secret`), sono il ripiego e al primo avvio si copiano nel database.
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    #: Gli schemi dei deep link a cui il checkout può tornare oltre ai percorsi del sito: l'app (`chat.tarots.app://…`).
    #: Un elenco chiuso: un ritorno arbitrario sarebbe un open redirect.
    ritorno_schemi_app: List[str] = Field(default_factory=lambda: ["chat.tarots.app"])
    #: Gli indirizzi pubblici: dove sta l'API (per la pagina di pagamento
    #: simulata) e dove torna l'utente dopo aver pagato.
    api_public_url: str = "http://localhost:8100"
    web_public_url: str = "http://localhost:3000"

    # --- osservabilita' ----------------------------------------------------
    otlp_endpoint: str = "http://localhost:4318"
    tracing_enabled: bool = True
    log_level: str = "INFO"

    # --- modelli -----------------------------------------------------------
    #: Nome dell'applicazione per il registro provider di llmswitch.
    llmswitch_app_name: str = "tarots"
    #: Endpoint predefinito per la generazione. LM Studio, vLLM e OpenAI
    #: parlano lo stesso dialetto, quindi cambiare fornitore e' cambiare questo
    #: indirizzo — finche' la fase 1 non porta il registro di llmswitch.
    llm_base_url: str = "http://127.0.0.1:1234/v1"
    llm_model: str = ""          # vuoto: si usa il primo modello caricato
    llm_api_key: str = "non-serve-in-locale"
    #: Nasconde i nomi di persona al fornitore del modello (`tarot/pseudonimi.py`): gli arriva «Persona_1», chi legge
    #: rivede il nome vero. Acceso: spegnerlo serve solo per confrontare il comportamento di un modello.
    anonimizza_nomi: bool = True
    #: JSON: campi aggiunti a ogni richiesta al modello predefinito (vedi `ModelloConfigurato.parametri`), per
    #: esempio `{"reasoning_effort": "low"}` per regolare il ragionamento. Vuoto: nessuno.
    llm_parametri: Dict[str, Any] = Field(default_factory=dict)
    #: JSON: il margine di token per il ragionamento che si aggiunge al tetto visibile di ogni richiesta quando il
    #: livello non è `none`, per livello (es. `{"xhigh": 32768}`). I livelli non indicati tengono i valori di
    #: `llm/ragionamento.MARGINE_LIVELLO`.
    margini_ragionamento: Dict[str, int] = Field(default_factory=dict)
    #: Oltre questo tempo senza un singolo token la richiesta viene interrotta.
    #: E' un timeout fra i token, non sulla durata totale: una risposta lunga e'
    #: legittima, un silenzio di due minuti no.
    llm_stream_timeout: float = 120.0

    #: Un elenco di fornitori dato dall'ambiente: solo un ripiego per lo sviluppo locale (`docker compose up` senza
    #: predisporre nulla) e per i test. In produzione i fornitori si configurano dalla **console**
    #: (`domain.config_models.LlmProvider`, cifrati in database con `llm/cifratura.py`): questa lista si legge solo
    #: finché la tabella è vuota. JSON: `[{"nome": "...", "provider": "...", "base_url": "...", "model": "...",
    #: "api_key": "...", "senza_filtri": false}, ...]`.
    modelli: List["ModelloConfigurato"] = Field(default_factory=list)
    #: Chiave Fernet (32 byte base64 url-safe) con cui le chiavi dei fornitori LLM sono cifrate nel database. Il
    #: valore predefinito è SOLO per lo sviluppo: `validate_production()` lo respinge in produzione, dove ne serve
    #: una propria (`Fernet.generate_key()`), messa nel Secret come le altre credenziali.
    llm_provider_key: str = "pF6wjvqBFeElH8yC0tfWcG6KFZnKDr5s6n4L5EjmMTE="

    #: Quale fornitore genera le risposte: `openai-compatible` (OpenAI, LM
    #: Studio, vLLM, llama.cpp e affini) o `anthropic`.
    llm_provider: str = "openai-compatible"
    #: Che motore sta dietro `llm_base_url`: decide la `ContextStrategy`.
    #: `auto` lo deduce dall'indirizzo; si imposta a mano quando l'indirizzo
    #: non basta a riconoscerlo — un vLLM dietro un nome di dominio qualunque.
    #: Valori: auto, openai, vllm, llamacpp, lmstudio, other.
    llm_engine: str = "auto"
    #: Slot paralleli del server llama.cpp (`--parallel`). Serve a mandare lo
    #: stesso prefisso sempre allo stesso slot, dove la KV-cache e' calda.
    llm_kv_slots: int = 1

    #: Anthropic, quando `llm_provider = anthropic`.
    anthropic_base_url: str = "https://api.anthropic.com"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-5"
    #: Il Messages API pretende `max_tokens`: questo e' il valore quando la
    #: versione della personalita' non ne indica uno.
    anthropic_max_tokens: int = 2048

    # --- letture -----------------------------------------------------------
    #: Quante domande di contesto prima della stesa: le sceglie il modello in
    #: base al quesito, ma mai meno del minimo né più del massimo.
    intervista_min_domande: int = 2
    intervista_max_domande: int = 6
    #: I crediti con cui nasce un utente di prova creato dal seed.
    crediti_utente_di_prova: int = 1000
    #: Il sale delle impronte anonime di chi visita un link condiviso (indirizzo e
    #: identificativo del browser). Facoltativo dalla v9 (Fase 2c): senza, al primo avvio se ne
    #: genera uno casuale che si conserva cifrato nel database (`configurazioni/segreti.py`); se
    #: c'è, vince questo e si copia nel database.
    condivisione_sale: str = ""
    #: Il segreto dell'HMAC con cui si conservano gli indirizzi IP (GDPR, Fase 1): in `user_consents`, `audit_log` e
    #: `consensi_storico` l'IP non si scrive mai in chiaro, ma troncato (IPv4 /24, IPv6 /48) più questa impronta
    #: dell'indirizzo intero (`tarot/ip_protetto.py`). Facoltativo dalla v9 (Fase 2c): senza, al primo avvio se ne
    #: genera uno casuale conservato cifrato nel database; se c'è, vince questo e si copia nel database.
    ip_hash_secret: str = ""
    #: Con `true` le letture usano il modello finto di `tarot/finto.py`:
    #: serve a provare il flusso intero senza un modello vero.
    llm_finto: bool = False
    #: Il registro dei consumi delle chiamate ai modelli (`llm/consumi.py`, tabella `llm_consumi`): token in ingresso,
    #: in cache, in uscita e di ragionamento, per compito. Acceso anche in produzione: scrive in background e un errore
    #: di scrittura non tocca la lettura. `false` lo spegne (i test lo spengono, salvo quelli che lo provano).
    consumi_llm: bool = True
    #: La memoria di prima, con gli embedding (`tarot/memoria.py`, `memoria_retrieval.py`): l'estrazione dopo ogni
    #: lettura (compito `memoria_estrazione`, che ereditava il ragionamento), la vettorizzazione e il recupero per
    #: somiglianza all'apertura. Spenta dalla riduzione dei costi: la sostituisce lo stato sintetico
    #: (`tarot/stato_memoria.py`), e in produzione l'embedding non ha mai funzionato. `true` la riaccende com'era.
    memoria_embedding: bool = False

    #: Notifica notturna ai motori di ricerca (v8, libreria `seo-notify`). Ogni canale è
    #: facoltativo: senza configurazione si salta, non fa fallire gli altri.
    #: La chiave IndexNow (Bing, Yandex…) NON è un segreto: il protocollo la vuole pubblica, in
    #: `https://<sito>/<chiave>.txt` (il file sta in `frontend/public/`).
    indexnow_chiave: str = ""
    #: Il JSON di un service account Google con accesso alla proprietà in Search Console (montato
    #: da un Secret). Vuoto o file assente: Google si salta.
    search_console_credenziali: str = ""
    #: La proprietà come registrata in Search Console: `sc-domain:tarots.chat` (proprietà di
    #: dominio) o `https://tarots.chat/` (prefisso URL).
    search_console_proprieta: str = ""
    #: L'hub WebSub a cui annunciare il feed RSS del blog. Vuoto: WebSub si salta.
    websub_hub: str = ""

    #: Analytics (v8, libreria `lanterna`). Spenti: nessuna raccolta, l'endpoint risponde 204 e
    #: scarta tutto.
    analytics_attivi: bool = True
    #: Il file .mmdb di DB-IP City Lite (scaricato nell'immagine). Vuoto o assente: niente paese e
    #: città, il resto funziona.
    analytics_geo: str = ""
    #: Il dominio pubblico del sito, per riconoscere i referrer interni.
    analytics_dominio: str = "tarots.chat"
    #: Mesi di conservazione di sessioni ed eventi grezzi (poi resta il riepilogo giornaliero).
    analytics_ritenzione_mesi: int = 25

    #: La posta in uscita del backend (v8: il rapporto settimanale degli analytics). Stalwart, lo
    #: stesso server e mittente di Keycloak. Senza host il rapporto non parte (e lo dice).
    #: Dalla v9 (Fase 2c) si imposta dalla console (Impostazioni → Posta in uscita): questi valori
    #: sono il ripiego, e al primo avvio si copiano da soli nel database (password cifrata).
    smtp_host: str = ""
    smtp_porta: int = 465
    #: SMTPS implicito (465). Falso: STARTTLS (587).
    smtp_ssl: bool = True
    smtp_utente: str = ""
    smtp_password: str = ""
    smtp_mittente: str = ""

    #: Il backup notturno sul NAS (v8.3). La destinazione si sceglie dalla console; dalla v9 (Fase 2c) anche la
    #: credenziale (chiave SSH o password, cifrata nel database). Il Secret montato (la chiave SSH privata in
    #: questo file, oppure una password) resta il ripiego e al primo avvio si copia nel database.
    backup_chiave_ssh: str = "/etc/tarots-backup/ssh-key"
    backup_password: str = ""
    #: I programmi del client PostgreSQL, alla versione del server (l'immagine dell'API porta il 18).
    backup_pg_dump: str = "pg_dump"
    backup_pg_restore: str = "pg_restore"

    cors_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:3001"]
    )

    def llm_configurato(self) -> bool:
        """C'è un modello vero a cui chiedere le letture?

        Le domande dell'intervista, le interpretazioni e il responso li scrive
        un modello: senza, il servizio non deve fingere di funzionare con testi
        di ripiego uguali per tutti. Vale `true` se:

        - c'è il modello finto (sviluppo e test);
        - `TAROT_MODELLI` ne elenca uno utilizzabile;
        - Anthropic ha una chiave;
        - l'indirizzo `TAROT_LLM_BASE_URL` è stato impostato **esplicitamente**:
          il valore predefinito, un LM Studio su localhost, non basta, perché in
          un container non c'è nulla su quella porta.
        """
        if self.llm_finto:
            return True
        if self.modelli:
            return any(
                bool(m.api_key) if m.provider == "anthropic" else bool(m.base_url)
                for m in self.modelli
            )
        if self.llm_provider == "anthropic":
            return bool(self.anthropic_api_key)
        return "llm_base_url" in self.model_fields_set

    def validate_production(self) -> List[str]:
        """Impostazioni che in produzione sarebbero un difetto.

        Restituisce i problemi invece di sollevare: chi avvia il servizio
        decide se rifiutarsi di partire o soltanto segnalare.
        """
        problems: List[str] = []
        if self.environment == "prod":
            if self.llm_finto:
                problems.append(
                    "TAROT_LLM_FINTO e' attivo in produzione: le letture "
                    "userebbero testi finti"
                )
            if self.auth_disabled:
                problems.append(
                    "TAROT_AUTH_DISABLED e' attivo in produzione: ogni endpoint "
                    "sarebbe accessibile senza credenziali"
                )
            if "*" in self.cors_origins:
                problems.append("CORS aperto a qualunque origine in produzione")
            # Il sale delle condivisioni e il segreto degli IP non si chiedono più (v9, Fase 2c): senza ambiente se ne
            # genera uno casuale al primo avvio, conservato cifrato nel database. Solo i valori di sviluppo scritti
            # a mano nell'ambiente sono un difetto.
            if self.condivisione_sale == "sale-di-sviluppo":
                problems.append("TAROT_CONDIVISIONE_SALE e' quello di sviluppo in produzione: toglilo, se ne genera uno")
            if self.ip_hash_secret == "segreto-ip-di-sviluppo":
                problems.append(
                    "TAROT_IP_HASH_SECRET e' quello di sviluppo in produzione: l'impronta degli indirizzi IP "
                    "salvati si potrebbe ricalcolare (toglilo: se ne genera uno)"
                )
            if self.llm_provider_key == "pF6wjvqBFeElH8yC0tfWcG6KFZnKDr5s6n4L5EjmMTE=":
                problems.append(
                    "TAROT_LLM_PROVIDER_KEY e' quella di sviluppo in produzione: chi legge il database "
                    "leggerebbe anche le chiavi dei fornitori LLM"
                )
            if "localhost" in self.database_url:
                problems.append("il database punta a localhost in produzione")
            # Dalla v9 (Fase 2c) il fornitore e le chiavi di Stripe si scelgono dalla console: l'ambiente è solo il
            # ripiego, e in produzione il simulatore non vale mai (`configurazioni/correnti.py` lo tratta come
            # `disattivato`). Blocca l'avvio solo un `mock` chiesto esplicitamente dall'ambiente; le chiavi di Stripe
            # mancanti non bloccano più (possono stare in console: la pagina Pagamenti dice cosa manca).
            esplicito = "billing_provider" in self.model_fields_set
            if self.billing_provider == "mock" and esplicito:
                problems.append(
                    "fornitore di pagamento simulato in produzione: chiunque "
                    "potrebbe attivare qualunque piano senza pagare. Finché un "
                    "fornitore vero non c'è, TAROT_BILLING_PROVIDER=disattivato"
                )
            # Senza fornitore non si accetta nessun evento, e il segreto non
            # firma niente: pretenderlo costringerebbe a inventarne uno.
            # Stripe firma con il suo segreto (`stripe_webhook_secret`), non con questo.
            if (
                esplicito
                and self.billing_provider not in ("disattivato", "stripe")
                and self.billing_webhook_secret == "segreto-di-sviluppo-da-cambiare"
            ):
                problems.append(
                    "segreto dei webhook di pagamento lasciato al valore di "
                    "sviluppo: chiunque potrebbe firmare un pagamento finto"
                )
        return problems


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
