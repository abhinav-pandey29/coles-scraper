"""
Models for Coles scrapers.
"""

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional


@dataclass
class ProductTile:
    """
    Model for product tiles found on Coles' **category browsing pages**.
    """

    name: str = field(default="Unknown Product")
    url: str = field(default=None)
    price: Optional[str] = field(default=None)
    price_calc_method: Optional[str] = field(default=None)
    image_url: Optional[str] = field(default=None)
    promotion_type: Optional[str] = field(default=None)

    def __repr__(self):
        repr_string = (
            f"\n{'='*40}\n"
            f"ProductTile:\n"
            f"  Name               : {self.name or 'N/A'}\n"
            f"  URL                : {self.url or 'N/A'}\n"
            f"  Price              : {self.price or 'N/A'}\n"
            f"  Price Calculation  : {self.price_calc_method or 'N/A'}\n"
            f"  Image URL          : {self.image_url or 'N/A'}\n"
            f"  Promotion Type     : {self.promotion_type or 'N/A'}\n"
            f"{'='*40}\n"
        )
        return repr_string

    dict = asdict


@dataclass
class Product:
    """
    Model for product details on Coles' **dedicated product pages**.
    """

    url: str
    slug: str
    name: str = field(default="Unknown Product")
    brand_name: Optional[str] = field(default=None)
    brand_slug: Optional[str] = field(default=None)
    image_url: Optional[str] = None
    price: Optional[str] = None
    price_calc_desc: Optional[str] = None
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    additional_desc: Optional[str] = None
    nutritional_info: Optional[Dict] = None
    ingredients: Optional[str] = None
    allergens: Optional[str] = None
    dietary: Optional[str] = None
    usage_instructions: Optional[str] = None
    storage_instructions: Optional[str] = None
    warnings: Optional[str] = None
    retail_limit: Optional[str] = field(default=None)
    promotional_limit: Optional[str] = field(default=None)
    product_code: Optional[str] = field(default=None)

    def __repr__(self):
        repr_string = (
            f"\n{'='*40}\n"
            f"Product:\n"
            f"  Name               : {self.name or 'N/A'}\n"
            f"  Brand              : {self.brand_name or 'N/A'}\n"
            f"  Brand Slug         : {self.brand_slug or 'N/A'}\n"
            f"  Categories         : {', '.join(self.categories) or 'N/A'}\n"
            f"  Retail Limit       : {self.retail_limit or 'N/A'}\n"
            f"  Promotional Limit  : {self.promotional_limit or 'N/A'}\n"
            f"  Product Code       : {self.product_code or 'N/A'}\n"
            f"{'='*40}\n"
        )
        return repr_string
