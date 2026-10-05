# Edit an existing article

`tarots_blog.py` can change and delete **only the articles this key created** (`mine` lists them; for any other
article the API answers `404`, the same as "does not exist").

```
python scripts/tarots_blog.py mine                       # find the id
python scripts/tarots_blog.py update <id> patch.json     # change some fields
python scripts/tarots_blog.py delete-draft <id>          # delete a draft
```
- `patch.json` holds **only the fields to change**, with the same names as an article file (`title`, `subtitle`,
  `body` or `body_file`, `language`, `section`, `tags`, `slug`, `seo_title`, `seo_description`, `focus_keyword`,
  `secondary_keywords`, `faq`, `cover_alt`, `cover_image_id`, `canonical_url`, `noindex`, `status`
  (`draft|published|archived`), `publish_at`, `featured`). An unknown field is an error. `body`/`body_file`
  replaces the **whole** text; `tags`, `faq` and `secondary_keywords` replace the whole list.
- Keep `patch.json` in the article's work folder (`new "<slug>"` makes one if the article has none): `update` then
  accepts the slug or the folder instead of the path, like `check` and `post`.
- There is **no dry run and no score gate** on `update`: the change is saved, then the SEO report is printed. Run
  `check` on the full article first. A `dry_run` field in the patch is refused (the server would ignore it and
  save).
- Without `blog:publish`: an article that is already published or archived cannot be changed (`403`), and
  `status: published|archived`, `publish_at` or `featured` in the patch are ignored with a `note:`.
- `delete-draft` deletes **drafts only** (`409` otherwise); a published article is archived from the console.
- Pictures of an existing article (cover or inline): use the **`tarots-blog-images`** skill (`cover`, `inline`),
  not `update` with a new `cover_image_id`, so the picture rules and the record of used pictures apply.
