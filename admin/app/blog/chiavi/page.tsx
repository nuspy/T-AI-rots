"use client";

import { useState } from "react";
import {
  chiaviApi,
  creaChiaveApi,
  revocaChiaveApi,
  type ChiaveApi,
  type PermessoChiave,
} from "@/lib/blog";
import { quandoCompleto } from "@/lib/formato";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../../comuni.module.css";
import stili from "../blog.module.css";
import { Schede } from "../schede";

/* Le chiavi per pubblicare sul blog da un programma: un agente (Hermes, OpenClaw, uno script) che scrive gli
 * articoli via REST (`/v1/blog/…`).
 *
 * **La chiave si vede una volta sola**: alla creazione. Nel database resta solo un'impronta, quindi non si può
 * rileggere né recuperare: se si perde, si revoca e se ne crea un'altra. Ogni chiave ha permessi (scrivere bozze,
 * pubblicare, cambiare le immagini) e due limiti (richieste al minuto, articoli al giorno). Vede e modifica solo gli
 * articoli che ha creato; il permesso «Cambiare le immagini» è l'eccezione: tocca le immagini di tutti. Revocarla la ferma subito. */

const PERMESSI: { id: PermessoChiave; nome: string; aiuto: string }[] = [
  { id: "blog:write", nome: "Scrivere bozze", aiuto: "Crea e modifica bozze, carica immagini, controlla la SEO." },
  {
    id: "blog:publish",
    nome: "Pubblicare",
    aiuto: "Può anche pubblicare: l'articolo esce sul sito senza passare da una persona.",
  },
  {
    id: "blog:media",
    nome: "Cambiare le immagini",
    aiuto: "Solo le immagini (copertina e immagini nel testo) di qualunque articolo, anche pubblicato: per uno skill che rifà le immagini. Non tocca testo, SEO né stato.",
  },
];

const nomePermesso = (p: string) => PERMESSI.find((x) => x.id === p)?.nome ?? p;

export default function Chiavi() {
  const elenco = useDati(chiaviApi);
  const { esegui, inCorso, errore } = useAzione();
  const [nome, setNome] = useState("");
  const [permessi, setPermessi] = useState<PermessoChiave[]>(["blog:write"]);
  const [limiteMinuto, setLimiteMinuto] = useState(30);
  const [limiteGiorno, setLimiteGiorno] = useState(20);
  const [nuova, setNuova] = useState<{ nome: string; chiave: string } | null>(null);
  const [copiata, setCopiata] = useState(false);
  const [daRevocare, setDaRevocare] = useState<number | null>(null);

  const scambia = (p: PermessoChiave) =>
    setPermessi((prima) => (prima.includes(p) ? prima.filter((x) => x !== p) : [...prima, p]));

  const crea = async () => {
    const r = await esegui((t) =>
      creaChiaveApi(t, { nome: nome.trim(), scopes: permessi, limite_minuto: limiteMinuto, limite_giorno: limiteGiorno }),
    );
    if (r) {
      setNuova({ nome: r.nome, chiave: r.chiave });
      setCopiata(false);
      setNome("");
      setPermessi(["blog:write"]);
      elenco.ricarica();
    }
  };

  const copia = async () => {
    if (!nuova) return;
    try {
      await navigator.clipboard.writeText(nuova.chiave);
      setCopiata(true);
    } catch {
      /* Senza permesso per gli appunti: la chiave è selezionabile con un clic nel riquadro. */
      setCopiata(false);
    }
  };

  const revoca = async (k: ChiaveApi) => {
    if ((await esegui((t) => revocaChiaveApi(t, k.id))) !== null) {
      setDaRevocare(null);
      elenco.ricarica();
    }
  };

  const valido = nome.trim().length > 0 && permessi.length > 0;
  const attive = (elenco.dati ?? []).filter((k) => k.attiva);
  const revocate = (elenco.dati ?? []).filter((k) => !k.attiva);

  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Blog · Chiavi</h1>
          <p className={comuni.sottotitolo}>
            Le chiavi permettono a un programma (un agente, uno script) di pubblicare articoli sul blog via REST. Ogni
            chiave ha i suoi permessi e i suoi limiti, e si può revocare in qualsiasi momento.
          </p>
        </div>
      </div>

      <Schede />

      {(errore || elenco.errore) && (
        <p className={comuni.errore} role="alert">
          {errore ?? elenco.errore}
        </p>
      )}

      {nuova && (
        <section className={stili.chiaveNuova} aria-labelledby="chiave-nuova" role="status">
          <h2 id="chiave-nuova" className={stili.pannelloTitolo}>
            Chiave «{nuova.nome}» creata
          </h2>
          <p className={comuni.riquadroNota} style={{ marginBottom: 0 }}>
            <strong>Copiala adesso: non si potrà rivedere.</strong> Nel database resta solo un&apos;impronta. Passala
            all&apos;agente come variabile d&apos;ambiente (<span className={comuni.mono}>TAROTS_API_KEY</span>), mai in un
            file del progetto né in un messaggio.
          </p>
          <code>{nuova.chiave}</code>
          <div className={comuni.riga}>
            <button type="button" className={comuni.primaria} style={{ height: 44 }} onClick={copia}>
              {copiata ? "Copiata" : "Copia la chiave"}
            </button>
            <button type="button" className={comuni.secondaria} style={{ height: 44 }} onClick={() => setNuova(null)}>
              Ho salvato la chiave
            </button>
          </div>
        </section>
      )}

      <section className={stili.pannello} aria-labelledby="crea-chiave" style={{ marginBottom: "1.25rem" }}>
        <h2 id="crea-chiave" className={stili.pannelloTitolo}>
          Nuova chiave
        </h2>
        <form
          onSubmit={(ev) => {
            ev.preventDefault();
            if (valido) void crea();
          }}
        >
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Nome</span>
            <input
              className={comuni.ingresso}
              value={nome}
              maxLength={80}
              onChange={(e) => setNome(e.target.value)}
              placeholder="A chi la dai: per esempio «Hermes — articoli settimanali»"
            />
          </label>

          <fieldset style={{ border: 0, padding: 0, margin: 0 }}>
            <legend className={comuni.campoEtichetta}>Permessi</legend>
            <div className={stili.permessi}>
              {PERMESSI.map((p) => (
                <label key={p.id} className={stili.interruttore} style={{ alignItems: "flex-start" }}>
                  <input type="checkbox" checked={permessi.includes(p.id)} onChange={() => scambia(p.id)} />
                  <span>
                    {p.nome}
                    <span className={comuni.campoAiuto} style={{ display: "block" }}>
                      {p.aiuto}
                    </span>
                  </span>
                </label>
              ))}
            </div>
          </fieldset>

          <div className={comuni.riga}>
            <label className={comuni.campo}>
              <span className={comuni.campoEtichetta}>Richieste al minuto</span>
              <input
                className={comuni.ingresso}
                type="number"
                inputMode="numeric"
                min={1}
                max={600}
                value={limiteMinuto}
                onChange={(e) => setLimiteMinuto(Math.max(1, Math.min(600, Number(e.target.value) || 1)))}
              />
            </label>
            <label className={comuni.campo}>
              <span className={comuni.campoEtichetta}>Articoli al giorno</span>
              <input
                className={comuni.ingresso}
                type="number"
                inputMode="numeric"
                min={1}
                max={500}
                value={limiteGiorno}
                onChange={(e) => setLimiteGiorno(Math.max(1, Math.min(500, Number(e.target.value) || 1)))}
              />
            </label>
          </div>

          <button type="submit" className={comuni.primaria} style={{ height: 44, marginBottom: "0.9rem" }} disabled={inCorso || !valido}>
            Crea la chiave
          </button>
        </form>
      </section>

      {!elenco.dati && elenco.inCorso && <p className={comuni.caricamento}>Caricamento…</p>}
      {elenco.dati && elenco.dati.length === 0 && (
        <div className={comuni.vuoto}>Nessuna chiave ancora: creane una per far pubblicare un agente.</div>
      )}

      {attive.length > 0 && (
        <ul className={`${stili.elenco} ${elenco.inCorso ? comuni.inRicarica : ""}`} aria-label="Chiavi attive" style={{ marginBottom: "1rem" }}>
          {attive.map((k) => (
            <li key={k.id} className={stili.voce} style={{ gridTemplateColumns: "minmax(0, 1fr)" }}>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem 1rem", alignItems: "center" }}>
                <div className={stili.voceTesto} style={{ flex: "1 1 14rem" }}>
                  <strong>{k.nome}</strong>
                  <p className={stili.dettagli}>
                    <span className={comuni.mono}>{k.prefisso}…</span>
                    <span>{k.scopes.map(nomePermesso).join(" · ")}</span>
                    <span>
                      {k.limite_minuto}/min · {k.limite_giorno} articoli/giorno
                    </span>
                  </p>
                  <p className={stili.dettagli}>
                    <span>creata {quandoCompleto(k.creata)}</span>
                    <span>{k.ultimo_uso ? `ultimo uso ${quandoCompleto(k.ultimo_uso)}` : "mai usata"}</span>
                    <span>{k.usi} richieste</span>
                  </p>
                </div>
                {daRevocare === k.id ? (
                  <span className={stili.conferma} role="alert">
                    Revocare «{k.nome}»? Smette di funzionare subito.
                    <button type="button" className={comuni.distruttiva} style={{ height: 44 }} disabled={inCorso} onClick={() => revoca(k)}>
                      Sì, revoca
                    </button>
                    <button type="button" className={comuni.secondaria} style={{ height: 44 }} onClick={() => setDaRevocare(null)}>
                      Annulla
                    </button>
                  </span>
                ) : (
                  <button type="button" className={comuni.distruttiva} style={{ height: 44 }} disabled={inCorso} onClick={() => setDaRevocare(k.id)}>
                    Revoca
                  </button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}

      {revocate.length > 0 && (
        <details style={{ marginBottom: "1rem" }}>
          <summary className={stili.comandoLink} style={{ display: "inline-flex", cursor: "pointer" }}>
            Chiavi revocate ({revocate.length})
          </summary>
          <ul className={stili.elenco} aria-label="Chiavi revocate" style={{ marginTop: "0.6rem" }}>
            {revocate.map((k) => (
              <li key={k.id} className={stili.voce} style={{ gridTemplateColumns: "minmax(0, 1fr)" }}>
                <div className={stili.voceTesto}>
                  <strong className={comuni.spento}>{k.nome}</strong>
                  <p className={stili.dettagli}>
                    <span className={comuni.mono}>{k.prefisso}…</span>
                    <span>revocata {quandoCompleto(k.revocata)}</span>
                    <span>{k.usi} richieste in tutto</span>
                  </p>
                </div>
              </li>
            ))}
          </ul>
        </details>
      )}
    </>
  );
}
