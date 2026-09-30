# Prompts for TAROTS blog pictures

## Why this file exists
The first covers of the blog were all the same picture: a table, candles, tarot cards laid out. A reader scrolling
the blog sees twelve times the same thing and learns nothing about any article. Every picture must now answer one
question: **what is this article about, seen rather than said?**

## Find the subject (in this order)
1. **The human situation** the article speaks to: a first date, a break-up, waiting for news, a hard choice, grief,
   a new job, a friendship, a creative block, a return home. This gives the strongest pictures.
2. **The card's own world**, translated into a real scene instead of the card itself:
   - The Empress → an overgrown summer garden, ripe fruit, a pregnant woman seen from behind among wheat.
   - The Tower → a lighthouse in a storm, a wall cracking open to let light in, a city skyline after lightning.
   - Ace of Cups → a spring overflowing into a stone basin at dawn, a single water lily opening.
   - Five of Cups → a figure on a bridge in the rain looking at spilled glasses, and two standing ones behind.
   - The Star → a woman pouring water into a lake under a clear night full of stars, seen from far away.
   - Queen of Cups → a seaside house at dusk, a woman on the steps listening to the tide.
3. **The season or the sky** when the article is tied to a moment: equinox light across a field, a winter
   solstice window with one candle, a full moon over a harbour, a meteor shower above hills.
4. **An object charged with meaning**, alone and well lit: an old key, a letter with a broken seal, a pair of
   rings on a windowsill, a compass, a notebook with a pressed flower (no readable writing).
5. **A visual metaphor**: two paths in a wood, a door ajar, a thread tying two cups, a ladder towards a window,
   a bird leaving a cage.

A single tarot card may appear as a **detail** of a larger scene (a card tucked in a book, on a mirror frame), never
a spread, never several cards, never the "reading table".

## Vary across the batch
Before each prompt, look at the subjects already used in this run (`python scripts/tarots_images.py progress`).
Change at least two of: setting (indoor / city / sea / garden / mountain / sky), time (dawn / noon / dusk / night),
subject (person / object / landscape / animal), distance (close-up / medium / wide), season.

## House style (append to every prompt, unchanged)
```
editorial painterly illustration, soft natural light, warm paper-cream highlights, deep plum shadows, touches of
brass gold and verdigris green, gentle film grain, calm composition with breathing space, contemplative mood,
no text, no letters, no numbers, no watermark, no logo
```
The palette is the site's own (paper `#f4efe5`, plum `#3c1846`, brass `#b28336`, verdigris `#19706f`): the pictures
sit on that background and must feel at home there.

## Shape
- Cover: `--aspect 3:2`, one clear focal point a little off-centre, nothing important at the far edges (the lists
  crop to a thumbnail).
- Picture in the text: `--aspect 4:3`, or `1:1` for a symbol close-up. It illustrates the paragraph it follows.

## Prompt recipe
`<subject from the article> + <setting, time, season> + <composition and distance> + <house style>`

### Examples
- *Five of Cups tarot meaning (grief, what remains)*:
  "A lone figure in a dark coat on a stone bridge in soft rain, three overturned glasses on the parapet, two full
  glasses still standing behind them catching the last light, a river and a distant village at dusk, seen from a
  distance, " + house style.
- *The Empress in love*:
  "A couple seen from behind walking through a high summer meadow full of poppies and ripe wheat, her hand resting
  on her belly, a stone farmhouse and fruit trees far away, golden late-afternoon light, wide view, " + house style.
- *Tarot journaling* (inline picture):
  "Close-up of an open notebook on a windowsill with a pressed rose and a fountain pen, morning light, a single
  tarot card tucked between the pages showing only its patterned back, " + house style.
- *Autumn equinox reading*:
  "An orchard at the autumn equinox, half the trees still green and half turned gold, a wooden ladder leaning on a
  tree, a basket of apples, low sun exactly on the horizon, " + house style.

## Refuse, regenerate or rewrite if
- the picture shows cards on a table anyway, or more than one card;
- there is text, letters, numbers or a logo anywhere (even fake writing);
- hands or faces are malformed, or a face looks like a real, recognisable person;
- it looks like a stock photo or like the actual Thoth deck artwork;
- it could illustrate any other article just as well.

## Alt text
Describe what is in the picture, for someone who cannot see it, 8–125 characters:
"A lone figure on a stone bridge in the rain, three glasses overturned and two still standing". The keyword only if
it fits naturally; never a list of keywords.
