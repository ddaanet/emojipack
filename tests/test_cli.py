"""CLI tests for emojipack-generator."""

import json
import os
import plistlib
import subprocess
import zipfile
from pathlib import Path
from unittest.mock import patch

import yaml
from typer.testing import CliRunner

from emojipack.cli import app
from emojipack.pack import SnippetPack
from emojipack.snippets import AlfredSnippet

from .test_download import SAMPLE_GEMOJI_JSON

runner = CliRunner()


def test_help_command_exits_successfully():
    """Running emojipack --help exits successfully."""
    venv = os.environ.get("VIRTUAL_ENV")
    assert venv, "VIRTUAL_ENV not set"
    script_path = Path(venv) / "bin" / "emojipack"
    result = subprocess.run(
        [str(script_path), "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "usage:" in result.stdout.lower() or "help" in result.stdout.lower()


def test_generates_emoji_pack_alfredsnippets(tmp_path: Path):
    """CLI generates Emoji Pack.alfredsnippets with emoji snippets."""
    with (
        patch("emojipack.download.fetch_with_cache") as mock_fetch,
        runner.isolated_filesystem(temp_dir=tmp_path),
    ):
        mock_fetch.return_value = json.dumps(SAMPLE_GEMOJI_JSON)
        result = runner.invoke(app, ["generate"])
        assert result.exit_code == 0

        output_file = Path("Emoji Pack.alfredsnippets")
        assert output_file.exists()

        with zipfile.ZipFile(output_file) as zf:
            assert "info.plist" in zf.namelist()
            snippet_files = [n for n in zf.namelist() if n.endswith(".json")]
            assert len(snippet_files) == 3
            assert "smiley-1F603.json" in snippet_files
            assert "+1-1F44D.json" in snippet_files
            assert "thumbsup-1F44D.json" in snippet_files


def test_generates_macos_plist_with_flag(tmp_path: Path):
    """CLI generates Emoji Pack.plist with --macos flag."""
    with (
        patch("emojipack.download.fetch_with_cache") as mock_fetch,
        runner.isolated_filesystem(temp_dir=tmp_path),
    ):
        mock_fetch.return_value = json.dumps(SAMPLE_GEMOJI_JSON)
        result = runner.invoke(app, ["generate", "--macos"])
        assert result.exit_code == 0
        output_file = Path("Emoji Pack.plist")
        assert output_file.exists()
        with output_file.open("rb") as f:
            data = plistlib.load(f)
        assert data == [
            {"phrase": "😃", "shortcut": ":smiley:"},
            {"phrase": "👍", "shortcut": ":+1:"},
            {"phrase": "👍", "shortcut": ":thumbsup:"},
        ]


def test_compare_subcommand_outputs_yaml(tmp_path: Path):
    """CLI compare shows counts by default, lists only removed."""
    theirs_pack = SnippetPack(
        prefix=":",
        suffix=":",
        snippets=[
            AlfredSnippet(
                "thumbsup", "👍 Thumbs up", "👍", uid="thumbsup-1F44D"
            ),
            AlfredSnippet("+1", "👍 Thumbs up", "👍", uid="+1-1F44D"),
        ],
    )
    mine_pack = SnippetPack(
        prefix=":",
        suffix=":",
        snippets=[
            AlfredSnippet("tada", "🎉 Party popper", "🎉", uid="tada-1F389")
        ],
    )
    theirs_path = tmp_path / "theirs.alfredsnippets"
    mine_path = tmp_path / "mine.alfredsnippets"
    theirs_pack.write(theirs_path)
    mine_pack.write(mine_path)
    result = runner.invoke(app, ["compare", str(theirs_path), str(mine_path)])
    assert result.exit_code == 0
    output = yaml.safe_load(result.stdout)
    expected = {
        "emojis": {
            "removed": ["👍 Thumbs up"],
            "found": 0,
            "added_emoji_presentation": 0,
            "removed_space": 0,
            "added": 1,
        },
        "keywords": {
            "removed": {"thumbsup": "👍 Thumbs up", "+1": "👍 Thumbs up"},
            "modified": {},
            "matching": 0,
            "added": 1,
        },
    }
    assert output == expected


def test_compare_verbose_shows_keywords(tmp_path: Path):
    """CLI compare --verbose shows keywords for all categories."""
    theirs_pack = SnippetPack(
        prefix=":",
        suffix=":",
        snippets=[
            AlfredSnippet("thumbsup", "👍 Thumbs up", "👍", uid="t1"),
            AlfredSnippet("+1", "👍 Thumbs up", "👍", uid="t2"),
        ],
    )
    mine_pack = SnippetPack(
        prefix=":",
        suffix=":",
        snippets=[
            AlfredSnippet("tada", "🎉 Party popper", "🎉", uid="m1"),
        ],
    )
    theirs_path = tmp_path / "theirs.alfredsnippets"
    mine_path = tmp_path / "mine.alfredsnippets"
    theirs_pack.write(theirs_path)
    mine_pack.write(mine_path)
    result = runner.invoke(
        app, ["compare", "--verbose", str(theirs_path), str(mine_path)]
    )
    assert result.exit_code == 0
    output = yaml.safe_load(result.stdout)
    expected = {
        "emojis": {
            "removed": {"👍 Thumbs up": ["thumbsup", "+1"]},
            "found": {},
            "added_emoji_presentation": {},
            "removed_space": {},
            "added": {"🎉 Party popper": ["tada"]},
        },
        "keywords": {
            "removed": {"thumbsup": "👍 Thumbs up", "+1": "👍 Thumbs up"},
            "added": {"tada": "🎉 Party popper"},
            "matching": {},
            "modified": {},
        },
    }
    assert output == expected


def test_generates_macos_plist_with_prefix_dot_suffix_dot(tmp_path: Path):
    """CLI generates plist with prefix '.' suffix '.' shortcuts."""
    with (
        patch("emojipack.download.fetch_with_cache") as mock_fetch,
        runner.isolated_filesystem(temp_dir=tmp_path),
    ):
        mock_fetch.return_value = json.dumps(SAMPLE_GEMOJI_JSON)
        result = runner.invoke(
            app, ["generate", "--macos", "--prefix", ".", "--suffix", "."]
        )
        assert result.exit_code == 0
        output_file = Path("Emoji Pack.plist")
        assert output_file.exists()
        with output_file.open("rb") as f:
            data = plistlib.load(f)
        assert data == [
            {"phrase": "😃", "shortcut": ".smiley."},
            {"phrase": "👍", "shortcut": ".+1."},
            {"phrase": "👍", "shortcut": ".thumbsup."},
        ]


def test_generates_macos_plist_with_prefix_dot_empty_suffix(tmp_path: Path):
    """CLI generates plist with prefix '.' and empty suffix shortcuts."""
    with (
        patch("emojipack.download.fetch_with_cache") as mock_fetch,
        runner.isolated_filesystem(temp_dir=tmp_path),
    ):
        mock_fetch.return_value = json.dumps(SAMPLE_GEMOJI_JSON)
        result = runner.invoke(
            app, ["generate", "--macos", "--prefix", ".", "--suffix="]
        )
        assert result.exit_code == 0
        output_file = Path("Emoji Pack.plist")
        assert output_file.exists()
        with output_file.open("rb") as f:
            data = plistlib.load(f)
        assert data == [
            {"phrase": "😃", "shortcut": ".smiley"},
            {"phrase": "👍", "shortcut": ".+1"},
            {"phrase": "👍", "shortcut": ".thumbsup"},
        ]
