"use client";

/* Attribuisce un'iscrizione al link da cui si arriva.
 *
 * Chi apre una lettura condivisa e poi si iscrive fa guadagnare cinque letture a
 * chi gliel'ha mandata. La pagina pubblica ricorda il link (`ricordaOrigine`); qui,
 * la prima volta che c'è una sessione, lo si dice al server, che decide se vale:
 * l'account deve essere nuovo, con email verificata, e diverso da chi ha condiviso.
 * Un rifiuto è definitivo: il link si dimentica in ogni caso, tranne per un guasto
 * momentaneo (rete, server), che si ritenta al prossimo accesso. */

import { useEffect, useRef } from "react";
import { ErroreApi, attribuisciIscrizione } from "@/lib/api";
import { dimenticaOrigine, idVisitatore, leggiOrigine } from "@/lib/condivisione";
import { useSessione } from "@/lib/sessione";

export function AttribuzioneCondivisione() {
  const { autenticata, token } = useSessione();
  const tentato = useRef(false);

  useEffect(() => {
    if (!autenticata || !token || tentato.current) return;
    const link = leggiOrigine();
    if (!link) return;
    tentato.current = true;
    attribuisciIscrizione(token, link, idVisitatore()).then(
      () => dimenticaOrigine(),
      (e: unknown) => {
        if (e instanceof ErroreApi && e.stato < 500 && e.stato !== 401) dimenticaOrigine();
        else tentato.current = false;
      },
    );
  }, [autenticata, token]);

  return null;
}
