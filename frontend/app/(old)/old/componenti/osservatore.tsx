"use client";

/* L'osservatore delle pagine (v8, `lanterna-osservatore`): una pagina vista a ogni cambio di
 * percorso, tempo attivo, click e viste dichiarati nel markup (`data-an`, `data-an-vista`).
 * Nessun cookie. Il token, se c'è, lega la visita all'account (vedi l'informativa); l'id del
 * browser parte solo col consenso del banner. */

import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { avvia, type Osservatore } from "lanterna-osservatore";
import { ProviderOsservatore } from "lanterna-osservatore/react";
import { leggiConsenso } from "@/lib/api";
import { ENDPOINT_ANALYTICS, idPerAnalytics, impostaConsensoAnalytics } from "@/lib/analytics";
import { useLingua } from "@/lib/lingua";
import { useSessione } from "@/lib/sessione";

export function OsservatorePagine({ children }: { children: React.ReactNode }) {
  const percorso = usePathname();
  const { lingua } = useLingua();
  const sessione = useSessione();
  const [osservatore, setOsservatore] = useState<Osservatore | null>(null);
  /* L'osservatore nasce una volta: legge lingua e token dai ref, sempre aggiornati. */
  const linguaRef = useRef(lingua);
  const tokenRef = useRef(sessione.token);
  useEffect(() => {
    linguaRef.current = lingua;
    tokenRef.current = sessione.token;
  }, [lingua, sessione.token]);

  useEffect(() => {
    const o = avvia({
      endpoint: ENDPOINT_ANALYTICS,
      esclusi: ["/admin", "/api"],
      lingua: () => linguaRef.current,
      token: () => tokenRef.current,
      idBrowser: idPerAnalytics,
    });
    // Solo nel browser e una volta sola: l'osservatore attacca ascoltatori al documento.
    setOsservatore(o);
    return () => o.ferma();
  }, []);

  /* Il consenso già dato in una visita precedente accende subito il livello esteso. */
  useEffect(() => {
    if (!sessione.pronta) return;
    leggiConsenso(sessione.token)
      .then((c) => impostaConsensoAnalytics(c.cookie))
      .catch(() => {});
  }, [sessione.pronta, sessione.token]);

  useEffect(() => {
    osservatore?.pagina(percorso);
  }, [osservatore, percorso]);

  return <ProviderOsservatore osservatore={osservatore}>{children}</ProviderOsservatore>;
}
