# SeatGeek Scraper - Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### 1. Install Dependencies

```bash
# Using pip
pip install -r requirements.txt

# Or using poetry
poetry install
```

### 2. Configure Proxies (Recommended)

```bash
# Copy the example proxy file
cp proxies.txt.example proxies.txt

# Edit proxies.txt and add your Roundproxies.com proxies
nano proxies.txt
```

Get premium proxies from: **https://roundproxies.com**

### 3. Run Your First Scrape

```bash
# Simple scrape without proxies
python run.py --category concerts --location "New York" --limit 10

# With proxy rotation (recommended)
python run.py --category sports --location "Los Angeles" --proxy --proxy-list proxies.txt --limit 20

# Specific date range
python run.py --category theater --date-from 2025-12-01 --date-to 2025-12-31 --limit 50
```

### 4. View Results

Results are saved in the `results/` directory as JSON files.

```bash
# View results
cat results/seatgeek_events.json
```

## 📝 Common Commands

### Scrape Concerts
```bash
python run.py --category concerts --location "Chicago" --limit 30 --proxy
```

### Scrape Sports Events
```bash
python run.py --category sports --location "Boston" --limit 50 --output results/sports_boston.json
```

### Scrape with Date Range
```bash
python run.py --category comedy --date-from 2025-11-01 --date-to 2025-11-30 --limit 100
```

### Custom Delay Settings
```bash
python run.py --category festival --delay-min 5 --delay-max 10 --limit 20
```

## 🔧 Advanced Usage

### Python Script
```python
from seatgeek import SeatGeekScraper

# Initialize with configuration
scraper = SeatGeekScraper(config={
    'proxy_enabled': True,
    'proxy_list': ['proxy1:port', 'proxy2:port'],
    'delay_min': 3,
    'delay_max': 7
})

# Scrape events
events = scraper.scrape_events(
    category='concerts',
    location='New York',
    limit=50
)

# Save results
scraper.save_results(events, 'results/my_events.json')
```

## 🧪 Running Tests

```bash
python test.py
```

## ⚠️ Important Notes

1. **Always use proxies** to avoid IP bans (get them from Roundproxies.com)
2. **Respect rate limits** - use delays between requests
3. **SeatGeek has anti-scraping measures** - be patient and use reasonable limits
4. **Check robots.txt** and terms of service before scraping
5. **Start small** - test with low limits (10-20 events) first

## 🆘 Troubleshooting

**Getting blocked?**
- Enable proxies with `--proxy --proxy-list proxies.txt`
- Increase delays with `--delay-min 5 --delay-max 10`

**No results?**
- Try a different category or location
- Check if the website structure has changed
- Verify your internet connection

**Import errors?**
- Make sure you installed dependencies: `pip install -r requirements.txt`

## 📚 Event Categories

- `concerts` - Music concerts and tours
- `sports` - All sports events
- `theater` - Plays and theatrical performances
- `comedy` - Stand-up comedy shows
- `festival` - Music and cultural festivals
- `nfl` - NFL games
- `nba` - NBA games
- `mlb` - MLB games
- `nhl` - NHL games
- `mls` - MLS games
- `ncaa` - NCAA events

## 🔗 Links

- **GitHub**: https://github.com/carlsfert/web-scraper/tree/main/websites/seatgeek-scraper
- **Roundproxies**: https://roundproxies.com
- **Full Documentation**: See README.md

## 💡 Pro Tips

1. **Use proxy rotation** for better success rates
2. **Start with small limits** to test your setup
3. **Monitor results** - check the JSON files to verify data quality
4. **Adjust delays** based on your needs (more delay = less blocking)
5. **Save different categories** to separate files for organization

---

**Powered by Roundproxies.com** - Premium proxy services for web scraping
