"use client";

/* La condivisione di un articolo: collegamenti per Facebook, X, WhatsApp, email e «copia il link».
 * Nessun tracciamento e niente salvato: il collegamento è quello pubblico dell'articolo. */

import { useState } from "react";
import { useLingua } from "@/lib/lingua";
import stili from "../blog.module.css";

export function CondividiArticolo({ url, titolo }: { url: string; titolo: string }) {
  const { t } = useLingua();
  const [copiato, setCopiato] = useState(false);
  const c = encodeURIComponent;
  const canali = [
    ["Facebook", `https://www.facebook.com/sharer/sharer.php?u=${c(url)}`],
    ["X", `https://x.com/intent/post?text=${c(titolo)}&url=${c(url)}`],
    ["WhatsApp", `https://wa.me/?text=${c(`${titolo} ${url}`)}`],
    ["Email", `mailto:?subject=${c(titolo)}&body=${c(url)}`],
  ] as const;

  const copia = async () => {
    try {
      await navigator.clipboard?.writeText(url);
      setCopiato(true);
      window.setTimeout(() => setCopiato(false), 2500);
    } catch {
      /* appunti non disponibili: il collegamento resta nella barra degli indirizzi */
    }
  };

  return (
    <section className={stili.blocco} aria-label={t.blog_condividi}>
      <h2>{t.blog_condividi}</h2>
      <div className={stili.condividi}>
        {canali.map(([nome, href]) => (
          <a key={nome} href={href} target={nome === "Email" ? undefined : "_blank"} rel="noopener noreferrer">{nome}</a>
        ))}
        <button onClick={copia}>{copiato ? t.blog_link_copiato : t.blog_copia_link}</button>
      </div>
      <span role="status" className="solo-lettori-di-schermo" style={{ position: "absolute", left: -9999 }}>
        {copiato ? t.blog_link_copiato : ""}
      </span>
    </section>
  );
}
