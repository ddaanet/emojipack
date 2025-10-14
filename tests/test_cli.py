"""CLI tests for emojipack-generator."""

import os
import subprocess
from pathlib import Path


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
