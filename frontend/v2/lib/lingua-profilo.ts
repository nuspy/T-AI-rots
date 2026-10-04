"use client";

/* La lingua del menu e quella del profilo (v9, Fase 2d: decisione dell'operatore).
 *
 * **Vince l'ultima scelta.** Chi è dentro e cambia lingua dal menu la cambia anche nel profilo (`PATCH /me/profile`,
 * che segna `locale_scelta_il`): oracolo, email e notifiche la seguono. Il browser ricorda quando l'ha scelta
 * (`lingua_il`), il server pure.
 *
 * **All'accesso** (una volta per persona e per scheda) si confrontano le due scelte:
 *  - una scelta fatta qui più recente di quella del profilo (per esempio dal menu prima di entrare, o su questo
 *    dispositivo) → va nel profilo;
 *  - se no, se il profilo ha una scelta → **vince il profilo**: il sito passa alla lingua del profilo. È la proposta
 *    dell'operatore, ed è la regola giusta perché il profilo è la scelta esplicita della persona e vale ovunque —
 *    l'email del promemoria arriva in quella lingua — mentre la lingua di questo browser può essere solo quella di
 *    sistema di un computer in prestito;
 *  - nessuna delle due ha mai scelto → la lingua in cui la persona sta leggendo (quella del browser) va nel profilo:
 *    è la migliore che si sappia, meglio dell'«it» di ripiego con cui nasce un account senza lingua nel token.
 *
 * **Nessun ciclo.** Applicare la lingua del profilo non scrive nel profilo; scrivere nel profilo succede solo per un
 * gesto (il menu) o una volta all'accesso. Nessun effetto osserva la lingua per scriverla.
 *
 * Le lingue del menu sono le quindici di `lib/i18n/lingue.ts`, le stesse che il profilo accetta (`tarot/lingue.py`:
 * lo controlla `test_lingua_profilo.py`). */

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { aggiornaProfilo, leggiProfilo } from "@/lib/api";
import { useSessione } from "@/lib/sessione";
import { comeLingua, type Lingua } from "@/v2/i18n";
import { conPrefissoIt, useLingua } from "./lingua";
import { indirizzoV2, senzaPrefisso } from "./percorsi";

const CHIAVE_IL = "lingua_il";
const CHIAVE_ALLINEATA = "lingua_allineata";

function leggiNumero(chiave: string): number | null {
  try {
    const v = Number(window.localStorage.getItem(chiave));
    return Number.isFinite(v) && v > 0 ? v : null;
  } catch {
    return null;
  }
}

/** Il menu (o il profilo) ha scelto una lingua: lo si ricorda con l'ora, per il confronto all'accesso. */
export function segnaScelta(quando: number = Date.now()) {
  try {
    window.localStorage.setItem(CHIAVE_IL, String(quando));
  } catch {
    /* vale per questa visita */
  }
}

/** Scrive la lingua nel profilo. Mai un errore visibile: il menu ha già cambiato l'interfaccia, e il profilo si
 *  riallinea al prossimo accesso. */
export async function salvaNelProfilo(token: string | null, lingua: Lingua): Promise<void> {
  try {
    const p = await aggiornaProfilo(token, { locale: lingua });
    const il = p.locale_scelta_il ? Date.parse(p.locale_scelta_il) : NaN;
    if (Number.isFinite(il)) segnaScelta(il);
  } catch {
    /* rete o sessione: riprova il prossimo accesso */
  }
}

function soggetto(token: string | null): string {
  if (!token) return "sviluppo";
  try {
    const corpo = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    return String(JSON.parse(atob(corpo)).sub ?? "");
  } catch {
    return "";
  }
}

/** L'allineamento all'accesso, da montare una volta (nella testata). */
export function SincroniaLinguaProfilo() {
  const sessione = useSessione();
  const router = useRouter();
  const { lingua, imposta } = useLingua();
  // La lingua si legge dopo il caricamento del profilo: intanto il provider ha letto le preferenze del browser.
  const attuale = useRef(lingua);
  useEffect(() => { attuale.current = lingua; }, [lingua]);

  useEffect(() => {
    if (!sessione.pronta || !sessione.autenticata) return;
    const chi = soggetto(sessione.token);
    try {
      if (window.sessionStorage.getItem(CHIAVE_ALLINEATA) === chi) return;
    } catch {
      /* senza archivio si allinea a ogni montaggio: è idempotente */
    }
    let annullato = false;
    void (async () => {
      let profilo;
      try {
        profilo = await leggiProfilo(sessione.token);
      } catch {
        return;
      }
      if (annullato) return;
      try {
        window.sessionStorage.setItem(CHIAVE_ALLINEATA, chi);
      } catch {
        /* idem */
      }
      const delProfilo = comeLingua(profilo.locale);
      const qui = attuale.current;
      const profiloIl = profilo.locale_scelta_il ? Date.parse(profilo.locale_scelta_il) : null;
      const localeIl = leggiNumero(CHIAVE_IL);
      if (localeIl !== null && (profiloIl === null || localeIl > profiloIl)) {
        if (delProfilo !== qui) await salvaNelProfilo(sessione.token, qui);
      } else if (profiloIl !== null && delProfilo) {
        segnaScelta(profiloIl);
        if (delProfilo !== qui) {
          imposta(delProfilo);
          // Come il menu: un indirizzo `/it/…` dice «italiano», gli altri sono inglesi o neutri.
          const percorso = window.location.pathname;
          const prefisso = conPrefissoIt(percorso);
          const verso = `${senzaPrefisso(percorso)}${window.location.search}`;
          if (prefisso !== (delProfilo === "it")) router.replace(indirizzoV2(verso, delProfilo === "it"));
        }
      } else if (delProfilo !== qui) {
        await salvaNelProfilo(sessione.token, qui);
      }
    })();
    return () => { annullato = true; };
  }, [sessione.pronta, sessione.autenticata, sessione.token, imposta, router]);

  return null;
}
