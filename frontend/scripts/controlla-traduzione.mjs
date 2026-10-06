// v9.5: la console usa lo stesso motore di traduzione automatica del sito, in copia (`admin/lib/`), in attesa dei
// suoi dizionari. Questo controllo fallisce se le copie non coincidono con quelle del sito (`v2/lib/`).
//
//   node scripts/controlla-traduzione.mjs        (dalla cartella frontend; esce con 1 se una copia è diversa)
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const RADICE = join(fileURLToPath(new URL(".", import.meta.url)), "..", "..");
const COPIE = ["traduzione-auto.ts", "usa-traduzione.ts"];
const leggi = (p) => readFileSync(join(RADICE, p), "utf8").replace(/\r\n/g, "\n");

const diverse = COPIE.filter((nome) => {
  try {
    return leggi(`frontend/v2/lib/${nome}`) !== leggi(`admin/lib/${nome}`);
  } catch {
    return true;
  }
});
if (diverse.length) {
  console.error(`Copie diverse fra frontend/v2/lib e admin/lib: ${diverse.join(", ")} (ricopiale dal sito).`);
  process.exit(1);
}
console.log("ok: il motore di traduzione della console è uguale a quello del sito");
