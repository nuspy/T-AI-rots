"""Google dalla console (v8.6): la procedura guidata del service account, la verifica, le statistiche GA4, e l'ID di
misurazione che il sito legge per caricare il contatore (solo col consenso ai cookie).

Il JSON del service account entra una volta (`POST /credenziali`) e non esce più: le risposte portano l'email del
service account, il progetto e gli ultimi caratteri dell'id della chiave, mai la chiave.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from pydantic import BaseModel, Field

from ...auth.dependencies import COOKIE_ANONIMO, CurrentUser, DbSession, OptionalUser, require_role
from ...domain import consent_repositories
from ...domain.repositories import AuditRepository
from ...tarot import google

router = APIRouter(prefix="/admin/google", tags=["google"], dependencies=[Depends(require_role("admin"))])
#: Pubblico, senza account: il sito chiede qui se c'è un contatore di Google da caricare (col consenso).
router_pubblico = APIRouter(tags=["google"])


@router.get("")
async def stato(session: DbSession) -> Dict[str, Any]:
    return google.stato_json(await google.config(session))


class CredenzialiIn(BaseModel):
    #: Il contenuto del file .json del service account, letto dal browser.
    json_service_account: str = Field(min_length=20, max_length=20_000)


@router.post("/credenziali")
async def carica_credenziali(payload: CredenzialiIn, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    try:
        riga = await google.salva_credenziali(session, payload.json_service_account, autore_id=user.id)
    except google.ErroreGoogle as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    await AuditRepository(session).record(
        action="google.credenziali", actor_id=user.id, target_type="config_google", target_id="1",
        after={"client_email": riga.client_email, "project_id": riga.project_id},
    )
    await session.commit()
    return google.stato_json(riga)


@router.delete("/credenziali")
async def togli_credenziali(user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    riga = await google.togli_credenziali(session, autore_id=user.id)
    await AuditRepository(session).record(
        action="google.credenziali.togli", actor_id=user.id, target_type="config_google", target_id="1",
    )
    await session.commit()
    return google.stato_json(riga)


class ImpostazioniGoogleIn(BaseModel):
    #: Stringa vuota: si torna al valore predefinito (quello dell'ambiente, o `sc-domain:<dominio>`).
    sc_proprieta: Optional[str] = Field(default=None, max_length=300)
    ga4_proprieta_id: Optional[str] = Field(default=None, max_length=20)
    ga4_misurazione_id: Optional[str] = Field(default=None, max_length=20)


@router.put("/impostazioni")
async def imposta(payload: ImpostazioniGoogleIn, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    dati = payload.model_dump(exclude_unset=True)
    riga = await google.config_o_nuova(session)
    if "sc_proprieta" in dati:
        valore = (dati["sc_proprieta"] or "").strip()
        if valore and not google.PROPRIETA_SC.match(valore):
            raise HTTPException(status_code=422, detail=(
                "Proprietà Search Console non valida: «sc-domain:tarots.chat» (dominio) oppure "
                "«https://tarots.chat/» (prefisso URL, con la barra finale)."))
        riga.sc_proprieta = valore or None
    if "ga4_proprieta_id" in dati:
        valore = (dati["ga4_proprieta_id"] or "").strip().removeprefix("properties/")
        if valore and not google.PROPRIETA_GA4.match(valore):
            raise HTTPException(status_code=422, detail=(
                "L'ID della proprietà GA4 è un numero (Amministrazione → Dettagli proprietà), non l'ID G-…"))
        riga.ga4_proprieta_id = valore or None
    if "ga4_misurazione_id" in dati:
        valore = (dati["ga4_misurazione_id"] or "").strip().upper()
        if valore and not google.MISURAZIONE.match(valore):
            raise HTTPException(status_code=422, detail=(
                "L'ID di misurazione comincia con «G-» (Amministrazione → Stream di dati → il flusso web)."))
        riga.ga4_misurazione_id = valore or None
    riga.updated_by = user.id
    await AuditRepository(session).record(
        action="google.impostazioni", actor_id=user.id, target_type="config_google", target_id="1",
        after={"sc_proprieta": riga.sc_proprieta, "ga4_proprieta_id": riga.ga4_proprieta_id,
               "ga4_misurazione_id": riga.ga4_misurazione_id},
    )
    await session.commit()
    return google.stato_json(riga)


@router.post("/verifica")
async def verifica(user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    """Prova ogni passo (chiave, Search Console, sitemap, GA4, contatore) e dice quale manca."""
    passi = await google.verifica(session)
    await AuditRepository(session).record(
        action="google.verifica", actor_id=user.id, target_type="config_google", target_id="1",
        after={k: bool(v.get("ok")) for k, v in passi.items()},
    )
    await session.commit()
    return google.stato_json(await google.config(session))


@router.get("/statistiche")
async def statistiche(session: DbSession, giorni: int = Query(default=30, ge=1, le=366)) -> Dict[str, Any]:
    """Le statistiche principali di GA4. Se qualcosa manca, `pronto: false` e cosa manca (non un errore: la console
    guida la configurazione)."""
    riga = await google.config(session)
    cred = google.credenziali_di(riga)
    mancano = []
    if cred is None:
        mancano.append("le credenziali del service account")
    if not (riga and riga.ga4_proprieta_id):
        mancano.append("l'ID della proprietà GA4")
    if mancano:
        return {"pronto": False, "mancano": mancano, "misurazione": riga.ga4_misurazione_id if riga else None}
    try:
        dati = await google.statistiche_ga4(cred, riga.ga4_proprieta_id, giorni)
    except google.ErroreGoogle as exc:
        return {"pronto": False, "errore": str(exc), "mancano": [], "misurazione": riga.ga4_misurazione_id}
    return {"pronto": True, "misurazione": riga.ga4_misurazione_id, "proprieta": riga.ga4_proprieta_id, **dati}


#: Dalla versione 2 l'informativa nomina Google Analytics: solo un «accettato» dato su quel testo lo accende. Chi
#: aveva accettato la versione 1 (che parlava solo dell'identificativo di lanterna) deve scegliere di nuovo.
VERSIONE_INFORMATIVA_GOOGLE = 2


def _numero_versione(versione: Optional[str]) -> int:
    try:
        return int(str(versione or "").lower().lstrip("v").split(".")[0])
    except ValueError:
        return 0


@router_pubblico.get("/consenso-google")
async def consenso_google(request: Request, response: Response, session: DbSession, user: OptionalUser) -> Dict[str, bool]:
    """Se questo browser (o account) ha acconsentito a Google Analytics: un «accettato» su `google_analytics` (dalla
    Fase 1 del GDPR un consenso a sé; chi aveva accettato i cookie è stato convertito con la versione del testo di
    allora) dato su un'informativa che lo nomina. `da_rinnovare`: aveva accettato un testo precedente, il banner deve
    ricomparire."""
    response.headers["Cache-Control"] = "no-store"
    anon_id = None if user else request.cookies.get(COOKIE_ANONIMO)
    correnti = await consent_repositories.correnti_per(session, user_id=user.id if user else None, anon_id=anon_id)
    cookie = correnti.get("google_analytics")
    accettato = cookie is not None and cookie.valore == "accettato"
    attuale = accettato and _numero_versione(cookie.versione_informativa) >= VERSIONE_INFORMATIVA_GOOGLE
    return {"attivo": attuale, "da_rinnovare": accettato and not attuale}


@router_pubblico.get("/impostazioni-google")
async def impostazioni_google(session: DbSession, response: Response) -> Dict[str, Optional[str]]:
    """L'ID di misurazione GA4 (pubblico per natura: sta in ogni pagina che carica il contatore). Il sito lo usa solo
    dopo il consenso ai cookie."""
    riga = await google.config(session)
    response.headers["Cache-Control"] = "public, max-age=300"
    return {"ga4_misurazione_id": riga.ga4_misurazione_id if riga else None}
