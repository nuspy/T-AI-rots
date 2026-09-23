"use client";

/* Il profilo: la data di nascita per le carte personali, il codice invito. */

import { useState } from "react";
import { aggiornaProfilo, leggiProfilo, riscattaInvito } from "@/lib/api";
import { useLingua } from "@/lib/lingua";
import { useAzione, useCarica } from "@/lib/usa";
import { Carta } from "../componenti/carta";
import { Involucro } from "../componenti/testata";
import stili from "../pagine.module.css";

export default function PaginaProfilo() {
  const { t } = useLingua();
  return (
    <Involucro titolo={t.nav_profilo}>
      <Profilo />
    </Involucro>
  );
}

function Profilo() {
  const profilo = useCarica(leggiProfilo);
  const { esegui, inCorso, errore } = useAzione();
  const [nascita, setNascita] = useState<string | null>(null);
  const [codice, setCodice] = useState(() => {
    try {
      return typeof window !== "undefined" ? (window.localStorage.getItem("invito") ?? "") : "";
    } catch {
      return "";
    }
  });
  const [esito, setEsito] = useState<string | null>(null);
  const [copiato, setCopiato] = useState(false);
  const p = profilo.dati;
  if (profilo.errore) return <p className={stili.errore}>{profilo.errore}</p>;
  if (!p) return null;

  const invito = typeof window !== "undefined" ? `${window.location.origin}/?invito=${p.referral_code}` : "";

  return (
    <>
      <section className={`pannello ${stili.scheda} ${stili.sezione}`}>
        <span className={stili.etichetta}>{p.email}</span>
        <h2 className={stili.sezioneTitolo}>Le tue carte personali</h2>
        <p className={stili.nota}>
          Dalla data di nascita si ricavano, per riduzione teosofica, la carta dell&apos;anima — la lezione di una vita — e la carta
          del tuo anno personale. Se la indichi, l&apos;oracolo ne terrà conto nelle letture.
        </p>
        <div className={stili.linea}>
          <label className={stili.campo}>
            Data di nascita
            <input type="date" value={nascita ?? p.birth_date ?? ""} onChange={(e) => setNascita(e.target.value)} />
          </label>
          <button className="bottone" disabled={inCorso || !nascita}
            onClick={async () => { await esegui((t) => aggiornaProfilo(t, { birth_date: nascita })); profilo.ricarica(); }}>
            Salva
          </button>
        </div>
        {errore && <p className={stili.errore}>{errore}</p>}
        {p.carta_anima && p.carta_anno && (
          <div className={stili.carteRiga}>
            {[["Carta dell'anima", p.carta_anima], ["Carta dell'anno", p.carta_anno]].map(([titolo, c]) => (
              <div key={titolo as string} style={{ textAlign: "center" }}>
                <Carta carta={c as typeof p.carta_anima} rivelata larghezza={150} />
                <p className={stili.etichetta} style={{ marginTop: 8 }}>{titolo as string}</p>
              </div>
            ))}
          </div>
        )}
      </section>

      <section className={`pannello ${stili.scheda} ${stili.sezione}`}>
        <h2 className={stili.sezioneTitolo}>Invita chi ami</h2>
        <p className={stili.nota}>Per ogni persona che si iscrive con il tuo codice, tu e lei ricevete 3 letture in regalo.</p>
        <span className={stili.codice}>{p.referral_code}</span>
        <div className={stili.linea}>
          <button className="bottone-secondario" onClick={async () => {
            if (navigator.share) {
              try { await navigator.share({ title: "T·AI·rots", text: `Il mio codice invito: ${p.referral_code}`, url: invito }); return; } catch { /* annullato */ }
            }
            await navigator.clipboard?.writeText(`${p.referral_code} — ${invito}`);
            setCopiato(true);
          }}>
            {copiato ? "Copiato" : "Condividi il codice"}
          </button>
        </div>
        {!p.invitato && (
          <div className={stili.linea}>
            <label className={stili.campo}>
              Hai un codice invito?
              <input value={codice} onChange={(e) => setCodice(e.target.value.toUpperCase())} maxLength={16} />
            </label>
            <button className="bottone" disabled={inCorso || codice.length < 4} onClick={async () => {
              const r = await esegui((t) => riscattaInvito(t, codice));
              if (r) {
                setEsito(`Hai ricevuto ${r.crediti} letture in regalo.`);
                try { window.localStorage.removeItem("invito"); } catch { /* pazienza */ }
                profilo.ricarica();
              }
            }}>
              Riscatta
            </button>
          </div>
        )}
        {esito && <p className={stili.avvisoBuono}>{esito}</p>}
      </section>
    </>
  );
}
