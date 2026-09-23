"use client";

import { useState } from "react";
import { catalogo, modificaPiano, type ModificaPiano, type Piano } from "@/lib/api";
import { centesimiDa, importoPerCampo, soldi } from "@/lib/formato";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../comuni.module.css";
import stili from "./catalogo.module.css";

/* Il catalogo: cosa si vende e a quanto.
 *
 * Due cose diverse sotto lo stesso modello. Un **abbonamento** dà un numero
 * di letture al giorno per un periodo, e ha un prezzo mensile e uno
 * annuale. Un **pacchetto** accredita crediti una volta sola, che non
 * scadono, e ha un prezzo solo — quello che il backend chiama «mensile».
 *
 * I prezzi si scrivono in euro e partono in centesimi: il backend conta
 * sempre in centesimi, e un 9,90 che arrivasse come 9 (o come 990 euro) è il
 * tipo di errore che si scopre dai reclami. Un prezzo nuovo vale dal
 * pagamento successivo: chi sta pagando paga quello che ha visto.
 */

export default function Catalogo() {
  const { dati, errore, inCorso, ricarica } = useDati(catalogo);

  const ordinati = [...(dati ?? [])].sort((a, b) => a.rango - b.rango);
  const abbonamenti = ordinati.filter((p) => p.tipo === "abbonamento");
  const pacchetti = ordinati.filter((p) => p.tipo === "pacchetto");

  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Catalogo</h1>
          <p className={comuni.sottotitolo}>
            Piani e pacchetti, con prezzi e limiti. Ogni modifica finisce nel
            registro con lo stato di prima; un piano disattivato sparisce dalla
            vendita ma chi lo ha già continua a usarlo.
          </p>
        </div>
      </div>

      {errore && <p className={comuni.errore}>{errore}</p>}
      {!dati && inCorso && <p className={comuni.caricamento}>Caricamento…</p>}

      {dati && (
        <>
          <Sezione
            titolo="Abbonamenti"
            nota="Letture al giorno per la durata del periodo, con rinnovo mensile o annuale."
            piani={abbonamenti}
            ricarica={ricarica}
          />
          <Sezione
            titolo="Pacchetti"
            nota="Crediti accreditati una volta sola, che non scadono: un credito, una lettura."
            piani={pacchetti}
            ricarica={ricarica}
          />
        </>
      )}
    </>
  );
}

function Sezione({
  titolo,
  nota,
  piani,
  ricarica,
}: {
  titolo: string;
  nota: string;
  piani: Piano[];
  ricarica: () => void;
}) {
  return (
    <section className={stili.sezione}>
      <h2 className={stili.sezioneTitolo}>{titolo}</h2>
      <p className={comuni.riquadroNota}>{nota}</p>
      {piani.length === 0 ? (
        <div className={comuni.vuoto}>Nessuna voce.</div>
      ) : (
        <div className={stili.piani}>
          {piani.map((p) => (
            <SchedaPiano key={p.slug} piano={p} ricarica={ricarica} />
          ))}
        </div>
      )}
    </section>
  );
}

function letture(piano: Piano): string {
  const n = piano.limiti.letture_al_giorno;
  if (n === undefined || n === null) return "—";
  return n < 0 ? "illimitate" : `${n} al giorno`;
}

function SchedaPiano({ piano, ricarica }: { piano: Piano; ricarica: () => void }) {
  const [modifica, setModifica] = useState(false);
  const pacchetto = piano.tipo === "pacchetto";

  return (
    <article className={piano.attivo ? stili.piano : stili.pianoSpento}>
      <header className={stili.pianoTestata}>
        <div>
          <h3 className={stili.pianoNome}>{piano.nome}</h3>
          <div className={comuni.mono}>{piano.slug}</div>
        </div>
        <span className={`${comuni.stato} ${piano.attivo ? comuni.positivo : comuni.spento}`}>
          {piano.attivo ? "in vendita" : "disattivato"}
        </span>
      </header>

      {modifica ? (
        <Modulo
          piano={piano}
          chiudi={() => setModifica(false)}
          salvato={() => {
            setModifica(false);
            ricarica();
          }}
        />
      ) : (
        <>
          {piano.descrizione && <p className={stili.descrizione}>{piano.descrizione}</p>}
          <dl className={stili.dati}>
            {pacchetto ? (
              <>
                <dt>Prezzo</dt>
                <dd>{soldi(piano.prezzo_mensile)}</dd>
                <dt>Crediti</dt>
                <dd>{piano.crediti ?? 0}</dd>
              </>
            ) : (
              <>
                <dt>Mensile</dt>
                <dd>{soldi(piano.prezzo_mensile)}</dd>
                <dt>Annuale</dt>
                <dd>{soldi(piano.prezzo_annuale)}</dd>
                <dt>Letture</dt>
                <dd>{letture(piano)}</dd>
                {!!piano.crediti && (
                  <>
                    <dt>Crediti per periodo</dt>
                    <dd>{piano.crediti}</dd>
                  </>
                )}
                <dt>Abbonati</dt>
                <dd>{piano.abbonati}</dd>
              </>
            )}
          </dl>
          <button className={comuni.secondaria} onClick={() => setModifica(true)}>
            Modifica
          </button>
        </>
      )}
    </article>
  );
}

/* Il modulo manda solo ciò che è cambiato: un campo lasciato com'era non
 * deve comparire nel registro come modificato, e due amministratori che
 * cambiano campi diversi dello stesso piano non devono cancellarsi a
 * vicenda. */
function Modulo({
  piano,
  chiudi,
  salvato,
}: {
  piano: Piano;
  chiudi: () => void;
  salvato: () => void;
}) {
  const pacchetto = piano.tipo === "pacchetto";
  const { esegui, inCorso, errore } = useAzione();

  const [nome, setNome] = useState(piano.nome);
  const [descrizione, setDescrizione] = useState(piano.descrizione ?? "");
  const [mensile, setMensile] = useState(importoPerCampo(piano.prezzo_mensile));
  const [annuale, setAnnuale] = useState(importoPerCampo(piano.prezzo_annuale));
  const [crediti, setCrediti] = useState(String(piano.crediti ?? 0));
  const [alGiorno, setAlGiorno] = useState(
    piano.limiti.letture_al_giorno === undefined ? "" : String(piano.limiti.letture_al_giorno),
  );
  const [attivo, setAttivo] = useState(piano.attivo);
  const [problema, setProblema] = useState<string | null>(null);

  const invia = async (e: React.FormEvent) => {
    e.preventDefault();
    setProblema(null);

    const corpo: ModificaPiano = {};
    if (nome.trim() && nome.trim() !== piano.nome) corpo.name = nome.trim();
    if (descrizione.trim() !== (piano.descrizione ?? "")) corpo.description = descrizione.trim();

    const cMensile = centesimiDa(mensile);
    if (cMensile === null) return setProblema("Il prezzo non è un importo valido.");
    if (cMensile !== piano.prezzo_mensile) corpo.price_monthly = cMensile;

    if (!pacchetto) {
      const cAnnuale = centesimiDa(annuale);
      if (cAnnuale === null) return setProblema("Il prezzo annuale non è un importo valido.");
      if (cAnnuale !== piano.prezzo_annuale) corpo.price_yearly = cAnnuale;

      if (alGiorno.trim() !== "") {
        const n = Number(alGiorno);
        if (!Number.isInteger(n) || n < -1) {
          return setProblema("Le letture al giorno sono un intero da 0 in su, o −1 per illimitate.");
        }
        if (n !== piano.limiti.letture_al_giorno) corpo.letture_al_giorno = n;
      }
    }

    const nCrediti = Number(crediti);
    if (!Number.isInteger(nCrediti) || nCrediti < 0) {
      return setProblema("I crediti sono un intero da 0 in su.");
    }
    if (nCrediti !== (piano.crediti ?? 0)) corpo.credits_per_period = nCrediti;

    if (attivo !== piano.attivo) corpo.active = attivo;

    if (Object.keys(corpo).length === 0) {
      chiudi();
      return;
    }
    const fatto = await esegui((t) => modificaPiano(t, piano.slug, corpo));
    if (fatto) salvato();
  };

  return (
    <form onSubmit={invia} className={stili.modulo}>
      <label className={comuni.campo}>
        <span className={comuni.campoEtichetta}>Nome</span>
        <input className={comuni.ingresso} value={nome} maxLength={80} onChange={(e) => setNome(e.target.value)} />
      </label>
      <label className={comuni.campo}>
        <span className={comuni.campoEtichetta}>Descrizione</span>
        <textarea
          className={comuni.area}
          style={{ minHeight: "5rem", fontFamily: "inherit" }}
          value={descrizione}
          maxLength={1000}
          onChange={(e) => setDescrizione(e.target.value)}
        />
      </label>

      <div className={comuni.riga}>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>{pacchetto ? "Prezzo (€)" : "Prezzo mensile (€)"}</span>
          <input
            className={comuni.ingresso}
            inputMode="decimal"
            value={mensile}
            onChange={(e) => setMensile(e.target.value)}
            placeholder="9,90"
          />
        </label>
        {!pacchetto && (
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Prezzo annuale (€)</span>
            <input
              className={comuni.ingresso}
              inputMode="decimal"
              value={annuale}
              onChange={(e) => setAnnuale(e.target.value)}
              placeholder="99,00"
            />
          </label>
        )}
      </div>

      <div className={comuni.riga}>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>{pacchetto ? "Crediti" : "Crediti per periodo"}</span>
          <input
            className={comuni.ingresso}
            type="number"
            min={0}
            step={1}
            value={crediti}
            onChange={(e) => setCrediti(e.target.value)}
          />
        </label>
        {!pacchetto && (
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Letture al giorno</span>
            <input
              className={comuni.ingresso}
              type="number"
              min={-1}
              step={1}
              value={alGiorno}
              onChange={(e) => setAlGiorno(e.target.value)}
            />
            <span className={comuni.campoAiuto}>−1 per illimitate.</span>
          </label>
        )}
      </div>

      <label className={stili.spunta}>
        <input type="checkbox" checked={attivo} onChange={(e) => setAttivo(e.target.checked)} />
        In vendita
      </label>

      {(problema || errore) && <p className={comuni.errore}>{problema ?? errore}</p>}

      <div className={stili.comandi}>
        <button className={comuni.primaria} type="submit" disabled={inCorso}>
          Salva
        </button>
        <button className={comuni.secondaria} type="button" onClick={chiudi} disabled={inCorso}>
          Annulla
        </button>
      </div>
    </form>
  );
}
