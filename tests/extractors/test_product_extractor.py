"""
Tests for ColesProductExtractor.
"""

import pytest

from src.extractors import ColesProductExtractor
from src.models import Product

TEST_HTML_FILEPATH = "tests/assets/coles-appy-fizz-250ml-8060378.html"
EXPECTED_PRODUCT_DATA = {
    "name": "Appy Fizz | 250mL",
    "brand_name": "Appy",
    "brand_url": "/brands/appy-4039743300",
    "categories": ["Home", "All categories", "Pantry", "International foods", "Indian"],
    "retail_limit": "Retail limit: 20",
    "promotional_limit": "Promotional limit: 12",
    "product_code": "Code: 8060378",
}


@pytest.fixture(scope="module")
def html_content():
    filepath = TEST_HTML_FILEPATH
    with open(filepath, "r", encoding="utf-8") as file:
        return file.read()


def test_get_product(html_content):
    extractor = ColesProductExtractor(html_content)
    product = extractor.extract()

    assert isinstance(product, Product)
    assert product == Product(**EXPECTED_PRODUCT_DATA)
