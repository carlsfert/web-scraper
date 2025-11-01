# Product Hunt Scraper

This scraper uses **Playwright** and Python to scrape product data from Product Hunt.

Full tutorial **[How to Scrape Product Hunt](https://roundproxies.com/blog/scrape-product-hunt/)**

The scraping code is located in the `producthunt.py` file. It's fully documented and simplified for educational purposes, and the example scraper run code can be found in `run.py` file.

## What This Scraper Does

This scraper scrapes:
* **Product Hunt daily products** - Today's featured launches from the homepage
* **Product Hunt product details** - Comprehensive information including makers, descriptions, upvotes, comments, and topics
* **Product Hunt search** - Search results for any query
* **Product Hunt historical archives** - Products from any past date

For output examples, see the `./results` directory.

## Features

- ✅ Scrapes daily product listings from homepage
- ✅ Extracts detailed product information (name, tagline, description, makers, upvotes, comments)
- ✅ Searches for products by keyword
- ✅ Accesses historical archive data from any date
- ✅ Uses Playwright for JavaScript rendering
- ✅ Implements anti-detection measures
- ✅ Includes comprehensive test suite
- ✅ Exports data to JSON format

## Fair Use Disclaimer

Note that this code is provided free of charge as is, and Roundproxies does not provide free web scraping support or consultation. For any bugs, see the issue tracker.

## Setup and Use

This Product Hunt scraper uses **Python 3.10+** with **Playwright** for browser automation and Beautiful Soup for HTML parsing.

### Prerequisites

1. Ensure you have **Python 3.10+** and **poetry Python package manager** on your system.
2. Install Poetry if you haven't already:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

### Installation

1. Clone and install Python environment:

```bash
poetry install
```

2. Install Playwright browsers:

```bash
poetry run playwright install chromium
```

### Running the Scraper

Run the example scraper:

```bash
poetry run python run.py
```

This will:
1. Scrape today's products (limited to 5 for demo)
2. Extract detailed information for the first product
3. Search for AI-related products
4. Scrape products from 7 days ago

### Running Tests

Run all tests:

```bash
poetry install --with dev
poetry run pytest test.py
```

Run specific test categories:

```bash
# Test daily product scraping
poetry run pytest test.py -k test_daily_scraping

# Test individual product scraping
poetry run pytest test.py -k test_product_scraping

# Test search functionality
poetry run pytest test.py -k test_search_scraping

# Test archive scraping
poetry run pytest test.py -k test_archive_scraping

# Test data consistency
poetry run pytest test.py -k test_data_consistency
```

## Usage Examples

### Scrape Today's Products

```python
import asyncio
from producthunt import scrape_daily_products

async def main():
    # Scrape all products from today
    products = await scrape_daily_products()
    
    # Or limit to first 10
    products = await scrape_daily_products(max_products=10)
    
    for product in products:
        print(f"{product['name']} - {product['upvotes']} upvotes")
        print(f"  {product['tagline']}")
        print(f"  {product['url']}\n")

asyncio.run(main())
```

### Scrape Product Details

```python
import asyncio
from producthunt import scrape_product

async def main():
    url = "https://www.producthunt.com/posts/your-product"
    product = await scrape_product(url)
    
    print(f"Name: {product['name']}")
    print(f"Description: {product['description']}")
    print(f"Upvotes: {product['upvotes']}")
    print(f"Comments: {product['comments']}")
    print(f"Makers: {', '.join([m['name'] for m in product['makers']])}")
    print(f"Website: {product['website']}")
    print(f"Topics: {', '.join(product['topics'])}")

asyncio.run(main())
```

### Search for Products

```python
import asyncio
from producthunt import scrape_search

async def main():
    # Search for AI products
    results = await scrape_search("AI", max_results=20)
    
    for result in results:
        print(f"{result['name']} - {result['upvotes']} upvotes")
        print(f"  {result['tagline']}\n")

asyncio.run(main())
```

### Scrape Historical Archive

```python
import asyncio
from datetime import datetime
from producthunt import scrape_archive

async def main():
    # Scrape products from a specific date
    date = datetime(2024, 1, 15)
    products = await scrape_archive(date, max_products=10)
    
    for product in products:
        print(f"{product['name']} - {product['upvotes']} upvotes")
        print(f"  Date: {product['date']}")
        print(f"  {product['url']}\n")

asyncio.run(main())
```

### Scrape Multiple Dates

```python
import asyncio
from datetime import datetime, timedelta
from producthunt import scrape_archive

async def main():
    # Scrape last 7 days
    start_date = datetime.now() - timedelta(days=7)
    
    all_products = []
    for i in range(7):
        date = start_date + timedelta(days=i)
        print(f"Scraping {date.strftime('%Y-%m-%d')}...")
        
        products = await scrape_archive(date, max_products=5)
        all_products.extend(products)
        
        # Be respectful with delays
        await asyncio.sleep(3)
    
    print(f"\nTotal products scraped: {len(all_products)}")

asyncio.run(main())
```

## Output Format

### Daily Products

```json
[
  {
    "name": "Product Name",
    "tagline": "Short description of the product",
    "upvotes": "342",
    "url": "https://www.producthunt.com/posts/product-name"
  }
]
```

### Product Details

```json
{
  "name": "Product Name",
  "tagline": "Short description",
  "description": "Full product description with details...",
  "upvotes": "342",
  "comments": "28",
  "makers": [
    {
      "name": "Maker Name",
      "profile_url": "https://www.producthunt.com/@username"
    }
  ],
  "website": "https://example.com",
  "topics": ["Productivity", "Design", "AI"],
  "url": "https://www.producthunt.com/posts/product-name"
}
```

### Search Results

```json
[
  {
    "name": "AI Product",
    "tagline": "Revolutionary AI tool",
    "upvotes": "156",
    "url": "https://www.producthunt.com/posts/ai-product",
    "search_query": "AI"
  }
]
```

### Archive Products

```json
[
  {
    "name": "Historical Product",
    "tagline": "Product from the past",
    "upvotes": "89",
    "url": "https://www.producthunt.com/posts/historical-product",
    "date": "2024-01-15"
  }
]
```

## Anti-Detection Features

This scraper implements several anti-detection techniques:

- **Custom User-Agent**: Mimics real browsers
- **Viewport Configuration**: Sets realistic screen dimensions
- **Navigation Properties**: Hides automation signals (webdriver, plugins, languages)
- **Human-like Delays**: Includes delays between requests
- **Browser Arguments**: Disables automation control features

## Rate Limiting & Best Practices

To use this scraper responsibly:

- ✅ Add delays between requests (2-3 seconds minimum)
- ✅ Respect Product Hunt's terms of service
- ✅ Use the scraper for legitimate purposes (research, analysis, personal projects)
- ✅ Don't overwhelm the servers with concurrent requests
- ✅ Consider using Product Hunt's official API for commercial use

## Troubleshooting

### Playwright Installation Issues

If you encounter issues installing Playwright browsers:

```bash
# Install browsers manually
poetry run playwright install chromium

# Or install all browsers
poetry run playwright install
```

### Import Errors

Make sure all dependencies are installed:

```bash
poetry install
```

### Selectors Not Working

Product Hunt may update their HTML structure. If selectors break:

1. Inspect the page in a browser
2. Update the CSS selectors in `producthunt.py`
3. Look for `data-test` attributes as they're more stable

### TimeoutError

If you get timeout errors:

- Increase the timeout values in `producthunt.py`
- Check your internet connection
- Product Hunt might be temporarily down

## Project Structure

```
producthunt-scraper/
├── producthunt.py       # Main scraping logic
├── run.py              # Example usage script
├── test.py             # Test suite
├── pyproject.toml      # Dependencies and configuration
├── README.md           # This file
└── results/            # Output directory for scraped data
    ├── daily_products.json
    ├── product_details.json
    ├── search_results.json
    └── archive_products.json
```

## Dependencies

- **playwright** - Browser automation
- **beautifulsoup4** - HTML parsing
- **lxml** - Fast XML/HTML parser
- **pytest** - Testing framework (dev dependency)
- **pytest-asyncio** - Async test support (dev dependency)

## License

MIT License - Feel free to use this code for your projects.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Support

For issues or questions:

- Check the [issue tracker](https://github.com/scrapfly/scrapfly-scrapers/issues)
- Review Product Hunt's structure for selector changes
- Consult the [Playwright documentation](https://playwright.dev/python/)

## Disclaimer

This scraper is for educational purposes. Always respect website terms of service and robots.txt. Use responsibly and consider rate limiting to avoid overloading servers.
