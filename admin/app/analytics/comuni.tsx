"use client";

/* I pezzi condivisi delle pagine analytics (v8).
 *
 * - Il **periodo** sta nell'indirizzo (`?giorni=30`): una vista si condivide con un link e il tasto
 *   indietro fa quello che ci si aspetta.
 * - I **giorni** sono quelli italiani (Europe/Rome), come li conta il server.
 * - Ogni numero porta il confronto col periodo precedente di pari durata.
 * - Un tocco su una barra apre l'Esploratore con quel valore già come filtro (drill-down).
 */

import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useCallback } from "react";
import { elencaAnnotazioni, interroga, type Filtro, type Formato, type Interrogazione, type Risultato } from "@/lib/analytics";
import { useDati } from "@/lib/usa";
import comuni from "../comuni.module.css";
import { compatto, percento, type Punto, type Segno } from "../grafici";

export const PERIODI = [7, 30, 90, 365];

export const etichettaPeriodo = (g: number) => (g === 365 ? "Ultimo anno" : `Ultimi ${g} giorni`);

const FUSO = "Europe/Rome";
const isoRoma = new Intl.DateTimeFormat("en-CA", { timeZone: FUSO, year: "numeric", month: "2-digit", day: "2-digit" });
const giornoBreve = new Intl.DateTimeFormat("it-IT", { day: "numeric", month: "short", timeZone: "UTC" });
const meseBreve = new Intl.DateTimeFormat("it-IT", { month: "short", year: "2-digit", timeZone: "UTC" });
const euro = new Intl.NumberFormat("it-IT", { style: "currency", currency: "EUR" });
const decimali = new Intl.NumberFormat("it-IT", { maximumFractionDigits: 2 });

/** Oggi in Italia, come `aaaa-mm-gg`. */
export const oggi = () => isoRoma.format(new Date());

export function giorniPrima(iso: string, n: number): string {
  const d = new Date(`${iso}T00:00:00Z`);
  d.setUTCDate(d.getUTCDate() - n);
  return d.toISOString().slice(0, 10);
}

/** Il periodo scelto, letto dall'indirizzo, e il modo di cambiarlo. */
export function usePeriodo() {
  const parametri = useSearchParams();
  const router = useRouter();
  const percorso = usePathname();
  const scelto = Number(parametri.get("giorni"));
  const giorni = PERIODI.includes(scelto) ? scelto : 30;
  const a = oggi();
  const da = giorniPrima(a, giorni - 1);
  const imposta = useCallback(
    (g: number) => {
      const nuovi = new URLSearchParams(parametri.toString());
      nuovi.set("giorni", String(g));
      router.replace(`${percorso}?${nuovi.toString()}`, { scroll: false });
    },
    [parametri, percorso, router],
  );
  return { giorni, da, a, imposta };
}

export function FiltriPeriodo({ giorni, imposta }: { giorni: number; imposta: (g: number) => void }) {
  return (
    <div className={comuni.filtri} role="group" aria-label="Periodo">
      {PERIODI.map((g) => (
        <button
          key={g}
          className={g === giorni ? comuni.filtroScelto : comuni.filtro}
          aria-pressed={g === giorni}
          onClick={() => imposta(g)}
        >
          {etichettaPeriodo(g)}
        </button>
      ))}
    </div>
  );
}

/** Carica un'interrogazione; si ricarica quando cambia il suo contenuto. */
export function useRisultato(q: Interrogazione | null) {
  const chiave = q ? JSON.stringify(q) : "";
  return useDati<Risultato | null>(
    useCallback((t: string) => (q ? interroga(t, q) : Promise.resolve(null)), [chiave]), // eslint-disable-line react-hooks/exhaustive-deps
    [chiave],
  );
}

export function formatta(v: number | string | null | undefined, formato: Formato = "intero"): string {
  if (v === null || v === undefined || v === "") return "—";
  if (typeof v === "string") return v;
  switch (formato) {
    case "euro":
      return euro.format(v);
    case "percento":
      return percento(v, 1);
    case "secondi":
      return v >= 60 ? `${Math.floor(v / 60)} min ${Math.round(v % 60)} s` : `${decimali.format(v)} s`;
    case "decimale":
      return decimali.format(v);
    default:
      return compatto(v);
  }
}

/** Una serie temporale completa: i giorni (o mesi) senza righe valgono zero, non spariscono. */
export function serie(
  righe: Record<string, unknown>[] | undefined,
  misura: string,
  da: string,
  a: string,
  granularita: "giorno" | "mese" = "giorno",
): Punto[] {
  const per = new Map((righe ?? []).map((r) => [String(r.periodo).slice(0, granularita === "mese" ? 7 : 10), Number(r[misura] ?? 0)]));
  const punti: Punto[] = [];
  const inizio = new Date(`${da}T00:00:00Z`);
  const fine = new Date(`${a}T00:00:00Z`);
  if (granularita === "mese") {
    const d = new Date(Date.UTC(inizio.getUTCFullYear(), inizio.getUTCMonth(), 1));
    while (d <= fine) {
      const chiave = d.toISOString().slice(0, 7);
      punti.push({ chiave, etichetta: meseBreve.format(d), valore: per.get(chiave) ?? 0 });
      d.setUTCMonth(d.getUTCMonth() + 1);
    }
    return punti;
  }
  for (const d = new Date(inizio); d <= fine; d.setUTCDate(d.getUTCDate() + 1)) {
    const chiave = d.toISOString().slice(0, 10);
    punti.push({ chiave, etichetta: giornoBreve.format(d), valore: per.get(chiave) ?? 0 });
  }
  return punti;
}

/** Il collegamento all'Esploratore con un'interrogazione già composta (drill-down). */
export function indirizzoEsploratore(q: Partial<Interrogazione> & { sorgente: string }, giorni: number): string {
  return `/analytics/esploratore?giorni=${giorni}&q=${encodeURIComponent(JSON.stringify(q))}`;
}

export function useApprofondisci(giorni: number) {
  const router = useRouter();
  return useCallback(
    (sorgente: string, misure: string[], dimensione: string, valore: string, prossima?: string, filtri: Filtro[] = []) => {
      router.push(
        indirizzoEsploratore(
          {
            sorgente,
            misure,
            dimensioni: prossima ? [prossima] : [],
            filtri: [...filtri, { dimensione, operatore: "uguale", valori: [valore] }],
          },
          giorni,
        ),
      );
    },
    [router, giorni],
  );
}

const SCHEDE = [
  { href: "/analytics", etichetta: "Traffico" },
  { href: "/analytics/adesso", etichetta: "Adesso" },
  { href: "/analytics/utenti", etichetta: "Utenti" },
  { href: "/analytics/imbuti", etichetta: "Imbuti" },
  { href: "/analytics/uscite", etichetta: "Uscite" },
  { href: "/analytics/ricavi", etichetta: "Ricavi" },
  { href: "/analytics/esploratore", etichetta: "Esploratore" },
  { href: "/analytics/rapporti", etichetta: "Rapporti" },
  { href: "/analytics/studi", etichetta: "Studi (Colab)" },
  { href: "/analytics/google", etichetta: "Google" },
  { href: "/analytics/impostazioni", etichetta: "Impostazioni" },
];

export function Schede() {
  const percorso = usePathname();
  const parametri = useSearchParams();
  const giorni = parametri.get("giorni");
  const suffisso = giorni ? `?giorni=${giorni}` : "";
  return (
    <nav className={comuni.filtri} aria-label="Sezioni degli analytics">
      {SCHEDE.map((s) => {
        const attiva = s.href === "/analytics" ? percorso === "/analytics" : percorso.startsWith(s.href);
        return (
          <Link
            key={s.href}
            href={`${s.href}${suffisso}`}
            className={attiva ? comuni.filtroScelto : comuni.filtro}
            aria-current={attiva ? "page" : undefined}
          >
            {s.etichetta}
          </Link>
        );
      })}
    </nav>
  );
}

/** Le righe di un risultato come barre (prima dimensione, una misura), con l'«altro» fuori. */
export function barreDa(r: Risultato | null | undefined, dimensione: string, misura: string, quante = 10) {
  return (r?.righe ?? []).slice(0, quante).map((riga) => ({
    chiave: String(riga[dimensione]),
    etichetta: String(riga[dimensione]),
    valore: riga[misura] === null ? null : Number(riga[misura]),
  }));
}


/** Le annotazioni del periodo come segni per i grafici giornalieri (un periodo segna ogni suo giorno). */
export function useSegni(da: string, a: string): Segno[] {
  const annotazioni = useDati(useCallback((t: string) => elencaAnnotazioni(t, da, a), [da, a]), [da, a]);
  const segni: Segno[] = [];
  for (const x of annotazioni.dati ?? []) {
    const inizio = x.giorno < da ? da : x.giorno;
    const fine = (x.fine ?? x.giorno) > a ? a : (x.fine ?? x.giorno);
    for (let g = inizio; g <= fine; g = giorniPrima(g, -1)) segni.push({ chiave: g, testo: x.titolo });
  }
  return segni;
}
