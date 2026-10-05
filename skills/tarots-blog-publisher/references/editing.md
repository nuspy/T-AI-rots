# Edit an existing article

One key reads, changes and deletes **any draft** of the blog, whoever wrote it (another key, the console): there are
no «articles of another key» any more (5/10/2026). With `blog:publish` it changes published and archived articles
too. The key can do it; **you do it only to the article the operator (or the job) names**, never to one you chose.

```
python scripts/tarots_blog.py list-posts                  # every article with its id, newest first, 25 a page
python scripts/tarots_blog.py list-posts --status bozza --page 2
python scripts/tarots_blog.py mine                        # only those this key created (= list-posts --mine)
python scripts/tarots_blog.py titles --grep tower --json  # find one by topic: the rows carry "id" too
python scripts/tarots_blog.py update <id> patch.json      # change some fields
python scripts/tarots_blog.py delete-draft <id>           # delete a draft
```
- `patch.json` holds **only the fields to change**, with the same names as an article file (`title`, `subtitle`,
  `body` or `body_file`, `language`, `section`, `subject`, `tags`, `slug`, `seo_title`, `seo_description`,
  `focus_keyword`, `secondary_keywords`, `faq`, `cover_alt`, `cover_image_id`, `canonical_url`, `noindex`, `status`
  (`draft|published|archived`), `publish_at`, `featured`). An unknown field is an error. `body`/`body_file`
  replaces the **whole** text; `tags`, `faq` and `secondary_keywords` replace the whole list.
- `subject` is `{"type": "card"|"spread", "ref": "<id or slug>"}` (ids from `catalog`): an article about one card
  belongs in that card's section (`major-arcana`, or `wands`, `cups`, `swords`, `disks`), one about a spread in a
  section of spreads. Change both together when you move an article.
- Keep `patch.json` in the article's work folder (`new "<slug>"` makes one if the article has none): `update` then
  accepts the slug or the folder instead of the path, like `check` and `post`.
- There is **no dry run and no score gate** on `update`: the change is saved, then the SEO report is printed. Run
  `check` on the full article first. A `dry_run` field in the patch is refused (the server would ignore it and
  save).
- Without `blog:publish`: an article that is already published or archived cannot be changed (`403`), and
  `status: published|archived`, `publish_at` or `featured` in the patch are ignored with a `note:`.
- `delete-draft` is for drafts (any key's). Deleting a published article needs `blog:publish` **and** the
  operator's explicit request for that very article; otherwise the console archives it.
- When the key is not the article's author, the server keeps a record of the change (before and after) for the
  operator.
- `404` means a wrong id (or an article deleted meanwhile): `list-posts` gives the ids.
- Pictures of an existing article (cover or inline): use the **`tarots-blog-images`** skill (`cover`, `inline`),
  not `update` with a new `cover_image_id`, so the picture rules and the record of used pictures apply.
