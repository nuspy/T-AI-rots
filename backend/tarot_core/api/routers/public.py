"""Ciò che si legge senza account: stese, carte, disclaimer, letture condivise.

Le pagine pubbliche delle carte servono anche a chi cerca «significato del
Tre di Spade»: sono la porta d'ingresso organica del servizio.
"""
from __future__ import annotations

import secrets
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import Response
from lanterna.rete import ip_client
from pydantic import BaseModel, Field
from sqlalchemy import select

from ...auth.dependencies import COOKIE_ANONIMO, DbSession, OptionalUser
from ...billing import mazzi as mazzi_billing
from ...domain import consent_repositories, deck_repositories
from ...domain.consent_models import TIPI_CORRENTI
from ...domain.repositories import ReadingRepository
from ...domain.share_models import ShareImage
from ...settings import get_settings
from ...tarot.condivisione import anonimizza, simbolo_partner
from ...tarot.conoscenza import speciale as categoria_speciale
from ...tarot.giorno import carta_universale, oggi_utc
from ...tarot.lingue import in_lingua, lingua_per_paese
from ...tarot.stampa_mazzo import pdf_per_mazzo
from ...tarot.testi import DISCLAIMER, QUALCUNO_DI_SPECIALE
from ..deps import get_conoscenza
from .blog import immagini_catalogo

router = APIRouter(tags=["pubblico"])


@router.get("/lingua-suggerita")
async def lingua_suggerita(request: Request) -> Dict[str, Optional[str]]:
    """L'ultimo indizio per la lingua di chi arriva (dopo la scelta salvata e la lingua del browser o del telefono):
    il paese dell'IP, letto nel database geografico locale (nessun servizio esterno, l'IP non si salva)."""
    from lanterna.geo import luogo

    paese = luogo(get_settings().analytics_geo or None, ip_client(request)).paese
    return {"paese": paese, "lingua": lingua_per_paese(paese)}

#: Lo stesso anno di `readings.py::DURATA_COOKIE_ANONIMO` — non importato da lì per non accoppiare
#: due router per una singola costante: un consenso cookie può arrivare prima di qualunque lettura,
#: quindi questo file deve poter generare l'identità anonima da solo.
DURATA_COOKIE_ANONIMO = 60 * 60 * 24 * 365


#: `?lang=` sceglie la lingua dei testi lunghi: `en` (la lingua delle pagine pubbliche) o `it`. Senza,
#: l'italiano di sempre: chi non lo chiede non vede cambiare niente.
Lang = Query(default=None, max_length=10, description="it o en: la lingua dei testi")


@router.get("/spreads")
async def stese(
    session: DbSession,
    categoria: Optional[str] = Query(default=None, pattern="^(standard|lavoro|compatibilita|coppia)$"),
    tema: Optional[str] = Query(default=None, pattern="^(lavoro)$"),
    lang: Optional[str] = Lang,
) -> List[Dict[str, Any]]:
    """Le stese. Con `?categoria=` solo quelle della lettura standard, di lavoro e
    affari, di compatibilità o di coppia; senza, tutte. La home e la scelta della stesa
    standard chiedono `standard`, così le letture speciali non vi compaiono.

    Con `?tema=lavoro` le stese che il sito propone per quel tema: quelle della categoria
    `lavoro` e poi le standard con `"lavoro"` in `temi` (ogni stesa porta `temi`, per chi
    preferisce filtrare da sé l'elenco completo). `tema` vince su `categoria`.

    Ogni stesa porta `immagine` (v9.4): l'illustrazione del catalogo, `{url, mini, alt}`, o null."""
    conoscenza = get_conoscenza()
    if tema:
        scelte = conoscenza.stese_per_tema(tema)
    else:
        scelte = conoscenza.stese_per(categoria) if categoria else conoscenza.stese.values()
    immagini = await immagini_catalogo(session, "stesa")
    return [conoscenza.stesa_pubblica(s, lang) | {"immagine": immagini.get(s["id"])} for s in scelte]


@router.get("/spreads/{spread_id}")
async def stesa(spread_id: str, session: DbSession, lang: Optional[str] = Lang) -> Dict[str, Any]:
    """Una stesa, per la sua pagina pubblica: posizioni, significati, regole e l'illustrazione (`immagine`, o null).
    Si trova per id (`croce-celtica`) o per slug (`celtic-cross`)."""
    conoscenza = get_conoscenza()
    trovata = conoscenza.stesa(conoscenza.risolvi_stesa(spread_id) or "")
    if trovata is None:
        raise HTTPException(status_code=404, detail="Stesa sconosciuta")
    immagini = await immagini_catalogo(session, "stesa")
    return conoscenza.stesa_pubblica(trovata, lang) | {"immagine": immagini.get(trovata["id"])}


@router.get("/cards")
def carte(lang: Optional[str] = Lang) -> List[Dict[str, Any]]:
    conoscenza = get_conoscenza()
    return [conoscenza.carta_pubblica(i, lang=lang) for i in conoscenza.ordine]


@router.get("/cards/{card_id}")
def carta(card_id: str, lang: Optional[str] = Lang) -> Dict[str, Any]:
    """Una carta, per id (`maj-17`) o per slug in qualunque lingua (`the-star`, `la-stella`)."""
    conoscenza = get_conoscenza()
    trovata = conoscenza.risolvi_carta(card_id)
    if trovata is None:
        raise HTTPException(status_code=404, detail="Carta sconosciuta")
    return conoscenza.carta_pubblica(trovata, completa=True, lang=lang)


@router.get("/daily-card/today")
def carta_di_oggi(lang: Optional[str] = Lang) -> Dict[str, Any]:
    """La carta del giorno per tutti, senza account: un Arcano maggiore, la stessa per chiunque per tutto il giorno
    (UTC). Non è la carta personale di `/me/daily-card`, che ha la serie dei giorni di fila."""
    conoscenza = get_conoscenza()
    giorno = oggi_utc()
    carta = conoscenza.carta_pubblica(carta_universale(conoscenza, giorno), completa=True, lang=lang)
    return {"giorno": giorno.isoformat(), "carta": carta, "testo": carta["dritto"]}


@router.get("/disclaimer")
def disclaimer(lang: str = "it") -> Dict[str, str]:
    return {"testo": in_lingua(DISCLAIMER, lang)}


@router.get("/impostazioni-pubbliche")
async def impostazioni_pubbliche(session: DbSession) -> Dict[str, int]:
    """I numeri del regalo d'iscrizione e del referral: niente di sensibile, servono alla home e al profilo per
    mostrare cifre vere invece di un testo fisso che l'amministrazione potrebbe aver cambiato."""
    from ...domain.impostazioni_repositories import correnti, pubblico

    return pubblico(await correnti(session))


@router.get("/consenso")
async def consenso_attuale(request: Request, session: DbSession, user: OptionalUser) -> Dict[str, Optional[str]]:
    """I consensi correnti di questa persona (loggata o anonima), uno per tipo di `TIPI_CORRENTI`: il banner e la
    sezione «Privacy e consensi» del profilo li usano per non richiedere di nuovo una scelta già data. `None` per un
    tipo mai deciso — non un rifiuto implicito.

    `cookie` non è più un consenso a sé (dalla Fase 1 del GDPR è diviso in `statistiche` e `google_analytics`): resta
    nella risposta, uguale a `statistiche`, solo per il vecchio sito sotto `/old`."""
    anon_id = None if user else request.cookies.get(COOKIE_ANONIMO)
    correnti = await consent_repositories.correnti_per(session, user_id=user.id if user else None, anon_id=anon_id)
    stato: Dict[str, Optional[str]] = {
        tipo: (correnti[tipo].valore if tipo in correnti else None) for tipo in TIPI_CORRENTI
    }
    stato["cookie"] = stato["statistiche"]
    return stato


#: I tipi che si possono scegliere anche senza account: quelli del banner. Gli altri riguardano dati che esistono solo
#: con un account (i testi, la scheda, le notifiche dell'app).
TIPI_ANONIMI = ("statistiche", "google_analytics", "pubblicita")
#: `cookie` si accetta ancora in scrittura dal vecchio sito: vale per `statistiche` e `google_analytics` insieme.
_TIPO_IN = "^(" + "|".join(TIPI_CORRENTI + ("cookie",)) + ")$"


class Consenso(BaseModel):
    tipo: str = Field(pattern=_TIPO_IN)
    valore: str = Field(pattern="^(accettato|rifiutato)$")
    #: La versione del testo informativo che questa persona ha effettivamente visto prima di
    #: scegliere — non un default silenzioso: un consenso senza sapere a quale testo si riferisce
    #: non è verificabile in un contenzioso.
    versione_informativa: str = Field(min_length=1, max_length=20)
    #: Da dove: il sito o le app (Fase 7–9).
    origine: str = Field(default="web", pattern="^(web|android|ios)$")


class Scelta(BaseModel):
    tipo: str = Field(pattern=_TIPO_IN)
    valore: str = Field(pattern="^(accettato|rifiutato)$")


class Consensi(BaseModel):
    """Più scelte insieme («accetta tutto», «rifiuta tutto», «scegli» del banner), sullo stesso testo informativo."""

    scelte: List[Scelta] = Field(min_length=1, max_length=len(TIPI_CORRENTI) + 1)
    versione_informativa: str = Field(min_length=1, max_length=20)
    origine: str = Field(default="web", pattern="^(web|android|ios)$")


def _identita_consenso(request: Request, response: Response, user) -> Optional[str]:
    """L'`anon_id` di chi sceglie senza account, creandolo se manca: un consenso arriva quasi sempre PRIMA di
    qualunque lettura, quindi qui — non solo in `/readings/anonime` — può nascere l'identità anonima (`tarots_anon`),
    stessa convenzione di v6 Fase F."""
    if user is not None:
        return None
    anon_id = request.cookies.get(COOKIE_ANONIMO)
    if anon_id is None:
        anon_id = secrets.token_urlsafe(32)
        in_produzione = get_settings().environment == "prod"
        response.set_cookie(
            COOKIE_ANONIMO, anon_id, max_age=DURATA_COOKIE_ANONIMO,
            httponly=True, secure=in_produzione, samesite="none" if in_produzione else "lax",
        )
    return anon_id


async def _registra_scelte(
    session, request: Request, user, anon_id: Optional[str], scelte: List[Scelta], versione: str, origine: str,
) -> None:
    from ...tarot.consensi import dopo_la_scelta

    espanse: Dict[str, str] = {}
    for s in scelte:
        # Il vecchio «cookie» del sito sotto /old: le due categorie che sostituisce, con la stessa scelta.
        for tipo in (("statistiche", "google_analytics") if s.tipo == "cookie" else (s.tipo,)):
            espanse[tipo] = s.valore
    if user is None and any(t not in TIPI_ANONIMI for t in espanse):
        raise HTTPException(status_code=401, detail="Questo consenso si sceglie dopo aver effettuato l'accesso")
    for tipo, valore in espanse.items():
        await consent_repositories.registra(
            session, user_id=user.id if user else None, anon_id=anon_id,
            tipo=tipo, valore=valore, versione_informativa=versione, ip=ip_client(request), origine=origine,
        )
        await dopo_la_scelta(session, user, tipo, valore)


@router.post("/consenso")
async def registra_consenso(
    payload: Consenso, request: Request, response: Response, session: DbSession, user: OptionalUser,
) -> Dict[str, str]:
    """Registra (o sostituisce) il consenso di questa persona per `payload.tipo`, con una riga nello storico.

    Funziona anche per chi non si è mai registrato, per i tipi del banner (`TIPI_ANONIMI`). Revocare
    `dati_particolari` toglie subito ciò che ne dipende (`tarot/consensi.py`)."""
    anon_id = _identita_consenso(request, response, user)
    await _registra_scelte(
        session, request, user, anon_id, [Scelta(tipo=payload.tipo, valore=payload.valore)],
        payload.versione_informativa, payload.origine,
    )
    await session.commit()
    return {"esito": "ok"}


@router.post("/consensi")
async def registra_consensi(
    payload: Consensi, request: Request, response: Response, session: DbSession, user: OptionalUser,
) -> Dict[str, Optional[str]]:
    """Più scelte in una volta, nella stessa transazione: o tutte o nessuna. Restituisce lo stato aggiornato."""
    anon_id = _identita_consenso(request, response, user)
    await _registra_scelte(
        session, request, user, anon_id, payload.scelte, payload.versione_informativa, payload.origine,
    )
    await session.commit()
    correnti = await consent_repositories.correnti_per(session, user_id=user.id if user else None, anon_id=anon_id)
    stato: Dict[str, Optional[str]] = {
        tipo: (correnti[tipo].valore if tipo in correnti else None) for tipo in TIPI_CORRENTI
    }
    stato["cookie"] = stato["statistiche"]
    return stato


@router.get("/eta-minima")
async def eta_minima_pubblica(request: Request, user: OptionalUser) -> Dict[str, Any]:
    """L'età minima per usare il servizio da qui (`tarot/eta_minima.py`): per il paese del profilo, se c'è, altrimenti
    per quello stimato dall'IP (database geografico locale, l'IP non si salva). Il sito la mostra nella conferma
    «ho almeno N anni»."""
    from ...tarot import eta_minima

    paese = (user.posizione_paese if user else None) or eta_minima.paese_da_ip(ip_client(request))
    return {"anni": eta_minima.anni_minimi(paese), "paese": paese}


@router.get("/shared/{token}")
async def condivisa(token: str, session: DbSession) -> Dict[str, Any]:
    """Una lettura condivisa: domanda, carte, responso. Niente intervista,
    niente nome di chi l'ha fatta.

    Nelle letture speciali (compatibilità, coppia) il nome dell'altra persona
    diventa «qualcuno di speciale» in ogni testo, e al suo posto il frontend
    disegna il simbolo del suo genere: escono `partner_simbolo` e `partner_frase`,
    mai nome, cognome, date, intervista o compatibilità zodiacale.
    """
    lettura = await ReadingRepository(session).by_share_token(token)
    if lettura is None or lettura.status != "completata":
        raise HTTPException(status_code=404, detail="Lettura non trovata")
    conoscenza = get_conoscenza()
    stesa = conoscenza.stesa(lettura.spread_id)
    categoria = conoscenza.categoria_di(stesa) if stesa else "standard"
    partner = (lettura.persone or {}).get("partner") or {}
    speciale = categoria_speciale(categoria) or lettura.persone is not None
    frase = in_lingua(QUALCUNO_DI_SPECIALE, lettura.lang)

    def anonimo(testo: Optional[str]) -> Optional[str]:
        if not speciale:
            return testo
        for nome in (partner.get("nome"), partner.get("cognome")):
            testo = anonimizza(testo, nome, frase, lang=lettura.lang)
        return testo

    return {
        "question": anonimo(lettura.question),
        "lang": lettura.lang,
        "mazzo": deck_repositories.slug_immagini(lettura.mazzo),
        "stesa": conoscenza.stesa_pubblica(stesa) if stesa else None,
        "categoria": categoria,
        "speciale": speciale,
        "partner_simbolo": simbolo_partner(partner.get("genere")) if speciale else None,
        "partner_frase": frase if speciale else None,
        "cards": [
            {
                "posizione": c.posizione,
                "calcolata": c.calcolata,
                "rivelata": True,
                "carta": conoscenza.carta_pubblica(c.card_id),
                "rovescio": c.rovescio,
                "interpretazione": anonimo(c.interpretazione),
            }
            for c in lettura.cards
        ],
        "synthesis": anonimo(lettura.synthesis),
        "share_text": anonimo(lettura.share_text),
        "immagine": await _ha_immagine(session, lettura.id),
        "created_at": lettura.created_at.isoformat(),
        "disclaimer": in_lingua(DISCLAIMER, lettura.lang),
    }


async def _ha_immagine(session, reading_id) -> bool:
    riga = (await session.execute(
        select(ShareImage.reading_id).where(ShareImage.reading_id == reading_id)
    )).first()
    return riga is not None


# ---- mazzi (v5, Fase B) -----------------------------------------------------------------------


@router.get("/decks")
async def mazzi(session: DbSession, lang: Optional[str] = Query(default=None, pattern="^[a-z]{2}$")) -> List[Dict[str, Any]]:
    """I mazzi visibili nel negozio adesso: attivi e dentro la finestra di attivazione, se c'è. `lang`: nome e
    descrizione in quella lingua (poi l'inglese, poi l'originale)."""
    attivi = await deck_repositories.attivi_ora(session)
    offerte = await deck_repositories.offerte_per(session, [d.id for d in attivi])
    return [mazzi_billing.mazzo_con_prezzo_json(d, offerte.get(d.id), lang) for d in attivi]


@router.get("/decks/{slug}")
async def mazzo(slug: str, session: DbSession, lang: Optional[str] = Query(default=None, pattern="^[a-z]{2}$")) -> Dict[str, Any]:
    d = await deck_repositories.per_slug(session, slug)
    if d is None or not d.attivo_ora:
        raise HTTPException(status_code=404, detail="Mazzo non trovato")
    offerta = await deck_repositories.offerta_per(session, d.id)
    return mazzi_billing.mazzo_con_prezzo_json(d, offerta, lang)


@router.get("/decks/{slug}/pdf")
async def mazzo_pdf_gratuito(slug: str, session: DbSession) -> Response:
    """Il PDF da stampare, gratis: solo se il mazzo lo offre a prezzo zero — un prezzo assente
    (non offerto) o positivo (a pagamento, si compra in `POST /orders`) restano un 404."""
    d = await deck_repositories.per_slug(session, slug)
    if d is None or not d.attivo_ora or d.prezzo_stampa != 0:
        raise HTTPException(status_code=404, detail="PDF non disponibile per questo mazzo")
    conoscenza = get_conoscenza()
    corpo = await pdf_per_mazzo(
        d.slug, list(conoscenza.ordine), gratuito=True, web_public_url=get_settings().web_public_url,
        precaricate=await deck_repositories.immagini_per_pdf(session, d),
    )
    return Response(
        content=corpo, media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{d.slug}-tarots-chat.pdf"'},
    )


#: Le carte di un mazzo caricato dalla console: un giorno in cache, poi si riconvalida con l'ETag (una carta
#: corretta si vede entro un giorno). Con `?v=<versione della serie>` l'indirizzo cambia a ogni nuova serie: allora la
#: cache è di un anno.
CACHE_CARTA = "public, max-age=86400, stale-while-revalidate=604800"
CACHE_CARTA_VERSIONATA = "public, max-age=31536000, immutable"


@router.get("/decks/{slug}/cards/{nome}")
async def immagine_carta_mazzo(
    slug: str, nome: str, request: Request, session: DbSession, v: Optional[str] = Query(default=None, max_length=16),
) -> Response:
    """Una carta (`maj-00.webp`) o il dorso (`dorso.webp`) di un mazzo caricato dalla console. Non guarda se il mazzo
    è in vendita adesso: le letture già fatte e quelle condivise devono continuare a mostrare le loro carte. Il sito
    ci arriva da `/cards/<slug>/<id>.webp` quando quel file non è fra i suoi (`frontend/app/(v2)/cards/[id]/[file]`)."""
    if not nome.endswith(".webp"):
        raise HTTPException(status_code=404, detail="Immagine non trovata")
    img = await deck_repositories.immagine_pubblicata(session, slug, nome[: -len(".webp")])
    if img is None:
        raise HTTPException(status_code=404, detail="Immagine non trovata")
    etag = f'"{img.etag}"'
    versionata = False
    if v is not None:
        mazzo = await deck_repositories.per_slug(session, slug)
        versionata = mazzo is not None and v == mazzo.immagini_versione
    intestazioni = {
        "ETag": etag,
        "Cache-Control": CACHE_CARTA_VERSIONATA if versionata else CACHE_CARTA,
        "X-Content-Type-Options": "nosniff",
    }
    richiesti = [x.strip() for x in request.headers.get("if-none-match", "").split(",")]
    if etag in richiesti or f"W/{etag}" in richiesti:
        return Response(status_code=304, headers=intestazioni)
    return Response(content=img.webp, media_type="image/webp", headers=intestazioni)
