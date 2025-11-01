"""
eBay Web Scraper
A scraper for extracting product data from eBay search results.
Designed to work with Roundproxies.com rotating proxies.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import os
from datetime import datetime
from typing import List, Dict, Optional
import re


class EbayScraper:
    """
    eBay product scraper with proxy support.
    """
    
    def __init__(
        self,
        proxies: Optional[Dict[str, str]] = None,
        delay: float = 2.0,
        timeout: int = 30
    ):
        """
        Initialize the eBay scraper.
        
        Args:
            proxies: Dictionary with proxy configuration
                    {'http': 'http://user:pass@proxy:port', 'https': '...'}
            delay: Delay between requests in seconds (default: 2.0)
            timeout: Request timeout in seconds (default: 30)
        """
        self.proxies = proxies
        self.delay = delay
        self.timeout = timeout
        self.base_url = "https://www.ebay.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Create results directory if it doesn't exist
        os.makedirs('results', exist_ok=True)
    
    def search(
        self,
        query: str,
        max_pages: int = 1,
        condition: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> List[Dict]:
        """
        Search for products on eBay.
        
        Args:
            query: Search query string
            max_pages: Maximum number of pages to scrape
            condition: Filter by condition ('new', 'used', 'refurbished')
            min_price: Minimum price filter
            max_price: Maximum price filter
            
        Returns:
            List of product dictionaries
        """
        all_results = []
        
        for page in range(1, max_pages + 1):
            print(f"Scraping page {page}/{max_pages}...")
            
            # Build search URL
            url = self._build_search_url(query, page, condition, min_price, max_price)
            
            try:
                # Make request
                response = self._make_request(url)
                
                if response.status_code == 200:
                    # Parse products
                    products = self._parse_search_results(response.text)
                    all_results.extend(products)
                    print(f"Found {len(products)} products on page {page}")
                else:
                    print(f"Error: Received status code {response.status_code} on page {page}")
                    
            except Exception as e:
                print(f"Error scraping page {page}: {str(e)}")
            
            # Delay between requests
            if page < max_pages:
                time.sleep(self.delay)
        
        # Save results
        self._save_results(all_results, query)
        
        return all_results
    
    def _build_search_url(
        self,
        query: str,
        page: int,
        condition: Optional[str],
        min_price: Optional[float],
        max_price: Optional[float]
    ) -> str:
        """Build the search URL with parameters."""
        # Base search URL
        url = f"{self.base_url}/sch/i.html?_nkw={query.replace(' ', '+')}"
        
        # Add pagination
        if page > 1:
            url += f"&_pgn={page}"
        
        # Add condition filter
        if condition:
            condition_map = {
                'new': '1000',
                'used': '3000',
                'refurbished': '2000'
            }
            if condition.lower() in condition_map:
                url += f"&LH_ItemCondition={condition_map[condition.lower()]}"
        
        # Add price filters
        if min_price:
            url += f"&_udlo={min_price}"
        if max_price:
            url += f"&_udhi={max_price}"
        
        # Sort by best match
        url += "&_sop=12"
        
        return url
    
    def _make_request(self, url: str) -> requests.Response:
        """
        Make HTTP request with proxy and error handling.
        
        Args:
            url: URL to request
            
        Returns:
            Response object
        """
        try:
            response = requests.get(
                url,
                headers=self.headers,
                proxies=self.proxies,
                timeout=self.timeout
            )
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
            raise
    
    def _parse_search_results(self, html: str) -> List[Dict]:
        """
        Parse product data from search results HTML.
        
        Args:
            html: HTML content of search results page
            
        Returns:
            List of product dictionaries
        """
        soup = BeautifulSoup(html, 'lxml')
        products = []
        
        # Find all product listings
        items = soup.find_all('div', {'class': 's-item__info'})
        
        for item in items:
            try:
                product = self._extract_product_data(item)
                if product:
                    products.append(product)
            except Exception as e:
                print(f"Error parsing product: {str(e)}")
                continue
        
        return products
    
    def _extract_product_data(self, item) -> Optional[Dict]:
        """
        Extract product information from a listing element.
        
        Args:
            item: BeautifulSoup element containing product data
            
        Returns:
            Dictionary with product information or None
        """
        try:
            # Title
            title_elem = item.find('div', {'class': 's-item__title'})
            title = title_elem.get_text(strip=True) if title_elem else None
            
            # Skip if no title or if it's a header
            if not title or title.lower() in ['shop on ebay', 'new listing']:
                return None
            
            # URL
            link_elem = item.find_parent('div', {'class': 's-item__wrapper'})
            url = None
            if link_elem:
                link = link_elem.find('a', {'class': 's-item__link'})
                url = link.get('href') if link else None
            
            # Price
            price_elem = item.find('span', {'class': 's-item__price'})
            price = price_elem.get_text(strip=True) if price_elem else None
            
            # Extract currency and numeric price
            currency = None
            price_numeric = None
            if price:
                currency_match = re.search(r'([A-Z]{3}|\$|€|£)', price)
                currency = currency_match.group(1) if currency_match else 'USD'
                price_match = re.search(r'[\d,]+\.?\d*', price)
                if price_match:
                    price_numeric = float(price_match.group().replace(',', ''))
            
            # Condition
            condition_elem = item.find('span', {'class': 'SECONDARY_INFO'})
            condition = condition_elem.get_text(strip=True) if condition_elem else None
            
            # Shipping
            shipping_elem = item.find('span', {'class': 's-item__shipping'})
            shipping = shipping_elem.get_text(strip=True) if shipping_elem else None
            
            # Location
            location_elem = item.find('span', {'class': 's-item__location'})
            location = location_elem.get_text(strip=True) if location_elem else None
            
            # Seller info
            seller_elem = item.find('span', {'class': 's-item__seller-info-text'})
            seller = seller_elem.get_text(strip=True) if seller_elem else None
            
            # Bids/Watchers
            bids_elem = item.find('span', {'class': 's-item__bids'})
            bids = bids_elem.get_text(strip=True) if bids_elem else None
            
            watchers_elem = item.find('span', {'class': 's-item__watchcount'})
            watchers = watchers_elem.get_text(strip=True) if watchers_elem else None
            
            # Image
            image_url = None
            image_wrapper = item.find_parent('div', {'class': 's-item__wrapper'})
            if image_wrapper:
                img_elem = image_wrapper.find('img', {'class': 's-item__image-img'})
                if img_elem:
                    image_url = img_elem.get('src')
            
            # Build product dictionary
            product = {
                'title': title,
                'price': price,
                'price_numeric': price_numeric,
                'currency': currency,
                'condition': condition,
                'url': url,
                'image_url': image_url,
                'seller': seller,
                'shipping': shipping,
                'location': location,
                'bids': bids,
                'watchers': watchers,
                'timestamp': datetime.now().isoformat()
            }
            
            return product
            
        except Exception as e:
            print(f"Error extracting product data: {str(e)}")
            return None
    
    def _save_results(self, results: List[Dict], query: str):
        """
        Save results to JSON file.
        
        Args:
            results: List of product dictionaries
            query: Original search query (used in filename)
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_query = re.sub(r'[^\w\s-]', '', query).strip().replace(' ', '_')
        filename = f"results/ebay_{safe_query}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\nResults saved to {filename}")
        print(f"Total products scraped: {len(results)}")
    
    def get_product_details(self, product_url: str) -> Dict:
        """
        Scrape detailed information from a product page.
        
        Args:
            product_url: URL of the product page
            
        Returns:
            Dictionary with detailed product information
        """
        try:
            response = self._make_request(product_url)
            
            if response.status_code != 200:
                return {'error': f'Status code: {response.status_code}'}
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Extract detailed information
            details = {
                'url': product_url,
                'title': self._safe_extract(soup, 'h1', {'class': 'x-item-title__mainTitle'}),
                'price': self._safe_extract(soup, 'div', {'class': 'x-price-primary'}),
                'condition': self._safe_extract(soup, 'div', {'class': 'x-item-condition'}),
                'description': self._safe_extract(soup, 'div', {'class': 'x-item-description'}),
                'seller': self._safe_extract(soup, 'span', {'class': 'ux-seller-section__item--seller'}),
                'seller_feedback': self._safe_extract(soup, 'span', {'class': 'ux-seller-section__item--seller'}),
                'timestamp': datetime.now().isoformat()
            }
            
            return details
            
        except Exception as e:
            return {'error': str(e)}
    
    def _safe_extract(self, soup, tag: str, attrs: Dict) -> Optional[str]:
        """Safely extract text from HTML element."""
        elem = soup.find(tag, attrs)
        return elem.get_text(strip=True) if elem else None


if __name__ == "__main__":
    # Example usage
    scraper = EbayScraper()
    results = scraper.search("laptop", max_pages=2)
    print(f"Scraped {len(results)} products")
