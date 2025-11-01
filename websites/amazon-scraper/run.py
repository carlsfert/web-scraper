"""
Amazon Scraper - Main Run Script

This script demonstrates how to use the Amazon scraper.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from amazon_scraper import AmazonScraper
from utils import save_to_json, save_to_csv, format_product_for_display


async def main():
    """Run example scraping tasks."""
    
    print("=" * 80)
    print("Amazon Scraper - Demo Run")
    print("=" * 80)
    
    # Initialize scraper
    async with AmazonScraper(domain='com', headless=True) as scraper:
        
        # 1. Search for products
        print("\n1. Searching for 'wireless headphones'...")
        print("-" * 80)
        search_results = await scraper.search_products(
            query='wireless headphones',
            max_pages=1,
            max_results=5
        )
        
        print(f"Found {len(search_results)} products")
        
        # Save search results
        save_to_json(search_results, 'search_results.json', 'outputs')
        save_to_csv(search_results, 'search_results.csv', 'outputs')
        
        # Display first result
        if search_results:
            print("\nFirst product:")
            print(f"  Title: {search_results[0]['title'][:60]}...")
            print(f"  Price: {search_results[0]['price']}")
            print(f"  Rating: {search_results[0]['rating']} ({search_results[0]['reviews_count']} reviews)")
            print(f"  ASIN: {search_results[0]['asin']}")
        
        # 2. Get product details
        if search_results:
            print("\n2. Getting detailed product information...")
            print("-" * 80)
            asin = search_results[0]['asin']
            
            product_details = await scraper.get_product_details(asin)
            
            # Save product details
            save_to_json(product_details, 'product_details.json', 'outputs')
            
            print("\nProduct Details:")
            print(f"  Title: {product_details.get('title', 'N/A')[:60]}...")
            print(f"  Brand: {product_details.get('brand', 'N/A')}")
            print(f"  Price: {product_details.get('price', 'N/A')}")
            print(f"  Rating: {product_details.get('rating', 'N/A')} ({product_details.get('reviews_count', 'N/A')} reviews)")
            print(f"  Availability: {product_details.get('availability', 'N/A')}")
            print(f"  Categories: {', '.join(product_details.get('categories', [])[:3])}")
            print(f"  Images: {len(product_details.get('images', []))} images found")
            print(f"  Specifications: {len(product_details.get('specifications', {}))} specs found")
        
        # 3. Get product reviews
        if search_results:
            print("\n3. Getting product reviews...")
            print("-" * 80)
            asin = search_results[0]['asin']
            
            reviews = await scraper.get_product_reviews(
                asin=asin,
                max_pages=1,
                max_reviews=5
            )
            
            print(f"Found {len(reviews)} reviews")
            
            # Save reviews
            save_to_json(reviews, 'product_reviews.json', 'outputs')
            save_to_csv(reviews, 'product_reviews.csv', 'outputs')
            
            # Display first review
            if reviews:
                print("\nFirst review:")
                print(f"  Rating: {reviews[0]['rating']}/5")
                print(f"  Title: {reviews[0]['title']}")
                print(f"  Reviewer: {reviews[0]['reviewer']}")
                print(f"  Date: {reviews[0]['date']}")
                print(f"  Verified: {reviews[0]['verified_purchase']}")
                print(f"  Text: {reviews[0]['text'][:100]}...")
    
    print("\n" + "=" * 80)
    print("Scraping completed! Check the ./outputs directory for results.")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
