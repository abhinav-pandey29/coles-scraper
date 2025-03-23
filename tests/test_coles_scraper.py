"""
Tests for ColesScraper.
"""

from unittest.mock import Mock, patch

import pytest
import requests

from src.scrapers import ColesProductScraper, ColesProductTileScraper
from src.coles_scraper import ColesScraper


class TestColesScraper:

    @pytest.fixture
    def mock_fetcher(self):
        """Create a mock ColesPageFetcher with refresh_cookie mocked."""
        with patch("src.fetcher.ColesPageFetcher") as MockFetcher:
            mock_fetcher = MockFetcher.return_value
            mock_fetcher.refresh_cookie = Mock()
            mock_fetcher.get = Mock()
            yield mock_fetcher

    @pytest.fixture
    def scraper(self, mock_fetcher):
        """Create a ColesScraper instance with mocked fetcher."""
        return ColesScraper(fetcher=mock_fetcher)

    @pytest.fixture
    def mock_response(self):
        """Create a mock response object."""
        mock_resp = Mock(spec=requests.Response)
        mock_resp.raise_for_status = Mock()
        mock_resp.text = ""
        return mock_resp

    def test_initialization(self, mock_fetcher):
        """Test that ColesScraper initializes with a fetcher."""
        # Test with user-provided fetcher
        scraper = ColesScraper(fetcher=mock_fetcher)
        assert scraper.fetcher == mock_fetcher
        assert scraper.product_extractor == ColesProductScraper
        assert scraper.product_tile_extractor == ColesProductTileScraper

        # Test with default fetcher
        with patch("src.coles_scraper.ColesPageFetcher") as MockFetcher:
            default_scraper = ColesScraper()
            MockFetcher.assert_called_once()
            assert default_scraper.fetcher == MockFetcher.return_value
            assert scraper.product_extractor == ColesProductScraper
            assert scraper.product_tile_extractor == ColesProductTileScraper
