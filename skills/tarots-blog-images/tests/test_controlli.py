"""The picture rules of tarots_images.py, offline: no network, no LitMedia, no API (every remote call is replaced).

    backend/.venv/Scripts/python.exe -m pytest skills/tarots-blog-images/tests -q -p no:cacheprovider

The prompts refused here are the real ones of the run that made ~50 covers out of one fixed prompt per section
(the agent's own scripts `publish_sequential_balanced.py` and `publish_50_sequential.py`, plus a few from its
other attempts): cards on velvet, cards on a desk, a journal with cards, a generic mood instead of a scene. Under
the newer rule (cards may be context, never the picture) every one of them is still refused: they are all spreads
or cards as the subject.
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
def test_hermes_prompts_are_still_refused(prompt):
    assert ti.card_problem(prompt)
    assert ti.prompt_problems(prompt, [])
    # even with the house style appended, as the skill asks
    assert ti.card_problem(prompt + ", " + STYLE)
    # each one is a spread, a set of cards or a card as the subject: never just context
    assert {family for family, _w, _what in ti.card_problems(prompt)} & {ti.SPREAD, "many", "subject"}


REFUSED = {
    # the card as the subject: at the start, in the first clause, in the first 8 words, a close-up
    "subject": [
        "a single card tucked between the pages of a notebook on a windowsill",
        "a tarot card showing the High Priestess between two pillars",
        "an old oracle card leaning against a crystal, moonlight through the curtains",
        "a playing card stuck in the frame of a mirror",
        "On a quiet morning the old card waits on the windowsill, rain outside",
        "a single arcanum glowing in the dark",
        "close-up of a card resting on a moss-covered stone in a forest clearing at dawn",
        "a forest clearing at dawn, mist between the birches, a fox, and in the foreground a large card",
        "a Rider-Waite style illustration of a woman with a lion",
        "a lighthouse in a storm in tarot-style artwork with a card frame",
        "Atu XVI of the Thoth trumps",
    ],
    # more than one card
    "many": [
        "CARDS in an old wooden box on a dusty shelf",
        "a worn deck wrapped in black silk on an altar of river stones",
        "an old wooden deck tied with a ribbon",
        "Thoth deck illustrations, Egyptian motifs, purple and gold",
        "a garden at dawn, a bench, and three cards forgotten on it",
        "a pile of tarot under a reading lamp",
        "the Major Arcana painted on the walls of a chapel",
        "a vintage tarocchi box on a shelf",
    ],
    # spreads and layouts
    "spread": [
        "a Celtic Cross spread on a wooden floor",
        "a three-card spread beside a cup of tea",
        "the spread on the table catches the candlelight",
        "a quiet attic, rain on the skylight, a celtic cross layout under the lamp",
        "an empty reading table by a window at dawn, candles burning",
        "a Lenormand reading in a Paris café",
        "a cartomancer's parlour with lace curtains",
        "a velvet cloth with a card laid on the table",
        "two cards face down beside a teacup",
        "a fan of cards in an old woman's hand by the fire",
    ],
    # hands holding or turning a card
    "hands": [
        "a snowy garden at dusk seen from a warm kitchen, an old woman's hands turning over a single card",
        "a harbour at night, gulls asleep on the posts, a sailor holding a card up to the lantern",
        "a quiet library at noon, dust in the sunbeams, a card between her fingers",
    ],
}


@pytest.mark.parametrize("family,prompt", [(f, p) for f, ps in REFUSED.items() for p in ps])
def test_cards_as_the_picture_are_refused(family, prompt):
    found = ti.card_problems(prompt)
    assert found, prompt
    assert family in {f for f, _w, _what in found}, (prompt, found)


@pytest.mark.parametrize("prompt", [
    # ordinary words that are not cards
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
    # tarot as context, the names of the cards as a world or a symbol
    "a lighthouse in a storm, a tarot-inspired scene",
    "a lighthouse struck by lightning on a black cliff, the energy of the Tower",
    "a summer garden heavy with fruit and bees, the abundance of the Empress",
    "the Queen of Cups on a throne by the sea",
    "The Hanged Man suspended from a living tree",
    "the High Priestess between two pillars",
    "a stone fountain overflowing in a cloister at noon, the Ace of Cups as a spring of water",
    "a sunflower field under a white midday sky, a child on a grey pony, the joy of the Sun",
    "a crescent moon over a still pool, two towers far away, a dog and a wolf on the bank: the Moon",
    "a woman on a windy cliff at dawn, a sword-straight posture, the clarity of the Queen of Swords",
    "a forge in a mountain village, sparks and staves of oak, the fire of the Wands",
    "a tarot reader walking home at dusk along a canal, her coat wet with rain",
    # one single small card later in the scene
    "A rain-streaked kitchen window at dawn, a kettle steaming on the stove, a coat on the chair, bread on the "
    "board, and on the windowsill a single card tucked in a notebook",
])
def test_cards_as_context_are_accepted(prompt):
    assert ti.card_problems(prompt) == [], (prompt, ti.card_problems(prompt))


def test_alt_text_describing_a_spread_is_an_error():
    for alt in ("Three tarot cards laid out on a velvet cloth", "A Celtic Cross spread under a lamp",
                "Tarot cards on a velvet tablecloth"):
        with pytest.raises(ti.Failure) as err:
            ti._check_alt(alt)
        assert err.value.code == ti.EXIT_RULE and "spread" in str(err.value)
    assert ti._check_alt("A lone figure on a stone bridge in the rain at dusk")


def test_alt_text_mentioning_a_card_is_only_a_warning(capsys):
    assert ti._check_alt("A tarot card of the Tower propped on a windowsill") == "A tarot card of the Tower propped on a windowsill"
    assert "warning" in capsys.readouterr().err
    # the article's keyword, with a card's name, is not even a warning
    assert ti._check_alt("A lighthouse in a storm, an image of The Tower tarot meaning")
    assert ti._check_alt("A summer garden for the Queen of Cups")
    assert capsys.readouterr().err == ""


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


# Each with its four dimensions (kind, shot, light, setting): different kinds and lights, so they pass in a row.
GOOD = [
    "A lone figure in a dark coat on a stone bridge in soft rain, three overturned glasses on the parapet, two full "
    "glasses still standing behind them catching the last light, a river and a distant village at dusk, seen from a "
    "distance, " + STYLE,
    "A couple seen from behind walking through a high summer meadow full of poppies and ripe wheat, her hand resting "
    "on her belly, a stone farmhouse and fruit trees far away, golden late-afternoon light, wide view, " + STYLE,
    "A lighthouse on a black basalt cliff of the Breton coast in a winter storm, one bolt of lightning splitting the "
    "sky, waves breaking against the rocks, the lamp still burning, seen from the harbour below, looking up, " + STYLE,
    "Ten small brass lanterns hanging in a dark orchard under the stars, six in a cross and four in a rising column, "
    "thin threads of light joining them, seen from above like a constellation, " + STYLE,
]
DIMS = [
    {"kind": "figure-at-distance", "shot": "wide", "light": "overcast", "setting": "river village"},
    {"kind": "figure-from-behind", "shot": "wide", "light": "golden-hour", "setting": "summer meadow"},
    {"kind": "architecture", "shot": "low-angle", "light": "storm-light", "setting": "Breton coast"},
    {"kind": "abstract-symbol", "shot": "aerial", "light": "starlight", "setting": "Normandy orchard"},
]


def _opts(d):
    return ["--kind", d["kind"], "--shot", d["shot"], "--light", d["light"], "--setting", d["setting"]]


@pytest.mark.parametrize("prompt,dims", list(zip(GOOD, DIMS)))
def test_good_prompts_pass(prompt, dims):
    assert ti.prompt_problems(prompt, []) == []
    assert ti.dimension_problems(prompt, dims, []) == []


# ---- similarity -------------------------------------------------------------------------------------------------

def test_good_prompts_are_different_enough_from_each_other():
    for i, a in enumerate(GOOD):
        assert ti.prompt_problems(a, GOOD[:i]) == [], a
        assert ti.dimension_problems(a, DIMS[i], DIMS[:i]) == [], a


def test_a_near_copy_is_refused_with_the_closest_prompt_and_percentage():
    earlier = [GOOD[2]]
    again = ("A lighthouse on a dark basalt cliff of the Breton coast in a spring storm, a bolt of lightning splitting "
             "the sky, waves breaking against the rocks, the lamp burning, seen from the harbour below, " + STYLE)
    assert ti.similarity(again, GOOD[2]) >= ti.MAX_SIMILARITY
    problems = ti.prompt_problems(again, earlier)
    assert len(problems) == 1 and "too close" in problems[0]
    assert "%" in problems[0] and "lighthouse on a black basalt cliff" in problems[0]
    assert ti.HOUSE_STYLE not in problems[0]  # the closest prompt is shown without the style line


def _fake_litmedia(script, args, timeout):
    out_dir = Path(args[args.index("--output-dir") + 1])
    (out_dir / "image_1.jpg").write_bytes(b"\xff\xd8 fake picture " + args[args.index("--prompt") + 1].encode())

    class Done:
        returncode, stdout, stderr = 0, "", ""
    return Done()


def test_same_prompt_twice_is_refused_by_generate(isolated, monkeypatch):
    monkeypatch.setattr(ti, "balance", lambda: 100)
    monkeypatch.setattr(ti, "_litmedia", _fake_litmedia)
    out = isolated / "work" / "bridge-cover.jpg"
    assert ti.main(["generate", "--prompt", GOOD[0], *_opts(DIMS[0]), "--out", str(out)]) == ti.EXIT_OK

    data = json.loads(ti.PROGRESS_PATH.read_text(encoding="utf-8"))
    entry = data["_generated"][0]
    assert entry["prompt"] == GOOD[0] and entry["file"] == str(out) and entry["when"]
    assert entry["sha256"] == ti.sha256_of(out)
    # the four dimensions are recorded with the picture
    assert {k: entry[k] for k in ("kind", "shot", "light", "setting")} == DIMS[0]

    # the same prompt again (also as a dry run) is refused before LitMedia is asked anything
    monkeypatch.setattr(ti, "_litmedia", lambda *a, **k: pytest.fail("LitMedia called for a refused prompt"))
    assert ti.main(["generate", "--prompt", GOOD[0], *_opts(DIMS[1]), "--out", str(isolated / "b.jpg"), "--dry-run"]) == ti.EXIT_RULE
    assert ti.main(["generate", "--prompt", GOOD[0], *_opts(DIMS[1]), "--out", str(isolated / "b.jpg")]) == ti.EXIT_RULE
    # a different scene is fine
    assert ti.main(["generate", "--prompt", GOOD[1], *_opts(DIMS[1]), "--out", str(isolated / "c.jpg"), "--dry-run"]) == ti.EXIT_OK


def test_prompts_kept_by_the_older_progress_format_count_too(isolated):
    old = {"post-1": {"cover": {"file": "x.jpg", "url": "/u", "alt": "a bridge", "prompt": GOOD[0], "when": "2026-10-01"},
                      "inline": []}}
    ti.PROGRESS_PATH.write_text(json.dumps(old), encoding="utf-8")
    assert ti._known_prompts(ti._progress()) == [GOOD[0]]
    assert ti.main(["prompt-check", "--prompt", GOOD[0], *_opts(DIMS[0])]) == ti.EXIT_RULE


# ---- the four dimensions ----------------------------------------------------------------------------------------

def _history(*rows):
    """Earlier pictures with their dimensions, oldest first; the prompts share nothing with the ones tested."""
    return [{"prompt": f"zq{i}", "file": f"f{i}.jpg", "sha256": f"s{i}", "aspect": "3:2", "when": "2026-10-05T10:00:00",
             "kind": k, "shot": s, "light": l, "setting": st} for i, (k, s, l, st) in enumerate(rows)]


def _write(history, extra=None):
    ti.PROGRESS_PATH.write_text(json.dumps({"_generated": history, **(extra or {})}), encoding="utf-8")


def test_the_four_options_are_required(isolated):
    for missing in ("--kind", "--shot", "--light", "--setting"):
        args = ["prompt-check", "--prompt", GOOD[0], *_opts(DIMS[0])]
        i = args.index(missing)
        del args[i:i + 2]
        with pytest.raises(SystemExit):
            ti.main(args)


def test_a_value_outside_the_catalog_is_a_usage_error(isolated, capsys):
    bad = dict(DIMS[0], kind="tarot-table")
    assert ti.main(["prompt-check", "--prompt", GOOD[0], *_opts(bad)]) == ti.EXIT_USAGE
    err = capsys.readouterr().err
    assert "--kind «tarot-table» is not in the catalog" in err and "landscape" in err and "journey-or-path" in err
    # spelling is forgiven: case, spaces and underscores
    assert ti.dimensions("Figure At Distance", "WIDE", "golden_hour", "  river   village ")["kind"] == "figure-at-distance"
    with pytest.raises(ti.Failure):
        ti.dimensions("landscape", "wide", "dawn", "a very long setting that is really a whole scene of many words")


def test_catalogs_have_the_promised_size():
    assert len(ti.KINDS) >= 16 and len(ti.SHOTS) == 12 and len(ti.LIGHTS) == 10
    assert "hands-and-gesture" in ti.KINDS and "firelight" in ti.LIGHTS and "over-the-shoulder" in ti.SHOTS


def test_a_kind_of_the_last_three_is_refused_and_the_free_kinds_are_listed():
    history = _history(("landscape", "wide", "dawn", "Mediterranean harbour"),
                       ("animal", "close-up", "moonlight", "Japanese garden"),
                       ("interior", "symmetrical", "midday", "Victorian library"))
    problems = ti.dimension_problems(GOOD[3], dict(DIMS[3], kind="animal"), history)
    assert len(problems) == 1 and "--kind animal is the kind of one of the last 3" in problems[0]
    assert "Kinds free now:" in problems[0] and "architecture" in problems[0]
    assert "landscape," not in problems[0].split("Kinds free now:")[1]
    # four pictures later the kind is free again
    later = history + _history(("celestial", "wide", "starlight", "a"), ("street-or-market", "wide", "overcast", "b"),
                               ("journey-or-path", "aerial", "dawn", "c"))
    assert ti.dimension_problems(GOOD[3], dict(DIMS[3], kind="animal"), later) == []


def test_a_kind_and_shot_pair_of_the_last_twenty_is_refused():
    history = _history(("abstract-symbol", "aerial", "dawn", "x"), *[(k, "wide", "midday", f"s{i}") for i, k in
                                                                     enumerate(["landscape", "animal", "interior"])])
    problems = ti.dimension_problems(GOOD[3], DIMS[3], history)
    assert len(problems) == 1 and "--kind abstract-symbol with --shot aerial" in problems[0]
    assert "Shots still free with abstract-symbol:" in problems[0] and "aerial," not in problems[0].split("free with")[1]
    # 20 pictures later the pair is free again
    filler = _history(*[(k, "wide", l, f"t{i}") for i, (k, l) in
                        enumerate(zip(["landscape", "animal", "interior", "celestial"] * 5, ["midday", "dawn"] * 10))])
    assert ti.dimension_problems(GOOD[3], DIMS[3], history[:1] + filler) == []


def test_the_light_of_the_last_two_is_refused():
    history = _history(("landscape", "wide", "starlight", "a"), ("animal", "wide", "midday", "b"))
    problems = ti.dimension_problems(GOOD[3], DIMS[3], history)
    assert len(problems) == 1 and "--light starlight is the light of one of the last 2" in problems[0]
    assert "Lights free now:" in problems[0] and "starlight" not in problems[0].split("Lights free now:")[1]


def test_firelight_is_rare():
    prompt = ("A potter's hands shaping a wet clay bowl on the wheel in a small Umbrian workshop at night, firelight "
              "from the kiln on the shelves of drying cups, seen close-up, " + STYLE)
    dims = {"kind": "hands-and-gesture", "shot": "close-up", "light": "firelight", "setting": "Umbrian workshop"}
    assert ti.prompt_problems(prompt, []) == [] and ti.dimension_problems(prompt, dims, []) == []
    history = _history(("interior", "wide", "firelight", "a"), *[("landscape", "wide", l, f"b{i}") for i, l in
                                                                 enumerate(["dawn", "midday", "dawn", "midday", "dawn"])])
    problems = ti.dimension_problems(prompt, dims, history)
    assert len(problems) == 1 and "firelight stays rare: it was used 6 picture(s) ago" in problems[0]
    assert "Lights free now:" in problems[0]
    # once it has left the last ten it is allowed again
    more = _history(*[("landscape", "wide", l, f"c{i}") for i, l in enumerate(["dawn", "midday", "dawn", "midday"])])
    assert len(ti.dimension_problems(prompt, dims, history + more)) == 1
    assert ti.dimension_problems(prompt, dims, history + more + _history(("animal", "wide", "dawn", "d"))) == []


def test_a_setting_of_the_last_ten_is_refused_after_normalisation():
    history = _history(("landscape", "wide", "dawn", "The Mediterranean harbours"), ("animal", "wide", "midday", "b"))
    prompt = ("A fisherman seen from behind mending a red net on the quay of a small Mediterranean harbour, gulls on "
              "the bollards, sunset light on the water, wide view, " + STYLE)
    dims = {"kind": "figure-from-behind", "shot": "wide", "light": "golden-hour", "setting": "harbour, Mediterranean"}
    problems = ti.dimension_problems(prompt, dims, history)
    assert len(problems) == 1 and "--setting «harbour, Mediterranean» was already used" in problems[0]
    assert "The Mediterranean harbours" in problems[0] and "another place, culture or era" in problems[0]
    assert ti.setting_key("Café de Flore") == ti.setting_key("cafe  de flore")


def test_the_prompt_must_show_the_declared_light_shot_and_setting():
    dims = dict(DIMS[3], light="dawn", shot="over-the-shoulder", setting="Kyoto temple")
    problems = ti.dimension_problems(GOOD[3], dims, [])
    assert len(problems) == 3
    assert "does not show the light declared with --light dawn" in problems[0] and "'sunrise'" in problems[0]
    assert "does not show the composition declared with --shot over-the-shoulder" in problems[1]
    assert "does not name the setting declared with --setting «Kyoto temple»" in problems[2]
    # the house style's "soft natural light" never counts as a declared light
    assert ti.dimension_problems("a field, wide, " + STYLE, dict(DIMS[1], setting="field"), []) != []


def test_older_entries_without_dimensions_count_only_for_similarity(isolated):
    _write([{"prompt": GOOD[2], "file": "old.jpg", "sha256": "x", "aspect": "3:2", "when": "2026-10-01"}])
    assert ti.dimension_history(ti._progress()) == []
    # same kind, shot and light as the old entry's scene: no dimension rule, but the prompt is too similar
    assert ti.main(["prompt-check", "--prompt", GOOD[2], *_opts(DIMS[2])]) == ti.EXIT_RULE
    assert ti.main(["prompt-check", "--prompt", GOOD[3], *_opts(dict(DIMS[3], kind="architecture"))]) == ti.EXIT_OK


# ---- prompt-check, catalog, progress -----------------------------------------------------------------------------

def test_prompt_check_is_offline_and_reports(capsys):
    assert ti.main(["prompt-check", "--prompt", GOOD[1], *_opts(DIMS[1])]) == ti.EXIT_OK
    out = capsys.readouterr().out
    assert "ok:" in out and "content words:" in out and "figure-from-behind · wide · golden-hour" in out

    assert ti.main(["prompt-check", "--prompt", HERMES_BALANCED[0], *_opts(DIMS[1])]) == ti.EXIT_RULE
    out = capsys.readouterr().out
    assert "REFUSED" in out and "card" in out

    assert ti.main(["prompt-check", "--prompt", GOOD[1], *_opts(DIMS[1]), "--alt", "Three tarot cards laid out on velvet"]) == ti.EXIT_RULE
    assert ti.main(["prompt-check", "--prompt", GOOD[1], *_opts(DIMS[1]), "--alt", "A tarot card of the Empress on a gate"]) == ti.EXIT_OK
    assert "alt text warning" in capsys.readouterr().out


def test_catalog_lists_every_value_and_what_is_free(isolated, capsys):
    _write(_history(("landscape", "wide", "dawn", "Mediterranean harbour")))
    assert ti.main(["catalog"]) == ti.EXIT_OK
    out = capsys.readouterr().out
    for name in list(ti.KINDS) + list(ti.SHOTS) + list(ti.LIGHTS):
        assert name in out
    assert "Free for the next picture" in out and "(not: landscape)" in out and "Mediterranean harbour" in out


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


def test_a_file_whose_prompt_has_a_card_only_as_context_is_accepted(isolated):
    pic = _picture(isolated, "tower.jpg", b"\xff\xd8 lighthouse")
    Path(pic + ".prompt.txt").write_text(GOOD[2] + ", the energy of the Tower", encoding="utf-8")
    assert ti.check_file("post-A", pic) == ti.sha256_of(pic)


def test_progress_lists_the_last_twenty_with_their_dimensions(isolated, capsys):
    rows = [{"prompt": p, "file": f"f{i}.jpg", "sha256": str(i), "aspect": "3:2", "when": "2026-10-05T10:00:00", **d}
            for i, (p, d) in enumerate(zip(GOOD, DIMS))]
    older = [{"prompt": f"older scene number {i}", "file": f"o{i}.jpg", "sha256": f"o{i}", "aspect": "3:2",
              "when": "2026-10-01T10:00:00"} for i in range(20)]
    data = {
        "_generated": older + rows,
        "_used": {"0": {"post": "post-A", "kind": "cover", "file": "f0.jpg", "when": "2026-10-05"}},
        "post-A": {"cover": {"file": "f0.jpg", "prompt": GOOD[0]}, "inline": []},
    }
    ti.PROGRESS_PATH.write_text(json.dumps(data), encoding="utf-8")
    assert ti.main(["progress"]) == ti.EXIT_OK
    out = capsys.readouterr().out
    lines = out.split("\n")
    first = next(i for i, l in enumerate(lines) if l.strip().startswith("1."))
    assert "abstract-symbol · aerial · starlight · Normandy orchard" in lines[first]  # newest first
    assert "lanterns" in lines[first + 1]
    assert "Last 20 pictures generated" in out and " 20. " in out and " 21. " not in out
    assert "(no dimensions: an older record)" in out
    assert "Free for the next picture" in out and "(not: abstract-symbol, architecture, figure-from-behind)" in out
    assert "_generated" not in out and "_used" not in out
