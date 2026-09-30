"use client";

/* I provider della v2: accesso (lo stesso client Keycloak della v1, col ritorno alla radice), lingua v2,
 * sessione, analytics, e i pezzi globali (il dock del lettore, il banner dei cookie, il promemoria della 2FA).
 *
 * Il ritorno dell'accesso è la home: la pagina che riceve il codice deve essere una pagina della v2, perché è il suo
 * `AuthProvider` a riscattarlo (la v1 sotto `/old` ha il suo ritorno, `/old`). Il client Keycloak accetta ogni indirizzo del sito (`/*`). I token stanno
 * nello stesso `localStorage` del sito (stessa autorità, stesso client): chi è entrato di là è dentro anche qui.
 *
 * L'attribuzione delle condivisioni e il riscatto automatico degli inviti sono quelli del sito: non hanno testi né
 * collegamenti, solo una chiamata all'API alla prima sessione. */

import { useMemo } from "react";
import { AuthProvider } from "react-oidc-context";
import { WebStorageStateStore } from "oidc-client-ts";
import { AttribuzioneCondivisione } from "@/lib/attribuzione";
import { RiscattoInvitoAutomatico } from "@/lib/riscatto-invito";
import { SITE_URL } from "@/lib/condivisione";
import { AUTH_DISATTIVATA, SessioneDiSviluppo, SessioneKeycloak } from "@/lib/sessione";
import { ProviderCarrello } from "@/v2/lib/carrello";
import { ProviderLinguaV2, type Lingua } from "@/v2/lib/lingua";
import { R } from "@/v2/lib/percorsi";
import { BannerCookieV2 } from "./banner-cookie";
import { DockLettore } from "./dock";
import { OsservatoreV2 } from "./osservatore";
import { Promemoria2faV2 } from "./promemoria-2fa";

const authority = `${
  process.env.NEXT_PUBLIC_KEYCLOAK_URL ?? "http://localhost:8080"
}/realms/${process.env.NEXT_PUBLIC_KEYCLOAK_REALM ?? "tarots"}`;

/* Dopo l'accesso: via `code` e `state` dall'indirizzo, e di nuovo dove si era (una lettura a metà, il profilo).
 * Solo indirizzi del sito: un `ritorno` che porta fuori (un altro dominio, la v1 sotto `/old`) resta qui. */
function onSigninCallback(user: unknown): void {
  const stato = (user as { state?: { ritorno?: string } } | undefined)?.state;
  const r = stato?.ritorno;
  const dentro = typeof r === "string" && r.startsWith("/") && !r.startsWith("//") && !/^\/old(\/|\?|$)/.test(r);
  window.history.replaceState({}, document.title, dentro ? r : window.location.pathname);
}

const nelBrowser = typeof window !== "undefined";

export function ProvidersV2({ children, linguaIniziale }: { children: React.ReactNode; linguaIniziale?: Lingua }) {
  const config = useMemo(
    () =>
      AUTH_DISATTIVATA
        ? null
        : {
            authority,
            client_id: process.env.NEXT_PUBLIC_KEYCLOAK_CLIENT_ID ?? "tarot-frontend",
            redirect_uri: nelBrowser ? `${window.location.origin}${R.home}` : `${SITE_URL}${R.home}`,
            post_logout_redirect_uri: nelBrowser ? `${window.location.origin}${R.home}` : `${SITE_URL}${R.home}`,
            response_type: "code",
            scope: "openid profile email",
            automaticSilentRenew: true,
            userStore: nelBrowser ? new WebStorageStateStore({ store: window.localStorage }) : undefined,
            onSigninCallback,
          },
    [],
  );

  const globali = (
    <OsservatoreV2>
      <ProviderCarrello>
        <DockLettore />
        <BannerCookieV2 />
        {children}
      </ProviderCarrello>
    </OsservatoreV2>
  );

  if (!config) {
    return (
      <ProviderLinguaV2 iniziale={linguaIniziale}>
        <SessioneDiSviluppo>{globali}</SessioneDiSviluppo>
      </ProviderLinguaV2>
    );
  }

  return (
    <AuthProvider {...config}>
      <ProviderLinguaV2 iniziale={linguaIniziale}>
        <SessioneKeycloak ritorno2fa={R.profilo}>
          <AttribuzioneCondivisione />
          <RiscattoInvitoAutomatico />
          <Promemoria2faV2 />
          {globali}
        </SessioneKeycloak>
      </ProviderLinguaV2>
    </AuthProvider>
  );
}
