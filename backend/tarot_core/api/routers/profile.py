"""Il profilo di chi consulta: data di nascita, carte personali, inviti,
carta del giorno."""
from __future__ import annotations

import hashlib
from datetime import date, datetime, timedelta
from typing import Any, Dict, Optional
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from ...auth.dependencies import CurrentUser, DbSession
from ...billing.credits import RegistroCrediti
from ...domain.base import utcnow
from ...domain.models import DailyCard, User
from ...domain.repositories import AuditRepository, nuovo_codice_invito
from ...settings import get_settings
from ...tarot.numerologia import carta_dell_anima, carta_dell_anno
from ..deps import get_conoscenza

router = APIRouter(prefix="/me", tags=["profilo"])

#: Il giorno della carta del giorno è quello italiano: «oggi» per chi la
#: apre, non per il server.
FUSO = ZoneInfo("Europe/Rome")


class ModificaProfilo(BaseModel):
    birth_date: Optional[date] = None
    locale: Optional[str] = Field(default=None, pattern="^(it|en)$")


class Invito(BaseModel):
    codice: str = Field(min_length=4, max_length=16)


def _oggi() -> date:
    return datetime.now(FUSO).date()


def _profilo_json(user: User) -> Dict[str, Any]:
    conoscenza = get_conoscenza()
    dati: Dict[str, Any] = {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "locale": user.locale,
        "birth_date": user.birth_date.isoformat() if user.birth_date else None,
        "referral_code": user.referral_code,
        "invitato": user.referred_by is not None,
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
    return _profilo_json(user)


@router.patch("/profile")
async def modifica(payload: ModificaProfilo, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    if payload.birth_date is not None:
        if payload.birth_date > _oggi() or payload.birth_date.year < 1900:
            raise HTTPException(status_code=400, detail="Data di nascita non valida")
        user.birth_date = payload.birth_date
    if payload.locale:
        user.locale = payload.locale
    await session.commit()
    return _profilo_json(user)


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
