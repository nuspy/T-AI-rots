#!/usr/bin/env python3
"""tarots_blog.py: publish to the TAROTS chat blog through its REST API (v1).

Standard library only (Python 3.8+). Configuration comes from the environment, never from arguments or files:

    TAROTS_API_URL   the API base, e.g. https://tarots.chat/api   (https only; http is accepted for localhost)
    TAROTS_API_KEY   a `tk_live_...` key created in the console (Blog > Keys)

Commands (run `tarots_blog.py <command> -h` for the options):

    guide                  what the blog accepts and the SEO thresholds (read once, before writing)
    sections               the sections articles can go in
    tags                   tags already in use (reuse them)
    catalog [--grep TEXT]  cards and spreads with the ready-made internal-link shortcut
    mine                   articles this key created (avoid duplicates, pick an unused keyword)
    check ARTICLE.json     SEO report without saving anything
    upload IMAGE           upload a cover image, print its id
    post ARTICLE.json      check, then create the article (draft unless the JSON says "published")
    update ID PATCH.json   change fields of an article this key created
    delete-draft ID        delete a draft this key created

Exit codes: 0 ok · 2 usage or bad article file · 3 SEO score below the threshold (nothing saved)
· 4 the API refused (message printed) · 5 configuration missing or unsafe.

The key is only ever sent to TAROTS_API_URL, is never printed, and redirects are not followed (a redirect would
carry the key to another host): if the server redirects, fix TAROTS_API_URL.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

EXIT_OK, EXIT_USAGE, EXIT_SCORE, EXIT_API, EXIT_CONFIG = 0, 2, 3, 4, 5

MAX_IMAGE_BYTES = 8_000_000
IMAGE_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}

#: Friendly (English) keys of an article file → the API field. The API's own names are accepted as they are.
FIELDS = {
    "title": "titolo", "subtitle": "sottotitolo", "body": "testo", "markdown": "testo", "language": "lang",
    "section": "sezione", "cover_image_id": "immagine_id", "cover_alt": "immagine_alt", "image_alt": "immagine_alt",
    "seo_title": "seo_titolo", "seo_description": "seo_descrizione", "focus_keyword": "seo_parola_chiave",
    "secondary_keywords": "seo_parole_chiave", "status": "stato", "publish_at": "pubblicato_il",
    "featured": "in_evidenza",
}
#: Fields with the same name in both vocabularies.
SAME = {"lang", "tags", "slug", "canonical_url", "noindex", "faq", "dry_run"}
API_FIELDS = set(FIELDS.values()) | SAME
STATUS = {"draft": "bozza", "published": "pubblicato", "archived": "archiviato"}


class Failure(Exception):
    def __init__(self, message: str, code: int = EXIT_API):
        super().__init__(message)
        self.code = code


# ---- configuration and HTTP ------------------------------------------------------------------------------------


def config() -> Dict[str, str]:
    base = os.environ.get("TAROTS_API_URL", "").strip().rstrip("/")
    key = os.environ.get("TAROTS_API_KEY", "").strip()
    if not base:
        raise Failure("TAROTS_API_URL is not set (for example https://tarots.chat/api).", EXIT_CONFIG)
    url = urllib.parse.urlparse(base)
    local = url.hostname in ("localhost", "127.0.0.1", "::1")
    if url.scheme != "https" and not (url.scheme == "http" and local):
        raise Failure("TAROTS_API_URL must be https (http is only accepted for localhost): the key would travel in clear text.", EXIT_CONFIG)
    if not key.startswith("tk_live_"):
        raise Failure("TAROTS_API_KEY is not set or is not a tk_live_ key. Create one in the console: Blog > Keys.", EXIT_CONFIG)
    return {"base": base, "key": key}


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """A redirect would forward the Authorization header to whatever host it points at: never follow one."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D401
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


def call(
    method: str, path: str, *, body: Optional[Any] = None, raw: Optional[bytes] = None,
    content_type: Optional[str] = None, query: Optional[Dict[str, Any]] = None, timeout: int = 60,
) -> Any:
    """One request to `/v1/blog{path}`. Returns the decoded JSON (or None for 204). Raises `Failure`."""
    cfg = config()
    url = f"{cfg['base']}/v1/blog{path}"
    if query:
        url += "?" + urllib.parse.urlencode({k: v for k, v in query.items() if v is not None})
    headers = {"Authorization": f"Bearer {cfg['key']}", "Accept": "application/json", "User-Agent": "tarots-blog-publisher/1.0"}
    data = None
    if raw is not None:
        data, headers["Content-Type"] = raw, content_type or "application/octet-stream"
    elif body is not None:
        data, headers["Content-Type"] = json.dumps(body).encode("utf-8"), "application/json"
    request = urllib.request.Request(url, data=data, method=method, headers=headers)
    # Only reads are retried: a repeated POST could create a duplicate article.
    for attempt in range(2 if method == "GET" else 1):
        try:
            with _OPENER.open(request, timeout=timeout) as response:
                payload = response.read()
                return json.loads(payload) if payload else None
        except urllib.error.HTTPError as exc:
            raise Failure(explain(exc)) from None
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            if attempt == 0 and method == "GET":
                time.sleep(2)
                continue
            raise Failure(f"Cannot reach the API ({getattr(exc, 'reason', exc)}). Check TAROTS_API_URL and the network.") from None
    return None  # pragma: no cover


def explain(exc: urllib.error.HTTPError) -> str:
    """A short, useful message for an HTTP error. Never includes request headers (the key)."""
    try:
        detail = json.loads(exc.read().decode("utf-8", "replace")).get("detail")
    except Exception:  # noqa: BLE001
        detail = None
    if isinstance(detail, (dict, list)):
        detail = json.dumps(detail, ensure_ascii=False)
    redirect = "The server redirected the request. Point TAROTS_API_URL at the final address; redirects are not followed."
    hints = {
        301: redirect, 302: redirect, 307: redirect, 308: redirect,
        401: "The key was rejected: wrong, revoked or expired. Create a new one in the console (Blog > Keys).",
        403: "This key lacks the permission for that action (or the article is not yours to change).",
        404: "Not found: wrong id, or the article was created by another key.",
        413: "The file is too large (8 MB at most).",
        415: "Unsupported file type: send PNG, JPEG or WebP.",
        429: "Rate limit or daily limit reached. Wait, and do not retry in a loop.",
    }
    hint = hints.get(exc.code, "")
    return f"HTTP {exc.code}" + (f": {detail}" if detail else "") + (f"\n  {hint}" if hint else "")


# ---- reading an article file -----------------------------------------------------------------------------------


def normalize(article: Dict[str, Any], base_dir: Optional[Path] = None) -> Dict[str, Any]:
    """From an article file (friendly or API field names) to the API payload.

    `body_file` (a Markdown path, relative to the JSON file) fills `testo`. FAQ items may be `{question, answer}`.
    `status` may be draft | published | archived. Unknown keys are an error: a typo must not silently vanish."""
    out: Dict[str, Any] = {}
    unknown: List[str] = []
    for key, value in article.items():
        if key == "body_file":
            continue
        target = FIELDS.get(key, key if key in API_FIELDS else None)
        if target is None:
            unknown.append(key)
        else:
            out[target] = value
    if unknown:
        allowed = sorted(set(FIELDS) | SAME | {"body_file"})
        raise Failure(f"Unknown field(s): {', '.join(sorted(unknown))}. Allowed: {', '.join(allowed)}.", EXIT_USAGE)
    if "body_file" in article:
        path = Path(article["body_file"])
        if base_dir is not None and not path.is_absolute():
            path = base_dir / path
        try:
            out["testo"] = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise Failure(f"Cannot read body_file {path}: {exc.strerror}", EXIT_USAGE) from None
    if isinstance(out.get("stato"), str):
        out["stato"] = STATUS.get(out["stato"].lower(), out["stato"])
    if isinstance(out.get("faq"), list):
        out["faq"] = [
            {"domanda": f.get("domanda", f.get("question", "")), "risposta": f.get("risposta", f.get("answer", ""))}
            if isinstance(f, dict) else f
            for f in out["faq"]
        ]
    if isinstance(out.get("seo_parole_chiave"), str):
        out["seo_parole_chiave"] = [p.strip() for p in out["seo_parole_chiave"].split(",") if p.strip()]
    if isinstance(out.get("tags"), str):
        out["tags"] = [p.strip() for p in out["tags"].split(",") if p.strip()]
    return out


def load_article(path: str) -> Dict[str, Any]:
    file = Path(path)
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
    except OSError as exc:
        raise Failure(f"Cannot read {file}: {exc.strerror}", EXIT_USAGE) from None
    except json.JSONDecodeError as exc:
        raise Failure(f"{file} is not valid JSON: {exc}", EXIT_USAGE) from None
    if not isinstance(data, dict):
        raise Failure(f"{file} must contain a JSON object.", EXIT_USAGE)
    return normalize(data, file.parent)


# ---- output -----------------------------------------------------------------------------------------------------


def show(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


MARK = {"errore": "FIX ", "avviso": "WARN", "ok": "ok  "}


def report(seo: Dict[str, Any]) -> None:
    s = seo.get("statistiche", {})
    print(f"SEO score: {seo['punteggio']}/100 ({seo['giudizio']})  words={s.get('parole')} h2={s.get('titoli_h2')} "
          f"internal_links={s.get('collegamenti_interni')} external_links={s.get('collegamenti_esterni')} faq={s.get('faq')}")
    todo = [c for c in seo["controlli"] if c["esito"] != "ok"]
    for c in sorted(todo, key=lambda c: (c["esito"] != "errore", -c["peso"])):
        print(f"  {MARK[c['esito']]} [{c['id']}] {c['messaggio']}")
    if not todo:
        print("  every check passes")


# ---- commands -----------------------------------------------------------------------------------------------------


def cmd_guide(_a) -> int:
    show(call("GET", "/guide"))
    return EXIT_OK


def cmd_sections(a) -> int:
    rows = call("GET", "/sections")
    if a.json:
        show(rows)
    else:
        for r in rows:
            print(f"{r['slug']:32} {r['percorso']}")
        if not rows:
            print("(no sections: publish without `section`)")
    return EXIT_OK


def cmd_tags(a) -> int:
    rows = call("GET", "/tags")
    if a.json:
        show(rows)
    else:
        for r in rows:
            print(f"{r['nome']} ({r['n']})")
        if not rows:
            print("(no tags yet)")
    return EXIT_OK


def cmd_catalog(a) -> int:
    data = call("GET", "/catalog")
    needle = (a.grep or "").lower()
    keep = lambda r: not needle or needle in r["slug"].lower() or needle in r["nome"].lower()  # noqa: E731
    cards, spreads = [r for r in data["carte"] if keep(r)], [r for r in data["stese"] if keep(r)]
    if a.json:
        show({"cards": cards, "spreads": spreads})
        return EXIT_OK
    for title, rows in (("Cards", cards), ("Spreads", spreads)):
        print(f"{title}:")
        for r in rows:
            print(f"  {r['scorciatoia']:36} {r['nome']}")
    return EXIT_OK


def cmd_mine(a) -> int:
    data = call("GET", "/posts", query={"stato": a.status, "pagina": a.page, "per_pagina": a.per_page})
    if a.json:
        show(data)
        return EXIT_OK
    print(f"{data['totale']} article(s), page {data['pagina']}")
    for p in data["articoli"]:
        print(f"  {p['id']}  {p['stato']:10} {p['lang']}  {p['slug']}  | {p['titolo']}  | keyword: {p.get('seo_parola_chiave') or '-'}")
    return EXIT_OK


def cmd_check(a) -> int:
    payload = load_article(a.article)
    seo = call("POST", "/seo-check", body={k: v for k, v in payload.items() if k != "dry_run"})
    if a.json:
        show(seo)
    else:
        report(seo)
    return EXIT_OK if seo["punteggio"] >= a.min_score else EXIT_SCORE


def upload(path: str) -> Dict[str, Any]:
    file = Path(path)
    kind = IMAGE_TYPES.get(file.suffix.lower())
    if kind is None:
        raise Failure("The cover must be a PNG, JPEG or WebP file.", EXIT_USAGE)
    try:
        raw = file.read_bytes()
    except OSError as exc:
        raise Failure(f"Cannot read {file}: {exc.strerror}", EXIT_USAGE) from None
    if len(raw) > MAX_IMAGE_BYTES:
        raise Failure("The image is larger than 8 MB: export it smaller (the site scales it to 1600 px wide anyway).", EXIT_USAGE)
    return call("POST", "/media", raw=raw, content_type=kind)


def cmd_upload(a) -> int:
    image = upload(a.image)
    if a.json:
        show(image)
    else:
        print(f"uploaded: id={image['id']} {image['larghezza']}x{image['altezza']} ({image['byte']} bytes)")
        print(f'use it as "cover_image_id": "{image["id"]}"')
    return EXIT_OK


def cmd_post(a) -> int:
    payload = load_article(a.article)
    if a.cover:
        image = upload(a.cover)
        payload["immagine_id"] = image["id"]
        print(f"cover uploaded: {image['id']}", file=sys.stderr)
    payload.pop("dry_run", None)
    trial = call("POST", "/posts", body={**payload, "dry_run": True})
    seo = trial["seo"]
    report(seo)
    if seo["punteggio"] < a.min_score:
        if not a.save_anyway:
            print(f"Not saved: the score is below {a.min_score}. Fix the items above and run again "
                  f"(or use --save-anyway to keep it as a draft for an editor).", file=sys.stderr)
            return EXIT_SCORE
        payload["stato"] = "bozza"
        payload.pop("pubblicato_il", None)
        print("Saving as a draft because of --save-anyway.", file=sys.stderr)
    if a.dry_run:
        print("dry run: nothing saved")
        return EXIT_OK
    result = call("POST", "/posts", body=payload)
    article = result["articolo"]
    if a.json:
        show(result)
    else:
        print(f"saved: id={article['id']} status={article['stato']} lang={article['lang']}")
        print(f"url:   {result['url']}" + ("" if article["stato"] == "pubblicato" else "   (not public until an editor publishes it)"))
        for warning in result.get("avvisi", []):
            print(f"note:  {warning}")
    return EXIT_OK


def cmd_update(a) -> int:
    payload = load_article(a.patch)
    result = call("PATCH", f"/posts/{urllib.parse.quote(a.id)}", body=payload)
    if a.json:
        show(result)
    else:
        article = result["articolo"]
        print(f"updated: id={article['id']} status={article['stato']}  url: {result['url']}")
        report(result["seo"])
        for warning in result.get("avvisi", []):
            print(f"note:  {warning}")
    return EXIT_OK


def cmd_delete(a) -> int:
    call("DELETE", f"/posts/{urllib.parse.quote(a.id)}")
    print("deleted")
    return EXIT_OK


# ---- entry point ----------------------------------------------------------------------------------------------------


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="tarots_blog.py", description=__doc__.split("\n\n")[0])
    p.add_argument("--json", action="store_true", help="print the raw JSON instead of a summary")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("guide", help="what the blog accepts and the SEO thresholds").set_defaults(run=cmd_guide)
    sub.add_parser("sections", help="sections articles can go in").set_defaults(run=cmd_sections)
    sub.add_parser("tags", help="tags already in use").set_defaults(run=cmd_tags)
    c = sub.add_parser("catalog", help="cards and spreads with their link shortcuts")
    c.add_argument("--grep", help="only entries whose slug or name contains this text")
    c.set_defaults(run=cmd_catalog)
    m = sub.add_parser("mine", help="articles this key created")
    m.add_argument("--status", choices=["bozza", "pubblicato", "archiviato"])
    m.add_argument("--page", type=int, default=1)
    m.add_argument("--per-page", type=int, default=25)
    m.set_defaults(run=cmd_mine)

    k = sub.add_parser("check", help="SEO report without saving")
    k.add_argument("article")
    k.add_argument("--min-score", type=int, default=85)
    k.set_defaults(run=cmd_check)
    u = sub.add_parser("upload", help="upload a cover image")
    u.add_argument("image")
    u.set_defaults(run=cmd_upload)
    r = sub.add_parser("post", help="check, then create the article")
    r.add_argument("article")
    r.add_argument("--cover", help="an image file to upload and use as the cover")
    r.add_argument("--min-score", type=int, default=85, help="refuse to save below this SEO score (default 85)")
    r.add_argument("--save-anyway", action="store_true", help="below the score, keep it as a draft instead of refusing")
    r.add_argument("--dry-run", action="store_true", help="check only; save nothing")
    r.set_defaults(run=cmd_post)
    x = sub.add_parser("update", help="change fields of an article this key created")
    x.add_argument("id")
    x.add_argument("patch")
    x.set_defaults(run=cmd_update)
    d = sub.add_parser("delete-draft", help="delete a draft this key created")
    d.add_argument("id")
    d.set_defaults(run=cmd_delete)
    return p


def main(argv: Optional[List[str]] = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass
    args = parser().parse_args(argv)
    try:
        return args.run(args)
    except Failure as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exc.code


if __name__ == "__main__":
    sys.exit(main())
