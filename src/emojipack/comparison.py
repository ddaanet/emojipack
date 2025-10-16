"""Emoji snippet pack comparison."""

from dataclasses import dataclass

from emojipack.pack import SnippetPack
from emojipack.snippets import AlfredSnippet


@dataclass
class EmojiComparison:
    """Result of comparing two emoji snippet packs by content."""

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
        EmojiComparison with added and removed emoji mappings
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
    removed = {
        emoji: snippets
        for emoji, snippets in theirs_by_emoji.items()
        if emoji not in mine_by_emoji
    }
    added = {
        emoji: snippets
        for emoji, snippets in mine_by_emoji.items()
        if emoji not in theirs_by_emoji
    }
    return EmojiComparison(added=added, removed=removed)
