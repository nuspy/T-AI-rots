# Prompts for TAROTS blog pictures

## Why this file exists
The blog's covers went wrong twice. First they were all one picture: a table, candles, tarot cards laid out. Then
an agent wrote one fixed prompt per section ("mystical tarot card spread on a velvet tablecloth…", "open journal
with tarot cards…") and made about fifty covers out of six prompts: cards everywhere, the same picture over and
over, sometimes the very same file on two articles. A reader scrolling the blog sees the same thing again and
learns nothing about any article.

Every picture must now answer one question: **what is this article about, seen rather than said?** And with
thousands of articles to come, every picture must also **look different from the last ones**: that is what the
four dimensions below are for.

## Cards: context yes, subject never
The blog is about tarot. The names of the cards (the Sun, the Moon, the Star, the Tower, the Empress, the Wands,
the Cups, the Swords, the Disks, the Queen of Cups…) are the very world the pictures show, and a card somewhere in
the scene does no harm. What the blog never shows is **a picture of cards**.

`tarots_images.py` refuses (exit 7, nothing generated, nothing spent):
- **a card as the subject**: the prompt starts with it, or the word *card* falls in the first clause or in the
  first 8 content words, a *close-up of a card*, *a tarot card showing…*, a large or glowing card, a card in the
  foreground; also *tarot imagery/artwork/style*, a *card frame*, *Atu XVI*, a named deck's art (*Rider-Waite*,
  *Marseille tarot*): the model paints the card;
- **more than one card**: *cards*, *a deck* (a ship's deck or a deck chair is fine), *a pile/stack/pack of tarot*,
  *three cards*, *a hand of cards*, *the arcana*, *the Thoth trumps*, *tarocchi*;
- **a spread or a layout**: *a three-card spread*, *a Celtic Cross layout*, *cards on a table*, *a reading table*,
  *a tarot reading*, *a fan of cards*, *cards face down*, a cartomancer's parlour;
- **a hand holding or turning a card**.

It accepts:
- **"tarot" as an adjective of context**: *a tarot-inspired scene*, *a tarot reader walking home at dusk*;
- **the names of the cards as a world or a symbol**: *a lighthouse struck by lightning, the energy of the Tower*;
  *the Queen of Cups on a throne by the sea*; *a stone fountain overflowing in a cloister, the Ace of Cups as a
  spring*;
- **one single small card, later in the scene**: *…a coat on the chair, and on the windowsill a single card tucked
  in a notebook*.

Ordinary words are never mistaken for cards: *cardinal*, *cardigan*, *discard*, *the deck of a ship*, *wings
spread*, *a map spread out*, *a Celtic cross of stone on a hillside*, *an arcane astrolabe*.

The safest picture still shows the card **through its world**: the places, people, seasons, objects and
metaphors the article speaks about. A card is a detail at most.

## Read the article first, then write the prompt
```
python scripts/tarots_images.py show <id>
```
Read the whole text. The prompt is written **for this article and no other**, and it **names at least one concrete
thing from the text**: a place, an image the author uses, a situation, a season, an object, a gesture. If the
same prompt could illustrate another article of the blog, it is not finished. **The subject always comes from the
article**; the dimensions below only decide its form.

Find the subject in this order:
1. **The human situation** the article speaks to: a first date, a break-up, waiting for news, a hard choice,
   grief, a new job, a friendship, a creative block, a return home. This gives the strongest pictures.
2. **The card's own world**, as a real scene: the Tower → a lighthouse in a storm; the Empress → a summer garden.
3. **The season or the sky** when the article is tied to a moment: equinox, solstice, a full or new moon.
4. **An object charged with meaning**, alone and well lit: an old key, a letter with a broken seal, two rings.
5. **A visual metaphor**: two paths in a wood, a door ajar, a bird leaving a cage, a thread between two cups.

## Variety: four dimensions, declared and checked
Eight kinds of picture were too few for thousands of articles. Every `generate` (and `prompt-check`) now declares
the **form** of the picture with four required options, and the script records them in
`~/.tarots-blog/images-progress.json`:

```
--kind     what the picture shows          17 values (catalog below)
--shot     how it is framed                12 values
--light    its light                       10 values
--setting  where or when it is             free text: a place, a culture or an era, in a few words
```

17 × 12 × 10 = **2,040 forms**, times settings without end. `python scripts/tarots_images.py catalog` prints the
catalogs and what is free right now; `progress` shows the last 20 pictures with their four dimensions.

### What the script refuses
- a **kind** used by any of the **last 3** pictures;
- a **kind + shot** pair already used in the **last 20**;
- a **light** equal to one of the **last 2**; **firelight** stays rare: refused if used in the **last 10**;
- a **setting** used in the **last 10** (compared without case, accents, articles, plurals or word order:
  "The Mediterranean harbours" = "harbour, Mediterranean");
- a prompt that **does not show its choices**: it must contain one of the words of the declared light and one of
  the declared shot (listed below, in brackets), and a word of the declared setting. The house style line does not
  count ("soft natural light" is not a light choice).

Every refusal says what to change and lists the values still free. Pictures recorded before the dimensions existed
count only for the similarity check below.

### Kinds (`--kind`)
| Kind | What it shows |
|---|---|
| `landscape` | open land: a coast, a field, a mountain pass, a valley |
| `sky-and-weather` | the sky and what it does: clouds, rain, wind, a rainbow, snow falling |
| `architecture` | a building or a structure seen from outside: a lighthouse, a bridge, a cloister, a tower |
| `interior` | a room or an inside place: a kitchen, a library, a greenhouse, a stairwell |
| `street-or-market` | public everyday life: a street, a market, a station, a harbour front |
| `figure-from-behind` | one or two people seen from behind, near enough to read the gesture, no face |
| `figure-at-distance` | a person small in a large space, never recognisable |
| `hands-and-gesture` | hands doing something the article speaks of: planting, writing, holding a cup (never cards) |
| `still-life-object` | one object charged with meaning, alone and well lit: a key, a letter, two rings |
| `nature-macro` | a natural detail very close: a seed head, frost on a leaf, bark, a shell |
| `animal` | an animal that carries the article's meaning: a heron, a fox in snow, bees, a horse |
| `water-and-reflection` | a sea, a river, a pool or a puddle, and what it mirrors |
| `celestial` | the moon, the planets, the stars or an eclipse as the subject |
| `ritual-or-craft` | making or rite: weaving, pottery, bread, a procession, a lit offering |
| `abstract-symbol` | a visual metaphor: threads, doors, lights in a pattern, a labyrinth |
| `map-or-diagram` | a drawn map, a sky chart or a plan, with no readable letters or numbers |
| `journey-or-path` | a road, a path, steps, a crossing, a boat leaving |

### Shots (`--shot`), with the words the prompt must contain (one of them)
| Shot | What it is | Words |
|---|---|---|
| `wide` | the whole place, the subject small in it | wide, wide view, panoramic, vast, seen from afar, seen from a distance, far away, in the distance |
| `close-up` | the subject fills the frame | close-up, close view, up close, tight framing, detail of, seen close |
| `macro` | closer than the eye: texture, drops, fibres | macro, extreme close-up, magnified, tiny details |
| `aerial` | from high above, the land as a pattern | aerial, bird's-eye, from high above, from the air, seen from above, drone view |
| `low-angle` | from below, looking up at the subject | low angle, from below, looking up, worm's eye, seen from beneath |
| `silhouette` | the subject dark against a bright sky or window | silhouette, silhouetted, backlit, against the light, dark outline |
| `through-a-window-or-doorway` | seen through a frame in the foreground | through a window, through a doorway, through an open door, through an arch, framed by a window, window frame, door frame |
| `reflection` | the subject seen in water, glass or a mirror | reflection, reflected, mirrored, mirror, doubled in the water |
| `symmetrical` | centred, the two halves answering each other | symmetrical, symmetry, centred, perfectly balanced |
| `off-centre-negative-space` | a small subject to one side, much empty space | off-centre, negative space, empty space, to one side, small in the frame |
| `over-the-shoulder` | behind a person, seeing what they see | over the shoulder, over her/his/their shoulder |
| `top-down` | straight down on a surface or the ground | top-down, from directly above, straight down, overhead view, flat lay |

### Lights (`--light`), with the words the prompt must contain (one of them)
| Light | What it is | Words |
|---|---|---|
| `dawn` | first light, cool and clean | dawn, sunrise, daybreak, first light, early morning |
| `golden-hour` | low warm sun, long shadows | golden hour, golden light, late afternoon, low sun, sunset, evening sun |
| `midday` | high sun, short shadows, bright colours | midday, noon, high sun, full daylight, bright daylight |
| `overcast` | soft grey light, no shadows, often rain | overcast, cloudy, grey sky, grey light, diffused light, soft rain, drizzle, rain |
| `blue-hour` | after sunset, deep blue sky, first lamps | blue hour, dusk, twilight, after sunset, nightfall |
| `moonlight` | night lit by the moon | moonlight, moonlit, full moon, crescent moon, moon |
| `starlight` | night under the stars, no moon | starlight, starlit, starry, stars, milky way |
| `storm-light` | dark sky and sudden brightness | storm, stormy, lightning, thunder, thunderclouds, gale |
| `fog-or-mist` | the far things fade into white | fog, foggy, mist, misty, haze, hazy |
| `firelight` | candles, lamps, a hearth: **rare**, not twice in 10 | firelight, fire, candlelight, candle, lamplight, lantern light, hearth, embers, bonfire |

### Settings (`--setting`)
A place, a culture or an era in a few words (8 at most): "Mediterranean harbour", "Japanese garden", "Victorian
library", "desert at the edge of a salt lake", "Andean market town", "1920s Paris café", "Norwegian fjord in
winter". Choose it from the article when the article has one (a myth's country, a festival's town, a season's
landscape); otherwise choose one that suits its mood and is far from the last ten. Name it in the prompt.

## Other rules
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
- Check a prompt before spending anything:
  `python scripts/tarots_images.py prompt-check --prompt "…" --kind … --shot … --light … --setting "…" --alt "…"`.

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
above, so they never make two prompts look alike, never make a thin prompt long enough and never count as the
declared light or shot.

## Shape
- Cover: `--aspect 3:2`, one clear focal point a little off-centre, nothing important at the far edges (the lists
  crop to a thumbnail).
- Picture in the text: `--aspect 4:3`, or `1:1` for a close-up. It illustrates the paragraph it follows and has a
  different kind from the cover (the script makes sure of it if they are generated one after the other).

## Prompt recipe
`<subject from the article, with one concrete element of the text> + <the kind> + <the setting> + <the light, in
its own words> + <the shot, in its own words> + <house style>`

### Examples
Each with its options; the prompt is followed by `, ` + house style. In this order they pass every check one after
the other; in a real run the options must also be free in `progress`.
- *The Tower in the Thoth deck* (cover):
  `--kind architecture --shot low-angle --light storm-light --setting "Breton fishing coast"`
  "A lighthouse on a black basalt cliff of the Breton coast in a winter storm, one bolt of lightning splitting the
  sky, a crack running down the white tower and warm light pouring out through it, seen from the fishing harbour
  below, looking up, the sudden energy of the Tower"
- *The Empress in love* (cover):
  `--kind figure-from-behind --shot wide --light golden-hour --setting "Tuscan farmland"`
  "A couple seen from behind walking through a high summer meadow of Tuscan farmland, poppies and ripe wheat, her
  hand resting on her belly, a stone farmhouse and fruit trees far away, golden late-afternoon light, wide view,
  the abundance of the Empress"
- *The Celtic Cross spread, position by position* (inline 4:3; the spread as a metaphor, never cards):
  `--kind abstract-symbol --shot aerial --light starlight --setting "Normandy orchard"`
  "Ten small brass lanterns hanging in a Normandy orchard under the stars, six forming a cross and four rising in a
  column beside it, thin threads of light joining them in order, seen from above like a constellation"
- *A three-card spread for a decision* (cover):
  `--kind journey-or-path --shot off-centre-negative-space --light fog-or-mist --setting "Scottish Highlands river"`
  "Three stepping stones crossing a shallow Highlands river in morning mist, the first half hidden, the second wet
  and shining, the third on the far bank under a birch, a walker's boots on the first stone, small to one side of
  the frame, wide grey water around"
- *Tarot journaling for beginners* (cover; one small card allowed, later in the scene):
  `--kind hands-and-gesture --shot over-the-shoulder --light dawn --setting "Cornish seaside village"`
  "A woman's hands writing in a linen notebook on her knees, on the steps of a Cornish seaside house at sunrise,
  seen over her shoulder, wet sand and gulls below, a mug steaming on the step, a single card tucked between the
  pages"
- *Shadow work* (cover):
  `--kind nature-macro --shot macro --light overcast --setting "Welsh hill wood"`
  "A fern unfurling in the deep shade of a dry-stone wall in a Welsh hill wood, macro view of the curled tip, moss
  and dew drops, grey light after soft rain, the rest of the frame in plum shadow"
- *The autumn equinox* (cover):
  `--kind landscape --shot symmetrical --light golden-hour --setting "Kentish orchard"`
  "A Kentish orchard at the autumn equinox, half the trees still green and half turned gold, a wooden ladder and a
  basket of apples at the centre, perfectly balanced, low sun exactly on the horizon"
- *The full moon in Pisces* (cover):
  `--kind animal --shot reflection --light moonlight --setting "Somerset Levels"`
  "A grey heron standing still in a flooded meadow of the Somerset Levels under a full moon, bird and moon doubled
  in the water, mist over the reeds, a line of willows behind, late winter"
- *Five of Cups, grief* (cover):
  `--kind figure-at-distance --shot wide --light blue-hour --setting "Prague river bridge"`
  "A lone figure in a dark coat on a stone bridge over the Vltava in Prague at dusk, three overturned glasses on
  the parapet, two full glasses still standing behind them, the river and the old town far away, seen from a
  distance, the sorrow of the Five of Cups"

## Refuse, regenerate or rewrite if
- the picture is a picture of cards anyway (a card filling the frame, a spread, a deck, hands holding cards), or a
  card shows up big where the prompt asked for none;
- there is text, letters, numbers or a logo anywhere (even fake writing);
- hands or faces are malformed, or a face looks like a real, recognisable person;
- it looks like a stock photo or like the actual Thoth deck artwork;
- it could illustrate any other article just as well.

## Alt text
Describe what is in the picture, for someone who cannot see it, 8–125 characters:
"A lone figure on a stone bridge in the rain, three glasses overturned and two still standing". The keyword only if
it fits naturally; never a list of keywords. An alt text that describes a spread is refused; one that mentions a
card gets a warning: keep it only if the picture really shows that card, small, in the context.
