"""La console «Conservazione dati» (GDPR, Fase 1).

L'operatore ha deciso una conservazione **senza scadenza automatica** per letture anonime e chat («fino a
cancellazione dell'interessato o dell'amministratore», `docs/privacy/conservazione.md`): niente pulizie notturne, ma
da qui si vede quanto c'è e di che età, e si cancella a mano. Ogni cancellazione passa da un'**anteprima** (quante
righe, la più vecchia e la più recente) e da una conferma che ripete quel numero: se nel frattempo i dati sono cambiati
la cancellazione si ferma (409) e chiede una nuova anteprima. Ogni esecuzione resta nel registro.

| voce | cosa | l'azione |
|---|---|---|
| `letture_anonime` | le letture gratuite di chi non si è mai iscritto | cancellate (colloquio e carte con loro) |
| `chat_proattiva` | i messaggi della chat con l'oracolo | cancellati |
| `ip_audit` | gli indirizzi (già troncati) e le impronte nel registro | tolti dalle righe, che restano |
| `account_in_cancellazione` | gli account chiusi dalla persona, nei 30 giorni o oltre | cancellazione eseguita adesso |
| `consensi_storici` | le scelte dello storico dei consensi | cancellate, tranne l'ultima per persona e tipo |

`giorni` è l'età minima delle righe da toccare (0 = tutte quelle della voce).
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Request
from lanterna.rete import ip_client
from pydantic import BaseModel, Field
from sqlalchemy import String, and_, case, cast, delete, func, literal, or_, select, update

from ...auth.dependencies import CurrentUser, DbSession, require_role
from ...domain.base import utcnow
from ...domain.chat_models import ChatProattivaTurno
from ...domain.consent_models import ConsensoStorico
from ...domain.models import AuditLog, Reading, User
from ...domain.repositories import AuditRepository
from ...tarot import cancellazione

router = APIRouter(prefix="/admin/conservazione", tags=["conservazione"], dependencies=[Depends(require_role("admin"))])

#: Le fasce d'età mostrate in console, in giorni: [da, a).
FASCE = (
    ("meno di 30 giorni", 0, 30),
    ("30 giorni – 6 mesi", 30, 182),
    ("6 mesi – 1 anno", 182, 365),
    ("1 – 2 anni", 365, 730),
    ("oltre 2 anni", 730, None),
)


class Voce:
    """Una voce della console: dove sta la data, quali righe conta, cosa vuol dire «cancellare»."""

    def __init__(self, chiave: str, titolo: str, descrizione: str, azione: str, colonna, filtro: Callable[[], Any]) -> None:
        self.chiave = chiave
        self.titolo = titolo
        self.descrizione = descrizione
        self.azione = azione
        self.colonna = colonna
        self.filtro = filtro

    def condizione(self, giorni: int, adesso: datetime):
        return and_(self.filtro(), self.colonna <= adesso - timedelta(days=giorni))


def _ultime_scelte():
    """Le righe dello storico che sono l'ultima scelta della loro persona su quel tipo: non si cancellano mai da qui,
    sono la prova del consenso in vigore."""
    soggetto = func.coalesce(cast(ConsensoStorico.user_id, String), ConsensoStorico.anon_id)
    numerate = select(
        ConsensoStorico.id,
        func.row_number().over(
            partition_by=(soggetto, ConsensoStorico.tipo),
            order_by=(ConsensoStorico.created_at.desc(), ConsensoStorico.id.desc()),
        ).label("n"),
    ).subquery()
    return select(numerate.c.id).where(numerate.c.n == 1)


VOCI: Dict[str, Voce] = {
    v.chiave: v
    for v in (
        Voce(
            "letture_anonime", "Letture anonime",
            "Le letture gratuite di chi non si è mai iscritto (quesito, colloquio, carte, anteprima). Una lettura "
            "anonima reclamata all'iscrizione è dell'account e non compare qui.",
            "Cancella le letture (con colloquio e carte)",
            Reading.created_at, lambda: Reading.owner_id.is_(None),
        ),
        Voce(
            "chat_proattiva", "Chat con l'oracolo",
            "I messaggi della chat proattiva, della persona e dell'oracolo. Le memorie nate dalla chat restano.",
            "Cancella i messaggi",
            ChatProattivaTurno.created_at, lambda: literal(True),
        ),
        Voce(
            "ip_audit", "IP nel registro",
            "Gli indirizzi IP del registro, già troncati (IPv4 /24, IPv6 /48), e le loro impronte. La riga del "
            "registro resta: si toglie solo da dove arrivava l'azione.",
            "Togli IP e impronte dalle righe",
            AuditLog.created_at, lambda: or_(AuditLog.ip.is_not(None), AuditLog.ip_hash.is_not(None)),
        ),
        Voce(
            "account_in_cancellazione", "Account in cancellazione",
            "Gli account che la persona ha chiuso: nei 30 giorni si possono ancora riaprire, poi il CronJob notturno "
            "li cancella. Da qui la cancellazione si esegue subito (utente in Keycloak e dati personali; la "
            "contabilità resta pseudonimizzata).",
            "Esegui adesso la cancellazione",
            User.cancellazione_richiesta_il,
            lambda: and_(User.cancellazione_richiesta_il.is_not(None), User.cancellazione_eseguita_il.is_(None)),
        ),
        Voce(
            "consensi_storici", "Storico dei consensi",
            "Ogni scelta fatta su statistiche, Google Analytics, pubblicità, testi, dati particolari, marketing e la "
            "conferma dell'età. L'ultima scelta di ogni persona per ogni tipo non si cancella mai: è la prova del "
            "consenso in vigore.",
            "Cancella le scelte superate",
            ConsensoStorico.created_at, lambda: ConsensoStorico.id.not_in(_ultime_scelte()),
        ),
    )
}


def _voce(chiave: str) -> Voce:
    voce = VOCI.get(chiave)
    if voce is None:
        raise HTTPException(status_code=404, detail="Voce sconosciuta")
    return voce


async def _conta(session, voce: Voce, giorni: int, adesso: datetime) -> Dict[str, Any]:
    riga = (await session.execute(
        select(func.count(), func.min(voce.colonna), func.max(voce.colonna))
        .select_from(voce.colonna.class_).where(voce.condizione(giorni, adesso))
    )).one()
    return {
        "quanti": int(riga[0] or 0),
        "piu_vecchio": riga[1].isoformat() if riga[1] else None,
        "piu_recente": riga[2].isoformat() if riga[2] else None,
    }


@router.get("")
async def riepilogo(session: DbSession) -> Dict[str, Any]:
    """Ogni voce con il totale e i conteggi per fascia d'età."""
    adesso = utcnow()
    voci: List[Dict[str, Any]] = []
    for voce in VOCI.values():
        eta = func.extract("epoch", literal(adesso) - voce.colonna) / 86400
        colonne = [
            func.count(case((and_(eta >= da, eta < a) if a is not None else eta >= da, 1)))
            for _, da, a in FASCE
        ]
        riga = (await session.execute(
            select(func.count(), *colonne).select_from(voce.colonna.class_).where(voce.filtro())
        )).one()
        voci.append({
            "chiave": voce.chiave, "titolo": voce.titolo, "descrizione": voce.descrizione, "azione": voce.azione,
            "totale": int(riga[0] or 0),
            "fasce": [{"etichetta": f[0], "da_giorni": f[1], "a_giorni": f[2], "quanti": int(n or 0)}
                      for f, n in zip(FASCE, riga[1:])],
        })
    return {"voci": voci, "giorni_ripensamento": cancellazione.GIORNI_RIPENSAMENTO}


class Selezione(BaseModel):
    #: Solo le righe più vecchie di così (0 = tutte quelle della voce).
    giorni: int = Field(ge=0, le=36500)


class Esecuzione(Selezione):
    #: Il numero mostrato dall'anteprima: se non torna, i dati sono cambiati e non si tocca niente.
    attesi: int = Field(ge=0)


@router.post("/{chiave}/anteprima")
async def anteprima(chiave: str, payload: Selezione, session: DbSession) -> Dict[str, Any]:
    voce = _voce(chiave)
    return {"voce": voce.chiave, "giorni": payload.giorni, "azione": voce.azione, **await _conta(session, voce, payload.giorni, utcnow())}


@router.post("/{chiave}/esegui")
async def esegui(chiave: str, payload: Esecuzione, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    voce = _voce(chiave)
    adesso = utcnow()
    conteggio = await _conta(session, voce, payload.giorni, adesso)
    if conteggio["quanti"] != payload.attesi:
        raise HTTPException(status_code=409, detail={
            "motivo": "anteprima_superata", "quanti": conteggio["quanti"],
            "messaggio": "I dati sono cambiati dopo l'anteprima: rifalla prima di confermare.",
        })
    condizione = voce.condizione(payload.giorni, adesso)
    dettaglio: Dict[str, Any] = {}
    if chiave == "letture_anonime":
        fatti = (await session.execute(delete(Reading).where(condizione))).rowcount
    elif chiave == "chat_proattiva":
        fatti = (await session.execute(delete(ChatProattivaTurno).where(condizione))).rowcount
    elif chiave == "ip_audit":
        fatti = (await session.execute(update(AuditLog).where(condizione).values(ip=None, ip_hash=None))).rowcount
    elif chiave == "consensi_storici":
        fatti = (await session.execute(delete(ConsensoStorico).where(condizione))).rowcount
    else:  # account_in_cancellazione
        from .privacy import keycloak_admin

        utenti = (await session.execute(select(User).where(condizione))).scalars().all()
        keycloak = keycloak_admin()
        fatti, falliti = 0, []
        for utente in utenti:
            try:
                async with session.begin_nested():
                    await cancellazione.esegui(session, utente, keycloak=keycloak, attore_id=user.id, motivo="console")
                fatti += 1
            except Exception as exc:  # noqa: BLE001 - uno che fallisce (Keycloak giù) non ferma gli altri
                falliti.append({"utente": utente.id, "errore": str(exc)[:200]})
        dettaglio["falliti"] = falliti
    await AuditRepository(session).record(
        action=f"conservazione.{chiave}", actor_id=user.id, target_type="conservazione", target_id=chiave,
        after={"giorni": payload.giorni, "fatti": int(fatti or 0), **dettaglio}, ip=ip_client(request),
    )
    await session.commit()
    return {"voce": chiave, "fatti": int(fatti or 0), **dettaglio}

