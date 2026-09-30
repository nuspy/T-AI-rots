"use client";

/* Il genere di una persona: il menu con le cinque risposte, il testo libero di
 * «Altro» e la casella facoltativa «persona trans», separata dal genere.
 *
 * Lo usano il modulo delle letture speciali (per chi consulta e per l'altra
 * persona) e il profilo. Non c'è un campo sull'orientamento: non serve alla
 * lettura ed è un dato sensibile. «Preferisco non dirlo» è una risposta valida.
 */

import { useId } from "react";
import type { Genere } from "@/lib/api";
import { useLingua } from "@/lib/lingua";
import stili from "./campi.module.css";

const GENERI: Genere[] = ["donna", "uomo", "non_binario", "altro", "non_dice"];

export function CampiGenere({
  genere,
  altro,
  trans,
  onGenere,
  onAltro,
  onTrans,
  errore,
  erroreAltro,
  etichetta,
}: {
  genere: Genere | "";
  altro: string;
  trans: boolean;
  onGenere: (g: Genere | "") => void;
  onAltro: (testo: string) => void;
  onTrans: (v: boolean) => void;
  errore?: string;
  erroreAltro?: string;
  etichetta?: string;
}) {
  const { t } = useLingua();
  const id = useId();
  return (
    <div className={stili.gruppo}>
      <div className={stili.riga}>
        <label className={`${stili.campo} ${errore ? stili.campoErrore : ""}`}>
          {etichetta ?? t.persone_genere}
          <select
            value={genere}
            onChange={(e) => onGenere(e.target.value as Genere | "")}
            aria-invalid={!!errore}
            aria-describedby={errore ? `${id}-errore` : undefined}
          >
            <option value="">{t.persone_genere_scegli}</option>
            {GENERI.map((g) => (
              <option key={g} value={g}>{t.generi[g]}</option>
            ))}
          </select>
          {errore && <span id={`${id}-errore`} className={stili.errore} role="alert">{errore}</span>}
        </label>
        {genere === "altro" && (
          <label className={`${stili.campo} ${erroreAltro ? stili.campoErrore : ""}`}>
            {t.persone_genere_altro}
            <input
              value={altro}
              onChange={(e) => onAltro(e.target.value)}
              maxLength={30}
              dir="auto"
              aria-invalid={!!erroreAltro}
            />
            {erroreAltro && <span className={stili.errore} role="alert">{erroreAltro}</span>}
          </label>
        )}
      </div>
      <label className={stili.casella}>
        <input type="checkbox" checked={trans} onChange={(e) => onTrans(e.target.checked)} />
        {t.persone_trans}
      </label>
    </div>
  );
}
