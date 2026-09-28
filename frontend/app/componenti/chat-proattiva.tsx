"use client";

/* La chat proattiva (v6, Fase E): solo per chi ha fatto login. L'AI apre da sola dopo X minuti di
 * inattività (configurabile da console) o dopo l'ultimo turno, con un "chime" delicato — mai per una
 * risposta diretta a un messaggio dell'utente, solo per un'iniziativa dell'AI. Il mute è una
 * preferenza locale (localStorage), non un confine di sicurezza. */

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import {
  avviaChat, impostazioniChat, inviaMessaggioChat, storicoChat, type TurnoChat,
} from "@/lib/api";
import { useLingua } from "@/lib/lingua";
import { useSessione } from "@/lib/sessione";
import { useCarica } from "@/lib/usa";
import stili from "./chat-proattiva.module.css";

const CHIAVE_MUTO = "tarots.chat.muto";

const leggiMuto = (): boolean => {
  try {
    return window.localStorage.getItem(CHIAVE_MUTO) === "1";
  } catch {
    return false;
  }
};

const scriviMuto = (v: boolean) => {
  try {
    window.localStorage.setItem(CHIAVE_MUTO, v ? "1" : "0");
  } catch {
    /* preferenza persa: il widget riparte non muto al prossimo giro, non è grave */
  }
};

export function ChatProattiva() {
  const { t } = useLingua();
  const sessione = useSessione();
  const router = useRouter();
  const impostazioni = useCarica(impostazioniChat);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const caricatoRef = useRef(false);

  const [aperto, setAperto] = useState(false);
  const [muto, setMuto] = useState(false);
  const [turni, setTurni] = useState<TurnoChat[]>([]);
  const [nuovo, setNuovo] = useState(false);
  const [testo, setTesto] = useState("");
  const [inCorso, setInCorso] = useState(false);

  useEffect(() => setMuto(leggiMuto()), []);

  // Storico iniziale, una sola volta dopo il login.
  useEffect(() => {
    if (!sessione.autenticata || caricatoRef.current) return;
    caricatoRef.current = true;
    void storicoChat(sessione.token).then((r) => setTurni(r.turni)).catch(() => undefined);
  }, [sessione.autenticata, sessione.token]);

  const suona = useCallback(() => {
    if (muto) return;
    audioRef.current?.play().catch(() => undefined);
  }, [muto]);

  const chiediApertura = useCallback(async () => {
    const r = await avviaChat(sessione.token).catch(() => null);
    if (!r?.turno) return;
    setTurni((prima) => [...prima, r.turno!]);
    suona();
    if (!aperto) setNuovo(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessione.token, suona, aperto]);

  // Il timer di inattività: riparte a ogni turno (dell'AI o dell'utente).
  useEffect(() => {
    if (!sessione.autenticata || !impostazioni.dati) return;
    if (timerRef.current) clearTimeout(timerRef.current);
    const millisecondi = impostazioni.dati.proattiva_minuti_inattivita * 60_000;
    timerRef.current = setTimeout(() => { void chiediApertura(); }, millisecondi);
    return () => { if (timerRef.current) clearTimeout(timerRef.current); };
  }, [sessione.autenticata, impostazioni.dati, turni.length, chiediApertura]);

  if (!sessione.autenticata) return null;

  const invia = async () => {
    const testoDaInviare = testo.trim();
    if (!testoDaInviare || inCorso) return;
    setTesto("");
    setInCorso(true);
    setTurni((prima) => [
      ...prima,
      { id: `locale-${Date.now()}`, ruolo: "utente", testo: testoDaInviare, proposta: null, creato: null },
    ]);
    const r = await inviaMessaggioChat(sessione.token, testoDaInviare).catch(() => null);
    setInCorso(false);
    if (r?.turno) setTurni((prima) => [...prima, r.turno!]);
    // Nessun chime: è una risposta diretta a ciò che l'utente ha appena scritto, non un'iniziativa.
  };

  const vaiALettura = (argomento: string, categoria: string) => {
    const parametri = new URLSearchParams({ tipo: categoria, domanda: argomento });
    router.push(`/leggi?${parametri.toString()}`);
  };

  return (
    <>
      {/* eslint-disable-next-line jsx-a11y/media-has-caption -- un suono di notifica, non un contenuto */}
      <audio ref={audioRef} src="/suoni/chime.wav" preload="auto" />

      {!aperto && (
        <button
          type="button" className={stili.lanciatore} aria-label={t.chat_apri}
          onClick={() => { setAperto(true); setNuovo(false); }}
        >
          ✦
          {nuovo && <span className={stili.pallino} aria-hidden="true" />}
        </button>
      )}

      {aperto && (
        <div className={stili.pannello} role="dialog" aria-label={t.chat_titolo}>
          <div className={stili.intestazione}>
            <h2 className={stili.titolo}>{t.chat_titolo}</h2>
            <div className={stili.azioniIntestazione}>
              <button
                type="button" className={stili.iconaTocco}
                title={muto ? t.chat_muto_attiva : t.chat_muto_disattiva}
                aria-label={muto ? t.chat_muto_attiva : t.chat_muto_disattiva}
                onClick={() => { const v = !muto; setMuto(v); scriviMuto(v); }}
              >
                {muto ? "🔇" : "🔊"}
              </button>
              <button
                type="button" className={stili.iconaTocco} title={t.chat_chiudi} aria-label={t.chat_chiudi}
                onClick={() => setAperto(false)}
              >
                ✕
              </button>
            </div>
          </div>

          <div className={stili.corpo}>
            {turni.map((turno) => (
              <div key={turno.id}>
                <p className={`${stili.turno} ${turno.ruolo === "ai" ? stili.turnoAi : stili.turnoUtente}`}>
                  {turno.testo}
                </p>
                {turno.proposta && (
                  <button
                    type="button" className={`bottone-secondario ${stili.proposta}`}
                    onClick={() => vaiALettura(turno.proposta!.argomento, turno.proposta!.categoria)}
                  >
                    {t.chat_leggi_le_carte_per(turno.proposta.argomento)}
                  </button>
                )}
              </div>
            ))}
          </div>

          <div className={stili.modulo}>
            <input
              className={stili.campo} value={testo} placeholder={t.chat_placeholder}
              onChange={(e) => setTesto(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") void invia(); }}
            />
            <button type="button" className={`bottone ${stili.invia}`} disabled={inCorso || !testo.trim()} onClick={invia}>
              {t.chat_invia}
            </button>
          </div>
        </div>
      )}
    </>
  );
}
