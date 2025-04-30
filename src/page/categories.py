"""
Page Object Model for Coles browse page.
"""

from src.core.base_page import BasePage
from src.core.webdriver import By


class CategoriesPageLocators:
    """
    A class for Categories page locators. All Categories page
    locators should come here.
    """

    CATEGORY_CARD = (By.XPATH, '//*[@data-testid="category-card"]')


class CategoriesPage(BasePage):
    """Categories page action methods come here"""

    url = "https://www.coles.com.au/browse"

    def list_categories(self):
        cards = self.find_elements(CategoriesPageLocators.CATEGORY_CARD)
        categories = [
            {
                "name": card.text,
                "url": card.get_attribute("href"),
                "slug": card.get_attribute("href").split("/")[-1],
            }
            for card in cards
        ]
        return categories
