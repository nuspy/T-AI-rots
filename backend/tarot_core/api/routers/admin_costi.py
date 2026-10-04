"""La console: quanto costano le inferenze (pagina «Costi»).

Legge `llm_consumi` — una riga per chiamata a un modello, scritta da `llm/consumi.py` — e la mette in tre forme:

- **per compito e fase**: dove vanno i token (intervista, validazione, interpretazione, sintesi, giudizio, teaser,
  chat, memoria…), quanti di ragionamento, quante chiamate fallite;
- **per giorno**: l'andamento, da confrontare col pannello del fornitore;
- **per lettura**: il consumo medio di una lettura completata e di una abbandonata (ferma all'intervista o a metà).

Ogni somma si traduce in dollari con i listini (`llm_listini`), modificabili da qui: il fornitore in uso e quelli che si
stanno valutando. La cache di un listino in valutazione si applica solo alla parte cacheabile dell'ingresso (i messaggi
di sistema in testa, vedi `llm/listini.py`); per il listino in uso vale la cache che il fornitore ha riportato.

Dove il fornitore non ha riportato il consumo (`usage_riportato` falso) i token si stimano dai caratteri, 3,5 per
token: la colonna `stimate` dice quante chiamate sono contate così.
"""
from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from lanterna.rete import ip_client
from pydantic import BaseModel, Field
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError

from ...auth.dependencies import CurrentUser, DbSession, require_role
from ...domain.base import utcnow
from ...domain.consumi_models import LlmListino
from ...domain.repositories import AuditRepository
from ...llm.listini import Listino, costo

router = APIRouter(prefix="/admin", tags=["costi"], dependencies=[Depends(require_role("admin"))])

#: Caratteri per token quando il fornitore non riporta il consumo: la media misurata sui prompt italiani e inglesi
#: della piattaforma col vocabolario di Nemotron (vedi `docs/costi-inferenze.md`).
CARATTERI_PER_TOKEN = 3.5

def _token(colonna: str, caratteri: str) -> str:
    """I token riportati dal fornitore; senza, la stima dai caratteri. Una chiamata respinta (`errore` senza consumo:
    un 400, un formato rifiutato) non ha generato niente e non si fattura: vale zero."""
    return (f"(case when usage_riportato then {colonna} when esito = 'errore' then 0 "
            f"else ({caratteri}) / {CARATTERI_PER_TOKEN} end)")


_INGRESSO = _token("token_ingresso", "caratteri_ingresso")
_SOMME = f"""
    count(*) as chiamate,
    sum(case when esito <> 'ok' then 1 else 0 end) as errori,
    sum(case when usage_riportato or esito = 'errore' then 0 else 1 end) as stimate,
    sum({_INGRESSO}) as ingresso,
    sum(token_cache) as cache,
    sum({_token("token_uscita", "caratteri_uscita + caratteri_ragionamento")}) as uscita,
    sum({_token("token_ragionamento", "caratteri_ragionamento")}) as ragionamento,
    sum(case when caratteri_ingresso > 0 then {_INGRESSO} * caratteri_sistema::float / caratteri_ingresso
             else 0 end) as cacheabile,
    avg(durata_ms) as durata_media_ms
"""


def _numeri(riga: Any) -> Dict[str, Any]:
    dati = dict(riga._mapping)
    for chiave in ("chiamate", "errori", "stimate"):
        if chiave in dati:
            dati[chiave] = int(dati[chiave] or 0)
    for chiave in ("ingresso", "cache", "uscita", "ragionamento", "cacheabile", "durata_media_ms"):
        if chiave in dati:
            dati[chiave] = round(float(dati[chiave] or 0), 1)
    return dati


def _costi(listini: List[Listino], dati: Dict[str, Any], *, diviso: float = 1.0) -> Dict[str, float]:
    diviso = diviso or 1.0
    return {
        l.nome: round(costo(
            l, ingresso=dati.get("ingresso", 0) / diviso, uscita=dati.get("uscita", 0) / diviso,
            cacheabile=dati.get("cacheabile", 0) / diviso, cache_misurata=dati.get("cache", 0) / diviso,
        ), 6)
        for l in listini
    }


def listino_json(l: LlmListino) -> Dict[str, Any]:
    return {
        "id": l.id, "nome": l.nome, "prezzo_ingresso": float(l.prezzo_ingresso), "prezzo_cache": float(l.prezzo_cache),
        "prezzo_uscita": float(l.prezzo_uscita), "cache_hit": float(l.cache_hit), "attuale": l.attuale, "nota": l.nota,
    }


async def _listini(session) -> List[LlmListino]:
    return list((await session.execute(
        select(LlmListino).order_by(LlmListino.attuale.desc(), LlmListino.nome)
    )).scalars().all())


@router.get("/costi")
async def riepilogo(session: DbSession, giorni: int = Query(default=14, ge=1, le=365)) -> Dict[str, Any]:
    """I consumi degli ultimi `giorni`, con il costo stimato per ogni listino."""
    dal = utcnow() - timedelta(days=giorni)
    righe_listini = await _listini(session)
    listini = [Listino.da(l) for l in righe_listini]
    parametri = {"dal": dal}

    totali = _numeri((await session.execute(text(
        f"select {_SOMME} from llm_consumi where created_at >= :dal"), parametri)).one())
    totali["costi"] = _costi(listini, totali)

    per_compito = []
    for riga in (await session.execute(text(
        f"select compito, fase, {_SOMME} from llm_consumi where created_at >= :dal "
        "group by compito, fase order by sum(token_uscita) desc, compito, fase"), parametri)):
        dati = _numeri(riga)
        dati["costi"] = _costi(listini, dati)
        per_compito.append(dati)

    per_giorno = []
    for riga in (await session.execute(text(
        f"select to_char(created_at at time zone 'UTC', 'YYYY-MM-DD') as giorno, compito, {_SOMME} "
        "from llm_consumi where created_at >= :dal group by 1, 2 order by 1, 2"), parametri)):
        dati = _numeri(riga)
        dati["costi"] = _costi(listini, dati)
        per_giorno.append(dati)

    # Per lettura: lo stato di oggi della lettura decide se è completata, annullata (crisi) o abbandonata — ferma
    # all'intervista o a metà strada. Una lettura ancora in corso conta fra le abbandonate: la pagina lo dice.
    letture = []
    for riga in (await session.execute(text(
        f"""select case when r.status = 'completata' then 'completata'
                        when r.status = 'annullata' then 'annullata'
                        when r.id is null then 'cancellata'
                        else 'abbandonata' end as stato,
                   count(distinct c.reading_id) as letture, {_SOMME}
            from llm_consumi c left join readings r on r.id = c.reading_id
            where c.created_at >= :dal and c.reading_id is not null
            group by 1 order by 1"""), parametri)):
        dati = _numeri(riga)
        dati["letture"] = int(riga._mapping["letture"] or 0)
        dati["costi_per_lettura"] = _costi(listini, dati, diviso=dati["letture"])
        dati["per_lettura"] = {
            k: round(dati[k] / max(dati["letture"], 1), 1) for k in ("chiamate", "ingresso", "uscita", "ragionamento")
        }
        letture.append(dati)

    # Le chiamate fuori da una lettura: la chat dell'oracolo, il recupero delle memorie all'apertura, gli strumenti.
    fuori = []
    for riga in (await session.execute(text(
        f"select riferimento, compito, {_SOMME} from llm_consumi "
        "where created_at >= :dal and reading_id is null group by 1, 2 order by 1, 2"), parametri)):
        dati = _numeri(riga)
        dati["costi"] = _costi(listini, dati)
        fuori.append(dati)

    return {
        "giorni": giorni, "dal": dal.isoformat(), "caratteri_per_token": CARATTERI_PER_TOKEN,
        "listini": [listino_json(l) for l in righe_listini],
        "totali": totali, "per_compito": per_compito, "per_giorno": per_giorno, "letture": letture,
        "fuori_lettura": fuori,
    }


# ---- listini ----------------------------------------------------------------------------------------------------


class ListinoIn(BaseModel):
    nome: str = Field(min_length=1, max_length=60)
    prezzo_ingresso: float = Field(ge=0, le=1000)
    prezzo_cache: float = Field(ge=0, le=1000)
    prezzo_uscita: float = Field(ge=0, le=1000)
    cache_hit: float = Field(default=0, ge=0, le=1)
    attuale: bool = False
    nota: str = Field(default="", max_length=300)


async def _uno_solo_attuale(session, tenuto: LlmListino) -> None:
    """Un solo listino «in uso»: segnarne uno toglie il segno agli altri."""
    if tenuto.attuale:
        for altro in await _listini(session):
            if altro.id != tenuto.id and altro.attuale:
                altro.attuale = False


@router.get("/costi/listini")
async def elenco_listini(session: DbSession) -> Dict[str, Any]:
    return {"listini": [listino_json(l) for l in await _listini(session)]}


@router.post("/costi/listini", status_code=201)
async def crea_listino(
    payload: ListinoIn, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    listino = LlmListino(**{**payload.model_dump(), "nome": payload.nome.strip(), "nota": payload.nota.strip()})
    session.add(listino)
    try:
        await session.flush()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=409, detail=f"Esiste già un listino «{payload.nome}».") from exc
    await _uno_solo_attuale(session, listino)
    await AuditRepository(session).record(
        action="llm_listino.crea", actor_id=user.id, target_type="llm_listino", target_id=str(listino.id),
        after=listino_json(listino), ip=ip_client(request),
    )
    await session.commit()
    return listino_json(listino)


@router.put("/costi/listini/{id_listino}")
async def modifica_listino(
    id_listino: int, payload: ListinoIn, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    listino: Optional[LlmListino] = await session.get(LlmListino, id_listino)
    if listino is None:
        raise HTTPException(status_code=404, detail="Listino non trovato")
    prima = listino_json(listino)
    for campo, valore in payload.model_dump().items():
        setattr(listino, campo, valore.strip() if isinstance(valore, str) else valore)
    try:
        await session.flush()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=409, detail=f"Esiste già un listino «{payload.nome}».") from exc
    await _uno_solo_attuale(session, listino)
    await AuditRepository(session).record(
        action="llm_listino.modifica", actor_id=user.id, target_type="llm_listino", target_id=str(listino.id),
        before=prima, after=listino_json(listino), ip=ip_client(request),
    )
    await session.commit()
    return listino_json(listino)


@router.delete("/costi/listini/{id_listino}", status_code=204)
async def elimina_listino(id_listino: int, request: Request, user: CurrentUser, session: DbSession) -> None:
    listino = await session.get(LlmListino, id_listino)
    if listino is None:
        raise HTTPException(status_code=404, detail="Listino non trovato")
    prima = listino_json(listino)
    await session.delete(listino)
    await AuditRepository(session).record(
        action="llm_listino.elimina", actor_id=user.id, target_type="llm_listino", target_id=str(id_listino),
        before=prima, ip=ip_client(request),
    )
    await session.commit()
