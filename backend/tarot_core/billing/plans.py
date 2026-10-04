"""Abbonamenti: chi ha cosa, e fino a quando.

**Il pagamento non è qui.** `BillingProvider` è il confine: quando arriverà un
fornitore vero — Stripe o altri — sarà un'implementazione di questo protocollo,
e il resto della piattaforma non cambierà. Per ora c'è quello finto, che
concede tutto: in sviluppo serve provare il servizio, non il pagamento.

**Il rinnovo accredita, non azzera.** A ogni periodo il piano aggiunge i suoi
crediti con una scadenza; quelli comprati a parte restano. Azzerare il saldo
al rinnovo sarebbe più semplice e porterebbe via crediti pagati.
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Protocol, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.base import utcnow
from ..domain.billing_models import STATI_VIVI, Plan, Subscription
from .credits import RegistroCrediti
from .entitlements import PIANO_PREDEFINITO, Diritti, diritti_da

logger = logging.getLogger(__name__)

#: Quanto dura un periodo mensile. Trenta giorni e non «il mese»: un mese
#: civile dura fra ventotto e trentuno giorni, e far dipendere i crediti dal
#: calendario significa che a febbraio se ne ricevono meno senza che nessuno
#: lo abbia deciso.
GIORNI_PERIODO = 30


class BillingProvider(Protocol):
    """Il confine verso chi incassa davvero, per la parte degli abbonamenti.

    Volutamente magro: creare un abbonamento, disdirlo, dire se è pagato.
    Tutto ciò che riguarda carte, ricevute e imposte resta dall'altra parte —
    quella è materia in cui sbagliare costa, e va gestita da chi lo fa di
    mestiere.

    È la metà di `pagamenti.ProviderPagamenti`, che lo estende con la pagina di
    pagamento e la verifica degli eventi (v9): un solo elenco di questi tre
    metodi, e non due che possono divergere. `GestoreAbbonamenti` chiede solo
    questa metà, così un fornitore di prova non deve fingere una cassa.
    """

    async def crea_abbonamento(
        self, user_id: int, piano: Plan, *, annuale: bool = False,
    ) -> str:
        """Restituisce l'identificativo esterno dell'abbonamento."""
        ...

    async def disdici(self, external_id: str) -> None:
        ...

    async def e_pagato(self, external_id: str) -> bool:
        ...


class ProviderDiSviluppo(BillingProvider):
    """Concede tutto senza incassare nulla.

    Esiste perché in sviluppo serve provare il servizio, non il pagamento. Il
    nome lo dice a chi legge i log: un `external_id` che comincia per
    `sviluppo-` in un database di produzione è un difetto visibile a occhio.
    """

    async def crea_abbonamento(
        self, user_id: int, piano: Plan, *, annuale: bool = False,
    ) -> str:
        return f"sviluppo-{uuid.uuid4().hex[:12]}"

    async def disdici(self, external_id: str) -> None:
        return None

    async def e_pagato(self, external_id: str) -> bool:
        return True


class NienteDaIncassare:
    """Il «fornitore» di ciò che non si paga: piani gratuiti e regalati (v9).

    Il CronJob degli abbonamenti lo usa per rinnovarli: chiedere a Stripe se un
    piano gratuito è pagato non ha senso, e lo farebbe fallire.
    """

    name = "interno"

    async def crea_abbonamento(self, user_id: int, piano: Plan, *, annuale: bool = False) -> str:
        return f"gratuito-{uuid.uuid4().hex[:12]}"

    async def disdici(self, external_id: str) -> None:
        return None

    async def e_pagato(self, external_id: str) -> bool:
        return True


def gratuito(piano: Plan) -> bool:
    return piano.price_monthly <= 0 and piano.price_yearly <= 0


def fornitore_di(piano: Plan, nome: Optional[str]) -> str:
    """Chi rinnova un abbonamento a questo piano (`Subscription.provider`).

    Un piano gratuito è sempre `interno`: non c'è niente da incassare, anche se
    l'abbonamento è nato col simulatore. Per gli altri vale il fornitore che ha
    incassato; `disattivato`, `coupon` e i nomi sconosciuti sono `interno`.
    """
    from ..domain.billing_models import FORNITORI

    if gratuito(piano) or not nome or nome not in FORNITORI:
        return "interno"
    return nome


@dataclass
class EsitoRinnovo:
    abbonamento_id: uuid.UUID
    crediti_accreditati: int = 0
    nuovo_periodo_fine: Optional[datetime] = None
    chiuso: bool = False
    motivo: str = ""


class GestoreAbbonamenti:
    def __init__(
        self,
        session: AsyncSession,
        provider: Optional[BillingProvider] = None,
    ) -> None:
        self._session = session
        if provider is None:
            from .pagamenti import provider_pagamenti

            provider = provider_pagamenti()
        self._provider = provider
        self._crediti = RegistroCrediti(session)

    # -- lettura -----------------------------------------------------------

    async def piani(
        self, *, solo_attivi: bool = True, tipo: Optional[str] = None,
    ) -> Sequence[Plan]:
        query = select(Plan).order_by(Plan.rank)
        if solo_attivi:
            query = query.where(Plan.active.is_(True))
        if tipo:
            query = query.where(Plan.tipo == tipo)
        return (await self._session.execute(query)).scalars().all()

    async def piano_per_slug(self, slug: str) -> Optional[Plan]:
        return (await self._session.execute(
            select(Plan).where(Plan.slug == slug)
        )).scalar_one_or_none()

    async def abbonamento_di(self, user_id: int) -> Optional[Subscription]:
        """L'abbonamento vivo di un utente, se ne ha uno.

        Il più recente fra quelli vivi: un utente che passa da un piano a un
        altro può averne due per qualche istante, e servire il vecchio
        sarebbe l'errore più evidente possibile.
        """
        return (await self._session.execute(
            select(Subscription)
            .where(
                Subscription.user_id == user_id,
                # `in_sospeso` (Fase 2b) è la tolleranza dopo un pagamento fallito: le letture comprese restano.
                Subscription.status.in_(STATI_VIVI),
            )
            .order_by(Subscription.created_at.desc())
            .limit(1)
        )).scalar_one_or_none()

    async def tariffe_in_vigore(self) -> bool:
        """C'è un catalogo, cioè: questa installazione fa pagare?

        Serve a non far dipendere il funzionamento del prodotto da un seed.
        Senza nessun piano in tabella, addebitare ogni lettura significa che
        **nessuno** può consultare le carte: un'installazione
        appena migrata sarebbe muta, e il motivo — una tabella vuota — non
        somiglia per niente al sintomo.

        La scelta opposta, regalare tutto per una tabella vuota, si paga in
        mancati incassi e si vede nei log; questa si paga in un servizio che
        non parte e sembra rotto. Fra i due si sceglie quello che lascia il
        prodotto usabile e lo dichiara.
        """
        return bool(await self._session.scalar(
            select(Plan.id).where(Plan.active.is_(True)).limit(1)
        ))

    async def diritti_di(self, user_id: int) -> Diritti:
        """Cosa può fare questo utente, adesso."""
        abbonamento = await self.abbonamento_di(user_id)
        base = await self.piano_per_slug(PIANO_PREDEFINITO)
        return diritti_da(abbonamento, piano_base=base)

    # -- scrittura ---------------------------------------------------------

    async def apri_piano_base(self, user_id: int) -> Optional[Subscription]:
        """Apre il piano gratuito a chi non ha nessun abbonamento.

        Serve perché i crediti del piano gratuito, se il catalogo ne prevede,
        sono righe del registro: senza aprirlo, un account nuovo riceverebbe
        402 alla prima lettura anche dove il catalogo ne regala qualcuna.

        Non fa nulla se un abbonamento c'è già, né se il piano gratuito non è
        stato ancora scritto in tabella: in quel caso il servizio funziona
        lo stesso sui diritti base, e inventare un piano da qui
        significherebbe che il catalogo si crea da solo.
        """
        if await self.abbonamento_di(user_id) is not None:
            return None

        piano = await self.piano_per_slug(PIANO_PREDEFINITO)
        if piano is None:
            logger.warning(
                "Nessun piano «%s» in catalogo: l'utente %s resta sui diritti "
                "base e senza crediti.", PIANO_PREDEFINITO, user_id,
            )
            return None

        return await self.sottoscrivi(user_id, piano)

    async def sottoscrivi(
        self,
        user_id: int,
        piano: Plan,
        *,
        annuale: bool = False,
        in_prova: bool = False,
        external_id: Optional[str] = None,
        fornitore: Optional[str] = None,
        canale: str = "sistema",
        riferimento: Optional[str] = None,
        listino: Optional[int] = None,
        importo: Optional[int] = None,
        sconto_ricorrente: int = 0,
        prova: bool = False,
        giorni_prova: int = 0,
        sostituisce: Optional[uuid.UUID] = None,
        fine: Optional[datetime] = None,
    ) -> Subscription:
        """Apre un abbonamento e accredita i crediti del primo periodo.

        Fase 2b: `listino` e `importo` sono il prezzo del periodo e quanto è stato pagato davvero (la base di un
        conguaglio futuro), `sconto_ricorrente` lo sconto dei rinnovi. Con `prova` l'abbonamento nasce `in_prova` per
        `giorni_prova` giorni, e alla fine diventa annuale. Con `sostituisce` è un upgrade: il vecchio abbonamento
        si chiude **subito** presso il fornitore, senza rimborso, perché il suo valore residuo è già stato scalato
        dal prezzo del nuovo.

        `external_id` arriva dal fornitore quando l'abbonamento nasce da un
        pagamento confermato; senza, lo si chiede al fornitore — è il caso
        del piano gratuito, che non passa da nessun pagamento.

        `fornitore` dice chi lo rinnoverà (`Subscription.provider`): un piano
        gratuito è sempre `interno`, perché non c'è niente da incassare.
        `canale` e `riferimento` finiscono sulla riga dei crediti del primo
        periodo (il riferimento è quello dell'incasso: con lo stesso, un
        secondo accredito non si scrive).

        `fine` (Fase 4) è la fine del primo periodo secondo il fornitore: gli store la dicono, e i loro mesi (e le
        loro prove) non durano per forza quanto i nostri.
        """
        if piano.pacchetto:
            raise ValueError("un pacchetto si compra, non si sottoscrive")

        precedente = await self.abbonamento_di(user_id)
        if precedente is not None:
            chiudi_subito = getattr(self._provider, "chiudi_subito", None)
            if sostituisce is not None and precedente.id == sostituisce and precedente.external_id and chiudi_subito:
                # L'upgrade col conguaglio: il residuo è già stato tolto dal prezzo del nuovo, il vecchio si chiude
                # adesso e non si rimborsa (rimborsarlo lo pagherebbe due volte all'utente).
                if precedente.programma_esterno and hasattr(self._provider, "annulla_programma"):
                    await self._provider.annulla_programma(precedente.programma_esterno)
                await chiudi_subito(precedente.external_id)
            elif precedente.external_id and precedente.cancel_at is None:
                # Disdetto anche presso il fornitore, se non lo era già. Chiuderlo
                # soltanto qui lasciava il fornitore libero di rinnovare — e di
                # addebitare — un piano che l'utente non aveva più: chi passava
                # da Base a Gold avrebbe pagato entrambi.
                await self._provider.disdici(precedente.external_id)
            # Chiuso e non cancellato: il passaggio da un piano all'altro
            # resta leggibile nella storia dell'utente.
            precedente.status = "disdetto"
            precedente.cancel_at = utcnow()

        if external_id is None:
            external_id = await self._provider.crea_abbonamento(
                user_id, piano, annuale=annuale,
            )

        inizio = utcnow()
        if prova and giorni_prova > 0:
            durata = timedelta(days=giorni_prova)
        else:
            durata = timedelta(days=365 if annuale else GIORNI_PERIODO)

        abbonamento = Subscription(
            user_id=user_id,
            plan_id=piano.id,
            status="in_prova" if (in_prova or prova) else "attivo",
            period_start=inizio,
            period_end=fine if fine is not None and fine > inizio else inizio + durata,
            external_id=external_id,
            provider=fornitore_di(piano, fornitore or getattr(self._provider, "name", None)),
            annuale=annuale,
            prova=prova,
            listino=listino if listino is not None else (piano.price_yearly if annuale else piano.price_monthly),
            importo_periodo=0 if prova else importo,
            sconto_ricorrente=sconto_ricorrente,
        )
        self._session.add(abbonamento)
        await self._session.flush()

        if piano.credits_per_period > 0:
            await self._crediti.accredita(
                user_id,
                piano.credits_per_period,
                reason="accredito_piano",
                note=f"piano {piano.slug}",
                # Scadono con il periodo: un piano che ne dà cento al mese non
                # deve farli accumulare all'infinito, o il piano più basso
                # diventa col tempo indistinguibile dal più alto.
                expires_at=abbonamento.period_end,
                canale=canale,
                provider=abbonamento.provider,
                riferimento_esterno=riferimento,
            )

        logger.info(
            "Abbonamento %s aperto per l'utente %s (piano %s)",
            str(abbonamento.id)[:8], user_id, piano.slug,
        )
        return abbonamento

    async def disdici(self, abbonamento: Subscription) -> Subscription:
        """Segna la disdetta. L'abbonamento resta attivo fino a scadenza.

        È già stato pagato: chiuderlo subito toglierebbe qualcosa a cui
        l'utente ha diritto, e la differenza fra «ho disdetto» e «non ho più
        accesso» è esattamente ciò che rende accettabile disdire.
        """
        if abbonamento.external_id:
            await self._provider.disdici(abbonamento.external_id)

        abbonamento.cancel_at = abbonamento.period_end
        await self._session.flush()
        return abbonamento

    async def rinnova(
        self,
        abbonamento: Subscription,
        *,
        pagato: bool = False,
        riferimento: Optional[str] = None,
        fine: Optional[datetime] = None,
        canale: str = "sistema",
        importo: Optional[int] = None,
    ) -> EsitoRinnovo:
        """Apre il periodo successivo, o chiude l'abbonamento se disdetto.

        `pagato=True` quando il rinnovo arriva da un evento del fornitore che
        ha già incassato (Stripe `invoice.paid`): non si richiede se è pagato,
        e non si guarda la disdetta — se il fornitore ha incassato, il periodo
        è dovuto. `fine` è la fine del periodo secondo il fornitore (i suoi mesi
        sono di calendario, i nostri di trenta giorni); `riferimento` l'incasso,
        che rende idempotente l'accredito; `importo` quanto è stato incassato.

        Fase 2b: il periodo nuovo dura un anno o trenta giorni secondo `annuale` (non quanto il precedente: una prova
        dura quattordici giorni e si converte in un annuale). Un downgrade programmato parte qui. Un pagamento non
        riuscito apre la tolleranza (`in_sospeso`, letture comprese ancora attive) invece di sospendere subito.
        """
        from .abbonamenti import applica_downgrade, apri_tolleranza, chiudi_tolleranza, impostazioni

        esito = EsitoRinnovo(abbonamento_id=abbonamento.id)
        adesso = utcnow()

        if not pagato and abbonamento.cancel_at is not None and abbonamento.cancel_at <= adesso:
            abbonamento.status = "disdetto"
            esito.chiuso = True
            esito.motivo = "disdetto dall'utente"
            await self._session.flush()
            return esito

        if not pagato and abbonamento.external_id:
            if not await self._provider.e_pagato(abbonamento.external_id):
                # Non disdetto, e nemmeno sospeso subito: un pagamento può fallire per una carta scaduta, e togliere
                # le letture al primo tentativo non riuscito perderebbe chi voleva restare. Tolleranza (Fase 2b).
                # Il simulatore non ha fatture: se ne inventa una, che la sua pagina fa pagare come quella di Stripe.
                fattura = abbonamento.fattura_aperta or (
                    f"mock_in_{abbonamento.id.hex[:12]}" if abbonamento.provider == "mock" else None
                )
                await apri_tolleranza(self._session, abbonamento, fattura=fattura)
                esito.motivo = "pagamento non riuscito"
                return esito

        if pagato and fine is not None and abbonamento.period_end >= fine and abbonamento.status == "attivo":
            # Lo stesso incasso arrivato di nuovo (un altro evento per la stessa fattura): il periodo c'è già.
            esito.motivo = "già rinnovato"
            return esito

        if abbonamento.piano_successivo_id is not None:
            successivo = abbonamento.piano_successivo or await self._session.get(Plan, abbonamento.piano_successivo_id)
            if successivo is not None:
                riga = await impostazioni(self._session)
                applica_downgrade(abbonamento, successivo, percento_rinnovo=riga.sconto_rinnovo)

        piano = abbonamento.plan
        durata = timedelta(days=365 if abbonamento.annuale else GIORNI_PERIODO)
        inizio = abbonamento.period_end
        # Senza un incasso esterno il riferimento è il periodo stesso: due giri del cron sullo stesso abbonamento (o
        # un cron e una replica) non accreditano due volte lo stesso periodo.
        riferimento = riferimento or f"rinnovo:{abbonamento.id}:{inizio.isoformat()}"
        if piano.credits_per_period > 0 and await self._crediti.gia_registrato(
            abbonamento.provider, riferimento, "accredito_piano",
        ):
            esito.motivo = "già rinnovato"
            return esito

        abbonamento.period_start = inizio
        abbonamento.period_end = fine if fine is not None and fine > inizio else inizio + durata
        abbonamento.status = "attivo"
        chiudi_tolleranza(abbonamento)
        if importo is not None:
            abbonamento.importo_periodo = int(importo)
        else:
            listino = abbonamento.listino
            if listino is None:
                listino = piano.price_yearly if abbonamento.annuale else piano.price_monthly
            abbonamento.importo_periodo = max(0, listino - abbonamento.sconto_ricorrente)

        if piano.credits_per_period > 0:
            await self._crediti.accredita(
                abbonamento.user_id,
                piano.credits_per_period,
                reason="accredito_piano",
                note=f"rinnovo {piano.slug}",
                expires_at=abbonamento.period_end,
                canale=canale,
                provider=abbonamento.provider,
                riferimento_esterno=riferimento,
            )
            esito.crediti_accreditati = piano.credits_per_period

        esito.nuovo_periodo_fine = abbonamento.period_end
        await self._session.flush()
        if abbonamento.coupon_id is not None:
            # Fase 2d: il rinnovo scontato dal coupon entra nel resoconto, e il coupon «per N periodi» ne ha uno in meno.
            from .offerte import dopo_rinnovo

            await dopo_rinnovo(
                self._session, abbonamento, self._provider, riferimento=riferimento,
                sconto_pagato=abbonamento.sconto_ricorrente,
            )
        if not gratuito(piano):
            # La commissione di chi ha invitato (Fase 2b): una percentuale dell'importo del periodo, in crediti — anche
            # sulla conversione di una prova, che è il suo primo incasso.
            from .referral import commissione_da_abbonamento

            await commissione_da_abbonamento(
                self._session, abbonamento.user_id, abbonamento.importo_periodo, riferimento=riferimento,
            )
            await self._email_rinnovo(abbonamento, riferimento)
        return esito

    async def _email_rinnovo(self, abbonamento: Subscription, riferimento: str) -> None:
        """«Il tuo abbonamento è stato rinnovato»: una volta per incasso (o per periodo, se interno).

        Non per gli abbonamenti degli store (Fase 4): la ricevuta la manda lo store, con l'importo vero nella valuta
        del paese; la nostra direbbe il listino del sito, che lì non è il prezzo pagato.
        """
        from ..domain.models import User
        from ..posta import data_in, importo_in, lingua_di, manda

        if abbonamento.provider in ("google_play", "app_store"):
            return
        utente = await self._session.get(User, abbonamento.user_id)
        lingua = lingua_di(utente)
        await manda(self._session, utente, "rinnovo_avvenuto", f"rinnovo_avvenuto:{abbonamento.id}:{riferimento}", {
            "piano": abbonamento.plan.name, "data": data_in(abbonamento.period_end, lingua),
            "importo": importo_in(abbonamento.importo_periodo or 0, abbonamento.plan.currency, lingua),
        })

    async def da_rinnovare(self, *, limite: int = 100) -> Sequence[Subscription]:
        """Gli abbonamenti il cui periodo è finito.

        È il lavoro periodico del worker: senza, un abbonamento pagato smette
        di accreditare crediti alla fine del primo mese e nessuno se ne
        accorge finché l'utente non se ne lamenta.
        """
        return (await self._session.execute(
            select(Subscription)
            .where(
                Subscription.status.in_(("in_prova", "attivo")),
                Subscription.period_end <= utcnow(),
            )
            .order_by(Subscription.period_end)
            .limit(limite)
        )).scalars().all()
