from selenium.common.exceptions import NoSuchElementException


def assert_element_presence(page_object, locator):
    """Asserts that an element is present on the page."""
    try:
        element = page_object.find_element(locator)
        return element
    except NoSuchElementException as error:
        raise AssertionError(
            f"Element with locator {locator} was not found."
        ) from error
