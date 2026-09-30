/* La biblioteca delle carte e la pagina di una carta. */

import type { carte as Base } from "../en/carte";

export const carte: typeof Base = {
  meta_titolo: "A Thoth-tarot kártyatára",
  meta_descrizione: "A Thoth-tarot 78 kártyája: képek, megfelelések és jelentések, mindegyik egy-egy út egy kérdés felé.",
  eyebrow: "A Thoth-tarot kártyatára",
  titolo: "Nézd meg a kártyát, mielőtt megszólalásra kéred.",
  intro: "Minden kártya egy képet, megfelelések sorát és több szintű jelentést fog össze. A szerepe egy jóslásban mégis a pozíciótól, a körülötte lévő lapoktól és a kérdésedtől függ.",
  filtri: { tutte: "Mind", maggiori: "Nagy Arkánumok", bastoni: "Botok", coppe: "Kelyhek", spade: "Kardok", dischi: "Korongok" } as Record<string, string>,
  filtri_aria: "A kártyák szűrése",
  n_carte: { uno: "1 kártya", molti: "{n} kártya" },

  carta_eyebrow: "Thoth-tarot · {arcano}",
  carta_riflessione: "Kiindulópont az elmélkedéshez",
  carta_domanda: "Mire kéri a figyelmedet ez a kártya: {carta}?",
  carta_nota: "A jelentés a pozícióval, a környező lapokkal és a kérdéseddel együtt változik. Amit alább olvasol, nyelvként fogadd, ne ítéletként.",
  dritta: "Egyenes",
  rovesciata: "Fordított",
  rovesciata_nota: "A Thoth-hagyományban a fordított kártyát a szomszédos lapokkal való méltósága szerint olvassuk; ez az árnyékoldala.",
  livelli: { essoterico: "Első látásra", psicologico: "Benned", iniziatico: "Az úton", ombra: "Az árnyék" } as Record<string, string>,
  ambiti_titolo: "Szerelemben, munkában, szellemben",
  ambiti: { amore: "Szerelem", lavoro: "Munka", spirito: "Szellem" } as Record<string, string>,
  corrispondenze: "Megfelelések",
  sentiero: "{n}. ösvény",
  crowley: "Crowley jegyzete",
  parole: "Kulcsszavak",
  cta_leggi: "Olvasd ezt a kártyát egy rituáléban",
  cta_fisica: "Húzd ki a saját paklidból",
  articoli_su: "A naplóból",
  precedente: "Előző kártya",
  successiva: "Következő kártya",
  torna: "Vissza a kártyatárhoz",
  non_trovata: "Ez a kártya nincs a kártyatárban.",
};
