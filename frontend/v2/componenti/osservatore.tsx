"use client";

/* L'osservatore delle pagine della v2: lo stesso di `app/(sito)/componenti/osservatore.tsx` (libreria `lanterna`),
 * con la lingua della v2. Le visite della v2 arrivano con il loro percorso (`/v2/...`): la console le distingue
 * da quelle del sito. */

import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { avvia, type Osservatore } from "lanterna-osservatore";
import { ProviderOsservatore } from "lanterna-osservatore/react";
import { ENDPOINT_ANALYTICS, idPerAnalytics } from "@/lib/analytics";
import { useSessione } from "@/lib/sessione";
import { useConsensi } from "@/v2/lib/consensi";
import { useLingua } from "@/v2/lib/lingua";
import { proprietaEventi } from "@/v2/lib/varianti";

export function OsservatoreV2({ children }: { children: React.ReactNode }) {
  const percorso = usePathname();
  const { lingua } = useLingua();
  const sessione = useSessione();
  const [osservatore, setOsservatore] = useState<Osservatore | null>(null);
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
      /* v9.5: `piattaforma: web` in ogni evento e, sulle pagine di lettura, la `variante` (prova 90/10). */
      proprieta: proprietaEventi,
    });
    setOsservatore(o);
    return () => o.ferma();
  }, []);

  /* Il livello esteso dipende dal consenso `statistiche` (GDPR, Fase 1): lo stato dei consensi lo legge a ogni cambio
   * di sessione e lo applica da sé (`v2/lib/consensi.ts`). */
  useConsensi();

  useEffect(() => {
    osservatore?.pagina(percorso);
  }, [osservatore, percorso]);

  return <ProviderOsservatore osservatore={osservatore}>{children}</ProviderOsservatore>;
}
