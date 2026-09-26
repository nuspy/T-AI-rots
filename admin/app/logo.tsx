import { LOGO, NOME_MARCHIO, urlLogo } from "@/lib/marchio";

/* Il logo di TAROTS chat nella console: piccolo in testata, grande sulla soglia. Il logo è già il nome, ma la
 * console ha il suo titolo accanto («Console»): qui l'immagine è decorativa solo se c'è del testo che la nomina. */
export function Logo({ altezza = 40, decorativo = false }: { altezza?: number; decorativo?: boolean }) {
  return (
    // eslint-disable-next-line @next/next/no-img-element -- immagine piccola e già in WebP
    <img
      src={urlLogo(altezza > 56 ? 256 : 128)}
      width={LOGO.larghezza}
      height={LOGO.altezza}
      alt={decorativo ? "" : NOME_MARCHIO}
      style={{ height: altezza, width: "auto", display: "block", flex: "none" }}
      draggable={false}
    />
  );
}
