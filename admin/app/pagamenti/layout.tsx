/* Pagamenti: i passaggi alla cassa e, nel sotto-tab «Stripe», chi incassa (v9, Fase 2c). Le pagine condividono
 * l'intestazione e i sotto-tab. */

import comuni from "../comuni.module.css";
import { Schede } from "./schede";

export default function LayoutPagamenti({ children }: { children: React.ReactNode }) {
  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Pagamenti</h1>
          <p className={comuni.sottotitolo}>
            Ogni passaggio alla cassa, concluso o no, e chi incassa. Le chiavi di Stripe si impostano da qui, nel
            sotto-tab «Stripe»: nessun file da toccare sul server.
          </p>
        </div>
      </div>
      <Schede />
      {children}
    </>
  );
}
