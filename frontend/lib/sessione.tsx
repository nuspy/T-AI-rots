"use client";

/* Chi sta usando l'app, qualunque sia il modo in cui è entrato.
 *
 * Il resto dell'interfaccia chiede `useSessione()` e non sa se dietro c'è
 * Keycloak o lo sviluppo senza autenticazione. Serve perché
 * `NEXT_PUBLIC_AUTH_DISABLED=true` — l'app contro un backend con
 * `TAROT_AUTH_DISABLED=true` — deve funzionare senza montare `AuthProvider`,
 * e un `useAuth()` chiamato fuori dal suo provider fallisce.
 */

import { createContext, useContext, useMemo } from "react";
import { useAuth } from "react-oidc-context";

export interface Sessione {
  pronta: boolean;
  autenticata: boolean;
  token: string | null;
  nome: string | null;
  entra: (ritorno?: string) => void;
  registrati: () => void;
  esci: () => void;
}

const Contesto = createContext<Sessione | null>(null);

export const AUTH_DISATTIVATA = process.env.NEXT_PUBLIC_AUTH_DISABLED === "true";

export function SessioneKeycloak({ children }: { children: React.ReactNode }) {
  const auth = useAuth();
  const valore = useMemo<Sessione>(
    () => ({
      pronta: !auth.isLoading,
      autenticata: auth.isAuthenticated,
      token: auth.user?.access_token ?? null,
      nome: auth.user?.profile?.given_name ?? auth.user?.profile?.name ?? null,
      entra: (ritorno) =>
        auth.signinRedirect(ritorno ? { state: { ritorno } } : undefined),
      /* La registrazione è la pagina di Keycloak, social compresi:
       * `prompt=create` apre direttamente il modulo invece del login. */
      registrati: () => auth.signinRedirect({ prompt: "create" }),
      esci: () => auth.signoutRedirect(),
    }),
    [auth],
  );
  return <Contesto.Provider value={valore}>{children}</Contesto.Provider>;
}

export function SessioneDiSviluppo({ children }: { children: React.ReactNode }) {
  const valore = useMemo<Sessione>(
    () => ({
      pronta: true,
      autenticata: true,
      token: null,
      nome: "Sviluppo",
      entra: () => {},
      registrati: () => {},
      esci: () => {},
    }),
    [],
  );
  return <Contesto.Provider value={valore}>{children}</Contesto.Provider>;
}

export function useSessione(): Sessione {
  const s = useContext(Contesto);
  if (!s) throw new Error("useSessione fuori dal provider");
  return s;
}
