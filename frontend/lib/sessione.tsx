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
  /* Ruolo `admin`: dà accesso alla console (vedi `ADMIN_URL`). */
  admin: boolean;
  entra: (ritorno?: string) => void;
  registrati: () => void;
  /* Lancia l'attivazione della verifica in due passaggi (Keycloak: «Configure OTP»)
   * e torna al profilo. Non fa niente senza Keycloak (sviluppo senza autenticazione). */
  attiva2fa: () => void;
  esci: () => void;
}

const Contesto = createContext<Sessione | null>(null);

export const AUTH_DISATTIVATA = process.env.NEXT_PUBLIC_AUTH_DISABLED === "true";

/* Dove sta la console di amministrazione: sullo stesso dominio, sotto `/admin`,
 * in produzione; in sviluppo è un'altra porta (`NEXT_PUBLIC_ADMIN_URL`). */
export const ADMIN_URL = process.env.NEXT_PUBLIC_ADMIN_URL ?? "/admin";

/* I ruoli di realm dal token d'accesso. Il token si legge, non si verifica: qui
 * serve solo a mostrare o nascondere un collegamento — chi lo apre senza il
 * ruolo trova la console che gli risponde 403. */
function ruoliDaToken(token?: string | null): string[] {
  if (!token) return [];
  try {
    const corpo = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    const dati = JSON.parse(atob(corpo.padEnd(Math.ceil(corpo.length / 4) * 4, "=")));
    return Array.isArray(dati?.realm_access?.roles) ? dati.realm_access.roles : [];
  } catch {
    return [];
  }
}

export function SessioneKeycloak({
  children, ritorno2fa = "/profilo",
}: {
  children: React.ReactNode;
  /** Dove torna chi attiva la verifica in due passaggi: il profilo del sito, o quello della v2. */
  ritorno2fa?: string;
}) {
  const auth = useAuth();
  const valore = useMemo<Sessione>(
    () => ({
      pronta: !auth.isLoading,
      autenticata: auth.isAuthenticated,
      token: auth.user?.access_token ?? null,
      nome: auth.user?.profile?.given_name ?? auth.user?.profile?.name ?? null,
      admin: ruoliDaToken(auth.user?.access_token).includes("admin"),
      entra: (ritorno) =>
        auth.signinRedirect(ritorno ? { state: { ritorno } } : undefined),
      /* La registrazione è la pagina di Keycloak, social compresi:
       * `prompt=create` apre direttamente il modulo invece del login. */
      registrati: () => auth.signinRedirect({ prompt: "create" }),
      /* «Application initiated action» di Keycloak: dopo l'accesso (o subito, se la
       * sessione è fresca) mostra la configurazione dell'OTP e poi torna qui. */
      attiva2fa: () =>
        auth.signinRedirect({ extraQueryParams: { kc_action: "CONFIGURE_TOTP" }, state: { ritorno: ritorno2fa } }),
      esci: () => auth.signoutRedirect(),
    }),
    [auth, ritorno2fa],
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
      admin: true,
      entra: () => {},
      registrati: () => {},
      attiva2fa: () => {},
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
