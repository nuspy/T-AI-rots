"use client";

import { useMemo } from "react";
import { AuthProvider } from "react-oidc-context";
import { WebStorageStateStore } from "oidc-client-ts";
import { SITE_URL } from "@/lib/condivisione";
import { ProviderLingua, type Lingua } from "@/lib/lingua";
import { AUTH_DISATTIVATA, SessioneDiSviluppo, SessioneKeycloak } from "@/lib/sessione";
import { AttribuzioneCondivisione } from "./componenti/attribuzione";
import { ChatProattiva } from "./componenti/chat-proattiva";
import { InvitoDomanda } from "./componenti/invito-domanda";
import { Promemoria2fa } from "./componenti/promemoria-2fa";
import { RiscattoInvitoAutomatico } from "./componenti/riscatto-invito";

/* Autenticazione: il codice di autorizzazione con PKCE, come in Personalities.
 *
 * Il client è pubblico — gira in un browser, dove nessun segreto resta
 * segreto — quindi PKCE non è un'opzione fra le altre: è ciò che impedisce a
 * chi intercettasse il codice di riscattarlo. Registrazione, login con email e
 * login social (Google, Facebook, Apple) sono pagine di Keycloak.
 *
 * I token stanno in `sessionStorage`: durano quanto la scheda.
 *
 * **Il provider gira anche sul server.** Le pagine pubbliche (carte, stese, blog) devono
 * uscire dal server già scritte: chi le cerca — un motore di ricerca, un'anteprima
 * dei social — non aspetta JavaScript. `react-oidc-context` sul server non crea il
 * gestore dell'accesso e dice «sessione in caricamento», come nel primo rendering del
 * browser: i due alberi coincidono e l'idratazione non ha da correggere niente.
 * Ciò che dipende dal browser (`redirect_uri` da `window.location.origin`, i token in
 * `sessionStorage`) si calcola solo dove `window` esiste.
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

const nelBrowser = typeof window !== "undefined";

export function Providers({ children, linguaIniziale }: { children: React.ReactNode; linguaIniziale?: Lingua }) {
  const config = useMemo(
    () =>
      AUTH_DISATTIVATA
        ? null
        : {
            authority,
            client_id: process.env.NEXT_PUBLIC_KEYCLOAK_CLIENT_ID ?? "tarot-frontend",
            /* Sul server non serve a niente (il gestore non esiste): un valore qualunque. */
            redirect_uri: nelBrowser ? window.location.origin : SITE_URL,
            post_logout_redirect_uri: nelBrowser ? window.location.origin : SITE_URL,
            response_type: "code",
            scope: "openid profile email",
            /* Rinnovo silenzioso prima della scadenza: senza, una lettura
             * lunga si interrompe con un 401 a metà del responso. */
            automaticSilentRenew: true,
            userStore: nelBrowser ? new WebStorageStateStore({ store: window.sessionStorage }) : undefined,
            onSigninCallback,
          },
    [],
  );

  if (!config) {
    return (
      <ProviderLingua iniziale={linguaIniziale}>
        <SessioneDiSviluppo>{children}</SessioneDiSviluppo>
      </ProviderLingua>
    );
  }

  return (
    <AuthProvider {...config}>
      <ProviderLingua iniziale={linguaIniziale}>
        <SessioneKeycloak>
          <AttribuzioneCondivisione />
          <RiscattoInvitoAutomatico />
          <Promemoria2fa />
          <InvitoDomanda />
          <ChatProattiva />
          {children}
        </SessioneKeycloak>
      </ProviderLingua>
    </AuthProvider>
  );
}
