"use client";

import { VECCHIO, vecchio } from "@/lib/percorsi";
import { useMemo } from "react";
import { AuthProvider } from "react-oidc-context";
import { WebStorageStateStore } from "oidc-client-ts";
import { SITE_URL } from "@/lib/condivisione";
import { ProviderLingua, type Lingua } from "@/lib/lingua";
import { AUTH_DISATTIVATA, SessioneDiSviluppo, SessioneKeycloak } from "@/lib/sessione";
import { AttribuzioneCondivisione } from "@/lib/attribuzione";
import { BannerCookie } from "./componenti/banner-cookie";
import { Oracolo } from "./componenti/oracolo";
import { OsservatorePagine } from "./componenti/osservatore";
import { Promemoria2fa } from "./componenti/promemoria-2fa";
import { RiscattoInvitoAutomatico } from "@/lib/riscatto-invito";

/* Autenticazione: il codice di autorizzazione con PKCE, come in Personalities.
 *
 * Il client è pubblico — gira in un browser, dove nessun segreto resta
 * segreto — quindi PKCE non è un'opzione fra le altre: è ciò che impedisce a
 * chi intercettasse il codice di riscattarlo. Registrazione, login con email e
 * login social (Google, Facebook, Apple) sono pagine di Keycloak.
 *
 * I token stanno in `localStorage` (v6, Fase G: prima erano in `sessionStorage`, e duravano solo
 * quanto la scheda). La scelta è deliberata e non priva di costo: un token in `localStorage` è
 * leggibile da qualunque script capace di eseguire nella pagina — niente nel browser lo protegge,
 * a differenza di un cookie `HttpOnly`. Il progetto si affidava a `sessionStorage` esplicitamente
 * per questa ragione. Il cambio è stato scelto per il login persistente (non rifare l'accesso a ogni
 * riapertura del browser), accettando il rischio: se in futuro emergesse un vettore XSS altrove,
 * l'impatto passa da "la scheda si disconnette" a "il token resta rubabile finché non scade o non
 * si fa logout esplicito ovunque". Nessuna mitigazione aggiuntiva oltre a quelle già in essere
 * (niente HTML grezzo nel blog, nessun `dangerouslySetInnerHTML`).
 *
 * **Il provider gira anche sul server.** Le pagine pubbliche (carte, stese, blog) devono
 * uscire dal server già scritte: chi le cerca — un motore di ricerca, un'anteprima
 * dei social — non aspetta JavaScript. `react-oidc-context` sul server non crea il
 * gestore dell'accesso e dice «sessione in caricamento», come nel primo rendering del
 * browser: i due alberi coincidono e l'idratazione non ha da correggere niente.
 * Ciò che dipende dal browser (`redirect_uri` da `window.location.origin`, i token in
 * `localStorage`) si calcola solo dove `window` esiste.
 */

const authority = `${
  process.env.NEXT_PUBLIC_KEYCLOAK_URL ?? "http://localhost:8080"
}/realms/${process.env.NEXT_PUBLIC_KEYCLOAK_REALM ?? "tarots"}`;

function onSigninCallback(user: unknown): void {
  /* Toglie `code` e `state` dalla barra degli indirizzi dopo il login, e
   * torna dove l'utente stava — la lettura interrotta, per esempio. */
  const stato = (user as { state?: { ritorno?: string } } | undefined)?.state;
  const ritorno = stato?.ritorno && stato.ritorno.startsWith("/") && !stato.ritorno.startsWith("//") ? vecchio(stato.ritorno) : window.location.pathname;
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
            redirect_uri: nelBrowser ? `${window.location.origin}${VECCHIO}` : `${SITE_URL}${VECCHIO}`,
            post_logout_redirect_uri: nelBrowser ? `${window.location.origin}${VECCHIO}` : `${SITE_URL}${VECCHIO}`,
            response_type: "code",
            scope: "openid profile email",
            /* Rinnovo silenzioso prima della scadenza: senza, una lettura
             * lunga si interrompe con un 401 a metà del responso. */
            automaticSilentRenew: true,
            userStore: nelBrowser ? new WebStorageStateStore({ store: window.localStorage }) : undefined,
            onSigninCallback,
          },
    [],
  );

  if (!config) {
    return (
      <ProviderLingua iniziale={linguaIniziale}>
        <SessioneDiSviluppo>
          <OsservatorePagine>
            <BannerCookie />
            {children}
          </OsservatorePagine>
        </SessioneDiSviluppo>
      </ProviderLingua>
    );
  }

  return (
    <AuthProvider {...config}>
      <ProviderLingua iniziale={linguaIniziale}>
        <SessioneKeycloak>
          <OsservatorePagine>
            <AttribuzioneCondivisione />
            <RiscattoInvitoAutomatico />
            <Promemoria2fa />
            <Oracolo />
            <BannerCookie />
            {children}
          </OsservatorePagine>
        </SessioneKeycloak>
      </ProviderLingua>
    </AuthProvider>
  );
}
