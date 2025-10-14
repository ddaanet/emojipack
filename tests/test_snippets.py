"""Snippet generation tests for emojipack."""

from emojipack.snippets import generate_uid


def test_generate_uid():
    """generate_uid creates stable UID from keyword and emoji hex codes."""
    uid = generate_uid("smiley", "😃")
    assert isinstance(uid, str)
    assert len(uid) > 0
    assert uid == generate_uid("smiley", "😃")
    assert uid != generate_uid("different", "😃")
    assert uid != generate_uid("smiley", "👍")
