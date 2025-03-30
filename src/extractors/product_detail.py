"""
Extractor for product detail page.
"""

from src import models
from src.core.base_extractor import HtmlExtractor


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
        Retrieves product data from the product page's HTML content.

        :return: A Product instance with product details.
        """
        return models.Product(
            url=self.extract_url(),
            slug=self.extract_slug(),
            name=self.extract_name(),
            brand_name=self.extract_brand_name(),
            brand_slug=self.extract_brand_slug(),
            price=self.extract_price(),
            price_calc_desc=self.extract_price_calc_desc(),
            image_url=self.extract_image_url(),
            categories=self.extract_categories(),
            tags=self.extract_tags(),
            additional_desc=self.extract_additional_desc(),
            nutritional_info=self.extract_nutritional_info(),
            ingredients=self.extract_panel_text("ingredients-panel"),
            allergens=self.extract_panel_text("allergen-panel"),
            dietary=self.extract_panel_text("dietary-panel"),
            usage_instructions=self.extract_panel_text("usage-instructions-panel"),
            storage_instructions=self.extract_panel_text("storage-instructions-panel"),
            warnings=self.extract_panel_text("warnings-panel"),
            retail_limit=self.extract_text_by_testid("p", "retail-limit"),
            promotional_limit=self.extract_text_by_testid("p", "promotional-limit"),
            product_code=self.extract_text_by_testid("p", "product-code"),
        )

    # -------- Extraction helper methods --------
    def extract_url(self):
        return self.get_attribute(
            self.soup, "link", attrs={"rel": "canonical"}, attr="href"
        )

    def extract_slug(self):
        og_url = self.get_attribute(
            self.soup, "meta", attrs={"property": "og:url"}, attr="content"
        )
        return og_url.rstrip("/").split("/")[-1] if og_url else None

    def extract_name(self):
        return self.get_text_content(self.soup, "h1", class_="product__title")

    def extract_brand_name(self):
        return self.get_text_content(
            self.soup, "a", attrs={"data-testid": "brand-link"}
        )

    def extract_brand_slug(self):
        brand_url = self.get_attribute(
            self.soup, "a", attrs={"data-testid": "brand-link"}, attr="href"
        )
        return brand_url.rstrip("/").split("/")[-1] if brand_url else None

    def extract_price(self):
        return self.get_text_content(
            self.soup, "span", attrs={"data-testid": "pricing"}
        )

    def extract_price_calc_desc(self):
        return self.get_text_content(
            self.soup, "div", class_="price__calculation_method"
        )

    def extract_image_url(self):
        return self.get_attribute(
            self.soup, "meta", attrs={"property": "og:image"}, attr="content"
        )

    def extract_categories(self):
        return self.get_all_text_content(self.soup, "span", attrs={"itemprop": "name"})

    def extract_tags(self):
        return self.get_all_text_content(
            self.soup.find("ul", class_="dietary-allergen-list"), "li"
        )

    def extract_additional_desc(self):
        return self.get_text_content(
            self.soup, "div", attrs={"data-testid": "read-more-content"}
        )

    def extract_nutritional_info(self):
        table = self.soup.select_one(
            "[data-testid='nutritional-information-panel'] table"
        )
        if not table:
            return {}
        headers = [th.get_text(strip=True) for th in table.select("tr th")[1:]]
        nutritional_info = {}
        for row in table.select("tr")[1:]:
            cells = row.select("th, td")
            nutrient = cells[0].get_text(strip=True)
            values = [cell.get_text(strip=True) for cell in cells[1:]]
            nutritional_info[nutrient] = dict(zip(headers, values))
        return nutritional_info

    def extract_panel_text(self, panel_testid: str):
        raw_text = self.get_text_content(
            self.soup, "div", attrs={"data-testid": panel_testid}
        )
        return self.clean_whitespace(raw_text)

    def extract_text_by_testid(self, name: str, testid: str):
        raw_text = self.get_text_content(self.soup, name, attrs={"data-testid": testid})
        return self.clean_whitespace(raw_text)

    @staticmethod
    def clean_whitespace(text):
        import re

        if text:
            return re.sub(r"\s+", " ", text).strip()
        return None
