"""Download tests for emojipack."""

from unittest.mock import Mock, patch

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


def test_fetch_gemoji_data():
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
