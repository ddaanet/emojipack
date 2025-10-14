"""Download emoji data from GitHub."""

import json
from pathlib import Path
from typing import TypedDict

import platformdirs
import requests_cache

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


def fetch_with_cache(url: str) -> str:
    """Fetch URL with HTTP caching."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    session = requests_cache.CachedSession(str(CACHE_DIR / "http_cache"))
    response = session.get(url, timeout=30)
    response.raise_for_status()
    return response.text


def fetch_gemoji_data() -> list[GemojiEntry]:
    """Fetch emoji data from github/gemoji repository."""
    text = fetch_with_cache(GEMOJI_JSON_URL)
    raw_data = json.loads(text)

    return [
        {
            "emoji": entry["emoji"],
            "description": entry["description"],
            "aliases": entry["aliases"],
            "tags": entry["tags"],
        }
        for entry in raw_data
    ]
