"""
Tests for ColesProductTileExtractor.
"""

import bs4
import pytest

from src.models import ProductTile
from src.extractors import ColesProductTileExtractor

TEST_HTML_FILEPATH = "tests/assets/coles-browse-dairy-eggs-fridge-page-4.html"
EXPECTED_PRODUCT_COUNT = 58
EXPECTED_FIRST_PRODUCT_DATA = {
    "name": "Coles Cheese Shredded Tasty Light | 700g",
    "url": "/product/coles-cheese-shredded-tasty-light-700g-8145346",
    "price": "$9.50",
    "price_calc_method": "$13.57 per 1kg",
    "image_url": "/_next/image?url=https%3A%2F%2Fproductimages.coles.com.au%2Fproductimages%2F8%2F8145346.jpg&w=640&q=90",
}
EXPECTED_LAST_PRODUCT_DATA = {
    "name": "Primo Pepperoni Hot Salami | 80g",
    "url": "/product/primo-pepperoni-hot-salami-80g-2808735",
    "price": "$3.95",
    "price_calc_method": "$49.38 per 1kg",
    "image_url": "/_next/image?url=https%3A%2F%2Fproductimages.coles.com.au%2Fproductimages%2F2%2F2808735.jpg&w=640&q=90",
}


@pytest.fixture(scope="module")
def html_content():
    filepath = TEST_HTML_FILEPATH
    with open(filepath, "r", encoding="utf-8") as file:
        return file.read()


def test_get_all_products(html_content):
    extractor = ColesProductTileExtractor(html_content)
    products = extractor.extract()

    assert isinstance(products, list)
    assert len(products) == EXPECTED_PRODUCT_COUNT

    for product in products:
        assert isinstance(product, ProductTile)

    assert products[0] == ProductTile(**EXPECTED_FIRST_PRODUCT_DATA)
    assert products[-1] == ProductTile(**EXPECTED_LAST_PRODUCT_DATA)


def test_find_all_product_tiles(html_content):
    extractor = ColesProductTileExtractor(html_content)
    tiles = extractor.find_all_product_tiles()

    assert isinstance(tiles, list)
    assert len(tiles) == EXPECTED_PRODUCT_COUNT

    for tile in tiles:
        assert isinstance(tile, bs4.element.Tag)
