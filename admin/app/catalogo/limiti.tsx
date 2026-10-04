"use client";

/* I limiti nuovi degli abbonamenti (v9, Fase 2b): oltre alle letture al giorno, alla settimana, al mese e totali del
 * periodo pagato. Le finestre sono mobili (ultime 24 ore, 7 giorni, 30 giorni); «totali» vale dall'inizio del periodo
 * pagato alla sua fine. Vuoto o −1: nessun limite. Oltre un limite il sito chiede il consenso a usare un credito, e le
 * prime letture oltre il limite (dalla console «Abbonamenti») sono regalate. */

import comuni from "../comuni.module.css";

export const LIMITI_NUOVI = [
  { chiave: "letture_alla_settimana", etichetta: "Letture alla settimana", breve: "a settimana" },
  { chiave: "letture_al_mese", etichetta: "Letture al mese", breve: "al mese" },
  { chiave: "letture_totali", etichetta: "Letture totali del periodo pagato", breve: "per periodo" },
] as const;

export type ChiaveLimite = (typeof LIMITI_NUOVI)[number]["chiave"];
export type ValoriLimiti = Record<ChiaveLimite, string>;

export function valoriLimiti(limiti: Record<string, unknown>): ValoriLimiti {
  const v = (k: ChiaveLimite) => (typeof limiti[k] === "number" ? String(limiti[k]) : "");
  return { letture_alla_settimana: v("letture_alla_settimana"), letture_al_mese: v("letture_al_mese"), letture_totali: v("letture_totali") };
}

/** I limiti da mandare: vuoto = senza limite (−1). `null` e il problema se un valore non è un intero da −1 in su. */
export function limitiDaValori(valori: ValoriLimiti): { limiti: Record<ChiaveLimite, number> } | { problema: string } {
  const limiti = {} as Record<ChiaveLimite, number>;
  for (const l of LIMITI_NUOVI) {
    const testo = valori[l.chiave].trim();
    const n = testo === "" ? -1 : Number(testo);
    if (!Number.isInteger(n) || n < -1) return { problema: `«${l.etichetta}»: un intero da 0 in su, −1 o vuoto per nessun limite.` };
    limiti[l.chiave] = n;
  }
  return { limiti };
}

/** Il riassunto dei limiti nella scheda del piano: «3 al giorno · 15 a settimana». */
export function testoLimiti(limiti: Record<string, unknown>): string {
  const giorno = limiti.letture_al_giorno;
  const parti: string[] = [];
  if (typeof giorno === "number") parti.push(giorno < 0 ? "illimitate al giorno" : `${giorno} al giorno`);
  for (const l of LIMITI_NUOVI) {
    const n = limiti[l.chiave];
    if (typeof n === "number" && n >= 0) parti.push(`${n} ${l.breve}`);
  }
  return parti.join(" · ") || "—";
}

export function CampiLimiti({ valori, onCambia }: { valori: ValoriLimiti; onCambia: (v: ValoriLimiti) => void }) {
  return (
    <div className={comuni.riga}>
      {LIMITI_NUOVI.map((l) => (
        <label key={l.chiave} className={comuni.campo}>
          <span className={comuni.campoEtichetta}>{l.etichetta}</span>
          <input className={comuni.ingresso} type="number" min={-1} step={1} value={valori[l.chiave]} placeholder="nessun limite"
            onChange={(e) => onCambia({ ...valori, [l.chiave]: e.target.value })} />
          <span className={comuni.campoAiuto}>{l.chiave === "letture_totali" ? "Dall'inizio alla fine del periodo pagato." : "Finestra mobile."} Vuoto: nessun limite.</span>
        </label>
      ))}
    </div>
  );
}
