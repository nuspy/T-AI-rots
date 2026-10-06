"use client";

/* Quante domande fa l'oracolo prima delle carte (v8.5): minimo e massimo. Fra i due decide il modello; dopo il
 * minimo, a ogni domanda nuova il sito chiede a chi consulta se vuole aggiungere altro («Sì, continuiamo») o
 * passare alle carte («No, basta così»).
 *
 * Qui stanno anche i due controlli fatti da un secondo modello — sulle domande dell'intervista e sul responso — con i
 * loro tre modi, e l'interruttore della memoria breve nei prompt. Ogni controllo LLM è una chiamata pagata: nel modo
 * «solo casi dubbi» parte soltanto quando un controllo automatico, gratuito, trova qualcosa da guardare. */

import { useState } from "react";
import { useAzione, useDati } from "@/lib/usa";
import { chiamata } from "@/lib/api";
import comuni from "../comuni.module.css";

type Modo = "dubbi" | "spento" | "acceso";

interface ImpostazioniIntervista {
  min_domande: number;
  max_domande: number;
  validatore_domande: Modo;
  guardia_responso: Modo;
  memoria_stato_nei_prompt: boolean;
  /** v9.5: quante persone su cento, al primo arrivo su /read, ricevono la lettura in chat invece della classica. */
  chat_percentuale: number;
}

const leggi = (t: string) => chiamata<ImpostazioniIntervista>(t, "/admin/impostazioni-intervista");
const salva = (t: string, corpo: Partial<ImpostazioniIntervista>) =>
  chiamata<ImpostazioniIntervista>(t, "/admin/impostazioni-intervista", { method: "PUT", body: JSON.stringify(corpo) });

/* I tre modi, con le parole per chi non è tecnico: cosa succede e quanto costa. */
const MODI: { valore: Modo; nome: string }[] = [
  { valore: "dubbi", nome: "Solo nei casi dubbi (consigliato)" },
  { valore: "acceso", nome: "Sempre" },
  { valore: "spento", nome: "Mai" },
];

export function RiquadroIntervista() {
  const { dati, errore, inCorso, ricarica } = useDati(leggi);
  if (errore) return <p className={comuni.errore}>{errore}</p>;
  if (inCorso && !dati) return <p className={comuni.caricamento}>Caricamento…</p>;
  return dati ? <Modulo valori={dati} ricarica={ricarica} /> : null;
}

function Modulo({ valori, ricarica }: { valori: ImpostazioniIntervista; ricarica: () => void }) {
  const { esegui, inCorso, errore } = useAzione();
  const [minimo, setMinimo] = useState(String(valori.min_domande));
  const [massimo, setMassimo] = useState(String(valori.max_domande));
  const [validatore, setValidatore] = useState<Modo>(valori.validatore_domande);
  const [guardia, setGuardia] = useState<Modo>(valori.guardia_responso);
  const [memoria, setMemoria] = useState(valori.memoria_stato_nei_prompt);
  const [chat, setChat] = useState(String(valori.chat_percentuale ?? 90));
  const [salvato, setSalvato] = useState(false);
  const [problema, setProblema] = useState<string | null>(null);

  const invia = async (e: React.FormEvent) => {
    e.preventDefault();
    setProblema(null);
    setSalvato(false);
    const a = Number(minimo);
    const b = Number(massimo);
    if (!Number.isInteger(a) || a < 0 || a > 12) return setProblema("Il minimo è un intero fra 0 e 12 (0: si può passare alle carte fin dalla prima domanda).");
    if (!Number.isInteger(b) || b < 1 || b > 12) return setProblema("Il massimo è un intero fra 1 e 12.");
    if (a > b) return setProblema("Il minimo non può superare il massimo.");
    const c = Number(chat);
    if (!Number.isInteger(c) || c < 0 || c > 100) return setProblema("La quota della lettura in chat è un intero fra 0 e 100.");
    const fatto = await esegui((t) => salva(t, {
      min_domande: a, max_domande: b, validatore_domande: validatore, guardia_responso: guardia,
      memoria_stato_nei_prompt: memoria, chat_percentuale: c,
    }));
    if (fatto) {
      setSalvato(true);
      ricarica();
    }
  };

  return (
    <section className={comuni.riquadro} aria-labelledby="intervista-titolo">
      <h2 id="intervista-titolo" className={comuni.riquadroTitolo}>Intervista e controlli della lettura</h2>
      <form onSubmit={invia} className={comuni.riga} style={{ flexWrap: "wrap", alignItems: "flex-end" }}>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Minimo di domande</span>
          <input className={comuni.ingresso} inputMode="numeric" value={minimo} onChange={(e) => setMinimo(e.target.value)} />
          <span className={comuni.campoAiuto}>
            Prima di questo numero l&apos;oracolo non passa alle carte. Dopo ogni risposta, nella chat, chi consulta
            sceglie fra «Passa alla lettura», «Voglio dire qualcosa di libero» e «Voglio rispondere a un&apos;altra
            domanda» (quest&apos;ultimo non c&apos;è al massimo). Con 0 può passare alle carte fin dalla prima domanda
            (consigliato: 0–2, dai dati sugli abbandoni).
          </span>
        </label>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Massimo di domande</span>
          <input className={comuni.ingresso} inputMode="numeric" value={massimo} onChange={(e) => setMassimo(e.target.value)} />
          <span className={comuni.campoAiuto}>Raggiunto il massimo, l&apos;intervista si chiude da sola.</span>
        </label>

        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Controllo delle domande da parte di un secondo modello</span>
          <select className={comuni.selezione} value={validatore} onChange={(e) => setValidatore(e.target.value as Modo)}>
            {MODI.map((m) => <option key={m.valore} value={m.valore}>{m.nome}</option>)}
          </select>
          <span className={comuni.campoAiuto}>
            Ogni domanda passa sempre dai controlli automatici gratuiti (non ripete il quesito, non chiede previsioni,
            non ripete domande già fatte). Il secondo modello, a pagamento, la rilegge per essere sicuri che non chieda
            a chi consulta la risposta al suo quesito. «Solo nei casi dubbi»: lo interpella quando la domanda chiede
            un&apos;opinione, parla del futuro, somiglia al quesito o tocca i sentimenti dell&apos;altra persona — e
            sempre per le lingue diverse da italiano e inglese.
          </span>
        </label>

        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Controllo di sicurezza del responso</span>
          <select className={comuni.selezione} value={guardia} onChange={(e) => setGuardia(e.target.value as Modo)}>
            {MODI.map((m) => <option key={m.valore} value={m.valore}>{m.nome}</option>)}
          </select>
          <span className={comuni.campoAiuto}>
            Un secondo modello rilegge il responso prima che arrivi a chi consulta, e se trova un problema lo fa
            riscrivere. «Solo nei casi dubbi»: lo interpella quando un controllo automatico trova temi di crisi,
            promesse di certezza, morte o malattia, salute, soldi o questioni legali, certezze sui sentimenti di altri o,
            nelle letture di coppia, verdetti sulla relazione — e sempre per le lingue diverse da italiano e inglese.
            «Mai»: restano solo i filtri automatici delle frasi proibite.
          </span>
        </label>

        <label
          className={comuni.campo}
          style={{ flexDirection: "row", alignItems: "flex-start", gap: "0.6rem", minHeight: 48, flexBasis: "100%", maxWidth: "62ch" }}
        >
          <input
            type="checkbox"
            checked={memoria}
            onChange={(e) => setMemoria(e.target.checked)}
            style={{ width: 22, height: 22, flex: "none" }}
          />
          <span>
            <span className={comuni.campoEtichetta}>Usa la memoria breve nelle letture e nell&apos;oracolo</span>
            <span className={comuni.campoAiuto} style={{ display: "block" }}>
              Dopo ogni lettura il lettore aggiorna un riassunto breve di ciò che sa della persona (lo si vede e si
              modifica dal profilo). Spento: il riassunto si aggiorna ma non entra ancora nelle domande, nei responsi e
              nell&apos;oracolo.
            </span>
          </span>
        </label>

        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Lettura in chat: persone su 100</span>
          <input className={comuni.ingresso} inputMode="numeric" value={chat} onChange={(e) => setChat(e.target.value)} />
          <span className={comuni.campoAiuto}>
            Prova delle due versioni della lettura: chi arriva per la prima volta riceve la lettura tutta in chat con
            questa probabilità, gli altri la classica. La scelta resta legata alla persona (all&apos;account su tutti i
            dispositivi, al dispositivo per chi non è registrato): cambiare il numero vale solo per chi arriva dopo.
            Il confronto è in Analisi → Uscite, filtro «variante».
          </span>
        </label>

        {(problema || errore) && <p className={comuni.errore}>{problema ?? errore}</p>}
        {salvato && !problema && !errore && <p className={comuni.esito}>Salvato.</p>}
        <button className={comuni.primaria} type="submit" disabled={inCorso}>Salva</button>
      </form>
    </section>
  );
}
