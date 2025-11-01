"""
Example usage of Trustpilot Scraper

This script demonstrates various ways to use the scraper.
"""

import asyncio
from trustpilot import TrustpilotScraper


async def example_1_basic_scraping():
    """Example 1: Basic company scraping"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Company Scraping")
    print("="*60 + "\n")
    
    scraper = TrustpilotScraper()
    
    # Scrape reviews from a single company
    reviews = await scraper.scrape_company_reviews("amazon.com", max_pages=2)
    
    print(f"Scraped {len(reviews)} reviews from Amazon")
    if reviews:
        print(f"First review: {reviews[0]['title']} - {reviews[0]['rating']}/5")


async def example_2_search_companies():
    """Example 2: Search for companies"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Search Companies")
    print("="*60 + "\n")
    
    scraper = TrustpilotScraper()
    
    # Search for companies in electronics category
    companies = await scraper.search_companies("electronics", pages=1)
    
    print(f"Found {len(companies)} electronics companies")
    for i, company in enumerate(companies[:5], 1):
        print(f"{i}. {company.get('displayName')} - Score: {company.get('score', 'N/A')}")


async def example_3_with_proxies():
    """Example 3: Using proxies"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Scraping with Proxies")
    print("="*60 + "\n")
    
    # List of proxy URLs (example format)
    proxies = [
        "http://user:pass@proxy1.example.com:8080",
        "http://user:pass@proxy2.example.com:8080",
    ]
    
    scraper = TrustpilotScraper(
        proxies=proxies,
        max_workers=3,
        request_delay=(2, 4)
    )
    
    # Scrape with rotating proxies
    reviews = await scraper.scrape_company_reviews("ebay.com", max_pages=1)
    print(f"Scraped {len(reviews)} reviews using proxies")


async def example_4_filtered_reviews():
    """Example 4: Scraping with filters"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Filtered Review Scraping")
    print("="*60 + "\n")
    
    scraper = TrustpilotScraper()
    
    # Scrape only 1-star verified reviews
    reviews = await scraper.scrape_company_reviews(
        "walmart.com",
        max_pages=2,
        stars="1",
        verified_only=True,
        sort="recency"
    )
    
    print(f"Scraped {len(reviews)} 1-star verified reviews")
    verified_count = sum(1 for r in reviews if r.get('verified'))
    print(f"Verified: {verified_count}/{len(reviews)}")


async def example_5_company_profile():
    """Example 5: Get company profile"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Company Profile")
    print("="*60 + "\n")
    
    scraper = TrustpilotScraper()
    
    # Get detailed company information
    profile = await scraper.scrape_company_profile("bestbuy.com")
    
    print(f"Company: {profile['name']}")
    print(f"Trust Score: {profile['trust_score']}/5")
    print(f"Total Reviews: {profile['total_reviews']:,}")
    print(f"Verified: {profile['verified']}")
    print(f"Response Rate: {profile.get('response_rate', 'N/A')}")


async def example_6_multiple_companies():
    """Example 6: Scrape multiple companies"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Multiple Companies")
    print("="*60 + "\n")
    
    scraper = TrustpilotScraper(max_workers=5)
    
    companies = ["amazon.com", "ebay.com", "walmart.com"]
    
    # Scrape all companies concurrently
    results = await scraper.scrape_multiple_companies(
        companies,
        max_pages_per_company=2
    )
    
    for company, reviews in results.items():
        avg_rating = sum(r['rating'] for r in reviews) / len(reviews) if reviews else 0
        print(f"{company}: {len(reviews)} reviews, avg rating: {avg_rating:.2f}/5")


async def example_7_category_scraping():
    """Example 7: Scrape by category"""
    print("\n" + "="*60)
    print("EXAMPLE 7: Category Scraping")
    print("="*60 + "\n")
    
    scraper = TrustpilotScraper()
    
    # Scrape companies from electronics category
    companies = await scraper.scrape_category(
        "electronics_technology",
        pages=1,
        min_reviews=100
    )
    
    print(f"Found {len(companies)} electronics companies with 100+ reviews")


async def example_8_save_to_file():
    """Example 8: Save results to file"""
    print("\n" + "="*60)
    print("EXAMPLE 8: Save to File")
    print("="*60 + "\n")
    
    scraper = TrustpilotScraper()
    
    # Scrape and save to JSONL file
    await scraper.scrape_multiple_companies(
        ["amazon.com"],
        max_pages_per_company=3,
        output_file="results/example_output.jsonl"
    )
    
    print("Results saved to results/example_output.jsonl")


async def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("TRUSTPILOT SCRAPER - EXAMPLE USAGE")
    print("="*60)
    
    # Comment out examples you don't want to run
    # WARNING: These make real requests to Trustpilot
    # Uncomment only one at a time to avoid rate limiting
    
    # await example_1_basic_scraping()
    # await example_2_search_companies()
    # await example_3_with_proxies()  # Requires valid proxies
    # await example_4_filtered_reviews()
    # await example_5_company_profile()
    # await example_6_multiple_companies()
    # await example_7_category_scraping()
    # await example_8_save_to_file()
    
    print("\n" + "="*60)
    print("Note: Uncomment the examples you want to run")
    print("Be mindful of rate limits when scraping")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Run examples
    asyncio.run(main())
