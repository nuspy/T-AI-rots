"""I segmenti delle campagne (v9, Fase 5): i filtri della console diventano una query SQL sugli utenti.

Si può filtrare su lingua, paese, fascia d'età, primo canale di arrivo, attività recente, giorni dall'ultima lettura,
acquisti fatti, piano e abbonamento a pagamento, prova in corso, saldo dei crediti, piattaforma dei dispositivi.

**Le regole che non si scavalcano.**

- Le **promozioni** vanno solo a chi ha il consenso `marketing` **accettato** (un consenso mai dato vale come
  rifiutato, art. 7 GDPR): la condizione è dentro la query, non a carico di chi scrive la campagna.
- Mai i dati dell'art. 9 (la casella «persona trans», i ricordi sulla salute) e **mai il genere** (decisione del
  3/10): non esistono come filtro, e un filtro sconosciuto è un errore (`extra="forbid"`), non un campo ignorato.
- Mai chi ha chiuso l'account o ne ha chiesto la cancellazione.

`destinatari()` dà la query degli id; `conta()` l'anteprima della console (quanti corrispondono, quanti hanno un
dispositivo attivo su un canale scelto, e per le promozioni quanti mancano per il consenso).
"""
from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict, List, Optional, Sequence

from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import and_, exists, func, literal, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..analytics.catalogo import ND, fascia_eta
from ..domain.analytics_models import TABELLE
from ..domain.base import utcnow
from ..domain.billing_models import STATI_VIVI, CreditEntry, PaymentCheckout, Plan, Subscription
from ..domain.consent_models import UserConsent
from ..domain.models import DailyCard, Reading, User
from ..domain.notifiche_models import CANALI, PIATTAFORME, DispositivoNotifica
from ..domain.ordini_models import Ordine

FASCE_ETA = ("<18", "18-24", "25-34", "35-44", "45-54", "55-64", "65+", "nd")


class Filtro(BaseModel):
    """Tutte le condizioni sono in «e»; dentro una lista, in «o». Un campo vuoto non filtra."""

    model_config = ConfigDict(extra="forbid")

    lingue: List[str] = Field(default_factory=list, max_length=20)
    #: ISO a due lettere, dalla posizione attuale del profilo.
    paesi: List[str] = Field(default_factory=list, max_length=60)
    fasce_eta: List[str] = Field(default_factory=list, max_length=len(FASCE_ETA))
    #: Il canale del primo contatto (analytics): `organico`, `social`, `diretto`… `nd` per chi non ne ha uno.
    primi_canali: List[str] = Field(default_factory=list, max_length=20)
    #: Entrato, ha letto o ha aperto la carta del giorno negli ultimi N giorni.
    attivi_negli_ultimi_giorni: Optional[int] = Field(default=None, ge=1, le=3650)
    #: Nessuna attività da almeno N giorni (per riattivare).
    inattivi_da_giorni: Optional[int] = Field(default=None, ge=1, le=3650)
    #: L'ultima lettura: almeno N giorni fa (o mai), al massimo N giorni fa.
    ultima_lettura_almeno_giorni: Optional[int] = Field(default=None, ge=0, le=3650)
    ultima_lettura_al_massimo_giorni: Optional[int] = Field(default=None, ge=0, le=3650)
    #: Vero: ha pagato almeno una volta (crediti, abbonamento o ordine); falso: mai.
    ha_acquistato: Optional[bool] = None
    #: Gli slug dei piani (abbonamento vivo su uno di questi).
    piani: List[str] = Field(default_factory=list, max_length=30)
    #: Vero: un abbonamento a pagamento vivo (anche in prova); falso: nessuno.
    abbonamento_attivo: Optional[bool] = None
    in_prova: Optional[bool] = None
    crediti_min: Optional[int] = Field(default=None, ge=0, le=1_000_000)
    crediti_max: Optional[int] = Field(default=None, ge=0, le=1_000_000)
    #: Le piattaforme dei dispositivi attivi: `android`, `ios`, `web`.
    piattaforme: List[str] = Field(default_factory=list, max_length=3)

    @field_validator("lingue")
    @classmethod
    def _lingue(cls, v: List[str]) -> List[str]:
        return sorted({x.strip().lower()[:5] for x in v if x.strip()})

    @field_validator("paesi")
    @classmethod
    def _paesi(cls, v: List[str]) -> List[str]:
        return sorted({x.strip().upper()[:2] for x in v if x.strip()})

    @field_validator("fasce_eta")
    @classmethod
    def _fasce(cls, v: List[str]) -> List[str]:
        sconosciute = [x for x in v if x not in FASCE_ETA]
        if sconosciute:
            raise ValueError(f"fasce d'età sconosciute: {', '.join(sconosciute)}")
        return v

    @field_validator("piattaforme")
    @classmethod
    def _piattaforme(cls, v: List[str]) -> List[str]:
        if any(p not in PIATTAFORME for p in v):
            raise ValueError("piattaforme ammesse: android, ios, web")
        return v


def _dispositivo_attivo(canali: Sequence[str], piattaforme: Sequence[str] = ()):
    condizioni = [DispositivoNotifica.user_id == User.id, DispositivoNotifica.attivo.is_(True),
                  DispositivoNotifica.canale.in_(list(canali))]
    if piattaforme:
        condizioni.append(DispositivoNotifica.piattaforma.in_(list(piattaforme)))
    return exists().where(and_(*condizioni))


def _marketing():
    return exists().where(
        UserConsent.user_id == User.id, UserConsent.tipo == "marketing", UserConsent.valore == "accettato",
    )


def _attivo_dal(da):
    U = TABELLE.utenti
    return or_(
        exists().where(U.c.utente_id == User.id, U.c.ultimo_accesso >= da),
        exists().where(Reading.owner_id == User.id, Reading.created_at >= da),
        exists().where(DailyCard.user_id == User.id, DailyCard.created_at >= da),
        exists().where(DispositivoNotifica.user_id == User.id, DispositivoNotifica.ultimo_visto >= da),
    )


def _abbonamento_vivo(*condizioni):
    return exists().where(
        Subscription.user_id == User.id, Subscription.status.in_(STATI_VIVI), *condizioni,
    )


def condizioni(filtro: Filtro, *, adesso=None) -> List[Any]:
    """Le condizioni SQL del filtro, su `User`. Senza consenso né dispositivi: quelli li aggiunge `destinatari`."""
    adesso = adesso or utcnow()
    c: List[Any] = [User.deleted_at.is_(None), User.cancellazione_richiesta_il.is_(None)]
    if filtro.lingue:
        lingua = func.lower(func.split_part(func.replace(User.locale, "_", "-"), "-", 1))
        c.append(lingua.in_(filtro.lingue))
    if filtro.paesi:
        c.append(func.upper(User.posizione_paese).in_(filtro.paesi))
    if filtro.fasce_eta:
        fasce = [ND if f == "nd" else f for f in filtro.fasce_eta]
        c.append(fascia_eta(User.birth_date).in_(fasce))
    if filtro.primi_canali:
        U = TABELLE.utenti
        primo = select(U.c.primo_canale).where(U.c.utente_id == User.id).scalar_subquery()
        canali = [ND if x == "nd" else x for x in filtro.primi_canali]
        c.append(func.coalesce(primo, literal(ND)).in_(canali))
    if filtro.attivi_negli_ultimi_giorni:
        c.append(_attivo_dal(adesso - timedelta(days=filtro.attivi_negli_ultimi_giorni)))
    if filtro.inattivi_da_giorni:
        c.append(~_attivo_dal(adesso - timedelta(days=filtro.inattivi_da_giorni)))
    ultima = select(func.max(Reading.created_at)).where(Reading.owner_id == User.id).scalar_subquery()
    if filtro.ultima_lettura_almeno_giorni is not None:
        c.append(or_(ultima.is_(None), ultima <= adesso - timedelta(days=filtro.ultima_lettura_almeno_giorni)))
    if filtro.ultima_lettura_al_massimo_giorni is not None:
        c.append(ultima >= adesso - timedelta(days=filtro.ultima_lettura_al_massimo_giorni))
    if filtro.ha_acquistato is not None:
        acquisto = or_(
            exists().where(PaymentCheckout.user_id == User.id, PaymentCheckout.status == "pagato"),
            exists().where(Ordine.user_id == User.id, Ordine.status == "pagato"),
        )
        c.append(acquisto if filtro.ha_acquistato else ~acquisto)
    if filtro.piani:
        c.append(_abbonamento_vivo(Subscription.plan_id.in_(select(Plan.id).where(Plan.slug.in_(filtro.piani)))))
    if filtro.abbonamento_attivo is not None:
        pagamento = _abbonamento_vivo(Subscription.plan_id.in_(
            select(Plan.id).where(or_(Plan.price_monthly > 0, Plan.price_yearly > 0))
        ))
        c.append(pagamento if filtro.abbonamento_attivo else ~pagamento)
    if filtro.in_prova is not None:
        prova = exists().where(Subscription.user_id == User.id, Subscription.status == "in_prova")
        c.append(prova if filtro.in_prova else ~prova)
    if filtro.crediti_min is not None or filtro.crediti_max is not None:
        saldo = select(func.coalesce(func.sum(CreditEntry.delta), 0)).where(
            CreditEntry.user_id == User.id,
            or_(CreditEntry.expires_at.is_(None), CreditEntry.expires_at > adesso),
        ).scalar_subquery()
        if filtro.crediti_min is not None:
            c.append(saldo >= filtro.crediti_min)
        if filtro.crediti_max is not None:
            c.append(saldo <= filtro.crediti_max)
    if filtro.piattaforme:
        c.append(_dispositivo_attivo(CANALI, filtro.piattaforme))
    return c


def destinatari(filtro: Filtro, tipo: str, canali: Sequence[str] = CANALI, *, adesso=None):
    """La query degli id di chi riceve: il filtro, il consenso per le promozioni, un dispositivo attivo sui canali."""
    c = condizioni(filtro, adesso=adesso)
    if tipo == "promozione":
        c.append(_marketing())
    c.append(_dispositivo_attivo(canali, filtro.piattaforme))
    return select(User.id).where(*c).order_by(User.id)


async def conta(session: AsyncSession, filtro: Filtro, tipo: str, canali: Sequence[str] = CANALI) -> Dict[str, Any]:
    """L'anteprima della console: quanti corrispondono al filtro, quanti si raggiungono davvero, e perché no."""
    base = condizioni(filtro)
    corrispondono = (await session.execute(select(func.count()).select_from(User).where(*base))).scalar_one()
    con_consenso = corrispondono
    if tipo == "promozione":
        con_consenso = (await session.execute(
            select(func.count()).select_from(User).where(*base, _marketing())
        )).scalar_one()
    raggiungibili = (await session.execute(
        select(func.count()).select_from(destinatari(filtro, tipo, canali).subquery())
    )).scalar_one()
    sottoquery = destinatari(filtro, tipo, canali).subquery()
    per_piattaforma = dict((await session.execute(
        select(DispositivoNotifica.piattaforma, func.count(func.distinct(DispositivoNotifica.user_id)))
        .where(DispositivoNotifica.user_id.in_(select(sottoquery.c.id)), DispositivoNotifica.attivo.is_(True),
               DispositivoNotifica.canale.in_(list(canali)))
        .group_by(DispositivoNotifica.piattaforma)
    )).all())
    return {
        "corrispondono": corrispondono,
        "senza_consenso": corrispondono - con_consenso,
        "senza_dispositivo": con_consenso - raggiungibili,
        "destinatari": raggiungibili,
        "per_piattaforma": {p: int(per_piattaforma.get(p, 0)) for p in PIATTAFORME},
    }
