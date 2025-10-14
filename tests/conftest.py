"""Global test fixtures for emojipack tests."""

import pytest


@pytest.fixture(autouse=True)
def no_requests(monkeypatch: pytest.MonkeyPatch):
    """Remove requests.sessions.Session.request for all tests.

    This prevents any real HTTP requests during tests.
    """
    monkeypatch.delattr("requests.sessions.Session.request")
