import logging
import random
import time
from typing import Callable, Dict, List, Optional

import requests
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from src.webdriver_utils import init_seleniumwire_webdriver

logger = logging.getLogger(__name__)


class ColesPageFetcher:
    """
    Class to manage requests to Coles website.
    """

    DEFAULT_DRIVER_FACTORY = init_seleniumwire_webdriver
    DEFAULT_HEADERS = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
    }
    DEFAULT_REFRESH_URLS = [
        "https://www.coles.com.au/browse/fruit-vegetables",
        "https://www.coles.com.au/browse/frozen",
        "https://www.coles.com.au/browse/dairy-eggs-fridge",
        "https://www.coles.com.au/browse/household",
    ]

    def __init__(
        self,
        driver_factory: Optional[Callable] = None,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict] = None,
        refresh_url: Optional[str] = None,
        sleep_func=time.sleep,
    ):
        """
        :param driver_factory: Callable to create a Selenium (seleniumwire) driver.
        :param session: An optional requests.Session instance.
        :param headers: Optional headers dict; if not provided, defaults are used.
        :param refresh_url: URL to visit when refreshing cookie. Defaults to a random grocery category page.
        :param sleep_func: Function to use for sleeping. Defaults to time.sleep (can be overridden in tests).
        """
        self.driver_factory = driver_factory or self.DEFAULT_DRIVER_FACTORY
        self.session = session or requests.Session()
        self.session.headers = (
            headers.copy() if headers else self.DEFAULT_HEADERS.copy()
        )
        self.refresh_url = refresh_url or random.choice(self.DEFAULT_REFRESH_URLS)
        self.sleep_func = sleep_func

        if not self.session.headers.get("cookie"):
            self.refresh_cookie()

    def get(self, url: str) -> requests.Response:
        """
        Performs a GET request. On error (network or bot detection), refreshes the cookie and retries.
        """
        try:
            response = self._get(url)
        except (requests.RequestException, ValueError) as e:
            logger.error("Error retrieving page with URL '%s': %s", url, e)
            self.refresh_cookie()
            response = self._get(url)

        return response

    def _get(self, url: str) -> requests.Response:
        """
        Internal GET request method that raises a ValueError if bot detection content is found.
        """
        response = self.session.get(url=url)
        response.raise_for_status()

        if ("Incapsula" in str(response.content)) or (
            "Pardon Our Interruption" in str(response.content)
        ):
            logger.warning("Request blocked by bot detection measures.")
            raise ValueError("Bot detected!")

        return response

    def refresh_cookie(self):
        """
        Refreshes current request session's cookie.

        This method opens a browser, and performs two consecutive visits to a predefined
        Coles webpage. 1. The first visit triggers the initial creation of the cookie.
        2. The second visit allows interception of a valid cookie from network requests.

        The intercepted cookie is then stored in the session's headers. This ensures
        that subsequent HTTP requests are properly authenticated.
        """
        logger.info("Refreshing cookie using refresh_url: %s", self.refresh_url)
        driver = self.driver_factory()
        driver.request_interceptor = self._intercept_cookie

        try:
            # First call to prompt cookie creation,
            # Second call to intercept cookie and update headers
            for _ in range(2):
                try:
                    driver.get(self.refresh_url)
                    WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "#coles-targeting-header-container")
                        )
                    )
                    self.sleep_func(5)
                except Exception as e:
                    logger.warning(f"Error while refreshing cookie: {e}")
                    break
        finally:
            driver.quit()

    def _intercept_cookie(self, request):
        """
        Intercepts the cookie from a refresh URL request and sets it in session headers.
        """
        if request.url.startswith(self.refresh_url):
            cookie_value = request.headers.get("cookie")
            if cookie_value:
                logger.info("Intercepted cookie: %s", cookie_value)
                self.session.headers["cookie"] = cookie_value
