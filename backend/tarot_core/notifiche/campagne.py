"""Le campagne della console (v9, Fase 5): un messaggio a un segmento, subito o a un'ora stabilita.

La vita di una campagna: `bozza` (si scrive, si traduce, si conta, si prova con «invia a me») → `programmata` (con
`programmata_il`; «invia adesso» è una programmazione all'istante) → `in_invio` (il giro dei 15 minuti la prende) →
`inviata`. Fino a quando non è `inviata` la si può `annullare`.

**L'invio.** A ogni giro si prendono i destinatari del segmento (`segmenti.destinatari`, con il consenso `marketing`
per le promozioni) che non hanno ancora una riga per questa campagna, e per ciascuno:

- nelle ore di silenzio della persona (se la campagna le rispetta) si rimanda al giro successivo;
- per una promozione, oltre il tetto settimanale della persona (e della console) si salta;
- altrimenti si manda (`Postino.manda`: una riga per persona, unica per campagna).

Quando non resta nessuno da rimandare la campagna è `inviata`; dopo 48 ore lo è comunque (chi è entrato nel
segmento dopo non la riceve). I contatori si aggiornano a ogni giro.
"""
from __future__ import annotations

import logging
from collections import Counter
from datetime import timedelta
from typing import Any, Dict

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.models import User
from ..domain.notifiche_models import CampagnaNotifica, InvioNotifica
from . import config as conf
from .invio import Postino, preferenze_di, promozioni_recenti
from .segmenti import Filtro, destinatari

logger = logging.getLogger(__name__)

DURATA_MASSIMA = timedelta(hours=48)


async def aggiorna_contatori(session: AsyncSession, campagna: CampagnaNotifica) -> None:
    riga = (await session.execute(
        select(
            func.count(),
            func.count().filter(InvioNotifica.consegnati > 0),
            func.count().filter(InvioNotifica.stato.in_(("errore", "token_invalido"))),
            func.count().filter(InvioNotifica.aperto_il.is_not(None)),
        ).where(InvioNotifica.campagna_id == campagna.id, InvioNotifica.tipo == "campagna")
    )).one()
    campagna.destinatari, campagna.inviati, campagna.errori, campagna.aperti = (int(x) for x in riga)


async def esegui(session: AsyncSession, campagna: CampagnaNotifica, postino: Postino) -> Dict[str, int]:
    """Un giro di una campagna `in_invio`. Fa il commit a ogni persona."""
    adesso = postino.adesso
    conti: Counter = Counter()
    promozione = campagna.tipo == "promozione"
    canali = [c for c in (campagna.canali or []) if c in postino.canali_disponibili]
    gia = select(InvioNotifica.user_id).where(InvioNotifica.campagna_id == campagna.id, InvioNotifica.tipo == "campagna")
    ids = []
    if canali:
        sq = destinatari(Filtro.model_validate(campagna.filtro or {}), campagna.tipo, canali, adesso=adesso).subquery()
        ids = list((await session.execute(select(sq.c.id).where(sq.c.id.not_in(gia)).order_by(sq.c.id))).scalars())
    else:
        conti["nessun_canale"] += 1
    attesa = 0
    for inizio in range(0, len(ids), 200):
        blocco = ids[inizio:inizio + 200]
        preferenze = await preferenze_di(session, blocco, postino.cfg)
        utenti = {u.id: u for u in (await session.execute(select(User).where(User.id.in_(blocco)))).scalars()}
        for user_id in blocco:
            utente, pref = utenti[user_id], preferenze[user_id]
            if campagna.rispetta_silenzio and conf.in_silenzio(
                adesso.astimezone(conf.fuso_di(utente)), pref.silenzio_dal, pref.silenzio_al,
            ):
                attesa += 1
                continue
            if promozione and await promozioni_recenti(session, user_id, adesso) >= pref.tetto_promozioni:
                conti["saltati_tetto"] += 1
                continue
            try:
                r = await postino.manda(
                    utente, "campagna", campagna.testi or {}, campagna.deep_link, campagna=campagna,
                    immagine=campagna.immagine, canali=canali, promozione=promozione, base=campagna.lingua_base,
                )
                conti[r.esito] += 1
                await session.commit()
            except Exception:  # noqa: BLE001 — una persona non deve fermare la campagna
                await session.rollback()
                logger.exception("Campagna %s: errore per l'utente %s", campagna.id, user_id)
                conti["errori_giro"] += 1
    conti["in_attesa"] = attesa
    campagna.saltati = conti["saltati_tetto"]
    await aggiorna_contatori(session, campagna)
    if attesa == 0 or (campagna.iniziata_il and adesso - campagna.iniziata_il >= DURATA_MASSIMA):
        campagna.stato = "inviata"
        campagna.finita_il = adesso
    await session.commit()
    return dict(conti)


async def giro(session: AsyncSession, postino: Postino) -> Dict[str, int]:
    """Le campagne arrivate all'ora (→ `in_invio`) e quelle già in invio."""
    adesso = postino.adesso
    conti: Counter = Counter()
    pronte = (await session.execute(
        select(CampagnaNotifica).where(CampagnaNotifica.stato == "programmata", CampagnaNotifica.programmata_il <= adesso)
        .with_for_update(skip_locked=True)
    )).scalars().all()
    for c in pronte:
        c.stato = "in_invio"
        c.iniziata_il = adesso
    await session.commit()
    in_invio = (await session.execute(
        select(CampagnaNotifica).where(CampagnaNotifica.stato == "in_invio").order_by(CampagnaNotifica.id)
    )).scalars().all()
    for c in in_invio:
        for chiave, n in (await esegui(session, c, postino)).items():
            conti[f"campagna:{chiave}"] += n
        conti["campagne"] += 1
    return dict(conti)


async def invia_a_me(session: AsyncSession, campagna: CampagnaNotifica, utente: User) -> Dict[str, Any]:
    """«Invia a me» dalla console: la campagna così com'è, sui dispositivi dell'amministratore, senza silenzio, tetti
    né consenso (è una prova). Non conta nei numeri della campagna. Non fa il commit."""
    postino = await Postino.prepara(session)
    if not postino.canali_disponibili:
        return {"esito": "nessun_canale", "dettagli": [],
                "messaggio": "Nessun canale pronto: carica il service account di Firebase o lascia generare le chiavi VAPID."}
    canali = [c for c in (campagna.canali or []) if c in postino.canali_disponibili] or list(postino.canali_disponibili)
    r = await postino.manda(
        utente, "prova", campagna.testi or {}, campagna.deep_link, campagna=campagna, immagine=campagna.immagine,
        canali=canali, promozione=campagna.tipo == "promozione", base=campagna.lingua_base,
    )
    messaggi = {
        "nessun_dispositivo": "Nessun tuo dispositivo registrato su questi canali: apri il sito con questo account e "
                              "attiva le notifiche dal profilo (o dall'app), poi riprova.",
        "inviato": "Inviata: controlla il telefono o il browser.",
        "token_invalido": "I tuoi dispositivi non sono più validi (permesso tolto?): attiva di nuovo le notifiche.",
        "errore": "Non è partita: guarda il dettaglio.",
    }
    return {"esito": r.esito, "dettagli": r.dettagli, "messaggio": messaggi.get(r.esito, r.esito)}
