"""Il postino delle notifiche (v9, Fase 5): un messaggio a una persona, su tutti i suoi dispositivi attivi.

`Postino.manda()` fa, per una persona:

1. prende i suoi dispositivi attivi sui canali scelti e **disponibili** (FCM solo con il service account di Firebase
   in console, Web Push solo con le chiavi VAPID): senza dispositivi raggiungibili non scrive niente;
2. **prenota l'invio** in `invii_notifica` con `INSERT … ON CONFLICT DO NOTHING`: gli indici unici (tipo + persona +
   giorno locale per le automatiche, campagna + persona per le campagne) fanno sì che un secondo giro, o una
   seconda replica, trovi la prenotazione e non mandi di nuovo;
3. manda, nella lingua del dispositivo (o della persona), con il limite di velocità della console;
4. registra l'esito: un dispositivo che il servizio dichiara sparito (404/410, `UNREGISTERED`) si disattiva subito,
   uno che sbaglia dieci volte di fila anche.

Le ore di silenzio, le preferenze e i tetti delle promozioni li guarda chi chiama (`automatiche.py`, `campagne.py`):
dipendono dall'ora locale e dal tipo di messaggio. `preferenze_di()` li dà già risolti (preferenze della persona,
altrimenti i predefiniti della console).

Il limite di velocità: al più `limite_al_minuto` invii al minuto, a lotti di un secondo. Le prove sostituiscono
`ATTESA` per non aspettare.
"""
from __future__ import annotations

import asyncio
import logging
import time as orologio
import uuid
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Any, Awaitable, Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.base import utcnow
from ..domain.models import User
from ..domain.notifiche_models import (
    CANALI, CampagnaNotifica, ConfigNotifiche, DispositivoNotifica, InvioNotifica, PreferenzeNotifica,
)
from ..settings import get_settings
from . import config as conf
from . import fcm, webpush

logger = logging.getLogger(__name__)

ATTESA: Callable[[float], Awaitable[None]] = asyncio.sleep
#: Dopo quanti errori di fila un dispositivo smette di essere usato.
ERRORI_MASSIMI = 10

# Le parole dell'azione «non mandarmi più promozioni» delle notifiche Web Push, nelle sei lingue.
DISISCRIVI = {
    "en": "No more promotions", "it": "Niente più promozioni", "hu": "Ne kérek több ajánlatot",
    "ru": "Больше без акций", "uk": "Більше без акцій", "es": "No más promociones",
}


def lingua_di(codice: Optional[str]) -> str:
    c = ((codice or "en").split("-")[0].split("_")[0]).lower()
    return c if c in conf.LINGUE else "en"


def scegli_testo(testi: Mapping[str, Mapping[str, str]], lingua: str, base: str = "en",
                 valori: Optional[Mapping[str, Any]] = None) -> Tuple[str, str]:
    """Titolo e corpo nella lingua di chi riceve, poi in inglese, poi nella lingua base, poi il primo che c'è; con i
    segnaposto `{nome}` riempiti."""
    scelto: Mapping[str, str] = {}
    for codice in (lingua, "en", base, *testi.keys()):
        t = testi.get(codice) or {}
        if (t.get("titolo") or "").strip() and (t.get("corpo") or "").strip():
            scelto = t
            break

    def riempi(s: str) -> str:
        for nome, valore in (valori or {}).items():
            s = s.replace("{" + nome + "}", str(valore))
        return s

    return riempi(str(scelto.get("titolo", "")))[:120], riempi(str(scelto.get("corpo", "")))[:400]


@dataclass(frozen=True)
class Preferenze:
    carta_giorno: bool
    ora_carta: time
    silenzio_dal: Optional[time]
    silenzio_al: Optional[time]
    promemoria: bool
    tetto_promozioni: int


def preferenze_effettive(riga: Optional[PreferenzeNotifica], cfg: ConfigNotifiche) -> Preferenze:
    if riga is None:
        return Preferenze(True, cfg.ora_carta, cfg.silenzio_dal, cfg.silenzio_al, True, cfg.tetto_promozioni_settimana)
    return Preferenze(
        riga.carta_giorno, riga.ora_carta, riga.silenzio_dal, riga.silenzio_al, riga.promemoria,
        # La persona può abbassare il tetto, non alzarlo sopra quello della console.
        min(riga.tetto_promozioni_settimana, cfg.tetto_promozioni_settimana),
    )


async def preferenze_di(session: AsyncSession, user_ids: Iterable[int], cfg: ConfigNotifiche) -> Dict[int, Preferenze]:
    ids = list(user_ids)
    righe = {}
    if ids:
        righe = {p.user_id: p for p in (await session.execute(
            select(PreferenzeNotifica).where(PreferenzeNotifica.user_id.in_(ids))
        )).scalars()}
    return {i: preferenze_effettive(righe.get(i), cfg) for i in ids}


async def promozioni_recenti(session: AsyncSession, user_id: int, adesso: datetime) -> int:
    """Quante promozioni la persona ha ricevuto negli ultimi sette giorni (per il tetto)."""
    return (await session.execute(
        select(func.count()).select_from(InvioNotifica).join(CampagnaNotifica, CampagnaNotifica.id == InvioNotifica.campagna_id)
        .where(InvioNotifica.user_id == user_id, InvioNotifica.tipo == "campagna", CampagnaNotifica.tipo == "promozione",
               InvioNotifica.consegnati > 0, InvioNotifica.created_at >= adesso - timedelta(days=7))
    )).scalar_one()


@dataclass
class Risultato:
    invio: Optional[InvioNotifica]
    #: `inviato`, `errore`, `token_invalido` (come l'invio), `nessun_dispositivo`, `gia_inviato`.
    esito: str
    dettagli: List[Dict[str, Any]]


class Postino:
    """Un giro di invii: le credenziali si leggono una volta, il limite di velocità vale per tutto il giro."""

    def __init__(self, session: AsyncSession, cfg: ConfigNotifiche, *, cred: Any, vapid_privata: str,
                 chiave: bytes, adesso: Optional[datetime] = None) -> None:
        self.session = session
        self.cfg = cfg
        self.cred = cred
        self.vapid_privata = vapid_privata
        self.chiave = chiave
        self.adesso = adesso or utcnow()
        impostazioni = get_settings()
        self.url_api = impostazioni.api_public_url.rstrip("/")
        self.url_sito = impostazioni.web_public_url.rstrip("/")
        self._lotto = max(1, cfg.limite_al_minuto // 60)
        self._nel_lotto = 0
        self._inizio_lotto = orologio.monotonic()
        self.inviati = 0

    @classmethod
    async def prepara(cls, session: AsyncSession, *, adesso: Optional[datetime] = None) -> "Postino":
        cfg = await conf.config(session)
        privata, _ = await conf.chiavi_vapid(session)
        return cls(session, cfg, cred=conf.credenziali_firebase(cfg), vapid_privata=privata,
                   chiave=await conf.chiave_firma(session), adesso=adesso)

    @property
    def canali_disponibili(self) -> Tuple[str, ...]:
        return tuple(c for c in CANALI if (c == "fcm" and self.cred is not None) or (c == "webpush" and self.vapid_privata))

    async def _rallenta(self) -> None:
        self._nel_lotto += 1
        if self._nel_lotto < self._lotto:
            return
        trascorso = orologio.monotonic() - self._inizio_lotto
        if trascorso < 1.0:
            await ATTESA(1.0 - trascorso)
        self._nel_lotto = 0
        self._inizio_lotto = orologio.monotonic()

    async def dispositivi(self, user_id: int, canali: Sequence[str] = CANALI) -> List[DispositivoNotifica]:
        ammessi = [c for c in canali if c in self.canali_disponibili]
        if not ammessi:
            return []
        return list((await self.session.execute(
            select(DispositivoNotifica).where(
                DispositivoNotifica.user_id == user_id, DispositivoNotifica.attivo.is_(True),
                DispositivoNotifica.canale.in_(ammessi),
            ).order_by(DispositivoNotifica.id)
        )).scalars())

    def link_disiscrizione(self, user_id: int) -> str:
        return f"{self.url_api}/notifiche/disiscrivi?t={conf.token_disiscrizione(self.chiave, user_id, 'promozioni')}"

    async def manda(
        self, utente: User, tipo: str, testi: Mapping[str, Mapping[str, str]], link: str, *,
        campagna: Optional[CampagnaNotifica] = None, giorno: Optional[date] = None,
        valori: Optional[Mapping[str, Any]] = None, immagine: Optional[str] = None,
        canali: Sequence[str] = CANALI, promozione: bool = False, base: str = "en",
    ) -> Risultato:
        dispositivi = await self.dispositivi(utente.id, canali)
        if not dispositivi:
            return Risultato(None, "nessun_dispositivo", [])
        nuovo = uuid.uuid4()
        prenotato = (await self.session.execute(
            insert(InvioNotifica).values(
                id=nuovo, tipo=tipo, campagna_id=campagna.id if campagna else None, user_id=utente.id,
                giorno=giorno, stato="errore", dispositivi=len(dispositivi), created_at=self.adesso,
            ).on_conflict_do_nothing().returning(InvioNotifica.id)
        )).scalar_one_or_none()
        if prenotato is None:
            return Risultato(None, "gia_inviato", [])
        invio = await self.session.get(InvioNotifica, nuovo)
        assert invio is not None

        dettagli: List[Dict[str, Any]] = []
        firma = conf.firma(self.chiave, f"aperta:{nuovo}")
        for d in dispositivi:
            lingua = lingua_di(d.lingua or utente.locale)
            titolo, corpo = scegli_testo(testi, lingua, base, valori)
            await self._rallenta()
            if d.canale == "fcm":
                esito = await fcm.invia(self.cred, fcm.messaggio_fcm(
                    d.token, titolo, corpo, {"link": link, "invio": str(nuovo), "firma": firma, "tipo": tipo},
                    immagine=immagine, canale_android="promozioni" if promozione else "servizio",
                ))
            else:
                dati: Dict[str, Any] = {
                    "titolo": titolo, "corpo": corpo, "link": link, "immagine": immagine, "tag": tipo,
                    "invio": str(nuovo), "firma": firma, "api": self.url_api,
                }
                if promozione:
                    dati["azioni"] = [{"azione": "disiscrivi", "titolo": DISISCRIVI[lingua],
                                       "link": self.link_disiscrizione(utente.id)}]
                esito = await webpush.invia(self.vapid_privata, self.cfg.vapid_contatto, d.endpoint or "",
                                            d.p256dh or "", d.auth or "", dati)
            self.inviati += 1
            self._registra_dispositivo(d, esito)
            dettagli.append({"dispositivo": d.id, "canale": d.canale, "piattaforma": d.piattaforma,
                             "esito": esito.stato, "messaggio": esito.messaggio})

        consegnati = [x for x in dettagli if x["esito"] == "ok"]
        invio.consegnati = len(consegnati)
        if consegnati:
            invio.stato = "inviato"
            invio.dispositivo_id = consegnati[0]["dispositivo"]
        elif all(x["esito"] == "token_invalido" for x in dettagli):
            invio.stato = "token_invalido"
        else:
            invio.stato = "errore"
        errori = [x["messaggio"] for x in dettagli if x["esito"] != "ok" and x["messaggio"]]
        invio.errore = ("; ".join(errori))[:300] or None
        await self.session.flush()
        return Risultato(invio, invio.stato, dettagli)

    def _registra_dispositivo(self, d: DispositivoNotifica, esito: fcm.Esito) -> None:
        if esito.stato == "ok":
            d.errori = 0
            return
        d.ultimo_errore = esito.messaggio[:300] or esito.stato
        if esito.stato == "token_invalido":
            d.attivo = False
            d.disattivato_il = self.adesso
            return
        d.errori += 1
        if d.errori >= ERRORI_MASSIMI:
            logger.warning("Dispositivo %s disattivato dopo %s errori di fila: %s", d.id, d.errori, d.ultimo_errore)
            d.attivo = False
            d.disattivato_il = self.adesso


async def segna_aperta(session: AsyncSession, invio_id: uuid.UUID, *, adesso: Optional[datetime] = None) -> bool:
    """Il tocco sulla notifica: la prima volta conta (stato `aperto`, e un'apertura in più alla campagna)."""
    invio = await session.get(InvioNotifica, invio_id)
    if invio is None:
        return False
    if invio.aperto_il is None:
        invio.aperto_il = adesso or utcnow()
        invio.stato = "aperto"
        if invio.campagna_id is not None and invio.tipo == "campagna":
            campagna = await session.get(CampagnaNotifica, invio.campagna_id)
            if campagna is not None:
                campagna.aperti += 1
        await session.flush()
    return True
