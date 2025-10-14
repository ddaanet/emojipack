"""Snippet generation tests for emojipack."""

from emojipack.snippets import AlfredSnippet, generate_uid
from tests.test_download import EXPECTED_GEMOJI_ENTRIES


def test_generate_uid():
    """generate_uid creates stable UID from keyword and emoji hex codes."""
    uid = generate_uid("smiley", "😃")
    assert isinstance(uid, str)
    assert len(uid) > 0
    assert uid == generate_uid("smiley", "😃")
    assert uid != generate_uid("different", "😃")
    assert uid != generate_uid("smiley", "👍")


def test_alfred_snippet_from_gemoji():
    """AlfredSnippet.from_gemoji converts entry with single alias."""
    entry = EXPECTED_GEMOJI_ENTRIES[0]
    snippet = AlfredSnippet.from_gemoji(entry, "smiley")
    assert snippet.keyword == "smiley"
    assert snippet.name == "grinning face with big eyes"
    assert snippet.snippet == "😃"
    assert snippet.uid == "smiley-1F603"


def test_alfred_snippet_from_gemoji_multiple_aliases():
    """AlfredSnippet.from_gemoji handles entry with multiple aliases."""
    entry = EXPECTED_GEMOJI_ENTRIES[1]
    snippet = AlfredSnippet.from_gemoji(entry, "thumbsup")
    assert snippet.keyword == "thumbsup"
    assert snippet.uid == "thumbsup-1F44D"


def test_alfred_snippet_to_json():
    """AlfredSnippet.to_json generates JSON dict for Alfred."""
    entry = EXPECTED_GEMOJI_ENTRIES[0]
    snippet = AlfredSnippet.from_gemoji(entry, "smiley")
    json_data = snippet.to_json()
    assert json_data["alfredsnippet"]["keyword"] == "smiley"
    assert json_data["alfredsnippet"]["name"] == "grinning face with big eyes"
    assert json_data["alfredsnippet"]["snippet"] == "😃"
    assert json_data["alfredsnippet"]["uid"] == "smiley-1F603"
    assert json_data["alfredsnippet"]["dontautoexpand"] is False
