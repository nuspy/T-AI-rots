"use client";

/* La lingua del menu e quella del profilo (v9, Fase 2d; regola rivista il 9/10 su decisione dell'operatore).
 *
 * **Un gesto vale ovunque.** Chi è dentro e cambia lingua (il codice in testata, il piede, il dialogo della prima
 * visita, l'offerta nella lettura) la cambia anche nel profilo (`PATCH /me/profile`, che segna `locale_scelta_il`):
 * oracolo, email e notifiche la seguono. Tutti questi gesti passano da `useCambiaLingua`.
 *
 * **All'accesso** (una volta per persona e per scheda):
 *  - il profilo ha una scelta (`locale_scelta_il`) → **vince l'account**, sempre, qualunque cosa ricordi questo
 *    browser: il sito passa alla lingua del profilo (interfaccia, cookie, indirizzo `/it`). L'account è la scelta
 *    esplicita della persona e vale ovunque — l'email del promemoria arriva in quella lingua — mentre la lingua di
 *    questo browser può essere quella di un computer in prestito;
 *  - l'account non ha mai scelto → la lingua in cui la persona stava leggendo prima di entrare va nel profilo: è la
 *    migliore che si sappia, meglio dell'«it» di ripiego con cui nasce un account senza lingua nel token.
 *
 * **Nessun ciclo.** Applicare la lingua del profilo non scrive nel profilo; scrivere nel profilo succede solo per un
 * gesto o una volta all'accesso. Nessun effetto osserva la lingua per scriverla.
 *
 * Le lingue del menu sono le quindici di `lib/i18n/lingue.ts`, le stesse che il profilo accetta (`tarot/lingue.py`:
 * lo controlla `test_lingua_profilo.py`). */

import { useCallback, useEffect, useRef } from "react";
import { usePathname, useRouter } from "next/navigation";
import { aggiornaProfilo, leggiProfilo } from "@/lib/api";
import { useSessione } from "@/lib/sessione";
import { comeLingua, type Lingua } from "@/v2/i18n";
import { conPrefissoIt, useLingua } from "./lingua";
import { dimenticaLinguaTraduzione } from "./lingua-traduzione";
import { R, indirizzoV2, senzaPrefisso } from "./percorsi";

const CHIAVE_IL = "lingua_il";
const CHIAVE_ALLINEATA = "lingua_allineata";

/** Una lingua è stata scelta: lo si ricorda con l'ora (serve a chi legge `lingua_il`, per esempio le app). */
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

/** Un indirizzo `/it/…` dice «italiano»: con un'altra lingua si va all'indirizzo inglese della stessa pagina, con
 *  l'italiano a quello italiano (`/cards/x` → `/it/carte/x`). Null se l'indirizzo va già bene. */
function indirizzoPer(lingua: Lingua, percorso: string, ricerca: string): string | null {
  const prefisso = conPrefissoIt(percorso);
  if (prefisso === (lingua === "it")) return null;
  return indirizzoV2(`${senzaPrefisso(percorso)}${ricerca}`, lingua === "it");
}

/** Il gesto «voglio il sito in questa lingua», uguale ovunque: interfaccia e cookie, l'ora della scelta, il profilo
 *  per chi è dentro, l'indirizzo `/it` da sistemare. La lingua delle traduzioni automatiche torna a seguire il sito. */
export function useCambiaLingua(): (l: Lingua) => void {
  const { imposta } = useLingua();
  const sessione = useSessione();
  const router = useRouter();
  const percorso = usePathname() ?? R.home;
  return useCallback((l: Lingua) => {
    imposta(l);
    segnaScelta();
    dimenticaLinguaTraduzione();
    if (sessione.autenticata) void salvaNelProfilo(sessione.token, l);
    const verso = indirizzoPer(l, percorso, window.location.search);
    if (verso) router.replace(verso);
  }, [imposta, sessione.autenticata, sessione.token, router, percorso]);
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
      if (profiloIl !== null && Number.isFinite(profiloIl) && delProfilo) {
        /* L'account ha scelto: vince lui. Anche a lingua uguale si scrive il cookie, così questo browser la ricorda
         * (e il dialogo della prima visita non si apre). */
        segnaScelta(profiloIl);
        imposta(delProfilo);
        const verso = indirizzoPer(delProfilo, window.location.pathname, window.location.search);
        if (verso) router.replace(verso);
      } else {
        /* L'account non ha mai scelto: gli va la lingua di prima dell'accesso. */
        await salvaNelProfilo(sessione.token, qui);
      }
    })();
    return () => { annullato = true; };
  }, [sessione.pronta, sessione.autenticata, sessione.token, imposta, router]);

  return null;
}
