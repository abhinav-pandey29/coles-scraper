"""
Tests for helper and utility functions.
"""

import pytest

from src.core.utils import validate_url

COLES_URL_PREFIX = r"^https?://(www\.)?coles\.com\.au"
PRODUCT_URL_PATTERN = f"{COLES_URL_PREFIX}/product/.+"  # Product path
BROWSE_URL_PATTERN = f"{COLES_URL_PREFIX}/browse/.+"  # Browse path

TEST_VALID_PRODUCT_URLS = [
    "https://coles.com.au/product/item1",
    "http://www.coles.com.au/product/something-else",
    "https://coles.com.au/product/long-product-name-with-hyphens",
]
TEST_INVALID_PRODUCT_URLS = [
    "https://coles.com.au",
    "http://coles.com.au/browse/category",
    "https://wrong.com/product/item",
    "https://coles.com.au/",
    "https://coles.com.au/product/",
]
TEST_VALID_BROWSE_URLS = [
    "https://coles.com.au/browse/category",
    "http://www.coles.com.au/browse/subcategory",
    "https://coles.com.au/browse/long-category-name",
]
TEST_INVALID_BROWSE_URLS = [
    "https://coles.com.au",
    "http://coles.com.au/product/item",
    "https://wrong.com/browse/category",
    "https://coles.com.au/",
    "https://coles.com.au/browse/",
]


@pytest.mark.parametrize(
    "pattern, valid_urls, invalid_urls",
    [
        (PRODUCT_URL_PATTERN, TEST_VALID_PRODUCT_URLS, TEST_INVALID_PRODUCT_URLS),
        (BROWSE_URL_PATTERN, TEST_VALID_BROWSE_URLS, TEST_INVALID_BROWSE_URLS),
    ],
)
def test_url_validation(pattern, valid_urls, invalid_urls):
    """
    Test URL validation function for different URL patterns.

    Verifies that:
    - Valid URLs pass validation and return the original URL
    - Invalid URLs raise a ValueError with an appropriate error message
    """
    # Test valid URLs
    for url in valid_urls:
        try:
            result = validate_url(url=url, pattern=pattern)
            assert result == url, f"Valid URL {url} should pass validation"
        except ValueError:
            pytest.fail(f"Valid URL {url} should not raise ValueError")

    # Test invalid URLs
    for url in invalid_urls:
        with pytest.raises(ValueError, match="Invalid URL"):
            validate_url(url=url, pattern=pattern)
