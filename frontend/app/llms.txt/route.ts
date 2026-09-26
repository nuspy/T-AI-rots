/* `/llms.txt`: una presentazione del sito in testo semplice, per i motori di risposta e gli assistenti che
 * leggono il web (formato llmstxt.org). Cosa è il servizio, dove stanno le pagine che contano, in inglese per
 * primo. Statico: cambia solo quando cambia il sito. */

import { SITE_URL } from "@/lib/condivisione";
import { NOME_MARCHIO } from "@/lib/marchio";

export function GET() {
  const testo = `# ${NOME_MARCHIO}

> ${NOME_MARCHIO} is an AI tarot reading service built on the Thoth Tarot (Aleister Crowley and Lady Frieda Harris). You ask a question, pick the spread, shuffle and choose the cards yourself, and receive a written interpretation that reads each card in its position. The site also has a free card of the day, a complete guide to the 78 cards and the spreads, and a blog on tarot and Western esotericism (Golden Dawn, Hermetic Qabalah, astrology, symbolism).

The site is published in English (canonical) and Italian (under /it). Card and spread texts are written for readers, not scraped from elsewhere.

## Tarot reference
- [The 78 cards](${SITE_URL}/cards): every Major and Minor Arcana card of the Thoth Tarot, with meaning, keywords, Qabalistic and astrological correspondences, and reversed meaning.
- [Tarot spreads](${SITE_URL}/spreads): three-card, Celtic Cross, Horseshoe, Astrological Wheel and relationship spreads, with the position meanings and how to read them.
- [The Thoth deck](${SITE_URL}/deck): the deck used for every reading.
- [Card of the day](${SITE_URL}/card-of-the-day): one card for everyone, the same all day (UTC), with a short reading.

## Blog
- [The tarot blog](${SITE_URL}/blog): guides and articles on card meanings, spreads, the Golden Dawn, Hermetic Qabalah and tarot for love and relationships.
- [RSS feed](${SITE_URL}/blog/feed.xml)

## Service
- [Pricing](${SITE_URL}/pricing): the card of the day is free; readings use credits.
- [Sitemap](${SITE_URL}/sitemap.xml)

## Optional
- [Italiano](${SITE_URL}/it): the same site in Italian.
`;
  return new Response(testo, {
    headers: { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "public, max-age=3600" },
  });
}
