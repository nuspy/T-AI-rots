"use client";

/* La stesa in miniatura: le sue posizioni vere, in scala. Serve alla scelta della
 * stesa in una lettura (animata) e alle pagine pubbliche delle stese (ferma: chi legge
 * senza JavaScript, e i crawler, non devono vedere rettangoli invisibili). */

import { motion } from "framer-motion";
import type { Stesa } from "@/lib/api";

export function MiniaturaStesa({
  stesa, animata = false, className,
}: {
  stesa: Stesa;
  animata?: boolean;
  className?: string;
}) {
  return (
    <svg viewBox="0 0 100 64" className={className} aria-hidden="true">
      {stesa.posizioni.map((p, i) => {
        const w = stesa.posizioni.length > 8 ? 6 : 9;
        const h = w * 1.6;
        const comune = {
          x: p.x * 100 - w / 2,
          y: p.y * 64 - h / 2,
          width: w,
          height: h,
          rx: 1.2,
          fill: p.calcolata ? "rgba(185,164,255,0.35)" : "rgba(216,180,90,0.25)",
          stroke: "#d8b45a",
          strokeWidth: 0.6,
          transform: p.rotazione ? `rotate(${p.rotazione} ${p.x * 100} ${p.y * 64})` : undefined,
        };
        return animata ? (
          <motion.rect
            key={p.n}
            {...comune}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 * i, duration: 0.4 }}
          />
        ) : (
          <rect key={p.n} {...comune} />
        );
      })}
    </svg>
  );
}
