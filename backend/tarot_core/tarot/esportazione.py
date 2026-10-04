"""L'esportazione dei propri dati (GDPR art. 15 e 20): un archivio ZIP di file JSON.

`GET /me/esportazione` (`api/routers/privacy.py`) lo costruisce in memoria e lo consegna subito: niente file
temporanei sul server, niente link da tenere vivi. Una volta al giorno per persona (`LIMITE_ORE`): l'archivio tocca
tutte le tabelle dell'account, e chiederlo a raffica non serve a nessuno.

**Cosa c'è.** Un file per argomento, con i nomi dei campi come sono nel database (stabili, e già leggibili in
italiano), le date in ISO 8601 UTC:

- `profilo.json` — la scheda (anagrafica, genere, posizione, scelte), il partner ricordato, l'età confermata;
- `letture.json` — ogni lettura con il quesito, il colloquio dell'intervista, le carte, le interpretazioni, il
  responso, il diario, la condivisione;
- `memorie.json` — ciò che il lettore ricorda, comprese le versioni sostituite (senza il vettore numerico usato per
  la ricerca: è un calcolo del testo, non un'informazione in più);
- `stato_memoria.json` — lo stato sintetico della memoria: le voci con categoria, campo, testo e date;
- `chat.json` — la chat con l'oracolo;
- `consensi.json` — le scelte attuali e tutto lo storico (IP troncati, mai interi);
- `crediti.json` — il registro dei crediti;
- `abbonamenti.json` — abbonamenti, pagamenti avviati e coupon usati;
- `ordini.json` — gli ordini con le righe, e gli indirizzi salvati;
- `dati_social.json` — cosa è arrivato dai social, da quale e quando;
- `altro.json` — carte del giorno, mazzi sbloccati, voti e temi suggeriti, iscrizioni arrivate dai tuoi link.

Non ci sono le statistiche di navigazione (sono legate all'account solo come conteggi, e l'opposizione dal profilo
le scollega), né il registro interno (`audit_log`), che documenta il trattamento e non è un dato fornito dalla persona.
"""
from __future__ import annotations

import io
import json
import uuid
import zipfile
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any, Dict, Iterable, List

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain import memoria_repositories
from ..domain.billing_models import CouponRedemption, CreditEntry, PaymentCheckout, Subscription
from ..domain.chat_models import ChatProattivaTurno
from ..domain.consent_models import ConsensoStorico, UserConsent
from ..domain.deck_models import DeckUnlock
from ..domain.memory_models import UserMemory
from ..domain.models import DailyCard, Reading, User
from ..domain.ordini_models import IndirizzoSpedizione, Ordine
from ..domain.share_models import ShareSignup
from ..domain.voting_models import DeckSuggestion, DeckVote

#: Ogni quante ore si può chiedere un nuovo archivio.
LIMITE_ORE = 24

#: Colonne che non escono mai: segreti tecnici, vettori, blob.
_ESCLUSE = {"embedding", "deck_state", "deck_salt", "webp", "mini_webp"}


def _valore(v: Any) -> Any:
    if isinstance(v, (datetime, date, time)):
        return v.isoformat()
    if isinstance(v, uuid.UUID):
        return str(v)
    if isinstance(v, Decimal):
        return str(v)
    if isinstance(v, (bytes, bytearray, memoryview)):
        return None
    return v


def riga(oggetto: Any, *, escludi: Iterable[str] = ()) -> Dict[str, Any]:
    """Le colonne di una riga come dizionario JSON. Generico di proposito: una colonna aggiunta domani al modello entra
    nell'esportazione senza toccare questo file."""
    via = _ESCLUSE | set(escludi)
    return {
        c.key: _valore(getattr(oggetto, c.key))
        for c in oggetto.__table__.columns
        if c.key not in via
    }


async def _tutte(session: AsyncSession, query) -> List[Any]:
    return list((await session.execute(query)).scalars())


async def _notifiche(session: AsyncSession, uid: int) -> Dict[str, Any]:
    from ..domain.notifiche_models import DispositivoNotifica, InvioNotifica, PreferenzeNotifica

    preferenze = await session.get(PreferenzeNotifica, uid)
    return {
        "preferenze": riga(preferenze) if preferenze else None,
        "dispositivi": [riga(d, escludi={"token", "endpoint", "p256dh", "auth", "impronta", "anon_id"}) for d in await _tutte(
            session, select(DispositivoNotifica).where(DispositivoNotifica.user_id == uid).order_by(DispositivoNotifica.id))],
        "invii": [riga(i) for i in await _tutte(
            session, select(InvioNotifica).where(InvioNotifica.user_id == uid).order_by(InvioNotifica.created_at))],
    }


async def raccogli(session: AsyncSession, user: User) -> Dict[str, Any]:
    """Tutti i dati dell'account, per file."""
    uid = user.id
    profilo = riga(user, escludi={"keycloak_sub", "dati_social", "unione_in_attesa", "unione_risolta"})

    letture = []
    for lettura in await _tutte(session, select(Reading).where(Reading.owner_id == uid).order_by(Reading.created_at)):
        dati = riga(lettura, escludi={"anon_id", "commitment"})
        dati["intervista"] = [{"ordine": t.ordine, "ruolo": t.ruolo, "testo": t.testo, "il": _valore(t.created_at)}
                              for t in lettura.turns]
        dati["carte"] = [riga(c, escludi={"id", "reading_id"}) for c in lettura.cards]
        letture.append(dati)

    memorie = [riga(m) for m in await _tutte(
        session, select(UserMemory).where(UserMemory.owner_id == uid).order_by(UserMemory.created_at))]
    chat = [riga(t) for t in await _tutte(
        session, select(ChatProattivaTurno).where(ChatProattivaTurno.owner_id == uid).order_by(ChatProattivaTurno.ordine))]
    consensi = {
        "attuali": [riga(c, escludi={"anon_id"}) for c in await _tutte(
            session, select(UserConsent).where(UserConsent.user_id == uid).order_by(UserConsent.tipo))],
        "storico": [riga(c, escludi={"ip_hash"}) for c in await _tutte(
            session, select(ConsensoStorico).where(ConsensoStorico.user_id == uid).order_by(ConsensoStorico.created_at))],
    }
    crediti = [riga(c) for c in await _tutte(
        session, select(CreditEntry).where(CreditEntry.user_id == uid).order_by(CreditEntry.created_at, CreditEntry.id))]
    abbonamenti = {
        "abbonamenti": [riga(s) for s in await _tutte(
            session, select(Subscription).where(Subscription.user_id == uid).order_by(Subscription.created_at))],
        "pagamenti": [riga(p) for p in await _tutte(
            session, select(PaymentCheckout).where(PaymentCheckout.user_id == uid).order_by(PaymentCheckout.created_at))],
        "coupon": [riga(c) for c in await _tutte(
            session, select(CouponRedemption).where(CouponRedemption.user_id == uid).order_by(CouponRedemption.created_at))],
    }
    ordini = []
    for ordine in await _tutte(session, select(Ordine).where(Ordine.user_id == uid).order_by(Ordine.created_at)):
        dati = riga(ordine)
        dati["righe"] = [riga(r, escludi={"ordine_id"}) for r in ordine.righe]
        ordini.append(dati)
    indirizzi = [riga(i) for i in await _tutte(
        session, select(IndirizzoSpedizione).where(IndirizzoSpedizione.user_id == uid))]
    altro = {
        "carte_del_giorno": [riga(d) for d in await _tutte(
            session, select(DailyCard).where(DailyCard.user_id == uid).order_by(DailyCard.giorno))],
        "mazzi_sbloccati": [riga(d) for d in await _tutte(session, select(DeckUnlock).where(DeckUnlock.user_id == uid))],
        "voti_mazzi": [riga(v) for v in await _tutte(session, select(DeckVote).where(DeckVote.user_id == uid))],
        "temi_suggeriti": [riga(s) for s in await _tutte(
            session, select(DeckSuggestion).where(DeckSuggestion.user_id == uid))],
        # v9, Fase 5: le notifiche (dei dispositivi non i recapiti tecnici: token e chiavi del browser).
        "notifiche": await _notifiche(session, uid),
        "iscrizioni_dai_tuoi_link": [
            {"il": _valore(s.created_at), "crediti": s.crediti, "sei": "chi ha condiviso" if s.sharer_id == uid else "chi si è iscritto"}
            for s in await _tutte(session, select(ShareSignup).where(
                or_(ShareSignup.sharer_id == uid, ShareSignup.new_user_id == uid)))
        ],
    }
    social = {
        "provenienza": user.dati_social,
        "importa_social": user.importa_social,
        "rileva_posizione": user.rileva_posizione,
    }
    return {
        "profilo.json": profilo,
        "letture.json": letture,
        "memorie.json": memorie,
        "stato_memoria.json": await memoria_repositories.stato_di(session, uid),
        "chat.json": chat,
        "consensi.json": consensi,
        "crediti.json": crediti,
        "abbonamenti.json": abbonamenti,
        "ordini.json": {"ordini": ordini, "indirizzi": indirizzi},
        "dati_social.json": social,
        "altro.json": altro,
    }


LEGGIMI = """TAROTS chat — i tuoi dati / your data
=======================================

Questo archivio contiene i dati del tuo account, un file JSON per argomento (date in UTC, formato ISO 8601).
This archive contains your account data, one JSON file per topic (dates in UTC, ISO 8601).

profilo.json      la scheda / your profile
letture.json      le letture con colloquio, carte e responso / readings with interview, cards and answer
memorie.json      cio' che il lettore ricorda / what the reader remembers
stato_memoria.json  il riassunto che il lettore tiene oggi / the summary the reader keeps today
chat.json         la chat con l'oracolo / the chat with the oracle
consensi.json     le tue scelte e il loro storico / your choices and their history
crediti.json      il registro dei crediti / the credit ledger
abbonamenti.json  abbonamenti, pagamenti, coupon / subscriptions, payments, coupons
ordini.json       ordini e indirizzi / orders and addresses
dati_social.json  cosa e' arrivato dai social / what came from social sign-in
altro.json        carte del giorno, mazzi, voti, inviti / daily cards, decks, votes, invitations

Generato il / generated on: {quando}
"""


def zip_di(dati: Dict[str, Any], quando: datetime) -> bytes:
    """L'archivio: i file JSON e un LEGGIMI.txt."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archivio:
        for nome, contenuto in dati.items():
            archivio.writestr(nome, json.dumps(contenuto, ensure_ascii=False, indent=2, default=_valore))
        archivio.writestr("LEGGIMI.txt", LEGGIMI.replace("{quando}", quando.isoformat()))
    return buffer.getvalue()
