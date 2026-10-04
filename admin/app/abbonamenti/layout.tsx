/* Abbonamenti (v9, Fase 2b): chi è abbonato e in che stato, e le regole del rinnovo, della prova e della tolleranza.
 * Le due pagine condividono l'intestazione e i sotto-tab. */

import comuni from "../comuni.module.css";
import { Schede } from "./schede";

export default function LayoutAbbonamenti({ children }: { children: React.ReactNode }) {
  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Abbonamenti</h1>
          <p className={comuni.sottotitolo}>
            Gli abbonamenti per stato — in prova, attivi, in tolleranza dopo un pagamento fallito, sospesi, chiusi — con
            le azioni per conto dell&apos;utente, e le regole: sconto del rinnovo automatico, prova gratuita, giorni di
            tolleranza, condoni oltre i limiti, banner della prova. I prezzi e i limiti dei piani sono nel Catalogo.
          </p>
        </div>
      </div>
      <Schede />
      {children}
    </>
  );
}
