"use client";

/* I pezzi di modulo comuni a un coupon e a un lotto (v9, Fase 2d): i piani a cui vale, la durata sugli abbonamenti, il
 * cumulo con gli sconti del rinnovo automatico e della prova, la campagna. */

import type { DurataCoupon } from "@/lib/offerte";
import comuni from "../comuni.module.css";
import stili from "./coupon.module.css";

export function SceltaPiani({
  piani, scelti, cambia,
}: {
  piani: { slug: string; nome: string }[];
  scelti: string[];
  cambia: (v: string[]) => void;
}) {
  return (
    <fieldset className={stili.gruppo}>
      <legend className={comuni.campoEtichetta}>Vale per</legend>
      <div className={stili.sceltePiani}>
        {piani.map((p) => (
          <label key={p.slug} className={stili.spunta}>
            <input
              type="checkbox"
              checked={scelti.includes(p.slug)}
              onChange={(e) => cambia(e.target.checked ? [...scelti, p.slug] : scelti.filter((s) => s !== p.slug))}
            />
            {p.nome}
          </label>
        ))}
      </div>
      <span className={comuni.campoAiuto}>Nessuna spunta: tutte le offerte.</span>
    </fieldset>
  );
}

export interface Regole {
  durata: DurataCoupon;
  periodi: string;
  cumulabile: boolean;
}

/** Quanti pagamenti di un abbonamento sconta, e se si somma agli altri sconti. Non vale per i codici regalo. */
export function CampiRegole({ regole, cambia, bloccate = false }: {
  regole: Regole; cambia: (r: Regole) => void; bloccate?: boolean;
}) {
  return (
    <fieldset className={stili.gruppo} disabled={bloccate}>
      <legend className={comuni.campoEtichetta}>Sugli abbonamenti</legend>
      <div className={comuni.riga}>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Durata dello sconto</span>
          <select
            className={comuni.selezione}
            value={regole.durata}
            onChange={(e) => cambia({ ...regole, durata: e.target.value as DurataCoupon })}
          >
            <option value="una_volta">Solo il primo pagamento</option>
            <option value="periodi">Per N pagamenti</option>
            <option value="sempre">Per sempre (ogni rinnovo)</option>
          </select>
        </label>
        {regole.durata === "periodi" && (
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Quanti pagamenti</span>
            <input
              className={comuni.ingresso} type="number" min={2} max={36} inputMode="numeric" value={regole.periodi}
              onChange={(e) => cambia({ ...regole, periodi: e.target.value })}
            />
            <span className={comuni.campoAiuto}>Il primo compreso: 3 = «−30% per 3 mesi» su un mensile.</span>
          </label>
        )}
      </div>
      <label className={stili.spunta}>
        <input type="checkbox" checked={regole.cumulabile} onChange={(e) => cambia({ ...regole, cumulabile: e.target.checked })} />
        Cumulabile con lo sconto del rinnovo automatico e della prova
      </label>
      <span className={comuni.campoAiuto}>
        Non cumulabile (di default): vale lo sconto più alto per l&apos;utente, e il sito dice quale. Cumulabile: si
        sommano, al centesimo. Durata e cumulo non cambiano più dopo il primo uso.
      </span>
    </fieldset>
  );
}

/** Le regole come le vuole il backend: `periodi` solo per «per N pagamenti». `null` se il numero non va. */
export function regoleDaInviare(r: Regole): { durata: DurataCoupon; periodi: number | null; cumulabile: boolean } | null {
  if (r.durata !== "periodi") return { durata: r.durata, periodi: null, cumulabile: r.cumulabile };
  const n = Number(r.periodi);
  if (!Number.isInteger(n) || n < 2 || n > 36) return null;
  return { durata: r.durata, periodi: n, cumulabile: r.cumulabile };
}

export function CampoCampagna({ valore, cambia, suggerite, obbligatoria = false }: {
  valore: string; cambia: (v: string) => void; suggerite: string[]; obbligatoria?: boolean;
}) {
  return (
    <label className={comuni.campo}>
      <span className={comuni.campoEtichetta}>Campagna{obbligatoria ? "" : " (facoltativa)"}</span>
      <input
        className={comuni.ingresso} value={valore} maxLength={80} required={obbligatoria} list="campagne-note"
        onChange={(e) => cambia(e.target.value)} placeholder="es. newsletter-ottobre, influencer-x"
      />
      <datalist id="campagne-note">
        {suggerite.map((c) => <option key={c} value={c} />)}
      </datalist>
      <span className={comuni.campoAiuto}>Testo libero: il resoconto raggruppa i coupon per campagna.</span>
    </label>
  );
}
