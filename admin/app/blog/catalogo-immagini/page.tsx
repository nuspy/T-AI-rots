"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { Suspense, useCallback, useMemo, useState } from "react";
import {
  catalogoImmagini,
  impostaImmagineCatalogo,
  togliImmagineCatalogo,
  urlMedia,
  type Immagine,
  type TipoCatalogo,
  type VoceCatalogo,
} from "@/lib/blog";
import { quandoCompleto } from "@/lib/formato";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../../comuni.module.css";
import stili from "../blog.module.css";
import { Schede } from "../schede";
import { SelettoreImmagine } from "../selettore-immagine";

/* Le immagini del catalogo (v9.4): l'illustrazione di ogni stesa e l'immagine di ogni sezione del Journal, in una
 * pagina sola, per vedere a colpo d'occhio che cosa manca.
 *
 * Le stese non sono articoli: la loro immagine sta in una tabella a parte (`catalogo_immagini`); quella di una
 * sezione sta nella sezione stessa, la stessa che si cambia da «Sezioni». L'immagine si sceglie dalla libreria del
 * blog o si carica sul posto, con lo stesso selettore degli articoli; togliere un'immagine non la cancella dalla
 * libreria.
 *
 * Il tipo mostrato sta nell'indirizzo (`?tipo=stesa` o `?tipo=sezione`): si può tornare qui o mandare il link. */

const TIPI: { valore: TipoCatalogo; etichetta: string; spiegazione: string }[] = [
  {
    valore: "stesa",
    etichetta: "Stese",
    spiegazione:
      "L'illustrazione di ogni stesa: compare sulla pagina della stesa e nelle sezioni del Journal che elencano le stese.",
  },
  {
    valore: "sezione",
    etichetta: "Sezioni",
    spiegazione:
      "L'immagine di ogni sezione del Journal: compare in testa alla sezione e nel riquadro che la presenta. È la stessa che si cambia da «Sezioni».",
  },
];

export default function CatalogoImmagini() {
  /* `useSearchParams` nella build statica va dentro un confine di attesa. */
  return (
    <Suspense fallback={<p className={comuni.caricamento}>Caricamento…</p>}>
      <Contenuto />
    </Suspense>
  );
}

function Contenuto() {
  const parametri = useSearchParams();
  const router = useRouter();
  const percorso = usePathname();
  const tipo: TipoCatalogo = parametri.get("tipo") === "sezione" ? "sezione" : "stesa";

  const elenco = useDati(useCallback((t: string) => catalogoImmagini(t, tipo), [tipo]));
  const [cerca, setCerca] = useState("");
  const [soloMancanti, setSoloMancanti] = useState(false);
  const [aperta, setAperta] = useState<string | null>(null);
  const [esito, setEsito] = useState<string | null>(null);

  const cambiaTipo = (nuovo: TipoCatalogo) => {
    setAperta(null);
    setEsito(null);
    router.replace(`${percorso}?tipo=${nuovo}`, { scroll: false });
  };

  const voci = elenco.dati ?? [];
  const mancanti = voci.filter((v) => !v.immagine).length;
  const visibili = useMemo(() => {
    const testo = cerca.trim().toLowerCase();
    return (elenco.dati ?? []).filter(
      (v) =>
        (!soloMancanti || !v.immagine) &&
        (!testo || v.nome.toLowerCase().includes(testo) || v.riferimento.toLowerCase().includes(testo)),
    );
  }, [elenco.dati, cerca, soloMancanti]);

  const spiegazione = TIPI.find((t) => t.valore === tipo)?.spiegazione;

  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Blog · Immagini del catalogo</h1>
          <p className={comuni.sottotitolo}>
            Le illustrazioni delle stese e le immagini delle sezioni. Qui le assegni, le cambi o le togli: togliere
            un&apos;immagine non la cancella dalla libreria.
          </p>
        </div>
      </div>

      <Schede />

      <div className={stili.commutatore} role="group" aria-label="Che cosa mostrare">
        {TIPI.map((t) => (
          <button key={t.valore} type="button" aria-pressed={tipo === t.valore} onClick={() => cambiaTipo(t.valore)}>
            {t.etichetta}
          </button>
        ))}
      </div>
      <p className={comuni.riquadroNota} style={{ marginTop: "0.75rem" }}>
        {spiegazione}
      </p>

      <div className={comuni.riga} style={{ alignItems: "center", marginBottom: "0.75rem" }}>
        <label className={comuni.campo} style={{ marginBottom: 0 }}>
          <span className={comuni.campoEtichetta}>Cerca per nome</span>
          <input
            className={comuni.ingresso}
            type="search"
            value={cerca}
            onChange={(e) => setCerca(e.target.value)}
            placeholder={tipo === "stesa" ? "Per esempio «celtic»" : "Per esempio «arcana»"}
          />
        </label>
        <label className={stili.interruttore} style={{ flex: "0 1 auto" }}>
          <input type="checkbox" checked={soloMancanti} onChange={(e) => setSoloMancanti(e.target.checked)} />
          Solo quelle senza immagine
        </label>
      </div>

      {elenco.dati && (
        <p className={comuni.riquadroNota} role="status">
          {voci.length === 0
            ? null
            : mancanti === 0
              ? `Tutte le ${voci.length} hanno un'immagine.`
              : `${mancanti} su ${voci.length} senza immagine.`}
        </p>
      )}

      {esito && (
        <p className={comuni.esito} role="status">
          {esito}
        </p>
      )}
      {elenco.errore && (
        <p className={comuni.errore} role="alert">
          {elenco.errore}
        </p>
      )}
      {!elenco.dati && elenco.inCorso && <p className={comuni.caricamento}>Caricamento…</p>}
      {elenco.dati && voci.length === 0 && (
        <div className={comuni.vuoto}>{tipo === "stesa" ? "Nessuna stesa nel catalogo." : "Nessuna sezione. Creane una da «Sezioni»."}</div>
      )}
      {elenco.dati && voci.length > 0 && visibili.length === 0 && (
        <div className={comuni.vuoto}>Nessuna voce corrisponde alla ricerca.</div>
      )}

      {visibili.length > 0 && (
        <ul className={`${stili.elenco} ${elenco.inCorso ? comuni.inRicarica : ""}`} aria-label={tipo === "stesa" ? "Stese" : "Sezioni"}>
          {visibili.map((v) => (
            <Riga
              key={`${v.tipo}/${v.riferimento}`}
              voce={v}
              aperta={aperta === v.riferimento}
              apri={() => {
                setEsito(null);
                setAperta(aperta === v.riferimento ? null : v.riferimento);
              }}
              fatto={(messaggio) => {
                setAperta(null);
                setEsito(messaggio);
                elenco.ricarica();
              }}
            />
          ))}
        </ul>
      )}
    </>
  );
}

function Riga({
  voce,
  aperta,
  apri,
  fatto,
}: {
  voce: VoceCatalogo;
  aperta: boolean;
  apri: () => void;
  fatto: (messaggio: string) => void;
}) {
  const { esegui, inCorso, errore } = useAzione();
  const [togliendo, setTogliendo] = useState(false);

  const togli = async () => {
    if ((await esegui((t) => togliImmagineCatalogo(t, voce.tipo, voce.riferimento))) !== null) {
      setTogliendo(false);
      fatto(`Immagine tolta da «${voce.nome}». Resta nella libreria delle immagini.`);
    }
  };

  const miniatura = voce.immagine ? urlMedia(voce.immagine.mini || voce.immagine.url) : null;

  return (
    <li className={stili.voce}>
      {miniatura ? (
        // eslint-disable-next-line @next/next/no-img-element -- miniatura dall'API
        <img className={stili.copertina} src={miniatura} alt="" width={72} height={54} loading="lazy" />
      ) : (
        <span className={stili.senzaCopertina}>nessuna</span>
      )}
      <div className={stili.voceTesto}>
        <span className={stili.voceTitolo}>{voce.nome}</span>
        <p className={stili.dettagli}>
          <span className={comuni.mono}>{voce.riferimento}</span>
          {voce.immagine ? (
            <span>Testo alternativo: {voce.immagine.alt ? `«${voce.immagine.alt}»` : "nessuno"}</span>
          ) : (
            <span>Senza immagine</span>
          )}
          {voce.aggiornata && <span>cambiata {quandoCompleto(voce.aggiornata)}</span>}
        </p>
      </div>
      <div className={stili.azioniVoce}>
        <button
          type="button"
          className={comuni.secondaria}
          style={{ height: 44 }}
          aria-expanded={aperta}
          onClick={apri}
          disabled={inCorso}
        >
          {voce.immagine ? "Cambia" : "Assegna un'immagine"}
          <span className={stili.soloLettori}> a {voce.nome}</span>
        </button>
        {voce.immagine &&
          (togliendo ? (
            <span className={stili.conferma} role="alert">
              Togliere l&apos;immagine?
              <button type="button" className={comuni.distruttiva} style={{ height: 44 }} disabled={inCorso} onClick={togli}>
                Sì, togli
              </button>
              <button type="button" className={comuni.secondaria} style={{ height: 44 }} onClick={() => setTogliendo(false)}>
                Annulla
              </button>
            </span>
          ) : (
            <button type="button" className={comuni.secondaria} style={{ height: 44 }} disabled={inCorso} onClick={() => setTogliendo(true)}>
              Togli
              <span className={stili.soloLettori}> l&apos;immagine di {voce.nome}</span>
            </button>
          ))}
      </div>
      {errore && (
        <p className={comuni.errore} role="alert" style={{ gridColumn: "1 / -1" }}>
          {errore}
        </p>
      )}
      {aperta && <Modifica voce={voce} chiudi={apri} fatto={fatto} />}
    </li>
  );
}

function Modifica({ voce, chiudi, fatto }: { voce: VoceCatalogo; chiudi: () => void; fatto: (messaggio: string) => void }) {
  const { esegui, inCorso, errore } = useAzione();
  const [scelta, setScelta] = useState<{ id: string; url: string } | null>(
    voce.immagine_id && voce.immagine ? { id: voce.immagine_id, url: voce.immagine.url } : null,
  );
  /* Per una sezione il server ripiega sul nome quando l'alt manca, e lo restituisce: qui si mostra vuoto per non
   * salvare come scelto a mano ciò che era solo il ripiego. */
  const altIniziale = voce.immagine?.alt && !(voce.tipo === "sezione" && voce.immagine.alt === voce.nome) ? voce.immagine.alt : "";
  const [alt, setAlt] = useState(altIniziale);
  const [selettore, setSelettore] = useState(!voce.immagine);

  const salva = async () => {
    if (!scelta) return;
    const r = await esegui((t) =>
      impostaImmagineCatalogo(t, voce.tipo, voce.riferimento, { immagine_id: scelta.id, alt: alt.trim() || null }),
    );
    if (r) fatto(`Immagine di «${voce.nome}» salvata.`);
  };

  const invariata = scelta?.id === voce.immagine_id && alt.trim() === altIniziale.trim();

  return (
    <div className={stili.modulo} style={{ gridColumn: "1 / -1", margin: "0.25rem 0 0" }}>
      <div className={comuni.riga} style={{ alignItems: "center", marginBottom: "0.75rem" }}>
        {scelta ? (
          // eslint-disable-next-line @next/next/no-img-element -- l'immagine scelta
          <img
            src={urlMedia(scelta.url) ?? ""}
            alt=""
            width={160}
            height={120}
            style={{ flex: "0 0 auto", objectFit: "cover", border: "1px solid var(--filo)", borderRadius: "var(--raggio)" }}
          />
        ) : (
          <p className={comuni.riquadroNota} style={{ margin: 0 }}>
            Scegli un&apos;immagine dalla libreria o caricane una nuova.
          </p>
        )}
        <button
          type="button"
          className={comuni.secondaria}
          style={{ height: 44 }}
          aria-expanded={selettore}
          onClick={() => setSelettore(!selettore)}
        >
          {scelta ? "Scegli un'altra immagine" : "Scegli o carica"}
        </button>
      </div>

      {selettore && (
        <SelettoreImmagine
          scelta={scelta?.id}
          alScelta={(i: Immagine) => {
            setScelta({ id: i.id, url: i.url });
            setSelettore(false);
          }}
          chiudi={() => setSelettore(false)}
        />
      )}

      <label className={comuni.campo}>
        <span className={comuni.campoEtichetta}>Testo alternativo dell&apos;immagine</span>
        <input
          className={comuni.ingresso}
          value={alt}
          maxLength={200}
          onChange={(e) => setAlt(e.target.value)}
          placeholder={voce.tipo === "sezione" ? `Vuoto: «${voce.nome}»` : "Che cosa mostra l'immagine"}
        />
        <span className={comuni.campoAiuto}>
          Una frase che descrive l&apos;immagine a chi non la vede: la leggono i lettori di schermo per i non vedenti e i
          motori di ricerca. Per esempio «Una candela accesa su un tavolo con dieci carte disposte a croce».
          {voce.tipo === "sezione" ? " Vuoto: si usa il nome della sezione." : ""}
        </span>
      </label>

      {errore && (
        <p className={comuni.errore} role="alert">
          {errore}
        </p>
      )}
      <div className={stili.azioniModulo}>
        <button
          type="button"
          className={comuni.primaria}
          style={{ height: 44 }}
          disabled={inCorso || !scelta || invariata}
          onClick={salva}
        >
          {inCorso ? "Salvataggio…" : "Salva"}
        </button>
        <button type="button" className={comuni.secondaria} style={{ height: 44 }} onClick={chiudi}>
          Annulla
        </button>
      </div>
    </div>
  );
}
