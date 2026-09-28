"use client";

import { useMemo, useSyncExternalStore } from "react";
import { AuthProvider } from "react-oidc-context";
import { WebStorageStateStore } from "oidc-client-ts";
import {
  AUTENTICAZIONE_SPENTA,
  SessioneDiSviluppo,
  SessioneOidc,
} from "@/lib/sessione";

/* Autenticazione della console. Stesso meccanismo del frontend, client
 * diverso: `tarot-admin` ha i propri redirect e vive su un'altra porta
 * (3001), così un token della console non vale per l'applicazione utente e
 * viceversa.
 *
 * Il codice di autorizzazione con PKCE.
 *
 * Il client è pubblico — gira in un browser, dove nessun segreto resta
 * segreto — quindi PKCE non è un'opzione fra le altre: è ciò che impedisce a
 * chi intercettasse il codice di riscattarlo.
 *
 * I token stanno in `localStorage` (v6, Fase G: prima erano in `sessionStorage`, apposta, proprio
 * perché un token che sopravvive alla chiusura del browser su una macchina condivisa è un token che
 * qualcun altro può usare — qui il rischio è più alto che nel frontend, dato il ruolo `admin`). Il
 * cambio è deliberato per il login persistente anche in console, su richiesta esplicita, e accetta
 * lo stesso compromesso del frontend: un token in `localStorage` è leggibile da qualunque script
 * capace di eseguire nella pagina, niente nel browser lo protegge come farebbe un cookie `HttpOnly`.
 * Nessuna mitigazione aggiuntiva oltre a quelle già in essere. Chi amministra da una postazione
 * condivisa dovrebbe comunque fare logout esplicito, non solo chiudere la scheda.
 *
 * **Perché il provider si monta solo dopo l'idratazione.** `redirect_uri` si
 * ricava da `window.location.origin`, che sul server non esiste. Montandolo
 * subito, l'`UserManager` nascerebbe con un indirizzo di ritorno vuoto e lo
 * terrebbe per sempre: il pulsante d'accesso non farebbe nulla — senza errori
 * in console, che è il modo peggiore in cui un difetto possa presentarsi.
 *
 * **Con `NEXT_PUBLIC_AUTH_DISABLED=true`** Keycloak non entra in gioco: niente
 * soglia d'accesso, niente token, e le richieste partono senza
 * `Authorization`. Ha senso solo accanto a un backend con
 * `TAROT_AUTH_DISABLED=true`, il cui utente di sviluppo è amministratore.
 */

/* Il percorso base con cui la console è stata costruita (`/admin` o vuoto):
 * l'indirizzo di ritorno del login lo comprende, e deve coincidere con uno dei
 * redirect del client `tarot-admin` in Keycloak. */
const BASE = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

const authority = `${
  process.env.NEXT_PUBLIC_KEYCLOAK_URL ?? "http://localhost:8080"
}/realms/${process.env.NEXT_PUBLIC_KEYCLOAK_REALM ?? "tarots"}`;

function onSigninCallback(): void {
  /* Toglie `code` e `state` dalla barra degli indirizzi dopo il login.
   * Senza, un aggiornamento della pagina rimanderebbe a Keycloak un codice già
   * consumato, e l'errore che ne esce parla di `invalid_grant` — cioè sembra
   * un guasto dell'autenticazione e non un semplice ricaricamento. */
  window.history.replaceState({}, document.title, window.location.pathname);
}

/* Vero sul client, falso sul server e durante l'idratazione.
 *
 * `useSyncExternalStore` e non uno stato impostato in un effetto: dà lo
 * stesso risultato — il primo rendering coincide con quello del server, il
 * successivo sa di essere nel browser — senza il rendering a cascata che un
 * `setState` dentro `useEffect` provoca. Non c'è niente a cui iscriversi: il
 * valore non cambia più dopo il montaggio. */
const nessunaIscrizione = () => () => {};

function useSulClient(): boolean {
  return useSyncExternalStore(nessunaIscrizione, () => true, () => false);
}

export function Providers({ children }: { children: React.ReactNode }) {
  const montato = useSulClient();

  const config = useMemo(
    () =>
      montato && !AUTENTICAZIONE_SPENTA
        ? {
            authority,
            client_id:
              process.env.NEXT_PUBLIC_KEYCLOAK_CLIENT_ID ?? "tarot-admin",
            redirect_uri: `${window.location.origin}${BASE}/`,
            post_logout_redirect_uri: `${window.location.origin}${BASE}/`,
            response_type: "code",
            scope: "openid profile email",
            /* Rinnovo silenzioso prima della scadenza: senza, una sessione
             * lunga in console si interrompe con un 401 a metà di una
             * modifica al catalogo. */
            automaticSilentRenew: true,
            userStore: new WebStorageStateStore({
              store: window.localStorage,
            }),
            onSigninCallback,
          }
        : null,
    [montato],
  );

  if (AUTENTICAZIONE_SPENTA) {
    return <SessioneDiSviluppo>{children}</SessioneDiSviluppo>;
  }

  if (!config) return null;

  return (
    <AuthProvider {...config}>
      <SessioneOidc>{children}</SessioneOidc>
    </AuthProvider>
  );
}
