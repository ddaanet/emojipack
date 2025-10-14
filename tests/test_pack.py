"""Snippet pack tests for emojipack."""

import plistlib

from emojipack.pack import SnippetPack


def test_snippet_pack_info_plist():
    """SnippetPack.create_info_plist generates valid plist with settings."""
    pack = SnippetPack(prefix=":", suffix=":")
    plist = pack.create_info_plist()
    data = plistlib.loads(plist.encode())
    assert data["snippetkeywordprefix"] == ":"
    assert data["snippetkeywordsuffix"] == ":"


def test_snippet_pack_info_plist_escapes_xml():
    """SnippetPack.create_info_plist escapes XML special characters."""
    pack = SnippetPack(prefix="<&>", suffix='"test"')
    plist = pack.create_info_plist()
    data = plistlib.loads(plist.encode())
    assert data["snippetkeywordprefix"] == "<&>"
    assert data["snippetkeywordsuffix"] == '"test"'
