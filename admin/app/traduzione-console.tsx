"use client";

/* La console in altre lingue, per ora con la traduzione automatica del browser (v9.5): la console è scritta in
 * italiano e, se si sceglie un'altra lingua, Chrome la traduce sul computer (lo stesso motore del sito,
 * `lib/traduzione-auto.ts`). È una soluzione temporanea, in attesa dei dizionari della console
 * (`docs/backlog-i18n-console.md`). Funziona solo dove il browser ha la Translator API (Chrome desktop 138+): altrove
 * il selettore dice che non è disponibile. La lingua scelta resta nel browser. */

import { useCallback, useSyncExternalStore } from "react";
import { supportata } from "@/lib/traduzione-auto";
import type { StatoTraduzione } from "@/lib/usa-traduzione";

export const LINGUE_CONSOLE = [
  { codice: "it", nome: "Italiano" },
  { codice: "en", nome: "English" },
  { codice: "hu", nome: "Magyar" },
  { codice: "fr", nome: "Français" },
  { codice: "es", nome: "Español" },
  { codice: "de", nome: "Deutsch" },
] as const;

const CHIAVE = "console_lingua";
const EVENTO = "console-lingua";

function leggi(): string {
  try {
    const v = window.localStorage.getItem(CHIAVE);
    return LINGUE_CONSOLE.some((l) => l.codice === v) ? (v as string) : "it";
  } catch {
    return "it";
  }
}

function iscrivi(avvisa: () => void): () => void {
  window.addEventListener(EVENTO, avvisa);
  window.addEventListener("storage", avvisa);
  return () => {
    window.removeEventListener(EVENTO, avvisa);
    window.removeEventListener("storage", avvisa);
  };
}

/** La lingua della console scelta in questo browser (italiano se nessuna). */
export function useLinguaConsole(): [string, (codice: string) => void] {
  const lingua = useSyncExternalStore(iscrivi, leggi, () => "it");
  const imposta = useCallback((codice: string) => {
    try {
      window.localStorage.setItem(CHIAVE, codice);
    } catch {
      // senza memoria del browser la scelta vale fino al ricaricamento
    }
    window.dispatchEvent(new Event(EVENTO));
  }, []);
  return [lingua, imposta];
}

export function SceltaLinguaConsole({ className }: { className?: string }) {
  const [lingua, imposta] = useLinguaConsole();
  const disponibile = useSyncExternalStore(() => () => {}, supportata, () => true);
  return (
    <label className={className} data-no-trad
           title={disponibile ? "Traduzione automatica nel browser (temporanea)" : "Serve Chrome desktop 138 o successivo"}>
      <span style={{ position: "absolute", width: 1, height: 1, overflow: "hidden", clip: "rect(0 0 0 0)" }}>
        Lingua della console
      </span>
      <select value={lingua} onChange={(e) => imposta(e.target.value)} disabled={!disponibile}
              style={{ minHeight: 44, font: "inherit" }}>
        {LINGUE_CONSOLE.map((l) => <option key={l.codice} value={l.codice}>{l.nome}</option>)}
      </select>
    </label>
  );
}

/** Il riquadro in cima alla pagina: cosa sta facendo la traduzione, e come tornare all'italiano. */
export function AvvisoTraduzioneConsole({ stato, className }: { stato: StatoTraduzione; className?: string }) {
  const [, imposta] = useLinguaConsole();
  if (stato.fase === "nessuna") return null;
  const testo = {
    offerta: "La traduzione della console va scaricata una volta da Chrome.",
    scarico: `Scaricamento del modello di traduzione… ${stato.percento ?? 0}%`,
    in_corso: "Traduzione in corso…",
    tradotta: "Console tradotta automaticamente dall'italiano, sul computer.",
    originale: "Console in italiano (originale).",
    errore: "La traduzione automatica non è riuscita.",
  }[stato.fase];
  return (
    <aside className={className} role="status" aria-live="polite" data-no-trad>
      <span>{testo}</span>
      {(stato.fase === "offerta" || stato.fase === "originale") && (
        <button type="button" onClick={stato.traduci}>Traduci</button>
      )}
      {stato.fase === "tradotta" && <button type="button" onClick={stato.mostraOriginale}>Mostra l&apos;italiano</button>}
      {stato.fase !== "scarico" && stato.fase !== "in_corso" && (
        <button type="button" onClick={() => imposta("it")}>Torna all&apos;italiano</button>
      )}
    </aside>
  );
}
