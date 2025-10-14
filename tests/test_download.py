"""Download tests for emojipack."""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from emojipack.download import GEMOJI_JSON_URL, fetch_gemoji_data

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


@pytest.fixture
def cache_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Provide isolated cache directory for tests."""
    test_cache = tmp_path / "cache"
    monkeypatch.setattr("emojipack.download.CACHE_DIR", test_cache)
    return test_cache


def test_fetch_gemoji_data(cache_dir: Path):
    """fetch_gemoji_data requests URL and returns list[GemojiEntry]."""
    with patch("emojipack.download.requests.get") as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_GEMOJI_JSON
        mock_get.return_value = mock_response

        result = fetch_gemoji_data()

        mock_get.assert_called_once_with(GEMOJI_JSON_URL, timeout=30)
        mock_response.raise_for_status.assert_called_once()

        assert result == [
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


def test_cache_file_created_after_first_download(cache_dir: Path):
    """Cache file is created with raw JSON after download."""
    with patch("emojipack.download.requests.get") as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_GEMOJI_JSON
        mock_get.return_value = mock_response

        fetch_gemoji_data()

        cache_file = cache_dir / "gemoji.json"
        assert cache_file.exists()
        cached_data = json.loads(cache_file.read_text())
        assert cached_data == SAMPLE_GEMOJI_JSON


def test_cached_data_returned_without_new_request(cache_dir: Path):
    """Cached data is used without making HTTP request."""
    cache_dir.mkdir()
    cache_file = cache_dir / "gemoji.json"
    cache_file.write_text(json.dumps(SAMPLE_GEMOJI_JSON))

    with patch("emojipack.download.requests.get") as mock_get:
        result = fetch_gemoji_data()

        mock_get.assert_not_called()
        assert [r["emoji"] for r in result] == ["😃", "👍"]
