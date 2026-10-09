"use client";

/* Il selettore della lingua del sito (9/10). Chiuso mostra solo il codice («IT»), aperto l'elenco «IT · Italiano»: il
 * codice con il nome nella lingua stessa, così «UK · Українська» non si scambia per il Regno Unito. Niente bandiere
 * (una lingua non è un paese).
 *
 * Un `<select>` nativo non sa mostrare un testo da chiuso e un altro da aperto: qui c'è il modello «listbox» delle
 * ARIA Authoring Practices. Il pulsante dice che apre un elenco (`aria-haspopup`, `aria-expanded`); l'elenco prende
 * il fuoco e la voce attiva si segue con `aria-activedescendant`. Da tastiera: frecce, Home/Fine, Pagina su/giù, una
 * lettera per saltare alla lingua che comincia così, Invio o Spazio per scegliere, Esc per chiudere (il fuoco torna al
 * pulsante), Tab per uscire. Col dito o col mouse: un tocco sulla voce; un tocco fuori chiude. Voci alte 44 px.
 *
 * Scegliere è il gesto di `useCambiaLingua`: interfaccia, cookie, profilo per chi è dentro, indirizzo `/it`. */

import { useEffect, useId, useRef, useState, type KeyboardEvent } from "react";
import { LINGUE, datiLingua } from "@/v2/i18n";
import { useLingua } from "@/v2/lib/lingua";
import { useCambiaLingua } from "@/v2/lib/lingua-profilo";

export function SelettoreLingua({ su = false }: {
  /** L'elenco si apre verso l'alto (nel piede, in fondo alla pagina). */
  su?: boolean;
}) {
  const { t, lingua } = useLingua();
  const cambia = useCambiaLingua();
  const id = useId();
  const [aperto, setAperto] = useState(false);
  const [attiva, setAttiva] = useState(0);
  const contenitore = useRef<HTMLDivElement>(null);
  const pulsante = useRef<HTMLButtonElement>(null);
  const elenco = useRef<HTMLUListElement>(null);
  const corrente = Math.max(0, LINGUE.findIndex((l) => l.codice === lingua));
  const nome = datiLingua(lingua).nome;
  const codice = lingua.toUpperCase();

  const apri = (indice = corrente) => {
    setAttiva(indice);
    setAperto(true);
  };
  const chiudi = (fuocoAlPulsante = true) => {
    setAperto(false);
    if (fuocoAlPulsante) pulsante.current?.focus();
  };
  const scegli = (indice: number) => {
    const l = LINGUE[indice]?.codice;
    chiudi();
    if (l && l !== lingua) cambia(l);
  };

  /* Aperto: il fuoco va all'elenco; un tocco fuori lo chiude senza riprendersi il fuoco. */
  useEffect(() => {
    if (!aperto) return;
    elenco.current?.focus();
    const fuori = (e: PointerEvent) => {
      if (!contenitore.current?.contains(e.target as Node)) setAperto(false);
    };
    document.addEventListener("pointerdown", fuori);
    return () => document.removeEventListener("pointerdown", fuori);
  }, [aperto]);

  /* La voce attiva resta in vista mentre ci si muove con le frecce. */
  useEffect(() => {
    if (!aperto) return;
    document.getElementById(`${id}-o${attiva}`)?.scrollIntoView({ block: "nearest" });
  }, [aperto, attiva, id]);

  const tastoPulsante = (e: KeyboardEvent<HTMLButtonElement>) => {
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault();
      apri();
    }
  };

  const tastoElenco = (e: KeyboardEvent<HTMLUListElement>) => {
    const ultimo = LINGUE.length - 1;
    const vai = (i: number) => { e.preventDefault(); setAttiva(Math.min(ultimo, Math.max(0, i))); };
    switch (e.key) {
      case "ArrowDown": vai(attiva + 1); return;
      case "ArrowUp": vai(attiva - 1); return;
      case "Home": vai(0); return;
      case "End": vai(ultimo); return;
      case "PageDown": vai(attiva + 5); return;
      case "PageUp": vai(attiva - 5); return;
      case "Enter":
      case " ":
        e.preventDefault();
        scegli(attiva);
        return;
      case "Escape":
        e.preventDefault();
        chiudi();
        return;
      case "Tab":
        setAperto(false);
        return;
    }
    /* Una lettera: la prossima lingua il cui codice o nome comincia così. */
    if (e.key.length === 1 && !e.ctrlKey && !e.metaKey && !e.altKey) {
      const lettera = e.key.toLocaleLowerCase();
      for (let passo = 1; passo <= LINGUE.length; passo++) {
        const i = (attiva + passo) % LINGUE.length;
        const l = LINGUE[i];
        if (l.codice.startsWith(lettera) || l.nome.toLocaleLowerCase().startsWith(lettera)) {
          vai(i);
          return;
        }
      }
    }
  };

  return (
    <div className={`lang-menu${su ? " lang-menu-su" : ""}`} ref={contenitore}
      onBlur={(e) => { if (aperto && !contenitore.current?.contains(e.relatedTarget as Node | null)) setAperto(false); }}>
      <button ref={pulsante} type="button" className="lang-code"
        aria-haspopup="listbox" aria-expanded={aperto} aria-controls={aperto ? `${id}-l` : undefined}
        aria-label={`${codice} · ${t.comune.aria_lingua}: ${nome}`} title={`${t.comune.aria_lingua}: ${nome}`}
        onClick={() => (aperto ? chiudi() : apri())} onKeyDown={tastoPulsante}>
        <span aria-hidden="true">{codice}</span>
      </button>
      {aperto && (
        <ul id={`${id}-l`} ref={elenco} className="lang-list" role="listbox" tabIndex={-1}
          aria-label={t.comune.aria_lingua} aria-activedescendant={`${id}-o${attiva}`} onKeyDown={tastoElenco}>
          {LINGUE.map((l, i) => (
            <li key={l.codice} id={`${id}-o${i}`} role="option" aria-selected={l.codice === lingua}
              className={i === attiva ? "attiva" : undefined}
              onPointerMove={() => { if (i !== attiva) setAttiva(i); }}
              onClick={() => scegli(i)}>
              <b>{l.codice.toUpperCase()}</b>
              <span aria-hidden="true">·</span>
              <span lang={l.codice} dir="auto">{l.nome}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
