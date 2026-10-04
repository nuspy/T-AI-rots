"use client";

/* «Accesso dall'app» (v9, Fase 6), nelle schede Android e iOS. Le app entrano passando da Keycloak nel browser del
 * telefono, con il client pubblico `tarot-mobile`: Google su Android, Apple su iPhone. Il realm in produzione è nato
 * prima di quel client: il pulsante lo crea (una volta; se c'è già non lo tocca). Le credenziali dei social restano
 * quelle di «Accesso con i social», le stesse del sito. */

import Link from "next/link";
import { useState } from "react";
import { preparaAccessoApp } from "@/lib/app-mobili";
import { useAzione } from "@/lib/usa";
import comuni from "../comuni.module.css";
import stili from "./app-mobili.module.css";

export function AccessoApp({ piattaforma }: { piattaforma: "android" | "ios" }) {
  const { esegui, inCorso, errore } = useAzione();
  const [esito, setEsito] = useState<string | null>(null);
  const social = piattaforma === "android" ? "Google" : "Apple";

  return (
    <section className={comuni.riquadro} aria-labelledby={`titolo-accesso-${piattaforma}`}>
      <h2 id={`titolo-accesso-${piattaforma}`} className={comuni.riquadroTitolo}>Accesso dall&apos;app</h2>
      <p className={comuni.riquadroNota}>
        Nell&apos;app {piattaforma === "android" ? "per Android" : "per iPhone e iPad"} si entra solo con{" "}
        <strong>{social}</strong>, passando dalla pagina di accesso nel browser del telefono. Il social si configura una
        volta per il sito e per le app in <Link href="/accesso-social">Accesso con i social</Link>
        {piattaforma === "ios" ? " (lì la chiave .p8 di «Sign in with Apple» e la scadenza del segreto)" : ""}.
        Chi ha già un account con la stessa email lo ritrova; chi usa «Nascondi la mia email» di Apple può collegare
        Apple dal profilo del sito o usare il codice che l&apos;app gli mostra.
      </p>
      <p className={comuni.riquadroNota}>
        Una volta sola, prima della prima prova dell&apos;app: crea in Keycloak il client delle app (tarot-mobile).
      </p>
      <div className={stili.azioni}>
        <button type="button" className={comuni.secondaria} disabled={inCorso} onClick={async () => {
          setEsito(null);
          const r = await esegui((t) => preparaAccessoApp(t));
          if (r) setEsito(r.messaggio);
        }}>
          {inCorso ? "Preparazione…" : "Prepara l'accesso dall'app"}
        </button>
      </div>
      <div aria-live="polite">
        {errore && <p className={comuni.errore}>{errore}</p>}
        {esito && !errore && <p className={comuni.esito}>{esito}</p>}
      </div>
    </section>
  );
}
