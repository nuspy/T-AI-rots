/* Metodo e privacy: i contenuti legali del sito (stesso titolare, stesse scelte, stesse statistiche), più che cosa
 * ricorda il lettore e come si usa l'AI. */

import type { privacy as Base } from "../en/privacy";

export const privacy: typeof Base = {
  meta_titolo: "Módszer és adatvédelem",
  meta_descrizione: "Mit őrzünk meg, miért, és hogyan döntesz: jóslások, emlékezet, statisztikák és sütik.",
  eyebrow: "Módszer és adatvédelem",
  titolo: "A misztikus nem jelenti azt, hogy átláthatatlan.",
  intro: "Mit őrzünk meg, miért, és hogyan döntesz. Ugyanezek a szabályok érvényesek a TAROTS chat minden oldalán.",

  letture_titolo: "A jóslásaid és az emlékezeted",
  letture_testo: "A jóslásokat a fiókodban őrizzük, hogy visszatérhess hozzájuk. Amire a tarotolvasód emlékszik, az a jóslásaidból és beszélgetéseidből származik, és A történetemben bármikor átnézheted, módosíthatod vagy törölheted. Egy jóslás törlése véglegesen eltávolítja.",
  letture_cta: "Kezeld, mire emlékszik",
  ai_titolo: "Hogyan használjuk a mesterséges intelligenciát",
  ai_testo: "Egy MI a kérdésed és a szavaid összefüggésében értelmezi a kártyákat. A két emberről szóló jóslásokban a másik személy vezetékneve soha nem jut el az MI-hez. Az MI nem ismeri a jövőt, és egyetlen jóslás sem jóslat a jövőről.",

  custode_titolo: "Adatkezelő",
  custode_testo: "A TAROTS chat által gyűjtött személyes adatok kezelője Andrea Taini.",
  partner_titolo: "Adatmegosztás partnerekkel",
  partner_testo: "Eldöntheted, hogy engedélyezed-e adataid megosztását partnereinkkel. Ez a választás független a sütikre vonatkozótól, és bármikor módosíthatod ezen az oldalon.",
  partner_si: "Engedélyezem",
  partner_no: "Nem engedélyezem",
  partner_stato_si: "Engedélyezted adataid megosztását a partnerekkel.",
  partner_stato_no: "Nem engedélyezted adataid megosztását a partnerekkel.",
  stat_titolo: "Használati statisztikák",
  stat_anonime: "Névtelenül mérjük, hogyan használják az oldalt: a meglátogatott oldalakat, hogy honnan érkezik a látogatás (keresőmotor, közösségi média, kampány), az eszköz és a böngésző típusát, a hozzávetőleges országot és várost. Sütik nélkül, és semmit sem tárolunk a böngésződben. Az IP-címet csak a látogatás pillanatában használjuk az ország és a város becslésére, valamint egy naponta változó ujjlenyomat kiszámítására: soha nem tároljuk.",
  stat_account: "Ha van fiókod és be vagy jelentkezve, a látogatásaidat a fiókodhoz kapcsoljuk, a szolgáltatás fejlesztéséhez fűződő jogos érdekünk alapján (például hogy melyik csatornáról érkeznek az új tagok, és mi vezet egy vásárláshoz). Bármikor tiltakozhatsz a fiókodban: onnantól a látogatásokat nem kapcsoljuk a fiókodhoz, és a korábbiakkal való kapcsolatot töröljük.",
  stat_esteso: "Ha a sütisávban elfogadod („It's fine”), a böngésződet a későbbi napokon is felismerjük egy véletlenszerű azonosítóval. Ha elutasítod vagy meggondolod magad, az azonosítót a szervereink is elfelejtik.",
  stat_conservazione: "A részletes látogatásokat és eseményeket 25 hónapig őrizzük meg; utána csak névtelen napi összesítések maradnak. Az automatikus elemzések és az exportok csak összesített adatokat használnak.",
  stat_geo: "IP-alapú helymeghatározás:",
  cookie_titolo: "A sütikkel kapcsolatos döntésed",
  cookie_si: "Elfogadom",
  cookie_no: "Nem fogadom el",
  cookie_stato_si: "Elfogadtad: visszatéréskor felismerjük a böngésződet.",
  cookie_stato_no: "Nem fogadtad el: a látogatások névtelenek maradnak, a böngésző azonosítóját elfelejtettük.",
};
