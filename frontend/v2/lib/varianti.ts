/* La prova della lettura (v9.5): la versione classica e quella tutta in chat, con indirizzi propri. Qui come si
 * riconosce la variante dal percorso, per marcare gli eventi delle statistiche (`piattaforma` e `variante` in ogni
 * evento, vedi `componenti/osservatore.tsx`) e le letture salvate. Finché la lettura in chat non c'è, le pagine della
 * lettura sono quelle classiche. */

export type VarianteLettura = "classica" | "chat";

const CHAT = ["/read-chat", "/it/read-chat"];
const CLASSICA = ["/read-classic", "/it/read-classic", "/read", "/it/read", "/v2/read", "/it/v2/read"];

const sotto = (p: string, base: string) => p === base || p.startsWith(`${base}/`);

/** La variante della pagina di lettura, o null se il percorso non è una pagina di lettura. */
export function varianteDaPercorso(percorso: string): VarianteLettura | null {
  const p = percorso.split(/[?#]/)[0].replace(/\/$/, "") || "/";
  if (CHAT.some((b) => sotto(p, b))) return "chat";
  if (CLASSICA.some((b) => sotto(p, b))) return "classica";
  return null;
}

/** Le proprietà comuni di ogni evento del sito: la piattaforma e, sulle pagine di lettura, la variante. */
export function proprietaEventi(percorso: string): Record<string, string> {
  const variante = varianteDaPercorso(percorso);
  return variante ? { piattaforma: "web", variante } : { piattaforma: "web" };
}
