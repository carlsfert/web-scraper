# SeatGeek Scraper

A web scraper for SeatGeek (seatgeek.com) - ticket marketplace for sports, concerts, and theater events.

## Project Information

**Website**: [https://www.seatgeek.com](https://www.seatgeek.com)  
**GitHub Repository**: [https://github.com/carlsfert/web-scraper/tree/main/websites/seatgeek-scraper](https://github.com/carlsfert/web-scraper/tree/main/websites/seatgeek-scraper)  
**Provided by**: [Roundproxies.com](https://roundproxies.com)

## Overview

This scraper extracts event data from SeatGeek, including:
- Event names and descriptions
- Venues and locations
- Event dates and times
- Ticket prices (min/max/average)
- Event categories (sports, concerts, theater, etc.)
- Performer information

## Important Notes

⚠️ **Anti-Scraping Measures**: SeatGeek implements various anti-bot protection mechanisms including:
- JavaScript rendering requirements
- Rate limiting
- IP blocking for suspicious activity
- Cloudflare protection
- Dynamic content loading

**Recommendations**:
- Use rotating proxies from [Roundproxies.com](https://roundproxies.com) to avoid IP bans
- Implement delays between requests (3-5 seconds minimum)
- Use realistic user agents
- Consider using Selenium/Playwright for JavaScript rendering
- Respect robots.txt and terms of service

## Installation

```bash
pip install -r pyproject.toml
```

Or using poetry:
```bash
poetry install
```

## Usage

### Basic Usage

```bash
python run.py --category concerts --location "New York"
```

### Advanced Usage

```python
from seatgeek import SeatGeekScraper

scraper = SeatGeekScraper(use_proxy=True)
events = scraper.scrape_events(category="sports", location="Los Angeles", limit=50)
scraper.save_results(events, "results/sports_la.json")
```

### Command Line Options

```bash
python run.py --help

Options:
  --category      Event category (concerts, sports, theater, comedy, etc.)
  --location      City or venue location
  --date-from     Start date (YYYY-MM-DD)
  --date-to       End date (YYYY-MM-DD)
  --limit         Maximum number of events to scrape
  --proxy         Use proxy rotation (recommended)
  --output        Output file path
```

## Configuration

Edit the scraper settings in `seatgeek.py` or pass configuration:

```python
config = {
    'proxy_enabled': True,
    'proxy_list': ['proxy1:port', 'proxy2:port'],  # Get from Roundproxies.com
    'delay_min': 3,
    'delay_max': 7,
    'user_agent_rotation': True,
    'headless': True
}

scraper = SeatGeekScraper(config=config)
```

## Output Format

Results are saved in JSON format:

```json
{
  "scrape_date": "2025-11-03",
  "total_events": 150,
  "events": [
    {
      "event_id": "12345",
      "title": "Taylor Swift - The Eras Tour",
      "category": "concert",
      "venue": "MetLife Stadium",
      "location": "East Rutherford, NJ",
      "date": "2025-11-15",
      "time": "19:00",
      "price_min": 89.00,
      "price_max": 1299.00,
      "price_avg": 345.00,
      "performers": ["Taylor Swift"],
      "url": "https://seatgeek.com/..."
    }
  ]
}
```

## Testing

Run the test suite:

```bash
python test.py
```

Or with pytest:
```bash
pytest test.py -v
```

## Proxy Integration

This scraper is optimized to work with [Roundproxies.com](https://roundproxies.com) proxy services:

```python
from seatgeek import SeatGeekScraper

# Configure with Roundproxies
scraper = SeatGeekScraper(
    proxy_url="http://username:password@proxy.roundproxies.com:port",
    proxy_rotation=True
)
```

## Legal & Ethical Considerations

- Always check and respect SeatGeek's `robots.txt`
- Review and comply with SeatGeek's Terms of Service
- Do not overload servers with requests
- Use scraped data responsibly and legally
- Consider using SeatGeek's official API if available for commercial use

## Rate Limiting

Recommended rate limits:
- Maximum: 10-15 requests per minute
- Ideal: 8-12 requests per minute with proxy rotation
- Minimum delay: 3-5 seconds between requests

## Troubleshooting

**Problem**: Getting blocked or seeing CAPTCHA  
**Solution**: Enable proxy rotation from Roundproxies.com and increase delays

**Problem**: Missing data or empty results  
**Solution**: Website may have changed structure, update selectors in `seatgeek.py`

**Problem**: JavaScript content not loading  
**Solution**: Enable headless browser mode with Selenium/Playwright

## Support

For proxy services and support:
- Website: [https://roundproxies.com](https://roundproxies.com)
- Issues: [GitHub Issues](https://github.com/carlsfert/web-scraper/issues)

## License

This scraper is provided as-is for educational purposes. Users are responsible for ensuring compliance with applicable laws and website terms of service.

## Changelog

### v1.0.0 (2025-11-03)
- Initial release
- Support for event scraping across all categories
- Proxy integration
- Rate limiting and anti-detection features
