"use client";

import { createContext, useContext } from "react";
import { useAuth } from "react-oidc-context";

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

/** Traduce `useAuth` nella sessione. Va montato dentro l'`AuthProvider`. */
export function SessioneOidc({ children }: { children: React.ReactNode }) {
  const auth = useAuth();
  const profilo = auth.user?.profile;

  const sessione: Sessione = {
    inCaricamento: auth.isLoading,
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
    entra: () => {
      auth.signinRedirect().catch(() => undefined);
    },
    esci: () => {
      auth.signoutRedirect().catch(() => undefined);
    },
  };

  return <Contesto.Provider value={sessione}>{children}</Contesto.Provider>;
}
