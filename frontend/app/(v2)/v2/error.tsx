"use client";

/* Un errore imprevisto in una pagina della v2: si può riprovare, o andare altrove. */

import { useEffect } from "react";
import { Pagina } from "@/v2/componenti/pagina";
import { ErroreV2 } from "@/v2/pagine/errori";

export default function Errore({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => {
    console.error(error);
  }, [error]);
  return (
    <Pagina>
      <ErroreV2 onRiprova={reset} />
    </Pagina>
  );
}
