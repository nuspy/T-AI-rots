# Writing the body: links, pictures, video, emphasis

The body is Markdown in `article.md`, in the article's work folder. No HTML, no `# H1` (the page title is the H1;
a `# …` line at the very top is removed by the script with a `note:`). Sections start at `##`.

## Internal links
Inside sentences, with shortcuts: `[[card:the-tower]]`, `[[spread:celtic-cross]]`, `[[post:some-existing-slug]]`.
A card or spread on a line of its own becomes a card with its picture. Take the exact shortcut from
`tarots_blog.py catalog --grep <word>` (cards and spreads) or the slug from `titles --grep <word>` (posts). An
unknown reference disappears silently, so copy, don't guess. Two to five per article.

## External source
At least one reputable source you actually opened (a museum, a library, an academic or established reference, an
agency such as a national observatory for astronomical dates), as `[a few words](https://…)` inside a sentence.

## Inline picture — decide explicitly, don't silently skip
For every article decide whether a scene from the text, an abstract picture of a spread's positions (lights,
stones, a constellation: never a layout of cards) or a close-up of a symbol would genuinely help — most articles
about a spread or a specific symbol do benefit from one. If yes:
```
python ../tarots-blog-images/scripts/tarots_images.py generate --article <slug> --aspect 4:3 --kind … --shot … --light … --setting "…" --prompt "…"
python scripts/tarots_blog.py upload "<the file generate printed>" --for <slug>
```
`generate` saves it in the work folder's `foto/` with a name of its own, `inline-<YYYYMMDD-HHMMSS>.jpg` (a
different form from the cover), and prints the exact `upload` command to run; `upload` also finds a bare name there,
and prints the `url`. Paste it into `article.md` as ordinary Markdown: `![alt text](url)`. One is normally enough,
not one per paragraph. State the decision either way in the report.

## Captions
Put the caption in the image title — `![alt text](url "The caption under the picture")`. Alt describes the picture
for who can't see it; the caption says why it is there.

## Inline video
A line on its own with `[[video:youtube:VIDEO_ID]]` (11-character id from the URL, e.g. `dQw4w9WgXcQ`) or
`[[video:vimeo:VIDEO_ID]]` (the number in the Vimeo URL) embeds that video. No other host. Use only a real,
relevant, existing video (a tradition's own explainer, a museum/library recording) — never invent one.

## Rich text (sparingly)
`:text[a phrase]{color=brass}` / `{color=plum}` / `{color=verdigris}` / `{color=muted}`, `:text[bigger]{size=large}`
(`small`, `large`, `title`), both together `:text[…]{color=plum size=large}`, and `:underline[…]`. Only these
values exist (the site's palette): anything else is ignored, and no HTML ever runs. One or two highlights per
article at most; `**bold**` is still the default.
