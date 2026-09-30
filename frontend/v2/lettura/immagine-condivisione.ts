/* L'immagine di una lettura condivisa e il bigliettino d'invito, nello stile della v2 (v8.5).
 *
 * Stesso contratto dell'immagine del sito (`app/(sito)/leggi/immagine-condivisione.ts`): 800×600 disegnati nel
 * browser, mandati in PNG, ridotti dal server a un WebP 400×300; solo ciò che la pagina pubblica mostra già. Cambia
 * il linguaggio visivo: il prugna della v2 al posto del cielo notturno, il motivo ad anello del tavolo del rito dietro
 * le carte, la cornice chiara delle carte v2, l'ottone per i numeri e l'indirizzo, Libre Baskerville e DM Sans. E le
 * carte sono quelle del mazzo della lettura, non sempre del Thoth.
 *
 * Il sito (v1, sotto `/old`) continua a usare il suo generatore. */

import type { LetturaCondivisa, Stesa } from "@/lib/api";
import { DOMINIO } from "@/lib/condivisione";
import { comeLingua, nomeCarta, nomeStesa, type Lingua } from "@/lib/i18n";
import { percorsoCarta } from "@/lib/mazzo-attivo";
import { LATO_SIMBOLO, PERCORSI_SIMBOLI, simboloDi } from "@/lib/simboli";
import { sintesiDelResponso } from "@/lib/sintesi";
import { paragrafo, type G } from "@/lib/immagine-condivisione";
import { SCALA_CARTE, larghezzaBase } from "@/lib/geometria-tavolo";

export const MISURA = { w: 800, h: 600 };
export const MISURA_FINALE = { w: 400, h: 300 };
export const MISURA_BIGLIETTINO = { w: 1000, h: 700 };

/* La tavolozza della v2 (app/(v2)/v2/v2.css). */
const PRUGNA = "#3c1846";
const PRUGNA_SCURO = "#201026";
const OTTONE = "#b28336";
const OTTONE_CHIARO = "#d6b66d";
const CARTA = "#f4efe5";
const CORNICE_CARTA = "#f5e6bf";
const TENUE = "#d9cade";
const ESTENSIONE = process.env.NEXT_PUBLIC_CARD_EXT ?? "webp";

interface Caratteri { serif: string; sans: string }

function caratteri(): Caratteri {
  const stile = getComputedStyle(document.documentElement);
  const corpo = getComputedStyle(document.body);
  const prendi = (nome: string) => stile.getPropertyValue(nome).trim() || corpo.getPropertyValue(nome).trim();
  return {
    serif: prendi("--font-v2-serif") ? `${prendi("--font-v2-serif")}, "Libre Baskerville", Georgia, serif` : `"Libre Baskerville", Georgia, serif`,
    sans: prendi("--font-v2-sans") ? `${prendi("--font-v2-sans")}, "DM Sans", Arial, sans-serif` : `"DM Sans", Arial, sans-serif`,
  };
}

async function caratteriPronti(tipo: Caratteri) {
  try {
    await document.fonts?.ready;
    await Promise.all([
      document.fonts?.load(`400 30px ${tipo.serif}`),
      document.fonts?.load(`italic 400 24px ${tipo.serif}`),
      document.fonts?.load(`600 16px ${tipo.sans}`),
    ]);
  } catch {
    /* si disegna con i caratteri che ci sono */
  }
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

/* Il fondo prugna, più chiaro al centro, e la cornice d'ottone sottile. */
function fondo(g: G, w: number, h: number) {
  const f = g.createRadialGradient(w * 0.34, h * 0.5, 30, w * 0.5, h * 0.5, Math.max(w, h) * 0.75);
  f.addColorStop(0, "#572064");
  f.addColorStop(0.55, PRUGNA);
  f.addColorStop(1, PRUGNA_SCURO);
  g.fillStyle = f;
  g.fillRect(0, 0, w, h);
  const m = Math.round(Math.min(w, h) * 0.035);
  g.strokeStyle = "rgba(214,182,109,.75)";
  g.lineWidth = 1.5;
  g.strokeRect(m, m, w - 2 * m, h - 2 * m);
}

/* Il motivo ad anello del tavolo del rito: cerchi concentrici d'ottone, appena accennati. */
function anelli(g: G, cx: number, cy: number, raggio: number) {
  g.save();
  for (let i = 0; i < 5; i++) {
    g.strokeStyle = `rgba(214,182,109,${0.22 - i * 0.035})`;
    g.lineWidth = i === 0 ? 1.6 : 1;
    g.beginPath();
    g.arc(cx, cy, raggio * (0.42 + i * 0.16), 0, Math.PI * 2);
    g.stroke();
  }
  g.restore();
}

interface Scatola { x: number; y: number; w: number; h: number }

/* Le carte uscite nelle loro posizioni, ritagliate sul loro ingombro (come nel sito), con la cornice chiara v2. */
async function tavolo(
  g: G, stesa: Stesa, carte: LetturaCondivisa["cards"], scatola: Scatola, cartaMax: number, tipo: Caratteri, ll: Lingua,
  mazzo: string | null,
) {
  const posate = carte.filter((c) => c.carta);
  const immagini = new Map(await Promise.all(
    posate.map(async (c) => [c.posizione, await caricaImmagine(percorsoCarta(mazzo, `${c.carta!.id}.${ESTENSIONE}`))] as const),
  ));
  const quadrato = stesa.forma === "quadrata";
  const TH = 600;
  const TW = quadrato ? TH : (TH * 16) / 12;
  const lc = TW * larghezzaBase(stesa) * SCALA_CARTE;
  const ac = (lc * 16) / 9;
  const MARGINE = 20;
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  for (const c of posate) {
    const pos = stesa.posizioni.find((q) => q.n === c.posizione);
    if (!pos) continue;
    const a = (pos.rotazione * Math.PI) / 180;
    const mx = (Math.abs(Math.cos(a)) * lc + Math.abs(Math.sin(a)) * ac) / 2;
    const my = (Math.abs(Math.sin(a)) * lc + Math.abs(Math.cos(a)) * ac) / 2;
    minX = Math.min(minX, pos.x * TW - mx); maxX = Math.max(maxX, pos.x * TW + mx);
    minY = Math.min(minY, pos.y * TH - my); maxY = Math.max(maxY, pos.y * TH + my);
  }
  if (!isFinite(minX)) return;
  minX -= MARGINE; maxX += MARGINE; minY -= MARGINE; maxY += MARGINE;
  const s = Math.min(scatola.w / (maxX - minX), scatola.h / (maxY - minY), cartaMax / lc);
  const ox = scatola.x + (scatola.w - (maxX - minX) * s) / 2 - minX * s;
  const oy = scatola.y + (scatola.h - (maxY - minY) * s) / 2 - minY * s;

  anelli(g, scatola.x + scatola.w / 2, scatola.y + scatola.h / 2, Math.min(scatola.w, scatola.h) * 0.62);

  const LC = lc * s;
  const AC = ac * s;
  const bordo = Math.max(3, LC * 0.035);
  for (const c of posate) {
    const pos = stesa.posizioni.find((q) => q.n === c.posizione);
    if (!pos) continue;
    const px = ox + pos.x * TW * s;
    const py = oy + pos.y * TH * s;
    const giro = ((pos.rotazione + (c.rovescio ? 180 : 0)) * Math.PI) / 180;
    const img = immagini.get(c.posizione);
    g.save();
    g.translate(px, py);
    g.rotate(giro);
    g.shadowColor = "rgba(20,8,26,.55)";
    g.shadowBlur = 16;
    g.shadowOffsetY = 8;
    g.fillStyle = CORNICE_CARTA;
    rettangolo(g, -LC / 2, -AC / 2, LC, AC, LC * 0.05);
    g.fill();
    g.shadowColor = "transparent";
    g.save();
    rettangolo(g, -LC / 2 + bordo, -AC / 2 + bordo, LC - 2 * bordo, AC - 2 * bordo, LC * 0.035);
    g.clip();
    if (img) g.drawImage(img, -LC / 2 + bordo, -AC / 2 + bordo, LC - 2 * bordo, AC - 2 * bordo);
    else {
      g.fillStyle = PRUGNA;
      g.fillRect(-LC / 2, -AC / 2, LC, AC);
      g.fillStyle = CARTA;
      g.font = `400 ${Math.max(12, LC * 0.12)}px ${tipo.serif}`;
      g.textAlign = "center";
      g.fillText(nomeCarta(c.carta!, ll), 0, 0, LC - 12);
    }
    g.restore();
    g.restore();

    /* Il numero della posizione, sull'angolo in alto a sinistra come nella stesa. */
    const teta = (pos.rotazione * Math.PI) / 180;
    const bx = px + (-LC / 2) * Math.cos(teta) - (-AC / 2) * Math.sin(teta);
    const by = py + (-LC / 2) * Math.sin(teta) + (-AC / 2) * Math.cos(teta);
    const r = Math.max(11, Math.min(16, LC * 0.13));
    g.fillStyle = OTTONE;
    g.beginPath();
    g.arc(bx, by, r, 0, Math.PI * 2);
    g.fill();
    g.fillStyle = PRUGNA_SCURO;
    g.font = `700 ${Math.round(r * 1.05)}px ${tipo.sans}`;
    g.textAlign = "center";
    g.textBaseline = "middle";
    g.fillText(String(c.posizione), bx, by + 1);
    g.textBaseline = "alphabetic";
  }
}

/* Il marchio della v2: il segno ✦ nella sua losanga, «TAROTS» e «chat» in corsivo d'ottone. */
function marchio(g: G, x: number, y: number, dimensione: number, tipo: Caratteri, allinea: "left" | "center" = "left") {
  g.save();
  g.font = `400 ${dimensione}px ${tipo.serif}`;
  const tarots = "TAROTS ";
  g.font = `400 ${dimensione}px ${tipo.serif}`;
  const w1 = g.measureText(tarots).width;
  g.font = `italic 400 ${dimensione}px ${tipo.serif}`;
  const w2 = g.measureText("chat").width;
  const segno = dimensione * 1.1;
  const totale = segno + dimensione * 0.5 + w1 + w2;
  const x0 = allinea === "center" ? x - totale / 2 : x;
  /* La losanga del segno. */
  const cy = y - dimensione * 0.35;
  g.strokeStyle = OTTONE_CHIARO;
  g.lineWidth = 1.4;
  g.beginPath();
  const hx = segno * 0.42, hy = segno * 0.55;
  g.moveTo(x0 + segno / 2, cy - hy);
  g.lineTo(x0 + segno / 2 + hx, cy - hy * 0.64);
  g.lineTo(x0 + segno / 2 + hx, cy + hy * 0.64);
  g.lineTo(x0 + segno / 2, cy + hy);
  g.lineTo(x0 + segno / 2 - hx, cy + hy * 0.64);
  g.lineTo(x0 + segno / 2 - hx, cy - hy * 0.64);
  g.closePath();
  g.stroke();
  g.fillStyle = OTTONE_CHIARO;
  g.font = `400 ${dimensione * 0.62}px ${tipo.serif}`;
  g.textAlign = "center";
  g.textBaseline = "middle";
  g.fillText("✦", x0 + segno / 2, cy + 1);
  g.textBaseline = "alphabetic";
  g.textAlign = "left";
  g.fillStyle = CARTA;
  g.font = `400 ${dimensione}px ${tipo.serif}`;
  g.fillText(tarots, x0 + segno + dimensione * 0.5, y);
  g.fillStyle = OTTONE_CHIARO;
  g.font = `italic 400 ${dimensione}px ${tipo.serif}`;
  g.fillText("chat", x0 + segno + dimensione * 0.5 + w1, y);
  g.restore();
}

function simbolo(g: G, nome: string | null, cx: number, cy: number, lato: number) {
  const k = lato / LATO_SIMBOLO;
  const quale = simboloDi(nome);
  g.save();
  g.translate(cx - lato / 2, cy - lato / 2);
  g.scale(k, k);
  g.strokeStyle = OTTONE_CHIARO;
  g.fillStyle = "rgba(214,182,109,.16)";
  g.lineWidth = 3;
  g.lineCap = "round";
  g.lineJoin = "round";
  const percorso = new Path2D(PERCORSI_SIMBOLI[quale]);
  if (quale === "stella") g.fill(percorso);
  g.stroke(percorso);
  g.restore();
}

/** L'immagine della lettura condivisa: PNG 800×600, o `null` se il browser non sa disegnarla. */
export async function componiImmagineV2(l: LetturaCondivisa): Promise<Blob | null> {
  if (!l.stesa) return null;
  const { w: W, h: H } = MISURA;
  const tela = document.createElement("canvas");
  tela.width = W;
  tela.height = H;
  const g = tela.getContext("2d", { alpha: false });
  if (!g) return null;
  const tipo = caratteri();
  await caratteriPronti(tipo);
  const ll: Lingua = comeLingua(l.lang) ?? "it";
  const lingua = l.lang || "it";
  g.direction = ll === "ar" ? "rtl" : "ltr";

  fondo(g, W, H);
  await tavolo(g, l.stesa, l.cards, { x: 40, y: 44, w: 430, h: H - 88 }, 128, tipo, ll, l.mazzo ?? null);

  const colX = 500;
  const colW = W - colX - 44;
  marchio(g, colX, 78, 26, tipo);

  g.fillStyle = OTTONE_CHIARO;
  g.font = `600 12px ${tipo.sans}`;
  g.textAlign = "left";
  g.fillText(nomeStesa(l.stesa, ll).toUpperCase().split("").join(String.fromCharCode(8202)), colX, 122);

  let y = 158;
  const testo = l.share_text ?? "";
  if (testo) {
    g.fillStyle = CARTA;
    g.font = `italic 400 22px ${tipo.serif}`;
    y = paragrafo(g, testo, colX, y, colW, 29, 2, lingua, "left") + 8;
  }
  if (l.speciale) {
    simbolo(g, l.partner_simbolo, colX + 14, y + 8, 26);
    g.fillStyle = TENUE;
    g.font = `italic 400 17px ${tipo.serif}`;
    g.textAlign = "left";
    g.fillText(l.partner_frase ?? "", colX + 36, y + 14);
    y += 36;
  }
  g.fillStyle = OTTONE_CHIARO;
  g.fillRect(colX, y + 6, 36, 2);
  g.fillStyle = CARTA;
  g.font = `400 20px ${tipo.serif}`;
  y = paragrafo(g, `«${l.question}»`, colX, y + 36, colW, 27, 3, lingua, "left") + 10;
  g.fillStyle = TENUE;
  g.font = `400 16px ${tipo.sans}`;
  const righe = Math.max(2, Math.min(6, Math.floor((H - 104 - y) / 23)));
  paragrafo(g, sintesiDelResponso(l.synthesis, 160), colX, y + 6, colW, 23, righe, lingua, "left");

  g.textAlign = "left";
  g.fillStyle = OTTONE_CHIARO;
  g.font = `600 20px ${tipo.sans}`;
  g.fillText(DOMINIO, colX, H - 56);
  return new Promise((ok) => tela.toBlob((b) => ok(b), "image/png"));
}

/** Il bigliettino d'invito: PNG 1000×700 da scaricare. */
export async function componiBigliettinoV2(codice: string, claim: string, omaggio: string, lingua: string): Promise<Blob | null> {
  const { w: W, h: H } = MISURA_BIGLIETTINO;
  const tela = document.createElement("canvas");
  tela.width = W;
  tela.height = H;
  const g = tela.getContext("2d", { alpha: false });
  if (!g) return null;
  const tipo = caratteri();
  await caratteriPronti(tipo);
  fondo(g, W, H);
  anelli(g, W / 2, H / 2, H * 0.62);
  marchio(g, W / 2, 132, 40, tipo, "center");

  g.textAlign = "center";
  g.fillStyle = CARTA;
  g.font = `italic 400 32px ${tipo.serif}`;
  paragrafo(g, claim, W / 2, 250, W - 240, 42, 2, lingua, "center");
  g.fillStyle = OTTONE_CHIARO;
  g.font = `600 30px ${tipo.sans}`;
  g.fillText(omaggio, W / 2, 380);

  const tw = 440;
  g.fillStyle = CARTA;
  rettangolo(g, W / 2 - tw / 2, 430, tw, 104, 4);
  g.fill();
  g.strokeStyle = OTTONE;
  g.lineWidth = 3;
  rettangolo(g, W / 2 - tw / 2, 430, tw, 104, 4);
  g.stroke();
  g.fillStyle = PRUGNA;
  g.font = `700 50px ${tipo.sans}`;
  g.fillText(codice, W / 2, 500);

  g.fillStyle = OTTONE_CHIARO;
  g.font = `600 24px ${tipo.sans}`;
  g.fillText(DOMINIO, W / 2, H - 64);
  return new Promise((ok) => tela.toBlob((b) => ok(b), "image/png"));
}
