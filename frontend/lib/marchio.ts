/* Il nome e il logo del prodotto, in un posto solo.
 *
 * Il prodotto si chiamava con il suo nome tecnico, T·AI·rots; oggi è **TAROTS chat**. Il logo è l'illustrazione
 * della maga con la carta e la scritta dorata (`Grafica/Logo_02_transp.png`): `tools/prepara_logo.py` ne ripulisce
 * i bordi e ne scrive le versioni in WebP (`public/marchio/logo-<larghezza>.webp`), le icone del browser e
 * l'immagine di anteprima per i social. Cambiare logo vuol dire rifare quelle immagini, non toccare il codice.
 *
 * In un testo semplice — titoli di pagina, metadati, email — il nome si scrive di seguito: «TAROTS chat». */

export const PAROLA = "TAROTS";
export const VOCE = "chat";
export const NOME_MARCHIO = `${PAROLA} ${VOCE}`;

/** Il logo: dov'è, in quali larghezze esiste, e le misure dell'originale (servono a riservare lo spazio). */
export const LOGO = {
  cartella: "/marchio",
  prefisso: "logo",
  larghezze: [128, 192, 256, 384, 512, 768, 1024, 1347],
  larghezza: 1347,
  altezza: 1168,
} as const;

/** L'indirizzo del logo alla larghezza data (una delle `LOGO.larghezze`). */
export const urlLogo = (larghezza: number): string => `${LOGO.cartella}/${LOGO.prefisso}-${larghezza}.webp`;

/** L'attributo `srcSet` con tutte le larghezze fino a `massima`. */
export const srcSetLogo = (massima: number = LOGO.larghezza): string =>
  LOGO.larghezze.filter((l) => l <= massima).map((l) => `${urlLogo(l)} ${l}w`).join(", ");
