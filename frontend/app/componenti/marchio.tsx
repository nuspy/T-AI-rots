import { LOGO, NOME_MARCHIO, srcSetLogo, urlLogo } from "@/lib/marchio";
import stili from "./marchio.module.css";

/* Il logo di TAROTS chat: la maga con la carta e la scritta dorata.
 *
 * Un'immagine, non un disegno in codice: si serve in più larghezze (`srcset`) e il browser sceglie la più piccola
 * che basti allo schermo — a 52 px di altezza in testata pesa ~20 KB, a tutta soglia ~200 KB. Le misure
 * dell'originale stanno negli attributi `width` e `height`, così la pagina riserva lo spazio prima che l'immagine
 * arrivi e non salta.
 *
 * Due disposizioni. `riga` è la testata: piccola, a sinistra, un collegamento. `blocco` è la soglia: grande, con un
 * solo ingresso morbido (scompare con `prefers-reduced-motion`). Il logo è già il nome: l'unico testo alternativo è
 * «TAROTS chat». Si scrive anche dal server. */

export function Marchio({
  variante = "riga", priorita = false,
}: {
  variante?: "riga" | "blocco";
  /** Vero per il logo che si vede subito (la testata, la soglia): il browser lo scarica per primo. */
  priorita?: boolean;
}) {
  const grande = variante === "blocco";
  return (
    // eslint-disable-next-line @next/next/no-img-element -- il logo ha già le sue larghezze in WebP (`srcset`)
    <img
      className={grande ? stili.blocco : stili.riga}
      src={urlLogo(grande ? 768 : 256)}
      srcSet={srcSetLogo()}
      sizes={grande ? "(max-width: 860px) 88vw, 540px" : "(max-width: 860px) 52px, 62px"}
      width={LOGO.larghezza}
      height={LOGO.altezza}
      alt={NOME_MARCHIO}
      decoding="async"
      fetchPriority={priorita ? "high" : "auto"}
      loading={priorita ? "eager" : "lazy"}
      draggable={false}
    />
  );
}
