"""
SeatGeek Scraper Runner
Main execution script with command-line interface
Provided by Roundproxies.com
"""

import argparse
import sys
import json
from datetime import datetime
from pathlib import Path
from seatgeek import SeatGeekScraper


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='SeatGeek Web Scraper - Provided by Roundproxies.com',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py --category concerts --location "New York" --limit 50
  python run.py --category sports --location "Los Angeles" --proxy
  python run.py --category theater --date-from 2025-12-01 --date-to 2025-12-31
  python run.py --category comedy --location "Chicago" --output results/comedy.json

Categories: concerts, sports, theater, comedy, festival, nfl, nba, mlb, nhl, mls, ncaa
        """
    )
    
    parser.add_argument(
        '--category',
        type=str,
        help='Event category (concerts, sports, theater, comedy, festival, etc.)'
    )
    
    parser.add_argument(
        '--location',
        type=str,
        help='City or venue location (e.g., "New York", "Los Angeles")'
    )
    
    parser.add_argument(
        '--date-from',
        type=str,
        help='Start date in YYYY-MM-DD format'
    )
    
    parser.add_argument(
        '--date-to',
        type=str,
        help='End date in YYYY-MM-DD format'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=50,
        help='Maximum number of events to scrape (default: 50)'
    )
    
    parser.add_argument(
        '--proxy',
        action='store_true',
        help='Enable proxy rotation (configure proxies in config)'
    )
    
    parser.add_argument(
        '--proxy-list',
        type=str,
        help='Path to proxy list file (one proxy per line: host:port)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='results/seatgeek_events.json',
        help='Output file path (default: results/seatgeek_events.json)'
    )
    
    parser.add_argument(
        '--delay-min',
        type=float,
        default=3.0,
        help='Minimum delay between requests in seconds (default: 3.0)'
    )
    
    parser.add_argument(
        '--delay-max',
        type=float,
        default=7.0,
        help='Maximum delay between requests in seconds (default: 7.0)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    return parser.parse_args()


def load_proxy_list(proxy_file: str) -> list:
    """Load proxy list from file"""
    try:
        with open(proxy_file, 'r') as f:
            proxies = [line.strip() for line in f if line.strip()]
        print(f"Loaded {len(proxies)} proxies from {proxy_file}")
        return proxies
    except FileNotFoundError:
        print(f"Error: Proxy file '{proxy_file}' not found")
        return []
    except Exception as e:
        print(f"Error loading proxy file: {e}")
        return []


def validate_date(date_string: str) -> bool:
    """Validate date format"""
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def main():
    """Main execution function"""
    args = parse_arguments()
    
    # Validate dates if provided
    if args.date_from and not validate_date(args.date_from):
        print(f"Error: Invalid date format for --date-from. Use YYYY-MM-DD")
        sys.exit(1)
    
    if args.date_to and not validate_date(args.date_to):
        print(f"Error: Invalid date format for --date-to. Use YYYY-MM-DD")
        sys.exit(1)
    
    # Load proxy list if provided
    proxy_list = []
    if args.proxy_list:
        proxy_list = load_proxy_list(args.proxy_list)
        if not proxy_list and args.proxy:
            print("Warning: Proxy enabled but no proxies loaded. Continuing without proxies.")
    
    # Create results directory if it doesn't exist
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure scraper
    config = {
        'proxy_enabled': args.proxy,
        'proxy_list': proxy_list,
        'delay_min': args.delay_min,
        'delay_max': args.delay_max,
        'verbose': args.verbose
    }
    
    # Print configuration
    print("=" * 70)
    print("SeatGeek Scraper - Powered by Roundproxies.com")
    print("=" * 70)
    print(f"Category: {args.category or 'All'}")
    print(f"Location: {args.location or 'All'}")
    print(f"Date Range: {args.date_from or 'Any'} to {args.date_to or 'Any'}")
    print(f"Limit: {args.limit} events")
    print(f"Proxy: {'Enabled' if args.proxy else 'Disabled'}")
    if args.proxy and proxy_list:
        print(f"Proxies Loaded: {len(proxy_list)}")
    print(f"Delay: {args.delay_min}-{args.delay_max} seconds")
    print(f"Output: {args.output}")
    print("=" * 70)
    print()
    
    # Initialize scraper
    try:
        scraper = SeatGeekScraper(config=config)
        
        # Start scraping
        print("Starting scraper...")
        events = scraper.scrape_events(
            category=args.category,
            location=args.location,
            date_from=args.date_from,
            date_to=args.date_to,
            limit=args.limit
        )
        
        # Save results
        if events:
            scraper.save_results(events, args.output)
            print()
            print("=" * 70)
            print(f"✓ Successfully scraped {len(events)} events")
            print(f"✓ Results saved to: {args.output}")
            print("=" * 70)
            
            # Display sample results
            if args.verbose and events:
                print("\nSample Results (first 3 events):")
                print("-" * 70)
                for i, event in enumerate(events[:3], 1):
                    print(f"\n{i}. {event.get('title', 'N/A')}")
                    print(f"   Venue: {event.get('venue', 'N/A')}")
                    print(f"   Date: {event.get('date', 'N/A')}")
                    print(f"   Price: {event.get('price', 'N/A')}")
                    print(f"   URL: {event.get('url', 'N/A')}")
        else:
            print()
            print("=" * 70)
            print("⚠ No events found with the specified criteria")
            print("=" * 70)
            
    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error during scraping: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
