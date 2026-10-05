# Cover and inline pictures

One way only: the **`tarots-blog-images`** skill's `tarots_images.py generate`, which calls **`litmedia-skill`**
(LitMedia API) and checks every prompt before spending a credit. Never `browser-image-gen`, never the LitMedia
website, never the agent's own image tool, never `litmedia-skill`'s `ai_image.py` called directly.

## Settings
| | Cover | Inline picture |
|---|---|---|
| Model | Seedream 5.0 | Seedream 5.0 |
| Resolution | 2K (10 credits; there is no 1K, never 4K) | 2K |
| Aspect | `3:2` (the default) | `4:3`, or `1:1` for a close-up |
| How many | one | normally one, two at most |

## Commands (from this skill's folder)
```
python ../tarots-blog-images/scripts/tarots_images.py balance
python ../tarots-blog-images/scripts/tarots_images.py progress        # the last 20 pictures and what is free next
python ../tarots-blog-images/scripts/tarots_images.py catalog         # every value of --kind, --shot, --light
python ../tarots-blog-images/scripts/tarots_images.py prompt-check --prompt "<prompt>" --kind <kind> --shot <shot> --light <light> --setting "<setting>" --alt "<alt>" --article <slug>
python ../tarots-blog-images/scripts/tarots_images.py generate --article <slug> --prompt "<prompt>" --kind <kind> --shot <shot> --light <light> --setting "<setting>"
python ../tarots-blog-images/scripts/tarots_images.py generate --article <slug> --prompt "<prompt>" --kind <kind> --shot <shot> --light <light> --setting "<setting>" --aspect 4:3
```
`--article <slug>` saves into the article's work folder (made by `tarots_blog.py new`):
`~/.tarots-blog/work/<YYYY-MM-DD>-<slug>/foto/`, as `cover.jpg` for a 3:2 picture and `inline-1.jpg`, `inline-2.jpg`...
for the others (`--out NAME` chooses the name; a bare name without `--article` goes in the newest work folder). The
full path is printed; an existing file is never overwritten. Never `--out work/...` or any path inside a skill's
folder.
For example:
```
python ../tarots-blog-images/scripts/tarots_images.py generate --kind architecture --shot low-angle --light storm-light --setting "Breton fishing coast" --article the-tower-tarot-card-meaning-thoth --prompt "A lighthouse on a black basalt cliff of the Breton coast in a winter storm, one bolt of lightning splitting the sky, a crack running down the white tower and warm light pouring out through it, seen from the fishing harbour below, looking up, the sudden energy of the Tower, <house style>"
```
Then `python scripts/tarots_blog.py post <slug>`: without `--cover` it takes `foto/cover.jpg` (or `.jpeg`, `.png`,
`.webp`) by itself, with a `note:`; with no cover in `foto/` it stops with exit 11 and saves nothing. `--cover NAME`
chooses another file; `--no-cover` saves without a cover, only when the generation failed (say why in the report).
`python scripts/tarots_blog.py upload inline-1.jpg --for <slug>` uploads an inline picture (it prints the `url` to
write as `![alt](url)` in the body): a bare name is looked for in the work folder's `foto/`. If `tarots-blog-images`
is not next to this skill, find its folder by name in the agent's skills directories; if it is not installed,
`post --no-cover` and say so.

## What `post` (its cover) and `upload` check
Both read the record `tarots_images.py` writes (`~/.tarots-blog/images-progress.json`, or `TAROTS_IMAGES_PROGRESS`)
and refuse the file before uploading anything (exit 7) when:
- it was not made by `tarots_images.py generate`. A picture **the operator supplied** passes with
  `--operator-image` and a warning; that option is never a way around a refusal;
- the same picture (same sha256, whatever the name) is already used by another article;
- the prompt it was generated from makes cards the picture (the same rules as `generate`, copied in
  `tarots_blog.py`: a card as the subject, two or more cards, a spread, a hand holding a card);
- the prompt draws one small card and the article is not about that very card (the same card rule as `generate`,
  copied too): for `post` the article is its article.json (`title`, `focus_keyword`); for `upload` it is the
  `--for` slug or id, looked for in its work folder, then in the titles copy (`titles` refreshes it). `upload`
  without `--for` refuses a picture with a card.

A file that is not PNG, JPEG or WebP is refused first, as a usage error (exit 2).

After a successful `post` the cover's sha256 is recorded with the new article's id and slug; after `upload`, with
the `--for` slug or id. Without `--for` the picture is tied to that single upload and refused afterwards: always
pass it.

## The prompt
Write it with `tarots-blog-images/references/prompts.md`: the reasons and the rules, the catalogs, the house style
line, examples. In short:
- **The subject is this article's content**: a concrete scene, place, object or gesture from its text; never a
  prompt per section or a template.
- **Cards as context, never as the picture.** Refused: a card as the subject (at the start, in the first clause or
  the first 8 content words, a close-up of a card), more than one card (cards, a deck, a pile, the arcana), a spread
  or layout (cards on a table, a reading, a fan of cards, cards face down), hands holding or turning a card.
  Accepted: "tarot" as an adjective, the names of the cards as a world or a symbol, without the word *card* ("a
  lighthouse struck by lightning, the energy of the Tower").
- **A card in the picture only for an article about that very card.** One single small card later in the scene
  is allowed only when the article's **title or focus keyword names that card** (Thoth and Rider-Waite names are the
  same card: Adjustment = Justice, Lust = Strength, Art = Temperance, Aeon = Judgement, Universe = World…), the
  prompt **names it in the same phrase** and draws it **in the style of the Thoth deck** (a new drawing, never a
  copy, never Rider-Waite or Marseille). `generate` and `prompt-check` then need `--article <slug or id>`.
  Accepted, for *The Tower tarot card meaning*: "…a wool coat drying by the door, seen through the window, on the
  shelf a single small card of the Tower leaning on a cup, in the style of the Thoth deck". Refused, for *Tarot
  Meditation for Libra Season Balance* (an agent added a small Fool there and got a large Rider-Waite Fool): "…and
  beside it a single small card of the Fool" → *this article is not about a specific card: no card in its picture;
  show its world instead*. The full rule (which names count, *Full Moon* vs *The Moon tarot card*):
  `tarots-blog-images/references/prompts.md`.
- **The form changes every time**, declared with four required options: `--kind` (17 values: landscape,
  sky-and-weather, architecture, interior, street-or-market, figure-from-behind, figure-at-distance,
  hands-and-gesture, still-life-object, nature-macro, animal, water-and-reflection, celestial, ritual-or-craft,
  abstract-symbol, map-or-diagram, journey-or-path), `--shot` (12: wide, close-up, macro, aerial, low-angle,
  silhouette, through-a-window-or-doorway, reflection, symmetrical, off-centre-negative-space, over-the-shoulder,
  top-down), `--light` (10: dawn, golden-hour, midday, overcast, blue-hour, moonlight, starlight, storm-light,
  fog-or-mist, firelight) and `--setting` (a place, culture or era in a few words). Refused: a kind of the last 3
  pictures, a kind+shot pair of the last 20, a light of the last 2 (firelight: of the last 10), a setting of the
  last 10; and a prompt that does not show the declared light, shot and setting in its own words.

`generate` refuses a prompt that breaks these rules (exit 7) and says what to change, with the values still free:
rewrite it, do not work around it. The cover and the inline picture of one article get two different forms.

## Rules
- **Cost and consent**: 10 credits a picture. Before the first generation of a session tell the operator the
  number of pictures and the cost, and get a yes (a standing "go ahead" from the operator counts).
  In an unattended run the job's instructions are that standing ok: a cover and at most one inline picture.
- **Look at every picture** before using it. Reject it if it is a picture of cards anyway (a card filling the
  frame, a spread, a deck), has text, letters, malformed hands or faces, or has nothing to do with the article. A
  second try needs a rewritten prompt and a new form.
- **Never reuse a picture** of another article, and never the cover as the inline picture.
- **TLS errors are not to be bypassed.** Report them and publish without the picture.
- **LitMedia down, out of credits or failing**: no picture, said in the report. Never another tool.
  `ModuleNotFoundError: requests`: `tarots_images.py` picks by itself a Python that has LitMedia's dependencies;
  with none it exits 5 naming the `pip install -r` command: report it, never install anything yourself.
- **Illustration, not evidence**: no fake photos of real people, no fake documents, no copy of the Thoth deck's
  artwork (copyrighted).
- **Never send the blog key to LitMedia** (or anywhere but `TAROTS_API_URL`).

## Alt text
Describe what is really in the picture, 8–125 characters: `"A lighthouse on a basalt cliff struck by lightning,
warm light pouring from a crack in the tower"`. The keyword only if the picture really shows it (otherwise accept
the `chiave_nell_alt` warning). `tarots_images.py prompt-check --alt` refuses an alt that describes a spread and
warns about one that mentions a card: keep a card in the alt only if the picture really shows it.

## Inline pictures are not optional by default
Decide for every article whether one belongs (a scene from the text, an abstract picture of a spread's positions,
a close-up of a symbol) and say so in the report either way: "inline image: yes, showing X" / "inline image: none,
the topic didn't call for one". Place it where it serves the text: not at the very top (that is the cover) and not
inside the closing paragraph.
