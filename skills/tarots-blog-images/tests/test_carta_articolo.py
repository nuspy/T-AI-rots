"""A card in the picture only for an article about that very card (operator's rule, 5/10/2026), offline.

    backend/.venv/Scripts/python.exe -m pytest skills/tarots-blog-images/tests -q -p no:cacheprovider

The case that made the rule: for «Tarot Meditation for Libra Season Balance», an article about no card, Hermes
added "one single small card" to the prompt and out came a large Rider-Waite Fool. No network, no LitMedia, no key:
the article comes from a work folder, from the titles copy, or from a fake of the API.
"""
from __future__ import annotations

import datetime
import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "tarots_images.py"
_spec = importlib.util.spec_from_file_location("tarots_images_carta", SCRIPT)
ti = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ti)

STYLE = ti.HOUSE_STYLE
TODAY = datetime.date.today().isoformat()
TOWER_ID = "5f0c3a1e-8b7d-4c2a-9e61-2d4b8f7a9c10"

SCENE = ("A lighthouse keeper's kitchen on a stormy night, rain on the glass, lightning over the sea, a kettle on the "
         "stove, a wool coat drying by the door, seen through the window")
DIMS = ["--kind", "interior", "--shot", "through-a-window-or-doorway", "--light", "storm-light",
        "--setting", "Breton lighthouse"]
TOWER_CARD = SCENE + (", on the shelf a single small card of the Tower leaning on a cup, in the style of the Thoth "
                      "deck, " + STYLE)
TOWER_NO_THOTH = SCENE + ", on the shelf a single small card of the Tower leaning on a cup, " + STYLE
NAMELESS_CARD = SCENE + ", on the shelf a single small card leaning on a cup, in the style of the Thoth deck, " + STYLE
# the Libra case: one small card added "as context" to an article about no card
FOOL_CARD = SCENE + (", on the shelf a single small card of the Fool leaning on a cup, in the style of the Thoth "
                     "deck, " + STYLE)
SYMBOL_ONLY = SCENE + ", the sudden energy of the Tower in the storm, " + STYLE


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    """Own progress file, work folders and titles copy; no key saved; any network call fails loudly."""
    monkeypatch.setattr(ti, "PROGRESS_PATH", tmp_path / "images-progress.json")
    monkeypatch.setattr(ti, "CACHE_PATH", tmp_path / "no-media-key.json")
    monkeypatch.setenv("TAROTS_WORK_DIR", str(tmp_path / "work"))
    monkeypatch.setenv("TAROTS_TITLES_CACHE", str(tmp_path / "titles-cache.json"))
    for name in ("TAROTS_MEDIA_KEY", "TAROTS_API_URL"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(ti, "_articles_found", {})

    def no_network(*_a, **_k):
        raise AssertionError("a check touched the network")

    monkeypatch.setattr(ti, "call", no_network)
    monkeypatch.setattr(ti, "balance", no_network)
    monkeypatch.setattr(ti, "_litmedia", no_network)
    return tmp_path


def _work_folder(tmp: Path, slug: str, title: str, keyword: str = "") -> Path:
    folder = tmp / "work" / f"{TODAY}-{slug}"
    (folder / "foto").mkdir(parents=True)
    (folder / "article.json").write_text(json.dumps({"title": title, "focus_keyword": keyword, "slug": slug}),
                                         encoding="utf-8")
    return folder


def _titles(tmp: Path, *rows) -> None:
    articles = {r["id"]: r for r in rows}
    (tmp / "titles-cache.json").write_text(json.dumps({"version": 1, "articles": articles}), encoding="utf-8")


def _check(prompt, *extra):
    return ti.main(["prompt-check", "--prompt", prompt, *DIMS, *extra])


# ---- the cards of an article: title and focus keyword --------------------------------------------------------------

@pytest.mark.parametrize("text,cards", [
    # no card: the Libra article, astrology and idioms with a card's name in them
    ("Tarot Meditation for Libra Season Balance", []),
    ("Full Moon tarot spread", []),
    ("New Moon intentions with tarot", []),
    ("Tarot for your Sun sign", []),
    ("Star sign tarot: what your zodiac says", []),
    ("Moon in Scorpio tarot ritual", []),
    ("The art of tarot journaling", []),
    ("Thoth tarot art and its painter", []),
    ("Tarot fortune telling for beginners", []),
    ("World Tarot Day 2026", []),
    ("Tower Bridge at night: a walk in London", []),
    ("Death anniversary rituals", []),
    ("A tarot spread for lovers", []),
    ("The suit of Cups in the Thoth deck", []),       # a suit alone is not one card
    ("Luna piena e tarocchi", []),
    # a common name next to a tarot word, or as the whole title
    ("The Moon tarot card meaning", ["the Moon"]),
    ("Sun tarot card in love", ["the Sun"]),
    ("The Star in the Thoth tarot", ["the Star"]),
    ("Death card meaning: endings and change", ["Death"]),
    ("The Tower", ["the Tower"]),
    ("The Chariot tarot", ["the Chariot"]),
    ("The World card reversed", ["the Universe"]),
    ("Art card meaning in the Thoth tarot", ["Art"]),
    ("La Torre nei tarocchi", ["the Tower"]),
    # unmistakable names, anywhere
    ("Hierophant reversed in love", ["the Hierophant"]),
    ("The High Priestess and intuition", ["the Priestess"]),
    ("The Hanged Man: letting go", ["the Hanged Man"]),
    ("Wheel of Fortune and the cycles of life", ["Fortune"]),
    ("Ace of Cups in a love reading", ["the Ace of Cups"]),
    ("3 of Swords: heartbreak", ["the Three of Swords"]),
    ("Knight of Wands vs Prince of Wands", ["the Knight of Wands", "the Prince of Wands"]),
    ("Asso di Coppe", ["the Ace of Cups"]),
    ("Æon and Judgement compared", ["the Aeon"]),
])
def test_the_cards_of_an_article(text, cards):
    assert ti.cards_of_article([text]) == cards


@pytest.mark.parametrize("a,b", [
    ("Adjustment tarot card", "Justice tarot card"), ("Lust tarot card", "Strength tarot card"),
    ("Art tarot card", "Temperance"), ("The Aeon", "Judgement tarot card"), ("The Universe", "The World tarot card"),
    ("Fortune tarot card", "Wheel of Fortune"), ("The Magus", "The Magician"), ("The Priestess tarot", "High Priestess"),
    ("Princess of Disks", "Princess of Pentacles"), ("Page of Coins", "Knave of Disks"), ("Two of Cups", "Due di Coppe"),
])
def test_thoth_and_rider_waite_names_are_the_same_card(a, b):
    assert ti.cards_of_article([a]) == ti.cards_of_article([b]) != []


def test_court_cards_are_compared_by_name():
    # the Thoth Knight is the Rider-Waite King, the Thoth Prince the Rider-Waite Knight: no guessing
    assert ti.cards_of_article(["Knight of Cups"]) != ti.cards_of_article(["Prince of Cups"])
    assert ti.cards_of_article(["King of Cups"]) != ti.cards_of_article(["Knight of Cups"])


# ---- the card a prompt draws ---------------------------------------------------------------------------------------

def test_the_card_drawn_is_the_one_named_in_its_phrase():
    assert ti.cards_shown(TOWER_CARD) == ["the Tower"]
    assert ti.cards_shown(NAMELESS_CARD) == [None]
    assert ti.cards_shown(SYMBOL_ONLY) is None                      # a name without the word "card": no card
    # the name nearest to "card" in its phrase; a full moon in the same phrase is not the Moon
    near = SCENE + ", on the shelf a small Tower card under the full moon, " + STYLE
    assert ti.cards_shown(near) == ["the Tower"]
    two = SCENE + ", a single card of the Tower on the shelf; a single card of the Star by the door, " + STYLE
    assert ti.cards_shown(two) == ["the Tower", "the Star"]


# ---- prompt-check and generate -------------------------------------------------------------------------------------

def test_a_card_without_article_is_refused(capsys):
    assert _check(TOWER_CARD) == ti.EXIT_RULE
    out = capsys.readouterr().out
    assert "give --article <slug or id>" in out and "about that very card" in out


def test_libra_case_an_article_about_no_card_gets_no_card(isolated, capsys):
    _work_folder(isolated, "libra-season-tarot", "Tarot Meditation for Libra Season Balance", "libra season tarot")
    assert _check(FOOL_CARD, "--article", "libra-season-tarot") == ti.EXIT_RULE
    out = capsys.readouterr().out
    assert "this article is not about a specific card: no card in its picture; show its world instead" in out
    # its world, without a drawn card, is fine; so is a card's name as a symbol
    assert _check(SYMBOL_ONLY, "--article", "libra-season-tarot") == ti.EXIT_OK


def test_the_card_of_the_article_from_its_work_folder_is_accepted(isolated, capsys):
    _work_folder(isolated, "tower-tarot-meaning", "The Tower: sudden change", "tower tarot card meaning")
    assert _check(TOWER_CARD, "--article", "tower-tarot-meaning") == ti.EXIT_OK
    out = capsys.readouterr().out
    assert "ok:" in out and "card warning" not in out


def test_another_card_or_a_nameless_one_is_refused(isolated, capsys):
    _work_folder(isolated, "tower-tarot-meaning", "The Tower: sudden change", "tower tarot card meaning")
    assert _check(FOOL_CARD, "--article", "tower-tarot-meaning") == ti.EXIT_RULE
    out = capsys.readouterr().out
    assert "the card drawn (the Fool) is not a card of this article" in out and "is about the Tower" in out
    assert _check(NAMELESS_CARD, "--article", "tower-tarot-meaning") == ti.EXIT_RULE
    assert "name it in the same phrase, e.g. «a single small card of the Tower»" in capsys.readouterr().out
    two = SCENE + ", a single card of the Tower on the shelf; a single card of the Star by the door, " + STYLE
    assert _check(two, "--article", "tower-tarot-meaning") == ti.EXIT_RULE
    assert "more than one card" in capsys.readouterr().out


def test_without_thoth_a_warning_and_a_copy_or_rider_waite_is_refused(isolated, capsys):
    _work_folder(isolated, "tower-tarot-meaning", "The Tower: sudden change", "tower tarot card meaning")
    assert _check(TOWER_NO_THOTH, "--article", "tower-tarot-meaning") == ti.EXIT_OK
    assert "card warning: the prompt does not say the card is in the style of the Thoth deck" in capsys.readouterr().out
    copy = TOWER_CARD.replace("in the style of the Thoth deck",
                              "in the style of the Thoth deck, a faithful reproduction of the original painting")
    assert _check(copy, "--article", "tower-tarot-meaning") == ti.EXIT_RULE
    assert "never a reproduction" in capsys.readouterr().out
    rider = TOWER_CARD.replace("in the style of the Thoth deck", "in the Rider-Waite style")
    assert _check(rider, "--article", "tower-tarot-meaning") == ti.EXIT_RULE


def test_the_rest_is_refused_whatever_the_article(isolated):
    _work_folder(isolated, "tower-tarot-meaning", "The Tower: sudden change", "tower tarot card meaning")
    for prompt in (SCENE + ", three cards of the Tower on the shelf, " + STYLE,
                   SCENE + ", a Celtic Cross spread on the table, " + STYLE,
                   SCENE + ", a hand turning over a card of the Tower, " + STYLE,
                   "a single card of the Tower on a shelf, " + SCENE + ", " + STYLE):
        assert _check(prompt, "--article", "tower-tarot-meaning") == ti.EXIT_RULE, prompt


def test_the_style_of_the_thoth_deck_is_not_a_deck_in_the_picture():
    assert ti.card_problems(TOWER_CARD) == []
    assert ti.card_problems("Thoth deck illustrations, Egyptian motifs, purple and gold")  # still refused


def test_the_titles_copy_finds_the_article_by_slug_or_id(isolated, capsys):
    _titles(isolated,
            {"id": TOWER_ID, "slug": "the-tower-card", "titolo": "The Tower card meaning",
             "parola_chiave": "tower card meaning", "lang": "en"},
            {"id": "libra-1", "slug": "libra-season", "titolo": "Tarot Meditation for Libra Season Balance",
             "parola_chiave": "libra season tarot", "lang": "en"})
    assert _check(TOWER_CARD, "--article", "the-tower-card") == ti.EXIT_OK
    assert _check(TOWER_CARD, "--article", TOWER_ID) == ti.EXIT_OK
    assert _check(TOWER_CARD, "--article", "libra-season") == ti.EXIT_RULE
    assert "not about a specific card" in capsys.readouterr().out
    assert ti.find_article("the-tower-card")["source"].startswith("the titles copy")


def test_the_work_folder_comes_before_the_titles_copy(isolated):
    _work_folder(isolated, "the-tower-card", "The Tower card meaning", "tower card meaning")
    _titles(isolated, {"id": "x", "slug": "the-tower-card", "titolo": "Libra season", "parola_chiave": "libra"})
    assert ti.find_article("the-tower-card")["source"].endswith("article.json")


def test_an_unknown_article_is_refused_without_a_key(capsys):
    assert _check(TOWER_CARD, "--article", "nowhere-to-be-found") == ti.EXIT_RULE
    assert "«nowhere-to-be-found» was not found" in capsys.readouterr().out


def test_with_a_media_key_the_api_is_asked_last(monkeypatch):
    monkeypatch.setattr(ti, "config", lambda: {"base": "https://tarots.example/api", "key": "tk_live_x"})
    asked = []

    def fake_call(method, path, **_k):
        asked.append((method, path))
        if path == f"/media-posts/{TOWER_ID}":
            return {"id": TOWER_ID, "slug": "the-tower", "titolo": "The Tower tarot card", "parola_chiave": "tower"}
        if path == "/media-posts":
            return {"totale": 1, "articoli": [{"id": "l1", "slug": "libra", "titolo": "Libra season balance",
                                               "parola_chiave": "libra tarot"}]}
        raise AssertionError(path)

    monkeypatch.setattr(ti, "call", fake_call)
    assert _check(TOWER_CARD, "--article", TOWER_ID) == ti.EXIT_OK
    assert asked == [("GET", f"/media-posts/{TOWER_ID}")]
    assert _check(TOWER_CARD, "--article", "libra") == ti.EXIT_RULE
    assert asked[-1] == ("GET", "/media-posts")
    # a prompt without a card never looks for its article
    asked.clear()
    assert _check(SYMBOL_ONLY, "--article", "somewhere-else") == ti.EXIT_OK
    assert asked == []


def test_generate_refuses_before_litmedia_and_finds_the_folder_of_an_id(isolated, monkeypatch, capsys):
    folder = _work_folder(isolated, "the-tower", "The Tower tarot card", "tower tarot")
    _titles(isolated, {"id": TOWER_ID, "slug": "the-tower", "titolo": "The Tower tarot card", "parola_chiave": "tower"})
    assert ti.main(["generate", "--prompt", TOWER_CARD, *DIMS, "--out", str(isolated / "a.jpg"), "--dry-run"]) == ti.EXIT_RULE
    assert "give --article" in capsys.readouterr().err
    assert ti.main(["generate", "--prompt", TOWER_NO_THOTH, *DIMS, "--article", TOWER_ID, "--dry-run"]) == ti.EXIT_OK
    captured = capsys.readouterr()
    assert str(folder / "foto" / "cover.jpg") in captured.out
    assert "warning: the prompt does not say the card is in the style of the Thoth deck" in captured.err


def test_a_file_whose_prompt_draws_another_card_cannot_go_on_an_article(isolated):
    _titles(isolated, {"id": TOWER_ID, "slug": "the-tower", "titolo": "The Tower tarot card", "parola_chiave": "tower"},
            {"id": "libra-1", "slug": "libra", "titolo": "Libra season balance", "parola_chiave": "libra tarot"})
    pic = isolated / "tower.jpg"
    pic.write_bytes(b"\xff\xd8 tower card")
    Path(str(pic) + ".prompt.txt").write_text(TOWER_CARD, encoding="utf-8")
    assert ti.check_file(TOWER_ID, str(pic)) == ti.sha256_of(pic)
    with pytest.raises(ti.Failure) as err:
        ti.check_file("libra-1", str(pic))
    assert err.value.code == ti.EXIT_RULE and "not about a specific card" in str(err.value)
