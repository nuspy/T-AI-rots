"use client";

/* Una lettura condivisa: la porta d'ingresso di chi riceve il link. Niente
 * colloquio, niente nome: solo domanda, carte e responso. */

import { use, useCallback } from "react";
import Link from "next/link";
import { leggiCondivisa } from "@/lib/api";
import { useLingua } from "@/lib/lingua";
import { useCarica } from "@/lib/usa";
import { Markdown } from "../../componenti/markdown";
import { Involucro } from "../../componenti/testata";
import { Tavolo, type Posata } from "../../leggi/tavolo";
import stili from "../../leggi/leggi.module.css";

export default function PaginaCondivisa({ params }: { params: Promise<{ token: string }> }) {
  const { token } = use(params);
  return (
    <Involucro larga pubblica>
      <Condivisa token={token} />
    </Involucro>
  );
}

function Condivisa({ token }: { token: string }) {
  const { t } = useLingua();
  const l = useCarica(useCallback(() => leggiCondivisa(token), [token]), [token], { pubblico: true });
  if (l.errore) return <p className={stili.errore}>{l.errore}</p>;
  if (!l.dati || !l.dati.stesa) return null;
  const posate: Posata[] = l.dati.cards.map((c) => ({ ...c, slot: null, dignita: null }));
  return (
    <div>
      <div className={stili.intestazione}>
        <span className={stili.stesaEtichetta}>{l.dati.stesa.nome}</span>
        <p className={`oracolo ${stili.domandaTitolo}`}>«{l.dati.question}»</p>
      </div>
      <Tavolo stesa={l.dati.stesa} posate={posate} prossima={null} rivelazioneInCorso={false} evidenzia={null} />
      <div className={stili.zonaResponso}>
        <section className={`pannello ${stili.responso}`}>
          <h2 className={stili.responsoTitolo}>✦ {t.il_responso} ✦</h2>
          {l.dati.synthesis && <Markdown testo={l.dati.synthesis} className={`oracolo ${stili.responsoTesto}`} />}
          <p className={stili.disclaimerFinale}>{l.dati.disclaimer}</p>
          <div className={stili.azioniCentro}>
            <Link href="/leggi" className="bottone">✦ {t.inizia}</Link>
            <Link href="/carta-del-giorno" className="bottone-secondario">☉ {t.nav_giorno}</Link>
          </div>
        </section>
      </div>
    </div>
  );
}
