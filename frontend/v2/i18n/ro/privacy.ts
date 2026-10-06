/* COPIA DELL'INGLESE — da tradurre. Rigenerata da copia-inglese.mjs finché questa riga resta qui. */
/* Method & privacy. The legal content is the site's own (same controller, same choices, same statistics policy);
 * the V2 adds what the reader remembers and how the AI is used, in plain words. */

export const privacy = {
  meta_titolo: "Method & privacy",
  meta_descrizione: "What is kept, why, and how you decide: readings, memory, statistics and cookies.",
  eyebrow: "Method & privacy",
  titolo: "Mystical does not have to mean opaque.",
  intro: "What is kept, why, and how you decide. The same rules apply to every page of TAROTS chat.",

  letture_titolo: "Your readings and your memory",
  letture_testo: "Readings are kept in your account so you can return to them. What your reader remembers comes from your readings and conversations, and you can review, edit or delete it at any time from My story. Deleting a reading removes it for good.",
  letture_cta: "Manage what is remembered",
  letture_accesso: "For security reasons only (for example to handle a report of abuse or a request for help), the administrators of TAROTS chat can read your readings, conversations, what the reader remembers and your profile data. Each access requires a stated reason and is recorded in a log.",
  ai_titolo: "How the AI is used",
  ai_testo: "An AI interprets the cards in the context of your question and your words. Names never reach the AI provider: it receives a placeholder (“Persona_1”) and you read the real name; the other person's surname is never sent. The AI does not know the future, and no reading is a prediction. With every request we ask the provider not to store the answers: your texts are not kept by it to train its models.",

  custode_titolo: "Who is responsible for your data",
  // The controller's details come from the console (Settings → Controller details): {placeholders} are filled in by
  // the page, and an empty field shows the neutral sentence next to it.
  custode_testo: "The data controller for the personal data collected by TAROTS chat (https://tarots.chat) is {titolare}.",
  custode_testo_senza_nome: "The data controller for the personal data collected by TAROTS chat (https://tarots.chat) can be reached at the privacy contact below.",
  custode_indirizzo: "Postal address: {indirizzo}.",
  custode_indirizzo_vuoto: "Postal address: available on request from the privacy contact.",
  custode_codice: "Tax code or VAT number: {codice}.",
  custode_email: "Privacy contact: {email}",
  custode_email_vuoto: "Privacy contact: being updated; meanwhile you can exercise your rights from your account.",
  custode_dpo: "Data protection officer (DPO): {dpo}.",
  custode_dpo_no: "No data protection officer (DPO) has been appointed.",

  scelte_titolo: "Your choices on this browser",
  scelte_testo: "Everything below is off until you turn it on, and you can change it here at any time. Technical cookies (signing in, the anonymous free reading, remembering these choices) need no consent: without them the site does not work.",
  scelte_account: "The choices that concern your account — your words for statistics, sensitive data, promotions — are in your account.",
  scelte_account_cta: "Privacy and consents",

  finalita_titolo: "What we use, why, and on what legal basis",
  finalita_intro: "Each use of your data has its own purpose and its own legal basis under the GDPR:",
  finalita: [
    { cosa: "Account and profile", perche: "To give you an account, keep your readings and personal cards, and sign you in (also with a social account).", base: "Basis: the contract you ask for (art. 6.1.b GDPR)." },
    { cosa: "Readings, interview, memory and chat", perche: "To read the cards for you with an AI and remember what helps in the next readings.", base: "Basis: contract; for sensitive data, your explicit consent (art. 9.2.a)." },
    { cosa: "The free reading without an account", perche: "To let you try one reading before signing up.", base: "Basis: steps you ask for before a contract (art. 6.1.b)." },
    { cosa: "Payments, credits, orders and shipping", perche: "To sell credits, plans and decks, and to keep the accounts the law requires.", base: "Basis: contract and legal obligations (art. 6.1.b and 6.1.c)." },
    { cosa: "Security and records", perche: "To protect accounts and the service, and to know who did what. IP addresses are stored only shortened, with a keyed fingerprint.", base: "Basis: legitimate interest (art. 6.1.f)." },
    { cosa: "Anonymous statistics", perche: "To count visits without cookies and without storing anything in your browser.", base: "Basis: legitimate interest." },
    { cosa: "Statistics linked to your account", perche: "To understand which channels bring members and what leads to a purchase.", base: "Basis: legitimate interest; you can object from your account (art. 21)." },
    { cosa: "Site statistics with a browser identifier", perche: "To recognise your browser when you come back.", base: "Basis: your consent (art. 6.1.a)." },
    { cosa: "Google Analytics", perche: "To measure how the site is used.", base: "Basis: your consent." },
    { cosa: "Ads", perche: "To show Google AdSense ads in a few marked spaces, only if they are switched on.", base: "Basis: your consent." },
    { cosa: "Your words for statistics and blog ideas", perche: "To understand, anonymously and in aggregate, which topics matter to people (never quoting anyone). Not active yet.", base: "Basis: your separate, optional consent." },
    { cosa: "Promotions", perche: "Offers and news through notifications, when they arrive.", base: "Basis: your consent." },
    { cosa: "Minimum age", perche: "To check you are old enough to use the service on your own.", base: "Basis: legal obligation (art. 8 GDPR) and contract." },
  ],

  art9_titolo: "Sensitive data",
  art9_testo: "Some things you may tell us are special categories of data: being trans, your health. The “trans person” box and memories about your health are used only with your explicit consent, which you give where you tick the box and can withdraw at any time from your account: the box is then cleared and those memories deleted. Without it, they never reach the AI.",
  art9_crisi: "If you write that you want to harm yourself, the reading stops and we show where to find help straight away. We only count that it happened, without linking it to you.",

  stat_titolo: "Usage statistics",
  stat_anonime: "We measure anonymously how the site is used: pages visited, where the visit comes from (search engine, social network, campaign), device and browser type, approximate country and city. No cookies, and nothing is stored in your browser. Your IP address is only used at the moment of the visit, to estimate country and city and to compute a fingerprint that changes every day: it is never stored.",
  stat_account: "If you have an account and are signed in, your visits are linked to your account, based on our legitimate interest in understanding how to improve the service (for example which channel new members come from and what leads to a purchase). You can object at any time from your account: from then on visits are no longer linked, and the link with past ones is deleted.",
  stat_esteso: "If you turn on “Site statistics”, we also recognise your browser when you come back on later days, with a random identifier kept in your browser. If you decline or change your mind, the identifier is forgotten by our servers too.",
  stat_google: "If you turn on “Google Analytics”, we also use Google Analytics 4, a service of Google Ireland Ltd., which sets its own cookies (_ga) to count visits and understand how the site is used. It is loaded only after your consent (Google Consent Mode), with Google signals and ad personalisation turned off; Google Analytics 4 does not store IP addresses. Google may process the data in the United States under the EU-US Data Privacy Framework. If you decline or withdraw your consent, Google Analytics stops and its cookies are deleted.",
  stat_conservazione: "Detailed visits and events are kept for 25 months; after that only anonymous daily totals remain. Automated analyses and exports only use aggregated data.",
  stat_geo: "IP geolocation:",
  pubblicita_titolo: "Advertising",
  pubblicita_testo: "Some pages can show up to three spaces marked “Advertisement”, filled by Google AdSense, a service of Google Ireland Ltd. Ads load only if you accept here or in the banner: Google then sets its own cookies (such as __gads and __gpi) to deliver ads, limit how often you see them and measure them, and may process data in the United States under the EU-US Data Privacy Framework. Ads are not personalised unless this page says otherwise. If you decline, the spaces are not shown and nothing is loaded from Google AdSense.",

  social_titolo: "Signing in with a social",
  social_account: "One account per person: if you sign in with Google, Facebook, Apple, GitHub or LinkedIn using the same email as an existing account, it is the same account, with the same readings and credits.",
  social_cosa: "From that account we receive what it shares with us: first and last name, email, profile picture, language and — only if you allow it on the provider's screen — date of birth, gender and city. We use them only to fill in the fields of your account that are still empty, never over what you wrote.",
  social_perche: "Why: the date of birth gives your personal cards (soul card and year card) and gender is used for pronouns and agreement in readings about two people; name, language and picture save you retyping them. Legal basis: the service you ask for, and your choice on the provider's screen.",
  social_posizione: "Current location: country and city, from the social if it shares them, otherwise estimated at each sign-in from your IP address with a database kept on our server (the address is not stored and nothing is sent to third parties). It helps us adapt the service.",
  social_controllo: "From your account you see where each detail comes from, correct or delete it, stop the import or the location, or delete in one go everything that came from socials. Linked socials are managed from your account settings (“Linked accounts”).",
  social_cta: "Manage your details",

  responsabili_titolo: "Who else handles your data, and where",
  responsabili_intro: "We do not sell your data and do not share it with partners. These providers process it on our behalf, or as independent controllers when you choose to use them:",
  responsabili: [
    { chi: "Hosting", cosa: "our server and database. Provider and location: {hosting}." },
    { chi: "AI providers", cosa: "the language-model providers we configure receive the text of your question, interview and chat — with names replaced by a placeholder and never the surname — only to write the reading. Current providers and countries: {fornitori_ai}." },
    { chi: "Google", cosa: "Google Analytics and AdSense (only with your consent) and sign-in with Google (Google Ireland Ltd., data may go to the United States)." },
    { chi: "Sign-in providers", cosa: "Apple, Facebook (Meta), GitHub and LinkedIn, only if you choose to sign in with them: they are independent controllers of your account with them." },
    { chi: "Payments", cosa: "Stripe, for card payments (Stripe Payments Europe, data may go to the United States). We never see your card number." },
    { chi: "App notifications", cosa: "Firebase Cloud Messaging (Google), for the app notifications, when they arrive." },
    { chi: "Email and backups", cosa: "mail you write to an @tarots.chat address goes through Namecheap's forwarding service (United States) and lands in a Gmail mailbox of the data controller (Google); the emails we send you leave from our own server, hosted by Hivelocity in London; backups are kept in our own storage in Italy, with no third parties." },
  ],
  hosting_vuoto: "a provider bound by a data processing agreement",
  fornitori_ai_vuoto: "none active at the moment",
  fornitori_ai_proprio: "on our own server, no third party",
  trasferimenti: "When data leaves the European Economic Area we rely on an adequacy decision of the European Commission (the United Kingdom; the United States for companies certified under the EU-US Data Privacy Framework) or on the Commission's standard contractual clauses.",

  conservazione_titolo: "How long we keep it",
  conservazione: [
    "Account, readings, memory and chat: until you delete them or your account. There is no automatic expiry: we may also delete old data ourselves, for example free readings without an account and old chats.",
    "The free reading without an account: until we delete it; if you sign up, it becomes part of your account.",
    "Detailed visit statistics: 25 months, then only anonymous daily totals.",
    "Your consent choices: as long as we need to prove them.",
    "Accounting records (payments, credits, orders): as long as the law requires (in Italy, ten years). If you delete your account, they stay detached from your identity.",
    "Backups: deleted data disappears from the backups as they rotate, within about a week.",
  ],

  diritti_titolo: "Your rights",
  diritti_testo: "You can ask to access your data, correct it, delete it, receive it in a portable format, restrict its use or object to it, and withdraw any consent at any time — without affecting what was done before.",
  diritti_come: "Most of it you can do yourself: download your data and delete your account from your account page, and change every consent there or on this page. For anything else, write to the privacy contact above: we answer within one month.",
  diritti_cta_dati: "Your data and consents",
  diritti_cta_elimina: "Delete your account",
  garante_titolo: "Complaints",
  garante_testo: "If you think your data is processed unlawfully, you can complain to the Italian data protection authority (Garante per la protezione dei dati personali, www.garanteprivacy.it) or to the authority of the country where you live or work.",

  eta_titolo: "Minimum age",
  eta_testo: "TAROTS chat is for people aged 16 or over; 14 in Italy and Spain, 15 in France — the age at which the law lets you use online services on your own. We ask you to confirm it before the first reading. If the date of birth in your account is below the minimum, readings and chat stop.",

  versione: "Version 3 — 3 October 2026.",
};
