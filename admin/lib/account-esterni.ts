/* «Account» (v9, Fase 3): i servizi esterni che chiedono un account, con stato, passi, primo link e dove sta il
 * segreto. Il registro sta nel backend (`servizi_esterni/registro.py`); le impostazioni restano nelle sezioni. */

import { chiamata } from "./api";

export type StatoServizio = "errore" | "da_configurare" | "configurato" | "verificato" | "manuale" | "non_usato";

export const NOMI_STATO: Record<StatoServizio, string> = {
  errore: "Errore",
  da_configurare: "Da configurare",
  configurato: "Configurato",
  verificato: "Verificato",
  manuale: "Fuori dal sito",
  non_usato: "Non usato",
};

/** Il segno accanto alla parola: lo stato non si legge dal solo colore. */
export const SEGNO_STATO: Record<StatoServizio, string> = {
  errore: "✗",
  da_configurare: "○",
  configurato: "◐",
  verificato: "✓",
  manuale: "↗",
  non_usato: "–",
};

export interface ServizioEsterno {
  id: string;
  nome: string;
  categoria: string;
  /** La pagina della console dove si imposta, o `null` se vive fuori dalla console. */
  sezione: string | null;
  stato: StatoServizio;
  dettaglio: string;
  come_fare: string[];
  /** Solo il primo indirizzo della procedura del fornitore. */
  primo_link: string | null;
  dove_sta_il_segreto: string;
  costi: string;
  verificabile: boolean;
  fase: string | null;
  nota: string;
  /** Dove si imposta (v9, Fase 2c): in console (`sezione`), sul server (solo i tre segreti che restano lì), dal
   *  fornitore (fuori dal sito) o in automatico. */
  dove: DoveSiImposta;
  dove_testo: string;
}

export type DoveSiImposta = "console" | "server" | "fornitore" | "automatico";

export const SEGNO_DOVE: Record<DoveSiImposta, string> = {
  console: "⚙",
  server: "▣",
  fornitore: "↗",
  automatico: "↻",
};

export interface ElencoServizi {
  servizi: ServizioEsterno[];
  categorie: string[];
  stati: StatoServizio[];
  riepilogo: Record<StatoServizio, number>;
}

export interface EsitoVerificaServizio {
  servizio: ServizioEsterno;
  esito: { stato: StatoServizio; dettaglio: string };
}

export const elencoServizi = (t: string) => chiamata<ElencoServizi>(t, "/admin/account-esterni");

export const verificaServizio = (t: string, id: string) =>
  chiamata<EsitoVerificaServizio>(t, `/admin/account-esterni/${encodeURIComponent(id)}/verifica`, { method: "POST" });
