"""La console degli analytics (v8): catalogo, interrogazioni, imbuti, coorti.

Solo amministratori. Nessun SQL arriva da fuori: la console compone interrogazioni con i nomi del
catalogo (`analytics/catalogo.py`), e un nome sconosciuto è un 422. Ogni query ha un tempo massimo.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Literal, Optional
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import HTMLResponse
from lanterna import colab
from lanterna.analisi import coorti, imbuto
from lanterna.esporta import csv_da, xlsx_da
from lanterna.interroga import ErroreInterrogazione, Interrogazione, descrivi, esegui, limiti
from pydantic import BaseModel, Field
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import DBAPIError

from ...analytics import ai, catalogo, imbuti, rapporto, viste
from ...auth.dependencies import CurrentUser, DbSession, require_role
from ...domain.analytics_models import TABELLE

router = APIRouter(prefix="/admin/analytics", tags=["analytics"], dependencies=[Depends(require_role("admin"))])

FUSO = "Europe/Rome"


def _errore(exc: Exception) -> HTTPException:
    if isinstance(exc, DBAPIError) and "statement timeout" in str(exc).lower():
        return HTTPException(status_code=422, detail="L'interrogazione è troppo pesante: restringi l'intervallo o le dimensioni.")
    return HTTPException(status_code=422, detail=str(exc))


@router.get("/catalogo")
async def leggi_catalogo() -> Dict[str, Any]:
    return {
        "sorgenti": descrivi(catalogo.CATALOGO),
        "imbuti": imbuti.descrivi(),
        "coorti": {nome: {"etichetta": etichetta} for nome, (etichetta, _, _) in catalogo.COORTI.items()},
    }


@router.post("/interroga")
async def interroga(q: Interrogazione, session: DbSession) -> Dict[str, Any]:
    try:
        risultato = await esegui(session, catalogo.CATALOGO, q, fuso=FUSO)
    except (ErroreInterrogazione, DBAPIError) as exc:
        await session.rollback()
        raise _errore(exc) from exc
    return risultato.json()


class RichiestaImbuto(BaseModel):
    imbuto: str = Field(max_length=40)
    da: date
    a: date
    entro_ore: Optional[int] = Field(default=None, ge=1, le=24 * 60)
    segmento: Optional[str] = Field(default=None, max_length=40)


@router.post("/imbuto")
async def calcola_imbuto(r: RichiestaImbuto, session: DbSession) -> Dict[str, Any]:
    if r.imbuto not in imbuti.IMBUTI:
        raise HTTPException(status_code=422, detail=f"imbuto sconosciuto: {r.imbuto}")
    if r.a < r.da or (r.a - r.da).days > 366:
        raise HTTPException(status_code=422, detail="intervallo non valido (massimo un anno)")
    etichetta, per, passi = imbuti.IMBUTI[r.imbuto]
    inizio, fine = limiti(r.da, r.a, FUSO)
    try:
        esito = await imbuto(
            session, TABELLE, passi, inizio, fine, per=per, entro_ore=r.entro_ore,
            segmento=r.segmento if per == "sessione" else None,
        )
    except (ValueError, DBAPIError) as exc:
        await session.rollback()
        raise _errore(exc) from exc
    return {"imbuto": r.imbuto, "etichetta": etichetta, "per": per, "da": r.da.isoformat(), "a": r.a.isoformat(), **esito}


class RichiestaCoorti(BaseModel):
    tipo: str = Field(max_length=40)
    granularita: Literal["settimana", "mese"] = "mese"
    periodi: int = Field(default=12, ge=1, le=36)
    da: Optional[date] = None


@router.post("/coorti")
async def calcola_coorti(r: RichiestaCoorti, session: DbSession) -> Dict[str, Any]:
    if r.tipo not in catalogo.COORTI:
        raise HTTPException(status_code=422, detail=f"coorte sconosciuta: {r.tipo}")
    etichetta, attivita, somma = catalogo.COORTI[r.tipo]
    primo = catalogo.primo_iscrizione()
    if r.da is not None:
        primo = primo.where(catalogo.UT.c.created_at >= limiti(r.da, r.da, FUSO)[0])
    try:
        righe: List[Dict[str, Any]] = await coorti(
            session, primo, attivita(), granularita=r.granularita, periodi=r.periodi, somma=somma, fuso=FUSO,
        )
    except DBAPIError as exc:
        await session.rollback()
        raise _errore(exc) from exc
    return {"tipo": r.tipo, "etichetta": etichetta, "granularita": r.granularita, "somma": somma, "coorti": righe}


# ---- export (F5) ---------------------------------------------------------------------------


def _file(contenuto: bytes, nome: str, formato: str) -> Response:
    tipo = "text/csv; charset=utf-8" if formato == "csv" else (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    return Response(
        content=contenuto, media_type=tipo,
        headers={"Content-Disposition": f'attachment; filename="{nome}.{formato}"', "Cache-Control": "no-store"},
    )


@router.post("/esporta")
async def esporta_vista(
    q: Interrogazione, session: DbSession, formato: Literal["csv", "xlsx"] = Query(default="csv"),
) -> Response:
    """La vista corrente della console, così com'è (stesse righe, stessi totali)."""
    try:
        risultato = await esegui(session, catalogo.CATALOGO, q, fuso=FUSO)
    except (ErroreInterrogazione, DBAPIError) as exc:
        await session.rollback()
        raise _errore(exc) from exc
    nome = f"tarots-{q.sorgente}-{q.da.isoformat()}-{q.a.isoformat()}"
    if formato == "csv":
        return _file(csv_da(risultato), nome, "csv")
    return _file(xlsx_da([(catalogo.CATALOGO[q.sorgente].etichetta, risultato, "")]), nome, "xlsx")


@router.get("/collezioni")
async def elenco_collezioni() -> Dict[str, Any]:
    return {nome: {"etichetta": etichetta} for nome, (etichetta, _) in viste.COLLEZIONI.items()}


async def collezione_xlsx(session, nome: str, da: date, a: date, *, k_minimo: Optional[int] = None) -> bytes:
    """Un file Excel con un foglio per interrogazione della collezione."""
    _, costruisci = viste.COLLEZIONI[nome]
    fogli = []
    for titolo, q, descrizione in costruisci(da, a):
        fogli.append((titolo, await esegui(session, catalogo.CATALOGO, q, fuso=FUSO, k_minimo=k_minimo), descrizione))
    return xlsx_da(fogli)


# ---- interpretazione AI (F6) -----------------------------------------------------------------


class RichiestaAnalisi(BaseModel):
    sezione: str = Field(max_length=40)
    giorni: int = Field(default=30, ge=1, le=366)
    vista: Optional[Interrogazione] = None


@router.post("/analizza")
async def chiedi_analisi(r: RichiestaAnalisi, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    """Una chiamata al modello scelto per `analisi_dati`, sui fatti calcolati per la sezione."""
    from ...llm.base import GenerationError
    from ...llm.compiti import Compito
    from ..deps import aggiorna_assegnazioni, provider_per

    await aggiorna_assegnazioni(session)
    try:
        return await ai.analizza(session, provider_per(Compito.ANALISI_DATI), sezione=r.sezione, giorni=r.giorni,
                                 vista=r.vista, autore_id=user.id)
    except (ValueError, ErroreInterrogazione, DBAPIError) as exc:
        await session.rollback()
        raise _errore(exc) from exc
    except GenerationError as exc:
        raise HTTPException(status_code=503, detail=f"Il modello non ha risposto in modo utilizzabile: {exc}") from exc


@router.get("/analisi")
async def elenco_analisi(session: DbSession, sezione: Optional[str] = Query(default=None, max_length=40),
                         limite: int = Query(default=20, ge=1, le=100)) -> List[Dict[str, Any]]:
    return await ai.storico(session, sezione, limite)


class Annotazione(BaseModel):
    giudizio: Optional[Literal[-1, 1]] = None
    azione_adottata: Optional[str] = Field(default=None, max_length=1000)


@router.patch("/analisi/{analisi_id}")
async def annota_analisi(analisi_id: uuid.UUID, a: Annotazione, session: DbSession) -> Dict[str, Any]:
    riga = await ai.annota(session, analisi_id, giudizio=a.giudizio, azione=a.azione_adottata,
                           campi=a.model_fields_set)
    if riga is None:
        raise HTTPException(status_code=404, detail="Analisi non trovata")
    return riga


class Impostazioni(BaseModel):
    contesto_ai: str = Field(default="", max_length=4000)


@router.get("/impostazioni")
async def leggi_impostazioni(session: DbSession) -> Dict[str, Any]:
    return {"contesto_ai": await ai.leggi_contesto(session)}


@router.put("/impostazioni")
async def scrivi_impostazioni(i: Impostazioni, session: DbSession) -> Dict[str, Any]:
    await ai.scrivi_contesto(session, i.contesto_ai)
    await session.commit()
    return {"contesto_ai": await ai.leggi_contesto(session)}


# ---- rapporto settimanale (F7) -----------------------------------------------------------------


class NuovoDestinatario(BaseModel):
    email: str = Field(min_length=3, max_length=320, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@router.get("/rapporto")
async def stato_rapporto(session: DbSession) -> Dict[str, Any]:
    d, i = TABELLE.destinatari, TABELLE.invii
    destinatari = (await session.execute(select(d).order_by(d.c.email))).mappings().all()
    invii = (await session.execute(select(i).order_by(i.c.created_at.desc()).limit(20))).mappings().all()
    da, a = rapporto.settimana_conclusa()
    return {
        "smtp_configurato": rapporto.config_smtp().configurato,
        "opzioni": await rapporto.opzioni(session),
        "prossima_settimana": {"da": da.isoformat(), "a": a.isoformat()},
        "destinatari": [{"id": x["id"], "email": x["email"], "attivo": x["attivo"]} for x in destinatari],
        "invii": [{**{k: x[k] for k in ("tipo", "destinatari", "riuscito", "dettaglio", "manuale")},
                   "id": str(x["id"]), "da": x["da"].isoformat(), "a": x["a"].isoformat(),
                   "creato_il": x["created_at"].isoformat()} for x in invii],
    }


@router.post("/rapporto/destinatari", status_code=201)
async def aggiungi_destinatario(n: NuovoDestinatario, session: DbSession) -> Dict[str, Any]:
    d = TABELLE.destinatari
    email = n.email.strip().lower()
    await session.execute(pg_insert(d).values(email=email).on_conflict_do_update(index_elements=[d.c.email], set_={"attivo": True}))
    await session.commit()
    return {"email": email}


@router.delete("/rapporto/destinatari/{destinatario_id}", status_code=204)
async def togli_destinatario(destinatario_id: int, session: DbSession) -> Response:
    d = TABELLE.destinatari
    await session.execute(delete(d).where(d.c.id == destinatario_id))
    await session.commit()
    return Response(status_code=204)


class OpzioniRapporto(BaseModel):
    ai: bool = False


@router.put("/rapporto/opzioni")
async def imposta_opzioni_rapporto(o: OpzioniRapporto, session: DbSession) -> Dict[str, Any]:
    await rapporto.scrivi_opzioni(session, o.model_dump())
    await session.commit()
    return await rapporto.opzioni(session)


@router.get("/rapporto/anteprima", response_class=HTMLResponse)
async def anteprima_rapporto(session: DbSession) -> HTMLResponse:
    """L'HTML del rapporto della settimana conclusa, senza interpretazione AI (nessun costo)."""
    da, a = rapporto.settimana_conclusa()
    contenuto = await rapporto.componi_rapporto(session, da, a, con_ai=False)
    return HTMLResponse(contenuto["html"])


@router.post("/rapporto/invia")
async def invia_rapporto_ora(session: DbSession) -> Dict[str, Any]:
    """Lo stesso invio del lunedì notte, subito, a tutti i destinatari attivi."""
    from ...llm.compiti import Compito
    from ..deps import aggiorna_assegnazioni, provider_per

    await aggiorna_assegnazioni(session)
    return await rapporto.invia_rapporto(session, manuale=True, provider=provider_per(Compito.ANALISI_DATI))


# ---- Colab: token, risultati, notebook (F8) ---------------------------------------------------------


class NuovoToken(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    giorni: int = Field(default=30, ge=1, le=365)
    ambiti: List[Literal["esporta", "importa"]] = Field(default_factory=lambda: ["esporta", "importa"])


@router.get("/studi")
async def studi(session: DbSession) -> Dict[str, Any]:
    t, r = TABELLE.token, TABELLE.importati
    token = (await session.execute(select(t).order_by(t.c.created_at.desc()).limit(50))).mappings().all()
    risultati = (await session.execute(select(r).order_by(r.c.created_at.desc()).limit(50))).mappings().all()
    return {
        "collezioni": {n: e for n, (e, _) in viste.COLLEZIONI.items()},
        "token": [{"id": str(x["id"]), "nome": x["nome"], "ambiti": x["ambiti"], "scade_il": x["scade_il"].isoformat(),
                   "revocato_il": x["revocato_il"].isoformat() if x["revocato_il"] else None,
                   "ultimo_uso": x["ultimo_uso"].isoformat() if x["ultimo_uso"] else None} for x in token],
        "risultati": [{"id": str(x["id"]), "titolo": x["titolo"], "descrizione": x["descrizione"], "colonne": x["colonne"],
                       "righe": x["righe"][:200], "totale_righe": len(x["righe"]),
                       "creato_il": x["created_at"].isoformat()} for x in risultati],
    }


@router.post("/studi/token", status_code=201)
async def crea_token(n: NuovoToken, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    """Il token si mostra solo qui: nel database ne resta l'impronta."""
    creato = await colab.crea_token(session, TABELLE, nome=n.nome, giorni=n.giorni, ambiti=list(n.ambiti), autore_id=user.id)
    await session.commit()
    return creato


@router.delete("/studi/token/{token_id}", status_code=204)
async def revoca_token(token_id: uuid.UUID, session: DbSession) -> Response:
    await colab.revoca(session, TABELLE, token_id)
    await session.commit()
    return Response(status_code=204)


@router.delete("/studi/risultati/{risultato_id}", status_code=204)
async def togli_risultato(risultato_id: uuid.UUID, session: DbSession) -> Response:
    await session.execute(delete(TABELLE.importati).where(TABELLE.importati.c.id == risultato_id))
    await session.commit()
    return Response(status_code=204)


@router.get("/studi/notebook.ipynb")
async def scarica_notebook(
    collezione: str = Query(default="traffico", max_length=40), giorni: int = Query(default=90, ge=1, le=366),
) -> Response:
    from ...settings import get_settings

    if collezione not in viste.COLLEZIONI:
        raise HTTPException(status_code=404, detail="Collezione sconosciuta")
    etichetta, _ = viste.COLLEZIONI[collezione]
    testo = colab.notebook(api=get_settings().api_public_url.rstrip("/"), collezione=collezione,
                           titolo=f"TAROTS chat — {etichetta}", giorni=giorni)
    return Response(content=testo.encode("utf-8"), media_type="application/x-ipynb+json",
                    headers={"Content-Disposition": f'attachment; filename="tarots-{collezione}.ipynb"'})


@router.get("/collezioni/{nome}.xlsx")
async def esporta_collezione(nome: str, session: DbSession, giorni: int = Query(default=30, ge=1, le=366)) -> Response:
    if nome not in viste.COLLEZIONI:
        raise HTTPException(status_code=404, detail="Collezione sconosciuta")
    a = datetime.now(ZoneInfo(FUSO)).date()
    da = a - timedelta(days=giorni - 1)
    try:
        contenuto = await collezione_xlsx(session, nome, da, a)
    except (ErroreInterrogazione, DBAPIError) as exc:
        await session.rollback()
        raise _errore(exc) from exc
    return _file(contenuto, f"tarots-{nome}-{da.isoformat()}-{a.isoformat()}", "xlsx")
