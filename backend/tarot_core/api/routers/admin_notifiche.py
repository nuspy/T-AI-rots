"""La console «Notifications» (v9, Fase 5): campagne, automatiche, consegne e aperture, impostazioni.

- **Campagne**: elenco, nuova/modifica (testi per lingua con «Traduci» dall'LLM, segmento con il **conteggio dei
  destinatari** in anteprima, canali, immagine, pagina d'arrivo), «invia a me», programmazione o invio subito,
  annullamento.
- **Automatiche**: accese o spente, l'ora, i testi per lingua.
- **Consegne e aperture**: per tipo e per giorno.
- **Impostazioni**: il service account di Firebase (caricato, cifrato, mai rimostrato; «Prova» con un messaggio solo
  convalidato), lo stato delle chiavi VAPID (generate da sole), ore di silenzio, ora della carta, tetti, velocità.

Ogni scrittura va nel registro di audit, mai con i segreti.
"""
from __future__ import annotations

from datetime import datetime, time, timedelta
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from lanterna.rete import ip_client
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func, select

from ...auth.dependencies import CurrentUser, DbSession, require_role
from ...domain.base import utcnow
from ...domain.billing_models import Plan
from ...domain.notifiche_models import (
    CANALI, PIATTAFORME, TIPI_AUTOMATICI, CampagnaNotifica, DispositivoNotifica, InvioNotifica,
)
from ...domain.repositories import AuditRepository
from ...notifiche import campagne, fcm, segmenti, traduzione
from ...notifiche import config as conf

router = APIRouter(prefix="/admin/notifiche", tags=["notifiche"], dependencies=[Depends(require_role("admin"))])

NOMI_AUTOMATICHE = {
    "carta_giorno": "Carta del giorno",
    "serie_in_pericolo": "Serie in pericolo",
    "crediti_in_scadenza": "Crediti in scadenza",
    "benvenuto": "Benvenuto (il giorno dopo l'iscrizione)",
    "rinnovo_fallito": "Rinnovo non riuscito",
    "promemoria_prova": "Fine della prova (2 giorni prima)",
}
SPIEGAZIONI_AUTOMATICHE = {
    "carta_giorno": "All'ora scelta dalla persona (predefinita nelle impostazioni), se oggi non ha ancora aperto la carta.",
    "serie_in_pericolo": "La sera, a chi ha almeno tre giorni di fila e oggi non ha ancora girato la carta. Segnaposto: {n}.",
    "crediti_in_scadenza": "Tre giorni prima che scadano crediti di piano (dalla v9 i crediti comprati non scadono: di "
                           "solito non serve). Segnaposto: {n}, {data}.",
    "benvenuto": "Una volta, fra uno e quattro giorni dopo l'iscrizione, all'ora indicata.",
    "rinnovo_fallito": "Appena un rinnovo non riesce (si apre la tolleranza), una volta. Segnaposto: {piano}.",
    "promemoria_prova": "Insieme all'email, i giorni prima della fine della prova scelti in «Abbonamenti». Segnaposto: "
                        "{giorni}, {data}, {sconto}.",
}


def _testi_validi(testi: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    puliti: Dict[str, Dict[str, str]] = {}
    for lingua, t in (testi or {}).items():
        if lingua not in conf.LINGUE or not isinstance(t, dict):
            raise ValueError(f"lingua non ammessa: {lingua}")
        titolo, corpo = str(t.get("titolo") or "").strip(), str(t.get("corpo") or "").strip()
        if len(titolo) > 120 or len(corpo) > 400:
            raise ValueError(f"testo troppo lungo in {lingua}: titolo fino a 120 caratteri, testo fino a 400")
        if titolo or corpo:
            puliti[lingua] = {"titolo": titolo, "corpo": corpo}
    return puliti


def _ora(valore: Optional[time]) -> Optional[str]:
    return conf.ora_testo(valore)


# ---- vista ------------------------------------------------------------------------------------------------------


async def _vista(session) -> Dict[str, Any]:
    cfg = await conf.config(session)
    _, pubblica = await conf.chiavi_vapid(session)
    dispositivi = (await session.execute(
        select(DispositivoNotifica.canale, DispositivoNotifica.piattaforma, DispositivoNotifica.attivo, func.count())
        .group_by(DispositivoNotifica.canale, DispositivoNotifica.piattaforma, DispositivoNotifica.attivo)
    )).all()
    conteggi = {p: {"attivi": 0, "disattivati": 0} for p in PIATTAFORME}
    for _canale, piattaforma, attivo, n in dispositivi:
        conteggi[piattaforma]["attivi" if attivo else "disattivati"] += int(n)
    piani = (await session.execute(select(Plan.slug, Plan.name).order_by(Plan.rank, Plan.id))).all()
    return {
        "firebase": {
            "presente": bool(cfg.firebase_cifrato), "progetto": cfg.firebase_progetto, "email": cfg.firebase_email,
            "caricato_il": cfg.firebase_caricato_il.isoformat() if cfg.firebase_caricato_il else None,
            "prova_il": cfg.firebase_prova_il.isoformat() if cfg.firebase_prova_il else None,
            "esito": cfg.firebase_esito or {},
        },
        "vapid": {
            "presente": bool(pubblica), "pubblica": pubblica or None,
            "creata_il": cfg.vapid_creata_il.isoformat() if cfg.vapid_creata_il else None,
            "contatto": cfg.vapid_contatto,
        },
        "impostazioni": {
            "ora_carta": _ora(cfg.ora_carta), "silenzio_dal": _ora(cfg.silenzio_dal), "silenzio_al": _ora(cfg.silenzio_al),
            "tetto_promozioni_settimana": cfg.tetto_promozioni_settimana, "limite_al_minuto": cfg.limite_al_minuto,
            "vapid_contatto": cfg.vapid_contatto,
        },
        "automatiche": [
            {"tipo": t, "nome": NOMI_AUTOMATICHE[t], "spiegazione": SPIEGAZIONI_AUTOMATICHE[t], **conf.automatica(cfg, t),
             "ha_ora": conf.PREDEFINITE[t]["ora"] is not None}
            for t in TIPI_AUTOMATICI
        ],
        "dispositivi": conteggi,
        "catalogo": {
            "lingue": list(conf.LINGUE), "canali": list(CANALI), "piattaforme": list(PIATTAFORME),
            "fasce_eta": list(segmenti.FASCE_ETA), "piani": [{"slug": s, "nome": n} for s, n in piani],
        },
    }


@router.get("")
async def leggi(session: DbSession) -> Dict[str, Any]:
    vista = await _vista(session)
    await session.commit()
    return vista


# ---- impostazioni e Firebase -------------------------------------------------------------------------------------


class ImpostazioniIn(BaseModel):
    ora_carta: Optional[time] = None
    silenzio: Optional[bool] = None
    silenzio_dal: Optional[time] = None
    silenzio_al: Optional[time] = None
    tetto_promozioni_settimana: Optional[int] = Field(default=None, ge=0, le=14)
    limite_al_minuto: Optional[int] = Field(default=None, ge=10, le=100000)
    vapid_contatto: Optional[str] = Field(default=None, max_length=200, pattern=r"^(mailto:[^@\s]+@[^@\s]+|https://\S+)$")


def _senza_secondi(t: time) -> time:
    return t.replace(second=0, microsecond=0, tzinfo=None)


@router.put("/impostazioni")
async def modifica_impostazioni(payload: ImpostazioniIn, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    cfg = await conf.config(session)
    prima = {"ora_carta": _ora(cfg.ora_carta), "silenzio_dal": _ora(cfg.silenzio_dal), "silenzio_al": _ora(cfg.silenzio_al),
             "tetto": cfg.tetto_promozioni_settimana, "limite": cfg.limite_al_minuto, "contatto": cfg.vapid_contatto}
    if payload.ora_carta is not None:
        cfg.ora_carta = _senza_secondi(payload.ora_carta)
    if payload.silenzio is False:
        cfg.silenzio_dal = cfg.silenzio_al = None
    elif payload.silenzio_dal is not None or payload.silenzio_al is not None or payload.silenzio:
        cfg.silenzio_dal = _senza_secondi(payload.silenzio_dal or cfg.silenzio_dal or time(22))
        cfg.silenzio_al = _senza_secondi(payload.silenzio_al or cfg.silenzio_al or time(8))
    if payload.tetto_promozioni_settimana is not None:
        cfg.tetto_promozioni_settimana = payload.tetto_promozioni_settimana
    if payload.limite_al_minuto is not None:
        cfg.limite_al_minuto = payload.limite_al_minuto
    if payload.vapid_contatto is not None:
        cfg.vapid_contatto = payload.vapid_contatto
    cfg.updated_by = user.id
    await session.flush()
    await AuditRepository(session).record(
        action="notifiche.impostazioni", actor_id=user.id, target_type="config_notifiche", target_id="1", before=prima,
        after={"ora_carta": _ora(cfg.ora_carta), "silenzio_dal": _ora(cfg.silenzio_dal), "silenzio_al": _ora(cfg.silenzio_al),
               "tetto": cfg.tetto_promozioni_settimana, "limite": cfg.limite_al_minuto, "contatto": cfg.vapid_contatto},
        ip=ip_client(request),
    )
    vista = await _vista(session)
    await session.commit()
    return vista


class FirebaseIn(BaseModel):
    service_account_json: str = Field(min_length=20, max_length=20_000)


@router.put("/firebase")
async def carica_firebase(payload: FirebaseIn, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    cfg = await conf.config(session)
    try:
        dati = conf.salva_firebase(cfg, payload.service_account_json, autore_id=user.id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    await session.flush()
    await AuditRepository(session).record(
        action="notifiche.firebase", actor_id=user.id, target_type="config_notifiche", target_id="1",
        after={"caricato": True, **dati}, ip=ip_client(request),
    )
    vista = await _vista(session)
    await session.commit()
    return vista


@router.delete("/firebase")
async def togli_firebase(request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    cfg = await conf.config(session)
    conf.togli_firebase(cfg, autore_id=user.id)
    await session.flush()
    await AuditRepository(session).record(
        action="notifiche.firebase", actor_id=user.id, target_type="config_notifiche", target_id="1",
        after={"caricato": False}, ip=ip_client(request),
    )
    vista = await _vista(session)
    await session.commit()
    return vista


async def prova_firebase(session) -> Dict[str, Any]:
    """La prova (anche dal registro «Account»): salva l'esito e lo restituisce."""
    cfg = await conf.config(session)
    cred = conf.credenziali_firebase(cfg)
    if cred is None:
        esito = {"ok": False, "messaggio": "Manca il JSON del service account di Firebase: caricalo qui sotto."}
    else:
        e = await fcm.prova(cred)
        esito = {"ok": e.stato == "ok", "messaggio": e.messaggio}
    cfg.firebase_prova_il = utcnow()
    cfg.firebase_esito = esito
    await session.flush()
    return esito


@router.post("/firebase/prova")
async def prova(session: DbSession) -> Dict[str, Any]:
    await prova_firebase(session)
    vista = await _vista(session)
    await session.commit()
    return vista


# ---- automatiche --------------------------------------------------------------------------------------------------


class AutomaticaIn(BaseModel):
    attiva: Optional[bool] = None
    ora: Optional[str] = Field(default=None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    testi: Optional[Dict[str, Dict[str, str]]] = None

    @field_validator("testi")
    @classmethod
    def _testi(cls, v):
        return None if v is None else _testi_validi(v)


@router.put("/automatiche/{tipo}")
async def modifica_automatica(tipo: str, payload: AutomaticaIn, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    if tipo not in TIPI_AUTOMATICI:
        raise HTTPException(status_code=404, detail="Notifica automatica sconosciuta")
    cfg = await conf.config(session)
    tutte = dict(cfg.automatiche or {})
    attuale = dict(tutte.get(tipo) or {})
    if payload.attiva is not None:
        attuale["attiva"] = payload.attiva
    if payload.ora is not None and conf.PREDEFINITE[tipo]["ora"] is not None:
        attuale["ora"] = payload.ora
    if payload.testi is not None:
        # Solo le lingue scritte per intero; una lingua svuotata torna al testo predefinito.
        attuale["testi"] = {k: v for k, v in payload.testi.items() if v["titolo"] and v["corpo"]}
    tutte[tipo] = attuale
    cfg.automatiche = tutte
    cfg.updated_by = user.id
    await session.flush()
    await AuditRepository(session).record(
        action="notifiche.automatica", actor_id=user.id, target_type="config_notifiche", target_id=tipo,
        after={"attiva": attuale.get("attiva"), "ora": attuale.get("ora"), "lingue": sorted((attuale.get("testi") or {}))},
        ip=ip_client(request),
    )
    vista = await _vista(session)
    await session.commit()
    return vista


# ---- traduzione e conteggio ---------------------------------------------------------------------------------------


class TraduciIn(BaseModel):
    base: str = Field(pattern="^(" + "|".join(conf.LINGUE) + ")$")
    titolo: str = Field(min_length=1, max_length=120)
    corpo: str = Field(min_length=1, max_length=400)
    lingue: List[str] = Field(min_length=1, max_length=len(conf.LINGUE))

    @field_validator("lingue")
    @classmethod
    def _lingue(cls, v: List[str]) -> List[str]:
        if any(x not in conf.LINGUE for x in v):
            raise ValueError("lingue ammesse: " + ", ".join(conf.LINGUE))
        return v


@router.post("/traduci")
async def traduci(payload: TraduciIn) -> Dict[str, Any]:
    from ...llm.compiti import Compito
    from ..deps import provider_per

    provider = provider_per(Compito.TRADUZIONE_ARTICOLO)
    try:
        testi = await traduzione.traduci(provider, payload.base, {"titolo": payload.titolo, "corpo": payload.corpo},
                                         payload.lingue)
    except traduzione.TraduzioneNonRiuscita as exc:
        raise HTTPException(status_code=502, detail=f"Traduzione non riuscita: {exc}") from exc
    return {"testi": testi}


class ConteggioIn(BaseModel):
    tipo: Literal["servizio", "promozione"]
    filtro: segmenti.Filtro = Field(default_factory=segmenti.Filtro)
    canali: List[Literal["fcm", "webpush"]] = Field(default_factory=lambda: list(CANALI), min_length=1)


@router.post("/conteggio")
async def conteggio(payload: ConteggioIn, session: DbSession) -> Dict[str, Any]:
    return await segmenti.conta(session, payload.filtro, payload.tipo, payload.canali)


# ---- campagne -----------------------------------------------------------------------------------------------------


class CampagnaIn(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    tipo: Literal["servizio", "promozione"]
    testi: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    lingua_base: str = Field(default="it", pattern="^(" + "|".join(conf.LINGUE) + ")$")
    #: Un percorso del sito: `/` o `/qualcosa` (mai `//altro-sito`, che il browser leggerebbe come un dominio).
    deep_link: str = Field(default="/", max_length=300, pattern=r"^/([^/\s][^\s]*)?$")
    immagine: Optional[str] = Field(default=None, max_length=500, pattern=r"^https://\S+$")
    filtro: segmenti.Filtro = Field(default_factory=segmenti.Filtro)
    canali: List[Literal["fcm", "webpush"]] = Field(default_factory=lambda: list(CANALI), min_length=1)
    rispetta_silenzio: bool = True

    @field_validator("testi")
    @classmethod
    def _testi(cls, v):
        return _testi_validi(v)


def _campagna_json(c: CampagnaNotifica) -> Dict[str, Any]:
    return {
        "id": c.id, "nome": c.nome, "tipo": c.tipo, "testi": c.testi or {}, "lingua_base": c.lingua_base,
        "deep_link": c.deep_link, "immagine": c.immagine, "filtro": c.filtro or {}, "canali": c.canali or [],
        "rispetta_silenzio": c.rispetta_silenzio, "stato": c.stato,
        "programmata_il": c.programmata_il.isoformat() if c.programmata_il else None,
        "iniziata_il": c.iniziata_il.isoformat() if c.iniziata_il else None,
        "finita_il": c.finita_il.isoformat() if c.finita_il else None,
        "contatori": {"destinatari": c.destinatari, "inviati": c.inviati, "errori": c.errori, "saltati": c.saltati,
                      "aperti": c.aperti},
        "creata_il": c.created_at.isoformat() if c.created_at else None,
        "modificata_il": c.updated_at.isoformat() if c.updated_at else None,
    }


async def _fresca(session, c: CampagnaNotifica) -> Dict[str, Any]:
    """La campagna dopo il commit: `updated_at` lo scrive il database e va riletto."""
    await session.refresh(c)
    return _campagna_json(c)


async def _campagna(session, campagna_id: int) -> CampagnaNotifica:
    c = await session.get(CampagnaNotifica, campagna_id)
    if c is None:
        raise HTTPException(status_code=404, detail="Campagna inesistente")
    return c


@router.get("/campagne")
async def elenco_campagne(session: DbSession, limite: int = Query(default=100, ge=1, le=500)) -> Dict[str, Any]:
    righe = (await session.execute(
        select(CampagnaNotifica).order_by(CampagnaNotifica.created_at.desc(), CampagnaNotifica.id.desc()).limit(limite)
    )).scalars().all()
    return {"campagne": [_campagna_json(c) for c in righe]}


@router.post("/campagne", status_code=201)
async def crea_campagna(payload: CampagnaIn, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    c = CampagnaNotifica(creata_da=user.id, stato="bozza")
    _applica(c, payload)
    session.add(c)
    await session.flush()
    await AuditRepository(session).record(
        action="notifiche.campagna.crea", actor_id=user.id, target_type="campagna_notifica", target_id=str(c.id),
        after={"nome": c.nome, "tipo": c.tipo}, ip=ip_client(request),
    )
    await session.commit()
    return await _fresca(session, c)


def _applica(c: CampagnaNotifica, payload: CampagnaIn) -> None:
    c.nome, c.tipo, c.testi, c.lingua_base = payload.nome.strip(), payload.tipo, payload.testi, payload.lingua_base
    c.deep_link, c.immagine = payload.deep_link, payload.immagine
    c.filtro = payload.filtro.model_dump(exclude_defaults=True)
    c.canali = list(dict.fromkeys(payload.canali))
    c.rispetta_silenzio = payload.rispetta_silenzio


@router.get("/campagne/{campagna_id}")
async def leggi_campagna(campagna_id: int, session: DbSession) -> Dict[str, Any]:
    return _campagna_json(await _campagna(session, campagna_id))


@router.put("/campagne/{campagna_id}")
async def modifica_campagna(campagna_id: int, payload: CampagnaIn, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    c = await _campagna(session, campagna_id)
    if c.stato not in ("bozza", "programmata"):
        raise HTTPException(status_code=409, detail="Una campagna già partita non si modifica: duplicala")
    _applica(c, payload)
    await session.flush()
    await AuditRepository(session).record(
        action="notifiche.campagna.modifica", actor_id=user.id, target_type="campagna_notifica", target_id=str(c.id),
        after={"nome": c.nome, "tipo": c.tipo, "stato": c.stato}, ip=ip_client(request),
    )
    await session.commit()
    return await _fresca(session, c)


@router.delete("/campagne/{campagna_id}")
async def elimina_campagna(campagna_id: int, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    c = await _campagna(session, campagna_id)
    if c.stato != "bozza":
        raise HTTPException(status_code=409, detail="Si eliminano solo le bozze: una campagna programmata si annulla")
    await session.delete(c)
    await AuditRepository(session).record(
        action="notifiche.campagna.elimina", actor_id=user.id, target_type="campagna_notifica", target_id=str(campagna_id),
        ip=ip_client(request),
    )
    await session.commit()
    return {"eliminata": campagna_id}


def _pronta(c: CampagnaNotifica) -> None:
    base = (c.testi or {}).get(c.lingua_base) or {}
    if not base.get("titolo") or not base.get("corpo"):
        raise HTTPException(status_code=422, detail="Scrivi almeno titolo e testo nella lingua di partenza")
    if not c.canali:
        raise HTTPException(status_code=422, detail="Scegli almeno un canale")


class ProgrammaIn(BaseModel):
    #: Nullo: subito (al prossimo giro, entro 15 minuti).
    quando: Optional[datetime] = None


@router.post("/campagne/{campagna_id}/programma")
async def programma(campagna_id: int, payload: ProgrammaIn, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    c = await _campagna(session, campagna_id)
    if c.stato not in ("bozza", "programmata"):
        raise HTTPException(status_code=409, detail=f"La campagna è già {c.stato}")
    _pronta(c)
    adesso = utcnow()
    quando = payload.quando or adesso
    if quando.tzinfo is None:
        raise HTTPException(status_code=422, detail="Serve l'ora con il fuso (ISO 8601)")
    if quando < adesso - timedelta(minutes=5):
        raise HTTPException(status_code=422, detail="L'ora scelta è già passata")
    c.programmata_il = quando
    c.stato = "programmata"
    await session.flush()
    await AuditRepository(session).record(
        action="notifiche.campagna.programma", actor_id=user.id, target_type="campagna_notifica", target_id=str(c.id),
        after={"programmata_il": quando.isoformat(), "tipo": c.tipo, "filtro": c.filtro}, ip=ip_client(request),
    )
    await session.commit()
    return await _fresca(session, c)


@router.post("/campagne/{campagna_id}/annulla")
async def annulla(campagna_id: int, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    c = await _campagna(session, campagna_id)
    if c.stato in ("inviata", "annullata"):
        raise HTTPException(status_code=409, detail=f"La campagna è già {c.stato}")
    prima = c.stato
    c.stato = "annullata"
    c.finita_il = utcnow()
    await session.flush()
    await AuditRepository(session).record(
        action="notifiche.campagna.annulla", actor_id=user.id, target_type="campagna_notifica", target_id=str(c.id),
        before={"stato": prima}, ip=ip_client(request),
    )
    await session.commit()
    return await _fresca(session, c)


@router.post("/campagne/{campagna_id}/duplica", status_code=201)
async def duplica(campagna_id: int, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    c = await _campagna(session, campagna_id)
    copia = CampagnaNotifica(
        nome=f"{c.nome} (copia)"[:120], tipo=c.tipo, testi=dict(c.testi or {}), lingua_base=c.lingua_base,
        deep_link=c.deep_link, immagine=c.immagine, filtro=dict(c.filtro or {}), canali=list(c.canali or []),
        rispetta_silenzio=c.rispetta_silenzio, stato="bozza", creata_da=user.id,
    )
    session.add(copia)
    await session.commit()
    return await _fresca(session, copia)


@router.post("/campagne/{campagna_id}/invia-a-me")
async def invia_a_me(campagna_id: int, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    c = await _campagna(session, campagna_id)
    if not c.testi:
        raise HTTPException(status_code=422, detail="Scrivi almeno un testo prima di provarla")
    esito = await campagne.invia_a_me(session, c, user)
    await session.commit()
    return esito


# ---- consegne e aperture ------------------------------------------------------------------------------------------


@router.get("/statistiche")
async def statistiche(session: DbSession, giorni: int = Query(default=30, ge=1, le=365)) -> Dict[str, Any]:
    dal = utcnow() - timedelta(days=giorni)
    colonne = (
        func.count(),
        func.count().filter(InvioNotifica.consegnati > 0),
        func.count().filter(InvioNotifica.stato == "errore"),
        func.count().filter(InvioNotifica.stato == "token_invalido"),
        func.count().filter(InvioNotifica.aperto_il.is_not(None)),
    )

    def riga(valori) -> Dict[str, Any]:
        totale, consegnati, errori, invalidi, aperti = (int(x) for x in valori)
        return {"invii": totale, "consegnati": consegnati, "errori": errori, "token_invalidi": invalidi,
                "aperti": aperti, "tasso_apertura": round(aperti / consegnati, 3) if consegnati else None}

    per_tipo = (await session.execute(
        select(InvioNotifica.tipo, *colonne).where(InvioNotifica.created_at >= dal).group_by(InvioNotifica.tipo)
    )).all()
    giorno = func.date(func.timezone("Europe/Rome", InvioNotifica.created_at))
    per_giorno = (await session.execute(
        select(giorno, *colonne).where(InvioNotifica.created_at >= dal).group_by(giorno).order_by(giorno)
    )).all()
    totali = (await session.execute(select(*colonne).where(InvioNotifica.created_at >= dal))).one()
    disattivati = (await session.execute(
        select(func.count()).select_from(DispositivoNotifica)
        .where(DispositivoNotifica.disattivato_il >= dal, DispositivoNotifica.attivo.is_(False))
    )).scalar_one()
    return {
        "giorni": giorni,
        "totali": riga(totali),
        "per_tipo": [{"tipo": t, "nome": NOMI_AUTOMATICHE.get(t, {"campagna": "Campagne", "prova": "Prove («invia a me»)"}.get(t, t)),
                      **riga(v)} for t, *v in per_tipo],
        "per_giorno": [{"giorno": g.isoformat(), **riga(v)} for g, *v in per_giorno],
        "dispositivi_disattivati": int(disattivati),
    }

