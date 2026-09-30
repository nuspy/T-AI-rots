"use client";

/* Vota il prossimo mazzo (v7, Fase K): un voto per utente per tornata, mai sommato — un nuovo voto
 * sostituisce il precedente. Le percentuali si vedono solo dopo aver votato, per non influenzare
 * la scelta di chi non ha ancora votato (`GET /voto/mazzi` fa lo stesso lato server). */

import { useState } from "react";
import { statoVotoMazzi, suggerisciTemaMazzo, votaMazzo, type CandidatoVoto } from "@/lib/api";
import { useLingua } from "@/lib/lingua";
import { useAzione, useCarica } from "@/lib/usa";
import { Involucro } from "../componenti/testata";
import stili from "../pagine.module.css";

export default function PaginaVotaMazzo() {
  const { t } = useLingua();
  return (
    <Involucro titolo={t.vota_titolo} sottotitolo={t.vota_sottotitolo}>
      <VotaMazzo />
    </Involucro>
  );
}

function VotaMazzo() {
  const { t } = useLingua();
  const stato = useCarica(statoVotoMazzi);
  const { esegui, inCorso, errore } = useAzione();
  /* Il voto appena dato: finché non arriva la ricarica di `stato`, vale questo invece di
   * `s.mio_voto` — così il bottone e la sezione "grazie" rispondono subito al tocco. */
  const [votatoOra, setVotatoOra] = useState<string | null>(null);

  if (stato.errore) return <p className={stili.errore}>{stato.errore}</p>;
  const s = stato.dati;
  if (!s) return null;

  const mioVoto = votatoOra ?? s.mio_voto;
  const haVotato = mioVoto !== null;

  const vota = async (candidateId: string) => {
    const r = await esegui((tok) => votaMazzo(tok, candidateId));
    if (r) {
      setVotatoOra(candidateId);
      stato.ricarica();
    }
  };

  return (
    <>
      {s.tornata ? (
        <>
          {haVotato && <p className="oracolo">{t.vota_grazie}</p>}
          <div className={stili.griglia}>
            {s.candidati.map((c) => (
              <Candidato key={c.id} c={c} mioVoto={mioVoto} inCorso={inCorso} onVota={() => vota(c.id)} />
            ))}
          </div>
          {haVotato && <p className={stili.nota}>{t.vota_cambia_voto}</p>}
          {errore && <p className={stili.errore}>{errore}</p>}
        </>
      ) : (
        <p className={stili.nota}>{t.vota_nessuna_tornata}</p>
      )}

      {s.vincitori_precedenti && s.vincitori_precedenti.length > 0 && (
        <section className={stili.sezione} style={{ marginTop: 32 }}>
          <h2 className={stili.sezioneTitolo}>{t.vota_vincitori_titolo}</h2>
          <ul className={stili.elenco}>
            {s.vincitori_precedenti.map((v) => (
              <li key={v.nome} className={`pannello ${stili.riga}`}>
                <div className={stili.rigaCorpo}>
                  <p className={stili.rigaTitolo}>{v.nome}</p>
                </div>
                <span className={stili.positivo}>{t.vota_percentuale(v.percentuale)}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      <SuggerisciTema />
    </>
  );
}

function SuggerisciTema() {
  const { t } = useLingua();
  const { esegui, inCorso, errore } = useAzione();
  const [testo, setTesto] = useState("");
  const [inviato, setInviato] = useState(false);

  const invia = async () => {
    if (testo.trim().length < 3) return;
    const r = await esegui((tok) => suggerisciTemaMazzo(tok, testo.trim()));
    if (r) { setTesto(""); setInviato(true); }
  };

  return (
    <section className={`pannello ${stili.scheda}`} style={{ marginTop: 32 }}>
      <h2 className={stili.sezioneTitolo}>{t.vota_suggerisci_titolo}</h2>
      <p className={stili.nota}>{t.vota_suggerisci_testo}</p>
      <textarea
        style={{
          width: "100%", minHeight: 90, resize: "vertical", padding: "10px 12px", borderRadius: 10,
          border: "1px solid var(--bordo)", background: "rgba(7, 5, 15, 0.6)", color: "var(--testo)", font: "inherit",
        }}
        value={testo}
        maxLength={1000}
        placeholder={t.vota_suggerisci_placeholder}
        onChange={(e) => { setTesto(e.target.value); setInviato(false); }}
      />
      <div className={stili.linea}>
        <button className="bottone-secondario" disabled={inCorso || testo.trim().length < 3} onClick={invia}>
          {t.vota_suggerisci_invia}
        </button>
      </div>
      {inviato && <p className="oracolo">{t.vota_suggerisci_grazie}</p>}
      {errore && <p className={stili.errore}>{t.vota_suggerisci_errore}</p>}
    </section>
  );
}

function Candidato({
  c, mioVoto, inCorso, onVota,
}: { c: CandidatoVoto; mioVoto: string | null; inCorso: boolean; onVota: () => void }) {
  const { t } = useLingua();
  const votatoQui = mioVoto === c.id;
  return (
    <div className={`pannello ${stili.scheda} ${votatoQui ? stili.schedaEvidente : ""}`}>
      <span className={stili.nome}>{c.nome}</span>
      {c.descrizione && <p className={stili.nota}>{c.descrizione}</p>}
      {c.campioni.some((camp) => camp.url) && (
        <div className={stili.carteRiga}>
          {c.campioni.filter((camp) => camp.url).map((camp, i) => (
            /* eslint-disable-next-line @next/next/no-img-element */
            <img key={i} src={camp.url as string} alt={camp.etichetta ?? c.nome}
              style={{ width: 110, borderRadius: 8 }} />
          ))}
        </div>
      )}
      {c.percentuale !== null && (
        <div className={stili.misura}>
          <div className={stili.barra}><span style={{ width: `${c.percentuale}%` }} /></div>
          {t.vota_percentuale(c.percentuale)}
        </div>
      )}
      <button
        className={votatoQui ? "bottone" : "bottone-secondario"}
        disabled={inCorso || votatoQui}
        onClick={onVota}
      >
        {votatoQui ? t.vota_votato : t.vota_bottone}
      </button>
    </div>
  );
}
