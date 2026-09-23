"use client";

/* Una lettura conclusa, da rileggere: il tavolo, il colloquio, il responso,
 * il diario. */

import { use, useCallback, useState } from "react";
import { useRouter } from "next/navigation";
import {
  annotaLettura, cancellaLettura, condividiLettura, leggiLettura,
} from "@/lib/api";
import { useLingua } from "@/lib/lingua";
import { useAzione, useCarica } from "@/lib/usa";
import { Markdown } from "../../componenti/markdown";
import { Involucro } from "../../componenti/testata";
import { Tavolo, type Posata } from "../../leggi/tavolo";
import pag from "../../pagine.module.css";
import stili from "../../leggi/leggi.module.css";

export default function PaginaDettaglio({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  return (
    <Involucro larga>
      <Dettaglio id={id} />
    </Involucro>
  );
}

function Dettaglio({ id }: { id: string }) {
  const { t, lingua } = useLingua();
  const router = useRouter();
  const lettura = useCarica(useCallback((tok: string | null) => leggiLettura(tok, id), [id]), [id]);
  const { esegui } = useAzione();
  const [link, setLink] = useState<string | null>(null);

  if (lettura.errore) return <p className={pag.errore}>{lettura.errore}</p>;
  const l = lettura.dati;
  if (!l) return null;

  const posate: Posata[] = l.cards.map((c) => ({
    posizione: c.posizione,
    slot: null,
    calcolata: c.calcolata,
    rivelata: c.rivelata,
    carta: c.carta,
    rovescio: c.rovescio,
    interpretazione: c.interpretazione,
    dignita: l.dignita?.[String(c.posizione)] ?? null,
  }));

  const annota = async (esito: string) => {
    await esegui((tok) => annotaLettura(tok, id, esito));
    lettura.ricarica();
  };
  const condividi = async () => {
    const r = await esegui((tok) => condividiLettura(tok, id, !l.share_token));
    setLink(r?.share_token ? `${window.location.origin}/s/${r.share_token}` : null);
    lettura.ricarica();
  };
  const cancella = async () => {
    if (!window.confirm(t.conferma_cancella)) return;
    await esegui((tok) => cancellaLettura(tok, id));
    router.push("/letture");
  };

  return (
    <div className={stili.consulto}>
      <div className={stili.colonnaTavolo}>
        <div className={stili.intestazione}>
          <span className={stili.stesaEtichetta}>{lingua === "en" ? l.stesa_dati.nome_en : l.stesa_dati.nome}</span>
          <p className={`oracolo ${stili.domandaTitolo}`}>«{l.question}»</p>
          <p className={pag.nota}>{new Date(l.created_at).toLocaleString("it-IT")}</p>
        </div>
        <Tavolo stesa={l.stesa_dati} posate={posate} prossima={null} rivelazioneInCorso={false} evidenzia={null} />
      </div>
      <div className={stili.colonnaDialogo}>
        <div className={`pannello ${pag.scheda}`}>
          <span className={pag.etichetta}>{t.si_e_avverato}</span>
          <div className={pag.linea}>
            {(["si", "in_parte", "no"] as const).map((e) => (
              <button key={e} className={l.feedback === e ? "bottone" : "bottone-secondario"} onClick={() => annota(e)}>
                {t[e]}
              </button>
            ))}
          </div>
          <div className={pag.linea}>
            <button className="bottone-secondario" onClick={condividi}>
              {l.share_token ? (lingua === "en" ? "Stop sharing" : "Ritira la condivisione") : t.condividi}
            </button>
            <button className="bottone-secondario" onClick={cancella}>{t.cancella}</button>
          </div>
          {(link || l.share_token) && (
            <p className={pag.nota}>
              <a href={link ?? `/s/${l.share_token}`}>{link ?? `/s/${l.share_token}`}</a>
            </p>
          )}
          {l.context_summary && (
            <>
              <span className={pag.etichetta}>{lingua === "en" ? "The picture" : "Il quadro"}</span>
              <p className="oracolo">{l.context_summary}</p>
            </>
          )}
        </div>
      </div>
      {l.synthesis && (
        <div className={stili.zonaResponso}>
          <section className={`pannello ${stili.responso}`}>
            <h2 className={stili.responsoTitolo}>✦ {t.il_responso} ✦</h2>
            <Markdown testo={l.synthesis} className={`oracolo ${stili.responsoTesto}`} />
            <p className={stili.disclaimerFinale}>{l.disclaimer}</p>
            {l.commitment && (
              <details className={stili.verifica}>
                <summary>{t.verifica_mazzo}</summary>
                <p>{t.verifica_testo}</p>
                <code>{l.commitment}</code>
                {l.deck_salt && <p>salt: <code>{l.deck_salt}</code></p>}
              </details>
            )}
          </section>
        </div>
      )}
    </div>
  );
}
