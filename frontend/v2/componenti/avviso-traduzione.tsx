"use client";

/* Il riquadro della traduzione automatica (v9.5), in cima ai contenuti che esistono solo in inglese (articoli del
 * blog, schede di carte, stese e mazzi). Si vede solo dove il browser sa tradurre (Chrome desktop 138+) e la lingua
 * scelta non è quella del contenuto. Il menu è il selettore di lingua del sito: cambiarlo cambia e salva la lingua di
 * tutto il sito, e la pagina si ritraduce. */

import { f } from "@/v2/i18n";
import { useLingua } from "@/v2/lib/lingua";
import type { StatoTraduzione } from "@/v2/lib/usa-traduzione";
import { SelettoreLingua } from "./testata";

function nomeLingua(codice: string | null, locale: string): string {
  if (!codice) return "";
  try {
    return new Intl.DisplayNames([locale], { type: "language" }).of(codice) ?? codice;
  } catch {
    return codice;
  }
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
      {(stato.fase === "tradotta" || stato.fase === "originale" || stato.fase === "offerta") && (
        <span className="small" style={{ display: "inline-flex", alignItems: "center", gap: ".4rem" }}>
          {k.traduzione_altra_lingua} <SelettoreLingua />
        </span>
      )}
      {stato.fase === "tradotta" && (
        <button type="button" className="button button-quiet button-small" style={{ minHeight: 44 }} onClick={stato.nonPiu}>
          {k.traduzione_mai}
        </button>
      )}
    </aside>
  );
}
