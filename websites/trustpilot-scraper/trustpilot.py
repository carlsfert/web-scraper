"""
Trustpilot Scraper - Extract reviews and company data from Trustpilot.com

This module provides comprehensive scraping capabilities for Trustpilot,
including company search, review extraction, and anti-bot protection.
"""

import asyncio
import json
import random
import time
from collections import deque
from datetime import datetime
from itertools import cycle
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlencode

import httpx
from parsel import Selector


class TrustpilotScraperMonitor:
    """Monitor scraper performance and track metrics"""
    
    def __init__(self, window_size: int = 100):
        self.success_rate = deque(maxlen=window_size)
        self.response_times = deque(maxlen=window_size)
        self.last_review_date = None
        self.total_requests = 0
        self.total_reviews = 0
    
    async def track_request(self, func, *args, **kwargs):
        """Track performance metrics for scraping requests"""
        start = time.time()
        success = False
        result = None
        
        try:
            result = await func(*args, **kwargs)
            success = True
            self.total_requests += 1
            
            # Track review data if available
            if isinstance(result, list) and result:
                self.total_reviews += len(result)
                dates = [r.get('dates', {}).get('publishedDate') for r in result if isinstance(r, dict)]
                if dates:
                    self.last_review_date = max(filter(None, dates))
            
            return result
            
        except Exception as e:
            print(f"❌ Request failed: {e}")
            raise
            
        finally:
            elapsed = time.time() - start
            self.success_rate.append(1 if success else 0)
            self.response_times.append(elapsed)
            
            # Alert if performance drops
            if len(self.success_rate) == self.success_rate.maxlen:
                rate = sum(self.success_rate) / len(self.success_rate)
                avg_time = sum(self.response_times) / len(self.response_times)
                
                if rate < 0.8:
                    print(f"⚠️  WARNING: Success rate dropped to {rate:.1%}")
                    print(f"⚠️  Consider adding more proxies or reducing request rate")
                
                if avg_time > 5.0:
                    print(f"⚠️  SLOW: Average response time {avg_time:.2f}s")
    
    def get_stats(self) -> Dict:
        """Get current performance statistics"""
        if not self.success_rate:
            return {"status": "no_data"}
        
        return {
            "success_rate": sum(self.success_rate) / len(self.success_rate),
            "avg_response_time": sum(self.response_times) / len(self.response_times),
            "total_requests": self.total_requests,
            "total_reviews": self.total_reviews,
            "last_review_date": self.last_review_date
        }


class TrustpilotScraper:
    """Main scraper class for Trustpilot data extraction"""
    
    BASE_URL = "https://www.trustpilot.com"
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
    ]
    
    def __init__(
        self,
        proxies: Optional[List[str]] = None,
        max_workers: int = 5,
        request_delay: Tuple[float, float] = (1.0, 3.0),
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize Trustpilot scraper
        
        Args:
            proxies: List of proxy URLs (optional)
            max_workers: Maximum concurrent workers
            request_delay: Tuple of (min, max) delay between requests in seconds
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts for failed requests
        """
        self.proxies = cycle(proxies) if proxies else None
        self.max_workers = max_workers
        self.request_delay = request_delay
        self.timeout = timeout
        self.max_retries = max_retries
        self.monitor = TrustpilotScraperMonitor()
    
    def _get_headers(self) -> Dict[str, str]:
        """Generate randomized request headers"""
        return {
            'User-Agent': random.choice(self.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Referer': 'https://www.google.com/'
        }
    
    async def _delay(self):
        """Apply random delay between requests"""
        delay = random.uniform(*self.request_delay)
        await asyncio.sleep(delay)
    
    def _extract_next_data(self, html: str) -> Dict:
        """Extract JSON data from __NEXT_DATA__ script tag"""
        try:
            selector = Selector(html)
            script_data = selector.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
            
            if not script_data:
                raise ValueError("No __NEXT_DATA__ found in page")
            
            return json.loads(script_data)
        except Exception as e:
            raise ValueError(f"Failed to extract NEXT_DATA: {e}")
    
    async def _make_request(
        self,
        url: str,
        params: Optional[Dict] = None,
        retry_count: int = 0
    ) -> httpx.Response:
        """Make HTTP request with retry logic"""
        try:
            await self._delay()
            
            proxy = next(self.proxies) if self.proxies else None
            headers = self._get_headers()
            
            async with httpx.AsyncClient(
                proxies=proxy,
                timeout=self.timeout,
                follow_redirects=True
            ) as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                return response
                
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            if retry_count < self.max_retries:
                wait_time = 2 ** retry_count  # Exponential backoff
                print(f"⚠️  Request failed, retrying in {wait_time}s... (attempt {retry_count + 1}/{self.max_retries})")
                await asyncio.sleep(wait_time)
                return await self._make_request(url, params, retry_count + 1)
            raise
    
    async def search_companies(
        self,
        query: str,
        pages: int = 1
    ) -> List[Dict]:
        """
        Search for companies on Trustpilot
        
        Args:
            query: Search keyword
            pages: Number of pages to scrape
            
        Returns:
            List of company data dictionaries
        """
        results = []
        
        for page in range(1, pages + 1):
            try:
                url = f"{self.BASE_URL}/search"
                params = {'query': query, 'page': page}
                
                print(f"🔍 Searching companies: '{query}' (page {page}/{pages})")
                
                response = await self._make_request(url, params)
                data = self._extract_next_data(response.text)
                
                # Extract business units
                page_props = data.get('props', {}).get('pageProps', {})
                business_units = page_props.get('businessUnits', {}).get('businesses', [])
                
                results.extend(business_units)
                print(f"✅ Found {len(business_units)} companies on page {page}")
                
            except Exception as e:
                print(f"❌ Failed to scrape search page {page}: {e}")
        
        print(f"📊 Total companies found: {len(results)}")
        return results
    
    async def scrape_company_profile(self, company_domain: str) -> Dict:
        """
        Scrape company profile data
        
        Args:
            company_domain: Company domain (e.g., 'amazon.com')
            
        Returns:
            Company data dictionary
        """
        try:
            url = f"{self.BASE_URL}/review/{company_domain}"
            
            print(f"🏢 Scraping company profile: {company_domain}")
            
            response = await self._make_request(url)
            data = self._extract_next_data(response.text)
            
            page_props = data.get('props', {}).get('pageProps', {})
            business_unit = page_props.get('businessUnit', {})
            
            company_data = {
                'domain': company_domain,
                'name': business_unit.get('displayName'),
                'trust_score': business_unit.get('trustScore'),
                'total_reviews': business_unit.get('numberOfReviews', {}).get('total', 0),
                'verified': business_unit.get('isVerified', False),
                'claimed': business_unit.get('isClaimed', False),
                'claimed_date': business_unit.get('claimedDate'),
                'response_rate': business_unit.get('responseRate'),
                'response_time': business_unit.get('responseTime'),
                'location': business_unit.get('location'),
                'website_url': business_unit.get('websiteUrl'),
                'scraped_at': datetime.now().isoformat()
            }
            
            print(f"✅ Company profile scraped: {company_data['name']} ({company_data['trust_score']} stars)")
            return company_data
            
        except Exception as e:
            print(f"❌ Failed to scrape company profile {company_domain}: {e}")
            raise
    
    async def scrape_company_reviews(
        self,
        company_domain: str,
        max_pages: Optional[int] = None,
        sort: str = 'recency',
        stars: Optional[str] = None,
        verified_only: bool = False
    ) -> List[Dict]:
        """
        Scrape all reviews for a company using the private API
        
        Args:
            company_domain: Company domain (e.g., 'amazon.com')
            max_pages: Maximum pages to scrape (None for all)
            sort: Sort order ('recency', 'highest_rated', 'lowest_rated')
            stars: Filter by stars (e.g., '1', '5')
            verified_only: Only return verified reviews
            
        Returns:
            List of review dictionaries
        """
        all_reviews = []
        
        try:
            # First, get the build ID from the main page
            main_url = f"{self.BASE_URL}/review/{company_domain}"
            response = await self._make_request(main_url)
            data = self._extract_next_data(response.text)
            build_id = data.get('buildId')
            
            if not build_id:
                raise ValueError("Could not extract build ID")
            
            # Construct API endpoint
            api_url = f"{self.BASE_URL}/_next/data/{build_id}/review/{company_domain}.json"
            
            page = 1
            total_pages = None
            
            while True:
                try:
                    # Build parameters
                    params = {
                        'businessUnit': company_domain,
                        'page': page,
                        'sort': sort
                    }
                    
                    if stars:
                        params['stars'] = stars
                    
                    if verified_only:
                        params['verified'] = 'true'
                    
                    print(f"📝 Scraping reviews for {company_domain} (page {page}" +
                          (f"/{total_pages}" if total_pages else "") + ")")
                    
                    response = await self._make_request(api_url, params)
                    review_data = response.json()
                    
                    page_props = review_data.get('pageProps', {})
                    reviews = page_props.get('reviews', [])
                    
                    # Process reviews
                    for review in reviews:
                        processed_review = {
                            'id': review.get('id'),
                            'company_domain': company_domain,
                            'rating': review.get('rating'),
                            'title': review.get('title', ''),
                            'content': review.get('text', ''),
                            'author_name': review.get('consumer', {}).get('displayName'),
                            'author_id': review.get('consumer', {}).get('id'),
                            'verified': review.get('labels', {}).get('verification', {}).get('isVerified', False),
                            'review_date': review.get('dates', {}).get('publishedDate'),
                            'experience_date': review.get('dates', {}).get('experiencedDate'),
                            'company_reply': review.get('reply', {}).get('message') if review.get('reply') else None,
                            'helpful_count': review.get('likes', 0),
                            'scraped_at': datetime.now().isoformat()
                        }
                        all_reviews.append(processed_review)
                    
                    print(f"✅ Scraped {len(reviews)} reviews (total: {len(all_reviews)})")
                    
                    # Check pagination
                    if not total_pages:
                        pagination = page_props.get('filters', {}).get('pagination', {})
                        total_pages = pagination.get('totalPages', 1)
                    
                    # Check if we should continue
                    if page >= total_pages or (max_pages and page >= max_pages):
                        break
                    
                    page += 1
                    
                except Exception as e:
                    print(f"❌ Error scraping page {page}: {e}")
                    break
            
            print(f"🎉 Completed scraping: {len(all_reviews)} total reviews")
            return all_reviews
            
        except Exception as e:
            print(f"❌ Failed to scrape reviews for {company_domain}: {e}")
            raise
    
    async def scrape_category(
        self,
        category: str,
        pages: int = 1,
        min_reviews: int = 0
    ) -> List[Dict]:
        """
        Scrape companies from a category
        
        Args:
            category: Category slug (e.g., 'electronics_technology')
            pages: Number of pages to scrape
            min_reviews: Minimum number of reviews filter
            
        Returns:
            List of company data dictionaries
        """
        results = []
        
        for page in range(1, pages + 1):
            try:
                url = f"{self.BASE_URL}/categories/{category}"
                params = {
                    'page': page,
                    'numberofreviews': min_reviews,
                    'status': 'all'
                }
                
                print(f"📂 Scraping category '{category}' (page {page}/{pages})")
                
                response = await self._make_request(url, params)
                data = self._extract_next_data(response.text)
                
                page_props = data.get('props', {}).get('pageProps', {})
                companies = page_props.get('businessUnits', [])
                
                results.extend(companies)
                print(f"✅ Found {len(companies)} companies on page {page}")
                
            except Exception as e:
                print(f"❌ Failed to scrape category page {page}: {e}")
        
        print(f"📊 Total companies in category: {len(results)}")
        return results
    
    async def scrape_multiple_companies(
        self,
        company_domains: List[str],
        max_pages_per_company: int = 10,
        output_file: Optional[str] = None
    ) -> Dict[str, List[Dict]]:
        """
        Scrape multiple companies concurrently
        
        Args:
            company_domains: List of company domains
            max_pages_per_company: Max pages to scrape per company
            output_file: Optional JSONL output file path
            
        Returns:
            Dictionary mapping company domains to review lists
        """
        semaphore = asyncio.Semaphore(self.max_workers)
        results = {}
        
        async def scrape_with_limit(domain: str):
            async with semaphore:
                try:
                    reviews = await self.monitor.track_request(
                        self.scrape_company_reviews,
                        domain,
                        max_pages=max_pages_per_company
                    )
                    results[domain] = reviews
                    
                    # Write to file if specified
                    if output_file:
                        await self._write_reviews_to_file(domain, reviews, output_file)
                    
                except Exception as e:
                    print(f"❌ Failed to scrape {domain}: {e}")
                    results[domain] = []
        
        # Execute all scraping tasks
        tasks = [scrape_with_limit(domain) for domain in company_domains]
        await asyncio.gather(*tasks)
        
        # Print summary
        stats = self.monitor.get_stats()
        print("\n" + "=" * 50)
        print("📊 SCRAPING SUMMARY")
        print("=" * 50)
        print(f"Success Rate: {stats.get('success_rate', 0):.1%}")
        print(f"Avg Response Time: {stats.get('avg_response_time', 0):.2f}s")
        print(f"Total Reviews: {stats.get('total_reviews', 0)}")
        print(f"Total Requests: {stats.get('total_requests', 0)}")
        print("=" * 50)
        
        return results
    
    async def _write_reviews_to_file(
        self,
        company_domain: str,
        reviews: List[Dict],
        filename: str
    ):
        """Write reviews to JSONL file"""
        import aiofiles
        
        async with aiofiles.open(filename, 'a', encoding='utf-8') as f:
            for review in reviews:
                await f.write(json.dumps(review, ensure_ascii=False) + '\n')


# Convenience functions for quick access
async def scrape_company(domain: str, max_pages: int = 10) -> List[Dict]:
    """Quick function to scrape a single company"""
    scraper = TrustpilotScraper()
    return await scraper.scrape_company_reviews(domain, max_pages=max_pages)


async def search_companies(query: str, pages: int = 1) -> List[Dict]:
    """Quick function to search companies"""
    scraper = TrustpilotScraper()
    return await scraper.search_companies(query, pages=pages)
