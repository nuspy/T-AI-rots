"""Il catalogo chiuso dei tipi di fornitore che la console propone.

Sottoinsieme di `llmswitch.providers.TYPES` (progetto separato dell'utente, pensato per un'app desktop mono-utente
con motori locali e abbonamenti OAuth): qui serve solo la parte utile a un backend server-side — endpoint
OpenAI-compatibili o Anthropic, a chiave o senza. Niente CLI ad abbonamento (Codex, Claude Code…): sono account
personali di chi sviluppa, non fornitori di un servizio con utenti propri.

Ogni voce dà alla console un'etichetta, il dialetto (`provider`), l'indirizzo predefinito e se serve una chiave: la
console li propone come punto di partenza, non li impone — `base_url` resta modificabile (un `lmstudio` o un `vllm`
di solito vive su una macchina dell'utente, non su un indirizzo fisso).
"""
from __future__ import annotations

from typing import Dict, TypedDict


class TipoFornitore(TypedDict):
    label: str
    provider: str          # "openai-compatible" | "anthropic"
    base_url: str           # "" quando non c'è un indirizzo predefinito sensato
    auth: str                # "api_key" | "none"
    nota: str


CATALOGO: Dict[str, TipoFornitore] = {
    "lmstudio": {
        "label": "LM Studio", "provider": "openai-compatible", "auth": "none",
        "base_url": "http://127.0.0.1:1234/v1",
        "nota": "Server locale. Il modello già in memoria ha la precedenza su quello scelto qui.",
    },
    "vllm": {
        "label": "vLLM", "provider": "openai-compatible", "auth": "none", "base_url": "",
        "nota": "Istanza vLLM, OpenAI-compatibile.",
    },
    "llamacpp": {
        "label": "llama.cpp (llama-server)", "provider": "openai-compatible", "auth": "none",
        "base_url": "http://127.0.0.1:8080/v1",
        "nota": "Serve il modello passato all'avvio: non se ne cambia da qui.",
    },
    "openai": {
        "label": "OpenAI", "provider": "openai-compatible", "auth": "api_key",
        "base_url": "https://api.openai.com/v1", "nota": "API a consumo.",
    },
    "anthropic": {
        "label": "Claude (Anthropic)", "provider": "anthropic", "auth": "api_key",
        "base_url": "https://api.anthropic.com", "nota": "API a consumo.",
    },
    "nvidia": {
        "label": "NVIDIA NIM", "provider": "openai-compatible", "auth": "api_key",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "nota": "Modelli di build.nvidia.com. Il livello gratuito è una prova: niente produzione, prompt riutilizzabili.",
    },
    "nebius": {
        "label": "Nebius Token Factory", "provider": "openai-compatible", "auth": "api_key",
        "base_url": "https://api.tokenfactory.nebius.com/v1", "nota": "Modelli aperti a consumo.",
    },
    "deepinfra": {
        "label": "DeepInfra", "provider": "openai-compatible", "auth": "api_key",
        "base_url": "https://api.deepinfra.com/v1/openai",
        "nota": "Modelli aperti a consumo, con sconto sulla cache del prefisso. Ragionamento con reasoning_effort: "
                "da verificare per il modello scelto.",
    },
    "darkbloom": {
        "label": "Darkbloom", "provider": "openai-compatible", "auth": "api_key", "base_url": "",
        "nota": "OpenAI-compatibile. Da verificare: indirizzo dell'API, nome del modello, campo del ragionamento e "
                "sede per l'informativa.",
    },
    "deepseek": {
        "label": "DeepSeek", "provider": "openai-compatible", "auth": "api_key",
        "base_url": "https://api.deepseek.com/v1", "nota": "",
    },
    "kimi": {
        "label": "Kimi (Moonshot AI)", "provider": "openai-compatible", "auth": "api_key",
        "base_url": "https://api.moonshot.ai/v1", "nota": "Endpoint internazionale.",
    },
    "qwen": {
        "label": "Qwen (Alibaba Model Studio)", "provider": "openai-compatible", "auth": "api_key",
        "base_url": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1", "nota": "Endpoint internazionale.",
    },
    "zai": {
        "label": "Z.AI (piano API)", "provider": "openai-compatible", "auth": "api_key",
        "base_url": "https://api.z.ai/api/paas/v4", "nota": "",
    },
    "zai_coding": {
        "label": "Z.AI (piano coding)", "provider": "openai-compatible", "auth": "api_key",
        "base_url": "https://api.z.ai/api/coding/paas/v4", "nota": "Quota separata dal piano API.",
    },
    "unsloth": {
        "label": "Unsloth", "provider": "openai-compatible", "auth": "api_key",
        "base_url": "http://localhost:8000/v1", "nota": "Server locale su llama.cpp.",
    },
    "openai_compat": {
        "label": "Generico (OpenAI-compatibile)", "provider": "openai-compatible", "auth": "api_key",
        "base_url": "", "nota": "Qualunque server che espone /v1/chat/completions.",
    },
}


class Sede(TypedDict):
    #: Chi tratta i dati (il nome che l'informativa privacy mostra).
    azienda: str
    #: Il paese dove l'azienda ha sede e tratta le richieste, codice ISO 3166 a due lettere (il sito lo scrive nella
    #: lingua di chi legge). Vuoto: un motore che gira su un server nostro (nessun terzo) o un fornitore generico di
    #: cui il catalogo non sa nulla.
    paese: str
    #: Un motore installato da noi (nessun fornitore esterno riceve i testi).
    proprio: bool


#: Dove stanno i fornitori del catalogo, per l'elenco dell'informativa privacy (v9, Fase 2c: l'elenco si legge dai
#: fornitori attivi in console, non si scrive a mano). Gli endpoint «internazionali» sono quelli fuori dalla Cina
#: continentale: Alibaba Model Studio internazionale ha sede a Singapore.
SEDI: Dict[str, Sede] = {
    "lmstudio": {"azienda": "LM Studio", "paese": "", "proprio": True},
    "vllm": {"azienda": "vLLM", "paese": "", "proprio": True},
    "llamacpp": {"azienda": "llama.cpp", "paese": "", "proprio": True},
    "unsloth": {"azienda": "Unsloth", "paese": "", "proprio": True},
    "openai": {"azienda": "OpenAI", "paese": "US", "proprio": False},
    "anthropic": {"azienda": "Anthropic", "paese": "US", "proprio": False},
    "nvidia": {"azienda": "NVIDIA", "paese": "US", "proprio": False},
    "nebius": {"azienda": "Nebius", "paese": "NL", "proprio": False},
    "deepinfra": {"azienda": "DeepInfra", "paese": "US", "proprio": False},
    # Sede da verificare prima di attivarlo: senza paese l'informativa lo mostra come fornitore generico.
    "darkbloom": {"azienda": "Darkbloom", "paese": "", "proprio": False},
    "deepseek": {"azienda": "DeepSeek", "paese": "CN", "proprio": False},
    "kimi": {"azienda": "Moonshot AI (Kimi)", "paese": "CN", "proprio": False},
    "qwen": {"azienda": "Alibaba Cloud (Qwen)", "paese": "SG", "proprio": False},
    "zai": {"azienda": "Z.AI (Zhipu)", "paese": "CN", "proprio": False},
    "zai_coding": {"azienda": "Z.AI (Zhipu)", "paese": "CN", "proprio": False},
    "openai_compat": {"azienda": "", "paese": "", "proprio": False},
}
