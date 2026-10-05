# The key: first setup and changes

**Every run starts with `python scripts/tarots_blog.py guide`.** If it prints the key's permissions (with
`note: using the saved key (prefix tk_live_…)`), everything is set: never ask the operator for a key or a URL.
Only when `guide` fails with a message about a missing key, follow the steps below.

## First setup
1. An editor creates a key in the console: **Blog → Keys**. The key is shown once, and its permissions are chosen
   only now: they cannot be added later. **Recommended: ONE key with the three permissions write + publish + media**
   (`blog:write`, `blog:publish`, `blog:media`): this skill writes and publishes with it, and `tarots-blog-images`
   uses the same saved key for the pictures of existing articles (it reads this skill's key when it has no media key
   of its own). A key with `blog:write` alone saves drafts only; without `blog:media` the picture skill gets a 403
   that says to make the one key.
2. Put it in the environment for this run only:
   ```
   TAROTS_API_URL=https://tarots.chat/api        # the API base of the site
   TAROTS_API_KEY=tk_live_…
   ```
   The **first** run with nothing saved yet remembers both, in `~/.tarots-blog/credentials.json` — a file
   outside any repository, never inside this project, `chmod 600` where the OS supports it. Every run after
   that needs neither variable: omit them and the saved ones are used automatically (a one-line `note:` on
   stderr says so, every time, so it is never silently invisible).
   Or save it explicitly: `python scripts/tarots_blog.py key save` with the two variables set. Both skills then use
   it: `python ../tarots-blog-images/scripts/tarots_images.py key show` names it as the key in use (an old separate
   media key, if one is saved, wins: `tarots_images.py key clear` forgets it).
3. Check: `python scripts/tarots_blog.py guide` prints what the key can do and the SEO thresholds.

If `guide` fails with `error: …`, read the message: it says what is wrong (URL, key, network). Do not work around it.

## Given a new key when one is already saved
Never swapped in silently. If `TAROTS_API_KEY` is set to a key that differs from the one already saved, every
command refuses with an error naming both by prefix and asks for one of three explicit choices:
- `python scripts/tarots_blog.py key show` — compare the saved key's prefix against the new one first.
- `python scripts/tarots_blog.py key save` — replace the saved key with the one in `TAROTS_API_KEY` now.
- unset `TAROTS_API_KEY` — keep using the saved key, untouched.

`python scripts/tarots_blog.py key clear` forgets the saved key entirely (a bare `guide` or any other command then
falls back to needing `TAROTS_API_KEY` set, as on a first run). Only the 12-character prefix is ever shown or
printed — never the full key — matching how the console lists keys.
