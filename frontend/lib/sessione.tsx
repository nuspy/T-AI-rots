"use client";

/* Chi sta usando l'app, qualunque sia il modo in cui è entrato.
 *
 * Il resto dell'interfaccia chiede `useSessione()` e non sa se dietro c'è
 * Keycloak o lo sviluppo senza autenticazione. Serve perché
 * `NEXT_PUBLIC_AUTH_DISABLED=true` — l'app contro un backend con
 * `TAROT_AUTH_DISABLED=true` — deve funzionare senza montare `AuthProvider`,
 * e un `useAuth()` chiamato fuori dal suo provider fallisce.
 */

import { createContext, useContext, useEffect, useMemo, useRef, useState } from "react";
import { useAuth, type AuthContextProps } from "react-oidc-context";

export interface Sessione {
  pronta: boolean;
  autenticata: boolean;
  token: string | null;
  nome: string | null;
  /* Ruolo `admin`: dà accesso alla console (vedi `ADMIN_URL`). */
  admin: boolean;
  entra: (ritorno?: string) => void;
  registrati: () => void;
  /* La registrazione con un ritorno (v9, Fase 2b): la pagina della prova, per chi la sceglie dal banner. A parte da
   * `registrati`, che si passa così com'è agli `onClick` (riceverebbe l'evento come ritorno). */
  registratiPoi: (ritorno: string) => void;
  /* Un passaggio da Keycloak che torna **su questa stessa pagina** (v9, Fase 6): l'indirizzo di ritorno è la pagina
   * stessa (con i suoi parametri), così è lei a ricevere il codice e a ricaricarsi davvero. Con `entra(ritorno)` il
   * codice arriva alla home, che poi cambia solo l'indirizzo (`replaceState`): la pagina mostrata resta la home.
   * Serve al collegamento di Apple e Google, che vuole una sessione di Keycloak fresca nel browser. */
  entraQui: (ritorno: string) => void;
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

/* Lo scope del login persistente: con `offline_access` Keycloak rilascia un token di rinnovo **offline**, che non
 * dipende dalla sessione del browser (cookie) e sopravvive alla chiusura del browser, al riavvio della macchina e
 * a quello di Keycloak. Scade solo dopo `offlineSessionIdleTimeout` senza alcun uso (ogni rinnovo lo fa ripartire;
 * si regola dalla console, «Impostazioni → Login persistente») o con il logout, che lo revoca. Vedi
 * `deploy/keycloak/README.md`, «Login persistente». Lo stesso valore nei provider del sito, della v1 e della console.
 * Il costo, accettato: il token offline sta in `localStorage` come gli altri, e chi riuscisse a leggerlo (un XSS)
 * resterebbe dentro finché non viene revocato — col logout, o da Keycloak (Utenti → Sessioni → offline). */
export const SCOPE_PERSISTENTE = "openid profile email offline_access";

/* La lingua della pagina, per la pagina di accesso di Keycloak (`ui_locales`): chi naviga il sito in ungherese
 * trova il login in ungherese. Keycloak ignora una lingua che il realm non offre e usa la sua predefinita. */
function linguaPagina(): Record<string, string> {
  const lingua = typeof document !== "undefined" ? document.documentElement.lang : "";
  return lingua ? { ui_locales: lingua } : {};
}

/* La ripresa della sessione all'apertura.
 *
 * I token stanno in `localStorage`. Chi torna dopo ore (o giorni) trova un token d'accesso scaduto, e
 * `react-oidc-context` lo dichiara «non autenticato» senza provare a rinnovarlo: il rinnovo automatico parte solo
 * *prima* della scadenza, a pagina aperta. Qui, se c'è ancora un token di rinnovo, lo si usa una volta: riesce
 * (token offline valido) e si è di nuovo dentro senza vedere Keycloak; fallisce (revocato, scaduto per
 * inattività) e i token vecchi si buttano, così il sito mostra «Entra».
 *
 * Restituisce vero finché la ripresa è possibile o in corso: la sessione non è ancora «pronta», così l'interfaccia
 * non lampeggia «Entra» per un istante a chi in realtà è dentro. */
function useRipresaSessione(auth: AuthContextProps): boolean {
  const tokenRinnovo = auth.user?.refresh_token ?? null;
  const [fallitaPer, setFallitaPer] = useState<string | null>(null);
  const inCorso = useRef<string | null>(null);
  const riprendibile =
    !auth.isLoading && !auth.isAuthenticated && !auth.activeNavigator && !!tokenRinnovo && tokenRinnovo !== fallitaPer;

  useEffect(() => {
    if (!riprendibile || !tokenRinnovo || inCorso.current === tokenRinnovo) return;
    inCorso.current = tokenRinnovo;
    auth
      .signinSilent()
      .catch(() => {
        setFallitaPer(tokenRinnovo);
        return auth.removeUser();
      })
      .catch(() => undefined);
  }, [riprendibile, tokenRinnovo, auth]);

  return riprendibile;
}

export function SessioneKeycloak({
  children, ritorno2fa = "/profilo",
}: {
  children: React.ReactNode;
  /** Dove torna chi attiva la verifica in due passaggi: il profilo del sito, o quello della v2. */
  ritorno2fa?: string;
}) {
  const auth = useAuth();
  const riprendendo = useRipresaSessione(auth);
  const valore = useMemo<Sessione>(
    () => ({
      pronta: !auth.isLoading && !riprendendo,
      autenticata: auth.isAuthenticated,
      token: auth.user?.access_token ?? null,
      nome: auth.user?.profile?.given_name ?? auth.user?.profile?.name ?? null,
      admin: ruoliDaToken(auth.user?.access_token).includes("admin"),
      entra: (ritorno) =>
        auth.signinRedirect({ extraQueryParams: linguaPagina(), ...(ritorno ? { state: { ritorno } } : {}) }),
      /* La registrazione è la pagina di Keycloak, social compresi:
       * `prompt=create` apre direttamente il modulo invece del login. */
      registrati: () => auth.signinRedirect({ prompt: "create", extraQueryParams: linguaPagina() }),
      registratiPoi: (ritorno) => auth.signinRedirect({ prompt: "create", extraQueryParams: linguaPagina(), state: { ritorno } }),
      entraQui: (ritorno) =>
        auth.signinRedirect({
          redirect_uri: `${window.location.origin}${ritorno}`, extraQueryParams: linguaPagina(), state: { ritorno },
        }),
      /* «Application initiated action» di Keycloak: dopo l'accesso (o subito, se la
       * sessione è fresca) mostra la configurazione dell'OTP e poi torna qui. */
      attiva2fa: () =>
        auth.signinRedirect({
          extraQueryParams: { kc_action: "CONFIGURE_TOTP", ...linguaPagina() }, state: { ritorno: ritorno2fa },
        }),
      /* Il logout vero: prima si revoca il token offline (la chiusura della sessione del browser in Keycloak non
       * lo tocca: resterebbe valido, e chi lo avesse copiato resterebbe dentro), poi si chiude la sessione. Se la
       * revoca non riesce (rete) si esce comunque: meglio fuori con un token orfano che bloccati dentro. */
      esci: () => {
        void auth
          .revokeTokens(["refresh_token"])
          .catch(() => undefined)
          .then(() => auth.signoutRedirect())
          .catch(() => undefined);
      },
    }),
    [auth, riprendendo, ritorno2fa],
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
      registratiPoi: () => {},
      entraQui: () => {},
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
