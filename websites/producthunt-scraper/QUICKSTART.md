# Product Hunt Scraper - Quick Start Guide

## 🚀 What You Got

A complete Product Hunt scraper with the same structure as the AliExpress scraper example. This scraper can extract:

- ✅ Daily product listings
- ✅ Detailed product information
- ✅ Search results
- ✅ Historical archive data

## 📁 Project Structure

```
producthunt-scraper/
├── producthunt.py              # Main scraping logic (5 functions)
├── run.py                      # Example usage script
├── test.py                     # Complete test suite
├── pyproject.toml              # Dependencies & config
├── README.md                   # Full documentation
├── LICENSE                     # MIT License
├── .gitignore                  # Git ignore rules
└── results/                    # Example output files
    ├── daily_products.json
    ├── product_details.json
    ├── search_results.json
    └── archive_products.json
```

## ⚡ Quick Setup (5 steps)

1. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Navigate to the project**:
   ```bash
   cd producthunt-scraper
   ```

3. **Install dependencies**:
   ```bash
   poetry install
   ```

4. **Install Playwright browsers**:
   ```bash
   poetry run playwright install chromium
   ```

5. **Run the scraper**:
   ```bash
   poetry run python run.py
   ```

## 🎯 What the Scraper Does

When you run `poetry run python run.py`, it will:

1. Scrape 5 products from today's homepage
2. Get detailed info for the first product
3. Search for "AI" products (5 results)
4. Scrape products from 7 days ago (5 results)
5. Save everything to JSON files in `./results/`

## 📝 Available Functions

### 1. Scrape Daily Products
```python
from producthunt import scrape_daily_products

products = await scrape_daily_products(max_products=10)
```

### 2. Scrape Product Details
```python
from producthunt import scrape_product

product = await scrape_product("https://www.producthunt.com/posts/product-name")
```

### 3. Search Products
```python
from producthunt import scrape_search

results = await scrape_search("AI", max_results=20)
```

### 4. Scrape Archive
```python
from datetime import datetime
from producthunt import scrape_archive

products = await scrape_archive(datetime(2025, 1, 15), max_products=10)
```

## 🧪 Running Tests

Run all tests:
```bash
poetry run pytest test.py
```

Run specific tests:
```bash
poetry run pytest test.py -k test_daily_scraping
poetry run pytest test.py -k test_product_scraping
poetry run pytest test.py -k test_search_scraping
poetry run pytest test.py -k test_archive_scraping
```

## 📊 Output Format

All scraped data is saved as JSON files in the `./results/` directory. See the example files included!

## ⚠️ Important Notes

1. **Rate Limiting**: The scraper includes 2-3 second delays between requests
2. **Respect ToS**: Use responsibly and respect Product Hunt's terms of service
3. **Anti-Detection**: Includes user-agent rotation and browser automation hiding
4. **Dependencies**: Requires Python 3.10+ and Playwright

## 🐛 Troubleshooting

**Issue**: Playwright installation fails
```bash
# Solution: Install browsers manually
poetry run playwright install
```

**Issue**: Selectors not working
- Product Hunt may have updated their HTML
- Check and update CSS selectors in `producthunt.py`
- Look for `data-test` attributes (more stable)

**Issue**: Timeout errors
- Increase timeout values in the code
- Check your internet connection
- Product Hunt might be experiencing issues

## 📚 Learn More

- See `README.md` for complete documentation
- Check `producthunt.py` for detailed code comments
- Review `test.py` for usage examples
- Examine `results/*.json` for output examples

## 🎉 Ready to Go!

You now have a fully functional Product Hunt scraper. Start with:

```bash
poetry run python run.py
```

And watch it scrape Product Hunt data into JSON files!

Happy scraping! 🚀
