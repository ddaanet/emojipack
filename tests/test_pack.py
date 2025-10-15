"""Snippet pack tests for emojipack."""

import json
import plistlib
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING

from emojipack.pack import SnippetPack
from emojipack.snippets import AlfredSnippet

from .test_download import EXPECTED_GEMOJI_ENTRIES

if TYPE_CHECKING:
    from emojipack.download import GemojiEntry


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


def test_snippet_pack_write_alfredsnippets(tmp_path: Path):
    """SnippetPack.write writes .alfredsnippets zip with snippets."""
    snippets = [
        AlfredSnippet.from_gemoji(EXPECTED_GEMOJI_ENTRIES[0], "smiley"),
        AlfredSnippet.from_gemoji(EXPECTED_GEMOJI_ENTRIES[1], "thumbsup"),
    ]
    pack = SnippetPack(prefix=":", suffix=":", snippets=snippets)
    output_file = tmp_path / "test.alfredsnippets"
    pack.write(output_file)

    with zipfile.ZipFile(output_file) as zf:
        plist_data = plistlib.loads(zf.read("info.plist"))
        assert plist_data == {
            "snippetkeywordprefix": ":",
            "snippetkeywordsuffix": ":",
        }

        snippet_data = json.loads(zf.read("smiley-1F603.json"))
        assert snippet_data == {
            "alfredsnippet": {
                "keyword": "smiley",
                "name": "😃 Grinning face with big eyes - happy, joy, haha",
                "snippet": "😃",
                "uid": "smiley-1F603",
                "dontautoexpand": False,
            }
        }


def test_snippet_pack_write_macos_plist(tmp_path: Path):
    """SnippetPack.write_macos_plist writes macOS text expansions."""
    snippets = [
        AlfredSnippet.from_gemoji(EXPECTED_GEMOJI_ENTRIES[0], "smiley"),
        AlfredSnippet.from_gemoji(EXPECTED_GEMOJI_ENTRIES[1], "thumbsup"),
    ]
    pack = SnippetPack(prefix=":", suffix=":", snippets=snippets)
    output_file = tmp_path / "expansions.plist"
    pack.write_macos_plist(output_file)
    with output_file.open("rb") as f:
        data = plistlib.load(f)
    assert data == [
        {"phrase": "😃", "shortcut": ":smiley:"},
        {"phrase": "👍", "shortcut": ":thumbsup:"},
    ]


def test_snippet_pack_write_macos_plist_replaces_spaces(tmp_path: Path):
    """SnippetPack.write_macos_plist replaces spaces with dashes."""
    entry: GemojiEntry = {
        "emoji": "🎅",
        "description": "Santa Claus",
        "aliases": ["santa_claus"],
        "tags": [],
    }
    snippet = AlfredSnippet.from_gemoji(entry, "santa_claus")
    pack = SnippetPack(prefix=":", suffix=":", snippets=[snippet])
    output_file = tmp_path / "expansions.plist"
    pack.write_macos_plist(output_file)
    with output_file.open("rb") as f:
        data = plistlib.load(f)
    assert data == [{"phrase": "🎅", "shortcut": ":santa-claus:"}]


def test_snippet_pack_read(tmp_path: Path):
    """SnippetPack.read loads .alfredsnippets zip with snippets."""
    snippets = [
        AlfredSnippet.from_gemoji(EXPECTED_GEMOJI_ENTRIES[0], "smiley"),
        AlfredSnippet.from_gemoji(EXPECTED_GEMOJI_ENTRIES[1], "thumbsup"),
    ]
    pack = SnippetPack(prefix=":", suffix=":", snippets=snippets)
    output_file = tmp_path / "test.alfredsnippets"
    pack.write(output_file)

    loaded_pack = SnippetPack.read(output_file)

    assert loaded_pack.prefix == pack.prefix
    assert loaded_pack.suffix == pack.suffix
    assert loaded_pack.snippets == pack.snippets
