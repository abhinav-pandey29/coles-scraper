"""
Script to scrape all products for given categories on the Coles website.
"""

import logging
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

import pandas as pd
import pytz

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.coles_scraper import ColesScraper
from src.models import ProductTile

logger = logging.getLogger(__name__)

LOCAL_TZ = pytz.timezone("Australia/Sydney")
PAUSE_BETWEEN_CATEGORIES = 300  # 5 minutes


@dataclass
class BrowseQuery:
    category: str
    page: int = 1

    @property
    def url(self) -> str:
        return f"https://www.coles.com.au/browse/{self.category}?page={self.page}"

    def __repr__(self):
        return f"Category: {self.category}, Pg. {self.page}"


class ColesCategoryProductPipeline:
    """
    Pipeline to extract, transform, and load product data from Coles category browse pages.

    Responsibilities:
    - Extract: Paginate through Coles browse pages to collect product tiles per category.
    - Transform: Parse and clean product details and extract structured fields.
    - Load: Append new data to the raw dataset, archive duplicates, and write cleaned data to processed output.

    Raw data is saved to:        data/raw/products.csv
    Archived duplicates to:      data/archive/products_dropped.csv
    Transformed output to:       data/processed/products.csv
    """

    def __init__(
        self,
        scraper: ColesScraper,
        categories: List[str],
        raw_path: str = "data/raw/products.csv",
        archive_path: str = "data/archive/products_dropped.csv",
        processed_path: str = "data/processed/products.csv",
    ):
        self.scraper = scraper
        self.categories = categories
        self.raw_path = Path(raw_path)
        self.archive_path = Path(archive_path)
        self.processed_path = Path(processed_path)

    def run(self):
        self.now = datetime.now(tz=LOCAL_TZ)
        for i, category in enumerate(self.categories):
            products = self.extract(category)
            self.load(products, category)
            if i < len(self.categories) - 1:
                logger.info("Sleeping for %d seconds...", PAUSE_BETWEEN_CATEGORIES)
                time.sleep(PAUSE_BETWEEN_CATEGORIES)

    def extract(self, category: str) -> List[ProductTile]:
        query = BrowseQuery(category=category, page=1)
        products = []
        while True:
            try:
                results = self.scraper.scrape_browse_category_url(query.url)
                logger.info("Extracted %d products (%s)", len(results), query)
            except Exception as e:
                results = []
                logger.error("Error extracting products for %s: %s", query, e)

            time.sleep(1)

            if results:
                products.extend(results)
                query.page += 1
            else:
                break

        logger.info("Total `%s` products: %d", category, len(products))
        return products

    def load(self, products: List[ProductTile], category: str):
        if not products:
            logger.warning("No products found for category: %s", category)
            return

        df_new = pd.DataFrame(products)
        df_new["category"] = category
        df_new["date"] = self.now.strftime("%Y-%m-%d")
        df_new["timestamp"] = self.now.isoformat()

        df_deduped = self._save_raw_and_archive(df_new)
        cleaned_products_df = self.transform(df_deduped)

        self.processed_path.parent.mkdir(parents=True, exist_ok=True)
        cleaned_products_df.to_csv(self.processed_path, index=False)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["url"] = "https://www.coles.com.au" + df["url"]
        df["image_url"] = "https://www.coles.com.au" + df["image_url"]
        df["product_id"] = df["url"].str.extract(r"product\/(.+)\-\d+$")
        df["size"] = df["name"].str.extract(r"\| (.+)$")
        df["price_aud"] = df["price"].str.extract(r"\$([\d,]+\.\d+)").astype(float)
        df["was_price_aud"] = (
            df["price_calc_method"].str.extract(r"Was \$([\d,]+\.\d+)").astype(float)
        )
        df["was_date"] = df["price_calc_method"].str.extract(
            r"Was \$[\d,]+\.\d+ on (\w{3} \d{4})"
        )
        df["unit_price_aud"] = (
            df["price_calc_method"]
            .str.replace(",", "")
            .str.extract(r"\$([\d,]+\.\d+) per")
            .astype(float)
        )
        df["unit"] = (
            df["price_calc_method"]
            .str.replace("Was", "")
            .str.extract(r"\$[\d,]+\.\d+ per (\w+)(?:\s*Was)?")
        )

        df.drop_duplicates(subset=["product_id"], keep="first", inplace=True)

        df = df.rename(
            columns={
                "name": "product_name",
                "url": "product_url",
                "price": "display_price",
                "price_calc_method": "pricing_details",
                "image_url": "product_image_url",
                "date": "scrape_date",
                "timestamp": "scrape_timestamp",
                "price_aud": "current_price_aud",
                "was_price_aud": "previous_price_aud",
                "was_date": "previous_price_date",
                "unit": "unit_of_measure",
            }
        )

        cols_order = [
            "product_id",
            "product_name",
            "category",
            "size",
            "product_url",
            "product_image_url",
            "display_price",
            "current_price_aud",
            "promotion_type",
            "unit_price_aud",
            "unit_of_measure",
            "previous_price_aud",
            "pricing_details",
            "previous_price_date",
            "scrape_date",
            "scrape_timestamp",
        ]
        if len(cols_order) < len(df.columns):
            _dropped_cols = [col for col in df.columns if col not in cols_order]
            logger.warning(f"Dropping columns not in output schema: {_dropped_cols}")

        return df[cols_order]

    def _save_raw_and_archive(self, df_new: pd.DataFrame) -> pd.DataFrame:
        path = self.raw_path
        archive = self.archive_path

        if path.exists():
            df_existing = pd.read_csv(path)
            products_df = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            products_df = df_new.copy()

        products_df["timestamp_parsed"] = pd.to_datetime(
            products_df["timestamp"], errors="coerce", utc=True
        )
        products_df.sort_values("timestamp_parsed", ascending=False, inplace=True)

        dup_mask = products_df.duplicated(subset=["url"], keep="first")
        df_final = products_df[~dup_mask].drop(columns=["timestamp_parsed"])
        df_dropped = products_df[dup_mask].drop(columns=["timestamp_parsed"])

        path.parent.mkdir(parents=True, exist_ok=True)
        df_final.to_csv(path, index=False)

        if not df_dropped.empty:
            if archive.exists():
                df_archive = pd.read_csv(archive)
                df_archive = pd.concat([df_archive, df_dropped], ignore_index=True)
            else:
                df_archive = df_dropped
            archive.parent.mkdir(parents=True, exist_ok=True)
            df_archive.to_csv(archive, index=False)

        logger.info("Saved %d deduplicated rows to %s", len(df_final), path)
        logger.info("Archived %d duplicate rows to %s", len(df_dropped), archive)
        return df_final


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    # Silence seleniumwire logs of network requests
    logging.getLogger("seleniumwire.handler").setLevel(logging.WARNING)

    headers = {
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"
        ),
        # Paste cookie string from browser Dev Tools if needed
        "cookie": None,
    }
    scraper = ColesScraper(headers=headers)

    categories = [
        # "fruit-vegetables",
        "dairy-eggs-fridge",
        "pantry",
        "meat-seafood",
        "bakery",
        "frozen",
        "household",
        "health-beauty",
        "deli",
        "pet",
        "baby",
        "liquor",
    ]
    pipeline = ColesCategoryProductPipeline(scraper, categories)
    pipeline.run()
