"""
Core package for Coles scraper.
"""

from .base_extractor import HtmlExtractor
from .base_page import BasePage
from .fetcher import ColesPageFetcher
from .utils import validate_url
from .webdriver import init_seleniumwire_webdriver, initialize_driver
