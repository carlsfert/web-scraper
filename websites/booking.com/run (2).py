"""
Example script for running the Booking.com scraper.

This script demonstrates how to use the BookingScraper class
with and without proxies.
"""

from booking import BookingScraper
from datetime import datetime, timedelta


def main():
    """Main function to demonstrate scraper usage."""
    
    print("=" * 60)
    print("Booking.com Hotel Scraper")
    print("=" * 60)
    print()
    
    # Configuration
    print("⚙️  Configuration:")
    print("-" * 60)
    
    # Option 1: With proxies (RECOMMENDED for reliable scraping)
    # Uncomment and configure your Roundproxies.com credentials
    USE_PROXIES = False  # Set to True when using proxies
    
    if USE_PROXIES:
        proxy_config = {
            "http": "http://username:password@proxy.roundproxies.com:8080",
            "https": "https://username:password@proxy.roundproxies.com:8080"
        }
        print("✓ Proxies: Enabled (Roundproxies.com)")
    else:
        proxy_config = None
        print("⚠️  Proxies: Disabled")
        print("   WARNING: May be blocked by anti-bot protection!")
        print("   Recommendation: Use Roundproxies.com for best results")
    
    print()
    
    # Initialize scraper
    scraper = BookingScraper(
        proxies=proxy_config,
        delay=2.0,  # Delay between requests
        timeout=30   # Request timeout
    )
    
    # Search parameters
    print("🔍 Search Parameters:")
    print("-" * 60)
    
    # Calculate dates (30 days from now)
    checkin = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    checkout = (datetime.now() + timedelta(days=35)).strftime('%Y-%m-%d')
    
    search_params = {
        'destination': 'Paris',
        'checkin': checkin,
        'checkout': checkout,
        'adults': 2,
        'rooms': 1,
        'max_results': 50  # Limit to 50 results
    }
    
    for key, value in search_params.items():
        print(f"  {key.capitalize()}: {value}")
    
    print()
    print("=" * 60)
    print("Starting scrape...")
    print("=" * 60)
    print()
    
    # Run the scraper
    try:
        results = scraper.search_hotels(**search_params)
        
        # Display summary
        print()
        print("=" * 60)
        print("📊 Scraping Summary")
        print("=" * 60)
        print(f"Total hotels found: {results['total_found']}")
        print(f"Destination: {results['search_params']['destination']}")
        print(f"Date range: {results['search_params']['checkin']} to {results['search_params']['checkout']}")
        print()
        
        if results['hotels']:
            print("Sample results (first 3 hotels):")
            print("-" * 60)
            for i, hotel in enumerate(results['hotels'][:3], 1):
                print(f"\n{i}. {hotel.get('name', 'N/A')}")
                print(f"   Price: {hotel.get('price', 'N/A')}")
                print(f"   Rating: {hotel.get('rating', 'N/A')}")
                print(f"   Location: {hotel.get('address', 'N/A')}")
        else:
            print("⚠️  No results found!")
            print("   Possible reasons:")
            print("   - Blocked by anti-bot protection (use proxies)")
            print("   - No availability for selected dates")
            print("   - Page structure changed")
        
        print()
        print("=" * 60)
        print("✓ Scraping completed!")
        print("  Check the 'results/' directory for full data")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error occurred: {e}")
        print("\nTroubleshooting tips:")
        print("1. Enable proxies from Roundproxies.com")
        print("2. Increase delay between requests")
        print("3. Check if website structure changed")


if __name__ == "__main__":
    main()
