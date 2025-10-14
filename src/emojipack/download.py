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


def fetch_with_cache(name: str, url: str) -> str:
    """Fetch URL with HTTP caching using ETag and Last-Modified headers."""
    cache_file = CACHE_DIR / f"{name}.cache"
    meta_file = CACHE_DIR / f"{name}.meta.json"

    headers = {}
    if cache_file.exists() and meta_file.exists():
        metadata = json.loads(meta_file.read_text())
        if metadata.get("url") == url:
            if "etag" in metadata:
                headers["If-None-Match"] = metadata["etag"]
            if "last_modified" in metadata:
                headers["If-Modified-Since"] = metadata["last_modified"]

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    if response.status_code == 304:
        return cache_file.read_text()

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(response.text)

    metadata = {"url": url}
    if "ETag" in response.headers:
        metadata["etag"] = response.headers["ETag"]
    if "Last-Modified" in response.headers:
        metadata["last_modified"] = response.headers["Last-Modified"]
    meta_file.write_text(json.dumps(metadata))

    return response.text


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
