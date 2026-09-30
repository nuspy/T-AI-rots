/* V2 is deliberately self-contained: route constants and every internal href point to /v2.
 * It is a static parallel prototype in public/v2; no V1 page or component is imported. */
(() => {
  "use strict";

  const V2 = "/v2";
  const routes = {
    home: `${V2}/index.html`, read: `${V2}/read/index.html`, decks: `${V2}/decks/index.html`,
    thoth: `${V2}/decks/thoth/index.html`, cards: `${V2}/cards/index.html`, lovers: `${V2}/cards/the-lovers/index.html`,
    physical: `${V2}/physical-reading/index.html`, explore: `${V2}/explore/index.html`, blog: `${V2}/blog/index.html`,
    article: `${V2}/blog/the-lovers-and-choice/index.html`, story: `${V2}/my-story/index.html`, pricing: `${V2}/pricing/index.html`,
    shop: `${V2}/shop/index.html`, daily: `${V2}/daily-card/index.html`, spreads: `${V2}/spreads/index.html`,
    shared: `${V2}/shared/index.html`, profile: `${V2}/profile/index.html`,
  };
  const cardImage = (id) => `/cards/${id}.webp`;
  const byId = (id) => document.getElementById(id);
  const analytics = (event, detail = {}) => {
    try {
      const values = JSON.parse(localStorage.getItem("tarots.v2.events") || "[]");
      values.push({ event, detail, at: new Date().toISOString() });
      localStorage.setItem("tarots.v2.events", JSON.stringify(values.slice(-100)));
    } catch { /* V2 remains useful with storage disabled. */ }
  };
  const clean = (value) => String(value || "").replace(/[&<>"']/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" })[character]);
  const link = (href, label, cls = "") => `<a class="${cls}" href="${href}">${label}</a>`;
  const card = (id, alt, cls = "") => `<img class="${cls}" src="${cardImage(id)}" width="360" height="640" loading="lazy" alt="${alt}">`;

  function header(active = "") {
    const nav = [
      ["read", "Read"], ["decks", "Decks"], ["explore", "Explore"], ["story", "My story"], ["shop", "Shop"],
    ].map(([key, label]) => `<a href="${routes[key]}"${active === key ? ' aria-current="page"' : ""}>${label}</a>`).join("");
    return `<header class="site-header">
      <a class="brand" href="${routes.home}" aria-label="Tarots.chat V2 home"><span class="brand-mark" aria-hidden="true">✦</span><span>TAROTS <em>chat</em></span></a>
      <nav class="primary-nav" aria-label="V2 navigation">${nav}</nav>
      <div class="header-actions"><a class="text-link" href="${routes.profile}">Sign in</a><a class="button button-brass button-small" href="${routes.read}">Start reading</a></div>
    </header>`;
  }

  function footer() {
    return `<footer class="site-footer">
      <section><a class="brand" href="${routes.home}"><span class="brand-mark" aria-hidden="true">✦</span><span>TAROTS <em>chat</em></span></a><p>A living Tarot experience: question, ritual, interpretation and the thread you choose to keep.</p></section>
      <section><h2>Read</h2><ul><li><a href="${routes.read}">Start a free reading</a></li><li><a href="${routes.physical}">Use your own cards</a></li><li><a href="${routes.daily}">Card of the day</a></li><li><a href="${routes.story}">My story</a></li></ul></section>
      <section><h2>Explore</h2><ul><li><a href="${routes.decks}">Decks</a></li><li><a href="${routes.cards}">Card library</a></li><li><a href="${routes.spreads}">Spreads</a></li><li><a href="${routes.blog}">Journal</a></li></ul></section>
      <section><h2>About</h2><ul><li><a href="${routes.pricing}">Reading packages</a></li><li><a href="${routes.shop}">Deck &amp; PDF</a></li><li><a href="#method">Method &amp; privacy</a></li><li><a href="${routes.shared}">Share a reading</a></li></ul></section>
    </footer>`;
  }

  const topic = (symbol, name, note) => `<a class="topic" href="${routes.read}?topic=${encodeURIComponent(name)}"><span class="topic-icon" aria-hidden="true">${symbol}</span><b>${name}</b><small>${note}</small></a>`;
  const step = (symbol, title, description) => `<div class="ritual-step"><span aria-hidden="true">${symbol}</span><b>${title}</b><p>${description}</p></div>`;

  function home() {
    return `${header("home")}<main id="main" class="page">
      <section class="hero" aria-labelledby="hero-title">
        <div class="hero-copy">
          <p class="eyebrow">Thoth Tarot · guided ritual · contextual interpretation</p>
          <h1 id="hero-title" class="display">A question can become a <em>way back</em> to yourself.</h1>
          <p class="lede">Ask what is on your mind. Then shuffle, cut and choose the cards yourself. TAROTS chat connects the symbols, your question and the story you bring with you.</p>
          <form id="hero-question" class="question-form" novalidate>
            <label for="hero-question-input">What is on your mind?</label>
            <input id="hero-question-input" name="question" minlength="3" maxlength="1000" required placeholder="What is on your mind?" autocomplete="off">
            <button class="button button-brass" type="submit">Ask your question</button>
          </form>
          <div id="quick-response" class="notice hidden" role="status"></div>
          <div class="minor-cta"><a href="${routes.read}">Start your free reading</a><a href="${routes.physical}">Already have cards in your hands?</a></div>
          <div class="trust-strip"><span>No prediction is guaranteed</span><span>You choose the cards</span><span>Memory stays yours to manage</span></div>
        </div>
        <div class="ritual-object" aria-label="A Thoth Tarot card on a ritual table">
          <div class="hero-card">${card("maj-06", "The Lovers, a Thoth Tarot card")}</div>
          <p class="orbit-note"><strong>A living ritual</strong>Not a random card. A moment you take part in.</p>
        </div>
      </section>

      <section class="experience"><div class="band">
        <div class="section-head"><div><p class="eyebrow">See the experience</p><h2 class="section-title">The conversation leads. The ritual makes it yours.</h2></div><p class="section-intro">You can begin without an account. Receive a short response first, then decide whether to enter a deeper reading.</p></div>
        <div class="demo-stage"><div class="demo-copy"><p class="eyebrow">A question, in context</p><div class="chat-thread"><p class="message message-user">“I want to know whether I am avoiding a choice.”</p><p class="message">We can look at the choice without forcing an answer. Is the tension about a relationship, work, or both?</p><p class="message message-user">“Both, but the relationship is what I feel first.”</p></div></div><div class="demo-ritual"><p class="eyebrow">Then the cards</p><div class="ritual-preview" aria-hidden="true"><img class="card-back" src="/cards/dorso.webp" alt=""><img class="card-back" src="/cards/dorso.webp" alt=""><img class="card-back" src="/cards/dorso.webp" alt=""><span class="demo-caption">Shuffle · interrupt · cut · choose · reveal</span></div></div></div>
      </div></section>

      <section class="band"><div class="section-head"><div><p class="eyebrow">Begin where you are</p><h2 class="section-title">What is asking for your attention?</h2></div><a class="button button-quiet" href="${routes.read}">Ask your own question</a></div>
        <div class="topic-grid">${topic("♁", "Love", "what is opening")}${topic("☌", "Relationship", "what is changing")}${topic("♃", "Career", "where to place energy")}${topic("↔", "A difficult decision", "what each path asks")}${topic("◌", "Something unexplained", "what wants a name")}${topic("✦", "Self-discovery", "what wants to be seen")}</div>
      </section>

      <section class="band band-tight"><p class="eyebrow">The digital ritual</p><h2 class="section-title">A reading has a tempo.</h2><div class="ritual-steps">${step("1", "Ask", "Give the reading a real question.")}${step("2", "Shuffle", "Begin the movement, then interrupt it.")}${step("3", "Cut", "Choose where the deck divides.")}${step("4", "Draw", "Select cards from the opened fan.")}${step("5", "Reveal", "See each card in its place.")}${step("6", "Interpret", "Connect cards, question and context.")}</div></section>

      <section class="memory"><div class="band memory-layout"><div class="memory-card"><p>“Last week you asked how your relationship might develop. How are things going now?”</p><footer>A follow-up begins with what matters, not a blank page.</footer></div><div><p class="eyebrow">Your reader remembers your story</p><h2 class="section-title">Continuity without pretending to know more than you share.</h2><ul class="memory-list"><li><strong>Questions and themes</strong><span>so you can return to the thread of a situation.</span></li><li><strong>Readings and outcomes</strong><span>so reflection can include what happened next.</span></li><li><strong>Your choices</strong><span>you can review, edit or delete what is remembered.</span></li></ul><a class="button button-quiet" href="${routes.story}">See how memory works</a></div></div></section>

      <section class="band"><p class="eyebrow">Why it feels different</p><div class="difference-grid"><article class="difference"><span>✦</span><h3>A ritual you participate in</h3><p>You make the interruption, cut and selection part of the reading.</p></article><article class="difference"><span>◌</span><h3>Contextual interpretation</h3><p>The reading holds the question, positions, combinations and conversation together.</p></article><article class="difference"><span>↺</span><h3>A story with memory</h3><p>Return to an earlier question and see it with what has changed.</p></article><article class="difference"><span>✋</span><h3>Your physical deck is welcome</h3><p>Draw cards in the room, then bring their positions here for interpretation.</p></article></div></section>

      <section class="band deck-layout"><div class="deck-spread" aria-hidden="true">${card("maj-17", "", "")}${card("maj-06", "", "")}${card("maj-02", "", "")}</div><div><span class="available">Available now</span><p class="eyebrow">Choose a visual language</p><h2 class="section-title">Begin with the Thoth Tarot. Leave room for more worlds.</h2><p class="section-intro">The Thoth Tarot is available now. The reading experience is designed around a deck, so new decks can bring their own card library, ritual, stories and physical edition without replacing the path you are on.</p><div class="future-decks" aria-label="Future decks, not yet available"><span>The Lovers · planned</span><span>Italian Celebration · planned</span><span>Halloween Tarots · planned</span></div><a class="button button-quiet" href="${routes.thoth}">Explore the Thoth deck</a></div></section>

      <section class="physical"><div class="band physical-layout"><div><p class="eyebrow">A bridge to the physical world</p><h2 class="section-title">Already have a Tarot deck?</h2><p class="section-intro">Draw the cards yourself, put them in their positions, and let Tarots.chat help you read the pattern. The ritual stays in your hands.</p><a class="button" href="${routes.physical}">Use your own cards</a></div><div class="physical-card">${card("maj-09", "The Hermit Thoth Tarot card")}<div><h3>Physical card reading</h3><p>Choose a spread, name the cards you drew, add your question and continue with a guided interpretation.</p></div></div></div></section>

      <section id="method" class="funnel"><div class="band"><p class="eyebrow">Free first, deeper by choice</p><h2 class="section-title">Value arrives before the invitation to register.</h2><p class="section-intro">A free conversation and basic response let you see the reader’s approach. When you want a full reading, create an account to keep it and receive three additional free readings.</p><div class="funnel-steps"><div class="funnel-step"><b>01 · Start</b><p>Ask a question and receive a short response.</p></div><div class="funnel-step"><b>02 · Deepen</b><p>Enter a guided ritual and reveal the full reading.</p></div><div class="funnel-step"><b>03 · Keep it</b><p>Create an account when the reading has earned its place.</p></div><div class="funnel-step"><b>04 · Return</b><p>Keep the thread, use your free readings, come back to the story.</p></div></div></div></section>

      <section class="band"><div class="section-head"><div><p class="eyebrow">The content graph</p><h2 class="section-title">A journal that leads back to a question.</h2></div><a class="button button-quiet" href="${routes.blog}">Visit the journal</a></div><div class="content-grid"><a class="article" href="${routes.article}"><small>Card meaning</small><h3>The Lovers: choosing without dividing yourself</h3></a><a class="article" href="${routes.cards}"><small>Card library</small><h3>Read the images, correspondences and meanings</h3></a><a class="article" href="${routes.spreads}"><small>Ritual guide</small><h3>Which spread helps a difficult decision?</h3></a></div></section>

      <section class="band faq"><div><p class="eyebrow">A clear boundary</p><h2 class="section-title">Mystical does not have to mean misleading.</h2></div><div class="faq-list"><details class="faq-item"><summary>Is this a prediction?</summary><p>No. Tarot can be a reflective language for questions, patterns and choices. It does not guarantee future events or scientific certainty.</p></details><details class="faq-item"><summary>What does the reader remember?</summary><p>When you choose to create an account, it can retain your questions, readings and selected context to support follow-ups. You can manage or delete it.</p></details><details class="faq-item"><summary>Do I need a Tarots.chat deck?</summary><p>No. You can use the Thoth deck in the digital ritual or draw from your own physical Tarot deck and enter the cards you pulled.</p></details><details class="faq-item"><summary>Why create an account after the first experience?</summary><p>Registration is where a reading becomes part of your story: it saves the full reading, unlocks the additional free readings and lets memory work for you.</p></details></div></section>

      <section class="final"><div class="band"><p class="eyebrow">The first step is simple</p><h2 class="display">Ask the question that has been waiting.</h2><p>Come into the ritual. Let the cards speak. Return when life gives the question a new shape.</p><a class="button button-brass" href="${routes.read}">Start your free reading</a></div></section>
    </main>${footer()}`;
  }

  function read() {
    const query = new URLSearchParams(location.search).get("question") || new URLSearchParams(location.search).get("topic") || "";
    const seeded = query ? `<p class="message message-user">${clean(query)}</p><p class="message">Thank you for naming that. Before we draw, what feels most alive in this question right now?</p>` : `<p class="message">Tell me what is on your mind. A few honest words are enough to begin.</p>`;
    return `${header("read")}<main id="main"><section class="subhero"><p class="eyebrow">A free beginning</p><h1 class="display">Start with the question, not the account.</h1><p class="section-intro">This V2 reading shows the intended flow: conversation first, a basic response, then a ritual you can choose to deepen.</p></section><section class="band"><div class="read-layout"><section class="read-panel"><p class="eyebrow">Conversation</p><h2>What is present for you?</h2><div id="conversation" class="conversation">${seeded}</div><form id="conversation-form" class="input-row"><label class="skip" for="conversation-input">Your response</label><input id="conversation-input" maxlength="1000" placeholder="Write a little more…"><button class="button" type="submit">Send</button></form><div id="full-reading-offer" class="notice">A short response is available without registration. When you are ready, enter the ritual for the full reading.</div></section><section class="read-panel dark"><p class="eyebrow">Your ritual</p><div id="ritual-console" class="ritual-console"><div><p id="ritual-status" class="console-status">The deck is waiting</p><p id="ritual-copy" class="console-copy">When you are ready, begin the shuffle. You can interrupt it yourself.</p><button id="ritual-action" class="button button-brass" type="button">Begin the shuffle</button><div id="fan" class="fan hidden" aria-label="Choose one card from the fan"><button type="button" data-card="maj-06"><img src="/cards/dorso.webp" alt="Choose card one"></button><button type="button" data-card="maj-17"><img src="/cards/dorso.webp" alt="Choose card two"></button><button type="button" data-card="maj-02"><img src="/cards/dorso.webp" alt="Choose card three"></button></div><div id="reveal" class="reveal hidden" aria-live="polite"></div></div></div></section></div><p class="notice">The full production reader can reuse the existing reading APIs: anonymous opening, interview, interruptible fan, selection, reveal streaming, synthesis, sharing and memory. This isolated static V2 demonstrates the conversion and ritual UI without changing those services.</p></section></main>${footer()}`;
  }

  function decks() {
    return `${header("decks")}<main id="main"><section class="subhero"><p class="eyebrow">A multi-deck home</p><h1 class="display">Each deck is a language with its own atmosphere.</h1><p class="section-intro">Deck pages are not shop shelves. They are entrances into an image system, a card library, readings and a physical ritual.</p></section><section class="band deck-layout"><div class="deck-spread" aria-hidden="true">${card("maj-00", "")}${card("maj-06", "")}${card("maj-19", "")}</div><div><span class="available">Available now</span><h2 class="section-title">Thoth Tarot</h2><p class="section-intro">A complete 78-card visual language, read through the guided ritual and the context you bring.</p><a class="button" href="${routes.thoth}">Enter the Thoth deck</a></div></section><section class="band band-tight"><p class="eyebrow">In development</p><div class="difference-grid"><article class="difference"><span>♡</span><h3>The Lovers</h3><p>Planned. A future deck, not currently selectable for readings.</p></article><article class="difference"><span>✺</span><h3>Italian Celebration</h3><p>Planned. A future deck, not currently selectable for readings.</p></article><article class="difference"><span>☾</span><h3>Halloween Tarots</h3><p>Planned. A future deck, not currently selectable for readings.</p></article><article class="difference"><span>✡</span><h3>Jewish Secrets</h3><p>Planned. A future deck, not currently selectable for readings.</p></article></div></section></main>${footer()}`;
  }

  function thoth() {
    return `${header("decks")}<main id="main"><section class="subhero"><span class="available">Available now</span><p class="eyebrow">The Thoth Tarot</p><h1 class="display">A deck of vivid symbols, held inside a personal question.</h1><p class="section-intro">Explore the image language, draw in the guided ritual, or bring a physical draw to the reader.</p></section><section class="band deck-layout"><div class="deck-spread" aria-hidden="true">${card("maj-02", "")}${card("maj-06", "")}${card("maj-17", "")}</div><div><h2 class="section-title">Your deck. Your ritual. Your reader.</h2><p class="section-intro">The Thoth Tarot is the current active deck. Its card library, readings, article links and future printable/physical materials lead into one shared personal story.</p><div class="minor-cta"><a href="${routes.read}?deck=thoth">Start a Thoth reading</a><a href="${routes.cards}">Open the card library</a><a href="${routes.physical}?deck=thoth">Read physical cards</a></div></div></section><section class="band band-tight"><div class="cards-grid">${[["maj-00", "The Fool"], ["maj-02", "The High Priestess"], ["maj-06", "The Lovers"], ["maj-09", "The Hermit"], ["maj-17", "The Star"], ["maj-19", "The Sun"]].map(([id, name]) => `<a class="card-tile" href="${id === "maj-06" ? routes.lovers : routes.cards}">${card(id, `${name}, Thoth Tarot card`)}<span>${name}</span></a>`).join("")}</div></section></main>${footer()}`;
  }

  function cards() {
    const cards = [["maj-00", "The Fool"], ["maj-01", "The Magus"], ["maj-02", "The High Priestess"], ["maj-06", "The Lovers"], ["maj-09", "The Hermit"], ["maj-11", "Lust"], ["maj-17", "The Star"], ["maj-19", "The Sun"], ["maj-21", "The Universe"]];
    return `${header("decks")}<main id="main"><section class="subhero"><p class="eyebrow">Thoth Tarot card library</p><h1 class="display">See the card before you ask it to speak.</h1><p class="section-intro">A V2 card page connects visual detail and meaning with an article, a deck, a question and a reading — without leaving the V2 experience.</p></section><section class="band"><div class="cards-grid">${cards.map(([id, name]) => `<a class="card-tile" href="${id === "maj-06" ? routes.lovers : `${routes.cards}?card=${id}`}">${card(id, `${name}, Thoth Tarot card`)}<span>${name}</span></a>`).join("")}</div></section></main>${footer()}`;
  }

  function lovers() {
    return `${header("decks")}<main id="main"><section class="subhero"><p class="eyebrow">Thoth Tarot · Major Arcana</p><h1 class="display">The Lovers: a choice that asks for wholeness.</h1><p class="section-intro">A card page gives the image room to be seen, then provides a path toward reflection or a full reading.</p></section><section class="band deck-layout"><div>${card("maj-06", "The Lovers, a Thoth Tarot card")}</div><div><p class="eyebrow">A reflective starting point</p><h2 class="section-title">What are you being asked to bring together?</h2><p class="section-intro">The Lovers can open a conversation about commitment, desire, values and the choices that make a life feel internally coherent. Meaning changes with the position, the surrounding cards and your question.</p><a class="button" href="${routes.read}?deck=thoth&card=the-lovers">Read this card in a ritual</a><div class="minor-cta"><a href="${routes.article}">Read the related journal piece</a><a href="${routes.thoth}">Back to the Thoth deck</a></div></div></section></main>${footer()}`;
  }

  function physical() {
    return `${header("read")}<main id="main"><section class="subhero"><p class="eyebrow">Physical Tarot mode</p><h1 class="display">Your hands draw the cards. The reader helps you hear the pattern.</h1><p class="section-intro">Choose a simple spread, record the cards you actually drew, then add your question. This path complements the existing manual-card reading API rather than inventing a second model.</p></section><section class="band"><div class="read-layout"><section class="read-panel"><p class="eyebrow">1 · Place the cards</p><h2>Three-card reflection</h2><div class="cards-grid" style="grid-template-columns:repeat(3,1fr)">${[["maj-06", "What binds"], ["maj-09", "What clarifies"], ["maj-17", "What opens"]].map(([id, name]) => `<button class="card-tile manual-card" type="button" data-name="${name}" data-card="${id}">${card(id, `${name}, selected physical card`)}<span>${name}</span></button>`).join("")}</div><p id="physical-selection" class="notice">Select a position to name the card you drew.</p></section><section class="read-panel dark"><p class="eyebrow">2 · Give it a question</p><h2>What should the cards help you examine?</h2><textarea id="physical-question" rows="5" placeholder="Write your question in your own words…"></textarea><p id="physical-answer" class="console-copy">Your physical draw remains yours. The interpretation begins when you name what you want to understand.</p><button id="physical-start" class="button button-brass" type="button">Interpret my cards</button></section></div></section></main>${footer()}`;
  }

  function explore() {
    return `${header("explore")}<main id="main"><section class="subhero"><p class="eyebrow">Explore the Tarot</p><h1 class="display">Follow an image to a meaning, then back to your own question.</h1><p class="section-intro">V2 treats the journal, cards, spreads and decks as a connected content graph — not disconnected pages.</p></section><section class="band"><div class="content-grid"><a class="article" href="${routes.article}"><small>Journal</small><h3>The Lovers and the courage to choose</h3></a><a class="article" href="${routes.lovers}"><small>Card</small><h3>See The Lovers in the Thoth library</h3></a><a class="article" href="${routes.spreads}"><small>Spread</small><h3>Find a ritual for a difficult decision</h3></a></div></section></main>${footer()}`;
  }

  function blog() {
    return `${header("explore")}<main id="main"><section class="subhero"><p class="eyebrow">The journal</p><h1 class="display">Ideas to sit with, not answers to consume.</h1><p class="section-intro">Articles connect to cards, deck imagery, questions and readings. Every internal destination stays inside V2.</p></section><section class="band"><div class="content-grid"><a class="article" href="${routes.article}"><small>Choice · The Lovers</small><h3>The Lovers: choosing without dividing yourself</h3></a><a class="article" href="${routes.lovers}"><small>Card library</small><h3>What changes when a card appears in a position?</h3></a><a class="article" href="${routes.read}?topic=A difficult decision"><small>Reading ritual</small><h3>Ask a difficult decision a more useful question</h3></a></div></section></main>${footer()}`;
  }

  function article() {
    return `${header("explore")}<main id="main"><article><section class="subhero"><p class="eyebrow">Card meaning · The Lovers</p><h1 class="display">Choosing without dividing yourself.</h1><p class="section-intro">The Lovers is not simply a question of romance. It can ask how desire, values and action might stop pulling in opposite directions.</p></section><section class="band" style="max-width:850px"><p>When a card appears in a reading, it does not arrive as a sealed verdict. Its role is shaped by the question, its position and the other symbols around it. The Lovers can be useful when a decision has been reduced to two impossible sides.</p><p>Instead of asking which side will win, try asking: what must be honoured for this choice to feel whole? What relation, promise or image of yourself is already involved?</p><aside class="memory-card"><p>Bring the card into a question. The ritual makes the interpretation specific.</p></aside><p>From here, you can read the image in the card library, explore the Thoth deck or start a personal reading. These are V2 routes, designed to preserve the path rather than sending you to a different site experience.</p><div class="minor-cta"><a href="${routes.lovers}">Explore The Lovers card</a><a href="${routes.read}?deck=thoth&card=the-lovers">Read with this card</a><a href="${routes.thoth}">Explore the Thoth deck</a></div></section></article></main>${footer()}`;
  }

  function story() {
    return `${header("story")}<main id="main"><section class="subhero"><p class="eyebrow">Your reader remembers your story</p><h1 class="display">A private thread you can return to, edit or release.</h1><p class="section-intro">This page makes memory visible and manageable. Example entries are illustrative; account-backed memory remains provided by the existing profile APIs.</p></section><section class="band story-grid"><aside class="story-sidebar"><h2>What is remembered</h2><p>Questions, readings, selected themes and outcomes can be retained to make follow-ups meaningful.</p><a class="button button-quiet" href="${routes.profile}">Manage memory</a></aside><section class="story-main"><h2>Your recent thread</h2><article class="memory-entry"><small>Relationship · 7 days ago</small><h3>How will this relationship develop?</h3><p>You noticed uncertainty around a choice. The reader asked you to watch for the moment where reassurance replaces a real conversation.</p><a href="${routes.read}?topic=Relationship">Continue this conversation</a></article><article class="memory-entry"><small>Career · 21 days ago</small><h3>Should I leave the role I have?</h3><p>You wanted to distinguish exhaustion from a genuine change of direction. A follow-up can compare what has shifted since then.</p><a href="${routes.read}?topic=Career">Return to this question</a></article></section></section></main>${footer()}`;
  }

  function pricing() {
    return `${header("read")}<main id="main"><section class="subhero"><p class="eyebrow">Readings, packages and subscriptions</p><h1 class="display">Choose continuity when it has become useful.</h1><p class="section-intro">The product priority is not deck merchandising. It is a reading practice you can return to: free entry, deeper readings, packages and subscriptions.</p></section><section class="band"><div class="pricing-grid"><article class="plan"><h2>Free beginning</h2><p class="price">$0</p><p>Try the conversation and basic reading. Create an account after value has been demonstrated.</p><ul><li>Free first reading</li><li>Three additional free readings after signup</li><li>Save a full reading when registered</li></ul><a class="button button-quiet" href="${routes.read}">Start free</a></article><article class="plan featured"><h2>Reading package</h2><p class="price">Packages</p><p>For the moments you want to return to a question, without changing your pace.</p><ul><li>Full guided rituals</li><li>Saved readings and shares</li><li>Use with active decks</li></ul><a class="button button-brass" href="${routes.read}">Choose a package</a></article><article class="plan"><h2>Ongoing reader</h2><p class="price">Subscription</p><p>For a continuing practice, with memory and follow-up at the centre.</p><ul><li>Repeat readings</li><li>Memory-aware follow-ups</li><li>Manage your story</li></ul><a class="button button-quiet" href="${routes.story}">See your story</a></article></div><p class="notice">Live plan names, prices, checkout and entitlement checks must remain backed by the existing plans and checkout APIs; this static V2 uses no invented commercial claims.</p></section></main>${footer()}`;
  }

  function shop() {
    return `${header("shop")}<main id="main"><section class="subhero"><p class="eyebrow">Deck and printable ritual</p><h1 class="display">A physical extension, not the reason you came.</h1><p class="section-intro">A deck or PDF can make the ritual tangible and bring a QR entry back to a reading, but readings, packages and continuity remain the primary experience.</p></section><section class="band"><div class="shop-grid"><article class="shop-object">${card("dorso", "Back of the Tarots.chat Thoth deck")}<div><h2>Physical deck</h2><p>Premium deck presentation belongs here, after the reader has shown its value. Availability and price should come from the existing deck/order API.</p><a class="button button-quiet" href="${routes.thoth}">Explore the active deck</a></div></article><article class="shop-object">${card("maj-06", "The Lovers, printable card") }<div><h2>Printable PDF</h2><p>Continue a ritual offline, then use a QR or direct V2 link to bring a physical draw into the reader.</p><a class="button button-quiet" href="${routes.physical}?deck=thoth&source=qr">Continue with your cards</a></div></article></div></section></main>${footer()}`;
  }

  function daily() {
    return `${header("read")}<main id="main"><section class="subhero"><p class="eyebrow">Card of the day</p><h1 class="display">A small encounter, available without an account.</h1><p class="section-intro">The live daily-card result is provided by the existing API. V2 uses this page as a self-contained route and an entry to a deeper question.</p></section><section class="band deck-layout"><div>${card("maj-17", "The Star, Thoth Tarot card")}</div><div><p class="eyebrow">The Star</p><h2 class="section-title">Where can you make room for a quieter kind of hope?</h2><p class="section-intro">Take the image as a reflective prompt, not a promise. If something specific is asking for attention, bring it into a reading.</p><a class="button" href="${routes.read}">Ask a fuller question</a></div></section></main>${footer()}`;
  }

  function spreads() {
    return `${header("explore")}<main id="main"><section class="subhero"><p class="eyebrow">Spreads</p><h1 class="display">Choose a shape that helps the question unfold.</h1><p class="section-intro">The existing spread API remains the source for live names, positions and layouts. V2 keeps its internal destinations inside V2.</p></section><section class="band"><div class="difference-grid"><a class="difference" href="${routes.read}?spread=three-cards"><span>III</span><h3>Three-card reflection</h3><p>What binds, what clarifies, what opens.</p></a><a class="difference" href="${routes.read}?spread=decision"><span>↔</span><h3>Difficult decision</h3><p>Make the tension between paths visible.</p></a><a class="difference" href="${routes.read}?spread=relationship"><span>☌</span><h3>Relationship</h3><p>Bring the dynamic into a shared frame.</p></a><a class="difference" href="${routes.physical}"><span>✋</span><h3>Physical draw</h3><p>Place the cards you already pulled.</p></a></div></section></main>${footer()}`;
  }

  function shared() {
    return `${header("explore")}<main id="main"><section class="subhero"><p class="eyebrow">A shareable reading</p><h1 class="display">Share an opening, and give someone else a way in.</h1><p class="section-intro">The existing sharing and referral service keeps the real attribution and credits. V2 makes the destination a V2 reading rather than a V1 page.</p></section><section class="band"><div class="static-share"><q>“The part I needed was not an answer. It was a better question.”</q><p>Shared from a personal Tarot reading. The reading stays private; this is only an invitation to begin.</p><button id="share-button" class="button button-brass" type="button">Copy V2 invitation link</button><p id="share-result" aria-live="polite"></p></div></section></main>${footer()}`;
  }

  function profile() {
    return `${header("story")}<main id="main"><section class="subhero"><p class="eyebrow">Your account</p><h1 class="display">Your story is yours to manage.</h1><p class="section-intro">This V2 profile entry is designed around continuity: readings, memory, referral credits and physical-deck details are arranged as parts of one personal story.</p></section><section class="band story-grid"><aside class="story-sidebar"><h2>Account actions</h2><p>Sign in, profile and account security continue to be governed by the existing authentication layer.</p><a class="button button-quiet" href="${routes.story}">View your story</a></aside><section class="story-main"><h2>Manage what the reader knows</h2><article class="memory-entry"><small>Memory</small><h3>Review, edit or delete retained context</h3><p>Explain what is remembered and why before showing any controls. Existing memory APIs remain the back-end contract.</p></article><article class="memory-entry"><small>Referral</small><h3>Share an invitation and earn reading credits</h3><p>Use V2 share destinations while preserving existing referral attribution and server-side credit rules.</p><a href="${routes.shared}">Open your V2 invitation</a></article><article class="memory-entry"><small>Physical ritual</small><h3>Decks, PDFs and delivery details</h3><p>Keep these secondary to the reading journey, but easy to find when relevant.</p><a href="${routes.shop}">Visit deck &amp; PDF</a></article></section></section></main>${footer()}`;
  }

  const renderers = {
    "/v2": home, "/v2/index.html": home, "/v2/read/index.html": read, "/v2/decks/index.html": decks,
    "/v2/decks/thoth/index.html": thoth, "/v2/cards/index.html": cards, "/v2/cards/the-lovers/index.html": lovers,
    "/v2/physical-reading/index.html": physical, "/v2/explore/index.html": explore, "/v2/blog/index.html": blog,
    "/v2/blog/the-lovers-and-choice/index.html": article, "/v2/my-story/index.html": story, "/v2/pricing/index.html": pricing,
    "/v2/shop/index.html": shop, "/v2/daily-card/index.html": daily, "/v2/spreads/index.html": spreads,
    "/v2/shared/index.html": shared, "/v2/profile/index.html": profile,
  };

  function bindHome() {
    const form = byId("hero-question");
    if (!form) return;
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const input = byId("hero-question-input");
      const question = input.value.trim();
      if (question.length < 3) { input.focus(); return; }
      analytics("question_submitted", { entry: "hero" });
      const response = byId("quick-response");
      response.classList.remove("hidden");
      response.innerHTML = `<strong>A first thought:</strong> “${clean(question)}” is worth slowing down for. A full reading can put this question into a chosen spread and let you take part in the draw. <a href="${routes.read}?question=${encodeURIComponent(question)}">Continue into the ritual</a>.`;
    });
    analytics("landing_view");
  }

  function bindRead() {
    const form = byId("conversation-form");
    if (form) form.addEventListener("submit", (event) => {
      event.preventDefault();
      const input = byId("conversation-input");
      const text = input.value.trim();
      if (!text) return;
      const thread = byId("conversation");
      thread.insertAdjacentHTML("beforeend", `<p class="message message-user">${clean(text)}</p><p class="message">I hear that this matters. Let the cards give the question another surface: choose when to stop the shuffle, then choose a card.</p>`);
      input.value = ""; analytics("conversation_started");
    });
    const action = byId("ritual-action");
    if (!action) return;
    let stage = "waiting";
    action.addEventListener("click", () => {
      const status = byId("ritual-status"), copy = byId("ritual-copy"), fan = byId("fan");
      if (stage === "waiting") { stage = "shuffling"; status.textContent = "The deck is moving"; copy.textContent = "Let it move for a moment. When it feels right, interrupt the shuffle."; action.textContent = "Interrupt the shuffle"; analytics("shuffle_started"); return; }
      if (stage === "shuffling") { stage = "choose"; status.textContent = "The fan is open"; copy.textContent = "Cut has been made. Choose one card from the fan."; action.classList.add("hidden"); fan.classList.remove("hidden"); analytics("shuffle_interrupted"); analytics("deck_cut"); }
    });
    document.querySelectorAll("#fan button").forEach((button) => button.addEventListener("click", () => {
      document.querySelectorAll("#fan button").forEach((entry) => entry.setAttribute("aria-pressed", "false"));
      button.setAttribute("aria-pressed", "true");
      const id = button.dataset.card;
      const meanings = { "maj-06": ["The Lovers", "A choice becomes clearer when you ask what must remain whole."], "maj-17": ["The Star", "Make room for a small, honest hope instead of demanding certainty."], "maj-02": ["The High Priestess", "Not everything needs to be named at once; listen for what is still forming."] };
      const reveal = byId("reveal");
      reveal.classList.remove("hidden");
      reveal.innerHTML = `${card(id, `${meanings[id][0]}, revealed Thoth Tarot card`)}<div><h3>${meanings[id][0]}</h3><p>${meanings[id][1]} This is a short V2 preview; a full reading interprets positions and combinations in context.</p><a class="button button-small" href="${routes.profile}">Get the full reading free</a></div>`;
      byId("ritual-status").textContent = "One card revealed"; byId("ritual-copy").textContent = "You made the selection. Continue after creating an account when you want to keep the full reading."; analytics("card_drawn"); analytics("card_revealed");
    }));
  }

  function bindPhysical() {
    let selected = null;
    document.querySelectorAll(".manual-card").forEach((button) => button.addEventListener("click", () => {
      selected = button.dataset.name;
      document.querySelectorAll(".manual-card").forEach((entry) => entry.style.outline = "none");
      button.style.outline = "3px solid #19706f";
      byId("physical-selection").textContent = `${selected} is ready for your physical draw. You can replace this selection before interpreting.`;
      analytics("physical_reading_started");
    }));
    const start = byId("physical-start");
    if (start) start.addEventListener("click", () => {
      const question = byId("physical-question").value.trim();
      const answer = byId("physical-answer");
      if (!selected || question.length < 3) { answer.textContent = "Choose a card position and add a question before beginning the interpretation."; return; }
      answer.textContent = `You placed “${selected}” beside “${question}”. A full interpretation can now use the existing manual-card reading flow to combine the positions, the cards and your context.`;
      analytics("question_submitted", { entry: "physical" });
    });
  }

  function bindShare() {
    const button = byId("share-button");
    if (!button) return;
    button.addEventListener("click", async () => {
      const value = `${location.origin}${routes.read}?source=share`;
      try { await navigator.clipboard.writeText(value); byId("share-result").textContent = "V2 invitation link copied."; } catch { byId("share-result").textContent = value; }
      analytics("share_completed", { destination: "v2" });
    });
  }

  /* `/v2/read`, `/v2/read/` and `/v2/read/index.html` are the same page: the server rewrites the clean
   * forms to the file, so the router must accept all three. */
  const pulito = location.pathname.replace(/\/index\.html$/, "").replace(/\/$/, "") || "/v2";
  const path = pulito === "/v2" ? "/v2" : `${pulito}/index.html`;
  const view = renderers[path] || home;
  document.title = ({ home: "Tarots.chat V2 — a living Tarot ritual", read: "Start a free Tarot reading — Tarots.chat V2", decks: "Tarot decks — Tarots.chat V2", thoth: "Thoth Tarot — Tarots.chat V2", cards: "Card library — Tarots.chat V2", lovers: "The Lovers — Tarots.chat V2", physical: "Read your physical cards — Tarots.chat V2", story: "My story — Tarots.chat V2" })[view.name] || "Tarots.chat V2";
  byId("app").innerHTML = view();
  bindHome(); bindRead(); bindPhysical(); bindShare();
})();
