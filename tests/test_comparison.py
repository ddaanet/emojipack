"""Tests for emoji pack comparison."""

from emojipack.comparison import (
    EmojiComparison,
    EmojiMatch,
    KeywordComparison,
    KeywordMatch,
    compare_emojis,
    compare_keywords,
    normalize_emoji,
)
from emojipack.pack import SnippetPack
from emojipack.snippets import AlfredSnippet


def test_compare_packs_with_different_emojis():
    """Compare two packs with different emoji content."""
    theirs_snippets = [
        AlfredSnippet("thumbsup", "👍 Thumbs up", "👍", uid="thumbsup-1F44D"),
        AlfredSnippet("+1", "👍 Thumbs up", "👍", uid="+1-1F44D"),
        AlfredSnippet("heart", "❤️ Red heart", "❤️", uid="heart-2764"),
    ]
    mine_snippets = [
        AlfredSnippet("heart", "❤️ Red heart", "❤️", uid="heart-2764"),
        AlfredSnippet("tada", "🎉 Party popper", "🎉", uid="tada-1F389"),
    ]
    theirs = SnippetPack(prefix=":", suffix=":", snippets=theirs_snippets)
    mine = SnippetPack(prefix=":", suffix=":", snippets=mine_snippets)
    result = compare_emojis(theirs, mine)
    expected = EmojiComparison(
        found={
            "❤️": EmojiMatch(
                theirs=[theirs_snippets[2]], mine=[mine_snippets[0]]
            )
        },
        added_emoji_presentation={},
        removed_space={},
        removed={"👍": [theirs_snippets[0], theirs_snippets[1]]},
        added={"🎉": [mine_snippets[1]]},
    )
    assert result == expected


def test_compare_packs_ignores_comment_snippets():
    """Compare packs ignores snippets with names starting with #."""
    theirs = SnippetPack(
        prefix=":",
        suffix=":",
        snippets=[
            AlfredSnippet("comment", "# Comment", "💬", "c1"),
        ],
    )
    mine = SnippetPack(
        prefix=":",
        suffix=":",
        snippets=[
            AlfredSnippet("comment2", "# Another", "📝", "c2"),
        ],
    )
    result = compare_emojis(theirs, mine)
    expected = EmojiComparison(
        found={},
        added_emoji_presentation={},
        removed_space={},
        added={},
        removed={},
    )
    assert result == expected


def test_compare_packs_found_exact_matches():
    """Emojis with exact content match appear in found category."""
    heart_theirs = AlfredSnippet(
        keyword="heart", name="❤️ Red heart", snippet="❤️", uid="h1"
    )
    heart_mine = AlfredSnippet(
        keyword="heart", name="❤️ Red heart", snippet="❤️", uid="h2"
    )
    theirs = SnippetPack(prefix=":", suffix=":", snippets=[heart_theirs])
    mine = SnippetPack(prefix=":", suffix=":", snippets=[heart_mine])

    result = compare_emojis(theirs, mine)

    expected = EmojiComparison(
        found={"❤️": EmojiMatch(theirs=[heart_theirs], mine=[heart_mine])},
        added_emoji_presentation={},
        removed_space={},
        added={},
        removed={},
    )
    assert result == expected


def test_compare_packs_added_emoji_presentation():
    """Emojis where mine adds U+FE0F appear in added_emoji_presentation."""
    heart_plain = AlfredSnippet(
        "heart", "\u2764 Red heart", "\u2764", uid="h1"
    )
    heart_presentation = AlfredSnippet(
        "heart", "\u2764\ufe0f Red heart", "\u2764\ufe0f", uid="h2"
    )
    theirs = SnippetPack(prefix=":", suffix=":", snippets=[heart_plain])
    mine = SnippetPack(prefix=":", suffix=":", snippets=[heart_presentation])

    result = compare_emojis(theirs, mine)

    expected = EmojiComparison(
        found={},
        added_emoji_presentation={
            "\u2764\ufe0f": EmojiMatch(
                theirs=[heart_plain], mine=[heart_presentation]
            )
        },
        removed_space={},
        added={},
        removed={},
    )
    assert result == expected


def test_compare_packs_removed_space():
    """Emojis where mine removes spaces appear in removed_space."""
    unicorn_space = AlfredSnippet("unicorn", "🦄 Unicorn", "🦄 ", uid="u1")
    unicorn_no_space = AlfredSnippet("unicorn", "🦄 Unicorn", "🦄", uid="u2")
    theirs = SnippetPack(prefix=":", suffix=":", snippets=[unicorn_space])
    mine = SnippetPack(prefix=":", suffix=":", snippets=[unicorn_no_space])

    result = compare_emojis(theirs, mine)

    expected = EmojiComparison(
        found={},
        added_emoji_presentation={},
        removed_space={
            "🦄 ": EmojiMatch(theirs=[unicorn_space], mine=[unicorn_no_space])
        },
        added={},
        removed={},
    )
    assert result == expected


def test_compare_packs_keycap_emoji_presentation():
    """Keycap emojis with variation selector inserted before keycap."""
    keycap_plain = AlfredSnippet("1", "1⃣ Keycap 1", "\u0031\u20e3", uid="k1")
    keycap_vs = AlfredSnippet(
        "1", "1️⃣ Keycap 1", "\u0031\ufe0f\u20e3", uid="k2"
    )
    theirs = SnippetPack(prefix=":", suffix=":", snippets=[keycap_plain])
    mine = SnippetPack(prefix=":", suffix=":", snippets=[keycap_vs])

    result = compare_emojis(theirs, mine)

    expected = EmojiComparison(
        found={},
        added_emoji_presentation={
            "\u0031\ufe0f\u20e3": EmojiMatch(
                theirs=[keycap_plain], mine=[keycap_vs]
            )
        },
        removed_space={},
        added={},
        removed={},
    )
    assert result == expected


def test_compare_packs_all_categories():
    """Test with emojis in all different categories simultaneously."""
    theirs_snippets = [
        AlfredSnippet(
            "heart", "\u2764\ufe0f Red heart", "\u2764\ufe0f", uid="1"
        ),
        AlfredSnippet("star", "\u2b50 Star", "\u2b50", uid="2"),
        AlfredSnippet("unicorn", "🦄 Unicorn", "🦄 ", uid="3"),
        AlfredSnippet("old", "👴 Old", "👴", uid="4"),
    ]
    mine_snippets = [
        AlfredSnippet(
            "heart", "\u2764\ufe0f Red heart", "\u2764\ufe0f", uid="5"
        ),
        AlfredSnippet("star", "\u2b50\ufe0f Star", "\u2b50\ufe0f", uid="6"),
        AlfredSnippet("unicorn", "🦄 Unicorn", "🦄", uid="7"),
        AlfredSnippet("new", "🎉 New", "🎉", uid="8"),
    ]
    theirs = SnippetPack(prefix=":", suffix=":", snippets=theirs_snippets)
    mine = SnippetPack(prefix=":", suffix=":", snippets=mine_snippets)

    result = compare_emojis(theirs, mine)

    expected = EmojiComparison(
        found={
            "\u2764\ufe0f": EmojiMatch(
                theirs=[theirs_snippets[0]], mine=[mine_snippets[0]]
            )
        },
        added_emoji_presentation={
            "\u2b50\ufe0f": EmojiMatch(
                theirs=[theirs_snippets[1]], mine=[mine_snippets[1]]
            )
        },
        removed_space={
            "🦄 ": EmojiMatch(
                theirs=[theirs_snippets[2]], mine=[mine_snippets[2]]
            )
        },
        added={"🎉": [mine_snippets[3]]},
        removed={"👴": [theirs_snippets[3]]},
    )
    assert result == expected


def test_normalize_emoji_trailing_space():
    """Normalize emoji removes trailing space, noop when none."""
    assert normalize_emoji("❤️ ") == "❤️"
    assert normalize_emoji("❤️") == "❤️"


def test_normalize_emoji_adds_variation_selector():
    """Normalize emoji adds U+FE0F if not present."""
    assert normalize_emoji("\u2764") == "\u2764\ufe0f"
    assert normalize_emoji("\u2764\ufe0f") == "\u2764\ufe0f"


def test_normalize_emoji_keycap_special_case():
    """Normalize emoji inserts U+FE0F before keycap, not after."""
    assert normalize_emoji("1\u20e3") == "1\ufe0f\u20e3"
    assert normalize_emoji("1\ufe0f\u20e3") == "1\ufe0f\u20e3"


def test_compare_keywords_matching():
    """Keywords with same normalized emoji are classified as matching."""
    theirs_snippets = [
        AlfredSnippet(":heart:", "❤️ Heart", "❤️", "h1"),
        AlfredSnippet(":love:", "❤️ Heart", "❤️", "h2"),
    ]
    mine_snippets = [
        AlfredSnippet("heart", "❤️ Heart", "❤️", "h3"),
        AlfredSnippet("love", "❤️ Heart", "❤️", "h4"),
    ]
    theirs = SnippetPack(snippets=theirs_snippets)
    mine = SnippetPack(prefix=":", suffix=":", snippets=mine_snippets)

    result = compare_keywords(theirs, mine)

    expected = KeywordComparison(
        matching={"heart": mine_snippets[0], "love": mine_snippets[1]},
        removed={},
        added={},
        modified={},
    )
    assert result == expected


def test_compare_keywords_added_and_removed():
    """Keywords only in one pack are classified as added or removed."""
    theirs_snippets = [
        AlfredSnippet(":heart:", "❤️ Heart", "❤️", "h1"),
        AlfredSnippet(":love:", "❤️ Heart", "❤️", "h2"),
    ]
    mine_snippets = [
        AlfredSnippet("heart", "❤️ Heart", "❤️", "h3"),
        AlfredSnippet("red", "❤️ Heart", "❤️", "h4"),
    ]
    theirs = SnippetPack(snippets=theirs_snippets)
    mine = SnippetPack(snippets=mine_snippets)

    result = compare_keywords(theirs, mine)

    expected = KeywordComparison(
        matching={"heart": mine_snippets[0]},
        removed={"love": theirs_snippets[1]},
        added={"red": mine_snippets[1]},
        modified={},
    )
    assert result == expected


def test_compare_keywords_modified():
    """Keywords in both with different normalized emoji are modified."""
    theirs_snippets = [
        AlfredSnippet(":heart:", "❤️ Heart", "❤️", "h1"),
    ]
    mine_snippets = [
        AlfredSnippet("heart", "❤️ Heart", "💙", "h2"),
    ]
    theirs = SnippetPack(snippets=theirs_snippets)
    mine = SnippetPack(snippets=mine_snippets)

    result = compare_keywords(theirs, mine)

    expected = KeywordComparison(
        matching={},
        removed={},
        added={},
        modified={
            "heart": KeywordMatch(
                theirs=theirs_snippets[0], mine=mine_snippets[0]
            )
        },
    )
    assert result == expected


def test_compare_keywords_matching_after_normalization():
    """Keywords match when emoji content is same after normalization."""
    theirs_snippets = [
        AlfredSnippet(":heart:", "❤️ Heart", "\u2764 ", "h1"),
    ]
    mine_snippets = [
        AlfredSnippet("heart", "❤️ Heart", "\u2764\ufe0f", "h2"),
    ]
    theirs = SnippetPack(snippets=theirs_snippets)
    mine = SnippetPack(snippets=mine_snippets)

    result = compare_keywords(theirs, mine)

    expected = KeywordComparison(
        matching={"heart": mine_snippets[0]},
        removed={},
        added={},
        modified={},
    )
    assert result == expected
