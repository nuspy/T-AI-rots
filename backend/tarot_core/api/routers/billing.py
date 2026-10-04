"""Piani, pacchetti, abbonamenti, crediti. Da Personalities, con i pacchetti.

**Due «no» diversi, e vanno detti in modo diverso.** Un utente a cui viene
negata una lettura deve sapere se gli manca la *moneta* (servono crediti) o
se il servizio è rotto. Un unico errore li confonderebbe, e chi lo riceve non saprebbe cosa fare — che è il modo
in cui un limite commerciale diventa un guasto percepito.

| | codice | come si risolve |
|---|---|---|
| il saldo non basta e la quota è finita | 402 | si comprano crediti, o si aspetta il giorno dopo |
| il provider non risponde | 503 | non dipende dall'utente |

**Il saldo non si scrive da qui.** Nessun endpoint accredita su richiesta
dell'utente: i crediti entrano col rinnovo del piano o con un acquisto
registrato dal provider, e una rettifica manuale è un'operazione
amministrativa con il suo motivo obbligatorio e il suo record di audit.
L'unica eccezione è il **codice regalo** (`/me/coupon/riscatta`): il credito lo dà un codice che
l'amministrazione ha creato, a uso limitato, con le sue regole (`billing/offerte.py`).
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import html
import uuid
from urllib.parse import urlsplit

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel, Field

from ...analytics import eventi as analytics
from ...auth.dependencies import CurrentUser, DbSession, OptionalUser, require_role
from ...billing import abbonamenti as gestione_abbonamenti
from ...billing import offerte
from ...billing.credits import RegistroCrediti
from ...billing.lingue import in_lingua
from ...billing.pagamenti import (
    ANNULLATO, PAGATO, FirmaNonValida, GestorePagamenti, PagamentiNonDisponibili,
    PagamentiSimulati, provider_pagamenti,
)
from ...billing.plans import GestoreAbbonamenti
from ...billing.quote import ContatoreQuote
from ...domain.billing_models import PaymentCheckout
from ...domain.models import User
from ...settings import get_settings
from ...domain.repositories import AuditRepository

logger = logging.getLogger(__name__)

router = APIRouter(tags=["abbonamenti"])

#: Le rotte amministrative stanno su un router a parte perché il ruolo si
#: dichiara una volta sola: ripeterlo endpoint per endpoint significa
#: dimenticarlo su quello aggiunto di fretta.
router_admin = APIRouter(
    prefix="/admin",
    tags=["abbonamenti"],
    dependencies=[Depends(require_role("admin"))],
)


class Sottoscrizione(BaseModel):
    piano: str = Field(min_length=1, max_length=40)
    annuale: bool = False
    #: Dove tornare dopo il pagamento: la lettura interrotta per mancanza di
    #: crediti, per esempio. Solo percorsi del frontend o il deep link
    #: dell'app (schemi in `ritorno_schemi_app`), mai indirizzi esterni — un
    #: ritorno arbitrario sarebbe un open redirect.
    ritorno: Optional[str] = Field(default=None, max_length=300)
    #: Un codice sconto. Lo sconto vale sul primo pagamento.
    coupon: Optional[str] = Field(default=None, max_length=60)
    #: Il rinnovo automatico (v9, Fase 2b): acceso per default, con lo sconto del rinnovo sul prezzo; spento, si paga
    #: il listino e il periodo non si rinnova. Per un pacchetto non conta.
    rinnovo: bool = True


class AnteprimaCoupon(BaseModel):
    codice: str = Field(min_length=1, max_length=60)
    piano: str = Field(min_length=1, max_length=40)
    annuale: bool = False
    #: Fase 2d: il rinnovo automatico scelto (il suo sconto si somma al coupon o compete con lui) e la prova.
    rinnovo: bool = True
    prova: bool = False


class RiscattoCodice(BaseModel):
    codice: str = Field(min_length=1, max_length=60)


class Rettifica(BaseModel):
    delta: int = Field(description="positivo accredita, negativo toglie")
    #: Obbligatorio: una rettifica senza motivo è indistinguibile da un
    #: errore, e sei mesi dopo nessuno sa più perché quel saldo è cambiato.
    motivo: str = Field(min_length=3, max_length=500)


class StornoManuale(BaseModel):
    #: Obbligatorio come per la rettifica: chi legge il registro deve sapere perché quei crediti sono stati tolti.
    motivo: str = Field(min_length=3, max_length=500)


def deep_link_ammesso(indirizzo: str) -> bool:
    """Un deep link dell'app con uno schema dell'elenco chiuso (`ritorno_schemi_app`), senza spazi né controlli."""
    if not indirizzo or any(c.isspace() or ord(c) < 32 for c in indirizzo) or "\\" in indirizzo:
        return False
    schema = urlsplit(indirizzo).scheme.lower()
    return bool(schema) and schema in {s.lower() for s in get_settings().ritorno_schemi_app}


def _ritorno_valido(ritorno: str, base: str) -> str:
    """Il ritorno di un checkout: un percorso del sito (diventa assoluto) o il deep link dell'app; altro no."""
    if ritorno.startswith("/") and not ritorno.startswith("//"):
        return f"{base}{ritorno}"
    if deep_link_ammesso(ritorno):
        return ritorno
    raise HTTPException(status_code=400, detail="Ritorno non valido")


def _piano_json(p, lang: Optional[str] = None, impostazioni=None) -> Dict[str, Any]:
    dati = {
        "slug": p.slug,
        "nome": in_lingua(p.nomi, lang, p.name),
        "tipo": p.tipo,
        "descrizione": in_lingua(p.descrizioni, lang, p.description),
        "valuta": p.currency,
        "prezzo_mensile": p.price_monthly,
        "prezzo_annuale": p.price_yearly,
        "crediti_per_periodo": p.credits_per_period,
        "limiti": p.limits or {},
        "diritti": p.entitlements or {},
        #: Il livello (l'ordine del catalogo): decide se un cambio di piano è un upgrade o un downgrade.
        "livello": p.rank,
    }
    if impostazioni is not None and not p.pacchetto:
        # Fase 2b: il prezzo con e senza rinnovo automatico, e l'annuale della prova.
        dati["prezzi"] = gestione_abbonamenti.prezzi_piano(p, impostazioni)
    return dati


def _abbonamento_json(a, lang: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """L'abbonamento come lo vede il conto (v9, Fase 2b: con rinnovo automatico, prossimo addebito, tolleranza)."""
    return gestione_abbonamenti.abbonamento_json(a, lang)


@router.get("/plans")
async def piani(
    session: DbSession, lang: Optional[str] = Query(default=None, pattern="^[a-z]{2}$"),
) -> List[Dict[str, Any]]:
    """Il catalogo. Pubblico: si guarda prima di avere un account. `lang`: nomi e descrizioni in quella lingua
    (poi l'inglese, poi l'originale); senza, l'originale."""
    riga = await gestione_abbonamenti.impostazioni(session)
    piani = [_piano_json(p, lang, riga) for p in await GestoreAbbonamenti(session).piani()]
    await session.commit()
    return piani


@router.get("/me/billing")
async def il_mio_conto(
    user: CurrentUser, session: DbSession, lang: Optional[str] = Query(default=None, pattern="^[a-z]{2}$"),
) -> Dict[str, Any]:
    """Piano, diritti e saldo in una chiamata.

    Insieme e non in tre endpoint perché è una schermata sola: chiederli
    separatamente significa mostrarne uno prima degli altri, e un saldo che
    compare prima del piano a cui appartiene si legge male.
    """
    gestore = GestoreAbbonamenti(session)
    abbonamento = await gestore.abbonamento_di(user.id)
    diritti = await gestore.diritti_di(user.id)
    idonea, motivo = await gestione_abbonamenti.idoneita_prova(session, user.id, abbonamento)

    return {
        "abbonamento": _abbonamento_json(abbonamento, lang),
        "diritti": diritti.to_dict(),
        "saldo": await RegistroCrediti(session).saldo(user.id),
        # Quanto dei limiti è usato: mostrarlo prima evita che il limite si
        # scopra come un rifiuto. `limite` nullo significa illimitato, e senza
        # catalogo attivo l'installazione non limita affatto. Fase 2b: tutti i limiti del piano (giorno, settimana,
        # mese, totali del periodo pagato).
        "uso": (await ContatoreQuote(session).uso(
            user.id, diritti,
            periodo_inizio=abbonamento.period_start if abbonamento else None,
            periodo_fine=abbonamento.period_end if abbonamento else None,
        )).to_dict(diritti),
        "limiti_attivi": await gestore.tariffe_in_vigore(),
        # Letture comprese: un abbonamento a pagamento con limiti (oltre un limite, condono o consenso a un credito).
        "letture_comprese": gestione_abbonamenti.ha_letture_comprese(abbonamento, diritti),
        # Il banner della prova lo legge da qui: idonea = mai avuta e nessun abbonamento a pagamento.
        "prova": {"idonea": idonea, "motivo": motivo},
    }


@router.get("/me/credits")
async def i_miei_crediti(
    user: CurrentUser, session: DbSession, limite: int = 50,
) -> Dict[str, Any]:
    """Saldo e movimenti.

    I movimenti e non il solo saldo: il registro è append-only proprio perché
    chi vede sparire dei crediti possa vedere anche *quando* e *per cosa*. Un
    numero da solo non si può contestare.
    """
    registro = RegistroCrediti(session)
    return {
        "saldo": await registro.saldo(user.id),
        "movimenti": [
            m.to_dict() for m in await registro.movimenti(user.id, limite=limite)
        ],
    }


@router.post("/me/subscription", status_code=status.HTTP_201_CREATED)
async def sottoscrivi(
    payload: Sottoscrizione, user: CurrentUser, session: DbSession,
    risposta: Response,
) -> Dict[str, Any]:
    """Apre un abbonamento gratuito, chiudendo il precedente.

    Da un piano pagato al gratuito **non si passa subito**: il periodo è già
    stato pagato, e toglierlo adesso sarebbe prendere senza dare. Il piano
    pagato viene disdetto a fine periodo (202), e il gratuito lo apre la
    manutenzione quando quello scade — è lo stesso percorso di una disdetta.
    """
    gestore = GestoreAbbonamenti(session)
    piano = await gestore.piano_per_slug(payload.piano)
    if piano is None or not piano.active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Il piano «{payload.piano}» non esiste o non è più offerto.",
        )

    if piano.pacchetto:
        raise HTTPException(
            status_code=400,
            detail=f"«{piano.name}» è un pacchetto di crediti: si compra (POST /me/checkout).",
        )

    prezzo = piano.price_yearly if payload.annuale else piano.price_monthly
    attuale = await gestore.abbonamento_di(user.id)
    if (
        prezzo <= 0
        and attuale is not None
        and attuale.plan_id != piano.id
        and (attuale.plan.price_monthly > 0 or attuale.plan.price_yearly > 0)
    ):
        if attuale.cancel_at is None:
            await gestore.disdici(attuale)
        await session.commit()
        await session.refresh(attuale, ["plan"])
        risposta.status_code = status.HTTP_202_ACCEPTED
        return {
            "abbonamento": _abbonamento_json(attuale),
            "saldo": await RegistroCrediti(session).saldo(user.id),
            "passaggio": {
                "piano": piano.slug,
                "dal": attuale.period_end.isoformat(),
            },
        }

    if prezzo > 0:
        # Il varco che c'era: questo endpoint attivava qualunque piano, anche
        # il più caro, senza passare da nessun pagamento. Un piano che costa
        # qualcosa nasce solo dall'evento firmato del fornitore.
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=(
                f"Il piano «{piano.slug}» è a pagamento: si attiva passando dal "
                f"pagamento (POST /me/checkout)."
            ),
        )

    abbonamento = await gestore.sottoscrivi(
        user.id, piano, annuale=payload.annuale,
    )
    await session.commit()
    await session.refresh(abbonamento, ["plan"])

    return {
        "abbonamento": _abbonamento_json(abbonamento),
        "saldo": await RegistroCrediti(session).saldo(user.id),
    }


@router.post("/me/checkout", status_code=status.HTTP_201_CREATED)
async def apri_checkout(
    payload: Sottoscrizione, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    """Apre una sessione di pagamento e dice dove andare a pagare.

    L'abbonamento non nasce qui: nasce quando il fornitore conferma il
    pagamento. Chi apre la pagina e poi la chiude non ha comprato niente.
    """
    gestore = GestoreAbbonamenti(session)
    piano = await gestore.piano_per_slug(payload.piano)
    if piano is None or not piano.active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Il piano «{payload.piano}» non esiste o non è più offerto.",
        )
    annuale = payload.annuale and not piano.pacchetto
    if (piano.price_yearly if annuale else piano.price_monthly) <= 0:
        raise HTTPException(
            status_code=400,
            detail=f"Il piano «{piano.slug}» è gratuito: non serve pagare.",
        )
    sconto_rinnovo = 0
    if not piano.pacchetto:
        # Fase 2b. Mai un secondo addebito: con una fattura aperta si paga quella; con un abbonamento a pagamento già
        # attivo si cambia piano (col conguaglio), non se ne apre un secondo.
        try:
            await gestione_abbonamenti.verifica_nessuna_fattura_aperta(session, user.id)
        except gestione_abbonamenti.ErroreAbbonamento as exc:
            raise HTTPException(status_code=409, detail={"motivo": exc.motivo, "messaggio": str(exc)}) from exc
        attuale = await gestore.abbonamento_di(user.id)
        if attuale is not None and not gestione_abbonamenti.gratuito(attuale.plan):
            raise HTTPException(status_code=409, detail={
                "motivo": "abbonamento_attivo",
                "messaggio": "Hai già un abbonamento: cambia piano dal profilo o dai prezzi, col conguaglio.",
            })
        if payload.rinnovo:
            riga = await gestione_abbonamenti.impostazioni(session)
            sconto_rinnovo = gestione_abbonamenti.percentuale(
                piano.price_yearly if annuale else piano.price_monthly, riga.sconto_rinnovo,
            )

    base = get_settings().web_public_url.rstrip('/')
    # Senza un ritorno esplicito si torna ai prezzi in inglese (la lingua canonica del sito); il frontend indica sempre
    # il proprio, nella lingua di chi ha pagato (`/pricing` o `/it/piano`). L'app indica il suo deep link.
    ritorno = f"{base}/pricing"
    if payload.ritorno:
        payload.ritorno = _ritorno_valido(payload.ritorno, base)
    sconto = None
    composizione = None
    if payload.coupon and payload.coupon.strip():
        chiavi = _chiavi_tentativi(request, user.id)
        _limita_tentativi(chiavi)
        try:
            valutato = await offerte.valuta(session, user.id, payload.coupon, piano, annuale=annuale)
            # Fase 2d: il coupon con lo sconto del rinnovo, sommati o il più alto dei due (`offerte.componi`).
            composizione = offerte.componi(
                valutato.listino, base=sconto_rinnovo, valutato=valutato, abbonamento=not piano.pacchetto,
                rinnovo=payload.rinnovo,
            )
        except offerte.CouponNonValido as exc:
            _conta_tentativo(chiavi, exc)
            raise _errore_coupon(exc) from exc
        sconto = composizione.sconto_per_pagamento()

    if sconto is not None and sconto.finale == 0:
        # Un pacchetto azzerato dal coupon: niente da pagare, quindi nessun fornitore. I crediti sono già dati.
        checkout = await GestorePagamenti(session).apri_gratis(user.id, piano, sconto)
        await analytics.evento(
            session, analytics.ACQUISTO, utente_id=user.id, valore_centesimi=0, valuta=checkout.currency,
            proprieta={"tipo": "crediti", "piano": piano.slug, "annuale": False, "coupon": True},
        )
        await session.commit()
        torna = payload.ritorno or ritorno
        return {
            "checkout_id": str(checkout.id), "url": f"{torna}{'&' if '?' in torna else '?'}checkout={checkout.id}",
            "importo": 0, "sconto": checkout.sconto, "valuta": checkout.currency, "gratis": True,
        }

    try:
        # Un savepoint e non un rollback: si annulla solo la sessione di
        # pagamento creata prima di chiedere l'indirizzo, non il resto della
        # transazione.
        async with session.begin_nested():
            checkout, url = await GestorePagamenti(session).apri(
                user.id, piano, annuale=annuale, ritorno=payload.ritorno or ritorno, sconto=sconto,
                rinnovo=payload.rinnovo and not piano.pacchetto, sconto_rinnovo=sconto_rinnovo,
                sconto_ricorrente=composizione.sconto_ricorrente if composizione and composizione.applicato else None,
            )
    except PagamentiNonDisponibili as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc),
        ) from exc
    await analytics.evento(
        session, analytics.CHECKOUT_AVVIATO, utente_id=user.id, valore_centesimi=checkout.importo,
        valuta=checkout.currency,
        proprieta={"tipo": "crediti" if piano.pacchetto else "abbonamento", "piano": piano.slug, "annuale": annuale,
                   "coupon": sconto is not None},
    )
    await session.commit()
    return {
        "checkout_id": str(checkout.id), "url": url, "importo": checkout.importo, "sconto": checkout.sconto,
        "valuta": checkout.currency, "gratis": False, "listino": checkout.listino,
        "sconto_rinnovo": checkout.sconto_rinnovo, "rinnovo": checkout.rinnovo,
        # Fase 2d: il codice valeva ma un altro sconto era più alto (non cumulabile): non si è consumato.
        "coupon": composizione.to_dict() if composizione else None,
    }


# ---- codici sconto e codici regalo --------------------------------------------------------------
#
# Un codice si prova a mano: chi ne indovina uno sconta un acquisto o riscuote crediti. Dieci codici inesistenti in
# un'ora — per persona **o** per indirizzo IP, così né cambiare account né restare anonimi aggira il limite — fermano chi
# prova a caso (429 `troppi_tentativi`, che il sito traduce). Il conto sta in memoria del processo: con più repliche il
# limite si moltiplica, ma un codice di otto caratteri su 32 simboli ha 10^12 combinazioni, e a quel ritmo non si
# indovina. Maiuscole e spazi non contano (`offerte.normalizza_codice`).

_TENTATIVI: Dict[str, List[float]] = {}
FINESTRA_TENTATIVI = 3600.0
MAX_FALLITI = 10
TROPPI_TENTATIVI = "Troppi codici sbagliati: riprova fra un'ora."


def _chiavi_tentativi(request: Request, user_id: Optional[int]) -> List[str]:
    from lanterna.rete import ip_client

    chiavi = [f"u:{user_id}"] if user_id is not None else []
    ip = ip_client(request)
    if ip:
        chiavi.append(f"ip:{ip}")
    return chiavi


def _limita_tentativi(chiavi: List[str]) -> None:
    import time

    ora = time.monotonic()
    if len(_TENTATIVI) > 10_000:
        # Gli indirizzi passati senza tentativi recenti non servono più: la memoria non cresce senza fine.
        for chiave in [k for k, v in _TENTATIVI.items() if not v or ora - v[-1] >= FINESTRA_TENTATIVI]:
            _TENTATIVI.pop(chiave, None)
    for chiave in chiavi:
        recenti = [t for t in _TENTATIVI.get(chiave, []) if ora - t < FINESTRA_TENTATIVI]
        _TENTATIVI[chiave] = recenti
        if len(recenti) >= MAX_FALLITI:
            attesa = int(FINESTRA_TENTATIVI - (ora - recenti[0])) + 1
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS, headers={"Retry-After": str(attesa)},
                detail={"motivo": "troppi_tentativi", "messaggio": TROPPI_TENTATIVI, "riprova_fra": attesa},
            )


def _conta_tentativo(chiavi: List[str], exc: "offerte.CouponNonValido") -> None:
    """Conta solo i codici che **non esistono**: sono i tentativi a caso. Un codice che esiste ma non vale (scaduto, non
    per questa offerta…) non è un tentativo, e una pagina che lo prova su ogni offerta non deve bloccare chi lo ha."""
    import time

    if exc.motivo == "coupon_sconosciuto":
        for chiave in chiavi:
            _TENTATIVI.setdefault(chiave, []).append(time.monotonic())


def _errore_coupon(exc: "offerte.CouponNonValido") -> HTTPException:
    return HTTPException(status_code=422, detail={"motivo": exc.motivo, "messaggio": str(exc)})


@router.post("/me/coupon/anteprima")
async def anteprima_coupon(
    payload: AnteprimaCoupon, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    """Quanto costerebbe un'offerta con questo codice, senza aprire nessun pagamento. Fase 2d: con il rinnovo
    automatico scelto (o la prova) e il cumulo, come lo farà il pagamento."""
    piano = await GestoreAbbonamenti(session).piano_per_slug(payload.piano)
    if piano is None or not piano.active:
        raise HTTPException(status_code=404, detail=f"Il piano «{payload.piano}» non esiste o non è più offerto.")
    chiavi = _chiavi_tentativi(request, user.id)
    _limita_tentativi(chiavi)
    annuale = (payload.annuale or payload.prova) and not piano.pacchetto
    try:
        s = await offerte.valuta(session, user.id, payload.codice, piano, annuale=annuale)
        base = 0
        if not piano.pacchetto and (payload.rinnovo or payload.prova):
            riga = await gestione_abbonamenti.impostazioni(session)
            base = gestione_abbonamenti.percentuale(
                s.listino, riga.sconto_prova if payload.prova else riga.sconto_rinnovo,
            )
        composizione = offerte.componi(
            s.listino, base=base, valutato=s, abbonamento=not piano.pacchetto, rinnovo=payload.rinnovo,
            prova=payload.prova and not piano.pacchetto,
        )
    except offerte.CouponNonValido as exc:
        _conta_tentativo(chiavi, exc)
        raise _errore_coupon(exc) from exc
    await session.commit()
    return {
        "codice": s.coupon.code, "tipo": s.coupon.tipo, "listino": s.listino,
        # `sconto` e `importo` sono quelli del pagamento intero (rinnovo automatico e coupon secondo il cumulo).
        "sconto": composizione.sconto, "importo": composizione.importo, "valuta": piano.currency,
        "gratis": composizione.importo == 0 and not composizione.prova,
        "coupon": offerte.coupon_pubblico(s.coupon), **composizione.to_dict(),
    }


class AnteprimaPubblica(BaseModel):
    codice: str = Field(min_length=1, max_length=60)


@router.post("/coupon/anteprima")
async def anteprima_pubblica(
    payload: AnteprimaPubblica, request: Request, user: OptionalUser, session: DbSession,
) -> Dict[str, Any]:
    """Il codice di un link (`/pricing?coupon=CODICE`) su tutte le offerte, anche senza account (Fase 2d): chi
    arriva da una newsletter vede subito il prezzo barrato e quanto risparmia. Senza accesso non si controllano le
    regole della persona (già usato, solo primo acquisto): le ricontrolla il pagamento. Limite dei tentativi per IP."""
    chiavi = _chiavi_tentativi(request, user.id if user else None)
    _limita_tentativi(chiavi)
    try:
        coupon = await offerte.verifica_sconto(session, user.id if user else None, payload.codice)
    except offerte.CouponNonValido as exc:
        _conta_tentativo(chiavi, exc)
        raise _errore_coupon(exc) from exc
    riga = await gestione_abbonamenti.impostazioni(session)
    piani = await GestoreAbbonamenti(session).piani()
    from ...billing.pagamenti import PagamentiDisattivati

    risposta = {
        "coupon": offerte.coupon_pubblico(coupon),
        "offerte": offerte.preventivi(
            coupon, list(piani), percento_rinnovo=riga.sconto_rinnovo, percento_prova=riga.sconto_prova,
            con_prova=not isinstance(provider_pagamenti(), PagamentiDisattivati),
        ),
    }
    await session.commit()
    return risposta


@router.post("/me/coupon/riscatta")
async def riscatta_codice(
    payload: RiscattoCodice, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    """Riscatta un codice regalo: i crediti arrivano subito."""
    chiavi = _chiavi_tentativi(request, user.id)
    _limita_tentativi(chiavi)
    try:
        coupon, crediti = await offerte.riscatta_regalo(session, user.id, payload.codice)
    except offerte.CouponNonValido as exc:
        # Niente da annullare: le regole si controllano prima di scrivere (e la riga bloccata si libera a fine richiesta).
        _conta_tentativo(chiavi, exc)
        raise _errore_coupon(exc) from exc
    await AuditRepository(session).record(
        actor_id=user.id, action="coupon.redeem", target_type="coupon", target_id=coupon.code, after={"crediti": crediti},
    )
    await analytics.evento(session, analytics.COUPON_RISCATTATO, utente_id=user.id, proprieta={"crediti": crediti})
    await session.commit()
    return {"crediti": crediti, "saldo": await RegistroCrediti(session).saldo(user.id)}


@router.get("/me/checkout/{checkout_id}")
async def stato_checkout(
    checkout_id: uuid.UUID, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    """Com'è andata: la pagina di ritorno lo chiede invece di fidarsi dell'URL.

    L'indirizzo di ritorno lo può scrivere chiunque; lo stato della sessione
    no — è cambiato solo dall'evento firmato del fornitore.
    """
    checkout = await session.get(PaymentCheckout, checkout_id)
    if checkout is None or checkout.user_id != user.id:
        raise HTTPException(status_code=404, detail="Pagamento non trovato")
    return {
        "checkout_id": str(checkout.id),
        "stato": checkout.status,
        "piano": checkout.plan.slug,
        "nome": checkout.plan.name,
        "tipo": checkout.plan.tipo,
        # Fase 2b: una prova, un cambio di piano, e perché un pagamento non ha prodotto ciò che chiedeva
        # (`prova_gia_usata`, `carta_gia_usata`).
        "prova": checkout.prova,
        "cambio": checkout.sostituisce_id is not None,
        "esito": checkout.esito,
    }


@router.post("/billing/webhook")
async def webhook(request: Request, session: DbSession) -> Dict[str, Any]:
    """Gli eventi del fornitore di pagamento: piani (`checkout.*`) e ordini del negozio mazzi
    (`ordine.*`, v5 Fase B3) — smistati sul tipo, condividono lo stesso `payment_events` per
    l'idempotenza (è indicizzato per id-evento del fornitore, non per ciò che paga).

    Senza autenticazione dell'utente — chi chiama è il fornitore — e per
    questo con la firma verificata prima di leggere qualunque cosa. Risponde
    200 anche a un evento già applicato: il fornitore rimanda finché non lo
    riceve, e un errore qui lo farebbe rimandare per sempre.
    """
    from ...billing.ordini import GestoreOrdini

    corpo = await request.body()
    gestore = GestorePagamenti(session)
    try:
        evento = gestore.provider.verifica(corpo, request.headers)
    except FirmaNonValida as exc:
        logger.warning("Evento di pagamento rifiutato: %s", exc)
        raise HTTPException(status_code=400, detail=f"evento non valido: {exc}") from exc

    if evento.tipo.startswith("ordine."):
        esito = await GestoreOrdini(session, gestore.provider).applica(evento)
    else:
        esito = await gestore.applica(evento)
    await session.commit()
    logger.info("Evento %s (%s): %s", evento.id, evento.tipo, esito)
    return {"ricevuto": evento.id, "esito": esito}


@router.get("/billing/ritorno-app")
async def ritorno_app(verso: str = Query(max_length=300)) -> RedirectResponse:
    """Il rimbalzo verso l'app dopo il pagamento (v9): Stripe torna solo a indirizzi web, l'app vuole il suo deep link.

    Si riconvalida lo schema contro l'elenco chiuso: chi costruisse a mano questo indirizzo non deve poterlo usare
    per mandare altrove.
    """
    if not deep_link_ammesso(verso):
        raise HTTPException(status_code=400, detail="Ritorno non valido")
    return RedirectResponse(verso, status_code=status.HTTP_303_SEE_OTHER)


# ---- la pagina di pagamento del simulatore ---------------------------------


def _simulatore() -> PagamentiSimulati:
    provider = provider_pagamenti()
    if not isinstance(provider, PagamentiSimulati):
        raise HTTPException(status_code=404, detail="Non disponibile")
    return provider


@router.get("/billing/mock/checkout/{checkout_id}", response_class=HTMLResponse)
async def pagina_simulata(
    checkout_id: uuid.UUID, session: DbSession, ritorno: str = "",
) -> HTMLResponse:
    """La pagina che un fornitore vero ospiterebbe. Esiste solo col simulatore."""
    _simulatore()
    checkout = await session.get(PaymentCheckout, checkout_id)
    if checkout is None:
        raise HTTPException(status_code=404, detail="Pagamento non trovato")

    importo = f"{checkout.importo / 100:.2f} {checkout.currency}"
    periodo = (
        f"{checkout.plan.credits_per_period} letture, una tantum" if checkout.plan.pacchetto
        else "un anno" if checkout.annuale else "un mese"
    )
    chiuso = checkout.status != "aperto"
    return HTMLResponse(_PAGINA.format(
        piano=html.escape(checkout.plan.name),
        importo=html.escape(importo),
        periodo=periodo,
        azione=f"/billing/mock/checkout/{checkout.id}/esito",
        ritorno=html.escape(ritorno, quote=True),
        stato=html.escape(checkout.status),
        disabilitato="disabled" if chiuso else "",
    ))


@router.post("/billing/mock/checkout/{checkout_id}/esito")
async def esito_simulato(
    checkout_id: uuid.UUID, request: Request, session: DbSession,
) -> RedirectResponse:
    """Il clic su «Paga» o «Annulla».

    Non attiva niente da sé: costruisce l'evento che il fornitore
    manderebbe, lo firma e lo fa passare dalla stessa verifica e dallo stesso
    gestore di un evento vero. È questo che rende il simulatore una prova del
    percorso di produzione invece di una scorciatoia.
    """
    simulatore = _simulatore()
    modulo = await request.form()
    scelta = str(modulo.get("esito", ""))
    ritorno = str(modulo.get("ritorno", "")) or get_settings().web_public_url

    checkout = await session.get(PaymentCheckout, checkout_id)
    if checkout is None:
        raise HTTPException(status_code=404, detail="Pagamento non trovato")

    tipo = PAGATO if scelta == "paga" else ANNULLATO
    corpo = simulatore.evento(tipo, {
        "checkout_id": str(checkout.id),
        "subscription_id": f"mock_sub_{checkout.id.hex[:16]}",
        "importo": checkout.importo,
    })
    gestore = GestorePagamenti(session, simulatore)
    evento = simulatore.verifica(corpo, {"X-Mock-Signature": simulatore.firma(corpo)})
    await gestore.applica(evento)
    await session.commit()

    separatore = "&" if "?" in ritorno else "?"
    return RedirectResponse(
        f"{ritorno}{separatore}checkout={checkout.id}", status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/billing/mock/ordine/{ordine_id}", response_class=HTMLResponse)
async def pagina_simulata_ordine(ordine_id: uuid.UUID, session: DbSession, ritorno: str = "") -> HTMLResponse:
    """La pagina simulata di pagamento per un ordine del negozio mazzi (v5, Fase B3) — sorella di
    `pagina_simulata`, per un `Ordine` invece che un `PaymentCheckout`."""
    from ...domain.ordini_models import Ordine

    _simulatore()
    ordine = await session.get(Ordine, ordine_id)
    if ordine is None:
        raise HTTPException(status_code=404, detail="Ordine non trovato")

    importo = f"{ordine.importo_totale / 100:.2f} {ordine.valuta}"
    n_righe = sum(r.quantita for r in ordine.righe)
    periodo = f"{n_righe} {'mazzo' if n_righe == 1 else 'mazzi'}, una tantum"
    chiuso = ordine.status != "aperto"
    return HTMLResponse(_PAGINA.format(
        piano="Il tuo ordine",
        importo=html.escape(importo),
        periodo=periodo,
        azione=f"/billing/mock/ordine/{ordine.id}/esito",
        ritorno=html.escape(ritorno, quote=True),
        stato=html.escape(ordine.status),
        disabilitato="disabled" if chiuso else "",
    ))


@router.post("/billing/mock/ordine/{ordine_id}/esito")
async def esito_simulato_ordine(ordine_id: uuid.UUID, request: Request, session: DbSession) -> RedirectResponse:
    """Il clic su «Paga» o «Annulla» per un ordine — sorella di `esito_simulato`."""
    from ...billing.ordini import ORDINE_ANNULLATO, ORDINE_PAGATO, GestoreOrdini
    from ...domain.ordini_models import Ordine

    simulatore = _simulatore()
    modulo = await request.form()
    scelta = str(modulo.get("esito", ""))
    ritorno = str(modulo.get("ritorno", "")) or get_settings().web_public_url

    ordine = await session.get(Ordine, ordine_id)
    if ordine is None:
        raise HTTPException(status_code=404, detail="Ordine non trovato")

    tipo = ORDINE_PAGATO if scelta == "paga" else ORDINE_ANNULLATO
    corpo = simulatore.evento(tipo, {"ordine_id": str(ordine.id), "importo": ordine.importo_totale})
    gestore = GestoreOrdini(session, simulatore)
    evento = simulatore.verifica(corpo, {"X-Mock-Signature": simulatore.firma(corpo)})
    await gestore.applica(evento)
    await session.commit()

    separatore = "&" if "?" in ritorno else "?"
    return RedirectResponse(f"{ritorno}{separatore}ordine={ordine.id}", status_code=status.HTTP_303_SEE_OTHER)


_PAGINA = """<!doctype html>
<html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pagamento simulato</title>
<style>
  body {{ font: 16px/1.5 system-ui, sans-serif; background: #0d0a1a; color: #efe6d2;
         margin: 0; min-height: 100vh; display: grid; place-items: center; padding: 16px; }}
  main {{ background: #1a1430; border-top: 4px solid #c9a24a; max-width: 420px; width: 100%;
          padding: 28px; box-sizing: border-box; }}
  .avviso {{ font-size: 13px; color: #f3d9a4; background: #2a2045; padding: 8px 10px; margin: 0 0 20px; }}
  h1 {{ font: 400 28px Georgia, serif; margin: 0 0 4px; }}
  .importo {{ font: 400 36px Georgia, serif; margin: 16px 0 24px; }}
  form {{ display: flex; gap: 10px; flex-wrap: wrap; }}
  button {{ min-height: 48px; padding: 0 18px; font-size: 15px; border: 1px solid #c9a24a;
            background: #c9a24a; color: #0d0a1a; cursor: pointer; flex: 1; }}
  button.annulla {{ background: transparent; color: #cfc3e8; border-color: #4b3f70; }}
  button:disabled {{ opacity: .45; cursor: not-allowed; }}
  button:focus-visible {{ outline: 3px solid #c4624d; outline-offset: 2px; }}
</style></head>
<body><main>
  <p class="avviso">Pagamento simulato: nessuna carta viene addebitata. In produzione questa
  pagina è ospitata dal fornitore di pagamento.</p>
  <h1>{piano}</h1>
  <div>{periodo}</div>
  <div class="importo">{importo}</div>
  <form method="post" action="{azione}">
    <input type="hidden" name="ritorno" value="{ritorno}">
    <button name="esito" value="paga" {disabilitato}>Paga</button>
    <button name="esito" value="annulla" class="annulla" {disabilitato}>Annulla</button>
  </form>
  <p style="font-size:13px;color:#a99cc9;margin-top:16px">Stato: {stato}</p>
</main></body></html>"""



@router.post("/me/subscription/cancel")
async def disdici(user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    """Disdice: l'abbonamento resta attivo fino a scadenza.

    Già pagato. Chiuderlo subito toglierebbe qualcosa a cui l'utente ha
    diritto, e la differenza fra «ho disdetto» e «non ho più accesso» è
    esattamente ciò che rende accettabile disdire.
    """
    gestore = GestoreAbbonamenti(session)
    abbonamento = await gestore.abbonamento_di(user.id)
    if abbonamento is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Non hai un abbonamento attivo.",
        )

    try:
        if not gestione_abbonamenti.gratuito(abbonamento.plan):
            # Fase 2b: è lo spegnimento del rinnovo automatico, con la sua email di conferma formale.
            await gestione_abbonamenti.imposta_rinnovo(
                session, abbonamento, False, configurato=gestore._provider, utente=user,
            )
        else:
            await gestore.disdici(abbonamento)
    except gestione_abbonamenti.ErroreAbbonamento as exc:
        raise HTTPException(status_code=409, detail={"motivo": exc.motivo, "messaggio": str(exc), **exc.dati}) from exc
    except PagamentiNonDisponibili as exc:
        # Il fornitore non ha confermato la disdetta: meglio dirlo che segnarla qui e lasciarlo addebitare.
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    await session.commit()
    await session.refresh(abbonamento, ["plan"])
    return {"abbonamento": _abbonamento_json(abbonamento)}


@router_admin.get("/users/{user_id}/credits")
async def crediti_di(
    user_id: int, session: DbSession, limite: int = 100,
) -> Dict[str, Any]:
    registro = RegistroCrediti(session)
    if await session.get(User, user_id) is None:
        raise HTTPException(status_code=404, detail="Utente non trovato")

    return {
        "saldo": await registro.saldo(user_id),
        "movimenti": [
            m.to_dict() for m in await registro.movimenti(user_id, limite=limite)
        ],
    }


@router_admin.post("/users/{user_id}/credits")
async def rettifica(
    user_id: int,
    payload: Rettifica,
    user: CurrentUser,
    session: DbSession,
) -> Dict[str, Any]:
    """Corregge un saldo, lasciando scritto perché.

    Una riga in più e non una modifica di quelle esistenti: entrambe restano,
    e la storia resta leggibile. Un saldo aggiustato cancellando ciò che non
    tornava è un saldo giusto che non sa spiegarsi.
    """
    if await session.get(User, user_id) is None:
        raise HTTPException(status_code=404, detail="Utente non trovato")

    registro = RegistroCrediti(session)
    prima = await registro.saldo(user_id)
    try:
        await registro.rettifica(user_id, payload.delta, note=payload.motivo)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    dopo = await registro.saldo(user_id)
    await AuditRepository(session).record(
        actor_id=user.id,
        action="credits.adjust",
        target_type="user",
        target_id=str(user_id),
        before={"saldo": prima},
        after={"saldo": dopo, "delta": payload.delta, "motivo": payload.motivo},
    )
    await session.commit()

    return {"saldo": dopo, "delta": payload.delta}


@router_admin.post("/users/{user_id}/credits/{voce_id}/storno")
async def storna_a_mano(
    user_id: int, voce_id: int, payload: StornoManuale, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    """Registra lo storno di un incasso: un rimborso fatto a mano dalla dashboard del fornitore, una contestazione
    di cui il webhook non ha trovato i crediti, un incasso di prima del registro multicanale.

    **Non rimborsa il denaro**: quello si fa presso il fornitore. Qui si tolgono i crediti che quell'incasso aveva
    dato, con lo stesso riferimento — se poi arriva anche l'evento del fornitore, trova lo storno già fatto e non
    toglie due volte. Il saldo può andare sotto zero, come per uno storno automatico.
    """
    from ...domain.billing_models import CreditEntry

    voce = await session.get(CreditEntry, voce_id)
    if voce is None or voce.user_id != user_id:
        raise HTTPException(status_code=404, detail="Movimento non trovato")
    if voce.reason not in ("acquisto", "accredito_piano") or voce.delta <= 0:
        raise HTTPException(status_code=422, detail="Si storna solo un acquisto o un accredito di piano.")

    registro = RegistroCrediti(session)
    prima = await registro.saldo(user_id)
    riga, nuova = await registro.storna(
        user_id, voce.delta, provider=voce.provider,
        riferimento_esterno=voce.riferimento_esterno or f"voce:{voce.id}",
        canale="console", note=f"storno manuale: {payload.motivo}", expires_at=voce.expires_at,
    )
    if not nuova:
        raise HTTPException(status_code=409, detail="Questo incasso è già stato stornato.")
    dopo = await registro.saldo(user_id)
    await AuditRepository(session).record(
        actor_id=user.id, action="credits.reverse", target_type="user", target_id=str(user_id),
        before={"saldo": prima},
        after={
            "saldo": dopo, "voce": voce.id, "crediti": -riga.delta, "provider": voce.provider,
            "riferimento": riga.riferimento_esterno, "motivo": payload.motivo,
        },
    )
    await session.commit()
    return {"saldo": dopo, "delta": riga.delta}


@router_admin.get("/payments/config")
async def configurazione_pagamenti() -> Dict[str, Any]:
    """Il fornitore attivo e lo stato delle chiavi di Stripe, per la console. **Mai i valori**: solo se ci sono e,
    dalla forma della chiave, se è di prova o reale."""
    from ...billing.stripe import EVENTI

    from ...configurazioni.correnti import pagamenti as pagamenti_correnti

    impostazioni = get_settings()
    # v9 Fase 2c: i valori in uso (console, poi ambiente); il dettaglio sta in `/admin/configurazioni/stripe`.
    correnti = pagamenti_correnti(impostazioni)
    return {
        "provider": correnti.provider,
        "stripe": {
            "chiave_segreta": bool(correnti.chiave_segreta),
            "segreto_webhook": bool(correnti.segreto_webhook),
            "modalita": correnti.modalita,
        },
        # L'indirizzo pubblico dell'API: dietro il gateway è `https://tarots.chat/api/billing/webhook`.
        "webhook_url": f"{impostazioni.api_public_url.rstrip('/')}/billing/webhook",
        "eventi": list(EVENTI),
        "schemi_app": list(impostazioni.ritorno_schemi_app),
    }
