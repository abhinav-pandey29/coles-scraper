"""
Script to scrape all available categories on the Coles website.
"""

import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.poms.categories import CategoriesPage
from src.core.webdriver_utils import initialize_driver

DEST_DIR = "./data/raw"
DEST_FILEPATH = os.path.join(DEST_DIR, "product-categories.json")


def dump_categories(categories):
    os.makedirs(DEST_DIR, exist_ok=True)
    with open(DEST_FILEPATH, "w") as dst:
        json.dump(categories, dst)


if __name__ == "__main__":

    driver = initialize_driver(implicit_wait=15)

    page = CategoriesPage(driver=driver)
    page.open()

    found_categories = page.list_categories()
    if found_categories:
        dump_categories(found_categories)

    driver.quit()
