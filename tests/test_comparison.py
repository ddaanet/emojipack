"""Tests for emoji pack comparison."""

from emojipack.comparison import compare_packs
from emojipack.pack import SnippetPack
from emojipack.snippets import AlfredSnippet


def test_compare_packs_with_different_emojis():
    """Compare two packs with different emoji content."""
    theirs_snippets = [
        AlfredSnippet(
            keyword="thumbsup",
            name="👍 Thumbs up",
            snippet="👍",
            uid="thumbsup-1F44D",
        ),
        AlfredSnippet(
            keyword="+1",
            name="👍 Thumbs up",
            snippet="👍",
            uid="+1-1F44D",
        ),
        AlfredSnippet(
            keyword="heart",
            name="❤️ Red heart",
            snippet="❤️",
            uid="heart-2764",
        ),
    ]
    mine_snippets = [
        AlfredSnippet(
            keyword="heart",
            name="❤️ Red heart",
            snippet="❤️",
            uid="heart-2764",
        ),
        AlfredSnippet(
            keyword="tada",
            name="🎉 Party popper",
            snippet="🎉",
            uid="tada-1F389",
        ),
    ]
    theirs = SnippetPack(prefix=":", suffix=":", snippets=theirs_snippets)
    mine = SnippetPack(prefix=":", suffix=":", snippets=mine_snippets)
    result = compare_packs(theirs, mine)
    expected_removed = {"👍": [theirs_snippets[0], theirs_snippets[1]]}
    expected_added = {"🎉": [mine_snippets[1]]}
    assert result.removed == expected_removed
    assert result.added == expected_added


def test_compare_packs_ignores_comment_snippets():
    """Compare packs ignores snippets with names starting with #."""
    theirs = SnippetPack(
        prefix=":",
        suffix=":",
        snippets=[
            AlfredSnippet(
                keyword="comment",
                name="# This is a comment",
                snippet="💬",
                uid="comment-1",
            ),
            AlfredSnippet(
                keyword="heart",
                name="❤️ Red heart",
                snippet="❤️",
                uid="heart-2764",
            ),
        ],
    )
    mine = SnippetPack(
        prefix=":",
        suffix=":",
        snippets=[
            AlfredSnippet(
                keyword="heart",
                name="❤️ Red heart",
                snippet="❤️",
                uid="heart-2764",
            ),
            AlfredSnippet(
                keyword="another-comment",
                name="# Another comment",
                snippet="📝",
                uid="comment-2",
            ),
        ],
    )
    result = compare_packs(theirs, mine)
    assert result.removed == {}
    assert result.added == {}
