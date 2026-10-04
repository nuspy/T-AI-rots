/* I risultati attesi del porting di `frontend/lib/indirizzi.ts` (`lib/rotte/indirizzi.dart`): lo script esegue il
 * codice TypeScript del sito su un elenco di indirizzi e scrive `test/fixtures/indirizzi_attesi.json`; il test Dart
 * (`test/indirizzi_test.dart`) controlla che la versione Dart dia gli stessi risultati.
 *
 *   node tool/indirizzi_attesi.mjs        (da mobile/; usa il compilatore TypeScript di frontend/node_modules) */

import { readFileSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import vm from "node:vm";

const qui = dirname(fileURLToPath(import.meta.url));
const frontend = resolve(qui, "../../frontend");
const ts = createRequire(resolve(frontend, "package.json"))("typescript");

const sorgente = readFileSync(resolve(frontend, "lib/indirizzi.ts"), "utf-8");
const { outputText } = ts.transpileModule(sorgente, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } });
const modulo = { exports: {} };
vm.runInNewContext(outputText, { module: modulo, exports: modulo.exports });
const { normalizza, pubblico, risolvi, interno, indicizzabile } = modulo.exports;

const indirizzi = [
  "/", "/it", "/it/", "/cards", "/cards/maj-17", "/it/carte/la-stella", "/carte/maj-17", "/stese", "/piano",
  "/carta-del-giorno", "/card-of-the-day", "/it/carta-del-giorno", "/daily-card", "/it/daily-card", "/it/cards/x",
  "/spreads/croce-celtica", "/it/stese/croce-celtica", "/pricing", "/it/piano", "/leggi", "/letture", "/letture/abc",
  "/s/tok", "/interpreta", "/vota-mazzo", "/deck", "/mazzo", "/mazzo/thoth", "/it/mazzo/thoth", "/profilo",
  "/blog/section/x", "/blog/sezione/x", "/blog/tag/y", "/blog/articolo", "/v2/cards/x", "/it/v2/daily-card",
  "/read", "/my-story/123", "/shared/tok", "/shop", "/cart", "/explore", "/privacy", "/account/elimina", "/decks/thoth",
];
const interni = [
  "/", "/cards", "/cards/maj-17?x=1#a", "/daily-card", "/pricing?ritorno=/read", "/spreads/x", "/read?question=a",
  "/carte/maj-17", "/blog/section/x", "https://esterno.example/x", "#ancora", "//cdn.example/x", "/my-story",
];

const uscita = {
  risolvi: Object.fromEntries(indirizzi.map((p) => [p, risolvi(p)])),
  interno: Object.fromEntries(indirizzi.map((p) => [p, interno(p)])),
  pubblico: Object.fromEntries(interni.map((p) => [p, { en: pubblico("en", p), it: pubblico("it", p) }])),
  normalizza: Object.fromEntries(interni.map((p) => [p, normalizza(p)])),
  indicizzabile: Object.fromEntries(interni.filter((p) => p.startsWith("/")).map((p) => [p, indicizzabile(p)])),
};
writeFileSync(resolve(qui, "../test/fixtures/indirizzi_attesi.json"), `${JSON.stringify(uscita, null, 1)}\n`);
console.log(`Scritti i risultati di ${indirizzi.length + interni.length} indirizzi.`);
