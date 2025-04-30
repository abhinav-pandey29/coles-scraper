"""
This script uses a Selenium-driven browser to search for products on the Coles
website and save the HTML content of individual product pages to local storage.
It is designed to avoid duplicate processing by checking against an existing
index of saved product IDs.
"""

import json
import logging
import os
import sys
import time
from datetime import datetime
from glob import glob

import pandas as pd
import selenium.webdriver.support.expected_conditions as EC
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.core.base_page import BasePage
from src.core.webdriver import initialize_driver

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

SRC_GLOB = "data/raw/products-by-category/*/*.json"
DST_DIR = "data/raw/product-webpages"
DST_FILEPATH_TEMPLATE = DST_DIR + "/{product_id}.html"
METADATA_FILEPATH = "data/raw/00_index.json"
SHORT_SLEEP_SECONDS = 5
MID_SLEEP_SECONDS = 10


def load_targets():
    data = []
    for path in glob(SRC_GLOB):
        data.append(pd.read_json(path))

    df = pd.concat(data, axis=0)
    df["product_id"] = df["url"].apply(lambda url: url.split("/")[-1])
    df["name"] = df["name"].apply(lambda nm: nm.split("|")[0].lower().strip())

    scraped_products = load_index()
    target_mask = ~df["product_id"].isin(scraped_products)
    targets = df.loc[target_mask, "name"].unique()
    return targets


def dump_html(product_id, html_content):
    os.makedirs(DST_DIR, exist_ok=True)
    file_path = DST_FILEPATH_TEMPLATE.format(product_id=product_id)
    with open(file_path, "w", encoding="utf-8") as dst:
        dst.write(html_content)
        logger.info(f"Page saved to {file_path}")
        update_index(product_id=product_id)


def update_index(product_id):
    metadata = load_index()
    metadata[product_id] = str(datetime.today())
    with open(METADATA_FILEPATH, "w") as f:
        json.dump(metadata, f)


def init_index():
    for path in glob(DST_DIR + "/*.html"):
        product_id = path.split("\\")[-1].replace(".html", "")
        update_index(product_id)


def load_index():
    try:
        with open(METADATA_FILEPATH, "r") as f:
            metadata = json.load(f)
    except FileNotFoundError:
        metadata = {}
    return metadata


class ColesPageLocators:
    SEARCH_BAR = (By.ID, "search-text-input")
    SEARCH_ICON = (By.ID, "search-icon")
    SEARCH_INPUT = (By.ID, "search-box-input")
    PRODUCT_CARD = (By.XPATH, '//section[@data-testid="product-tile"]')
    BRAND_LINK = (By.XPATH, '//a[@data-testid="brand-link"]')
    CLOSE_POPUP_BUTTON = (By.XPATH, '//button[@aria-label="close popup"]')


class ColesPage(BasePage):

    def search(self, query):
        try:
            self.click_element(ColesPageLocators.SEARCH_BAR)
        except ElementNotInteractableException:
            self.click_element(ColesPageLocators.SEARCH_ICON)

        search_input = self.click_element(ColesPageLocators.SEARCH_INPUT)
        search_input.send_keys(Keys.CONTROL, "a")
        search_input.send_keys(query)
        time.sleep(1)
        search_input.send_keys(Keys.ENTER)

    def close_popup(self):
        return self.click_element(ColesPageLocators.CLOSE_POPUP_BUTTON)

    def click_search_result(self, index: int = 0) -> bool:
        product_cards = self.find_elements(ColesPageLocators.PRODUCT_CARD)
        try:
            target = product_cards[index]
            target.click()
            return True
        except IndexError:
            logger.info(
                f"Cannot click card at index {index}."
                + f"No. of products = {len(product_cards)}",
            )
            return False

    def save_product_from_search(self, query):
        self.search(query)
        time.sleep(SHORT_SLEEP_SECONDS)
        try:
            clicked = self.click_search_result(0)
        except ElementClickInterceptedException:
            self.close_popup()
            clicked = self.click_search_result(0)

        if clicked and self._is_product_page_loaded():
            product_id = self.driver.current_url.split("/")[-1]
            product_html = self.driver.page_source
            dump_html(product_id=product_id, html_content=product_html)
        else:
            logger.info("Couldn't save!")

    def _is_product_page_loaded(self) -> bool:
        WebDriverWait(self.driver, MID_SLEEP_SECONDS).until(
            EC.visibility_of_element_located(ColesPageLocators.BRAND_LINK)
        )
        return self.driver.current_url.startswith("https://www.coles.com.au/product")


if __name__ == "__main__":

    logger.info("Started")
    targets = load_targets()

    logger.info("Initializing driver")
    driver = initialize_driver()
    driver.get("https://www.coles.com.au")

    coles_page = ColesPage(driver)
    for query in targets[::-1]:
        logger.debug(f"Querying: {query}")
        try:
            coles_page.save_product_from_search(query)
        except (
            StaleElementReferenceException,
            TimeoutException,
            NoSuchElementException,
        ) as e:
            logger.info(f"Failed for {query}. ExceptionType: {type(e)}")
            time.sleep(5)
            continue
