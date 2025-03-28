from typing import Tuple

import chromedriver_autoinstaller
import undetected_chromedriver as uc
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire.undetected_chromedriver.v2 import Chrome, ChromeOptions


def initialize_driver(headless=False, implicit_wait: int = None):
    options = uc.ChromeOptions()
    options.add_argument("--log-level=3")
    options.add_argument("--deny-permission-prompts")
    if headless:
        options.add_argument("--headless")

    executable_path = chromedriver_autoinstaller.install()
    driver = uc.Chrome(options=options, driver_executable_path=executable_path)
    if implicit_wait and isinstance(implicit_wait, (int, float)):
        driver.implicitly_wait(implicit_wait)
    return driver


def init_seleniumwire_webdriver(*args):
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--deny-permission-prompts")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    return Chrome(options=chrome_options)


def wait_for_presence_of_element(
    driver, locator: Tuple[str, str], timeout: int = 30
) -> None:
    """
    Wait for the presence of a particular web element. This does not necessarily mean that the element is visible.

    :param driver: Selenium WebDriver instance
    :param locator: Locator for the element.
    :param timeout: Maximum wait time in seconds
    :raises: TimeoutException if element is not found within timeout
    """
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))
