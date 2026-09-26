"use client";

/* Il collegamento grafico alla pagina del mazzo: «compra il mazzo con la grafica
 * originale». Sta in fondo alle pagine pubbliche (carte, stese) e in home. Tutta la
 * targa è il collegamento; le carte in ventaglio sono le immagini vere del mazzo. */

import Link from "next/link";
import { DOMINIO } from "@/lib/condivisione";
import { useLingua } from "@/lib/lingua";
import { ESTENSIONE } from "./carta";
import stili from "./banner-mazzo.module.css";

/* Il dorso e tre carte scelte per il colore: la Stella, il Sole, l'Universo. */
const VENTAGLIO = [
  { file: "maj-17", giro: -17 },
  { file: "maj-19", giro: -6 },
  { file: "maj-21", giro: 5 },
  { file: "dorso", giro: 16 },
];

export function BannerMazzo() {
  const { t } = useLingua();
  return (
    <Link href="/mazzo" className={stili.banner}>
      <span className={stili.ventaglio} aria-hidden="true">
        {VENTAGLIO.map((c, i) => (
          // eslint-disable-next-line @next/next/no-img-element -- decorativa, già WebP piccola
          <img
            key={c.file}
            src={`/cards/${c.file}.${ESTENSIONE}`}
            alt=""
            width={90}
            height={160}
            loading="lazy"
            style={{ transform: `rotate(${c.giro}deg)`, zIndex: i }}
          />
        ))}
      </span>
      <span className={stili.testo}>
        <span className={stili.sigillo} aria-hidden="true">✦ ❖ ✦</span>
        <strong>{t.mazzo_banner_titolo(DOMINIO)}</strong>
        <span>{t.mazzo_banner_testo}</span>
      </span>
      <span className={stili.cta}>{t.mazzo_banner_cta} →</span>
    </Link>
  );
}
