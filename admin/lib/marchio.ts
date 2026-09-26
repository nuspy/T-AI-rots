/* Il nome e il logo di TAROTS chat, per la console (un'app a parte: qui solo ciò che serve).
 * Il logo sta in `public/marchio/`, scritto da `tools/prepara_logo.py`; sotto `basePath` (`/admin` in produzione). */

export const NOME_MARCHIO = "TAROTS chat";
export const BASE = process.env.NEXT_PUBLIC_BASE_PATH ?? "";
export const LOGO = { larghezza: 1347, altezza: 1168 } as const;
export const urlLogo = (larghezza: 128 | 256): string => `${BASE}/marchio/logo-${larghezza}.webp`;
