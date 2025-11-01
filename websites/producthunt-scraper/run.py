"""
Example scraper run script.

This script demonstrates how to use the Product Hunt scraper functions.
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from producthunt import (
    scrape_daily_products,
    scrape_product,
    scrape_search,
    scrape_archive
)


async def main():
    """
    Run example scraping tasks for Product Hunt.
    """
    # Create results directory if it doesn't exist
    results_dir = Path("./results")
    results_dir.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("Product Hunt Scraper - Example Run")
    print("=" * 60)
    
    # 1. Scrape today's products (limited to 5 for demo)
    print("\n1. Scraping today's products...")
    print("-" * 60)
    daily_products = await scrape_daily_products(max_products=5)
    print(f"Scraped {len(daily_products)} products from today")
    
    # Save daily products
    with open(results_dir / "daily_products.json", "w", encoding="utf-8") as f:
        json.dump(daily_products, f, indent=2, ensure_ascii=False)
    print(f"Saved to: {results_dir / 'daily_products.json'}")
    
    # Display sample
    if daily_products:
        print("\nSample product:")
        print(f"  Name: {daily_products[0]['name']}")
        print(f"  Tagline: {daily_products[0]['tagline']}")
        print(f"  Upvotes: {daily_products[0]['upvotes']}")
        print(f"  URL: {daily_products[0]['url']}")
    
    # 2. Scrape detailed information for the first product
    if daily_products:
        print("\n2. Scraping detailed product information...")
        print("-" * 60)
        product_url = daily_products[0]['url']
        
        product_details = await scrape_product(product_url)
        print(f"Scraped details for: {product_details['name']}")
        
        # Save product details
        with open(results_dir / "product_details.json", "w", encoding="utf-8") as f:
            json.dump(product_details, f, indent=2, ensure_ascii=False)
        print(f"Saved to: {results_dir / 'product_details.json'}")
        
        # Display details
        print("\nProduct details:")
        print(f"  Name: {product_details['name']}")
        print(f"  Tagline: {product_details['tagline']}")
        print(f"  Description: {product_details['description'][:100]}...")
        print(f"  Upvotes: {product_details['upvotes']}")
        print(f"  Comments: {product_details['comments']}")
        print(f"  Makers: {', '.join([m['name'] for m in product_details['makers']])}")
        print(f"  Website: {product_details['website']}")
        print(f"  Topics: {', '.join(product_details['topics'])}")
    
    # 3. Search for AI products
    print("\n3. Searching for 'AI' products...")
    print("-" * 60)
    search_results = await scrape_search("AI", max_results=5)
    print(f"Found {len(search_results)} AI-related products")
    
    # Save search results
    with open(results_dir / "search_results.json", "w", encoding="utf-8") as f:
        json.dump(search_results, f, indent=2, ensure_ascii=False)
    print(f"Saved to: {results_dir / 'search_results.json'}")
    
    # Display sample
    if search_results:
        print("\nSample search result:")
        print(f"  Name: {search_results[0]['name']}")
        print(f"  Tagline: {search_results[0]['tagline']}")
        print(f"  Upvotes: {search_results[0]['upvotes']}")
    
    # 4. Scrape archive from 7 days ago
    print("\n4. Scraping archive from 7 days ago...")
    print("-" * 60)
    archive_date = datetime.now() - timedelta(days=7)
    archive_products = await scrape_archive(archive_date, max_products=5)
    print(f"Scraped {len(archive_products)} products from {archive_date.strftime('%Y-%m-%d')}")
    
    # Save archive results
    with open(results_dir / "archive_products.json", "w", encoding="utf-8") as f:
        json.dump(archive_products, f, indent=2, ensure_ascii=False)
    print(f"Saved to: {results_dir / 'archive_products.json'}")
    
    # Display sample
    if archive_products:
        print("\nSample archive product:")
        print(f"  Name: {archive_products[0]['name']}")
        print(f"  Tagline: {archive_products[0]['tagline']}")
        print(f"  Upvotes: {archive_products[0]['upvotes']}")
        print(f"  Date: {archive_products[0]['date']}")
    
    print("\n" + "=" * 60)
    print("Scraping completed! Check the ./results directory for output files.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
