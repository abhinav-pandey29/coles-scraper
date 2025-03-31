"""
Tests for ColesProductTileExtractor.
"""

import bs4
import pytest

from src.extractors import ColesProductTileExtractor
from src.models import ProductTile
from tests.helpers import load_html_content, load_json

TEST_BROWSE_CATEGORY_PAGES = [
    "browse-category-dairy-eggs-fridge-page-4",
]


@pytest.mark.parametrize(
    "page_html_path, expected_output_path",
    [
        (
            f"tests/assets/html_content/{page_filename}.html",
            f"tests/assets/labelled_data/{page_filename}.json",
        )
        for page_filename in TEST_BROWSE_CATEGORY_PAGES
    ],
)
def test_get_all_products(page_html_path, expected_output_path):
    html_content = load_html_content(page_html_path)
    labels = load_json(expected_output_path)

    extractor = ColesProductTileExtractor(html_content)
    products = extractor.extract()

    assert isinstance(products, list)
    assert len(products) == labels["EXPECTED_PRODUCT_COUNT"]

    for product in products:
        assert isinstance(product, ProductTile)

    assert products[0] == ProductTile(**labels["EXPECTED_FIRST_PRODUCT_DATA"])
    assert products[-1] == ProductTile(**labels["EXPECTED_LAST_PRODUCT_DATA"])


@pytest.mark.parametrize(
    "page_html_path, expected_output_path",
    [
        (
            f"tests/assets/html_content/{page_filename}.html",
            f"tests/assets/labelled_data/{page_filename}.json",
        )
        for page_filename in TEST_BROWSE_CATEGORY_PAGES
    ],
)
def test_find_all_product_tiles(page_html_path, expected_output_path):
    html_content = load_html_content(page_html_path)
    labels = load_json(expected_output_path)

    extractor = ColesProductTileExtractor(html_content)
    tiles = extractor.find_all_product_tiles()

    assert isinstance(tiles, list)
    assert len(tiles) == labels["EXPECTED_PRODUCT_COUNT"]

    for tile in tiles:
        assert isinstance(tile, bs4.element.Tag)
