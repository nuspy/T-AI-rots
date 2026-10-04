/* Notifications (v9, Fase 5): le notifiche push nelle app (Firebase Cloud Messaging) e sul sito (Web Push). Le
 * pagine condividono l'intestazione e i sotto-tab. */

import comuni from "../comuni.module.css";
import { Schede } from "./schede";

export default function LayoutNotifiche({ children }: { children: React.ReactNode }) {
  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Notifications</h1>
          <p className={comuni.sottotitolo}>
            I messaggi che arrivano sul telefono (app Android e iPhone) e nel browser (sito): la carta del giorno e gli
            altri promemoria automatici, le campagne che scrivi tu per un gruppo di utenti, e come sono andati. Le
            promozioni partono solo verso chi ha dato il consenso «promozioni».
          </p>
        </div>
      </div>
      <Schede />
      {children}
    </>
  );
}
