/* La dimensione del testo (A− / A+, `testo.tsx`): le costanti e lo script del layout, in un file senza "use client"
 * perché il layout (del server) legga la stringa vera. */

export const CHIAVE_TESTO = "tarots.testo";
/** I passi, in percentuale della dimensione di base del browser. */
export const PASSI_TESTO = [70, 80, 90, 100, 110, 120, 130] as const;
export const BASE_TESTO = 100;

/** Lo script del layout: gira prima del disegno e applica la dimensione salvata. Niente dipendenze. */
export const SCRIPT_TESTO =
  `try{var t=Number(localStorage.getItem(${JSON.stringify(CHIAVE_TESTO)}));` +
  `if([${PASSI_TESTO.join(",")}].indexOf(t)>=0&&t!==${BASE_TESTO})document.documentElement.style.fontSize=t+"%"}catch(e){}`;
