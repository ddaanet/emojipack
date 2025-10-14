"""Download emoji data from GitHub."""

from typing import TypedDict

import requests

GEMOJI_JSON_URL = (
    "https://raw.githubusercontent.com/github/gemoji/master/db/emoji.json"
)


class GemojiEntry(TypedDict):
    """Gemoji database entry with filtered keys."""

    emoji: str  # The emoji character
    description: str  # Human-readable description, not the unicode name
    aliases: list[str]  # Keywords for the emoji, without colons
    tags: list[str]  # Additional search tags


def fetch_gemoji_data() -> list[GemojiEntry]:
    """Fetch emoji data from github/gemoji repository."""
    response = requests.get(GEMOJI_JSON_URL, timeout=30)
    response.raise_for_status()
    raw_data = response.json()

    return [
        {
            "emoji": entry["emoji"],
            "description": entry["description"],
            "aliases": entry["aliases"],
            "tags": entry["tags"],
        }
        for entry in raw_data
    ]
