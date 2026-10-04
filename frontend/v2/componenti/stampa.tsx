"use client";

/* La stampa di una lettura (v8.5): «Stampa in PDF» apre la stampa del browser, che su computer e telefono offre
 * «Salva come PDF». Il foglio di stampa (`@media print` in v2.css) toglie testata, piede, barra dell'oracolo e
 * pulsanti, e mostra ciò che serve sulla carta: la domanda, le carte una per una con la loro spiegazione,
 * l'interpretazione, la nota di copyright. */

import type { Stesa } from "@/lib/api";
import { nomeCarta, nomePosizione } from "@/lib/i18n/nomi";
import type { Posata } from "@/v2/lettura/tavolo";
import { useLingua, useLinguaNomi } from "@/v2/lib/lingua";

export function PulsanteStampa({ etichetta, piccolo = false }: { etichetta: string; piccolo?: boolean }) {
  return (
    <button type="button" className={`button button-quiet ${piccolo ? "button-small" : ""} non-stampare`}
      onClick={() => window.print()} data-an="stampa_pdf">
      <span aria-hidden="true">⎙</span> {etichetta}
    </button>
  );
}

/** Le carte della lettura, una per una, solo nella stampa (sullo schermo stanno sul tavolo e nella conversazione). */
export function CarteDaStampare({ stesa, posate }: { stesa: Stesa; posate: Posata[] }) {
  const { t } = useLingua();
  const ll = useLinguaNomi();
  const rivelate = [...posate].filter((p) => p.rivelata && p.carta).sort((a, b) => a.posizione - b.posizione);
  if (!rivelate.length) return null;
  return (
    <section className="solo-stampa stampa-carte" aria-hidden="true">
      {rivelate.map((p) => {
        const pos = stesa.posizioni.find((x) => x.n === p.posizione);
        return (
          <article key={p.posizione} className="stampa-carta">
            <h3>
              {p.posizione}. {pos ? nomePosizione(pos, ll) : ""} — {nomeCarta(p.carta!, ll)}
              {p.rovescio ? ` (${t.lettura.rovesciata})` : ""}
            </h3>
            {p.interpretazione && <p dir="auto">{p.interpretazione}</p>}
          </article>
        );
      })}
    </section>
  );
}

/** La nota di copyright in fondo alla stampa. */
export function NotaStampa({ anno }: { anno?: string | null }) {
  return <p className="solo-stampa stampa-nota">© {anno ? `${anno} ` : ""}TAROTS chat · tarots.chat</p>;
}
