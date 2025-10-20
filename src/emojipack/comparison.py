"""Emoji snippet pack comparison."""

from dataclasses import dataclass

from emojipack.pack import SnippetPack
from emojipack.snippets import AlfredSnippet

EMOJI_VS = "\ufe0f"  # Emoji variation selector
KEYCAP = "\u20e3"  # Combining enclosing keycap


class DuplicateKeywordError(ValueError):
    """Raised when a keyword appears multiple times in a snippet pack."""

    def __init__(self, keyword: str, pack: SnippetPack) -> None:
        """Initialize with keyword and pack."""
        super().__init__(f"Duplicate keyword: {keyword}")
        self.keyword = keyword
        self.pack = pack


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


@dataclass
class KeywordMatch:
    """Pair of snippets from both packs for the same keyword."""

    theirs: AlfredSnippet
    mine: AlfredSnippet


@dataclass
class KeywordComparison:
    """Result of comparing keywords across snippet packs."""

    removed: dict[str, AlfredSnippet]
    added: dict[str, AlfredSnippet]
    matching: dict[str, AlfredSnippet]
    modified: dict[str, KeywordMatch]


@dataclass
class SnippetPackComparison:
    """Result of comparing two snippet packs."""

    emojis: EmojiComparison
    keywords: KeywordComparison


def _non_comment_snippets(pack: SnippetPack) -> list[AlfredSnippet]:
    """Filter out snippets with names starting with '#'."""
    return [s for s in pack.snippets if not s.name.startswith("#")]


def normalize_emoji(emoji: str) -> str:
    """Normalize emoji by removing spaces and adding variation selector."""
    emoji = emoji.replace(" ", "")
    if emoji.endswith(KEYCAP) and not emoji.endswith(EMOJI_VS + KEYCAP):
        emoji = emoji[: -len(KEYCAP)] + EMOJI_VS + KEYCAP
    if not emoji.endswith(KEYCAP) and not emoji.endswith(EMOJI_VS):
        emoji = emoji + EMOJI_VS
    return emoji


def compare_emojis(theirs: SnippetPack, mine: SnippetPack) -> EmojiComparison:
    """Compare two snippet packs, grouping snippets by emoji content."""
    theirs_by_emoji: dict[str, list[AlfredSnippet]] = {}
    for snippet in _non_comment_snippets(theirs):
        theirs_by_emoji.setdefault(snippet.snippet, []).append(snippet)
    mine_by_emoji: dict[str, list[AlfredSnippet]] = {}
    for snippet in _non_comment_snippets(mine):
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

        if theirs_emoji.endswith(KEYCAP):
            base = theirs_emoji[: -len(KEYCAP)]
            theirs_with_presentation = base + EMOJI_VS + KEYCAP
        else:
            theirs_with_presentation = theirs_emoji + EMOJI_VS

        if theirs_with_presentation in mine_by_emoji:
            added_emoji_presentation[theirs_with_presentation] = EmojiMatch(
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


def compare_keywords(
    theirs: SnippetPack, mine: SnippetPack
) -> KeywordComparison:
    """Compare keywords between two snippet packs."""
    theirs_by_keyword: dict[str, AlfredSnippet] = {}
    for snippet in _non_comment_snippets(theirs):
        keyword = snippet.keyword.strip(":")
        if keyword in theirs_by_keyword:
            raise DuplicateKeywordError(keyword, theirs)
        theirs_by_keyword[keyword] = snippet

    mine_by_keyword: dict[str, AlfredSnippet] = {}
    for snippet in _non_comment_snippets(mine):
        keyword = snippet.keyword
        if keyword in mine_by_keyword:
            raise DuplicateKeywordError(keyword, mine)
        mine_by_keyword[keyword] = snippet

    matching: dict[str, AlfredSnippet] = {}
    removed: dict[str, AlfredSnippet] = {}
    modified: dict[str, KeywordMatch] = {}

    for keyword, theirs_snippet in theirs_by_keyword.items():
        if keyword not in mine_by_keyword:
            removed[keyword] = theirs_snippet
            continue
        mine_snippet = mine_by_keyword[keyword]
        theirs_normalized = normalize_emoji(theirs_snippet.snippet)
        mine_normalized = normalize_emoji(mine_snippet.snippet)
        if theirs_normalized == mine_normalized:
            matching[keyword] = mine_snippet
        else:
            modified[keyword] = KeywordMatch(theirs_snippet, mine_snippet)

    added = {
        keyword: snippet
        for keyword, snippet in mine_by_keyword.items()
        if keyword not in theirs_by_keyword
    }

    return KeywordComparison(
        matching=matching,
        removed=removed,
        added=added,
        modified=modified,
    )


def compare_packs(
    theirs: SnippetPack, mine: SnippetPack
) -> SnippetPackComparison:
    """Compare two snippet packs by emojis and keywords."""
    emojis = compare_emojis(theirs, mine)
    keywords = compare_keywords(theirs, mine)
    return SnippetPackComparison(emojis, keywords)
