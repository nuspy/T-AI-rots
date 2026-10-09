/* Lo stile dell'app (mobile/) dallo stesso CSS della v2: una sola fonte per sito e app.
 *
 *   node scripts/genera-token.mjs              scrive mobile/lib/tema/token.g.dart
 *   node scripts/genera-token.mjs --controlla  non scrive nulla: esce con 1 se il file dell'app non è aggiornato
 *
 * Cosa legge da `app/(v2)/v2.css`:
 * - **`:root`**: tutte le variabili. I colori (`#rrggbb`, `rgba()`) diventano `Color`, i caratteri l'elenco delle
 *   famiglie (la prima quella dell'app, le altre il ripiego), i `clamp(min, Nvw, max)` una `MisuraFluida`, i px e i
 *   rem un `double` (1rem = 16 px, come nel browser);
 * - **i punti di rottura**: tutte le `@media (max-width: Npx)` del file, in ordine;
 * - **raggi, spazi e durate** che nel `:root` non ci sono ma che il sito usa ovunque: si leggono dalla regola che
 *   li definisce (tabella `DERIVATI` qui sotto: nome nell'app, selettore, proprietà, eventuale media query). Se
 *   una regola cambia nel CSS, il token cambia; se sparisce, lo script si ferma e lo dice.
 *
 * Ciò che non è un valore semplice (ombre, gradienti) resta nel codice dell'app, accanto al selettore da cui viene. */

import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const qui = dirname(fileURLToPath(import.meta.url));
const CSS = resolve(qui, "../app/(v2)/v2.css");
const USCITA = resolve(qui, "../../mobile/lib/tema/token.g.dart");
const controlla = process.argv.includes("--controlla");

/** [nome Dart, selettore, proprietà, media query (facoltativa), come leggere il valore]. */
const DERIVATI = [
  ["raggio", ".button", "border-radius"],
  ["raggioPillola", ".chip", "border-radius"],
  ["durataTransizione", ".button", "transition", null, "durata"],
  ["altezzaBottone", ".button", "min-height"],
  ["altezzaBottonePiccolo", ".button-small", "min-height"],
  ["corpo", "body", "font", null, "dimensioneFont"],
  ["interlinea", "body", "font", null, "interlinea"],
  ["larghezzaBanda", ".band", "max-width"],
  ["larghezzaEroe", ".hero", "max-width"],
  ["altezzaTestata", ".site-header", "min-height"],
  ["altezzaTestataTelefono", ".site-header", "min-height", "(max-width: 760px)"],
  ["etichettaTestataTelefono", ".primary-nav .nav-breve", "font-size", "(max-width: 760px)"],
  ["etichettaTestataStretta", ".primary-nav .nav-breve", "font-size", "(max-width: 359px)"],
  ["iconaTestataTelefono", ".primary-nav .nav-icona", "width", "(max-width: 760px)"],
  ["bersaglioMinimo", ".hdr-icon", "min-height"],
  ["bersaglioTestataTelefono", ".header-actions .hdr-icon", "min-height", "(max-width: 760px)"],
  ["bordoModale", ".dialog", "border-top", null, "primoPx"],
  ["larghezzaModale", ".dialog", "width", null, "primoPx"],
];

/* ---- un CSS minimo: regole e media query ---------------------------------------------------------------------- */

function senzaCommenti(testo) {
  return testo.replace(/\/\*[\s\S]*?\*\//g, "");
}

/** Le regole come {media, selettori, dichiarazioni}; le @media annidate una volta (come in v2.css). */
function regole(testo, media = null) {
  const uscita = [];
  let i = 0;
  while (i < testo.length) {
    const apre = testo.indexOf("{", i);
    if (apre === -1) break;
    const testa = testo.slice(i, apre).trim();
    let profondita = 1;
    let j = apre + 1;
    while (j < testo.length && profondita > 0) {
      if (testo[j] === "{") profondita++;
      else if (testo[j] === "}") profondita--;
      j++;
    }
    const corpo = testo.slice(apre + 1, j - 1);
    if (testa.startsWith("@media")) {
      uscita.push(...regole(corpo, testa.slice(6).trim()));
    } else if (!testa.startsWith("@")) {
      const dichiarazioni = new Map();
      for (const d of corpo.split(";")) {
        const due = d.indexOf(":");
        if (due === -1) continue;
        dichiarazioni.set(d.slice(0, due).trim(), d.slice(due + 1).trim());
      }
      uscita.push({ media, selettori: testa.split(",").map((s) => s.replace(/\s+/g, " ").trim()), dichiarazioni });
    }
    i = j;
  }
  return uscita;
}

/* ---- valori --------------------------------------------------------------------------------------------------- */

const camel = (nome) => nome.replace(/^--/, "").replace(/-([a-z0-9])/g, (_, c) => c.toUpperCase());

function px(valore) {
  const m = /^(-?[\d.]+)(px|rem)?$/.exec(valore.trim());
  if (!m) return null;
  const n = Number(m[1]);
  return m[2] === "rem" ? n * 16 : n;
}

const numero = (n) => (Number.isInteger(n) ? `${n}.0` : String(Number(n.toFixed(4))));
const esadecimale = (n) => Math.round(n).toString(16).padStart(2, "0").toUpperCase();

function colore(valore) {
  let m = /^#([0-9a-f]{6})$/i.exec(valore);
  if (m) return `Color(0xFF${m[1].toUpperCase()})`;
  m = /^#([0-9a-f]{3})$/i.exec(valore);
  if (m) return `Color(0xFF${[...m[1]].map((c) => c + c).join("").toUpperCase()})`;
  m = /^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+)\s*)?\)$/i.exec(valore);
  if (m) {
    const a = m[4] === undefined ? 1 : Number(m[4]);
    return `Color(0x${esadecimale(a * 255)}${esadecimale(+m[1])}${esadecimale(+m[2])}${esadecimale(+m[3])})`;
  }
  return null;
}

function famiglie(valore) {
  const nomi = valore.split(",").map((s) => s.trim()).filter((s) => !s.startsWith("var("));
  if (!nomi.length || !nomi.every((n) => /^("[^"]+"|[\w-]+)$/.test(n))) return null;
  return nomi.map((n) => n.replace(/"/g, ""));
}

function fluida(valore) {
  const m = /^clamp\(\s*([^,]+),\s*([\d.]+)vw\s*,\s*([^)]+)\)$/.exec(valore);
  if (!m || px(m[1]) === null || px(m[3]) === null) return null;
  return `MisuraFluida(minimo: ${numero(px(m[1]))}, vw: ${numero(Number(m[2]))}, massimo: ${numero(px(m[3]))})`;
}

/** Una variabile di `:root` come riga Dart, o null (con il motivo) se non è un valore che l'app usa. */
function variabile(nome, valore) {
  const id = camel(nome);
  const c = colore(valore);
  if (c) return `  /// \`${nome}: ${valore}\`\n  static const Color ${id} = ${c};`;
  const f = famiglie(valore);
  if (f) return `  /// \`${nome}\`: la prima famiglia è nei font dell'app, le altre sono il ripiego del sito.\n  static const List<String> ${id} = [${f.map((n) => `'${n}'`).join(", ")}];`;
  const fl = fluida(valore);
  if (fl) return `  /// \`${nome}: ${valore}\`\n  static const MisuraFluida ${id} = ${fl};`;
  const p = px(valore);
  if (p !== null) return `  /// \`${nome}: ${valore}\`\n  static const double ${id} = ${numero(p)};`;
  return null;
}

function derivato([nome, selettore, proprieta, media = null, modo = "px"], tutte) {
  const regola = [...tutte].reverse().find((r) => r.media === media && r.selettori.includes(selettore) && r.dichiarazioni.has(proprieta));
  if (!regola) throw new Error(`Non trovo «${selettore} { ${proprieta} }»${media ? ` in @media ${media}` : ""} nel CSS della v2`);
  const valore = regola.dichiarazioni.get(proprieta);
  const commento = `  /// \`${media ? `@media ${media} ` : ""}${selettore} { ${proprieta}: ${valore} }\``;
  if (modo === "durata") {
    const m = /([\d.]+)(m?s)\b/.exec(valore);
    if (!m) throw new Error(`${selettore}: nessuna durata in «${valore}»`);
    const ms = m[2] === "s" ? Number(m[1]) * 1000 : Number(m[1]);
    return `${commento}\n  static const Duration ${nome} = Duration(milliseconds: ${Math.round(ms)});`;
  }
  if (modo === "dimensioneFont" || modo === "interlinea") {
    const m = /([\d.]+(?:px|rem))\/([\d.]+)/.exec(valore);
    if (!m) throw new Error(`${selettore}: «font» senza dimensione/interlinea: «${valore}»`);
    const v = modo === "dimensioneFont" ? px(m[1]) : Number(m[2]);
    return `${commento}\n  static const double ${nome} = ${numero(v)};`;
  }
  const testo = modo === "primoPx" ? (/([\d.]+(?:px|rem))/.exec(valore)?.[1] ?? "") : valore;
  const v = px(testo);
  if (v === null) throw new Error(`${selettore} { ${proprieta}: ${valore} } non è una misura`);
  return `${commento}\n  static const double ${nome} = ${numero(v)};`;
}

/* ---- generazione ---------------------------------------------------------------------------------------------- */

const css = senzaCommenti(readFileSync(CSS, "utf-8"));
const tutte = regole(css);
const root = tutte.find((r) => r.selettori.includes(":root") && r.media === null);
if (!root) throw new Error("Nel CSS della v2 non c'è `:root`");

const righeRoot = [];
const saltate = [];
for (const [nome, valore] of root.dichiarazioni) {
  if (!nome.startsWith("--")) continue;
  const riga = variabile(nome, valore);
  if (riga) righeRoot.push(riga);
  else saltate.push(`${nome}: ${valore}`);
}

const punti = [...new Set([...css.matchAll(/@media\s*\(max-width:\s*(\d+)px\)/g)].map((m) => Number(m[1])))].sort((a, b) => a - b);

const dart = `// GENERATO da frontend/scripts/genera-token.mjs da frontend/app/(v2)/v2.css: non modificare a mano.
// Per cambiare un colore o una misura si cambia il CSS del sito e si rilancia lo script.

// ignore_for_file: lines_longer_than_80_chars

import 'package:flutter/widgets.dart';

/// Una misura che cresce con la larghezza della finestra: \`clamp(minimo, vw, massimo)\` del CSS.
@immutable
class MisuraFluida {
  /// Il valore più piccolo, in px logici.
  final double minimo;

  /// La percentuale della larghezza della finestra (\`4vw\` → 4).
  final double vw;

  /// Il valore più grande, in px logici.
  final double massimo;

  /// \`clamp(minimo, vw, massimo)\`.
  const MisuraFluida({required this.minimo, required this.vw, required this.massimo});

  /// Il valore per una finestra larga [larghezza] px logici.
  double per(double larghezza) => (larghezza * vw / 100).clamp(minimo, massimo);
}

/// I valori del CSS della v2: variabili di \`:root\`, punti di rottura e misure ricorrenti.
abstract final class Token {
${righeRoot.join("\n\n")}

  /// I punti di rottura del CSS (\`@media (max-width: Npx)\`), dal più stretto.
  static const List<double> puntiDiRottura = [${punti.map((p) => numero(p)).join(", ")}];

${DERIVATI.map((d) => derivato(d, tutte)).join("\n\n")}
}
`;

if (saltate.length) console.warn(`variabili non convertite: ${saltate.join("; ")}`);

if (controlla) {
  if (!existsSync(USCITA) || readFileSync(USCITA, "utf-8") !== dart) {
    console.error(`da rigenerare: ${USCITA}\nI token dell'app non corrispondono a v2.css: \`node scripts/genera-token.mjs\`.`);
    process.exit(1);
  }
  console.log(`Token aggiornati: ${righeRoot.length} variabili, ${punti.length} punti di rottura, ${DERIVATI.length} misure.`);
} else {
  mkdirSync(dirname(USCITA), { recursive: true });
  writeFileSync(USCITA, dart, "utf-8");
  console.log(`Scritto ${USCITA}: ${righeRoot.length} variabili, ${punti.length} punti di rottura, ${DERIVATI.length} misure.`);
}
