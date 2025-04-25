"""
Script to scrape all product URLs from Coles sitemap.
"""

import json
import logging
import os
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from src.core.webdriver import initialize_driver

logger = logging.getLogger(__name__)

# --- Constants ---
BASE_URL = "https://www.coles.com.au"
ROBOTS_URL = BASE_URL + "/robots.txt"
SITEMAP_INDEX_URL = BASE_URL + "/sitemap/sitemap-index-products.xml"
PRODUCT_LINKS_REGEX = re.compile(r".+/product/.+")

DEFAULT_TIMEOUT = 20  # seconds
OUTPUT_PATH = Path("data/raw/product-urls-from-sitemap.json")


# --- Session Handling ---
def get_authenticated_session() -> requests.Session:
    driver = initialize_driver(implicit_wait=DEFAULT_TIMEOUT)
    try:
        driver.get(BASE_URL)

        session = requests.Session()
        for cookie in driver.get_cookies():
            session.cookies.set(cookie["name"], cookie["value"])
        session.headers.update(
            {
                "User-Agent": driver.execute_script("return navigator.userAgent"),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
                "Accept-Language": "en-US,en;q=0.9",
                "Connection": "keep-alive",
            }
        )
        return session
    finally:
        driver.quit()


# --- Sitemap Scraping ---
def extract_product_urls_from_sitemaps(session: requests.Session) -> list[str]:
    """
    Extracts all product URLs from the Coles sitemap using an authenticated session.

    Steps:
    1. Check robots.txt to confirm access to sitemap index.
    2. Fetch sitemap index and extract sitemap URLs.
    3. Parse each sitemap for product URLs.
    """
    robots_txt = session.get(ROBOTS_URL).text
    assert SITEMAP_INDEX_URL in robots_txt

    sitemap_index = BeautifulSoup(session.get(SITEMAP_INDEX_URL).content, "xml")
    sitemap_urls = [loc.text.strip() for loc in sitemap_index.find_all("loc")]

    product_urls = []
    for sitemap_url in sitemap_urls:
        sitemap = BeautifulSoup(session.get(sitemap_url).content, "xml")
        urls = [
            loc.text.strip()
            for loc in sitemap.find_all("loc", string=PRODUCT_LINKS_REGEX)
        ]
        product_urls.extend(urls)

    return product_urls


# --- Main Orchestration ---
def get_product_urls() -> list[str]:
    try:
        session = get_authenticated_session()
        return extract_product_urls_from_sitemaps(session)
    except Exception as e:
        logger.exception(f"Failed to extract product URLs: {e}")
        return []


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger.info(f"Scraping products from sitemap")
    urls = get_product_urls()
    logger.info(f"Found {len(urls)} products in sitemap")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        unique_urls = sorted(set(urls))
        json.dump(unique_urls, f)

    logger.info(f"Saved results to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
