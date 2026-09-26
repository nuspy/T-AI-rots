"use client";

/* La lingua dell'interfaccia, in quindici lingue.
 *
 * Un dizionario piccolo e non una libreria: le stringhe dell'interfaccia sono
 * poche decine (vedi `lib/i18n`), e i testi lunghi — domande dell'oracolo,
 * interpretazioni, responso, disclaimer — arrivano dal server già nella lingua
 * del quesito. La scelta si ricorda nel browser.
 *
 * Due lingue, non una: quella dell'INTERFACCIA (questa, scelta dal selettore) e
 * quella della LETTURA (quella del quesito, ricavata dal server e salvata con la
 * lettura). Dentro una lettura, i nomi di carte, stese e posizioni seguono la
 * seconda — sono il contenuto del dialogo con l'oracolo — e si leggono con
 * `useLinguaNomi()`. Ogni nuovo quesito la rinnova.
 */

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { usePathname } from "next/navigation";
import { impostaLinguaMessaggi } from "./api";
import {
  PREDEFINITA, TRADOTTE, comeLingua, datiLingua, dizionario, linguaDelBrowser,
  type Dizionario, type Lingua,
} from "./i18n";

import { risolvi } from "./percorsi";

export type { Chiave, Lingua } from "./i18n";
export { LINGUE, TRADOTTE } from "./i18n";

interface ContestoLingua {
  lingua: Lingua;
  imposta: (l: Lingua) => void;
  t: Dizionario;
  /* Il codice per le date e i numeri: «it-IT», «hu-HU»… */
  locale: string;
  /* Vero se la pagina va da destra a sinistra: lingua RTL con interfaccia tradotta. */
  rtl: boolean;
}

const Contesto = createContext<ContestoLingua | null>(null);

/* La lingua con cui mostrare i nomi di carte e stese: quella della lettura in
 * corso, se c'è; altrimenti quella dell'interfaccia. */
const ContestoNomi = createContext<Lingua | null>(null);

const CHIAVE = "lingua";

/* **Chi decide la lingua.**
 *
 * Nelle pagine pubbliche (soglia, carte, stese, mazzo, piano, blog) la decide l'indirizzo: `/it/…` è italiano, il
 * resto è inglese. È la stessa lingua con cui il server ha scritto la pagina, e quindi quella che un motore di
 * ricerca legge; il browser del visitatore non la cambia. Fa eccezione una lingua scelta a mano che non sia
 * italiano né inglese (per esempio l'ungherese): cambia le etichette dell'interfaccia, non il testo della pagina.
 *
 * Nelle pagine private (letture, profilo…) vale la scelta salvata, poi la lingua del browser, poi quella con cui
 * il server ha risposto. Le preferenze si leggono dopo il montaggio: sul server non c'è `localStorage`, e
 * leggerle durante il rendering darebbe due alberi diversi fra server e client. */
export function ProviderLingua({
  children, iniziale = PREDEFINITA,
}: {
  children: React.ReactNode;
  /** La lingua dell'indirizzo, letta sul server (`x-lang`): da qui parte il primo rendering. */
  iniziale?: Lingua;
}) {
  const percorso = usePathname() ?? "/";
  const url = useMemo(() => risolvi(percorso), [percorso]);
  const [salvata, setSalvata] = useState<Lingua | null>(null);
  const [rilevata, setRilevata] = useState<Lingua | null>(null);

  useEffect(() => {
    let scelta: Lingua | null = null;
    try {
      scelta = comeLingua(window.localStorage.getItem(CHIAVE));
    } catch {
      /* archiviazione non disponibile: si va sulle preferenze del browser */
    }
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setSalvata(scelta);
    setRilevata(linguaDelBrowser(navigator.languages?.length ? navigator.languages : [navigator.language]));
  }, []);

  const lingua: Lingua = useMemo(() => {
    if (url.pubblica) {
      return salvata && salvata !== "it" && salvata !== "en" ? salvata : url.lingua;
    }
    return salvata ?? rilevata ?? iniziale;
  }, [url, salvata, rilevata, iniziale]);

  const dati = datiLingua(lingua);
  /* Il verso della pagina segue la lingua SOLO se l'interfaccia è tradotta in
   * quella lingua: con il ripiego sull'inglese, specchiare la pagina darebbe
   * testo inglese con la punteggiatura dalla parte sbagliata. Il contenuto che
   * arriva dal server (domande, responso) sceglie il proprio verso da solo, con
   * `dir="auto"`. Aggiungendo `ar.ts` e mettendo `ar` in `TRADOTTE`, l'arabo
   * passa da destra a sinistra senza altro. */
  const rtl = dati.rtl && TRADOTTE.includes(lingua);

  useEffect(() => {
    document.documentElement.lang = lingua;
    document.documentElement.dir = rtl ? "rtl" : "ltr";
    impostaLinguaMessaggi(lingua);
  }, [lingua, rtl]);

  const imposta = useCallback((l: Lingua) => {
    setSalvata(l);
    try {
      window.localStorage.setItem(CHIAVE, l);
    } catch {
      /* pazienza: vale per questa visita */
    }
  }, []);

  const valore = useMemo(
    () => ({ lingua, imposta, t: dizionario(lingua), locale: dati.locale, rtl }),
    [lingua, imposta, dati.locale, rtl],
  );
  return <Contesto.Provider value={valore}>{children}</Contesto.Provider>;
}

export function useLingua(): ContestoLingua {
  const c = useContext(Contesto);
  if (!c) throw new Error("useLingua fuori dal provider");
  return c;
}

/** Dentro una lettura: i nomi seguono la lingua del quesito. */
export function LinguaNomi({ valore, children }: { valore: Lingua | null; children: React.ReactNode }) {
  return <ContestoNomi.Provider value={valore}>{children}</ContestoNomi.Provider>;
}

/** La lingua dei nomi di carte e stese: quella della lettura, o quella dell'interfaccia. */
export function useLinguaNomi(): Lingua {
  const interfaccia = useLingua().lingua;
  const lettura = useContext(ContestoNomi);
  return lettura ?? interfaccia;
}
