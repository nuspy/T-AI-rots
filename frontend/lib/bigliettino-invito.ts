/* Il bigliettino d'invito, composto nel browser: un'immagine da salvare e condividere sui social.
 *
 * A differenza dell'immagine di una lettura condivisa (`app/leggi/immagine-condivisione.ts`, di cui riusa i
 * pezzi: sfondo, cornice, marchio, testo a capo), qui il contenuto è **statico per utente** — logo, palette,
 * codice d'invito, un claim breve — e non serve nessun server: si scarica direttamente il PNG che il browser ha
 * disegnato (`canvas.toBlob`), senza il giro per la riduzione a WebP che le letture condivise fanno per il peso
 * di un'anteprima social — qui la misura è già piccola.
 */

import { caratteri, cornice, disegnaMarchio, paragrafo, sfondo, type G } from "./immagine-condivisione";
import { DOMINIO } from "@/lib/condivisione";

export const MISURA_BIGLIETTINO = { w: 1000, h: 700 };

const ORO_CHIARO = "#f1d68e";
const LAVANDA = "#b9a4ff";
const CARTA = "#efe6d2";

/** Compone il bigliettino: PNG 1000×700. `null` se il browser non sa disegnare o non produce il PNG. */
export async function componiBigliettino(
  codice: string, claim: string, omaggio: string, lingua: string,
): Promise<Blob | null> {
  const { w: W, h: H } = MISURA_BIGLIETTINO;
  const tela = document.createElement("canvas");
  tela.width = W;
  tela.height = H;
  const g: G | null = tela.getContext("2d", { alpha: false });
  if (!g) return null;

  const tipo = caratteri();
  try {
    await document.fonts?.ready;
    await Promise.all([
      document.fonts?.load(`700 60px ${tipo.titoli}`),
      document.fonts?.load(`italic 500 30px ${tipo.oracolo}`),
    ]);
  } catch {
    /* si disegna con i caratteri che ci sono */
  }

  sfondo(g, W, H, `invito:${codice}`);
  cornice(g, W, H);

  await disegnaMarchio(g, W / 2 - 90, 64, 96, tipo);

  g.textAlign = "center";
  g.fillStyle = ORO_CHIARO;
  g.font = `italic 500 30px ${tipo.oracolo}`;
  paragrafo(g, claim, W / 2, 240, W - 220, 38, 2, lingua, "center");

  g.fillStyle = LAVANDA;
  g.font = `700 44px ${tipo.titoli}`;
  g.fillText(omaggio, W / 2, 380);

  // Il codice, in evidenza dentro una targa.
  const targaW = 420;
  const targaX = W / 2 - targaW / 2;
  g.strokeStyle = "rgba(216,180,90,0.85)";
  g.lineWidth = 2;
  g.strokeRect(targaX, 440, targaW, 96);
  g.fillStyle = CARTA;
  g.font = `700 48px ${tipo.interfaccia}`;
  g.textAlign = "center";
  g.fillText(codice, W / 2, 500);

  g.fillStyle = ORO_CHIARO;
  g.font = `700 26px ${tipo.titoli}`;
  g.fillText(DOMINIO, W / 2, H - 60);

  return new Promise((ok) => tela.toBlob((b) => ok(b), "image/png"));
}

/** Scarica il blob come file: un collegamento invisibile, cliccato e rimosso subito. */
export function scaricaBlob(blob: Blob, nomeFile: string): void {
  const indirizzo = URL.createObjectURL(blob);
  try {
    const a = document.createElement("a");
    a.href = indirizzo;
    a.download = nomeFile;
    document.body.appendChild(a);
    a.click();
    a.remove();
  } finally {
    setTimeout(() => URL.revokeObjectURL(indirizzo), 0);
  }
}
