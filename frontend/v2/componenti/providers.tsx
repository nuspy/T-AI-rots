"use client";

/* I provider della v2: accesso (lo stesso client Keycloak della v1, col ritorno alla radice), lingua v2,
 * sessione, analytics, e i pezzi globali (il dock del lettore, il banner dei cookie, il promemoria della 2FA).
 *
 * Il ritorno dell'accesso è la home: la pagina che riceve il codice deve essere una pagina della v2, perché è il suo
 * `AuthProvider` a riscattarlo (la v1 sotto `/old` ha il suo ritorno, `/old`). Il client Keycloak accetta ogni indirizzo del sito (`/*`). I token stanno
 * nello stesso `localStorage` del sito (stessa autorità, stesso client): chi è entrato di là è dentro anche qui.
 *
 * L'attribuzione delle condivisioni e il riscatto automatico degli inviti sono quelli del sito: non hanno testi né
 * collegamenti, solo una chiamata all'API alla prima sessione. Lo stesso per i dati dai social (`ImportaProfiloSocial`):
 * una chiamata dopo ogni accesso, che riempie solo i campi vuoti della scheda. */

import { useMemo } from "react";
import { AuthProvider } from "react-oidc-context";
import { WebStorageStateStore } from "oidc-client-ts";
import { AttribuzioneCondivisione } from "@/lib/attribuzione";
import { RiscattoInvitoAutomatico } from "@/lib/riscatto-invito";
import { SITE_URL } from "@/lib/condivisione";
import { AUTH_DISATTIVATA, SCOPE_PERSISTENTE, SessioneDiSviluppo, SessioneKeycloak } from "@/lib/sessione";
import { ProviderCarrello } from "@/v2/lib/carrello";
import { ProviderLinguaV2, type Lingua } from "@/v2/lib/lingua";
import { R } from "@/v2/lib/percorsi";
import { BannerCookieV2 } from "./banner-cookie";
import { ContatoreGoogle } from "./contatore-google";
import { DockLettore } from "./dock";
import { OsservatoreV2 } from "./osservatore";
import { PrivacyAccesso } from "./privacy-accesso";
import { ImportaProfiloSocial } from "./profilo-social";
import { FusoAutomatico } from "./notifiche";
import { Promemoria2faV2 } from "./promemoria-2fa";
import { ProviderPubblicita, type StatoInizialePubblicita } from "./pubblicita";
import { ConfermaUnione } from "./unione-account";

const authority = `${
  process.env.NEXT_PUBLIC_KEYCLOAK_URL ?? "http://localhost:8080"
}/realms/${process.env.NEXT_PUBLIC_KEYCLOAK_REALM ?? "tarots"}`;

/* Dopo l'accesso: via `code` e `state` dall'indirizzo, e di nuovo dove si era (una lettura a metà, il profilo).
 * Solo indirizzi del sito: un `ritorno` che porta fuori (un altro dominio, la v1 sotto `/old`) resta qui. */
function onSigninCallback(user: unknown): void {
  const stato = (user as { state?: { ritorno?: string } } | undefined)?.state;
  const r = stato?.ritorno;
  const dentro = typeof r === "string" && r.startsWith("/") && !r.startsWith("//") && !/^\/old(\/|\?|$)/.test(r);
  const qui = window.location.pathname;
  /* Un'altra pagina: la si carica davvero. Cambiare solo l'indirizzo (`replaceState`) lasciava sullo schermo la
   * pagina che ha ricevuto il codice (la home), con l'indirizzo di un'altra. I token sono già nel `localStorage`:
   * la pagina nuova parte con la sessione aperta. */
  if (dentro && r.split(/[?#]/)[0] !== qui) {
    window.location.replace(r);
    return;
  }
  /* La stessa pagina: si tolgono solo `code` e `state` dall'indirizzo, tenendo lo stato del router di Next. */
  window.history.replaceState(window.history.state, document.title, dentro ? r : qui);
}

const nelBrowser = typeof window !== "undefined";

export function ProvidersV2({
  children, linguaIniziale, pubblicita,
}: { children: React.ReactNode; linguaIniziale?: Lingua; pubblicita?: StatoInizialePubblicita }) {
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
            /* Login persistente fino al logout: token di rinnovo offline (vedi `SCOPE_PERSISTENTE`). */
            scope: SCOPE_PERSISTENTE,
            automaticSilentRenew: true,
            userStore: nelBrowser ? new WebStorageStateStore({ store: window.localStorage }) : undefined,
            onSigninCallback,
          },
    [],
  );

  const globali = (
    <OsservatoreV2>
      <ProviderPubblicita iniziale={pubblicita}>
        <ProviderCarrello>
          <DockLettore />
          <BannerCookieV2 />
          <PrivacyAccesso />
          <ContatoreGoogle />
          <FusoAutomatico />
          {children}
        </ProviderCarrello>
      </ProviderPubblicita>
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
          <ImportaProfiloSocial />
          <ConfermaUnione />
          {globali}
        </SessioneKeycloak>
      </ProviderLinguaV2>
    </AuthProvider>
  );
}
