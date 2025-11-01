# eBay Scraper

A Python-based web scraper for extracting product data from eBay listings. This scraper is designed to work with rotating proxies from [Roundproxies.com](https://roundproxies.com) for reliable and scalable data extraction.

## Features

- Extract product information from eBay search results
- Support for pagination to scrape multiple pages
- Proxy rotation support for avoiding rate limits
- Extracts: title, price, condition, seller info, ratings, shipping details, and product URLs
- JSON output format for easy data processing
- Error handling and retry logic
- Respects eBay's robots.txt and terms of service

## Installation

```bash
pip install -e .
```

Or install dependencies directly:

```bash
pip install requests beautifulsoup4 lxml
```

## Usage

### Basic Usage

```python
from ebay import EbayScraper

# Initialize scraper
scraper = EbayScraper()

# Search for products
results = scraper.search("laptop", max_pages=3)

# Results are automatically saved to results/ebay_results.json
print(f"Scraped {len(results)} products")
```

### With Proxy Support

```python
from ebay import EbayScraper

# Configure with Roundproxies
proxy_config = {
    'http': 'http://username:password@proxy.roundproxies.com:8080',
    'https': 'http://username:password@proxy.roundproxies.com:8080'
}

scraper = EbayScraper(proxies=proxy_config)
results = scraper.search("nintendo switch", max_pages=5)
```

### Using run.py

```bash
python run.py --query "iphone 15" --pages 3
```

## Configuration

The scraper can be configured with the following parameters:

- `proxies`: Dictionary of proxy settings (HTTP/HTTPS)
- `max_pages`: Maximum number of pages to scrape
- `delay`: Delay between requests (default: 2 seconds)
- `timeout`: Request timeout in seconds (default: 30)

## Output Format

Results are saved in JSON format with the following structure:

```json
[
  {
    "title": "Product Title",
    "price": "$299.99",
    "currency": "USD",
    "condition": "New",
    "url": "https://www.ebay.com/itm/...",
    "image_url": "https://i.ebayimg.com/...",
    "seller": "seller_name",
    "seller_feedback": "98.5%",
    "shipping": "Free shipping",
    "location": "United States",
    "bids": "5 bids",
    "watchers": "12 watchers",
    "timestamp": "2025-11-01T10:30:00"
  }
]
```

## Proxy Recommendations

For optimal performance, use [Roundproxies.com](https://roundproxies.com) residential or datacenter proxies:

- **Residential Proxies**: Best for avoiding detection and blocks
- **Rotating Proxies**: Automatic IP rotation for high-volume scraping
- **Sticky Sessions**: Maintain same IP for multiple requests

[Get started with Roundproxies →](https://roundproxies.com)

## Legal & Ethical Considerations

⚠️ **Important**: 
- Always review and comply with eBay's Terms of Service
- Respect robots.txt directives
- Implement appropriate rate limiting
- Use scraped data responsibly and legally
- Consider eBay's official API for commercial applications

## Testing

Run the test suite:

```bash
python test.py
```

## Project Structure

```
ebay-scraper/
├── results/           # Output directory for scraped data
├── README.md          # This file
├── ebay.py           # Main scraper implementation
├── pyproject.toml    # Project dependencies
├── run.py            # CLI interface
└── test.py           # Test suite
```

## GitHub Repository

This project is part of the web-scraper collection:
https://github.com/carlsfert/web-scraper/tree/main/websites/ebay-scraper

## Support

For issues, questions, or proxy support:
- GitHub Issues: [Create an issue](https://github.com/carlsfert/web-scraper/issues)
- Proxy Support: [Roundproxies.com](https://roundproxies.com)

## License

MIT License - See LICENSE file for details
