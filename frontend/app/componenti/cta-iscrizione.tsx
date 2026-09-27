"use client";

/* L'invito a iscriversi: solo per chi non ha fatto l'accesso, ovunque compaia — mai per chi è già dentro. I
 * numeri sono veri (letti da `/impostazioni-pubbliche`, che l'amministrazione può cambiare dalla console), non un
 * testo fisso che rischia di disallinearsi. */

import { impostazioniPubbliche } from "@/lib/api";
import { useLingua } from "@/lib/lingua";
import { useSessione } from "@/lib/sessione";
import { useCarica } from "@/lib/usa";
import stili from "./cta-iscrizione.module.css";

export function CtaIscrizione({ compatta = false }: { compatta?: boolean }) {
  const sessione = useSessione();
  const { t } = useLingua();
  const impostazioni = useCarica(impostazioniPubbliche, [], { pubblico: true });

  if (!sessione.pronta || sessione.autenticata || !impostazioni.dati) return null;

  return (
    <div className={compatta ? stili.compatta : stili.riquadro}>
      <div>
        <strong className={stili.titolo}>{t.cta_iscrizione_titolo}</strong>
        <p className={stili.testo}>
          {t.cta_iscrizione_testo(impostazioni.dati.crediti_iscrizione, impostazioni.dati.crediti_invito)}
        </p>
      </div>
      <button className="bottone" onClick={sessione.registrati}>
        {t.registrati}
      </button>
    </div>
  );
}
