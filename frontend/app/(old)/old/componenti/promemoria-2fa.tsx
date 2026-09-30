"use client";

/* Il promemoria della verifica in due passaggi, una volta a ogni ingresso.
 *
 * Compare dopo l'accesso a chi non l'ha attivata (o non si sa se l'ha attivata), una
 * sola volta per sessione del browser. «Più tardi» lo chiude fino al prossimo ingresso;
 * la casella «Non mostrare più» lo spegne per sempre, su ogni dispositivo
 * (`promemoria_2fa` nel profilo), e si riaccende dal profilo. Non compare sulle pagine
 * pubbliche delle letture condivise, né in sviluppo senza Keycloak. */

import { useEffect, useRef, useState } from "react";
import { usePathname } from "next/navigation";
import { aggiornaProfilo, leggiProfilo } from "@/lib/api";
import { useLingua } from "@/lib/lingua";
import { leggiStato2fa } from "@/lib/sicurezza";
import { useSessione } from "@/lib/sessione";
import { Modale } from "./modale";
import stili from "./promemoria.module.css";

const CHIAVE = "tarots.promemoria2fa";

const giaMostrato = () => {
  try {
    return window.sessionStorage.getItem(CHIAVE) === "1";
  } catch {
    return false;
  }
};

const segnaMostrato = () => {
  try {
    window.sessionStorage.setItem(CHIAVE, "1");
  } catch {
    /* memoria bloccata: il promemoria può ricomparire a ogni pagina caricata */
  }
};

export function Promemoria2fa() {
  const { t } = useLingua();
  const sessione = useSessione();
  const percorso = usePathname();
  const [aperto, setAperto] = useState(false);
  const [nonMostrare, setNonMostrare] = useState(false);
  const controllato = useRef(false);
  const { autenticata, token } = sessione;

  useEffect(() => {
    if (!autenticata || !token || controllato.current || percorso.startsWith("/old/s/")) return;
    controllato.current = true;
    if (giaMostrato()) return;
    void (async () => {
      const profilo = await leggiProfilo(token).catch(() => null);
      if (!profilo || !profilo.promemoria_2fa) return;
      if ((await leggiStato2fa(token)) === "attiva") return;
      segnaMostrato();
      setAperto(true);
    })();
  }, [autenticata, token, percorso]);

  const chiudi = (attiva: boolean) => {
    setAperto(false);
    /* La scelta «non mostrare più» vale qualunque pulsante si prema (anche Esc). */
    if (nonMostrare) void aggiornaProfilo(token, { promemoria_2fa: false }).catch(() => undefined);
    if (attiva) sessione.attiva2fa();
  };

  return (
    <Modale aperta={aperto} titolo={t.sic_titolo} onChiudi={() => chiudi(false)}>
      <p className={stili.testo}>{t.sic_testo}</p>
      <label className={stili.casella}>
        <input type="checkbox" checked={nonMostrare} onChange={(e) => setNonMostrare(e.target.checked)} />
        <span>{t.sic_non_mostrare}</span>
      </label>
      <div className={stili.azioni}>
        <button className={`bottone ${stili.pulsante}`} onClick={() => chiudi(true)} autoFocus>
          {t.sic_attiva}
        </button>
        <button className={`bottone-secondario ${stili.pulsante}`} onClick={() => chiudi(false)}>
          {t.sic_piu_tardi}
        </button>
      </div>
    </Modale>
  );
}
