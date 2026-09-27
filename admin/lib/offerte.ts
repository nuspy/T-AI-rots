/* Coupon di sconto, codici regalo e regali di crediti, dalla console.
 *
 * Tre tipi di coupon. `percentuale` (1-100) e `importo` (centesimi) scontano un pagamento, sul primo pagamento: un
 * abbonamento si rinnova a prezzo pieno. `crediti` è un codice regalo, che chi lo riscatta cambia in crediti senza
 * pagare. Un coupon già usato non si elimina né cambia valore: si disattiva. */

import { chiamata } from "./api";

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
}

export const coupons = (t: string) => chiamata<Coupon[]>(t, "/admin/coupons");

export const creaCoupon = (t: string, corpo: NuovoCoupon) =>
  chiamata<Coupon>(t, "/admin/coupons", { method: "POST", body: JSON.stringify(corpo) });

export const modificaCoupon = (t: string, id: number, corpo: ModificaCoupon) =>
  chiamata<Coupon>(t, `/admin/coupons/${id}`, { method: "PATCH", body: JSON.stringify(corpo) });

export const eliminaCoupon = (t: string, id: number) =>
  chiamata<void>(t, `/admin/coupons/${id}`, { method: "DELETE" });

export const riscattiDi = (t: string, id: number) =>
  chiamata<{ coupon: Coupon; riscatti: Riscatto[] }>(t, `/admin/coupons/${id}/riscatti`);

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
