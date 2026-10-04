"""La pubblicità dalla console («Advertisements»): l'interruttore generale, le caselle dei tre banner, i parametri di
Google AdSense, i dati dell'iscrizione e gli appunti sul profilo pagamenti; dal lato pubblico, ciò che serve al sito e
`ads.txt`.

Ogni scrittura finisce nel registro di audit (`domain/pubblicita_repositories.py`). Il sito legge
`/impostazioni-pubblicita`: solo interruttore effettivo, slot, formati e caselle — mai i dati di registrazione.
"""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import PlainTextResponse
from lanterna.rete import ip_client
from pydantic import BaseModel, Field

from ...auth.dependencies import CurrentUser, DbSession, require_role
from ...domain import pubblicita_repositories as pubblicita

router = APIRouter(prefix="/admin/pubblicita", tags=["pubblicita"], dependencies=[Depends(require_role("admin"))])
#: Pubblico, senza account: il sito chiede qui se ci sono spazi da mostrare, e `ads.txt`.
router_pubblico = APIRouter(tags=["pubblicita"])

Posizione = Literal["terzo", "due_terzi", "fine"]
Formato = Literal["auto", "rectangle", "horizontal", "vertical"]
Stato = Literal["non_iniziata", "ads_txt_verificato", "in_revisione", "approvato", "rifiutato"]


async def _vista(session) -> Dict[str, Any]:
    gen = await pubblicita.generali(session)
    google = await pubblicita.fornitore(session, "google")
    return {
        "generale": pubblicita.vista_generale(gen),
        "fornitori": {"google": pubblicita.vista_google(google)},
        "catalogo": {
            "fornitori": [{"chiave": k, **v} for k, v in pubblicita.FORNITORI.items()],
            "posizioni": list(pubblicita.POSIZIONI),
            "formati": list(pubblicita.FORMATI),
            "stati_registrazione": list(pubblicita.STATI_REGISTRAZIONE),
        },
        #: Ciò che vede il sito adesso, per l'anteprima della console.
        "pubblico": pubblicita.vista_pubblica(gen, google),
    }


@router.get("")
async def leggi(session: DbSession) -> Dict[str, Any]:
    return await _vista(session)


class GeneraliIn(BaseModel):
    attiva: Optional[bool] = None
    fornitore: Optional[str] = Field(default=None, max_length=40)
    posizioni: Optional[Dict[Posizione, bool]] = None
    pagine_escluse: Optional[List[str]] = Field(default=None, max_length=50)


@router.put("")
async def modifica(payload: GeneraliIn, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    try:
        await pubblicita.aggiorna_generali(
            session, payload.model_dump(exclude_unset=True), attore_id=user.id, ip=ip_client(request),
        )
    except pubblicita.ErrorePubblicita as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    await session.commit()
    return await _vista(session)


class ParametriGoogleIn(BaseModel):
    editore: Optional[str] = Field(default=None, max_length=40)
    slot: Optional[Dict[Posizione, Optional[str]]] = None
    formato: Optional[Dict[Posizione, Formato]] = None
    responsive: Optional[bool] = None
    prova: Optional[bool] = None
    personalizzati: Optional[bool] = None


class RegistrazioneGoogleIn(BaseModel):
    email: Optional[str] = Field(default=None, max_length=200)
    titolare: Optional[str] = Field(default=None, max_length=200)
    id_cliente: Optional[str] = Field(default=None, max_length=60)
    data_iscrizione: Optional[date] = None
    stato: Optional[Stato] = None
    note: Optional[str] = Field(default=None, max_length=2000)


class GoogleIn(BaseModel):
    parametri: Optional[ParametriGoogleIn] = None
    registrazione: Optional[RegistrazioneGoogleIn] = None


@router.put("/fornitori/google")
async def modifica_google(payload: GoogleIn, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    parametri = payload.parametri.model_dump(exclude_unset=True) if payload.parametri else None
    registrazione = payload.registrazione.model_dump(exclude_unset=True, mode="json") if payload.registrazione else None
    try:
        await pubblicita.aggiorna_google(session, parametri, registrazione, attore_id=user.id, ip=ip_client(request))
    except pubblicita.ErrorePubblicita as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    await session.commit()
    return await _vista(session)


class PagamentiGoogleIn(BaseModel):
    """I dettagli del profilo pagamenti di AdSense, come appunti: il profilo vero sta in AdSense. Del conto, solo le
    ultime 4 cifre (la validazione vera, anche sui testi liberi, è in `aggiorna_pagamenti_google`)."""

    id_profilo: Optional[str] = Field(default=None, max_length=40)
    beneficiario: Optional[str] = Field(default=None, max_length=200)
    tipo_profilo: Optional[Literal["individuale", "azienda"]] = None
    indirizzo: Optional[str] = Field(default=None, max_length=500)
    metodo: Optional[Literal["bonifico", "bonifico_internazionale", "altro"]] = None
    banca: Optional[str] = Field(default=None, max_length=120)
    #: Al più 4 caratteri dopo aver tolto spazi e trattini: un IBAN intero si rifiuta.
    conto_ultime4: Optional[str] = Field(default=None, max_length=9)
    soglia: Optional[float] = Field(default=None, ge=0, le=1_000_000)
    valuta: Optional[str] = Field(default=None, max_length=3)
    stato_fiscale: Optional[Literal["non_inviate", "inviate", "accettate"]] = None
    modulo_fiscale: Optional[Literal["W-8BEN", "W-8BEN-E", "W-9", "altro"]] = None
    stato_pin: Optional[Literal["non_ricevuto", "ricevuto", "verificato"]] = None
    ultimo_pagamento: Optional[date] = None
    note: Optional[str] = Field(default=None, max_length=2000)


@router.put("/fornitori/google/pagamenti")
async def modifica_pagamenti_google(
    payload: PagamentiGoogleIn, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    try:
        await pubblicita.aggiorna_pagamenti_google(
            session, payload.model_dump(exclude_unset=True, mode="json"), attore_id=user.id, ip=ip_client(request),
        )
    except pubblicita.ErrorePubblicita as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    await session.commit()
    return await _vista(session)


@router_pubblico.get("/impostazioni-pubblicita")
async def impostazioni_pubblicita(session: DbSession, response: Response) -> Dict[str, Any]:
    """Gli spazi da mostrare: `{"attiva": false}` finché la console non li accende. Il sito carica gli annunci solo
    dopo il consenso alla pubblicità di chi guarda."""
    response.headers["Cache-Control"] = "public, max-age=60"
    return await pubblicita.leggi_pubblica(session)


@router_pubblico.get("/ads.txt", response_class=PlainTextResponse)
async def ads_txt(session: DbSession) -> PlainTextResponse:
    """La riga di AdSense per `ads.txt` (il sito la serve alla sua radice). 404 senza ID editore."""
    testo = await pubblicita.leggi_ads_txt(session)
    if testo is None:
        raise HTTPException(status_code=404, detail="Nessun ID editore impostato")
    return PlainTextResponse(testo, headers={"Cache-Control": "public, max-age=300"})
