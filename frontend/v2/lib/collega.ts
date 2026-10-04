/* Collegare Apple e Google all'account (v9, Fase 6): le chiamate di `backend/tarot_core/api/routers/collega.py`.
 *
 * - `leggiCollegamenti`: i social collegati e quelli che si possono collegare (Google e Apple, se accesi).
 * - `urlCollegamento`: l'indirizzo del collegamento avviato dal sito (`/broker/{alias}/link` di Keycloak). Va aperto
 *   subito dopo un passaggio da Keycloak, perché l'id della sessione nel token deve essere quello del browser.
 * - `usaCodice`: il codice monouso mostrato dall'app su un account appena nato; qui, nell'account vecchio, lo si usa
 *   e l'accesso dell'app passa a questo account. */

import { chiama, ErroreApi } from "@/lib/api";

export type SocialCollegabile = "google" | "apple";

export interface Collegamenti {
  raggiungibile: boolean;
  collegati: string[];
  collegabili: SocialCollegabile[];
}

export const leggiCollegamenti = (token: string | null) => chiama<Collegamenti>(token, "/me/collega");

export const urlCollegamento = (token: string | null, provider: SocialCollegabile, ritorno: string) =>
  chiama<{ url: string }>(token, "/me/collega/social", { method: "POST", body: { provider, ritorno } });

export const usaCodice = (token: string | null, codice: string) =>
  chiama<{ provider: string[]; spostati: Record<string, number> }>(token, "/me/collega/usa", {
    method: "POST", body: { codice },
  });

/** Il motivo che il server dà a un rifiuto (`detail.motivo`), per scegliere il testo giusto. */
export function motivoErrore(e: unknown): { motivo: string; provider?: string[] } {
  if (e instanceof ErroreApi && e.dettaglio && typeof e.dettaglio === "object") {
    const d = e.dettaglio as { motivo?: unknown; provider?: unknown };
    if (typeof d.motivo === "string") {
      return { motivo: d.motivo, provider: Array.isArray(d.provider) ? d.provider.map(String) : undefined };
    }
  }
  return { motivo: "generico" };
}

/** Le parti dell'indirizzo che il collegamento usa: `?collega=apple` (dopo il passaggio da Keycloak, si chiede
 *  l'indirizzo e si parte) e `?collegato=apple` (il ritorno da Keycloak, con `link_error` se non è riuscito). */
export const PARAMETRO_COLLEGA = "collega";
export const PARAMETRO_COLLEGATO = "collegato";

export function eCollegabile(valore: string | null): valore is SocialCollegabile {
  return valore === "google" || valore === "apple";
}
