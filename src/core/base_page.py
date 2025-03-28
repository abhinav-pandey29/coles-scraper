"""
Base Page Object Model for Selenium-based interactions.

All page objects should inherit from this.
"""

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    """Base Page class."""

    url: str

    def __init__(self, driver):
        self.driver = driver

    def open(self):
        self.driver.get(self.url)

    def find_element(self, locator):
        return self.driver.find_element(*locator)

    def find_elements(self, locator):
        return self.driver.find_elements(*locator)

    def click_element(self, locator):
        element = self.find_element(locator)
        element.click()
        return element

    def click_element_with_wait(self, locator, duration=10):
        element = WebDriverWait(self.driver, duration).until(
            EC.element_to_be_clickable(locator)
        )
        element.click()
        return element

    def wait_for_element_visibility(self, locator, timeout=30) -> bool:
        """Returns True if the element is visible within the timeout, False otherwise."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False
