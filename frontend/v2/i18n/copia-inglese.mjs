/* Copia l'inglese nelle lingue della v2 non ancora tradotte.
 *
 *   node v2/i18n/copia-inglese.mjs
 *
 * Per ognuna delle dodici lingue senza traduzione, la sua cartella diventa una copia esatta di `en/`, con una
 * riga in cima a ogni file che la segna come copia. Un file che ha perso quella riga è stato tradotto: lo script
 * non lo tocca più. Si rilancia ogni volta che si aggiunge o cambia un testo inglese: il compilatore lo ricorda,
 * perché una chiave che manca in una lingua è un errore di tipo. */

import { existsSync, mkdirSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const QUI = dirname(fileURLToPath(import.meta.url));
const COPIE = ["de", "ru", "uk", "fr", "es", "pt", "ro", "pl", "zh", "hi", "ko", "ar"];
const SEGNO = "/* COPIA DELL'INGLESE — da tradurre. Rigenerata da copia-inglese.mjs finché questa riga resta qui. */";

const sorgenti = readdirSync(join(QUI, "en")).filter((f) => f.endsWith(".ts"));
let scritti = 0;
let tradotti = 0;
for (const lingua of COPIE) {
  const cartella = join(QUI, lingua);
  mkdirSync(cartella, { recursive: true });
  for (const file of sorgenti) {
    const destinazione = join(cartella, file);
    if (existsSync(destinazione) && !readFileSync(destinazione, "utf8").startsWith(SEGNO)) {
      tradotti++;
      continue;
    }
    writeFileSync(destinazione, `${SEGNO}\n${readFileSync(join(QUI, "en", file), "utf8")}`);
    scritti++;
  }
}
console.log(`copie scritte: ${scritti}; file già tradotti lasciati com'erano: ${tradotti}`);
