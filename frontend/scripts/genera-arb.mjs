/* I testi dell'app (mobile/) dagli stessi dizionari della v2: una sola fonte per sito e app.
 *
 *   node scripts/genera-arb.mjs              scrive mobile/lib/l10n/app_<lingua>.arb e liste.g.dart
 *   node scripts/genera-arb.mjs --controlla  non scrive nulla: esce con 1 se i file dell'app non sono aggiornati
 *
 * Dopo averlo lanciato: `flutter gen-l10n` in mobile/ (lo fa anche `flutter pub get`, con `generate: true`).
 *
 * Come legge: i dizionari sono TypeScript (`frontend/v2/i18n/<lingua>/*.ts`), dati puri senza funzioni. Si
 * traducono in CommonJS col compilatore TypeScript del sito e si valutano in una sandbox, seguendo gli import
 * relativi; `import type` sparisce con la traduzione. Così si legge esattamente ciò che legge il sito, anche le
 * lingue che sono copie dell'inglese.
 *
 * Come appiattisce: `sezione.chiave` → `sezione_chiave`. Le voci annidate seguono la stessa regola:
 * - una stringa resta una stringa; i segnaposto `{nome}` (quelli di `f()`) diventano argomenti ICU, dichiarati
 *   nell'ARB inglese come `Object`; gli a capo `\n` restano (le etichette brevi della testata li usano);
 * - `{ uno, molti }` (quelli di `plurale()`) diventa un plurale ICU `{n, plural, =1{…} other{…}}`: come il sito,
 *   «uno» solo per n = 1, tutto il resto è «molti» (anche nelle lingue con più forme, finché non si traducono);
 * - un elenco (`temi: [...]`) diventa `home_temi_0_nome`, `home_temi_1_nome`…; un `Record<string, string>`
 *   diventa `lettura_temi_amore`… Per leggerli come elenchi e mappe in Dart, lo script scrive anche
 *   `mobile/lib/l10n/liste.g.dart` (un'estensione di `AppLocalizations`), dalla forma dell'inglese;
 * - qualunque altra cosa (numeri, booleani, funzioni) si segnala e si salta: nei dizionari non dovrebbe esserci.
 *
 * Le parentesi graffe che non sono un segnaposto romperebbero il formato ICU: lo script si ferma e dice dove. */

import { existsSync, mkdirSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import vm from "node:vm";

const qui = dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
const ts = require("typescript");

const I18N = resolve(qui, "../v2/i18n");
const USCITA = resolve(qui, "../../mobile/lib/l10n");
const BASE = "en";
const controlla = process.argv.includes("--controlla");

/* ---- lettura dei dizionari TypeScript ------------------------------------------------------------------------ */

const cache = new Map();

function caricaModulo(file) {
  if (cache.has(file)) return cache.get(file).exports;
  const sorgente = readFileSync(file, "utf-8");
  const { outputText } = ts.transpileModule(sorgente, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 },
    fileName: file,
  });
  const modulo = { exports: {} };
  cache.set(file, modulo);
  const richiedi = (spec) => {
    if (!spec.startsWith(".")) throw new Error(`${file}: import non relativo «${spec}» in un dizionario`);
    const base = resolve(dirname(file), spec);
    const candidato = [`${base}.ts`, join(base, "index.ts")].find((p) => existsSync(p));
    if (!candidato) throw new Error(`${file}: non trovo «${spec}»`);
    return caricaModulo(candidato);
  };
  vm.runInNewContext(outputText, { module: modulo, exports: modulo.exports, require: richiedi }, { filename: file });
  return modulo.exports;
}

/** Il dizionario di una lingua: l'unico oggetto esportato da `<lingua>/index.ts` (le copie esportano `en`). */
function dizionario(lingua) {
  const esportati = Object.values(caricaModulo(join(I18N, lingua, "index.ts")));
  const oggetti = esportati.filter((v) => v && typeof v === "object");
  if (oggetti.length !== 1) throw new Error(`${lingua}/index.ts: mi aspetto un solo dizionario esportato`);
  return oggetti[0];
}

/** Le lingue: le cartelle di `v2/i18n`, l'inglese per primo. */
const lingue = readdirSync(I18N, { withFileTypes: true })
  .filter((d) => d.isDirectory() && existsSync(join(I18N, d.name, "index.ts")))
  .map((d) => d.name)
  .sort((a, b) => (a === BASE ? -1 : b === BASE ? 1 : a.localeCompare(b)));

/* ---- appiattimento --------------------------------------------------------------------------------------------- */

const SEGNAPOSTO = /\{(\w+)\}/g;
const avvisi = [];

const plurale = (v) =>
  v && typeof v === "object" && !Array.isArray(v) && Object.keys(v).length === 2 &&
  typeof v.uno === "string" && typeof v.molti === "string";

/** Un pezzo di chiave valido in un identificatore Dart. */
const pezzo = (k) => String(k).replace(/[^A-Za-z0-9_]/g, "_");

/** Una stringa del dizionario come testo ICU: i segnaposto restano, le graffe sciolte fermano tutto. */
function icu(testo, dove) {
  const senza = testo.replace(SEGNAPOSTO, "");
  if (/[{}]/.test(senza)) throw new Error(`${dove}: una parentesi graffa che non è un segnaposto: ${JSON.stringify(testo)}`);
  return testo;
}

const nomiSegnaposto = (testo) => [...testo.matchAll(SEGNAPOSTO)].map((m) => m[1]);

/** {chiave: {testo, segnaposto, plurale}} e la forma (per liste.g.dart). */
function appiattisci(diz, lingua) {
  const voci = new Map();
  const metti = (chiave, voce, dove) => {
    if (voci.has(chiave)) throw new Error(`${dove}: la chiave «${chiave}» esiste già (due voci diventano uguali)`);
    voci.set(chiave, voce);
  };
  const visita = (valore, chiave, dove) => {
    if (typeof valore === "string") {
      metti(chiave, { testo: icu(valore, dove), segnaposto: [...new Set(nomiSegnaposto(valore))], plurale: false }, dove);
    } else if (plurale(valore)) {
      const uno = icu(valore.uno, dove);
      const molti = icu(valore.molti, dove);
      const altri = [...new Set([...nomiSegnaposto(uno), ...nomiSegnaposto(molti)])].filter((n) => n !== "n");
      metti(chiave, { testo: `{n, plural, =1{${uno}} other{${molti}}}`, segnaposto: altri, plurale: true }, dove);
    } else if (Array.isArray(valore)) {
      valore.forEach((v, i) => visita(v, `${chiave}_${i}`, `${dove}[${i}]`));
    } else if (valore && typeof valore === "object") {
      for (const [k, v] of Object.entries(valore)) visita(v, `${chiave}_${pezzo(k)}`, `${dove}.${k}`);
    } else {
      avvisi.push(`${lingua}: ${dove} non è un testo (${typeof valore}): saltata`);
    }
  };
  for (const [sezione, contenuto] of Object.entries(diz)) visita(contenuto, pezzo(sezione), sezione);
  return voci;
}

/* ---- ARB ------------------------------------------------------------------------------------------------------- */

function arb(lingua, voci, base) {
  const uscita = { "@@locale": lingua };
  for (const [chiave, voce] of voci) {
    uscita[chiave] = voce.testo;
    if (lingua !== BASE) continue;
    const segnaposto = {};
    if (voce.plurale) segnaposto.n = { type: "int" };
    for (const nome of voce.segnaposto) segnaposto[nome] = { type: "Object" };
    if (Object.keys(segnaposto).length) uscita[`@${chiave}`] = { placeholders: segnaposto };
  }
  if (base) {
    /* Una voce appena aggiunta all'inglese e non ancora copiata (`copia-inglese.mjs`) o tradotta: l'app mostra
     * l'inglese, come farebbe il sito, e lo script lo dice. Una voce che l'inglese non ha più si lascia fuori. */
    const mancanti = [];
    for (const [chiave, voce] of base) {
      if (!voci.has(chiave)) {
        mancanti.push(chiave);
        uscita[chiave] = voce.testo;
      }
    }
    if (mancanti.length) {
      const esempi = mancanti.slice(0, 3).join(", ");
      avvisi.push(`${lingua}: ${mancanti.length} voci non ancora copiate o tradotte, si usa l'inglese (${esempi}…)`);
    }
    for (const chiave of voci.keys()) {
      if (!base.has(chiave)) {
        avvisi.push(`${lingua}: «${chiave}» non è nell'inglese, si lascia fuori`);
        delete uscita[chiave];
      }
    }
  }
  return `${JSON.stringify(uscita, null, 2)}\n`;
}

/* ---- liste.g.dart: elenchi e mappe come in TypeScript ---------------------------------------------------------- */

const camel = (k) => k.replace(/_([a-z0-9])/gi, (_, c) => c.toUpperCase());

/** Come si legge una voce in Dart: un getter, o un metodo se ha segnaposto (che diventano argomenti con nome). */
function uso(chiave, argomenti) {
  const voce = base.get(chiave);
  if (!voce || voce.plurale) return null;
  for (const n of voce.segnaposto) argomenti.add(n);
  return voce.segnaposto.length ? `${chiave}(${voce.segnaposto.join(", ")})` : chiave;
}

/** Il tipo Dart di un elemento di elenco e l'espressione che lo costruisce. */
function elemento(valore, chiave, argomenti) {
  if (typeof valore === "string") {
    const espr = uso(chiave, argomenti);
    return espr && { tipo: "String", espr };
  }
  if (valore && typeof valore === "object" && !Array.isArray(valore) && !plurale(valore) &&
      Object.values(valore).every((v) => typeof v === "string")) {
    const campi = Object.keys(valore);
    const espr = campi.map((c) => uso(`${chiave}_${pezzo(c)}`, argomenti));
    if (espr.some((e) => !e)) return null;
    return {
      tipo: `({${campi.map((c) => `String ${pezzo(c)}`).join(", ")}})`,
      espr: `(${campi.map((c, i) => `${pezzo(c)}: ${espr[i]}`).join(", ")})`,
    };
  }
  return null;
}

/** Getter senza segnaposto, metodo con gli argomenti con nome se qualche voce ne ha. */
const firma = (tipo, nome, argomenti) =>
  argomenti.size ? `${tipo} ${nome}({${[...argomenti].map((a) => `required Object ${a}`).join(", ")}})` : `${tipo} get ${nome}`;

/** Le lingue tradotte davvero: quelle senza la riga «COPIA DELL'INGLESE» (`copia-inglese.mjs`) in cima ai file. */
const tradotte = lingue.filter((l) => !readFileSync(join(I18N, l, "comune.ts"), "utf-8").includes("COPIA DELL'INGLESE"));

function liste(diz) {
  const righe = [];
  const visita = (valore, chiave) => {
    if (Array.isArray(valore)) {
      const argomenti = new Set();
      const el = valore.map((v, i) => elemento(v, `${chiave}_${i}`, argomenti));
      if (el.length && el.every((e) => e && e.tipo === el[0].tipo)) {
        righe.push(`  /// \`${chiave.replace(/_/, ".")}\` del dizionario della v2 (${el.length} voci).`);
        righe.push(`  ${firma(`List<${el[0].tipo}>`, camel(chiave), argomenti)} => [${el.map((e) => e.espr).join(", ")}];`);
      } else {
        avvisi.push(`${chiave}: elenco misto o con plurali, niente getter in liste.g.dart (le voci restano nell'ARB)`);
      }
    } else if (valore && typeof valore === "object" && !plurale(valore)) {
      const valori = Object.values(valore);
      if (valori.length && valori.every((v) => typeof v === "string")) {
        const argomenti = new Set();
        const voci = Object.keys(valore).map((k) => [k, uso(`${chiave}_${pezzo(k)}`, argomenti)]);
        if (voci.every(([, e]) => e)) {
          righe.push(`  /// \`${chiave.replace(/_/, ".")}\` come mappa, con le chiavi originali.`);
          righe.push(`  ${firma("Map<String, String>", camel(chiave), argomenti)} => {${voci
            .map(([k, e]) => `'${k.replace(/[\\'$]/g, (c) => `\\${c}`)}': ${e}`).join(", ")}};`);
        }
      }
      for (const [k, v] of Object.entries(valore)) if (typeof v !== "string") visita(v, `${chiave}_${pezzo(k)}`);
    }
  };
  for (const [sezione, contenuto] of Object.entries(diz)) {
    for (const [k, v] of Object.entries(contenuto)) visita(v, `${pezzo(sezione)}_${pezzo(k)}`);
  }
  return [
    "// GENERATO da frontend/scripts/genera-arb.mjs: non modificare a mano.",
    "// Gli elenchi e le mappe dei dizionari della v2, ricomposti dalle voci appiattite dell'ARB.",
    "",
    "// I campi dei record hanno i nomi delle chiavi dei dizionari (`fornitori_ai`), come nel sito.",
    "// ignore_for_file: lines_longer_than_80_chars, public_member_api_docs, non_constant_identifier_names",
    "",
    "import 'generato/app_localizations.dart';",
    "",
    "/// Le lingue tradotte davvero; le altre sono copie dell'inglese (il verso della pagina resta sinistra→destra).",
    `const Set<String> lingueTradotte = {${tradotte.map((l) => `'${l}'`).join(", ")}};`,
    "",
    "/// Elenchi e mappe dei dizionari, come nel sito (`h.temi.map(…)`).",
    "extension ListeL10n on AppLocalizations {",
    ...righe,
    "}",
    "",
  ].join("\n");
}

/* ---- scrittura o controllo ------------------------------------------------------------------------------------- */

const file = new Map();
const base = appiattisci(dizionario(BASE), BASE);
for (const lingua of lingue) {
  const voci = lingua === BASE ? base : appiattisci(dizionario(lingua), lingua);
  file.set(join(USCITA, `app_${lingua}.arb`), arb(lingua, voci, lingua === BASE ? null : base));
}
file.set(join(USCITA, "liste.g.dart"), liste(dizionario(BASE)));

for (const a of avvisi) console.warn(`avviso: ${a}`);

if (controlla) {
  const vecchi = file.size;
  const diversi = [...file].filter(([p, testo]) => !existsSync(p) || readFileSync(p, "utf-8") !== testo).map(([p]) => p);
  const presenti = existsSync(USCITA) ? readdirSync(USCITA).filter((n) => /^app_.*\.arb$/.test(n)) : [];
  const avanzi = presenti.filter((n) => !file.has(join(USCITA, n)));
  if (diversi.length || avanzi.length) {
    for (const p of diversi) console.error(`da rigenerare: ${p}`);
    for (const n of avanzi) console.error(`di troppo: ${join(USCITA, n)}`);
    console.error("Gli ARB dell'app non corrispondono ai dizionari della v2: `node scripts/genera-arb.mjs`.");
    process.exit(1);
  }
  console.log(`ARB aggiornati: ${lingue.length} lingue, ${base.size} voci (${vecchi} file).`);
} else {
  mkdirSync(USCITA, { recursive: true });
  for (const [p, testo] of file) writeFileSync(p, testo, "utf-8");
  console.log(`Scritti ${file.size} file in ${USCITA}: ${lingue.length} lingue, ${base.size} voci.`);
}
