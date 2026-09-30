"use client";

/* Il promemoria della verifica in due passaggi, una volta a ogni ingresso: stessa logica del sito
 * (`app/(sito)/componenti/promemoria-2fa.tsx`), stessa memoria di sessione — chi l'ha già visto di là non lo
 * rivede qui. Non compare sulle letture condivise. */

import { useEffect, useRef, useState } from "react";
import { usePathname } from "next/navigation";
import { aggiornaProfilo, leggiProfilo } from "@/lib/api";
import { leggiStato2fa } from "@/lib/sicurezza";
import { useSessione } from "@/lib/sessione";
import { useLingua } from "@/v2/lib/lingua";
import { senzaPrefisso } from "@/v2/lib/percorsi";
import { Modale } from "./modale";

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
    /* memoria bloccata: il promemoria può ricomparire */
  }
};

export function Promemoria2faV2() {
  const { t } = useLingua();
  const sessione = useSessione();
  const percorso = senzaPrefisso(usePathname() ?? "");
  const [aperto, setAperto] = useState(false);
  const [nonMostrare, setNonMostrare] = useState(false);
  const controllato = useRef(false);
  const { autenticata, token } = sessione;

  useEffect(() => {
    if (!autenticata || !token || controllato.current || percorso.startsWith("/v2/shared")) return;
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
    if (nonMostrare) void aggiornaProfilo(token, { promemoria_2fa: false }).catch(() => undefined);
    if (attiva) sessione.attiva2fa();
  };

  return (
    <Modale aperta={aperto} titolo={t.comune.sic_titolo} onChiudi={() => chiudi(false)}>
      <p className="prose">{t.comune.sic_testo}</p>
      <label className="check">
        <input type="checkbox" checked={nonMostrare} onChange={(e) => setNonMostrare(e.target.checked)} />
        <span>{t.comune.sic_non_mostrare}</span>
      </label>
      <div className="button-row">
        <button type="button" className="button" onClick={() => chiudi(true)} autoFocus>{t.comune.sic_attiva}</button>
        <button type="button" className="button button-quiet" onClick={() => chiudi(false)}>{t.comune.sic_piu_tardi}</button>
      </div>
    </Modale>
  );
}
