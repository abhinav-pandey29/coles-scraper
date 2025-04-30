import re
from typing import List

import selenium.webdriver.support.expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait

from src.core import BasePage


class ShoppingMethodPanel(BasePage):

    SUBURB_INPUT = (By.ID, "suburb-postcode-autocomplete")
    SUBURB_DD_ITEMS = (
        By.XPATH,
        '//li[contains(@id, "suburb-postcode-autocomplete-option")]',
    )
    STORE_RADIO_ITEMS = (By.XPATH, '//div[@data-rocket-comp="card-radio"]')
    STORE_RADIO_LABEL = (By.XPATH, ".//span[contains(text(), 'Coles')]")
    STORE_RADIO_INPUT = (By.XPATH, ".//input")
    SET_LOCATION_BUTTON = (By.XPATH, '//button/span[contains(text(), "Set location")]')

    SUBURB_REGEX = re.compile(
        r"^(?P<suburb>.+), (?P<state>[A-Za-z]{2,3}) (?P<postcode>\d{4})$"
    )

    def input_suburb(self, value: str) -> List[WebElement]:
        field = self.find_element(self.SUBURB_INPUT)
        field.send_keys(Keys.LEFT_CONTROL, "a")
        field.send_keys(value)

        try:
            return WebDriverWait(self.driver, 10).until(
                EC.visibility_of_all_elements_located(self.SUBURB_DD_ITEMS)
            )
        except TimeoutException:
            return []

    def choose_suburb(self, full_label: str) -> None:
        full_label = full_label.strip()

        match = self.SUBURB_REGEX.match(full_label)
        if not match:
            raise ValueError(f"Invalid suburb label format: '{full_label}'")

        search_term = match.group("postcode") or match.group("suburb")
        options = self.input_suburb(search_term)

        for option in options:
            if option.text.strip().lower() == full_label.lower():
                option.click()
                return

        suburb_options = [option.text for option in options]
        formatted_options = "\n  - " + "\n  - ".join(suburb_options)
        raise ValueError(
            f"Suburb '{full_label}' not found in dropdown options.\n"
            f"Available options were:{formatted_options}"
        )

    def find_store_radio_items(self) -> List[WebElement]:
        try:
            return WebDriverWait(self.driver, 10).until(
                EC.visibility_of_all_elements_located(self.STORE_RADIO_ITEMS)
            )
        except TimeoutException:
            return []

    def set_location(self) -> None:
        self.click_element_with_wait(self.SET_LOCATION_BUTTON)

    def choose_store(self, full_label: str, auto_confirm: bool = True) -> None:
        options = self.find_store_radio_items()

        for option in options:
            option_label = option.find_element(*self.STORE_RADIO_LABEL)

            option_label_norm = option_label.text.strip().lower()
            full_label_norm = full_label.strip().lower()

            if option_label_norm == full_label_norm:
                option.click()
                if auto_confirm:
                    self.set_location()
                return

        store_names = [
            option.find_element(*self.STORE_RADIO_LABEL).text for option in options
        ]
        formatted_options = "\n  - " + "\n  - ".join(store_names)
        raise ValueError(
            f"Store '{full_label}' not found in available options.\n"
            f"Available options were:{formatted_options}"
        )

    def choose_closest_store(self, auto_confirm: bool = True) -> None:
        options = self.find_store_radio_items()
        if not options:
            raise ValueError("No store options found.")

        # Assumes store options are sorted by proximity
        options[0].click()
        if auto_confirm:
            self.set_location()
