"use client";

import { useState } from "react";
import {
  impostazioniChat, impostazioniCrediti, impostazioniSessione,
  salvaImpostazioniChat, salvaImpostazioniCrediti, salvaImpostazioniSessione,
  type ImpostazioniChat as ValoriChat, type ImpostazioniCrediti as Valori,
  type ImpostazioniSessione as ValoriSessione,
} from "@/lib/impostazioni";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../comuni.module.css";
import { RiquadroIntervista } from "./intervista";

/* I numeri del regalo d'iscrizione e del referral.
 *
 * Tre soli campi, non un elenco: una riga di database, non una tabella da amministrare. `crediti_invito` è il
 * TOTALE che l'invitato ha in saldo dopo il riscatto (il regalo d'iscrizione conta già), non un extra da sommare —
 * chi imposta 5 qui fa sì che un invitato arrivi a 5, non a 3+5.
 */

export default function Impostazioni() {
  const { dati, errore, inCorso, ricarica } = useDati(impostazioniCrediti);
  const chat = useDati(impostazioniChat);
  const sessioneLogin = useDati(impostazioniSessione);

  return (
    <>
      <p className={comuni.riquadroNota}>
        I crediti che l&apos;iscrizione e il referral regalano, e la commissione che chi invita riceve su ogni acquisto
        futuro di chi ha invitato; la chat, l&apos;intervista e la sessione di accesso.
      </p>

      {errore && <p className={comuni.errore}>{errore}</p>}
      {inCorso && !dati && <p className={comuni.caricamento}>Caricamento…</p>}
      {dati && <Modulo valori={dati} ricarica={ricarica} />}

      {chat.errore && <p className={comuni.errore}>{chat.errore}</p>}
      {chat.inCorso && !chat.dati && <p className={comuni.caricamento}>Caricamento…</p>}
      {chat.dati && <ModuloChat valori={chat.dati} ricarica={chat.ricarica} />}

      <RiquadroIntervista />

      {sessioneLogin.errore && <p className={comuni.errore}>{sessioneLogin.errore}</p>}
      {sessioneLogin.inCorso && !sessioneLogin.dati && <p className={comuni.caricamento}>Caricamento…</p>}
      {sessioneLogin.dati && <ModuloSessione valori={sessioneLogin.dati} ricarica={sessioneLogin.ricarica} />}
    </>
  );
}

function Modulo({ valori, ricarica }: { valori: Valori; ricarica: () => void }) {
  const { esegui, inCorso, errore } = useAzione();
  const [iscrizione, setIscrizione] = useState(String(valori.crediti_iscrizione));
  const [invito, setInvito] = useState(String(valori.crediti_invito));
  const [commissione, setCommissione] = useState(String(valori.commissione_referral_percentuale));
  const [salvato, setSalvato] = useState(false);
  const [problema, setProblema] = useState<string | null>(null);

  const invia = async (e: React.FormEvent) => {
    e.preventDefault();
    setProblema(null);
    setSalvato(false);
    const n1 = Number(iscrizione);
    const n2 = Number(invito);
    const n3 = Number(commissione);
    if (!Number.isInteger(n1) || n1 < 0) return setProblema("I crediti d'iscrizione sono un intero non negativo.");
    if (!Number.isInteger(n2) || n2 < 0) return setProblema("I crediti del referral sono un intero non negativo.");
    if (!Number.isInteger(n3) || n3 < 0 || n3 > 100) return setProblema("La commissione è una percentuale da 0 a 100.");
    const fatto = await esegui((t) =>
      salvaImpostazioniCrediti(t, {
        crediti_iscrizione: n1, crediti_invito: n2, commissione_referral_percentuale: n3,
      }),
    );
    if (fatto) {
      setSalvato(true);
      ricarica();
    }
  };

  return (
    <section className={comuni.riquadro} aria-labelledby="crediti-titolo">
      <h2 id="crediti-titolo" className={comuni.riquadroTitolo}>
        Regalo d&apos;iscrizione e referral
      </h2>
      <form onSubmit={invia} className={comuni.riga} style={{ flexWrap: "wrap", alignItems: "flex-end" }}>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Letture regalate all&apos;iscrizione</span>
          <input
            className={comuni.ingresso} inputMode="numeric" value={iscrizione}
            onChange={(e) => setIscrizione(e.target.value)}
          />
          <span className={comuni.campoAiuto}>A ogni nuovo account, subito, senza bisogno di un invito.</span>
        </label>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Totale con un codice d&apos;invito</span>
          <input className={comuni.ingresso} inputMode="numeric" value={invito} onChange={(e) => setInvito(e.target.value)} />
          <span className={comuni.campoAiuto}>
            Il saldo finale dell&apos;invitato (non si somma al regalo d&apos;iscrizione). Chi invita riceve lo
            stesso numero.
          </span>
        </label>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Commissione sugli acquisti futuri (%)</span>
          <input
            className={comuni.ingresso} inputMode="numeric" value={commissione}
            onChange={(e) => setCommissione(e.target.value)}
          />
          <span className={comuni.campoAiuto}>
            A ogni pacchetto o rinnovo di chi è stato invitato, per sempre — non solo alla prima volta.
          </span>
        </label>
        {(problema || errore) && <p className={comuni.errore}>{problema ?? errore}</p>}
        {salvato && !problema && !errore && <p className={comuni.esito}>Salvato.</p>}
        <button className={comuni.primaria} type="submit" disabled={inCorso}>
          Salva
        </button>
      </form>
    </section>
  );
}

/* Chat proattiva (v6, Fase E): quanti minuti di inattività prima che l'AI apra da sola una
 * conversazione con l'utente, basandosi sulle sue memorie. */
function ModuloChat({ valori, ricarica }: { valori: ValoriChat; ricarica: () => void }) {
  const { esegui, inCorso, errore } = useAzione();
  const [minuti, setMinuti] = useState(String(valori.proattiva_minuti_inattivita));
  const [perVisita, setPerVisita] = useState(String(valori.proattiva_max_per_visita));
  const [salvato, setSalvato] = useState(false);
  const [problema, setProblema] = useState<string | null>(null);

  const invia = async (e: React.FormEvent) => {
    e.preventDefault();
    setProblema(null);
    setSalvato(false);
    const n = Number(minuti);
    if (!Number.isInteger(n) || n < 1 || n > 180) {
      return setProblema("I minuti di inattività sono un intero fra 1 e 180.");
    }
    const v = Number(perVisita);
    if (!Number.isInteger(v) || v < 0 || v > 20) {
      return setProblema("Le aperture per visita sono un intero fra 0 e 20.");
    }
    const fatto = await esegui((t) => salvaImpostazioniChat(t, { proattiva_minuti_inattivita: n, proattiva_max_per_visita: v }));
    if (fatto) {
      setSalvato(true);
      ricarica();
    }
  };

  return (
    <section className={comuni.riquadro} aria-labelledby="chat-titolo">
      <h2 id="chat-titolo" className={comuni.riquadroTitolo}>Chat proattiva</h2>
      <form onSubmit={invia} className={comuni.riga} style={{ flexWrap: "wrap", alignItems: "flex-end" }}>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Minuti di inattività prima che l&apos;AI scriva da sola</span>
          <input
            className={comuni.ingresso} inputMode="numeric" value={minuti}
            onChange={(e) => setMinuti(e.target.value)}
          />
          <span className={comuni.campoAiuto}>
            Vale sia per l&apos;attesa di una risposta sia per il tempo dopo l&apos;ultimo turno.
          </span>
        </label>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Aperture automatiche per visita (massimo)</span>
          <input
            className={comuni.ingresso} inputMode="numeric" value={perVisita}
            onChange={(e) => setPerVisita(e.target.value)}
          />
          <span className={comuni.campoAiuto}>
            Quante volte l&apos;oracolo scrive da solo a chi è dentro, in una visita (al caricamento e dopo il
            silenzio): ognuna è un&apos;inferenza. 0 = mai da solo. Chi non ha un account vede temi già scritti, senza
            inferenze.
          </span>
        </label>
        {(problema || errore) && <p className={comuni.errore}>{problema ?? errore}</p>}
        {salvato && !problema && !errore && <p className={comuni.esito}>Salvato.</p>}
        <button className={comuni.primaria} type="submit" disabled={inCorso}>
          Salva
        </button>
      </form>
    </section>
  );
}

/* Login persistente: chi entra resta dentro — anche chiudendo il browser e riavviando la macchina — finché non fa
 * logout. Tecnicamente è il token offline di Keycloak (scope `offline_access`): qui se ne regolano le due durate,
 * scritte subito su Keycloak e lette da lì a ogni apertura. Vale per il sito e per questa console. */
function ModuloSessione({ valori, ricarica }: { valori: ValoriSessione; ricarica: () => void }) {
  const { esegui, inCorso, errore } = useAzione();
  const [inattivita, setInattivita] = useState(String(valori.inattivita_giorni ?? 365));
  const [massima, setMassima] = useState(String(valori.durata_massima_giorni ?? 0));
  const [salvato, setSalvato] = useState(false);
  const [problema, setProblema] = useState<string | null>(null);

  const invia = async (e: React.FormEvent) => {
    e.preventDefault();
    setProblema(null);
    setSalvato(false);
    const giorni = Number(inattivita);
    const tetto = Number(massima);
    if (!Number.isInteger(giorni) || giorni < 1 || giorni > 3650) {
      return setProblema("I giorni di inattività sono un intero fra 1 e 3650.");
    }
    if (!Number.isInteger(tetto) || tetto < 0 || tetto > 3650) {
      return setProblema("La durata massima è un intero fra 0 (nessun limite) e 3650.");
    }
    if (tetto > 0 && tetto < giorni) {
      return setProblema("La durata massima non può essere più breve dell'inattività ammessa.");
    }
    const fatto = await esegui((t) =>
      salvaImpostazioniSessione(t, { inattivita_giorni: giorni, durata_massima_giorni: tetto }),
    );
    if (fatto) {
      setSalvato(true);
      ricarica();
    }
  };

  return (
    <section className={comuni.riquadro} aria-labelledby="sessione-titolo">
      <h2 id="sessione-titolo" className={comuni.riquadroTitolo}>Login persistente</h2>
      <p className={comuni.riquadroNota}>
        Chi entra resta dentro, anche chiudendo il browser o riavviando, finché non fa logout. Le durate si cambiano
        subito su Keycloak e valgono per il sito e per questa console.
      </p>
      {!valori.keycloak_raggiungibile && (
        <p className={comuni.errore}>
          Keycloak non risponde, i valori attuali non si possono leggere: {valori.errore}
        </p>
      )}
      <form onSubmit={invia} className={comuni.riga} style={{ flexWrap: "wrap", alignItems: "flex-end" }}>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Giorni senza visite prima di dover rientrare</span>
          <input
            className={comuni.ingresso} inputMode="numeric" value={inattivita}
            onChange={(e) => setInattivita(e.target.value)}
          />
          <span className={comuni.campoAiuto}>
            Ogni visita li fa ripartire da capo: chi torna almeno una volta in questo periodo non rientra mai.
          </span>
        </label>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Durata massima dall&apos;accesso (giorni, 0 = nessuna)</span>
          <input
            className={comuni.ingresso} inputMode="numeric" value={massima}
            onChange={(e) => setMassima(e.target.value)}
          />
          <span className={comuni.campoAiuto}>
            Con 0 si resta dentro fino al logout. Un numero obbliga a rientrare comunque dopo quel tempo.
          </span>
        </label>
        {(problema || errore) && <p className={comuni.errore}>{problema ?? errore}</p>}
        {salvato && !problema && !errore && <p className={comuni.esito}>Salvato su Keycloak.</p>}
        <button className={comuni.primaria} type="submit" disabled={inCorso}>
          Salva
        </button>
      </form>
    </section>
  );
}
