"use client";

/* Le carte d'esempio di un candidato al voto (fino a cinque, nell'ordine scelto in console): una fila di miniature;
 * un tocco ne apre l'ingrandimento nel dialogo della v2 (Esc chiude, il fuoco torna sulla miniatura), le frecce
 * ai lati e quelle della tastiera passano alla precedente e alla successiva, un tocco sulla carta grande chiude.
 * Le immagini stanno nell'API (`/blog/media/…`): la miniatura per la fila, la grande per l'ingrandimento. */

import { useEffect, useState } from "react";
import type { CampioneVoto } from "@/lib/api";
import { urlMedia } from "@/lib/blog";
import { f } from "@/v2/i18n";
import { useLingua } from "@/v2/lib/lingua";
import { Modale } from "./modale";
import stili from "./campioni-voto.module.css";

export function CampioniVoto({ nome, campioni }: { nome: string; campioni: CampioneVoto[] }) {
  const { t } = useLingua();
  const k = t.mazzi;
  const validi = campioni.filter((c): c is CampioneVoto & { url: string } => Boolean(c.url));
  const [zoom, setZoom] = useState<number | null>(null);
  const totale = validi.length;

  useEffect(() => {
    if (zoom == null || totale < 2) return;
    const tasto = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight") setZoom((z) => (z == null ? z : (z + 1) % totale));
      if (e.key === "ArrowLeft") setZoom((z) => (z == null ? z : (z - 1 + totale) % totale));
    };
    document.addEventListener("keydown", tasto);
    return () => document.removeEventListener("keydown", tasto);
  }, [zoom, totale]);

  if (totale === 0) return null;
  const inZoom = zoom != null ? validi[zoom] : null;

  return (
    <>
      <ul className={stili.fila} aria-label={f(k.campioni_titolo, { mazzo: nome })}>
        {validi.map((c, i) => (
          <li key={c.url}>
            <button type="button" className={stili.miniatura} onClick={() => setZoom(i)}
              aria-label={f(k.campione_ingrandisci, { n: i + 1, mazzo: nome })}>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={urlMedia(c.mini ?? c.url) ?? undefined} alt="" width={90} height={160} loading="lazy" decoding="async" />
            </button>
          </li>
        ))}
      </ul>
      {inZoom && zoom != null && (
        <Modale aperta titolo={f(k.campione_zoom, { mazzo: nome, n: zoom + 1, tot: totale })} onChiudi={() => setZoom(null)}>
          <div className="deck-zoom">
            <button type="button" className="deck-zoom-carta" onClick={() => setZoom(null)} aria-label={k.campione_chiudi}>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={urlMedia(inZoom.url) ?? undefined} alt={inZoom.etichetta ?? f(k.campione_zoom, { mazzo: nome, n: zoom + 1, tot: totale })}
                width={360} height={640} decoding="async" />
            </button>
            {totale > 1 && (
              <>
                <button type="button" className="deck-zoom-freccia deck-zoom-prec" aria-label={t.negozio.galleria_prec}
                  onClick={() => setZoom((zoom - 1 + totale) % totale)}>←</button>
                <button type="button" className="deck-zoom-freccia deck-zoom-succ" aria-label={t.negozio.galleria_succ}
                  onClick={() => setZoom((zoom + 1) % totale)}>→</button>
              </>
            )}
          </div>
          {inZoom.etichetta && <p className={`small muted ${stili.contatore}`}>{inZoom.etichetta}</p>}
        </Modale>
      )}
    </>
  );
}
