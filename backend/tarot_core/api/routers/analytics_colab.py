"""Gli analytics per i notebook (v8, Colab): export delle collezioni e import dei risultati.

Autenticazione con un token creato in console (Analytics → Studi), non con Keycloak: un notebook
non fa il login. Il token ha una scadenza e degli ambiti; nel database ne resta solo l'impronta.

- `GET /analytics/export/{collezione}?giorni=N` (ambito `esporta`): i fogli della collezione come JSON,
  con la **soglia k** attiva (gruppi di meno di 5 persone esclusi): i dati escono dal sistema.
- `POST /analytics/importa` (ambito `importa`): un risultato da mostrare in console, con l'intestazione
  `X-Firma` = HMAC-SHA256 del corpo, usando il token come chiave.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Header, HTTPException, Query, Request
from lanterna import colab
from lanterna.interroga import esegui
from sqlalchemy.dialects.postgresql import insert

from ...analytics import catalogo, viste
from ...auth.dependencies import DbSession
from ...domain.analytics_models import TABELLE

router = APIRouter(prefix="/analytics", tags=["analytics-colab"])

FUSO = "Europe/Rome"
K_MINIMO = 5


def _bearer(authorization: Optional[str]) -> Optional[str]:
    if authorization and authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1].strip()
    return None


async def _token_o_401(session, authorization: Optional[str], ambito: str):
    riga = await colab.verifica_token(session, TABELLE, _bearer(authorization), ambito)
    if riga is None:
        raise HTTPException(status_code=401, detail="Token mancante, scaduto, revocato o senza questo permesso",
                            headers={"WWW-Authenticate": "Bearer"})
    return riga


@router.get("/export/{collezione}")
async def esporta(
    collezione: str, session: DbSession, giorni: int = Query(default=90, ge=1, le=366),
    authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    await _token_o_401(session, authorization, "esporta")
    if collezione not in viste.COLLEZIONI:
        raise HTTPException(status_code=404, detail="Collezione sconosciuta")
    a = datetime.now(ZoneInfo(FUSO)).date()
    da = a - timedelta(days=giorni - 1)
    etichetta, costruisci = viste.COLLEZIONI[collezione]
    fogli = []
    for titolo, q, descrizione in costruisci(da, a):
        r = await esegui(session, catalogo.CATALOGO, q, fuso=FUSO, k_minimo=K_MINIMO)
        fogli.append({
            "titolo": titolo, "descrizione": descrizione, "colonne": r.colonne,
            "righe": [[riga.get(c["nome"]) for c in r.colonne] for riga in r.righe],
            "totali": r.totali, "soppresse": r.soppresse,
        })
    await session.commit()  # l'ultimo uso del token
    return {"collezione": collezione, "etichetta": etichetta, "da": da.isoformat(), "a": a.isoformat(), "fogli": fogli}


@router.post("/importa", status_code=201)
async def importa(
    request: Request, session: DbSession,
    authorization: Optional[str] = Header(default=None), x_firma: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    riga_token = await _token_o_401(session, authorization, "importa")
    corpo = await request.body()
    if len(corpo) > 5_000_000:
        raise HTTPException(status_code=413, detail="Risultato troppo grande")
    if not colab.firma_valida(_bearer(authorization) or "", corpo, x_firma or ""):
        raise HTTPException(status_code=401, detail="Firma del risultato non valida")
    try:
        dati = colab.valida_import(json.loads(corpo))
    except (ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    nuovo = uuid.uuid4()
    await session.execute(insert(TABELLE.importati).values(id=nuovo, token_id=riga_token["id"], **dati))
    await session.commit()
    return {"id": str(nuovo), "righe": len(dati["righe"])}
