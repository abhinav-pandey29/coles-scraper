# Coles Scraper

Coles Scraper is a collection of web scraping utilities designed to automate the extraction of product details from the [Coles](https://www.coles.com.au/) website using Selenium and request-based approaches.

**Disclaimer**: This is a hobby project for my personal portfolio. Please scrape responsibly and adhere to website terms of service.

## Setup

```sh
git clone https://github.com/abhinav-pandey29/coles-scraper.git
cd coles-scraper
python3 -m venv env && env\Scripts\activate # or source env/bin/activate on Mac
pip install -r requirements.txt
```

## Core Components

- [ColesProductTileExtractor](#colesproducttileextractor)
- [ColesProductExtractor](#colesproductextractor)
- [ColesPageFetcher](#colespagefetcher)

### ColesProductTileExtractor

For extracting product data from category browsing pages, with URLs like `https://www.coles.com.au/browse/<category>` or `https://www.coles.com.au/browse/<category>?page=<page_number>`

Examples:

- `https://www.coles.com.au/browse/fruit-vegetables`
- `https://www.coles.com.au/browse/pantry?page=2`
- `https://www.coles.com.au/browse/dairy-eggs-fridge?page=4`

#### Supported categories include:

- `fruit-vegetables`
- `dairy-eggs-fridge`
- `pantry`
- `meat-seafood`
- `bakery`
- `frozen`
- `household`
- `health-beauty`
- `deli`
- `pet`
- `baby`
- `liquor`

Usage example:

```python
from src.extractors import ColesProductTileExtractor

# Obtain HTML content via your preferred method
html_content = ...

# Create extractor instance and extract products
extractor = ColesProductTileExtractor(html_content)
products = extractor.extract()

# Each product contains fields like name, url, price, etc.
for product in products:
    print(product.dict())
```

Example output:

```json
{
  "name": "Coles Bananas | approx 170g",
  "url": "/product/coles-bananas-approx.-170g-409499",
  "price": "$0.68",
  "price_calc_method": "$4.00 per 1kg",
  "image_url": "/next/image?url=https%3A%2F%2Fproductimages.coles.com.au%2F409499.jpg&w=640&q=90"
}
```

### ColesProductExtractor

For extracting detailed information from product pages, with URLs like `https://www.coles.com.au/product/<product-id>`

Examples:

- `https://www.coles.com.au/product/appy-fizz-250ml-8060378`
- `https://www.coles.com.au/product/coles-bananas-approx-170g-409499`

Usage example:

```python
from src.extractors import ColesProductExtractor

# Obtain HTML content for a product page
html_content = ...

# Create extractor instance and get product details
extractor = ColesProductExtractor(html_content)
product = extractor.extract()

print(product.dict())
```

Example output:

```json
{
  "name": "Appy Fizz | 250mL",
  "brand_name": "Appy",
  "brand_url": "/brands/appy-4039743300",
  "categories": [
    "Home",
    "All categories",
    "Pantry",
    "International foods",
    "Indian"
  ],
  "retail_limit": "Retail limit: 20",
  "promotional_limit": "Promotional limit: 12",
  "product_code": "Code: 8060378"
}
```

### ColesPageFetcher

For managing requests with automatic cookie refresh and bot detection handling:

```python
from src.fetcher import ColesPageFetcher

# Initialize fetcher with optional custom headers
fetcher = ColesPageFetcher()

# Fetch pages with automatic cookie management
browse_response = fetcher.get("https://www.coles.com.au/browse/fruit-vegetables")
product_response = fetcher.get("https://www.coles.com.au/product/appy-fizz-250ml-8060378")
```

## Scripts

The project includes several utility scripts in the `scripts/` directory:

- [`scrape_products.py`](scripts/scrape_products.py): Script to scrape all products from specified categories.
- [`scrape_categories.py`](scripts/scrape_categories.py): Script to scrape available product categories.
- [`save_product_page_html.py`](scripts/save_product_page_html.py): Script to save individual product page HTML content.

## Data Storage

Scraped data is stored in the following structure:

- `data/raw/`: Raw scraped data
- `data/processed/`: Cleaned and processed data
- `data/archive/`: Historical data for tracking changes
