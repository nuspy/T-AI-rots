/* Dati strutturati (JSON-LD) in una pagina.
 *
 * `<` diventa `<`: un titolo o un testo scritto da un autore non deve poter chiudere il tag `<script>`
 * (vedi la guida JSON-LD di Next). Si scrive dal server, così stanno nell'HTML che leggono i motori di ricerca. */
export function JsonLd({ dati }: { dati: Record<string, unknown> }) {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(dati).replace(/</g, "\\u003c") }}
    />
  );
}
