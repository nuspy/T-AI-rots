"use client";

/* Nome e descrizione nelle lingue del sito (v8.5), per un piano o un mazzo. Sul sito si mostra la lingua della
 * pagina, poi l'inglese, poi il nome originale: una lingua lasciata vuota non è un errore. Chiuso per non occupare
 * la scheda; il riassunto dice quante lingue sono coperte. */

import comuni from "./comuni.module.css";

export const LINGUE_SITO: { codice: string; nome: string }[] = [
  { codice: "en", nome: "Inglese" }, { codice: "it", nome: "Italiano" }, { codice: "hu", nome: "Ungherese" },
  { codice: "ru", nome: "Russo" }, { codice: "uk", nome: "Ucraino" }, { codice: "es", nome: "Spagnolo" },
  { codice: "de", nome: "Tedesco" }, { codice: "fr", nome: "Francese" }, { codice: "pt", nome: "Portoghese" },
  { codice: "ro", nome: "Rumeno" }, { codice: "pl", nome: "Polacco" }, { codice: "zh", nome: "Cinese" },
  { codice: "hi", nome: "Hindi" }, { codice: "ko", nome: "Coreano" }, { codice: "ar", nome: "Arabo" },
];

export type Testi = Record<string, string>;

/** Le traduzioni cambiate rispetto a prima? (Per mandare solo ciò che è cambiato.) */
export function diverse(a: Testi, b: Testi): boolean {
  const pulito = (x: Testi) => JSON.stringify(Object.entries(x).filter(([, v]) => v.trim()).sort());
  return pulito(a) !== pulito(b);
}

export function Traduzioni({
  nomi, descrizioni, onNomi, onDescrizioni, massimoNome = 80, massimoDescrizione = 1000,
}: {
  nomi: Testi;
  descrizioni: Testi;
  onNomi: (t: Testi) => void;
  onDescrizioni: (t: Testi) => void;
  massimoNome?: number;
  massimoDescrizione?: number;
}) {
  const coperte = LINGUE_SITO.filter((l) => (nomi[l.codice] ?? "").trim()).length;
  return (
    <details>
      <summary className={comuni.campoEtichetta} style={{ cursor: "pointer", minHeight: 44, display: "flex", alignItems: "center" }}>
        Traduzioni ({coperte}/{LINGUE_SITO.length} lingue col nome)
      </summary>
      <p className={comuni.campoAiuto}>Una lingua vuota mostra l&apos;inglese, e senza inglese il nome qui sopra.</p>
      <div style={{ display: "grid", gap: ".75rem", gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))" }}>
        {LINGUE_SITO.map((l) => (
          <fieldset key={l.codice} style={{ border: "1px solid var(--linea, #ddd)", borderRadius: 6, padding: ".6rem", margin: 0 }}>
            <legend className={comuni.campoEtichetta}>{l.nome} ({l.codice})</legend>
            <input
              className={comuni.ingresso} aria-label={`Nome in ${l.nome.toLowerCase()}`} placeholder="Nome"
              value={nomi[l.codice] ?? ""} maxLength={massimoNome} dir="auto"
              onChange={(e) => onNomi({ ...nomi, [l.codice]: e.target.value })}
            />
            <textarea
              className={comuni.area} aria-label={`Descrizione in ${l.nome.toLowerCase()}`} placeholder="Descrizione"
              style={{ minHeight: "3.5rem", marginTop: ".4rem", fontFamily: "inherit", width: "100%" }}
              value={descrizioni[l.codice] ?? ""} maxLength={massimoDescrizione} dir="auto"
              onChange={(e) => onDescrizioni({ ...descrizioni, [l.codice]: e.target.value })}
            />
          </fieldset>
        ))}
      </div>
    </details>
  );
}
