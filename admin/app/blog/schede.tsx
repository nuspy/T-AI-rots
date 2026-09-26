"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import stili from "./blog.module.css";

const PARTI = [
  { href: "/blog", etichetta: "Articoli" },
  { href: "/blog/sezioni", etichetta: "Sezioni" },
  { href: "/blog/immagini", etichetta: "Immagini" },
  { href: "/blog/etichette", etichetta: "Etichette" },
];

/* Le parti del blog, una sotto l'altra nella navigazione principale ma qui affiancate: la console ha una voce
 * sola, «Blog», e il resto sta dentro. */
export function Schede() {
  const percorso = usePathname();
  return (
    <nav className={stili.schede} aria-label="Parti del blog">
      {PARTI.map((p) => {
        const attiva = p.href === "/blog" ? percorso === "/blog" : percorso.startsWith(p.href);
        return (
          <Link
            key={p.href}
            href={p.href}
            className={attiva ? stili.schedaAttiva : stili.scheda}
            aria-current={attiva ? "page" : undefined}
          >
            {p.etichetta}
          </Link>
        );
      })}
    </nav>
  );
}
