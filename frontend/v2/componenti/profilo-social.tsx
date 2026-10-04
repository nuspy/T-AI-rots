"use client";

/* Dopo ogni accesso, una volta: `POST /me/profilo-social`. Il server riempie i campi vuoti della scheda con i dati
 * dei social collegati (nome, cognome, data di nascita, sesso, lingua, foto) e aggiorna la posizione attuale; non
 * sovrascrive mai ciò che la persona ha scritto. Non mostra niente: chi vuole vedere cosa è arrivato lo trova nel
 * profilo, con il nome del social accanto al campo.
 *
 * «Una volta per accesso»: l'accesso è `auth_time` del token (cambia solo con un login vero, non con i rinnovi del
 * token offline). Con il login persistente un accesso può durare mesi: la chiamata si ripete comunque dopo un giorno,
 * per tenere aggiornata la posizione. Il token del social che Keycloak conserva vale circa un'ora dal login con quel
 * social: chiamare subito dopo l'accesso è ciò che permette di leggerlo. */

import { useEffect, useRef } from "react";
import { importaProfiloSocial } from "@/lib/api";
import { useSessione } from "@/lib/sessione";

const CHIAVE = "tarots.profiloSocial";
const UN_GIORNO = 24 * 60 * 60 * 1000;

function accessoDelToken(token: string): string | null {
  try {
    const corpo = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    const dati = JSON.parse(atob(corpo.padEnd(Math.ceil(corpo.length / 4) * 4, "=")));
    return dati?.sub ? `${dati.sub}:${dati.auth_time ?? ""}` : null;
  } catch {
    return null;
  }
}

function giaFatto(accesso: string): boolean {
  try {
    const salvato = JSON.parse(window.localStorage.getItem(CHIAVE) ?? "null") as { accesso?: string; il?: number } | null;
    return salvato?.accesso === accesso && typeof salvato.il === "number" && Date.now() - salvato.il < UN_GIORNO;
  } catch {
    return false;
  }
}

function segnaFatto(accesso: string): void {
  try {
    window.localStorage.setItem(CHIAVE, JSON.stringify({ accesso, il: Date.now() }));
  } catch {
    /* memoria bloccata: la chiamata si ripeterà, ed è idempotente */
  }
}

export function ImportaProfiloSocial() {
  const { autenticata, token } = useSessione();
  const fatto = useRef<string | null>(null);

  useEffect(() => {
    if (!autenticata || !token) return;
    const accesso = accessoDelToken(token);
    if (!accesso || fatto.current === accesso || giaFatto(accesso)) return;
    fatto.current = accesso;
    void importaProfiloSocial(token)
      .then(() => segnaFatto(accesso))
      .catch(() => {
        /* un social che non risponde non è un errore per chi entra: riproverà al prossimo caricamento */
        fatto.current = null;
      });
  }, [autenticata, token]);

  return null;
}
