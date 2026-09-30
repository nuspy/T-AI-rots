/* Sul server: legge dall'API i percorsi che la pagina userà, per `DatiIniziali` (`v2/lib/iniziali.tsx`). Un percorso
 * che non risponde si salta: la pagina lo chiederà dal browser, come prima. */

import { leggiDalServer } from "@/lib/server-api";

export async function precarica(percorsi: (string | null | undefined)[], secondi = 60): Promise<Record<string, unknown>> {
  const elenco = [...new Set(percorsi.filter((p): p is string => !!p))];
  const valori = await Promise.all(elenco.map((p) => leggiDalServer<unknown>(p, { secondi })));
  return Object.fromEntries(elenco.flatMap((p, i) => (valori[i] == null ? [] : [[p, valori[i]]])));
}
