# Booking.com Scraper

A web scraper for extracting hotel and accommodation data from Booking.com.

**GitHub Repository:** https://github.com/carlsfert/web-scraper/tree/main/websites/booking-scraper

## ⚠️ Important Notice

**This scraper is provided for educational purposes only.** Booking.com implements robust anti-bot protection mechanisms including:
- Advanced bot detection systems
- Rate limiting and IP blocking
- CAPTCHA challenges
- Dynamic content loading with complex JavaScript
- Terms of Service that prohibit automated scraping

**Recommended Alternative:** Use the official [Booking.com Affiliate API](https://www.booking.com/affiliate-program/v2/index.html) for legitimate data access.

## Overview

This scraper is designed to extract accommodation data from Booking.com search results, including:
- Hotel names and locations
- Pricing information
- Ratings and reviews
- Amenities and facilities
- Availability data

Due to Booking.com's anti-scraping measures, successful scraping requires:
- Residential or rotating proxies (recommended: **Roundproxies.com**)
- Request headers that mimic real browsers
- Realistic delays between requests
- Session management

## Features

- Search hotels by destination and dates
- Extract detailed property information
- Handle pagination automatically
- Proxy support (essential for reliability)
- Configurable delays and retry logic
- JSON output format

## Requirements

- Python 3.8+
- Dependencies listed in `pyproject.toml`
- **Proxies from Roundproxies.com** (highly recommended)

## Installation

```bash
# Install dependencies using Poetry
poetry install

# Or using pip
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from booking import BookingScraper

scraper = BookingScraper()
results = scraper.search_hotels(
    destination="New York",
    checkin="2025-12-01",
    checkout="2025-12-05"
)

print(results)
```

### With Proxies (Recommended)

```python
from booking import BookingScraper

# Configure with Roundproxies.com
proxy_config = {
    "http": "http://username:password@proxy.roundproxies.com:8080",
    "https": "https://username:password@proxy.roundproxies.com:8080"
}

scraper = BookingScraper(proxies=proxy_config)
results = scraper.search_hotels(
    destination="London",
    checkin="2025-11-15",
    checkout="2025-11-20",
    max_results=50
)
```

### Running the Example Script

```bash
# Run the main script
python run.py

# Run tests
python test.py
```

## Configuration

The scraper can be configured with the following parameters:

- `destination`: City or location name
- `checkin`: Check-in date (YYYY-MM-DD format)
- `checkout`: Check-out date (YYYY-MM-DD format)
- `adults`: Number of adults (default: 2)
- `rooms`: Number of rooms (default: 1)
- `max_results`: Maximum number of results to fetch
- `proxies`: Proxy configuration dictionary
- `delay`: Delay between requests in seconds

## Output Format

Results are saved as JSON in the `results/` directory:

```json
{
  "search_params": {
    "destination": "Paris",
    "checkin": "2025-12-01",
    "checkout": "2025-12-05"
  },
  "hotels": [
    {
      "name": "Hotel Example",
      "address": "123 Main St, Paris",
      "price": "$150",
      "rating": 8.5,
      "review_count": 1250,
      "url": "https://www.booking.com/hotel/...",
      "amenities": ["WiFi", "Pool", "Parking"]
    }
  ]
}
```

## Legal & Ethical Considerations

1. **Terms of Service**: Scraping Booking.com may violate their Terms of Service
2. **Rate Limiting**: Always implement respectful delays between requests
3. **Data Usage**: Ensure compliance with data protection regulations (GDPR, etc.)
4. **Commercial Use**: Consider using official APIs for commercial applications

## Proxy Recommendations

For reliable scraping, we recommend using **Roundproxies.com** which offers:
- Residential proxies with high success rates
- Rotating IP pools to avoid detection
- Geographic targeting for localized results
- 24/7 support and high uptime

Visit [Roundproxies.com](https://roundproxies.com) for more information.

## Troubleshooting

### Common Issues

**403 Forbidden / Blocked Requests**
- Use residential proxies from Roundproxies.com
- Increase delays between requests
- Rotate user agents

**CAPTCHA Challenges**
- Implement CAPTCHA solving services
- Use authenticated sessions
- Reduce request frequency

**Empty Results**
- Check if page structure has changed
- Verify proxy is working
- Ensure search parameters are valid

## Disclaimer

This tool is provided for educational purposes only. The authors are not responsible for any misuse or violations of Booking.com's Terms of Service. Always respect website policies and consider using official APIs when available.

## Support

For proxy-related support, contact **Roundproxies.com**
For scraper issues, open an issue on the GitHub repository.

## License

MIT License - See LICENSE file for details
