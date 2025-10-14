"""Download emoji data from GitHub."""

import json
from pathlib import Path
from typing import TypedDict

import platformdirs
import requests

GEMOJI_JSON_URL = (
    "https://raw.githubusercontent.com/github/gemoji/master/db/emoji.json"
)
CACHE_DIR = Path(platformdirs.user_cache_dir("emojipack", "ddaanet"))


class GemojiEntry(TypedDict):
    """Gemoji database entry with filtered keys."""

    emoji: str  # The emoji character
    description: str  # Human-readable description, not the unicode name
    aliases: list[str]  # Keywords for the emoji, without colons
    tags: list[str]  # Additional search tags


def fetch_gemoji_data() -> list[GemojiEntry]:
    """Fetch emoji data from github/gemoji repository."""
    cache_file = CACHE_DIR / "gemoji.json"

    if cache_file.exists():
        raw_data = json.loads(cache_file.read_text())
    else:
        response = requests.get(GEMOJI_JSON_URL, timeout=30)
        response.raise_for_status()
        raw_data = response.json()

        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(json.dumps(raw_data))

    return [
        {
            "emoji": entry["emoji"],
            "description": entry["description"],
            "aliases": entry["aliases"],
            "tags": entry["tags"],
        }
        for entry in raw_data
    ]
