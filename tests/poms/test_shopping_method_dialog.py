"""
Tests for ShoppingMethodDialog.
"""

from unittest.mock import Mock, patch

from src.poms.shopping_method_dialog import ShoppingMethodDialogLocators as Locators
from tests.poms.utils import assert_element_presence


def test_focus_click_and_collect_tab(shopping_method_dialog):
    locator = Locators.CLICK_AND_COLLECT_TAB
    assert_element_presence(shopping_method_dialog, locator)

    tab_element = shopping_method_dialog.find_element(locator)
    assert tab_element.get_attribute("data-is-active") in ("true", "false")

    shopping_method_dialog.focus_click_and_collect_tab()

    tab_element = shopping_method_dialog.find_element(locator)
    assert tab_element.get_attribute("data-is-active") == "true"


def test_match_suburb_from_autocomplete(shopping_method_dialog):
    query = "leederville"
    expected_match = Mock(text="Leederville, WA 6007")
    mock_autocomplete_options = [
        Mock(text="West Leederville, WA 6007"),
        expected_match,
    ]
    with patch.object(
        shopping_method_dialog,
        "find_elements",
        return_value=mock_autocomplete_options,
    ):
        match = shopping_method_dialog.match_suburb_from_autocomplete(query)

        assert match is not None
        assert match == expected_match


def test_search_and_select_suburb(shopping_method_dialog):
    locator = Locators.SUBURB_INPUT
    assert_element_presence(shopping_method_dialog, locator)

    shopping_method_dialog.search_and_select_suburb("Leederville")

    search_element = shopping_method_dialog.find_element(locator)
    assert search_element.get_attribute("value") == "Leederville, WA 6007"


# NOTE: This test depends on success of above tests.
def test_select_store_by_index(shopping_method_dialog):
    assert_element_presence(shopping_method_dialog, Locators.STORE_OPTION)

    target_idx = 0  # Select first store from list
    selection = shopping_method_dialog.select_store_by_index(target_idx)

    assert selection is not None
    assert selection.text.startswith("Coles West Leederville")
    # `Set Location` button appears only after successful store selection.
    assert_element_presence(shopping_method_dialog, Locators.SET_LOCATION_BUTTON)
