"""Gli abbonamenti dal lato dell'utente (v9, Fase 2b): rinnovo automatico, cambio di piano col conguaglio, prova
gratuita, «Sistema il pagamento».

| endpoint | cosa |
|---|---|
| `GET /abbonamenti/pubblico` | banner e prova: acceso, giorni, sconti (anche senza account) |
| `GET /me/abbonamento` | la sezione «Abbonamento» del profilo: stato, rinnovo, prossimo addebito, prova, fattura |
| `POST /me/abbonamento/rinnovo` | spegne o riaccende il rinnovo automatico (email di conferma) |
| `POST /me/abbonamento/cambio/anteprima` | le tre righe del conguaglio, senza toccare niente |
| `POST /me/abbonamento/cambio` | upgrade → il pagamento (Checkout); downgrade → programmato alla scadenza |
| `DELETE /me/abbonamento/cambio` | toglie il downgrade programmato |
| `GET /me/abbonamento/pagamento` | dove pagare la fattura aperta (la stessa, mai un nuovo addebito) |
| `POST /me/prova` | la prova gratuita: il Checkout che registra il metodo di pagamento |

Gli abbonamenti degli store rispondono 409 `store` con il link alla gestione dello store: lì si spegne il rinnovo e
lì si cambia piano (il conguaglio lo fa lo store).
"""
from __future__ import annotations

import html
import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy import select

from ...analytics import eventi as analytics
from ...auth.dependencies import CurrentUser, DbSession
from ...billing import abbonamenti as gestione
from ...billing.credits import RegistroCrediti
from ...billing.pagamenti import RINNOVATO, GestorePagamenti, PagamentiDisattivati, PagamentiNonDisponibili, PagamentiSimulati, provider_pagamenti
from ...billing.plans import GestoreAbbonamenti
from ...domain.billing_models import Subscription
from ...settings import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["abbonamenti"])

LINGUA = Query(default=None, pattern="^[a-z]{2}$")


class Rinnovo(BaseModel):
    attivo: bool


class Cambio(BaseModel):
    piano: str = Field(min_length=1, max_length=40)
    annuale: bool = False
    #: Il rinnovo automatico del piano nuovo: acceso, il prezzo ha lo sconto del rinnovo.
    rinnovo: bool = True
    ritorno: Optional[str] = Field(default=None, max_length=300)


class Prova(BaseModel):
    piano: str = Field(min_length=1, max_length=40)
    ritorno: Optional[str] = Field(default=None, max_length=300)
    #: Fase 2d: un codice sconto (dal link). Si somma allo sconto della prova o vale il più alto dei due.
    coupon: Optional[str] = Field(default=None, max_length=60)


def _errore(exc: gestione.ErroreAbbonamento) -> HTTPException:
    codice = status.HTTP_404_NOT_FOUND if exc.motivo == "nessun_abbonamento" else status.HTTP_409_CONFLICT
    if exc.motivo == "piano_non_valido":
        codice = status.HTTP_422_UNPROCESSABLE_ENTITY
    return HTTPException(status_code=codice, detail={"motivo": exc.motivo, "messaggio": str(exc), **exc.dati})


def _pagamenti_attivi() -> bool:
    return not isinstance(provider_pagamenti(), PagamentiDisattivati)


async def _abbonamento_pagato(session, user_id: int) -> Subscription:
    abbonamento = await GestoreAbbonamenti(session).abbonamento_di(user_id)
    if abbonamento is None or gestione.gratuito(abbonamento.plan):
        raise _errore(gestione.ErroreAbbonamento("nessun_abbonamento", "Non hai un abbonamento a pagamento attivo."))
    return abbonamento


@router.get("/abbonamenti/pubblico")
async def pubblico(session: DbSession) -> Dict[str, Any]:
    """Il banner e la pagina della prova li leggono anche senza account: cosa offre la prova e se è accesa."""
    riga = await gestione.impostazioni(session)
    attivi = _pagamenti_attivi()
    await session.commit()
    return {
        "banner_prova": bool(riga.banner_prova and attivi),
        "prova_disponibile": attivi,
        "giorni_prova": riga.giorni_prova,
        "sconto_prova": riga.sconto_prova,
        "sconto_rinnovo": riga.sconto_rinnovo,
        "condoni_per_periodo": riga.condoni_per_periodo,
        "giorni_promemoria_prova": riga.giorni_promemoria_prova,
        "giorni_tolleranza": riga.giorni_tolleranza,
    }


@router.get("/me/abbonamento")
async def il_mio_abbonamento(user: CurrentUser, session: DbSession, lang: Optional[str] = LINGUA) -> Dict[str, Any]:
    riga = await gestione.impostazioni(session)
    abbonamento = await gestione.ultimo_abbonamento(session, user.id)
    vivo = await GestoreAbbonamenti(session).abbonamento_di(user.id)
    idonea, motivo = await gestione.idoneita_prova(session, user.id, vivo)
    prova = await gestione.prova_di(session, user.id)
    await session.commit()
    return {
        "abbonamento": gestione.abbonamento_json(abbonamento, lang, tolleranza=riga.giorni_tolleranza),
        "prova": {
            "idonea": idonea and _pagamenti_attivi(), "motivo": motivo,
            "usata_il": prova.created_at.isoformat() if prova else None,
        },
        "impostazioni": {
            "sconto_rinnovo": riga.sconto_rinnovo, "sconto_prova": riga.sconto_prova, "giorni_prova": riga.giorni_prova,
            "giorni_tolleranza": riga.giorni_tolleranza,
        },
        "saldo": await RegistroCrediti(session).saldo(user.id),
    }


@router.post("/me/abbonamento/rinnovo")
async def rinnovo(payload: Rinnovo, user: CurrentUser, session: DbSession, lang: Optional[str] = LINGUA) -> Dict[str, Any]:
    """Spegne (con la conferma formale per email) o riaccende il rinnovo automatico."""
    abbonamento = await _abbonamento_pagato(session, user.id)
    try:
        await gestione.imposta_rinnovo(session, abbonamento, payload.attivo, configurato=provider_pagamenti(), utente=user)
    except gestione.ErroreAbbonamento as exc:
        raise _errore(exc) from exc
    except PagamentiNonDisponibili as exc:
        # Il fornitore non ha confermato: meglio dirlo che segnarlo qui e lasciarlo addebitare.
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    await session.commit()
    await session.refresh(abbonamento, ["plan", "piano_successivo"])
    riga = await gestione.impostazioni(session)
    return {"abbonamento": gestione.abbonamento_json(abbonamento, lang, tolleranza=riga.giorni_tolleranza)}


async def _piano(session, slug: str):
    piano = await GestoreAbbonamenti(session).piano_per_slug(slug)
    if piano is None or not piano.active:
        raise HTTPException(status_code=404, detail=f"Il piano «{slug}» non esiste o non è più offerto.")
    return piano


@router.post("/me/abbonamento/cambio/anteprima")
async def anteprima_cambio(payload: Cambio, user: CurrentUser, session: DbSession, lang: Optional[str] = LINGUA) -> Dict[str, Any]:
    """Il conto del cambio di piano, riga per riga: valore residuo, abbonamento nuovo, totale."""
    abbonamento = await _abbonamento_pagato(session, user.id)
    piano = await _piano(session, payload.piano)
    try:
        conto = await gestione.anteprima_cambio(session, abbonamento, piano, annuale=payload.annuale, rinnovo=payload.rinnovo)
    except gestione.ErroreAbbonamento as exc:
        raise _errore(exc) from exc
    await session.commit()
    return conto.to_dict(lang)


@router.post("/me/abbonamento/cambio")
async def cambia(payload: Cambio, user: CurrentUser, session: DbSession, lang: Optional[str] = LINGUA) -> Dict[str, Any]:
    """Un upgrade apre il pagamento del totale mostrato (il vecchio si chiude quando il nuovo è pagato); un downgrade
    si programma per la fine del periodo pagato."""
    from .billing import _ritorno_valido

    abbonamento = await _abbonamento_pagato(session, user.id)
    piano = await _piano(session, payload.piano)
    configurato = provider_pagamenti()
    try:
        await gestione.verifica_nessuna_fattura_aperta(session, user.id)
        conto = await gestione.anteprima_cambio(session, abbonamento, piano, annuale=payload.annuale, rinnovo=payload.rinnovo)
        if conto.tipo == "downgrade":
            await gestione.programma_downgrade(session, abbonamento, piano, annuale=payload.annuale, configurato=configurato)
            await session.commit()
            riga = await gestione.impostazioni(session)
            return {"tipo": "downgrade", "conguaglio": conto.to_dict(lang),
                    "abbonamento": gestione.abbonamento_json(abbonamento, lang, tolleranza=riga.giorni_tolleranza)}
    except gestione.ErroreAbbonamento as exc:
        raise _errore(exc) from exc
    except PagamentiNonDisponibili as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    base = get_settings().web_public_url.rstrip("/")
    ritorno = _ritorno_valido(payload.ritorno, base) if payload.ritorno else f"{base}/pricing"
    try:
        async with session.begin_nested():
            checkout, url = await GestorePagamenti(session, configurato).apri(
                user.id, piano, annuale=payload.annuale, ritorno=ritorno, rinnovo=payload.rinnovo,
                sconto_rinnovo=conto.sconto_rinnovo, residuo=conto.residuo, sostituisce=abbonamento,
            )
    except PagamentiNonDisponibili as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    if checkout.importo != conto.totale:
        # Non deve succedere: l'anteprima e il checkout fanno lo stesso conto. Se succede, non si fa pagare una cifra
        # diversa da quella mostrata.
        logger.error("Conguaglio diverso dall'anteprima: %s ≠ %s", checkout.importo, conto.totale)
        raise HTTPException(status_code=409, detail={"motivo": "conto_cambiato", "messaggio": "Il conto è cambiato: riprova."})
    await analytics.evento(
        session, analytics.CHECKOUT_AVVIATO, utente_id=user.id, valore_centesimi=checkout.importo, valuta=checkout.currency,
        proprieta={"tipo": "abbonamento", "piano": piano.slug, "annuale": payload.annuale, "coupon": False, "cambio": True},
    )
    await session.commit()
    return {"tipo": "upgrade", "conguaglio": conto.to_dict(lang), "checkout_id": str(checkout.id), "url": url,
            "importo": checkout.importo, "valuta": checkout.currency}


@router.delete("/me/abbonamento/cambio")
async def annulla_cambio(user: CurrentUser, session: DbSession, lang: Optional[str] = LINGUA) -> Dict[str, Any]:
    abbonamento = await _abbonamento_pagato(session, user.id)
    try:
        await gestione.annulla_downgrade(session, abbonamento, configurato=provider_pagamenti())
    except PagamentiNonDisponibili as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    await session.commit()
    riga = await gestione.impostazioni(session)
    return {"abbonamento": gestione.abbonamento_json(abbonamento, lang, tolleranza=riga.giorni_tolleranza)}


@router.get("/me/abbonamento/pagamento")
async def sistema_pagamento(user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    """Dove saldare il pagamento rimasto in sospeso: **la stessa fattura aperta** presso il fornitore. Pagarla ferma
    i tentativi automatici, e non c'è un secondo addebito. Per gli store: la gestione dello store."""
    abbonamento = await gestione.fattura_aperta_di(session, user.id)
    if abbonamento is None:
        vivo = await GestoreAbbonamenti(session).abbonamento_di(user.id)
        if vivo is not None and gestione.nello_store(vivo) and vivo.status == "in_sospeso":
            abbonamento = vivo
    if abbonamento is None:
        raise HTTPException(status_code=404, detail={"motivo": "niente_da_pagare", "messaggio": "Non c'è niente da pagare."})
    if gestione.nello_store(abbonamento):
        return {"provider": abbonamento.provider, "store": True, "url": gestione.GESTIONE_STORE.get(abbonamento.provider)}
    fornitore = gestione.fornitore_per(abbonamento, provider_pagamenti())
    url_fattura = getattr(fornitore, "url_fattura", None) if fornitore is not None else None
    if url_fattura is None or not abbonamento.fattura_aperta:
        raise HTTPException(status_code=503, detail="Il pagamento non è disponibile in questo momento: riprova fra poco.")
    try:
        url = await url_fattura(abbonamento.fattura_aperta)
    except PagamentiNonDisponibili as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if url is None:
        # La fattura non è più aperta: pagata (l'evento arriverà) o annullata.
        return {"provider": abbonamento.provider, "store": False, "url": None, "gia_pagata": True}
    return {"provider": abbonamento.provider, "store": False, "url": url}


@router.post("/me/prova", status_code=status.HTTP_201_CREATED)
async def inizia_prova(payload: Prova, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    """La prova gratuita: il Checkout registra il metodo di pagamento, oggi non si paga niente; alla fine della prova
    l'annuale del livello scelto con lo sconto della prova, per sempre (si disdice dal profilo)."""
    from ...billing import offerte
    from .billing import _chiavi_tentativi, _conta_tentativo, _errore_coupon, _limita_tentativi, _ritorno_valido

    piano = await _piano(session, payload.piano)
    if piano.pacchetto or piano.price_yearly <= 0:
        raise HTTPException(status_code=422, detail={"motivo": "piano_non_valido", "messaggio": "La prova vale per gli abbonamenti annuali."})
    vivo = await GestoreAbbonamenti(session).abbonamento_di(user.id)
    idonea, motivo = await gestione.idoneita_prova(session, user.id, vivo)
    if not idonea:
        raise HTTPException(status_code=409, detail={"motivo": motivo, "messaggio": "La prova gratuita non è disponibile per questo account."})
    try:
        await gestione.verifica_nessuna_fattura_aperta(session, user.id)
    except gestione.ErroreAbbonamento as exc:
        raise _errore(exc) from exc
    riga = await gestione.impostazioni(session)
    base = get_settings().web_public_url.rstrip("/")
    ritorno = _ritorno_valido(payload.ritorno, base) if payload.ritorno else f"{base}/trial"
    sconto_prova = gestione.percentuale(piano.price_yearly, riga.sconto_prova)
    composizione = None
    if payload.coupon and payload.coupon.strip():
        # Fase 2d: il coupon contro (o insieme a) lo sconto della prova, sulla conversione e sui rinnovi.
        chiavi = _chiavi_tentativi(request, user.id)
        _limita_tentativi(chiavi)
        try:
            valutato = await offerte.valuta(session, user.id, payload.coupon, piano, annuale=True)
            composizione = offerte.componi(valutato.listino, base=sconto_prova, valutato=valutato, prova=True)
        except offerte.CouponNonValido as exc:
            _conta_tentativo(chiavi, exc)
            raise _errore_coupon(exc) from exc
    applicato = composizione is not None and composizione.applicato
    try:
        async with session.begin_nested():
            checkout, url = await GestorePagamenti(session).apri(
                user.id, piano, annuale=True, ritorno=ritorno, prova=True, giorni_prova=riga.giorni_prova,
                sconto_rinnovo=sconto_prova, sconto=composizione.sconto_per_pagamento() if applicato else None,
                sconto_ricorrente=composizione.sconto_ricorrente if applicato else None,
            )
    except PagamentiNonDisponibili as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    await analytics.evento(
        session, analytics.CHECKOUT_AVVIATO, utente_id=user.id, valore_centesimi=0, valuta=checkout.currency,
        proprieta={"tipo": "prova", "piano": piano.slug, "annuale": True, "coupon": applicato},
    )
    await session.commit()
    return {"checkout_id": str(checkout.id), "url": url, "importo": 0, "valuta": checkout.currency, "prova": True,
            "coupon": composizione.to_dict() if composizione else None}


# ---- la fattura aperta del simulatore ------------------------------------------------------------------------------


def _simulatore() -> PagamentiSimulati:
    provider = provider_pagamenti()
    if not isinstance(provider, PagamentiSimulati):
        raise HTTPException(status_code=404, detail="Non disponibile")
    return provider


async def _della_fattura(session, fattura: str) -> Subscription:
    abbonamento = (await session.execute(
        select(Subscription).where(Subscription.fattura_aperta == fattura).limit(1)
    )).scalar_one_or_none()
    if abbonamento is None:
        raise HTTPException(status_code=404, detail="Fattura non trovata")
    return abbonamento


@router.get("/billing/mock/fattura/{fattura}", response_class=HTMLResponse)
async def fattura_simulata(fattura: str, session: DbSession) -> HTMLResponse:
    """La pagina della fattura aperta, come quella ospitata di Stripe. Esiste solo col simulatore."""
    from .billing import _PAGINA

    _simulatore()
    abbonamento = await _della_fattura(session, fattura)
    importo = gestione.prossimo_rinnovo(abbonamento) or abbonamento.listino or 0
    return HTMLResponse(_PAGINA.format(
        piano=html.escape(abbonamento.plan.name), importo=html.escape(f"{importo / 100:.2f} {abbonamento.plan.currency}"),
        periodo="fattura aperta del rinnovo", azione=f"/billing/mock/fattura/{html.escape(fattura)}/esito",
        ritorno=html.escape(f"{get_settings().web_public_url.rstrip('/')}/profile#abbonamento", quote=True),
        stato=html.escape(abbonamento.status), disabilitato="",
    ))


@router.post("/billing/mock/fattura/{fattura}/esito")
async def fattura_simulata_esito(fattura: str, request: Request, session: DbSession) -> RedirectResponse:
    """«Paga» sulla fattura del simulatore: l'evento firmato che Stripe manderebbe (`invoice.paid`)."""
    simulatore = _simulatore()
    modulo = await request.form()
    ritorno = str(modulo.get("ritorno", "")) or get_settings().web_public_url
    abbonamento = await _della_fattura(session, fattura)
    if str(modulo.get("esito", "")) == "paga":
        corpo = simulatore.evento(RINNOVATO, {
            "subscription_id": abbonamento.external_id, "riferimento": fattura,
            "importo": gestione.prossimo_rinnovo(abbonamento) or abbonamento.listino or 0,
        })
        evento = simulatore.verifica(corpo, {"X-Mock-Signature": simulatore.firma(corpo)})
        await GestorePagamenti(session, simulatore).applica(evento)
        await session.commit()
    return RedirectResponse(ritorno, status_code=status.HTTP_303_SEE_OTHER)
