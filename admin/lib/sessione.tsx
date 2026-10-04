"use client";

import { createContext, useContext, useEffect, useRef, useState } from "react";
import { useAuth, type AuthContextProps } from "react-oidc-context";

/* Chi sta usando la console, detto in un modo che non dipende da Keycloak.
 *
 * In Personalities le pagine chiamano `useAuth()` direttamente. Qui non si
 * può: con `NEXT_PUBLIC_AUTH_DISABLED=true` l'`AuthProvider` non c'è, e
 * `useAuth` fuori dal suo provider lancia un errore invece di restituire
 * «nessuno». Il guscio e i hook leggono quindi questa sessione, che in
 * produzione è un riflesso di `useAuth` e in sviluppo è un valore fisso.
 */

/** L'autenticazione è spenta: il backend gira con `TAROT_AUTH_DISABLED`. */
export const AUTENTICAZIONE_SPENTA =
  process.env.NEXT_PUBLIC_AUTH_DISABLED === "true";

export interface Sessione {
  inCaricamento: boolean;
  autenticato: boolean;
  /** Il token per le chiamate: `null` finché non c'è, stringa vuota quando
   *  l'autenticazione è spenta e le richieste partono senza intestazione. */
  token: string | null;
  chi: string | null;
  ruoli: string[];
  entra: () => void;
  esci: () => void;
}

const nessuno = () => undefined;

/* La sessione di sviluppo: stesso ruolo del principal di sviluppo del
 * backend, così la console mostra tutto ciò che quello le lascerà fare. */
const SVILUPPO: Sessione = {
  inCaricamento: false,
  autenticato: true,
  token: "",
  chi: "sviluppo",
  ruoli: ["admin"],
  entra: nessuno,
  esci: nessuno,
};

const Contesto = createContext<Sessione>(SVILUPPO);

export function useSessione(): Sessione {
  return useContext(Contesto);
}

export function SessioneDiSviluppo({ children }: { children: React.ReactNode }) {
  return <Contesto.Provider value={SVILUPPO}>{children}</Contesto.Provider>;
}

/* I ruoli dove Keycloak li scrive: quelli di realm e quelli dei client. Il
 * backend li unisce allo stesso modo (`_extract_roles`), e la console deve
 * dire di sì a chi il backend lascerà passare. */
function ruoliDi(profilo: Record<string, unknown> | undefined): string[] {
  if (!profilo) return [];
  const realm =
    (profilo.realm_access as { roles?: string[] } | undefined)?.roles ?? [];
  const risorse =
    (profilo.resource_access as Record<string, { roles?: string[] }> | undefined) ?? {};
  return [...realm, ...Object.values(risorse).flatMap((r) => r?.roles ?? [])];
}

/* Le claim di un JWT, senza verificarne la firma: la verifica è del backend,
 * che è chi decide. Qui servono solo a sapere cosa mostrare. */
function claimDelToken(token: string | undefined): Record<string, unknown> | undefined {
  if (!token) return undefined;
  try {
    const corpo = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    return JSON.parse(atob(corpo.padEnd(Math.ceil(corpo.length / 4) * 4, "=")));
  } catch {
    return undefined;
  }
}

/* Lo scope del login persistente, lo stesso del sito (`frontend/lib/sessione.tsx`): con `offline_access` il
 * token di rinnovo è offline, sopravvive alla chiusura del browser e al riavvio della macchina, e scade solo dopo
 * l'inattività impostata in «Impostazioni → Login persistente» o con il logout, che lo revoca. Chi amministra da
 * una postazione condivisa deve uscire con «Esci», non solo chiudere la scheda. */
export const SCOPE_PERSISTENTE = "openid profile email offline_access";

/* La ripresa all'apertura: con il token d'accesso scaduto ma un token di rinnovo ancora in `localStorage`, lo si
 * usa una volta invece di mostrare di nuovo l'accesso (`react-oidc-context` da solo non ci prova). Se fallisce
 * (revocato, scaduto) i token vecchi si buttano e compare la soglia d'accesso. Vero finché la ripresa è
 * possibile o in corso: la console resta «in caricamento» invece di lampeggiare la soglia. */
function useRipresaSessione(auth: AuthContextProps): boolean {
  const tokenRinnovo = auth.user?.refresh_token ?? null;
  const [fallitaPer, setFallitaPer] = useState<string | null>(null);
  const inCorso = useRef<string | null>(null);
  const riprendibile =
    !auth.isLoading && !auth.isAuthenticated && !auth.activeNavigator && !!tokenRinnovo && tokenRinnovo !== fallitaPer;

  useEffect(() => {
    if (!riprendibile || !tokenRinnovo || inCorso.current === tokenRinnovo) return;
    inCorso.current = tokenRinnovo;
    /* `react-oidc-context` non rifiuta la promessa quando il rinnovo fallisce: mette l'errore in `auth.error` e
     * restituisce `null`. Va trattato come un fallimento, altrimenti la ripresa resta «in corso» per sempre. */
    const fallita = () => {
      setFallitaPer(tokenRinnovo);
      return auth.removeUser();
    };
    auth
      .signinSilent()
      .then((utente) => (utente ? undefined : fallita()), fallita)
      .catch(() => undefined);
  }, [riprendibile, tokenRinnovo, auth]);

  return riprendibile;
}

/** Traduce `useAuth` nella sessione. Va montato dentro l'`AuthProvider`. */
export function SessioneOidc({ children }: { children: React.ReactNode }) {
  const auth = useAuth();
  const riprendendo = useRipresaSessione(auth);
  const profilo = auth.user?.profile;

  const sessione: Sessione = {
    inCaricamento: auth.isLoading || riprendendo,
    autenticato: auth.isAuthenticated,
    token: auth.user?.access_token ?? null,
    chi: (profilo?.email ?? profilo?.name ?? null) as string | null,
    /* **Anche** dal token d'accesso: i ruoli di realm Keycloak li scrive lì
     * (`realm_access`) e non nell'ID token da cui viene il profilo. Il backend
     * legge il token d'accesso, e la console deve concordare con lui — prima
     * leggeva solo il profilo, e nessun amministratore riusciva a entrare. */
    ruoli: [
      ...new Set([
        ...ruoliDi(profilo as Record<string, unknown> | undefined),
        ...ruoliDi(claimDelToken(auth.user?.access_token)),
      ]),
    ],
    /* La console è in italiano: anche la pagina di accesso di Keycloak. */
    entra: () => {
      auth.signinRedirect({ extraQueryParams: { ui_locales: "it" } }).catch(() => undefined);
    },
    /* Prima la revoca del token offline (chiudere la sessione del browser in Keycloak non lo invalida), poi il
     * logout. Se la revoca non riesce si esce comunque. */
    esci: () => {
      auth
        .revokeTokens(["refresh_token"])
        .catch(() => undefined)
        .then(() => auth.signoutRedirect())
        .catch(() => undefined);
    },
  };

  return <Contesto.Provider value={sessione}>{children}</Contesto.Provider>;
}
