"use client";

/* Le carte svelate (v8.5): una per una, con la loro spiegazione, prima dell'interpretazione dell'insieme. Mentre
 * le carte si girano, la spiegazione arriva in streaming; la carta in arrivo ha il cursore. Prima stavano nella
 * conversazione: ora stanno dove si legge il risultato, e si stampano con esso. Dalla v8.6 le carte si girano tutte
 * insieme e il lettore le legge con una chiamata sola: un solo avviso d'attesa per tutte, finché non arriva il primo
 * pezzo di testo. Dal 9/10 i testi crescono mentre il modello li scrive, anche alternando le carte: il cursore sta
 * sulla carta che sta crescendo (`inScrittura`), e quella carta porta `data-in-scrittura` (la chat la segue). */

import type { Stesa } from "@/lib/api";
import { nomeCarta, nomePosizione } from "@/lib/i18n/nomi";
import { ImmagineCarta } from "@/v2/componenti/carta";
import { useLingua, useLinguaNomi } from "@/v2/lib/lingua";
import stili from "./lettura.module.css";
import type { Posata } from "./tavolo";

export function CarteSvelate({ stesa, posate, attiva, lettoreLegge = false, inScrittura = null }: {
  stesa: Stesa; posate: Posata[]; attiva: boolean;
  /* Le carte sono girate e il lettore le sta leggendo tutte insieme: un solo avviso d'attesa, nessun cursore. */
  lettoreLegge?: boolean;
  /* La posizione il cui testo sta arrivando adesso; se non si sa, il cursore va sulla prima carta ancora vuota (e
   * nessun cursore quando le carte hanno tutte il loro testo: allora si scrive il responso). */
  inScrittura?: number | null;
}) {
  const { t } = useLingua();
  const ll = useLinguaNomi();
  const rivelate = [...posate].filter((p) => p.rivelata && p.carta).sort((a, b) => a.posizione - b.posizione);
  if (!rivelate.length) return null;
  const inArrivo = inScrittura ?? rivelate.find((p) => !p.interpretazione)?.posizione ?? null;
  const cursore = attiva && !lettoreLegge && inArrivo !== null;
  return (
    <section className={stili.carteSvelate} aria-labelledby="titolo-carte-svelate" aria-live="polite" aria-busy={cursore}>
      <h2 id="titolo-carte-svelate" className={stili.carteSvelateTitolo}>{t.lettura.carte_svelate}</h2>
      {lettoreLegge && (
        <p className={stili.lettoreLegge} role="status">
          <span className={stili.lettoreLeggePunti} aria-hidden="true"><i /><i /><i /></span>
          {t.lettura.lettore_legge}
        </p>
      )}
      <ol>
        {rivelate.map((p) => {
          const pos = stesa.posizioni.find((x) => x.n === p.posizione);
          const nome = nomeCarta(p.carta!, ll);
          const scrive = cursore && p.posizione === inArrivo;
          return (
            <li key={p.posizione} className={stili.cartaSvelata} data-in-scrittura={scrive ? "carta" : undefined}>
              <ImmagineCarta id={p.carta!.id} alt={nome} classe={`${stili.cartaSvelataImmagine} ${p.rovescio ? stili.rovescia : ""}`} />
              <div>
                <p className={stili.cartaSvelataPosto}>{p.posizione}. {pos ? nomePosizione(pos, ll) : ""}</p>
                <h3>{nome}{p.rovescio ? ` · ${t.lettura.rovesciata}` : ""}</h3>
                <p dir="auto">
                  {p.interpretazione}
                  {scrive && <span className={stili.cursore} aria-hidden="true">▍</span>}
                </p>
              </div>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
