"""
Tests for ColesProductExtractor.
"""

import pytest

from src.extractors import ColesProductExtractor
from src.models import Product
from tests.helpers import load_html_content, load_json

TEST_PRODUCT_PAGES = [
    "product-detail-coles-appy-fizz-250ml-8060378",
]


@pytest.mark.parametrize(
    "page_html_path, expected_output_path",
    [
        (
            f"tests/assets/html_content/{page_filename}.html",
            f"tests/assets/labelled_data/{page_filename}.json",
        )
        for page_filename in TEST_PRODUCT_PAGES
    ],
)
def test_get_product(page_html_path, expected_output_path):
    """Test product detail extraction matches expected output."""
    html_content = load_html_content(page_html_path)
    expected_product_data = load_json(expected_output_path)

    extractor = ColesProductExtractor(html_content)
    product = extractor.extract()

    assert isinstance(product, Product)
    assert product == Product(**expected_product_data)
