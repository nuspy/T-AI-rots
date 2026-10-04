/* App mobili (v9, Fase 3): gli account degli store e cosa l'app vende. Le pagine condividono l'intestazione e i
 * sotto-tab. */

import comuni from "../comuni.module.css";
import { Schede } from "./schede";

export default function LayoutAppMobili({ children }: { children: React.ReactNode }) {
  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>App mobili</h1>
          <p className={comuni.sottotitolo}>
            Le app Android (Google Play) e iOS per iPhone e iPad (App Store): account sviluppatore, credenziali per
            verificare gli acquisti, profilo pagamenti, i prodotti in vendita negli store e quando mostrare il
            pulsante Stripe. Tutti gli account esterni, con lo stato, sono anche in «Account».
          </p>
        </div>
      </div>
      <Schede />
      {children}
    </>
  );
}
