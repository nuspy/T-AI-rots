"""I contenuti di un utente in console (v9.5): letture, chat, memorie, profilazione.

Fino alla v9.4 la console non leggeva le letture (vedi `admin.py`): ne contava solo il numero. L'operatore (6/10/2026)
ha deciso che, **per ragioni di sicurezza** (abusi, segnalazioni, richieste di supporto), gli amministratori possano
leggere sotto il profilo di ogni utente le domande e le risposte, le letture, la chat con l'oracolo, le memorie estratte
e i dati di profilazione. Sono dati intimi e spesso particolari (art. 9 GDPR), quindi:

- **solo il ruolo `admin`**, dichiarato sul router;
- **prima un motivo**: `POST …/accesso` con il motivo (5–300 caratteri) apre un accesso di `DURATA_ACCESSO` minuti,
  scritto nel registro (`admin.contenuti.accesso`, con il motivo); ogni scheda si legge solo con quell'accesso, dello
  stesso amministratore e per lo stesso utente;
- **ogni lettura è registrata**: `admin.contenuti.lettura` con la scheda e la pagina;
- gli accessi a un utente si rivedono da `GET …/accessi` (chi, quando, perché, cosa ha aperto).

Cosa non esce mai da qui: lo stato del mazzo e il sale (`deck_state`, `deck_salt`), i vettori delle memorie, i token
dei dispositivi e gli endpoint push (credenziali di consegna, non dati della persona).
"""
from __future__ import annotations

import secrets
from datetime import timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from lanterna.rete import ip_client
from pydantic import BaseModel, Field
from sqlalchemy import func, select

from ...auth.dependencies import CurrentUser, DbSession, require_role
from ...domain.base import utcnow
from ...domain.chat_models import ChatProattivaTurno
from ...domain.consent_models import ConsensoStorico, UserConsent
from ...domain.memory_models import MemoriaStato, UserMemory
from ...domain.models import AuditLog, DailyCard, Reading, User
from ...domain.notifiche_models import DispositivoNotifica, PreferenzeNotifica
from ...domain.repositories import AuditRepository

router = APIRouter(prefix="/admin/users/{user_id}/contenuti", tags=["console"],
                   dependencies=[Depends(require_role("admin"))])

#: Per quanti minuti vale un accesso aperto con un motivo.
DURATA_ACCESSO = 30
AZIONE_ACCESSO = "admin.contenuti.accesso"
AZIONE_LETTURA = "admin.contenuti.lettura"
SCHEDE = ("letture", "chat", "memorie", "profilo")


class NuovoAccesso(BaseModel):
    motivo: str = Field(min_length=5, max_length=300)


async def _utente(session, user_id: int) -> User:
    u = await session.get(User, user_id)
    if u is None:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    return u


def _iso(d) -> Optional[str]:
    return d.isoformat() if d else None


@router.post("/accesso")
async def apri_accesso(user_id: int, payload: NuovoAccesso, request: Request, user: CurrentUser,
                       session: DbSession) -> Dict[str, Any]:
    """Apre un accesso ai contenuti dell'utente: il motivo resta nel registro."""
    await _utente(session, user_id)
    motivo = " ".join(payload.motivo.split())
    if len(motivo) < 5:
        raise HTTPException(status_code=422, detail="Scrivi il motivo dell'accesso (almeno 5 caratteri).")
    accesso = secrets.token_urlsafe(16)
    scade = utcnow() + timedelta(minutes=DURATA_ACCESSO)
    await AuditRepository(session).record(
        action=AZIONE_ACCESSO, actor_id=user.id, target_type="user", target_id=str(user_id),
        after={"accesso": accesso, "motivo": motivo, "scade": scade.isoformat()},
        ip=ip_client(request), correlation_id=getattr(request.state, "correlation_id", None),
    )
    await session.commit()
    return {"accesso": accesso, "scade": scade.isoformat(), "minuti": DURATA_ACCESSO}


async def _verifica(session, user, request: Request, user_id: int, accesso: str, scheda: str,
                    dettagli: Optional[Dict[str, Any]] = None) -> None:
    """Pretende un accesso valido (stesso amministratore, stesso utente, non scaduto) e registra la lettura."""
    if not accesso:
        raise HTTPException(status_code=403, detail="Serve un accesso con il motivo: POST …/contenuti/accesso.")
    limite = utcnow() - timedelta(minutes=DURATA_ACCESSO)
    trovato = (await session.execute(
        select(AuditLog.id).where(
            AuditLog.action == AZIONE_ACCESSO, AuditLog.actor_id == user.id,
            AuditLog.target_type == "user", AuditLog.target_id == str(user_id),
            AuditLog.created_at >= limite, AuditLog.after["accesso"].astext == accesso,
        ).limit(1)
    )).scalar_one_or_none()
    if trovato is None:
        raise HTTPException(status_code=403, detail="Accesso scaduto o non valido: indica di nuovo il motivo.")
    await AuditRepository(session).record(
        action=AZIONE_LETTURA, actor_id=user.id, target_type="user", target_id=str(user_id),
        after={"accesso": accesso, "scheda": scheda, **(dettagli or {})},
        ip=ip_client(request), correlation_id=getattr(request.state, "correlation_id", None),
    )
    await session.commit()


def _pagina(pagina: int, per_pagina: int) -> tuple:
    per_pagina = max(1, min(per_pagina, 50))
    return max(1, pagina), per_pagina


# ---- letture --------------------------------------------------------------------------------------------------


def _lettura_json(r: Reading) -> Dict[str, Any]:
    return {
        "id": str(r.id), "stesa": r.spread_id, "stato": r.status, "lingua": r.lang, "consumo": r.consumo,
        "manuale": r.manuale, "mazzo": r.deck_id,
        "creata": _iso(r.created_at), "completata": _iso(r.completed_at),
        "domanda": r.question,
        "intervista": [{"ruolo": t.ruolo, "testo": t.testo, "quando": _iso(t.created_at)} for t in r.turns],
        "quadro": r.context_summary,
        "carte": [{"posizione": c.posizione, "carta": c.card_id, "rovescio": c.rovescio, "calcolata": c.calcolata,
                   "interpretazione": c.interpretazione} for c in r.cards],
        "sintesi": r.synthesis, "anteprima": r.teaser, "guardrail": r.guard_outcome,
        "memorie_usate": r.memorie_recuperate or [],
        "persone": r.persone,
        "diario": {"esito": r.feedback, "nota": r.feedback_note, "quando": _iso(r.feedback_at)} if r.feedback else None,
        "condivisa": bool(r.share_token), "testo_condivisione": r.share_text,
    }


@router.get("/letture")
async def letture(user_id: int, request: Request, user: CurrentUser, session: DbSession,
                  accesso: str = "", pagina: int = 1, per_pagina: int = 10) -> Dict[str, Any]:
    await _utente(session, user_id)
    pagina, per_pagina = _pagina(pagina, per_pagina)
    await _verifica(session, user, request, user_id, accesso, "letture", {"pagina": pagina})
    totale = (await session.execute(select(func.count()).where(Reading.owner_id == user_id))).scalar_one()
    righe = (await session.execute(
        select(Reading).where(Reading.owner_id == user_id)
        .order_by(Reading.created_at.desc()).offset((pagina - 1) * per_pagina).limit(per_pagina)
    )).scalars().all()
    carte_giorno = (await session.execute(
        select(DailyCard).where(DailyCard.user_id == user_id).order_by(DailyCard.giorno.desc()).limit(30)
    )).scalars().all() if pagina == 1 else []
    return {
        "totale": totale, "pagina": pagina, "per_pagina": per_pagina,
        "letture": [_lettura_json(r) for r in righe],
        "carte_del_giorno": [{"giorno": _iso(c.giorno), "carta": c.card_id, "rovescio": c.rovescio, "testo": c.testo}
                             for c in carte_giorno],
    }


# ---- chat -----------------------------------------------------------------------------------------------------


@router.get("/chat")
async def chat(user_id: int, request: Request, user: CurrentUser, session: DbSession,
               accesso: str = "", pagina: int = 1, per_pagina: int = 50) -> Dict[str, Any]:
    await _utente(session, user_id)
    pagina, per_pagina = _pagina(pagina, per_pagina)
    await _verifica(session, user, request, user_id, accesso, "chat", {"pagina": pagina})
    totale = (await session.execute(
        select(func.count()).where(ChatProattivaTurno.owner_id == user_id))).scalar_one()
    righe = (await session.execute(
        select(ChatProattivaTurno).where(ChatProattivaTurno.owner_id == user_id)
        .order_by(ChatProattivaTurno.ordine.desc()).offset((pagina - 1) * per_pagina).limit(per_pagina)
    )).scalars().all()
    return {
        "totale": totale, "pagina": pagina, "per_pagina": per_pagina,
        # dal più recente; la console li rimette in ordine di conversazione
        "messaggi": [{"ordine": t.ordine, "ruolo": t.ruolo, "testo": t.testo, "proposta": t.proposta,
                      "quando": _iso(t.created_at)} for t in righe],
    }


# ---- memorie --------------------------------------------------------------------------------------------------


@router.get("/memorie")
async def memorie(user_id: int, request: Request, user: CurrentUser, session: DbSession,
                  accesso: str = "") -> Dict[str, Any]:
    await _utente(session, user_id)
    await _verifica(session, user, request, user_id, accesso, "memorie")
    righe = (await session.execute(
        select(UserMemory).where(UserMemory.owner_id == user_id).order_by(UserMemory.created_at.desc()).limit(500)
    )).scalars().all()
    stato = await session.get(MemoriaStato, user_id)
    return {
        "stato_sintetico": {"voci": stato.voci, "aggiornato": _iso(stato.updated_at)} if stato else None,
        "memorie": [{"id": str(m.id), "contenuto": m.contenuto, "tipo": m.tipo, "campo": m.campo_attinenza,
                     "fonte": m.fonte, "lettura": str(m.reading_id) if m.reading_id else None,
                     "sostituita_da": str(m.superseded_by) if m.superseded_by else None,
                     "creata": _iso(m.created_at)} for m in righe],
    }


# ---- profilazione ---------------------------------------------------------------------------------------------


@router.get("/profilo")
async def profilo(user_id: int, request: Request, user: CurrentUser, session: DbSession,
                  accesso: str = "") -> Dict[str, Any]:
    u = await _utente(session, user_id)
    await _verifica(session, user, request, user_id, accesso, "profilo")
    consensi = (await session.execute(
        select(UserConsent).where(UserConsent.user_id == user_id).order_by(UserConsent.tipo)
    )).scalars().all()
    storico = (await session.execute(
        select(ConsensoStorico).where(ConsensoStorico.user_id == user_id)
        .order_by(ConsensoStorico.created_at.desc()).limit(200)
    )).scalars().all()
    preferenze = await session.get(PreferenzeNotifica, user_id)
    dispositivi = (await session.execute(
        select(DispositivoNotifica).where(DispositivoNotifica.user_id == user_id)
        .order_by(DispositivoNotifica.created_at.desc())
    )).scalars().all()
    invitati = (await session.execute(select(func.count()).where(User.referred_by == user_id))).scalar_one()
    return {
        "persona": {
            "nome": u.nome, "cognome": u.cognome, "nome_pubblico": u.nome_pubblico, "email": u.email,
            "nascita": _iso(u.birth_date), "genere": u.gender, "genere_altro": u.gender_custom, "trans": u.is_trans,
            "eta_confermata": {"anni": u.eta_confermata_anni, "quando": _iso(u.eta_confermata_il)},
            "lingua": u.locale, "lingua_scelta_il": _iso(u.locale_scelta_il), "fuso_orario": u.fuso_orario,
            "registro_linguistico": u.registro_linguistico,
            "partner_ricordato": u.partner_ricordato,
            "posizione": {"paese": u.posizione_paese, "citta": u.posizione_citta, "fonte": u.posizione_fonte,
                          "quando": _iso(u.posizione_il)},
            "dati_social": u.dati_social or {}, "importa_social": u.importa_social,
            "rileva_posizione": u.rileva_posizione,
            "invitato_da": u.referred_by, "codice_invito": u.referral_code, "invitati": invitati,
            "premi_condivisione": u.share_rewards,
            "cancellazione_richiesta": _iso(u.cancellazione_richiesta_il),
        },
        "consensi": [{"tipo": c.tipo, "valore": c.valore, "informativa": c.versione_informativa, "origine": c.origine,
                      "aggiornato": _iso(c.updated_at)} for c in consensi],
        "storico_consensi": [{"tipo": c.tipo, "valore": c.valore, "informativa": c.versione_informativa,
                              "origine": c.origine, "quando": _iso(c.created_at)} for c in storico],
        "notifiche": {
            "carta_del_giorno": preferenze.carta_giorno, "ora_carta": _iso(preferenze.ora_carta),
            "silenzio": [_iso(preferenze.silenzio_dal), _iso(preferenze.silenzio_al)],
            "promemoria": preferenze.promemoria,
            "tetto_promozioni_settimana": preferenze.tetto_promozioni_settimana,
        } if preferenze else None,
        "dispositivi": [{"canale": d.canale, "piattaforma": d.piattaforma, "lingua": d.lingua,
                         "fuso_orario": d.fuso_orario, "versione_app": d.versione_app, "attivo": d.attivo,
                         "ultimo_visto": _iso(d.ultimo_visto), "registrato": _iso(d.created_at)} for d in dispositivi],
    }


# ---- il registro degli accessi --------------------------------------------------------------------------------


@router.get("/accessi")
async def accessi(user_id: int, session: DbSession, limite: int = 100) -> Dict[str, Any]:
    """Chi ha aperto i contenuti di questo utente, quando, perché e quali schede. Leggerlo non apre i contenuti."""
    await _utente(session, user_id)
    righe = (await session.execute(
        select(AuditLog, User.email).join(User, User.id == AuditLog.actor_id, isouter=True).where(
            AuditLog.action.in_((AZIONE_ACCESSO, AZIONE_LETTURA)),
            AuditLog.target_type == "user", AuditLog.target_id == str(user_id),
        ).order_by(AuditLog.created_at.desc()).limit(max(1, min(limite, 500)))
    )).all()
    return {"accessi": [
        {"quando": _iso(a.created_at), "chi": email or a.actor_id,
         "azione": "accesso" if a.action == AZIONE_ACCESSO else "lettura",
         "motivo": (a.after or {}).get("motivo"), "scheda": (a.after or {}).get("scheda"),
         "pagina": (a.after or {}).get("pagina")}
        for a, email in righe
    ]}
