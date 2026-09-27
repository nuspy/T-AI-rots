"use client";

/* «Hai un codice?»: un codice sconto (si applica ai prezzi della pagina, sul primo pagamento) e un codice regalo
 * (dà crediti subito). Si mostra solo a chi ha un account: un codice si lega a una persona.
 *
 * Il codice sconto si prova con **una** chiamata, sulla prima offerta a pagamento: se non esiste, l'errore è generale e
 * non si ripete su ogni offerta (il server limita i tentativi con codici inesistenti). Se esiste ma non vale per
 * quella offerta, resta applicato: ogni offerta dice da sé se lo accetta. */

import { useState } from "react";
import { anteprimaCoupon, motivoCodice, riscattaCodice } from "@/lib/api";
import { useLingua } from "@/lib/lingua";
import { useSessione } from "@/lib/sessione";
import { useToken } from "@/lib/usa";
import stili from "../pagine.module.css";

/* Motivi che riguardano una singola offerta: il codice esiste ed è buono, solo non vale lì. */
const PER_OFFERTA = new Set(["coupon_non_per_questo_piano", "coupon_azzera_abbonamento"]);

const normalizza = (testo: string) => testo.replace(/\s+/g, "").toUpperCase();

export function SezioneCodici({
  applicato, applica, provaSu, suRiscatto,
}: {
  applicato: string | null;
  applica: (codice: string | null) => void;
  /** Lo slug di un'offerta a pagamento su cui provare il codice sconto. */
  provaSu: string | null;
  suRiscatto: () => void;
}) {
  const { t } = useLingua();
  const sessione = useSessione();
  const token = useToken();

  const [sconto, setSconto] = useState("");
  const [erroreSconto, setErroreSconto] = useState<string | null>(null);
  const [regalo, setRegalo] = useState("");
  const [esitoRegalo, setEsitoRegalo] = useState<{ buono: boolean; testo: string } | null>(null);
  const [inCorso, setInCorso] = useState(false);

  if (!sessione.autenticata) return null;

  const messaggio = (e: unknown) => t.errori_codice[motivoCodice(e) ?? ""] ?? t.err_richiesta;

  const provaSconto = async (e: React.FormEvent) => {
    e.preventDefault();
    const codice = normalizza(sconto);
    if (!codice || !provaSu) return;
    setErroreSconto(null);
    setInCorso(true);
    try {
      await anteprimaCoupon(token, codice, provaSu);
      applica(codice);
    } catch (errore) {
      const motivo = motivoCodice(errore);
      if (motivo && PER_OFFERTA.has(motivo)) applica(codice);
      else setErroreSconto(messaggio(errore));
    } finally {
      setInCorso(false);
    }
  };

  const riscatta = async (e: React.FormEvent) => {
    e.preventDefault();
    const codice = normalizza(regalo);
    if (!codice) return;
    setEsitoRegalo(null);
    setInCorso(true);
    try {
      const r = await riscattaCodice(token, codice);
      setEsitoRegalo({ buono: true, testo: t.codice_riscattato(r.crediti) });
      setRegalo("");
      suRiscatto();
    } catch (errore) {
      setEsitoRegalo({ buono: false, testo: messaggio(errore) });
    } finally {
      setInCorso(false);
    }
  };

  return (
    <section className={stili.sezione} aria-labelledby="codici">
      <h2 id="codici" className={stili.sezioneTitolo}>{t.codici_titolo}</h2>

      {applicato ? (
        <p className={stili.avvisoBuono} role="status">
          {t.codice_applicato(applicato)}{" "}
          <button type="button" className="bottone-secondario" onClick={() => { applica(null); setSconto(""); }}>
            {t.codice_togli}
          </button>
        </p>
      ) : (
        <form onSubmit={provaSconto}>
          <div className={stili.linea}>
            <label className={stili.campo}>
              <span>{t.codice_sconto}</span>
              <input
                value={sconto}
                onChange={(e) => setSconto(e.target.value)}
                autoCapitalize="characters"
                autoComplete="off"
                spellCheck={false}
                maxLength={60}
                aria-describedby="codice-sconto-aiuto"
              />
            </label>
            <button className="bottone-secondario" type="submit" disabled={inCorso || !sconto.trim() || !provaSu}>
              {t.codice_applica}
            </button>
          </div>
          <p id="codice-sconto-aiuto" className={stili.nota}>{t.codice_sconto_aiuto}</p>
          {erroreSconto && <p className={stili.errore} role="alert">{erroreSconto}</p>}
        </form>
      )}

      <form onSubmit={riscatta} style={{ marginTop: 16 }}>
        <div className={stili.linea}>
          <label className={stili.campo}>
            <span>{t.codice_regalo}</span>
            <input
              value={regalo}
              onChange={(e) => setRegalo(e.target.value)}
              autoCapitalize="characters"
              autoComplete="off"
              spellCheck={false}
              maxLength={60}
              aria-describedby="codice-regalo-aiuto"
            />
          </label>
          <button className="bottone-secondario" type="submit" disabled={inCorso || !regalo.trim()}>
            {t.codice_riscatta}
          </button>
        </div>
        <p id="codice-regalo-aiuto" className={stili.nota}>{t.codice_regalo_aiuto}</p>
        {esitoRegalo && (
          <p className={esitoRegalo.buono ? stili.avvisoBuono : stili.errore} role={esitoRegalo.buono ? "status" : "alert"}>
            {esitoRegalo.testo}
          </p>
        )}
      </form>
    </section>
  );
}
