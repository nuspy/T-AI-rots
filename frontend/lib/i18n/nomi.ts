/* I nomi di carte, stese e posizioni nella lingua richiesta.
 *
 * Il server manda `nomi`: l'inglese sempre (il nome di Thoth, lo standard
 * internazionale) e le lingue per cui esiste una traduzione dei nomi
 * (oggi l'ungherese). Per l'italiano si usano i campi originali. Una lingua
 * senza nomi propri ricade sull'inglese: mai un campo vuoto.
 */

import type { Carta, Posizione, Stesa } from "../api";
import type { Lingua } from "./lingue";

export function nomeCarta(carta: Carta, lingua: Lingua): string {
  if (lingua === "it") return carta.nome_it;
  return carta.nomi?.[lingua] ?? carta.nomi?.en ?? carta.nome_thoth;
}

export function nomeStesa(stesa: Stesa, lingua: Lingua): string {
  if (lingua === "it") return stesa.nome;
  return stesa.nomi?.[lingua] ?? stesa.nomi?.en ?? stesa.nome_en ?? stesa.nome;
}

/** Il nome di una stesa dai soli campi che lo storico riceve: l'italiano e i `nomi`. */
export function nomeStesaDaNomi(nome: string, nomi: Record<string, string> | undefined, lingua: Lingua): string {
  if (lingua === "it") return nome;
  return nomi?.[lingua] ?? nomi?.en ?? nome;
}

export function nomePosizione(posizione: Posizione, lingua: Lingua): string {
  if (lingua === "it") return posizione.nome;
  return posizione.nomi?.[lingua] ?? posizione.nomi?.en ?? posizione.nome_en ?? posizione.nome;
}
