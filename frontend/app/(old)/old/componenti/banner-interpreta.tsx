"use client";

/* Il collegamento alla lettura da mazzo fisico (v5, "Interpreta i miei tarocchi"): una funzione
 * unica del sito, promossa in home una volta costruita — non prima (vedi docs/backlog-v5.md).
 * Stessa targa visiva di BannerMazzo, per coerenza. */

import Link from "@/app/(old)/old/componenti/link";
import { useLingua } from "@/lib/lingua";
import { ESTENSIONE } from "./carta";
import stili from "./banner-mazzo.module.css";

const VENTAGLIO = [
  { file: "maj-01", giro: -17 },
  { file: "maj-02", giro: -6 },
  { file: "maj-00", giro: 5 },
  { file: "dorso", giro: 16 },
];

export function BannerInterpreta() {
  const { t } = useLingua();
  return (
    <Link href="/interpreta" className={stili.banner}>
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
        <strong>{t.interpreta_promo_titolo}</strong>
        <span>{t.interpreta_promo_testo}</span>
      </span>
      <span className={stili.cta}>{t.interpreta_promo_cta} →</span>
    </Link>
  );
}
