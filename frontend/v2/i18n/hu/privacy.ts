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
  letture_accesso: "Kizárólag biztonsági okokból (például visszaélésről szóló bejelentés vagy segítségkérés kezelésére) a TAROTS chat adminisztrátorai elolvashatják a jóslásaidat, a beszélgetéseidet, azt, amire a tarotolvasód emlékszik, és a profiladataidat. Minden hozzáféréshez meg kell adni az okát, és naplózásra kerül.",
  ai_titolo: "Hogyan használjuk a mesterséges intelligenciát",
  ai_testo: "Egy MI a kérdésed és a szavaid összefüggésében értelmezi a kártyákat. A nevek soha nem jutnak el az MI szolgáltatójához: az egy helyettesítő jelölést kap („Persona_1”), te pedig a valódi nevet olvasod; a másik személy vezetékneve soha nem kerül továbbításra. Az MI nem ismeri a jövőt, és egyetlen jóslás sem jóslat a jövőről. Minden kérésnél megkérjük a szolgáltatót, hogy ne tárolja a válaszokat: a szövegeid nem maradnak nála a modelljei tanítására.",

  custode_titolo: "Ki felel az adataidért",
  // Az adatkezelő adatai a konzolból jönnek (Impostazioni → Dati del titolare): a {helyőrzőket} az oldal tölti ki, az
  // üres mező helyett a semleges mondat jelenik meg.
  custode_testo: "A TAROTS chat (https://tarots.chat) által gyűjtött személyes adatok kezelője {titolare}.",
  custode_testo_senza_nome: "A TAROTS chat (https://tarots.chat) által gyűjtött személyes adatok kezelője az alábbi adatvédelmi elérhetőségen érhető el.",
  custode_indirizzo: "Postai cím: {indirizzo}.",
  custode_indirizzo_vuoto: "Postai cím: kérésre megadjuk az adatvédelmi elérhetőségen.",
  custode_codice: "Adószám vagy adóazonosító jel: {codice}.",
  custode_email: "Adatvédelmi kapcsolattartás: {email}",
  custode_email_vuoto: "Adatvédelmi kapcsolattartás: frissítés alatt; addig a fiókodból gyakorolhatod a jogaidat.",
  custode_dpo: "Adatvédelmi tisztviselő (DPO): {dpo}.",
  custode_dpo_no: "Adatvédelmi tisztviselőt (DPO) nem neveztünk ki.",

  scelte_titolo: "A döntéseid ebben a böngészőben",
  scelte_testo: "Minden, ami alább látható, kikapcsolva marad, amíg be nem kapcsolod, és itt bármikor megváltoztathatod. A technikai sütikhez (a belépés, a fiók nélküli ingyenes jóslás, ezeknek a döntéseknek a megjegyzése) nem kell hozzájárulás: nélkülük az oldal nem működik.",
  scelte_account: "A fiókodat érintő döntések — a szavaid statisztikákhoz, a különleges adatok, a promóciók — a fiókodban találhatók.",
  scelte_account_cta: "Adatvédelem és hozzájárulások",

  finalita_titolo: "Mit használunk, miért és milyen jogalapon",
  finalita_intro: "Az adataid minden felhasználásának megvan a maga célja és a GDPR szerinti jogalapja:",
  finalita: [
    { cosa: "Fiók és profil", perche: "Hogy fiókot adjunk neked, megőrizzük a jóslásaidat és a személyes kártyáidat, és be tudj lépni (közösségi fiókkal is).", base: "Jogalap: a szerződés, amelyet kérsz (GDPR 6. cikk (1) b))." },
    { cosa: "Jóslások, interjú, emlékezet és chat", perche: "Hogy MI segítségével kártyát vessünk neked, és megjegyezzük, ami a következő jóslásoknál segít.", base: "Jogalap: szerződés; a különleges adatoknál a kifejezett hozzájárulásod (9. cikk (2) a))." },
    { cosa: "A fiók nélküli ingyenes jóslás", perche: "Hogy regisztráció előtt kipróbálhass egy jóslást.", base: "Jogalap: a szerződéskötést megelőzően általad kért lépések (6. cikk (1) b))." },
    { cosa: "Fizetések, kreditek, rendelések és szállítás", perche: "Hogy krediteket, csomagokat és paklikat értékesítsünk, és vezessük a törvény által előírt nyilvántartást.", base: "Jogalap: szerződés és jogi kötelezettségek (6. cikk (1) b) és c))." },
    { cosa: "Biztonság és naplók", perche: "Hogy védjük a fiókokat és a szolgáltatást, és tudjuk, ki mit tett. Az IP-címeket csak rövidítve tároljuk, kulcsos ujjlenyomattal.", base: "Jogalap: jogos érdek (6. cikk (1) f))." },
    { cosa: "Névtelen statisztikák", perche: "Hogy sütik nélkül, a böngésződben semmit sem tárolva számoljuk a látogatásokat.", base: "Jogalap: jogos érdek." },
    { cosa: "A fiókodhoz kapcsolt statisztikák", perche: "Hogy megértsük, mely csatornák hoznak tagokat, és mi vezet vásárláshoz.", base: "Jogalap: jogos érdek; a fiókodban tiltakozhatsz (21. cikk)." },
    { cosa: "Az oldal statisztikái böngészőazonosítóval", perche: "Hogy felismerjük a böngésződet, amikor visszatérsz.", base: "Jogalap: a hozzájárulásod (6. cikk (1) a))." },
    { cosa: "Google Analytics", perche: "Hogy mérjük, hogyan használják az oldalt.", base: "Jogalap: a hozzájárulásod." },
    { cosa: "Hirdetések", perche: "Hogy néhány megjelölt helyen Google AdSense-hirdetéseket mutassunk, csak ha be vannak kapcsolva.", base: "Jogalap: a hozzájárulásod." },
    { cosa: "A szavaid statisztikákhoz és blogötletekhez", perche: "Hogy névtelenül és összesítve megértsük, mely témák fontosak az embereknek (soha senkit nem idézve). Még nem aktív.", base: "Jogalap: a külön, nem kötelező hozzájárulásod." },
    { cosa: "Promóciók", perche: "Ajánlatok és újdonságok értesítésekben, amikor elérhetők lesznek.", base: "Jogalap: a hozzájárulásod." },
    { cosa: "Korhatár", perche: "Hogy ellenőrizzük, elég idős vagy-e ahhoz, hogy egyedül használd a szolgáltatást.", base: "Jogalap: jogi kötelezettség (GDPR 8. cikk) és szerződés." },
  ],

  art9_titolo: "Különleges adatok",
  art9_testo: "Néhány dolog, amit elmondhatsz nekünk, a személyes adatok különleges kategóriájába tartozik: az, hogy transznemű vagy, és az egészséged. A „transznemű személy” jelölőnégyzetet és az egészségedről szóló emlékeket csak a kifejezett hozzájárulásoddal használjuk, amelyet ott adsz meg, ahol a jelölőnégyzetet bejelölöd, és a fiókodban bármikor visszavonhatsz: ekkor a jelölőnégyzet kiürül, és ezek az emlékek törlődnek. Nélküle soha nem jutnak el az MI-hez.",
  art9_crisi: "Ha azt írod, hogy ártani akarsz magadnak, a jóslás leáll, és azonnal megmutatjuk, hol találsz segítséget. Csak azt számoljuk, hogy ez megtörtént, anélkül hogy hozzád kapcsolnánk.",

  stat_titolo: "Használati statisztikák",
  stat_anonime: "Névtelenül mérjük, hogyan használják az oldalt: a meglátogatott oldalakat, hogy honnan érkezik a látogatás (keresőmotor, közösségi média, kampány), az eszköz és a böngésző típusát, a hozzávetőleges országot és várost. Sütik nélkül, és semmit sem tárolunk a böngésződben. Az IP-címet csak a látogatás pillanatában használjuk az ország és a város becslésére, valamint egy naponta változó ujjlenyomat kiszámítására: soha nem tároljuk.",
  stat_account: "Ha van fiókod és be vagy jelentkezve, a látogatásaidat a fiókodhoz kapcsoljuk, a szolgáltatás fejlesztéséhez fűződő jogos érdekünk alapján (például hogy melyik csatornáról érkeznek az új tagok, és mi vezet egy vásárláshoz). Bármikor tiltakozhatsz a fiókodban: onnantól a látogatásokat nem kapcsoljuk a fiókodhoz, és a korábbiakkal való kapcsolatot töröljük.",
  stat_esteso: "Ha bekapcsolod „Az oldal statisztikái” lehetőséget, a böngésződet a későbbi napokon is felismerjük, amikor visszatérsz, egy a böngésződben tárolt véletlenszerű azonosítóval. Ha elutasítod vagy meggondolod magad, az azonosítót a szervereink is elfelejtik.",
  stat_google: "Ha bekapcsolod a „Google Analytics” lehetőséget, a Google Analytics 4-et is használjuk (a Google Ireland Ltd. szolgáltatása), amely saját sütiket (_ga) helyez el a látogatások számlálásához és annak megértéséhez, hogyan használják az oldalt. Csak a hozzájárulásod után töltődik be (Google Consent Mode), kikapcsolt Google-jelekkel és hirdetés-személyre szabással; a Google Analytics 4 nem tárol IP-címeket. A Google az adatokat az Egyesült Államokban is kezelheti az EU–USA adatvédelmi keretrendszer alapján. Ha elutasítod vagy visszavonod a hozzájárulásodat, a Google Analytics leáll, és a sütijei törlődnek.",
  stat_conservazione: "A részletes látogatásokat és eseményeket 25 hónapig őrizzük meg; utána csak névtelen napi összesítések maradnak. Az automatikus elemzések és az exportok csak összesített adatokat használnak.",
  stat_geo: "IP-alapú helymeghatározás:",
  pubblicita_titolo: "Hirdetések",
  pubblicita_testo: "Egyes oldalakon legfeljebb három „Hirdetés” jelölésű hely jelenhet meg, amelyeket a Google AdSense, a Google Ireland Ltd. szolgáltatása tölt ki. A hirdetések csak akkor töltődnek be, ha itt vagy a sávban elfogadod: ekkor a Google saját sütiket (például __gads és __gpi) állít be a hirdetések megjelenítéséhez, gyakoriságuk korlátozásához és méréséhez, és az adatokat az EU–USA adatvédelmi keretrendszer alapján az Egyesült Államokban is kezelheti. A hirdetések nem személyre szabottak, hacsak ez az oldal másként nem jelzi. Ha elutasítod, a helyek nem jelennek meg, és a Google AdSense-ből semmi sem töltődik be.",
  pubblicita_tcf: "Az Európai Unióban, az Egyesült Királyságban és Svájcban a hirdetésekkel kapcsolatos döntésedet a Google hozzájárulás-kezelő eszköze (IAB TCF 2.2 tanúsítvánnyal) kéri be és őrzi meg, az első látogatáskor jelenik meg: az számít, nem az ezen az oldalon lévő jelölőnégyzetek.",
  pubblicita_tcf_cambia: "A hirdetési döntés módosítása",

  social_titolo: "Belépés közösségi fiókkal",
  social_account: "Egy fiók személyenként: ha Google-lal, Facebookkal, Apple-lel, GitHubbal vagy LinkedInnel egy már létező fiók e-mail-címével lépsz be, az ugyanaz a fiók, ugyanazokkal az olvasásokkal és kreditekkel.",
  social_cosa: "Abból a fiókból azt kapjuk meg, amit megoszt velünk: kereszt- és vezetéknév, e-mail, profilkép, nyelv és — csak ha a szolgáltató képernyőjén engedélyezed — születési dátum, nem és város. Csak a fiókod még üres mezőinek kitöltésére használjuk, soha nem írjuk felül, amit te írtál.",
  social_perche: "Miért: a születési dátumból jönnek a személyes kártyáid (a lélekkártya és az év kártyája), a nem pedig a páros olvasások megszólításaihoz kell; a név, a nyelv és a kép miatt nem kell újra beírnod őket. Jogalap: a kért szolgáltatás és a döntésed a szolgáltató képernyőjén.",
  social_posizione: "Jelenlegi hely: ország és város, a közösségi fiókból, ha megosztja, különben minden belépéskor becsülve az IP-címedből egy a szerverünkön tárolt adatbázissal (a címet nem tároljuk, és semmi nem megy harmadik félhez). Segít a szolgáltatás alakításában.",
  social_controllo: "A fiókodban látod, honnan jön minden adat, kijavíthatod vagy törölheted, leállíthatod az átvételt vagy a helymeghatározást, vagy egyszerre törölheted mindazt, ami közösségi fiókokból jött. Az összekapcsolt fiókokat a fiókbeállításokban kezeled („Összekapcsolt fiókok”).",
  social_cta: "Adataid kezelése",

  responsabili_titolo: "Ki kezeli még az adataidat, és hol",
  responsabili_intro: "Nem adjuk el az adataidat, és nem osztjuk meg partnerekkel. Ezek a szolgáltatók a megbízásunkból kezelik őket, vagy önálló adatkezelőként, ha úgy döntesz, hogy igénybe veszed őket:",
  responsabili: [
    { chi: "Tárhely", cosa: "a szerverünk és az adatbázisunk. Szolgáltató és helyszín: {hosting}." },
    { chi: "MI-szolgáltatók", cosa: "az általunk beállított nyelvimodell-szolgáltatók megkapják a kérdésed, az interjú és a chat szövegét — a neveket helyettesítő jelölésre cserélve, a vezetéknevet soha — kizárólag a jóslás megírásához. Jelenlegi szolgáltatók és országok: {fornitori_ai}." },
    { chi: "Google", cosa: "Google Analytics és AdSense (csak a hozzájárulásoddal), valamint a Google-lal való belépés (Google Ireland Ltd., az adatok az Egyesült Államokba is kerülhetnek)." },
    { chi: "Belépési szolgáltatók", cosa: "Apple, Facebook (Meta), GitHub és LinkedIn, csak ha velük lépsz be: a náluk lévő fiókod önálló adatkezelői." },
    { chi: "Fizetések", cosa: "Stripe, a kártyás fizetésekhez (Stripe Payments Europe, az adatok az Egyesült Államokba is kerülhetnek). A kártyaszámodat soha nem látjuk." },
    { chi: "Alkalmazásértesítések", cosa: "Firebase Cloud Messaging (Google), az alkalmazás értesítéseihez, amikor elérhetők lesznek." },
    { chi: "E-mail és biztonsági mentések", cosa: "az @tarots.chat címre írt leveleid a Namecheap továbbító szolgáltatásán (Egyesült Államok) keresztül az adatkezelő egyik Gmail-postafiókjába érkeznek (Google); az általunk küldött e-mailek a saját szerverünkről indulnak, amelyet a Hivelocity üzemeltet Londonban; a biztonsági mentések a saját tárhelyünkön vannak Olaszországban, harmadik fél nélkül." },
  ],
  hosting_vuoto: "adatfeldolgozási szerződéssel kötött szolgáltató",
  fornitori_ai_vuoto: "jelenleg egy sem aktív",
  fornitori_ai_proprio: "a saját szerverünkön, harmadik fél nélkül",
  trasferimenti: "Ha az adatok elhagyják az Európai Gazdasági Térséget, az Európai Bizottság megfelelőségi határozatára (az Egyesült Királyság; az Egyesült Államok az EU–USA adatvédelmi keretrendszerben tanúsított vállalatok esetén) vagy a Bizottság általános szerződési feltételeire támaszkodunk.",

  conservazione_titolo: "Meddig őrizzük meg",
  conservazione: [
    "Fiók, jóslások, emlékezet és chat: amíg nem törlöd őket vagy a fiókodat. Nincs automatikus lejárat: a régi adatokat mi magunk is törölhetjük, például a fiók nélküli ingyenes jóslásokat és a régi chateket.",
    "A fiók nélküli ingyenes jóslás: amíg nem töröljük; ha regisztrálsz, a fiókod része lesz.",
    "Részletes látogatási statisztikák: 25 hónap, utána csak névtelen napi összesítések.",
    "A hozzájárulásokkal kapcsolatos döntéseid: ameddig igazolnunk kell őket.",
    "Számviteli nyilvántartások (fizetések, kreditek, rendelések): ameddig a törvény előírja (Olaszországban tíz évig). Ha törlöd a fiókodat, a személyazonosságodtól leválasztva maradnak meg.",
    "Biztonsági mentések: a törölt adatok a mentések cseréjével, körülbelül egy héten belül eltűnnek belőlük.",
  ],

  diritti_titolo: "A jogaid",
  diritti_testo: "Kérheted, hogy hozzáférj az adataidhoz, kijavítsd, töröld őket, hordozható formátumban megkapd őket, korlátozd a felhasználásukat vagy tiltakozz ellene, és bármikor visszavonhatsz bármely hozzájárulást — anélkül, hogy ez érintené a korábban történteket.",
  diritti_come: "A legtöbbet magad is megteheted: a fiókod oldalán letöltheted az adataidat és törölheted a fiókodat, és ott vagy ezen az oldalon bármely hozzájárulást megváltoztathatsz. Minden másért írj a fenti adatvédelmi kapcsolattartónak: egy hónapon belül válaszolunk.",
  diritti_cta_dati: "Az adataid és a hozzájárulásaid",
  diritti_cta_elimina: "A fiókod törlése",
  garante_titolo: "Panaszok",
  garante_testo: "Ha úgy gondolod, hogy az adataidat jogellenesen kezelik, panaszt tehetsz az olasz adatvédelmi hatóságnál — Garante per la protezione dei dati personali (www.garanteprivacy.it) —, vagy annak az országnak a hatóságánál, ahol élsz vagy dolgozol.",

  eta_titolo: "Korhatár",
  eta_testo: "A TAROTS chat 16 éves kortól használható; Olaszországban és Spanyolországban 14, Franciaországban 15 éves kortól — ez az az életkor, amelytől a törvény megengedi, hogy egyedül használd az online szolgáltatásokat. Az első jóslás előtt megkérünk, hogy erősítsd meg. Ha a fiókodban megadott születési dátum a korhatár alatt van, a jóslások és a chat leállnak.",

  versione: "3. változat — 2026. október 3.",
};
