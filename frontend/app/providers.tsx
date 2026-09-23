"use client";

import { useMemo, useSyncExternalStore } from "react";
import { AuthProvider } from "react-oidc-context";
import { WebStorageStateStore } from "oidc-client-ts";
import { ProviderLingua } from "@/lib/lingua";
import { AUTH_DISATTIVATA, SessioneDiSviluppo, SessioneKeycloak } from "@/lib/sessione";

/* Autenticazione: il codice di autorizzazione con PKCE, come in Personalities.
 *
 * Il client è pubblico — gira in un browser, dove nessun segreto resta
 * segreto — quindi PKCE non è un'opzione fra le altre: è ciò che impedisce a
 * chi intercettasse il codice di riscattarlo. Registrazione, login con email e
 * login social (Google, Facebook, Apple) sono pagine di Keycloak.
 *
 * I token stanno in `sessionStorage`: durano quanto la scheda.
 *
 * **Il provider si monta solo dopo l'idratazione.** `redirect_uri` si ricava
 * da `window.location.origin`, che sul server non esiste.
 */

const authority = `${
  process.env.NEXT_PUBLIC_KEYCLOAK_URL ?? "http://localhost:8080"
}/realms/${process.env.NEXT_PUBLIC_KEYCLOAK_REALM ?? "tarots"}`;

function onSigninCallback(user: unknown): void {
  /* Toglie `code` e `state` dalla barra degli indirizzi dopo il login, e
   * torna dove l'utente stava — la lettura interrotta, per esempio. */
  const stato = (user as { state?: { ritorno?: string } } | undefined)?.state;
  const ritorno = stato?.ritorno && stato.ritorno.startsWith("/") ? stato.ritorno : window.location.pathname;
  window.history.replaceState({}, document.title, ritorno);
}

const nessunaIscrizione = () => () => {};

function useSulClient(): boolean {
  return useSyncExternalStore(nessunaIscrizione, () => true, () => false);
}

export function Providers({ children }: { children: React.ReactNode }) {
  const montato = useSulClient();

  const config = useMemo(
    () =>
      montato && !AUTH_DISATTIVATA
        ? {
            authority,
            client_id: process.env.NEXT_PUBLIC_KEYCLOAK_CLIENT_ID ?? "tarot-frontend",
            redirect_uri: window.location.origin,
            post_logout_redirect_uri: window.location.origin,
            response_type: "code",
            scope: "openid profile email",
            /* Rinnovo silenzioso prima della scadenza: senza, una lettura
             * lunga si interrompe con un 401 a metà del responso. */
            automaticSilentRenew: true,
            userStore: new WebStorageStateStore({ store: window.sessionStorage }),
            onSigninCallback,
          }
        : null,
    [montato],
  );

  if (!montato) return null;

  if (AUTH_DISATTIVATA || !config) {
    return (
      <ProviderLingua>
        <SessioneDiSviluppo>{children}</SessioneDiSviluppo>
      </ProviderLingua>
    );
  }

  return (
    <AuthProvider {...config}>
      <ProviderLingua>
        <SessioneKeycloak>{children}</SessioneKeycloak>
      </ProviderLingua>
    </AuthProvider>
  );
}
