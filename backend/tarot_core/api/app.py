"""Applicazione FastAPI di TAROTS chat.

Lo scheletro — CORS, correlazione, tracce, verifica della configurazione di
produzione, gestore degli errori — viene da Personalities. Le rotte sono
quelle della lettura, della cassa e della console.
"""
from __future__ import annotations

import logging
import uuid
from contextlib import asynccontextmanager

import truststore
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ..observability.correlation import correlation_scope
from ..observability.tracing import (
    instrument_engine, setup_tracing, span_corrente_con_correlazione,
)
from ..settings import get_settings
from .routers import (
    admin, admin_analytics, admin_blog, admin_impostazioni, admin_llm, admin_mazzi, admin_offerte, admin_ordini, admin_seo, admin_voto,
    analytics, analytics_colab, billing, blog, chat, condivisione, profile, public, readings, rest_blog, shop, voto,
)

# Le chiamate ai fornitori LLM (e a qualunque altro servizio HTTPS esterno) verificano il certificato con
# l'archivio del sistema operativo, non solo con quello di `certifi`: su Windows, dietro un antivirus o un proxy
# aziendale che aggiunge le proprie radici, `certifi` da solo produce `CERTIFICATE_VERIFY_FAILED` per un servizio
# che è raggiungibile e valido (già capitato con il download del vocabolario di tiktoken, aggirato allora con
# `curl`; qui non si può, perché la chiamata è dentro il processo a ogni lettura). Non è un aggiramento della
# verifica: verifica ancora, solo contro un insieme di radici più completo — lo stesso che già usa `curl` su
# questa macchina. Va fatto prima che qualunque client HTTPS costruisca il suo contesto SSL: qui, all'importazione
# del modulo che crea l'applicazione, è il punto più presto disponibile.
truststore.inject_into_ssl()

logger = logging.getLogger(__name__)

#: Intestazione che lega fra loro tutte le tappe di una richiesta: intervista,
#: modello, guardrail. Senza un identificativo comune, i tempi dei singoli
#: stadi non si ricompongono.
CORRELATION_HEADER = "X-Correlation-ID"


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    problemi = settings.validate_production()
    for problem in problemi:
        logger.error("Configurazione non adatta alla produzione: %s", problem)
    if problemi and settings.environment == "prod":
        # In produzione non si parte: un'API con l'autenticazione spenta o il
        # pagamento simulato non è un servizio degradato, è una porta aperta —
        # e un errore nei log, a servizio avviato, lo legge qualcuno troppo
        # tardi.
        raise RuntimeError(
            "configurazione non adatta alla produzione: " + "; ".join(problemi)
        )

    logger.info(
        "Avvio di %s (ambiente=%s)", settings.service_name, settings.environment,
    )
    if settings.llm_finto:
        logger.warning(
            "Modello finto attivo (TAROT_LLM_FINTO): le letture non usano un "
            "modello vero. Accettabile solo in sviluppo e nei test."
        )
    # La base di conoscenza si valida all'avvio: un mazzo incompleto è un
    # errore di rilascio, e va visto prima della prima lettura.
    from .deps import get_conoscenza

    get_conoscenza()

    if settings.auth_disabled:
        logger.warning(
            "Autenticazione disattivata: ogni endpoint risponde senza credenziali. "
            "Accettabile solo in sviluppo."
        )

    # Il motore si costruisce qui e non alla prima richiesta: cosi' un errore
    # nella stringa di connessione si vede all'avvio. La strumentazione di
    # FastAPI invece e' gia' stata agganciata in `create_app()`, prima che
    # Starlette congelasse la catena dei middleware.
    try:
        from ..domain.session import get_engine

        instrument_engine(get_engine())
    except Exception as exc:
        logger.error("Motore di database non inizializzato: %s", exc)

    yield

    from ..domain.session import dispose_engine

    await dispose_engine()
    logger.info("Arresto di %s", settings.service_name)


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="TAROTS chat",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=[CORRELATION_HEADER],
    )

    @app.middleware("http")
    async def correlation_id(request: Request, call_next):
        """Assegna o propaga l'identificativo di correlazione.

        Se il chiamante ne porta uno lo si conserva — cosi' una richiesta
        iniziata nel frontend resta riconoscibile attraverso i servizi.
        """
        value = request.headers.get(CORRELATION_HEADER) or str(uuid.uuid4())
        request.state.correlation_id = value

        # Anche nella variabile di contesto: `request.state` e' raggiungibile
        # solo da chi ha l'oggetto richiesta sottomano, e gli strati in fondo
        # — repository, client dei modelli — non ce l'hanno.
        with correlation_scope(value):
            span_corrente_con_correlazione()
            response = await call_next(request)

        response.headers[CORRELATION_HEADER] = value
        return response

    @app.get("/healthz", tags=["ops"])
    def healthz() -> dict:
        """Il processo è vivo. Deliberatamente senza controlli sui supporti.

        Una sonda di liveness che verifica database e Redis fa riavviare un
        servizio sano quando è il database a essere lento, moltiplicando il
        guasto invece di contenerlo. La prontezza a ricevere traffico è
        un'altra domanda, e avrà il suo endpoint.
        """
        return {"status": "ok", "service": get_settings().service_name}

    app.include_router(public.router)
    app.include_router(readings.router)
    app.include_router(condivisione.router)
    app.include_router(blog.router)
    app.include_router(admin_blog.router)
    app.include_router(admin_offerte.router)
    app.include_router(admin_mazzi.router)
    app.include_router(admin_ordini.router)
    app.include_router(admin_llm.router)
    app.include_router(admin_impostazioni.router)
    app.include_router(rest_blog.router)
    app.include_router(profile.router)
    app.include_router(billing.router)
    app.include_router(billing.router_admin)
    app.include_router(shop.router)
    app.include_router(admin.router)
    app.include_router(chat.router)
    app.include_router(voto.router)
    app.include_router(admin_voto.router)
    app.include_router(admin_seo.router)
    app.include_router(analytics.router)
    app.include_router(admin_analytics.router)
    app.include_router(analytics_colab.router)

    # Qui e non nel lifespan: la strumentazione di FastAPI inserisce un
    # middleware ASGI, e Starlette costruisce la catena dei middleware alla
    # prima richiesta — agganciarla dopo significa non agganciarla affatto,
    # senza che nulla lo segnali. Il sintomo e' sottile: le tracce arrivano
    # lo stesso, ma contengono solo le chiamate in uscita e mai la richiesta
    # che le ha causate.
    setup_tracing(app)

    @app.exception_handler(Exception)
    async def unhandled(request: Request, exc: Exception):
        """Nessuna traccia di stack verso il chiamante, ma il riferimento sì.

        L'identificativo restituito è lo stesso che compare nei log: è ciò che
        permette di ritrovare l'errore senza chiedere all'utente di
        descriverlo.
        """
        correlation = getattr(request.state, "correlation_id", "n/d")
        logger.exception("Errore non gestito (correlation_id=%s)", correlation)
        return JSONResponse(
            status_code=500,
            content={"error": "internal_error", "correlation_id": correlation},
        )

    return app


app = create_app()
