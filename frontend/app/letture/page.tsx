"use client";

/* Lo storico: ogni lettura è salvata, e ogni lettura si può cancellare. */

import Link from "next/link";
import { motion } from "framer-motion";
import { cancellaLettura, elencaLetture } from "@/lib/api";
import { useLingua } from "@/lib/lingua";
import { useAzione, useCarica } from "@/lib/usa";
import { Involucro } from "../componenti/testata";
import stili from "../pagine.module.css";

const STATI: Record<string, string> = {
  intervista: "in intervista",
  ventaglio: "pronta da mescolare",
  scelta: "carte da scegliere",
  rivelazione: "carte da rivelare",
  sintesi: "in attesa del responso",
  completata: "completata",
  annullata: "sospesa",
};

export default function PaginaLetture() {
  const { t, lingua } = useLingua();
  return (
    <Involucro
      titolo={t.nav_letture}
      sottotitolo={lingua === "en"
        ? "Every reading is saved. You can reopen it, note whether it came true, or delete it for good."
        : "Ogni lettura resta salvata. Puoi riaprirla, annotare se si è avverata, o cancellarla per sempre."}
    >
      <Elenco />
    </Involucro>
  );
}

function Elenco() {
  const { t } = useLingua();
  const letture = useCarica(elencaLetture);
  const { esegui } = useAzione();

  const cancella = async (id: string) => {
    if (!window.confirm(t.conferma_cancella)) return;
    await esegui((tok) => cancellaLettura(tok, id));
    letture.ricarica();
  };

  if (letture.errore) return <p className={stili.errore}>{letture.errore}</p>;
  if (!letture.dati) return null;
  if (letture.dati.letture.length === 0) {
    return (
      <div className={`pannello ${stili.vuoto}`}>
        <p className="oracolo">{t.nessuna_lettura}</p>
        <Link href="/leggi" className="bottone">✦ {t.inizia}</Link>
      </div>
    );
  }
  return (
    <ul className={stili.elenco}>
      {letture.dati.letture.map((l, i) => (
        <motion.li key={l.id} className={`pannello ${stili.riga}`} initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.03 }}>
          <div className={stili.rigaCorpo}>
            <Link href={l.status === "completata" ? `/letture/${l.id}` : `/leggi?id=${l.id}`}>
              <p className={stili.rigaTitolo}>«{l.question}»</p>
            </Link>
            <p className={stili.rigaDettagli}>
              {l.stesa} · {new Date(l.created_at).toLocaleDateString("it-IT", { day: "numeric", month: "long", year: "numeric" })}
              {" · "}{STATI[l.status] ?? l.status}
              {l.carte.length > 0 && ` · ${l.carte.slice(0, 4).join(", ")}${l.carte.length > 4 ? "…" : ""}`}
              {l.feedback && ` · ${t.si_e_avverato} ${t[l.feedback as "si" | "in_parte" | "no"]}`}
            </p>
          </div>
          <button className="bottone-secondario" onClick={() => cancella(l.id)} aria-label={`${t.cancella}: ${l.question}`}>
            {t.cancella}
          </button>
        </motion.li>
      ))}
    </ul>
  );
}
