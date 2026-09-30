"use client";

/* Un errore imprevisto durante il rendering di una pagina: stesso vestito del sito, un modo per riprovare e
 * qualche collegamento per ripartire. Deve essere un componente client (il confine d'errore lo richiede) e non
 * può usare `Involucro` (che a sua volta si aspetta un albero già montato sotto il layout radice, non sopra un
 * confine d'errore): markup semplice, gli stessi stili globali del sito. */

import { useEffect } from "react";
import Link from "./componenti/link";
import { useLingua } from "@/lib/lingua";
import stili from "./errore.module.css";

export default function Errore({ error, retry }: { error: Error & { digest?: string }; retry: () => void }) {
  const { t } = useLingua();

  useEffect(() => {
    console.error(error);
  }, [error]);

  const voci = [
    { href: "/", etichetta: t.marchio },
    { href: "/leggi", etichetta: t.nav_leggi },
    { href: "/carte", etichetta: t.nav_carte },
    { href: "/blog", etichetta: t.nav_blog },
  ];

  return (
    <div className={stili.pagina}>
      <div className={`pannello ${stili.riquadro}`}>
        <h1 className={stili.titolo}>{t.errore_titolo}</h1>
        <p className={stili.testo}>{t.errore_testo}</p>
        <div className={stili.suggerimenti}>
          <button type="button" className="bottone" onClick={retry}>{t.errore_riprova}</button>
          {voci.map((v) => (
            <Link key={v.href} href={v.href} className="bottone-secondario">{v.etichetta}</Link>
          ))}
        </div>
      </div>
    </div>
  );
}
