"""The picture rules of tarots_images.py, offline: no network, no LitMedia, no API (every remote call is replaced).

    backend/.venv/Scripts/python.exe -m pytest skills/tarots-blog-images/tests -q -p no:cacheprovider

The prompts refused here are the real ones of the run that made ~50 covers out of one fixed prompt per section
(the agent's own scripts `publish_sequential_balanced.py` and `publish_50_sequential.py`, plus a few from its
other attempts): cards on velvet, cards on a desk, a journal with cards, a generic mood instead of a scene.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "tarots_images.py"
_spec = importlib.util.spec_from_file_location("tarots_images", SCRIPT)
ti = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ti)

STYLE = ti.HOUSE_STYLE


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    """Each test gets its own progress file, and any attempt to reach the network fails loudly."""
    monkeypatch.setattr(ti, "PROGRESS_PATH", tmp_path / "images-progress.json")

    def no_network(*_a, **_k):
        raise AssertionError("a check touched the network")

    monkeypatch.setattr(ti, "call", no_network)
    monkeypatch.setattr(ti, "balance", no_network)
    monkeypatch.setattr(ti, "_litmedia", no_network)
    return tmp_path


# ---- cards ------------------------------------------------------------------------------------------------------

# publish_sequential_balanced.py, SECTION_PROMPTS (one per section, reused for every article of that section)
HERMES_BALANCED = [
    "Mystical tarot card spread on a velvet tablecloth, romantic hearts and roses floating in golden light, ethereal "
    "lighting, deep purple and warm red color palette, magical atmosphere of love and passion, professional photography style",
    "Tarot cards layout with romantic symbolism, intertwined hands, heart motifs in gold stars, soft pink and purple "
    "tones, intimate and connected energy, mystical lighting, professional photography",
    "Professional tarot reading on dark office desk, achievement symbols like crowns and coins, blue and gold color "
    "scheme, success and ambition motifs, focused determination, ethereal business lighting",
    "Meditative tarot spread with chakras glowing above, divine golden light beams from heaven, spiritual symbols and "
    "sacred geometry, ethereal white and purple glow, transcendent atmosphere, professional photography",
    "Ancient tarot cards with detailed symbolic elements, mysterious runes and cryptic icons scattered around, dark "
    "mystical background with glowing magical sigils, arcane and esoteric atmosphere, professional photography",
    "Open tarot journal notebook on wooden table with writing pen, three tarot cards laid out for study, soft warm lamp "
    "lighting, contemplative mood, coffee cup nearby, scholarly and reflective atmosphere",
]
# publish_50_sequential.py, generate_cover()
HERMES_50 = [
    "Mystical tarot card with hearts and roses, golden stars, romantic atmosphere, deep purple and pink palette, ethereal lighting",
    "Elegant tarot spread showing connection and partnership, golden moon symbols, intimate setting, warm colors",
    "Spiritual tarot imagery with sacred geometry, cosmic background, meditation aura, mystical purple and gold tones",
    "Professional tarot card with ambition symbols, success motifs, clean composition, rich emerald and gold palette",
    "Symbolic tarot artwork with archetypal elements, shadow play, intellectual atmosphere, deep blue and silver tones",
    "Personal tarot journal layout, handwritten notes visible, reflective mood, soft warm lighting, cozy setting",
]


@pytest.mark.parametrize("prompt", HERMES_BALANCED + HERMES_50)
def test_hermes_prompts_are_refused(prompt):
    assert ti.card_problem(prompt)
    assert ti.prompt_problems(prompt, [])
    # even with the house style appended, as the skill asks
    assert ti.card_problem(prompt + ", " + STYLE)


@pytest.mark.parametrize("prompt", [
    # without the word "tarot": every way of asking for a card
    "a single card tucked between the pages of a notebook on a windowsill",
    "CARDS face down on a velvet cloth under a full moon",
    "a fan of cards in an old woman's hand by the fire",
    "a worn deck wrapped in black silk on an altar of river stones",
    "an old wooden deck tied with a ribbon",
    "Thoth deck illustrations, Egyptian motifs, purple and gold",
    "the Major Arcana painted on the walls of a chapel",
    "a single arcanum glowing in the dark",
    "an empty reading table by a window at dawn, candles burning",
    "a Celtic Cross spread on a wooden floor",
    "a three-card spread beside a cup of tea",
    "the spread on the table catches the candlelight",
    "a Rider-Waite style illustration of a woman with a lion",
    "a playing card stuck in the frame of a mirror",
    "an oracle card leaning against a crystal",
    "a cartomancer's parlour with lace curtains",
    "a Lenormand reading in a Paris café",
    "the Queen of Cups on a throne by the sea",
    "The Hanged Man suspended from a living tree",
    "the High Priestess between two pillars",
    "a vintage tarocchi box on a shelf",
    "Atu XVI of the Thoth trumps",
])
def test_every_kind_of_card_is_refused(prompt):
    assert ti.card_problem(prompt), prompt


@pytest.mark.parametrize("prompt", [
    "a red cardinal on a snowy branch at first light",
    "a woman in a grey cardigan walking a dog along a canal",
    "discarded letters and a broken wax seal on a stone step",
    "cardboard boxes stacked in an empty flat on moving day",
    "cardamom pods and cinnamon in a copper bowl",
    "the deck of a sailing ship at dawn, ropes coiled by the mast",
    "deck chairs on a wooden pier in late September",
    "a ferry deck crowded with gulls, the island coming closer",
    "a heron with its wings spread wide over a marsh",
    "evening light spreading across a wheat field",
    "a map spread out on a kitchen table, a compass on it",
    "the spread of dawn light across the hills",
    "a weathered Celtic cross on an Irish hillside in fog",
    "a woman reading a letter by a rain-streaked window",
    "an arcane brass astrolabe in a museum case",
    "an ibis wading at dusk, sacred bird of the Egyptian god Thoth",
    "a postcard pinned to a corkboard above a desk",
    "a queen bee among honeycombs, a beekeeper's gloved hand",
])
def test_ordinary_words_are_not_cards(prompt):
    assert ti.card_problem(prompt) is None, prompt


def test_the_word_tarot_is_refused_in_prompts_but_a_keyword_may_stay_in_alt_text():
    assert ti.card_problem("a lighthouse in a storm, a tarot-inspired scene")
    assert ti.card_problem("A lighthouse in a storm, an image of The Tower tarot meaning", alt=True) is None
    assert ti.card_problem("A summer garden for the Queen of Cups", alt=True) is None
    assert ti.card_problem("Tarot cards on a velvet tablecloth", alt=True)


def test_alt_text_describing_cards_is_an_error():
    with pytest.raises(ti.Failure) as err:
        ti._check_alt("Three tarot cards laid out on a velvet cloth")
    assert err.value.code == ti.EXIT_RULE
    assert ti._check_alt("A lone figure on a stone bridge in the rain at dusk")


def test_allow_cards_option_is_gone(isolated):
    with pytest.raises(SystemExit):
        ti.main(["generate", "--prompt", "x", "--out", str(isolated / "a.jpg"), "--allow-cards", "--dry-run"])


# ---- generic prompts --------------------------------------------------------------------------------------------

@pytest.mark.parametrize("prompt", [
    # card-free prompts of the same run: a mood for a category, not a scene from an article
    "Romantic couple embracing under moonlight, love and passion, ethereal atmosphere, deep red and pink palette",
    "Professional setting with upward trajectory, ambition and success, blue and gold tones",
    "Meditative figure in purple light, inner wisdom and enlightenment, mystical atmosphere",
    "Mystical moonlit night scene, full silver moon through wispy clouds, dreamy fog over tranquil lake, deep blue "
    "purple ethereal lighting, professional photography style",
    "a beautiful mystical scene, " + STYLE,
])
def test_generic_prompts_are_refused(prompt):
    problems = ti.prompt_problems(prompt, [])
    assert any("describe a concrete scene from this article" in p.lower() for p in problems), problems


def test_house_style_words_do_not_count_as_content():
    assert ti.content_words(STYLE) == set()
    # a paraphrase of part of the style does not count either
    assert ti.content_words("editorial painterly illustration, deep plum shadows, brass gold") == set()


GOOD = [
    "A lone figure in a dark coat on a stone bridge in soft rain, three overturned glasses on the parapet, two full "
    "glasses still standing behind them catching the last light, a river and a distant village at dusk, seen from a "
    "distance, " + STYLE,
    "A couple seen from behind walking through a high summer meadow full of poppies and ripe wheat, her hand resting "
    "on her belly, a stone farmhouse and fruit trees far away, golden late-afternoon light, wide view, " + STYLE,
    "A lighthouse on a black basalt cliff in a winter storm, one bolt of lightning splitting the sky, waves breaking "
    "against the rocks, the lamp still burning, seen from a fishing harbour far below, " + STYLE,
    "Ten small brass lanterns hanging in a dark orchard at night, six in a cross and four in a rising column, thin "
    "threads of light joining them, seen from above like a constellation, " + STYLE,
]


@pytest.mark.parametrize("prompt", GOOD)
def test_good_prompts_pass(prompt):
    assert ti.prompt_problems(prompt, []) == []


# ---- similarity -------------------------------------------------------------------------------------------------

def test_good_prompts_are_different_enough_from_each_other():
    for i, a in enumerate(GOOD):
        assert ti.prompt_problems(a, GOOD[:i]) == [], a


def test_a_near_copy_is_refused_with_the_closest_prompt_and_percentage():
    earlier = [GOOD[2]]
    again = ("A lighthouse on a dark basalt cliff in a spring storm, a bolt of lightning splitting the sky, waves "
             "breaking against the rocks, the lamp burning, seen from a harbour far below, " + STYLE)
    assert ti.similarity(again, GOOD[2]) >= ti.MAX_SIMILARITY
    problems = ti.prompt_problems(again, earlier)
    assert len(problems) == 1 and "too close" in problems[0]
    assert "%" in problems[0] and "lighthouse on a black basalt cliff" in problems[0]
    assert ti.HOUSE_STYLE not in problems[0]  # the closest prompt is shown without the style line


def test_same_prompt_twice_is_refused_by_generate(isolated, monkeypatch):
    monkeypatch.setattr(ti, "balance", lambda: 100)

    def fake_litmedia(script, args, timeout):
        out_dir = Path(args[args.index("--output-dir") + 1])
        (out_dir / "image_1.jpg").write_bytes(b"\xff\xd8 fake picture " + args[args.index("--prompt") + 1].encode())

        class Done:
            returncode, stdout, stderr = 0, "", ""
        return Done()

    monkeypatch.setattr(ti, "_litmedia", fake_litmedia)
    out = isolated / "work" / "bridge-cover.jpg"
    assert ti.main(["generate", "--prompt", GOOD[0], "--out", str(out)]) == ti.EXIT_OK

    data = json.loads(ti.PROGRESS_PATH.read_text(encoding="utf-8"))
    entry = data["_generated"][0]
    assert entry["prompt"] == GOOD[0] and entry["file"] == str(out) and entry["when"]
    assert entry["sha256"] == ti.sha256_of(out)

    # the same prompt again (also as a dry run) is refused before LitMedia is asked anything
    monkeypatch.setattr(ti, "_litmedia", lambda *a, **k: pytest.fail("LitMedia called for a refused prompt"))
    assert ti.main(["generate", "--prompt", GOOD[0], "--out", str(isolated / "b.jpg"), "--dry-run"]) == ti.EXIT_RULE
    assert ti.main(["generate", "--prompt", GOOD[0], "--out", str(isolated / "b.jpg")]) == ti.EXIT_RULE
    # a different scene is fine
    assert ti.main(["generate", "--prompt", GOOD[1], "--out", str(isolated / "c.jpg"), "--dry-run"]) == ti.EXIT_OK


def test_prompts_kept_by_the_older_progress_format_count_too(isolated):
    old = {"post-1": {"cover": {"file": "x.jpg", "url": "/u", "alt": "a bridge", "prompt": GOOD[0], "when": "2026-10-01"},
                      "inline": []}}
    ti.PROGRESS_PATH.write_text(json.dumps(old), encoding="utf-8")
    assert ti._known_prompts(ti._progress()) == [GOOD[0]]
    assert ti.main(["prompt-check", "--prompt", GOOD[0]]) == ti.EXIT_RULE


# ---- prompt-check -----------------------------------------------------------------------------------------------

def test_prompt_check_is_offline_and_reports(capsys):
    assert ti.main(["prompt-check", "--prompt", GOOD[1]]) == ti.EXIT_OK
    out = capsys.readouterr().out
    assert "ok:" in out and "content words:" in out

    assert ti.main(["prompt-check", "--prompt", HERMES_BALANCED[0]]) == ti.EXIT_RULE
    out = capsys.readouterr().out
    assert "REFUSED" in out and "card" in out

    assert ti.main(["prompt-check", "--prompt", GOOD[1], "--alt", "Three tarot cards on velvet"]) == ti.EXIT_RULE


# ---- the same file on two articles ------------------------------------------------------------------------------

def _picture(folder: Path, name: str, content: bytes) -> str:
    path = folder / name
    path.write_bytes(content)
    return str(path)


def test_a_cover_already_used_for_another_article_is_refused(isolated):
    pic = _picture(isolated, "cover.jpg", b"\xff\xd8 one picture")
    ti._record("post-A", "cover", {"file": pic, "sha256": ti.sha256_of(pic), "url": "/m/1", "alt": "a bridge"})
    data = json.loads(ti.PROGRESS_PATH.read_text(encoding="utf-8"))
    assert data["_used"][ti.sha256_of(pic)]["post"] == "post-A"

    copy = _picture(isolated, "renamed-copy.png", b"\xff\xd8 one picture")  # same bytes, another name
    assert ti.main(["cover", "post-B", copy, "--alt", "A lone figure on a bridge", "--dry-run"]) == ti.EXIT_RULE
    assert ti.main(["inline", "post-B", "--add", "1", copy, "A lone figure on a bridge", "--dry-run"]) == ti.EXIT_RULE


def test_the_same_article_may_get_its_own_picture_again(isolated, monkeypatch):
    pic = _picture(isolated, "cover.jpg", b"\xff\xd8 one picture")
    ti._record("post-A", "cover", {"file": pic, "sha256": ti.sha256_of(pic), "url": "/m/1", "alt": "a bridge"})
    monkeypatch.setattr(ti, "call", lambda *a, **k: {"titolo": "An article"})
    assert ti.main(["cover", "post-A", pic, "--alt", "A lone figure on a bridge", "--dry-run"]) == ti.EXIT_OK


def test_older_records_without_hash_are_hashed_from_their_file(isolated):
    pic = _picture(isolated, "old.jpg", b"\xff\xd8 an older picture")
    old = {"post-A": {"cover": {"file": pic, "url": "/m/1", "alt": "a bridge", "when": "2026-10-01"}, "inline": []}}
    ti.PROGRESS_PATH.write_text(json.dumps(old), encoding="utf-8")
    assert ti._used_files(ti._progress()) == {ti.sha256_of(pic): "post-A"}
    with pytest.raises(ti.Failure):
        ti.check_file("post-B", pic)


def test_one_inline_command_cannot_use_the_same_picture_twice(isolated):
    a = _picture(isolated, "a.jpg", b"\xff\xd8 same")
    b = _picture(isolated, "b.jpg", b"\xff\xd8 same")
    code = ti.main(["inline", "post-A", "--add", "1", a, "A heron over a marsh", "--add", "3", b,
                    "A heron over a marsh again", "--dry-run"])
    assert code == ti.EXIT_RULE


def test_a_file_generated_from_a_card_prompt_is_refused(isolated):
    pic = _picture(isolated, "old-cover.jpg", b"\xff\xd8 cards")
    Path(pic + ".prompt.txt").write_text(HERMES_BALANCED[0], encoding="utf-8")
    with pytest.raises(ti.Failure) as err:
        ti.check_file("post-A", pic)
    assert err.value.code == ti.EXIT_RULE


def test_progress_lists_the_last_pictures_and_skips_internal_keys(isolated, capsys):
    data = {
        "_generated": [{"prompt": p, "file": f"f{i}.jpg", "sha256": str(i), "aspect": "3:2", "when": "2026-10-05T10:00:00"}
                       for i, p in enumerate(GOOD)],
        "_used": {"0": {"post": "post-A", "kind": "cover", "file": "f0.jpg", "when": "2026-10-05"}},
        "post-A": {"cover": {"file": "f0.jpg", "prompt": GOOD[0]}, "inline": []},
    }
    ti.PROGRESS_PATH.write_text(json.dumps(data), encoding="utf-8")
    assert ti.main(["progress"]) == ti.EXIT_OK
    out = capsys.readouterr().out
    assert "Last pictures generated" in out and "lanterns" in out.split("\n")[2]  # newest first
    assert "_generated" not in out and "_used" not in out
