/* Il backup del database sul NAS (v8.3): destinazione, prova del collegamento, backup subito, copie sul NAS, storico
 * e ripristino. La credenziale del NAS non passa mai di qui: sta in un Secret (vedi deploy/k8s/LEGGIMI.md). */

import { chiamata } from "./api";

export interface ImpostazioniBackup {
  attivo: boolean;
  host: string;
  porta: number;
  utente: string;
  cartella: string;
  conserva: number;
  impronta_host: string | null;
}

export interface EsecuzioneBackup {
  id: string;
  tipo: "backup" | "sicurezza" | "ripristino" | "prova";
  manuale: boolean;
  esito: "in_corso" | "ok" | "errore" | "saltato";
  file: string | null;
  byte: number | null;
  sha256: string | null;
  durata_secondi: number | null;
  eliminati: string[];
  dettaglio: string | null;
  avviata_il: string | null;
  finita_il: string | null;
}

export interface StatoRipristino {
  in_corso: boolean;
  fase: string;
  file: string | null;
  esito: "ok" | "errore" | null;
  dettaglio: string | null;
  passi: string[];
  iniziato: string | null;
  finito: string | null;
}

export interface StatoBackup {
  impostazioni: ImpostazioniBackup;
  credenziale: { chiave_ssh: boolean; password: boolean; configurata: boolean };
  esecuzioni: EsecuzioneBackup[];
  ripristino: StatoRipristino;
}

export interface CopiaBackup { nome: string; byte: number; data: string; sicurezza: boolean; con_sha256: boolean }

export type EsitoProva =
  | { riuscita: true; impronta: string; accettata: boolean; copie: number; millisecondi: number }
  | { riuscita: false; dettaglio: string };

export const statoBackup = (t: string) => chiamata<StatoBackup>(t, "/admin/backup");
export const salvaImpostazioniBackup = (t: string, v: Omit<ImpostazioniBackup, "impronta_host">) =>
  chiamata<ImpostazioniBackup>(t, "/admin/backup/impostazioni", { method: "PUT", body: JSON.stringify(v) });
export const provaBackup = (t: string, fidati = false) =>
  chiamata<EsitoProva>(t, "/admin/backup/prova", { method: "POST", body: JSON.stringify({ fidati }) });
export const eseguiBackup = (t: string) => chiamata<{ avviato: boolean }>(t, "/admin/backup/esegui", { method: "POST" });
export const copieBackup = (t: string) => chiamata<{ copie: CopiaBackup[] }>(t, "/admin/backup/copie");
export const ripristinaBackup = (t: string, file: string, conferma: string) =>
  chiamata<{ avviato: boolean }>(t, "/admin/backup/ripristina", { method: "POST", body: JSON.stringify({ file, conferma }) });
export const statoRipristino = (t: string) => chiamata<StatoRipristino>(t, "/admin/backup/ripristino");
