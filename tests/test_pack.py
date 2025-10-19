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


def test_snippet_pack_set_icon(tmp_path: Path):
    """SnippetPack.set_icon sets the _icon attribute."""
    pack = SnippetPack(prefix=":", suffix=":")
    icon_path = tmp_path / "test_icon.png"
    icon_path.write_bytes(b"fake_png_data")
    pack.set_icon(icon_path)
    assert pack._icon == icon_path


def test_snippet_pack_write_with_icon(tmp_path: Path):
    """SnippetPack.write includes icon.png when icon is set."""
    snippets = [
        AlfredSnippet.from_gemoji(EXPECTED_GEMOJI_ENTRIES[0], "smiley"),
    ]
    pack = SnippetPack(prefix=":", suffix=":", snippets=snippets)
    icon_path = tmp_path / "test_icon.png"
    icon_data = b"fake_png_data"
    icon_path.write_bytes(icon_data)
    pack.set_icon(icon_path)
    output_file = tmp_path / "test.alfredsnippets"
    pack.write(output_file)

    with zipfile.ZipFile(output_file) as zf:
        assert "icon.png" in zf.namelist()
        assert zf.read("icon.png") == icon_data


def test_snippet_pack_write_without_icon(tmp_path: Path):
    """SnippetPack.write works without icon (backward compatibility)."""
    snippets = [
        AlfredSnippet.from_gemoji(EXPECTED_GEMOJI_ENTRIES[0], "smiley"),
    ]
    pack = SnippetPack(prefix=":", suffix=":", snippets=snippets)
    output_file = tmp_path / "test.alfredsnippets"
    pack.write(output_file)

    with zipfile.ZipFile(output_file) as zf:
        assert "icon.png" not in zf.namelist()
        assert "info.plist" in zf.namelist()
        assert "smiley-1F603.json" in zf.namelist()


def test_snippet_pack_read_skips_icon(tmp_path: Path):
    """SnippetPack.read skips icon.png file."""
    snippets = [
        AlfredSnippet.from_gemoji(EXPECTED_GEMOJI_ENTRIES[0], "smiley"),
    ]
    pack = SnippetPack(prefix=":", suffix=":", snippets=snippets)
    icon_path = tmp_path / "test_icon.png"
    icon_path.write_bytes(b"fake_png_data")
    pack.set_icon(icon_path)
    output_file = tmp_path / "test.alfredsnippets"
    pack.write(output_file)

    loaded_pack = SnippetPack.read(output_file)

    assert loaded_pack.prefix == pack.prefix
    assert loaded_pack.suffix == pack.suffix
    assert loaded_pack.snippets == pack.snippets


def test_snippet_pack_read_without_info_plist(tmp_path: Path):
    """SnippetPack.read handles missing info.plist with empty prefix/suffix."""
    snippet = AlfredSnippet("smile", "😀 Grinning", "😀", uid="smile-1F600")
    output_file = tmp_path / "test.alfredsnippets"
    with zipfile.ZipFile(output_file, "w") as zf:
        content = json.dumps(snippet.to_json(), ensure_ascii=False)
        zf.writestr(f"{snippet.uid}.json", content)
    loaded_pack = SnippetPack.read(output_file)
    expected = SnippetPack(prefix="", suffix="", snippets=[snippet])
    assert loaded_pack == expected
