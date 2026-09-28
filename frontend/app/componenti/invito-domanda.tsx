"use client";

/* L'invito "fammi una domanda" (v6, Fase F): globale, su ogni pagina — appena sotto il logo in
 * home, ancorato a 1/3 dell'altezza altrove. Per chi non ha fatto login promette la lettura
 * gratuita; per chi è già dentro no (l'omaggio è solo per chi deve ancora registrarsi). Non apre
 * direttamente una lettura: porta a `/leggi` con la domanda già scritta, come il bottone della chat
 * proattiva — lì lo stesso flusso, anonimo o autenticato, sceglie la stesa e comincia. */

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useLingua } from "@/lib/lingua";
import { useSessione } from "@/lib/sessione";
import stili from "./invito-domanda.module.css";

const CHIAVE_CHIUSO = "tarots.invito.chiuso";

export function InvitoDomanda() {
  const { t } = useLingua();
  const sessione = useSessione();
  const router = useRouter();
  const pathname = usePathname();
  const inHome = pathname === "/";
  const [domanda, setDomanda] = useState("");
  const [chiuso, setChiuso] = useState(false);

  useEffect(() => {
    if (inHome) return;
    try {
      setChiuso(window.sessionStorage.getItem(CHIAVE_CHIUSO) === "1");
    } catch {
      /* niente memoria: resta visibile */
    }
  }, [inHome]);

  // Le letture condivise pubbliche e la pagina della lettura stessa non hanno bisogno dell'invito:
  // chi le apre sta già facendo qualcos'altro di preciso (leggere una lettura altrui, o la propria).
  if (pathname?.startsWith("/s/") || pathname?.startsWith("/leggi")) return null;
  if (!inHome && chiuso) return null;

  const chiudi = () => {
    setChiuso(true);
    try {
      window.sessionStorage.setItem(CHIAVE_CHIUSO, "1");
    } catch {
      /* preferenza persa: l'invito ricompare al prossimo giro, non è grave */
    }
  };

  const invia = () => {
    const testo = domanda.trim();
    if (!testo) return;
    router.push(`/leggi?tipo=standard&domanda=${encodeURIComponent(testo)}`);
  };

  return (
    <div className={`${stili.invito} ${inHome ? stili.inHome : stili.altrove}`} role="complementary">
      {!inHome && (
        <button type="button" className={stili.chiudi} aria-label={t.chat_chiudi} onClick={chiudi}>✕</button>
      )}
      <p className={stili.titolo}>{sessione.autenticata ? t.invito_titolo_autenticato : t.invito_titolo}</p>
      <div className={stili.modulo}>
        <input
          className={stili.campo} value={domanda} placeholder={t.invito_placeholder}
          onChange={(e) => setDomanda(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") invia(); }}
        />
        <button type="button" className="bottone" disabled={!domanda.trim()} onClick={invia}>
          {t.invito_invia}
        </button>
      </div>
    </div>
  );
}
