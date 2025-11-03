"""
Alibaba.com Web Scraper
Extracts product data from Alibaba search results and product pages.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
import csv
from typing import List, Dict, Optional
from urllib.parse import urljoin, quote_plus
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AlibabaScraper:
    """
    A scraper for Alibaba.com that extracts product information.
    
    Note: Alibaba has strong anti-scraping measures. Use proxies and rate limiting.
    """
    
    BASE_URL = "https://www.alibaba.com"
    SEARCH_URL = "https://www.alibaba.com/trade/search"
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    
    def __init__(self, proxies: Optional[Dict] = None, delay: tuple = (2, 5)):
        """
        Initialize the Alibaba scraper.
        
        Args:
            proxies: Dictionary with proxy configuration
            delay: Tuple (min, max) for random delay between requests in seconds
        """
        self.proxies = proxies
        self.delay = delay
        self.session = requests.Session()
        
    def _get_headers(self) -> Dict:
        """Generate headers with random user agent."""
        return {
            'User-Agent': random.choice(self.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
    
    def _random_delay(self):
        """Add random delay between requests."""
        time.sleep(random.uniform(self.delay[0], self.delay[1]))
    
    def _make_request(self, url: str, params: Optional[Dict] = None) -> Optional[requests.Response]:
        """
        Make HTTP request with error handling.
        
        Args:
            url: URL to request
            params: Query parameters
            
        Returns:
            Response object or None if failed
        """
        try:
            response = self.session.get(
                url,
                params=params,
                headers=self._get_headers(),
                proxies=self.proxies,
                timeout=30
            )
            
            if response.status_code == 200:
                return response
            elif response.status_code == 403:
                logger.warning("Access forbidden (403). Proxy or IP may be blocked.")
            elif response.status_code == 429:
                logger.warning("Rate limited (429). Waiting 60 seconds...")
                time.sleep(60)
            else:
                logger.warning(f"Request failed with status code: {response.status_code}")
                
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return None
    
    def search_products(self, keyword: str, max_pages: int = 1) -> List[Dict]:
        """
        Search for products on Alibaba.
        
        Args:
            keyword: Search keyword
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of product dictionaries
        """
        logger.info(f"Searching for '{keyword}' on Alibaba (max {max_pages} pages)...")
        all_products = []
        
        for page in range(1, max_pages + 1):
            logger.info(f"Scraping page {page}/{max_pages}...")
            
            params = {
                'fsb': 'y',
                'IndexArea': 'product_en',
                'CatId': '',
                'SearchText': keyword,
                'viewtype': 'G',
                'page': page
            }
            
            response = self._make_request(self.SEARCH_URL, params)
            
            if response is None:
                logger.warning(f"Failed to fetch page {page}. Stopping.")
                break
            
            products = self._parse_search_results(response.text)
            
            if not products:
                logger.info("No more products found. Stopping.")
                break
            
            all_products.extend(products)
            logger.info(f"Found {len(products)} products on page {page}")
            
            # Add delay before next page
            if page < max_pages:
                self._random_delay()
        
        logger.info(f"Total products scraped: {len(all_products)}")
        return all_products
    
    def _parse_search_results(self, html: str) -> List[Dict]:
        """
        Parse product data from search results page.
        
        Args:
            html: HTML content of search results
            
        Returns:
            List of product dictionaries
        """
        products = []
        soup = BeautifulSoup(html, 'lxml')
        
        # Try to find products in different possible structures
        # Alibaba's HTML structure may vary
        product_cards = (
            soup.find_all('div', class_='organic-list-offer') or
            soup.find_all('div', {'data-content': 'true'}) or
            soup.find_all('div', class_='m-gallery-product-item-wrap')
        )
        
        for card in product_cards:
            try:
                product = self._extract_product_data(card)
                if product:
                    products.append(product)
            except Exception as e:
                logger.debug(f"Error parsing product card: {str(e)}")
                continue
        
        # Try alternative: look for JSON data in script tags
        if not products:
            products = self._extract_from_json(html)
        
        return products
    
    def _extract_product_data(self, card) -> Optional[Dict]:
        """
        Extract product data from a product card element.
        
        Args:
            card: BeautifulSoup element containing product card
            
        Returns:
            Dictionary with product data or None
        """
        product = {}
        
        # Title
        title_elem = (
            card.find('h2', class_='search-card-e-title') or
            card.find('a', class_='organic-list-offer-outter') or
            card.find('a', {'class': lambda x: x and 'title' in x.lower() if x else False})
        )
        product['title'] = title_elem.get_text(strip=True) if title_elem else 'N/A'
        
        # URL
        link_elem = card.find('a', href=True)
        if link_elem and link_elem.get('href'):
            product['url'] = urljoin(self.BASE_URL, link_elem['href'])
        else:
            product['url'] = 'N/A'
        
        # Price
        price_elem = (
            card.find('span', class_='search-card-e-price-main') or
            card.find('div', class_='price') or
            card.find('span', {'class': lambda x: x and 'price' in x.lower() if x else False})
        )
        product['price'] = price_elem.get_text(strip=True) if price_elem else 'N/A'
        
        # MOQ (Minimum Order Quantity)
        moq_elem = (
            card.find('span', class_='search-card-e-moq') or
            card.find('div', {'class': lambda x: x and 'moq' in x.lower() if x else False})
        )
        product['moq'] = moq_elem.get_text(strip=True) if moq_elem else 'N/A'
        
        # Supplier
        supplier_elem = (
            card.find('a', class_='search-card-e-company') or
            card.find('div', class_='supplier') or
            card.find('span', {'class': lambda x: x and 'company' in x.lower() if x else False})
        )
        product['supplier'] = supplier_elem.get_text(strip=True) if supplier_elem else 'N/A'
        
        # Image
        img_elem = card.find('img', {'src': True})
        product['image_url'] = img_elem['src'] if img_elem else 'N/A'
        
        # Orders/Sales
        orders_elem = card.find('span', {'class': lambda x: x and 'order' in x.lower() if x else False})
        product['orders'] = orders_elem.get_text(strip=True) if orders_elem else 'N/A'
        
        return product if product.get('title') != 'N/A' else None
    
    def _extract_from_json(self, html: str) -> List[Dict]:
        """
        Try to extract product data from embedded JSON in script tags.
        
        Args:
            html: HTML content
            
        Returns:
            List of product dictionaries
        """
        products = []
        soup = BeautifulSoup(html, 'lxml')
        
        # Look for script tags containing JSON data
        script_tags = soup.find_all('script', type='application/json')
        
        for script in script_tags:
            try:
                data = json.loads(script.string)
                # Navigate through possible JSON structures
                # This is highly dependent on Alibaba's actual structure
                if isinstance(data, dict):
                    # Try to find product arrays in the JSON
                    products_data = self._find_products_in_json(data)
                    if products_data:
                        products.extend(products_data)
            except (json.JSONDecodeError, AttributeError):
                continue
        
        return products
    
    def _find_products_in_json(self, data, products=None) -> List[Dict]:
        """
        Recursively search for product data in JSON structure.
        
        Args:
            data: JSON data structure
            products: Accumulator for products
            
        Returns:
            List of product dictionaries
        """
        if products is None:
            products = []
        
        if isinstance(data, dict):
            # Check if this dict looks like a product
            if 'title' in data or 'subject' in data or 'productTitle' in data:
                product = {
                    'title': data.get('title') or data.get('subject') or data.get('productTitle', 'N/A'),
                    'price': data.get('price') or data.get('priceInfo', 'N/A'),
                    'moq': data.get('moq') or data.get('minOrderQuantity', 'N/A'),
                    'supplier': data.get('supplier') or data.get('companyName', 'N/A'),
                    'url': data.get('url') or data.get('link', 'N/A'),
                    'image_url': data.get('image') or data.get('imageUrl', 'N/A'),
                    'orders': data.get('orders') or data.get('salesCount', 'N/A')
                }
                products.append(product)
            
            # Recursively search nested dicts
            for value in data.values():
                self._find_products_in_json(value, products)
        
        elif isinstance(data, list):
            # Recursively search list items
            for item in data:
                self._find_products_in_json(item, products)
        
        return products
    
    def get_product_details(self, product_url: str) -> Optional[Dict]:
        """
        Scrape detailed information from a product page.
        
        Args:
            product_url: URL of the product page
            
        Returns:
            Dictionary with detailed product information or None
        """
        logger.info(f"Fetching product details from: {product_url}")
        
        response = self._make_request(product_url)
        if response is None:
            return None
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        details = {
            'url': product_url,
            'title': 'N/A',
            'description': 'N/A',
            'price': 'N/A',
            'specifications': {}
        }
        
        # Extract title
        title = soup.find('h1', class_='product-title') or soup.find('h1')
        if title:
            details['title'] = title.get_text(strip=True)
        
        # Extract description
        desc = soup.find('div', class_='description') or soup.find('div', {'data-role': 'description'})
        if desc:
            details['description'] = desc.get_text(strip=True)[:500]  # Limit length
        
        # Extract specifications
        spec_table = soup.find('table', class_='product-property')
        if spec_table:
            rows = spec_table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    details['specifications'][key] = value
        
        self._random_delay()
        return details
    
    def save_to_csv(self, products: List[Dict], filename: str):
        """
        Save products to CSV file.
        
        Args:
            products: List of product dictionaries
            filename: Output CSV filename
        """
        if not products:
            logger.warning("No products to save.")
            return
        
        # Get all unique keys from all products
        all_keys = set()
        for product in products:
            all_keys.update(product.keys())
        
        fieldnames = sorted(all_keys)
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(products)
            
            logger.info(f"Saved {len(products)} products to {filename}")
        except IOError as e:
            logger.error(f"Error saving to CSV: {str(e)}")


if __name__ == "__main__":
    # Example usage
    scraper = AlibabaScraper()
    
    # Search for products
    products = scraper.search_products("laptop", max_pages=2)
    
    # Save results
    if products:
        scraper.save_to_csv(products, "results/alibaba_products.csv")
        print(f"\nScraped {len(products)} products:")
        for i, product in enumerate(products[:5], 1):
            print(f"\n{i}. {product.get('title', 'N/A')}")
            print(f"   Price: {product.get('price', 'N/A')}")
            print(f"   Supplier: {product.get('supplier', 'N/A')}")
