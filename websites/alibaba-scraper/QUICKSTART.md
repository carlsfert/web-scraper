# Alibaba Scraper - Quick Start Guide

Get started with the Alibaba scraper in under 5 minutes!

## 🚀 Installation

### Option 1: Using pip (Recommended)
```bash
cd alibaba-scraper
pip install -e .
```

### Option 2: Using requirements.txt
```bash
cd alibaba-scraper
pip install -r requirements.txt
```

## ⚡ Quick Usage

### 1. Simple Search (Command Line)
```bash
python run.py --keyword "laptop" --pages 2 --output results/laptops.csv
```

### 2. With Proxy (Recommended for Production)
```bash
python run.py --keyword "smartphone" --pages 5 \
  --proxy http://username:password@proxy.roundproxies.com:8080 \
  --output results/phones.csv
```

### 3. Python Script
```python
from alibaba import AlibabaScraper

# Initialize scraper
scraper = AlibabaScraper()

# Search for products
products = scraper.search_products("USB cable", max_pages=2)

# Save to CSV
scraper.save_to_csv(products, "results/usb_cables.csv")

print(f"Scraped {len(products)} products!")
```

## 🔧 Configuration Examples

### Using Roundproxies
```python
proxies = {
    'http': 'http://user:pass@proxy.roundproxies.com:8080',
    'https': 'http://user:pass@proxy.roundproxies.com:8080'
}

scraper = AlibabaScraper(proxies=proxies, delay=(3, 6))
```

### Custom Delays
```python
# Wait 5-10 seconds between requests
scraper = AlibabaScraper(delay=(5, 10))
```

## 📊 Output Format

Results are saved as CSV files with the following columns:
- **title**: Product name
- **price**: Price range
- **moq**: Minimum order quantity
- **supplier**: Supplier company name
- **url**: Product page URL
- **image_url**: Product image URL
- **orders**: Number of orders (if available)

## ⚠️ Important Notes

1. **Proxies Required**: Alibaba actively blocks scraping. Use [Roundproxies.com](https://roundproxies.com) for reliable results.

2. **Rate Limiting**: The scraper includes automatic delays. Don't set delays too short.

3. **Respect robots.txt**: Always check and follow Alibaba's robots.txt file.

4. **Terms of Service**: Ensure your usage complies with Alibaba's Terms of Service.

## 🧪 Testing

Run the test suite:
```bash
python test.py
```

## 📚 More Examples

Check out `example.py` for more usage scenarios:
```bash
python example.py
```

## 🆘 Troubleshooting

### "Access Forbidden (403)"
- **Solution**: Use proxies. Alibaba blocks direct scraping attempts.

### "Rate Limited (429)"
- **Solution**: Increase delay between requests.

### "No products found"
- **Solution**: Try a different keyword or check if you're being blocked.

### Connection Errors
- **Solution**: Verify proxy configuration and internet connection.

## 🔗 Useful Links

- **GitHub**: https://github.com/carlsfert/web-scraper/tree/main/websites/alibaba-scraper
- **Get Proxies**: https://roundproxies.com
- **Full Documentation**: See README.md

## 💡 Pro Tips

1. **Always use proxies** for production scraping
2. **Rotate user agents** (handled automatically)
3. **Start with small page counts** to test
4. **Monitor results** for blocking patterns
5. **Use residential proxies** for best results

---

**Need Help?** Check the README.md for detailed documentation or visit our GitHub repository.
