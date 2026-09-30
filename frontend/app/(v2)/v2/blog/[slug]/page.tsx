import type { Metadata } from "next";
import type { ArticoloBlog } from "@/lib/blog";
import { leggiDalServer } from "@/lib/server-api";
import { Pagina } from "@/v2/componenti/pagina";
import { metaV2, testiServer } from "@/v2/lib/meta";
import { ArticoloDiario } from "@/v2/pagine/blog";

/* Il titolo e la descrizione dell'articolo li scrive il server (anteprime nei social quando si condivide un
 * articolo dalla v2); il testo lo carica la pagina. */
export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const a = await leggiDalServer<ArticoloBlog>(`/blog/posts/${encodeURIComponent(slug)}`, { secondi: 30 });
  if (!a) return { title: (await testiServer()).blog.meta_titolo };
  return metaV2(a.seo_titolo ?? a.titolo, a.seo_descrizione, `/v2/blog/${slug}`);
}

export default async function PaginaArticolo({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  return (
    <Pagina>
      <ArticoloDiario slug={slug} />
    </Pagina>
  );
}
