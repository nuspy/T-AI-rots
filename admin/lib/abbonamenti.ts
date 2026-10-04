/* La console «Abbonamenti» (v9, Fase 2b): le impostazioni (sconti, prova, tolleranza, promemoria, condoni, banner) e
 * l'elenco degli abbonamenti per stato, con le azioni. Il backend è `api/routers/admin_abbonamenti.py`: ogni modifica
 * e ogni azione resta nel registro, con il prima e il dopo. */

import { chiamata, interrogazione } from "./api";

export type StatoAbbonamento = "in_prova" | "attivo" | "in_sospeso" | "sospeso" | "disdetto" | "scaduto";
export type AzioneAbbonamento = "rinnovo_spento" | "rinnovo_acceso" | "sospendi" | "proroga" | "chiudi";

export interface ImpostazioniAbbonamenti {
  sconto_rinnovo: number;
  sconto_prova: number;
  giorni_prova: number;
  giorni_tolleranza: number;
  giorni_promemoria_prova: number;
  condoni_per_periodo: number;
  banner_prova: boolean;
}

export interface AbbonamentoConsole {
  id: string;
  piano: string;
  nome: string;
  stato: StatoAbbonamento;
  provider: string;
  store: boolean;
  annuale: boolean;
  prova: boolean;
  periodo_inizio: string;
  periodo_fine: string;
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
  utente: { id: number; email: string | null };
  external_id: string | null;
  creato: string | null;
  azioni: AzioneAbbonamento[];
}

export interface ElencoAbbonamenti {
  totale: number;
  conteggi: Record<StatoAbbonamento, number>;
  /** v9, Fase 4: quanti abbonamenti a pagamento per chi li incassa (stripe, google_play, app_store…). */
  per_fornitore?: Record<string, number>;
  abbonamenti: AbbonamentoConsole[];
}

/** Chi incassa un abbonamento, con il nome da mostrare (`Subscription.provider`). */
export const FORNITORI_ABBONAMENTO: Record<string, string> = {
  stripe: "Stripe (sito)",
  google_play: "Google Play",
  app_store: "App Store",
  mock: "Simulatore",
  interno: "Interno (regalato)",
};

export const leggiImpostazioniAbbonamenti = (t: string) =>
  chiamata<ImpostazioniAbbonamenti>(t, "/admin/abbonamenti/impostazioni");

export const scriviImpostazioniAbbonamenti = (t: string, campi: Partial<ImpostazioniAbbonamenti>) =>
  chiamata<ImpostazioniAbbonamenti>(t, "/admin/abbonamenti/impostazioni", { method: "PUT", body: JSON.stringify(campi) });

export const elencoAbbonamenti = (
  t: string, filtri: { stato?: string; q?: string; provider?: string; limite?: number; offset?: number },
) => chiamata<ElencoAbbonamenti>(t, `/admin/abbonamenti${interrogazione(filtri)}`);

export const azioneAbbonamento = (t: string, id: string, azione: AzioneAbbonamento, motivo: string, giorni?: number) =>
  chiamata<AbbonamentoConsole>(t, `/admin/abbonamenti/${id}/azione`, { method: "POST", body: JSON.stringify({ azione, motivo, giorni }) });
