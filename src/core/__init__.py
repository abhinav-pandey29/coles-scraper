"""
Core package for Coles scraper.
"""

from .base_extractor import HtmlExtractor
from .fetcher import ColesPageFetcher
from .webdriver_utils import init_seleniumwire_webdriver, initialize_driver
