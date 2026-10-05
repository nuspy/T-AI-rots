/* La stesa in miniatura: le sue posizioni vere, in scala, in ottone su prugna. Le posizioni calcolate (la sintesi
 * della Croce semplice) in verderame. */

import type { Posizione } from "@/lib/api";

/** Basta la geometria delle posizioni: una `Stesa` dell'API o un elemento di una sezione «stese» del Journal. */
type PosizioneSchema = Pick<Posizione, "n" | "x" | "y"> & Partial<Pick<Posizione, "rotazione" | "calcolata">>;

export function MiniaturaStesa({ stesa, className }: { stesa: { posizioni: PosizioneSchema[] }; className?: string }) {
  return (
    <svg viewBox="0 0 100 64" className={className} aria-hidden="true">
      {stesa.posizioni.map((p) => {
        const w = stesa.posizioni.length > 8 ? 6 : 9;
        const h = w * 1.6;
        return (
          <rect
            key={p.n}
            x={p.x * 100 - w / 2}
            y={p.y * 64 - h / 2}
            width={w}
            height={h}
            fill={p.calcolata ? "rgba(25,112,111,.55)" : "rgba(214,182,109,.28)"}
            stroke="#d6b66d"
            strokeWidth={0.6}
            transform={p.rotazione ? `rotate(${p.rotazione} ${p.x * 100} ${p.y * 64})` : undefined}
          />
        );
      })}
    </svg>
  );
}
