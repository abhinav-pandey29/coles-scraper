"""
Tests for ColesPageFetcher.
"""

from unittest.mock import MagicMock

import pytest
import requests

from src.core.fetcher import ColesPageFetcher

# --- Helpers for Testing --- #


class FakeResponse:
    """A simple fake requests.Response."""

    def __init__(self, content, status_code=200):
        self.content = content.encode("utf-8")
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError("HTTP Error")


class FakeDriver:
    """
    A fake Selenium driver that simulates cookie interception.
    When get() is called, it immediately calls the assigned request_interceptor.
    """

    def __init__(self):
        self.request_interceptor = None

    def get(self, url):
        if self.request_interceptor:
            # Create a fake request object with a cookie header.
            fake_request = MagicMock()
            fake_request.url = url
            fake_request.headers = {"cookie": "fake_cookie=1"}
            self.request_interceptor(fake_request)

        pass

    def quit(self):
        pass


@pytest.fixture
def fake_driver_factory():
    """Fixture that returns a callable producing FakeDriver instances."""
    return lambda: FakeDriver()


# --- Tests --- #


def test_initialization(fake_driver_factory):
    """
    Test that when no cookie is provided in headers,
    __init__ calls refresh_cookie and sets the cookie.
    """
    # Provide an empty headers dict so that __init__ calls refresh_cookie.
    fetcher = ColesPageFetcher(
        driver_factory=fake_driver_factory,
        headers={},
        sleep_func=lambda x: None,
        refresh_url="http://fake.refresh/",
    )
    # After __init__, the fake driver's intercept_cookie should have set the cookie.
    assert fetcher.session.headers.get("cookie") == "fake_cookie=1"


def test_initialization_with_defaults(fake_driver_factory):
    """
    Test that when headers already include a cookie,
    __init__ does not call refresh_cookie and the cookie remains unchanged.
    """
    headers = {"user-agent": "dummy-agent", "cookie": "provided_cookie=abc"}
    fetcher = ColesPageFetcher(
        driver_factory=fake_driver_factory,
        headers=headers,
        sleep_func=lambda x: None,
        refresh_url="http://fake.refresh/",
    )
    # The cookie should remain as provided.
    assert fetcher.session.headers.get("cookie") == "provided_cookie=abc"


def test_get_without_detection(fake_driver_factory, monkeypatch):
    """
    Test that get() returns a valid response when no bot detection is triggered.
    """
    headers = {"user-agent": "dummy-agent", "cookie": "provided_cookie=abc"}
    fetcher = ColesPageFetcher(
        driver_factory=fake_driver_factory,
        headers=headers,
        sleep_func=lambda x: None,
        refresh_url="http://fake.refresh/",
    )

    def fake_get(url, **kwargs):
        return FakeResponse("Normal content")

    # Patch the session.get method.
    monkeypatch.setattr(fetcher.session, "get", fake_get)
    response = fetcher.get("http://example.com")
    assert "Normal content" in response.content.decode("utf-8")


def test_get_with_detection(fake_driver_factory, monkeypatch):
    """
    Test that get() handles bot detection by refreshing the cookie and retrying.
    """
    headers = {"user-agent": "dummy-agent", "cookie": "provided_cookie=abc"}
    fetcher = ColesPageFetcher(
        driver_factory=fake_driver_factory,
        headers=headers,
        sleep_func=lambda x: None,
        refresh_url="http://fake.refresh/",
    )

    call_count = [0]

    def fake_get(url, **kwargs):
        # First call returns a response with bot-detection text.
        if call_count[0] == 0:
            call_count[0] += 1
            return FakeResponse("Pardon Our Interruption", 200)
        # Second call returns valid content.
        else:
            return FakeResponse("Valid content", 200)

    monkeypatch.setattr(fetcher.session, "get", fake_get)

    # Patch refresh_cookie so that it updates the cookie to a dummy value.
    def fake_refresh_cookie():
        fetcher.session.headers["cookie"] = "dummy_cookie"

    monkeypatch.setattr(fetcher, "refresh_cookie", fake_refresh_cookie)

    response = fetcher.get("http://example.com")
    assert "Valid content" in response.content.decode("utf-8")
    assert fetcher.session.headers["cookie"] == "dummy_cookie"
