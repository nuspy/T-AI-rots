"use client";

/* Il riquadro della traduzione automatica (v9.5), in cima ai contenuti che esistono solo in inglese (articoli del
 * blog, schede di carte, stese e mazzi). Si vede solo dove il browser sa tradurre (Chrome desktop 138+) e la lingua
 * della traduzione non è quella del contenuto. Il menu è la lingua della TRADUZIONE (9/10): parte da quella del sito,
 * e una scelta diversa resta in un cookie suo (`lingua-traduzione.ts`), senza cambiare la lingua del sito. */

import { useId } from "react";
import { f } from "@/v2/i18n";
import { useLingua } from "@/v2/lib/lingua";
import { LINGUE_TRADUZIONE, nomeNativo, useLinguaTraduzione } from "@/v2/lib/lingua-traduzione";
import type { StatoTraduzione } from "@/v2/lib/usa-traduzione";

function nomeLingua(codice: string | null, locale: string): string {
  if (!codice) return "";
  try {
    return new Intl.DisplayNames([locale], { type: "language" }).of(codice) ?? codice;
  } catch {
    return codice;
  }
}

/** La lingua verso cui tradurre: codice e nome nativo, come il selettore del sito. */
function SceltaLinguaTraduzione() {
  const { t } = useLingua();
  const { lingua, scegli } = useLinguaTraduzione();
  const id = useId();
  return (
    <span className="small traduzione-lingua">
      <label htmlFor={id}>{t.comune.traduzione_lingua}</label>
      <select id={id} value={lingua} onChange={(e) => scegli(e.target.value)}>
        {LINGUE_TRADUZIONE.map((c) => <option key={c} value={c}>{`${c.toUpperCase()} · ${nomeNativo(c)}`}</option>)}
      </select>
    </span>
  );
}

export function AvvisoTraduzione({ stato }: { stato: StatoTraduzione }) {
  const { t, locale } = useLingua();
  const k = t.comune;
  if (stato.fase === "nessuna") return null;
  const da = nomeLingua(stato.da, locale);
  const a = nomeLingua(stato.a, locale);
  return (
    <aside className="panel traduzione-avviso" role="status" aria-live="polite" data-no-trad
           style={{ display: "flex", flexWrap: "wrap", gap: ".5rem .9rem", alignItems: "center", margin: "0 0 1rem", padding: ".7rem .9rem" }}>
      {stato.fase === "offerta" && (
        <>
          <span className="small">{f(k.traduzione_offerta, { lingua: a })}</span>
          <button type="button" className="button button-small" style={{ minHeight: 44 }} onClick={stato.traduci}>
            {k.traduzione_traduci}
          </button>
        </>
      )}
      {stato.fase === "scarico" && (
        <span className="small">{f(k.traduzione_scarico, { p: stato.percento ?? 0 })}</span>
      )}
      {stato.fase === "in_corso" && <span className="small">{k.traduzione_in_corso}</span>}
      {stato.fase === "tradotta" && (
        <>
          <span className="small">{f(k.traduzione_tradotta, { da })}</span>
          <button type="button" className="button button-quiet button-small" style={{ minHeight: 44 }} onClick={stato.mostraOriginale}>
            {f(k.traduzione_originale, { da })}
          </button>
        </>
      )}
      {stato.fase === "originale" && (
        <>
          <span className="small">{f(k.traduzione_e_originale, { da })}</span>
          <button type="button" className="button button-small" style={{ minHeight: 44 }} onClick={stato.traduci}>
            {f(k.traduzione_traduci_in_lingua, { lingua: a })}
          </button>
        </>
      )}
      {stato.fase === "errore" && <span className="small">{k.traduzione_errore}</span>}
      {(stato.fase === "tradotta" || stato.fase === "originale" || stato.fase === "offerta" || stato.fase === "errore") && (
        <SceltaLinguaTraduzione />
      )}
      {stato.fase === "tradotta" && (
        <button type="button" className="button button-quiet button-small" style={{ minHeight: 44 }} onClick={stato.nonPiu}>
          {k.traduzione_mai}
        </button>
      )}
    </aside>
  );
}
