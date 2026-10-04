"use client";

/* Le file di sotto-tab della console, uguali in ogni sezione che ne ha (Advertisements, App mobili…): ogni sezione
 * tiene il suo elenco di voci e lo passa a `Fila`, montata nel suo `layout.tsx`. */

import Link from "next/link";
import { usePathname } from "next/navigation";
import stili from "./schede-comuni.module.css";

export interface Voce {
  href: string;
  etichetta: string;
}

/** Una fila di schede: la voce attiva è quella col prefisso più lungo che corrisponde all'indirizzo. */
export function Fila({ voci, etichetta, piccola = false }: { voci: Voce[]; etichetta: string; piccola?: boolean }) {
  const percorso = usePathname();
  const attiva = voci
    .filter((v) => percorso === v.href || percorso.startsWith(`${v.href}/`))
    .sort((a, b) => b.href.length - a.href.length)[0]?.href;
  return (
    <nav className={piccola ? stili.schedeInterne : stili.schede} aria-label={etichetta}>
      {voci.map((v) => (
        <Link
          key={v.href}
          href={v.href}
          className={v.href === attiva ? stili.schedaAttiva : stili.scheda}
          aria-current={v.href === attiva ? "page" : undefined}
        >
          {v.etichetta}
        </Link>
      ))}
    </nav>
  );
}
