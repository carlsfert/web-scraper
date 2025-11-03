# Alibaba Scraper

A robust web scraper for extracting product data from Alibaba.com.

## Overview

This scraper is designed to extract product information from Alibaba.com, including product titles, prices, supplier information, minimum order quantities, and more. 

**Note:** Alibaba.com implements sophisticated anti-scraping measures including:
- Rate limiting
- CAPTCHA challenges
- IP blocking
- JavaScript rendering requirements
- Session validation

**Proxy Usage Recommended:** Due to these protections, using rotating proxies (like those from [Roundproxies.com](https://roundproxies.com)) is highly recommended for reliable scraping at scale.

## Features

- Search products by keyword
- Extract detailed product information
- Handle pagination
- Proxy support (essential for production use)
- Error handling and retry logic
- CSV export functionality

## GitHub Repository

https://github.com/carlsfert/web-scraper/tree/main/websites/alibaba-scraper

## Installation

```bash
pip install -e .
```

## Usage

### Basic Usage

```python
from alibaba import AlibabaScraper

scraper = AlibabaScraper()
results = scraper.search_products("laptop", max_pages=2)
scraper.save_to_csv(results, "results/alibaba_laptops.csv")
```

### With Proxy Support

```python
from alibaba import AlibabaScraper

# Using Roundproxies
proxies = {
    'http': 'http://username:password@proxy.roundproxies.com:port',
    'https': 'http://username:password@proxy.roundproxies.com:port'
}

scraper = AlibabaScraper(proxies=proxies)
results = scraper.search_products("electronics", max_pages=5)
```

### Command Line

```bash
python run.py --keyword "smartphone" --pages 3 --output results/smartphones.csv
```

## Data Extracted

- Product Title
- Price Range
- Supplier Name
- Minimum Order Quantity (MOQ)
- Product URL
- Image URLs
- Product Rating
- Number of Orders
- Shipping Information

## Important Notes

1. **Proxies are Essential**: Alibaba actively blocks scraping attempts. Use rotating residential proxies for best results.
2. **Rate Limiting**: Implement delays between requests (handled automatically).
3. **User-Agent Rotation**: The scraper rotates user agents to avoid detection.
4. **JavaScript Required**: Some content requires JavaScript rendering (Selenium option available).
5. **Terms of Service**: Ensure compliance with Alibaba's Terms of Service when scraping.

## Requirements

- Python 3.8+
- requests
- beautifulsoup4
- lxml
- pandas
- selenium (optional, for JS-heavy pages)

## Testing

```bash
python test.py
```

## Legal Disclaimer

This scraper is for educational purposes. Users are responsible for ensuring their scraping activities comply with:
- Alibaba's Terms of Service
- robots.txt directives
- Local data protection laws (GDPR, CCPA, etc.)
- Rate limiting and respectful scraping practices

Always use proxies and rate limiting to avoid overwhelming the target server.

## Support

For proxy solutions that work reliably with Alibaba, visit [Roundproxies.com](https://roundproxies.com).
