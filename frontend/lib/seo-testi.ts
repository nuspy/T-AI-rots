/* I testi delle pagine pubbliche pensati per farsi trovare, in inglese (canonico) e in italiano.
 *
 * Non sono testo dell'interfaccia (quello sta in `i18n/`): sono titoli, descrizioni, introduzioni e risposte che
 * un motore di ricerca legge e che un visitatore trova sulla pagina. Le parole chiave vengono da
 * `skills/tarots-blog-publisher/references/keywords.md`; ogni pagina ha **una** parola chiave principale e non
 * la divide con un'altra (niente cannibalizzazione).
 *
 * Nessuna affermazione che il prodotto non sostenga: la carta del giorno è gratuita, le letture si pagano con
 * crediti o abbonamento; il mazzo è in preparazione e non ha ancora un prezzo. */

import type { Carta, Stesa } from "./api";
import { NOME_MARCHIO } from "./marchio";
import type { LinguaPubblica } from "./percorsi";
import { breve } from "./seo";

type L = LinguaPubblica;

const scegli = <T,>(lingua: L, en: T, it: T): T => (lingua === "it" ? it : en);

/** «a, b e c» / «a, b and c». */
export function elencoParole(lingua: L, voci: string[]): string {
  const v = voci.filter(Boolean);
  if (v.length <= 1) return v.join("");
  const e = lingua === "it" ? " e " : " and ";
  return `${v.slice(0, -1).join(", ")}${e}${v[v.length - 1]}`;
}

/** La prima frase di un testo, per una risposta breve. */
export function primaFrase(testo: string): string {
  const m = testo.match(/^.+?[.!?](\s|$)/);
  return (m ? m[0] : testo).trim();
}

/* ---- la soglia ---------------------------------------------------------------------------------------------- */

export const HOME = {
  title: (l: L) => scegli(l, "AI Tarot Reading with the Thoth Tarot", "Lettura dei tarocchi con l'AI: il Tarocco di Thoth"),
  /* Il titolo assoluto: il marchio in fondo. */
  titleCompleto: (l: L) => `${HOME.title(l)} | ${NOME_MARCHIO}`,
  description: (l: L) =>
    scegli(
      l,
      "Online tarot reading with the Thoth Tarot and AI: a short interview, cards revealed one by one, and an interpretation rooted in Golden Dawn tradition.",
      "Lettura dei tarocchi online con il Tarocco di Thoth e l'AI: una breve intervista, le carte rivelate una a una e un'interpretazione fedele alla Golden Dawn.",
    ),
  h2Esplora: (l: L) => scegli(l, "Explore the cards and spreads", "Esplora le carte e le stese"),
  h2Domande: (l: L) => scegli(l, "Questions about AI tarot readings", "Domande sulle letture dei tarocchi con l'AI"),
  domande: (l: L): { d: string; r: string }[] =>
    scegli(
      l,
      [
        {
          d: "Is an AI tarot reading accurate?",
          r: "A tarot reading is a tool for reflection, not a prediction you can verify. What the AI adds is method: it asks about your question first, reads each card in its position with the traditional correspondences of the Thoth Tarot, and links the cards into one coherent interpretation. It does not know your future, and it will not tell you what to do about health, money or legal matters.",
        },
        {
          d: "What is the Thoth Tarot?",
          r: "The Thoth Tarot is a 78-card deck designed by Aleister Crowley and painted by Lady Frieda Harris between 1938 and 1943. It grew out of the Hermetic Order of the Golden Dawn, whose system maps every card to the Hebrew alphabet, a path on the Tree of Life, an element and an astrological attribution. That is why a reading here is more than a list of card meanings: each card is read with its own correspondences, in its position in the spread, and the cards are read in relation to one another.",
        },
        {
          d: "Is the tarot reading free?",
          r: "The card of the day is free. Readings use credits or a subscription; see the pricing page for the packages.",
        },
        {
          d: "What is the difference between the Thoth Tarot and the Rider-Waite tarot?",
          r: "Both have 78 cards. The Rider-Waite deck is built on scenes and is the usual starting point for beginners. The Thoth deck is built on the Golden Dawn correspondences and on Crowley's symbolism: it renames several cards (Strength becomes Lust, Justice becomes Adjustment, Temperance becomes Art) and it is usually read without reversed cards.",
        },
        {
          d: "Can I choose the spread?",
          r: "Yes. There are classic spreads such as the Celtic Cross, the horseshoe and the three-card spread, and there are spreads for compatibility and for relationships.",
        },
      ],
      [
        {
          d: "Una lettura dei tarocchi con l'AI è accurata?",
          r: "Una lettura dei tarocchi è uno strumento di riflessione, non una previsione verificabile. Ciò che l'AI aggiunge è il metodo: prima ti chiede della tua domanda, poi legge ogni carta nella sua posizione con le corrispondenze tradizionali del Tarocco di Thoth e unisce le carte in un'unica interpretazione coerente. Non conosce il tuo futuro e non ti dice che cosa fare in materia di salute, denaro o questioni legali.",
        },
        {
          d: "Che cos'è il Tarocco di Thoth?",
          r: "Il Tarocco di Thoth è un mazzo di 78 carte ideato da Aleister Crowley e dipinto da Lady Frieda Harris fra il 1938 e il 1943. Nasce dall'Ordine Ermetico della Golden Dawn, il cui sistema collega ogni carta all'alfabeto ebraico, a un sentiero dell'Albero della Vita, a un elemento e a un'attribuzione astrologica. Per questo una lettura qui è più di un elenco di significati: ogni carta è letta con le sue corrispondenze, nella sua posizione nella stesa, e le carte sono lette in relazione fra loro.",
        },
        {
          d: "La lettura dei tarocchi è gratuita?",
          r: "La carta del giorno è gratuita. Le letture si pagano con crediti o abbonamento: i pacchetti sono nella pagina dei prezzi.",
        },
        {
          d: "Che differenza c'è fra il Tarocco di Thoth e i tarocchi Rider-Waite?",
          r: "Hanno entrambi 78 carte. Il Rider-Waite si basa su scene ed è il punto di partenza abituale per chi comincia. Il Thoth si basa sulle corrispondenze della Golden Dawn e sul simbolismo di Crowley: rinomina alcune carte (la Forza diventa Lussuria, la Giustizia Regolazione, la Temperanza Arte) e di solito si legge senza carte rovesciate.",
        },
        {
          d: "Posso scegliere la stesa?",
          r: "Sì. Ci sono stese classiche come la croce celtica, il ferro di cavallo e le tre carte, e ci sono stese per la compatibilità e per la coppia.",
        },
      ],
    ),
};

/* ---- le carte -------------------------------------------------------------------------------------------------- */

export const CARTE = {
  title: (l: L) => scegli(l, "Thoth Tarot Card Meanings: All 78 Cards", "Significato delle carte dei tarocchi di Thoth: tutte le 78 carte"),
  description: (l: L) =>
    scegli(
      l,
      "The meaning of all 78 Thoth Tarot cards: Major and Minor Arcana with Hebrew letter, Tree of Life path, element, astrology, and love and career readings.",
      "Il significato delle 78 carte del Tarocco di Thoth: Arcani maggiori e minori con lettera ebraica, sentiero, elemento, astrologia e letture per amore e lavoro.",
    ),
  h1: (l: L) => scegli(l, "Thoth Tarot card meanings", "Significato delle carte dei tarocchi di Thoth"),
  intro: (l: L) =>
    scegli(
      l,
      "Every card of the Thoth Tarot, with its upright and reversed meaning, its reading for love, work and spirit, and its Golden Dawn correspondences: Hebrew letter, path on the Tree of Life, element and astrology. Start with the 22 Major Arcana, or browse a suit of the Minor Arcana: Wands, Cups, Swords or Disks.",
      "Ogni carta del Tarocco di Thoth, con il suo significato dritto e rovesciato, la lettura per amore, lavoro e spirito e le corrispondenze della Golden Dawn: lettera ebraica, sentiero sull'Albero della Vita, elemento e astrologia. Comincia dai 22 Arcani maggiori o sfoglia un seme degli Arcani minori: Bastoni, Coppe, Spade o Dischi.",
    ),
};

/** «Two of Wands — Dominion» → «Two of Wands»: il nome che si cerca, senza il titolo di Thoth. */
export const nomeBreve = (nome: string): string => nome.split(" — ")[0];

export interface CartaSeo {
  /* Il nome breve (senza titolo): è quello di titoli e domande. */
  nome: string;
  /* Il nome intero, per la prima menzione. */
  nomeCompleto?: string;
  arcano: "maggiore" | "minore";
  numero_romano: string | null;
  arcano_label?: string | null;
  seme_label?: string | null;
  elemento_label?: string | null;
  astrologia: string;
  parole_chiave: string[];
  lettera_ebraica: { nome: string } | null;
  percorso?: number | null;
  collega?: string[] | null;
  sefira?: string | null;
  dritto?: string;
  rovescio?: string;
  ambiti?: Record<string, string>;
}

/** Da una carta dell'API ai campi che servono ai testi. */
export function seoCarta(c: Carta): CartaSeo {
  const intero = c.nome ?? c.nome_it;
  return {
    nome: nomeBreve(intero),
    nomeCompleto: intero,
    arcano: c.arcano,
    numero_romano: c.numero_romano,
    arcano_label: c.arcano_label,
    seme_label: c.seme_label,
    elemento_label: c.elemento_label,
    astrologia: c.astrologia,
    parole_chiave: c.parole_chiave,
    lettera_ebraica: c.lettera_ebraica,
    percorso: c.percorso,
    collega: c.collega,
    sefira: c.sefira,
    dritto: c.dritto,
    rovescio: c.rovescio,
    ambiti: c.ambiti,
  };
}

export function attribuzioni(l: L, c: CartaSeo): string {
  const parti: string[] = [];
  if (c.lettera_ebraica) parti.push(scegli(l, `the Hebrew letter ${c.lettera_ebraica.nome}`, `la lettera ebraica ${c.lettera_ebraica.nome}`));
  if (c.percorso) {
    const tra = c.collega?.length === 2 ? scegli(l, ` between ${c.collega[0]} and ${c.collega[1]}`, ` fra ${c.collega[0]} e ${c.collega[1]}`) : "";
    parti.push(scegli(l, `path ${c.percorso} of the Tree of Life${tra}`, `il sentiero ${c.percorso} dell'Albero della Vita${tra}`));
  } else if (c.sefira) {
    parti.push(scegli(l, `the sephirah ${c.sefira}`, `la sefirah ${c.sefira}`));
  }
  if (c.elemento_label) parti.push(scegli(l, `the element ${c.elemento_label}`, `l'elemento ${c.elemento_label}`));
  if (c.astrologia) parti.push(scegli(l, `${c.astrologia} in astrology`, `${c.astrologia} in astrologia`));
  return elencoParole(l, parti);
}

export const CARTA = {
  title: (l: L, c: CartaSeo) =>
    scegli(l, `${c.nome} Tarot Card Meaning (Thoth Tarot)`, `${c.nome}: significato nei tarocchi di Thoth`),
  description: (l: L, c: CartaSeo) =>
    breve(
      scegli(
        l,
        `${c.nome} in the Thoth Tarot: ${c.parole_chiave.slice(0, 3).join(", ")}. Upright and reversed meaning, love, career and spirit, with its Hebrew letter and Tree of Life path. ${c.dritto ?? ""}`,
        `${c.nome} nel Tarocco di Thoth: ${c.parole_chiave.slice(0, 3).join(", ")}. Significato dritto e rovesciato, amore, lavoro e spirito, con lettera ebraica e sentiero. ${c.dritto ?? ""}`,
      ),
      160,
    ),
  h1: (l: L, c: CartaSeo) => scegli(l, `${c.nome} tarot card meaning`, `${c.nome}: significato della carta`),
  sottotitolo: (l: L, c: CartaSeo) =>
    [scegli(l, "Thoth Tarot", "Tarocco di Thoth"), c.arcano_label, c.numero_romano].filter(Boolean).join(" · "),
  intro: (l: L, c: CartaSeo) => {
    const dove =
      c.arcano === "maggiore"
        ? scegli(l, `card ${c.numero_romano ?? ""} of the Major Arcana`, `la carta ${c.numero_romano ?? ""} degli Arcani maggiori`)
        : scegli(l, `a card of the Minor Arcana, suit of ${c.seme_label ?? ""}`, `una carta degli Arcani minori, seme di ${c.seme_label ?? ""}`);
    const chiavi = elencoParole(l, c.parole_chiave.slice(0, 4));
    const corrispondenze = attribuzioni(l, c);
    const intero = c.nomeCompleto ?? c.nome;
    return scegli(
      l,
      `${intero} is ${dove} in the Thoth Tarot. In a reading it speaks of ${chiavi}.${corrispondenze ? ` In the Golden Dawn system it corresponds to ${corrispondenze}.` : ""}`,
      `${intero} è ${dove} nel Tarocco di Thoth. In una lettura parla di ${chiavi}.${corrispondenze ? ` Nel sistema della Golden Dawn corrisponde a ${corrispondenze}.` : ""}`,
    );
  },
  h2Significato: (l: L, c: CartaSeo) => scegli(l, `What does ${c.nome} mean?`, `Che cosa significa ${c.nome}?`),
  h2Rovescia: (l: L, c: CartaSeo) => scegli(l, `${c.nome} reversed`, `${c.nome} rovesciata`),
  notaRovescia: (l: L) =>
    scegli(
      l,
      "The Thoth Tarot is traditionally read without reversed cards: the reader judges from the cards around it whether a card is well or ill dignified. This is its ill-dignified or blocked reading:",
      "Il Tarocco di Thoth si legge tradizionalmente senza carte rovesciate: chi legge giudica, dalle carte vicine, se una carta è ben o mal dignificata. Questa è la sua lettura mal dignificata o bloccata:",
    ),
  h2Ambiti: (l: L, c: CartaSeo) => scegli(l, `${c.nome} in love, work and spirit`, `${c.nome} in amore, lavoro e spirito`),
  ambiti: (l: L): Record<string, string> => scegli(l, { amore: "In love", lavoro: "At work and career", spirito: "In spiritual practice" }, { amore: "In amore", lavoro: "Nel lavoro", spirito: "Nella pratica spirituale" }),
  livelli: (l: L): Record<string, string> =>
    scegli(
      l,
      { essoterico: "Everyday meaning", psicologico: "Psychological meaning", iniziatico: "Initiatic meaning", ombra: "The shadow side" },
      { essoterico: "Significato quotidiano", psicologico: "Significato psicologico", iniziatico: "Significato iniziatico", ombra: "Il lato d'ombra" },
    ),
  h2Corrispondenze: (l: L, c: CartaSeo) => scegli(l, `Kabbalah, astrology and the Hebrew letter of ${c.nome}`, `Cabala, astrologia e lettera ebraica di ${c.nome}`),
  h2Crowley: (l: L, c: CartaSeo) => scegli(l, `Crowley on ${c.nome}`, `Crowley su ${c.nome}`),
  h2Domande: (l: L) => scegli(l, "Frequently asked questions", "Domande frequenti"),
  domande: (l: L, c: CartaSeo): { d: string; r: string }[] => {
    const voci: { d: string; r: string }[] = [];
    if (c.dritto) voci.push({ d: scegli(l, `What does ${c.nome} mean in the Thoth Tarot?`, `Che cosa significa ${c.nome} nel Tarocco di Thoth?`), r: c.dritto });
    if (c.ambiti?.amore) voci.push({ d: scegli(l, `What does ${c.nome} mean in love?`, `Che cosa significa ${c.nome} in amore?`), r: c.ambiti.amore });
    if (c.ambiti?.lavoro) voci.push({ d: scegli(l, `What does ${c.nome} mean for work and career?`, `Che cosa significa ${c.nome} per il lavoro?`), r: c.ambiti.lavoro });
    if (c.rovescio) voci.push({ d: scegli(l, `What does ${c.nome} mean reversed?`, `Che cosa significa ${c.nome} rovesciata?`), r: `${CARTA.notaRovescia(l)} ${c.rovescio}` });
    const corr = attribuzioni(l, c);
    if (corr) {
      voci.push({
        d: scegli(l, `What are the Kabbalah and astrology correspondences of ${c.nome}?`, `Quali sono le corrispondenze cabalistiche e astrologiche di ${c.nome}?`),
        r: scegli(l, `In the Golden Dawn system ${c.nome} corresponds to ${corr}.`, `Nel sistema della Golden Dawn ${c.nome} corrisponde a ${corr}.`),
      });
    }
    return voci;
  },
  cta: (l: L, c: CartaSeo) => scegli(l, `Draw your own cards: get a reading that includes ${c.nome}`, `Pesca le tue carte: una lettura che comprende ${c.nome}`),
  precedente: (l: L) => scegli(l, "Previous card", "Carta precedente"),
  successiva: (l: L) => scegli(l, "Next card", "Carta successiva"),
};

/* ---- le stese ---------------------------------------------------------------------------------------------------- */

export const STESE = {
  title: (l: L) => scegli(l, "Tarot Spreads: Celtic Cross, Love & Couples", "Stese dei tarocchi: croce celtica, amore e coppia"),
  description: (l: L) =>
    scegli(
      l,
      "Tarot spreads with the meaning of every position: Celtic Cross, horseshoe, three-card, astrological wheel, plus compatibility and relationship spreads.",
      "Le stese dei tarocchi con il significato di ogni posizione: croce celtica, ferro di cavallo, tre carte, ruota astrologica, e stese per la compatibilità e per la coppia.",
    ),
  h1: (l: L) => scegli(l, "Tarot spreads and how to read them", "Le stese dei tarocchi e come si leggono"),
  intro: (l: L) =>
    scegli(
      l,
      "A spread is a layout that gives each card a position, and the position gives the card its question. These are the spreads you can use here, each with the meaning of every position and how to read the cards together: classic spreads, spreads for compatibility, and spreads for a relationship.",
      "Una stesa è uno schema che dà a ogni carta una posizione, e la posizione dà alla carta la sua domanda. Queste sono le stese che si possono usare qui, ciascuna con il significato di ogni posizione e il modo di leggere le carte insieme: stese classiche, stese di compatibilità e stese di coppia.",
    ),
};

export interface StesaSeo {
  nome: string;
  slug?: string;
  categoria: string;
  categoria_label?: string | null;
  mazzo_label?: string | null;
  carte_da_scegliere: number;
  origine: string;
  descrizione: string;
  regole: string[];
  posizioni: { n: number; nome: string; significato: string }[];
}

/** Da una stesa dell'API ai campi che servono ai testi. `nome` è quello da mostrare (lo dà la pagina). */
export function seoStesa(s: Stesa, nome: string): StesaSeo {
  return {
    nome,
    slug: s.slug,
    categoria: s.categoria,
    categoria_label: s.categoria_label,
    mazzo_label: s.mazzo_label,
    carte_da_scegliere: s.carte_da_scegliere,
    origine: s.origine,
    descrizione: s.descrizione,
    regole: s.regole,
    posizioni: s.posizioni.map((p) => ({ n: p.n, nome: p.nome, significato: p.significato })),
  };
}

export const STESA = {
  title: (l: L, s: StesaSeo) => scegli(l, `${s.nome}: Tarot Spread Positions & Meaning`, `${s.nome}: posizioni e significato della stesa`),
  description: (l: L, s: StesaSeo) =>
    breve(
      scegli(
        l,
        `How to read the ${s.nome} tarot spread: the meaning of all ${s.carte_da_scegliere} positions and how to read the cards together. ${s.descrizione}`,
        `Come si legge la stesa ${s.nome}: il significato delle ${s.carte_da_scegliere} posizioni e come leggere le carte insieme. ${s.descrizione}`,
      ),
      160,
    ),
  h1: (l: L, s: StesaSeo) => scegli(l, `${s.nome} tarot spread`, `Stesa ${s.nome}`),
  intro: (l: L, s: StesaSeo) =>
    scegli(
      l,
      `The ${s.nome} uses ${s.carte_da_scegliere} cards${s.mazzo_label ? ` (${s.mazzo_label.charAt(0).toLowerCase()}${s.mazzo_label.slice(1)})` : ""}. ${s.descrizione} ${s.origine}`,
      `La stesa ${s.nome} usa ${s.carte_da_scegliere} carte${s.mazzo_label ? ` (${s.mazzo_label.charAt(0).toLowerCase()}${s.mazzo_label.slice(1)})` : ""}. ${s.descrizione} ${s.origine}`,
    ),
  h2Posizioni: (l: L, s: StesaSeo) => scegli(l, `The ${s.carte_da_scegliere} positions of the ${s.nome}`, `Le ${s.carte_da_scegliere} posizioni della stesa ${s.nome}`),
  h2Come: (l: L, s: StesaSeo) => scegli(l, `How to read the ${s.nome}`, `Come si legge la stesa ${s.nome}`),
  h2Domande: (l: L) => scegli(l, "Frequently asked questions", "Domande frequenti"),
  domande: (l: L, s: StesaSeo): { d: string; r: string }[] => {
    const nomi = elencoParole(l, s.posizioni.map((p) => p.nome));
    return [
      {
        d: scegli(l, `How many cards does the ${s.nome} use?`, `Quante carte usa la stesa ${s.nome}?`),
        r: scegli(
          l,
          `The ${s.nome} uses ${s.carte_da_scegliere} cards${s.mazzo_label ? `: ${s.mazzo_label.charAt(0).toLowerCase()}${s.mazzo_label.slice(1)}` : ""}.`,
          `La stesa ${s.nome} usa ${s.carte_da_scegliere} carte${s.mazzo_label ? `: ${s.mazzo_label.charAt(0).toLowerCase()}${s.mazzo_label.slice(1)}` : ""}.`,
        ),
      },
      {
        d: scegli(l, `What do the positions of the ${s.nome} mean?`, `Che cosa significano le posizioni della stesa ${s.nome}?`),
        r: scegli(l, `The positions are: ${nomi}. Each card is read as the answer to the question of its position.`, `Le posizioni sono: ${nomi}. Ogni carta si legge come risposta alla domanda della sua posizione.`),
      },
      {
        d: scegli(l, `How do you read the ${s.nome}?`, `Come si legge la stesa ${s.nome}?`),
        r: s.regole.join(" "),
      },
      {
        d: scegli(l, `Where does the ${s.nome} come from?`, `Da dove viene la stesa ${s.nome}?`),
        r: s.origine,
      },
    ];
  },
  cta: (l: L, s: StesaSeo) => scegli(l, `Try the ${s.nome}: get a reading with this spread`, `Prova la stesa ${s.nome}: una lettura con questo schema`),
};

/* ---- il negozio ----------------------------------------------------------------------------------------------- */

export const MAZZO = {
  title: (l: L) => scegli(l, "Thoth Tarot Deck with Original Art (78 Cards)", "Mazzo di tarocchi di Thoth con grafica originale (78 carte)"),
  description: (l: L) =>
    scegli(
      l,
      "A Thoth Tarot deck with original artwork: 78 illustrated cards, a gold card back and a collector's box. In preparation: see the cards.",
      "Un mazzo di tarocchi di Thoth con grafica originale: 78 carte illustrate, un dorso dorato e un cofanetto da collezione. In preparazione: guarda le carte.",
    ),
};

export const PREZZI = {
  title: (l: L) => scegli(l, "Tarot Reading Prices: Plans and Packs", "Prezzi delle letture: abbonamenti e pacchetti"),
  description: (l: L) =>
    scegli(
      l,
      "Prices for online tarot readings with the Thoth Tarot: a free card of the day, monthly subscriptions and reading packs that never expire.",
      "Prezzi delle letture di tarocchi online con il Tarocco di Thoth: carta del giorno gratuita, abbonamenti mensili e pacchetti di letture senza scadenza.",
    ),
};

export const GIORNO = {
  h1: (l: L) => scegli(l, "Tarot card of the day", "Carta del giorno dei tarocchi"),
  intro: (l: L) =>
    scegli(
      l,
      "One card from the Thoth Tarot for everyone, the same until midnight UTC. Read it as a question to carry through the day, not as a prediction.",
      "Una carta del Tarocco di Thoth per tutti, la stessa fino a mezzanotte UTC. Leggila come una domanda da portare con te durante la giornata, non come una previsione.",
    ),
  sottotitolo: (l: L, data: string, nome: string) => scegli(l, `${data}: ${nome}`, `${data}: ${nome}`),
  pienoSignificato: (l: L, nome: string) => scegli(l, `Full meaning of ${nome}`, `Il significato completo di ${nome}`),
  personale: (l: L) =>
    scegli(
      l,
      "With a free account you get your own card of the day, different for each person, and a streak of consecutive days.",
      "Con un account gratuito hai la tua carta del giorno, diversa per ciascuno, e la serie dei giorni consecutivi.",
    ),
  title: (l: L) => scegli(l, "Tarot Card of the Day: Free Daily Tarot Card", "Carta del giorno: la tua carta dei tarocchi gratuita"),
  description: (l: L) =>
    scegli(
      l,
      "Draw your free tarot card of the day from the Thoth Tarot, with its meaning and a daily streak. One card, the same for the whole day.",
      "Pesca la tua carta del giorno gratuita dal Tarocco di Thoth, con il suo significato e la serie dei giorni consecutivi. Una carta, la stessa per tutta la giornata.",
    ),
};

export const BLOG = {
  title: (l: L) => scegli(l, "Tarot Blog: Thoth Tarot, Spreads & Esoterica", "Blog dei tarocchi: Thoth, stese ed esoterismo"),
  description: (l: L) =>
    scegli(
      l,
      "Guides and articles on the Thoth Tarot, tarot spreads, the Golden Dawn and Hermetic Qabalah, tarot for love and relationships, and how to read the cards.",
      "Guide e articoli sul Tarocco di Thoth, le stese, la Golden Dawn e la Qabalah ermetica, i tarocchi per amore e relazioni, e come si leggono le carte.",
    ),
  h1: (l: L) => scegli(l, "The tarot blog", "Il blog dei tarocchi"),
  parole: (l: L) =>
    scegli(
      l,
      ["tarot blog", "Thoth tarot", "tarot card meanings", "tarot spreads", "Golden Dawn", "Hermetic Qabalah", "learn tarot", "tarot for love", "esoteric blog"],
      ["blog tarocchi", "tarocchi di Thoth", "significato delle carte", "stese dei tarocchi", "Golden Dawn", "Qabalah ermetica", "imparare i tarocchi", "tarocchi amore", "blog esoterismo"],
    ),
  /* Una sezione: il titolo e la descrizione se l'autore non li ha scritti. */
  sezioneTitolo: (l: L, nome: string) => scegli(l, `${nome}: tarot articles, cards and spreads`, `${nome}: articoli, carte e stese dei tarocchi`),
  sezioneDescrizione: (l: L, nome: string) =>
    scegli(
      l,
      `${nome} on the ${NOME_MARCHIO} blog: guides on the Thoth Tarot, card meanings and tarot spreads.`,
      `${nome} sul blog di ${NOME_MARCHIO}: guide sul Tarocco di Thoth, significati delle carte e stese.`,
    ),
  etichettaTitolo: (l: L, nome: string) => scegli(l, `${nome}: tarot articles`, `${nome}: articoli sui tarocchi`),
  etichettaDescrizione: (l: L, nome: string) =>
    scegli(l, `Every ${NOME_MARCHIO} blog article about “${nome}”.`, `Tutti gli articoli del blog di ${NOME_MARCHIO} su «${nome}».`),
  feedTitolo: (l: L) => scegli(l, `${NOME_MARCHIO} — the tarot blog`, `${NOME_MARCHIO} — il blog dei tarocchi`),
  feedDescrizione: (l: L) =>
    scegli(
      l,
      "Guides and articles on the Thoth Tarot, tarot spreads, the Golden Dawn and Hermetic Qabalah.",
      "Guide e articoli sul Tarocco di Thoth, le stese, la Golden Dawn e la Qabalah ermetica.",
    ),
};
