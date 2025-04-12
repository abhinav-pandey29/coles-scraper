"""
Base extractors with common extraction utilities.

All extractor classes should inherit from these.
"""

import logging
from typing import List, Optional

from bs4 import BeautifulSoup
from bs4.element import Tag

logger = logging.getLogger(__name__)


class HtmlExtractor:
    """
    Base class for extracting data from HTML content using BeautifulSoup.
    """

    def __init__(self, html_content: str):
        self.soup = BeautifulSoup(html_content, "lxml")
        self.logger = logging.getLogger(self.__class__.__name__)

    def extract(self):
        raise NotImplementedError("Extractors must implement this method.")

    @staticmethod
    def get_text_content(tag: Tag, name: str, **kwargs) -> Optional[str]:
        """
        Extracts text content from a tag.

        :param tag: The BeautifulSoup tag to search within.
        :param name: The name of the tag to find.
        :param kwargs: Additional arguments to pass to the find method.
        :return: The text content if found, otherwise None.
        """
        try:
            element = tag.find(name, **kwargs)
            return element.text.strip() if element else None
        except Exception as e:
            logging.getLogger(HtmlExtractor.__name__).error(
                f"Error extracting text content: {e}"
            )
            return None

    @staticmethod
    def get_all_text_content(tag: Tag, name: str, **kwargs) -> List[str]:
        """
        Extracts text content from all matching tags.

        :param tag: The BeautifulSoup tag to search within.
        :param name: The name of the tag to find.
        :param kwargs: Additional arguments to pass to the find_all method.
        :return: A list of text content from all matching tags, or an empty list if none are found.
        """
        try:
            elements = tag.find_all(name, **kwargs)
            return [element.text.strip() for element in elements if element]
        except Exception as e:
            logging.getLogger(HtmlExtractor.__name__).error(
                f"Error extracting all text content: {e}"
            )
            return []

    @staticmethod
    def get_attribute(tag: Tag, name: str, attr: str, **kwargs) -> Optional[str]:
        """
        Extracts an attribute value from a tag.

        :param tag: The BeautifulSoup tag to search within.
        :param name: The name of the tag to find.
        :param attr: The attribute name to retrieve.
        :param kwargs: Additional arguments to pass to the find method.
        :return: The attribute value if found, otherwise None.
        """
        try:
            element = tag.find(name, **kwargs)
            return (
                element.attrs.get(attr).strip()
                if element and attr in element.attrs
                else None
            )
        except Exception as e:
            logging.getLogger(HtmlExtractor.__name__).error(
                f"Error extracting attribute '{attr}': {e}"
            )
            return None

    @staticmethod
    def get_all_attributes(
        tag: Tag, name: str, attr: str, **kwargs
    ) -> List[Optional[str]]:
        """
        Extracts a specified attribute value from all matching tags.

        :param tag: The BeautifulSoup tag to search within.
        :param name: The name of the tag to find.
        :param attr: The attribute name to retrieve from each tag.
        :param kwargs: Additional arguments to pass to the find_all method.
        :return: A list of attribute values from all matching tags, or an empty list if none are found.
        """
        try:
            elements = tag.find_all(name, **kwargs)
            return [
                (
                    element.attrs.get(attr).strip()
                    if element and attr in element.attrs
                    else None
                )
                for element in elements
            ]
        except Exception as e:
            logging.getLogger(HtmlExtractor.__name__).error(
                f"Error extracting all attribute values for '{attr}': {e}"
            )
            return []
