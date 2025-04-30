"""
Tests for common extraction methods.
"""

from bs4 import BeautifulSoup, Tag

from src.core.base_extractor import HtmlExtractor


def get_soup(html: str) -> Tag:
    """Helper to return a BeautifulSoup Tag from HTML."""
    return BeautifulSoup(html, "html.parser")


def test_get_text_content():
    html = '<div><p class="test"> Hello World </p></div>'
    soup = get_soup(html)
    div_tag = soup.find("div")
    result = HtmlExtractor.get_text_content(div_tag, "p", class_="test")
    assert result == "Hello World"


def test_get_text_content_not_found():
    html = '<div><p class="test"> Hello World </p></div>'
    soup = get_soup(html)
    div_tag = soup.find("div")
    result = HtmlExtractor.get_text_content(div_tag, "span", class_="nonexistent")
    assert result is None


def test_get_all_text_content():
    html = """
    <div>
      <span class="test">First</span>
      <span class="test"> Second </span>
      <span class="test">Third</span>
    </div>
    """
    soup = get_soup(html)
    div_tag = soup.find("div")
    result = HtmlExtractor.get_all_text_content(div_tag, "span", class_="test")
    # The extra spaces in " Second " should be stripped
    assert result == ["First", "Second", "Third"]


def test_get_all_text_content_empty():
    html = "<div><p>Only paragraph</p></div>"
    soup = get_soup(html)
    div_tag = soup.find("div")
    result = HtmlExtractor.get_all_text_content(div_tag, "span", class_="nonexistent")
    assert result == []


def test_get_attribute():
    html = '<div><a href="/link" class="btn">Click here</a></div>'
    soup = get_soup(html)
    div_tag = soup.find("div")
    result = HtmlExtractor.get_attribute(div_tag, "a", "href", class_="btn")
    assert result == "/link"


def test_get_attribute_not_found():
    html = '<div><a href="/link" class="btn">Click here</a></div>'
    soup = get_soup(html)
    div_tag = soup.find("div")
    # Attempt to retrieve an attribute that doesn't exist
    result = HtmlExtractor.get_attribute(div_tag, "a", "data-id", class_="btn")
    assert result is None


def test_get_all_attributes():
    html = """
    <div>
        <a href="/link1" class="btn">Link 1</a>
        <a href="/link2" class="btn">Link 2</a>
        <a href="/link3" class="btn">Link 3</a>
    </div>
    """
    soup = get_soup(html)
    div_tag = soup.find("div")
    result = HtmlExtractor.get_all_attributes(div_tag, "a", "href", class_="btn")
    assert result == ["/link1", "/link2", "/link3"]


def test_get_all_attributes_with_missing():
    html = """
    <div>
        <a href="/link1" class="btn">Link 1</a>
        <a class="btn">Link 2</a>
        <a href="/link3" class="btn">Link 3</a>
    </div>
    """
    soup = get_soup(html)
    div_tag = soup.find("div")
    result = HtmlExtractor.get_all_attributes(div_tag, "a", "href", class_="btn")
    # The second <a> tag has no 'href', so its value should be None.
    assert result == ["/link1", None, "/link3"]
