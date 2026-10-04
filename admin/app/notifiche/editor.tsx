"use client";

/* L'editor di una campagna: il messaggio in sei lingue (con «Traduci» dall'LLM, da rileggere), dove porta, a chi
 * arriva (filtri con il conteggio dei destinatari in anteprima), la prova su di sé e la programmazione.
 *
 * Il conteggio si aggiorna da solo poco dopo l'ultima modifica dei filtri: dice quanti corrispondono, quanti mancano
 * per il consenso (promozioni) o perché non hanno un dispositivo, e quanti la riceveranno davvero. */

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { quandoCompleto } from "@/lib/formato";
import {
  LINGUE, NOMI_CANALE, NOMI_LINGUA, NOMI_PIATTAFORMA, NOMI_STATO, NOMI_TIPO, annullaCampagna, conta, creaCampagna,
  duplicaCampagna, eliminaCampagna, filtroPulito, inviaAMe, leggiCampagna, modificaCampagna, programmaCampagna,
  statoNotifiche, traduci,
  type Campagna, type CampagnaIn, type Canale, type Conteggio, type EsitoInviaAMe, type Filtro, type Lingua,
  type Piattaforma, type TipoCampagna,
} from "@/lib/notifiche";
import { useAzione, useDati, useToken } from "@/lib/usa";
import comuni from "../comuni.module.css";
import { Anteprima, Casella, Scelte, TestiPerLingua } from "./comuni";
import stili from "./notifiche.module.css";

const VUOTA: CampagnaIn = {
  nome: "", tipo: "servizio", testi: {}, lingua_base: "it", deep_link: "/daily-card", immagine: null, filtro: {},
  canali: ["fcm", "webpush"], rispetta_silenzio: true,
};

const FASCE = ["<18", "18-24", "25-34", "35-44", "45-54", "55-64", "65+", "nd"];
const NOME_FASCIA = (f: string) => (f === "nd" ? "Non indicata" : f);

function daCampagna(c: Campagna): CampagnaIn {
  return {
    nome: c.nome, tipo: c.tipo, testi: c.testi, lingua_base: c.lingua_base, deep_link: c.deep_link, immagine: c.immagine,
    filtro: c.filtro, canali: c.canali, rispetta_silenzio: c.rispetta_silenzio,
  };
}

function numero(v: string): number | null {
  const n = Number.parseInt(v, 10);
  return Number.isFinite(n) && n >= 0 ? n : null;
}

/** Sì / no / qualsiasi, per un filtro facoltativo. */
function TreVie({ etichetta, valore, cambia }: { etichetta: string; valore: boolean | null | undefined; cambia: (v: boolean | null) => void }) {
  return (
    <label className={comuni.campo}>
      <span className={comuni.campoEtichetta}>{etichetta}</span>
      <select className={comuni.selezione} value={valore === true ? "si" : valore === false ? "no" : ""}
        onChange={(e) => cambia(e.target.value === "si" ? true : e.target.value === "no" ? false : null)}>
        <option value="">Qualsiasi</option>
        <option value="si">Sì</option>
        <option value="no">No</option>
      </select>
    </label>
  );
}

function Numero({ etichetta, valore, cambia, aiuto }: { etichetta: string; valore: number | null | undefined; cambia: (v: number | null) => void; aiuto?: string }) {
  return (
    <label className={comuni.campo}>
      <span className={comuni.campoEtichetta}>{etichetta}</span>
      <input className={comuni.ingresso} type="number" inputMode="numeric" min={0} value={valore ?? ""}
        onChange={(e) => cambia(numero(e.target.value))} />
      {aiuto && <span className={comuni.campoAiuto}>{aiuto}</span>}
    </label>
  );
}

function Elenco({ etichetta, valore, cambia, aiuto, maiuscolo }: { etichetta: string; valore: string[] | undefined; cambia: (v: string[]) => void; aiuto?: string; maiuscolo?: boolean }) {
  const [testo, setTesto] = useState((valore ?? []).join(", "));
  return (
    <label className={comuni.campo}>
      <span className={comuni.campoEtichetta}>{etichetta}</span>
      <input className={comuni.ingresso} value={testo} autoComplete="off" spellCheck={false}
        onChange={(e) => {
          const v = maiuscolo ? e.target.value.toUpperCase() : e.target.value;
          setTesto(v);
          cambia(v.split(/[,\s]+/).map((x) => x.trim()).filter(Boolean));
        }} />
      {aiuto && <span className={comuni.campoAiuto}>{aiuto}</span>}
    </label>
  );
}

export function EditorCampagna({ id }: { id: number | null }) {
  const router = useRouter();
  const token = useToken();
  const stato = useDati(statoNotifiche);
  const caricata = useDati((t) => (id ? leggiCampagna(t, id) : Promise.resolve(null)), [id]);
  const { esegui, inCorso, errore } = useAzione();
  const [campagna, setCampagna] = useState<Campagna | null>(null);
  const [bozza, setBozza] = useState<CampagnaIn | null>(null);
  const [lingua, setLingua] = useState<Lingua>("it");
  const [conteggio, setConteggio] = useState<Conteggio | null>(null);
  const [esito, setEsito] = useState<string | null>(null);
  const [prova, setProva] = useState<EsitoInviaAMe | null>(null);
  const [quando, setQuando] = useState("");

  const attuale = campagna ?? caricata.dati;
  const b: CampagnaIn = bozza ?? (attuale ? daCampagna(attuale) : VUOTA);
  const modificabile = !attuale || attuale.stato === "bozza" || attuale.stato === "programmata";
  const cambia = (parziale: Partial<CampagnaIn>) => setBozza({ ...b, ...parziale });
  const cambiaFiltro = (parziale: Partial<Filtro>) => cambia({ filtro: { ...b.filtro, ...parziale } });
  const f = b.filtro;

  /* Il conteggio dei destinatari, poco dopo l'ultima modifica (filtro, tipo, canali). */
  const chiaveConteggio = JSON.stringify([b.tipo, filtroPulito(b.filtro), b.canali]);
  useEffect(() => {
    if (token === null || b.canali.length === 0) return;
    let annullato = false;
    const t = window.setTimeout(() => {
      conta(token, b.tipo, filtroPulito(b.filtro), b.canali)
        .then((r) => { if (!annullato) setConteggio(r); })
        .catch(() => { if (!annullato) setConteggio(null); });
    }, 500);
    return () => { annullato = true; window.clearTimeout(t); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, chiaveConteggio]);

  useEffect(() => {
    if (!esito) return;
    const t = window.setTimeout(() => setEsito(null), 5000);
    return () => window.clearTimeout(t);
  }, [esito]);

  const segnaposto = useMemo(() => {
    const base = b.testi[b.lingua_base];
    return base ? Object.fromEntries(LINGUE.map((l) => [l, base])) : undefined;
  }, [b.testi, b.lingua_base]);

  if (caricata.errore || stato.errore) return <p className={comuni.errore} role="alert">{caricata.errore ?? stato.errore}</p>;
  if ((id && !attuale) || !stato.dati) return <p className={comuni.caricamento}>Caricamento…</p>;

  const s = stato.dati;
  const pronta = Boolean(b.nome.trim() && b.testi[b.lingua_base]?.titolo && b.testi[b.lingua_base]?.corpo && b.canali.length);
  const nessunCanale = !s.firebase.presente && !s.vapid.presente;

  const salva = async (): Promise<Campagna | null> => {
    const corpo = { ...b, filtro: filtroPulito(b.filtro) };
    const r = await esegui((t) => (attuale ? modificaCampagna(t, attuale.id, corpo) : creaCampagna(t, corpo)));
    if (r) {
      setCampagna(r);
      setBozza(null);
      if (!attuale) router.replace(`/notifiche/campagne/${r.id}`);
    }
    return r;
  };

  const traduciTutte = async (sovrascrivi: boolean) => {
    const base = b.testi[b.lingua_base];
    if (!base) return;
    const mancanti = LINGUE.filter((l) => l !== b.lingua_base && (sovrascrivi || !b.testi[l]?.titolo || !b.testi[l]?.corpo));
    if (mancanti.length === 0) {
      setEsito("Tutte le lingue hanno già un testo: usa «Ritraduci tutte» per sostituirli.");
      return;
    }
    const r = await esegui((t) => traduci(t, b.lingua_base, base, mancanti));
    if (r) {
      cambia({ testi: { ...b.testi, ...r.testi } });
      setEsito(`Tradotta in ${mancanti.length} lingue: rileggi prima di salvare.`);
    }
  };

  const provaSuDiMe = async () => {
    setProva(null);
    const c = bozza || !attuale ? await salva() : attuale;
    if (!c) return;
    const r = await esegui((t) => inviaAMe(t, c.id));
    if (r) setProva(r);
  };

  const programma = async (subito: boolean) => {
    const c = bozza || !attuale ? await salva() : attuale;
    if (!c) return;
    const iso = subito ? null : new Date(quando).toISOString();
    const r = await esegui((t) => programmaCampagna(t, c.id, iso));
    if (r) {
      setCampagna(r);
      setEsito(subito ? "Partirà al prossimo giro (entro 15 minuti)." : `Programmata: ${quandoCompleto(r.programmata_il)}.`);
    }
  };

  return (
    <>
      <p style={{ margin: "0 0 1rem" }}>
        <Link className={comuni.collegamento} href="/notifiche">← Tutte le campagne</Link>
      </p>
      {errore && <p className={comuni.errore} role="alert">{errore}</p>}
      <p className={comuni.esito} role="status" hidden={!esito}>{esito}</p>
      {nessunCanale && (
        <p className={comuni.avviso}>
          Nessun canale è pronto: carica il service account di Firebase in «Impostazioni» (app) o apri una volta la
          console per generare le chiavi del Web Push (sito).
        </p>
      )}
      {attuale && (
        <p className={comuni.riquadroNota}>
          <span className={comuni.etichetta}>{NOMI_STATO[attuale.stato]}</span>
          {attuale.programmata_il && attuale.stato === "programmata" && <>Parte {quandoCompleto(attuale.programmata_il)}. </>}
          {!modificabile && "Una campagna partita non si modifica: duplicala per riusarla."}
        </p>
      )}

      <div className={stili.griglia}>
        <div>
          <fieldset disabled={!modificabile || inCorso} style={{ border: 0, padding: 0, margin: 0, minWidth: 0 }}>
            <section className={comuni.riquadro} aria-labelledby="titolo-messaggio">
              <h2 id="titolo-messaggio" className={comuni.riquadroTitolo}>Il messaggio</h2>
              <div className={comuni.riga}>
                <label className={comuni.campo}>
                  <span className={comuni.campoEtichetta}>Nome interno</span>
                  <input className={comuni.ingresso} value={b.nome} maxLength={120} onChange={(e) => cambia({ nome: e.target.value })}
                    placeholder="Luna piena di ottobre" />
                  <span className={comuni.campoAiuto}>Solo per riconoscerla qui: non arriva a nessuno.</span>
                </label>
                <label className={comuni.campo}>
                  <span className={comuni.campoEtichetta}>Lingua di partenza</span>
                  <select className={comuni.selezione} value={b.lingua_base}
                    onChange={(e) => { cambia({ lingua_base: e.target.value as Lingua }); setLingua(e.target.value as Lingua); }}>
                    {LINGUE.map((l) => <option key={l} value={l}>{NOMI_LINGUA[l]}</option>)}
                  </select>
                </label>
              </div>
              <fieldset className={stili.chips}>
                <legend>Tipo</legend>
                {(["servizio", "promozione"] as TipoCampagna[]).map((t) => (
                  <label key={t} className={stili.chip}>
                    <input type="radio" name="tipo" checked={b.tipo === t} onChange={() => cambia({ tipo: t })} />
                    {NOMI_TIPO[t]}
                  </label>
                ))}
                <span className={comuni.campoAiuto} style={{ flexBasis: "100%" }}>
                  {b.tipo === "promozione"
                    ? "Offerte e sconti: solo a chi ha acceso «Promozioni» nei consensi, al massimo il tetto settimanale a testa, con il pulsante per non riceverne più."
                    : "Novità del servizio (una funzione nuova, un cambiamento): a tutti quelli del gruppo scelto. Non usarlo per vendere: per le offerte scegli «Promozione»."}
                </span>
              </fieldset>

              <TestiPerLingua testi={b.testi} lingua={lingua} scegli={setLingua} base={b.lingua_base} segnaposto={segnaposto}
                cambia={(l, t) => cambia({ testi: { ...b.testi, [l]: t } })} />
              <div className={stili.azioni}>
                <button type="button" className={comuni.secondaria} disabled={!b.testi[b.lingua_base]?.titolo || !b.testi[b.lingua_base]?.corpo}
                  onClick={() => traduciTutte(false)}>
                  Traduci nelle lingue vuote
                </button>
                <button type="button" className={comuni.secondaria} disabled={!b.testi[b.lingua_base]?.titolo || !b.testi[b.lingua_base]?.corpo}
                  onClick={() => traduciTutte(true)}>
                  Ritraduci tutte
                </button>
              </div>
              <p className={comuni.campoAiuto} style={{ marginTop: "-0.75rem" }}>
                La traduzione la fa il modello assegnato alla traduzione degli articoli: rileggila. Chi riceve legge la
                sua lingua, altrimenti l&apos;inglese, altrimenti la lingua di partenza.
              </p>
            </section>

            <section className={comuni.riquadro} aria-labelledby="titolo-arrivo">
              <h2 id="titolo-arrivo" className={comuni.riquadroTitolo}>Dove porta</h2>
              <div className={comuni.riga}>
                <label className={comuni.campo}>
                  <span className={comuni.campoEtichetta}>Pagina del sito</span>
                  <input className={comuni.ingresso} value={b.deep_link} maxLength={300} style={{ fontFamily: "var(--apparato)" }}
                    onChange={(e) => cambia({ deep_link: e.target.value })} placeholder="/pricing" spellCheck={false} />
                  <span className={comuni.campoAiuto}>Un percorso che inizia con «/» (per esempio /daily-card, /pricing, /blog/…): nell&apos;app apre la stessa schermata.</span>
                </label>
                <label className={comuni.campo}>
                  <span className={comuni.campoEtichetta}>Immagine grande (facoltativa)</span>
                  <input className={comuni.ingresso} type="url" inputMode="url" value={b.immagine ?? ""} spellCheck={false}
                    onChange={(e) => cambia({ immagine: e.target.value.trim() || null })} placeholder="https://…" />
                  <span className={comuni.campoAiuto}>Un indirizzo https, 2:1. La mostrano Android e Chrome; iPhone solo nell&apos;app.</span>
                </label>
              </div>
            </section>

            <section className={comuni.riquadro} aria-labelledby="titolo-destinatari">
              <h2 id="titolo-destinatari" className={comuni.riquadroTitolo}>Chi la riceve</h2>
              <p className={comuni.riquadroNota}>
                Tutte le condizioni insieme; dentro una riga, una qualsiasi. Vuoto: nessun filtro. Il genere e i dati
                sensibili (salute, «persona trans») non sono filtri, per scelta.
              </p>
              <Scelte titolo="Canali" voci={(["fcm", "webpush"] as Canale[]).map((c) => ({ valore: c, nome: NOMI_CANALE[c] }))}
                scelte={b.canali} cambia={(v) => cambia({ canali: v })} />
              <Scelte titolo="Lingua dell'account" voci={LINGUE.map((l) => ({ valore: l, nome: NOMI_LINGUA[l] }))}
                scelte={(f.lingue ?? []) as Lingua[]} cambia={(v) => cambiaFiltro({ lingue: v })} />
              <Scelte titolo="Fascia d'età" voci={FASCE.map((x) => ({ valore: x, nome: NOME_FASCIA(x) }))}
                scelte={f.fasce_eta ?? []} cambia={(v) => cambiaFiltro({ fasce_eta: v })} />
              <Scelte titolo="Dispositivo" voci={(["android", "ios", "web"] as Piattaforma[]).map((p) => ({ valore: p, nome: NOMI_PIATTAFORMA[p] }))}
                scelte={f.piattaforme ?? []} cambia={(v) => cambiaFiltro({ piattaforme: v })} />
              {s.catalogo.piani.length > 0 && (
                <Scelte titolo="Piano attivo" voci={s.catalogo.piani.map((p) => ({ valore: p.slug, nome: p.nome }))}
                  scelte={f.piani ?? []} cambia={(v) => cambiaFiltro({ piani: v })} />
              )}
              <div className={comuni.riga}>
                <Elenco etichetta="Paesi (codici ISO)" valore={f.paesi} maiuscolo cambia={(v) => cambiaFiltro({ paesi: v })}
                  aiuto="Separati da virgola: IT, ES, HU. È la posizione attuale del profilo." />
                <Elenco etichetta="Primo canale di arrivo" valore={f.primi_canali} cambia={(v) => cambiaFiltro({ primi_canali: v })}
                  aiuto="Come in Analytics: organico, social, diretto, referral, email… «nd» per chi non ne ha uno." />
              </div>
              <div className={comuni.riga}>
                <Numero etichetta="Attivi negli ultimi … giorni" valore={f.attivi_negli_ultimi_giorni} cambia={(v) => cambiaFiltro({ attivi_negli_ultimi_giorni: v })} />
                <Numero etichetta="Inattivi da almeno … giorni" valore={f.inattivi_da_giorni} cambia={(v) => cambiaFiltro({ inattivi_da_giorni: v })} />
              </div>
              <div className={comuni.riga}>
                <Numero etichetta="Ultima lettura: almeno … giorni fa" valore={f.ultima_lettura_almeno_giorni}
                  cambia={(v) => cambiaFiltro({ ultima_lettura_almeno_giorni: v })} aiuto="Comprende chi non ha mai letto." />
                <Numero etichetta="Ultima lettura: al massimo … giorni fa" valore={f.ultima_lettura_al_massimo_giorni}
                  cambia={(v) => cambiaFiltro({ ultima_lettura_al_massimo_giorni: v })} />
              </div>
              <div className={comuni.riga}>
                <TreVie etichetta="Ha mai acquistato" valore={f.ha_acquistato} cambia={(v) => cambiaFiltro({ ha_acquistato: v })} />
                <TreVie etichetta="Abbonamento a pagamento" valore={f.abbonamento_attivo} cambia={(v) => cambiaFiltro({ abbonamento_attivo: v })} />
                <TreVie etichetta="In prova" valore={f.in_prova} cambia={(v) => cambiaFiltro({ in_prova: v })} />
              </div>
              <div className={comuni.riga}>
                <Numero etichetta="Crediti: almeno" valore={f.crediti_min} cambia={(v) => cambiaFiltro({ crediti_min: v })} />
                <Numero etichetta="Crediti: al massimo" valore={f.crediti_max} cambia={(v) => cambiaFiltro({ crediti_max: v })} />
              </div>
              <Casella etichetta="Rispetta le ore di silenzio" valore={b.rispetta_silenzio} cambia={(v) => cambia({ rispetta_silenzio: v })}
                aiuto="Chi è nelle sue ore di silenzio (di notte, all'ora del suo paese) la riceve al primo giro dopo." />
            </section>
          </fieldset>
        </div>

        <aside className={stili.colonnaLaterale} aria-label="Anteprima e invio">
          <section className={comuni.riquadro} aria-labelledby="titolo-conteggio">
            <h2 id="titolo-conteggio" className={comuni.riquadroTitolo}>Destinatari</h2>
            <div className={stili.conteggio} aria-live="polite">
              {conteggio ? (
                <>
                  <span className={stili.conteggioGrande}>{conteggio.destinatari}</span>
                  <span>la riceveranno ({conteggio.per_piattaforma.android} Android, {conteggio.per_piattaforma.ios} iPhone/iPad, {conteggio.per_piattaforma.web} browser)</span>
                  <span className={comuni.campoAiuto}>
                    {conteggio.corrispondono} corrispondono ai filtri
                    {b.tipo === "promozione" && <>; {conteggio.senza_consenso} senza consenso alle promozioni</>}
                    ; {conteggio.senza_dispositivo} senza notifiche attive.
                  </span>
                </>
              ) : <span className={comuni.campoAiuto}>Conteggio…</span>}
            </div>
          </section>

          <section className={comuni.riquadro} aria-labelledby="titolo-anteprima">
            <h2 id="titolo-anteprima" className={comuni.riquadroTitolo}>Anteprima ({NOMI_LINGUA[lingua].toLowerCase()})</h2>
            <Anteprima testo={b.testi[lingua] ?? b.testi[b.lingua_base]} immagine={b.immagine} promozione={b.tipo === "promozione"} lingua={lingua} />
          </section>

          <section className={comuni.riquadro} aria-labelledby="titolo-invio">
            <h2 id="titolo-invio" className={comuni.riquadroTitolo}>Prova e invio</h2>
            {modificabile && (
              <div className={stili.azioni}>
                <button type="button" className={comuni.primaria} disabled={inCorso || !bozza || !b.nome.trim()} onClick={() => void salva().then((r) => r && setEsito("Bozza salvata."))}>
                  {inCorso ? "Attendi…" : attuale ? "Salva" : "Salva la bozza"}
                </button>
                <button type="button" className={comuni.secondaria} disabled={inCorso || !pronta} onClick={provaSuDiMe}>Invia a me</button>
              </div>
            )}
            {prova && (
              <div role="status" className={comuni.riquadroNota}>
                <strong>{prova.messaggio}</strong>
                {prova.dettagli.length > 0 && (
                  <ul style={{ margin: "0.3rem 0 0", paddingLeft: "1.1rem" }}>
                    {prova.dettagli.map((d) => (
                      <li key={d.dispositivo}>{NOMI_PIATTAFORMA[d.piattaforma]}: {d.esito === "ok" ? "consegnata" : `${d.esito} ${d.messaggio}`}</li>
                    ))}
                  </ul>
                )}
              </div>
            )}
            {modificabile && (
              <>
                <label className={comuni.campo}>
                  <span className={comuni.campoEtichetta}>Programma per (ora di questo computer)</span>
                  <input className={comuni.ingresso} type="datetime-local" value={quando} onChange={(e) => setQuando(e.target.value)} />
                </label>
                <div className={stili.azioni}>
                  <button type="button" className={comuni.secondaria} disabled={inCorso || !pronta || !quando} onClick={() => programma(false)}>Programma</button>
                  <button type="button" className={comuni.primaria} disabled={inCorso || !pronta} onClick={() => programma(true)}>Invia adesso</button>
                </div>
                <p className={comuni.campoAiuto}>«Invia adesso» parte al prossimo giro, entro 15 minuti. Prima prova su di te.</p>
              </>
            )}
            {attuale && (
              <div className={stili.azioni}>
                {(attuale.stato === "programmata" || attuale.stato === "in_invio") && (
                  <button type="button" className={comuni.distruttiva} disabled={inCorso}
                    onClick={async () => { const r = await esegui((t) => annullaCampagna(t, attuale.id)); if (r) { setCampagna(r); setEsito("Campagna annullata."); } }}>
                    Annulla la campagna
                  </button>
                )}
                <button type="button" className={comuni.secondaria} disabled={inCorso}
                  onClick={async () => { const r = await esegui((t) => duplicaCampagna(t, attuale.id)); if (r) router.push(`/notifiche/campagne/${r.id}`); }}>
                  Duplica
                </button>
                {attuale.stato === "bozza" && (
                  <button type="button" className={comuni.distruttiva} disabled={inCorso}
                    onClick={async () => {
                      if (!window.confirm("Eliminare questa bozza?")) return;
                      const r = await esegui((t) => eliminaCampagna(t, attuale.id));
                      if (r) router.push("/notifiche");
                    }}>
                    Elimina la bozza
                  </button>
                )}
              </div>
            )}
            {attuale && (attuale.stato === "inviata" || attuale.stato === "in_invio") && (
              <dl className={stili.numeri}>
                <div><dt>Raggiunti</dt><dd>{attuale.contatori.destinatari}</dd></div>
                <div><dt>Consegnati</dt><dd>{attuale.contatori.inviati}</dd></div>
                <div><dt>Aperti</dt><dd>{attuale.contatori.aperti}</dd></div>
                <div><dt>Errori</dt><dd>{attuale.contatori.errori}</dd></div>
                <div><dt>Saltati</dt><dd>{attuale.contatori.saltati}</dd></div>
              </dl>
            )}
          </section>
        </aside>
      </div>
    </>
  );
}
