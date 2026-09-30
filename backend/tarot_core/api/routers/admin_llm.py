"""La console: i fornitori LLM. Indirizzo, modello, chiave — configurati da qui, non dall'ambiente.

Fino al 2026-09-27 questo elenco viveva in `TAROT_MODELLI` e la console poteva solo scegliere fra i nomi già
elencati (vedi `domain/config_models.py` per il perché del cambio). Qui si aggiungono, modificano ed eliminano
fornitori: ogni scrittura finisce nel registro di audit **senza la chiave**, che non esce mai in chiaro da questi
endpoint — un fornitore la porta solo per rispondere `has_key: true/false`.

L'assegnazione compito→fornitore resta in `admin.py` (`GET/PUT /admin/models`): non è cambiata, perché sceglieva già
fra nomi e continua a farlo — i nomi vengono da qui invece che dall'ambiente.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from lanterna.rete import ip_client
from pydantic import BaseModel, Field, model_validator
from sqlalchemy.exc import IntegrityError

from ...auth.dependencies import CurrentUser, DbSession, require_role
from ...domain.config_models import LlmProvider
from ...domain.llm_repositories import fornitori_correnti, pubblico
from ...domain.repositories import AuditRepository
from ...llm.catalogo_fornitori import CATALOGO
from ...llm.cifratura import cifra
from ...llm.compiti import controlla_parametri
from ..deps import aggiorna_assegnazioni

router = APIRouter(prefix="/admin", tags=["fornitori-llm"], dependencies=[Depends(require_role("admin"))])


def _ip(request: Request) -> Optional[str]:
    return ip_client(request)


class FornitoreNuovo(BaseModel):
    nome: str = Field(min_length=1, max_length=60)
    tipo: str = Field(min_length=1, max_length=30)
    base_url: str = Field(default="", max_length=300)
    model: str = Field(default="", max_length=120)
    embed_model: str = Field(default="", max_length=120)
    api_key: str = Field(default="", max_length=400)
    motore: str = Field(default="", max_length=20)
    ragiona: bool = False
    parametri: Dict[str, Any] = Field(default_factory=dict)
    senza_filtri: bool = False
    descrizione: str = Field(default="", max_length=200)
    attivo: bool = True

    @model_validator(mode="after")
    def _coerente(self) -> "FornitoreNuovo":
        if self.tipo not in CATALOGO:
            raise ValueError(f"tipo di fornitore sconosciuto: {self.tipo!r}. Validi: {', '.join(sorted(CATALOGO))}")
        controlla_parametri(self.parametri)
        return self


class FornitoreModifica(BaseModel):
    """Ogni campo assente non si tocca. `api_key` è l'eccezione: assente = non si tocca, `""` = la svuota."""

    base_url: Optional[str] = Field(default=None, max_length=300)
    model: Optional[str] = Field(default=None, max_length=120)
    embed_model: Optional[str] = Field(default=None, max_length=120)
    api_key: Optional[str] = Field(default=None, max_length=400)
    motore: Optional[str] = Field(default=None, max_length=20)
    ragiona: Optional[bool] = None
    parametri: Optional[Dict[str, Any]] = None
    senza_filtri: Optional[bool] = None
    descrizione: Optional[str] = Field(default=None, max_length=200)
    attivo: Optional[bool] = None

    @model_validator(mode="after")
    def _coerente(self) -> "FornitoreModifica":
        if self.parametri is not None:
            controlla_parametri(self.parametri)
        return self


@router.get("/llm/providers")
async def elenco(session: DbSession) -> Dict[str, Any]:
    fornitori = await fornitori_correnti(session)
    return {
        "fornitori": [pubblico(f) for f in fornitori],
        "catalogo": [
            {"tipo": t, "label": spec["label"], "provider": spec["provider"], "auth": spec["auth"],
             "base_url": spec["base_url"], "nota": spec["nota"]}
            for t, spec in CATALOGO.items()
        ],
    }


@router.post("/llm/providers", status_code=201)
async def aggiungi(
    payload: FornitoreNuovo, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    spec = CATALOGO[payload.tipo]
    fornitore = LlmProvider(
        nome=payload.nome.strip(), tipo=payload.tipo, provider=spec["provider"],
        base_url=(payload.base_url or spec.get("base_url") or "").strip(),
        model=payload.model.strip(), embed_model=payload.embed_model.strip(),
        api_key_cifrata=cifra(payload.api_key), motore=payload.motore.strip(), ragiona=payload.ragiona,
        parametri=payload.parametri, senza_filtri=payload.senza_filtri,
        descrizione=payload.descrizione.strip(), attivo=payload.attivo, updated_by=user.id,
    )
    session.add(fornitore)
    try:
        await session.flush()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=409, detail=f"Esiste già un fornitore con nome «{payload.nome}».") from exc
    await AuditRepository(session).record(
        action="llm_provider.crea", actor_id=user.id, target_type="llm_provider",
        target_id=str(fornitore.id), after=pubblico(fornitore), ip=_ip(request),
    )
    await session.commit()
    await aggiorna_assegnazioni(session, forza=True)
    return pubblico(fornitore)


@router.put("/llm/providers/{id_fornitore}")
async def modifica(
    id_fornitore: int, payload: FornitoreModifica, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    fornitore = await session.get(LlmProvider, id_fornitore)
    if fornitore is None:
        raise HTTPException(status_code=404, detail="Fornitore non trovato")
    prima = pubblico(fornitore)

    campi = payload.model_dump(exclude_unset=True)
    for campo in ("base_url", "model", "embed_model", "motore", "descrizione"):
        if campo in campi:
            setattr(fornitore, campo, (campi[campo] or "").strip())
    for campo in ("ragiona", "senza_filtri", "attivo", "parametri"):
        if campo in campi:
            setattr(fornitore, campo, campi[campo])
    if "api_key" in campi:
        fornitore.api_key_cifrata = cifra(campi["api_key"])
    fornitore.updated_by = user.id

    await AuditRepository(session).record(
        action="llm_provider.modifica", actor_id=user.id, target_type="llm_provider",
        target_id=str(fornitore.id), before=prima, after=pubblico(fornitore), ip=_ip(request),
    )
    await session.commit()
    await aggiorna_assegnazioni(session, forza=True)
    return pubblico(fornitore)


@router.delete("/llm/providers/{id_fornitore}", status_code=204)
async def elimina(id_fornitore: int, request: Request, user: CurrentUser, session: DbSession) -> Response:
    fornitore = await session.get(LlmProvider, id_fornitore)
    if fornitore is None:
        raise HTTPException(status_code=404, detail="Fornitore non trovato")
    prima = pubblico(fornitore)
    await session.delete(fornitore)
    await AuditRepository(session).record(
        action="llm_provider.elimina", actor_id=user.id, target_type="llm_provider",
        target_id=str(id_fornitore), before=prima, ip=_ip(request),
    )
    await session.commit()
    await aggiorna_assegnazioni(session, forza=True)
    return Response(status_code=204)


class RispostaProva(BaseModel):
    ok: bool
    modelli: List[str] = Field(default_factory=list)
    errore: Optional[str] = None


@router.post("/llm/providers/{id_fornitore}/prova", response_model=RispostaProva)
async def prova(id_fornitore: int, session: DbSession) -> RispostaProva:
    """Prova la connessione: chiede al fornitore l'elenco dei suoi modelli, con la chiave che ha in questo momento.

    Non salva nulla e non passa dalla cache dei fornitori in uso: è una lettura isolata, così una chiave sbagliata
    non intacca ciò che le letture in corso stanno già usando.
    """
    fornitore = await session.get(LlmProvider, id_fornitore)
    if fornitore is None:
        raise HTTPException(status_code=404, detail="Fornitore non trovato")

    from ...llm.cifratura import decifra

    chiave = decifra(fornitore.api_key_cifrata)
    try:
        if fornitore.provider == "anthropic":
            from ...llm.anthropic import AnthropicProvider

            client = AnthropicProvider(base_url=fornitore.base_url or None, api_key=chiave or None)
        else:
            from ...llm.openai_compatible import OpenAICompatibleProvider

            client = OpenAICompatibleProvider(base_url=fornitore.base_url or None, api_key=chiave or None)
        modelli = await client.available_models()
    except Exception as exc:  # noqa: BLE001 - qualunque errore di rete o del server è un esito da mostrare, non da far esplodere
        return RispostaProva(ok=False, errore=str(exc)[:300])
    return RispostaProva(ok=True, modelli=modelli[:20])
