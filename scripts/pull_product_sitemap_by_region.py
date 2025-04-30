"""
Experimental script to scrape all product URLs from Coles sitemap
using region-specific cookies.

NOTE: Use `scripts/pull_product_sitemap.py` instead. The sitemap lists the
same products regardless of region, so this script is unnecessary.
"""

import json
import logging
import os
import random
import re
import sys
import time
from pathlib import Path

import requests
import selenium.webdriver.support.expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from src.core.webdriver import initialize_driver
from src.page import ShoppingMethodPanel

logger = logging.getLogger(__name__)

# --- Constants ---
BASE_URL = "https://www.coles.com.au"
ROBOTS_URL = BASE_URL + "/robots.txt"
SITEMAP_INDEX_URL = BASE_URL + "/sitemap/sitemap-index-products.xml"
PRODUCT_LINKS_REGEX = re.compile(r".+/product/.+")

DEFAULT_TIMEOUT = 20  # seconds
REGION_SUBURB_MAP = {
    "nsw": "Lane Cove, NSW 2066",
    "wa": "Innaloo, WA 6018",
    "vic": "Richmond, VIC 3121",
    "qld": "Carindale, QLD 4152",
    # "sa": "Norwood, SA 5067",
    # "nt": "Casuarina, NT 0810",
    # "tas": "Sandy Bay, TAS 7005",
    # "act": "Acton, ACT 2601",
}
OUTPUT_PATH = Path("data/raw/product-urls-by-region.json")


# --- Region Setup ---
def set_region(driver, region: str):
    suburb = REGION_SUBURB_MAP[region.lower()]
    logger.info(f"Setting region to {region} ({suburb})")

    driver.maximize_window()
    panel = _open_shopping_method_dialog(driver)
    panel.choose_suburb(suburb)
    panel.choose_closest_store(auto_confirm=True)
    logger.info("Region set successfully")


def _open_shopping_method_dialog(driver) -> ShoppingMethodPanel:
    selector_buttons = [
        '//*[@data-testid="choose-a-store-button"]',
        '//*[@data-testid="delivery-selector-button"]',
    ]
    for xpath in selector_buttons:
        if _try_click(driver, xpath):
            return ShoppingMethodPanel(driver)
    raise RuntimeError("Failed to open store selector.")


def _try_click(driver, xpath: str, timeout: int = 10) -> bool:
    try:
        button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        button.click()
        return True
    except TimeoutException:
        logger.debug("Button not clickable: %s", xpath)
        return False


# --- Session Handling ---
def get_authenticated_session(region: str) -> requests.Session:
    driver = initialize_driver(implicit_wait=DEFAULT_TIMEOUT)
    try:
        driver.get(BASE_URL)
        set_region(driver, region)

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
def get_product_urls(region: str) -> list[str]:
    try:
        session = get_authenticated_session(region)
        return extract_product_urls_from_sitemaps(session)
    except Exception as e:
        logger.exception(f"Failed to extract product URLs: {e}")
        return []


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    regions = list(REGION_SUBURB_MAP.keys())
    random.shuffle(regions)
    all_products = {}

    for region in regions:
        logger.info(f"Scraping products for region: {region}")
        urls = get_product_urls(region)
        logger.info(f"Found {len(urls)} products for {region}")
        all_products[region] = sorted(set(urls))

        time.sleep(DEFAULT_TIMEOUT)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(all_products, f)

    logger.info(f"Saved results to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
