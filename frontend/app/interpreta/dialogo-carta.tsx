"use client";

/* Il dialogo di "Interpreta i miei tarocchi" (v5): due passi, in testo — mai una griglia di
 * immagini, per restare leggero e navigabile anche su mobile.
 *
 *   1. seme: Arcani Maggiori, Bastoni, Coppe, Spade, Dischi — un elenco puntato con icona.
 *   2. carta: le carte di quel seme, un elenco puntato selezionabile; le già assegnate ad altre
 *      posizioni appaiono disattivate (un mazzo fisico non può ripetere una carta). Bottoni
 *      "Indietro" (torna al passo 1) e "OK" (conferma), come da specifica.
 */

import { useState } from "react";
import type { Carta } from "@/lib/api";
import { nomeCarta } from "@/lib/i18n";
import { useLingua } from "@/lib/lingua";
import { Modale } from "../componenti/modale";
import stili from "./interpreta.module.css";

type Seme = "maggiori" | "bastoni" | "coppe" | "spade" | "dischi";
const SEMI: { chiave: Seme; icona: string }[] = [
  { chiave: "maggiori", icona: "✦" },
  { chiave: "bastoni", icona: "🔥" },
  { chiave: "coppe", icona: "💧" },
  { chiave: "spade", icona: "⚔" },
  { chiave: "dischi", icona: "☉" },
];

export function DialogoCarta({
  aperta, nomePosizione, carte, occupate, onConferma, onChiudi,
}: {
  aperta: boolean;
  nomePosizione: string;
  carte: Carta[];
  /* Id già assegnati ad altre posizioni: appaiono disattivati nell'elenco. */
  occupate: Set<string>;
  onConferma: (cardId: string) => void;
  onChiudi: () => void;
}) {
  const { t, lingua } = useLingua();
  const [seme, setSeme] = useState<Seme | null>(null);
  const [scelta, setScelta] = useState<string | null>(null);

  const chiudi = () => {
    setSeme(null);
    setScelta(null);
    onChiudi();
  };

  const visibili = seme
    ? carte.filter((c) => (seme === "maggiori" ? c.arcano === "maggiore" : c.seme === seme))
    : [];

  return (
    <Modale aperta={aperta} titolo={`${nomePosizione}: ${seme ? t.interpreta_dialogo_carta_titolo : t.interpreta_dialogo_seme_titolo}`} onChiudi={chiudi}>
      {!seme && (
        <ul className={stili.semiElenco}>
          {SEMI.map((s) => (
            <li key={s.chiave}>
              <button type="button" className={stili.semeVoce} onClick={() => setSeme(s.chiave)}>
                <span aria-hidden="true">{s.icona}</span> {t.filtri[s.chiave]}
              </button>
            </li>
          ))}
        </ul>
      )}

      {seme && (
        <>
          <ul className={stili.carteElenco}>
            {visibili.map((c) => {
              const occupata = occupate.has(c.id) && scelta !== c.id;
              return (
                <li key={c.id}>
                  <button
                    type="button"
                    className={c.id === scelta ? stili.carteVoceScelta : stili.carteVoce}
                    disabled={occupata}
                    aria-pressed={c.id === scelta}
                    onClick={() => setScelta(c.id)}
                  >
                    {nomeCarta(c, lingua)}
                  </button>
                </li>
              );
            })}
          </ul>
          <div className={stili.dialogoAzioni}>
            <button type="button" className="bottone-secondario" onClick={() => { setSeme(null); setScelta(null); }}>
              {t.indietro}
            </button>
            <button
              type="button"
              className="bottone"
              disabled={!scelta}
              onClick={() => { if (scelta) { onConferma(scelta); chiudi(); } }}
            >
              {t.interpreta_conferma}
            </button>
          </div>
        </>
      )}
    </Modale>
  );
}
