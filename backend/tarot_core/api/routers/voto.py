"""Vota il prossimo mazzo (v7, Fase K): la tornata aperta e il voto, per chi ha un account.

Le statistiche (percentuali) si mostrano solo a chi ha già votato in questa tornata — mai prima,
per non influenzare la scelta: è esplicito nel backlog ("statistiche in % dopo votazione").

**"Tornate elettorali" (estensione)**: una tornata ha una scadenza dichiarata alla creazione
(`chiude_il`, console) e si chiude da sola — nessun processo separato: ogni lettura pubblica di
questo router prova prima a chiudere le tornate scadute (`voting_repositories.chiudi_tornate_scadute`),
cosi' chi arriva anche solo un istante dopo la scadenza vede già lo stato corretto."""
from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ...analytics import eventi as analytics
from ...auth.dependencies import CurrentUser, DbSession
from ...domain import voting_repositories
from ...domain.repositories import AuditRepository
from ...domain.voting_models import DeckSuggestion
from .blog import url_immagine, url_miniatura

router = APIRouter(prefix="/voto", tags=["voto"])


def _campioni_json(campioni: List[Dict[str, Any]]) -> List[Dict[str, Optional[str]]]:
    """Le carte d'esempio (al massimo cinque, nell'ordine scelto in console): `url` la grande, per l'ingrandimento;
    `mini` la miniatura, per l'elenco."""
    return [
        {
            "etichetta": c.get("etichetta"),
            "url": url_immagine(uuid.UUID(c["media_id"])) if c.get("media_id") else None,
            "mini": url_miniatura(uuid.UUID(c["media_id"])) if c.get("media_id") else None,
        }
        for c in campioni
    ]


async def _forse_chiudi_scadute(session: DbSession) -> None:
    if await voting_repositories.chiudi_tornate_scadute(session):
        await session.commit()


@router.get("/home")
async def voto_home(session: DbSession) -> Dict[str, Any]:
    """Il riepilogo per la home page: pubblico, senza autenticazione, perché deve essere visibile
    anche a chi non ha un account. `risultato_recente` porta OGNI candidato dell'ultima tornata
    chiusa (non solo i vincitori accettati) con le sue miniature — «i mazzi votati», non solo quello
    scelto — per il riquadro con le thumbnail ingrandibili in home."""
    await _forse_chiudi_scadute(session)

    aperta = await voting_repositories.tornata_aperta(session)
    risultato_recente: Optional[Dict[str, Any]] = None
    chiusa = await voting_repositories.ultima_tornata_chiusa(session)
    if chiusa is not None:
        candidati = await voting_repositories.candidati_di(session, chiusa.id)
        conteggi = await voting_repositories.conteggio_per_candidato(session, chiusa.id)
        totale = sum(conteggi.values())
        if totale:
            risultato_recente = {
                "chiusa_il": chiusa.chiusa_il.isoformat() if chiusa.chiusa_il else None,
                "candidati": [
                    {
                        "nome": c.nome,
                        "percentuale": round(100 * conteggi.get(c.id, 0) / totale),
                        "campioni": _campioni_json(c.campioni),
                    }
                    for c in candidati
                ],
            }

    return {"voto_aperto": aperta is not None, "risultato_recente": risultato_recente}


@router.get("/mazzi")
async def stato_voto(user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    await _forse_chiudi_scadute(session)
    tornata = await voting_repositories.tornata_aperta(session)
    risposta: Dict[str, Any] = {"tornata": None, "candidati": [], "vincitori_precedenti": None}

    if tornata is not None:
        candidati = await voting_repositories.candidati_di(session, tornata.id)
        voto = await voting_repositories.voto_di(session, tornata.id, user.id)
        conteggi = await voting_repositories.conteggio_per_candidato(session, tornata.id) if voto else {}
        totale_voti = sum(conteggi.values()) if conteggi else 0
        risposta["tornata"] = {"id": str(tornata.id)}
        risposta["mio_voto"] = str(voto.candidate_id) if voto else None
        risposta["candidati"] = [
            {
                "id": str(c.id), "nome": c.nome, "descrizione": c.descrizione,
                "campioni": _campioni_json(c.campioni),
                "percentuale": (
                    round(100 * conteggi.get(c.id, 0) / totale_voti) if voto and totale_voti else None
                ),
            }
            for c in candidati
        ]

    precedente = await voting_repositories.ultima_tornata_chiusa(session)
    if precedente is not None:
        candidati_precedenti = await voting_repositories.candidati_di(session, precedente.id)
        conteggi_precedenti = await voting_repositories.conteggio_per_candidato(session, precedente.id)
        totale_precedente = sum(conteggi_precedenti.values())
        vincitori = [c for c in candidati_precedenti if c.accettato]
        if vincitori and totale_precedente:
            risposta["vincitori_precedenti"] = [
                {
                    "nome": c.nome,
                    "percentuale": round(100 * conteggi_precedenti.get(c.id, 0) / totale_precedente),
                }
                for c in vincitori
            ]

    return risposta


@router.post("/mazzi/{candidate_id}")
async def vota(candidate_id: uuid.UUID, user: CurrentUser, session: DbSession) -> Dict[str, str]:
    await _forse_chiudi_scadute(session)
    tornata = await voting_repositories.tornata_aperta(session)
    if tornata is None:
        raise HTTPException(status_code=409, detail="Nessuna votazione è aperta al momento")
    candidati = await voting_repositories.candidati_di(session, tornata.id)
    if candidate_id not in {c.id for c in candidati}:
        raise HTTPException(status_code=404, detail="Candidato non trovato in questa tornata")
    await voting_repositories.vota(session, round_id=tornata.id, candidate_id=candidate_id, user_id=user.id)
    await analytics.evento(session, analytics.VOTO_MAZZO, utente_id=user.id)
    await session.commit()
    return {"esito": "ok"}


# ---- suggerisci un tema (estensione: per gli iscritti) ----------------------------------------------


class SuggerimentoIn(BaseModel):
    testo: str = Field(min_length=3, max_length=1000)


@router.post("/suggerimenti", status_code=201)
async def suggerisci_tema(payload: SuggerimentoIn, user: CurrentUser, session: DbSession) -> Dict[str, str]:
    """Un iscritto propone liberamente un tema per un futuro mazzo — testo libero, non ancora una
    proposta rifinita: l'admin la rivede in console e decide se trasformarla in una candidata vera
    per la riserva (`GET/POST /admin/voto/suggerimenti`)."""
    suggerimento = DeckSuggestion(user_id=user.id, testo=payload.testo.strip())
    session.add(suggerimento)
    await session.flush()
    await AuditRepository(session).record(
        action="voto.suggerimento.crea", actor_id=user.id, target_type="deck_suggestion", target_id=str(suggerimento.id),
    )
    await session.commit()
    return {"esito": "ok"}
