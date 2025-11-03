"""
Command-line interface for the Alibaba scraper.
Usage: python run.py --keyword "laptop" --pages 3 --output results/laptops.csv
"""

import argparse
import sys
import os
from alibaba import AlibabaScraper
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Scrape product data from Alibaba.com',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py --keyword "laptop" --pages 2
  python run.py --keyword "smartphone" --pages 5 --output results/phones.csv
  python run.py --keyword "electronics" --proxy http://user:pass@proxy.com:8080
  python run.py --keyword "furniture" --delay 3 6 --verbose
        """
    )
    
    parser.add_argument(
        '-k', '--keyword',
        type=str,
        required=True,
        help='Search keyword for products (required)'
    )
    
    parser.add_argument(
        '-p', '--pages',
        type=int,
        default=1,
        help='Number of pages to scrape (default: 1)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='results/alibaba_products.csv',
        help='Output CSV file path (default: results/alibaba_products.csv)'
    )
    
    parser.add_argument(
        '--proxy',
        type=str,
        help='Proxy URL (e.g., http://user:pass@proxy.roundproxies.com:8080)'
    )
    
    parser.add_argument(
        '--proxy-http',
        type=str,
        help='HTTP proxy URL'
    )
    
    parser.add_argument(
        '--proxy-https',
        type=str,
        help='HTTPS proxy URL'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        nargs=2,
        default=[2, 5],
        metavar=('MIN', 'MAX'),
        help='Random delay range between requests in seconds (default: 2 5)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--details',
        action='store_true',
        help='Fetch detailed information for each product (slower)'
    )
    
    return parser.parse_args()


def setup_proxies(args):
    """
    Setup proxy configuration from command-line arguments.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Proxy dictionary or None
    """
    proxies = None
    
    if args.proxy:
        proxies = {
            'http': args.proxy,
            'https': args.proxy
        }
        logger.info(f"Using proxy: {args.proxy}")
    elif args.proxy_http or args.proxy_https:
        proxies = {}
        if args.proxy_http:
            proxies['http'] = args.proxy_http
            logger.info(f"Using HTTP proxy: {args.proxy_http}")
        if args.proxy_https:
            proxies['https'] = args.proxy_https
            logger.info(f"Using HTTPS proxy: {args.proxy_https}")
    
    return proxies


def ensure_output_directory(filepath):
    """
    Ensure the output directory exists.
    
    Args:
        filepath: Path to the output file
    """
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created output directory: {directory}")


def main():
    """Main execution function."""
    args = parse_arguments()
    
    # Setup logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled")
    
    # Display configuration
    print("=" * 60)
    print("ALIBABA SCRAPER")
    print("=" * 60)
    print(f"Keyword:       {args.keyword}")
    print(f"Pages:         {args.pages}")
    print(f"Output:        {args.output}")
    print(f"Delay Range:   {args.delay[0]}-{args.delay[1]} seconds")
    print(f"Fetch Details: {'Yes' if args.details else 'No'}")
    print("=" * 60)
    print()
    
    # Setup proxies
    proxies = setup_proxies(args)
    
    if not proxies:
        print("⚠️  WARNING: No proxy configured!")
        print("   Alibaba actively blocks scraping attempts.")
        print("   Using proxies (e.g., from Roundproxies.com) is highly recommended.")
        print()
        response = input("Continue without proxy? (y/N): ")
        if response.lower() != 'y':
            print("Scraping cancelled.")
            sys.exit(0)
        print()
    
    # Create scraper instance
    try:
        scraper = AlibabaScraper(
            proxies=proxies,
            delay=tuple(args.delay)
        )
    except Exception as e:
        logger.error(f"Failed to initialize scraper: {str(e)}")
        sys.exit(1)
    
    # Search for products
    try:
        print(f"🔍 Searching for '{args.keyword}'...\n")
        products = scraper.search_products(args.keyword, max_pages=args.pages)
        
        if not products:
            print("\n❌ No products found.")
            sys.exit(1)
        
        print(f"\n✅ Found {len(products)} products")
        
        # Fetch detailed information if requested
        if args.details:
            print("\n📄 Fetching detailed information for each product...")
            detailed_products = []
            
            for i, product in enumerate(products, 1):
                if product.get('url') and product['url'] != 'N/A':
                    print(f"   [{i}/{len(products)}] Fetching details for: {product.get('title', 'N/A')[:50]}...")
                    details = scraper.get_product_details(product['url'])
                    
                    if details:
                        # Merge basic info with details
                        product.update(details)
                    
                    detailed_products.append(product)
                else:
                    detailed_products.append(product)
            
            products = detailed_products
        
        # Save to CSV
        print(f"\n💾 Saving results to {args.output}...")
        ensure_output_directory(args.output)
        scraper.save_to_csv(products, args.output)
        
        print("\n" + "=" * 60)
        print("SCRAPING COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"Total products: {len(products)}")
        print(f"Output file:    {args.output}")
        print(f"File size:      {os.path.getsize(args.output) / 1024:.2f} KB")
        print("=" * 60)
        
        # Display sample results
        print("\n📦 Sample Results (first 3 products):")
        print("-" * 60)
        for i, product in enumerate(products[:3], 1):
            print(f"\n{i}. {product.get('title', 'N/A')[:70]}")
            print(f"   Price:    {product.get('price', 'N/A')}")
            print(f"   MOQ:      {product.get('moq', 'N/A')}")
            print(f"   Supplier: {product.get('supplier', 'N/A')}")
            print(f"   URL:      {product.get('url', 'N/A')[:60]}...")
        
        print("\n" + "=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
