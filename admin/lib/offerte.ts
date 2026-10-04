/* Coupon di sconto, codici regalo e regali di crediti, dalla console.
 *
 * Tre tipi di coupon. `percentuale` (1-100) e `importo` (centesimi) scontano un pagamento: su un abbonamento il primo,
 * i primi N o tutti (Fase 2d, `durata`), sommati o no allo sconto del rinnovo e della prova (`cumulabile`). `crediti`
 * è un codice regalo, che chi lo riscatta cambia in crediti senza pagare. Un coupon già usato non si elimina né cambia
 * valore, durata o cumulo: si disattiva. Fase 2d: lotti di codici monouso, campagne e resoconto. */

import { chiamata, scaricaFile } from "./api";

export type TipoCoupon = "percentuale" | "importo" | "crediti";

export interface Coupon {
  id: number;
  codice: string;
  descrizione: string | null;
  tipo: TipoCoupon;
  /** Percentuale, centesimi o crediti, secondo il tipo. */
  valore: number;
  /** Gli slug dei piani a cui vale; vuoto = tutti. */
  piani: string[];
  solo_primo_acquisto: boolean;
  valido_dal: string | null;
  valido_fino: string | null;
  max_riscatti: number | null;
  max_per_utente: number;
  riscatti: number;
  attivo: boolean;
  creato: string | null;
  /* Fase 2d: durata sugli abbonamenti, cumulo con rinnovo e prova, campagna, lotto, link che applica il codice. */
  durata: DurataCoupon;
  periodi: number | null;
  cumulabile: boolean;
  campagna: string | null;
  lotto_id: number | null;
  link: { en: string; it: string } | null;
  resoconto?: Resoconto;
}

export type DurataCoupon = "una_volta" | "periodi" | "sempre";

/** Le cifre di un coupon o di una campagna (centesimi per gli importi). */
export interface Resoconto {
  coupon: number;
  riscatti: number;
  incasso_lordo: number;
  sconto_concesso: number;
  crediti_regalati: number;
  nuovi_utenti: number;
  prove: number;
  conversioni_da_prova: number;
  rinnovi_scontati: number;
}

export interface Campagna extends Resoconto {
  campagna: string | null;
  lotti: number;
}

export interface Lotto {
  id: number;
  prefisso: string;
  campagna: string | null;
  descrizione: string | null;
  quantita: number;
  usati: number;
  attivi: number;
  creato: string | null;
  regole: Pick<Coupon, "tipo" | "valore" | "piani" | "solo_primo_acquisto" | "valido_dal" | "valido_fino" | "durata" | "periodi" | "cumulabile"> | null;
}

export interface NuovoLotto {
  prefisso: string;
  quantita: number;
  campagna: string;
  description?: string;
  tipo: TipoCoupon;
  valore: number;
  piani?: string[];
  solo_primo_acquisto?: boolean;
  valido_dal?: string | null;
  valido_fino?: string | null;
  durata?: DurataCoupon;
  periodi?: number | null;
  cumulabile?: boolean;
}

/** Ciò che il backend accetta alla creazione. `code` vuoto: lo sceglie il server (8 caratteri leggibili). */
export interface NuovoCoupon {
  code?: string;
  description?: string;
  tipo: TipoCoupon;
  valore: number;
  piani?: string[];
  solo_primo_acquisto?: boolean;
  valido_dal?: string | null;
  valido_fino?: string | null;
  max_riscatti?: number | null;
  max_per_utente?: number;
  attivo?: boolean;
  durata?: DurataCoupon;
  periodi?: number | null;
  cumulabile?: boolean;
  campagna?: string | null;
}

export type ModificaCoupon = Partial<Omit<NuovoCoupon, "code" | "tipo">>;

export interface Riscatto {
  id: number;
  utente: number;
  email: string;
  sconto: number;
  crediti: number;
  pagamento: string | null;
  quando: string;
  /** Fase 2d: quanto è stato pagato, e se è lo sconto di un rinnovo (non un uso del codice). */
  importo: number;
  rinnovo: boolean;
}

/** I coupon singoli con le loro cifre; con `lotto` i codici di quel lotto. */
export const coupons = (t: string, lotto?: number) =>
  chiamata<Coupon[]>(t, lotto ? `/admin/coupons?lotto=${lotto}` : "/admin/coupons?resoconto=true");

export const lotti = (t: string) => chiamata<Lotto[]>(t, "/admin/coupon-lotti");

export const creaLotto = (t: string, corpo: NuovoLotto) =>
  chiamata<Lotto>(t, "/admin/coupon-lotti", { method: "POST", body: JSON.stringify(corpo) });

export const attivaLotto = (t: string, id: number, attivo: boolean) =>
  chiamata<Lotto>(t, `/admin/coupon-lotti/${id}`, { method: "PATCH", body: JSON.stringify({ attivo }) });

export const scaricaLotto = (t: string, lotto: Pick<Lotto, "id" | "prefisso">) =>
  scaricaFile(t, `/admin/coupon-lotti/${lotto.id}/csv`, {}, `coupon-${lotto.prefisso.toLowerCase()}-${lotto.id}.csv`);

export const campagne = (t: string) =>
  chiamata<{ campagne: Campagna[]; totale: Partial<Resoconto> }>(t, "/admin/coupon-campagne");

export const creaCoupon = (t: string, corpo: NuovoCoupon) =>
  chiamata<Coupon>(t, "/admin/coupons", { method: "POST", body: JSON.stringify(corpo) });

export const modificaCoupon = (t: string, id: number, corpo: ModificaCoupon) =>
  chiamata<Coupon>(t, `/admin/coupons/${id}`, { method: "PATCH", body: JSON.stringify(corpo) });

export const eliminaCoupon = (t: string, id: number) =>
  chiamata<void>(t, `/admin/coupons/${id}`, { method: "DELETE" });

export const riscattiDi = (t: string, id: number) =>
  chiamata<{ coupon: Coupon; riscatti: Riscatto[]; resoconto: Resoconto }>(t, `/admin/coupons/${id}/riscatti`);

/** «solo il primo pagamento», «per 3 periodi», «per sempre». */
export function durataCoupon(c: Pick<Coupon, "durata" | "periodi" | "tipo">): string {
  if (c.tipo === "crediti") return "—";
  if (c.durata === "sempre") return "per sempre (ogni rinnovo)";
  if (c.durata === "periodi") return `per ${c.periodi ?? 2} pagamenti (il primo compreso)`;
  return "solo il primo pagamento";
}

/** Un regalo: un pacchetto del catalogo (`piano`) oppure una quantità (`crediti`), non entrambi. */
export interface Regalo {
  piano?: string;
  crediti?: number;
  nota?: string;
}

export const regalaCrediti = (t: string, utenteId: number, corpo: Regalo) =>
  chiamata<{ saldo: number; crediti: number }>(t, `/admin/users/${utenteId}/regalo`, {
    method: "POST",
    body: JSON.stringify(corpo),
  });

/** Com'è fatto lo sconto, per chi legge l'elenco: «−20%», «−5,00 €», «25 crediti». */
export function valoreCoupon(c: Pick<Coupon, "tipo" | "valore">, soldi: (centesimi: number) => string): string {
  if (c.tipo === "percentuale") return `−${c.valore}%`;
  if (c.tipo === "importo") return `−${soldi(c.valore)}`;
  return `${c.valore} ${c.valore === 1 ? "credito" : "crediti"}`;
}
