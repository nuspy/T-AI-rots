"use client";

/* L'apertura delle pagine interne (il «subhero» del prototipo): occhiello, titolo, introduzione. I testi stanno
 * nella sezione del dizionario della pagina (`eyebrow`, `titolo`, `intro`; `intro_dentro` se chi è entrato deve
 * leggere altro). */

import { useSessione } from "@/lib/sessione";
import type { Dizionario } from "@/v2/i18n";
import { useLingua } from "@/v2/lib/lingua";

type ConApertura = { eyebrow: string; titolo: string; intro: string; intro_dentro?: string };
type Sezioni = { [K in keyof Dizionario]: Dizionario[K] extends ConApertura ? K : never }[keyof Dizionario];

export function Sottotitolo({
  sezione, compatto = false, children,
}: {
  sezione: Sezioni;
  compatto?: boolean;
  children?: React.ReactNode;
}) {
  const { t } = useLingua();
  const { autenticata } = useSessione();
  const s = t[sezione] as ConApertura;
  return (
    <section className={`subhero ${compatto ? "subhero-compact" : ""}`}>
      <p className="eyebrow">{s.eyebrow}</p>
      <h1 className="display">{s.titolo}</h1>
      <p className="section-intro">{autenticata && s.intro_dentro ? s.intro_dentro : s.intro}</p>
      {children}
    </section>
  );
}
