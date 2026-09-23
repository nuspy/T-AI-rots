/* Il responso arriva in un Markdown minimo — titoli `##`, paragrafi,
 * grassetto e corsivo — e lo si rende senza una libreria: il testo viene dal
 * modello, e non passa mai da `dangerouslySetInnerHTML`. */

import { Fragment } from "react";

function inline(testo: string): React.ReactNode[] {
  const parti = testo.split(/(\*\*[^*]+\*\*|\*[^*]+\*)/g);
  return parti.map((p, i) => {
    if (p.startsWith("**") && p.endsWith("**")) return <strong key={i}>{p.slice(2, -2)}</strong>;
    if (p.startsWith("*") && p.endsWith("*") && p.length > 2) return <em key={i}>{p.slice(1, -1)}</em>;
    return <Fragment key={i}>{p}</Fragment>;
  });
}

export function Markdown({ testo, className }: { testo: string; className?: string }) {
  const blocchi = testo.split(/\n{2,}/);
  return (
    <div className={className}>
      {blocchi.map((b, i) => {
        const righe = b.trim();
        if (!righe) return null;
        if (righe.startsWith("## ")) {
          const [titolo, ...resto] = righe.split("\n");
          return (
            <Fragment key={i}>
              <h3>{titolo.slice(3)}</h3>
              {resto.length > 0 && <p>{inline(resto.join(" "))}</p>}
            </Fragment>
          );
        }
        if (righe.startsWith("# ")) return <h3 key={i}>{righe.slice(2)}</h3>;
        if (/^[-*] /.test(righe)) {
          return (
            <ul key={i}>
              {righe.split("\n").map((r, j) => <li key={j}>{inline(r.replace(/^[-*] /, ""))}</li>)}
            </ul>
          );
        }
        return <p key={i}>{inline(righe.replace(/\n/g, " "))}</p>;
      })}
    </div>
  );
}
