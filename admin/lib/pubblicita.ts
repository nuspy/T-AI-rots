/* La pubblicità (Advertisements): le impostazioni generali degli spazi e i fornitori (oggi solo Google AdSense).
 *
 * Il modello è aperto per fornitore: `fornitori` è un dizionario per chiave, e un fornitore nuovo (affiliazioni, spazi
 * venduti direttamente) arriva come una chiave in più, con il suo sotto-tab nella console. */

import { chiamata } from "./api";

export type Posizione = "terzo" | "due_terzi" | "fine";
export type Formato = "auto" | "rectangle" | "horizontal" | "vertical";
export type StatoRegistrazione = "non_iniziata" | "ads_txt_verificato" | "in_revisione" | "approvato" | "rifiutato";

export const POSIZIONI: Posizione[] = ["terzo", "due_terzi", "fine"];

export const NOMI_POSIZIONE: Record<Posizione, string> = {
  terzo: "A un terzo",
  due_terzi: "A due terzi",
  fine: "Alla fine",
};

export const NOMI_FORMATO: Record<Formato, string> = {
  auto: "Automatico (consigliato)",
  rectangle: "Rettangolo",
  horizontal: "Orizzontale (banner)",
  vertical: "Verticale",
};

export const NOMI_STATO: Record<StatoRegistrazione, string> = {
  non_iniziata: "Non iniziata",
  ads_txt_verificato: "ads.txt verificato",
  in_revisione: "In revisione da Google",
  approvato: "Approvato",
  rifiutato: "Rifiutato",
};

export interface Generale {
  attiva: boolean;
  fornitore: string;
  posizioni: Record<Posizione, boolean>;
  pagine_escluse: string[];
}

export interface ParametriGoogle {
  editore: string;
  slot: Record<Posizione, string>;
  formato: Record<Posizione, Formato>;
  responsive: boolean;
  prova: boolean;
  personalizzati: boolean;
}

export interface RegistrazioneGoogle {
  email: string;
  titolare: string;
  id_cliente: string;
  /** `AAAA-MM-GG` o `null`. */
  data_iscrizione: string | null;
  stato: StatoRegistrazione;
  note: string;
}

export type TipoProfilo = "individuale" | "azienda";
export type MetodoPagamento = "bonifico" | "bonifico_internazionale" | "altro";
export type StatoFiscale = "non_inviate" | "inviate" | "accettate";
export type ModuloFiscale = "W-8BEN" | "W-8BEN-E" | "W-9" | "altro";
export type StatoPin = "non_ricevuto" | "ricevuto" | "verificato";

export const NOMI_TIPO_PROFILO: Record<TipoProfilo, string> = { individuale: "Individuale", azienda: "Azienda" };
export const NOMI_METODO: Record<MetodoPagamento, string> = {
  bonifico: "Bonifico (EFT/SEPA)",
  bonifico_internazionale: "Bonifico internazionale (wire)",
  altro: "Altro",
};
export const NOMI_STATO_FISCALE: Record<StatoFiscale, string> = {
  non_inviate: "Non inviate",
  inviate: "Inviate",
  accettate: "Accettate",
};
export const NOMI_MODULO: Record<ModuloFiscale, string> = {
  "W-8BEN": "W-8BEN (persona fuori dagli USA)",
  "W-8BEN-E": "W-8BEN-E (azienda fuori dagli USA)",
  "W-9": "W-9 (soggetto USA)",
  altro: "Altro",
};
export const NOMI_STATO_PIN: Record<StatoPin, string> = {
  non_ricevuto: "Non ancora ricevuto",
  ricevuto: "Ricevuto, da inserire",
  verificato: "Verificato",
};

/** Il profilo pagamenti di AdSense come appunti della console: il profilo vero sta in AdSense, e del conto si tengono
 *  solo le ultime 4 cifre. Il sito non riceve nulla di questo. */
export interface PagamentiGoogle {
  id_profilo: string;
  beneficiario: string;
  tipo_profilo: TipoProfilo;
  indirizzo: string;
  metodo: MetodoPagamento;
  banca: string;
  conto_ultime4: string;
  soglia: number | null;
  valuta: string;
  stato_fiscale: StatoFiscale;
  modulo_fiscale: ModuloFiscale;
  stato_pin: StatoPin;
  /** `AAAA-MM-GG` o `null`. */
  ultimo_pagamento: string | null;
  note: string;
}

/** Come `pagamenti_predefiniti()` del backend: la pagina parte da qui se la risposta non li porta (API più vecchia). */
export const PAGAMENTI_VUOTI: PagamentiGoogle = {
  id_profilo: "", beneficiario: "", tipo_profilo: "individuale", indirizzo: "", metodo: "bonifico", banca: "",
  conto_ultime4: "", soglia: null, valuta: "EUR", stato_fiscale: "non_inviate", modulo_fiscale: "W-8BEN",
  stato_pin: "non_ricevuto", ultimo_pagamento: null, note: "",
};

export interface FornitoreGoogle {
  etichetta: string;
  parametri: ParametriGoogle;
  registrazione: RegistrazioneGoogle;
  pagamenti: PagamentiGoogle;
  /** C'è un ID editore valido: la pubblicità si può accendere. */
  pronto: boolean;
  /** Il contenuto di `ads.txt` che il sito serve adesso, o `null`. */
  ads_txt: string | null;
}

/** Ciò che il sito riceve adesso (`/impostazioni-pubblicita`): per l'anteprima. */
export interface VistaPubblica {
  attiva: boolean;
  posizioni?: Partial<Record<Posizione, { slot: string; formato: Formato }>>;
}

export interface StatoPubblicita {
  generale: Generale;
  fornitori: { google: FornitoreGoogle };
  catalogo: { fornitori: { chiave: string; etichetta: string }[] };
  pubblico: VistaPubblica;
}

export const statoPubblicita = (t: string) => chiamata<StatoPubblicita>(t, "/admin/pubblicita");

export const salvaGenerale = (t: string, corpo: Partial<Generale>) =>
  chiamata<StatoPubblicita>(t, "/admin/pubblicita", { method: "PUT", body: JSON.stringify(corpo) });

export const salvaGoogle = (
  t: string,
  corpo: { parametri?: Partial<ParametriGoogle>; registrazione?: Partial<RegistrazioneGoogle> },
) => chiamata<StatoPubblicita>(t, "/admin/pubblicita/fornitori/google", { method: "PUT", body: JSON.stringify(corpo) });

export const salvaPagamentiGoogle = (t: string, corpo: Partial<PagamentiGoogle>) =>
  chiamata<StatoPubblicita>(t, "/admin/pubblicita/fornitori/google/pagamenti", {
    method: "PUT",
    body: JSON.stringify(corpo),
  });
