"use client";

/* Il selettore di mazzo con miniatura (v7, Fase J): riusato nella lettura (mazzo attivo) e nel
 * profilo (mazzo di default). Propone solo i mazzi posseduti dall'utente o gratuiti — mai uno che
 * non si può ancora leggere. La miniatura è dedotta dallo slug (`maj-00`, la prima carta del
 * mazzo), non un campo immagine a parte: decisione presa in fase di piano per non aggiungere
 * colonne al modello `Deck` quando il percorso si può già calcolare. */

import { ESTENSIONE } from "./carta";
import { percorsoCarta } from "@/lib/mazzo-attivo";
import type { Mazzo } from "@/lib/api";
import stili from "./seleziona-mazzo.module.css";

export function miniaturaMazzo(mazzo: Mazzo): string {
  return percorsoCarta(mazzo.predefinito ? null : mazzo.slug, `maj-00.${ESTENSIONE}`);
}

/** Solo i mazzi utilizzabili da questo utente: il predefinito (sempre), i gratuiti (prezzo
 * digitale nullo) e quelli posseduti (`deckIdsPosseduti`). */
export function mazziUtilizzabili(mazzi: Mazzo[], deckIdsPosseduti: number[]): Mazzo[] {
  return mazzi.filter(
    (m) => m.predefinito || m.prezzo_digitale === null || deckIdsPosseduti.includes(m.id),
  );
}

export function SelezionaMazzo({
  mazzi, valore, onCambia, id,
}: {
  mazzi: Mazzo[];
  /** `null` = il mazzo predefinito globale. */
  valore: number | null;
  onCambia: (deckId: number | null) => void;
  id?: string;
}) {
  const scelto = mazzi.find((m) => m.id === valore) ?? mazzi.find((m) => m.predefinito) ?? mazzi[0];

  return (
    <div className={stili.selettore}>
      {scelto && (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={miniaturaMazzo(scelto)} alt="" className={stili.miniatura} draggable={false} />
      )}
      <select
        id={id}
        className={stili.select}
        value={valore ?? ""}
        onChange={(e) => onCambia(e.target.value === "" ? null : Number(e.target.value))}
      >
        {mazzi.map((m) => (
          <option key={m.id} value={m.id}>{m.nome}{m.predefinito ? " (predefinito)" : ""}</option>
        ))}
      </select>
    </div>
  );
}
