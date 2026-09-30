"use client";

/* La lingua della v2: stesse quindici lingue del sito, dizionario suo (`v2/i18n`).
 *
 * Chi decide la lingua, nell'ordine:
 *  1. l'indirizzo, se comincia con `/it/v2`: è italiano (salvo una scelta salvata che non sia né italiano né
 *     inglese, per esempio l'ungherese — come nel sito);
 *  2. la scelta salvata nel browser (la chiave `lingua`, la stessa del sito: chi l'ha scelta di là la ritrova);
 *  3. la lingua del browser;
 *  4. quella con cui il server ha scritto la pagina.
 * Le preferenze si leggono dopo il montaggio: sul server non ci sono, e leggerle durante il rendering darebbe due
 * alberi diversi fra server e browser.
 *
 * La lingua della LETTURA è un'altra cosa (quella del quesito, decisa dal server): dentro una lettura i nomi di
 * carte e stese la seguono, con `LinguaNomi`/`useLinguaNomi`, come nel sito. */

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { usePathname } from "next/navigation";
import { impostaLinguaMessaggi, impostaMessaggiErrore } from "@/lib/api";
import {
  PREDEFINITA, TRADOTTE, caricaDizionario, comeLingua, datiLingua, dizionarioPronto, linguaDelBrowser,
  type Dizionario, type Lingua,
} from "@/v2/i18n";

export type { Dizionario, Lingua };

interface ContestoLingua {
  lingua: Lingua;
  imposta: (l: Lingua) => void;
  t: Dizionario;
  /** Il codice per date e numeri: «it-IT», «hu-HU»… */
  locale: string;
  rtl: boolean;
  /** Vero se l'indirizzo porta il prefisso `/it`: i collegamenti lo conservano. */
  prefissoIt: boolean;
}

const Contesto = createContext<ContestoLingua | null>(null);
const ContestoNomi = createContext<Lingua | null>(null);
const CHIAVE = "lingua";

export const conPrefissoIt = (percorso: string) => percorso === "/it" || percorso.startsWith("/it/");

export function ProviderLinguaV2({ children, iniziale = PREDEFINITA }: { children: React.ReactNode; iniziale?: Lingua }) {
  const percorso = usePathname() ?? "/v2";
  const prefissoIt = conPrefissoIt(percorso);
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
    if (prefissoIt) return salvata && salvata !== "it" && salvata !== "en" ? salvata : "it";
    return salvata ?? rilevata ?? iniziale;
  }, [prefissoIt, salvata, rilevata, iniziale]);

  /* Inglese e italiano sono già nel pacchetto; le altre lingue arrivano con un'importazione: fino ad allora si
   * vede l'inglese (come prima della traduzione), mai una pagina vuota. */
  const [caricato, setCaricato] = useState<{ lingua: Lingua; d: Dizionario } | null>(null);
  useEffect(() => {
    if (dizionarioPronto(lingua)) return;
    let annullato = false;
    void caricaDizionario(lingua).then((d) => { if (!annullato) setCaricato({ lingua, d }); });
    return () => { annullato = true; };
  }, [lingua]);
  const t: Dizionario =
    dizionarioPronto(lingua) ?? (caricato?.lingua === lingua ? caricato.d : dizionarioPronto("en")!);

  const dati = datiLingua(lingua);
  /* Il verso della pagina segue la lingua solo se l'interfaccia è tradotta in quella lingua (come nel sito). */
  const rtl = dati.rtl && TRADOTTE.includes(lingua);

  useEffect(() => {
    document.documentElement.lang = lingua;
    document.documentElement.dir = rtl ? "rtl" : "ltr";
    impostaLinguaMessaggi(lingua);
    impostaMessaggiErrore({ sessione: t.comune.err_sessione, richiesta: t.comune.err_richiesta });
  }, [lingua, rtl, t]);

  const imposta = useCallback((l: Lingua) => {
    setSalvata(l);
    try {
      window.localStorage.setItem(CHIAVE, l);
    } catch {
      /* vale per questa visita */
    }
  }, []);

  const valore = useMemo(
    () => ({ lingua, imposta, t, locale: dati.locale, rtl, prefissoIt }),
    [lingua, imposta, t, dati.locale, rtl, prefissoIt],
  );
  return <Contesto.Provider value={valore}>{children}</Contesto.Provider>;
}

export function useLingua(): ContestoLingua {
  const c = useContext(Contesto);
  if (!c) throw new Error("useLingua (v2) fuori dal provider");
  return c;
}

/** Dentro una lettura: i nomi di carte e stese seguono la lingua del quesito. */
export function LinguaNomi({ valore, children }: { valore: Lingua | null; children: React.ReactNode }) {
  return <ContestoNomi.Provider value={valore}>{children}</ContestoNomi.Provider>;
}

export function useLinguaNomi(): Lingua {
  const interfaccia = useLingua().lingua;
  return useContext(ContestoNomi) ?? interfaccia;
}
