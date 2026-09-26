"""Il profilo di chi consulta: data di nascita, genere, carte personali, il
partner ricordato, inviti, carta del giorno."""
from __future__ import annotations

import asyncio
import hashlib
from datetime import date, datetime, timedelta
from typing import Any, Dict, Optional
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException, Request, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import select

from ...auth.dependencies import CurrentUser, DbSession
from ...billing.credits import RegistroCrediti
from ...domain.base import utcnow
from ...domain.blog_models import MediaImage
from ...domain.models import DailyCard, User
from ...domain.repositories import AuditRepository, nuovo_codice_invito
from ...settings import get_settings
from ...tarot import blog as regole_blog
from ...tarot.numerologia import carta_dell_anima, carta_dell_anno
from ...tarot.persone import LUNGHEZZA_GENERE_ALTRO, mancanti, pulisci
from ..deps import get_conoscenza
from .blog import nome_pubblico, url_immagine
from .condivisione import contatore

router = APIRouter(prefix="/me", tags=["profilo"])

#: Il giorno della carta del giorno è quello italiano: «oggi» per chi la
#: apre, non per il server.
FUSO = ZoneInfo("Europe/Rome")


class ModificaProfilo(BaseModel):
    birth_date: Optional[date] = None
    locale: Optional[str] = Field(default=None, pattern="^(it|en)$")
    #: Il genere dichiarato. «non_dice» (preferisco non dirlo) è una risposta valida.
    gender: Optional[str] = Field(default=None, pattern="^(donna|uomo|non_binario|altro|non_dice)$")
    #: Il testo libero di «altro»: si azzera se il genere non è «altro».
    gender_custom: Optional[str] = Field(default=None, max_length=40)
    #: La casella facoltativa «persona trans», separata dal genere.
    is_trans: Optional[bool] = None
    #: Il promemoria della verifica in due passaggi all'accesso: `false` = «non mostrare più».
    promemoria_2fa: Optional[bool] = None
    #: Come ti presenti nei commenti del blog. Vuoto = si usa il primo nome.
    nome_pubblico: Optional[str] = Field(default=None, max_length=60)


class Invito(BaseModel):
    codice: str = Field(min_length=4, max_length=16)


def _oggi() -> date:
    return datetime.now(FUSO).date()


async def _profilo_json(user: User, session) -> Dict[str, Any]:
    conoscenza = get_conoscenza()
    dati: Dict[str, Any] = {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "locale": user.locale,
        "birth_date": user.birth_date.isoformat() if user.birth_date else None,
        "gender": user.gender,
        "gender_custom": user.gender_custom,
        "is_trans": user.is_trans,
        "promemoria_2fa": user.promemoria_2fa,
        "nome_pubblico": user.nome_pubblico,
        "nome_mostrato": nome_pubblico(user),
        "avatar": url_immagine(user.avatar_id),
        # Il partner ricordato ha il cognome: si mostra solo al proprietario.
        "partner_ricordato": user.partner_ricordato,
        # Cosa manca nella scheda per le letture di compatibilità e di coppia.
        "relazioni": {"completo": not mancanti(user), "mancanti": mancanti(user)},
        "referral_code": user.referral_code,
        "invitato": user.referred_by is not None,
        # Il contatore delle condivisioni accertate e dei premi (vedi condivisione.py).
        "condivisioni": await contatore(session, user),
        "carta_anima": None,
        "carta_anno": None,
    }
    if user.birth_date:
        dati["carta_anima"] = conoscenza.carta_pubblica(
            conoscenza.maggiore(carta_dell_anima(user.birth_date))["id"], completa=True,
        )
        dati["carta_anno"] = conoscenza.carta_pubblica(
            conoscenza.maggiore(carta_dell_anno(user.birth_date, _oggi().year))["id"], completa=True,
        )
    return dati


@router.get("/profile")
async def profilo(user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    if not user.referral_code:
        user.referral_code = nuovo_codice_invito()
        await session.commit()
    return await _profilo_json(user, session)


@router.patch("/profile")
async def modifica(payload: ModificaProfilo, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    if payload.birth_date is not None:
        if payload.birth_date > _oggi() or payload.birth_date.year < 1900:
            raise HTTPException(status_code=400, detail="Data di nascita non valida")
        user.birth_date = payload.birth_date
    if payload.locale:
        user.locale = payload.locale
    if payload.gender is not None:
        if payload.gender == "altro":
            testo = pulisci(payload.gender_custom, LUNGHEZZA_GENERE_ALTRO)
            if not testo:
                raise HTTPException(status_code=400, detail="Con «altro» scrivi come ti definisci")
            user.gender_custom = testo
        else:
            user.gender_custom = None
        user.gender = payload.gender
    if payload.is_trans is not None:
        user.is_trans = payload.is_trans
    if payload.promemoria_2fa is not None:
        user.promemoria_2fa = payload.promemoria_2fa
    if payload.nome_pubblico is not None:
        user.nome_pubblico = pulisci(payload.nome_pubblico, 60) or None
    await session.commit()
    return await _profilo_json(user, session)


@router.delete("/partner", status_code=status.HTTP_204_NO_CONTENT)
async def dimentica_partner(user: CurrentUser, session: DbSession) -> Response:
    """Cancella il partner ricordato. Idempotente: senza partner non fa nulla.

    Nel registro entra il fatto, mai i dati del partner: sono di un terzo.
    """
    if user.partner_ricordato is not None:
        user.partner_ricordato = None
        await AuditRepository(session).record(
            action="partner.forget", actor_id=user.id, target_type="user", target_id=str(user.id),
        )
        await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/referral")
async def riscatta(payload: Invito, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    """Riscatta un invito: crediti a chi invita e a chi è invitato.

    Una volta sola per account, e mai col proprio codice.
    """
    if user.referred_by is not None:
        raise HTTPException(status_code=409, detail="Hai già usato un invito")
    codice = payload.codice.strip().upper()
    if codice == (user.referral_code or ""):
        raise HTTPException(status_code=400, detail="Non puoi invitare te stesso")
    invitante = (await session.execute(
        select(User).where(User.referral_code == codice, User.deleted_at.is_(None))
    )).scalar_one_or_none()
    if invitante is None:
        raise HTTPException(status_code=404, detail="Codice invito sconosciuto")

    quanti = get_settings().crediti_invito
    registro = RegistroCrediti(session)
    user.referred_by = invitante.id
    await registro.accredita(user.id, quanti, reason="omaggio", note=f"invito {codice}")
    await registro.accredita(invitante.id, quanti, reason="omaggio", note=f"invito riscattato da {user.id}")
    await AuditRepository(session).record(
        action="referral.redeem", actor_id=user.id, target_type="user", target_id=str(invitante.id),
    )
    await session.commit()
    return {"crediti": quanti, "saldo": await registro.saldo(user.id)}


@router.get("/daily-card")
async def carta_del_giorno(user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    """La carta del giorno: gratuita, un Arcano maggiore, la stessa per tutto
    il giorno.

    Non serve un modello: il testo è il significato del mazzo nella sua
    lettura del giorno. È un rito quotidiano, e deve costare zero a chi lo
    offre per poter essere di tutti.
    """
    oggi = _oggi()
    conoscenza = get_conoscenza()
    riga = (await session.execute(
        select(DailyCard).where(DailyCard.user_id == user.id, DailyCard.giorno == oggi)
    )).scalar_one_or_none()
    if riga is None:
        # Deterministica per utente e giorno: se due richieste arrivano
        # insieme, entrambe scelgono la stessa carta.
        seme = hashlib.sha256(f"{user.id}:{oggi.isoformat()}".encode()).digest()
        maggiori = [i for i in conoscenza.ordine if conoscenza.carte[i]["arcano"] == "maggiore"]
        card_id = maggiori[seme[0] % len(maggiori)]
        rovescio = seme[1] % 4 == 0
        carta = conoscenza.carta(card_id)
        riga = DailyCard(
            user_id=user.id, giorno=oggi, card_id=card_id, rovescio=rovescio,
            testo=carta["rovescio"] if rovescio else carta["dritto"], created_at=utcnow(),
        )
        session.add(riga)
        try:
            await session.commit()
        except Exception:  # noqa: BLE001 - corsa sull'unicità: rileggiamo
            await session.rollback()
            riga = (await session.execute(
                select(DailyCard).where(DailyCard.user_id == user.id, DailyCard.giorno == oggi)
            )).scalar_one()

    giorni = set((await session.execute(
        select(DailyCard.giorno).where(
            DailyCard.user_id == user.id, DailyCard.giorno >= oggi - timedelta(days=366),
        )
    )).scalars())
    serie = 0
    giorno = oggi
    while giorno in giorni:
        serie += 1
        giorno -= timedelta(days=1)

    return {
        "giorno": oggi.isoformat(),
        "carta": conoscenza.carta_pubblica(riga.card_id, completa=True),
        "rovescio": riga.rovescio,
        "testo": riga.testo,
        "serie": serie,
    }


@router.put("/avatar")
async def carica_avatar(request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    """La tua immagine personale (avatar): compare accanto ai tuoi commenti. Si ritaglia al centro
    in un quadrato di 256 px e si riscrive in WebP; quella precedente si cancella."""
    if not request.headers.get("content-type", "").startswith("image/"):
        raise HTTPException(status_code=415, detail="Serve un'immagine")
    if int(request.headers.get("content-length") or 0) > regole_blog.MAX_CARICO_IMMAGINE:
        raise HTTPException(status_code=413, detail="Immagine troppo grande")
    try:
        webp, larghezza, altezza = await asyncio.to_thread(regole_blog.prepara_avatar, await request.body())
    except regole_blog.ImmagineNonValida as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    precedente = user.avatar_id
    nuova = MediaImage(uso="avatar", webp=webp, larghezza=larghezza, altezza=altezza, owner_id=user.id)
    session.add(nuova)
    await session.flush()
    user.avatar_id = nuova.id
    await session.flush()
    if precedente is not None:
        vecchia = await session.get(MediaImage, precedente)
        if vecchia is not None and vecchia.uso == "avatar" and vecchia.owner_id == user.id:
            await session.delete(vecchia)
    await session.commit()
    return {"avatar": url_immagine(nuova.id)}


@router.delete("/avatar", status_code=status.HTTP_204_NO_CONTENT)
async def togli_avatar(user: CurrentUser, session: DbSession) -> Response:
    if user.avatar_id is not None:
        immagine = await session.get(MediaImage, user.avatar_id)
        user.avatar_id = None
        await session.flush()
        if immagine is not None and immagine.uso == "avatar" and immagine.owner_id == user.id:
            await session.delete(immagine)
        await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
