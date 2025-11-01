"""
Amazon Scraper - Main Module

This module provides functions to scrape various data from Amazon including:
- Product search results
- Product details (price, title, description, images, etc.)
- Product reviews and ratings
- Best sellers in categories
"""

import asyncio
import json
import re
from typing import Dict, List, Optional
from urllib.parse import urljoin, quote_plus
from playwright.async_api import async_playwright, Page, Browser
from bs4 import BeautifulSoup


class AmazonScraper:
    """Main scraper class for Amazon data extraction."""
    
    def __init__(self, domain: str = "com", headless: bool = True):
        """
        Initialize the Amazon scraper.
        
        Args:
            domain: Amazon domain (com, co.uk, de, etc.)
            headless: Whether to run browser in headless mode
        """
        self.domain = domain
        self.base_url = f"https://www.amazon.{domain}"
        self.headless = headless
        self.browser: Optional[Browser] = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
        
    async def start(self):
        """Start the browser instance."""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        
    async def close(self):
        """Close the browser instance."""
        if self.browser:
            await self.browser.close()
            
    async def _setup_page(self, page: Page):
        """
        Configure page with anti-detection measures.
        
        Args:
            page: Playwright page instance
        """
        # Set realistic viewport
        await page.set_viewport_size({"width": 1920, "height": 1080})
        
        # Hide automation signals
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            window.chrome = {
                runtime: {}
            };
        """)
        
    async def search_products(
        self, 
        query: str, 
        max_pages: int = 1,
        max_results: Optional[int] = None
    ) -> List[Dict]:
        """
        Search for products on Amazon.
        
        Args:
            query: Search query string
            max_pages: Maximum number of pages to scrape
            max_results: Maximum number of results to return
            
        Returns:
            List of product dictionaries
        """
        if not self.browser:
            raise RuntimeError("Browser not started. Use async context manager or call start().")
            
        context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        await self._setup_page(page)
        
        all_products = []
        
        for page_num in range(1, max_pages + 1):
            print(f"Scraping search results page {page_num} for: {query}")
            
            # Build search URL
            search_url = f"{self.base_url}/s?k={quote_plus(query)}&page={page_num}"
            
            try:
                await page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
                await asyncio.sleep(2)
                
                # Wait for search results
                try:
                    await page.wait_for_selector('[data-component-type="s-search-result"]', timeout=10000)
                except:
                    print(f"No results found on page {page_num}")
                    break
                
                content = await page.content()
                soup = BeautifulSoup(content, 'lxml')
                
                # Find product cards
                products = soup.select('[data-component-type="s-search-result"]')
                
                if not products:
                    print(f"No products found on page {page_num}")
                    break
                
                for product in products:
                    try:
                        # Extract ASIN
                        asin = product.get('data-asin', '')
                        if not asin:
                            continue
                        
                        # Extract title
                        title_elem = product.select_one('h2 a span')
                        title = title_elem.text.strip() if title_elem else ''
                        
                        # Extract price
                        price = ''
                        price_elem = product.select_one('.a-price .a-offscreen')
                        if price_elem:
                            price = price_elem.text.strip()
                        
                        # Extract rating
                        rating = ''
                        rating_elem = product.select_one('[aria-label*="out of 5 stars"]')
                        if rating_elem:
                            rating_text = rating_elem.get('aria-label', '')
                            rating_match = re.search(r'([\d.]+)\s+out of', rating_text)
                            if rating_match:
                                rating = rating_match.group(1)
                        
                        # Extract review count
                        reviews = ''
                        reviews_elem = product.select_one('[aria-label*="stars"]')
                        if reviews_elem:
                            reviews_text = reviews_elem.get('aria-label', '')
                            reviews_match = re.search(r'([\d,]+)\s+rating', reviews_text)
                            if reviews_match:
                                reviews = reviews_match.group(1)
                        
                        # Extract image URL
                        image_url = ''
                        image_elem = product.select_one('img.s-image')
                        if image_elem:
                            image_url = image_elem.get('src', '')
                        
                        # Build product URL
                        product_url = f"{self.base_url}/dp/{asin}"
                        
                        product_data = {
                            'asin': asin,
                            'title': title,
                            'price': price,
                            'rating': rating,
                            'reviews_count': reviews,
                            'image_url': image_url,
                            'url': product_url,
                            'search_query': query
                        }
                        
                        all_products.append(product_data)
                        
                        if max_results and len(all_products) >= max_results:
                            break
                            
                    except Exception as e:
                        print(f"Error parsing product: {str(e)}")
                        continue
                
                if max_results and len(all_products) >= max_results:
                    break
                    
            except Exception as e:
                print(f"Error on page {page_num}: {str(e)}")
                break
        
        await context.close()
        
        if max_results:
            return all_products[:max_results]
        return all_products
    
    async def get_product_details(self, asin: str) -> Dict:
        """
        Get detailed information about a specific product.
        
        Args:
            asin: Amazon Standard Identification Number
            
        Returns:
            Dictionary containing detailed product information
        """
        if not self.browser:
            raise RuntimeError("Browser not started. Use async context manager or call start().")
            
        context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = await context.new_page()
        await self._setup_page(page)
        
        product_url = f"{self.base_url}/dp/{asin}"
        print(f"Scraping product: {product_url}")
        
        try:
            await page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(2)
            
            content = await page.content()
            soup = BeautifulSoup(content, 'lxml')
            
            # Extract title
            title = ''
            title_elem = soup.select_one('#productTitle')
            if title_elem:
                title = title_elem.text.strip()
            
            # Extract price
            price = ''
            price_elem = soup.select_one('.a-price .a-offscreen')
            if not price_elem:
                price_elem = soup.select_one('#priceblock_ourprice')
            if price_elem:
                price = price_elem.text.strip()
            
            # Extract rating
            rating = ''
            rating_elem = soup.select_one('[data-hook="rating-out-of-text"]')
            if rating_elem:
                rating_text = rating_elem.text.strip()
                rating_match = re.search(r'([\d.]+)', rating_text)
                if rating_match:
                    rating = rating_match.group(1)
            
            # Extract review count
            reviews_count = ''
            reviews_elem = soup.select_one('#acrCustomerReviewText')
            if reviews_elem:
                reviews_text = reviews_elem.text.strip()
                reviews_match = re.search(r'([\d,]+)', reviews_text)
                if reviews_match:
                    reviews_count = reviews_match.group(1)
            
            # Extract description
            description = ''
            desc_elem = soup.select_one('#feature-bullets')
            if desc_elem:
                bullets = desc_elem.select('li')
                description = ' '.join([b.text.strip() for b in bullets])
            
            # Extract brand
            brand = ''
            brand_elem = soup.select_one('#bylineInfo')
            if brand_elem:
                brand = brand_elem.text.strip().replace('Visit the ', '').replace(' Store', '')
            
            # Extract availability
            availability = ''
            avail_elem = soup.select_one('#availability')
            if avail_elem:
                availability = avail_elem.text.strip()
            
            # Extract images
            images = []
            image_elems = soup.select('#altImages img')
            for img in image_elems[:5]:  # Limit to 5 images
                img_url = img.get('src', '')
                if img_url and 'sprite' not in img_url:
                    # Get higher resolution version
                    img_url = re.sub(r'_[A-Z]{2}\d+_', '_SL1500_', img_url)
                    images.append(img_url)
            
            # Extract categories
            categories = []
            crumb_elems = soup.select('#wayfinding-breadcrumbs_feature_div .a-list-item a')
            for crumb in crumb_elems:
                categories.append(crumb.text.strip())
            
            # Extract product details/specifications
            specifications = {}
            spec_table = soup.select_one('#productDetails_techSpec_section_1')
            if spec_table:
                rows = spec_table.select('tr')
                for row in rows:
                    th = row.select_one('th')
                    td = row.select_one('td')
                    if th and td:
                        key = th.text.strip()
                        value = td.text.strip()
                        specifications[key] = value
            
            product_data = {
                'asin': asin,
                'title': title,
                'price': price,
                'rating': rating,
                'reviews_count': reviews_count,
                'description': description,
                'brand': brand,
                'availability': availability,
                'images': images,
                'categories': categories,
                'specifications': specifications,
                'url': product_url
            }
            
        except Exception as e:
            print(f"Error scraping product {asin}: {str(e)}")
            product_data = {'asin': asin, 'error': str(e)}
        
        await context.close()
        return product_data
    
    async def get_product_reviews(
        self, 
        asin: str, 
        max_reviews: Optional[int] = None,
        max_pages: int = 1
    ) -> List[Dict]:
        """
        Get reviews for a specific product.
        
        Args:
            asin: Amazon Standard Identification Number
            max_reviews: Maximum number of reviews to scrape
            max_pages: Maximum number of review pages to scrape
            
        Returns:
            List of review dictionaries
        """
        if not self.browser:
            raise RuntimeError("Browser not started. Use async context manager or call start().")
            
        context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()
        await self._setup_page(page)
        
        all_reviews = []
        
        for page_num in range(1, max_pages + 1):
            reviews_url = f"{self.base_url}/product-reviews/{asin}?pageNumber={page_num}"
            print(f"Scraping reviews page {page_num} for ASIN: {asin}")
            
            try:
                await page.goto(reviews_url, wait_until='domcontentloaded', timeout=30000)
                await asyncio.sleep(2)
                
                content = await page.content()
                soup = BeautifulSoup(content, 'lxml')
                
                # Find review cards
                review_cards = soup.select('[data-hook="review"]')
                
                if not review_cards:
                    print(f"No reviews found on page {page_num}")
                    break
                
                for review in review_cards:
                    try:
                        # Extract review ID
                        review_id = review.get('id', '')
                        
                        # Extract rating
                        rating = ''
                        rating_elem = review.select_one('[data-hook="review-star-rating"]')
                        if rating_elem:
                            rating_text = rating_elem.text.strip()
                            rating_match = re.search(r'([\d.]+)', rating_text)
                            if rating_match:
                                rating = rating_match.group(1)
                        
                        # Extract title
                        title = ''
                        title_elem = review.select_one('[data-hook="review-title"]')
                        if title_elem:
                            title_span = title_elem.select_one('span:not(.a-icon-alt)')
                            if title_span:
                                title = title_span.text.strip()
                        
                        # Extract review text
                        text = ''
                        text_elem = review.select_one('[data-hook="review-body"]')
                        if text_elem:
                            text = text_elem.text.strip()
                        
                        # Extract reviewer name
                        reviewer = ''
                        reviewer_elem = review.select_one('.a-profile-name')
                        if reviewer_elem:
                            reviewer = reviewer_elem.text.strip()
                        
                        # Extract review date
                        date = ''
                        date_elem = review.select_one('[data-hook="review-date"]')
                        if date_elem:
                            date = date_elem.text.strip()
                        
                        # Extract verified purchase
                        verified = False
                        verified_elem = review.select_one('[data-hook="avp-badge"]')
                        if verified_elem:
                            verified = True
                        
                        # Extract helpful count
                        helpful = ''
                        helpful_elem = review.select_one('[data-hook="helpful-vote-statement"]')
                        if helpful_elem:
                            helpful = helpful_elem.text.strip()
                        
                        review_data = {
                            'review_id': review_id,
                            'rating': rating,
                            'title': title,
                            'text': text,
                            'reviewer': reviewer,
                            'date': date,
                            'verified_purchase': verified,
                            'helpful_count': helpful,
                            'asin': asin
                        }
                        
                        all_reviews.append(review_data)
                        
                        if max_reviews and len(all_reviews) >= max_reviews:
                            break
                            
                    except Exception as e:
                        print(f"Error parsing review: {str(e)}")
                        continue
                
                if max_reviews and len(all_reviews) >= max_reviews:
                    break
                    
            except Exception as e:
                print(f"Error on reviews page {page_num}: {str(e)}")
                break
        
        await context.close()
        
        if max_reviews:
            return all_reviews[:max_reviews]
        return all_reviews


# Convenience functions for standalone use
async def search_products(query: str, max_pages: int = 1, domain: str = "com") -> List[Dict]:
    """Standalone function to search Amazon products."""
    async with AmazonScraper(domain=domain) as scraper:
        return await scraper.search_products(query, max_pages=max_pages)


async def get_product_details(asin: str, domain: str = "com") -> Dict:
    """Standalone function to get product details."""
    async with AmazonScraper(domain=domain) as scraper:
        return await scraper.get_product_details(asin)


async def get_product_reviews(asin: str, max_pages: int = 1, domain: str = "com") -> List[Dict]:
    """Standalone function to get product reviews."""
    async with AmazonScraper(domain=domain) as scraper:
        return await scraper.get_product_reviews(asin, max_pages=max_pages)
