/* Coupon (v9, Fase 2d): i coupon singoli, i lotti di codici monouso, le campagne con il resoconto. Le tre pagine
 * condividono l'intestazione, la nota sulle app e i sotto-tab. */

import comuni from "../comuni.module.css";
import { Schede } from "./schede";

export default function LayoutCoupon({ children }: { children: React.ReactNode }) {
  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Coupon e codici regalo</h1>
          <p className={comuni.sottotitolo}>
            Gli sconti valgono sul primo pagamento, sui primi N o per sempre, e si sommano o no allo sconto del rinnovo
            automatico e della prova; i codici regalo danno crediti. Ogni coupon ha il suo link che applica il codice
            da solo, e una campagna per il resoconto. Un coupon già usato non si elimina: si disattiva.
          </p>
        </div>
      </div>
      <p className={comuni.avviso} role="note">
        <strong>App:</strong> questi coupon valgono solo sugli acquisti con Stripe — il sito, o il pulsante della carta
        (Stripe) nelle app. Google Play e Apple hanno codici promozionali propri (promo code di Google, Offer Codes di
        Apple), che si creano nei loro pannelli: Play Console → l&apos;app → Monetizza → Promozioni; App Store Connect →
        l&apos;app → Abbonamenti → Codici offerta. I link sono in «Account».
      </p>
      <Schede />
      {children}
    </>
  );
}
