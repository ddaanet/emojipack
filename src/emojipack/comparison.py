"""Emoji snippet pack comparison."""

from dataclasses import dataclass

from emojipack.pack import SnippetPack
from emojipack.snippets import AlfredSnippet


@dataclass
class EmojiMatch:
    """Pair of snippet lists from both packs for the same emoji."""

    theirs: list[AlfredSnippet]
    mine: list[AlfredSnippet]


@dataclass
class EmojiComparison:
    """Result of comparing two emoji snippet packs by content."""

    found: dict[str, EmojiMatch]
    added_emoji_presentation: dict[str, EmojiMatch]
    removed_space: dict[str, EmojiMatch]
    added: dict[str, list[AlfredSnippet]]
    removed: dict[str, list[AlfredSnippet]]


def compare_packs(theirs: SnippetPack, mine: SnippetPack) -> EmojiComparison:
    """Compare two snippet packs, grouping snippets by emoji content.

    Snippets with names starting with '#' are ignored (used as comments
    in Joel's pack).

    Args:
        theirs: The reference pack (e.g., Joel's pack)
        mine: The pack to compare against the reference

    Returns:
        EmojiComparison with categorized emoji mappings
    """
    theirs_by_emoji: dict[str, list[AlfredSnippet]] = {}
    for snippet in theirs.snippets:
        if snippet.name.startswith("#"):
            continue
        theirs_by_emoji.setdefault(snippet.snippet, []).append(snippet)
    mine_by_emoji: dict[str, list[AlfredSnippet]] = {}
    for snippet in mine.snippets:
        if snippet.name.startswith("#"):
            continue
        mine_by_emoji.setdefault(snippet.snippet, []).append(snippet)

    found: dict[str, EmojiMatch] = {}
    added_emoji_presentation: dict[str, EmojiMatch] = {}
    removed_space: dict[str, EmojiMatch] = {}
    removed: dict[str, list[AlfredSnippet]] = {}
    mine_categorized: set[str] = set()

    for theirs_emoji, theirs_snippets in theirs_by_emoji.items():
        if theirs_emoji in mine_by_emoji:
            found[theirs_emoji] = EmojiMatch(
                theirs=theirs_snippets, mine=mine_by_emoji[theirs_emoji]
            )
            mine_categorized.add(theirs_emoji)
            continue

        theirs_with_presentation = theirs_emoji + "\ufe0f"
        if theirs_with_presentation in mine_by_emoji:
            added_emoji_presentation[theirs_emoji] = EmojiMatch(
                theirs=theirs_snippets,
                mine=mine_by_emoji[theirs_with_presentation],
            )
            mine_categorized.add(theirs_with_presentation)
            continue

        theirs_no_space = theirs_emoji.replace(" ", "")
        if (
            theirs_no_space != theirs_emoji
            and theirs_no_space in mine_by_emoji
        ):
            removed_space[theirs_emoji] = EmojiMatch(
                theirs=theirs_snippets,
                mine=mine_by_emoji[theirs_no_space],
            )
            mine_categorized.add(theirs_no_space)
            continue

        removed[theirs_emoji] = theirs_snippets

    added = {
        emoji: snippets
        for emoji, snippets in mine_by_emoji.items()
        if emoji not in mine_categorized
    }

    return EmojiComparison(
        found=found,
        added_emoji_presentation=added_emoji_presentation,
        removed_space=removed_space,
        added=added,
        removed=removed,
    )
