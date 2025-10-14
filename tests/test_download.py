"""Download tests for emojipack."""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from emojipack.download import (
    GEMOJI_JSON_URL,
    fetch_gemoji_data,
    fetch_with_cache,
)

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


def write_cache_metadata(
    cache_dir: Path,
    name: str,
    url: str,
    etag: str | None = None,
    last_modified: str | None = None,
) -> None:
    """Write cache metadata file for testing."""
    cache_dir.mkdir(exist_ok=True)
    metadata = {"url": url, "etag": etag, "last_modified": last_modified}
    (cache_dir / f"{name}.meta.json").write_text(json.dumps(metadata))


def test_fetch_gemoji_data(cache_dir: Path):
    """fetch_gemoji_data requests URL and returns list[GemojiEntry]."""
    with patch("emojipack.download.fetch_with_cache") as mock_fetch:
        mock_fetch.return_value = json.dumps(SAMPLE_GEMOJI_JSON)

        result = fetch_gemoji_data()

        mock_fetch.assert_called_once_with("gemoji", GEMOJI_JSON_URL)
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


def test_fetch_with_cache_downloads_on_cache_miss(cache_dir: Path):
    """fetch_with_cache downloads and saves text + metadata on cache miss."""
    with patch("emojipack.download.requests.get") as mock_get:
        mock_response = Mock()
        mock_response.text = '{"test": "data"}'
        mock_response.headers = {
            "ETag": '"abc123"',
            "Last-Modified": "Wed, 21 Oct 2015 07:28:00 GMT",
        }
        mock_get.return_value = mock_response

        result = fetch_with_cache("test", "http://example.com")

        assert result == '{"test": "data"}'
        cache_file = cache_dir / "test.cache"
        assert cache_file.read_text() == '{"test": "data"}'
        meta_file = cache_dir / "test.meta.json"
        metadata = json.loads(meta_file.read_text())
        assert metadata == {
            "url": "http://example.com",
            "etag": '"abc123"',
            "last_modified": "Wed, 21 Oct 2015 07:28:00 GMT",
        }


def test_fetch_with_cache_sends_conditional_headers(cache_dir: Path):
    """fetch_with_cache sends If-None-Match and If-Modified-Since headers."""
    cache_dir.mkdir()
    (cache_dir / "test.cache").write_text("cached content")
    (cache_dir / "test.meta.json").write_text(
        json.dumps(
            {
                "url": "http://example.com",
                "etag": '"old-etag"',
                "last_modified": "Mon, 01 Jan 2020 00:00:00 GMT",
            }
        )
    )

    with patch("emojipack.download.requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 304
        mock_get.return_value = mock_response

        fetch_with_cache("test", "http://example.com")

        call_kwargs = mock_get.call_args[1]
        assert call_kwargs["headers"]["If-None-Match"] == '"old-etag"'
        assert (
            call_kwargs["headers"]["If-Modified-Since"]
            == "Mon, 01 Jan 2020 00:00:00 GMT"
        )


def test_fetch_with_cache_uses_cache_on_304(cache_dir: Path):
    """fetch_with_cache returns cached content on 304 response."""
    cache_dir.mkdir()
    (cache_dir / "test.cache").write_text("cached content")
    (cache_dir / "test.meta.json").write_text(
        json.dumps(
            {
                "url": "http://example.com",
                "etag": '"etag"',
                "last_modified": "Mon, 01 Jan 2020 00:00:00 GMT",
            }
        )
    )

    with patch("emojipack.download.requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 304
        mock_get.return_value = mock_response

        result = fetch_with_cache("test", "http://example.com")

        assert result == "cached content"


def test_fetch_with_cache_updates_cache_on_200(cache_dir: Path):
    """fetch_with_cache updates cache with new content on 200 response."""
    cache_dir.mkdir()
    (cache_dir / "test.cache").write_text("old content")
    (cache_dir / "test.meta.json").write_text(
        json.dumps(
            {
                "url": "http://example.com",
                "etag": '"old-etag"',
                "last_modified": "Mon, 01 Jan 2020 00:00:00 GMT",
            }
        )
    )

    with patch("emojipack.download.requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "new content"
        mock_response.headers = {
            "ETag": '"new-etag"',
            "Last-Modified": "Tue, 01 Jan 2021 00:00:00 GMT",
        }
        mock_get.return_value = mock_response

        result = fetch_with_cache("test", "http://example.com")

        assert result == "new content"
        assert (cache_dir / "test.cache").read_text() == "new content"
        metadata = json.loads((cache_dir / "test.meta.json").read_text())
        assert metadata == {
            "url": "http://example.com",
            "etag": '"new-etag"',
            "last_modified": "Tue, 01 Jan 2021 00:00:00 GMT",
        }


def test_fetch_with_cache_ignores_cache_on_url_mismatch(cache_dir: Path):
    """fetch_with_cache ignores cache if URL doesn't match metadata."""
    cache_dir.mkdir()
    (cache_dir / "test.cache").write_text("cached content")
    write_cache_metadata(
        cache_dir,
        "test",
        "http://old-url.com",
        '"old-etag"',
        "Mon, 01 Jan 2020 00:00:00 GMT",
    )

    with patch("emojipack.download.requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "new content"
        mock_response.headers = {
            "ETag": '"new-etag"',
            "Last-Modified": "Tue, 01 Jan 2021 00:00:00 GMT",
        }
        mock_get.return_value = mock_response

        result = fetch_with_cache("test", "http://new-url.com")

        call_kwargs = mock_get.call_args[1]
        assert "If-None-Match" not in call_kwargs.get("headers", {})
        assert result == "new content"
