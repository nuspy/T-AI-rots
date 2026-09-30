/* Gli analytics (v8, libreria `lanterna`): catalogo, interrogazioni dichiarate, imbuti, coorti.
 * La console compone interrogazioni con i nomi del catalogo; il server non accetta altro. */

import { API, chiamata, scaricaFile } from "./api";

export type Formato = "intero" | "decimale" | "euro" | "percento" | "secondi";

export interface VoceCatalogo {
  etichetta: string;
  descrizione: string;
}

export interface SorgenteCatalogo extends VoceCatalogo {
  proprieta: boolean;
  misure: Record<string, VoceCatalogo & { formato: Formato }>;
  dimensioni: Record<string, VoceCatalogo & { personale: boolean }>;
}

export interface Catalogo {
  sorgenti: Record<string, SorgenteCatalogo>;
  imbuti: Record<string, { etichetta: string; per: "sessione" | "utente"; passi: string[] }>;
  coorti: Record<string, { etichetta: string }>;
}

export type Operatore = "uguale" | "diverso" | "in" | "non_in" | "contiene" | "vuoto" | "non_vuoto";

export interface Filtro {
  dimensione: string;
  operatore: Operatore;
  valori: (string | number | boolean)[];
}

export interface Interrogazione {
  sorgente: string;
  misure: string[];
  dimensioni?: string[];
  filtri?: Filtro[];
  da: string;
  a: string;
  granularita?: "giorno" | "settimana" | "mese" | null;
  confronto?: "precedente" | "anno_prima" | null;
  ordine?: { campo: string; discendente: boolean } | null;
  limite?: number;
}

export interface Colonna {
  nome: string;
  etichetta: string;
  tipo: "periodo" | "dimensione" | "misura";
  formato?: Formato;
  personale?: boolean;
}

export type Riga = Record<string, string | number | null>;

export interface Risultato {
  colonne: Colonna[];
  righe: Riga[];
  totali: Record<string, number | null>;
  da: string;
  a: string;
  confronto: null | {
    tipo: string;
    da: string;
    a: string;
    righe: Riga[];
    totali: Record<string, number | null>;
    soppresse: number;
  };
  soppresse: number;
  troncato: boolean;
}

export interface PassoImbuto {
  evento: string;
  etichetta: string;
  n: number;
  dal_primo: number | null;
  dal_precedente: number | null;
}

export interface EsitoImbuto {
  imbuto: string;
  etichetta: string;
  per: "sessione" | "utente";
  da: string;
  a: string;
  passi: PassoImbuto[];
  segmenti: { valore: string; passi: PassoImbuto[] }[] | null;
}

export interface Coorte {
  coorte: string;
  dimensione: number;
  valori: number[];
}

export interface EsitoCoorti {
  tipo: string;
  etichetta: string;
  granularita: "settimana" | "mese";
  somma: boolean;
  coorti: Coorte[];
}

export const leggiCatalogo = (t: string) => chiamata<Catalogo>(t, "/admin/analytics/catalogo");

export const interroga = (t: string, q: Interrogazione) =>
  chiamata<Risultato>(t, "/admin/analytics/interroga", { method: "POST", body: JSON.stringify(q) });

export const calcolaImbuto = (
  t: string,
  r: { imbuto: string; da: string; a: string; entro_ore?: number | null; segmento?: string | null },
) => chiamata<EsitoImbuto>(t, "/admin/analytics/imbuto", { method: "POST", body: JSON.stringify(r) });

export const calcolaCoorti = (
  t: string,
  r: { tipo: string; granularita: "settimana" | "mese"; periodi: number; da?: string | null },
) => chiamata<EsitoCoorti>(t, "/admin/analytics/coorti", { method: "POST", body: JSON.stringify(r) });

/* ---- export (F5) ---- */

export const esportaVista = (t: string, q: Interrogazione, formato: "csv" | "xlsx") =>
  scaricaFile(t, `/admin/analytics/esporta?formato=${formato}`, { method: "POST", body: JSON.stringify(q) }, `vista.${formato}`);

export const esportaCollezione = (t: string, nome: string, giorni: number) =>
  scaricaFile(t, `/admin/analytics/collezioni/${nome}.xlsx?giorni=${giorni}`, {}, `${nome}.xlsx`);

/* ---- interpretazione AI (F6) ---- */

export interface VoceAnalisi {
  titolo?: string;
  testo: string;
  fatti: string[];
  verificato: boolean;
  numeri_non_trovati: number[];
  importanza?: "alta" | "media" | "bassa";
  confidenza?: "alta" | "media" | "bassa";
  verifica?: string;
  impatto?: "alto" | "medio" | "basso";
  sforzo?: "alto" | "medio" | "basso";
  metrica?: string;
}

export interface RispostaAnalisi {
  sintesi: string;
  sintesi_verificata: boolean;
  osservazioni: VoceAnalisi[];
  collegamenti: VoceAnalisi[];
  ipotesi: VoceAnalisi[];
  azioni: VoceAnalisi[];
  dati_mancanti: string[];
  avvertenze: string[];
  verifica: { voci: number; verificate: number; citazioni_inesistenti: number };
}

export interface Analisi {
  id: string;
  sezione: string;
  parametri: { giorni: number; da: string; a: string };
  fatti: { id: string; sezione: string; testo: string }[];
  risposta: RispostaAnalisi | null;
  errore: string | null;
  modello: string | null;
  durata_ms: number | null;
  giudizio: -1 | 1 | null;
  azione_adottata: string | null;
  creata_il: string;
}

export const analizza = (t: string, r: { sezione: string; giorni: number; vista?: Interrogazione }) =>
  chiamata<Analisi>(t, "/admin/analytics/analizza", { method: "POST", body: JSON.stringify(r) });

export const storicoAnalisi = (t: string, sezione?: string) =>
  chiamata<Analisi[]>(t, `/admin/analytics/analisi?limite=10${sezione ? `&sezione=${sezione}` : ""}`);

export const annotaAnalisi = (t: string, id: string, a: { giudizio?: -1 | 1 | null; azione_adottata?: string | null }) =>
  chiamata<Analisi>(t, `/admin/analytics/analisi/${id}`, { method: "PATCH", body: JSON.stringify(a) });

export const leggiImpostazioni = (t: string) => chiamata<{ contesto_ai: string }>(t, "/admin/analytics/impostazioni");

export const scriviImpostazioni = (t: string, contesto_ai: string) =>
  chiamata<{ contesto_ai: string }>(t, "/admin/analytics/impostazioni", { method: "PUT", body: JSON.stringify({ contesto_ai }) });

/* ---- rapporto settimanale (F7) ---- */

export interface StatoRapporto {
  smtp_configurato: boolean;
  opzioni: { ai: boolean; avvisi: boolean };
  prossima_settimana: { da: string; a: string };
  destinatari: { id: number; email: string; attivo: boolean }[];
  invii: {
    id: string; tipo: string; da: string; a: string; destinatari: string[]; riuscito: boolean;
    dettaglio: string | null; manuale: boolean; creato_il: string;
  }[];
}

export const statoRapporto = (t: string) => chiamata<StatoRapporto>(t, "/admin/analytics/rapporto");
export const aggiungiDestinatario = (t: string, email: string) =>
  chiamata<{ email: string }>(t, "/admin/analytics/rapporto/destinatari", { method: "POST", body: JSON.stringify({ email }) });
export const togliDestinatario = (t: string, id: number) =>
  chiamata<void>(t, `/admin/analytics/rapporto/destinatari/${id}`, { method: "DELETE" });
export const opzioniRapporto = (t: string, o: { ai: boolean; avvisi: boolean }) =>
  chiamata<{ ai: boolean; avvisi: boolean }>(t, "/admin/analytics/rapporto/opzioni", { method: "PUT", body: JSON.stringify(o) });
export const inviaRapporto = (t: string) =>
  chiamata<{ riuscito: boolean; dettaglio: string }>(t, "/admin/analytics/rapporto/invia", { method: "POST" });

/** L'HTML del rapporto (senza AI), da mostrare in un riquadro isolato. */
export async function anteprimaRapporto(t: string): Promise<string> {
  const risposta = await fetch(`${API}/admin/analytics/rapporto/anteprima`, {
    headers: t ? { Authorization: `Bearer ${t}` } : {},
  });
  if (!risposta.ok) throw new Error("Anteprima non disponibile.");
  return risposta.text();
}

/* ---- Colab (F8) ---- */

export interface Studi {
  collezioni: Record<string, string>;
  token: { id: string; nome: string; ambiti: string[]; scade_il: string; revocato_il: string | null; ultimo_uso: string | null }[];
  risultati: {
    id: string; titolo: string; descrizione: string | null; colonne: string[]; righe: unknown[][];
    totale_righe: number; creato_il: string;
  }[];
}

export const leggiStudi = (t: string) => chiamata<Studi>(t, "/admin/analytics/studi");
export const creaToken = (t: string, r: { nome: string; giorni: number; ambiti: string[] }) =>
  chiamata<{ token: string; id: string; scade_il: string }>(t, "/admin/analytics/studi/token", {
    method: "POST", body: JSON.stringify(r),
  });
export const revocaToken = (t: string, id: string) => chiamata<void>(t, `/admin/analytics/studi/token/${id}`, { method: "DELETE" });
export const togliRisultato = (t: string, id: string) =>
  chiamata<void>(t, `/admin/analytics/studi/risultati/${id}`, { method: "DELETE" });
export const scaricaNotebook = (t: string, collezione: string, giorni: number) =>
  scaricaFile(t, `/admin/analytics/studi/notebook.ipynb?collezione=${collezione}&giorni=${giorni}`, {}, `tarots-${collezione}.ipynb`);

/* ---- annotazioni, obiettivi, avvisi, tempo reale ---- */

export type TipoAnnotazione = "campagna" | "rilascio" | "contenuto" | "prezzo" | "esterno" | "altro";

export interface Annotazione {
  id: number;
  giorno: string;
  fine: string | null;
  tipo: TipoAnnotazione;
  titolo: string;
  nota: string | null;
}

export const elencaAnnotazioni = (t: string, da?: string, a?: string) =>
  chiamata<Annotazione[]>(t, `/admin/analytics/annotazioni${da && a ? `?da=${da}&a=${a}` : ""}`);
export const creaAnnotazione = (t: string, n: Omit<Annotazione, "id">) =>
  chiamata<Annotazione>(t, "/admin/analytics/annotazioni", { method: "POST", body: JSON.stringify(n) });
export const togliAnnotazione = (t: string, id: number) =>
  chiamata<void>(t, `/admin/analytics/annotazioni/${id}`, { method: "DELETE" });

export interface RisultatoObiettivo {
  id: number;
  nome: string;
  tipo: "evento" | "pagina";
  valore: string;
  proprieta: Record<string, string>;
  completamenti: number;
  sessioni: number;
  utenti: number;
  tasso: number | null;
  sessioni_totali: number;
  sessioni_prima: number | null;
  tasso_prima: number | null;
}

export const risultatiObiettivi = (t: string, giorni: number) =>
  chiamata<{ da: string; a: string; obiettivi: RisultatoObiettivo[] }>(t, `/admin/analytics/obiettivi?giorni=${giorni}`);
export const creaObiettivo = (t: string, o: { nome: string; tipo: "evento" | "pagina"; valore: string; proprieta: Record<string, string> }) =>
  chiamata<{ nome: string }>(t, "/admin/analytics/obiettivi", { method: "POST", body: JSON.stringify(o) });
export const togliObiettivo = (t: string, id: number) =>
  chiamata<void>(t, `/admin/analytics/obiettivi/${id}`, { method: "DELETE" });

export const controllaAvvisi = (t: string) =>
  chiamata<{ giorno: string; avvisi: { metrica: string; tipo: string; testo: string }[] }>(t, "/admin/analytics/avvisi");

export interface TempoReale {
  minuti: number;
  sessioni_attive: number;
  pagine: { valore: string; sessioni: number }[];
  canali: { valore: string; sessioni: number }[];
  paesi: { valore: string; sessioni: number }[];
  dispositivi: { valore: string; sessioni: number }[];
  pagine_per_minuto: { minuto: string; pagine: number }[];
}

export const tempoReale = (t: string) => chiamata<TempoReale>(t, "/admin/analytics/tempo-reale");
