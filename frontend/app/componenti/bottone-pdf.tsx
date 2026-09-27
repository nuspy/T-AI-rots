"use client";

/* Il download del PDF di una riga già pagata (v5, Fase B4/B6): richiede il token, quindi un blob
 * invece di un semplice `<a href>` (che non può portare l'intestazione Authorization). Condiviso fra
 * il negozio (subito dopo il pagamento) e "I miei ordini" nel profilo (in qualunque momento dopo). */

import { useState } from "react";
import { scaricaPdfOrdine } from "@/lib/api";
import { useLingua } from "@/lib/lingua";
import { useToken } from "@/lib/usa";

export function BottonePdf({ ordineId, deckId, nome }: { ordineId: string; deckId: number; nome: string }) {
  const { t } = useLingua();
  const token = useToken();
  const [inCorso, setInCorso] = useState(false);
  const [errore, setErrore] = useState<string | null>(null);

  const scarica = async () => {
    setInCorso(true);
    setErrore(null);
    try {
      const blob = await scaricaPdfOrdine(token, ordineId, deckId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${nome || "mazzo"}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch {
      setErrore(t.negozio_pdf_errore);
    } finally {
      setInCorso(false);
    }
  };

  return (
    <div style={{ marginTop: 8 }}>
      <button type="button" className="bottone-secondario" disabled={inCorso} onClick={scarica}>
        {inCorso ? t.negozio_pdf_in_corso : `${t.negozio_scarica_pdf}${nome ? ` — ${nome}` : ""}`}
      </button>
      {errore && <p style={{ color: "var(--rosso)", margin: "4px 0 0" }}>{errore}</p>}
    </div>
  );
}
