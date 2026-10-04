"use client";

/* Il codice sconto sulla pagina dei prezzi (v9, Fase 2d): la banda con il codice applicato — cosa sconta, per quanto,
 * se si somma agli altri sconti, quando scade — e, su ogni offerta, quanto si risparmia e quale sconto vale.
 *
 * Mai solo il colore: il prezzo pieno è barrato (e letto come «prima»), il risparmio è scritto, la scadenza vicina è
 * una frase. I conti vengono dal server (`v2/lib/coupon.ts`). */

import { euro } from "@/lib/api";
import { f, plurale } from "@/v2/i18n";
import { useLingua } from "@/v2/lib/lingua";
import { giorniAllaScadenza, type AnteprimaCouponPubblica, type CouponPubblico, type VoceCoupon } from "@/v2/lib/coupon";

/** «−30%» o «−5,00 €». */
export function etichettaSconto(c: Pick<CouponPubblico, "tipo" | "valore">, valuta: string, locale: string): string {
  return c.tipo === "percentuale" ? `−${c.valore}%` : `−${euro(c.valore, valuta, locale)}`;
}

/** L'esito dell'anteprima: il coupon con le offerte, o perché non vale. */
export type EsitoCoupon = { ok: AnteprimaCouponPubblica } | { motivo: string };

export function BandaCoupon({ codice, esito, valuta = "EUR", onTogli }: {
  codice: string; esito: EsitoCoupon | null; valuta?: string; onTogli: () => void;
}) {
  const { t, locale } = useLingua();
  const k = t.prezzi;
  const togli = (
    <button type="button" className="button button-quiet button-small" onClick={onTogli}>{k.coupon.togli}</button>
  );
  if (!esito) return null;
  if ("motivo" in esito) {
    return (
      <div className="coupon-banda coupon-banda-errore" role="alert">
        <div>
          <p className="coupon-banda-titolo coupon-codice">{codice}</p>
          <p>{k.errori_codice[esito.motivo] ?? t.comune.err_richiesta}</p>
        </div>
        {togli}
      </div>
    );
  }
  const c = esito.ok.coupon;
  const sconto = etichettaSconto(c, valuta, locale);
  const durata = c.durata === "sempre" ? f(k.coupon.durata_sempre, { sconto })
    : c.durata === "periodi" ? f(k.coupon.durata_periodi, { sconto, n: c.periodi ?? 2 })
      : f(k.coupon.durata_una_volta, { sconto });
  const giorni = giorniAllaScadenza(c.valido_fino);
  return (
    <div className="coupon-banda" role="status">
      <div>
        <p className="coupon-banda-titolo">{f(k.coupon.applicato, { codice: c.codice })}</p>
        <p>{durata}. {c.cumulabile ? k.coupon.cumulabile : k.coupon.non_cumulabile}</p>
        {giorni !== null && (
          <p className="coupon-scadenza">{giorni === 0 ? k.coupon.scade_oggi : plurale(giorni, k.coupon.scade_tra)}</p>
        )}
        <p className="small muted">{k.coupon.solo_stripe}</p>
      </div>
      {togli}
    </div>
  );
}

/** Sotto il prezzo di un'offerta: il risparmio, quale sconto vale e perché, e il prezzo dopo lo sconto del codice. */
export function RigheCoupon({ voce, valuta, perPeriodo = "" }: { voce: VoceCoupon | null; valuta: string; perPeriodo?: string }) {
  const { t, locale } = useLingua();
  const k = t.prezzi;
  if (!voce) return null;
  if (voce.motivo) return <p className="small coupon-nota">{k.errori_codice[voce.motivo] ?? k.non_vale}</p>;
  const soldi = (n: number | undefined) => euro(n ?? 0, valuta, locale);
  const base = `−${soldi(voce.sconto_base)}`;
  const spiegazione = voce.vince === "entrambi" ? k.coupon.vince_entrambi
    : voce.vince === "coupon" && (voce.sconto_base ?? 0) > 0 ? f(k.coupon.vince_coupon, { base })
      : voce.vince === "rinnovo" ? f(k.coupon.vince_rinnovo, { base })
        : voce.vince === "prova" ? f(k.coupon.vince_prova, { base }) : null;
  // Il prezzo dei rinnovi quando lo sconto del codice finisce (se finisce, e se c'è un rinnovo).
  const finisce = voce.applicato && voce.rinnovo && voce.rinnovi_coupon !== null && voce.rinnovi_coupon !== undefined;
  const dopo = finisce ? (voce.listino ?? 0) - (voce.sconto_base ?? 0) : null;
  return (
    <>
      {voce.applicato && (voce.risparmio ?? 0) > 0 && (
        <p className="coupon-risparmio">{f(k.coupon.risparmi, { importo: soldi(voce.risparmio) })}</p>
      )}
      {spiegazione && <p className="small coupon-nota">{spiegazione}</p>}
      {dopo !== null && dopo !== voce.importo && (
        <p className="small coupon-nota">{f(k.coupon.poi, { prezzo: `${soldi(dopo)}${perPeriodo}` })}</p>
      )}
    </>
  );
}
