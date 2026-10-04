"""Gli abbonamenti dopo il pagamento (v9, Fase 2b): limiti e condoni, rinnovo automatico, conguaglio, prova,
tolleranza sui pagamenti falliti.

**L'abbonamento dà letture comprese, non crediti.** Entro i limiti del piano (`billing/quote.py`) una lettura è
`quota`; oltre, la lettura non parte da sola: `valuta_lettura` dice quale limite è superato, quante letture sono state
fatte nel periodo, quanti condoni restano e il saldo, e il sito chiede il consenso. Le prime letture oltre il limite
(due per periodo, dalla console) sono condonate; poi serve un credito, che si compra a parte e non scade.

**Il rinnovo automatico** è acceso per default e porta uno sconto (20%, dalla console) su ogni rinnovo. Spento, il
periodo pagato resta, il fornitore non rinnova (`cancel_at_period_end` su Stripe) e un nuovo acquisto senza rinnovo
paga il listino. Si riaccende fino alla scadenza. Ogni spegnimento manda una conferma formale per email.

**Il conguaglio di un upgrade** è un conto che l'utente deve poter rifare a mano (`calcola_residuo`):

    residuo   = importo pagato del periodo × giorni interi rimasti / giorni del periodo   (al centesimo, per eccesso a .5)
    da pagare = max(0, prezzo nuovo − sconto del rinnovo automatico se scelto − residuo)

Esempio dell'operatore: base mensile 10 €, a metà mese (15 giorni su 30) → residuo 5 €; annuale top 100 € con il
rinnovo automatico (−20%) → 80 €; da pagare 75 €. Il giorno in corso non conta fra i rimasti. Un residuo più grande
del prezzo nuovo porta il totale a zero, e la differenza si perde: è la regola dell'operatore. Il nuovo periodo parte
subito; un **downgrade** parte alla fine del periodo pagato, senza conguaglio.

**La prova gratuita** (14 giorni, una per persona e una per carta) registra il metodo di pagamento all'inizio e alla
fine diventa da sola un annuale del livello scelto con lo sconto della prova (50%) per sempre. Promemoria due giorni
prima (email, e l'aggancio per la notifica della Fase 5).

**Un pagamento fallito non toglie subito i diritti**: sette giorni di tolleranza (`in_sospeso`), con le letture
comprese ancora attive, email al fallimento, al terzo e al sesto giorno; poi `sospeso` e un'ultima email. Per pagare
si torna alla **stessa fattura aperta** (la sua pagina presso il fornitore): pagarla ferma i tentativi automatici, e
mentre c'è una fattura aperta non si apre nessun nuovo checkout — niente doppio addebito.

Gli abbonamenti degli store (Google Play, App Store) si gestiscono nello store: qui niente interruttore né conguaglio,
solo la spiegazione e il link (`ErroreAbbonamento('store')`). Il loro stato segue le notifiche dello store (Fase 4,
`billing/store/`): la disdetta manda la stessa email di conferma, il promemoria della prova vale anche per loro, i
solleciti di pagamento no (li manda lo store).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.abbonamenti_models import ImpostazioniAbbonamenti, ProvaGratuita
from ..domain.base import utcnow
from ..domain.billing_models import FORNITORI_ESTERNI, Plan, Subscription
from ..domain.models import User
from ..domain.repositories import AuditRepository
from .credits import RegistroCrediti
from .entitlements import Diritti
from .quote import ContatoreQuote, StatoLimite

logger = logging.getLogger(__name__)

ID_RIGA = 1

#: Gli abbonamenti che si gestiscono nello store e non qui.
STORE = ("google_play", "app_store")

#: Dove si gestiscono gli abbonamenti degli store (Fase 4 per la verifica; qui per la spiegazione).
GESTIONE_STORE = {
    "google_play": "https://play.google.com/store/account/subscriptions",
    "app_store": "https://apps.apple.com/account/subscriptions",
}


#: Il messaggio dell'errore `limite_superato` per chi usa l'API senza il dialogo del sito.
LIMITE_SUPERATO = {
    "en": "You have reached a reading limit of your subscription: confirm to continue.",
    "it": "Hai raggiunto un limite di letture del tuo abbonamento: conferma per continuare.",
    "hu": "Elérted az előfizetésed egyik olvasási korlátját: erősítsd meg a folytatáshoz.",
    "ru": "Ты достиг лимита раскладов своей подписки: подтверди, чтобы продолжить.",
    "uk": "Ти досяг ліміту розкладів своєї підписки: підтверди, щоб продовжити.",
    "es": "Has alcanzado un límite de lecturas de tu suscripción: confirma para continuar.",
}


class ErroreAbbonamento(Exception):
    """Un'operazione sull'abbonamento che non si può fare: il motivo è stabile, il messaggio si mostra."""

    def __init__(self, motivo: str, messaggio: str, **dati: Any) -> None:
        super().__init__(messaggio)
        self.motivo = motivo
        self.dati = dati


# ---- impostazioni ---------------------------------------------------------------------------------------------------


async def impostazioni(session: AsyncSession) -> ImpostazioniAbbonamenti:
    """La riga delle impostazioni, creandola con i default dell'operatore se manca."""
    riga = await session.get(ImpostazioniAbbonamenti, ID_RIGA)
    if riga is None:
        riga = ImpostazioniAbbonamenti(id=ID_RIGA)
        session.add(riga)
        await session.flush()
    return riga


CAMPI_IMPOSTAZIONI = (
    "sconto_rinnovo", "sconto_prova", "giorni_prova", "giorni_tolleranza", "giorni_promemoria_prova",
    "condoni_per_periodo", "banner_prova",
)


def impostazioni_json(riga: ImpostazioniAbbonamenti) -> Dict[str, Any]:
    return {campo: getattr(riga, campo) for campo in CAMPI_IMPOSTAZIONI}


async def aggiorna_impostazioni(
    session: AsyncSession, campi: Dict[str, Any], *, attore_id: int, ip: Optional[str] = None,
) -> ImpostazioniAbbonamenti:
    riga = await impostazioni(session)
    prima = impostazioni_json(riga)
    for campo in CAMPI_IMPOSTAZIONI:
        if campo in campi and campi[campo] is not None:
            setattr(riga, campo, campi[campo])
    riga.updated_by = attore_id
    dopo = impostazioni_json(riga)
    if prima != dopo:
        await AuditRepository(session).record(
            action="abbonamenti.impostazioni", actor_id=attore_id, target_type="impostazioni_abbonamenti",
            target_id=str(ID_RIGA), before=prima, after=dopo, ip=ip,
        )
    await session.flush()
    return riga


# ---- prezzi ---------------------------------------------------------------------------------------------------------


def percentuale(importo: int, percento: int) -> int:
    """`percento`% di `importo` in centesimi, al centesimo (mezzo centesimo per eccesso), in interi."""
    return (int(importo) * int(percento) + 50) // 100


def listino_di(piano: Plan, annuale: bool) -> int:
    return piano.price_yearly if annuale and not piano.pacchetto else piano.price_monthly


def gratuito(piano: Plan) -> bool:
    return piano.price_monthly <= 0 and piano.price_yearly <= 0


def prezzi_piano(piano: Plan, riga: ImpostazioniAbbonamenti) -> Dict[str, Any]:
    """Il prezzo di un piano con e senza rinnovo automatico, mensile e annuale: la pagina dei prezzi lo mostra così."""
    def voce(listino: int) -> Dict[str, int]:
        sconto = percentuale(listino, riga.sconto_rinnovo)
        return {"listino": listino, "con_rinnovo": listino - sconto, "sconto": sconto}

    return {
        "mensile": voce(piano.price_monthly),
        "annuale": voce(piano.price_yearly) if piano.price_yearly > 0 else None,
        "prova_annuale": (
            piano.price_yearly - percentuale(piano.price_yearly, riga.sconto_prova) if piano.price_yearly > 0 else None
        ),
    }


def prossimo_rinnovo(abbonamento: Subscription) -> Optional[int]:
    """Quanto costerà il prossimo rinnovo, se il rinnovo automatico è acceso (centesimi)."""
    if not abbonamento.rinnovo_automatico or abbonamento.listino is None:
        return None
    piano = abbonamento.piano_successivo or abbonamento.plan
    if abbonamento.piano_successivo is not None:
        listino = listino_di(piano, bool(abbonamento.annuale_successivo))
        return listino - percentuale(listino, _percento_ricorrente(abbonamento))
    return max(0, abbonamento.listino - abbonamento.sconto_ricorrente)


def _percento_ricorrente(abbonamento: Subscription) -> int:
    """La percentuale dello sconto ricorrente, ricavata da listino e importo (per un downgrade a un altro listino). Senza
    il coupon (Fase 2d): un cambio di piano lo chiude."""
    base = abbonamento.sconto_ricorrente if abbonamento.sconto_base is None else abbonamento.sconto_base
    if not abbonamento.listino or not base:
        return 0
    return round(base * 100 / abbonamento.listino)


# ---- chi gestisce l'abbonamento -------------------------------------------------------------------------------------


def nello_store(abbonamento: Subscription) -> bool:
    return abbonamento.provider in STORE


def fornitore_per(abbonamento: Subscription, configurato: Any) -> Optional[Any]:
    """Il fornitore che può agire sull'abbonamento presso di sé: quello configurato, se è lo stesso che lo incassa.
    `None` per i piani interni (gratuiti, regalati) e per quelli di un fornitore che non è più configurato."""
    if abbonamento.provider == getattr(configurato, "name", None) and abbonamento.external_id:
        return configurato
    return None


def _errore_store(abbonamento: Subscription) -> ErroreAbbonamento:
    return ErroreAbbonamento(
        "store", "Questo abbonamento si gestisce nello store da cui l'hai comprato.",
        provider=abbonamento.provider, gestione=GESTIONE_STORE.get(abbonamento.provider),
    )


# ---- letture comprese, limiti e condoni -----------------------------------------------------------------------------


@dataclass
class Valutazione:
    """Da dove si paga la prossima lettura."""

    #: `quota` (compresa), `credito` (un credito, senza limiti da superare: chi non ha un abbonamento con letture
    #: comprese), o `None` se un limite è superato e serve il consenso.
    consumo: Optional[str]
    superato: Optional[StatoLimite] = None
    condoni_rimasti: int = 0
    saldo: int = 0
    condoni_per_periodo: int = 0

    def dettaglio(self) -> Dict[str, Any]:
        """Il corpo dell'errore `limite_superato`: tutto ciò che il dialogo deve dire."""
        s = self.superato
        assert s is not None
        return {
            "motivo": "limite_superato",
            "limite": s.nome,
            "valore": s.limite,
            "usate": s.usati,
            "letture_fatte": s.fatte,
            "dal": s.dal.isoformat() if s.dal else None,
            "si_libera": s.si_libera.isoformat() if s.si_libera else None,
            "condoni_rimasti": self.condoni_rimasti,
            "condoni_per_periodo": self.condoni_per_periodo,
            "saldo": self.saldo,
            "scelta": "condono" if self.condoni_rimasti > 0 else "credito" if self.saldo > 0 else "acquisto",
        }


def ha_letture_comprese(abbonamento: Optional[Subscription], diritti: Diritti) -> bool:
    """L'utente ha un abbonamento a pagamento con letture comprese? Il piano gratuito non ne ha (ogni lettura costa
    un credito, come sempre), e nemmeno un piano che ne dichiara zero al giorno."""
    if abbonamento is None or not abbonamento.vivo or diritti.predefiniti or gratuito(abbonamento.plan):
        return False
    return diritti.limite("letture_al_giorno") != 0


async def valuta_lettura(
    session: AsyncSession, user_id: int, abbonamento: Optional[Subscription], diritti: Diritti,
) -> Valutazione:
    """Quota, credito, o limite superato (con i condoni rimasti e il saldo)."""
    if not ha_letture_comprese(abbonamento, diritti):
        return Valutazione(consumo="credito")
    assert abbonamento is not None
    contatore = ContatoreQuote(session)
    superato = await contatore.superato(
        user_id, diritti, periodo_inizio=abbonamento.period_start, periodo_fine=abbonamento.period_end,
    )
    if superato is None:
        return Valutazione(consumo="quota")
    riga = await impostazioni(session)
    return Valutazione(
        consumo=None, superato=superato, condoni_per_periodo=riga.condoni_per_periodo,
        condoni_rimasti=max(0, riga.condoni_per_periodo - superato.condoni),
        saldo=await RegistroCrediti(session).saldo(user_id),
    )


# ---- conguaglio -----------------------------------------------------------------------------------------------------


def calcola_residuo(pagato: int, inizio: datetime, fine: datetime, adesso: datetime) -> Tuple[int, int, int]:
    """(residuo, giorni rimasti, giorni del periodo). I giorni sono interi: il giorno in corso non conta fra i rimasti."""
    totale = max(1, round((fine - inizio).total_seconds() / 86400))
    rimasti = int(max(0.0, (fine - adesso).total_seconds()) // 86400)
    rimasti = min(rimasti, totale)
    residuo = (int(pagato) * rimasti * 2 + totale) // (2 * totale)
    return residuo, rimasti, totale


def tipo_cambio(abbonamento: Subscription, piano: Plan, annuale: bool) -> str:
    """`upgrade` (parte subito, col conguaglio), `downgrade` (parte alla scadenza) o `uguale`.

    Il livello è l'ordine del catalogo (`rank`). A parità di livello, passare dal mensile all'annuale è un upgrade
    (più lungo, pagato subito), il contrario un downgrade.
    """
    attuale = abbonamento.plan
    if piano.id == attuale.id and annuale == abbonamento.annuale:
        return "uguale"
    if piano.rank != attuale.rank:
        return "upgrade" if piano.rank > attuale.rank else "downgrade"
    if piano.id != attuale.id:
        # Stesso livello, piano diverso: decide il prezzo dell'intervallo scelto.
        return "upgrade" if listino_di(piano, annuale) >= listino_di(attuale, abbonamento.annuale) else "downgrade"
    return "upgrade" if annuale and not abbonamento.annuale else "downgrade"


@dataclass
class Conguaglio:
    tipo: str
    piano: Plan
    annuale: bool
    rinnovo: bool
    listino: int
    sconto_rinnovo: int
    nuovo: int
    residuo: int
    totale: int
    pagato: int
    giorni_rimasti: int
    giorni_periodo: int
    decorre: datetime
    valuta: str = "EUR"
    righe: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self, lang: Optional[str] = None) -> Dict[str, Any]:
        from .lingue import in_lingua

        return {
            "tipo": self.tipo,
            "piano": self.piano.slug,
            "nome": in_lingua(self.piano.nomi, lang, self.piano.name),
            "annuale": self.annuale,
            "rinnovo": self.rinnovo,
            "listino": self.listino,
            "sconto_rinnovo": self.sconto_rinnovo,
            "nuovo": self.nuovo,
            "residuo": self.residuo,
            "totale": self.totale,
            "pagato": self.pagato,
            "giorni_rimasti": self.giorni_rimasti,
            "giorni_periodo": self.giorni_periodo,
            "decorre": self.decorre.isoformat(),
            "valuta": self.valuta,
        }


async def anteprima_cambio(
    session: AsyncSession, abbonamento: Subscription, piano: Plan, *, annuale: bool, rinnovo: bool = True,
    adesso: Optional[datetime] = None,
) -> Conguaglio:
    """Il conto di un cambio di piano, senza toccare niente."""
    if nello_store(abbonamento):
        raise _errore_store(abbonamento)
    if piano.pacchetto or not piano.active or gratuito(piano):
        raise ErroreAbbonamento("piano_non_valido", "Si passa solo a un abbonamento a pagamento in vendita.")
    if annuale and piano.price_yearly <= 0:
        raise ErroreAbbonamento("piano_non_valido", "Questo piano non ha la versione annuale.")
    adesso = adesso or utcnow()
    tipo = tipo_cambio(abbonamento, piano, annuale)
    if tipo == "uguale":
        raise ErroreAbbonamento("stesso_piano", "È già il tuo abbonamento.")
    riga = await impostazioni(session)
    listino = listino_di(piano, annuale)
    sconto = percentuale(listino, riga.sconto_rinnovo) if rinnovo else 0
    nuovo = listino - sconto
    pagato = abbonamento.importo_periodo
    if pagato is None:
        pagato = abbonamento.listino if abbonamento.listino is not None else listino_di(abbonamento.plan, abbonamento.annuale)
    if abbonamento.status == "in_prova":
        pagato = 0          # la prova non è stata pagata: niente da restituire
    if tipo == "upgrade":
        residuo, rimasti, totale = calcola_residuo(pagato, abbonamento.period_start, abbonamento.period_end, adesso)
        da_pagare = max(0, nuovo - residuo)
        decorre = adesso
    else:
        residuo, rimasti, totale = 0, 0, 0
        da_pagare = nuovo
        decorre = abbonamento.period_end
    return Conguaglio(
        tipo=tipo, piano=piano, annuale=annuale, rinnovo=rinnovo, listino=listino, sconto_rinnovo=sconto, nuovo=nuovo,
        residuo=residuo, totale=da_pagare, pagato=pagato, giorni_rimasti=rimasti, giorni_periodo=totale,
        decorre=decorre, valuta=piano.currency,
    )


# ---- nessun doppio addebito -----------------------------------------------------------------------------------------


async def fattura_aperta_di(session: AsyncSession, user_id: int) -> Optional[Subscription]:
    """L'abbonamento dell'utente con una fattura rimasta da pagare, se c'è."""
    return (await session.execute(
        select(Subscription)
        .where(
            Subscription.user_id == user_id, Subscription.fattura_aperta.is_not(None),
            Subscription.status.in_(("in_prova", "attivo", "in_sospeso", "sospeso")),
        )
        .order_by(Subscription.created_at.desc()).limit(1)
    )).scalar_one_or_none()


async def verifica_nessuna_fattura_aperta(session: AsyncSession, user_id: int) -> None:
    """Mai un nuovo checkout di abbonamento mentre c'è una fattura aperta: si paga quella."""
    if await fattura_aperta_di(session, user_id) is not None:
        raise ErroreAbbonamento(
            "fattura_aperta",
            "C'è un pagamento del tuo abbonamento ancora da saldare: sistemalo dal profilo prima di un nuovo acquisto.",
        )


# ---- prova gratuita -------------------------------------------------------------------------------------------------


async def prova_di(session: AsyncSession, user_id: int) -> Optional[ProvaGratuita]:
    return (await session.execute(select(ProvaGratuita).where(ProvaGratuita.user_id == user_id))).scalar_one_or_none()


async def idoneita_prova(session: AsyncSession, user_id: Optional[int], abbonamento: Optional[Subscription]) -> Tuple[bool, Optional[str]]:
    """(idoneo, motivo). Una prova per persona, e non a chi ha già un abbonamento a pagamento."""
    if user_id is None:
        return True, None
    if await prova_di(session, user_id) is not None:
        return False, "prova_gia_usata"
    if abbonamento is not None and abbonamento.vivo and not gratuito(abbonamento.plan):
        return False, "abbonamento_attivo"
    return True, None


async def impronta_gia_usata(session: AsyncSession, impronta: Optional[str], user_id: int) -> bool:
    """La stessa carta ha già avuto una prova su un altro account?"""
    if not impronta:
        return False
    return bool(await session.scalar(
        select(ProvaGratuita.id).where(ProvaGratuita.impronta_carta == impronta, ProvaGratuita.user_id != user_id)
        .limit(1)
    ))


# ---- rinnovo automatico ---------------------------------------------------------------------------------------------


async def imposta_rinnovo(
    session: AsyncSession, abbonamento: Subscription, attivo: bool, *, configurato: Any, utente: User,
) -> Subscription:
    """Spegne o riaccende il rinnovo automatico, presso il fornitore e qui; manda l'email.

    Spento: il periodo pagato resta, il fornitore non rinnova. Un downgrade programmato si annulla (non ci sarà un
    periodo successivo in cui farlo partire). Riacceso (solo prima della scadenza): se l'abbonamento era stato
    comprato senza rinnovo, prende adesso lo sconto del rinnovo automatico per i rinnovi.
    """
    from ..posta import data_in, importo_in, lingua_di, manda

    if nello_store(abbonamento):
        raise _errore_store(abbonamento)
    if not abbonamento.vivo:
        raise ErroreAbbonamento("non_attivo", "L'abbonamento non è attivo.")
    if gratuito(abbonamento.plan):
        raise ErroreAbbonamento("gratuito", "Il piano gratuito non si rinnova a pagamento.")
    if attivo == abbonamento.rinnovo_automatico:
        return abbonamento
    adesso = utcnow()
    fornitore = fornitore_per(abbonamento, configurato)
    lingua = lingua_di(utente)
    if not attivo:
        if abbonamento.programma_esterno and fornitore is not None and hasattr(fornitore, "annulla_programma"):
            await fornitore.annulla_programma(abbonamento.programma_esterno)
        abbonamento.programma_esterno = None
        abbonamento.piano_successivo_id = None
        abbonamento.annuale_successivo = None
        if fornitore is not None and hasattr(fornitore, "rinnovo_automatico"):
            await fornitore.rinnovo_automatico(abbonamento.external_id, attivo=False)
        abbonamento.cancel_at = abbonamento.period_end
        await session.flush()
        await manda(session, utente, "rinnovo_spento", f"rinnovo_spento:{abbonamento.id}:{adesso.isoformat()}", {
            "piano": abbonamento.plan.name, "data": data_in(abbonamento.period_end, lingua),
            "oggi": data_in(adesso, lingua),
        })
    else:
        if abbonamento.period_end <= adesso:
            raise ErroreAbbonamento("scaduto", "Il periodo è finito: il rinnovo non si può più riattivare.")
        if fornitore is not None and hasattr(fornitore, "rinnovo_automatico"):
            await fornitore.rinnovo_automatico(abbonamento.external_id, attivo=True)
        if abbonamento.sconto_ricorrente == 0 and abbonamento.listino:
            from .offerte import base_di, motivo_sconto, ricalcola_sconto

            riga = await impostazioni(session)
            percento = riga.sconto_prova if abbonamento.prova else riga.sconto_rinnovo
            if base_di(abbonamento) == 0:
                abbonamento.sconto_base = percentuale(abbonamento.listino, percento)
            abbonamento.cancel_at = None                  # `ricalcola_sconto` guarda il rinnovo automatico
            # Fase 2d: lo sconto del rinnovo, più o contro il coupon che dura ancora.
            sconto = ricalcola_sconto(abbonamento)
            if sconto > 0:
                abbonamento.sconto_ricorrente = sconto
                if fornitore is not None and hasattr(fornitore, "applica_sconto_ricorrente"):
                    await fornitore.applica_sconto_ricorrente(
                        abbonamento.external_id, sconto, abbonamento.plan.currency, motivo=motivo_sconto(abbonamento),
                    )
        abbonamento.cancel_at = None
        await session.flush()
        await manda(session, utente, "rinnovo_riacceso", f"rinnovo_riacceso:{abbonamento.id}:{adesso.isoformat()}", {
            "piano": abbonamento.plan.name, "data": data_in(abbonamento.period_end, lingua),
            "importo": importo_in(prossimo_rinnovo(abbonamento) or 0, abbonamento.plan.currency, lingua),
        })
    await AuditRepository(session).record(
        action="subscription.renewal", actor_id=utente.id, target_type="subscription", target_id=str(abbonamento.id),
        after={"rinnovo_automatico": attivo},
    )
    return abbonamento


# ---- downgrade ------------------------------------------------------------------------------------------------------


async def programma_downgrade(
    session: AsyncSession, abbonamento: Subscription, piano: Plan, *, annuale: bool, configurato: Any,
) -> Subscription:
    """Il piano più basso parte alla fine del periodo pagato. Presso Stripe con un programma (subscription schedule):
    il periodo in corso resta com'è, il successivo si addebita al prezzo nuovo."""
    if nello_store(abbonamento):
        raise _errore_store(abbonamento)
    riga = await impostazioni(session)
    fornitore = fornitore_per(abbonamento, configurato)
    if abbonamento.programma_esterno and fornitore is not None and hasattr(fornitore, "annulla_programma"):
        await fornitore.annulla_programma(abbonamento.programma_esterno)
        abbonamento.programma_esterno = None
    if fornitore is not None and hasattr(fornitore, "programma_cambio"):
        listino = listino_di(piano, annuale)
        abbonamento.programma_esterno = await fornitore.programma_cambio(
            abbonamento.external_id, piano, annuale=annuale,
            sconto=percentuale(listino, riga.sconto_rinnovo) if abbonamento.rinnovo_automatico else 0,
            # La fase in corso tiene lo sconto che ha (coupon compreso, Fase 2d); quella nuova solo il rinnovo.
            sconto_attuale=abbonamento.sconto_ricorrente,
        )
    abbonamento.piano_successivo_id = piano.id
    abbonamento.annuale_successivo = annuale
    await session.flush()
    await session.refresh(abbonamento, ["piano_successivo"])
    return abbonamento


async def annulla_downgrade(session: AsyncSession, abbonamento: Subscription, *, configurato: Any) -> Subscription:
    fornitore = fornitore_per(abbonamento, configurato)
    if abbonamento.programma_esterno and fornitore is not None and hasattr(fornitore, "annulla_programma"):
        await fornitore.annulla_programma(abbonamento.programma_esterno)
    abbonamento.programma_esterno = None
    abbonamento.piano_successivo_id = None
    abbonamento.annuale_successivo = None
    await session.flush()
    await session.refresh(abbonamento, ["piano_successivo"])
    return abbonamento


def applica_downgrade(abbonamento: Subscription, piano: Plan, *, percento_rinnovo: int) -> None:
    """Al rinnovo: il piano programmato diventa quello dell'abbonamento."""
    annuale = bool(abbonamento.annuale_successivo)
    listino = listino_di(piano, annuale)
    abbonamento.plan_id = piano.id
    abbonamento.plan = piano
    abbonamento.annuale = annuale
    abbonamento.listino = listino
    abbonamento.sconto_ricorrente = percentuale(listino, percento_rinnovo) if abbonamento.rinnovo_automatico else 0
    abbonamento.sconto_base = abbonamento.sconto_ricorrente
    if abbonamento.coupon_id is not None:
        # Fase 2d: un cambio di piano chiude lo sconto del coupon (valeva sul listino del piano di prima).
        abbonamento.coupon_rinnovi_rimasti = 0
    abbonamento.piano_successivo_id = None
    abbonamento.piano_successivo = None
    abbonamento.annuale_successivo = None
    abbonamento.programma_esterno = None


# ---- tolleranza sui pagamenti falliti -------------------------------------------------------------------------------


async def apri_tolleranza(
    session: AsyncSession, abbonamento: Subscription, *, fattura: Optional[str] = None, adesso: Optional[datetime] = None,
) -> str:
    """Un pagamento non riuscito: `in_sospeso` per la tolleranza, la fattura da saldare, l'email (una volta).

    Un secondo fallimento dello stesso giro (i tentativi automatici del fornitore) non riapre la tolleranza: conta
    il primo. Un abbonamento già chiuso non si tocca.
    """
    from ..posta import data_in, importo_in, lingua_di, manda

    if abbonamento.status in ("disdetto", "scaduto"):
        return f"abbonamento {abbonamento.status}: invariato"
    adesso = adesso or utcnow()
    if fattura:
        abbonamento.fattura_aperta = fattura
    if abbonamento.pagamento_fallito_il is None:
        abbonamento.pagamento_fallito_il = adesso
    if abbonamento.status != "sospeso":
        abbonamento.status = "in_sospeso"
    await session.flush()
    riga = await impostazioni(session)
    utente = await session.get(User, abbonamento.user_id)
    lingua = lingua_di(utente)
    scadenza = abbonamento.pagamento_fallito_il + timedelta(days=riga.giorni_tolleranza)
    await manda(
        session, utente, "pagamento_fallito",
        f"pagamento_fallito:{abbonamento.id}:{_istante(abbonamento.pagamento_fallito_il)}",
        {
            "piano": abbonamento.plan.name, "giorni": riga.giorni_tolleranza, "data": data_in(scadenza, lingua),
            "importo": importo_in(prossimo_rinnovo(abbonamento) or abbonamento.listino or 0, abbonamento.plan.currency, lingua),
        },
    )
    return f"abbonamento {abbonamento.status}"


def _istante(quando: datetime) -> str:
    """Un istante per le chiavi delle email: i secondi dall'epoca, uguali comunque il database restituisca il fuso."""
    return str(int(quando.timestamp()))


def chiudi_tolleranza(abbonamento: Subscription) -> None:
    """Il pagamento è arrivato: niente più fattura aperta né tolleranza."""
    abbonamento.fattura_aperta = None
    abbonamento.pagamento_fallito_il = None


async def giro_tolleranza(session: AsyncSession, *, adesso: Optional[datetime] = None, configurato: Any = None) -> Dict[str, int]:
    """Il pezzo orario della tolleranza: solleciti al terzo e al sesto giorno, sospensione alla fine. Idempotente."""
    from ..posta import data_in, lingua_di, manda
    from .plans import GestoreAbbonamenti, NienteDaIncassare

    adesso = adesso or utcnow()
    riga = await impostazioni(session)
    conti: Dict[str, int] = {}
    in_tolleranza = (await session.execute(
        select(Subscription)
        .where(Subscription.status == "in_sospeso", Subscription.pagamento_fallito_il.is_not(None))
        .with_for_update(skip_locked=True)
    )).scalars().all()
    for abbonamento in in_tolleranza:
        if abbonamento.provider in STORE:
            # Fase 4: la tolleranza di uno store la tiene lo store (Google grace period e account hold, Apple Billing
            # Grace Period e billing retry), che avvisa l'utente da sé con l'importo vero e il link per sistemare il
            # pagamento; la sospensione arriva con la sua notifica (`billing/store/`). Qui niente solleciti né
            # sospensioni: con una tolleranza di Apple di 16 o 28 giorni, sospendere al settimo toglierebbe un
            # servizio che lo store dà ancora per pagato.
            continue
        # Un abbonamento interno (il simulatore, in sviluppo) non ha un fornitore che riprova da sé: si riprova qui.
        if abbonamento.provider not in FORNITORI_ESTERNI and configurato is not None:
            fornitore = configurato if abbonamento.provider == getattr(configurato, "name", None) else NienteDaIncassare()
            if await fornitore.e_pagato(abbonamento.external_id or ""):
                await GestoreAbbonamenti(session, fornitore).rinnova(abbonamento, pagato=True)
                conti["saldati"] = conti.get("saldati", 0) + 1
                continue
        utente = await session.get(User, abbonamento.user_id)
        lingua = lingua_di(utente)
        fallito = abbonamento.pagamento_fallito_il
        assert fallito is not None
        giorni = (adesso - fallito).total_seconds() / 86400
        scadenza = fallito + timedelta(days=riga.giorni_tolleranza)
        if giorni >= riga.giorni_tolleranza:
            abbonamento.status = "sospeso"
            await session.flush()
            await manda(session, utente, "sospensione", f"sospensione:{abbonamento.id}:{_istante(fallito)}", {
                "piano": abbonamento.plan.name, "giorni": riga.giorni_tolleranza,
            })
            conti["sospesi"] = conti.get("sospesi", 0) + 1
            continue
        for giorno in (6, 3):
            if giorni >= giorno and giorno < riga.giorni_tolleranza:
                esito = await manda(session, utente, "sollecito", f"sollecito_{giorno}:{abbonamento.id}:{_istante(fallito)}", {
                    "piano": abbonamento.plan.name, "giorni": max(1, riga.giorni_tolleranza - giorno),
                    "data": data_in(scadenza, lingua),
                })
                if esito != "già inviata":
                    conti[f"solleciti_{giorno}"] = conti.get(f"solleciti_{giorno}", 0) + 1
                break
    return conti


# ---- promemoria della prova -----------------------------------------------------------------------------------------


async def aggancio_notifica(
    utente: Optional[User], tipo: str, dati: Dict[str, Any], *, session: Optional[AsyncSession] = None,
) -> None:
    """L'aggancio per le notifiche push (Fase 5, `notifiche/automatiche.py`): la stessa notizia dell'email, sui
    dispositivi della persona (FCM e Web Push), con l'idempotenza di `invii_notifica`. Se adesso è l'ora di silenzio
    della persona, ci pensa il giro delle notifiche (ogni 15 minuti). Un errore qui non ferma il giro delle email."""
    if session is None or tipo != "promemoria_prova":
        return None
    from ..notifiche import automatiche

    try:
        async with session.begin_nested():
            await automatiche.promemoria_prova(session, utente, dati)
    except Exception:  # noqa: BLE001 — la notifica è un di più: l'email è già partita
        logger.warning("Notifica del promemoria della prova non mandata", exc_info=True)
    return None


async def giro_promemoria_prova(session: AsyncSession, *, adesso: Optional[datetime] = None) -> int:
    """Il promemoria della fine della prova, `giorni_promemoria_prova` giorni prima: una volta per prova."""
    from ..posta import data_in, importo_in, lingua_di, manda

    adesso = adesso or utcnow()
    riga = await impostazioni(session)
    in_scadenza = (await session.execute(
        select(Subscription).where(
            Subscription.status == "in_prova", Subscription.prova.is_(True), Subscription.cancel_at.is_(None),
            Subscription.period_end > adesso,
            Subscription.period_end <= adesso + timedelta(days=riga.giorni_promemoria_prova),
        )
    )).scalars().all()
    inviati = 0
    for abbonamento in in_scadenza:
        utente = await session.get(User, abbonamento.user_id)
        lingua = lingua_di(utente)
        dati = {
            "piano": abbonamento.plan.name, "data": data_in(abbonamento.period_end, lingua),
            "giorni": riga.giorni_promemoria_prova, "sconto": riga.sconto_prova,
            "importo": importo_in(prossimo_rinnovo(abbonamento) or 0, abbonamento.plan.currency, lingua),
        }
        esito = await manda(session, utente, "promemoria_prova", f"promemoria_prova:{abbonamento.id}", dati,
                            percorso="/trial")
        if esito != "già inviata":
            inviati += 1
            await aggancio_notifica(utente, "promemoria_prova", dati, session=session)
    return inviati


# ---- per il profilo e la console ------------------------------------------------------------------------------------


def abbonamento_json(abbonamento: Optional[Subscription], lang: Optional[str] = None, *, tolleranza: int = 7) -> Optional[Dict[str, Any]]:
    """Tutto ciò che la sezione «Abbonamento» del profilo mostra."""
    from .lingue import in_lingua

    if abbonamento is None:
        return None
    piano = abbonamento.plan
    successivo = abbonamento.piano_successivo
    fine_tolleranza = (
        abbonamento.pagamento_fallito_il + timedelta(days=tolleranza) if abbonamento.pagamento_fallito_il else None
    )
    return {
        "id": str(abbonamento.id),
        "piano": piano.slug,
        "nome": in_lingua(piano.nomi, lang, piano.name),
        "stato": abbonamento.status,
        "provider": abbonamento.provider,
        "store": nello_store(abbonamento),
        "gestione_store": GESTIONE_STORE.get(abbonamento.provider),
        "gratuito": gratuito(piano),
        "annuale": abbonamento.annuale,
        "prova": abbonamento.prova,
        "periodo_inizio": abbonamento.period_start.isoformat(),
        "periodo_fine": abbonamento.period_end.isoformat(),
        "disdetto_il": abbonamento.cancel_at.isoformat() if abbonamento.cancel_at else None,
        "rinnovo_automatico": abbonamento.rinnovo_automatico,
        "listino": abbonamento.listino,
        "importo_periodo": abbonamento.importo_periodo,
        "sconto_ricorrente": abbonamento.sconto_ricorrente,
        "prossimo_rinnovo": prossimo_rinnovo(abbonamento),
        "valuta": piano.currency,
        "fattura_aperta": abbonamento.fattura_aperta is not None,
        "pagamento_fallito_il": abbonamento.pagamento_fallito_il.isoformat() if abbonamento.pagamento_fallito_il else None,
        "fine_tolleranza": fine_tolleranza.isoformat() if fine_tolleranza else None,
        "piano_successivo": None if successivo is None else {
            "piano": successivo.slug, "nome": in_lingua(successivo.nomi, lang, successivo.name),
            "annuale": bool(abbonamento.annuale_successivo), "dal": abbonamento.period_end.isoformat(),
        },
        # Fase 2d: lo sconto del coupon che continua sui rinnovi («ancora 2 rinnovi», «per sempre»).
        "coupon": _coupon_json(abbonamento),
    }


def _coupon_json(abbonamento: Subscription) -> Optional[Dict[str, Any]]:
    from .offerte import coupon_attivo

    if not coupon_attivo(abbonamento) or abbonamento.coupon is None:
        return None
    c = abbonamento.coupon
    return {
        "codice": c.code, "tipo": c.tipo, "valore": c.valore, "cumulabile": c.cumulabile,
        "sconto": abbonamento.sconto_coupon, "per_sempre": abbonamento.coupon_rinnovi_rimasti is None,
        "rinnovi_rimasti": abbonamento.coupon_rinnovi_rimasti,
    }


async def ultimo_abbonamento(session: AsyncSession, user_id: int) -> Optional[Subscription]:
    """L'abbonamento vivo, o in mancanza l'ultimo sospeso con una fattura da saldare: il profilo mostra quello."""
    from .plans import GestoreAbbonamenti

    vivo = await GestoreAbbonamenti(session, provider=_SenzaFornitore()).abbonamento_di(user_id)
    if vivo is not None and not gratuito(vivo.plan):
        return vivo
    sospeso = (await session.execute(
        select(Subscription).where(Subscription.user_id == user_id, Subscription.status == "sospeso")
        .order_by(Subscription.created_at.desc()).limit(1)
    )).scalar_one_or_none()
    return sospeso or vivo


class _SenzaFornitore:
    """Per le sole letture: `GestoreAbbonamenti` non deve costruire il fornitore configurato per leggere."""

    name = "interno"

    async def crea_abbonamento(self, user_id: int, piano: Plan, *, annuale: bool = False) -> str:  # pragma: no cover
        raise RuntimeError("solo lettura")

    async def disdici(self, external_id: str) -> None:  # pragma: no cover
        return None

    async def e_pagato(self, external_id: str) -> bool:  # pragma: no cover
        return False
