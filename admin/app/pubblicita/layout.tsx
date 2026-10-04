/* Advertisements: gli spazi pubblicitari del sito. Le pagine condividono l'intestazione e i sotto-tab. */

import comuni from "../comuni.module.css";
import { Schede } from "./schede";

export default function LayoutPubblicita({ children }: { children: React.ReactNode }) {
  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Advertisements</h1>
          <p className={comuni.sottotitolo}>
            Tre spazi pubblicitari per pagina (a un terzo, a due terzi, alla fine prima della chiusura), nelle pagine di
            contenuto del sito. Spenti finché non li accendi; anche accesi, chi visita li vede solo dopo aver accettato
            gli annunci nel banner dei cookie.
          </p>
        </div>
      </div>
      <Schede />
      {children}
    </>
  );
}
