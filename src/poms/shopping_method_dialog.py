"""
Page Object Model for Coles shopping method dialog.
"""

import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from src.poms.base import BasePage


class ShoppingMethodDialogLocators:
    """
    A class for Shopping method dialog locators. All Shopping method dialog
    locators should come here.
    """

    DIALOG = (By.XPATH, '//*[@data-testid="shopping-method"]')
    CLICK_AND_COLLECT_TAB = (By.XPATH, '//*[@data-testid="tab-collection"]')
    SUBURB_INPUT = (By.ID, "suburb-postcode-autocomplete")
    SUBURB_OPTION = (
        By.XPATH,
        '//li[contains(@id, "suburb-postcode-autocomplete-option")]',
    )
    STORE_OPTION = (
        By.XPATH,
        '//div[contains(@id, "card-radio-button-CollectFromDrawerContent")]',
    )
    SET_LOCATION_BUTTON = (By.XPATH, '//button[@data-testid="cta-secondary"]')


class ShoppingMethodDialog(BasePage):
    """Shopping Method dialog actions come here."""

    def focus_click_and_collect_tab(self):
        """Activate 'Click & Collect' tab if not already active."""
        tab = self.find_element(ShoppingMethodDialogLocators.CLICK_AND_COLLECT_TAB)
        if tab.get_attribute("data-is-active") != "true":
            tab.click()

    def search_and_select_suburb(self, suburb_name: str):
        """Select suburb for Click & Collect."""
        search_input = self.click_element(ShoppingMethodDialogLocators.SUBURB_INPUT)
        search_input.send_keys(suburb_name)

        self.wait_for_element_visibility(ShoppingMethodDialogLocators.SUBURB_OPTION)
        matched_option = self.match_suburb_from_autocomplete(suburb_name)

        if matched_option:
            matched_option.click()
            self.wait_for_element_visibility(ShoppingMethodDialogLocators.STORE_OPTION)
        else:
            raise ValueError(f"Suburb not found: {suburb_name}")

    def match_suburb_from_autocomplete(self, suburb_name: str):
        """Find a matching suburb option from autocomplete suggestions."""
        suburb_options = self.find_elements(ShoppingMethodDialogLocators.SUBURB_OPTION)
        suburb_name_lower = suburb_name.lower()

        for option in suburb_options:
            if option.text.lower().startswith(suburb_name_lower):
                return option
        return None

    def select_store_by_index(self, index: int = 0) -> WebElement:
        """Select a store option based on its index."""
        store_options = self.find_elements(ShoppingMethodDialogLocators.STORE_OPTION)
        if index < len(store_options):
            store_options[index].click()
            return store_options[index]
        else:
            raise IndexError(f"Store option index '{index}' out of range.")

    def click_set_location(self):
        """Click the 'Set Location' button to confirm store selection."""
        self.click_element(ShoppingMethodDialogLocators.SET_LOCATION_BUTTON)
