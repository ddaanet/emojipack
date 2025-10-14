"""Download tests for emojipack."""

import json
from unittest.mock import patch

from emojipack.download import GEMOJI_JSON_URL, GemojiEntry, fetch_gemoji_data

SAMPLE_GEMOJI_JSON = [
    {
        "emoji": "😃",
        "description": "grinning face with big eyes",
        "category": "Smileys & Emotion",
        "aliases": ["smiley"],
        "tags": ["happy", "joy", "haha"],
        "unicode_version": "6.0",
        "ios_version": "6.0",
    },
    {
        "emoji": "👍",
        "description": "thumbs up",
        "category": "People & Body",
        "aliases": ["+1", "thumbsup"],
        "tags": ["approve", "ok"],
        "unicode_version": "6.0",
        "ios_version": "6.0",
        "skin_tones": True,
    },
]

EXPECTED_GEMOJI_ENTRIES: list[GemojiEntry] = [
    {
        "emoji": "😃",
        "description": "grinning face with big eyes",
        "aliases": ["smiley"],
        "tags": ["happy", "joy", "haha"],
    },
    {
        "emoji": "👍",
        "description": "thumbs up",
        "aliases": ["+1", "thumbsup"],
        "tags": ["approve", "ok"],
    },
]


def test_fetch_gemoji_data():
    """fetch_gemoji_data requests URL and returns list[GemojiEntry]."""
    with patch("emojipack.download.fetch_with_cache") as mock_fetch:
        mock_fetch.return_value = json.dumps(SAMPLE_GEMOJI_JSON)
        result = fetch_gemoji_data()
        mock_fetch.assert_called_once_with(GEMOJI_JSON_URL)
        assert result == EXPECTED_GEMOJI_ENTRIES
