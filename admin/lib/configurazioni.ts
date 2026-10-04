/* Le configurazioni dalla console (v9, Fase 2c): Stripe, posta in uscita, dati del titolare.
 *
 * I segreti (chiave segreta di Stripe, segreto del webhook, password della posta) si scrivono e non si rileggono: il
 * backend risponde solo se ci sono e da dove vengono (console o ambiente del server). Un campo segreto lasciato
 * vuoto in un salvataggio resta com'era. */

import { chiamata } from "./api";

export type Origine = "console" | "ambiente";
export type FornitorePagamento = "disattivato" | "mock" | "stripe";

export interface Presenza {
  impostata: boolean;
  origine: Origine | null;
}

export interface EsitoProva {
  ok: boolean;
  messaggio: string;
  nome?: string | null;
  incassa?: boolean | null;
}

export interface StatoStripe {
  provider: FornitorePagamento;
  provider_console: FornitorePagamento | null;
  provider_ambiente: string;
  origine_provider: Origine;
  produzione: boolean;
  modalita: "test" | "live" | null;
  chiave_segreta: Presenza & { tipo: "sk" | "rk" | null };
  chiave_pubblicabile: string | null;
  segreto_webhook: Presenza;
  webhook: { url_atteso: string; id: string | null; url: string | null; registrato_il: string | null };
  eventi: string[];
  ultima_prova: { quando: string | null; esito: EsitoProva | null };
}

export interface SalvaStripe {
  provider?: FornitorePagamento | null;
  modalita?: "test" | "live" | null;
  chiave_segreta?: string;
  chiave_pubblicabile?: string;
  togli_chiavi?: boolean;
}

export const statoStripe = (t: string) => chiamata<StatoStripe>(t, "/admin/configurazioni/stripe");
export const salvaStripe = (t: string, v: SalvaStripe) =>
  chiamata<StatoStripe>(t, "/admin/configurazioni/stripe", { method: "PUT", body: JSON.stringify(v) });
export const provaStripe = (t: string) =>
  chiamata<{ esito: EsitoProva; stato: StatoStripe }>(t, "/admin/configurazioni/stripe/prova", { method: "POST" });
export const registraWebhook = (t: string) =>
  chiamata<{ azione: "creato" | "aggiornato" | "sostituito"; doppioni_tolti: number; eventi: string[]; stato: StatoStripe }>(
    t, "/admin/configurazioni/stripe/webhook", { method: "POST" },
  );

export interface ValoriSmtp {
  host: string;
  porta: number;
  sicurezza: "ssl" | "starttls";
  utente: string;
  mittente: string;
  nome_mittente: string;
  dkim_selettore: string;
}

export interface StatoSmtp {
  origine: Origine | "nessuna";
  console: ValoriSmtp & { password: { impostata: boolean }; attiva: boolean };
  ambiente: Omit<ValoriSmtp, "nome_mittente" | "dkim_selettore"> & { password: { impostata: boolean } };
  in_uso: { host: string; porta: number; mittente: string; configurata: boolean };
  dominio: string;
  email_admin: string | null;
  ultima_prova: { quando: string | null; esito: { ok: boolean; messaggio: string } | null };
}

export const statoSmtp = (t: string) => chiamata<StatoSmtp>(t, "/admin/configurazioni/smtp");
export const salvaSmtp = (t: string, v: ValoriSmtp & { password?: string; togli_password?: boolean }) =>
  chiamata<StatoSmtp>(t, "/admin/configurazioni/smtp", { method: "PUT", body: JSON.stringify(v) });
export const provaSmtp = (t: string, destinatario: string) =>
  chiamata<{ ok: boolean; messaggio: string }>(t, "/admin/configurazioni/smtp/prova", {
    method: "POST", body: JSON.stringify({ destinatario }),
  });

export type StatoRecord = "presente" | "assente" | "errore";

export interface EsitoDns {
  dominio: string;
  errore?: string;
  spf: { stato: StatoRecord; valore?: string | null };
  dkim: { stato: StatoRecord; selettore?: string | null; valore?: string | null; provati?: string[] };
  dmarc: { stato: StatoRecord; valore?: string | null };
  mx: string[];
}

export const dnsPosta = (t: string, forza = false) =>
  chiamata<EsitoDns>(t, `/admin/configurazioni/smtp/dns${forza ? "?forza=true" : ""}`);

export interface FornitoreAi {
  nome: string;
  paese: string | null;
  proprio: boolean;
}

export interface Titolare {
  nome: string;
  indirizzo: string;
  codice_fiscale: string;
  email_privacy: string;
  dpo_nominato: boolean;
  dpo_contatto: string;
  hosting: string;
  aggiornato_il?: string | null;
  fornitori_ai?: FornitoreAi[];
  predefiniti?: { email_privacy: string; hosting: string };
}

export const leggiTitolare = (t: string) => chiamata<Titolare>(t, "/admin/configurazioni/titolare");
export const salvaTitolare = (t: string, v: Titolare) =>
  chiamata<Titolare>(t, "/admin/configurazioni/titolare", { method: "PUT", body: JSON.stringify(v) });
