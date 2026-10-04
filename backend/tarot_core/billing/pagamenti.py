"""Il pagamento: Stripe sul web (v9, `billing/stripe.py`), il simulatore in sviluppo.

Gli store delle app (Google Play, App Store) passano da qui dalla Fase 4 (`billing/store/`): il loro acquisto è
verificato presso lo store e tradotto negli stessi eventi, con id `gp:`/`as:`. Il flusso è lo stesso per tutti:

1. l'utente sceglie un piano e la piattaforma apre una **sessione di pagamento**;
2. il fornitore ospita la pagina dove si paga, e l'utente ci viene mandato;
3. a pagamento avvenuto il fornitore manda un **evento firmato**;
4. solo allora l'abbonamento nasce e i crediti del periodo vengono accreditati.

Un fornitore vero è un'implementazione di `ProviderPagamenti`: dove sta la
sua pagina, come firma i suoi eventi, cosa dice un rinnovo. Il resto — la
sessione, l'idempotenza, l'attivazione — non cambia.

**Il simulatore è un fornitore a tutti gli effetti.** Firma i suoi eventi con
HMAC e un timestamp come fanno quelli veri, e l'evento passa dalla stessa
verifica. Un simulatore che attivasse l'abbonamento direttamente proverebbe
un percorso che in produzione non esiste; questo prova quello vero, meno la
carta. **In produzione si rifiuta di partire**: altrimenti chiunque potrebbe
«pagare» il piano più caro con un clic.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, Mapping, Optional, Protocol

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.base import utcnow
from ..domain.billing_models import CANALI, STATI_ABBONAMENTO, PaymentCheckout, PaymentEvent, Plan, Subscription
from ..settings import Settings, get_settings
from .plans import BillingProvider

if TYPE_CHECKING:  # pragma: no cover
    from ..domain.ordini_models import Ordine
    from .offerte import Sconto

logger = logging.getLogger(__name__)

#: Quanto può essere vecchio un evento firmato. Oltre, si rifiuta: è la
#: difesa contro chi intercetta un evento valido e lo rimanda più tardi.
TOLLERANZA_SECONDI = 300

#: Gli eventi che la piattaforma sa gestire. Un fornitore traduce i suoi in questi (`billing/stripe.py`): il resto
#: del codice non sa come si chiamano da Stripe o dagli store.
PAGATO = "checkout.pagato"
ANNULLATO = "checkout.annullato"
SCADUTO = "checkout.scaduto"
RINNOVATO = "abbonamento.rinnovato"
RINNOVO_FALLITO = "abbonamento.pagamento_fallito"
ABBONAMENTO_CHIUSO = "abbonamento.annullato"
#: Lo stato dell'abbonamento presso il fornitore è cambiato (Stripe `customer.subscription.updated`): in regola, in
#: ritardo, disdetto a fine periodo o di nuovo con il rinnovo automatico. Non accredita mai: i crediti li dà solo un
#: incasso (`RINNOVATO`).
ABBONAMENTO_AGGIORNATO = "abbonamento.aggiornato"
#: Un incasso tornato indietro (rimborso o contestazione) e una contestazione vinta (v9).
STORNO = "pagamento.stornato"
STORNO_ANNULLATO = "pagamento.storno_annullato"
#: La prova sta per finire (Stripe `customer.subscription.trial_will_end`, tre giorni prima): un segnale in più, che
#: allinea la fine della prova a quella del fornitore. Il promemoria all'utente lo manda il cron, due giorni prima.
PROVA_IN_SCADENZA = "abbonamento.prova_in_scadenza"


class FirmaNonValida(Exception):
    """L'evento non viene dal fornitore, o è stato alterato, o è vecchio."""


@dataclass
class EventoPagamento:
    """Un evento del fornitore, già verificato."""

    id: str
    tipo: str
    dati: Dict[str, Any] = field(default_factory=dict)


class ProviderPagamenti(BillingProvider, Protocol):
    """Ciò che un fornitore di pagamento deve saper fare.

    Gli abbonamenti (`crea_abbonamento`, `disdici`, `e_pagato`) vengono da
    `BillingProvider`, che è ciò che chiede `GestoreAbbonamenti`; qui si
    aggiungono la cassa e gli eventi. Le pagine di pagamento sono asincrone
    (v9): un fornitore vero le crea con una chiamata alla sua API.
    """

    name: str

    async def url_di_pagamento(self, checkout: PaymentCheckout, *, ritorno: str, giorni_prova: int = 0) -> str:
        """Dove mandare l'utente a pagare un piano."""
        ...

    async def url_di_pagamento_ordine(self, ordine: "Ordine", *, ritorno: str) -> str:
        """Dove mandare l'utente a pagare un ordine del negozio mazzi (v5, Fase B3): un carrello non
        è un `Plan`, quindi non passa da `url_di_pagamento` — stesso principio, contenuto diverso."""
        ...

    def verifica(self, corpo: bytes, intestazioni: Mapping[str, str]) -> EventoPagamento:
        """Verifica la firma e interpreta l'evento. Solleva `FirmaNonValida`."""
        ...


class PagamentiSimulati:
    """Un fornitore che non incassa, e che per il resto si comporta come uno vero.

    La pagina di pagamento è servita dall'API stessa (`/billing/mock/...`) e
    manda i suoi eventi firmati allo stesso webhook dei fornitori veri. Per
    provare la sospensione di un abbonamento, `rinnovo_fallisce` fa rispondere
    «non pagato» ai rinnovi.
    """

    name = "mock"

    def __init__(self, settings: Optional[Settings] = None, *, rinnovo_fallisce: bool = False) -> None:
        settings = settings or get_settings()
        self._segreto = settings.billing_webhook_secret.encode("utf-8")
        self._api = settings.api_public_url.rstrip("/")
        self.rinnovo_fallisce = rinnovo_fallisce or settings.billing_mock_renewal_fails

    # -- pagina di pagamento -----------------------------------------------

    async def url_di_pagamento(self, checkout: PaymentCheckout, *, ritorno: str, giorni_prova: int = 0) -> str:
        from urllib.parse import quote

        return f"{self._api}/billing/mock/checkout/{checkout.id}?ritorno={quote(ritorno, safe='')}"

    async def url_di_pagamento_ordine(self, ordine: "Ordine", *, ritorno: str) -> str:
        from urllib.parse import quote

        return f"{self._api}/billing/mock/ordine/{ordine.id}?ritorno={quote(ritorno, safe='')}"

    # -- firma -------------------------------------------------------------

    def firma(self, corpo: bytes, *, istante: Optional[int] = None) -> str:
        """L'intestazione di firma, nel formato dei fornitori veri.

        `t=<timestamp>,v1=<hmac>`: il timestamp entra nel messaggio firmato,
        così che un evento non possa essere rimandato ringiovanito.
        """
        t = istante if istante is not None else int(time.time())
        firmato = f"{t}.".encode("utf-8") + corpo
        mac = hmac.new(self._segreto, firmato, hashlib.sha256).hexdigest()
        return f"t={t},v1={mac}"

    def verifica(self, corpo: bytes, intestazioni: Mapping[str, str]) -> EventoPagamento:
        intestazione = _cerca(intestazioni, "x-mock-signature")
        if not intestazione:
            raise FirmaNonValida("firma assente")

        parti = dict(p.split("=", 1) for p in intestazione.split(",") if "=" in p)
        try:
            t = int(parti["t"])
            ricevuta = parti["v1"]
        except (KeyError, ValueError) as exc:
            raise FirmaNonValida("firma malformata") from exc

        if abs(time.time() - t) > TOLLERANZA_SECONDI:
            raise FirmaNonValida("evento troppo vecchio: possibile ripetizione")

        attesa = self.firma(corpo, istante=t).split("v1=", 1)[1]
        # Confronto a tempo costante: un confronto normale si ferma al primo
        # carattere diverso, e il tempo di risposta rivelerebbe quanti ne
        # sono giusti a chi prova firme a tentativi.
        if not hmac.compare_digest(attesa, ricevuta):
            raise FirmaNonValida("firma non valida")

        try:
            evento = json.loads(corpo)
            return EventoPagamento(id=str(evento["id"]), tipo=str(evento["tipo"]), dati=evento.get("dati") or {})
        except (ValueError, KeyError) as exc:
            raise FirmaNonValida("corpo dell'evento illeggibile") from exc

    def evento(self, tipo: str, dati: Dict[str, Any]) -> bytes:
        """Il corpo di un evento, come lo emetterebbe il fornitore."""
        return json.dumps(
            {"id": f"evt_{uuid.uuid4().hex}", "tipo": tipo, "dati": dati},
            separators=(",", ":"), sort_keys=True,
        ).encode("utf-8")

    # -- rinnovi ------------------------------------------------------------

    async def crea_abbonamento(self, user_id: int, piano: Plan, *, annuale: bool = False) -> str:
        return f"mock_sub_{uuid.uuid4().hex[:16]}"

    async def disdici(self, external_id: str) -> None:
        return None

    async def e_pagato(self, external_id: str) -> bool:
        return not self.rinnovo_fallisce

    # -- gestione dell'abbonamento (Fase 2b): il simulatore non ha niente da cambiare presso di sé -----------------

    async def rinnovo_automatico(self, external_id: str, *, attivo: bool) -> None:
        return None

    async def applica_sconto_ricorrente(self, external_id: str, importo: int, valuta: str, *, motivo: str) -> None:
        return None

    async def chiudi_subito(self, external_id: str) -> None:
        return None

    async def programma_cambio(self, external_id: str, piano: Plan, *, annuale: bool, sconto: int, sconto_attuale: int) -> str:
        return f"mock_sched_{uuid.uuid4().hex[:12]}"

    async def annulla_programma(self, programma_id: str) -> None:
        return None

    async def impronta_carta(self, external_id: str) -> Optional[str]:
        """Il simulatore non vede carte: l'impronta, se c'è, arriva con l'evento (le prove la mettono lì)."""
        return None

    async def url_fattura(self, fattura_id: str) -> Optional[str]:
        """La fattura aperta del simulatore si paga dalla sua pagina, come quella ospitata di Stripe."""
        from urllib.parse import quote

        return f"{self._api}/billing/mock/fattura/{quote(fattura_id, safe='')}"


def _cerca(intestazioni: Mapping[str, str], nome: str) -> str:
    for k, v in intestazioni.items():
        if k.lower() == nome:
            return v
    return ""


class PagamentiNonDisponibili(RuntimeError):
    """Nessun fornitore di pagamento configurato."""


class PagamentiDisattivati:
    """Nessun fornitore ancora: i piani gratuiti funzionano, quelli a pagamento aspettano.

    È il modo di andare in produzione prima di aver scelto con chi incassare.
    Il simulatore lì non si può usare — regalerebbe i piani a chiunque apra la
    sua pagina — e senza un fornitore il servizio non partirebbe affatto.
    Qui un pagamento si rifiuta con un motivo che si può mostrare, e nessun
    evento viene accettato: non c'è nessuno autorizzato a mandarne.
    """

    name = "disattivato"

    async def url_di_pagamento(self, checkout: PaymentCheckout, *, ritorno: str, giorni_prova: int = 0) -> str:
        raise PagamentiNonDisponibili(
            "I pagamenti non sono ancora attivi: i piani a pagamento saranno "
            "disponibili a breve."
        )

    async def url_di_pagamento_ordine(self, ordine: "Ordine", *, ritorno: str) -> str:
        """Nessun indirizzo di pagamento: l'ordine resta registrato e «aperto» (in attesa di pagamento), così il
        negozio funziona fino in fondo — carrello, prezzi, sconti, indirizzo, riepilogo — e l'operatore vede in
        console chi avrebbe comprato cosa. Stringa vuota = «il pagamento non è attivo»: `shop.py` lo dice."""
        return ""

    def verifica(self, corpo: bytes, intestazioni: Mapping[str, str]) -> EventoPagamento:
        raise FirmaNonValida("nessun fornitore di pagamento configurato")

    async def crea_abbonamento(self, user_id: int, piano: Plan, *, annuale: bool = False) -> str:
        return f"gratuito-{uuid.uuid4().hex[:12]}"

    async def disdici(self, external_id: str) -> None:
        return None

    async def e_pagato(self, external_id: str) -> bool:
        # Solo ciò che non costava nulla si rinnova: un abbonamento pagato
        # rimasto da un fornitore precedente non ha più chi lo incassi.
        return external_id.startswith("gratuito-")


def provider_pagamenti(settings: Optional[Settings] = None) -> ProviderPagamenti:
    """Il fornitore configurato: il simulatore, o nessuno.

    Un nome sconosciuto è un errore all'avvio e non un ripiego silenzioso sul
    simulatore: in produzione il ripiego significherebbe regalare i piani.
    """
    settings = settings or get_settings()
    # v9 Fase 2c: il fornitore scelto in console, poi l'ambiente; in produzione mai il simulatore.
    from ..configurazioni.correnti import pagamenti as pagamenti_correnti

    nome = pagamenti_correnti(settings).provider
    if nome == "mock":
        return PagamentiSimulati(settings)
    if nome == "disattivato":
        return PagamentiDisattivati()
    if nome == "stripe":
        from .stripe import PagamentiStripe

        return PagamentiStripe(settings)
    raise ValueError(
        f"fornitore di pagamento sconosciuto: «{nome}». "
        f"Oggi sono disponibili `stripe`, `mock` e `disattivato`; un fornitore "
        f"vero si aggiunge implementando ProviderPagamenti."
    )


#: I fornitori che sono store delle app (Fase 4): l'abbonamento si gestisce lì, e lì si decide l'idoneità alla prova.
FORNITORI_STORE = ("google_play", "app_store")


def _istante_evento(valore: Any) -> Optional[Any]:
    """Un istante dell'evento (secondi dall'epoca) come data con fuso; `None` se manca o non si legge."""
    from datetime import datetime, timezone

    if valore in (None, ""):
        return None
    try:
        return datetime.fromtimestamp(int(valore), tz=timezone.utc)
    except (TypeError, ValueError, OverflowError, OSError):
        return None


def canale_di(dati: Mapping[str, Any]) -> str:
    """Il canale scritto nell'evento, se è uno di quelli ammessi; se no `web`: una cassa ospitata è una pagina web,
    anche quando la apre l'app."""
    canale = str(dati.get("canale") or "web")
    return canale if canale in CANALI else "web"


# ---------------------------------------------------------------------------


class GestorePagamenti:
    """Apre le sessioni e applica gli eventi, una volta sola ciascuno."""

    def __init__(self, session: AsyncSession, provider: Optional[ProviderPagamenti] = None) -> None:
        self._session = session
        self._provider = provider or provider_pagamenti()

    @property
    def provider(self) -> ProviderPagamenti:
        return self._provider

    async def apri(
        self, user_id: int, piano: Plan, *, annuale: bool, ritorno: str, sconto: Optional["Sconto"] = None,
        rinnovo: bool = True, sconto_rinnovo: int = 0, residuo: int = 0,
        sostituisce: Optional[Subscription] = None, prova: bool = False, giorni_prova: int = 0,
        sconto_ricorrente: Optional[int] = None,
    ) -> tuple[PaymentCheckout, str]:
        """Apre la sessione. Con un `sconto` l'importo chiesto è quello scontato e il coupon resta sul checkout.

        Fase 2b, per un abbonamento: `sconto_rinnovo` (centesimi) è lo sconto del rinnovo automatico scelto, che vale
        anche sui rinnovi; `residuo` il conguaglio dell'abbonamento `sostituisce` (un upgrade); con `prova` non si
        paga niente adesso (il metodo di pagamento si registra) e `sconto_rinnovo` è lo sconto della prova, per sempre.
        L'importo di adesso è `listino − sconto del rinnovo − coupon − residuo`, mai sotto zero: è quello mostrato
        all'utente, e il fornitore deve addebitare esattamente quello.

        Fase 2d: `sconto` è il solo pezzo del coupon **sopra** lo sconto del rinnovo (il cumulo lo decide
        `offerte.componi`); `sconto_ricorrente` lo sconto con cui partono i rinnovi (vuoto: `sconto_rinnovo`).
        """
        abbonamento = not piano.pacchetto
        listino = piano.price_yearly if annuale and abbonamento else piano.price_monthly
        coupon = sconto.sconto if sconto else 0
        if not abbonamento:
            rinnovo, sconto_rinnovo, residuo, prova = False, 0, 0, False
        importo = 0 if prova else max(0, listino - sconto_rinnovo - coupon - residuo)
        checkout = PaymentCheckout(
            user_id=user_id,
            plan_id=piano.id,
            annuale=annuale and abbonamento,
            status="aperto",
            provider=self._provider.name,
            importo=importo,
            coupon_id=sconto.coupon.id if sconto else None,
            sconto=coupon,
            currency=piano.currency,
            listino=listino,
            rinnovo=rinnovo,
            sconto_rinnovo=sconto_rinnovo,
            residuo=residuo,
            sostituisce_id=sostituisce.id if sostituisce is not None else None,
            prova=prova,
            sconto_ricorrente=sconto_ricorrente if abbonamento else None,
        )
        self._session.add(checkout)
        await self._session.flush()
        checkout.external_id = f"{self._provider.name}_cs_{checkout.id.hex[:16]}"
        # Un fornitore vero sostituisce `external_id` con la sua sessione (Stripe: `cs_…`).
        return checkout, await self._provider.url_di_pagamento(
            checkout, ritorno=ritorno, giorni_prova=giorni_prova if prova else 0,
        )

    async def apri_gratis(self, user_id: int, piano: Plan, sconto: "Sconto") -> PaymentCheckout:
        """Un pacchetto che il coupon porta a zero: non c'è niente da pagare, e quindi nessun fornitore.

        I crediti si accreditano subito, come regalo (`omaggio`, non `acquisto`: i conti delle vendite non devono
        contarli). Un abbonamento non passa di qui: `offerte.valuta` non lascia che un coupon lo azzeri.
        """
        from .credits import RegistroCrediti
        from .offerte import registra_uso

        if not piano.pacchetto or sconto.finale != 0:
            raise ValueError("solo un pacchetto azzerato da un coupon si completa senza pagamento")
        checkout = PaymentCheckout(
            user_id=user_id, plan_id=piano.id, annuale=False, status="pagato", provider="coupon", importo=0,
            coupon_id=sconto.coupon.id, sconto=sconto.sconto, currency=piano.currency, completed_at=utcnow(),
        )
        self._session.add(checkout)
        await self._session.flush()
        checkout.external_id = f"coupon_cs_{checkout.id.hex[:16]}"
        await RegistroCrediti(self._session).accredita(
            user_id, piano.credits_per_period, reason="omaggio",
            note=f"pacchetto {piano.slug} (codice {sconto.coupon.code})",
            canale="web", provider="interno", riferimento_esterno=checkout.external_id,
        )
        await registra_uso(self._session, checkout)
        return checkout

    async def applica(self, evento: EventoPagamento) -> str:
        """Applica un evento verificato. Restituisce cosa è successo.

        Idempotente per identificativo: la riga dell'evento si scrive nella
        stessa transazione dell'effetto, e un secondo invio dello stesso
        evento trova la riga già presente e non fa nulla. I fornitori
        rimandano gli eventi finché non ricevono un 200 — senza, un pagamento
        confermato due volte accrediterebbe due periodi.
        """
        if await self._session.get(PaymentEvent, evento.id) is not None:
            return "già applicato"

        self._session.add(PaymentEvent(
            id=evento.id, provider=self._provider.name, tipo=evento.tipo,
            payload=evento.dati, received_at=utcnow(),
        ))
        try:
            await self._session.flush()
        except IntegrityError:
            # Due repliche che ricevono lo stesso evento nello stesso istante:
            # la seconda perde la corsa sulla chiave primaria, e va bene così.
            await self._session.rollback()
            return "già applicato"

        if evento.tipo == PAGATO:
            return await self._pagato(evento)
        if evento.tipo == ANNULLATO:
            return await self._chiudi_checkout(evento, "annullato")
        if evento.tipo == SCADUTO:
            return await self._chiudi_checkout(evento, "scaduto")
        if evento.tipo == RINNOVATO:
            return await self._rinnovato(evento)
        if evento.tipo == RINNOVO_FALLITO:
            return await self._pagamento_fallito(evento)
        if evento.tipo == PROVA_IN_SCADENZA:
            return await self._prova_in_scadenza(evento)
        if evento.tipo == ABBONAMENTO_AGGIORNATO:
            return await self._aggiornato(evento)
        if evento.tipo == ABBONAMENTO_CHIUSO:
            return await self._stato_abbonamento(evento, "disdetto")
        if evento.tipo == STORNO:
            return await self._storno(evento)
        if evento.tipo == STORNO_ANNULLATO:
            return await self._storno_annullato(evento)

        logger.info("Evento di pagamento ignorato: %s", evento.tipo)
        return "ignorato"

    async def _checkout(self, evento: EventoPagamento) -> Optional[PaymentCheckout]:
        try:
            checkout_id = uuid.UUID(str(evento.dati.get("checkout_id")))
        except ValueError:
            return None
        return await self._session.get(PaymentCheckout, checkout_id)

    async def _pagato(self, evento: EventoPagamento) -> str:
        from .plans import GestoreAbbonamenti

        checkout = await self._checkout(evento)
        if checkout is None:
            return "checkout sconosciuto"
        if checkout.status != "aperto":
            # Pagato dopo essere stato annullato o scaduto: è un caso che il
            # fornitore può produrre, e va visto da una persona, non risolto
            # attivando in silenzio.
            logger.warning("Pagamento per un checkout %s: %s", checkout.status, checkout.id)
            return f"checkout {checkout.status}"

        checkout.status = "pagato"
        checkout.completed_at = utcnow()

        from ..analytics import eventi as analytics

        if not checkout.sandbox:
            # Fase 4: un acquisto di prova degli store (tester, App Review) accredita, ma non è un acquisto vero.
            await analytics.evento(
                self._session, analytics.ACQUISTO, utente_id=checkout.user_id,
                valore_centesimi=checkout.importo, valuta=checkout.currency,
                proprieta={
                    "tipo": "crediti" if checkout.plan.pacchetto else "abbonamento", "piano": checkout.plan.slug,
                    "annuale": checkout.annuale, "coupon": checkout.coupon_id is not None,
                },
            )

        from .offerte import registra_uso
        from .referral import commissione_da_acquisto

        # L'incasso presso il fornitore (Stripe: il PaymentIntent di un pacchetto, la prima fattura di un
        # abbonamento): è ciò che un rimborso citerà, e con cui lo storno ritroverà questi crediti.
        riferimento = str(evento.dati.get("riferimento") or checkout.external_id or checkout.id)
        canale = canale_di(evento.dati)

        if checkout.plan.pacchetto:
            # Un pacchetto non apre abbonamenti: accredita i suoi crediti, che
            # non scadono perché sono stati pagati.
            from .credits import RegistroCrediti

            await RegistroCrediti(self._session).accredita(
                checkout.user_id, checkout.plan.credits_per_period,
                reason="acquisto", note=f"pacchetto {checkout.plan.slug}",
                canale=canale, provider=self._provider.name, riferimento_esterno=riferimento,
            )
            await registra_uso(self._session, checkout)       # l'uso del coupon si conta a pagamento avvenuto
            if not checkout.sandbox:
                await commissione_da_acquisto(self._session, checkout.user_id, checkout.plan.credits_per_period)
            return "crediti accreditati"

        checkout.subscription_external_id = str(
            evento.dati.get("subscription_id") or f"{self._provider.name}_sub_{checkout.id.hex[:16]}"
        )

        if checkout.prova and self._provider.name not in FORNITORI_STORE:
            # Negli store l'idoneità alla prova la decide lo store (Google: mai abbonati; Apple: una per gruppo), e lo
            # store addebiterà comunque alla fine: rifiutarla qui lascerebbe l'utente a pagare senza abbonamento.
            rifiutata = await self._prova_rifiutata(checkout, evento)
            if rifiutata:
                # La prova rifiutata non ha prodotto niente: il coupon non risulta usato (un codice monouso resta
                # buono per un acquisto vero). Per questo l'uso si registra solo dopo questo controllo.
                return rifiutata

        await registra_uso(self._session, checkout)           # l'uso del coupon si conta a pagamento avvenuto

        from . import abbonamenti as gestione

        riga = await gestione.impostazioni(self._session)
        # Lo sconto dei rinnovi: quello della prova (per sempre) o del rinnovo automatico scelto; nessuno senza rinnovo.
        sconto_ricorrente = checkout.sconto_rinnovo if (checkout.rinnovo or checkout.prova) else 0
        if checkout.sconto_ricorrente is not None and (checkout.rinnovo or checkout.prova):
            sconto_ricorrente = checkout.sconto_ricorrente          # Fase 2d: col coupon che continua sui rinnovi
        abbonamento = await GestoreAbbonamenti(self._session, self._provider).sottoscrivi(
            checkout.user_id, checkout.plan, annuale=checkout.annuale,
            external_id=checkout.subscription_external_id,
            fornitore=self._provider.name, canale=canale, riferimento=riferimento,
            listino=checkout.listino, importo=checkout.importo, sconto_ricorrente=sconto_ricorrente,
            prova=checkout.prova, giorni_prova=riga.giorni_prova, sostituisce=checkout.sostituisce_id,
            fine=_istante_evento(evento.dati.get("fine")),
        )
        from .offerte import lega_abbonamento, motivo_sconto

        await lega_abbonamento(self._session, abbonamento, checkout)       # Fase 2d: il coupon sui rinnovi
        esterno = abbonamento.external_id if abbonamento.provider == self._provider.name else None
        if checkout.prova and await gestione.prova_di(self._session, checkout.user_id) is None:
            # Una riga per persona: una prova dello store dopo quella del sito (l'ha concessa lo store) non ne scrive
            # una seconda.
            from ..domain.abbonamenti_models import ProvaGratuita

            self._session.add(ProvaGratuita(
                user_id=checkout.user_id, subscription_id=abbonamento.id, provider=abbonamento.provider,
                impronta_carta=await self._impronta(checkout, evento),
            ))
        elif not checkout.rinnovo:
            # Comprato senza rinnovo automatico: un periodo, al listino, e poi niente (riaccendibile fino alla fine).
            if esterno and hasattr(self._provider, "rinnovo_automatico"):
                await self._provider.rinnovo_automatico(esterno, attivo=False)
            abbonamento.cancel_at = abbonamento.period_end
        elif sconto_ricorrente > 0 and esterno and hasattr(self._provider, "applica_sconto_ricorrente"):
            # Il primo pagamento aveva il suo sconto d'una volta (rinnovo + coupon + conguaglio); i rinnovi hanno solo
            # quello del rinnovo automatico, ora che il primo è incassato.
            await self._provider.applica_sconto_ricorrente(
                esterno, sconto_ricorrente, checkout.currency, motivo=motivo_sconto(abbonamento),
            )
        await self._session.flush()
        # La commissione di chi ha invitato: una percentuale di quanto è stato pagato adesso (zero per una prova).
        from .referral import commissione_da_abbonamento

        await commissione_da_abbonamento(
            self._session, checkout.user_id, 0 if checkout.sandbox else checkout.importo, riferimento=riferimento,
        )
        if checkout.prova:
            return "prova attivata"
        return "abbonamento cambiato" if checkout.sostituisce_id else "abbonamento attivato"

    async def _impronta(self, checkout: PaymentCheckout, evento: EventoPagamento) -> Optional[str]:
        """L'impronta della carta registrata per la prova: dall'evento, o chiesta al fornitore. Mai un errore."""
        impronta = evento.dati.get("impronta")
        if impronta:
            return str(impronta)[:64]
        chiedi = getattr(self._provider, "impronta_carta", None)
        if chiedi is None or not checkout.subscription_external_id:
            return None
        try:
            trovata = await chiedi(checkout.subscription_external_id)
        except PagamentiNonDisponibili:
            logger.warning("Impronta della carta non disponibile per %s", checkout.subscription_external_id)
            return None
        return str(trovata)[:64] if trovata else None

    async def _prova_rifiutata(self, checkout: PaymentCheckout, evento: EventoPagamento) -> Optional[str]:
        """Una prova per persona e per carta: se l'utente l'ha già avuta, o la carta l'ha già avuta su un altro
        account, l'abbonamento appena nato presso il fornitore si chiude subito (in prova: niente è stato addebitato)
        e la pagina di ritorno lo dice."""
        from . import abbonamenti as gestione

        motivo = None
        if await gestione.prova_di(self._session, checkout.user_id) is not None:
            motivo = "prova_gia_usata"
        elif await gestione.impronta_gia_usata(self._session, await self._impronta(checkout, evento), checkout.user_id):
            motivo = "carta_gia_usata"
        if motivo is None:
            return None
        chiudi = getattr(self._provider, "chiudi_subito", None)
        if chiudi is not None and checkout.subscription_external_id:
            await chiudi(checkout.subscription_external_id)
        checkout.esito = motivo
        logger.warning("Prova rifiutata (%s) per l'utente %s", motivo, checkout.user_id)
        return f"prova rifiutata: {motivo}"

    async def _chiudi_checkout(self, evento: EventoPagamento, stato: str) -> str:
        checkout = await self._checkout(evento)
        if checkout is None:
            return "checkout sconosciuto"
        if checkout.status == "aperto":
            checkout.status = stato
            checkout.completed_at = utcnow()
        return f"checkout {checkout.status}"

    async def _abbonamento(self, evento: EventoPagamento) -> Optional[Subscription]:
        """L'abbonamento citato dall'evento: il più recente con quell'id del fornitore."""
        external_id = str(evento.dati.get("subscription_id") or "")
        if not external_id:
            return None
        return (await self._session.execute(
            select(Subscription).where(Subscription.external_id == external_id)
            .order_by(Subscription.created_at.desc()).limit(1)
        )).scalar_one_or_none()

    async def _stato_abbonamento(self, evento: EventoPagamento, stato: str) -> str:
        abbonamento = await self._abbonamento(evento)
        if abbonamento is None:
            return "abbonamento sconosciuto"
        abbonamento.status = stato
        if stato == "sospeso" and evento.dati.get("riferimento"):
            # La fattura non pagata: si torna a pagare quella (la sua pagina presso il fornitore), mai una seconda.
            abbonamento.fattura_aperta = str(evento.dati["riferimento"])
        if stato == "disdetto":
            # Il fornitore l'ha chiuso: chi lo aveva torna sul piano gratuito, come alla fine di una disdetta.
            from .plans import GestoreAbbonamenti

            await self._session.flush()
            await GestoreAbbonamenti(self._session, self._provider).apri_piano_base(abbonamento.user_id)
        return f"abbonamento {stato}"

    async def _rinnovato(self, evento: EventoPagamento) -> str:
        """Il fornitore ha incassato un nuovo periodo (Stripe `invoice.paid` di un ciclo): si rinnova, una volta.

        Non passa da `e_pagato`: l'evento stesso dice che è pagato. L'idempotenza è doppia — l'id dell'evento in
        `payment_events` e il riferimento della fattura sulla riga dei crediti.
        """
        from datetime import datetime, timezone

        from .plans import GestoreAbbonamenti

        abbonamento = await self._abbonamento(evento)
        if abbonamento is None:
            return "abbonamento sconosciuto"
        fine = None
        if evento.dati.get("fine"):
            try:
                fine = datetime.fromtimestamp(int(evento.dati["fine"]), tz=timezone.utc)
            except (TypeError, ValueError):
                fine = None
        importo = evento.dati.get("importo")
        esito = await GestoreAbbonamenti(self._session, self._provider).rinnova(
            abbonamento, pagato=True, riferimento=evento.dati.get("riferimento") or None, fine=fine,
            canale=canale_di(evento.dati), importo=int(importo) if isinstance(importo, (int, float)) else None,
        )
        abbonamento.fattura_aperta = None
        abbonamento.pagamento_fallito_il = None
        return esito.motivo or "abbonamento rinnovato"

    async def _pagamento_fallito(self, evento: EventoPagamento) -> str:
        """Un rinnovo non pagato (Stripe `invoice.payment_failed`): la tolleranza, non la sospensione (Fase 2b).

        Le letture comprese restano per i giorni di tolleranza, l'utente riceve l'email con la fattura da saldare, e
        Stripe intanto riprova (Smart Retries). I tentativi successivi dello stesso giro non riaprono niente.
        """
        from .abbonamenti import apri_tolleranza

        abbonamento = await self._abbonamento(evento)
        if abbonamento is None:
            return "abbonamento sconosciuto"
        return await apri_tolleranza(self._session, abbonamento, fattura=str(evento.dati.get("riferimento") or "") or None)

    async def _prova_in_scadenza(self, evento: EventoPagamento) -> str:
        """La prova finisce presto secondo il fornitore: si allinea la fine (il promemoria lo manda il cron)."""
        from datetime import datetime, timezone

        abbonamento = await self._abbonamento(evento)
        if abbonamento is None:
            return "abbonamento sconosciuto"
        fine = evento.dati.get("fine")
        if abbonamento.status == "in_prova" and fine:
            nuova = datetime.fromtimestamp(int(fine), tz=timezone.utc)
            if nuova > abbonamento.period_start:
                abbonamento.period_end = nuova
        return "prova in scadenza"

    #: Gli stati di Stripe e i nostri (Fase 2b). `past_due` è la tolleranza (`in_sospeso`): Stripe riprova e intanto
    #: le letture comprese restano. `unpaid` e `paused` sono «sospeso»: Stripe ha smesso di riprovare.
    STATI_FORNITORE = {
        "active": "attivo", "trialing": "in_prova", "past_due": "in_sospeso", "unpaid": "sospeso", "paused": "sospeso",
        "canceled": "disdetto", "incomplete_expired": "scaduto",
    }

    async def _aggiornato(self, evento: EventoPagamento) -> str:
        """Lo stato locale segue quello del fornitore, senza mai accreditare (i crediti li dà solo `RINNOVATO`).

        Un abbonamento già chiuso qui (`disdetto`, `scaduto`) non torna vivo per un aggiornamento: succede quando
        l'utente passa a un altro piano e il vecchio resta «active» presso Stripe fino a fine periodo. Solo un
        incasso lo riaprirebbe. `disdetta_a_fine_periodo` è il rinnovo automatico spento (`cancel_at_period_end`):
        si segna come una disdetta, e si toglie se l'utente lo riaccende.
        """
        from datetime import datetime, timezone

        abbonamento = await self._abbonamento(evento)
        if abbonamento is None:
            return "abbonamento sconosciuto"
        if abbonamento.status in ("disdetto", "scaduto"):
            return f"abbonamento {abbonamento.status}: invariato"

        # Gli store (Fase 4) traducono già i loro stati nei nostri (`stato`); Stripe manda i suoi (`stato_fornitore`).
        stato = evento.dati.get("stato") if evento.dati.get("stato") in STATI_ABBONAMENTO else None
        stato = stato or self.STATI_FORNITORE.get(str(evento.dati.get("stato_fornitore") or ""))
        if stato == "in_sospeso":
            if abbonamento.status == "sospeso":
                # La tolleranza è già finita qui (il cron l'ha chiusa): Stripe che riprova non la riapre.
                stato = "sospeso"
            elif abbonamento.pagamento_fallito_il is None:
                abbonamento.pagamento_fallito_il = utcnow()
        if stato in ("attivo", "in_prova"):
            abbonamento.pagamento_fallito_il = None
        if stato:
            abbonamento.status = stato
        if stato in ("attivo", "in_prova", "in_sospeso", "sospeso"):
            if evento.dati.get("disdetta_a_fine_periodo"):
                fine = evento.dati.get("fine")
                abbonamento.cancel_at = (
                    datetime.fromtimestamp(int(fine), tz=timezone.utc) if fine else abbonamento.period_end
                )
            else:
                abbonamento.cancel_at = None
        if stato in ("disdetto", "scaduto"):
            from .plans import GestoreAbbonamenti

            await self._session.flush()
            await GestoreAbbonamenti(self._session, self._provider).apri_piano_base(abbonamento.user_id)
        return f"abbonamento {abbonamento.status}"

    async def _storno(self, evento: EventoPagamento) -> str:
        """Un incasso tornato indietro: rimborso del fornitore o contestazione (chargeback).

        Si ritrovano i crediti che quell'incasso aveva dato (per i suoi riferimenti: PaymentIntent, addebito,
        fattura) e si stornano — in proporzione, se il rimborso è parziale. Il saldo può andare sotto zero: i
        crediti possono essere già stati spesi (`RegistroCrediti.storna`).

        **La commissione di chi ha invitato non si storna mai** (regola dell'operatore, v9 Fase 2b): è un `omaggio` in
        crediti a un'altra persona, non denaro, e il rimborso dell'acquirente non la tocca. Per questo qui si cercano
        solo `acquisto` e `accredito_piano`.
        """
        from .credits import RegistroCrediti

        registro = RegistroCrediti(self._session)
        riferimenti = [str(r) for r in evento.dati.get("riferimenti") or [] if r]
        voci = await registro.per_riferimenti(self._provider.name, riferimenti, ("acquisto", "accredito_piano"))
        collegati = getattr(self._provider, "riferimenti_collegati", None)
        if not voci and collegati is not None:
            # Il fornitore sa dire quale fattura ha pagato quell'addebito (Stripe, dal 2025): si cerca anche con quella.
            voci = await registro.per_riferimenti(
                self._provider.name, await collegati(riferimenti), ("acquisto", "accredito_piano"),
            )
        if not voci:
            # Un ordine del negozio, o un incasso di prima del registro multicanale: niente crediti da togliere qui.
            # Se andavano tolti, lo storno si registra a mano dalla console (scheda dell'utente).
            logger.warning(
                "Storno senza crediti collegati (%s): %s", evento.tipo, evento.dati.get("riferimenti"),
            )
            return "storno senza crediti collegati"

        importo = int(evento.dati.get("importo") or 0)
        stornato = evento.dati.get("importo_stornato")
        causa = str(evento.dati.get("causa") or "rimborso")
        nuovi = 0
        for voce in voci:
            quanti = voce.delta
            if importo > 0 and stornato is not None and 0 < int(stornato) < importo:
                # Rimborso parziale: la parte corrispondente, arrotondata, mai zero.
                quanti = max(1, (voce.delta * int(stornato) + importo // 2) // importo)
            _, nuovo = await registro.storna(
                voce.user_id, quanti, provider=voce.provider,
                riferimento_esterno=str(voce.riferimento_esterno),
                note=f"{causa} presso {self._provider.name}", expires_at=voce.expires_at,
            )
            nuovi += int(nuovo)
        return "crediti stornati" if nuovi else "storno già registrato"

    async def _storno_annullato(self, evento: EventoPagamento) -> str:
        """Una contestazione vinta: il denaro è tornato, e i crediti stornati con lei tornano all'utente."""
        from .credits import RegistroCrediti

        registro = RegistroCrediti(self._session)
        riferimenti = [str(r) for r in evento.dati.get("riferimenti") or [] if r]
        storni = await registro.per_riferimenti(self._provider.name, riferimenti, ("storno",))
        collegati = getattr(self._provider, "riferimenti_collegati", None)
        if not storni and collegati is not None:
            storni = await registro.per_riferimenti(self._provider.name, await collegati(riferimenti), ("storno",))
        nuovi = 0
        for storno in storni:
            fatto = await registro.annulla_storno(
                storno.provider, str(storno.riferimento_esterno), note=f"contestazione vinta presso {self._provider.name}",
            )
            if fatto is not None:
                nuovi += int(fatto[1])
        if not storni:
            return "nessuno storno da annullare"
        return "storno annullato" if nuovi else "storno già annullato"
