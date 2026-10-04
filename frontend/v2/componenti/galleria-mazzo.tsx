"use client";

/* Le carte di un mazzo, prima di comprarlo: le 78 miniature raccolte per gruppo (Arcani maggiori, poi i quattro
 * semi). I pulsanti dei gruppi filtrano (v8.5: non fanno scorrere). Un tocco su una carta la ingrandisce: un tocco
 * qualunque sull'ingrandimento torna alle carte, le frecce ai lati (e da tastiera) passano alla precedente e alla
 * successiva del gruppo mostrato. Le immagini si caricano quando entrano nella vista.
 *
 * Con una carta ingrandita, anche la X, Esc e il tocco fuori dalla finestra tornano alle carte (non alla pagina):
 * la finestra si chiude solo dalla griglia. Tornando, la griglia riporta in vista la carta appena guardata. */

import { useEffect, useRef, useState } from "react";
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
  const [filtro, setFiltro] = useState<"tutte" | (typeof GRUPPI)[number]>("tutte");
  const elenco = (carte.dati ?? []).filter((c) => filtro === "tutte" || gruppoDi(c) === filtro);
  const [zoom, setZoom] = useState<number | null>(null);
  /* Il Thoth vive in `/cards/`, gli altri mazzi in `/cards/<slug>/`. */
  const cartella = mazzo.predefinito ? null : mazzo.slug;
  const inZoom = zoom != null ? elenco[zoom] : null;
  /* L'ultima carta ingrandita: tornando alla griglia la si riporta in vista (e prende il fuoco). */
  const ultima = useRef<string | null>(null);
  const idInZoom = inZoom?.id ?? null;
  useEffect(() => {
    if (idInZoom) ultima.current = idInZoom;
  }, [idInZoom]);

  useEffect(() => {
    if (zoom != null || !ultima.current) return;
    const el = document.querySelector<HTMLElement>(`[data-carta-galleria="${ultima.current}"]`);
    el?.scrollIntoView({ block: "center" });
    el?.focus({ preventScroll: true });
  }, [zoom]);

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
    <Modale aperta titolo={inZoom ? nomeDi(inZoom, lingua) : f(k.galleria_titolo, { mazzo: mazzo.nome })} onChiudi={inZoom ? () => setZoom(null) : onChiudi} larga>
      {carte.errore && <p className="error">{carte.errore}</p>}
      {!carte.dati && !carte.errore && <p className="muted">{t.comune.carica}</p>}
      {inZoom ? (
        <div className="deck-zoom">
          {/* Un tocco qualunque sull'ingrandimento torna alle carte. */}
          <button type="button" className="deck-zoom-carta" onClick={() => setZoom(null)} aria-label={k.galleria_torna}>
            <ImmagineCarta id={inZoom.id} alt={nomeDi(inZoom, lingua)} mazzo={cartella} priorita />
          </button>
          <button type="button" className="deck-zoom-freccia deck-zoom-prec" aria-label={k.galleria_prec}
            onClick={() => setZoom((zoom! - 1 + elenco.length) % elenco.length)}>←</button>
          <button type="button" className="deck-zoom-freccia deck-zoom-succ" aria-label={k.galleria_succ}
            onClick={() => setZoom((zoom! + 1) % elenco.length)}>→</button>
        </div>
      ) : (
        <>
          {elenco.length > 0 && <p className="small muted">{plurale(elenco.length, t.carte.n_carte)} · {k.galleria_nota}</p>}
          <div className="chips deck-gallery-jump" role="group" aria-label={k.galleria_gruppi}>
            {(["tutte", ...GRUPPI] as const).map((g) => (
              <button key={g} type="button" className="chip" aria-pressed={filtro === g}
                onClick={() => { setFiltro(g); setZoom(null); }}>
                {t.carte.filtri[g]}
              </button>
            ))}
          </div>
          {GRUPPI.map((g) => {
            const gruppo = elenco.map((c, i) => ({ c, i })).filter(({ c }) => gruppoDi(c) === g);
            if (!gruppo.length) return null;
            return (
              <section key={g} id={`galleria-${g}`} className="deck-gallery-group" aria-label={t.carte.filtri[g]}>
                <h3>{t.carte.filtri[g]}</h3>
                <div className="deck-gallery">
                  {gruppo.map(({ c, i }) => (
                    <button key={c.id} type="button" className="deck-thumb" onClick={() => setZoom(i)} data-carta-galleria={c.id}
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
