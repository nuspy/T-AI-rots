"use client";

/* Il banner cookie GDPR (v7, Fase G): globale, su ogni pagina, finché non c'è una scelta salvata
 * per questo browser/account. Le due etichette dei bottoni sono un requisito letterale
 * dell'operatore ("It's fine" / "Please no") — non tradotte, per scelta di tono del sito, a
 * differenza del resto del testo che segue la lingua corrente. */

import { useState } from "react";
import { leggiConsenso, registraConsenso } from "@/lib/api";
import { useLingua } from "@/lib/lingua";
import { useSessione } from "@/lib/sessione";
import { useCarica } from "@/lib/usa";
import stili from "./banner-cookie.module.css";

export function BannerCookie() {
  const { t } = useLingua();
  const sessione = useSessione();
  const consenso = useCarica(leggiConsenso, [], { pubblico: true });
  const [inCorso, setInCorso] = useState(false);
  const [nascosto, setNascosto] = useState(false);

  // In attesa della prima risposta, o con una scelta già registrata: nessun banner.
  if (!consenso.dati || consenso.dati.cookie !== null || nascosto) return null;

  const scegli = async (valore: "accettato" | "rifiutato") => {
    setInCorso(true);
    try {
      // `useAzione` non chiamerebbe l'azione per un visitatore anonimo (richiede sessione
      // autenticata): qui serve funzionare per chiunque, quindi si chiama l'API direttamente
      // con il token se c'è, `null` altrimenti — `credentials: "include"` fa viaggiare/ricevere
      // il cookie in entrambi i casi.
      await registraConsenso(sessione.token, "cookie", valore);
      setNascosto(true);
    } finally {
      setInCorso(false);
    }
  };

  return (
    <div className={stili.banner} role="dialog" aria-label={t.cookie_titolo}>
      <p className={stili.testo}>{t.cookie_testo}</p>
      <div className={stili.azioni}>
        <button type="button" className="bottone-secondario" disabled={inCorso} onClick={() => scegli("rifiutato")}>
          Please no
        </button>
        <button type="button" className="bottone" disabled={inCorso} onClick={() => scegli("accettato")}>
          It&apos;s fine
        </button>
      </div>
    </div>
  );
}
