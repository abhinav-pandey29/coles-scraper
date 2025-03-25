"""
Extractor for product detail page.
"""

from src import models
from src.extractors.common import HtmlExtractor


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
