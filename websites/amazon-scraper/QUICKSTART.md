# Amazon Scraper - Quick Start Guide

## 🎯 What This Does

A powerful Amazon web scraper that extracts:
- ✅ Product search results
- ✅ Detailed product information
- ✅ Customer reviews and ratings
- ✅ Product specifications and images
- ✅ Pricing and availability

## 📦 5-Minute Setup

### 1. Install Python Dependencies

```bash
cd amazon-scraper
pip install -r requirements.txt
```

### 2. Install Playwright Browser

```bash
playwright install chromium
```

### 3. Run the Demo

```bash
python run.py
```

That's it! The scraper will:
1. Search for "wireless headphones"
2. Get details for the top product
3. Fetch 5 customer reviews
4. Save everything to `outputs/` folder

## 🎨 What You Get

After running, check the `outputs/` directory for:

- `search_results.json` - List of products with prices, ratings
- `product_details.json` - Full product info with specs, images
- `product_reviews.json` - Customer reviews with ratings

## 💻 Basic Usage

### Search Products

```python
import asyncio
from src.amazon_scraper import AmazonScraper

async def main():
    async with AmazonScraper(domain='com') as scraper:
        results = await scraper.search_products(
            query='laptop',
            max_pages=1,
            max_results=10
        )
        print(f"Found {len(results)} products")

asyncio.run(main())
```

### Get Product Details

```python
import asyncio
from src.amazon_scraper import AmazonScraper

async def main():
    async with AmazonScraper(domain='com') as scraper:
        # Replace with any Amazon ASIN
        product = await scraper.get_product_details('B08N5WRWNW')
        print(f"Title: {product['title']}")
        print(f"Price: {product['price']}")
        print(f"Rating: {product['rating']}")

asyncio.run(main())
```

### Get Reviews

```python
import asyncio
from src.amazon_scraper import AmazonScraper

async def main():
    async with AmazonScraper(domain='com') as scraper:
        reviews = await scraper.get_product_reviews(
            asin='B08N5WRWNW',
            max_pages=2
        )
        print(f"Found {len(reviews)} reviews")

asyncio.run(main())
```

## 🌍 Use Different Amazon Sites

Just change the domain:

```python
# Amazon UK
async with AmazonScraper(domain='co.uk') as scraper:
    results = await scraper.search_products('book')

# Amazon Germany
async with AmazonScraper(domain='de') as scraper:
    results = await scraper.search_products('buch')

# Amazon Japan
async with AmazonScraper(domain='co.jp') as scraper:
    results = await scraper.search_products('本')
```

## 📁 Project Structure

```
amazon-scraper/
├── src/
│   ├── amazon_scraper.py    # Main scraper
│   └── utils.py             # Helper functions
├── config/
│   └── settings.py          # Configuration
├── tests/
│   └── test_scraper.py      # Tests
├── outputs/                 # Scraped data goes here
├── run.py                   # Example script
└── requirements.txt         # Dependencies
```

## 🧪 Run Tests

```bash
# All tests
pytest tests/test_scraper.py -v

# Specific tests
pytest tests/test_scraper.py -k test_search_products
pytest tests/test_scraper.py -k test_get_product_details
pytest tests/test_scraper.py -k test_get_product_reviews
```

## 🔧 Configuration

Edit `config/settings.py` to change:
- Default Amazon domain
- Browser headless mode
- Scraping delays
- Output directory
- Max pages/results

## 💡 Tips

### Find Product ASIN

The ASIN is in the Amazon URL:
```
https://www.amazon.com/dp/B08N5WRWNW
                         ^^^^^^^^^^
                         This is the ASIN
```

### Save Data

```python
from src.utils import save_to_json, save_to_csv

# Save as JSON
save_to_json(results, 'my_data.json', 'outputs')

# Save as CSV
save_to_csv(results, 'my_data.csv', 'outputs')
```

### Avoid Getting Blocked

- Add delays: Set `DELAY_BETWEEN_REQUESTS` in config
- Don't scrape too aggressively
- Use reasonable limits for pages/results
- Respect Amazon's terms of service

## 🐛 Troubleshooting

**Problem**: Can't install Playwright
```bash
# Solution
pip install playwright --force-reinstall
playwright install chromium
```

**Problem**: Scraper not finding products
- Check your internet connection
- Try with `headless=False` to see the browser
- Amazon might have changed their HTML (update selectors)

**Problem**: Getting CAPTCHA
- Reduce scraping frequency
- Add longer delays
- Stop and try again later

## 📖 More Info

- Full documentation: See `README.md`
- Example outputs: Check `outputs/` folder
- API details: Look at `src/amazon_scraper.py`

## ⚠️ Important

- This is for educational/personal use only
- Respect Amazon's terms of service
- Don't use for commercial purposes without permission
- Always scrape responsibly with delays

## 🚀 You're Ready!

Start scraping with:
```bash
python run.py
```

Or write your own script using the examples above!

Happy scraping! 🎉
