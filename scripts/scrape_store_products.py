"""
Demo: ColesStorePageFetcher

This demo script illustrates how to scrape product data from Coles for multiple stores
using the ColesStorePageFetcher class.

Features demonstrated:
- Fetching product data by store.
- Dynamically updating the store ID.
"""

import logging
import os
import sys
import time
from dataclasses import dataclass

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.fetcher import ColesStorePageFetcher
from src.scrapers import ColesProductTileScraper

logger = logging.getLogger(__name__)

SLEEP_DURATION_SECONDS = 5  # 5 seconds


@dataclass
class BrowseQuery:
    category: str
    page: int = 1

    @property
    def url(self) -> str:
        return f"https://www.coles.com.au/browse/{self.category}?page={self.page}"


def extract_products_from_browse(fetcher: ColesStorePageFetcher, query: BrowseQuery):
    response = fetcher.get(url=query.url)
    products = ColesProductTileScraper(response.content).get_all_products()
    logger.info(
        "Extracted %d products (Category %s, Pg. %d)",
        len(products),
        query.category,
        query.page,
    )
    return products


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logging.getLogger("seleniumwire.handler").setLevel(logging.WARNING)

    store_ids = ["0392", "0357"]
    test_query = tq = BrowseQuery("fruit-vegetables", page=1)
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
    }

    # Initialize fetcher (optionally, with store_id)
    # This opens the browser, selects a pre-defined store and stores the cookie.
    # Injects store_id into cookie, if provided
    fetcher = ColesStorePageFetcher(headers=headers, store_id=None)
    assert "fulfillmentStoreId" in fetcher.session.headers["cookie"]

    for store_id in store_ids:
        # Updates the fetcher settings and injects the provided store ID
        # into the session cookie
        fetcher.set_store(store_id=store_id)
        assert f"fulfillmentStoreId={store_id}" in fetcher.session.headers["cookie"]

        # Make GET request for your query from the configured store
        response = fetcher.get(url=tq.url)
        assert response.status_code == 200

        # Scrape products from the response webpage
        products = ColesProductTileScraper(response.content).get_all_products()
        logger.info(
            "Extracted %d products from StoreID:%s (Category %s, Pg. %d)",
            len(products),
            fetcher.store_id,
            tq.category,
            tq.page,
        )

        if store_id == store_id[-1]:
            break
        else:
            logger.info("Sleeping for %d seconds...", SLEEP_DURATION_SECONDS)
            time.sleep(SLEEP_DURATION_SECONDS)

    logger.info("Demo completed successfully.")
