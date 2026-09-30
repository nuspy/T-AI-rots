"use client";

/* Le carte di un mazzo, prima di comprarlo: le 78 miniature raccolte per gruppo (Arcani maggiori, poi i quattro
 * semi), e un tocco su una carta la ingrandisce, con la precedente e la successiva a portata di dito (e di freccia
 * da tastiera). Le immagini si caricano quando entrano nella vista: aprire la finestra non scarica il mazzo intero. */

import { useEffect, useState } from "react";
import { elencaCarte, type Carta, type Mazzo } from "@/lib/api";
import { nomeDi } from "@/v2/pagine/carte";
import { f, plurale } from "@/v2/i18n";
import { ImmagineCarta } from "./carta";
import { Modale } from "./modale";
import { linguaContenuti } from "@/v2/lib/dati";
import { useLingua } from "@/v2/lib/lingua";
import { useCarica } from "@/v2/lib/usa";

const GRUPPI = ["maggiori", "bastoni", "coppe", "spade", "dischi"] as const;
const gruppoDi = (c: Carta) => (c.arcano === "maggiore" ? "maggiori" : (c.seme ?? "maggiori"));

export function GalleriaMazzo({ mazzo, onChiudi }: { mazzo: Mazzo; onChiudi: () => void }) {
  const { t, lingua } = useLingua();
  const k = t.negozio;
  const carte = useCarica(() => elencaCarte(linguaContenuti(lingua)), [lingua], { pubblico: true });
  const elenco = carte.dati ?? [];
  const [zoom, setZoom] = useState<number | null>(null);
  /* Il Thoth vive in `/cards/`, gli altri mazzi in `/cards/<slug>/`. */
  const cartella = mazzo.predefinito ? null : mazzo.slug;
  const inZoom = zoom != null ? elenco[zoom] : null;

  useEffect(() => {
    if (zoom == null) return;
    const tasto = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight") setZoom((z) => (z == null ? z : (z + 1) % elenco.length));
      if (e.key === "ArrowLeft") setZoom((z) => (z == null ? z : (z - 1 + elenco.length) % elenco.length));
    };
    document.addEventListener("keydown", tasto);
    return () => document.removeEventListener("keydown", tasto);
  }, [zoom, elenco.length]);

  return (
    <Modale aperta titolo={inZoom ? nomeDi(inZoom, lingua) : f(k.galleria_titolo, { mazzo: mazzo.nome })} onChiudi={onChiudi} larga>
      {carte.errore && <p className="error">{carte.errore}</p>}
      {!carte.dati && !carte.errore && <p className="muted">{t.comune.carica}</p>}
      {inZoom ? (
        <div className="deck-zoom">
          <ImmagineCarta id={inZoom.id} alt={nomeDi(inZoom, lingua)} mazzo={cartella} priorita />
          <div className="button-row deck-zoom-nav">
            <button type="button" className="button button-quiet button-small"
              onClick={() => setZoom((zoom! - 1 + elenco.length) % elenco.length)}>← {k.galleria_prec}</button>
            <button type="button" className="button button-small" onClick={() => setZoom(null)}>{k.galleria_torna}</button>
            <button type="button" className="button button-quiet button-small"
              onClick={() => setZoom((zoom! + 1) % elenco.length)}>{k.galleria_succ} →</button>
          </div>
        </div>
      ) : (
        <>
          {elenco.length > 0 && <p className="small muted">{plurale(elenco.length, t.carte.n_carte)} · {k.galleria_nota}</p>}
          <nav className="chips deck-gallery-jump" aria-label={k.galleria_gruppi}>
            {GRUPPI.map((g) => (
              <button key={g} type="button" className="chip"
                onClick={() => document.getElementById(`galleria-${g}`)?.scrollIntoView({ behavior: "smooth", block: "start" })}>
                {t.carte.filtri[g]}
              </button>
            ))}
          </nav>
          {GRUPPI.map((g) => {
            const gruppo = elenco.map((c, i) => ({ c, i })).filter(({ c }) => gruppoDi(c) === g);
            if (!gruppo.length) return null;
            return (
              <section key={g} id={`galleria-${g}`} className="deck-gallery-group" aria-label={t.carte.filtri[g]}>
                <h3>{t.carte.filtri[g]}</h3>
                <div className="deck-gallery">
                  {gruppo.map(({ c, i }) => (
                    <button key={c.id} type="button" className="deck-thumb" onClick={() => setZoom(i)}
                      title={nomeDi(c, lingua)} aria-label={f(k.galleria_ingrandisci, { carta: nomeDi(c, lingua) })}>
                      <ImmagineCarta id={c.id} alt="" mazzo={cartella} />
                    </button>
                  ))}
                </div>
              </section>
            );
          })}
        </>
      )}
    </Modale>
  );
}
