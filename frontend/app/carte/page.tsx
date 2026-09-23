"use client";

/* Le 78 carte del Thoth, pubbliche: ciò che si cerca prima di consultare. */

import { useCallback, useState } from "react";
import Link from "next/link";
import { elencaCarte } from "@/lib/api";
import { useLingua } from "@/lib/lingua";
import { useCarica } from "@/lib/usa";
import { Faccia } from "../componenti/carta";
import { Involucro } from "../componenti/testata";
import stili from "../pagine.module.css";

const FILTRI = ["tutte", "maggiori", "bastoni", "coppe", "spade", "dischi"] as const;

export default function PaginaCarte() {
  const { t, lingua } = useLingua();
  const carte = useCarica(useCallback(() => elencaCarte(), []), [], { pubblico: true });
  const [filtro, setFiltro] = useState<(typeof FILTRI)[number]>("tutte");
  const visibili = (carte.dati ?? []).filter((c) =>
    filtro === "tutte" ? true : filtro === "maggiori" ? c.arcano === "maggiore" : c.seme === filtro,
  );
  return (
    <Involucro pubblica titolo={t.nav_carte}
      sottotitolo={lingua === "en"
        ? "The 78 cards of the Thoth Tarot with their attributions and meanings on several levels."
        : "Le 78 carte del Tarocco di Thoth con le loro attribuzioni e i significati sui diversi livelli."}>
      <div className={stili.filtri}>
        {FILTRI.map((f) => (
          <button key={f} className={f === filtro ? stili.filtroAttivo : stili.filtro} onClick={() => setFiltro(f)}>
            {f}
          </button>
        ))}
      </div>
      <div className={stili.griglaCarte}>
        {visibili.map((c) => (
          <Link key={c.id} href={`/carte/${c.id}`} className={stili.cartaLink}>
            <div style={{ width: "100%", aspectRatio: "3 / 5", borderRadius: 8, overflow: "hidden" }}>
              <Faccia carta={c} />
            </div>
            {c.nome_it}
          </Link>
        ))}
      </div>
    </Involucro>
  );
}
