"""Stripe: la cassa del sito (v9, Fase 2).

Un'implementazione di `ProviderPagamenti` che parla con la REST API di Stripe
con httpx, a moduli form-encoded come la vuole Stripe. **Niente SDK**: le
chiamate sono poche (sessione di Checkout, Price dei piani, coupon d'una volta,
rinnovo automatico, stato di un abbonamento, fatture) e le prove le
sostituiscono con un `MockTransport` (`TRASPORTO`), come per Keycloak e i
social. Nessuna prova parla con Stripe.

**La cassa è Checkout**, la pagina ospitata da Stripe: carte, Apple Pay e
Google Pay (sul web, se attivi nella dashboard e con il dominio verificato per
Apple Pay), SCA/3-D Secure, ricevute. Il sito non vede mai una carta.

- un **pacchetto** o un **ordine** del negozio → `mode=payment`, una riga con
  l'importo già calcolato qui;
- un **abbonamento** → `mode=subscription`, con un **Price** vero di Stripe
  per piano e intervallo (trovato per `lookup_key` o creato al primo uso), al
  listino: una Subscription vera, che si potrà cambiare di piano con il
  conguaglio, mettere in prova e spegnere/riaccendere (`cancel_at_period_end`).

**Il coupon resta nostro** (`billing/offerte.py`): a Stripe si manda solo
l'importo, mai la regola. Per un pacchetto è semplice: l'importo è già
scontato. Per un abbonamento lo sconto vale solo sul primo pagamento, e
l'unico modo di dirlo a Stripe è uno sconto d'una volta: si crea un coupon
Stripe con il solo importo da togliere (`amount_off`, `duration=once`,
`max_redemptions=1`), senza codice né regole.

**Fase 2b: sconti, conguaglio e prova, al centesimo.** Il Price resta sempre il listino. Il primo pagamento ha un
solo coupon d'una volta pari a tutto ciò che sconta (rinnovo automatico, coupon, valore residuo di un upgrade):
Stripe addebita esattamente il totale mostrato. Lo sconto dei rinnovi è un coupon `duration=forever` di **importo
fisso** (`tarots_rinnovo_<centesimi>_eur`, non una percentuale che Stripe arrotonderebbe a modo suo), messo
sull'abbonamento dal webhook a pagamento avvenuto. Spegnere il rinnovo è `cancel_at_period_end`: senza rinnovi, lo
sconto non si applica più a niente. L'**upgrade** chiude il vecchio abbonamento subito, senza rimborso
(`DELETE /subscriptions/{id}`, `prorate=false`) e ne apre uno nuovo dal Checkout col coupon del conguaglio: la
proration di Stripe calcola al secondo e sul prezzo di listino, non su quanto è stato pagato davvero, e non
coinciderebbe con le tre righe mostrate. Il **downgrade** è un programma (subscription schedule) che cambia prezzo
alla fine del periodo. La **prova** è un Checkout con `trial_period_days` e il coupon «per sempre» della prova;
l'impronta della carta (`card.fingerprint`) dà una prova per carta.

**Gli eventi** arrivano al webhook firmati (`Stripe-Signature`: `t=…,v1=…`,
HMAC-SHA256 di `t.corpo` con il segreto dell'endpoint, cinque minuti di
tolleranza) e si traducono qui negli eventi della piattaforma
(`billing/pagamenti.py`): il resto del codice non sa come li chiama Stripe.

| Stripe | piattaforma |
|---|---|
| `checkout.session.completed` (pagato), `…async_payment_succeeded` | `checkout.pagato` / `ordine.pagato` |
| `checkout.session.expired`, `…async_payment_failed` | `checkout.scaduto`/`annullato` / `ordine.annullato` |
| `invoice.paid` di un ciclo | `abbonamento.rinnovato` |
| `invoice.payment_failed` | `abbonamento.pagamento_fallito` (tolleranza `in_sospeso`, con la fattura aperta) |
| `customer.subscription.trial_will_end` | `abbonamento.prova_in_scadenza` (allinea la fine della prova) |
| `customer.subscription.updated` | `abbonamento.aggiornato` (stato e rinnovo automatico, mai crediti) |
| `customer.subscription.deleted` | `abbonamento.annullato` (disdetto) |
| `charge.refunded`, `charge.dispute.created` | `pagamento.stornato` |
| `charge.dispute.closed` vinta | `pagamento.storno_annullato` |

La prima fattura di un abbonamento (`invoice.paid` con
`billing_reason=subscription_create`) non rinnova niente: il primo periodo
lo apre `checkout.session.completed`. Gli altri eventi si registrano e si
ignorano.

**Le versioni dell'API di Stripe** cambiano la forma di alcuni oggetti (dal
2025 la fattura dice l'abbonamento in `parent.subscription_details` e
l'addebito non cita più la fattura). La traduzione legge entrambe le forme,
e per un rimborso di cui non trova la fattura la chiede a Stripe
(`riferimenti_collegati`).
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time
import uuid
from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional
from urllib.parse import quote, urlencode, urlsplit

import httpx

from ..domain.billing_models import PaymentCheckout, Plan
from ..settings import Settings, get_settings
from .pagamenti import (
    ABBONAMENTO_AGGIORNATO, ABBONAMENTO_CHIUSO, ANNULLATO, PAGATO, PROVA_IN_SCADENZA, RINNOVATO, RINNOVO_FALLITO, SCADUTO, STORNO, STORNO_ANNULLATO,
    TOLLERANZA_SECONDI, EventoPagamento, FirmaNonValida, PagamentiNonDisponibili, _cerca,
)

if TYPE_CHECKING:  # pragma: no cover
    from ..domain.ordini_models import Ordine

logger = logging.getLogger(__name__)

API = "https://api.stripe.com/v1"
TIMEOUT = 20.0

#: Le prove sostituiscono la rete con un `httpx.MockTransport` qui.
TRASPORTO: Optional[httpx.AsyncBaseTransport] = None

#: Gli eventi da abilitare sull'endpoint del webhook nella dashboard di Stripe (LEGGIMI, «Stripe»), e che la console
#: mostra all'operatore.
EVENTI = (
    "checkout.session.completed",
    "checkout.session.async_payment_succeeded",
    "checkout.session.async_payment_failed",
    "checkout.session.expired",
    "invoice.paid",
    "invoice.payment_failed",
    "customer.subscription.updated",
    "customer.subscription.deleted",
    "customer.subscription.trial_will_end",
    "charge.refunded",
    "charge.dispute.created",
    "charge.dispute.closed",
)


class ErroreStripe(PagamentiNonDisponibili):
    """Stripe non ha risposto, o ha risposto con un errore: si mostra un 503 che non rivela i dettagli."""


def firma(corpo: bytes, segreto: str, *, istante: Optional[int] = None) -> str:
    """L'intestazione `Stripe-Signature` che Stripe metterebbe su questo corpo. Serve alle prove e alla verifica."""
    t = istante if istante is not None else int(time.time())
    mac = hmac.new(segreto.encode("utf-8"), f"{t}.".encode("utf-8") + corpo, hashlib.sha256).hexdigest()
    return f"t={t},v1={mac}"


def _modulo(dati: Mapping[str, Any], prefisso: str = "") -> List[tuple[str, str]]:
    """Da un dizionario annidato ai campi form-encoded di Stripe: `line_items[0][price_data][currency]=eur`."""
    campi: List[tuple[str, str]] = []
    for chiave, valore in dati.items():
        nome = f"{prefisso}[{chiave}]" if prefisso else str(chiave)
        if valore is None:
            continue
        if isinstance(valore, Mapping):
            campi += _modulo(valore, nome)
        elif isinstance(valore, (list, tuple)):
            for i, elemento in enumerate(valore):
                if isinstance(elemento, Mapping):
                    campi += _modulo(elemento, f"{nome}[{i}]")
                else:
                    campi.append((f"{nome}[{i}]", _testo(elemento)))
        else:
            campi.append((nome, _testo(valore)))
    return campi


def _testo(valore: Any) -> str:
    if isinstance(valore, bool):
        return "true" if valore else "false"
    return str(valore)


def _separatore(indirizzo: str) -> str:
    return "&" if "?" in indirizzo else "?"


class PagamentiStripe:
    """Il fornitore Stripe. Le chiavi vengono dalla console (cifrate nel database), o come ripiego dall'ambiente
    (v9, Fase 2c: `configurazioni/correnti.py`)."""

    name = "stripe"

    def __init__(self, settings: Optional[Settings] = None) -> None:
        from ..configurazioni.correnti import pagamenti as pagamenti_correnti

        settings = settings or get_settings()
        correnti = pagamenti_correnti(settings)
        self._chiave = correnti.chiave_segreta
        self._segreto = correnti.segreto_webhook
        self._api_pubblica = settings.api_public_url.rstrip("/")

    # -- chiamate ----------------------------------------------------------

    async def _chiama(
        self, metodo: str, percorso: str, dati: Optional[Mapping[str, Any]] = None, *,
        idempotenza: Optional[str] = None, nulla_se_assente: bool = False,
    ) -> Dict[str, Any]:
        if not self._chiave:
            raise ErroreStripe("I pagamenti non sono ancora attivi: riprova più tardi.")
        intestazioni = {"Authorization": f"Bearer {self._chiave}"}
        corpo = None
        if dati is not None and metodo != "GET":
            intestazioni["Content-Type"] = "application/x-www-form-urlencoded"
            corpo = urlencode(_modulo(dati))
        if idempotenza:
            # Un secondo tentativo della stessa richiesta (un timeout, un doppio clic) riceve la stessa sessione.
            intestazioni["Idempotency-Key"] = idempotenza
        parametri = _modulo(dati) if dati is not None and metodo == "GET" else None
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT, transport=TRASPORTO) as client:
                risposta = await client.request(
                    metodo, f"{API}{percorso}", content=corpo, params=parametri, headers=intestazioni,
                )
        except httpx.HTTPError as exc:
            logger.error("Stripe non raggiungibile (%s %s): %s", metodo, percorso, exc)
            raise ErroreStripe("Il pagamento non è disponibile in questo momento: riprova fra poco.") from exc
        if risposta.status_code == 404 and nulla_se_assente:
            return {}
        if risposta.status_code >= 400:
            try:
                messaggio = risposta.json().get("error", {}).get("message", "")
            except ValueError:
                messaggio = risposta.text[:200]
            logger.error("Stripe ha rifiutato %s %s (%s): %s", metodo, percorso, risposta.status_code, messaggio)
            raise ErroreStripe("Il pagamento non è disponibile in questo momento: riprova fra poco.")
        return risposta.json()

    # -- pagine di pagamento -----------------------------------------------

    def _ritorno(self, ritorno: str) -> str:
        """Stripe torna solo a indirizzi web: un deep link dell'app passa dal rimbalzo dell'API, che lo riconvalida."""
        if urlsplit(ritorno).scheme in ("http", "https"):
            return ritorno
        return f"{self._api_pubblica}/billing/ritorno-app?verso={quote(ritorno, safe='')}"

    async def url_di_pagamento(self, checkout: PaymentCheckout, *, ritorno: str, giorni_prova: int = 0) -> str:
        piano = checkout.plan
        torna = self._ritorno(f"{ritorno}{_separatore(ritorno)}checkout={checkout.id}")
        metadati = {
            "tipo": "piano", "checkout_id": str(checkout.id), "user_id": str(checkout.user_id), "piano": piano.slug,
        }
        prezzo: Dict[str, Any] = {"currency": checkout.currency.lower(), "product_data": {"name": piano.name}}
        dati: Dict[str, Any] = {
            "client_reference_id": str(checkout.id), "metadata": metadati,
            "success_url": torna, "cancel_url": torna, "locale": "auto",
            "line_items": [{"price_data": prezzo, "quantity": 1}],
        }
        if piano.pacchetto:
            dati["mode"] = "payment"
            prezzo["unit_amount"] = checkout.importo
            dati["payment_intent_data"] = {"metadata": metadati}
        else:
            dati["mode"] = "subscription"
            # Un Price vero di Stripe per piano e intervallo, **al listino** (Fase 2b). Tutto ciò che il primo
            # pagamento sconta — rinnovo automatico, coupon, conguaglio di un upgrade — è un solo coupon d'una volta
            # con l'importo esatto (`amount_off`): Checkout ne accetta uno, e così Stripe addebita al centesimo il
            # totale che l'utente ha visto. Lo sconto dei rinnovi lo mette il webhook, a pagamento avvenuto
            # (`applica_sconto_ricorrente`). La prova è l'eccezione: niente da pagare adesso, e lo sconto per sempre
            # sta già nel Checkout.
            listino = checkout.listino if checkout.listino is not None else checkout.importo + checkout.sconto
            metadati.update({
                "rinnovo": "1" if checkout.rinnovo else "0", "prova": "1" if checkout.prova else "0",
                **({"sostituisce": str(checkout.sostituisce_id)} if checkout.sostituisce_id else {}),
            })
            dati["line_items"] = [{"price": await self._prezzo_ricorrente(
                piano, annuale=checkout.annuale, importo=listino, valuta=checkout.currency.lower(),
            ), "quantity": 1}]
            dati["subscription_data"] = {"metadata": metadati}
            if checkout.prova:
                # Il metodo di pagamento si registra adesso (sempre, anche se oggi non si paga niente); alla fine della
                # prova Stripe addebita l'annuale con lo sconto della prova, per sempre.
                dati["subscription_data"]["trial_period_days"] = max(1, giorni_prova)
                dati["payment_method_collection"] = "always"
                # Fase 2d: con un coupon, lo sconto della conversione è quello composto (prova più o contro il
                # coupon); quando il coupon finisce il webhook lo riporta alla sola prova.
                ricorrente = checkout.sconto_ricorrente if checkout.sconto_ricorrente is not None else checkout.sconto_rinnovo
                if ricorrente > 0:
                    dati["discounts"] = [{"coupon": await self._coupon_ricorrente(
                        ricorrente, checkout.currency,
                        motivo="prova" if ricorrente == checkout.sconto_rinnovo else "sconto",
                    )}]
            elif listino - checkout.importo > 0:
                coupon = await self._chiama("POST", "/coupons", {
                    "amount_off": listino - checkout.importo, "currency": checkout.currency.lower(), "duration": "once",
                    "max_redemptions": 1, "name": "Sconto TAROTS chat", "metadata": {"checkout_id": str(checkout.id)},
                }, idempotenza=f"coupon-{checkout.id}")
                dati["discounts"] = [{"coupon": coupon["id"]}]
        sessione = await self._chiama("POST", "/checkout/sessions", dati, idempotenza=f"checkout-{checkout.id}")
        checkout.external_id = str(sessione["id"])
        return str(sessione["url"])

    async def _prezzo_ricorrente(self, piano: Plan, *, annuale: bool, importo: int, valuta: str) -> str:
        """Il Price di Stripe di un piano e di un intervallo, trovato per `lookup_key` o creato.

        La chiave è stabile (`tarots_<piano>_<mese|anno>`); se il listino è cambiato in console, il Price nuovo se la
        prende (`transfer_lookup_key`) e i vecchi abbonati restano sul loro prezzo finché non si decide altrimenti,
        come vuole Stripe. Il prodotto nasce con il Price (`product_data`).
        """
        intervallo = "year" if annuale else "month"
        chiave = f"tarots_{piano.slug}_{'anno' if annuale else 'mese'}"
        trovati = await self._chiama("GET", "/prices", {"lookup_keys": [chiave], "active": True, "limit": 1})
        for prezzo in trovati.get("data") or []:
            if (
                prezzo.get("unit_amount") == importo and prezzo.get("currency") == valuta
                and (prezzo.get("recurring") or {}).get("interval") == intervallo
            ):
                return str(prezzo["id"])
        nuovo = await self._chiama("POST", "/prices", {
            "currency": valuta, "unit_amount": importo, "recurring": {"interval": intervallo},
            "lookup_key": chiave, "transfer_lookup_key": True,
            "product_data": {"name": piano.name, "metadata": {"piano": piano.slug}},
            "metadata": {"piano": piano.slug},
        }, idempotenza=f"prezzo-{chiave}-{importo}-{valuta}")
        return str(nuovo["id"])

    async def url_di_pagamento_ordine(self, ordine: "Ordine", *, ritorno: str) -> str:
        torna = self._ritorno(f"{ritorno}{_separatore(ritorno)}ordine={ordine.id}")
        n = sum(r.quantita for r in ordine.righe)
        metadati = {"tipo": "ordine", "ordine_id": str(ordine.id), "user_id": str(ordine.user_id)}
        sessione = await self._chiama("POST", "/checkout/sessions", {
            "mode": "payment", "client_reference_id": str(ordine.id), "metadata": metadati,
            "payment_intent_data": {"metadata": metadati},
            "success_url": torna, "cancel_url": torna, "locale": "auto",
            # Una riga sola con il totale: lo sconto a scaglioni vale sull'ordine intero, non sulle righe.
            "line_items": [{"quantity": 1, "price_data": {
                "currency": ordine.valuta.lower(), "unit_amount": ordine.importo_totale,
                "product_data": {"name": f"TAROTS chat — {n} {'mazzo' if n == 1 else 'mazzi'}"},
            }}],
        }, idempotenza=f"ordine-{ordine.id}")
        ordine.external_id = str(sessione["id"])
        return str(sessione["url"])

    # -- eventi ------------------------------------------------------------

    def verifica(self, corpo: bytes, intestazioni: Mapping[str, str]) -> EventoPagamento:
        if not self._segreto:
            raise FirmaNonValida("Stripe non configurato: manca il segreto del webhook")
        intestazione = _cerca(intestazioni, "stripe-signature")
        if not intestazione:
            raise FirmaNonValida("firma assente")

        t: Optional[int] = None
        firme: List[str] = []
        for parte in intestazione.split(","):
            chiave, _, valore = parte.strip().partition("=")
            if chiave == "t":
                try:
                    t = int(valore)
                except ValueError as exc:
                    raise FirmaNonValida("firma malformata") from exc
            elif chiave == "v1":
                firme.append(valore)
        if t is None or not firme:
            raise FirmaNonValida("firma malformata")
        if abs(time.time() - t) > TOLLERANZA_SECONDI:
            raise FirmaNonValida("evento troppo vecchio: possibile ripetizione")

        attesa = firma(corpo, self._segreto, istante=t).split("v1=", 1)[1]
        # Più `v1` quando l'operatore sta ruotando il segreto: ne basta uno. Confronto a tempo costante.
        if not any(hmac.compare_digest(attesa, ricevuta) for ricevuta in firme):
            raise FirmaNonValida("firma non valida")

        try:
            evento = json.loads(corpo)
            return traduci(evento)
        except (ValueError, KeyError, TypeError) as exc:
            raise FirmaNonValida("corpo dell'evento illeggibile") from exc

    async def riferimenti_collegati(self, riferimenti: List[str]) -> List[str]:
        """Le fatture pagate da questi PaymentIntent: un rimborso cita l'addebito, l'abbonamento è segnato sulla
        fattura. Dal 2025 l'addebito non nomina più la fattura, e la si chiede a Stripe. Mai un errore: senza
        risposta, lo storno si registra a mano."""
        trovati: List[str] = []
        for riferimento in riferimenti:
            if not riferimento or not riferimento.startswith("pi_"):
                continue
            try:
                risposta = await self._chiama("GET", "/invoice_payments", {
                    "payment": {"type": "payment_intent", "payment_intent": riferimento}, "limit": 3,
                })
            except ErroreStripe:
                continue
            trovati += [str(p["invoice"]) for p in risposta.get("data") or [] if p.get("invoice")]
        return trovati

    # -- abbonamenti -------------------------------------------------------

    async def crea_abbonamento(self, user_id: int, piano: Plan, *, annuale: bool = False) -> str:
        """Solo per i piani gratuiti, che non passano da Stripe: un abbonamento a pagamento nasce dal Checkout."""
        if piano.price_monthly > 0 or piano.price_yearly > 0:
            raise PagamentiNonDisponibili("un abbonamento a pagamento si attiva passando dal pagamento")
        return f"gratuito-{uuid.uuid4().hex[:12]}"

    async def disdici(self, external_id: str) -> None:
        """Disdetta a fine periodo: il periodo è pagato, e Stripe non addebita il successivo.

        Un id che non è di Stripe (un piano gratuito, un abbonamento del simulatore) non si manda a Stripe.
        """
        await self.rinnovo_automatico(external_id, attivo=False)

    async def rinnovo_automatico(self, external_id: str, *, attivo: bool) -> None:
        """Accende o spegne il rinnovo automatico (`cancel_at_period_end`): l'interruttore del profilo (Fase 2b).

        Senza chiave d'idempotenza: spegnere, riaccendere e rispegnere sono tre richieste diverse con lo stesso
        corpo, e la seconda uguale non deve ricevere la risposta in cache della prima.
        """
        if not external_id.startswith("sub_"):
            return None
        await self._chiama("POST", f"/subscriptions/{external_id}", {"cancel_at_period_end": not attivo})
        return None

    # -- Fase 2b: sconti dei rinnovi, upgrade, downgrade, prova --------------------------------------------------

    async def _coupon_ricorrente(self, importo: int, valuta: str, *, motivo: str) -> str:
        """Il coupon «per sempre» di un importo fisso, trovato per id o creato: `tarots_<motivo>_<centesimi>_<valuta>`.

        Un importo e non una percentuale: Stripe arrotonda le percentuali a modo suo, e il rinnovo deve costare al
        centesimo quanto il profilo mostra. L'id è deterministico, quindi lo stesso sconto è lo stesso coupon per
        tutti gli abbonati che ce l'hanno (e il nome compare sulla fattura).
        """
        valuta = valuta.lower()
        ident = f"tarots_{motivo}_{int(importo)}_{valuta}"
        if await self._chiama("GET", f"/coupons/{ident}", nulla_se_assente=True):
            return ident
        nome = {
            "rinnovo": "Rinnovo automatico TAROTS chat", "sconto": "Sconto TAROTS chat (codice e rinnovo)",
        }.get(motivo, "Prova TAROTS chat: sconto per sempre")
        creato = await self._chiama("POST", "/coupons", {
            "id": ident, "amount_off": int(importo), "currency": valuta, "duration": "forever", "name": nome,
            "metadata": {"motivo": motivo},
        }, idempotenza=f"coupon-{ident}")
        return str(creato.get("id") or ident)

    async def applica_sconto_ricorrente(self, external_id: str, importo: int, valuta: str, *, motivo: str) -> None:
        """Lo sconto di ogni rinnovo sull'abbonamento (sostituisce gli sconti che aveva: quello d'una volta del primo
        pagamento è già stato usato). Non tocca il periodo in corso e non crea addebiti proporzionali. Un importo zero
        toglie ogni sconto (Fase 2d: il coupon «per N periodi» è finito e non c'è lo sconto del rinnovo)."""
        if not external_id.startswith("sub_"):
            return None
        if importo <= 0:
            await self._chiama("POST", f"/subscriptions/{external_id}", {"discounts": ""})
            return None
        coupon = await self._coupon_ricorrente(importo, valuta, motivo=motivo)
        await self._chiama("POST", f"/subscriptions/{external_id}", {"discounts": [{"coupon": coupon}]})
        return None

    async def chiudi_subito(self, external_id: str) -> None:
        """Chiude l'abbonamento adesso, **senza rimborso né addebito proporzionale**: l'upgrade col conguaglio ha già
        scalato il valore residuo dal prezzo del nuovo (`prorate=false`, `invoice_now=false`)."""
        if not external_id.startswith("sub_"):
            return None
        await self._chiama("DELETE", f"/subscriptions/{external_id}", {"prorate": False, "invoice_now": False})
        return None

    async def programma_cambio(
        self, external_id: str, piano: Plan, *, annuale: bool, sconto: int, sconto_attuale: int,
    ) -> str:
        """Il downgrade alla scadenza, con un programma (subscription schedule): la fase in corso resta com'è
        (prezzo, sconto, fine), la successiva ha il prezzo del piano nuovo e lo sconto del rinnovo. Alla fine il
        programma si stacca (`end_behavior=release`) e l'abbonamento continua da solo. Funziona anche cambiando
        intervallo (annuale → mensile), che un semplice aggiornamento dell'abbonamento addebiterebbe subito."""
        programma = await self._chiama("POST", "/subscription_schedules", {"from_subscription": external_id})
        fase = (programma.get("phases") or [{}])[0]
        attuale = ((fase.get("items") or [{}])[0]).get("price")
        if isinstance(attuale, Mapping):
            attuale = attuale.get("id")
        valuta = piano.currency.lower()
        nuovo = await self._prezzo_ricorrente(
            piano, annuale=annuale, importo=piano.price_yearly if annuale else piano.price_monthly, valuta=valuta,
        )
        prima: Dict[str, Any] = {
            "items": [{"price": attuale, "quantity": 1}],
            "start_date": fase.get("start_date"), "end_date": fase.get("end_date"),
        }
        if sconto_attuale > 0:
            prima["discounts"] = [{"coupon": await self._coupon_ricorrente(sconto_attuale, valuta, motivo="rinnovo")}]
        dopo: Dict[str, Any] = {"items": [{"price": nuovo, "quantity": 1}], "iterations": 1}
        if sconto > 0:
            dopo["discounts"] = [{"coupon": await self._coupon_ricorrente(sconto, valuta, motivo="rinnovo")}]
        await self._chiama("POST", f"/subscription_schedules/{programma['id']}", {
            "end_behavior": "release", "proration_behavior": "none", "phases": [prima, dopo],
        })
        return str(programma["id"])

    async def annulla_programma(self, programma_id: str) -> None:
        """Toglie il downgrade programmato: l'abbonamento resta quello di adesso."""
        if not programma_id.startswith("sub_sched_"):
            return None
        await self._chiama("POST", f"/subscription_schedules/{programma_id}/release")
        return None

    async def impronta_carta(self, external_id: str) -> Optional[str]:
        """L'impronta della carta dell'abbonamento (`card.fingerprint`): la stessa carta ha la stessa impronta su
        qualunque cliente dello stesso account Stripe. Serve a dare una sola prova per carta."""
        if not external_id.startswith("sub_"):
            return None
        abbonamento = await self._chiama("GET", f"/subscriptions/{external_id}", {"expand": ["default_payment_method"]})
        metodo = abbonamento.get("default_payment_method")
        if isinstance(metodo, Mapping):
            return ((metodo.get("card") or {}).get("fingerprint")) or None
        return None

    async def url_fattura(self, fattura_id: str) -> Optional[str]:
        """La pagina di Stripe dove pagare una fattura rimasta aperta (`hosted_invoice_url`): dopo un rinnovo fallito
        si torna a pagare questa, non un nuovo checkout. `None` se non è più da pagare."""
        fattura = await self._chiama("GET", f"/invoices/{fattura_id}")
        if fattura.get("status") != "open":
            return None
        return fattura.get("hosted_invoice_url")

    async def e_pagato(self, external_id: str) -> bool:
        if external_id.startswith("gratuito-"):
            return True
        if not external_id.startswith("sub_"):
            return False
        abbonamento = await self._chiama("GET", f"/subscriptions/{external_id}")
        return abbonamento.get("status") in ("active", "trialing")


# ---------------------------------------------------------------------------


def _abbonamento_della_fattura(fattura: Mapping[str, Any]) -> Optional[str]:
    """L'abbonamento di una fattura, nelle due forme dell'API: `subscription` (fino al 2025) o
    `parent.subscription_details.subscription` (dopo)."""
    diretto = fattura.get("subscription")
    if isinstance(diretto, Mapping):
        diretto = diretto.get("id")
    if diretto:
        return str(diretto)
    dettagli = ((fattura.get("parent") or {}).get("subscription_details") or {})
    sub = dettagli.get("subscription")
    if isinstance(sub, Mapping):
        sub = sub.get("id")
    return str(sub) if sub else None


def _fine_periodo(fattura: Mapping[str, Any]) -> Optional[int]:
    righe = ((fattura.get("lines") or {}).get("data") or [])
    for riga in righe:
        fine = (riga.get("period") or {}).get("end")
        if fine:
            return int(fine)
    return int(fattura["period_end"]) if fattura.get("period_end") else None


def _id(valore: Any) -> Optional[str]:
    if isinstance(valore, Mapping):
        valore = valore.get("id")
    return str(valore) if valore else None


def traduci(evento: Mapping[str, Any]) -> EventoPagamento:
    """Da un evento Stripe (già verificato) a un evento della piattaforma. Ciò che non serve diventa `stripe.<tipo>`,
    che `GestorePagamenti.applica` registra e ignora."""
    from .ordini import ORDINE_ANNULLATO, ORDINE_PAGATO

    id_evento = str(evento["id"])
    tipo = str(evento["type"])
    oggetto: Mapping[str, Any] = evento["data"]["object"]

    def ignorato(perche: str = "") -> EventoPagamento:
        return EventoPagamento(id=id_evento, tipo=f"stripe.{tipo}", dati={"id_fornitore": _id(oggetto), "nota": perche})

    if tipo.startswith("checkout.session."):
        metadati = oggetto.get("metadata") or {}
        ordine = metadati.get("tipo") == "ordine"
        if tipo == "checkout.session.completed" and oggetto.get("payment_status") not in ("paid", "no_payment_required"):
            # Un bonifico SEPA o simili: il denaro arriverà più tardi, con `async_payment_succeeded`.
            return ignorato("pagamento in attesa")
        if tipo in ("checkout.session.completed", "checkout.session.async_payment_succeeded"):
            if ordine:
                return EventoPagamento(id=id_evento, tipo=ORDINE_PAGATO, dati={
                    "ordine_id": metadati.get("ordine_id") or oggetto.get("client_reference_id"),
                    "importo": oggetto.get("amount_total"), "id_fornitore": _id(oggetto),
                })
            abbonamento = _id(oggetto.get("subscription"))
            return EventoPagamento(id=id_evento, tipo=PAGATO, dati={
                "checkout_id": metadati.get("checkout_id") or oggetto.get("client_reference_id"),
                "subscription_id": abbonamento,
                # L'incasso: la prima fattura di un abbonamento, il PaymentIntent di un pagamento singolo.
                "riferimento": _id(oggetto.get("invoice")) if abbonamento else _id(oggetto.get("payment_intent")),
                "importo": oggetto.get("amount_total"), "id_fornitore": _id(oggetto),
            })
        if tipo in ("checkout.session.expired", "checkout.session.async_payment_failed"):
            if ordine:
                return EventoPagamento(id=id_evento, tipo=ORDINE_ANNULLATO, dati={
                    "ordine_id": metadati.get("ordine_id") or oggetto.get("client_reference_id"),
                })
            return EventoPagamento(id=id_evento, tipo=SCADUTO if tipo.endswith("expired") else ANNULLATO, dati={
                "checkout_id": metadati.get("checkout_id") or oggetto.get("client_reference_id"),
            })
        return ignorato()

    if tipo == "invoice.paid":
        abbonamento = _abbonamento_della_fattura(oggetto)
        if not abbonamento:
            return ignorato("fattura senza abbonamento")
        if oggetto.get("billing_reason") == "subscription_create":
            return ignorato("primo periodo: lo apre checkout.session.completed")
        return EventoPagamento(id=id_evento, tipo=RINNOVATO, dati={
            "subscription_id": abbonamento, "riferimento": _id(oggetto), "fine": _fine_periodo(oggetto),
            "importo": oggetto.get("amount_paid"),
        })

    if tipo == "invoice.payment_failed":
        abbonamento = _abbonamento_della_fattura(oggetto)
        if not abbonamento:
            return ignorato("fattura senza abbonamento")
        return EventoPagamento(id=id_evento, tipo=RINNOVO_FALLITO, dati={
            "subscription_id": abbonamento, "riferimento": _id(oggetto),
        })

    if tipo == "customer.subscription.trial_will_end":
        return EventoPagamento(id=id_evento, tipo=PROVA_IN_SCADENZA, dati={
            "subscription_id": _id(oggetto), "fine": oggetto.get("trial_end"),
        })

    if tipo == "customer.subscription.deleted":
        return EventoPagamento(id=id_evento, tipo=ABBONAMENTO_CHIUSO, dati={"subscription_id": _id(oggetto)})

    if tipo == "customer.subscription.updated":
        # La fine del periodo: sull'abbonamento fino al 2025, sulle sue voci dopo.
        voci = ((oggetto.get("items") or {}).get("data") or [{}])
        fine = oggetto.get("current_period_end") or voci[0].get("current_period_end")
        return EventoPagamento(id=id_evento, tipo=ABBONAMENTO_AGGIORNATO, dati={
            "subscription_id": _id(oggetto), "stato_fornitore": oggetto.get("status"),
            "disdetta_a_fine_periodo": bool(oggetto.get("cancel_at_period_end")),
            "fine": oggetto.get("cancel_at") or fine,
        })

    if tipo == "charge.refunded":
        return EventoPagamento(id=id_evento, tipo=STORNO, dati={
            "riferimenti": [r for r in (
                _id(oggetto.get("payment_intent")), _id(oggetto), _id(oggetto.get("invoice")),
            ) if r],
            "importo": oggetto.get("amount"), "importo_stornato": oggetto.get("amount_refunded"),
            "causa": "rimborso", "id_fornitore": _id(oggetto),
        })

    if tipo in ("charge.dispute.created", "charge.dispute.closed"):
        riferimenti = [r for r in (_id(oggetto.get("payment_intent")), _id(oggetto.get("charge"))) if r]
        if tipo == "charge.dispute.created":
            # Una contestazione si storna per intero: il fornitore trattiene l'intero importo finché non è decisa.
            return EventoPagamento(id=id_evento, tipo=STORNO, dati={
                "riferimenti": riferimenti, "causa": "contestazione", "id_fornitore": _id(oggetto),
            })
        if oggetto.get("status") == "won":
            return EventoPagamento(id=id_evento, tipo=STORNO_ANNULLATO, dati={
                "riferimenti": riferimenti, "id_fornitore": _id(oggetto),
            })
        return ignorato(f"contestazione chiusa: {oggetto.get('status')}")

    return ignorato()
