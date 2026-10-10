"use client";

/* I termini di servizio (10/10/2026). Il testo esiste solo in inglese (`en.termini`, lo stesso in ogni cartella di
 * lingua): la pagina lo mostra sempre in inglese, con `lang="en"`, e dove il browser sa tradurre (Translator API di
 * Chrome) lo traduce sul dispositivo nella lingua della traduzione, come gli articoli del blog: `AvvisoTraduzione` lo
 * dice e offre l'originale, e la nota `originale` ricorda che vale il testo inglese.
 *
 * I dati del gestore sono quelli del titolare dell'informativa (`GET /privacy/titolare`, letti anche dal server): i
 * {segnaposto} si riempiono qui, e un campo vuoto mostra la frase neutra accanto, mai un segnaposto. */

import { useRef } from "react";
import { AvvisoTraduzione } from "@/v2/componenti/avviso-traduzione";
import LinkV2 from "@/v2/componenti/link";
import { f } from "@/v2/i18n";
import { en } from "@/v2/i18n/en";
import { P } from "@/v2/lib/api-percorsi";
import { useLinguaTraduzione } from "@/v2/lib/lingua-traduzione";
import { R } from "@/v2/lib/percorsi";
import { usePubblico } from "@/v2/lib/usa";
import { useTraduzione } from "@/v2/lib/usa-traduzione";
import type { TitolarePubblico } from "./privacy";

export function Termini() {
  const k = en.termini;
  const titolare = usePubblico<TitolarePubblico>(P.titolare()).dati;
  const testa = useRef<HTMLDivElement>(null);
  const corpo = useRef<HTMLDivElement>(null);
  const linguaTraduzione = useLinguaTraduzione().lingua;
  const traduzione = useTraduzione([testa, corpo], linguaTraduzione, { sorgente: "en", chiave: "termini" });

  return (
    <>
      <section className="subhero subhero-compact">
        <AvvisoTraduzione stato={traduzione} />
        <div ref={testa} lang="en">
          <p className="eyebrow">{k.eyebrow}</p>
          <h1 className="display">{k.titolo}</h1>
          <p className="section-intro">{k.intro}</p>
          <p className="small muted termini-originale">{k.originale}</p>
        </div>
      </section>

      <section className="band band-tight">
        <div ref={corpo} lang="en" className="termini">
          <section className="panel" aria-labelledby="tm-chi">
            <h2 id="tm-chi">{k.chi_titolo}</h2>
            {titolare ? (
              <>
                <p>{titolare.nome ? f(k.chi_testo, { titolare: titolare.nome }) : k.chi_testo_senza_nome}</p>
                {titolare.indirizzo && <p>{f(k.chi_indirizzo, { indirizzo: titolare.indirizzo })}</p>}
                {titolare.codice_fiscale && <p>{f(k.chi_codice, { codice: titolare.codice_fiscale })}</p>}
                <p>
                  {titolare.email_privacy ? (
                    <>
                      {f(k.chi_email, { email: "" })}
                      <a className="inline" href={`mailto:${titolare.email_privacy}`} translate="no">{titolare.email_privacy}</a>
                    </>
                  ) : k.chi_email_vuoto}
                </p>
              </>
            ) : (
              <p className="muted" aria-busy="true">{k.chi_testo_senza_nome}</p>
            )}
          </section>

          {k.sezioni.map((s, i) => (
            <section key={s.titolo} className="panel" aria-labelledby={`tm-${i + 1}`}>
              <h2 id={`tm-${i + 1}`}>{s.titolo}</h2>
              {s.testi.map((x) => <p key={x}>{x}</p>)}
            </section>
          ))}

          <p className="small termini-piede">
            <LinkV2 className="inline" href={R.privacy}>{k.privacy_link}</LinkV2>
            <span className="muted"> · {k.versione}</span>
          </p>
        </div>
      </section>
    </>
  );
}
