"""La console: utenti, pagamenti, catalogo, statistiche, report, registro, modelli.

Tutto il router pretende il ruolo `admin`, dichiarato una volta sola sul
router: ripeterlo endpoint per endpoint significa dimenticarlo su quello
aggiunto di fretta.

**Qui la console non legge le letture.** Vede quante sono, di che stesa, quali
carte escono, come le giudicano gli utenti. Dalla v9.5 domande, responsi, chat,
memorie e profilazione di un utente si leggono solo da `admin_contenuti_utente.py`,
dopo aver indicato un motivo, e ogni accesso resta nel registro.
"""
from __future__ import annotations

import csv
import io
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from lanterna.rete import ip_client
from pydantic import BaseModel, Field
from sqlalchemy import Date, cast, distinct, func, select

from ...auth.dependencies import CurrentUser, DbSession, require_role
from ...auth.keycloak_admin import KeycloakAdmin, KeycloakAdminError, PasswordRifiutata, UtenteEsistente
from ...billing.credits import RegistroCrediti
from ...billing.plans import GestoreAbbonamenti
from ...domain.admin_repositories import (
    AdminUserRepository, AssegnazioniModelliRepository, ContestoAmministrativo,
    RegistroAuditRepository,
)
from ...domain.base import utcnow
from ...domain.billing_models import CreditEntry, PaymentCheckout, Plan, Subscription
from ...domain.models import AuditLog, DrawnCard, Reading, User
from ...llm.compiti import Compito
from ...settings import get_settings
from ...tarot.profilo_social import posizione_json
from ..deps import aggiorna_assegnazioni, get_conoscenza, get_registro_modelli

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/admin", tags=["console"], dependencies=[Depends(require_role("admin"))],
)


def _contesto(user, request: Request) -> ContestoAmministrativo:
    return ContestoAmministrativo(
        user,
        ip=ip_client(request),
        correlation_id=getattr(request.state, "correlation_id", None),
    )


# ---- utenti ---------------------------------------------------------------------


class ModificaUtente(BaseModel):
    attivo: Optional[bool] = None


def _utente_json(u: User) -> Dict[str, Any]:
    return {
        "id": u.id,
        "email": u.email,
        "display_name": u.display_name,
        "locale": u.locale,
        "attivo": u.deleted_at is None,
        "creato": u.created_at.isoformat() if u.created_at else None,
        "referral_code": u.referral_code,
        "invitato_da": u.referred_by,
    }


@router.get("/users")
async def utenti(
    request: Request, user: CurrentUser, session: DbSession,
    q: str = "", limite: int = 50, offset: int = 0,
) -> Dict[str, Any]:
    righe, totale = await AdminUserRepository(session, _contesto(user, request)).cerca(
        testo=q.strip(), limite=min(limite, 200), offset=max(offset, 0),
    )
    registro = RegistroCrediti(session)
    gestore = GestoreAbbonamenti(session)
    elenco = []
    for u in righe:
        dati = _utente_json(u)
        dati["saldo"] = await registro.saldo(u.id)
        abb = await gestore.abbonamento_di(u.id)
        dati["piano"] = abb.plan.slug if abb else None
        elenco.append(dati)
    return {"totale": totale, "utenti": elenco}


class NuovoUtente(BaseModel):
    #: Il realm usa l'email come nome utente: è anche ciò con cui la persona entra.
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=254)
    password: str = Field(min_length=1, max_length=128)
    nome: Optional[str] = Field(default=None, max_length=100)


@router.post("/users", status_code=201)
async def crea_utente(
    payload: NuovoUtente, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    """Un account creato a mano: nasce in Keycloak (email verificata, password definitiva) e subito anche qui, con
    il piano gratuito e il regalo d'iscrizione come per chi si iscrive da sé. Se la scrittura nel database fallisce,
    l'utente appena creato in Keycloak si cancella: non resta un account senza riga né traccia nel registro. La
    password non viene registrata da nessuna parte."""
    from ...auth.dependencies import accogli
    from ...auth.keycloak import Principal
    from ...domain.repositories import UserRepository

    email = payload.email.strip().lower()
    nome = (payload.nome or "").strip() or None
    kc = KeycloakAdmin()
    try:
        sub = await kc.crea_utente(email, payload.password, nome=nome)
    except UtenteEsistente:
        raise HTTPException(status_code=409, detail="Esiste già un utente con questa email")
    except PasswordRifiutata as exc:
        raise HTTPException(status_code=400, detail=f"Password non accettata dalla politica del realm ({exc.chiave})")
    except KeycloakAdminError as exc:
        dettaglio = str(exc)
        if exc.stato == 403:
            dettaglio += " — all'account di servizio di tarot-api manca il ruolo manage-users di realm-management"
        raise HTTPException(status_code=502, detail=dettaglio)

    try:
        nuovo = await UserRepository(session).ensure(
            Principal(subject=sub, email=email, display_name=nome, roles={"user"}),
        )
        if getattr(nuovo, "appena_creato", False):
            await accogli(session, nuovo, None)
        await AdminUserRepository(session, _contesto(user, request)).registra_creazione(nuovo)
        await session.commit()
    except Exception:
        logger.exception("Utente creato in Keycloak ma non nel database: lo tolgo da Keycloak")
        await session.rollback()
        try:
            await kc.cancella_utente(sub)
            rimasto = ""
        except KeycloakAdminError:
            # Rimasto in Keycloak: la riga locale nascerebbe comunque al suo primo accesso, e si può cancellare dalla
            # console di Keycloak. L'errore da riportare resta quello del database.
            logger.error("Utente %s non cancellato da Keycloak dopo il fallimento del database", sub)
            rimasto = f" L'utente è rimasto in Keycloak (id {sub}): si cancella dalla sua console."
        raise HTTPException(status_code=500, detail=f"Utente non creato: errore nel database.{rimasto}")
    return _utente_json(nuovo)


@router.get("/users/{user_id}")
async def utente(user_id: int, session: DbSession) -> Dict[str, Any]:
    u = await session.get(User, user_id)
    if u is None:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    gestore = GestoreAbbonamenti(session)
    registro = RegistroCrediti(session)
    abb = await gestore.abbonamento_di(u.id)
    letture = (await session.execute(
        select(Reading.status, func.count()).where(Reading.owner_id == u.id).group_by(Reading.status)
    )).all()
    pagamenti = (await session.execute(
        select(PaymentCheckout).where(PaymentCheckout.user_id == u.id)
        .order_by(PaymentCheckout.created_at.desc()).limit(50)
    )).scalars().all()
    return {
        **_utente_json(u),
        # La scheda anagrafica, con la provenienza dei campi presi dai social e la posizione attuale.
        "anagrafica": {
            "nome": u.nome, "cognome": u.cognome,
            "nascita": u.birth_date.isoformat() if u.birth_date else None,
            "genere": u.gender, "genere_altro": u.gender_custom,
            "posizione": posizione_json(u),
            "dati_social": u.dati_social or {},
            "importa_social": u.importa_social, "rileva_posizione": u.rileva_posizione,
        },
        "saldo": await registro.saldo(u.id),
        "abbonamento": {
            "piano": abb.plan.slug, "nome": abb.plan.name, "stato": abb.status,
            "fine": abb.period_end.isoformat(),
        } if abb else None,
        "letture": {stato: n for stato, n in letture},
        "movimenti": [m.to_dict() for m in await registro.movimenti(u.id, limite=50)],
        "pagamenti": [_pagamento_json(p) for p in pagamenti],
        # v9 Fase 4: gli acquisti nelle app, come li ha confermati lo store.
        "acquisti_store": await _acquisti_store(session, u.id),
    }


async def _acquisti_store(session, user_id: int) -> List[Dict[str, Any]]:
    from ...billing.store.comune import acquisto_json
    from ...domain.acquisti_store_models import AcquistoStore

    righe = (await session.execute(
        select(AcquistoStore).where(AcquistoStore.user_id == user_id)
        .order_by(AcquistoStore.created_at.desc(), AcquistoStore.id.desc()).limit(50)
    )).scalars().all()
    return [acquisto_json(a) for a in righe]


@router.patch("/users/{user_id}")
async def modifica_utente(
    user_id: int, payload: ModificaUtente, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    u = await session.get(User, user_id)
    if u is None:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    if u.id == user.id and payload.attivo is False:
        raise HTTPException(status_code=400, detail="Non puoi disattivare il tuo account")
    repo = AdminUserRepository(session, _contesto(user, request))
    if payload.attivo is False:
        await repo.disattiva(u)
    elif payload.attivo is True:
        await repo.riattiva(u)
    await session.commit()
    return _utente_json(u)


# ---- pagamenti e catalogo ------------------------------------------------------------


def _pagamento_json(p: PaymentCheckout) -> Dict[str, Any]:
    return {
        "id": str(p.id),
        "user_id": p.user_id,
        "piano": p.plan.slug,
        "nome": p.plan.name,
        "tipo": p.plan.tipo,
        "annuale": p.annuale,
        "stato": p.status,
        "fornitore": p.provider,
        "importo": p.importo,
        "valuta": p.currency,
        "sandbox": p.sandbox,
        "creato": p.created_at.isoformat() if p.created_at else None,
        "completato": p.completed_at.isoformat() if p.completed_at else None,
    }


@router.get("/payments")
async def pagamenti(
    session: DbSession, stato: str = "", limite: int = 100, offset: int = 0,
) -> Dict[str, Any]:
    filtro = [PaymentCheckout.status == stato] if stato else []
    totale = int(await session.scalar(
        select(func.count()).select_from(PaymentCheckout).where(*filtro)
    ) or 0)
    righe = (await session.execute(
        select(PaymentCheckout).where(*filtro).order_by(PaymentCheckout.created_at.desc())
        .limit(min(limite, 500)).offset(max(offset, 0))
    )).scalars().all()
    incassato = int(await session.scalar(
        select(func.coalesce(func.sum(PaymentCheckout.importo), 0))
        .where(PaymentCheckout.status == "pagato", PaymentCheckout.sandbox.is_(False))      # v9 Fase 4: niente prove
    ) or 0)
    return {"totale": totale, "incassato": incassato, "pagamenti": [_pagamento_json(p) for p in righe]}


class PianoModificato(BaseModel):
    name: Optional[str] = Field(default=None, max_length=80)
    description: Optional[str] = Field(default=None, max_length=1000)
    price_monthly: Optional[int] = Field(default=None, ge=0)
    price_yearly: Optional[int] = Field(default=None, ge=0)
    credits_per_period: Optional[int] = Field(default=None, ge=0)
    letture_al_giorno: Optional[int] = Field(default=None, ge=-1)
    #: I limiti della Fase 2b: per settimana, per mese, totali del periodo pagato. −1 = senza limite.
    letture_alla_settimana: Optional[int] = Field(default=None, ge=-1, le=10_000)
    letture_al_mese: Optional[int] = Field(default=None, ge=-1, le=10_000)
    letture_totali: Optional[int] = Field(default=None, ge=-1, le=100_000)
    active: Optional[bool] = None
    #: L'ordine di presentazione (più basso, più in alto).
    rank: Optional[int] = Field(default=None, ge=0, le=10_000)
    #: Le traduzioni (v8.5): lingua → testo. Si sostituiscono per intero; una lingua vuota si toglie.
    nomi: Optional[Dict[str, Optional[str]]] = None
    descrizioni: Optional[Dict[str, Optional[str]]] = None


def _piano_admin_json(p: Plan, abbonati: int = 0, usi: int = 0) -> Dict[str, Any]:
    return {
        "id": p.id, "slug": p.slug, "nome": p.name, "tipo": p.tipo,
        "descrizione": p.description, "nomi": p.nomi or {}, "descrizioni": p.descrizioni or {},
        "prezzo_mensile": p.price_monthly,
        "prezzo_annuale": p.price_yearly, "crediti": p.credits_per_period,
        "limiti": p.limits or {}, "attivo": p.active, "rango": p.rank,
        "abbonati": abbonati,
        # Abbonamenti (di ogni stato) più pagamenti aperti: se è zero, il piano si può eliminare.
        "usi": usi,
    }


@router.get("/plans")
async def catalogo(session: DbSession) -> List[Dict[str, Any]]:
    abbonati = dict((await session.execute(
        select(Subscription.plan_id, func.count())
        .where(Subscription.status.in_(("attivo", "in_prova"))).group_by(Subscription.plan_id)
    )).all())
    usi: Dict[int, int] = {}
    for tabella in (Subscription, PaymentCheckout):
        for piano_id, n in (await session.execute(select(tabella.plan_id, func.count()).group_by(tabella.plan_id))).all():
            usi[piano_id] = usi.get(piano_id, 0) + n
    piani = await GestoreAbbonamenti(session).piani(solo_attivi=False)
    return [_piano_admin_json(p, abbonati.get(p.id, 0), usi.get(p.id, 0)) for p in piani]


@router.patch("/plans/{slug}")
async def modifica_piano(
    slug: str, payload: PianoModificato, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    """Prezzi e limiti si cambiano da qui; il nuovo prezzo vale per i
    pagamenti successivi — chi sta pagando paga quello che ha visto."""
    piano = await GestoreAbbonamenti(session).piano_per_slug(slug)
    if piano is None:
        raise HTTPException(status_code=404, detail="Piano non trovato")
    prima = _piano_admin_json(piano)
    for campo in ("name", "description", "price_monthly", "price_yearly", "credits_per_period", "active", "rank"):
        valore = getattr(payload, campo)
        if valore is not None:
            setattr(piano, campo, valore)
    for limite in ("letture_al_giorno", "letture_alla_settimana", "letture_al_mese", "letture_totali"):
        valore = getattr(payload, limite)
        if valore is not None:
            piano.limits = {**(piano.limits or {}), limite: valore}
    from ...billing.lingue import pulisci

    if payload.nomi is not None:
        piano.nomi = pulisci(payload.nomi, 80)
    if payload.descrizioni is not None:
        piano.descrizioni = pulisci(payload.descrizioni, 1000)
    from ...domain.repositories import AuditRepository

    await AuditRepository(session).record(
        action="plan.update", actor_id=user.id, target_type="plan", target_id=slug,
        before=prima, after=_piano_admin_json(piano),
        ip=ip_client(request),
    )
    await session.commit()
    return _piano_admin_json(piano)


# ---- statistiche -------------------------------------------------------------------------


async def _conteggi(session, dal: datetime, al: datetime) -> Dict[str, int]:
    def tra(col):
        return (col >= dal) & (col < al)

    letture = int(await session.scalar(select(func.count()).select_from(Reading).where(tra(Reading.created_at))) or 0)
    completate = int(await session.scalar(
        select(func.count()).select_from(Reading).where(tra(Reading.created_at), Reading.status == "completata")
    ) or 0)
    attivi = int(await session.scalar(
        select(func.count(distinct(Reading.owner_id))).where(tra(Reading.created_at))
    ) or 0)
    nuovi = int(await session.scalar(select(func.count()).select_from(User).where(tra(User.created_at))) or 0)
    consumati = int(await session.scalar(
        select(func.coalesce(func.sum(-CreditEntry.delta), 0))
        .where(tra(CreditEntry.created_at), CreditEntry.reason == "consumo")
    ) or 0)
    venduti = int(await session.scalar(
        select(func.coalesce(func.sum(CreditEntry.delta), 0))
        .where(tra(CreditEntry.created_at), CreditEntry.reason == "acquisto")
    ) or 0)
    ricavi = int(await session.scalar(
        select(func.coalesce(func.sum(PaymentCheckout.importo), 0))
        .where(PaymentCheckout.status == "pagato", PaymentCheckout.sandbox.is_(False), tra(PaymentCheckout.completed_at))
    ) or 0)
    bloccate = int(await session.scalar(
        select(func.count()).select_from(Reading)
        .where(tra(Reading.created_at), Reading.guard_outcome.in_(("bloccato", "riscritto")))
    ) or 0)
    crisi = int(await session.scalar(
        select(func.count()).select_from(AuditLog)
        .where(tra(AuditLog.created_at), AuditLog.action == "reading.crisis")
    ) or 0)
    return {
        "letture": letture, "completate": completate, "utenti_attivi": attivi,
        "nuovi_utenti": nuovi, "crediti_consumati": consumati, "crediti_venduti": venduti,
        "ricavi": ricavi, "guardia_interventi": bloccate, "crisi": crisi,
    }


@router.get("/stats")
async def statistiche(session: DbSession, giorni: int = 30) -> Dict[str, Any]:
    giorni = max(1, min(giorni, 365))
    adesso = utcnow()
    dal = adesso - timedelta(days=giorni)
    precedente = await _conteggi(session, dal - timedelta(days=giorni), dal)
    attuale = await _conteggi(session, dal, adesso)

    giorno = cast(Reading.created_at, Date)
    serie = (await session.execute(
        select(giorno, func.count()).where(Reading.created_at >= dal).group_by(giorno).order_by(giorno)
    )).all()
    per_stesa = (await session.execute(
        select(Reading.spread_id, func.count()).where(Reading.created_at >= dal)
        .group_by(Reading.spread_id).order_by(func.count().desc())
    )).all()
    carte = (await session.execute(
        select(DrawnCard.card_id, func.count())
        .join(Reading, Reading.id == DrawnCard.reading_id)
        .where(Reading.created_at >= dal, DrawnCard.calcolata.is_(False))
        .group_by(DrawnCard.card_id).order_by(func.count().desc()).limit(12)
    )).all()
    feedback = (await session.execute(
        select(Reading.feedback, func.count()).where(Reading.feedback.is_not(None))
        .group_by(Reading.feedback)
    )).all()
    consumo = (await session.execute(
        select(Reading.consumo, func.count()).where(Reading.created_at >= dal).group_by(Reading.consumo)
    )).all()
    abbonamenti = (await session.execute(
        select(Plan.name, func.count()).join(Subscription, Subscription.plan_id == Plan.id)
        .where(Subscription.status.in_(("attivo", "in_prova"))).group_by(Plan.name)
    )).all()

    conoscenza = get_conoscenza()
    stese = {s["id"]: s["nome"] for s in conoscenza.stese.values()}
    return {
        "giorni": giorni,
        "attuale": attuale,
        "precedente": precedente,
        "serie": [{"giorno": g.isoformat(), "letture": n} for g, n in serie],
        "per_stesa": [{"stesa": stese.get(s, s), "letture": n} for s, n in per_stesa],
        "carte": [
            {"carta": conoscenza.carta(c)["nome_it"] if c in conoscenza.carte else c, "uscite": n}
            for c, n in carte
        ],
        "feedback": {f: n for f, n in feedback},
        "consumo": {c: n for c, n in consumo},
        "abbonamenti": {p: n for p, n in abbonamenti},
    }


# ---- report ------------------------------------------------------------------------------


def _csv(nome: str, intestazione: List[str], righe) -> StreamingResponse:
    buffer = io.StringIO()
    scrittore = csv.writer(buffer)
    scrittore.writerow(intestazione)
    for r in righe:
        scrittore.writerow(r)
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue().encode("utf-8-sig")]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{nome}.csv"'},
    )


@router.get("/reports/{tipo}.csv")
async def report(tipo: str, session: DbSession, giorni: int = 30) -> StreamingResponse:
    """Esportazioni per la contabilità e l'analisi. Le letture escono senza
    domanda né responso: metadati, non contenuti."""
    dal = utcnow() - timedelta(days=max(1, min(giorni, 3650)))
    if tipo == "utenti":
        righe = (await session.execute(select(User).order_by(User.id))).scalars().all()
        return _csv("utenti", ["id", "email", "nome", "lingua", "attivo", "creato", "invitato_da"], (
            [u.id, u.email, u.display_name, u.locale, u.deleted_at is None,
             u.created_at.isoformat() if u.created_at else "", u.referred_by or ""] for u in righe
        ))
    if tipo == "pagamenti":
        righe = (await session.execute(
            select(PaymentCheckout).where(PaymentCheckout.created_at >= dal).order_by(PaymentCheckout.created_at)
        )).scalars().all()
        return _csv("pagamenti", ["id", "utente", "piano", "tipo", "stato", "importo_centesimi", "valuta", "creato", "completato"], (
            [str(p.id), p.user_id, p.plan.slug, p.plan.tipo, p.status, p.importo, p.currency,
             p.created_at.isoformat() if p.created_at else "",
             p.completed_at.isoformat() if p.completed_at else ""] for p in righe
        ))
    if tipo == "crediti":
        righe = (await session.execute(
            select(CreditEntry).where(CreditEntry.created_at >= dal).order_by(CreditEntry.created_at)
        )).scalars().all()
        return _csv("crediti", [
            "id", "utente", "delta", "motivo", "lettura", "nota", "quando", "canale", "fornitore", "riferimento",
            "scade",
        ], (
            [
                r.id, r.user_id, r.delta, r.reason, str(r.reading_id or ""), r.note or "", r.created_at.isoformat(),
                r.canale, r.provider, r.riferimento_esterno or "", r.expires_at.isoformat() if r.expires_at else "",
            ]
            for r in righe
        ))
    if tipo == "letture":
        righe = (await session.execute(
            select(Reading).where(Reading.created_at >= dal).order_by(Reading.created_at)
        )).scalars().all()
        return _csv("letture", ["id", "utente", "stesa", "stato", "consumo", "guardia", "diario", "creata", "conclusa"], (
            [str(r.id), r.owner_id, r.spread_id, r.status, r.consumo, r.guard_outcome or "",
             r.feedback or "", r.created_at.isoformat(),
             r.completed_at.isoformat() if r.completed_at else ""] for r in righe
        ))
    raise HTTPException(status_code=404, detail="Report sconosciuto")


# ---- registro e modelli -------------------------------------------------------------------


@router.get("/audit")
async def registro(
    session: DbSession, limite: int = 100, offset: int = 0, azione: str = "", target_type: str = "",
) -> List[Dict[str, Any]]:
    righe = await RegistroAuditRepository(session).recenti(
        limite=min(limite, 500), offset=max(offset, 0), azione=azione or None, target_type=target_type or None,
    )
    return [
        {
            "id": r.id, "attore": r.actor_id, "azione": r.action,
            "tipo": r.target_type, "target": r.target_id,
            "prima": r.before, "dopo": r.after, "ip": r.ip, "correlazione": r.correlation_id,
            "quando": r.created_at.isoformat(),
        }
        for r in righe
    ]


class Assegnazione(BaseModel):
    modello: Optional[str] = Field(default=None, max_length=60)
    #: v7: se questo COMPITO ragiona, a prescindere dal fornitore assegnato. `None` in
    #: questa richiesta significa "non toccare" (compatibile con le richieste di prima di v7
    #: che assegnano solo il modello); un valore esplicito sovrascrive.
    ragiona: Optional[bool] = None
    parametri_override: Optional[Dict[str, Any]] = None
    #: I campi qui sotto si toccano solo se la richiesta li porta (`model_fields_set`): `null` riporta a «eredita dal
    #: fornitore» / «predefinito del compito», un valore lo scrive.
    livello: Optional[Literal["none", "minimal", "low", "medium", "high", "xhigh", "max"]] = None
    json_schema: Optional[bool] = None


#: I campi dell'assegnazione che si scrivono solo se presenti nella richiesta.
_CAMPI_COMPITO = ("livello", "json_schema")


@router.get("/models")
async def modelli(session: DbSession) -> Dict[str, Any]:
    await aggiorna_assegnazioni(session, forza=True)
    registro = get_registro_modelli()
    return {
        # Senza un modello vero le letture rispondono 503: la console lo dice.
        "configurato": registro.configurato,
        "finto": get_settings().llm_finto,
        "modelli": [
            {"nome": m.nome, "provider": m.provider, "model": m.model, "descrizione": m.descrizione}
            # Il modello «predefinito» ricavato dai valori di ripiego non è un
            # modello configurato: non si elenca come se lo fosse.
            for m in (registro.modelli if registro.configurato else [])
        ],
        "compiti": registro.stato(),
    }


@router.put("/models/{compito}")
async def assegna(
    compito: str, payload: Assegnazione, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    try:
        c = Compito(compito)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Compito sconosciuto") from exc
    registro = get_registro_modelli()
    if payload.modello is not None and not registro.esiste(payload.modello):
        raise HTTPException(status_code=400, detail="Modello non configurato")
    risultato = await AssegnazioniModelliRepository(session, _contesto(user, request)).assegna(
        c.value, payload.modello, ragiona=payload.ragiona, parametri_override=payload.parametri_override,
        **{campo: getattr(payload, campo) for campo in _CAMPI_COMPITO if campo in payload.model_fields_set},
    )
    await session.commit()
    # Lo stato in memoria si allinea a quello scritto (`risultato`), mai ricostruito dal solo
    # payload: un aggiornamento parziale (es. solo il modello, senza toccare il reasoning)
    # cancellerebbe altrimenti un override esistente fino al prossimo rinfresco periodico.
    if risultato is None:
        registro.assegna(c, None)
    else:
        registro.assegna(
            c, risultato.nome,
            ragiona_override=risultato.ragiona_override, parametri_override=risultato.parametri_override,
            livello=risultato.livello, json_schema=risultato.json_schema,
        )
    return {"compiti": registro.stato()}
