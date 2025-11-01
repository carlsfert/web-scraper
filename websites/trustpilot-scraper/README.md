# Trustpilot Scraper

A production-ready Python scraper for extracting company data, reviews, and ratings from Trustpilot.com. This scraper uses Trustpilot's hidden JSON data structure and private API endpoints for reliable, high-speed data extraction.

## Features

- 🚀 **Fast Extraction**: Direct JSON data access from `__NEXT_DATA__` script tags
- 🔍 **Multiple Search Methods**: Search by keyword, category, or direct company URL
- 📊 **Complete Data Coverage**: Company details, reviews, ratings, verification status
- 🛡️ **Anti-Bot Protection**: Built-in stealth features and proxy rotation support
- ⚡ **Async Processing**: Concurrent scraping with configurable workers
- 💾 **Flexible Storage**: JSONL file output with optional database integration
- 📈 **Performance Monitoring**: Built-in tracking for success rates and response times

## Installation

```bash
pip install -e .
```

## Quick Start

### Basic Usage

```python
import asyncio
from trustpilot import TrustpilotScraper

async def main():
    scraper = TrustpilotScraper()
    
    # Scrape a single company
    reviews = await scraper.scrape_company_reviews("amazon.com", max_pages=5)
    print(f"Scraped {len(reviews)} reviews")
    
    # Search for companies
    companies = await scraper.search_companies("electronics", pages=3)
    print(f"Found {len(companies)} companies")

asyncio.run(main())
```

### Advanced Usage with Proxies

```python
from trustpilot import TrustpilotScraper

proxies = [
    "http://user:pass@proxy1.example.com:8080",
    "http://user:pass@proxy2.example.com:8080",
]

scraper = TrustpilotScraper(proxies=proxies, max_workers=5)
await scraper.scrape_multiple_companies(["amazon.com", "ebay.com", "walmart.com"])
```

## Data Structure

### Company Data

```json
{
  "name": "Company Name",
  "domain": "example.com",
  "trust_score": 4.5,
  "total_reviews": 12500,
  "verified": true,
  "claimed_date": "2020-01-15T00:00:00Z",
  "response_rate": 95.2
}
```

### Review Data

```json
{
  "id": "review-123",
  "company_domain": "example.com",
  "rating": 5,
  "title": "Great service!",
  "content": "Review text here...",
  "author_name": "John D.",
  "verified": true,
  "review_date": "2024-10-15T12:30:00Z",
  "experience_date": "2024-10-10",
  "scraped_date": "2025-11-01T10:00:00Z"
}
```

## Configuration

The scraper can be configured through environment variables or directly in code:

```python
scraper = TrustpilotScraper(
    max_workers=10,           # Concurrent workers
    request_delay=(1, 3),     # Random delay between requests (min, max)
    timeout=30,               # Request timeout in seconds
    max_retries=3,            # Retry attempts for failed requests
    proxies=proxy_list        # List of proxy URLs
)
```

## Command Line Usage

Run the scraper from command line:

```bash
# Scrape a single company
python run.py --company amazon.com --pages 10

# Search and scrape companies
python run.py --search "electronics" --pages 5

# Use category scraping
python run.py --category electronics_technology --pages 10

# With proxies
python run.py --company amazon.com --proxy-file proxies.txt
```

## Anti-Bot Features

This scraper includes several anti-detection features:

- Random user agent rotation
- Request delay randomization
- Proxy rotation support
- Browser fingerprint spoofing
- Referrer header manipulation
- Cookie management
- Rate limiting compliance

## Legal & Ethical Considerations

- Always respect Trustpilot's `robots.txt` and Terms of Service
- Implement rate limiting to avoid overloading their servers (1-2 requests per second per IP)
- Use for legitimate purposes only (market research, sentiment analysis, etc.)
- Consider using [RoundProxies](https://roundproxies.com) residential proxies for large-scale scraping
- Store data responsibly and comply with GDPR/data protection regulations

## Troubleshooting

### 429 Too Many Requests

If you encounter rate limiting:
- Reduce concurrent workers
- Increase delay between requests
- Use residential proxies
- Implement exponential backoff

### Empty Results

- Check if the company domain is correct
- Verify the company exists on Trustpilot
- Ensure you're not blocked (check response status codes)
- Update the scraper if Trustpilot changed their structure

## Performance Tips

- Start with 5 workers and scale gradually
- Use residential proxies for large-scale scraping
- Monitor success rates (should stay above 80%)
- Keep average response times below 5 seconds
- Implement proper error handling and logging

## Contributing

Contributions are welcome! Please ensure:
- Code follows PEP 8 style guidelines
- All tests pass (`pytest test.py`)
- New features include tests
- Documentation is updated

## Disclaimer

This tool is for educational and research purposes. Users are responsible for ensuring their use complies with Trustpilot's Terms of Service and applicable laws. The authors are not responsible for misuse of this software.

## Links

- [Blog Post Tutorial](https://roundproxies.com/blog/trustpilot-scraper/)
- [RoundProxies Homepage](https://roundproxies.com)
- [GitHub Repository](https://github.com/carlsfert/web-scraper/tree/main/websites/trustpilot-scraper)

## License

MIT License - see LICENSE file for details
