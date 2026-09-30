"use client";

/* L'Oracolo (v8): un solo widget ancorato al fondo pagina, sempre visibile — non più un lanciatore
 * da aprire al click (quello era `chat-proattiva.tsx`, v6 Fase E) né un banner separato da esso
 * (quello era `invito-domanda.tsx`, v6/v7). Sostituisce entrambi.
 *
 * Chi non ha fatto login vede l'invito "Ask me something, I'll give you a free reading": scrivere e
 * inviare apre la lettura anonima vera (v6, Fase F) — l'AI risponde per davvero, solo attraverso il
 * percorso già esistente e già sicuro (un colpo gratuito per cookie), non una chat libera senza
 * autenticazione: aprire l'inferenza a chiunque senza login sarebbe un costo e un vettore di abuso
 * senza il limite che quel percorso già impone.
 *
 * Chi ha fatto login vede la stessa barra, ma con la conversazione vera (v6, Fase E): storico,
 * apertura proattiva dopo inattività, proposta di lettura. Non c'è più un pannello modale da aprire:
 * la cronologia, quando esiste, sta sopra la barra d'invio, sempre visibile.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import {
  avviaChat, impostazioniChat, inviaMessaggioChat, storicoChat, type TurnoChat,
} from "@/lib/api";
import { useLingua } from "@/lib/lingua";
import { useSessione } from "@/lib/sessione";
import { useCarica } from "@/lib/usa";
import stili from "./oracolo.module.css";

const CHIAVE_MUTO = "tarots.chat.muto";
const CHIAVE_CHIUSO = "tarots.invito.chiuso";

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

export function Oracolo() {
  const { t } = useLingua();
  const sessione = useSessione();
  const router = useRouter();
  const pathname = usePathname();
  const inHome = pathname === "/";

  // `useCarica` non chiama `fetcher` finché `sessione.autenticata` non è vera (vedi `usa.ts`).
  const impostazioni = useCarica(impostazioniChat);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const caricatoRef = useRef(false);

  const [muto, setMuto] = useState(false);
  const [turni, setTurni] = useState<TurnoChat[]>([]);
  const [testo, setTesto] = useState("");
  const [inCorso, setInCorso] = useState(false);
  const [chiuso, setChiuso] = useState(false);

  useEffect(() => setMuto(leggiMuto()), []);

  useEffect(() => {
    if (inHome) return;
    try {
      setChiuso(window.sessionStorage.getItem(CHIAVE_CHIUSO) === "1");
    } catch {
      /* niente memoria: resta visibile */
    }
  }, [inHome]);

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
  }, [sessione.token, suona]);

  // Il timer di inattività: riparte a ogni turno (dell'AI o dell'utente). Solo per chi ha fatto login:
  // per chi non l'ha fatto non esiste una conversazione da riaprire da sola.
  useEffect(() => {
    if (!sessione.autenticata || !impostazioni.dati) return;
    if (timerRef.current) clearTimeout(timerRef.current);
    const millisecondi = impostazioni.dati.proattiva_minuti_inattivita * 60_000;
    timerRef.current = setTimeout(() => { void chiediApertura(); }, millisecondi);
    return () => { if (timerRef.current) clearTimeout(timerRef.current); };
  }, [sessione.autenticata, impostazioni.dati, turni.length, chiediApertura]);

  // Le letture condivise pubbliche e la pagina della lettura stessa non hanno bisogno del widget:
  // chi le apre sta già facendo qualcos'altro di preciso.
  if (pathname?.startsWith("/s/") || pathname?.startsWith("/leggi")) return null;
  if (!inHome && chiuso && !sessione.autenticata) return null;

  const chiudi = () => {
    setChiuso(true);
    try {
      window.sessionStorage.setItem(CHIAVE_CHIUSO, "1");
    } catch {
      /* preferenza persa: il widget ricompare al prossimo giro, non è grave */
    }
  };

  const inviaAutenticato = async () => {
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

  // Chi non ha fatto login non ha una conversazione: scrivere apre la lettura anonima vera (già
  // esistente, già sicura — un colpo gratuito per cookie), non una chat libera senza autenticazione.
  const inviaAnonimo = () => {
    const domanda = testo.trim();
    if (!domanda) return;
    router.push(`/leggi?tipo=standard&domanda=${encodeURIComponent(domanda)}`);
  };

  const invia = () => { void (sessione.autenticata ? inviaAutenticato() : Promise.resolve(inviaAnonimo())); };

  return (
    <div className={`${stili.oracolo} ${inHome ? stili.inHome : stili.altrove}`} role="complementary">
      {sessione.autenticata && <audio ref={audioRef} src="/suoni/chime.wav" preload="auto" />}

      {!inHome && !sessione.autenticata && (
        <button type="button" className={stili.chiudi} aria-label={t.chat_chiudi} onClick={chiudi}>✕</button>
      )}
      {sessione.autenticata && (
        <button
          type="button" className={stili.chiudi}
          title={muto ? t.chat_muto_attiva : t.chat_muto_disattiva}
          aria-label={muto ? t.chat_muto_attiva : t.chat_muto_disattiva}
          onClick={() => { const v = !muto; setMuto(v); scriviMuto(v); }}
        >
          {muto ? "🔇" : "🔊"}
        </button>
      )}

      <p className={stili.titolo}>{sessione.autenticata ? t.chat_titolo : t.invito_titolo}</p>

      {sessione.autenticata && turni.length > 0 && (
        <div className={stili.storico} role="log">
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
      )}

      <div className={stili.modulo}>
        <input
          className={stili.campo} value={testo}
          placeholder={sessione.autenticata ? t.chat_placeholder : t.invito_placeholder}
          onChange={(e) => setTesto(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") invia(); }}
        />
        <button
          type="button" className={`bottone ${stili.invia}`}
          disabled={!testo.trim() || (sessione.autenticata && inCorso)}
          onClick={invia}
        >
          {sessione.autenticata ? t.chat_invia : t.invito_invia}
        </button>
      </div>
    </div>
  );
}
