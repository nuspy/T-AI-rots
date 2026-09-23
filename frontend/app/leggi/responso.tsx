"use client";

/* Il responso finale, le sue fasi, e ciò che se ne può fare dopo:
 * condividerlo, scaricarne l'immagine, annotarlo nel diario. */

import { useState } from "react";
import Link from "next/link";
import { AnimatePresence, motion } from "framer-motion";
import { condividiLettura, type Stesa } from "@/lib/api";
import { useLingua } from "@/lib/lingua";
import { useAzione } from "@/lib/usa";
import { Markdown } from "../componenti/markdown";
import type { Posata } from "./tavolo";
import stili from "./leggi.module.css";

export function FaseResponso({ fase }: { fase: string }) {
  const { t } = useLingua();
  const testi: Record<string, string> = {
    unione: t.fase_unione,
    guardia: t.fase_guardia,
    revisione: t.fase_revisione,
  };
  return (
    <div className={stili.fase}>
      <motion.div
        className={stili.sigilloRotante}
        animate={{ rotate: 360 }}
        transition={{ duration: 12, repeat: Infinity, ease: "linear" }}
        aria-hidden="true"
      >
        <svg viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="46" fill="none" stroke="#d8b45a" strokeOpacity="0.5" />
          <circle cx="50" cy="50" r="38" fill="none" stroke="#b9a4ff" strokeOpacity="0.35" strokeDasharray="2 4" />
          <path d="M50 12 L83 69 L17 69 Z M50 88 L17 31 L83 31 Z" fill="none" stroke="#f1d68e" strokeWidth="1.4" />
        </svg>
      </motion.div>
      <AnimatePresence mode="wait">
        <motion.p key={fase} className="oracolo" initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -6 }}>
          {testi[fase] ?? t.fase_unione}
        </motion.p>
      </AnimatePresence>
    </div>
  );
}

/** Disegna l'immagine da condividere: domanda, carte, una frase del responso. */
async function disegnaImmagine(domanda: string, stesa: Stesa, posate: Posata[], responso: string): Promise<Blob | null> {
  const W = 1080;
  const H = 1350;
  const tela = document.createElement("canvas");
  tela.width = W;
  tela.height = H;
  const g = tela.getContext("2d");
  if (!g) return null;
  await document.fonts?.ready;

  const sfondo = g.createRadialGradient(W / 2, H * 0.35, 50, W / 2, H * 0.5, H * 0.8);
  sfondo.addColorStop(0, "#2c1f5c");
  sfondo.addColorStop(1, "#07050f");
  g.fillStyle = sfondo;
  g.fillRect(0, 0, W, H);
  for (let i = 0; i < 260; i++) {
    g.fillStyle = `rgba(241,214,142,${Math.random() * 0.6})`;
    g.fillRect(Math.random() * W, Math.random() * H, 2, 2);
  }
  g.strokeStyle = "rgba(216,180,90,0.8)";
  g.lineWidth = 3;
  g.strokeRect(40, 40, W - 80, H - 80);

  const titoli = getComputedStyle(document.documentElement).getPropertyValue("--font-titoli") || "serif";
  const oracolo = getComputedStyle(document.documentElement).getPropertyValue("--font-oracolo") || "serif";
  g.textAlign = "center";
  g.fillStyle = "#f1d68e";
  g.font = `700 64px ${titoli}`;
  g.fillText("T·AI·rots", W / 2, 140);
  g.fillStyle = "#b9a4ff";
  g.font = `400 30px ${titoli}`;
  g.fillText(stesa.nome.toUpperCase(), W / 2, 190);

  const avvolgi = (testo: string, x: number, y: number, max: number, riga: number, massimeRighe = 6) => {
    const parole = testo.split(/\s+/);
    let linea = "";
    let n = 0;
    for (const p of parole) {
      const prova = linea ? `${linea} ${p}` : p;
      if (g.measureText(prova).width > max && linea) {
        g.fillText(linea, x, y + n * riga);
        n++;
        linea = p;
        if (n >= massimeRighe) return y + n * riga;
      } else linea = prova;
    }
    g.fillText(linea, x, y + n * riga);
    return y + (n + 1) * riga;
  };

  g.fillStyle = "#efe6d2";
  g.font = `italic 500 46px ${oracolo}`;
  let y = avvolgi(`«${domanda}»`, W / 2, 290, W - 200, 56, 3);

  y += 30;
  g.font = `400 34px ${titoli}`;
  for (const p of posate.filter((x) => x.carta).slice(0, 13)) {
    const pos = stesa.posizioni.find((q) => q.n === p.posizione);
    g.fillStyle = "#d8b45a";
    g.fillText(`${pos?.nome ?? p.posizione} · ${p.carta!.nome_it}${p.rovescio ? " ↺" : ""}`, W / 2, y);
    y += posate.length > 7 ? 44 : 54;
  }

  const tendenza = responso.split(/##\s*La tendenza più probabile/i)[1] ?? responso;
  const frase = tendenza.replace(/[#*]/g, "").trim().split(/(?<=[.!?])\s/).slice(0, 2).join(" ");
  g.fillStyle = "#efe6d2";
  g.font = `italic 400 38px ${oracolo}`;
  avvolgi(frase, W / 2, Math.max(y + 40, H - 360), W - 200, 48, 5);

  g.fillStyle = "rgba(179,168,207,0.8)";
  g.font = `400 22px sans-serif`;
  g.fillText("Lettura AI · non è una certezza · nessuna base scientifica", W / 2, H - 80);

  return new Promise((ok) => tela.toBlob((b) => ok(b), "image/png"));
}

export function Responso({
  id,
  domanda,
  stesa,
  posate,
  testo,
  finito,
  disclaimer,
  commitment,
  condivisoIniziale,
  saldo,
  onNuova,
}: {
  id: string;
  domanda: string;
  stesa: Stesa;
  posate: Posata[];
  testo: string;
  finito: boolean;
  disclaimer: string;
  commitment: string | null;
  condivisoIniziale: string | null;
  saldo: number | null;
  onNuova: () => void;
}) {
  const { t } = useLingua();
  const { esegui } = useAzione();
  const [token, setToken] = useState<string | null>(condivisoIniziale);
  const [avviso, setAvviso] = useState<string | null>(null);

  const condividi = async () => {
    let tk = token;
    if (!tk) {
      const r = await esegui((tok) => condividiLettura(tok, id, true));
      tk = r?.share_token ?? null;
      setToken(tk);
    }
    if (!tk) return;
    const url = `${window.location.origin}/s/${tk}`;
    if (navigator.share) {
      try {
        await navigator.share({ title: "T·AI·rots", text: domanda, url });
        return;
      } catch {
        /* annullato: si copia il link */
      }
    }
    await navigator.clipboard?.writeText(url);
    setAvviso(t.link_copiato);
  };

  const scarica = async () => {
    const blob = await disegnaImmagine(domanda, stesa, posate, testo);
    if (!blob) return;
    const file = new File([blob], "lettura-tarots.png", { type: "image/png" });
    if (navigator.canShare?.({ files: [file] })) {
      try {
        await navigator.share({ files: [file], title: "T·AI·rots" });
        return;
      } catch {
        /* annullato: si scarica */
      }
    }
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "lettura-tarots.png";
    a.click();
    URL.revokeObjectURL(a.href);
  };

  return (
    <motion.section
      className={`pannello ${stili.responso}`}
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7 }}
      aria-live="polite"
    >
      <h2 className={stili.responsoTitolo}>✦ {t.il_responso} ✦</h2>
      <Markdown testo={testo} className={`oracolo ${stili.responsoTesto}`} />
      {finito && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}>
          <p className={stili.disclaimerFinale}>{disclaimer}</p>
          {commitment && (
            <details className={stili.verifica}>
              <summary>{t.verifica_mazzo}</summary>
              <p>{t.verifica_testo}</p>
              <code>{commitment}</code>
            </details>
          )}
          <div className={stili.azioniCentro}>
            <button className="bottone" onClick={condividi}>{t.condividi}</button>
            <button className="bottone-secondario" onClick={scarica}>{t.scarica_immagine}</button>
            <button className="bottone-secondario" onClick={onNuova}>{t.nuova_lettura}</button>
          </div>
          {avviso && <p className={stili.avviso} role="status">{avviso}</p>}
          {saldo === 0 && (
            <p className={stili.avviso}>
              {t.crediti_finiti}. <Link href="/piano">{t.compra}</Link>
            </p>
          )}
        </motion.div>
      )}
    </motion.section>
  );
}
