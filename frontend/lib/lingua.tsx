"use client";

/* Italiano e inglese.
 *
 * Un dizionario piccolo e non una libreria: le stringhe dell'interfaccia sono
 * poche decine, e i testi lunghi — interpretazioni, responso, disclaimer —
 * arrivano già nella lingua giusta dal server, che la riceve con la lettura.
 * La scelta si ricorda nel browser.
 */

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

export type Lingua = "it" | "en";

const TESTI = {
  it: {
    marchio: "T·AI·rots",
    motto: "L'oracolo del Tarocco di Thoth, letto da un'intelligenza artificiale.",
    nav_leggi: "Consulta",
    nav_letture: "Le mie letture",
    nav_giorno: "Carta del giorno",
    nav_carte: "Le carte",
    nav_piano: "Crediti",
    nav_profilo: "Profilo",
    entra: "Entra",
    registrati: "Registrati",
    esci: "Esci",
    verifica_sessione: "Verifica della sessione…",
    serve_account: "Serve un account per consultare le carte.",
    inizia: "Inizia la consultazione",
    scegli_stesa: "Scegli la stesa",
    la_tua_domanda: "La tua domanda",
    domanda_segnaposto: "Scrivi ciò che vuoi chiedere alle carte: una domanda, un dubbio, o anche solo «cosa mi riserva il futuro?»",
    maggiori: "22 Arcani maggiori",
    completo: "78 carte",
    carte: "carte",
    accetto: "Ho capito, procediamo",
    disclaimer_titolo: "Prima di cominciare",
    oracolo: "L'oracolo",
    tu: "Tu",
    rispondi: "Rispondi",
    risposta_segnaposto: "Scrivi la tua risposta…",
    mescola: "Mescola le carte",
    mescolando: "Le carte si mescolano…",
    scegli_n: (n: number) => (n === 1 ? "Scegli l'ultima carta" : `Scegli ancora ${n} carte`),
    tocca_per_rivelare: "Tocca la carta che brilla per rivelarla",
    rivela: "Rivela",
    responso: "Ricevi il responso",
    fase_unione: "Le carte si parlano: sto unendo domanda, colloquio e stesa…",
    fase_guardia: "Il guardiano verifica il responso…",
    fase_revisione: "Il responso viene rivisto con maggiore cura…",
    il_responso: "Il responso",
    nuova_lettura: "Nuova lettura",
    condividi: "Condividi",
    scarica_immagine: "Scarica l'immagine",
    link_copiato: "Link copiato",
    crediti: "crediti",
    credito: "credito",
    compra: "Acquista crediti",
    crediti_finiti: "Hai esaurito i crediti",
    crediti_finiti_testo: "Ogni consultazione usa un credito, oppure una delle letture giornaliere del tuo abbonamento. Scegli un pacchetto o un abbonamento per continuare.",
    chiudi: "Chiudi",
    dritta: "dritta",
    rovesciata: "rovesciata",
    dignita: "Dignità",
    doppia_valenza: "Doppia valenza",
    sintesi_calcolata: "Sintesi calcolata",
    verifica_mazzo: "Verifica del mazzo",
    verifica_testo: "Le carte erano fissate prima della tua scelta. Hash del mazzo:",
    si: "Sì",
    in_parte: "In parte",
    no: "No",
    si_e_avverato: "Si è avverato?",
    cancella: "Cancella",
    conferma_cancella: "Cancellare definitivamente questa lettura?",
    nessuna_lettura: "Nessuna lettura ancora. Le carte aspettano la tua prima domanda.",
    lingua: "English",
  },
  en: {
    marchio: "T·AI·rots",
    motto: "The oracle of the Thoth Tarot, read by an artificial intelligence.",
    nav_leggi: "Consult",
    nav_letture: "My readings",
    nav_giorno: "Card of the day",
    nav_carte: "The cards",
    nav_piano: "Credits",
    nav_profilo: "Profile",
    entra: "Sign in",
    registrati: "Sign up",
    esci: "Sign out",
    verifica_sessione: "Checking your session…",
    serve_account: "You need an account to consult the cards.",
    inizia: "Begin the reading",
    scegli_stesa: "Choose the spread",
    la_tua_domanda: "Your question",
    domanda_segnaposto: "Write what you want to ask the cards: a question, a doubt, or simply «what does the future hold?»",
    maggiori: "22 Major Arcana",
    completo: "78 cards",
    carte: "cards",
    accetto: "I understand, let's begin",
    disclaimer_titolo: "Before we begin",
    oracolo: "The oracle",
    tu: "You",
    rispondi: "Answer",
    risposta_segnaposto: "Write your answer…",
    mescola: "Shuffle the cards",
    mescolando: "The cards are being shuffled…",
    scegli_n: (n: number) => (n === 1 ? "Choose the last card" : `Choose ${n} more cards`),
    tocca_per_rivelare: "Touch the glowing card to reveal it",
    rivela: "Reveal",
    responso: "Receive the answer",
    fase_unione: "The cards speak to each other: joining question, interview and spread…",
    fase_guardia: "The guardian is checking the answer…",
    fase_revisione: "The answer is being revised with greater care…",
    il_responso: "The answer",
    nuova_lettura: "New reading",
    condividi: "Share",
    scarica_immagine: "Download image",
    link_copiato: "Link copied",
    crediti: "credits",
    credito: "credit",
    compra: "Buy credits",
    crediti_finiti: "You are out of credits",
    crediti_finiti_testo: "Each consultation uses one credit, or one of your subscription's daily readings. Choose a pack or a subscription to continue.",
    chiudi: "Close",
    dritta: "upright",
    rovesciata: "reversed",
    dignita: "Dignity",
    doppia_valenza: "Double value",
    sintesi_calcolata: "Computed synthesis",
    verifica_mazzo: "Deck verification",
    verifica_testo: "The cards were fixed before your choice. Deck hash:",
    si: "Yes",
    in_parte: "Partly",
    no: "No",
    si_e_avverato: "Did it come true?",
    cancella: "Delete",
    conferma_cancella: "Permanently delete this reading?",
    nessuna_lettura: "No readings yet. The cards are waiting for your first question.",
    lingua: "Italiano",
  },
} as const;

export type Chiave = keyof (typeof TESTI)["it"];

interface ContestoLingua {
  lingua: Lingua;
  cambia: () => void;
  t: typeof TESTI["it"];
}

const Contesto = createContext<ContestoLingua | null>(null);

export function ProviderLingua({ children }: { children: React.ReactNode }) {
  const [lingua, setLingua] = useState<Lingua>("it");

  useEffect(() => {
    /* Letta dopo il montaggio: sul server non c'è `localStorage`, e leggerla
     * durante il rendering darebbe due alberi diversi fra server e client. */
    try {
      const salvata = window.localStorage.getItem("lingua");
      const scelta: Lingua | null =
        salvata === "en" || salvata === "it"
          ? salvata
          : navigator.language.startsWith("it") ? null : "en";
      // eslint-disable-next-line react-hooks/set-state-in-effect
      if (scelta) setLingua(scelta);
    } catch {
      /* archiviazione non disponibile: resta l'italiano */
    }
  }, []);

  useEffect(() => {
    document.documentElement.lang = lingua;
  }, [lingua]);

  const cambia = useCallback(() => {
    setLingua((l) => {
      const nuova = l === "it" ? "en" : "it";
      try {
        window.localStorage.setItem("lingua", nuova);
      } catch {
        /* pazienza: vale per questa visita */
      }
      return nuova;
    });
  }, []);

  const valore = useMemo(
    () => ({ lingua, cambia, t: TESTI[lingua] as typeof TESTI["it"] }),
    [lingua, cambia],
  );
  return <Contesto.Provider value={valore}>{children}</Contesto.Provider>;
}

export function useLingua(): ContestoLingua {
  const c = useContext(Contesto);
  if (!c) throw new Error("useLingua fuori dal provider");
  return c;
}
