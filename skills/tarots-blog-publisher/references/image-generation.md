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
python ../tarots-blog-images/scripts/tarots_images.py prompt-check --prompt "<prompt>" --alt "<alt>"
python ../tarots-blog-images/scripts/tarots_images.py generate --prompt "<prompt>" --out work/<slug>-cover.jpg
python ../tarots-blog-images/scripts/tarots_images.py generate --prompt "<prompt>" --aspect 4:3 --out work/<slug>-1.jpg
```
Then `python scripts/tarots_blog.py post article.json --cover work/<slug>-cover.jpg` for the cover, and
`python scripts/tarots_blog.py upload work/<slug>-1.jpg --for <slug>` for an inline picture (it prints the `url` to
write as `![alt](url)` in the body). If `tarots-blog-images` is not next to this skill, find its folder by name in
the agent's skills directories; if it is not installed, publish without pictures and say so.

## What `post --cover` and `upload` check
Both read the record `tarots_images.py` writes (`~/.tarots-blog/images-progress.json`, or `TAROTS_IMAGES_PROGRESS`)
and refuse the file before uploading anything (exit 7) when:
- it was not made by `tarots_images.py generate`. A picture **the operator supplied** passes with
  `--operator-image` and a warning; that option is never a way around a refusal;
- the same picture (same sha256, whatever the name) is already used by another article;
- the prompt it was generated from asks for a card.

After a successful `post` the cover's sha256 is recorded with the new article's id and slug; after `upload`, with
the `--for` slug or id. Without `--for` the picture is tied to that single upload and refused afterwards: always
pass it.

## The prompt
Write it with `tarots-blog-images/references/prompts.md`: the reasons and the rules, the kinds of picture, the
house style line, examples. In one breath: **no card of any kind** (not even the word "tarot"), a concrete scene
from this article's text, a different kind of picture from the last three, never a prompt per section or a
template. `generate` refuses a prompt that breaks these rules (exit 7) and says why: rewrite it, do not work
around it.

## Rules
- **Cost and consent**: 10 credits a picture. Before the first generation of a session tell the operator the
  number of pictures and the cost, and get a yes (a standing "go ahead" from the operator counts).
- **Look at every picture** before using it. Reject it if it shows a card or anything like one, text, letters,
  malformed hands or faces, or has nothing to do with the article. A second try needs a rewritten prompt.
- **Never reuse a picture** of another article, and never the cover as the inline picture.
- **TLS errors are not to be bypassed.** Report them and publish without the picture.
- **LitMedia down, out of credits or failing**: no picture, said in the report. Never another tool.
- **Illustration, not evidence**: no fake photos of real people, no fake documents, no copy of the Thoth deck's
  artwork (copyrighted).
- **Never send the blog key to LitMedia** (or anywhere but `TAROTS_API_URL`).

## Alt text
Describe what is really in the picture, 8–125 characters: `"A lighthouse on a basalt cliff struck by lightning,
warm light pouring from a crack in the tower"`. The keyword only if the picture really shows it (otherwise accept
the `chiave_nell_alt` warning); never "tarot cards".

## Inline pictures are not optional by default
Decide for every article whether one belongs (a scene from the text, an abstract picture of a spread's positions,
a close-up of a symbol) and say so in the report either way: "inline image: yes, showing X" / "inline image: none,
the topic didn't call for one". Place it where it serves the text: not at the very top (that is the cover) and not
inside the closing paragraph.
