import pytest
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from src.poms.shopping_method_dialog import (
    ShoppingMethodDialog,
    ShoppingMethodDialogLocators,
)
from src.webdriver_utils import initialize_driver


@pytest.fixture(scope="module")
def shopping_method_dialog():
    """
    Fixture to open the ShoppingMethodDialog and ensure it is fully loaded.
    """
    driver = initialize_driver()
    driver.get("https://coles.com.au/browse")
    choose_store_btn = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//*[@data-testid="choose-a-store-button"]')
        )
    )
    choose_store_btn.click()

    # Wait for the dialog to load
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(ShoppingMethodDialogLocators.DIALOG)
    )

    yield ShoppingMethodDialog(driver)

    driver.quit()
