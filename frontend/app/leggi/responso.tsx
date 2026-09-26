"use client";

/* Il responso finale, le sue fasi, e ciò che se ne può fare dopo:
 * condividerlo, scaricarne l'immagine, annotarlo nel diario. */

import { useState } from "react";
import Link from "next/link";
import { AnimatePresence, motion } from "framer-motion";
import { condividiLettura, type Stesa } from "@/lib/api";
import { dizionario, nomeCarta, nomePosizione, nomeStesa, type Lingua } from "@/lib/i18n";
import { useLingua, useLinguaNomi } from "@/lib/lingua";
import { useAzione } from "@/lib/usa";
import { ESTENSIONE } from "../componenti/carta";
import { Markdown } from "../componenti/markdown";
import { FATTORE, SCALA_CARTE, type Posata } from "./tavolo";
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

/* Un'immagine dalla cartella `public/cards`, o `null` se non si carica: la
 * carta senza faccia si disegna comunque, col suo nome. */
function caricaImmagine(src: string): Promise<HTMLImageElement | null> {
  return new Promise((ok) => {
    const img = new Image();
    img.onload = () => ok(img);
    img.onerror = () => ok(null);
    img.src = src;
  });
}

function rettangoloArrotondato(g: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number) {
  g.beginPath();
  g.moveTo(x + r, y);
  g.arcTo(x + w, y, x + w, y + h, r);
  g.arcTo(x + w, y + h, x, y + h, r);
  g.arcTo(x, y + h, x, y, r);
  g.arcTo(x, y, x + w, y, r);
  g.closePath();
}

/** Disegna l'immagine da condividere: domanda, **il tavolo con le carte**, una
 *  frase del responso. Il tavolo è quello della lettura: le carte stanno dove
 *  le ha posate la stesa, con le stesse proporzioni, la stessa rotazione delle
 *  carte orizzontali e il rovescio di quelle rovesciate. */
async function disegnaImmagine(
  domanda: string, stesa: Stesa, posate: Posata[], responso: string, ll: Lingua,
): Promise<Blob | null> {
  const W = 1080;
  const H = 1350;
  const tela = document.createElement("canvas");
  tela.width = W;
  tela.height = H;
  const g = tela.getContext("2d");
  if (!g) return null;
  await document.fonts?.ready;

  const conCarta = posate.filter((x) => x.carta);
  const immagini = new Map(
    await Promise.all(
      conCarta.map(async (p) => [p.posizione, await caricaImmagine(`/cards/${p.carta!.id}.${ESTENSIONE}`)] as const),
    ),
  );

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
  g.direction = ll === "ar" ? "rtl" : "ltr";
  g.textAlign = "center";
  g.fillStyle = "#f1d68e";
  g.font = `700 60px ${titoli}`;
  g.fillText("T·AI·rots", W / 2, 125);
  g.fillStyle = "#b9a4ff";
  g.font = `400 28px ${titoli}`;
  g.fillText(nomeStesa(stesa, ll).toUpperCase(), W / 2, 172);

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
  g.font = `italic 500 40px ${oracolo}`;
  avvolgi(`«${domanda}»`, W / 2, 232, W - 200, 50, 2);

  /* ---- il tavolo con le carte ---- */

  const quadrato = stesa.id === "ruota-astrologica";
  const TH = 600;
  const TW = quadrato ? TH : Math.round((TH * 16) / 12);
  const x0 = (W - TW) / 2;
  const y0 = 340;

  const tappeto = g.createRadialGradient(W / 2, y0 + TH / 2, 20, W / 2, y0 + TH / 2, TW * 0.6);
  tappeto.addColorStop(0, "rgba(72,46,140,0.85)");
  tappeto.addColorStop(1, "rgba(12,8,28,0.9)");
  g.fillStyle = tappeto;
  rettangoloArrotondato(g, x0, y0, TW, TH, quadrato ? TW / 2 : 26);
  g.fill();
  g.strokeStyle = "rgba(216,180,90,0.5)";
  g.lineWidth = 2;
  g.stroke();

  const lc = TW * (FATTORE[stesa.id] ?? 0.1) * SCALA_CARTE;
  const ac = (lc * 16) / 9;
  for (const p of conCarta) {
    const pos = stesa.posizioni.find((q) => q.n === p.posizione);
    if (!pos) continue;
    const cx = x0 + pos.x * TW;
    const cy = y0 + pos.y * TH;
    const giro = ((pos.rotazione + (p.rovescio ? 180 : 0)) * Math.PI) / 180;
    const img = immagini.get(p.posizione);

    g.save();
    g.translate(cx, cy);
    g.rotate(giro);
    g.shadowColor = "rgba(0,0,0,0.65)";
    g.shadowBlur = 16;
    g.shadowOffsetY = 6;
    g.fillStyle = "#171129";
    rettangoloArrotondato(g, -lc / 2, -ac / 2, lc, ac, lc * 0.06);
    g.fill();
    g.shadowColor = "transparent";
    g.save();
    rettangoloArrotondato(g, -lc / 2, -ac / 2, lc, ac, lc * 0.06);
    g.clip();
    if (img) {
      g.drawImage(img, -lc / 2, -ac / 2, lc, ac);
    } else {
      g.fillStyle = "#efe6d2";
      g.font = `400 ${Math.max(12, lc * 0.13)}px ${titoli}`;
      avvolgi(nomeCarta(p.carta!, ll), 0, 0, lc - 12, Math.max(14, lc * 0.15), 3);
    }
    g.restore();
    g.strokeStyle = "rgba(216,180,90,0.75)";
    g.lineWidth = 2;
    rettangoloArrotondato(g, -lc / 2, -ac / 2, lc, ac, lc * 0.06);
    g.stroke();
    g.restore();

    /* Il numero della posizione, sul primo angolo della carta come la vede la
     * stesa (senza il giro del rovescio): la legenda sotto lo spiega. */
    const teta = (pos.rotazione * Math.PI) / 180;
    const dx = -lc / 2;
    const dy = -ac / 2;
    const bx = cx + dx * Math.cos(teta) - dy * Math.sin(teta);
    const by = cy + dx * Math.sin(teta) + dy * Math.cos(teta);
    g.fillStyle = "#f1d68e";
    g.beginPath();
    g.arc(bx, by, 15, 0, Math.PI * 2);
    g.fill();
    g.fillStyle = "#1a1030";
    g.font = `700 18px ${titoli}`;
    g.textBaseline = "middle";
    g.fillText(String(p.posizione), bx, by + 1);
    g.textBaseline = "alphabetic";
  }

  /* ---- legenda: numero, posizione, carta ---- */

  const voci = conCarta.map((p) => {
    const pos = stesa.posizioni.find((q) => q.n === p.posizione);
    /* La carta prima, la posizione dopo: se la riga si accorcia, va via la posizione. */
    return `${p.posizione}. ${nomeCarta(p.carta!, ll)}${p.rovescio ? " ↺" : ""} · ${pos ? nomePosizione(pos, ll) : ""}`;
  });
  const colonne = voci.length <= 5 ? 1 : voci.length <= 10 ? 2 : 3;
  const righe = Math.ceil(voci.length / colonne);
  const largColonna = (W - 180) / colonne;
  g.font = `400 ${voci.length > 10 ? 17 : voci.length > 5 ? 19 : 22}px ${titoli}`;
  g.fillStyle = "#d8b45a";
  g.textAlign = "left";
  const tronca = (testo: string) => {
    let s = testo;
    while (s.length > 4 && g.measureText(s).width > largColonna - 16) s = s.slice(0, -2);
    return s === testo ? s : `${s.trimEnd()}…`;
  };
  const yLegenda = y0 + TH + 42;
  const xLegenda = colonne === 1 ? (W - Math.min(largColonna, 760)) / 2 : 90;
  voci.forEach((v, i) => {
    const c = Math.floor(i / righe);
    const r = i % righe;
    g.fillText(tronca(v), xLegenda + c * largColonna, yLegenda + r * 27);
  });
  g.textAlign = "center";

  /* ---- una frase del responso ---- */

  /* L'ultima sezione (`## …`) è la tendenza; il suo titolo lo scrive il modello
   * nella lingua della risposta, quindi non lo si cerca per nome: si prende
   * l'ultima sezione e se ne toglie la prima riga, il titolo. */
  const sezioni = responso.split(/^##\s+/m);
  const tendenza = sezioni.length > 1 ? sezioni[sezioni.length - 1].split("\n").slice(1).join("\n") : responso;
  const frase = tendenza.replace(/[#*]/g, "").trim().split(/(?<=[.!?。！？])\s*/).filter(Boolean).slice(0, 2).join(" ");
  g.fillStyle = "#efe6d2";
  g.font = `italic 400 36px ${oracolo}`;
  avvolgi(frase, W / 2, y0 + TH + 42 + Math.min(righe, 5) * 27 + 46, W - 200, 44, 3);

  g.fillStyle = "rgba(179,168,207,0.8)";
  g.font = `400 22px sans-serif`;
  g.fillText(dizionario(ll).immagine_piede, W / 2, H - 66);

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
  const ll = useLinguaNomi();
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
    const blob = await disegnaImmagine(domanda, stesa, posate, testo, ll);
    if (!blob) return;
    const file = new File([blob], "lettura-tarots.png", { type: "image/png" });
    /* Il foglio di condivisione solo sul telefono (puntatore «grossolano»): sul
     * computer, Edge e Chrome dichiarano di saper condividere file e «Scarica»
     * aprirebbe la condivisione di Windows invece di salvare l'immagine. */
    if (window.matchMedia("(pointer: coarse)").matches && navigator.canShare?.({ files: [file] })) {
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
