/* I dizionari, e il ripiego sull'inglese.
 *
 * Un dizionario si legge con `dizionario(lingua)`: l'inglese è la base, e la
 * traduzione della lingua (intera o parziale) la ricopre. Per le lingue senza
 * traduzione il risultato è l'inglese. Per aggiungere una lingua basta un file
 * `xx.ts` con un `Parziale` e una riga in `TRADUZIONI`.
 */

import { en } from "./en";
import { hu } from "./hu";
import { it, type Dizionario, type Parziale } from "./it";
import type { Lingua } from "./lingue";

export type { Chiave, Dizionario, Parziale } from "./it";
export {
  LINGUE, PREDEFINITA, TRADOTTE, comeLingua, datiLingua, linguaDelBrowser, type Lingua,
} from "./lingue";
export { nomeCarta, nomePosizione, nomeStesa, nomeStesaDaNomi } from "./nomi";

const TRADUZIONI: Partial<Record<Lingua, Parziale>> = { it, en, hu };

const memoria = new Map<Lingua, Dizionario>();

export function dizionario(lingua: Lingua): Dizionario {
  let d = memoria.get(lingua);
  if (!d) {
    d = { ...en, ...(TRADUZIONI[lingua] ?? {}) };
    memoria.set(lingua, d);
  }
  return d;
}
