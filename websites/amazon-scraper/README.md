# Amazon Scraper

A comprehensive web scraper for Amazon product data built with Python and Playwright. Extract product information, search results, reviews, and more from Amazon's marketplace.

## 🚀 Features

- **Product Search**: Search Amazon and extract product listings with prices, ratings, and reviews
- **Product Details**: Get comprehensive product information including descriptions, specifications, images, and categories
- **Product Reviews**: Extract customer reviews with ratings, text, reviewer info, and verification status
- **Multi-Domain Support**: Works with Amazon sites worldwide (US, UK, Germany, France, etc.)
- **Anti-Detection**: Built-in measures to avoid bot detection
- **Async/Await**: Fast, efficient scraping using asynchronous operations
- **Export Options**: Save data as JSON or CSV
- **Utility Functions**: Helper functions for data cleaning and formatting

## 📋 Requirements

- Python 3.10 or higher
- Playwright (automatically installs Chromium)
- BeautifulSoup4 for HTML parsing
- Additional dependencies in `requirements.txt`

## 🔧 Installation

### 1. Clone the repository

```bash
git clone https://github.com/carlsfert/amazon-scraper.git
cd amazon-scraper
```

### 2. Create virtual environment (recommended)

```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright browsers

```bash
playwright install chromium
```

## 🎯 Quick Start

### Run the demo script

```bash
python run.py
```

This will:
1. Search for "wireless headphones" on Amazon
2. Get detailed information for the first product
3. Fetch reviews for that product
4. Save all data to the `outputs/` directory

## 📚 Usage Examples

### Search for Products

```python
import asyncio
from src.amazon_scraper import AmazonScraper

async def search_example():
    async with AmazonScraper(domain='com', headless=True) as scraper:
        results = await scraper.search_products(
            query='laptop',
            max_pages=2,
            max_results=20
        )
        
        for product in results:
            print(f"{product['title']}")
            print(f"Price: {product['price']}")
            print(f"Rating: {product['rating']} ({product['reviews_count']} reviews)")
            print(f"ASIN: {product['asin']}\n")

asyncio.run(search_example())
```

### Get Product Details

```python
import asyncio
from src.amazon_scraper import AmazonScraper

async def product_details_example():
    async with AmazonScraper(domain='com') as scraper:
        # Get details for a specific product
        product = await scraper.get_product_details('B08N5WRWNW')
        
        print(f"Title: {product['title']}")
        print(f"Brand: {product['brand']}")
        print(f"Price: {product['price']}")
        print(f"Rating: {product['rating']}")
        print(f"Availability: {product['availability']}")
        print(f"\nDescription: {product['description'][:200]}...")
        print(f"\nCategories: {', '.join(product['categories'])}")
        print(f"Images: {len(product['images'])} available")
        print(f"Specifications: {len(product['specifications'])} items")

asyncio.run(product_details_example())
```

### Get Product Reviews

```python
import asyncio
from src.amazon_scraper import AmazonScraper

async def reviews_example():
    async with AmazonScraper(domain='com') as scraper:
        reviews = await scraper.get_product_reviews(
            asin='B08N5WRWNW',
            max_pages=3,
            max_reviews=50
        )
        
        for review in reviews:
            print(f"Rating: {review['rating']}/5")
            print(f"Title: {review['title']}")
            print(f"Reviewer: {review['reviewer']}")
            print(f"Verified: {review['verified_purchase']}")
            print(f"Text: {review['text'][:150]}...\n")

asyncio.run(reviews_example())
```

### Use Different Amazon Domains

```python
import asyncio
from src.amazon_scraper import AmazonScraper

async def multi_domain_example():
    # Amazon UK
    async with AmazonScraper(domain='co.uk') as scraper:
        uk_results = await scraper.search_products('book', max_results=5)
    
    # Amazon Germany
    async with AmazonScraper(domain='de') as scraper:
        de_results = await scraper.search_products('buch', max_results=5)
    
    # Amazon Japan
    async with AmazonScraper(domain='co.jp') as scraper:
        jp_results = await scraper.search_products('本', max_results=5)

asyncio.run(multi_domain_example())
```

### Save Data to Files

```python
import asyncio
from src.amazon_scraper import AmazonScraper
from src.utils import save_to_json, save_to_csv

async def save_data_example():
    async with AmazonScraper(domain='com') as scraper:
        results = await scraper.search_products('keyboard', max_results=10)
        
        # Save as JSON
        save_to_json(results, 'keyboards.json', 'outputs')
        
        # Save as CSV
        save_to_csv(results, 'keyboards.csv', 'outputs')

asyncio.run(save_data_example())
```

## 📁 Project Structure

```
amazon-scraper/
├── src/
│   ├── amazon_scraper.py      # Main scraper class
│   └── utils.py               # Utility functions
├── config/
│   └── settings.py            # Configuration settings
├── tests/
│   └── test_scraper.py        # Test suite
├── outputs/                   # Output directory for scraped data
│   ├── search_results.json
│   ├── product_details.json
│   └── product_reviews.json
├── run.py                     # Demo/example script
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest tests/test_scraper.py -v

# Run specific tests
pytest tests/test_scraper.py -k test_search_products
pytest tests/test_scraper.py -k test_get_product_details
pytest tests/test_scraper.py -k test_get_product_reviews

# Run utility function tests
pytest tests/test_scraper.py -k test_clean_price
pytest tests/test_scraper.py -k test_validate_asin
```

## 🛠️ Configuration

Edit `config/settings.py` to customize:

- Amazon domains
- Browser settings (headless mode, timeout)
- Scraping limits (max pages, max results)
- Delays between requests
- User agents for rotation
- Output formats and directories
- Logging settings

## 📊 Output Format

### Search Results

```json
{
  "asin": "B08N5WRWNW",
  "title": "Product Title",
  "price": "$348.00",
  "rating": "4.7",
  "reviews_count": "89,234",
  "image_url": "https://...",
  "url": "https://www.amazon.com/dp/B08N5WRWNW",
  "search_query": "wireless headphones"
}
```

### Product Details

```json
{
  "asin": "B08N5WRWNW",
  "title": "Product Title",
  "price": "$348.00",
  "rating": "4.7",
  "reviews_count": "89,234",
  "description": "Full product description...",
  "brand": "Sony",
  "availability": "In Stock",
  "images": ["url1", "url2", "url3"],
  "categories": ["Electronics", "Headphones"],
  "specifications": {
    "Brand": "Sony",
    "Model": "WH-1000XM4"
  },
  "url": "https://www.amazon.com/dp/B08N5WRWNW"
}
```

### Product Reviews

```json
{
  "review_id": "R3OZQKV7J8HMKP",
  "rating": "5.0",
  "title": "Review Title",
  "text": "Review text...",
  "reviewer": "John Smith",
  "date": "October 15, 2025",
  "verified_purchase": true,
  "helpful_count": "1,234 people found this helpful",
  "asin": "B08N5WRWNW"
}
```

## 🛡️ Anti-Detection Features

The scraper includes several anti-detection measures:

- **Realistic User-Agents**: Rotates between multiple browser user-agents
- **Browser Fingerprinting**: Hides automation signals (webdriver, plugins)
- **Human-like Delays**: Adds delays between requests
- **Realistic Viewport**: Sets proper screen dimensions
- **Chrome Runtime**: Adds chrome object to appear as regular browser

## ⚠️ Important Notes

### Legal & Ethical Considerations

- **Terms of Service**: Web scraping may violate Amazon's Terms of Service
- **Personal Use**: This tool is for educational and personal research purposes
- **Rate Limiting**: Always implement delays between requests
- **Respectful Scraping**: Don't overload Amazon's servers
- **Data Usage**: Respect copyright and don't republish scraped data commercially

### Limitations

- Amazon actively works to prevent scraping - expect occasional failures
- CAPTCHA challenges may appear with excessive requests
- Selectors may break if Amazon updates their HTML structure
- Some products may have limited or no data available
- Review counts and availability may not always be accurate

## 🔍 Troubleshooting

### Playwright Installation Issues

```bash
# Reinstall Playwright browsers
playwright install --force chromium

# Or install all browsers
playwright install
```

### Import Errors

```bash
# Make sure you're in the project directory
cd amazon-scraper

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Scraper Not Finding Products

- Check if Amazon is accessible from your network
- Try running with `headless=False` to see the browser
- Increase timeout values in `config/settings.py`
- Amazon may have updated their HTML structure - inspect and update selectors

### CAPTCHA Challenges

- Reduce scraping frequency
- Add longer delays between requests
- Use the scraper less aggressively
- Consider using Amazon's official API for commercial use

## 🌍 Supported Amazon Domains

- **US**: amazon.com
- **UK**: amazon.co.uk
- **Germany**: amazon.de
- **France**: amazon.fr
- **Italy**: amazon.it
- **Spain**: amazon.es
- **Canada**: amazon.ca
- **Japan**: amazon.co.jp
- **India**: amazon.in
- **Mexico**: amazon.com.mx
- **Australia**: amazon.com.au

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚖️ Disclaimer

This tool is provided for educational purposes only. The authors are not responsible for any misuse of this software. Always respect website terms of service and robots.txt files. Use at your own risk.

## 🙏 Acknowledgments

- Built with [Playwright](https://playwright.dev/)
- HTML parsing by [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)
- Inspired by the web scraping community

## 📧 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the troubleshooting section

---

**Happy Scraping! 🎉**

*Remember to scrape responsibly and respect Amazon's terms of service.*
