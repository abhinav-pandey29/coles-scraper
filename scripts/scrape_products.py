"""
Script to scrape all products for given categories on the Coles website.
"""

import logging
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import List

import pandas as pd
import pytz

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.coles_scraper import ColesScraper
from src.models import ProductTile

logger = logging.getLogger(__name__)

LOCAL_TZ = pytz.timezone("Australia/Sydney")
DURATION_5_MINS = 300


@dataclass
class BrowseQuery:
    category: str
    page: int = 1

    @property
    def url(self) -> str:
        return f"https://www.coles.com.au/browse/{self.category}?page={self.page}"

    def __repr__(self):
        return f"Category: {self.category}, Pg. {self.page}"


def update_csv_with_archive(
    new_df: pd.DataFrame, target_path: str, archive_path: str
) -> None:
    """
    Appends new_df to an existing CSV file at target_path, deduplicates rows (keeping only the latest
    record based on the 'timestamp' column), and saves dropped duplicate rows to archive_path.
    """
    if os.path.exists(target_path):
        df_existing = pd.read_csv(target_path)
        df_combined = pd.concat([df_existing, new_df], ignore_index=True)
    else:
        df_combined = new_df.copy()

    df_combined["timestamp_parsed"] = pd.to_datetime(
        df_combined["timestamp"], errors="coerce"
    )
    df_combined.sort_values("timestamp_parsed", ascending=False, inplace=True)
    dup_mask = df_combined.duplicated(subset=["url"], keep="first")

    # Latest prices and product info to save
    df_final = df_combined[~dup_mask].copy()
    df_final.drop(columns=["timestamp_parsed"], inplace=True)

    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    df_final.to_csv(target_path, index=False)
    logger.info("Saved %d deduplicated rows to %s", len(df_final), target_path)

    # Stale prices and product info to archive
    df_dropped = df_combined[dup_mask].copy()
    if not df_dropped.empty:
        df_dropped.drop(columns=["timestamp_parsed"], inplace=True)
        os.makedirs(os.path.dirname(archive_path), exist_ok=True)
        if os.path.exists(archive_path):
            df_archive = pd.read_csv(archive_path)
            df_archive = pd.concat([df_archive, df_dropped], ignore_index=True)
        else:
            df_archive = df_dropped
        df_archive.to_csv(archive_path, index=False)
        logger.info("Archived %d duplicate rows to %s", len(df_dropped), archive_path)


def process_product_data(input_path, output_path):
    """
    Reads scraped product data from a CSV, extracts and transforms
    fields, renames and reorders columns, and saves the processed product data
    to the output path.
    """
    df = pd.read_csv(input_path).copy()

    # Prepend base URL for product and image URLs.
    df["url"] = "https://www.coles.com.au" + df["url"]
    df["image_url"] = "https://www.coles.com.au" + df["image_url"]

    # Extract fields using regex.
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

    # Remove duplicate products.
    df.drop_duplicates(subset=["product_id"], keep="first", inplace=True)

    # Rename columns for clarity.
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

    # Reorder columns to group related information.
    cols_order = [
        "product_id",
        "product_name",
        "category",
        "size",
        "product_url",
        "product_image_url",
        "display_price",
        "current_price_aud",
        "unit_price_aud",
        "unit_of_measure",
        "previous_price_aud",
        "pricing_details",
        "previous_price_date",
        "scrape_date",
        "scrape_timestamp",
    ]
    df = df[cols_order]

    # Ensure the output directory exists and save the processed data.
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)


def dump_products(products: List[ProductTile], category: str) -> None:
    """
    Process and archive new product data for a given category.

    This function converts a list of ProductTile objects into a DataFrame,
    enriches it with metadata, appends it to the raw products CSV (archiving duplicates),
    and regenerates the processed products dataset.
    """
    if not products:
        logger.info("No products to save for category '%s'.", category)
        return

    df_new = pd.DataFrame(products)
    now = datetime.now(tz=LOCAL_TZ)
    df_new["category"] = category
    df_new["date"] = now.strftime("%Y-%m-%d")
    df_new["timestamp"] = now.isoformat()

    target_file = os.path.join("data", "raw", "products.csv")
    archive_file = os.path.join("data", "archive", "products_dropped.csv")
    processed_file = os.path.join("data", "processed", "products.csv")

    update_csv_with_archive(df_new, target_file, archive_file)
    logger.info("Processed %d new rows for category '%s'.", len(df_new), category)

    process_product_data(input_path=target_file, output_path=processed_file)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,  # Set to INFO or WARNING in production.
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    # Silence seleniumwire logs of network requests
    logging.getLogger("seleniumwire.handler").setLevel(logging.WARNING)

    categories = [
        "fruit-vegetables",
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
    headers = {
        "cookie": None,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
    }
    scraper = ColesScraper(headers=headers)

    for category in categories:
        query = BrowseQuery(category=category, page=1)
        products = []
        while True:
            try:
                browse_results = scraper.scrape_browse_category_url(query.url)
                logger.info("Extracted %d products (%s)", len(browse_results), query)
            except Exception as e:
                browse_results = []
                logger.error("Error extracting products for %s: %s", query, e)

            if browse_results:
                products.extend(browse_results)
                query.page += 1
            else:
                break

        dump_products(products, category)

        if category != categories[-1]:
            logger.info("Sleeping for %d seconds...", DURATION_5_MINS)
            time.sleep(DURATION_5_MINS)
