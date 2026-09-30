/* Gli analytics del sito (v8, libreria `lanterna`): lo stato del consenso per il livello esteso.
 *
 * Due livelli. **Base**, per tutti: nessun cookie e nulla salvato nel browser, il server conta le
 * visite con un'impronta che cambia ogni giorno. **Esteso**, solo con «It's fine» nel banner: si
 * manda anche l'identificativo casuale del browser (`idVisitatore`), che permette di riconoscere i
 * ritorni nei giorni successivi e le visite prima dell'iscrizione. «Please no», o la revoca, lo fa
 * dimenticare anche al server. */

import { dimentica } from "lanterna-osservatore";
import { API } from "./api";
import { idVisitatore } from "./condivisione";

export const ENDPOINT_ANALYTICS = `${API}/e`;

let esteso = false;

export function impostaConsensoAnalytics(valore: "accettato" | "rifiutato" | null): void {
  const prima = esteso;
  esteso = valore === "accettato";
  if (prima && !esteso) dimentica(idVisitatore(), `${API}/e/dimentica`);
}

/** Revoca esplicita (pagina privacy): il server dimentica l'identificativo di questo browser. Solo
 *  per chi aveva accettato: a chi non ha mai accettato non si crea nessun identificativo. */
export function dimenticaAnalytics(): void {
  esteso = false;
  dimentica(idVisitatore(), `${API}/e/dimentica`);
}

/** L'identificativo del browser, solo col consenso. */
export const idPerAnalytics = (): string | null => (esteso ? idVisitatore() : null);
