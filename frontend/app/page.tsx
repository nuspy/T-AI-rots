"use client";

/* La soglia: chi arriva vede subito le carte muoversi e capisce cosa succede
 * in una lettura, prima ancora di registrarsi. */

import { useCallback, useEffect } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { elencaCarte, elencaStese } from "@/lib/api";
import { useLingua } from "@/lib/lingua";
import { useCarica } from "@/lib/usa";
import { Carta } from "./componenti/carta";
import { Testata } from "./componenti/testata";
import stili from "./soglia.module.css";

const PASSI_IT = [
  ["Domanda", "Scrivi ciò che vuoi sapere: una scelta, un sentimento, o semplicemente il futuro."],
  ["Intervista", "L'oracolo ti fa poche domande per capire il contesto — mai la risposta al tuo quesito."],
  ["Le carte", "Scegli dal ventaglio: le carte sono già assegnate e si girano una a una sul tavolo."],
  ["Il responso", "L'AI unisce domanda, colloquio, stesa, dignità e simboli in una lettura coerente."],
];
const PASSI_EN = [
  ["Question", "Write what you want to know: a choice, a feeling, or simply the future."],
  ["Interview", "The oracle asks a few questions to understand the context — never the answer to your question."],
  ["The cards", "Choose from the fan: the cards are already assigned and turn over one by one on the table."],
  ["The answer", "The AI joins question, interview, spread, dignities and symbols into one coherent reading."],
];

export default function Soglia() {
  const { t, lingua } = useLingua();
  const carte = useCarica(useCallback(() => elencaCarte(), []), [], { pubblico: true });
  const stese = useCarica(useCallback(() => elencaStese(), []), [], { pubblico: true });
  const maggiori = (carte.dati ?? []).filter((c) => c.arcano === "maggiore");
  const scelte = [0, 1, 2, 17, 19, 21].map((n) => maggiori.find((c) => c.numero === n)).filter(Boolean);
  const passi = lingua === "en" ? PASSI_EN : PASSI_IT;

  /* Chi arriva da un invito porta il codice nell'indirizzo: lo si ricorda
   * fino alla registrazione, e il profilo lo propone da riscattare. */
  useEffect(() => {
    const codice = new URLSearchParams(window.location.search).get("invito");
    if (codice) {
      try {
        window.localStorage.setItem("invito", codice.toUpperCase());
      } catch {
        /* archiviazione non disponibile: il codice si scrive a mano */
      }
    }
  }, []);

  return (
    <div className={stili.soglia}>
      <Testata />
      <section className={stili.eroe}>
        <div className={stili.eroeTesto}>
          <motion.p className={stili.sovratitolo} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
            ✦ {lingua === "en" ? "Thoth Tarot · Aleister Crowley" : "Tarocco di Thoth · Aleister Crowley"} ✦
          </motion.p>
          <motion.h1 className={stili.titolo} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9 }}>
            T<span>·</span>AI<span>·</span>rots
          </motion.h1>
          <motion.p className={`oracolo ${stili.motto}`} initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            transition={{ delay: 0.5, duration: 1 }}>
            {t.motto}
          </motion.p>
          <motion.div className={stili.inviti} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}>
            <Link href="/leggi" className="bottone">✦ {t.inizia}</Link>
            <Link href="/carta-del-giorno" className="bottone-secondario">☉ {t.nav_giorno}</Link>
          </motion.div>
        </div>
        <div className={stili.eroeCarte} aria-hidden="true">
          {scelte.map((c, i) => (
            <motion.div
              key={c!.id}
              className={stili.cartaVolante}
              style={{ left: `${8 + i * 14}%`, zIndex: i === 2 ? 10 : i }}
              initial={{ opacity: 0, y: 80, rotate: -30 + i * 12 }}
              animate={{ opacity: 1, y: [0, -14, 0], rotate: -22 + i * 9 }}
              transition={{
                opacity: { delay: 0.3 + i * 0.12, duration: 0.8 },
                rotate: { delay: 0.3 + i * 0.12, duration: 0.8 },
                y: { duration: 4 + i * 0.4, repeat: Infinity, ease: "easeInOut", delay: i * 0.3 },
              }}
            >
              <Carta carta={c} rivelata={i % 2 === 0} larghezza={150} />
            </motion.div>
          ))}
        </div>
      </section>

      <section className={stili.sezione}>
        <h2>{lingua === "en" ? "How a reading unfolds" : "Come si svolge una lettura"}</h2>
        <div className={stili.passi}>
          {passi.map(([titolo, testo], i) => (
            <motion.div key={titolo} className={`pannello ${stili.passo}`} initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.1 }}>
              <span className={stili.numeroPasso}>{["I", "II", "III", "IV"][i]}</span>
              <h3>{titolo}</h3>
              <p>{testo}</p>
            </motion.div>
          ))}
        </div>
      </section>

      <section className={stili.sezione}>
        <h2>{lingua === "en" ? "Five traditional spreads" : "Cinque stese della tradizione"}</h2>
        <div className={stili.stese}>
          {(stese.dati ?? []).map((s) => (
            <Link key={s.id} href={`/leggi?stesa=${s.id}`} className={`pannello ${stili.stesa}`}>
              <strong>{lingua === "en" ? s.nome_en : s.nome}</strong>
              <span>{s.posizioni.length} {t.carte} · {s.mazzo === "maggiori" ? t.maggiori : t.completo}</span>
              <p>{s.descrizione}</p>
            </Link>
          ))}
        </div>
      </section>

      <section className={stili.sezione}>
        <h2>{lingua === "en" ? "Esoteric rigour" : "Rigore esoterico"}</h2>
        <div className={stili.rigore}>
          <p className="oracolo">
            {lingua === "en"
              ? "Every card carries its real Thoth attributions — Hebrew letter, path on the Tree of Life, decan, sephira — and is read on several levels. Neighbouring cards modulate each other through Crowley's elemental dignities; in the Simple Cross the synthesis is computed by theosophical addition, as Oswald Wirth taught."
              : "Ogni carta porta le sue vere attribuzioni del Thoth — lettera ebraica, sentiero sull'Albero della Vita, decano, sephira — ed è letta su più livelli. Le carte vicine si modulano a vicenda con le dignità elementali di Crowley; nella croce semplice la sintesi si calcola per somma teosofica, come insegnava Oswald Wirth."}
          </p>
          <p className="oracolo">
            {lingua === "en"
              ? "The deck is shuffled and sealed with a cryptographic hash before you choose: at the end of the reading you can verify that no card was changed after your choice."
              : "Il mazzo è mescolato e sigillato con un hash crittografico prima che tu scelga: a fine lettura puoi verificare che nessuna carta sia stata cambiata dopo la tua scelta."}
          </p>
        </div>
        <p className={stili.avvertenza}>
          {lingua === "en"
            ? "An AI reading, coherent and rigorous on the esoteric level. It is not a certainty: it shows the most probable of futures. There is no scientific evidence that tarot predictions are valid."
            : "Una lettura AI, coerente e rigorosa sul piano esoterico. Non è una certezza: mostra il più probabile dei futuri. Non esiste alcuna base scientifica che dimostri la validità delle previsioni dei tarocchi."}
        </p>
      </section>
    </div>
  );
}
