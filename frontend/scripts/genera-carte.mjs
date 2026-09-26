/* Genera le facce segnaposto delle 78 carte: un SVG 9:16 per carta, con il
 * solo valore della carta in testo. Le immagini definitive sono `.webp`: questi
 * si usano solo con NEXT_PUBLIC_CARD_EXT=svg.
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
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 640">
  <rect width="360" height="640" rx="20" fill="#171129"/>
  <rect x="14" y="14" width="332" height="612" rx="14" fill="none" stroke="#d8b45a" stroke-width="2.4"/>
  <text x="180" y="300" text-anchor="middle" font-family="Georgia, serif" font-size="${valore.length > 4 ? 52 : 100}" fill="#f1d68e">${esc(valore)}</text>
  <text x="180" y="410" text-anchor="middle" font-family="Georgia, serif" font-size="30" fill="#efe6d2">${esc(nome)}</text>
  <text x="180" y="458" text-anchor="middle" font-family="Georgia, serif" font-style="italic" font-size="23" fill="#b3a8cf">${esc(sotto ?? "")}</text>
</svg>
`;
  writeFileSync(join(uscita, `${c.id}.svg`), svg);
}
console.log(`${mazzo.length} carte scritte in public/cards`);
