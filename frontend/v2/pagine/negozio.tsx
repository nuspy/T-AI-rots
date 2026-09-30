"use client";

/* Il negozio della v2 (specifica v2, §4 e §11): un'estensione fisica, non il motivo per cui si viene. Stessa
 * meccanica del sito — mazzi e prezzi dall'API, carrello, ordine con indirizzo per la scatola fisica, ritorno dal
 * pagamento verificato sul server, PDF scaricabile — con il ponte verso la lettura delle proprie carte. */

import { Suspense, useCallback, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { useTraccia } from "lanterna-osservatore/react";
import {
  apriOrdine, elencaIndirizzi, elencaMazzi, euro, leggiOrdine, mieiMazzi, scaricaPdfOrdine, urlPdfGratuito,
  type Mazzo, type RigaOrdine, type TipoVoceOrdine,
} from "@/lib/api";
import { useSessione } from "@/lib/sessione";
import { f } from "@/v2/i18n";
import { ImmagineCarta } from "@/v2/componenti/carta";
import LinkV2 from "@/v2/componenti/link";
import { useLingua } from "@/v2/lib/lingua";
import { R, indirizzoV2 } from "@/v2/lib/percorsi";
import { useAzione, useCarica } from "@/v2/lib/usa";

interface Voce { deckId: number; tipo: TipoVoceOrdine; nome: string; prezzo: number; valuta: string; quantita: number }
const chiave = (deckId: number, tipo: TipoVoceOrdine) => `${deckId}:${tipo}`;

export function BottonePdfV2({ ordineId, deckId, nome }: { ordineId: string; deckId: number; nome: string }) {
  const { t } = useLingua();
  const { token } = useSessione();
  const [inCorso, setInCorso] = useState(false);
  const [errore, setErrore] = useState(false);
  const scarica = async () => {
    setInCorso(true);
    setErrore(false);
    try {
      const blob = await scaricaPdfOrdine(token, ordineId, deckId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${nome || "deck"}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch {
      setErrore(true);
    } finally {
      setInCorso(false);
    }
  };
  return (
    <div style={{ marginTop: ".5rem" }}>
      <button type="button" className="button button-quiet button-small" disabled={inCorso} onClick={scarica} data-an="deck_pdf_viewed">
        {inCorso ? t.negozio.pdf_in_corso : `${t.negozio.scarica_pdf}${nome ? ` — ${nome}` : ""}`}
      </button>
      {errore && <p className="error">{t.negozio.pdf_errore}</p>}
    </div>
  );
}

export function Negozio() {
  return <Suspense fallback={null}><NegozioContenuto /></Suspense>;
}

function NegozioContenuto() {
  const { t, locale, prefissoIt } = useLingua();
  const k = t.negozio;
  const sessione = useSessione();
  const parametri = useSearchParams();
  const traccia = useTraccia();
  const mazzi = useCarica(elencaMazzi, [], { pubblico: true });
  const posseduti = useCarica(mieiMazzi);
  const indirizzi = useCarica(elencaIndirizzi);
  const { esegui, inCorso, errore } = useAzione();
  const [indirizzoScelto, setIndirizzoScelto] = useState<string | null>(null);
  const [carrello, setCarrello] = useState<Map<string, Voce>>(new Map());
  const [esito, setEsito] = useState<{ buono: boolean; testo: string } | null>(null);
  const [pagato, setPagato] = useState<{ id: string; pdf: RigaOrdine[] } | null>(null);

  const elenco = mazzi.dati ?? [];
  const idPosseduti = new Set(posseduti.dati?.deck_ids ?? []);

  /* Il ritorno dal pagamento (`?ordine=…`): lo stato vero lo dice il server. */
  useEffect(() => {
    const ordineId = parametri.get("ordine");
    if (!ordineId || !sessione.autenticata) return;
    let annullato = false;
    leggiOrdine(sessione.token, ordineId)
      .then((o) => {
        if (annullato) return;
        if (o.status === "pagato") {
          setEsito({ buono: true, testo: k.pagato });
          setCarrello(new Map());
          setPagato({ id: ordineId, pdf: o.righe.filter((r) => r.tipo === "pdf") });
          traccia("purchase_completed", { tipo: "ordine" });
          posseduti.ricarica();
        } else if (o.status !== "aperto") setEsito({ buono: false, testo: k.annullato });
      })
      .catch(() => { if (!annullato) setEsito({ buono: false, testo: k.non_verificato }); });
    return () => { annullato = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [parametri, sessione.autenticata, sessione.token]);

  const aggiungi = useCallback((m: Mazzo, tipo: TipoVoceOrdine) => {
    const prezzo = tipo === "digitale" ? (m.offerta_attiva ? (m.prezzo_digitale_scontato ?? m.prezzo_digitale) : m.prezzo_digitale)
      : tipo === "pdf" ? m.prezzo_stampa : m.prezzo_fisico;
    if (prezzo == null) return;
    setCarrello((prima) => {
      const nuovo = new Map(prima);
      const c = chiave(m.id, tipo);
      nuovo.set(c, { deckId: m.id, tipo, nome: m.nome, prezzo, valuta: m.valuta, quantita: (nuovo.get(c)?.quantita ?? 0) + 1 });
      return nuovo;
    });
  }, []);

  const voci = [...carrello.values()];
  const totale = voci.reduce((s, v) => s + v.prezzo * v.quantita, 0);
  const valuta = voci[0]?.valuta ?? "EUR";
  const serveIndirizzo = voci.some((v) => v.tipo === "fisico");
  const elencoIndirizzi = indirizzi.dati?.indirizzi ?? [];
  const indirizzoAttivo = indirizzoScelto ?? elencoIndirizzi.find((i) => i.predefinito)?.id ?? elencoIndirizzi[0]?.id ?? null;
  const nomeTipo = (tipo: TipoVoceOrdine) => (tipo === "digitale" ? k.digitale : tipo === "pdf" ? k.pdf : k.fisico);

  const completa = async () => {
    if (!sessione.autenticata) { sessione.entra(indirizzoV2(R.negozio, prefissoIt)); return; }
    if (serveIndirizzo && !indirizzoAttivo) return;
    const corpo = voci.map((v) => ({ deck_id: v.deckId, tipo: v.tipo, quantita: v.quantita }));
    const r = await esegui((tok) => apriOrdine(tok, corpo, indirizzoV2(R.negozio, prefissoIt), serveIndirizzo ? indirizzoAttivo ?? undefined : undefined));
    if (r?.url) window.location.assign(r.url);
  };

  return (
    <>
      <section className="band band-tight">
        {esito && (
          <div className={esito.buono ? "success" : "error"} role="status" style={{ marginBottom: "1.5rem" }}>
            <p style={{ margin: 0 }}>{esito.testo}</p>
            {pagato?.pdf.map((r) => (
              <BottonePdfV2 key={r.deck_id} ordineId={pagato.id} deckId={r.deck_id} nome={elenco.find((m) => m.id === r.deck_id)?.nome ?? ""} />
            ))}
          </div>
        )}
        {mazzi.errore && <p className="error">{mazzi.errore}</p>}
        {mazzi.dati && elenco.length === 0 && <p className="notice">{k.vuoto}</p>}
        <div className="shop-grid">
          {elenco.map((m) => {
            const mio = m.predefinito || idPosseduti.has(m.id);
            const scontato = m.offerta_attiva && m.prezzo_digitale_scontato != null;
            const nelCarrello = (["digitale", "pdf", "fisico"] as const).reduce((s, x) => s + (carrello.get(chiave(m.id, x))?.quantita ?? 0), 0);
            const riga = (tipo: TipoVoceOrdine, prezzo: number, barrato?: number | null) => (
              <div className="button-row" style={{ justifyContent: "space-between", padding: ".5rem 0", borderTop: "1px solid var(--line)" }}>
                <span>{nomeTipo(tipo)}</span>
                <span>
                  {barrato != null && <s className="small muted">{euro(barrato, m.valuta, locale)}</s>}{" "}
                  <b>{euro(prezzo, m.valuta, locale)}</b>
                </span>
                <button type="button" className="button button-quiet button-small" onClick={() => aggiungi(m, tipo)}
                  data-an="carrello_aggiunto" data-an-mazzo={m.slug} data-an-tipo={tipo}>{k.aggiungi}</button>
              </div>
            );
            return (
              <article key={m.id} className="shop-object">
                <ImmagineCarta id="dorso" alt="" mazzo={m.predefinito ? null : m.slug} />
                <div>
                  <h3>{m.nome}</h3>
                  {m.descrizione && <p>{m.descrizione}</p>}
                  {mio && <p className="available" style={{ marginBottom: ".6rem" }}>{m.predefinito ? k.incluso : k.posseduto}</p>}
                  {!mio && m.prezzo_digitale != null && riga("digitale", scontato ? m.prezzo_digitale_scontato! : m.prezzo_digitale, scontato ? m.prezzo_digitale : null)}
                  {scontato && m.offerta_valido_fino && <p className="small muted">{f(k.offerta_fino, { data: new Date(m.offerta_valido_fino).toLocaleDateString(locale) })}</p>}
                  {m.prezzo_stampa === 0 && (
                    <a className="button button-quiet button-small" href={urlPdfGratuito(m.slug)} download data-an="deck_pdf_viewed">{k.pdf_gratis}</a>
                  )}
                  {m.prezzo_stampa != null && m.prezzo_stampa > 0 && riga("pdf", m.prezzo_stampa)}
                  {m.prezzo_fisico != null && riga("fisico", m.prezzo_fisico)}
                  {nelCarrello > 0 && <p className="small">{f(k.nel_carrello, { n: nelCarrello })}</p>}
                </div>
              </article>
            );
          })}
        </div>
      </section>

      <section className="band band-tight" aria-labelledby="titolo-carrello">
        <div className="story-grid">
          <div className="panel">
            <h2 id="titolo-carrello">{k.carrello}</h2>
            {voci.length === 0 ? <p className="muted">{k.carrello_vuoto}</p> : (
              <>
                <ul className="list-plain">
                  {voci.map((v) => (
                    <li key={chiave(v.deckId, v.tipo)} className="button-row" style={{ justifyContent: "space-between", padding: ".4rem 0" }}>
                      <span>{v.nome} — {nomeTipo(v.tipo)}{v.quantita > 1 ? ` × ${v.quantita}` : ""}</span>
                      <b>{euro(v.prezzo * v.quantita, v.valuta, locale)}</b>
                      <button type="button" className="button button-quiet button-small"
                        onClick={() => setCarrello((p) => { const n = new Map(p); n.delete(chiave(v.deckId, v.tipo)); return n; })}>{k.rimuovi}</button>
                    </li>
                  ))}
                </ul>
                <p><b>{k.totale}: {euro(totale, valuta, locale)}</b></p>
                <p className="small muted">{k.nota_sconto}</p>
                {serveIndirizzo && sessione.autenticata && (
                  <div className="field">
                    <span>{k.indirizzo}</span>
                    {elencoIndirizzi.length === 0 ? (
                      <p className="small">{k.indirizzo_manca} <LinkV2 className="inline" href={`${R.profilo}#indirizzi`}>{k.indirizzo_profilo}</LinkV2></p>
                    ) : (
                      <select value={indirizzoAttivo ?? ""} onChange={(e) => setIndirizzoScelto(e.target.value)}>
                        {elencoIndirizzi.map((i) => <option key={i.id} value={i.id}>{i.nome} — {i.via}, {i.citta}</option>)}
                      </select>
                    )}
                  </div>
                )}
                <button type="button" className="button" disabled={inCorso || (serveIndirizzo && sessione.autenticata && !indirizzoAttivo)} onClick={completa}>
                  {inCorso ? k.in_corso : sessione.autenticata ? k.completa : k.entra_per}
                </button>
                {errore && <p className="error">{errore}</p>}
              </>
            )}
          </div>
          <div className="static-share">
            <p className="eyebrow">{k.ponte_titolo}</p>
            <q>{t.mazzi.slogan}</q>
            <p>{k.ponte_testo}</p>
            <LinkV2 className="button button-brass" href={`${R.fisica}?source=shop`}>{k.ponte_cta}</LinkV2>
          </div>
        </div>
      </section>
    </>
  );
}
