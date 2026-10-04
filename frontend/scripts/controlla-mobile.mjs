/* Il controllo della fonte unica sito → app: fallisce se i testi (ARB) o lo stile (token) dell'app non
 * corrispondono più ai dizionari e al CSS della v2. Da lanciare prima di una build dell'app e in CI.
 *
 *   node scripts/controlla-mobile.mjs
 *
 * Non scrive nulla: per aggiornare, `node scripts/genera-arb.mjs` e `node scripts/genera-token.mjs`. */

import { spawnSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const qui = dirname(fileURLToPath(import.meta.url));
let fallito = false;
for (const script of ["genera-arb.mjs", "genera-token.mjs"]) {
  const esito = spawnSync(process.execPath, [join(qui, script), "--controlla"], { stdio: "inherit" });
  if (esito.status !== 0) fallito = true;
}
process.exit(fallito ? 1 : 0);
