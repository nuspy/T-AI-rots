# Prompts for TAROTS blog pictures

## Why this file exists
The blog's covers went wrong twice. First they were all one picture: a table, candles, tarot cards laid out. Then
an agent wrote one fixed prompt per section ("mystical tarot card spread on a velvet tablecloth…", "open journal
with tarot cards…") and made about fifty covers out of six prompts: cards everywhere, the same picture over and
over, sometimes the very same file on two articles. A reader scrolling the blog sees the same thing again and
learns nothing about any article.

Every picture must now answer one question: **what is this article about, seen rather than said?**

## Zero cards
**No blog picture shows a card. None, of any kind, not even one small card as a detail**: no tarot card, no deck,
no spread, no arcana, no reading table, no playing or oracle card, no card tucked in a book or on a mirror.

Why: the whole site is about cards, so a card in the picture adds nothing the title has not said; every image
model turns "tarot" into the same deck on the same table; and the card pictures are exactly what the operator
asked to remove. The article's card, spread or symbol is shown through **its world**: the places, people,
seasons, objects and metaphors it speaks about.

`tarots_images.py` refuses (exit 7, nothing generated, nothing spent):
- any prompt with the word **tarot**, a **card** or **cards**, a **deck** (a ship's deck or a deck chair is fine),
  a **spread**, the **arcana**, a **reading table**, Rider-Waite, Thoth trumps, cartomancy;
- the **name of a card** in the prompt (*Queen of Cups*, *High Priestess*, *Hanged Man*, *Wheel of Fortune*…):
  describe what the card is about instead. Do not write "The Tower" or "The Empress" in the prompt either, even
  though the script cannot catch every name: the model paints a card frame around them;
- an **alt text** that describes cards (the article's keyword may still appear in it, if it fits naturally).

## Read the article first, then write the prompt
```
python scripts/tarots_images.py show <id>
```
Read the whole text. The prompt is written **for this article and no other**, and it **names at least one concrete
thing from the text**: a place, an image the author uses, a situation, a season, an object, a gesture. If the
same prompt could illustrate another article of the blog, it is not finished.

Find the subject in this order:
1. **The human situation** the article speaks to: a first date, a break-up, waiting for news, a hard choice,
   grief, a new job, a friendship, a creative block, a return home. This gives the strongest pictures.
2. **The card's own world**, as a real scene: the Tower → a lighthouse in a storm; the Empress → a summer garden.
3. **The season or the sky** when the article is tied to a moment: equinox, solstice, a full or new moon.
4. **An object charged with meaning**, alone and well lit: an old key, a letter with a broken seal, two rings.
5. **A visual metaphor**: two paths in a wood, a door ajar, a bird leaving a cage, a thread between two cups.

## Variety: the rule to apply by yourself
Every picture first picks **one kind** from this list:

| Kind | For example |
|---|---|
| landscape or sky | a coast, a field, a mountain pass, a night sky, weather |
| architecture or place | a lighthouse, a cloister, a station, a greenhouse, a stair, a bridge |
| person from behind or far away | never a recognisable face, never a real person |
| symbolic object in a still life | outdoors or on a sill, never on the "reading table" |
| natural detail, close-up | a seed head, frost on a leaf, a shell, a cracked stone, bark |
| abstract visual metaphor | lights forming a pattern, threads, doors, mirrors of water |
| everyday life scene | a kitchen at dawn, a bus stop in the rain, a market, a garden chore |
| symbolic animal | a heron, a fox in snow, an owl, a horse in a field, bees |

- **Never the same kind as any of the last 3 pictures.** `python scripts/tarots_images.py progress` shows the last
  pictures generated, newest first: read it before every prompt.
- Inside the house style, change from the previous pictures the **time of day** (dawn, noon, dusk, night), the
  **light** (low sun, overcast, storm, moonlight, lamplight), the **season** and the **dominant colour** (plum
  dusk, brass autumn, verdigris sea, paper-white winter).
- **Never as a default scene**: a table with candles, an open book with a candle, a desk. They are what an agent
  writes when it has not read the article. Use one only if the article itself is about that place, and then not
  twice in the blog.
- `generate` refuses a prompt that shares 45% or more of its content words with any prompt already generated, and
  shows the closest one. There is no option to skip this: write a different scene, not the same one with three
  words changed. A regeneration after a bad result is a new prompt too.
- `generate` refuses a prompt with fewer than 12 content words once the house style and the empty words
  ("mystical", "ethereal", "atmosphere", "professional photography"…) are taken out: *describe a concrete scene
  from this article*.

## Never in series
- **One prompt per picture, written for that article.** Never one prompt per section, per category or per card
  suit; never a template with the title pasted in; never a list of prompts reused across articles.
- **Never write your own script to generate or publish in series** (a loop, a batch file, a "publish_sequential"
  helper). One article at a time, with this skill's commands, looking at each picture before using it.
- Check a prompt before spending anything: `python scripts/tarots_images.py prompt-check --prompt "…" --alt "…"`.

## How pictures are generated
Only with `python scripts/tarots_images.py generate …`, which calls the **`litmedia-skill`** (LitMedia API,
Seedream 5.0, 2K). Never `browser-image-gen`, never the agent's own built-in image tool, never the LitMedia
website in a browser. If LitMedia does not answer or fails: no picture, and say so in the report. Do not look
for another way.

## House style (append to every prompt, unchanged)
```
editorial painterly illustration, soft natural light, warm paper-cream highlights, deep plum shadows, touches of
brass gold and verdigris green, gentle film grain, calm composition with breathing space, contemplative mood,
no text, no letters, no numbers, no watermark, no logo
```
The palette is the site's own (paper `#f4efe5`, plum `#3c1846`, brass `#b28336`, verdigris `#19706f`): the pictures
sit on that background and must feel at home there. The words of this line do not count as content for the checks
above, so they never make two prompts look alike and never make a thin prompt long enough.

## Shape
- Cover: `--aspect 3:2`, one clear focal point a little off-centre, nothing important at the far edges (the lists
  crop to a thumbnail).
- Picture in the text: `--aspect 4:3`, or `1:1` for a close-up. It illustrates the paragraph it follows and is a
  different kind of picture from the cover.

## Prompt recipe
`<kind> + <subject from the article, with one concrete element of the text> + <setting, time, season, light> +
<composition and distance> + <house style>`

### Examples (none of them has a card)
- *The Tower in the Thoth deck* (cover, architecture or place; the card through its world):
  "A lighthouse on a black basalt cliff in a winter storm, one bolt of lightning splitting the sky, a crack running
  down the white tower and warm light pouring out through it, waves breaking on the rocks, seen from a fishing
  harbour far below at night, " + house style.
- *The Empress in love* (cover, person from behind):
  "A couple seen from behind walking through a high summer meadow full of poppies and ripe wheat, her hand resting
  on her belly, a stone farmhouse and fruit trees far away, golden late-afternoon light, wide view, " + house style.
- *The Celtic Cross spread, position by position* (inline 4:3, abstract metaphor, never cards):
  "Ten small brass lanterns hanging in a dark orchard at night, six forming a cross and four rising in a column
  beside it, thin threads of light joining them in order, seen from slightly above like a constellation, cool
  verdigris night air, " + house style.
- *A three-card spread for a decision* (cover, landscape, the spread as a metaphor):
  "Three stepping stones crossing a shallow river at dawn, the first half in mist, the second wet and shining, the
  third on the far bank under a birch tree, a walker's boots on the first stone, early spring, " + house style.
- *Tarot journaling for beginners* (cover, everyday life; the journal outdoors, not on a desk):
  "A woman seen from behind sitting on the steps of a seaside house at sunrise, a closed linen notebook on her
  knees and a pencil behind her ear, wet sand, gulls, a mug steaming on the step beside her, " + house style.
- *Shadow work* (cover, natural detail):
  "Close-up of a fern unfurling in the deep shade of a stone wall, one ray of low autumn sun reaching its tip, moss,
  dew, the rest of the frame in soft plum shadow, " + house style.
- *The autumn equinox* (cover, landscape):
  "An orchard at the autumn equinox, half the trees still green and half turned gold, a wooden ladder leaning on a
  tree, a basket of apples, low sun exactly on the horizon, " + house style.
- *The full moon in Pisces* (cover, symbolic animal):
  "A grey heron standing still in a flooded meadow under a full moon, the moon doubled in the water, mist over the
  reeds, a line of willows behind, late winter night, " + house style.
- *Five of Cups, grief* (cover, person far away; the card's name is not in the prompt):
  "A lone figure in a dark coat on a stone bridge in soft rain, three overturned glasses on the parapet, two full
  glasses still standing behind them catching the last light, a river and a distant village at dusk, seen from a
  distance, " + house style.

## Refuse, regenerate or rewrite if
- the picture shows a card anyway, or anything that looks like one (a framed rectangle with a figure, a deck);
- there is text, letters, numbers or a logo anywhere (even fake writing);
- hands or faces are malformed, or a face looks like a real, recognisable person;
- it looks like a stock photo or like the actual Thoth deck artwork;
- it could illustrate any other article just as well.

## Alt text
Describe what is in the picture, for someone who cannot see it, 8–125 characters:
"A lone figure on a stone bridge in the rain, three glasses overturned and two still standing". The keyword only if
it fits naturally; never a list of keywords; never "tarot cards" (there are none in the picture, and the script
refuses it).
