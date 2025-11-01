"""
Command-line interface for Trustpilot Scraper

Usage:
    python run.py --company amazon.com --pages 10
    python run.py --search "electronics" --pages 5
    python run.py --category electronics_technology --pages 10
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from trustpilot import TrustpilotScraper


def load_proxies_from_file(filepath: str) -> List[str]:
    """Load proxy list from file (one proxy per line)"""
    try:
        with open(filepath, 'r') as f:
            proxies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        print(f"✅ Loaded {len(proxies)} proxies from {filepath}")
        return proxies
    except FileNotFoundError:
        print(f"❌ Proxy file not found: {filepath}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading proxies: {e}")
        sys.exit(1)


def save_results(data: dict, output_dir: str = "results"):
    """Save scraping results to JSON file"""
    # Create results directory
    results_path = Path(output_dir)
    results_path.mkdir(exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = results_path / f"trustpilot_results_{timestamp}.json"
    
    # Save data
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Results saved to: {filename}")
    return filename


def save_reviews_jsonl(reviews: List[dict], company: str, output_dir: str = "results"):
    """Save reviews to JSONL format"""
    results_path = Path(output_dir)
    results_path.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = results_path / f"reviews_{company.replace('.', '_')}_{timestamp}.jsonl"
    
    with open(filename, 'w', encoding='utf-8') as f:
        for review in reviews:
            f.write(json.dumps(review, ensure_ascii=False) + '\n')
    
    print(f"💾 Reviews saved to: {filename}")
    return filename


async def scrape_single_company(args):
    """Scrape a single company's reviews"""
    print(f"\n{'=' * 60}")
    print(f"🎯 SCRAPING COMPANY: {args.company}")
    print(f"{'=' * 60}\n")
    
    # Load proxies if specified
    proxies = None
    if args.proxy_file:
        proxies = load_proxies_from_file(args.proxy_file)
    elif args.proxy:
        proxies = args.proxy
    
    # Initialize scraper
    scraper = TrustpilotScraper(
        proxies=proxies,
        max_workers=args.workers,
        request_delay=(args.min_delay, args.max_delay),
        timeout=args.timeout
    )
    
    try:
        # Scrape company profile
        if not args.skip_profile:
            print("📋 Fetching company profile...")
            profile = await scraper.scrape_company_profile(args.company)
            print(f"✅ Profile: {profile['name']} - {profile['trust_score']} stars "
                  f"({profile['total_reviews']} reviews)\n")
        
        # Scrape reviews
        reviews = await scraper.scrape_company_reviews(
            args.company,
            max_pages=args.pages,
            sort=args.sort,
            stars=args.stars,
            verified_only=args.verified_only
        )
        
        # Save results
        if args.format == 'json':
            result_data = {
                'company': args.company,
                'profile': profile if not args.skip_profile else None,
                'reviews': reviews,
                'scraped_at': datetime.now().isoformat(),
                'total_reviews': len(reviews)
            }
            save_results(result_data, args.output)
        else:  # jsonl
            save_reviews_jsonl(reviews, args.company, args.output)
        
        # Print summary
        print(f"\n{'=' * 60}")
        print(f"✨ SCRAPING COMPLETE!")
        print(f"{'=' * 60}")
        print(f"Total Reviews: {len(reviews)}")
        if reviews:
            ratings = [r['rating'] for r in reviews if r.get('rating')]
            if ratings:
                avg_rating = sum(ratings) / len(ratings)
                print(f"Average Rating: {avg_rating:.2f} / 5.0")
            verified = sum(1 for r in reviews if r.get('verified'))
            print(f"Verified Reviews: {verified} ({verified/len(reviews)*100:.1f}%)")
        print(f"{'=' * 60}\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


async def scrape_search(args):
    """Search and scrape companies"""
    print(f"\n{'=' * 60}")
    print(f"🔍 SEARCHING: {args.search}")
    print(f"{'=' * 60}\n")
    
    # Load proxies if specified
    proxies = None
    if args.proxy_file:
        proxies = load_proxies_from_file(args.proxy_file)
    elif args.proxy:
        proxies = args.proxy
    
    scraper = TrustpilotScraper(
        proxies=proxies,
        max_workers=args.workers,
        request_delay=(args.min_delay, args.max_delay)
    )
    
    try:
        # Search for companies
        companies = await scraper.search_companies(args.search, pages=args.pages)
        
        # Save results
        result_data = {
            'search_query': args.search,
            'companies': companies,
            'total_found': len(companies),
            'scraped_at': datetime.now().isoformat()
        }
        filename = save_results(result_data, args.output)
        
        # Print summary
        print(f"\n{'=' * 60}")
        print(f"✨ SEARCH COMPLETE!")
        print(f"{'=' * 60}")
        print(f"Companies Found: {len(companies)}")
        if companies:
            avg_score = sum(c.get('score', 0) for c in companies) / len(companies)
            print(f"Average Trust Score: {avg_score:.2f}")
        print(f"Results saved to: {filename}")
        print(f"{'=' * 60}\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


async def scrape_category(args):
    """Scrape companies from a category"""
    print(f"\n{'=' * 60}")
    print(f"📂 SCRAPING CATEGORY: {args.category}")
    print(f"{'=' * 60}\n")
    
    # Load proxies if specified
    proxies = None
    if args.proxy_file:
        proxies = load_proxies_from_file(args.proxy_file)
    elif args.proxy:
        proxies = args.proxy
    
    scraper = TrustpilotScraper(
        proxies=proxies,
        max_workers=args.workers,
        request_delay=(args.min_delay, args.max_delay)
    )
    
    try:
        companies = await scraper.scrape_category(
            args.category,
            pages=args.pages,
            min_reviews=args.min_reviews
        )
        
        # Save results
        result_data = {
            'category': args.category,
            'companies': companies,
            'total_found': len(companies),
            'scraped_at': datetime.now().isoformat()
        }
        filename = save_results(result_data, args.output)
        
        print(f"\n{'=' * 60}")
        print(f"✨ CATEGORY SCRAPING COMPLETE!")
        print(f"{'=' * 60}")
        print(f"Companies Found: {len(companies)}")
        print(f"Results saved to: {filename}")
        print(f"{'=' * 60}\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


async def scrape_multiple(args):
    """Scrape multiple companies from file"""
    print(f"\n{'=' * 60}")
    print(f"📋 SCRAPING MULTIPLE COMPANIES")
    print(f"{'=' * 60}\n")
    
    # Load company list
    try:
        with open(args.company_file, 'r') as f:
            companies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        print(f"✅ Loaded {len(companies)} companies from {args.company_file}\n")
    except FileNotFoundError:
        print(f"❌ Company file not found: {args.company_file}")
        sys.exit(1)
    
    # Load proxies if specified
    proxies = None
    if args.proxy_file:
        proxies = load_proxies_from_file(args.proxy_file)
    elif args.proxy:
        proxies = args.proxy
    
    scraper = TrustpilotScraper(
        proxies=proxies,
        max_workers=args.workers,
        request_delay=(args.min_delay, args.max_delay)
    )
    
    try:
        # Scrape all companies
        results = await scraper.scrape_multiple_companies(
            companies,
            max_pages_per_company=args.pages
        )
        
        # Save results
        result_data = {
            'companies': list(results.keys()),
            'results': results,
            'total_companies': len(results),
            'total_reviews': sum(len(reviews) for reviews in results.values()),
            'scraped_at': datetime.now().isoformat()
        }
        filename = save_results(result_data, args.output)
        
        print(f"\n{'=' * 60}")
        print(f"✨ BATCH SCRAPING COMPLETE!")
        print(f"{'=' * 60}")
        print(f"Companies Scraped: {len(results)}")
        print(f"Total Reviews: {result_data['total_reviews']}")
        print(f"Results saved to: {filename}")
        print(f"{'=' * 60}\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Trustpilot Scraper - Extract reviews and company data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape a single company
  python run.py --company amazon.com --pages 10

  # Search for companies
  python run.py --search "electronics" --pages 5

  # Scrape a category
  python run.py --category electronics_technology --pages 10

  # Scrape multiple companies from file
  python run.py --company-file companies.txt --pages 5

  # Use proxies
  python run.py --company amazon.com --proxy-file proxies.txt

  # Filter reviews
  python run.py --company amazon.com --stars 1 --verified-only
        """
    )
    
    # Mode selection
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--company', type=str, help='Company domain to scrape (e.g., amazon.com)')
    mode.add_argument('--search', type=str, help='Search query for companies')
    mode.add_argument('--category', type=str, help='Category slug to scrape')
    mode.add_argument('--company-file', type=str, help='File containing company domains (one per line)')
    
    # Common options
    parser.add_argument('--pages', type=int, default=10, help='Number of pages to scrape (default: 10)')
    parser.add_argument('--output', type=str, default='results', help='Output directory (default: results)')
    parser.add_argument('--format', choices=['json', 'jsonl'], default='json', help='Output format (default: json)')
    
    # Scraper configuration
    parser.add_argument('--workers', type=int, default=5, help='Number of concurrent workers (default: 5)')
    parser.add_argument('--min-delay', type=float, default=1.0, help='Minimum delay between requests (default: 1.0s)')
    parser.add_argument('--max-delay', type=float, default=3.0, help='Maximum delay between requests (default: 3.0s)')
    parser.add_argument('--timeout', type=int, default=30, help='Request timeout in seconds (default: 30)')
    
    # Proxy options
    parser.add_argument('--proxy', type=str, nargs='+', help='Proxy URLs (space-separated)')
    parser.add_argument('--proxy-file', type=str, help='File containing proxy URLs (one per line)')
    
    # Review filters (for --company mode)
    parser.add_argument('--sort', choices=['recency', 'highest_rated', 'lowest_rated'], 
                       default='recency', help='Sort order for reviews (default: recency)')
    parser.add_argument('--stars', type=str, choices=['1', '2', '3', '4', '5'], 
                       help='Filter by star rating')
    parser.add_argument('--verified-only', action='store_true', help='Only scrape verified reviews')
    parser.add_argument('--skip-profile', action='store_true', help='Skip company profile scraping')
    
    # Category options
    parser.add_argument('--min-reviews', type=int, default=0, 
                       help='Minimum number of reviews for category scraping (default: 0)')
    
    args = parser.parse_args()
    
    # Route to appropriate function
    try:
        if args.company:
            asyncio.run(scrape_single_company(args))
        elif args.search:
            asyncio.run(scrape_search(args))
        elif args.category:
            asyncio.run(scrape_category(args))
        elif args.company_file:
            asyncio.run(scrape_multiple(args))
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
