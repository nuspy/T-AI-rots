"use client";

/* Le 78 carte del Thoth, pubbliche: ciò che si cerca prima di consultare. */

import { useCallback, useState } from "react";
import Link from "next/link";
import { elencaCarte } from "@/lib/api";
import { useLingua } from "@/lib/lingua";
import { nomeCarta } from "@/lib/i18n";
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
      sottotitolo={t.carte_sottotitolo}>
      <div className={stili.filtri}>
        {FILTRI.map((f) => (
          <button key={f} className={f === filtro ? stili.filtroAttivo : stili.filtro} onClick={() => setFiltro(f)}>
            {t.filtri[f]}
          </button>
        ))}
      </div>
      <div className={stili.griglaCarte}>
        {visibili.map((c) => (
          <Link key={c.id} href={`/carte/${c.id}`} className={stili.cartaLink}>
            <div style={{ width: "100%", aspectRatio: "9 / 16", borderRadius: 8, overflow: "hidden" }}>
              <Faccia carta={c} />
            </div>
            {nomeCarta(c, lingua)}
          </Link>
        ))}
      </div>
    </Involucro>
  );
}
