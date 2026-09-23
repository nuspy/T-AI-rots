"""La base di conoscenza: mazzo Thoth, stese e dottrina di lettura.

Si carica una volta sola e si valida al caricamento. Un mazzo con 77 carte o
una stesa che cita una posizione inesistente sono errori di rilascio: devono
fermare l'avvio, non comparire alla prima lettura di un utente.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..paths import KNOWLEDGE_DIR

logger = logging.getLogger(__name__)

CAMPI_CARTA = (
    "id", "arcano", "numero", "seme", "rango", "nome_thoth", "nome_it",
    "elemento", "parole_chiave", "significati", "dritto", "rovescio", "ambiti",
)


class ConoscenzaNonValida(ValueError):
    """La base di conoscenza non è coerente."""


@dataclass(frozen=True)
class Conoscenza:
    carte: Dict[str, Dict[str, Any]]
    ordine: List[str]
    stese: Dict[str, Dict[str, Any]]
    dottrina: str

    @classmethod
    def carica(cls, cartella=KNOWLEDGE_DIR) -> "Conoscenza":
        mazzo = json.loads((cartella / "deck.json").read_text(encoding="utf-8"))
        stese = json.loads((cartella / "spreads.json").read_text(encoding="utf-8"))
        dottrina_path = cartella / "doctrine.md"
        dottrina = dottrina_path.read_text(encoding="utf-8") if dottrina_path.exists() else ""
        conoscenza = cls(
            carte={c["id"]: c for c in mazzo},
            ordine=[c["id"] for c in mazzo],
            stese={s["id"]: s for s in stese},
            dottrina=dottrina,
        )
        conoscenza.valida()
        logger.info(
            "Base di conoscenza: %d carte, %d stese, dottrina di %d caratteri",
            len(conoscenza.carte), len(conoscenza.stese), len(dottrina),
        )
        return conoscenza

    def valida(self) -> None:
        if len(self.carte) != 78 or len(self.ordine) != 78:
            raise ConoscenzaNonValida(f"il mazzo ha {len(self.carte)} carte, non 78")
        maggiori = [c for c in self.carte.values() if c["arcano"] == "maggiore"]
        if len(maggiori) != 22:
            raise ConoscenzaNonValida(f"{len(maggiori)} Arcani maggiori invece di 22")
        for carta in self.carte.values():
            mancanti = [k for k in CAMPI_CARTA if k not in carta]
            if mancanti:
                raise ConoscenzaNonValida(f"{carta.get('id')}: mancano {mancanti}")
        for stesa in self.stese.values():
            numeri = [p["n"] for p in stesa["posizioni"]]
            if numeri != list(range(1, len(numeri) + 1)):
                raise ConoscenzaNonValida(f"{stesa['id']}: posizioni non consecutive")
            if stesa["mazzo"] not in ("maggiori", "completo"):
                raise ConoscenzaNonValida(f"{stesa['id']}: mazzo sconosciuto")
            da_scegliere = sum(1 for p in stesa["posizioni"] if not p.get("calcolata"))
            if da_scegliere != stesa["carte_da_scegliere"]:
                raise ConoscenzaNonValida(f"{stesa['id']}: carte da scegliere incoerenti")
            for linea in stesa.get("linee", []):
                if any(n not in numeri for n in linea):
                    raise ConoscenzaNonValida(f"{stesa['id']}: linea con posizioni inesistenti")

    # -- lettura ---------------------------------------------------------

    def carta(self, card_id: str) -> Dict[str, Any]:
        return self.carte[card_id]

    def stesa(self, spread_id: str) -> Optional[Dict[str, Any]]:
        return self.stese.get(spread_id)

    def mazzo_per(self, stesa: Dict[str, Any]) -> List[str]:
        """Le carte in gioco per una stesa: i 22 maggiori o tutte e 78."""
        if stesa["mazzo"] == "maggiori":
            return [i for i in self.ordine if self.carte[i]["arcano"] == "maggiore"]
        return list(self.ordine)

    def maggiore(self, numero: int) -> Dict[str, Any]:
        for carta in self.carte.values():
            if carta["arcano"] == "maggiore" and carta["numero"] == numero:
                return carta
        raise KeyError(numero)

    def posizione(self, stesa: Dict[str, Any], n: int) -> Dict[str, Any]:
        return stesa["posizioni"][n - 1]

    def carta_pubblica(self, card_id: str, *, completa: bool = False) -> Dict[str, Any]:
        """Ciò che il frontend riceve di una carta rivelata.

        Senza `completa` si tolgono i testi lunghi: il pallino sopra la carta
        mostra l'interpretazione della lettura, non l'enciclopedia.
        """
        c = self.carte[card_id]
        base = {
            k: c.get(k) for k in (
                "id", "arcano", "numero", "numero_romano", "seme", "rango",
                "nome_thoth", "titolo_thoth", "nome_it", "lettera_ebraica",
                "elemento", "astrologia", "parole_chiave", "colori",
            )
        }
        if completa:
            base.update({
                k: c.get(k) for k in (
                    "percorso", "collega", "sefira", "significati", "dritto",
                    "rovescio", "ambiti", "nota_crowley",
                )
            })
        return base

    def stesa_pubblica(self, stesa: Dict[str, Any]) -> Dict[str, Any]:
        return {
            k: stesa.get(k) for k in (
                "id", "nome", "nome_en", "mazzo", "carte_da_scegliere", "origine",
                "descrizione", "posizioni", "regole", "coppie",
            )
        } | {"sintesi_wirth": bool(stesa.get("sintesi_wirth"))}
