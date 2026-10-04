/* Gli abbonamenti della Fase 2b (v9): rinnovo automatico, cambio di piano col conguaglio, prova gratuita, il
 * pagamento da sistemare, il limite di letture. Le chiamate stanno qui e non in `lib/api.ts` (condiviso da tutte le
 * fasi): usano lo stesso `chiama`, con lo stesso trattamento degli errori. */

import { ErroreApi, chiama } from "./api";

export type StatoAbbonamento = "in_prova" | "attivo" | "in_sospeso" | "sospeso" | "disdetto" | "scaduto";

export interface AbbonamentoDettaglio {
  id: string;
  piano: string;
  nome: string;
  stato: StatoAbbonamento;
  provider: string;
  store: boolean;
  gestione_store: string | null;
  gratuito: boolean;
  annuale: boolean;
  prova: boolean;
  periodo_inizio: string;
  periodo_fine: string;
  disdetto_il: string | null;
  rinnovo_automatico: boolean;
  listino: number | null;
  importo_periodo: number | null;
  sconto_ricorrente: number;
  prossimo_rinnovo: number | null;
  valuta: string;
  fattura_aperta: boolean;
  pagamento_fallito_il: string | null;
  fine_tolleranza: string | null;
  piano_successivo: { piano: string; nome: string; annuale: boolean; dal: string } | null;
  /** Fase 2d: il codice sconto che continua sui rinnovi (`per_sempre`, o quanti rinnovi restano). */
  coupon?: {
    codice: string; tipo: string; valore: number; cumulabile: boolean; sconto: number; per_sempre: boolean;
    rinnovi_rimasti: number | null;
  } | null;
}

export interface ImpostazioniPubblicheAbbonamenti {
  banner_prova: boolean;
  prova_disponibile: boolean;
  giorni_prova: number;
  sconto_prova: number;
  sconto_rinnovo: number;
  condoni_per_periodo: number;
  giorni_promemoria_prova: number;
  giorni_tolleranza: number;
}

export interface MioAbbonamento {
  abbonamento: AbbonamentoDettaglio | null;
  prova: { idonea: boolean; motivo: string | null; usata_il: string | null };
  impostazioni: { sconto_rinnovo: number; sconto_prova: number; giorni_prova: number; giorni_tolleranza: number };
  saldo: number;
}

/** Le tre righe del conguaglio (e il conto di un downgrade). */
export interface Conguaglio {
  tipo: "upgrade" | "downgrade";
  piano: string;
  nome: string;
  annuale: boolean;
  rinnovo: boolean;
  listino: number;
  sconto_rinnovo: number;
  nuovo: number;
  residuo: number;
  totale: number;
  pagato: number;
  giorni_rimasti: number;
  giorni_periodo: number;
  decorre: string;
  valuta: string;
}

/** Il corpo dell'errore 402 `limite_superato` di `POST /readings`. */
export interface LimiteSuperato {
  motivo: "limite_superato";
  limite: "letture_al_giorno" | "letture_alla_settimana" | "letture_al_mese" | "letture_totali";
  valore: number;
  usate: number;
  letture_fatte: number;
  si_libera: string | null;
  condoni_rimasti: number;
  condoni_per_periodo: number;
  saldo: number;
  scelta: "condono" | "credito" | "acquisto";
}

export const PERCORSO_PUBBLICO_ABBONAMENTI = "/abbonamenti/pubblico";

export const impostazioniAbbonamenti = () => chiama<ImpostazioniPubblicheAbbonamenti>(null, PERCORSO_PUBBLICO_ABBONAMENTI);

export const mioAbbonamento = (token: string | null, lang?: string) =>
  chiama<MioAbbonamento>(token, lang ? `/me/abbonamento?lang=${lang}` : "/me/abbonamento");

export const impostaRinnovo = (token: string | null, attivo: boolean, lang?: string) =>
  chiama<{ abbonamento: AbbonamentoDettaglio }>(token, `/me/abbonamento/rinnovo${lang ? `?lang=${lang}` : ""}`, {
    method: "POST", body: { attivo },
  });

export const anteprimaCambio = (token: string | null, piano: string, annuale: boolean, rinnovo: boolean, lang?: string) =>
  chiama<Conguaglio>(token, `/me/abbonamento/cambio/anteprima${lang ? `?lang=${lang}` : ""}`, {
    method: "POST", body: { piano, annuale, rinnovo },
  });

export const cambiaPiano = (
  token: string | null, piano: string, annuale: boolean, rinnovo: boolean, ritorno?: string, lang?: string,
) =>
  chiama<{ tipo: "upgrade" | "downgrade"; conguaglio: Conguaglio; url?: string; importo?: number; abbonamento?: AbbonamentoDettaglio }>(
    token, `/me/abbonamento/cambio${lang ? `?lang=${lang}` : ""}`, { method: "POST", body: { piano, annuale, rinnovo, ritorno } },
  );

export const annullaCambio = (token: string | null, lang?: string) =>
  chiama<{ abbonamento: AbbonamentoDettaglio }>(token, `/me/abbonamento/cambio${lang ? `?lang=${lang}` : ""}`, { method: "DELETE" });

export const pagamentoDaSistemare = (token: string | null) =>
  chiama<{ provider: string; store: boolean; url: string | null; gia_pagata?: boolean }>(token, "/me/abbonamento/pagamento");

/** La prova; `coupon` (Fase 2d): il codice del link, che si somma allo sconto della prova o vale il più alto dei due. */
export const iniziaProva = (token: string | null, piano: string, ritorno?: string, coupon?: string) =>
  chiama<{ checkout_id: string; url: string; importo: number; valuta: string }>(token, "/me/prova", {
    method: "POST", body: { piano, ritorno, coupon },
  });

/** Un abbonamento con il rinnovo automatico scelto (acceso: lo sconto del rinnovo; spento: il listino, un periodo). */
export const apriAbbonamento = (
  token: string | null, piano: string, annuale: boolean, rinnovo: boolean, ritorno?: string, coupon?: string,
) =>
  chiama<{ checkout_id: string; url: string; importo: number; valuta: string; gratis?: boolean }>(token, "/me/checkout", {
    method: "POST", body: { piano, annuale, rinnovo, ritorno, coupon },
  });

/** Il dettaglio di un 402 `limite_superato`, se l'errore è quello. */
export function limiteSuperato(e: unknown): LimiteSuperato | null {
  if (!(e instanceof ErroreApi) || e.stato !== 402) return null;
  const d = e.dettaglio as { motivo?: unknown } | undefined;
  return d && d.motivo === "limite_superato" ? (d as LimiteSuperato) : null;
}

/** Il motivo stabile di un errore dell'API (`fattura_aperta`, `store`, `prova_gia_usata`…). */
export function motivoErrore(e: unknown): string | null {
  if (!(e instanceof ErroreApi)) return null;
  const d = e.dettaglio as { motivo?: unknown } | undefined;
  return d && typeof d.motivo === "string" ? d.motivo : null;
}
