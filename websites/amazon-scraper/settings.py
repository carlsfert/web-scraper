"""
Configuration settings for Amazon scraper.
"""

# Amazon domain settings
AMAZON_DOMAINS = {
    'us': 'com',
    'uk': 'co.uk',
    'germany': 'de',
    'france': 'fr',
    'italy': 'it',
    'spain': 'es',
    'canada': 'ca',
    'japan': 'co.jp',
    'india': 'in',
    'mexico': 'com.mx',
    'australia': 'com.au'
}

# Default domain
DEFAULT_DOMAIN = 'com'

# Browser settings
HEADLESS_MODE = True
BROWSER_TIMEOUT = 30000  # 30 seconds

# Scraping settings
DEFAULT_MAX_PAGES = 1
DEFAULT_MAX_RESULTS = None  # No limit
DELAY_BETWEEN_REQUESTS = 2  # seconds

# User agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
]

# Output settings
OUTPUT_DIR = 'outputs'
OUTPUT_FORMAT = 'json'  # json, csv, or both

# Rate limiting
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# Logging
LOG_LEVEL = 'INFO'
LOG_FILE = 'amazon_scraper.log'
