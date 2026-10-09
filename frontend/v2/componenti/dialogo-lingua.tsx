"use client";

/* La lingua alla prima visita sul telefono (9/10).
 *
 * Chi apre il sito per la prima volta da un telefono (schermo stretto, o un telefono girato in orizzontale) e non ha
 * mai scelto una lingua (nessun cookie `lingua`, niente nel `localStorage`) trova prima di tutto questo dialogo: un
 * titolo, un riquadro con le quindici lingue («IT · Italiano»…, già scelta quella riconosciuta) che scorre DENTRO il
 * suo bordo, e sotto il riquadro «Accetta», sempre in vista. Accettare è il gesto del selettore (`useCambiaLingua`).
 * Mentre si sceglie, titolo e pulsante passano alla lingua scelta, se il suo dizionario c'è.
 *
 * Viene prima degli altri: il banner dei cookie e i dialoghi della lettura aspettano (`useLinguaDaScegliere`), così
 * arrivano già nella lingua giusta. Non c'è sul computer, né per chi è dentro: lì decide la lingua dell'account
 * (`lingua-profilo.ts`). Non ha la ✕: una scelta c'è sempre già, basta un tocco. */

import { useEffect, useId, useRef, useState } from "react";
import { useSessione } from "@/lib/sessione";
import { LINGUE, caricaDizionario, dizionarioPronto, type Dizionario, type Lingua } from "@/v2/i18n";
import { useLingua } from "@/v2/lib/lingua";
import { useCambiaLingua } from "@/v2/lib/lingua-profilo";

const TELEFONO = "(max-width: 760px), (pointer: coarse) and (max-height: 520px)";

function useTelefono(): boolean {
  const [telefono, setTelefono] = useState(false);
  useEffect(() => {
    const q = window.matchMedia(TELEFONO);
    const aggiorna = () => setTelefono(q.matches);
    aggiorna();
    q.addEventListener("change", aggiorna);
    return () => q.removeEventListener("change", aggiorna);
  }, []);
  return telefono;
}

/** `aperto`: il dialogo è aperto. `inAttesa`: è aperto o potrebbe aprirsi appena si sa (la scelta salvata non è ancora
 *  letta, la sessione non è ancora pronta): chi mostrerebbe un altro dialogo o un banner aspetta. */
export function useLinguaDaScegliere(): { aperto: boolean; inAttesa: boolean } {
  const { sceltaSalvata } = useLingua();
  const sessione = useSessione();
  const telefono = useTelefono();
  const inAttesa = telefono && sceltaSalvata !== true && !(sessione.pronta && sessione.autenticata);
  return { aperto: inAttesa && sceltaSalvata === false && sessione.pronta, inAttesa };
}

export function DialogoPrimaLingua() {
  const { aperto } = useLinguaDaScegliere();
  if (!aperto) return null;
  return <Dialogo />;
}

function Dialogo() {
  const { t, lingua } = useLingua();
  const cambia = useCambiaLingua();
  const id = useId();
  /* Finché non si tocca nulla vale la lingua riconosciuta (che può arrivare dopo l'apertura, dal paese). */
  const [toccata, setToccata] = useState<Lingua | null>(null);
  const scelta = toccata ?? lingua;
  const [caricato, setCaricato] = useState<{ lingua: Lingua; d: Dizionario } | null>(null);
  const riquadro = useRef<HTMLDivElement>(null);
  const scatola = useRef<HTMLDivElement>(null);

  /* I testi nella lingua che si sta scegliendo, appena il suo dizionario c'è; fino ad allora quelli della pagina. */
  useEffect(() => {
    if (dizionarioPronto(scelta)) return;
    let annullato = false;
    void caricaDizionario(scelta).then((d) => { if (!annullato) setCaricato({ lingua: scelta, d }); });
    return () => { annullato = true; };
  }, [scelta]);
  const k = (dizionarioPronto(scelta) ?? (caricato?.lingua === scelta ? caricato.d : t)).comune;

  /* All'apertura: la pagina sotto non scorre, il fuoco va sulla lingua già scelta (e la si porta in vista); Tab resta
   * nel dialogo. */
  useEffect(() => {
    const overflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const box = scatola.current;
    const scelto = box?.querySelector<HTMLInputElement>("input:checked");
    const voce = scelto?.closest("label");
    /* `.lingua-scatola` è posizionata: l'`offsetTop` della voce si misura dal suo bordo. */
    if (box && voce) box.scrollTop = voce.offsetTop - (box.clientHeight - voce.offsetHeight) / 2;
    scelto?.focus({ preventScroll: true });
    const tasto = (e: KeyboardEvent) => {
      if (e.key !== "Tab" || !riquadro.current) return;
      const focabili = [...riquadro.current.querySelectorAll<HTMLElement>("input:checked, button:not([disabled])")];
      if (!focabili.length) return;
      const [a, z] = [focabili[0], focabili[focabili.length - 1]];
      if (e.shiftKey && document.activeElement === a) { e.preventDefault(); z.focus(); }
      else if (!e.shiftKey && document.activeElement === z) { e.preventDefault(); a.focus(); }
    };
    document.addEventListener("keydown", tasto);
    return () => {
      document.removeEventListener("keydown", tasto);
      document.body.style.overflow = overflow;
    };
  }, []);

  return (
    <div className="dialog-backdrop lingua-sfondo">
      <div className="dialog lingua-dialogo" role="dialog" aria-modal="true" aria-labelledby={`${id}-t`}
        aria-describedby={`${id}-d`} ref={riquadro} tabIndex={-1} lang={scelta}>
        <h2 id={`${id}-t`}>{k.lingua_titolo}</h2>
        <p id={`${id}-d`} className="lingua-dialogo-testo">{k.lingua_testo}</p>
        {/* Il riquadro che scorre è un `div`: un `fieldset` non fa da contenitore di scorrimento in una colonna flex. */}
        <div className="lingua-scatola" ref={scatola}>
          <fieldset className="lingua-gruppo">
            <legend className="sr-only">{k.lingua_titolo}</legend>
            {LINGUE.map((l) => (
              <label key={l.codice} className="lingua-voce">
                <input type="radio" name={`${id}-lingua`} value={l.codice} checked={scelta === l.codice}
                  onChange={() => setToccata(l.codice)} />
                <b>{l.codice.toUpperCase()}</b>
                <span aria-hidden="true">·</span>
                <span lang={l.codice} dir="auto">{l.nome}</span>
              </label>
            ))}
          </fieldset>
        </div>
        <button type="button" className="button button-brass lingua-accetta" onClick={() => cambia(scelta)}>
          {k.lingua_accetta}
        </button>
      </div>
    </div>
  );
}
