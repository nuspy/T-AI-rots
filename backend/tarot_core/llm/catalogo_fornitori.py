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
