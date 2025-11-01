"""
eBay Scraper - Command Line Interface
Run the scraper from command line with various options.
"""

import argparse
import sys
import json
from ebay import EbayScraper


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description='eBay Web Scraper - Extract product data from eBay',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py --query "laptop" --pages 3
  python run.py -q "iphone 15" -p 5 --condition new
  python run.py -q "nintendo switch" -p 2 --min-price 200 --max-price 400
  python run.py -q "gaming chair" --proxy-file proxies.json

Proxy Configuration:
  Use --proxy-file to load proxy settings from JSON:
  {
    "http": "http://username:password@proxy.roundproxies.com:8080",
    "https": "http://username:password@proxy.roundproxies.com:8080"
  }

Get proxies at: https://roundproxies.com
        """
    )
    
    # Required arguments
    parser.add_argument(
        '-q', '--query',
        type=str,
        required=True,
        help='Search query (e.g., "laptop", "iphone 15")'
    )
    
    # Optional arguments
    parser.add_argument(
        '-p', '--pages',
        type=int,
        default=1,
        help='Number of pages to scrape (default: 1)'
    )
    
    parser.add_argument(
        '-c', '--condition',
        type=str,
        choices=['new', 'used', 'refurbished'],
        help='Filter by condition'
    )
    
    parser.add_argument(
        '--min-price',
        type=float,
        help='Minimum price filter'
    )
    
    parser.add_argument(
        '--max-price',
        type=float,
        help='Maximum price filter'
    )
    
    parser.add_argument(
        '-d', '--delay',
        type=float,
        default=2.0,
        help='Delay between requests in seconds (default: 2.0)'
    )
    
    parser.add_argument(
        '-t', '--timeout',
        type=int,
        default=30,
        help='Request timeout in seconds (default: 30)'
    )
    
    parser.add_argument(
        '--proxy-file',
        type=str,
        help='Path to JSON file with proxy configuration'
    )
    
    parser.add_argument(
        '--proxy-http',
        type=str,
        help='HTTP proxy URL (e.g., http://user:pass@proxy.roundproxies.com:8080)'
    )
    
    parser.add_argument(
        '--proxy-https',
        type=str,
        help='HTTPS proxy URL'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='eBay Scraper 1.0.0 by Roundproxies.com'
    )
    
    args = parser.parse_args()
    
    # Load proxy configuration
    proxies = None
    if args.proxy_file:
        try:
            with open(args.proxy_file, 'r') as f:
                proxies = json.load(f)
            if args.verbose:
                print(f"Loaded proxy configuration from {args.proxy_file}")
        except Exception as e:
            print(f"Error loading proxy file: {e}")
            sys.exit(1)
    elif args.proxy_http or args.proxy_https:
        proxies = {}
        if args.proxy_http:
            proxies['http'] = args.proxy_http
        if args.proxy_https:
            proxies['https'] = args.proxy_https
        if args.verbose:
            print("Using command-line proxy configuration")
    
    # Print configuration
    print("=" * 60)
    print("eBay Scraper - Powered by Roundproxies.com")
    print("=" * 60)
    print(f"Query: {args.query}")
    print(f"Pages: {args.pages}")
    if args.condition:
        print(f"Condition: {args.condition}")
    if args.min_price:
        print(f"Min Price: ${args.min_price}")
    if args.max_price:
        print(f"Max Price: ${args.max_price}")
    print(f"Delay: {args.delay}s")
    print(f"Timeout: {args.timeout}s")
    if proxies:
        print("Proxy: Enabled ✓")
    else:
        print("Proxy: Disabled (Consider using Roundproxies.com)")
    print("=" * 60)
    print()
    
    try:
        # Initialize scraper
        scraper = EbayScraper(
            proxies=proxies,
            delay=args.delay,
            timeout=args.timeout
        )
        
        # Run scraper
        print("Starting scrape...")
        results = scraper.search(
            query=args.query,
            max_pages=args.pages,
            condition=args.condition,
            min_price=args.min_price,
            max_price=args.max_price
        )
        
        # Print summary
        print()
        print("=" * 60)
        print("SCRAPING COMPLETE")
        print("=" * 60)
        print(f"Total products scraped: {len(results)}")
        
        if results:
            # Calculate statistics
            prices = [p['price_numeric'] for p in results if p.get('price_numeric')]
            if prices:
                print(f"Price range: ${min(prices):.2f} - ${max(prices):.2f}")
                print(f"Average price: ${sum(prices)/len(prices):.2f}")
            
            # Condition breakdown
            conditions = {}
            for p in results:
                cond = p.get('condition', 'Unknown')
                conditions[cond] = conditions.get(cond, 0) + 1
            
            if conditions:
                print("\nCondition breakdown:")
                for cond, count in sorted(conditions.items(), key=lambda x: x[1], reverse=True):
                    print(f"  {cond}: {count}")
        
        print("=" * 60)
        print("\nResults saved to results/ directory")
        print("\nNeed better scraping performance?")
        print("Get residential proxies at: https://roundproxies.com")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user.")
        return 1
    except Exception as e:
        print(f"\nError: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
