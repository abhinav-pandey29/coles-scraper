"""
Package for scraping product data from Coles online storefront.
"""

from .coles_scraper import ColesScraper
from .core import ColesPageFetcher
from .extractors import ColesProductExtractor, ColesProductTileExtractor
from .models import Product, ProductTile
