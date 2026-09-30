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

/** L'API non ha risposto (lenta, spenta, in errore): non vuol dire che la pagina non esista. */
export class ApiNonDisponibile extends Error {}

/** Legge un endpoint pubblico. `null` se non risponde o risponde con un errore: la
 *  pagina decide che fare (elenco vuoto, sezione nascosta). Le pagine che lo usano sono sempre
 *  scritte al momento della richiesta (`no-store`): mai in fase di build, quando l'API non c'è.
 *
 *  `obbligatorio`: per il dato senza cui la pagina non esiste (l'articolo, la carta). Allora `null`
 *  vuol dire solo «l'API ha risposto 404», e la pagina risponde 404; un'API lenta o in errore
 *  lancia `ApiNonDisponibile`, e la pagina risponde 500. La differenza conta per i motori: un 404
 *  toglie la pagina dall'indice, un 5xx si riprova più tardi (l'audit SEO del 30/9 ha visto 55
 *  pagine in 404 con sei richieste in parallelo e l'API lenta a freddo). */
export async function leggiDalServer<T>(
  percorso: string,
  { secondi = 30, obbligatorio = false }: { secondi?: number; obbligatorio?: boolean } = {},
): Promise<T | null> {
  const ora = Date.now();
  const noto = memoria.get(percorso);
  if (noto && noto.scade > ora) return noto.valore as T;
  let risposta: Response;
  try {
    risposta = await fetch(`${API_INTERNA}${percorso}`, {
      cache: "no-store",
      signal: AbortSignal.timeout(obbligatorio ? 15000 : 5000),
    });
  } catch (errore) {
    if (obbligatorio) throw new ApiNonDisponibile(`${percorso}: ${String(errore)}`);
    return null;
  }
  if (!risposta.ok) {
    if (obbligatorio && risposta.status !== 404) throw new ApiNonDisponibile(`${percorso}: HTTP ${risposta.status}`);
    return null;
  }
  try {
    const valore = (await risposta.json()) as T;
    memoria.set(percorso, { scade: ora + secondi * 1000, valore });
    if (memoria.size > 500) memoria.delete(memoria.keys().next().value as string);
    return valore;
  } catch (errore) {
    if (obbligatorio) throw new ApiNonDisponibile(`${percorso}: ${String(errore)}`);
    return null;
  }
}
