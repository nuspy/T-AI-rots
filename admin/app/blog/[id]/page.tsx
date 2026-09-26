"use client";

import { useParams } from "next/navigation";
import { Editor } from "../editor";

export default function ModificaArticolo() {
  const { id } = useParams<{ id: string }>();
  /* La chiave rimonta l'editor passando da un articolo all'altro: lo stato di un modulo non deve
   * sopravvivere a un articolo diverso. */
  return <Editor key={id} id={id} />;
}
