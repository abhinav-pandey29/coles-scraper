import logging
import random
import re
import time
from typing import Callable, Dict, List, Optional

import requests
import selenium.webdriver.support.expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from src.poms.shopping_method_dialog import ShoppingMethodDialog
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
        refresh_urls: List[str] = None,
        sleep_func=time.sleep,
    ):
        """
        :param driver_factory: Callable to create a Selenium (seleniumwire) driver.
        :param session: An optional requests.Session instance.
        :param headers: Optional headers dict; if not provided, defaults are used.
        :param refresh_urls: A list of URLs to use for cookie refresh. Defaults to a predefined list.
        :param sleep_func: Function to use for sleeping. Defaults to time.sleep (can be overridden in tests).
        """
        self.driver_factory = driver_factory or self.DEFAULT_DRIVER_FACTORY
        self.session = session or requests.Session()
        self.session.headers = (
            headers.copy() if headers else self.DEFAULT_HEADERS.copy()
        )
        self.refresh_urls = refresh_urls or self.DEFAULT_REFRESH_URLS
        self.refresh_url = random.choice(self.refresh_urls)
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
        driver.request_interceptor = self.intercept_cookie

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

    def intercept_cookie(self, request):
        if request.url.startswith(self.refresh_url):
            cookie_value = request.headers.get("cookie")
            if cookie_value:
                logger.info("Intercepted cookie: %s", cookie_value)
                self.session.headers["cookie"] = cookie_value


class ColesStorePageFetcher(ColesPageFetcher):
    """
    Extends ColesPageFetcher to manage location-specific requests to Coles website.
    """

    DEFAULT_SUBURB_NAME = "Leederville"

    def __init__(
        self,
        driver_factory=None,
        session=None,
        headers=None,
        refresh_urls=None,
        sleep_func=time.sleep,
        suburb_name=None,
        store_id=None,
    ):
        self.suburb_name = suburb_name or self.DEFAULT_SUBURB_NAME
        self.store_id = store_id
        super().__init__(driver_factory, session, headers, refresh_urls, sleep_func)

    def set_suburb(self, suburb_name: str):
        """
        Sets a new suburb for the session.
        """
        if suburb_name != self.suburb_name:
            self.suburb_name = suburb_name
            self.refresh_cookie()

    def set_store(self, store_id: str):
        """
        Sets the store ID in the session cookie.

        If a location-specific cookie already exists, injects the provided `store_id` directly.
        Otherwise, performs a full cookie refresh via browser interaction.
        """
        self.store_id = store_id
        if "fulfillmentStoreId" in self.session.headers["cookie"]:
            self.session.headers["cookie"] = self.inject_store_id(
                self.session.headers["cookie"],
                self.store_id,
            )
            logger.info("Injected store ID in cookie: %s", self.store_id)
        else:
            self.refresh_cookie()

    def refresh_cookie(self):
        """
        This method opens a browser and performs two consecutive visits to a predefined
        Coles webpage. 1. The first visit sets the location for Click & Collect, prompting
        the creation of a location-specific cookie. 2. The second visit intercepts the
        cookie containing the configured location from network requests.

        If a `store_id` is explicitly set, this method injects it into the intercepted cookie,
        replacing the existing `fulfillmentStoreId` value.

        The resulting cookie is stored in the session's headers. This ensures subsequent
        HTTP requests are properly authenticated with the selected location.
        """
        logger.info("Refreshing cookie using refresh_url: %s", self.refresh_url)
        driver = self.driver_factory()
        driver.request_interceptor = self.intercept_cookie

        try:
            driver.get(self.refresh_url)
            self.set_store_in_browser(driver)

            driver.get(self.refresh_url)
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "#coles-targeting-header-container")
                )
            )
        except Exception as e:
            logger.warning("Error while refreshing cookie: %s", e)
        finally:
            driver.quit()

    def intercept_cookie(self, request):
        if request.url.startswith(self.refresh_url):
            cookie_value = request.headers.get("cookie")
            if cookie_value:
                logger.info("Intercepted cookie: %s", cookie_value)
                if self.store_id is not None:
                    assert "fulfillmentStoreId" in cookie_value
                    cookie_value = self.inject_store_id(cookie_value, self.store_id)
                    logger.info("Injected store ID in cookie: %s", self.store_id)

                self.session.headers["cookie"] = cookie_value

    def set_store_in_browser(self, driver):
        """
        Sets the shopping location in the browser.

        1. Opens the store selection dialog ('Choose Store' or 'Set shopping method').
        2. Activates the 'Click & Collect' tab.
        3. Searches for and selects the configured suburb.
        4. Selects the first available store option from the results.
        """
        suburb_name = self.suburb_name

        if not self._click_if_present(
            driver, '//*[@data-testid="choose-a-store-button"]'
        ):
            self._click_if_present(
                driver, '//*[@data-testid="delivery-selector-button"]'
            )

        dialog = ShoppingMethodDialog(driver)
        dialog.focus_click_and_collect_tab()
        dialog.search_and_select_suburb(suburb_name)
        dialog.select_store_by_index(0)  # selects the first store in suburb
        dialog.click_set_location()

    @staticmethod
    def _click_if_present(driver, xpath: str, timeout: int = 10) -> bool:
        try:
            button = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            button.click()
            return True
        except TimeoutException:
            logger.debug("Button not found or not clickable: %s", xpath)
            return False

    @staticmethod
    def inject_store_id(cookie: str, store_id: str) -> str:
        return re.sub(
            pattern=r"fulfillmentStoreId=\d+",
            repl=f"fulfillmentStoreId={store_id}",
            string=cookie,
        )
