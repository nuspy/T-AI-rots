"use client";

/* Il negozio della v2 (specifica v2, §4 e §11): un'estensione fisica, non il motivo per cui si viene. Ogni mazzo
 * si compra in tre forme separate — la scatola fisica, il PDF da stampare, il mazzo digitale per le letture (il
 * Thoth, digitale, è già di tutti) — e si guarda carta per carta prima di comprarlo. Il carrello ha la sua pagina
 * (`/v2/cart`) e resta nel browser; prezzi, sconti e totale li calcola il server. Con i pagamenti non ancora attivi
 * l'ordine si registra lo stesso, in attesa: il negozio funziona fino in fondo, tranne l'incasso. */

import { Suspense, useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { useTraccia } from "lanterna-osservatore/react";
import {
  apriOrdine, elencaIndirizzi, elencaMazzi, euro, leggiOrdine, mieiMazzi, preventivoCarrello, scaricaPdfOrdine,
  urlPdfGratuito, ErroreApi, type Mazzo, type Preventivo, type RigaOrdine, type TipoVoceOrdine,
} from "@/lib/api";
import { useSessione } from "@/lib/sessione";
import { f, plurale } from "@/v2/i18n";
import { ImmagineCarta } from "@/v2/componenti/carta";
import { GalleriaMazzo } from "@/v2/componenti/galleria-mazzo";
import LinkV2 from "@/v2/componenti/link";
import { useCarrello } from "@/v2/lib/carrello";
import { useLingua } from "@/v2/lib/lingua";
import { R, indirizzoV2 } from "@/v2/lib/percorsi";
import { useAzione, useCarica } from "@/v2/lib/usa";

const TIPI: TipoVoceOrdine[] = ["fisico", "pdf", "digitale"];

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

/** Il listino di un formato. `null`: non in vendita. */
function listinoDi(m: Mazzo, tipo: TipoVoceOrdine): number | null {
  return tipo === "digitale" ? m.prezzo_digitale : tipo === "pdf" ? m.prezzo_stampa : m.prezzo_fisico;
}

/** Il prezzo da pagare adesso: lo scontato se l'offerta vale per quel formato, altrimenti il listino. */
function prezzoDi(m: Mazzo, tipo: TipoVoceOrdine): number | null {
  const scontato = tipo === "digitale" ? m.prezzo_digitale_scontato : tipo === "pdf" ? m.prezzo_stampa_scontato : m.prezzo_fisico_scontato;
  return scontato ?? listinoDi(m, tipo);
}

export function Negozio() {
  const { t, locale } = useLingua();
  const k = t.negozio;
  const sessione = useSessione();
  const carrello = useCarrello();
  const mazzi = useCarica(elencaMazzi, [], { pubblico: true });
  const posseduti = useCarica(mieiMazzi);
  const [galleria, setGalleria] = useState<Mazzo | null>(null);
  const [aggiunto, setAggiunto] = useState<string | null>(null);
  const annuncio = useRef<ReturnType<typeof setTimeout> | null>(null);
  useEffect(() => () => { if (annuncio.current) clearTimeout(annuncio.current); }, []);

  const elenco = mazzi.dati ?? [];
  const idPosseduti = new Set(posseduti.dati?.deck_ids ?? []);
  const nomeTipo = (tipo: TipoVoceOrdine) => (tipo === "digitale" ? k.digitale : tipo === "pdf" ? k.pdf : k.fisico);
  const etichettaAggiungi = (tipo: TipoVoceOrdine) =>
    (tipo === "digitale" ? k.aggiungi_digitale : tipo === "pdf" ? k.aggiungi_pdf : k.aggiungi_fisico);

  const aggiungi = (m: Mazzo, tipo: TipoVoceOrdine) => {
    carrello.aggiungi(m.id, tipo);
    setAggiunto(f(k.aggiunto, { cosa: `${m.nome} — ${nomeTipo(tipo)}` }));
    if (annuncio.current) clearTimeout(annuncio.current);
    annuncio.current = setTimeout(() => setAggiunto(null), 4000);
  };

  return (
    <section className="band band-tight">
      {mazzi.errore && <p className="error">{mazzi.errore}</p>}
      {mazzi.dati && elenco.length === 0 && <p className="notice">{k.vuoto}</p>}
      <p className="sr-only" role="status" aria-live="polite">{aggiunto ?? ""}</p>
      <div className="shop-grid">
        {elenco.map((m) => {
          /* Il digitale gratuito è di tutti, come il predefinito: nessun acquisto. */
          const mioDigitale = m.predefinito || m.prezzo_digitale === 0 || idPosseduti.has(m.id);
          const scontato = m.offerta_attiva;
          const nelCarrello = carrello.voci.filter((v) => v.deckId === m.id).reduce((s, v) => s + v.quantita, 0);
          return (
            <article key={m.id} className="shop-object">
              <button type="button" className="shop-cover" onClick={() => setGalleria(m)} aria-label={f(k.vedi_carte_di, { mazzo: m.nome })}>
                <ImmagineCarta id="dorso" alt="" mazzo={m.predefinito ? null : m.slug} />
                <span className="shop-cover-label">{k.vedi_carte}</span>
              </button>
              <div>
                <h3>{m.nome}</h3>
                {m.descrizione && <p>{m.descrizione}</p>}
                {m.offerta_attiva && <p className="badge-offer">{k.offerta}</p>}
                <ul className="list-plain shop-formats">
                  {TIPI.map((tipo) => {
                    if (tipo === "digitale" && mioDigitale) {
                      return (
                        <li key={tipo} className="shop-format">
                          <span>{nomeTipo(tipo)}</span>
                          <span className="available">{m.predefinito || m.prezzo_digitale === 0 ? k.incluso : k.posseduto}</span>
                        </li>
                      );
                    }
                    const prezzo = prezzoDi(m, tipo);
                    if (tipo === "digitale" && prezzo == null) return null;
                    if (tipo === "pdf" && prezzo === 0) {
                      return (
                        <li key={tipo} className="shop-format">
                          <span>{nomeTipo(tipo)}</span>
                          <a className="button button-quiet button-small" href={urlPdfGratuito(m.slug)} download data-an="deck_pdf_viewed">{k.pdf_gratis}</a>
                        </li>
                      );
                    }
                    return (
                      <li key={tipo} className="shop-format">
                        <span>
                          {nomeTipo(tipo)}
                          {prezzo != null ? (
                            <b className="shop-price">
                              {listinoDi(m, tipo) !== prezzo && <s className="small muted">{euro(listinoDi(m, tipo)!, m.valuta, locale)}</s>}{" "}
                              {euro(prezzo, m.valuta, locale)}
                            </b>
                          ) : <small className="muted shop-price">{k.prezzo_in_arrivo}</small>}
                        </span>
                        <button type="button" className="button button-small" disabled={prezzo == null}
                          onClick={() => aggiungi(m, tipo)} data-an="carrello_aggiunto" data-an-mazzo={m.slug} data-an-tipo={tipo}>
                          {etichettaAggiungi(tipo)}
                        </button>
                      </li>
                    );
                  })}
                </ul>
                {scontato && m.offerta_valido_fino && <p className="small muted">{f(k.offerta_fino, { data: new Date(m.offerta_valido_fino).toLocaleDateString(locale) })}</p>}
                <div className="button-row">
                  <button type="button" className="button button-quiet button-small" onClick={() => setGalleria(m)}>{k.vedi_carte}</button>
                  {nelCarrello > 0 && (
                    <LinkV2 className="button button-quiet button-small" href={R.carrello}>
                      {f(k.nel_carrello, { n: nelCarrello })} · {k.vai_carrello}
                    </LinkV2>
                  )}
                </div>
              </div>
            </article>
          );
        })}
      </div>
      {carrello.pezzi > 0 && (
        <div className="shop-bar">
          <span>{plurale(carrello.pezzi, k.pezzi)}</span>
          <LinkV2 className="button button-brass" href={R.carrello}>{k.vai_carrello}</LinkV2>
        </div>
      )}
      <div className="static-share" style={{ marginTop: "2.5rem" }}>
        <p className="eyebrow">{k.ponte_titolo}</p>
        <q>{t.mazzi.slogan}</q>
        <p>{k.ponte_testo}</p>
        <LinkV2 className="button button-brass" href={`${R.fisica}?source=shop`}>{k.ponte_cta}</LinkV2>
      </div>
      {galleria && <GalleriaMazzo mazzo={galleria} onChiudi={() => setGalleria(null)} />}
      {!sessione.autenticata && sessione.pronta && <p className="small muted" style={{ marginTop: "1rem" }}>{k.nota_account}</p>}
    </section>
  );
}

export function PaginaCarrello() {
  return <Suspense fallback={null}><CarrelloContenuto /></Suspense>;
}

function CarrelloContenuto() {
  const { t, locale, prefissoIt } = useLingua();
  const k = t.negozio;
  const sessione = useSessione();
  const carrello = useCarrello();
  const parametri = useSearchParams();
  const traccia = useTraccia();
  const mazzi = useCarica(elencaMazzi, [], { pubblico: true });
  const indirizzi = useCarica(elencaIndirizzi);
  const { esegui, inCorso, errore } = useAzione();
  const [indirizzoScelto, setIndirizzoScelto] = useState<string | null>(null);
  const [preventivo, setPreventivo] = useState<{ chiave: string; dati: Preventivo | null; errore: string | null } | null>(null);
  const [esito, setEsito] = useState<{ buono: boolean; testo: string; ordine?: string; pdf?: RigaOrdine[] } | null>(null);

  const perId = new Map((mazzi.dati ?? []).map((m) => [m.id, m]));
  /* Solo ciò che il catalogo vende ancora: una voce di un mazzo sparito non entra nel preventivo. */
  const voci = mazzi.dati ? carrello.voci.filter((v) => perId.has(v.deckId)) : carrello.voci;
  const chiave = JSON.stringify(voci);
  const nomeTipo = (tipo: TipoVoceOrdine) => (tipo === "digitale" ? k.digitale : tipo === "pdf" ? k.pdf : k.fisico);

  /* Il preventivo dal server a ogni cambiamento del carrello (con un attimo di pausa mentre si premono i +/−). */
  useEffect(() => {
    if (!carrello.pronto || !mazzi.dati || voci.length === 0) return;
    let annullato = false;
    const attesa = setTimeout(() => {
      preventivoCarrello(voci.map((v) => ({ deck_id: v.deckId, tipo: v.tipo, quantita: v.quantita })))
        .then((d) => { if (!annullato) setPreventivo({ chiave, dati: d, errore: null }); })
        .catch((e: unknown) => {
          if (!annullato) setPreventivo({ chiave, dati: null, errore: e instanceof ErroreApi && e.stato === 422 ? k.non_disponibile : t.comune.err_generico });
        });
    }, 250);
    return () => { annullato = true; clearTimeout(attesa); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chiave, carrello.pronto, mazzi.dati]);

  /* Il ritorno dal pagamento (`?ordine=…`), quando i pagamenti saranno attivi: lo stato vero lo dice il server. */
  useEffect(() => {
    const ordineId = parametri.get("ordine");
    if (!ordineId || !sessione.autenticata) return;
    let annullato = false;
    leggiOrdine(sessione.token, ordineId)
      .then((o) => {
        if (annullato) return;
        if (o.status === "pagato") {
          setEsito({ buono: true, testo: k.pagato, ordine: ordineId, pdf: o.righe.filter((r) => r.tipo === "pdf") });
          carrello.svuota();
          traccia("purchase_completed", { tipo: "ordine" });
        } else if (o.status !== "aperto") setEsito({ buono: false, testo: k.annullato });
      })
      .catch(() => { if (!annullato) setEsito({ buono: false, testo: k.non_verificato }); });
    return () => { annullato = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [parametri, sessione.autenticata, sessione.token]);

  const attuale = preventivo?.chiave === chiave ? preventivo : null;
  const q = attuale?.dati ?? null;
  const serveIndirizzo = voci.some((v) => v.tipo === "fisico");
  const elencoIndirizzi = indirizzi.dati?.indirizzi ?? [];
  const indirizzoAttivo = indirizzoScelto ?? elencoIndirizzi.find((i) => i.predefinito)?.id ?? elencoIndirizzi[0]?.id ?? null;
  const valuta = voci.length ? perId.get(voci[0].deckId)?.valuta ?? "EUR" : "EUR";
  const riga = (deckId: number, tipo: TipoVoceOrdine) => q?.righe.find((r) => r.deck_id === deckId && r.tipo === tipo);

  const completa = async () => {
    if (!sessione.autenticata) { sessione.entra(indirizzoV2(R.carrello, prefissoIt)); return; }
    if (serveIndirizzo && !indirizzoAttivo) return;
    const corpo = voci.map((v) => ({ deck_id: v.deckId, tipo: v.tipo, quantita: v.quantita }));
    const r = await esegui((tok) => apriOrdine(tok, corpo, indirizzoV2(R.carrello, prefissoIt), serveIndirizzo ? indirizzoAttivo ?? undefined : undefined));
    if (!r) return;
    if (r.url) { window.location.assign(r.url); return; }
    /* Pagamenti non ancora attivi: l'ordine è registrato, in attesa. Il carrello si svuota: l'ordine lo contiene. */
    setEsito({ buono: true, testo: f(k.ordine_registrato, { numero: r.id.slice(0, 8).toUpperCase(), totale: euro(r.importo_totale, r.valuta, locale) }), ordine: r.id });
    carrello.svuota();
    traccia("order_registered", { tipo: "ordine", pagamento: "non_attivo" });
  };

  return (
    <>
    <section className="subhero subhero-compact">
      <p className="eyebrow">{k.eyebrow}</p>
      <h1 className="display">{k.carrello}</h1>
    </section>
    <section className="band band-tight">
      {esito && (
        <div className={esito.buono ? "success" : "error"} role="status" style={{ marginBottom: "1.5rem" }}>
          <p style={{ margin: 0 }}>{esito.testo}</p>
          {esito.pdf?.map((r) => (
            <BottonePdfV2 key={r.deck_id} ordineId={esito.ordine!} deckId={r.deck_id} nome={perId.get(r.deck_id)?.nome ?? ""} />
          ))}
          {esito.ordine && (
            <p style={{ margin: ".75rem 0 0" }}>
              <LinkV2 className="inline" href={`${R.profilo}#ordini`}>{k.vedi_ordini}</LinkV2>
            </p>
          )}
        </div>
      )}
      <div className="story-grid">
        <div className="panel">
          {!carrello.pronto || (!mazzi.dati && !mazzi.errore) ? <p className="muted">{t.comune.carica}</p> : voci.length === 0 ? (
            <>
              <p className="muted">{k.carrello_vuoto}</p>
              <LinkV2 className="button" href={R.negozio}>{k.vai_negozio}</LinkV2>
            </>
          ) : (
            <>
              <ul className="list-plain cart-lines">
                {voci.map((v) => {
                  const m = perId.get(v.deckId)!;
                  const r = riga(v.deckId, v.tipo);
                  return (
                    <li key={`${v.deckId}:${v.tipo}`} className="cart-line">
                      <ImmagineCarta id="dorso" alt="" mazzo={m.predefinito ? null : m.slug} classe="cart-thumb" />
                      <div className="cart-line-text">
                        <b>{m.nome}</b>
                        <span className="small">{nomeTipo(v.tipo)}</span>
                        {r && r.prezzo_finale_unitario !== r.prezzo_pieno_unitario && (
                          <s className="small muted">{euro(r.prezzo_pieno_unitario, valuta, locale)}</s>
                        )}
                      </div>
                      <div className="stepper" role="group" aria-label={f(k.quantita_di, { cosa: m.nome })}>
                        <button type="button" onClick={() => carrello.quantita(v.deckId, v.tipo, v.quantita - 1)} aria-label={k.meno}>−</button>
                        <output aria-live="polite">{v.quantita}</output>
                        <button type="button" disabled={v.tipo === "digitale" || v.quantita >= 20}
                          onClick={() => carrello.quantita(v.deckId, v.tipo, v.quantita + 1)} aria-label={k.piu}>+</button>
                      </div>
                      <b className="cart-line-price">{r ? euro(r.prezzo_finale_unitario * r.quantita, valuta, locale) : "…"}</b>
                      <button type="button" className="text-button" onClick={() => carrello.togli(v.deckId, v.tipo)}>{k.rimuovi}</button>
                    </li>
                  );
                })}
              </ul>
              {attuale?.errore && <p className="error">{attuale.errore}</p>}
              <dl className="cart-totals">
                <dt>{k.subtotale}</dt><dd>{q ? euro(q.subtotale, valuta, locale) : "…"}</dd>
                {q && q.sconto_scaglioni > 0 && (
                  <><dt>{f(k.sconto_scaglioni, { p: q.scaglione_percentuale })}</dt><dd>−{euro(q.sconto_scaglioni, valuta, locale)}</dd></>
                )}
                <dt><b>{k.totale}</b></dt><dd><b>{q ? euro(q.totale, valuta, locale) : "…"}</b></dd>
              </dl>
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
              {q && !q.pagamento_attivo && <p className="notice small">{k.pagamento_non_attivo}</p>}
              <div className="button-row">
                <button type="button" className="button button-brass" disabled={inCorso || !q || (serveIndirizzo && sessione.autenticata && !indirizzoAttivo)} onClick={completa}>
                  {inCorso ? k.in_corso : sessione.autenticata ? k.completa : k.entra_per}
                </button>
                <LinkV2 className="button button-quiet" href={R.negozio}>{k.continua}</LinkV2>
              </div>
              {errore && <p className="error">{errore}</p>}
            </>
          )}
        </div>
        <div className="static-share">
          <p className="eyebrow">{k.ponte_titolo}</p>
          <q>{t.mazzi.slogan}</q>
          <p>{k.ponte_testo}</p>
          <LinkV2 className="button button-brass" href={`${R.fisica}?source=cart`}>{k.ponte_cta}</LinkV2>
        </div>
      </div>
    </section>
    </>
  );
}
