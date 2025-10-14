"""CLI tests for emojipack-generator."""

import json
import os
import plistlib
import subprocess
import zipfile
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from emojipack.cli import app

from .test_download import SAMPLE_GEMOJI_JSON

runner = CliRunner()


def test_help_command_exits_successfully():
    """Running emojipack-generator --help exits successfully."""
    venv = os.environ.get("VIRTUAL_ENV")
    assert venv, "VIRTUAL_ENV not set"
    script_path = Path(venv) / "bin" / "emojipack-generator"
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
        result = runner.invoke(app)
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
    """CLI generates Snippet Pack.plist with --macos flag."""
    with (
        patch("emojipack.download.fetch_with_cache") as mock_fetch,
        runner.isolated_filesystem(temp_dir=tmp_path),
    ):
        mock_fetch.return_value = json.dumps(SAMPLE_GEMOJI_JSON)
        result = runner.invoke(app, ["--macos"])
        assert result.exit_code == 0
        output_file = Path("Snippet Pack.plist")
        assert output_file.exists()
        with output_file.open("rb") as f:
            data = plistlib.load(f)
        assert data == [
            {"phrase": "😃", "shortcut": ":smiley:"},
            {"phrase": "👍", "shortcut": ":+1:"},
            {"phrase": "👍", "shortcut": ":thumbsup:"},
        ]
