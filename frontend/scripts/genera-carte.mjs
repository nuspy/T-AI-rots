/* Genera le facce segnaposto delle 78 carte: un SVG per carta, con il solo
 * valore della carta in testo. Servono finché non arrivano le immagini
 * definitive, che prenderanno il loro posto con lo stesso nome.
 *
 *   npm run carte
 *
 * Legge il mazzo dal backend, così i segnaposto non possono divergere dalle
 * carte che il server estrae. */

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const qui = dirname(fileURLToPath(import.meta.url));
const mazzo = JSON.parse(
  readFileSync(join(qui, "../../backend/tarot_core/knowledge/deck.json"), "utf-8"),
);
const uscita = join(qui, "../public/cards");
mkdirSync(uscita, { recursive: true });

const RANGHI = {
  asso: "Asso", due: "2", tre: "3", quattro: "4", cinque: "5", sei: "6", sette: "7",
  otto: "8", nove: "9", dieci: "10", cavaliere: "Cavaliere", regina: "Regina",
  principe: "Principe", principessa: "Principessa",
};

const esc = (t) => String(t).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

for (const c of mazzo) {
  const maggiore = c.arcano === "maggiore";
  const valore = maggiore ? c.numero_romano : RANGHI[c.rango] ?? "";
  const nome = maggiore ? c.nome_it : c.nome_it.split(" — ")[0];
  const sotto = maggiore ? c.nome_thoth : (c.titolo_thoth && !c.corte && c.rango !== "asso" ? c.titolo_thoth : c.seme);
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 500">
  <rect width="300" height="500" rx="18" fill="#171129"/>
  <rect x="12" y="12" width="276" height="476" rx="12" fill="none" stroke="#d8b45a" stroke-width="2"/>
  <text x="150" y="235" text-anchor="middle" font-family="Georgia, serif" font-size="${valore.length > 4 ? 44 : 84}" fill="#f1d68e">${esc(valore)}</text>
  <text x="150" y="320" text-anchor="middle" font-family="Georgia, serif" font-size="26" fill="#efe6d2">${esc(nome)}</text>
  <text x="150" y="360" text-anchor="middle" font-family="Georgia, serif" font-style="italic" font-size="20" fill="#b3a8cf">${esc(sotto ?? "")}</text>
</svg>
`;
  writeFileSync(join(uscita, `${c.id}.svg`), svg);
}
console.log(`${mazzo.length} carte scritte in public/cards`);
