"""Le letture comprese nell'abbonamento, i loro limiti, e da dove si paga una lettura.

**Quattro limiti (v9, Fase 2b)**: `letture_al_giorno`, `letture_alla_settimana`, `letture_al_mese` e
`letture_totali`. Un piano ne dichiara quanti vuole (`Plan.limits`); uno assente o negativo non limita.

**Finestre mobili, non il calendario.** È la scelta di Personalities, e vale anche qui: «al giorno» a mezzanotte UTC
significherebbe che a Roma il contatore si azzera all'una di notte, e che chi legge alle 23:50 e alle 00:10 ha usato
due giorni in venti minuti. Così il giorno sono le ultime 24 ore, la settimana gli ultimi 7 giorni, il mese gli
ultimi 30 (come il periodo mensile, `plans.GIORNI_PERIODO`). **Assunzione**: «totali» vuol dire *per periodo pagato*
dell'abbonamento — dall'inizio del periodo in corso (`period_start`) alla sua fine; col rinnovo il conto riparte.

**Oltre un limite** la lettura non parte da sola: il server risponde con il limite superato, quante letture sono già
state fatte nel periodo, i condoni rimasti e il saldo (`billing/abbonamenti.py`), e il sito chiede il consenso. Le
prime letture oltre il limite — due per periodo, dalla console — sono **condonate** (`consumo='condono'`): si contano
per limite e per periodo, nella stessa finestra del limite.

**L'ordine del pagamento.** Prima la quota dell'abbonamento, poi i crediti: i crediti comprati non scadono, e
consumarli per primi farebbe perdere all'utente ciò che il suo abbonamento gli dava.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.base import utcnow
from ..domain.models import Reading
from .entitlements import Diritti

logger = logging.getLogger(__name__)

#: La finestra delle letture «al giorno».
FINESTRA = timedelta(hours=24)

#: I limiti delle letture comprese, dal periodo più lungo al più corto: oltre più limiti insieme si dice quello che
#: dura di più (aspettare il giorno dopo non serve, se è finita la settimana).
LIMITI = ("letture_totali", "letture_al_mese", "letture_alla_settimana", "letture_al_giorno")

#: Le finestre mobili; `letture_totali` vale per il periodo pagato.
FINESTRE: Dict[str, timedelta] = {
    "letture_al_giorno": FINESTRA,
    "letture_alla_settimana": timedelta(days=7),
    "letture_al_mese": timedelta(days=30),
}

#: Quanto costa una lettura, in crediti. Fisso: un utente che guarda il
#: saldo deve poter dire quante letture gli restano.
COSTO_LETTURA = 1


@dataclass
class StatoLimite:
    """Un limite, adesso: quante letture comprese usate, quante fatte in tutto, i condoni già dati."""

    nome: str
    limite: Optional[int]
    usati: int
    fatte: int = 0
    condoni: int = 0
    dal: Optional[datetime] = None
    #: Quando si libera la prossima lettura compresa: la più vecchia esce dalla finestra, o finisce il periodo.
    si_libera: Optional[datetime] = None

    @property
    def superato(self) -> bool:
        return self.limite is not None and self.usati >= self.limite

    def to_dict(self) -> Dict[str, Optional[int]]:
        return {
            "usati": self.usati,
            "limite": self.limite,
            "restanti": None if self.limite is None else max(0, self.limite - self.usati),
        }


@dataclass
class Uso:
    limiti: Dict[str, StatoLimite] = field(default_factory=dict)

    @property
    def letture_24h(self) -> int:
        stato = self.limiti.get("letture_al_giorno")
        return stato.usati if stato else 0

    def to_dict(self, diritti: Optional[Diritti] = None) -> Dict[str, Dict[str, Optional[int]]]:
        return {nome: stato.to_dict() for nome, stato in self.limiti.items()}


class ContatoreQuote:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def inizio(self, nome: str, *, periodo_inizio: Optional[datetime] = None, adesso: Optional[datetime] = None) -> datetime:
        """Da quando si contano le letture di un limite."""
        adesso = adesso or utcnow()
        if nome == "letture_totali":
            return periodo_inizio or adesso - FINESTRE["letture_al_mese"]
        return adesso - FINESTRE[nome]

    async def _conta(self, user_id: int, dal: datetime, *consumi: str, limite: Optional[str] = None) -> int:
        condizioni = [Reading.owner_id == user_id, Reading.created_at >= dal]
        if consumi:
            condizioni.append(Reading.consumo.in_(consumi))
        if limite is not None:
            condizioni.append(Reading.limite == limite)
        return int(await self._session.scalar(select(func.count()).select_from(Reading).where(*condizioni)) or 0)

    async def letture_in_quota_24h(self, user_id: int) -> int:
        """Le letture pagate con la quota nelle ultime 24 ore (quelle con un credito o condonate non contano)."""
        return await self._conta(user_id, utcnow() - FINESTRA, "quota")

    async def stato(
        self, user_id: int, nome: str, limite: Optional[int], *,
        periodo_inizio: Optional[datetime] = None, periodo_fine: Optional[datetime] = None,
    ) -> StatoLimite:
        adesso = utcnow()
        dal = self.inizio(nome, periodo_inizio=periodo_inizio, adesso=adesso)
        usati = await self._conta(user_id, dal, "quota")
        stato = StatoLimite(nome=nome, limite=limite, usati=usati, dal=dal)
        if limite is not None and usati >= limite:
            stato.fatte = await self._conta(user_id, dal, "quota", "condono", "credito", "omaggio")
            stato.condoni = await self._conta(user_id, dal, "condono", limite=nome)
            if nome == "letture_totali":
                stato.si_libera = periodo_fine
            else:
                prima = await self._session.scalar(
                    select(func.min(Reading.created_at)).where(
                        Reading.owner_id == user_id, Reading.consumo == "quota", Reading.created_at >= dal,
                    )
                )
                stato.si_libera = (prima + FINESTRE[nome]) if prima is not None else None
        return stato

    async def uso(
        self, user_id: int, diritti: Optional[Diritti] = None, *,
        periodo_inizio: Optional[datetime] = None, periodo_fine: Optional[datetime] = None,
    ) -> Uso:
        """Lo stato di ogni limite del piano. Senza diritti, solo il giorno (com'era prima della Fase 2b)."""
        nomi: List[str] = ["letture_al_giorno"]
        if diritti is not None:
            nomi += [n for n in LIMITI if n != "letture_al_giorno" and n in diritti.limiti]
        uso = Uso()
        for nome in nomi:
            limite = diritti.limite(nome) if diritti is not None else None
            uso.limiti[nome] = await self.stato(
                user_id, nome, limite, periodo_inizio=periodo_inizio, periodo_fine=periodo_fine,
            )
        return uso

    async def superato(
        self, user_id: int, diritti: Diritti, *,
        periodo_inizio: Optional[datetime] = None, periodo_fine: Optional[datetime] = None,
    ) -> Optional[StatoLimite]:
        """Il limite superato che dura di più, o `None` se la quota copre ancora una lettura."""
        for nome in LIMITI:
            limite = diritti.limite(nome)
            if limite is None:
                continue
            stato = await self.stato(user_id, nome, limite, periodo_inizio=periodo_inizio, periodo_fine=periodo_fine)
            if stato.superato:
                return stato
        return None

    async def quota_disponibile(self, user_id: int, diritti: Diritti) -> bool:
        """Se l'abbonamento copre ancora una lettura nelle ultime 24 ore (solo il limite del giorno)."""
        if diritti.predefiniti:
            return False
        limite = diritti.limite("letture_al_giorno")
        if limite is None:
            return True
        if limite <= 0:
            return False
        return await self.letture_in_quota_24h(user_id) < limite
