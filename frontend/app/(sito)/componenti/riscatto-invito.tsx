"use client";

/* Riscatta da solo il codice d'invito, alla prima sessione autenticata.
 *
 * Stesso schema di `attribuzione.tsx` (che fa la stessa cosa per la condivisione delle letture): la pagina
 * pubblica ricorda il codice (`lib/inviti.ts::salvaInvito`, da `soglia.tsx`), qui lo si manda al server appena
 * c'è un token. Un rifiuto è definitivo (l'utente ha già un invito, il codice non esiste, è il proprio): il
 * codice si dimentica comunque, perché riprovarlo non cambierebbe l'esito. Solo un guasto di rete o del server
 * si ritenta al prossimo accesso — non si perde un regalo per un momento di rete debole.
 */

import { useEffect, useRef } from "react";
import { ErroreApi, riscattaInvito } from "@/lib/api";
import { dimenticaInvito, leggiInvito } from "@/lib/inviti";
import { useSessione } from "@/lib/sessione";

export function RiscattoInvitoAutomatico() {
  const { autenticata, token } = useSessione();
  const tentato = useRef(false);

  useEffect(() => {
    if (!autenticata || !token || tentato.current) return;
    const codice = leggiInvito();
    if (!codice) return;
    tentato.current = true;
    riscattaInvito(token, codice).then(
      () => dimenticaInvito(),
      (e: unknown) => {
        if (e instanceof ErroreApi && e.stato < 500 && e.stato !== 401) dimenticaInvito();
        else tentato.current = false;
      },
    );
  }, [autenticata, token]);

  return null;
}
