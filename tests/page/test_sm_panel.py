"""
Tests for ShoppingMethodPanel page object model.
"""

from unittest.mock import Mock, patch

import pytest
from selenium.common.exceptions import TimeoutException

from src.page import ShoppingMethodPanel


@pytest.fixture
def sm_panel():
    return ShoppingMethodPanel(driver=Mock())


def test_input_suburb(sm_panel):
    mock_input_element = Mock()
    sm_panel.find_element = Mock(return_value=mock_input_element)
    mock_autocomplete_options = [Mock(), Mock()]

    with patch(
        "selenium.webdriver.support.ui.WebDriverWait.until",
        return_value=mock_autocomplete_options,
    ):
        results = sm_panel.input_suburb("sydney")

    sm_panel.find_element.assert_called_with(sm_panel.SUBURB_INPUT)
    mock_input_element.send_keys.assert_called_with("sydney")
    assert results == mock_autocomplete_options


def test_input_suburb_not_found(sm_panel):
    mock_input_element = Mock()
    sm_panel.find_element = Mock(return_value=mock_input_element)

    with patch(
        "selenium.webdriver.support.ui.WebDriverWait.until",
        side_effect=TimeoutException,
    ):
        results = sm_panel.input_suburb("some-non-existent-place")

    assert results == []


def test_choose_suburb(sm_panel):
    test_suburb = "earLwOOD, nsW 2206"

    valid_selection = Mock(text="Earlwood, NSW 2206")
    invalid_selection = Mock(text="Clemton Park, NSW 2206")
    mock_suburb_options = [invalid_selection, valid_selection]
    sm_panel.input_suburb = Mock(return_value=mock_suburb_options)

    sm_panel.choose_suburb(full_label=test_suburb)

    sm_panel.input_suburb.assert_called_once_with("2206")
    valid_selection.click.assert_called_once()
    invalid_selection.click.assert_not_called()


def test_choose_suburb_raises_for_invalid_format(sm_panel):
    test_suburb = "Earlwood"

    sm_panel.input_suburb = Mock()

    with pytest.raises(
        ValueError, match=f"Invalid suburb label format: '{test_suburb}'"
    ):
        sm_panel.choose_suburb(full_label=test_suburb)

    sm_panel.input_suburb.assert_not_called()


def test_choose_suburb_raises_if_not_in_dropdown(sm_panel):
    test_suburb = "Smith Residence, NSW 2206"
    mock_suburb_options = [
        Mock(text="Earlwood, NSW 2206"),
        Mock(text="Clemton Park, NSW 2206"),
    ]
    sm_panel.input_suburb = Mock(return_value=mock_suburb_options)

    with pytest.raises(ValueError) as excinfo:
        sm_panel.choose_suburb(full_label=test_suburb)

        # Check error message includes input suburb and available options
        msg = str(excinfo.value)
        assert f"Suburb '{test_suburb}' not found in dropdown options." in msg
        assert all(option.text in msg for option in mock_suburb_options)

    sm_panel.input_suburb.assert_called_once_with("2206")
    for option in mock_suburb_options:
        option.click.assert_not_called()


def test_find_store_radio_items(sm_panel):
    mock_store_radio_items = [Mock(), Mock()]

    with patch(
        "selenium.webdriver.support.ui.WebDriverWait.until",
        return_value=mock_store_radio_items,
    ):
        with patch(
            "selenium.webdriver.support.expected_conditions.visibility_of_all_elements_located",
        ) as mock_find:
            results = sm_panel.find_store_radio_items()

            mock_find.assert_called_once_with(sm_panel.STORE_RADIO_ITEMS)

    assert results == mock_store_radio_items


def test_find_store_radio_items_not_found(sm_panel):
    with patch(
        "selenium.webdriver.support.ui.WebDriverWait.until",
        side_effect=TimeoutException,
    ):
        results = sm_panel.find_store_radio_items()

    assert results == []


def test_set_location(sm_panel):
    sm_panel.click_element_with_wait = Mock()

    sm_panel.set_location()

    sm_panel.click_element_with_wait.assert_called_once_with(
        sm_panel.SET_LOCATION_BUTTON
    )


def test_choose_store(sm_panel):
    test_store = "coles marrickville"

    other_option = Mock(find_element=Mock(return_value=Mock(text="Coles Surry Hills")))
    match_option = Mock(find_element=Mock(return_value=Mock(text="Coles Marrickville")))
    sm_panel.find_store_radio_items = Mock(return_value=[other_option, match_option])
    sm_panel.set_location = Mock()

    sm_panel.choose_store(full_label=test_store)

    other_option.click.assert_not_called()
    other_option.find_element.assert_called_once_with(*sm_panel.STORE_RADIO_LABEL)
    match_option.click.assert_called_once()
    match_option.find_element.assert_called_once_with(*sm_panel.STORE_RADIO_LABEL)
    sm_panel.set_location.assert_called_once()


def test_choose_store_raises_if_not_found(sm_panel):
    test_store = "coles redfern"

    mock_options = [
        Mock(find_element=Mock(return_value=Mock(text="Coles Surry Hills"))),
        Mock(find_element=Mock(return_value=Mock(text="Coles Marrickville"))),
    ]
    sm_panel.find_store_radio_items = Mock(return_value=mock_options)

    with pytest.raises(ValueError) as excinfo:
        sm_panel.choose_store(full_label=test_store)

        # Check error message includes input store and available options
        msg = str(excinfo.value)
        assert f"Store '{test_store}' not found in available options." in msg
        assert all(
            option.find_element.return_value.text in msg for option in mock_options
        )

    for option in mock_options:
        option.click.assert_not_called()


def test_choose_closest_store(sm_panel):
    mock_options = [
        Mock(find_element=Mock(return_value=Mock(text="Coles Surry Hills"))),
        Mock(find_element=Mock(return_value=Mock(text="Coles Marrickville"))),
    ]
    sm_panel.find_store_radio_items = Mock(return_value=mock_options)
    sm_panel.set_location = Mock()

    sm_panel.choose_closest_store()

    closest_option = mock_options[0]
    closest_option.click.assert_called_once()
    sm_panel.set_location.assert_called_once()


def test_choose_closest_store_raises_if_none_found(sm_panel):
    sm_panel.find_store_radio_items = Mock(return_value=[])

    with pytest.raises(ValueError, match="No store options found."):
        sm_panel.choose_closest_store()
