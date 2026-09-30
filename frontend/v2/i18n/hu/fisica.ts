/* Le proprie carte: si pesca con il proprio mazzo, si posano le carte, il lettore interpreta. */

import type { fisica as Base } from "../en/fisica";

export const fisica: typeof Base = {
  meta_titolo: "Értelmezd a saját kártyáidat",
  meta_descrizione: "Húzd ki a kártyákat a saját tarot-paklidból, tedd őket egy kirakás helyeire, és kapj vezetett értelmezést.",
  eyebrow: "Fizikai tarot",
  titolo: "A kezed húzza ki a kártyákat. A tarotolvasód segít meghallani a mintázatot.",
  intro: "Válaszd ki a kirakást, amelyet használtál, nevezd meg a ténylegesen kihúzott lapokat, aztán add hozzá a kérdésed. Semmit sem húzunk újra: a jóslás a te asztalodról indul.",

  passo_1: "1 · Tedd a helyükre a kártyákat",
  stesa_titolo: "Melyik kirakást raktad ki?",
  cambia_stesa: "Válassz másik kirakást",
  posiziona: "Érintsd meg az egyes pozíciókat, és nevezd meg a kártyát, amelyet ott találtál.",
  aggiungi: "Megnevezés",
  modifica: "Csere",
  mancano: "Még {n} pozíciót kell megnevezni",
  manca_una: "Még egy pozíciót kell megnevezni",
  pronte: "Minden kártya a helyén van.",

  passo_2: "2 · Adj neki egy kérdést",
  domanda_titolo: "Mit segítsenek megvizsgálni a kártyák?",
  domanda_segnaposto: "Írd le a kérdésed a saját szavaiddal…",
  domanda_testo: "A fizikai húzásod a tiéd marad. Az értelmezés akkor kezdődik, amikor megnevezed, mit szeretnél megérteni.",
  interpreta: "Értelmezd a kártyáimat",
  serve_account: "A saját kártyáid értelmezéséhez ingyenes fiók kell: az asztalod és a kérdésed megmarad, amíg belépsz.",
  entra: "Lépj be a folytatáshoz",

  seme_titolo: "{posizione}: melyik szín?",
  carta_titolo: "{posizione}: melyik kártya?",
  semi: { maggiori: "Nagy Arkánumok", bastoni: "Botok", coppe: "Kelyhek", spade: "Kardok", dischi: "Korongok" },
  conferma: "Tedd ide ezt a kártyát",
  gia_posata: "már az asztalon van",
};
