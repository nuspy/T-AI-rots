"""La console: i mazzi in vendita (v5, Fase B) e le loro immagini.

**Le immagini, due strade separate.** Le *immagini nel sito* (in fondo al file): uno ZIP o una cartella con le 78
carte e il dorso, convertiti in WebP e conservati nel database (`DeckCardImage`) — il sito le mostra subito. L'*archivio
ZIP da scaricare* (Fase I, `/artwork`): lo stesso ZIP conservato così com'è, da riscaricare ed estrarre a mano in
`frontend/public/cards/<slug>/` per installare il mazzo come file del sito (serve un rilascio).

**Cosa non si cancella.** Un mazzo già posseduto da qualcuno (una riga in `deck_unlocks`) o già usato
in una lettura non si elimina: si disattiva. Lo stesso principio di piani e coupon."""
from __future__ import annotations

import asyncio
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from lanterna.rete import ip_client
from pydantic import BaseModel, Field, field_validator, model_validator
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError

from ...auth.dependencies import CurrentUser, DbSession, require_role
from ...billing import mazzi as mazzi_billing
from ...billing.lingue import pulisci
from ...domain import deck_repositories
from ...domain.deck_models import Deck, DeckCardImage, DeckUnlock, OffertaMazzo
from ...domain.deck_upload_models import DeckArtworkUpload
from ...domain.models import Reading
from ...domain.repositories import AuditRepository
from ...tarot import immagini_mazzo
from ...tarot.artwork_validazione import ZipArtworkNonValido, nomi_attesi, valida_zip
from ..deps import get_conoscenza

#: Oltre non ha senso: 78 WebP a 360×640 pesano tipicamente 3-6 MB in totale compressi in uno ZIP;
#: un tetto largo (50 MB) scarta subito un file sbagliato invece di riempire la tabella di blob.
TETTO_ZIP_BYTE = 50 * 1024 * 1024

router = APIRouter(prefix="/admin", tags=["mazzi"], dependencies=[Depends(require_role("admin"))])

TETTO_PREZZO = 1_000_000  # centesimi: diecimila euro, oltre è un refuso


def _ip(request: Request) -> Optional[str]:
    return ip_client(request)


#: Lo slug è l'identificativo del mazzo negli indirizzi (`/decks/thoth`, `/cards/<slug>/…`) e nei file: minuscole,
#: cifre e trattini singoli fra le parole (niente trattino all'inizio o alla fine), da 2 a 40 caratteri. Non si
#: cambia dopo la creazione: indirizzi, letture e ordini lo ricordano.
SLUG_MAZZO = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class MazzoNuovo(BaseModel):
    slug: str = Field(min_length=2, max_length=40)
    nome: str = Field(min_length=1, max_length=80)
    descrizione: Optional[str] = Field(default=None, max_length=2000)
    predefinito: bool = False
    attivo: bool = True
    attivazione_da: Optional[datetime] = None
    attivazione_fino: Optional[datetime] = None
    prezzo_digitale: Optional[int] = Field(default=None, ge=0, le=TETTO_PREZZO)
    prezzo_stampa: Optional[int] = Field(default=None, ge=0, le=TETTO_PREZZO)
    prezzo_fisico: Optional[int] = Field(default=None, ge=0, le=TETTO_PREZZO)
    richiede_spedizione: bool = False
    valuta: str = Field(default="EUR", min_length=3, max_length=3)
    rank: int = 0

    @field_validator("slug")
    @classmethod
    def _slug_valido(cls, valore: str) -> str:
        if not SLUG_MAZZO.match(valore):
            raise ValueError(
                "lo slug usa solo lettere minuscole, cifre e trattini fra le parole (es. halloween-2026)"
            )
        return valore

    @model_validator(mode="after")
    def _finestra_sensata(self) -> "MazzoNuovo":
        if self.attivazione_da and self.attivazione_fino and self.attivazione_da >= self.attivazione_fino:
            raise ValueError("la finestra di attivazione deve avere un inizio prima della fine")
        return self


class MazzoMod(BaseModel):
    nome: Optional[str] = Field(default=None, min_length=1, max_length=80)
    descrizione: Optional[str] = Field(default=None, max_length=2000)
    #: Le traduzioni (v8.5): lingua → testo, sostituite per intero.
    nomi: Optional[Dict[str, Optional[str]]] = None
    descrizioni: Optional[Dict[str, Optional[str]]] = None
    attivo: Optional[bool] = None
    attivazione_da: Optional[datetime] = None
    attivazione_fino: Optional[datetime] = None
    prezzo_digitale: Optional[int] = Field(default=None, ge=0, le=TETTO_PREZZO)
    prezzo_stampa: Optional[int] = Field(default=None, ge=0, le=TETTO_PREZZO)
    prezzo_fisico: Optional[int] = Field(default=None, ge=0, le=TETTO_PREZZO)
    richiede_spedizione: Optional[bool] = None
    rank: Optional[int] = None


@router.get("/decks")
async def mazzi(session: DbSession) -> list[Dict[str, Any]]:
    tutti = await deck_repositories.tutti(session)
    offerte = await deck_repositories.offerte_per(session, [d.id for d in tutti])
    return [mazzi_billing.mazzo_con_prezzo_json(d, offerte.get(d.id)) for d in tutti]


@router.post("/decks", status_code=201)
async def crea_mazzo(payload: MazzoNuovo, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    if payload.predefinito and await deck_repositories.predefinito(session) is not None:
        raise HTTPException(status_code=409, detail="Esiste già un mazzo predefinito.")
    mazzo = Deck(
        slug=payload.slug, nome=payload.nome.strip(), descrizione=(payload.descrizione or "").strip() or None,
        predefinito=payload.predefinito, attivo=payload.attivo,
        attivazione_da=payload.attivazione_da, attivazione_fino=payload.attivazione_fino,
        prezzo_digitale=payload.prezzo_digitale, prezzo_stampa=payload.prezzo_stampa, prezzo_fisico=payload.prezzo_fisico,
        richiede_spedizione=payload.richiede_spedizione, valuta=payload.valuta.upper(), rank=payload.rank,
    )
    session.add(mazzo)
    try:
        await session.flush()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=409, detail=f"Esiste già un mazzo con lo slug «{payload.slug}».") from exc
    await AuditRepository(session).record(
        action="deck.create", actor_id=user.id, target_type="deck", target_id=mazzo.slug,
        after=deck_repositories.mazzo_json(mazzo), ip=_ip(request),
    )
    await session.commit()
    return deck_repositories.mazzo_json(mazzo)


@router.put("/decks/{slug}")
async def modifica_mazzo(slug: str, payload: MazzoMod, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    mazzo = await deck_repositories.per_slug(session, slug)
    if mazzo is None:
        raise HTTPException(status_code=404, detail="Mazzo non trovato")
    prima = deck_repositories.mazzo_json(mazzo)
    dati = payload.model_dump(exclude_unset=True)
    if "attivazione_da" in dati or "attivazione_fino" in dati:
        da_ = dati.get("attivazione_da", mazzo.attivazione_da)
        fino = dati.get("attivazione_fino", mazzo.attivazione_fino)
        if da_ and fino and da_ >= fino:
            raise HTTPException(status_code=422, detail="la finestra di attivazione deve avere un inizio prima della fine")
    for campo, valore in dati.items():
        if campo == "nome" and isinstance(valore, str):
            valore = valore.strip()
        if campo == "descrizione":
            valore = (valore or "").strip() or None
        if campo in ("nomi", "descrizioni"):
            valore = pulisci(valore, 80 if campo == "nomi" else 2000)
        setattr(mazzo, campo, valore)
    await session.flush()
    await AuditRepository(session).record(
        action="deck.update", actor_id=user.id, target_type="deck", target_id=mazzo.slug,
        before=prima, after=deck_repositories.mazzo_json(mazzo), ip=_ip(request),
    )
    await session.commit()
    return deck_repositories.mazzo_json(mazzo)


@router.delete("/decks/{slug}", status_code=204)
async def elimina_mazzo(slug: str, request: Request, user: CurrentUser, session: DbSession) -> Response:
    mazzo = await deck_repositories.per_slug(session, slug)
    if mazzo is None:
        raise HTTPException(status_code=404, detail="Mazzo non trovato")
    if mazzo.predefinito:
        raise HTTPException(status_code=409, detail="Il mazzo predefinito non si elimina.")
    sblocchi = await session.scalar(select(func.count()).select_from(DeckUnlock).where(DeckUnlock.deck_id == mazzo.id))
    letture = await session.scalar(select(func.count()).select_from(Reading).where(Reading.deck_id == mazzo.id))
    if sblocchi or letture:
        raise HTTPException(status_code=409, detail="Il mazzo è già posseduto o usato: disattivalo, non si elimina.")
    prima = deck_repositories.mazzo_json(mazzo)
    await session.delete(mazzo)
    await AuditRepository(session).record(
        action="deck.delete", actor_id=user.id, target_type="deck", target_id=slug, before=prima, ip=_ip(request),
    )
    await session.commit()
    return Response(status_code=204)


# ---- offerte a tempo (Fase B2) --------------------------------------------------------------------


class OffertaIn(BaseModel):
    tipo: str = Field(pattern="^(percentuale|importo)$")
    valore: int = Field(gt=0, le=TETTO_PREZZO)
    valido_dal: Optional[datetime] = None
    valido_fino: Optional[datetime] = None
    #: I prodotti scontati (v8.5): il digitale, il PDF da stampare, la scatola fisica.
    formati: List[Literal["digitale", "pdf", "fisico"]] = Field(default_factory=lambda: ["digitale"], min_length=1)

    @model_validator(mode="after")
    def _sensata(self) -> "OffertaIn":
        if self.tipo == "percentuale" and self.valore > 100:
            raise ValueError("uno sconto percentuale non può superare 100")
        if self.valido_dal and self.valido_fino and self.valido_dal >= self.valido_fino:
            raise ValueError("la finestra dell'offerta deve avere un inizio prima della fine")
        return self


@router.put("/decks/{slug}/offerta")
async def imposta_offerta(slug: str, payload: OffertaIn, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    """Crea o sostituisce l'offerta del mazzo: **una sola** alla volta, non si accumulano."""
    mazzo = await deck_repositories.per_slug(session, slug)
    if mazzo is None:
        raise HTTPException(status_code=404, detail="Mazzo non trovato")
    formati = list(dict.fromkeys(payload.formati))
    senza_prezzo = [f for f in formati if mazzi_billing.listino_di(mazzo, f) is None]
    if senza_prezzo:
        raise HTTPException(status_code=422, detail=f"Il mazzo non ha un prezzo da scontare per: {', '.join(senza_prezzo)}.")
    prima_offerta = await deck_repositories.offerta_per(session, mazzo.id)
    prima = mazzi_billing.mazzo_con_prezzo_json(mazzo, prima_offerta)
    if prima_offerta is None:
        session.add(OffertaMazzo(
            deck_id=mazzo.id, tipo=payload.tipo, valore=payload.valore,
            valido_dal=payload.valido_dal, valido_fino=payload.valido_fino, formati=formati,
        ))
    else:
        prima_offerta.tipo = payload.tipo
        prima_offerta.valore = payload.valore
        prima_offerta.valido_dal = payload.valido_dal
        prima_offerta.valido_fino = payload.valido_fino
        prima_offerta.formati = formati
    await session.flush()
    offerta = await deck_repositories.offerta_per(session, mazzo.id)
    await AuditRepository(session).record(
        action="deck.offerta.imposta", actor_id=user.id, target_type="deck", target_id=mazzo.slug,
        before=prima, after=mazzi_billing.mazzo_con_prezzo_json(mazzo, offerta), ip=_ip(request),
    )
    await session.commit()
    return mazzi_billing.mazzo_con_prezzo_json(mazzo, offerta)


@router.delete("/decks/{slug}/offerta", status_code=204)
async def rimuovi_offerta(slug: str, request: Request, user: CurrentUser, session: DbSession) -> Response:
    mazzo = await deck_repositories.per_slug(session, slug)
    if mazzo is None:
        raise HTTPException(status_code=404, detail="Mazzo non trovato")
    offerta = await deck_repositories.offerta_per(session, mazzo.id)
    if offerta is None:
        raise HTTPException(status_code=404, detail="Questo mazzo non ha un'offerta.")
    prima = mazzi_billing.mazzo_con_prezzo_json(mazzo, offerta)
    await session.delete(offerta)
    await AuditRepository(session).record(
        action="deck.offerta.rimuovi", actor_id=user.id, target_type="deck", target_id=mazzo.slug,
        before=prima, ip=_ip(request),
    )
    await session.commit()
    return Response(status_code=204)


# ---- upload dell'artwork (v7, Fase I) ----------------------------------------------------------
#
# Scope deciso con l'operatore: automatizza la RICEZIONE e la VALIDAZIONE dei file, non elimina il
# rilascio. L'artwork finale resta statico nell'immagine del frontend (vedi `deck_models.py`): dopo
# l'upload, l'amministratore scarica lo ZIP validato (stessa sessione autenticata del browser già
# usata per `scaricaReport`, `admin/lib/api.ts`) e lo estrae a mano in
# `frontend/public/cards/<slug>/` prima del prossimo build+deploy.


@router.post("/decks/{slug}/artwork", status_code=201)
async def carica_artwork(
    slug: str, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    corpo = await request.body()
    if not corpo:
        raise HTTPException(status_code=400, detail="Nessun file ricevuto")
    if len(corpo) > TETTO_ZIP_BYTE:
        raise HTTPException(status_code=413, detail=f"Il file supera {TETTO_ZIP_BYTE // (1024*1024)} MB")

    conoscenza = get_conoscenza()
    attesi = nomi_attesi(conoscenza.ordine)
    try:
        presenti, mancanti = valida_zip(corpo, attesi)
    except ZipArtworkNonValido as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if mancanti:
        raise HTTPException(
            status_code=400,
            detail={"motivo": "file_mancanti", "mancanti": sorted(mancanti), "attesi": len(attesi)},
        )

    riga = DeckArtworkUpload(
        slug=slug, zip_bytes=corpo, file_count=len(presenti & attesi), created_by=user.id,
    )
    session.add(riga)
    await AuditRepository(session).record(
        action="deck.artwork.carica", actor_id=user.id, target_type="deck", target_id=slug,
        after={"file_count": riga.file_count}, ip=_ip(request),
    )
    await session.commit()
    return {"id": str(riga.id), "slug": slug, "file_count": riga.file_count, "creato_il": riga.created_at.isoformat()}


@router.get("/decks/{slug}/artwork")
async def elenco_artwork(slug: str, session: DbSession) -> List[Dict[str, Any]]:
    righe = (await session.execute(
        select(DeckArtworkUpload)
        .where(DeckArtworkUpload.slug == slug)
        .order_by(DeckArtworkUpload.created_at.desc())
    )).scalars().all()
    return [
        {"id": str(r.id), "file_count": r.file_count, "creato_il": r.created_at.isoformat()}
        for r in righe
    ]


@router.get("/decks/{slug}/artwork/{upload_id}")
async def scarica_artwork(slug: str, upload_id: uuid.UUID, session: DbSession) -> Response:
    riga = await session.get(DeckArtworkUpload, upload_id)
    if riga is None or riga.slug != slug:
        raise HTTPException(status_code=404, detail="Upload non trovato")
    return Response(
        content=riga.zip_bytes, media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{slug}-artwork.zip"'},
    )


@router.delete("/decks/{slug}/artwork/{upload_id}", status_code=204)
async def elimina_artwork(
    slug: str, upload_id: uuid.UUID, request: Request, user: CurrentUser, session: DbSession,
) -> Response:
    riga = await session.get(DeckArtworkUpload, upload_id)
    if riga is None or riga.slug != slug:
        raise HTTPException(status_code=404, detail="Upload non trovato")
    await session.delete(riga)
    await AuditRepository(session).record(
        action="deck.artwork.elimina", actor_id=user.id, target_type="deck", target_id=slug,
        ip=_ip(request),
    )
    await session.commit()
    return Response(status_code=204)


# ---- le immagini del mazzo nel sito: ZIP o cartella, subito online -----------------------------------
#
# Stesse regole di `tools/installa_mazzo.py` (`tarot/immagini_mazzo.py`), ma senza rilascio: le immagini, convertite
# in WebP alla misura web, stanno in `DeckCardImage` e le serve `GET /decks/{slug}/cards/{id}.webp`. Lo ZIP si
# pubblica in una richiesta; la cartella arriva un file per richiesta in bozza, poi `pubblica` controlla che ci sia
# tutto e sostituisce in blocco la serie di prima: il sito non vede mai un mazzo a metà.


def _ids_attesi() -> List[str]:
    return immagini_mazzo.ids_attesi(get_conoscenza().ordine)


async def _mazzo_con_immagini(session: DbSession, slug: str) -> Deck:
    mazzo = await deck_repositories.per_slug(session, slug)
    if mazzo is None:
        raise HTTPException(status_code=404, detail="Mazzo non trovato")
    if mazzo.predefinito:
        raise HTTPException(
            status_code=409,
            detail="Il mazzo predefinito usa le immagini del sito (frontend/public/cards/): non si caricano qui.",
        )
    return mazzo


async def _corpo(request: Request, tetto: int) -> bytes:
    if int(request.headers.get("content-length") or 0) > tetto:
        raise HTTPException(status_code=413, detail=f"Il file supera {tetto // (1024 * 1024)} MB")
    corpo = await request.body()
    if not corpo:
        raise HTTPException(status_code=400, detail="Nessun file ricevuto")
    if len(corpo) > tetto:
        raise HTTPException(status_code=413, detail=f"Il file supera {tetto // (1024 * 1024)} MB")
    return corpo


def _rifiuto(exc: immagini_mazzo.ImmaginiMazzoNonValide) -> HTTPException:
    """Il dettaglio è un oggetto (`messaggio`, e gli elenchi `mancanti`/`avanzano`/`doppioni` quando servono): la
    console li mostra per esteso."""
    return HTTPException(status_code=422, detail=exc.dettaglio)


async def _stato_immagini(session: DbSession, mazzo: Deck) -> Dict[str, Any]:
    attesi = _ids_attesi()
    pubblicate = await deck_repositories.ids_immagini(session, mazzo.id, bozza=False)
    bozza = set(await deck_repositories.ids_immagini(session, mazzo.id, bozza=True))
    return {
        "slug": mazzo.slug,
        "versione": mazzo.immagini_versione,
        "attese": len(attesi),
        "pubblicate": len(pubblicate),
        "bozza": len(bozza),
        "mancanti_bozza": [cid for cid in attesi if cid not in bozza] if bozza else [],
        # Gli id da trovare (78 carte + dorso): la console controlla una cartella prima di caricarla.
        "ids_attesi": attesi,
    }


def _converti(dati: Dict[str, bytes]) -> Dict[str, Tuple[bytes, int, int]]:
    return {cid: immagini_mazzo.prepara_carta(b, cid) for cid, b in dati.items()}


async def _sostituisci_pubblicate(session: DbSession, mazzo: Deck, nuove: List[DeckCardImage]) -> None:
    """Le `nuove` diventano la serie del sito: prima si tolgono le vecchie (e ogni altra bozza), poi si girano
    queste, poi la versione. Tutto nella stessa transazione: il sito non vede mai un mazzo a metà."""
    tenere = [img.id for img in nuove if img.id is not None]
    await session.execute(
        delete(DeckCardImage).where(DeckCardImage.deck_id == mazzo.id, DeckCardImage.id.not_in(tenere))
        if tenere else delete(DeckCardImage).where(DeckCardImage.deck_id == mazzo.id)
    )
    for img in nuove:
        img.bozza = False
        if img.id is None:
            session.add(img)
    mazzo.immagini_versione = immagini_mazzo.versione(img.etag for img in nuove)
    await session.flush()


@router.get("/decks/{slug}/immagini")
async def stato_immagini(slug: str, session: DbSession) -> Dict[str, Any]:
    """Quante immagini ha il mazzo nel sito, la versione della serie, e la bozza di un caricamento in corso."""
    return await _stato_immagini(session, await _mazzo_con_immagini(session, slug))


@router.post("/decks/{slug}/immagini/zip")
async def carica_immagini_zip(slug: str, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    """Lo ZIP con le 78 carte e il dorso (corpo = lo ZIP grezzo): riconosciuto, controllato, convertito e pubblicato
    in una richiesta. Se manca qualcosa non cambia niente, e la risposta elenca cosa manca, cosa avanza e i doppioni."""
    mazzo = await _mazzo_con_immagini(session, slug)
    corpo = await _corpo(request, immagini_mazzo.MAX_ZIP)
    try:
        riconoscimento, dati = await asyncio.to_thread(immagini_mazzo.leggi_zip, corpo, _ids_attesi())
        convertite = await asyncio.to_thread(_converti, dati)
    except immagini_mazzo.ImmaginiMazzoNonValide as exc:
        raise _rifiuto(exc) from exc
    del corpo, dati
    nuove = [
        DeckCardImage(deck_id=mazzo.id, card_id=cid, webp=webp, larghezza=w, altezza=h, etag=immagini_mazzo.impronta(webp))
        for cid, (webp, w, h) in convertite.items()
    ]
    await _sostituisci_pubblicate(session, mazzo, nuove)
    await AuditRepository(session).record(
        action="deck.immagini.zip", actor_id=user.id, target_type="deck", target_id=mazzo.slug,
        after={"immagini": len(nuove), "versione": mazzo.immagini_versione}, ip=_ip(request),
    )
    await session.commit()
    return await _stato_immagini(session, mazzo) | {
        "riepilogo": {
            "installate": len(nuove),
            "avanzano": sorted(riconoscimento.avanzano),
            "ignorati": len(riconoscimento.ignorati),
        },
    }


@router.post("/decks/{slug}/immagini/file")
async def carica_immagine_file(
    slug: str, request: Request, session: DbSession,
    percorso: str = Query(min_length=1, max_length=500, description="il nome del file, con la sua cartella"),
) -> Dict[str, Any]:
    """Un file di una cartella (corpo = l'immagine grezza): finisce nella bozza, il sito non lo vede ancora. Il nome
    (senza estensione) deve essere l'id di una carta o `dorso`; si rimanda lo stesso file per sostituirlo."""
    mazzo = await _mazzo_con_immagini(session, slug)
    if not immagini_mazzo.percorso_sicuro(percorso):
        raise HTTPException(status_code=422, detail={"messaggio": f"{percorso}: percorso non ammesso."})
    cid, _ = immagini_mazzo.id_carta(percorso, set(_ids_attesi()))
    if cid is None:
        raise HTTPException(status_code=422, detail={
            "messaggio": f"{percorso}: non è una carta del mazzo (il nome deve essere l'id della carta, "
                         "come maj-00.webp o bastoni-06.png, oppure dorso.webp).",
        })
    corpo = await _corpo(request, immagini_mazzo.MAX_FILE)
    try:
        webp, larghezza, altezza = await asyncio.to_thread(immagini_mazzo.prepara_carta, corpo, percorso)
    except immagini_mazzo.ImmaginiMazzoNonValide as exc:
        raise _rifiuto(exc) from exc
    riga = (await session.execute(
        select(DeckCardImage).where(
            DeckCardImage.deck_id == mazzo.id, DeckCardImage.card_id == cid, DeckCardImage.bozza.is_(True),
        )
    )).scalar_one_or_none()
    if riga is None:
        riga = DeckCardImage(deck_id=mazzo.id, card_id=cid, bozza=True)
        session.add(riga)
    riga.webp, riga.larghezza, riga.altezza, riga.etag = webp, larghezza, altezza, immagini_mazzo.impronta(webp)
    await session.commit()
    return {"carta": cid, "bozza": len(await deck_repositories.ids_immagini(session, mazzo.id, bozza=True))}


@router.delete("/decks/{slug}/immagini/bozza", status_code=204)
async def scarta_bozza_immagini(slug: str, session: DbSession) -> Response:
    """Ricomincia un caricamento a più passi: la bozza si svuota, le immagini pubblicate restano."""
    mazzo = await _mazzo_con_immagini(session, slug)
    await session.execute(
        delete(DeckCardImage).where(DeckCardImage.deck_id == mazzo.id, DeckCardImage.bozza.is_(True))
    )
    await session.commit()
    return Response(status_code=204)


@router.post("/decks/{slug}/immagini/pubblica")
async def pubblica_bozza_immagini(slug: str, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    """La bozza diventa la serie del sito, se è completa (78 carte + dorso); altrimenti 422 con l'elenco di cosa
    manca, e non cambia niente."""
    mazzo = await _mazzo_con_immagini(session, slug)
    attesi = _ids_attesi()
    bozza = await deck_repositories.immagini_di(session, mazzo.id, bozza=True)
    presenti = {img.card_id for img in bozza}
    mancanti = [cid for cid in attesi if cid not in presenti]
    if mancanti:
        raise HTTPException(status_code=422, detail={
            "messaggio": f"Il mazzo non è completo: mancano {len(mancanti)} file su {len(attesi)}.",
            "mancanti": mancanti,
        })
    await _sostituisci_pubblicate(session, mazzo, bozza)
    await AuditRepository(session).record(
        action="deck.immagini.cartella", actor_id=user.id, target_type="deck", target_id=mazzo.slug,
        after={"immagini": len(bozza), "versione": mazzo.immagini_versione}, ip=_ip(request),
    )
    await session.commit()
    return await _stato_immagini(session, mazzo) | {
        "riepilogo": {"installate": len(bozza), "avanzano": [], "ignorati": 0},
    }


@router.delete("/decks/{slug}/immagini", status_code=204)
async def elimina_immagini(slug: str, request: Request, user: CurrentUser, session: DbSession) -> Response:
    """Toglie le immagini caricate dalla console (e la bozza): il mazzo torna ai file del sito, se ne ha."""
    mazzo = await _mazzo_con_immagini(session, slug)
    await session.execute(delete(DeckCardImage).where(DeckCardImage.deck_id == mazzo.id))
    prima = mazzo.immagini_versione
    mazzo.immagini_versione = None
    await AuditRepository(session).record(
        action="deck.immagini.elimina", actor_id=user.id, target_type="deck", target_id=mazzo.slug,
        before={"versione": prima}, ip=_ip(request),
    )
    await session.commit()
    return Response(status_code=204)
