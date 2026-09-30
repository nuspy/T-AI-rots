"use client";

/* Traffico (v8): da dove arrivano le visite, cosa guardano, quanto restano.
 *
 * Prima i numeri col periodo precedente, poi l'andamento, poi le ripartizioni; ogni barra si tocca
 * per aprire l'Esploratore già filtrato su quel valore. Senza cookie: «visitatori» somma gli univoci
 * di ogni giorno (lo stesso browser in due giorni conta due volte), e chi blocca gli script non c'è.
 */

import comuni from "../comuni.module.css";
import { Barre, Colonne, Tessera } from "../grafici";
import grafici from "../grafici.module.css";
import stili from "../statistiche.module.css";
import { FiltriPeriodo, barreDa, etichettaPeriodo, formatta, serie, useApprofondisci, usePeriodo, useRisultato } from "./comuni";
import { BottoniEsporta } from "./esporta";
import { PannelloAI } from "./pannello-ai";

const MISURE = ["sessioni", "visitatori", "pagine", "tasso_coinvolgimento", "tempo_medio", "utenti"];

export default function Traffico() {
  const { giorni, da, a, imposta } = usePeriodo();
  const approfondisci = useApprofondisci(giorni);
  const base = { da, a };

  const totali = useRisultato({ ...base, sorgente: "visite", misure: MISURE, confronto: "precedente" });
  const andamento = useRisultato({ ...base, sorgente: "visite", misure: ["sessioni"], granularita: "giorno", limite: 400 });
  const per = (dimensione: string) => ({ ...base, sorgente: "visite", misure: ["sessioni"], dimensioni: [dimensione], limite: 10 });
  const canali = useRisultato(per("canale"));
  const referrer = useRisultato(per("referrer"));
  const campagne = useRisultato(per("campagna"));
  const paesi = useRisultato(per("paese"));
  const dispositivi = useRisultato(per("dispositivo"));
  const ingressi = useRisultato(per("ingresso"));
  const pagine = useRisultato({
    ...base, sorgente: "eventi", misure: ["eventi"], dimensioni: ["percorso"], limite: 12,
    filtri: [{ dimensione: "nome", operatore: "uguale", valori: ["page_view"] }],
  });
  const azioni = useRisultato({
    ...base, sorgente: "eventi", misure: ["eventi", "sessioni"], dimensioni: ["nome"], limite: 15,
    filtri: [{ dimensione: "nome", operatore: "non_in", valori: ["page_view", "engagement"] }],
  });

  const t = totali.dati?.totali;
  const p = totali.dati?.confronto?.totali;
  const errore = totali.errore ?? andamento.errore;
  const vuoto = t && !t.sessioni;

  const tocca = (dimensione: string) => (valore: string) => approfondisci("visite", ["sessioni", "visitatori", "tasso_coinvolgimento"], dimensione, valore, dimensione === "canale" ? "referrer" : "ingresso");

  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Traffico</h1>
          <p className={comuni.sottotitolo}>
            Visite al sito misurate senza cookie. «Visitatori» somma gli univoci di ogni giorno; chi blocca gli
            script non compare. Tocca una barra per approfondire.
          </p>
        </div>
      </div>
      <FiltriPeriodo giorni={giorni} imposta={imposta} />

      {errore && <p className={comuni.errore} role="alert">{errore}</p>}
      {!totali.dati && totali.inCorso && <p className={comuni.caricamento}>Caricamento…</p>}
      {vuoto && (
        <div className={comuni.vuoto}>
          Nessuna visita registrata in questo periodo. La raccolta parte dal rilascio degli analytics: allarga il periodo o
          torna fra qualche giorno.
        </div>
      )}

      {t && !vuoto && (
        <div className={totali.inCorso ? comuni.inRicarica : undefined}>
          <div className={grafici.tessere}>
            <Tessera etichetta="Sessioni" valore={Number(t.sessioni)} precedente={p ? Number(p.sessioni) : null} />
            <Tessera etichetta="Visitatori" valore={Number(t.visitatori)} precedente={p ? Number(p.visitatori) : null}
              nota="univoci di ogni giorno, sommati" />
            <Tessera etichetta="Pagine viste" valore={Number(t.pagine)} precedente={p ? Number(p.pagine) : null} />
            <Tessera etichetta="Sessioni coinvolte" valore={t.tasso_coinvolgimento === null ? null : Number(t.tasso_coinvolgimento)}
              precedente={p?.tasso_coinvolgimento ?? null} formato={(n) => formatta(n, "percento")}
              nota="più di una pagina, 10 s attivi o un'azione" />
            <Tessera etichetta="Tempo attivo medio" valore={t.tempo_medio === null ? null : Number(t.tempo_medio)}
              precedente={p?.tempo_medio ?? null} formato={(n) => formatta(n, "secondi")} />
            <Tessera etichetta="Utenti registrati" valore={Number(t.utenti)} precedente={p ? Number(p.utenti) : null}
              nota="con l'accesso fatto" />
          </div>

          <Colonne
            titolo="Sessioni al giorno"
            descrizione={`${etichettaPeriodo(giorni)}, giorni italiani, giorni senza visite compresi.`}
            unita="sessioni"
            punti={serie(andamento.dati?.righe, "sessioni", da, a)}
          />

          <div className={stili.coppie}>
            <Barre titolo="Canali" descrizione="Da dove arriva la visita: motori, social, assistenti AI, campagne…"
              unita="sessioni" barre={barreDa(canali.dati, "canale", "sessioni")} onScegli={tocca("canale")} />
            <Barre titolo="Siti di provenienza" unita="sessioni" barre={barreDa(referrer.dati, "referrer", "sessioni")}
              onScegli={tocca("referrer")} />
            <Barre titolo="Campagne" descrizione="Dal parametro utm_campaign dei link." unita="sessioni"
              barre={barreDa(campagne.dati, "campagna", "sessioni")} onScegli={tocca("campagna")} />
            <Barre titolo="Paesi" descrizione="Stimati dall'indirizzo IP (DB-IP), che non si conserva." unita="sessioni"
              barre={barreDa(paesi.dati, "paese", "sessioni")} onScegli={tocca("paese")} />
            <Barre titolo="Dispositivi" unita="sessioni" barre={barreDa(dispositivi.dati, "dispositivo", "sessioni")}
              onScegli={tocca("dispositivo")} />
            <Barre titolo="Pagine d'ingresso" unita="sessioni" barre={barreDa(ingressi.dati, "ingresso", "sessioni")}
              onScegli={tocca("ingresso")} />
            <Barre titolo="Pagine più viste" unita="viste" barre={barreDa(pagine.dati, "percorso", "eventi", 12)}
              onScegli={(v) => approfondisci("eventi", ["eventi", "sessioni"], "percorso", v, "canale",
                [{ dimensione: "nome", operatore: "uguale", valori: ["page_view"] }])} />
            <Barre titolo="Azioni più frequenti" descrizione="Fasi della lettura, bottoni, acquisti: tutto tranne le pagine viste."
              unita="volte" barre={barreDa(azioni.dati, "nome", "eventi", 15)}
              colonneTabella={[{ titolo: "sessioni", valori: (azioni.dati?.righe ?? []).map((r) => formatta(Number(r.sessioni))) }]}
              onScegli={(v) => approfondisci("eventi", ["eventi", "sessioni", "utenti"], "nome", v, "percorso")} />
          </div>
        </div>
      )}
      <BottoniEsporta collezione="traffico" giorni={giorni} />
      <PannelloAI sezione="traffico" titolo="Traffico" giorni={giorni} />
    </>
  );
}
