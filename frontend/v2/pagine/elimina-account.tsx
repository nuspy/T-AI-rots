"use client";

/* «Elimina l'account» (GDPR, Fase 1). Una pagina pubblica: Google Play vuole un indirizzo che spieghi come si cancella
 * l'account e che cosa succede ai dati, apribile anche senza l'app e senza essere entrati.
 *
 * - Chi non è entrato legge cosa succede e come fare, ed entra per procedere.
 * - Chi è entrato può scaricare prima i suoi dati, poi conferma due volte: una casella («ho capito») e la parola da
 *   scrivere. La richiesta chiude subito l'account e le sessioni; per 30 giorni, rientrando, la si può annullare; poi
 *   i dati si cancellano (la contabilità resta, pseudonimizzata). */

import { useState } from "react";
import { chiediCancellazione, scaricaEsportazione, type StatoCancellazione } from "@/lib/privacy";
import { useSessione } from "@/lib/sessione";
import { f } from "@/v2/i18n";
import LinkV2 from "@/v2/componenti/link";
import { useLingua } from "@/v2/lib/lingua";
import { R } from "@/v2/lib/percorsi";
import { useAzione } from "@/v2/lib/usa";

export function EliminaAccount() {
  const { t, locale } = useLingua();
  const k = t.profilo;
  const sessione = useSessione();
  const { esegui, inCorso, errore } = useAzione();
  const [capito, setCapito] = useState(false);
  const [parola, setParola] = useState("");
  const [fatto, setFatto] = useState<StatoCancellazione | null>(null);
  const [esportato, setEsportato] = useState<string | null>(null);
  const giusta = parola.trim().toLocaleUpperCase(locale) === k.elimina_parola.toLocaleUpperCase(locale);
  const data = (iso: string | null) =>
    iso ? new Date(iso).toLocaleDateString(locale, { day: "numeric", month: "long", year: "numeric" }) : "";

  return (
    <>
    <section className="subhero subhero-compact">
      <p className="eyebrow">{k.elimina_eyebrow}</p>
      <h1 className="display">{k.elimina_h1}</h1>
      <p className="section-intro">{k.elimina_intro}</p>
    </section>
    <section className="band band-tight elimina-account">
      <div className="profile-grid">
        <section className="panel wide" aria-labelledby="el-cosa">
          <h2 id="el-cosa">{k.elimina_cosa_titolo}</h2>
          <ol className="small elimina-passi">
            <li>{f(k.elimina_passo1, { giorni: 30 })}</li>
            <li>{k.elimina_passo2}</li>
            <li>{k.elimina_passo3}</li>
          </ol>
          <h3>{k.elimina_resta_titolo}</h3>
          <p className="small">{k.elimina_resta}</p>
          <p className="small">{k.elimina_app} <LinkV2 className="inline" href={R.privacy}>{k.stat_privacy}</LinkV2></p>
        </section>

        {!sessione.pronta ? null : !sessione.autenticata ? (
          <section className="panel wide" aria-labelledby="el-entra">
            <h2 id="el-entra">{k.elimina_entra_titolo}</h2>
            <p className="small">{k.elimina_entra_testo}</p>
            <button type="button" className="button" onClick={() => sessione.entra(R.elimina)}>{k.entra}</button>
          </section>
        ) : fatto ? (
          <section className="panel wide" aria-labelledby="el-fatto" role="status">
            <h2 id="el-fatto">{k.elimina_fatto_titolo}</h2>
            <p>{f(k.elimina_fatto, { data: data(fatto.definitiva_il) })}</p>
            <button type="button" className="button button-quiet" onClick={sessione.esci}>{t.comune.cancellazione_esci}</button>
          </section>
        ) : (
          <section className="panel wide" aria-labelledby="el-conferma">
            <h2 id="el-conferma">{k.elimina_titolo}</h2>
            <p className="small">{k.elimina_prima}</p>
            <button type="button" className="button button-quiet button-small" disabled={inCorso} onClick={async () => {
              setEsportato(null);
              const r = await esegui((tok) => scaricaEsportazione(tok));
              if (r) setEsportato(r.ok ? k.esporta_fatto : f(k.esporta_attendi, { data: data(r.prossimaDal) }));
            }}>{k.esporta_cta}</button>
            {esportato && <p className="small" role="status">{esportato}</p>}

            <label className="check" style={{ marginTop: ".8rem" }}>
              <input type="checkbox" checked={capito} onChange={(e) => setCapito(e.target.checked)} />
              <span>{f(k.elimina_capito, { giorni: 30 })}</span>
            </label>
            <label className="field">
              <span>{f(k.elimina_scrivi, { parola: k.elimina_parola })}</span>
              <input value={parola} onChange={(e) => setParola(e.target.value)} autoComplete="off" autoCapitalize="characters"
                spellCheck={false} disabled={!capito} aria-invalid={parola !== "" && !giusta} />
            </label>
            <button type="button" className="button button-danger" disabled={!capito || !giusta || inCorso} onClick={async () => {
              const r = await esegui((tok) => chiediCancellazione(tok));
              if (r) setFatto(r);
            }}>{k.elimina_cta}</button>
            {errore && <p className="error" role="alert">{errore}</p>}
          </section>
        )}
      </div>
    </section>
    </>
  );
}
