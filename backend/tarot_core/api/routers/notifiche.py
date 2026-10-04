"""Le notifiche dal lato di chi le riceve (v9, Fase 5): dispositivi, preferenze, fuso orario, apertura, disiscrizione.

- `POST/DELETE /me/dispositivi`: il sito registra la sottoscrizione Web Push del browser, l'app il token FCM (con la
  piattaforma, la lingua, il fuso e la versione). **Solo con un account**: la carta del giorno personale e le
  promozioni (che chiedono il consenso `marketing`) hanno senso solo per chi ne ha uno. Lo stesso dispositivo
  registrato da un altro account passa a quell'account (il telefono ha cambiato proprietario, o si è entrati con un
  altro profilo).
- `GET/PUT /me/preferenze-notifica`: carta del giorno e la sua ora, ore di silenzio, promemoria, tetto delle
  promozioni; `PUT /me/fuso-orario`: il fuso rilevato dal sito (`Intl`) o dall'app, salvato in automatico.
- `GET /notifiche/vapid`: la chiave pubblica VAPID per `PushManager.subscribe` (pubblica per definizione).
- `POST /notifiche/aperta`: il service worker (o l'app) dice che la notifica è stata toccata; la firma HMAC
  dell'invio impedisce di segnare quelle degli altri.
- `GET /notifiche/disiscrivi?t=`: il link «niente più promozioni» delle notifiche, in un clic e senza accesso (token
  HMAC per quella persona). Revoca il consenso `marketing`, con la riga nello storico dei consensi come ogni revoca.
"""
from __future__ import annotations

import hashlib
import html
import uuid
from datetime import time
from typing import Any, Dict, Literal, Optional

from fastapi import APIRouter, HTTPException, Query, Request, Response
from fastapi.responses import HTMLResponse
from lanterna.rete import ip_client
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import delete, select

from ...auth.dependencies import CurrentUser, DbSession
from ...domain import consent_repositories
from ...domain.base import utcnow
from ...domain.notifiche_models import DispositivoNotifica, PreferenzeNotifica
from ...domain.repositories import AuditRepository
from ...notifiche import config as conf
from ...notifiche.invio import lingua_di, preferenze_effettive, segna_aperta

router = APIRouter(tags=["notifiche"])

#: La versione del «testo» della revoca in un clic, nello storico dei consensi.
VERSIONE_DISISCRIZIONE = "disiscrivi-v1"


def impronta(canale: str, token: Optional[str], endpoint: Optional[str]) -> str:
    valore = (token if canale == "fcm" else endpoint) or ""
    return hashlib.sha256(f"{canale}:{valore}".encode("utf-8")).hexdigest()


class DispositivoIn(BaseModel):
    canale: Literal["fcm", "webpush"]
    piattaforma: Literal["android", "ios", "web"]
    token: Optional[str] = Field(default=None, min_length=20, max_length=4096)
    endpoint: Optional[str] = Field(default=None, min_length=12, max_length=2048, pattern=r"^https://")
    p256dh: Optional[str] = Field(default=None, min_length=20, max_length=200, pattern=r"^[A-Za-z0-9_\-=]+$")
    auth: Optional[str] = Field(default=None, min_length=8, max_length=100, pattern=r"^[A-Za-z0-9_\-=]+$")
    lingua: Optional[str] = Field(default=None, max_length=10)
    fuso_orario: Optional[str] = Field(default=None, max_length=64)
    versione_app: Optional[str] = Field(default=None, max_length=40)

    @model_validator(mode="after")
    def _coerente(self) -> "DispositivoIn":
        if self.canale == "fcm" and not self.token:
            raise ValueError("Per FCM serve il token del dispositivo")
        if self.canale == "webpush" and not (self.endpoint and self.p256dh and self.auth):
            raise ValueError("Per il Web Push servono endpoint, p256dh e auth della sottoscrizione")
        if self.canale == "webpush" and self.piattaforma != "web":
            raise ValueError("Il Web Push è solo del sito (piattaforma web)")
        return self


class DispositivoVia(BaseModel):
    canale: Literal["fcm", "webpush"]
    token: Optional[str] = Field(default=None, max_length=4096)
    endpoint: Optional[str] = Field(default=None, max_length=2048)


def _dispositivo_json(d: DispositivoNotifica) -> Dict[str, Any]:
    return {
        "id": d.id, "canale": d.canale, "piattaforma": d.piattaforma, "attivo": d.attivo, "lingua": d.lingua,
        "versione_app": d.versione_app, "registrato_il": d.created_at.isoformat() if d.created_at else None,
        "ultimo_visto": d.ultimo_visto.isoformat() if d.ultimo_visto else None,
    }


@router.post("/me/dispositivi")
async def registra_dispositivo(payload: DispositivoIn, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    chiave = impronta(payload.canale, payload.token, payload.endpoint)
    adesso = utcnow()
    d = (await session.execute(select(DispositivoNotifica).where(DispositivoNotifica.impronta == chiave))).scalar_one_or_none()
    nuovo = d is None
    if d is None:
        d = DispositivoNotifica(impronta=chiave, canale=payload.canale)
        session.add(d)
    d.user_id, d.anon_id = user.id, None
    d.piattaforma = payload.piattaforma
    d.token = payload.token if payload.canale == "fcm" else None
    d.endpoint, d.p256dh, d.auth = (payload.endpoint, payload.p256dh, payload.auth) if payload.canale == "webpush" else (None, None, None)
    d.lingua = lingua_di(payload.lingua or user.locale)
    fuso = conf.valida_fuso(payload.fuso_orario)
    d.fuso_orario = fuso
    d.versione_app = payload.versione_app
    d.attivo, d.errori, d.ultimo_errore, d.disattivato_il = True, 0, None, None
    d.ultimo_visto = adesso
    if fuso and user.fuso_orario != fuso:
        user.fuso_orario = fuso
    await session.flush()
    if nuovo:
        await AuditRepository(session).record(
            action="notifiche.dispositivo", actor_id=user.id, target_type="dispositivo_notifica", target_id=str(d.id),
            after={"canale": d.canale, "piattaforma": d.piattaforma}, ip=ip_client(request),
        )
    await session.commit()
    return _dispositivo_json(d)


@router.delete("/me/dispositivi", status_code=204)
async def togli_dispositivo(payload: DispositivoVia, user: CurrentUser, session: DbSession) -> Response:
    """Il browser ha tolto la sottoscrizione (o l'app è uscita dall'account): la riga si cancella davvero."""
    await session.execute(delete(DispositivoNotifica).where(
        DispositivoNotifica.user_id == user.id,
        DispositivoNotifica.impronta == impronta(payload.canale, payload.token, payload.endpoint),
    ))
    await session.commit()
    return Response(status_code=204)


class PreferenzeIn(BaseModel):
    carta_giorno: Optional[bool] = None
    ora_carta: Optional[time] = None
    #: Entrambe nulle con `silenzio: false`: nessun silenzio.
    silenzio: Optional[bool] = None
    silenzio_dal: Optional[time] = None
    silenzio_al: Optional[time] = None
    promemoria: Optional[bool] = None
    tetto_promozioni_settimana: Optional[int] = Field(default=None, ge=0, le=14)


async def _preferenze_json(session, user) -> Dict[str, Any]:
    cfg = await conf.config(session)
    riga = await session.get(PreferenzeNotifica, user.id)
    p = preferenze_effettive(riga, cfg)
    dispositivi = (await session.execute(
        select(DispositivoNotifica).where(DispositivoNotifica.user_id == user.id).order_by(DispositivoNotifica.id)
    )).scalars().all()
    return {
        "carta_giorno": p.carta_giorno,
        "ora_carta": conf.ora_testo(p.ora_carta),
        "silenzio": p.silenzio_dal is not None and p.silenzio_al is not None,
        "silenzio_dal": conf.ora_testo(p.silenzio_dal) or conf.ora_testo(cfg.silenzio_dal),
        "silenzio_al": conf.ora_testo(p.silenzio_al) or conf.ora_testo(cfg.silenzio_al),
        "promemoria": p.promemoria,
        "tetto_promozioni_settimana": riga.tetto_promozioni_settimana if riga else cfg.tetto_promozioni_settimana,
        "tetto_massimo": cfg.tetto_promozioni_settimana,
        "promozioni": await consent_repositories.accettato(session, user.id, "marketing"),
        "fuso_orario": user.fuso_orario,
        "personalizzate": riga is not None,
        "dispositivi": [_dispositivo_json(d) for d in dispositivi],
    }


@router.get("/me/preferenze-notifica")
async def leggi_preferenze(user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    dati = await _preferenze_json(session, user)
    await session.commit()
    return dati


@router.put("/me/preferenze-notifica")
async def modifica_preferenze(payload: PreferenzeIn, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    cfg = await conf.config(session)
    riga = await session.get(PreferenzeNotifica, user.id)
    if riga is None:
        riga = PreferenzeNotifica(
            user_id=user.id, carta_giorno=True, ora_carta=cfg.ora_carta, silenzio_dal=cfg.silenzio_dal,
            silenzio_al=cfg.silenzio_al, promemoria=True, tetto_promozioni_settimana=cfg.tetto_promozioni_settimana,
        )
        session.add(riga)
        # Prima la riga con i predefiniti, poi le modifiche: un `None` nell'INSERT lascerebbe il default del database
        # (22:00) al posto di «nessun silenzio».
        await session.flush()
    for campo in ("carta_giorno", "ora_carta", "promemoria", "tetto_promozioni_settimana"):
        valore = getattr(payload, campo)
        if valore is not None:
            setattr(riga, campo, valore.replace(second=0, microsecond=0, tzinfo=None) if isinstance(valore, time) else valore)
    if payload.silenzio is False:
        riga.silenzio_dal = riga.silenzio_al = None
    elif payload.silenzio is True or payload.silenzio_dal or payload.silenzio_al:
        riga.silenzio_dal = (payload.silenzio_dal or riga.silenzio_dal or cfg.silenzio_dal or time(22)).replace(second=0, microsecond=0, tzinfo=None)
        riga.silenzio_al = (payload.silenzio_al or riga.silenzio_al or cfg.silenzio_al or time(8)).replace(second=0, microsecond=0, tzinfo=None)
    await session.flush()
    dati = await _preferenze_json(session, user)
    await session.commit()
    return dati


class FusoIn(BaseModel):
    fuso_orario: str = Field(min_length=1, max_length=64)


@router.put("/me/fuso-orario")
async def imposta_fuso(payload: FusoIn, user: CurrentUser, session: DbSession) -> Dict[str, Optional[str]]:
    """Il fuso del browser o del telefono, salvato in automatico: decide il giorno della carta del giorno."""
    fuso = conf.valida_fuso(payload.fuso_orario)
    if fuso is None:
        raise HTTPException(status_code=422, detail="Fuso orario sconosciuto")
    if user.fuso_orario != fuso:
        user.fuso_orario = fuso
        await session.commit()
    return {"fuso_orario": fuso}


@router.get("/notifiche/vapid")
async def chiave_vapid(session: DbSession) -> Dict[str, Any]:
    _, pubblica = await conf.chiavi_vapid(session)
    await session.commit()
    if not pubblica:
        raise HTTPException(status_code=503, detail="Web Push non disponibile")
    return {"chiave": pubblica}


class Apertura(BaseModel):
    invio: uuid.UUID
    firma: str = Field(min_length=8, max_length=64)


@router.post("/notifiche/aperta", status_code=204)
async def notifica_aperta(payload: Apertura, session: DbSession) -> Response:
    chiave = await conf.chiave_firma(session)
    if not conf.firma_valida(chiave, f"aperta:{payload.invio}", payload.firma):
        raise HTTPException(status_code=403, detail="Firma non valida")
    await segna_aperta(session, payload.invio)
    await session.commit()
    return Response(status_code=204)


#: La pagina della disiscrizione, nelle sei lingue: (titolo, testo, link al profilo).
_PAGINA = {
    "en": ("Done", "You won't receive promotions from TAROTS chat any more. Your card of the day and service reminders "
                   "stay as you chose: you can change everything from your profile.", "Open your profile"),
    "it": ("Fatto", "Non riceverai più promozioni da TAROTS chat. La carta del giorno e i promemoria restano come li hai "
                    "scelti: puoi cambiare tutto dal profilo.", "Apri il profilo"),
    "hu": ("Kész", "Többé nem kapsz ajánlatokat a TAROTS chattől. A napi kártya és az emlékeztetők úgy maradnak, ahogy "
                   "beállítottad: mindent módosíthatsz a profilodban.", "Profil megnyitása"),
    "ru": ("Готово", "Ты больше не будешь получать акции от TAROTS chat. Карта дня и напоминания остаются такими, как ты "
                     "выбрал(а): всё можно изменить в профиле.", "Открыть профиль"),
    "uk": ("Готово", "Ти більше не отримуватимеш акцій від TAROTS chat. Карта дня й нагадування залишаються такими, як ти "
                     "обрав(ла): усе можна змінити в профілі.", "Відкрити профіль"),
    "es": ("Hecho", "Ya no recibirás promociones de TAROTS chat. La carta del día y los recordatorios siguen como los "
                    "elegiste: puedes cambiarlo todo desde tu perfil.", "Abrir tu perfil"),
}
_NON_VALIDO = {
    "en": "This link is not valid. You can turn promotions off from your profile, under Notifications.",
    "it": "Questo link non è valido. Puoi spegnere le promozioni dal profilo, alla voce Notifiche.",
}


def _pagina(lingua: str, titolo: str, testo: str, link: Optional[str], etichetta: str, stato: int) -> HTMLResponse:
    from ...settings import get_settings

    profilo = get_settings().web_public_url.rstrip("/") + "/profile#notifiche"
    corpo = (
        f'<!doctype html><html lang="{lingua}"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">'
        f"<title>{html.escape(titolo)} · TAROTS chat</title>"
        "<style>body{font:16px/1.6 system-ui,sans-serif;margin:0;padding:max(24px,env(safe-area-inset-top)) 16px;"
        "background:#f6f1e7;color:#1d1a16}main{max-width:32rem;margin:10vh auto}h1{font-family:Georgia,serif}"
        "a{display:inline-block;min-height:48px;line-height:48px;padding:0 20px;border-radius:999px;background:#1d1a16;"
        "color:#f6f1e7;text-decoration:none}a:focus-visible{outline:3px solid #b8892d;outline-offset:3px}"
        "@media (prefers-color-scheme:dark){body{background:#14110e;color:#efe7da}a{background:#efe7da;color:#14110e}}"
        "</style></head><body><main>"
        f"<h1>{html.escape(titolo)}</h1><p>{html.escape(testo)}</p>"
        f'<p><a href="{html.escape(link or profilo)}">{html.escape(etichetta)}</a></p></main></body></html>'
    )
    return HTMLResponse(corpo, status_code=stato, headers={"Cache-Control": "no-store"})


@router.get("/notifiche/disiscrivi", response_class=HTMLResponse)
async def disiscrivi(request: Request, session: DbSession, t: str = Query(default="", max_length=200)) -> HTMLResponse:
    from ...domain.models import User

    chiave = await conf.chiave_firma(session)
    letto = conf.leggi_token_disiscrizione(chiave, t)
    utente = await session.get(User, letto[0]) if letto else None
    if letto is None or utente is None:
        await session.commit()
        lingua = "it" if (request.headers.get("accept-language") or "").lower().startswith("it") else "en"
        return _pagina(lingua, "TAROTS chat", _NON_VALIDO[lingua], None, _PAGINA[lingua][2], 400)
    lingua = lingua_di(utente.locale)
    _, ambito = letto
    if await consent_repositories.accettato(session, utente.id, "marketing"):
        await consent_repositories.registra(
            session, user_id=utente.id, anon_id=None, tipo="marketing", valore="rifiutato",
            versione_informativa=VERSIONE_DISISCRIZIONE, ip=ip_client(request), origine="web",
        )
    if ambito == "tutte":
        cfg = await conf.config(session)
        riga = await session.get(PreferenzeNotifica, utente.id)
        if riga is None:
            riga = PreferenzeNotifica(user_id=utente.id, ora_carta=cfg.ora_carta, silenzio_dal=cfg.silenzio_dal,
                                      silenzio_al=cfg.silenzio_al, tetto_promozioni_settimana=cfg.tetto_promozioni_settimana)
            session.add(riga)
        riga.carta_giorno = False
        riga.promemoria = False
    await session.commit()
    titolo, testo, etichetta = _PAGINA[lingua]
    return _pagina(lingua, titolo, testo, None, etichetta, 200)
