"""Il registro dei crediti.

**Il saldo è una somma.** Non c'è un contatore da aggiornare: ogni movimento è
una riga, e il saldo si ottiene sommandole. Costa una query in più per lettura
e restituisce ciò che un contatore perde — *perché* i conti non tornano. Una
sottrazione doppia si vede come due righe; dentro un contatore, sparisce.

**Il problema difficile è la concorrenza.** Due letture avviate insieme per
lo stesso utente leggono lo stesso saldo, entrambe lo trovano sufficiente,
entrambe sottraggono: il saldo finisce sotto zero e il servizio ha regalato
una lettura. Non è un caso raro — due schede aperte bastano.

La difesa è un lock sulla riga dell'utente, preso **prima** di leggere il
saldo. Serializza i movimenti di quell'utente e solo i suoi: due persone
diverse non si aspettano a vicenda.

Le alternative scartate, e perché:

- **un saldo materializzato con vincolo `>= 0`** sarebbe più veloce, ma
  duplica lo stato: il giorno in cui la somma e il contatore divergono —
  e divergono — non si sa quale dei due creda;
- **isolamento `SERIALIZABLE`** risolverebbe senza lock espliciti, al prezzo
  di far fallire transazioni che non c'entrano nulla, che chi chiama dovrebbe
  saper ripetere;
- **un controllo dentro l'`INSERT`** (`WHERE (SELECT sum...) >= costo`) sembra
  atomico e non lo è: in `READ COMMITTED` due transazioni concorrenti vedono
  entrambe il saldo di prima.

**La scadenza non scrive righe (v9).** I crediti di un piano scadono con il
periodo, e la somma li esclude da sé (`expires_at`). Il consumo che li ha
usati porta la **stessa** scadenza: alla fine del periodo escono dalla somma
l'accredito e i consumi che gli appartengono, e resta giusto ciò che era stato
comprato. Prima il consumo non scadeva, e chi aveva usato trenta dei cento
crediti del mese si ritrovava a meno trenta il mese dopo. Una riga di
`scadenza` scritta da un cron avrebbe sottratto i crediti una seconda volta
(la somma li esclude già) oppure costretto a togliere il filtro, lasciando il
saldo sbagliato fra la scadenza e il giro successivo del cron.

**Lo storno può portare il saldo sotto zero (v9).** Un pagamento rimborsato o
contestato toglie i crediti che aveva dato, anche se nel frattempo sono stati
spesi: il saldo negativo è il debito, e finché resta negativo non si aprono
letture (`api/routers/readings.py`). È l'unico movimento che non controlla il
saldo: rifiutarlo lascerebbe le letture regalate a chi si è fatto rimborsare.

**I movimenti che vengono da fuori sono idempotenti.** Un accredito o uno
storno con un `riferimento_esterno` si scrive una volta sola per fornitore e
motivo (indice unico parziale): lo stesso evento può arrivare dal webhook,
dal cron o dalla console, e conta una volta.
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List, Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.base import utcnow
from ..domain.billing_models import CreditEntry
from ..domain.models import User

logger = logging.getLogger(__name__)


class CreditiInsufficienti(Exception):
    """Il saldo non basta per l'operazione richiesta."""

    def __init__(self, servono: int, disponibili: int):
        super().__init__(
            f"servono {servono} crediti, disponibili {disponibili}"
        )
        self.servono = servono
        self.disponibili = disponibili


@dataclass
class Movimento:
    """Una riga del registro, come la legge chi la guarda."""

    delta: int
    reason: str
    quando: datetime
    note: Optional[str] = None
    reading_id: Optional[uuid.UUID] = None
    id: Optional[int] = None
    canale: str = "sistema"
    provider: str = "interno"
    riferimento: Optional[str] = None
    scade: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "delta": self.delta,
            "reason": self.reason,
            "quando": self.quando.isoformat(),
            "note": self.note,
            "reading_id": (
                str(self.reading_id) if self.reading_id else None
            ),
            "canale": self.canale,
            "provider": self.provider,
            "riferimento": self.riferimento,
            "scade": self.scade.isoformat() if self.scade else None,
        }


class RegistroCrediti:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def saldo(self, user_id: int) -> int:
        """I crediti disponibili adesso.

        Gli accrediti scaduti non contano: un piano che ne dà cento al mese
        non deve farli accumulare all'infinito, o il piano più basso diventa
        col tempo indistinguibile dal più alto. Con loro escono i consumi che
        li avevano usati (vedi la nota in cima).
        """
        totale = await self._session.scalar(
            select(func.coalesce(func.sum(CreditEntry.delta), 0)).where(
                CreditEntry.user_id == user_id,
                (CreditEntry.expires_at.is_(None))
                | (CreditEntry.expires_at > utcnow()),
            )
        )
        return int(totale or 0)

    async def accredita(
        self,
        user_id: int,
        quanti: int,
        *,
        reason: str = "accredito_piano",
        note: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        canale: str = "sistema",
        provider: str = "interno",
        riferimento_esterno: Optional[str] = None,
        acquisto_id: Optional[int] = None,
    ) -> CreditEntry:
        """Aggiunge crediti. Non serve lock: accreditare non può fallire.

        Con un `riferimento_esterno` è idempotente: se quel fornitore ha già
        accreditato quell'incasso per lo stesso motivo, si restituisce la riga
        che c'è e non se ne scrive un'altra.
        """
        if quanti <= 0:
            raise ValueError("un accredito muove una quantità positiva")

        if riferimento_esterno:
            gia = await self._per_riferimento(provider, riferimento_esterno, reason)
            if gia is not None:
                logger.info(
                    "Accredito già registrato: %s %s (%s)", provider, riferimento_esterno, reason,
                )
                return gia

        voce = CreditEntry(
            user_id=user_id,
            delta=quanti,
            reason=reason,
            note=note,
            expires_at=expires_at,
            canale=canale,
            provider=provider,
            riferimento_esterno=riferimento_esterno,
            acquisto_id=acquisto_id,
            created_at=utcnow(),
        )
        self._session.add(voce)
        await self._session.flush()
        return voce

    async def consuma(
        self,
        user_id: int,
        quanti: int,
        *,
        reading_id: Optional[uuid.UUID] = None,
        note: Optional[str] = None,
        canale: str = "web",
    ) -> CreditEntry:
        """Sottrae crediti, se ci sono.

        **Qui sta il lock.** Si blocca la riga dell'utente prima di leggere il
        saldo: senza, due richieste concorrenti leggono lo stesso valore,
        lo trovano entrambe sufficiente, e il saldo finisce sotto zero.

        Il lock si libera al commit della transazione del chiamante, che è
        anche quando la riga di consumo diventa visibile: fra la verifica e
        la scrittura non c'è istante in cui un'altra transazione possa
        inserirsi.

        **Prima i crediti che scadono**, dal più vicino alla scadenza: quelli
        comprati non scadono, e spenderli per primi farebbe perdere all'utente
        quelli del piano. Ogni parte del consumo porta la scadenza dei crediti
        che ha usato (una riga per parte); si restituisce la prima.
        """
        if quanti <= 0:
            raise ValueError("un consumo muove una quantità positiva")

        await self._blocca(user_id)

        disponibili = await self.saldo(user_id)
        if disponibili < quanti:
            raise CreditiInsufficienti(quanti, disponibili)

        parti: List[tuple[int, Optional[datetime]]] = []
        resto = quanti
        for scadenza, residuo in await self._in_scadenza(user_id):
            if resto == 0:
                break
            presi = min(resto, residuo)
            parti.append((presi, scadenza))
            resto -= presi
        if resto:
            parti.append((resto, None))

        voci = [
            CreditEntry(
                user_id=user_id,
                delta=-presi,
                reason="consumo",
                reading_id=reading_id,
                note=note,
                expires_at=scadenza,
                canale=canale,
                provider="interno",
                created_at=utcnow(),
            )
            for presi, scadenza in parti
        ]
        self._session.add_all(voci)
        await self._session.flush()

        logger.debug(
            "Consumati %d crediti dell'utente %s (restano %d)",
            quanti, user_id, disponibili - quanti,
        )
        return voci[0]

    async def rimborsa(
        self,
        user_id: int,
        quanti: int,
        *,
        reading_id: Optional[uuid.UUID] = None,
        note: Optional[str] = None,
        canale: str = "web",
    ) -> CreditEntry:
        """Restituisce crediti per qualcosa che non è riuscito.

        Riga propria e non cancellazione del consumo: chi legge il registro
        deve vedere che una risposta è stata tentata, è fallita, ed è stata
        restituita. Cancellando, quella storia sparirebbe e il saldo tornerebbe
        giusto senza spiegare nulla.

        Il rimborso rispecchia il consumo della stessa lettura, scadenze
        comprese: restituire senza scadenza un credito di piano lo renderebbe
        eterno. (Non è lo `storno`: quello è il denaro che torna indietro.)
        """
        parti: List[tuple[int, Optional[datetime]]] = []
        resto = quanti
        if reading_id is not None:
            consumi = (await self._session.execute(
                select(CreditEntry.delta, CreditEntry.expires_at)
                .where(
                    CreditEntry.user_id == user_id, CreditEntry.reading_id == reading_id,
                    CreditEntry.reason == "consumo",
                )
                .order_by(CreditEntry.id)
            )).all()
            for delta, scadenza in consumi:
                if resto == 0:
                    break
                presi = min(resto, -delta)
                parti.append((presi, scadenza))
                resto -= presi
        if resto:
            parti.append((resto, None))

        voci = [
            CreditEntry(
                user_id=user_id,
                delta=presi,
                reason="rimborso",
                reading_id=reading_id,
                note=note,
                expires_at=scadenza,
                canale=canale,
                provider="interno",
                created_at=utcnow(),
            )
            for presi, scadenza in parti
        ]
        self._session.add_all(voci)
        await self._session.flush()
        return voci[0]

    async def rettifica(
        self, user_id: int, delta: int, *, note: str, canale: str = "console",
    ) -> CreditEntry:
        """Correzione manuale, con la sua ragione obbligatoria.

        È il modo di riparare uno sbaglio senza toccare ciò che è già scritto:
        entrambe le righe restano, e la storia resta leggibile.
        """
        if not note.strip():
            raise ValueError("una rettifica senza motivo non è una rettifica")
        if delta == 0:
            raise ValueError("una rettifica che non muove nulla è rumore")

        voce = CreditEntry(
            user_id=user_id,
            delta=delta,
            reason="rettifica",
            note=note,
            canale=canale,
            provider="interno",
            created_at=utcnow(),
        )
        self._session.add(voce)
        await self._session.flush()
        return voce

    async def storna(
        self,
        user_id: int,
        quanti: int,
        *,
        provider: str,
        riferimento_esterno: str,
        canale: str = "sistema",
        note: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> tuple[CreditEntry, bool]:
        """Toglie i crediti di un pagamento tornato indietro (rimborso o contestazione).

        Idempotente per (`provider`, `riferimento_esterno`): il riferimento è
        quello dell'incasso stornato, così il webhook del fornitore, un secondo
        invio dello stesso evento e uno storno registrato a mano dalla console
        contano una volta sola. Restituisce la riga e se è nuova.

        Non controlla il saldo, e non è una dimenticanza: i crediti possono
        essere già stati spesi, e il saldo negativo è proprio ciò che resta da
        saldare. `expires_at` è quella dei crediti stornati: lo storno di un
        periodo di piano esce dalla somma quando quel periodo sarebbe scaduto.
        """
        if quanti <= 0:
            raise ValueError("uno storno muove una quantità positiva")
        if not riferimento_esterno:
            raise ValueError("uno storno senza riferimento non sarebbe idempotente")

        gia = await self._per_riferimento(provider, riferimento_esterno, "storno")
        if gia is not None:
            return gia, False

        voce = CreditEntry(
            user_id=user_id,
            delta=-quanti,
            reason="storno",
            note=note,
            expires_at=expires_at,
            canale=canale,
            provider=provider,
            riferimento_esterno=riferimento_esterno,
            created_at=utcnow(),
        )
        self._session.add(voce)
        await self._session.flush()
        logger.warning(
            "Storno di %d crediti dell'utente %s (%s %s)", quanti, user_id, provider, riferimento_esterno,
        )
        return voce, True

    async def annulla_storno(
        self,
        provider: str,
        riferimento_esterno: str,
        *,
        canale: str = "sistema",
        note: Optional[str] = None,
    ) -> Optional[tuple[CreditEntry, bool]]:
        """Compensa uno storno: la contestazione è stata vinta e il denaro è tornato.

        Una riga di `storno_annullato` uguale e contraria, con la stessa
        scadenza; idempotente come lo storno. `None` se quello storno non c'è.
        """
        storno = await self._per_riferimento(provider, riferimento_esterno, "storno")
        if storno is None:
            return None
        gia = await self._per_riferimento(provider, riferimento_esterno, "storno_annullato")
        if gia is not None:
            return gia, False

        voce = CreditEntry(
            user_id=storno.user_id,
            delta=-storno.delta,
            reason="storno_annullato",
            note=note,
            expires_at=storno.expires_at,
            canale=canale,
            provider=provider,
            riferimento_esterno=riferimento_esterno,
            created_at=utcnow(),
        )
        self._session.add(voce)
        await self._session.flush()
        return voce, True

    async def gia_registrato(self, provider: str, riferimento: str, reason: str) -> bool:
        """Quel fornitore ha già una riga con questo riferimento e questo motivo?"""
        return await self._per_riferimento(provider, riferimento, reason) is not None

    async def per_riferimenti(
        self, provider: str, riferimenti: Iterable[str], motivi: Sequence[str],
    ) -> List[CreditEntry]:
        """Le righe di un fornitore con uno di questi riferimenti e motivi: un incasso cercato per i suoi nomi."""
        candidati = [r for r in riferimenti if r]
        if not candidati:
            return []
        return list((await self._session.execute(
            select(CreditEntry)
            .where(
                CreditEntry.provider == provider,
                CreditEntry.riferimento_esterno.in_(candidati),
                CreditEntry.reason.in_(tuple(motivi)),
            )
            .order_by(CreditEntry.id)
        )).scalars().all())

    async def movimenti(
        self, user_id: int, *, limite: int = 100
    ) -> List[Movimento]:
        righe = (await self._session.execute(
            select(CreditEntry)
            .where(CreditEntry.user_id == user_id)
            .order_by(CreditEntry.created_at.desc(), CreditEntry.id.desc())
            .limit(limite)
        )).scalars().all()

        return [
            Movimento(
                delta=r.delta, reason=r.reason, quando=r.created_at,
                note=r.note, reading_id=r.reading_id, id=r.id,
                canale=r.canale, provider=r.provider,
                riferimento=r.riferimento_esterno, scade=r.expires_at,
            )
            for r in righe
        ]

    async def _per_riferimento(self, provider: str, riferimento: str, reason: str) -> Optional[CreditEntry]:
        return (await self._session.execute(
            select(CreditEntry).where(
                CreditEntry.provider == provider,
                CreditEntry.riferimento_esterno == riferimento,
                CreditEntry.reason == reason,
            )
        )).scalar_one_or_none()

    async def _in_scadenza(self, user_id: int) -> List[tuple[datetime, int]]:
        """I crediti ancora validi che scadono, raggruppati per scadenza, dal più vicino: quanto ne resta di ciascuno.

        Un gruppo è l'accredito di un periodo meno i consumi (e gli storni) che
        portano la sua stessa scadenza. Un residuo non positivo non si spende.
        """
        righe = (await self._session.execute(
            select(CreditEntry.expires_at, func.sum(CreditEntry.delta))
            .where(CreditEntry.user_id == user_id, CreditEntry.expires_at > utcnow())
            .group_by(CreditEntry.expires_at)
            .order_by(CreditEntry.expires_at)
        )).all()
        return [(scadenza, int(residuo)) for scadenza, residuo in righe if residuo and residuo > 0]

    async def _blocca(self, user_id: int) -> None:
        """Prende il lock sulla riga dell'utente.

        `FOR UPDATE` e non un lock consultivo: la riga esiste già, il lock
        muore con la transazione anche se il processo cade, e non c'è nessun
        identificativo numerico da inventare e da far coincidere fra moduli
        diversi.
        """
        await self._session.execute(
            select(User.id).where(User.id == user_id).with_for_update()
        )
