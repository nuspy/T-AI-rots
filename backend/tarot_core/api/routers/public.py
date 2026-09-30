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
from ...domain.consent_models import TIPI_CONSENSO
from ...domain.repositories import ReadingRepository
from ...domain.share_models import ShareImage
from ...settings import get_settings
from ...tarot.condivisione import anonimizza, simbolo_partner
from ...tarot.giorno import carta_universale, oggi_utc
from ...tarot.lingue import in_lingua
from ...tarot.stampa_mazzo import pdf_per_mazzo
from ...tarot.testi import DISCLAIMER, QUALCUNO_DI_SPECIALE
from ..deps import get_conoscenza

router = APIRouter(tags=["pubblico"])

#: Lo stesso anno di `readings.py::DURATA_COOKIE_ANONIMO` — non importato da lì per non accoppiare
#: due router per una singola costante: un consenso cookie può arrivare prima di qualunque lettura,
#: quindi questo file deve poter generare l'identità anonima da solo.
DURATA_COOKIE_ANONIMO = 60 * 60 * 24 * 365


#: `?lang=` sceglie la lingua dei testi lunghi: `en` (la lingua delle pagine pubbliche) o `it`. Senza,
#: l'italiano di sempre: chi non lo chiede non vede cambiare niente.
Lang = Query(default=None, max_length=10, description="it o en: la lingua dei testi")


@router.get("/spreads")
def stese(
    categoria: Optional[str] = Query(default=None, pattern="^(standard|compatibilita|coppia)$"),
    lang: Optional[str] = Lang,
) -> List[Dict[str, Any]]:
    """Le stese. Con `?categoria=` solo quelle della lettura standard, di
    compatibilità o di coppia; senza, tutte. La home e la scelta della stesa
    standard chiedono `standard`, così le letture speciali non vi compaiono."""
    conoscenza = get_conoscenza()
    scelte = conoscenza.stese_per(categoria) if categoria else conoscenza.stese.values()
    return [conoscenza.stesa_pubblica(s, lang) for s in scelte]


@router.get("/spreads/{spread_id}")
def stesa(spread_id: str, lang: Optional[str] = Lang) -> Dict[str, Any]:
    """Una stesa, per la sua pagina pubblica: posizioni, significati, regole. Si trova per id
    (`croce-celtica`) o per slug (`celtic-cross`)."""
    conoscenza = get_conoscenza()
    trovata = conoscenza.stesa(conoscenza.risolvi_stesa(spread_id) or "")
    if trovata is None:
        raise HTTPException(status_code=404, detail="Stesa sconosciuta")
    return conoscenza.stesa_pubblica(trovata, lang)


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
    """I consensi correnti di questa persona (loggata o anonima): il banner cookie e la sezione
    privacy del profilo li usano per non richiedere di nuovo una scelta già data. `None` per un
    tipo mai deciso — non un rifiuto implicito."""
    anon_id = None if user else request.cookies.get(COOKIE_ANONIMO)
    correnti = await consent_repositories.correnti_per(session, user_id=user.id if user else None, anon_id=anon_id)
    return {tipo: (correnti[tipo].valore if tipo in correnti else None) for tipo in TIPI_CONSENSO}


class Consenso(BaseModel):
    tipo: str = Field(pattern="^(cookie|condivisione_dati_partner)$")
    valore: str = Field(pattern="^(accettato|rifiutato)$")
    #: La versione del testo informativo che questa persona ha effettivamente visto prima di
    #: scegliere — non un default silenzioso: un consenso senza sapere a quale testo si riferisce
    #: non è verificabile in un contenzioso.
    versione_informativa: str = Field(min_length=1, max_length=20)


@router.post("/consenso")
async def registra_consenso(
    payload: Consenso, request: Request, response: Response, session: DbSession, user: OptionalUser,
) -> Dict[str, str]:
    """Registra (o sostituisce) il consenso di questa persona per `payload.tipo`.

    Funziona anche per chi non si è mai registrato: un consenso cookie arriva quasi sempre PRIMA
    di qualunque lettura, quindi qui — non solo in `/readings/anonime` — può nascere l'identità
    anonima (`tarots_anon`), stessa convenzione di v6 Fase F."""
    anon_id = None if user else request.cookies.get(COOKIE_ANONIMO)
    if user is None and anon_id is None:
        anon_id = secrets.token_urlsafe(32)
        in_produzione = get_settings().environment == "prod"
        response.set_cookie(
            COOKIE_ANONIMO, anon_id, max_age=DURATA_COOKIE_ANONIMO,
            httponly=True, secure=in_produzione, samesite="none" if in_produzione else "lax",
        )
    await consent_repositories.registra(
        session, user_id=user.id if user else None, anon_id=anon_id,
        tipo=payload.tipo, valore=payload.valore, versione_informativa=payload.versione_informativa,
        ip=ip_client(request),
    )
    await session.commit()
    return {"esito": "ok"}


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
    speciale = categoria != "standard" or lettura.persone is not None
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
    )
    return Response(
        content=corpo, media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{d.slug}-tarots-chat.pdf"'},
    )
