/* Impostazioni: le regole del sito, la posta in uscita e i dati del titolare (v9, Fase 2c). Le pagine condividono
 * l'intestazione e i sotto-tab. */

import comuni from "../comuni.module.css";
import { Schede } from "./schede";

export default function LayoutImpostazioni({ children }: { children: React.ReactNode }) {
  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Impostazioni</h1>
          <p className={comuni.sottotitolo}>
            Le regole del sito, la posta che il sito spedisce e chi è il titolare dei dati nell&apos;informativa
            privacy. Tutto da qui: nessun file da toccare sul server.
          </p>
        </div>
      </div>
      <Schede />
      {children}
    </>
  );
}
