import type { Metadata } from "next";
import { Pagina } from "@/v2/componenti/pagina";
import { testiServer } from "@/v2/lib/meta";
import { SezioneDiario } from "@/v2/pagine/blog";

export async function generateMetadata(): Promise<Metadata> {
  const t = await testiServer();
  return { title: t.blog.meta_titolo };
}

export default async function PaginaSezione({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  return (
    <Pagina>
      <SezioneDiario slug={slug} />
    </Pagina>
  );
}
