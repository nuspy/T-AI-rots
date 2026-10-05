"""La base di conoscenza: mazzo Thoth, stese e dottrina di lettura.

Si carica una volta sola e si valida al caricamento. Un mazzo con 77 carte o
una stesa che cita una posizione inesistente sono errori di rilascio: devono
fermare l'avvio, non comparire alla prima lettura di un utente.

I **nomi** in altre lingue stanno in `nomi.json` (ungherese, russo, ucraino e spagnolo): sono
dati, non testo dell'interfaccia, e vengono validati come il mazzo — una carta
o una posizione senza traduzione ferma l'avvio.

I **testi lunghi** (significati, attribuzioni, regole delle stese) esistono in italiano
e in inglese: quelli inglesi stanno in `knowledge/en/` (`cards-*.json`, `spreads-*.json`,
`termini.json`) e sono la lingua **canonica delle pagine pubbliche**: l'SEO internazionale
si fa in inglese. Anch'essi si validano all'avvio: una carta senza la sua scheda inglese, o
due slug uguali, sono errori di rilascio.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from functools import cached_property, lru_cache
from typing import Any, Dict, List, Optional

from ..paths import KNOWLEDGE_DIR
from .blog import slugify
from .lingue import lingua

logger = logging.getLogger(__name__)

#: Le categorie di stesa: la lettura standard, quella di lavoro e affari e le due letture speciali.
CATEGORIE = ("standard", "lavoro", "compatibilita", "coppia")

#: Le letture speciali: quelle che chiedono i dati di una seconda persona. Le altre (`standard`,
#: `lavoro`) si svolgono allo stesso modo, con la sola persona che consulta.
CATEGORIE_SPECIALI = ("compatibilita", "coppia")

#: I temi per cui una stesa standard si propone anche fuori dalla sua categoria: una stesa con
#: `"temi": ["lavoro"]` compare anche fra quelle di lavoro e affari (la Croce Celtica, il ferro di cavallo…).
TEMI = ("lavoro",)

#: Lo stile di una stesa speciale o di lavoro: come la si trova nella tradizione.
STILI = ("tradizionale", "moderna", "tendenza")

#: Di chi è il vissuto che una posizione descrive (solo nelle stese speciali).
SOGGETTI = ("tu", "partner", "coppia", "strada-a", "strada-b")

#: Le lingue dei testi lunghi. L'italiano sta nei dati originali, le altre in `knowledge/<codice>/`.
LINGUE_CONTENUTO = ("it", "en")

#: Cosa deve avere la scheda di una carta e di una stesa in un'altra lingua.
CAMPI_TESTO_CARTA = ("astro", "kw", "exo", "psy", "ini", "sha", "up", "rev", "love", "work", "spirit", "crowley")
CAMPI_TESTO_STESA = ("slug", "nome", "origine", "descrizione", "regole", "pos")
CAMPI_TESTO_POSIZIONE = ("nome", "significato", "domanda")

CAMPI_CARTA = (
    "id", "arcano", "numero", "seme", "rango", "nome_thoth", "nome_it",
    "elemento", "parole_chiave", "significati", "dritto", "rovescio", "ambiti",
)


class ConoscenzaNonValida(ValueError):
    """La base di conoscenza non è coerente."""


def speciale(categoria: str) -> bool:
    """Una lettura con due persone (compatibilità, coppia): chiede il partner e ha le regole sulle relazioni.
    La standard e quella di lavoro no."""
    return categoria in CATEGORIE_SPECIALI


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
    #: lingua → {"carte": {id: scheda}, "stese": {id: scheda}, "termini": {...}}: i testi lunghi tradotti.
    testi: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    @classmethod
    def carica(cls, cartella=KNOWLEDGE_DIR) -> "Conoscenza":
        mazzo = json.loads((cartella / "deck.json").read_text(encoding="utf-8"))
        stese = json.loads((cartella / "spreads.json").read_text(encoding="utf-8"))
        dottrina_path = cartella / "doctrine.md"
        # `\r\n`→`\n`: il prefisso di prompt che include questo testo deve restare byte-identico
        # a prescindere da come git ha fatto il checkout (`core.autocrlf` su Windows altrimenti
        # introduce CRLF silenziosamente, cambiando l'impronta del prefisso stabile).
        dottrina = (
            dottrina_path.read_text(encoding="utf-8").replace("\r\n", "\n")
            if dottrina_path.exists() else ""
        )
        nomi_path = cartella / "nomi.json"
        nomi = json.loads(nomi_path.read_text(encoding="utf-8")) if nomi_path.exists() else {}
        testi = _carica_testi(cartella)
        conoscenza = cls(
            carte={c["id"]: c for c in mazzo},
            ordine=[c["id"] for c in mazzo],
            stese={s["id"]: s for s in stese},
            dottrina=dottrina,
            nomi=nomi,
            testi=testi,
        )
        conoscenza.valida()
        logger.info(
            "Base di conoscenza: %d carte, %d stese, dottrina di %d caratteri, nomi in %s, testi in %s",
            len(conoscenza.carte), len(conoscenza.stese), len(dottrina), ", ".join(nomi) or "nessuna lingua",
            ", ".join(testi) or "solo italiano",
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
            self._valida_geometria(stesa)
            self._valida_categoria(stesa)
        self._valida_copertura_stili()
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

        self._valida_testi()

    def _valida_testi(self) -> None:
        """I testi lunghi tradotti coprono tutto il catalogo, con gli stessi campi e slug distinti."""
        for codice, per_lingua in self.testi.items():
            carte = per_lingua.get("carte", {})
            senza = [i for i in self.carte if i not in carte]
            if senza:
                raise ConoscenzaNonValida(f"testi {codice}: mancano le carte {senza[:3]}…")
            extra = [i for i in carte if i not in self.carte]
            if extra:
                raise ConoscenzaNonValida(f"testi {codice}: carte inesistenti {extra[:3]}")
            for card_id, scheda in carte.items():
                mancanti = [k for k in CAMPI_TESTO_CARTA if not scheda.get(k)]
                if mancanti:
                    raise ConoscenzaNonValida(f"testi {codice}: {card_id} senza {mancanti}")
                if len(scheda["kw"]) != len(self.carte[card_id]["parole_chiave"]):
                    raise ConoscenzaNonValida(f"testi {codice}: {card_id} ha un numero diverso di parole chiave")
            termini = per_lingua.get("termini", {})
            for campo in ("elemento", "seme", "rango", "arcano"):
                valori = {c.get(campo) for c in self.carte.values() if c.get(campo)}
                senza_termine = sorted(v for v in valori if v not in termini.get(campo, {}))
                if senza_termine:
                    raise ConoscenzaNonValida(f"testi {codice}: termini «{campo}» mancanti {senza_termine}")
            stese = per_lingua.get("stese", {})
            for stesa in self.stese.values():
                scheda = stese.get(stesa["id"])
                if not scheda:
                    raise ConoscenzaNonValida(f"testi {codice}: manca la stesa {stesa['id']}")
                mancanti = [k for k in CAMPI_TESTO_STESA if not scheda.get(k)]
                if mancanti:
                    raise ConoscenzaNonValida(f"testi {codice}: {stesa['id']} senza {mancanti}")
                if len(scheda["regole"]) != len(stesa["regole"]):
                    raise ConoscenzaNonValida(f"testi {codice}: {stesa['id']} ha un numero diverso di regole")
                for p in stesa["posizioni"]:
                    tradotta = scheda["pos"].get(str(p["n"]))
                    if not tradotta or any(not tradotta.get(k) for k in CAMPI_TESTO_POSIZIONE):
                        raise ConoscenzaNonValida(f"testi {codice}: {stesa['id']} posizione {p['n']} incompleta")
            slug_carte = [self._slug_carta_in(codice, i) for i in self.carte]
            slug_stese = [scheda["slug"] for scheda in stese.values()]
            for tipo, slug in (("carte", slug_carte), ("stese", slug_stese)):
                if len(set(slug)) != len(slug):
                    raise ConoscenzaNonValida(f"testi {codice}: slug duplicati fra le {tipo}")

    def _valida_geometria(self, stesa: Dict[str, Any]) -> None:
        """Le coordinate stanno sul tavolo e la larghezza delle carte è sensata."""
        for p in stesa["posizioni"]:
            if not (0 <= p["x"] <= 1 and 0 <= p["y"] <= 1):
                raise ConoscenzaNonValida(f"{stesa['id']}: la posizione {p['n']} è fuori dal tavolo")
        for campo in ("larghezza", "larghezza_stretto"):
            valore = stesa.get(campo)
            if valore is not None and not 0.05 <= valore <= 0.2:
                raise ConoscenzaNonValida(f"{stesa['id']}: `{campo}` fuori da 0.05–0.2")
        if stesa.get("forma", "standard") not in ("standard", "quadrata"):
            raise ConoscenzaNonValida(f"{stesa['id']}: `forma` sconosciuta")

    def _valida_categoria(self, stesa: Dict[str, Any]) -> None:
        """Le stese speciali hanno stile e soggetto; quelle di lavoro uno stile e nessun soggetto; le
        standard nessuno dei due, e solo loro possono proporsi per altri `temi`."""
        categoria = stesa.get("categoria", "standard")
        if categoria not in CATEGORIE:
            raise ConoscenzaNonValida(f"{stesa['id']}: categoria sconosciuta «{categoria}»")
        self._valida_temi(stesa, categoria)
        if categoria == "standard":
            if stesa.get("stile"):
                raise ConoscenzaNonValida(f"{stesa['id']}: una stesa standard non ha `stile`")
            return
        if stesa.get("stile") not in STILI:
            raise ConoscenzaNonValida(f"{stesa['id']}: `stile` mancante o sconosciuto")
        if stesa.get("sintesi_wirth"):
            raise ConoscenzaNonValida(f"{stesa['id']}: la sintesi di Wirth è solo della croce semplice")
        if not speciale(categoria):
            # Lavoro e affari: una persona sola, quindi nessun soggetto; e nessuna carta calcolata.
            for p in stesa["posizioni"]:
                if p.get("calcolata"):
                    raise ConoscenzaNonValida(f"{stesa['id']}: una stesa di {categoria} non ha carte calcolate")
                if "soggetto" in p:
                    raise ConoscenzaNonValida(f"{stesa['id']}: una stesa di {categoria} non ha `soggetto`")
            return
        for p in stesa["posizioni"]:
            if p.get("calcolata"):
                raise ConoscenzaNonValida(f"{stesa['id']}: una stesa speciale non ha carte calcolate")
            if p.get("soggetto") not in SOGGETTI:
                raise ConoscenzaNonValida(f"{stesa['id']}: la posizione {p['n']} non ha un `soggetto` valido")
            if p["soggetto"].startswith("strada-") and categoria != "coppia":
                raise ConoscenzaNonValida(f"{stesa['id']}: le strade sono solo della coppia")

    @staticmethod
    def _valida_temi(stesa: Dict[str, Any], categoria: str) -> None:
        """`temi`: una lista di temi noti, senza doppioni, e solo nelle stese standard (una stesa
        speciale chiede il partner, quindi non si può proporre per un tema da una persona sola)."""
        if "temi" not in stesa:
            return
        temi = stesa["temi"]
        if not isinstance(temi, list) or not temi:
            raise ConoscenzaNonValida(f"{stesa['id']}: `temi` dev'essere una lista non vuota")
        if categoria != "standard":
            raise ConoscenzaNonValida(f"{stesa['id']}: solo una stesa standard ha `temi`")
        sconosciuti = [t for t in temi if t not in TEMI]
        if sconosciuti:
            raise ConoscenzaNonValida(f"{stesa['id']}: temi sconosciuti {sconosciuti}")
        if len(set(temi)) != len(temi):
            raise ConoscenzaNonValida(f"{stesa['id']}: temi ripetuti")

    def _valida_copertura_stili(self) -> None:
        """Ogni lettura speciale offre almeno una stesa per ciascuno stile."""
        for categoria in ("compatibilita", "coppia"):
            stili = {s.get("stile") for s in self.stese_per(categoria)}
            mancanti = [x for x in STILI if x not in stili]
            if mancanti:
                raise ConoscenzaNonValida(f"{categoria}: nessuna stesa di stile {mancanti}")

    # -- lettura ---------------------------------------------------------

    def carta(self, card_id: str) -> Dict[str, Any]:
        return self.carte[card_id]

    def stesa(self, spread_id: str) -> Optional[Dict[str, Any]]:
        return self.stese.get(spread_id)

    @staticmethod
    def categoria_di(stesa: Dict[str, Any]) -> str:
        """`standard`, `lavoro`, `compatibilita` o `coppia`: l'assenza del campo è standard."""
        return stesa.get("categoria", "standard")

    def stese_per(self, categoria: str) -> List[Dict[str, Any]]:
        """Le stese di una categoria, nell'ordine del catalogo."""
        return [s for s in self.stese.values() if self.categoria_di(s) == categoria]

    def stese_per_tema(self, tema: str) -> List[Dict[str, Any]]:
        """Le stese che il sito propone per un tema (oggi `lavoro`): quelle della categoria omonima
        e, dopo, le standard che lo dichiarano in `temi`. Ciascuna nell'ordine del catalogo."""
        proprie = self.stese_per(tema)
        adatte = [s for s in self.stese.values() if tema in s.get("temi", ()) and s not in proprie]
        return proprie + adatte

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
        """Il nome della carta nella lingua: italiano, una lingua di `nomi.json` o, altrove, il
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

    # -- la lingua dei testi lunghi e gli indirizzi delle pagine ---------------

    def lingua_contenuto(self, lang: Optional[str]) -> str:
        """`it` o `en`: la lingua dei testi lunghi di una carta o di una stesa.

        Senza lingua (o con `it`) l'italiano, com'è sempre stato: chi non la chiede non vede
        cambiare niente. Ogni altra lingua ricade sull'inglese, la lingua internazionale delle
        pagine pubbliche.
        """
        if not lang:
            return "it"
        if lingua(lang) == "it":
            return "it"
        return "en" if "en" in self.testi else "it"

    def _slug_carta_in(self, codice: str, card_id: str) -> str:
        carta = self.carte[card_id]
        return slugify(carta["nome_it"] if codice == "it" else carta["nome_thoth"])

    def slug_carta(self, card_id: str, lang: Optional[str] = None) -> str:
        """L'indirizzo della carta: `la-stella` in italiano, `the-star` in inglese."""
        return self._slug_carta_in(self.lingua_contenuto(lang), card_id)

    def slug_stesa(self, spread_id: str, lang: Optional[str] = None) -> str:
        """`croce-celtica` in italiano (l'id stesso), `celtic-cross` in inglese."""
        codice = self.lingua_contenuto(lang)
        return spread_id if codice == "it" else self.testi[codice]["stese"][spread_id]["slug"]

    @cached_property
    def _indice_carte(self) -> Dict[str, str]:
        indice: Dict[str, str] = {}
        for card_id in self.carte:
            indice[card_id] = card_id
        for card_id in self.carte:
            for codice in ("it", *self.testi):
                indice.setdefault(self._slug_carta_in(codice, card_id), card_id)
        return indice

    @cached_property
    def _indice_stese(self) -> Dict[str, str]:
        indice: Dict[str, str] = {spread_id: spread_id for spread_id in self.stese}
        for per_lingua in self.testi.values():
            for spread_id, scheda in per_lingua.get("stese", {}).items():
                indice.setdefault(scheda["slug"], spread_id)
        return indice

    def risolvi_carta(self, chiave: str) -> Optional[str]:
        """L'id di una carta da un id o da uno slug in qualunque lingua (`maj-17`, `la-stella`, `the-star`)."""
        return self._indice_carte.get((chiave or "").strip().lower())

    def risolvi_stesa(self, chiave: str) -> Optional[str]:
        """L'id di una stesa da un id o da uno slug (`croce-celtica`, `celtic-cross`)."""
        return self._indice_stese.get((chiave or "").strip().lower())

    # -- ciò che esce verso il frontend --------------------------------------

    def carta_pubblica(self, card_id: str, *, completa: bool = False, lang: Optional[str] = None) -> Dict[str, Any]:
        """Ciò che il frontend riceve di una carta rivelata.

        Senza `completa` si tolgono i testi lunghi: il pallino sopra la carta
        mostra l'interpretazione della lettura, non l'enciclopedia. `nomi` porta
        il nome nelle altre lingue (`en` sempre, e quelle di `nomi.json`).

        Con `lang="en"` i testi (parole chiave, attribuzioni, significati) sono quelli inglesi
        e le etichette dei termini (`elemento_label`…) sono tradotte; `nome` e `slug` sono
        sempre nella lingua dei testi, e `slugs` porta l'indirizzo in ciascuna lingua (per
        `hreflang`). I campi grezzi (`elemento`, `seme`, `arcano`) non cambiano mai.
        """
        c = self.carte[card_id]
        codice = self.lingua_contenuto(lang)
        base = {
            k: c.get(k) for k in (
                "id", "arcano", "numero", "numero_romano", "seme", "rango",
                "nome_thoth", "titolo_thoth", "nome_it", "lettera_ebraica",
                "elemento", "astrologia", "parole_chiave", "colori",
            )
        }
        base["nomi"] = self._nomi_carta(c)
        base["lang"] = codice
        base["nome"] = self.nome_carta(card_id, codice)
        base["slug"] = self.slug_carta(card_id, codice)
        base["slugs"] = {k: self.slug_carta(card_id, k) for k in ("it", *self.testi)}
        scheda = self.testi[codice]["carte"][card_id] if codice != "it" else None
        if scheda is not None:
            termini = self.testi[codice]["termini"]
            base["parole_chiave"] = scheda["kw"]
            base["astrologia"] = scheda["astro"]
            for campo in ("elemento", "seme", "rango", "arcano"):
                valore = c.get(campo)
                base[f"{campo}_label"] = termini[campo].get(valore) if valore else None
        if completa:
            base.update({
                k: c.get(k) for k in (
                    "percorso", "collega", "sefira", "significati", "dritto",
                    "rovescio", "ambiti", "nota_crowley",
                )
            })
            if scheda is not None:
                base.update({
                    "significati": {
                        "essoterico": scheda["exo"], "psicologico": scheda["psy"],
                        "iniziatico": scheda["ini"], "ombra": scheda["sha"],
                    },
                    "dritto": scheda["up"],
                    "rovescio": scheda["rev"],
                    "ambiti": {"amore": scheda["love"], "lavoro": scheda["work"], "spirito": scheda["spirit"]},
                    "nota_crowley": scheda["crowley"],
                })
        return base

    def _tradizioni(self, stesa: Dict[str, Any]) -> Dict[str, str]:
        """La tradizione di una stesa in ogni lingua che ce l'ha: italiano e inglese dai testi, le altre da `nomi.json`."""
        tradizioni: Dict[str, str] = {}
        if stesa.get("tradizione"):
            tradizioni["it"] = stesa["tradizione"]
        for codice, per_lingua in self.testi.items():
            valore = per_lingua.get("stese", {}).get(stesa["id"], {}).get("tradizione")
            if valore:
                tradizioni[codice] = valore
        for codice, per_lingua in self.nomi.items():
            valore = per_lingua.get("stese", {}).get(stesa["id"], {}).get("tradizione")
            if valore:
                tradizioni[codice] = valore
        return tradizioni

    def stesa_pubblica(self, stesa: Dict[str, Any], lang: Optional[str] = None) -> Dict[str, Any]:
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
        codice = self.lingua_contenuto(lang)
        pubblica = {
            k: stesa.get(k) for k in (
                "id", "nome", "nome_en", "mazzo", "carte_da_scegliere", "origine",
                "descrizione", "regole", "coppie", "stile", "larghezza", "larghezza_stretto",
            )
        } | {
            "categoria": self.categoria_di(stesa),
            # I temi per cui una stesa standard si propone anche altrove (`["lavoro"]`); sempre una lista.
            "temi": list(stesa.get("temi", [])),
            "forma": stesa.get("forma", "standard"),
            "posizioni": posizioni,
            "nomi": nomi_di(stesa.get("nome_en"), lambda t: t.get("nome")),
            # La tradizione in poche parole («love», «Celtic tradition», «work», v9.4): nella lingua dei testi, e in
            # `tradizioni` in ogni lingua che ce l'ha (come `nomi`).
            "tradizione": stesa.get("tradizione"),
            "tradizioni": self._tradizioni(stesa),
            "sintesi_wirth": bool(stesa.get("sintesi_wirth")),
            "lang": codice,
            "slug": self.slug_stesa(stesa["id"], codice),
            "slugs": {k: self.slug_stesa(stesa["id"], k) for k in ("it", *self.testi)},
        }
        if codice != "it":
            per_lingua = self.testi[codice]
            scheda = per_lingua["stese"][stesa["id"]]
            termini = per_lingua["termini"]
            pubblica |= {
                "nome": scheda["nome"], "origine": scheda["origine"], "descrizione": scheda["descrizione"],
                "tradizione": scheda.get("tradizione") or stesa.get("tradizione"),
                "regole": scheda["regole"],
                "mazzo_label": termini.get("mazzo", {}).get(stesa["mazzo"]),
                "categoria_label": termini.get("categoria", {}).get(pubblica["categoria"]),
                "stile_label": termini.get("stile", {}).get(stesa.get("stile") or ""),
            }
            for p in pubblica["posizioni"]:
                testo = scheda["pos"][str(p["n"])]
                p["nome"], p["significato"], p["domanda"] = testo["nome"], testo["significato"], testo["domanda"]
        return pubblica


@lru_cache(maxsize=1)
def condivisa() -> Conoscenza:
    """La base di conoscenza, caricata una volta per processo: per chi non passa dall'API (il blog che risolve le
    scorciatoie `[[card:the-star]]` quando salva un articolo)."""
    return Conoscenza.carica()


def _carica_testi(cartella) -> Dict[str, Dict[str, Any]]:
    """`knowledge/<lingua>/` → carte, stese e termini nella lingua. Senza cartella, solo l'italiano."""
    testi: Dict[str, Dict[str, Any]] = {}
    for codice in LINGUE_CONTENUTO:
        if codice == "it":
            continue
        sotto = cartella / codice
        if not sotto.is_dir():
            continue
        per_lingua: Dict[str, Any] = {"carte": {}, "stese": {}, "termini": {}}
        for chiave, modello in (("carte", "cards-*.json"), ("stese", "spreads-*.json")):
            for file in sorted(sotto.glob(modello)):
                parte = json.loads(file.read_text(encoding="utf-8"))
                doppie = set(parte) & set(per_lingua[chiave])
                if doppie:
                    raise ConoscenzaNonValida(f"testi {codice}: {file.name} ripete {sorted(doppie)[:3]}")
                per_lingua[chiave].update(parte)
        termini = sotto / "termini.json"
        if termini.exists():
            per_lingua["termini"] = json.loads(termini.read_text(encoding="utf-8"))
        testi[codice] = per_lingua
    return testi
