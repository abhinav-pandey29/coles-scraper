"""
Tests for ColesScraper.
"""

from unittest.mock import Mock, patch

import pytest
import requests

from src.coles_scraper import ColesScraper
from src.scrapers import ColesProductScraper, ColesProductTileScraper

TEST_VALID_PRODUCT_URL = (
    "https://www.coles.com.au/product/smiths-original-chips-175g-24792"
)
TEST_VALID_BROWSE_URL = "https://www.coles.com.au/browse/snacks-and-confectionery"
TEST_INVALID_PRODUCT_URLS = [
    "https://www.coles.com.au/browse/chips",  # Not a product URL
    "https://www.woolworths.com.au/product/something",  # Wrong domain
    "http://coles.com.au/not-product/item",  # Wrong path
]
TEST_INVALID_BROWSE_URLS = [
    "https://www.coles.com.au/product/chips",  # Not a browse URL
    "https://www.woolworths.com.au/browse/something",  # Wrong domain
    "http://coles.com.au/search/item",  # Wrong path
]


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

    def test_url_validation_product(self, scraper):
        """Test that product URL validation works correctly."""
        try:
            with patch.object(scraper, "fetch"), patch.object(
                scraper, "product_extractor"
            ):
                scraper.scrape_product_url(TEST_VALID_PRODUCT_URL)
        except ValueError:
            pytest.fail("Valid product URL raised validation exception")

        for url in TEST_INVALID_PRODUCT_URLS:
            with pytest.raises(ValueError, match=r"Invalid URL:.*"):
                scraper.scrape_product_url(url)

    def test_url_validation_browse(self, scraper):
        """Test that browse URL validation works correctly."""
        try:
            with patch.object(scraper, "fetch"), patch.object(
                scraper, "product_tile_extractor"
            ):
                scraper.scrape_browse_category_url(TEST_VALID_BROWSE_URL)
        except ValueError:
            pytest.fail("Valid browse URL raised validation exception")

        for url in TEST_INVALID_BROWSE_URLS:
            with pytest.raises(ValueError, match=r"Invalid URL:.*"):
                scraper.scrape_browse_category_url(url)
