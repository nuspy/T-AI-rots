/* L'API vista dal server di Next: per le pagine che devono uscire già scritte.
 *
 * Le pagine pubbliche (carte, stese, blog) non aspettano il JavaScript del browser: chi
 * le cerca — un motore di ricerca, l'anteprima di un social — legge l'HTML del server.
 * Il server di Next parla con l'API dall'interno (`API_INTERNAL_URL`, per esempio il
 * servizio del cluster); nel browser resta `NEXT_PUBLIC_API_URL`. */

/* L'indirizzo pubblico dell'API: quello che il browser (e i social) raggiungono. */
export const API_PUBBLICA = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8100";

/* Quello che usa il server di Next: interno se c'è, altrimenti lo stesso pubblico. */
export const API_INTERNA = process.env.API_INTERNAL_URL ?? API_PUBBLICA;

/* Le risposte già lette, per pochi secondi: un crawler che visita cento pagine non deve
 * fare cento chiamate uguali all'API. Sta in memoria del processo (non nella cache dei dati
 * di Next): quella cuocerebbe nella build, quando l'API non c'è, un elenco vuoto. */
const memoria = new Map<string, { scade: number; valore: unknown }>();

/** Legge un endpoint pubblico. `null` se non risponde o risponde con un errore: la
 *  pagina decide che fare (404, elenco vuoto). Le pagine che lo usano sono sempre scritte
 *  al momento della richiesta (`no-store`): mai in fase di build, quando l'API non c'è. */
export async function leggiDalServer<T>(
  percorso: string,
  { secondi = 30 }: { secondi?: number } = {},
): Promise<T | null> {
  const ora = Date.now();
  const noto = memoria.get(percorso);
  if (noto && noto.scade > ora) return noto.valore as T;
  try {
    const risposta = await fetch(`${API_INTERNA}${percorso}`, {
      cache: "no-store",
      signal: AbortSignal.timeout(5000),
    });
    if (!risposta.ok) return null;
    const valore = (await risposta.json()) as T;
    memoria.set(percorso, { scade: ora + secondi * 1000, valore });
    if (memoria.size > 500) memoria.delete(memoria.keys().next().value as string);
    return valore;
  } catch {
    return null;
  }
}
