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
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Impostazioni</h1>
          <p className={comuni.sottotitolo}>
            I crediti che l&apos;iscrizione e il referral regalano, e la commissione che chi invita riceve su ogni
            acquisto futuro di chi ha invitato.
          </p>
        </div>
      </div>

      {errore && <p className={comuni.errore}>{errore}</p>}
      {inCorso && !dati && <p className={comuni.caricamento}>Caricamento…</p>}
      {dati && <Modulo valori={dati} ricarica={ricarica} />}

      {chat.errore && <p className={comuni.errore}>{chat.errore}</p>}
      {chat.inCorso && !chat.dati && <p className={comuni.caricamento}>Caricamento…</p>}
      {chat.dati && <ModuloChat valori={chat.dati} ricarica={chat.ricarica} />}

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
    const fatto = await esegui((t) => salvaImpostazioniChat(t, { proattiva_minuti_inattivita: n }));
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
        {(problema || errore) && <p className={comuni.errore}>{problema ?? errore}</p>}
        {salvato && !problema && !errore && <p className={comuni.esito}>Salvato.</p>}
        <button className={comuni.primaria} type="submit" disabled={inCorso}>
          Salva
        </button>
      </form>
    </section>
  );
}

/* Login persistente (v6, Fase G): la durata massima della sessione, in ore per comodità di lettura
 * — Keycloak la vuole in secondi, la conversione resta qui invece che nel modello del backend. */
function ModuloSessione({ valori, ricarica }: { valori: ValoriSessione; ricarica: () => void }) {
  const { esegui, inCorso, errore } = useAzione();
  const [ore, setOre] = useState(String(Math.round(valori.sso_session_max_lifespan_secondi / 3600)));
  const [salvato, setSalvato] = useState(false);
  const [problema, setProblema] = useState<string | null>(null);

  const invia = async (e: React.FormEvent) => {
    e.preventDefault();
    setProblema(null);
    setSalvato(false);
    const n = Number(ore);
    if (!Number.isFinite(n) || n < 0.1 || n > 8760) {
      return setProblema("Le ore sono un numero fra 0,1 e 8760 (un anno).");
    }
    const fatto = await esegui((t) =>
      salvaImpostazioniSessione(t, { sso_session_max_lifespan_secondi: Math.round(n * 3600) }),
    );
    if (fatto) {
      setSalvato(true);
      ricarica();
    }
  };

  return (
    <section className={comuni.riquadro} aria-labelledby="sessione-titolo">
      <h2 id="sessione-titolo" className={comuni.riquadroTitolo}>Login persistente</h2>
      <form onSubmit={invia} className={comuni.riga} style={{ flexWrap: "wrap", alignItems: "flex-end" }}>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Durata massima della sessione (ore)</span>
          <input className={comuni.ingresso} inputMode="decimal" value={ore} onChange={(e) => setOre(e.target.value)} />
          <span className={comuni.campoAiuto}>
            Cambia subito la sessione su Keycloak — vale sia per il sito sia per questa console.
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
