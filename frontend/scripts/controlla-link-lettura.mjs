// v9.5, la prova della lettura in chat (90/10): ogni link verso la lettura deve passare da `/read`, che sceglie la
// variante (`proxy.ts` nel sito, il router nell'app). Questo controllo fallisce se un file punta direttamente a
// `/read-chat` o `/read-classic` fuori dai pochi file che le conoscono di proposito.
//
//   node scripts/controlla-link-lettura.mjs        (dalla cartella frontend; esce con 1 se trova un link diretto)
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative, sep } from "node:path";
import { fileURLToPath } from "node:url";

const RADICE = join(fileURLToPath(new URL(".", import.meta.url)), "..", "..");
const CARTELLE = ["frontend/v2", "frontend/app", "frontend/lib", "frontend/proxy.ts", "mobile/lib"];
const AMMESSI = new Set([
  "frontend/proxy.ts",                         // lo smistatore
  "frontend/v2/lib/varianti.ts",               // la variante dal percorso (statistiche)
  "frontend/v2/lettura/lettura.tsx",           // l'allineamento alla variante del profilo
  "frontend/app/(v2)/read-chat/page.tsx",
  "frontend/app/(v2)/read-classic/page.tsx",
  "frontend/scripts/controlla-link-lettura.mjs",
  "mobile/lib/analytics/lanterna.dart",        // la variante dal percorso (statistiche)
  "mobile/lib/rotte/percorsi.dart",            // i due percorsi, usati solo dallo smistatore dell'app
]);
const ESTENSIONI = /\.(tsx?|mjs|dart)$/;
const DIRETTO = /\/read-(chat|classic)\b/;
// Un commento non è un collegamento: le righe che iniziano con //, /* o * non contano.
const COMMENTO = /^\s*(\/\/|\/\*|\*)/;

function* file(percorso) {
  const s = statSync(percorso, { throwIfNoEntry: false });
  if (!s) return;
  if (s.isFile()) { yield percorso; return; }
  for (const nome of readdirSync(percorso)) {
    if (nome === "node_modules" || nome.startsWith(".")) continue;
    yield* file(join(percorso, nome));
  }
}

const trovati = [];
for (const cartella of CARTELLE) {
  for (const f of file(join(RADICE, cartella))) {
    const rel = relative(RADICE, f).split(sep).join("/");
    if (!ESTENSIONI.test(f) || AMMESSI.has(rel)) continue;
    readFileSync(f, "utf8").split("\n").forEach((riga, i) => {
      if (!COMMENTO.test(riga) && DIRETTO.test(riga)) trovati.push(`${rel}:${i + 1}: ${riga.trim()}`);
    });
  }
}
if (trovati.length) {
  console.error("Link diretti a una variante della lettura (usa `/read`, che sceglie la variante):\n" + trovati.join("\n"));
  process.exit(1);
}
console.log("ok: tutti i link alla lettura passano da /read");
