"use client";

/* Come sta andando il servizio.
 *
 * Prima i numeri, poi l'andamento, poi la ripartizione: chi apre questa
 * pagina vuole sapere se qualcosa è cambiato, e un grafico prima dei numeri
 * lo costringe a leggere un'area per ricavare ciò che una cifra dice subito.
 * Ogni numero porta il confronto col periodo precedente di pari durata.
 *
 * Tutto ciò che si vede qui sono conteggi: la console non legge domande né
 * responsi, e le statistiche non fanno eccezione.
 */

import Link from "next/link";
import { useCallback, useMemo, useState } from "react";
import { leggiStatistiche, type Statistiche } from "@/lib/api";
import { soldi } from "@/lib/formato";
import { useDati } from "@/lib/usa";
import comuni from "./comuni.module.css";
import { Barre, Colonne, Tessera, compatto, percento, type Punto } from "./grafici";
import grafici from "./grafici.module.css";
import stili from "./statistiche.module.css";

const PERIODI = [7, 30, 90, 365];

const giornoBreve = new Intl.DateTimeFormat("it-IT", { day: "numeric", month: "short", timeZone: "UTC" });

const ETICHETTE_FEEDBACK: Record<string, string> = {
  si: "Sì",
  in_parte: "In parte",
  no: "No",
};

const ETICHETTE_CONSUMO: Record<string, { nome: string; spiega: string }> = {
  quota: { nome: "Quota del piano", spiega: "letture comprese nell'abbonamento" },
  credito: { nome: "Crediti", spiega: "un credito scalato dal saldo" },
  omaggio: { nome: "Omaggio", spiega: "letture regalate, senza costo" },
};

function periodo(g: number): string {
  return g === 365 ? "Ultimo anno" : `Ultimi ${g} giorni`;
}

/* Il backend manda solo i giorni in cui qualcuno ha letto: i giorni vuoti
 * vanno rimessi, o una settimana di silenzio sparirebbe dal grafico e il
 * calo non si vedrebbe. I giorni sono in UTC, come li conta il database. */
function serieCompleta(dati: Statistiche): Punto[] {
  const perGiorno = new Map(dati.serie.map((s) => [s.giorno.slice(0, 10), s.letture]));
  const oggi = new Date();
  const base = Date.UTC(oggi.getUTCFullYear(), oggi.getUTCMonth(), oggi.getUTCDate());
  const punti: Punto[] = [];
  for (let i = dati.giorni - 1; i >= 0; i--) {
    const d = new Date(base - i * 86_400_000);
    const chiave = d.toISOString().slice(0, 10);
    punti.push({ chiave, etichetta: giornoBreve.format(d), valore: perGiorno.get(chiave) ?? 0 });
  }
  return punti;
}

export default function StatistichePagina() {
  const [giorni, setGiorni] = useState(30);
  const { dati, errore, inCorso } = useDati(
    useCallback((t: string) => leggiStatistiche(t, giorni), [giorni]),
  );

  const punti = useMemo(() => (dati ? serieCompleta(dati) : []), [dati]);

  const ora = dati?.attuale;
  const prima = dati?.precedente;

  const giudizi = dati
    ? (["si", "in_parte", "no"] as const).map((k) => dati.feedback[k] ?? 0)
    : [];
  const giudicate = giudizi.reduce((a, b) => a + b, 0);

  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Statistiche</h1>
          <p className={comuni.sottotitolo}>
            Letture, utenti, crediti e incassi. Ogni numero porta accanto il
            periodo precedente di pari durata; nessuno viene dal contenuto
            delle letture, che la console non vede.
          </p>
        </div>
      </div>

      {/* I filtri sopra tutto ciò che filtrano, in una riga sola. */}
      <div className={comuni.filtri} role="group" aria-label="Periodo">
        {PERIODI.map((g) => (
          <button
            key={g}
            className={g === giorni ? comuni.filtroScelto : comuni.filtro}
            aria-pressed={g === giorni}
            onClick={() => setGiorni(g)}
          >
            {periodo(g)}
          </button>
        ))}
      </div>

      {errore && <p className={comuni.errore}>{errore}</p>}
      {!dati && inCorso && <p className={comuni.caricamento}>Caricamento…</p>}

      {ora && prima && dati && (
        /* Mentre si ricarica, il quadro resta: più chiaro, non vuoto. */
        <div className={inCorso ? comuni.inRicarica : undefined}>
          <div className={grafici.tessere}>
            <Tessera
              etichetta="Letture"
              valore={ora.letture}
              precedente={prima.letture}
              nota={`${compatto(ora.completate)} completate (${percento(ora.letture ? ora.completate / ora.letture : null)})`}
            />
            <Tessera etichetta="Utenti attivi" valore={ora.utenti_attivi} precedente={prima.utenti_attivi} />
            <Tessera etichetta="Nuovi utenti" valore={ora.nuovi_utenti} precedente={prima.nuovi_utenti} />
            <Tessera
              etichetta="Crediti consumati"
              valore={ora.crediti_consumati}
              precedente={prima.crediti_consumati}
            />
            <Tessera
              etichetta="Crediti venduti"
              valore={ora.crediti_venduti}
              precedente={prima.crediti_venduti}
              nota="accreditati da pacchetti acquistati"
            />
            <Tessera
              etichetta="Ricavi"
              valore={ora.ricavi}
              precedente={prima.ricavi}
              formato={(n) => soldi(n)}
              nota="pagamenti conclusi nel periodo"
            />
          </div>

          <Colonne
            titolo="Letture al giorno"
            descrizione={`${periodo(dati.giorni)}, giorni senza letture compresi. Giorni in UTC.`}
            unita="letture"
            punti={punti}
          />

          <div className={stili.coppie}>
            <Barre
              titolo="Letture per stesa"
              descrizione="Quali stese si scelgono, nel periodo."
              unita="letture"
              barre={dati.per_stesa.map((s) => ({
                chiave: s.stesa,
                etichetta: s.stesa,
                valore: s.letture,
              }))}
            />

            <Barre
              titolo="Carte più uscite"
              descrizione="Le dodici estratte più spesso; le carte calcolate non contano."
              unita="uscite"
              barre={dati.carte.map((c) => ({
                chiave: c.carta,
                etichetta: c.carta,
                valore: c.uscite,
              }))}
            />

            <Barre
              titolo="Come si paga una lettura"
              descrizione="Quota dell'abbonamento, credito dal saldo, oppure omaggio."
              unita="letture"
              barre={Object.entries(dati.consumo)
                .sort(([, a], [, b]) => (b ?? 0) - (a ?? 0))
                .map(([k, n]) => ({
                  chiave: k,
                  etichetta: ETICHETTE_CONSUMO[k]?.nome ?? k,
                  valore: n ?? 0,
                  dettaglio: ETICHETTE_CONSUMO[k]?.spiega,
                }))}
            />

            <Barre
              titolo="Abbonamenti in corso"
              descrizione="Attivi o in prova adesso, qualunque sia il periodo scelto."
              unita="abbonati"
              barre={Object.entries(dati.abbonamenti)
                .sort(([, a], [, b]) => b - a)
                .map(([nome, n]) => ({ chiave: nome, etichetta: nome, valore: n }))}
            />

            <Barre
              titolo="«Si è avverato?»"
              descrizione={`Il giudizio che gli utenti danno a posteriori, su tutte le letture: ${compatto(giudicate)} ${giudicate === 1 ? "risposta" : "risposte"}.`}
              unita="giudizi"
              barre={
                giudicate === 0
                  ? []
                  : (["si", "in_parte", "no"] as const).map((k, i) => ({
                      chiave: k,
                      etichetta: ETICHETTE_FEEDBACK[k],
                      valore: giudizi[i],
                      dettaglio: percento(giudizi[i] / giudicate),
                    }))
              }
            />
          </div>

          <section className={stili.sicurezza} aria-labelledby="titolo-sicurezza">
            <h2 id="titolo-sicurezza" className={stili.sicurezzaTitolo}>
              Sicurezza
            </h2>
            <p className={stili.sicurezzaNota}>
              Quante volte la guardia ha bloccato o riscritto un responso, e
              quante letture hanno fatto scattare il protocollo di crisi. Qui
              salire non è una buona notizia; il dettaglio sta nel{" "}
              <Link href="/registro">registro</Link>, senza il testo delle letture.
            </p>
            <div className={stili.tessereSicurezza}>
              <Tessera
                etichetta="Interventi della guardia"
                valore={ora.guardia_interventi}
                precedente={prima.guardia_interventi}
                meglio="giu"
                nota="responsi bloccati o riscritti"
              />
              <Tessera
                etichetta="Segnalazioni di crisi"
                valore={ora.crisi}
                precedente={prima.crisi}
                meglio="giu"
                nota="letture interrotte per rischio"
              />
            </div>
          </section>
        </div>
      )}
    </>
  );
}
