"""
Coles Scraper class.
"""

import logging
from typing import List

import requests

import src.models as models
from src._validators import url_validator
from src.extractors import ColesProductExtractor, ColesProductTileExtractor
from src.fetcher import ColesPageFetcher

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

COLES_URL_PREFIX = r"^https?://(www\.)?coles\.com\.au"
PRODUCT_URL_PATTERN = f"{COLES_URL_PREFIX}/product/.+"  # Product path
BROWSE_URL_PATTERN = f"{COLES_URL_PREFIX}/browse/.+"  # Browse path


class ColesScraper:
    """
    This helper class provides a facade for scraping Coles website.
    """

    def __init__(self, fetcher=None, headers=None):
        self.fetcher = fetcher or ColesPageFetcher(headers=headers)
        self.product_extractor = ColesProductExtractor
        self.product_tile_extractor = ColesProductTileExtractor

    def scrape_product(self, product_id: str) -> models.Product:
        url = f"https://www.coles.com.au/product/{product_id}"
        return self.scrape_product_url(url)

    def scrape_products_by_category(
        self, category: str, page: int = 1
    ) -> List[models.ProductTile]:
        url = f"https://www.coles.com.au/browse/{category}?page={page}"
        return self.scrape_browse_category_url(url)

    @url_validator(PRODUCT_URL_PATTERN)
    def scrape_product_url(self, url: str) -> models.Product:
        response = self.fetch(url)
        return self.product_extractor(response.text).extract()

    @url_validator(BROWSE_URL_PATTERN)
    def scrape_browse_category_url(self, url: str) -> List[models.ProductTile]:
        response = self.fetch(url)
        return self.product_tile_extractor(response.text).extract()

    def fetch(self, url: str) -> requests.Response:
        try:
            response = self.fetcher.get(url)
            response.raise_for_status()
            return response
        except Exception as e:
            logger.exception(f"Error fetching URL {url}: {e}")
            raise
