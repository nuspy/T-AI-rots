"""La base di conoscenza: mazzo Thoth, stese e dottrina di lettura.

Si carica una volta sola e si valida al caricamento. Un mazzo con 77 carte o
una stesa che cita una posizione inesistente sono errori di rilascio: devono
fermare l'avvio, non comparire alla prima lettura di un utente.

I **nomi** in altre lingue stanno in `nomi.json` (oggi l'ungherese): sono
dati, non testo dell'interfaccia, e vengono validati come il mazzo — una carta
o una posizione senza traduzione ferma l'avvio.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..paths import KNOWLEDGE_DIR
from .lingue import lingua

logger = logging.getLogger(__name__)

CAMPI_CARTA = (
    "id", "arcano", "numero", "seme", "rango", "nome_thoth", "nome_it",
    "elemento", "parole_chiave", "significati", "dritto", "rovescio", "ambiti",
)


class ConoscenzaNonValida(ValueError):
    """La base di conoscenza non è coerente."""


def _nome_inglese_carta(carta: Dict[str, Any]) -> str:
    """«Three of Cups — Abundance»: il nome di Thoth col suo titolo."""
    titolo = carta.get("titolo_thoth")
    return f"{carta['nome_thoth']} — {titolo}" if titolo else carta["nome_thoth"]


@dataclass(frozen=True)
class Conoscenza:
    carte: Dict[str, Dict[str, Any]]
    ordine: List[str]
    stese: Dict[str, Dict[str, Any]]
    dottrina: str
    #: lingua → {"carte": {id: nome}, "stese": {id: {"nome", "posizioni": {n: nome}}}}
    nomi: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    @classmethod
    def carica(cls, cartella=KNOWLEDGE_DIR) -> "Conoscenza":
        mazzo = json.loads((cartella / "deck.json").read_text(encoding="utf-8"))
        stese = json.loads((cartella / "spreads.json").read_text(encoding="utf-8"))
        dottrina_path = cartella / "doctrine.md"
        dottrina = dottrina_path.read_text(encoding="utf-8") if dottrina_path.exists() else ""
        nomi_path = cartella / "nomi.json"
        nomi = json.loads(nomi_path.read_text(encoding="utf-8")) if nomi_path.exists() else {}
        conoscenza = cls(
            carte={c["id"]: c for c in mazzo},
            ordine=[c["id"] for c in mazzo],
            stese={s["id"]: s for s in stese},
            dottrina=dottrina,
            nomi=nomi,
        )
        conoscenza.valida()
        logger.info(
            "Base di conoscenza: %d carte, %d stese, dottrina di %d caratteri, nomi in %s",
            len(conoscenza.carte), len(conoscenza.stese), len(dottrina), ", ".join(nomi) or "nessuna lingua",
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
            # L'ordine del racconto tocca ogni posizione una volta sola.
            racconto = stesa.get("racconto")
            if racconto is None or sorted(racconto) != numeri:
                raise ConoscenzaNonValida(f"{stesa['id']}: `racconto` non è una permutazione delle posizioni")
        for codice, per_lingua in self.nomi.items():
            senza_carte = [i for i in self.carte if i not in per_lingua.get("carte", {})]
            if senza_carte:
                raise ConoscenzaNonValida(f"nomi {codice}: mancano le carte {senza_carte[:3]}…")
            for stesa in self.stese.values():
                tradotta = per_lingua.get("stese", {}).get(stesa["id"])
                if not tradotta or not tradotta.get("nome"):
                    raise ConoscenzaNonValida(f"nomi {codice}: manca la stesa {stesa['id']}")
                manca = [p["n"] for p in stesa["posizioni"] if str(p["n"]) not in tradotta.get("posizioni", {})]
                if manca:
                    raise ConoscenzaNonValida(f"nomi {codice}: {stesa['id']} senza le posizioni {manca}")

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

    # -- nomi nelle lingue --------------------------------------------------

    def nome_carta(self, card_id: str, lang: str) -> str:
        """Il nome della carta nella lingua: italiano, ungherese o, altrove, il
        nome di Thoth in inglese (che è lo standard internazionale)."""
        carta = self.carte[card_id]
        codice = lingua(lang)
        if codice == "it":
            return carta["nome_it"]
        tradotto = self.nomi.get(codice, {}).get("carte", {}).get(card_id)
        return tradotto or _nome_inglese_carta(carta)

    def nome_stesa(self, stesa: Dict[str, Any], lang: str) -> str:
        codice = lingua(lang)
        if codice == "it":
            return stesa["nome"]
        tradotto = self.nomi.get(codice, {}).get("stese", {}).get(stesa["id"], {}).get("nome")
        return tradotto or stesa.get("nome_en") or stesa["nome"]

    def nome_posizione(self, stesa: Dict[str, Any], n: int, lang: str) -> str:
        posizione = self.posizione(stesa, n)
        codice = lingua(lang)
        if codice == "it":
            return posizione["nome"]
        tradotto = (
            self.nomi.get(codice, {}).get("stese", {}).get(stesa["id"], {}).get("posizioni", {}).get(str(n))
        )
        return tradotto or posizione.get("nome_en") or posizione["nome"]

    def _nomi_carta(self, carta: Dict[str, Any]) -> Dict[str, str]:
        nomi = {"en": _nome_inglese_carta(carta)}
        for codice, per_lingua in self.nomi.items():
            nome = per_lingua.get("carte", {}).get(carta["id"])
            if nome:
                nomi[codice] = nome
        return nomi

    # -- ciò che esce verso il frontend --------------------------------------

    def carta_pubblica(self, card_id: str, *, completa: bool = False) -> Dict[str, Any]:
        """Ciò che il frontend riceve di una carta rivelata.

        Senza `completa` si tolgono i testi lunghi: il pallino sopra la carta
        mostra l'interpretazione della lettura, non l'enciclopedia. `nomi` porta
        il nome nelle altre lingue (`en` sempre, e quelle di `nomi.json`).
        """
        c = self.carte[card_id]
        base = {
            k: c.get(k) for k in (
                "id", "arcano", "numero", "numero_romano", "seme", "rango",
                "nome_thoth", "titolo_thoth", "nome_it", "lettera_ebraica",
                "elemento", "astrologia", "parole_chiave", "colori",
            )
        }
        base["nomi"] = self._nomi_carta(c)
        if completa:
            base.update({
                k: c.get(k) for k in (
                    "percorso", "collega", "sefira", "significati", "dritto",
                    "rovescio", "ambiti", "nota_crowley",
                )
            })
        return base

    def stesa_pubblica(self, stesa: Dict[str, Any]) -> Dict[str, Any]:
        def nomi_di(nome_en: Optional[str], estrai) -> Dict[str, str]:
            nomi = {"en": nome_en} if nome_en else {}
            for codice, per_lingua in self.nomi.items():
                nome = estrai(per_lingua.get("stese", {}).get(stesa["id"], {}))
                if nome:
                    nomi[codice] = nome
            return nomi

        posizioni = [
            p | {"nomi": nomi_di(p.get("nome_en"), lambda t, n=p["n"]: t.get("posizioni", {}).get(str(n)))}
            for p in stesa["posizioni"]
        ]
        return {
            k: stesa.get(k) for k in (
                "id", "nome", "nome_en", "mazzo", "carte_da_scegliere", "origine",
                "descrizione", "regole", "coppie",
            )
        } | {
            "posizioni": posizioni,
            "nomi": nomi_di(stesa.get("nome_en"), lambda t: t.get("nome")),
            "sintesi_wirth": bool(stesa.get("sintesi_wirth")),
        }
