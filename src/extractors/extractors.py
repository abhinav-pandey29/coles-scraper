"""
Classes for extracting data from the Coles website.
"""

from typing import List

from bs4.element import Tag

from src import models
from src.extractors.common import HtmlExtractor


class ColesProductTileExtractor(HtmlExtractor):
    """
    Extracts product details from **category browsing pages** on the Coles website.

    This extractor processes HTML content of each "product tiles" from pages with URLs like:
        - https://www.coles.com.au/browse/fruit-vegetables
        - https://www.coles.com.au/browse/fruit-vegetables?page=4

    Typical usage example:
    >>> html_content = ...  # obtain the page's HTML via your fetching logic

    >>> tile_extractor = ColesProductTileExtractor(html_content)
    >>> product_tiles = tile_extractor.extract()

    >>> # Each 'ProductTile' contains fields like 'name', 'url', 'price', etc.
    >>> for tile in product_tiles:
    ...     print(tile.dict())

    Example Output:
    ```
    {
        "name": "Coles Cheese Shredded Tasty Light | 700g",
        "url": "/product/coles-cheese-shredded-tasty-light-700g-8145346",
        "price": "$9.50",
        "price_calc_method": "$13.57 per 1kg",
        "image_url": "/_next/image?url=https%3A%2F%2Fproductimages.coles.com.au%2Fproductimages%2F8%2F8145346.jpg&w=640&q=90",
    }
    ```
    """

    def extract(self) -> List[models.ProductTile]:
        """
        Retrieves all product data from the HTML content.

        :return: A list of ProductTile instances with product details.
        """
        data = []
        product_tiles = self.find_all_product_tiles()
        for tile in product_tiles:
            try:
                product = self.extract_product_from_tile(tile)
                data.append(product)
            except Exception as e:
                self.logger.warning(f"Failed to extract product from tile: {e}")
        return data

    def find_all_product_tiles(self) -> List[Tag]:
        """
        Finds all product tiles in the HTML content.

        :return: A list of BeautifulSoup Tag objects representing product tiles.
        """
        try:
            return self.soup.find_all("section", attrs={"data-testid": "product-tile"})
        except Exception as e:
            self.logger.error(f"Error finding product tiles: {e}")
            return []

    def extract_product_from_tile(self, tile: Tag) -> models.ProductTile:
        """
        Extracts product details from a single product tile.

        :param tile: The BeautifulSoup Tag object representing a product tile.
        :return: An instance of ProductTile with the product's details.
        """
        product_data = {
            "name": self.get_text_content(tile, "h2", class_="product__title"),
            "price": self.get_text_content(tile, "span", class_="price__value"),
            "price_calc_method": self.get_text_content(
                tile, "div", class_="price__calculation_method"
            ),
            "url": self.get_attribute(tile, "a", attr="href", class_="product__link"),
            "image_url": self.get_attribute(tile, "img", attr="src"),
        }
        return models.ProductTile(**product_data)


class ColesProductExtractor(HtmlExtractor):
    """
    Extracts detailed product information from **dedicated product pages** on the Coles website.

    This extractor processes HTML content of pages with URLs like:
        - https://www.coles.com.au/product/appy-fizz-250ml-8060378

    Typical usage example:
    >>> html_content = ...  # obtain the page's HTML via your fetching logic

    >>> product_extractor = ColesProductExtractor(html_content)
    >>> product = product_extractor.extract()

    >>> # Each 'Product' contains fields like 'name', 'brand_name', 'brand_url', etc.
    >>> print(product.dict())

    Example Output:
    ```
    {
        "name": "Appy Fizz | 250mL",
        "brand_name": "Appy",
        "brand_url": "/brands/appy-4039743300",
        "categories": ["Home", "All categories", "Pantry", "International foods", "Indian"],
        "retail_limit": "Retail limit: 20",
        "promotional_limit": "Promotional limit: 12",
        "product_code": "Code: 8060378",
    }
    ```
    """

    def extract(self) -> models.Product:
        """
        Retrieves product data from the product pages HTML content.

        :return: A Product instance with product details.
        """
        product_data = {
            "name": self.get_text_content(self.soup, "h1", class_="product__title"),
            "brand_name": self.get_text_content(
                self.soup, "a", attrs={"data-testid": "brand-link"}
            ),
            "brand_url": self.get_attribute(
                self.soup, "a", attrs={"data-testid": "brand-link"}, attr="href"
            ),
            "categories": self.get_all_text_content(
                self.soup, "span", attrs={"itemprop": "name"}
            ),
            "retail_limit": self.get_text_content(
                self.soup, "p", attrs={"data-testid": "retail-limit"}
            ),
            "promotional_limit": self.get_text_content(
                self.soup, "p", attrs={"data-testid": "promotional-limit"}
            ),
            "product_code": self.get_text_content(
                self.soup, "p", attrs={"data-testid": "product-code"}
            ),
        }
        return models.Product(**product_data)
