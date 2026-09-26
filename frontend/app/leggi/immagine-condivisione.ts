/* L'immagine di una lettura condivisa, composta nel browser.
 *
 * Una sola immagine, 4:3, che serve al post e all'anteprima del link. Il browser la
 * disegna a 800×600 e la manda in PNG (l'unico formato che ogni canvas sa produrre,
 * Safari compreso); il server la ricontrolla e la riduce a un **WebP 400×300 molto
 * compresso** (`tarot/condivisione.prepara_immagine`), poche decine di KB. Il doppio
 * della misura finale rende più nitidi i testi dopo la riduzione.
 *
 * Perché nel browser: è l'unico posto che sa scrivere in tutte le lingue (arabo,
 * cinese, hindi…) con i caratteri già caricati.
 *
 * Cosa contiene: la **stessa stesa** della lettura con le carte davvero uscite
 * **nelle loro posizioni**, ma compatta — il tavolo è ritagliato sulle carte e
 * ingrandito quanto basta —, il quesito, il testo personalizzato, una sintesi del
 * responso e, in fondo, l'indirizzo del sito. Nelle letture speciali il nome
 * dell'altra persona non c'è (lo ha già tolto il server): al suo posto il simbolo
 * del suo genere e la scritta «qualcuno di speciale» nella lingua della lettura.
 *
 * Tutto ciò che si disegna viene da `LetturaCondivisa`, cioè da ciò che il server
 * mostra a chiunque: l'immagine non può dire più della pagina pubblica. */

import type { LetturaCondivisa, Stesa } from "@/lib/api";
import { DOMINIO } from "@/lib/condivisione";
import {
  CENTRO_STELLA, COLORI, CONTORNO_CARTA, CORNICE, PAROLA, PERCORSO_STELLA, TELA, VOCE,
} from "@/lib/marchio";
import { comeLingua, nomeCarta, nomeStesa, type Lingua } from "@/lib/i18n";
import { sintesiDelResponso } from "@/lib/sintesi";
import { LATO_SIMBOLO, PERCORSI_SIMBOLI, simboloDi } from "@/lib/simboli";
import { ESTENSIONE } from "../componenti/carta";
import { COLORE_SOGGETTO, SCALA_CARTE, larghezzaBase } from "./tavolo";

/* Ciò che si disegna (il doppio di ciò che si pubblica) e ciò che il server salva. */
export const MISURA = { w: 800, h: 600 };
export const MISURA_FINALE = { w: 400, h: 300 };

const ORO = "#d8b45a";
const ORO_CHIARO = "#f1d68e";
const LAVANDA = "#b9a4ff";
const CARTA = "#efe6d2";
const NOTTE = "#07050f";

/* ---- strumenti di disegno ---- */

type G = CanvasRenderingContext2D;

interface Caratteri {
  titoli: string;
  oracolo: string;
  interfaccia: string;
}

function caratteri(): Caratteri {
  const stile = getComputedStyle(document.documentElement);
  return {
    titoli: stile.getPropertyValue("--font-titoli").trim() || "serif",
    oracolo: stile.getPropertyValue("--font-oracolo").trim() || "serif",
    interfaccia: stile.getPropertyValue("--font-ui").trim() || "sans-serif",
  };
}

/* Un generatore pseudo-casuale con seme: la polvere di stelle è la stessa a ogni
 * disegno della stessa lettura, e l'anteprima coincide con l'immagine caricata. */
function generatore(seme: string) {
  let h = 1779033703 ^ seme.length;
  for (let i = 0; i < seme.length; i++) {
    h = Math.imul(h ^ seme.charCodeAt(i), 3432918353);
    h = (h << 13) | (h >>> 19);
  }
  let a = h >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function caricaImmagine(src: string): Promise<HTMLImageElement | null> {
  return new Promise((ok) => {
    const img = new Image();
    img.onload = () => ok(img);
    img.onerror = () => ok(null);
    img.src = src;
  });
}

function rettangolo(g: G, x: number, y: number, w: number, h: number, r: number) {
  g.beginPath();
  g.moveTo(x + r, y);
  g.arcTo(x + w, y, x + w, y + h, r);
  g.arcTo(x + w, y + h, x, y + h, r);
  g.arcTo(x, y + h, x, y, r);
  g.arcTo(x, y, x + w, y, r);
  g.closePath();
}

/* Una stella a quattro punte, l'ornamento ricorrente. */
function stella(g: G, x: number, y: number, r: number) {
  g.beginPath();
  g.moveTo(x, y - r);
  g.quadraticCurveTo(x, y, x + r, y);
  g.quadraticCurveTo(x, y, x, y + r);
  g.quadraticCurveTo(x, y, x - r, y);
  g.quadraticCurveTo(x, y, x, y - r);
  g.closePath();
  g.fill();
}

/* Il testo a capo. Segmenta per parole con `Intl.Segmenter`, che conosce anche le
 * lingue senza spazi (cinese, giapponese, thai); dove manca si spezza sugli spazi.
 * Una parola più larga della riga si spezza per lettere. */
function segmenti(testo: string, lingua: string): string[] {
  try {
    return Array.from(new Intl.Segmenter(lingua, { granularity: "word" }).segment(testo), (s) => s.segment);
  } catch {
    return testo.split(/(\s+)/).filter(Boolean);
  }
}

function aCapo(g: G, testo: string, larghezza: number, lingua: string, massimo: number): string[] {
  const righe: string[] = [];
  let riga = "";
  const spingi = (parola: string) => {
    const prova = riga + parola;
    if (riga && g.measureText(prova).width > larghezza) {
      righe.push(riga.trimEnd());
      riga = parola.trimStart();
    } else {
      riga = prova;
    }
    while (g.measureText(riga).width > larghezza && riga.length > 1) {
      let taglio = riga.length - 1;
      while (taglio > 1 && g.measureText(riga.slice(0, taglio)).width > larghezza) taglio--;
      righe.push(riga.slice(0, taglio));
      riga = riga.slice(taglio);
    }
  };
  for (const s of segmenti(testo, lingua)) spingi(s);
  if (riga.trim()) righe.push(riga.trimEnd());
  if (righe.length <= massimo) return righe;
  /* Troppo lungo: si tiene l'inizio e si chiude con i puntini. */
  const tenute = righe.slice(0, massimo);
  let ultima = tenute[massimo - 1];
  while (ultima.length > 1 && g.measureText(`${ultima}…`).width > larghezza) ultima = ultima.slice(0, -1);
  tenute[massimo - 1] = `${ultima.trimEnd()}…`;
  return tenute;
}

/* Scrive un testo a capo centrato in `x` (o a sinistra di `x`); restituisce la
 * quota sotto l'ultima riga. */
function paragrafo(
  g: G, testo: string, x: number, y: number, larghezza: number, riga: number, massimo: number,
  lingua: string, allinea: "center" | "left" = "center",
): number {
  if (!testo) return y;
  g.textAlign = allinea;
  const righe = aCapo(g, testo, larghezza, lingua, massimo);
  righe.forEach((r, i) => g.fillText(r, x, y + i * riga));
  return y + righe.length * riga;
}

/* ---- il tavolo compatto ---- */

interface Scatola {
  x: number;
  y: number;
  w: number;
  h: number;
}

/* Il tavolo della stesa con le carte uscite, ritagliato sulle carte e scalato per
 * entrare in `scatola`. Le posizioni relative sono quelle della stesa: cambia solo
 * lo spazio vuoto intorno, non la distanza fra le carte. */
async function disegnaTavolo(
  g: G, stesa: Stesa, carte: LetturaCondivisa["cards"], scatola: Scatola, cartaMax: number, tipo: Caratteri, ll: Lingua,
) {
  const posate = carte.filter((c) => c.carta);
  const immagini = new Map(
    await Promise.all(
      posate.map(async (c) => [c.posizione, await caricaImmagine(`/cards/${c.carta!.id}.${ESTENSIONE}`)] as const),
    ),
  );

  const quadrato = stesa.forma === "quadrata";
  const TH = 600;
  const TW = quadrato ? TH : (TH * 16) / 12;
  const lc = TW * larghezzaBase(stesa) * SCALA_CARTE;
  const ac = (lc * 16) / 9;

  /* Il rettangolo che contiene tutte le carte (col loro giro), più il margine per il numero. */
  const MARGINE = 20;
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  for (const c of posate) {
    const pos = stesa.posizioni.find((q) => q.n === c.posizione);
    if (!pos) continue;
    const a = (pos.rotazione * Math.PI) / 180;
    const mx = (Math.abs(Math.cos(a)) * lc + Math.abs(Math.sin(a)) * ac) / 2;
    const my = (Math.abs(Math.sin(a)) * lc + Math.abs(Math.cos(a)) * ac) / 2;
    minX = Math.min(minX, pos.x * TW - mx);
    maxX = Math.max(maxX, pos.x * TW + mx);
    minY = Math.min(minY, pos.y * TH - my);
    maxY = Math.max(maxY, pos.y * TH + my);
  }
  if (!isFinite(minX)) return;
  minX -= MARGINE; maxX += MARGINE; minY -= MARGINE; maxY += MARGINE;

  const s = Math.min(scatola.w / (maxX - minX), scatola.h / (maxY - minY), cartaMax / lc);
  const ox = scatola.x + (scatola.w - (maxX - minX) * s) / 2 - minX * s;
  const oy = scatola.y + (scatola.h - (maxY - minY) * s) / 2 - minY * s;

  /* L'alone dietro il tavolo. */
  const cx = scatola.x + scatola.w / 2;
  const cy = scatola.y + scatola.h / 2;
  const alone = g.createRadialGradient(cx, cy, 10, cx, cy, Math.max(scatola.w, scatola.h) * 0.62);
  alone.addColorStop(0, "rgba(96,64,190,0.55)");
  alone.addColorStop(0.6, "rgba(50,30,110,0.22)");
  alone.addColorStop(1, "rgba(7,5,15,0)");
  g.fillStyle = alone;
  g.fillRect(scatola.x - 40, scatola.y - 40, scatola.w + 80, scatola.h + 80);

  const LC = lc * s;
  const AC = ac * s;
  for (const c of posate) {
    const pos = stesa.posizioni.find((q) => q.n === c.posizione);
    if (!pos) continue;
    const px = ox + pos.x * TW * s;
    const py = oy + pos.y * TH * s;
    const giro = ((pos.rotazione + (c.rovescio ? 180 : 0)) * Math.PI) / 180;
    const colore = pos.soggetto ? COLORE_SOGGETTO[pos.soggetto] : ORO;
    const img = immagini.get(c.posizione);

    g.save();
    g.translate(px, py);
    g.rotate(giro);
    g.shadowColor = "rgba(0,0,0,0.7)";
    g.shadowBlur = 18;
    g.shadowOffsetY = 7;
    g.fillStyle = "#171129";
    rettangolo(g, -LC / 2, -AC / 2, LC, AC, LC * 0.06);
    g.fill();
    g.shadowColor = "transparent";
    g.save();
    rettangolo(g, -LC / 2, -AC / 2, LC, AC, LC * 0.06);
    g.clip();
    if (img) {
      g.drawImage(img, -LC / 2, -AC / 2, LC, AC);
    } else {
      g.fillStyle = CARTA;
      g.font = `400 ${Math.max(13, LC * 0.13)}px ${tipo.titoli}`;
      g.textAlign = "center";
      const righe = aCapo(g, nomeCarta(c.carta!, ll), LC - 12, ll, 3);
      righe.forEach((r, i) => g.fillText(r, 0, (i - (righe.length - 1) / 2) * LC * 0.16));
    }
    g.restore();
    /* Il contorno col colore di chi parla la posizione (oro nelle letture normali). */
    g.strokeStyle = colore;
    g.globalAlpha = 0.9;
    g.lineWidth = Math.max(2, LC * 0.02);
    rettangolo(g, -LC / 2, -AC / 2, LC, AC, LC * 0.06);
    g.stroke();
    g.globalAlpha = 1;
    g.restore();

    /* Il numero della posizione sul primo angolo, come lo vede la stesa. */
    const teta = (pos.rotazione * Math.PI) / 180;
    const dx = -LC / 2;
    const dy = -AC / 2;
    const bx = px + dx * Math.cos(teta) - dy * Math.sin(teta);
    const by = py + dx * Math.sin(teta) + dy * Math.cos(teta);
    const r = Math.max(11, Math.min(17, LC * 0.14));
    g.fillStyle = colore;
    g.beginPath();
    g.arc(bx, by, r, 0, Math.PI * 2);
    g.fill();
    g.fillStyle = "#1a1030";
    g.font = `700 ${Math.round(r * 1.15)}px ${tipo.titoli}`;
    g.textAlign = "center";
    g.textBaseline = "middle";
    g.fillText(String(c.posizione), bx, by + 1);
    g.textBaseline = "alphabetic";
  }
}

/* ---- il simbolo dell'altra persona ---- */

/* Il marchio sul canvas: la carta col fumetto e la stella di Babalon, poi TAROTS in oro e *chat* in lavanda.
 * Stessa geometria del componente (`lib/marchio.ts`); qui a tratti pieni, perché sull'immagine a 800 px il
 * segno è grande abbastanza. `y` è il bordo alto del segno. */
function disegnaMarchio(g: G, x: number, y: number, altezza: number, tipo: Caratteri) {
  const k = altezza / TELA.altezza;
  g.save();
  g.translate(x, y);
  g.scale(k, k);
  const carta = new Path2D(CONTORNO_CARTA);
  const notte = g.createLinearGradient(0, 0, 0, TELA.altezza);
  notte.addColorStop(0, COLORI.notteAlta);
  notte.addColorStop(1, COLORI.notte);
  g.fillStyle = notte;
  g.fill(carta);
  const oro = g.createLinearGradient(0, 0, TELA.larghezza, TELA.altezza);
  oro.addColorStop(0, COLORI.oroChiaro);
  oro.addColorStop(0.5, COLORI.oro);
  oro.addColorStop(1, COLORI.oroScuro);
  g.strokeStyle = oro;
  g.lineJoin = "round";
  g.lineWidth = 2.2;
  g.stroke(carta);
  g.lineWidth = 0.7;
  g.globalAlpha = 0.5;
  g.beginPath();
  g.roundRect(CORNICE.x, CORNICE.y, CORNICE.larghezza, CORNICE.altezza, CORNICE.raggio);
  g.stroke();
  g.globalAlpha = 1;
  g.lineWidth = 1.7;
  g.stroke(new Path2D(PERCORSO_STELLA));
  g.fillStyle = oro;
  g.beginPath();
  g.arc(CENTRO_STELLA.x, CENTRO_STELLA.y, 2.3, 0, Math.PI * 2);
  g.fill();
  g.restore();

  const xTesto = x + TELA.larghezza * k + 16;
  const base = y + altezza * 0.62;
  g.textAlign = "left";
  g.fillStyle = ORO_CHIARO;
  g.font = `700 34px ${tipo.titoli}`;
  const spaziatura = (g as unknown as { letterSpacing?: string });
  const prima = spaziatura.letterSpacing;
  spaziatura.letterSpacing = "5px";
  g.fillText(PAROLA, xTesto, base);
  const larghezzaParola = g.measureText(PAROLA).width;
  spaziatura.letterSpacing = prima ?? "0px";
  g.fillStyle = LAVANDA;
  g.font = `italic 500 30px ${tipo.oracolo}`;
  g.fillText(VOCE, xTesto + larghezzaParola + 8, base);
}

function disegnaSimbolo(g: G, nome: string | null, cx: number, cy: number, lato: number) {
  const simbolo = simboloDi(nome);
  const k = lato / LATO_SIMBOLO;
  g.save();
  g.translate(cx - lato / 2, cy - lato / 2);
  g.scale(k, k);
  g.strokeStyle = ORO_CHIARO;
  g.fillStyle = "rgba(241,214,142,0.16)";
  g.lineWidth = 3.2;
  g.lineCap = "round";
  g.lineJoin = "round";
  g.shadowColor = "rgba(216,180,90,0.75)";
  g.shadowBlur = 14;
  const percorso = new Path2D(PERCORSI_SIMBOLI[simbolo]);
  if (simbolo === "stella") g.fill(percorso);
  g.stroke(percorso);
  g.restore();
}

/* ---- il disegno ---- */

function sfondo(g: G, w: number, h: number, seme: string) {
  const fondo = g.createRadialGradient(w / 2, h * 0.38, 40, w / 2, h * 0.5, Math.max(w, h) * 0.8);
  fondo.addColorStop(0, "#2c1f5c");
  fondo.addColorStop(1, NOTTE);
  g.fillStyle = fondo;
  g.fillRect(0, 0, w, h);
  const casuale = generatore(seme);
  const stelle = Math.round((w * h) / 9000);
  for (let i = 0; i < stelle; i++) {
    g.fillStyle = `rgba(241,214,142,${0.15 + casuale() * 0.5})`;
    g.fillRect(Math.floor(casuale() * w), Math.floor(casuale() * h), 2, 2);
  }
}

function cornice(g: G, w: number, h: number) {
  const m = Math.round(Math.min(w, h) * 0.027);
  g.strokeStyle = "rgba(216,180,90,0.85)";
  g.lineWidth = Math.max(2, m / 9);
  g.strokeRect(m, m, w - 2 * m, h - 2 * m);
  g.strokeStyle = "rgba(216,180,90,0.32)";
  g.lineWidth = 1;
  g.strokeRect(m * 1.5, m * 1.5, w - 3 * m, h - 3 * m);
  g.fillStyle = ORO_CHIARO;
  for (const [x, y] of [[m, m], [w - m, m], [m, h - m], [w - m, h - m]]) stella(g, x, y, m * 0.55);
}

/** Compone l'immagine di una lettura condivisa: PNG 800×600. `null` se il browser
 *  non sa disegnare o non produce il PNG. A sinistra il tavolo con le carte, a destra
 *  marchio, testo personalizzato, quesito, sintesi e, in basso, l'indirizzo del sito. */
export async function componiImmagine(l: LetturaCondivisa): Promise<Blob | null> {
  if (!l.stesa) return null;
  const { w: W, h: H } = MISURA;
  const tela = document.createElement("canvas");
  tela.width = W;
  tela.height = H;
  const g = tela.getContext("2d", { alpha: false });
  if (!g) return null;

  const tipo = caratteri();
  const ll: Lingua = comeLingua(l.lang) ?? "it";
  const lingua = l.lang || "it";
  try {
    await document.fonts?.ready;
    await Promise.all([
      document.fonts?.load(`700 40px ${tipo.titoli}`),
      document.fonts?.load(`italic 500 30px ${tipo.oracolo}`),
    ]);
  } catch {
    /* si disegna con i caratteri che ci sono */
  }
  g.direction = ll === "ar" ? "rtl" : "ltr";

  sfondo(g, W, H, `${l.stesa.id}:${l.question}`);
  cornice(g, W, H);

  const testo = l.share_text ?? "";
  const colX = 500;
  const colW = W - colX - 36;

  await disegnaTavolo(g, l.stesa, l.cards, { x: 36, y: 40, w: 440, h: H - 80 }, 130, tipo, ll);

  g.textAlign = "left";
  disegnaMarchio(g, colX, 34, 62, tipo);
  g.fillStyle = LAVANDA;
  g.font = `400 15px ${tipo.titoli}`;
  g.fillText(nomeStesa(l.stesa, ll).toUpperCase(), colX, 108);

  let y = 142;
  if (testo) {
    g.fillStyle = ORO_CHIARO;
    g.font = `italic 600 22px ${tipo.oracolo}`;
    y = paragrafo(g, testo, colX, y, colW, 27, 2, lingua, "left") + 8;
  }
  /* L'altra persona, nelle letture speciali: il simbolo e «qualcuno di speciale». */
  if (l.speciale) {
    disegnaSimbolo(g, l.partner_simbolo, colX + 16, y + 10, 30);
    g.fillStyle = LAVANDA;
    g.font = `italic 500 18px ${tipo.oracolo}`;
    g.textAlign = "left";
    g.fillText(l.partner_frase ?? "", colX + 40, y + 16);
    y += 40;
  }
  g.fillStyle = CARTA;
  g.font = `italic 500 22px ${tipo.oracolo}`;
  y = paragrafo(g, `«${l.question}»`, colX, y + 10, colW, 27, 3, lingua, "left") + 12;
  g.fillStyle = "rgba(239,230,210,0.9)";
  g.font = `italic 400 20px ${tipo.oracolo}`;
  const righe = Math.max(2, Math.min(5, Math.floor((H - 96 - y) / 25)));
  paragrafo(g, sintesiDelResponso(l.synthesis, 150), colX, y + 6, colW, 25, righe, lingua, "left");

  /* Il sito, sull'immagine. */
  g.textAlign = "left";
  g.fillStyle = ORO_CHIARO;
  g.font = `700 32px ${tipo.titoli}`;
  g.fillText(DOMINIO, colX, H - 50);

  return new Promise((ok) => tela.toBlob((b) => ok(b), "image/png"));
}
