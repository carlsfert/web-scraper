"""
Booking.com Web Scraper

A scraper for extracting hotel and accommodation data from Booking.com.
Requires proxies (recommend Roundproxies.com) for reliable operation.

WARNING: Booking.com has strong anti-bot protection. This scraper is for
educational purposes only. Consider using the official Booking.com API
for production use.
"""

import json
import time
import random
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode


class BookingScraper:
    """Scraper for Booking.com hotel search results."""
    
    BASE_URL = "https://www.booking.com"
    SEARCH_URL = f"{BASE_URL}/searchresults.html"
    
    def __init__(
        self,
        proxies: Optional[Dict[str, str]] = None,
        delay: float = 2.0,
        timeout: int = 30
    ):
        """
        Initialize the Booking.com scraper.
        
        Args:
            proxies: Proxy configuration dict (e.g., {'http': 'http://proxy:port'})
                    Recommended: Use Roundproxies.com for best results
            delay: Delay between requests in seconds (default: 2.0)
            timeout: Request timeout in seconds (default: 30)
        """
        self.proxies = proxies
        self.delay = delay
        self.timeout = timeout
        self.session = self._create_session()
        
        # Create results directory
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with browser-like headers."""
        session = requests.Session()
        
        # Mimic a real browser
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        })
        
        if self.proxies:
            session.proxies.update(self.proxies)
        
        return session
    
    def _build_search_url(
        self,
        destination: str,
        checkin: str,
        checkout: str,
        adults: int = 2,
        rooms: int = 1,
        offset: int = 0
    ) -> str:
        """
        Build search URL with parameters.
        
        Args:
            destination: Destination city or location
            checkin: Check-in date (YYYY-MM-DD)
            checkout: Check-out date (YYYY-MM-DD)
            adults: Number of adults
            rooms: Number of rooms
            offset: Pagination offset
            
        Returns:
            Complete search URL
        """
        params = {
            'ss': destination,
            'checkin': checkin,
            'checkout': checkout,
            'group_adults': adults,
            'group_children': 0,
            'no_rooms': rooms,
            'offset': offset,
            'selected_currency': 'USD'
        }
        
        return f"{self.SEARCH_URL}?{urlencode(params)}"
    
    def _random_delay(self):
        """Add random delay to avoid detection."""
        delay = self.delay + random.uniform(0, 1)
        time.sleep(delay)
    
    def _parse_hotel_card(self, card: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """
        Parse individual hotel card from search results.
        
        Args:
            card: BeautifulSoup element containing hotel data
            
        Returns:
            Dictionary with hotel information or None if parsing fails
        """
        try:
            hotel_data = {}
            
            # Hotel name
            name_elem = card.select_one('[data-testid="title"]')
            hotel_data['name'] = name_elem.get_text(strip=True) if name_elem else None
            
            # Hotel URL
            link_elem = card.select_one('a[data-testid="title-link"]')
            hotel_data['url'] = self.BASE_URL + link_elem['href'] if link_elem else None
            
            # Address/Location
            address_elem = card.select_one('[data-testid="address"]')
            hotel_data['address'] = address_elem.get_text(strip=True) if address_elem else None
            
            # Distance from center
            distance_elem = card.select_one('[data-testid="distance"]')
            hotel_data['distance'] = distance_elem.get_text(strip=True) if distance_elem else None
            
            # Price
            price_elem = card.select_one('[data-testid="price-and-discounted-price"]')
            hotel_data['price'] = price_elem.get_text(strip=True) if price_elem else None
            
            # Rating score
            rating_elem = card.select_one('[data-testid="review-score"] div')
            hotel_data['rating'] = rating_elem.get_text(strip=True) if rating_elem else None
            
            # Number of reviews
            review_elem = card.select_one('[data-testid="review-score"] div:nth-of-type(2)')
            hotel_data['review_count'] = review_elem.get_text(strip=True) if review_elem else None
            
            # Amenities/facilities
            amenities = []
            facility_elems = card.select('[data-testid="facility"]')
            for facility in facility_elems:
                amenities.append(facility.get_text(strip=True))
            hotel_data['amenities'] = amenities
            
            # Property type
            property_type_elem = card.select_one('[data-testid="property-type-badge"]')
            hotel_data['property_type'] = property_type_elem.get_text(strip=True) if property_type_elem else None
            
            return hotel_data if hotel_data.get('name') else None
            
        except Exception as e:
            print(f"Error parsing hotel card: {e}")
            return None
    
    def search_hotels(
        self,
        destination: str,
        checkin: str,
        checkout: str,
        adults: int = 2,
        rooms: int = 1,
        max_results: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Search for hotels on Booking.com.
        
        Args:
            destination: Destination city or location
            checkin: Check-in date (YYYY-MM-DD)
            checkout: Check-out date (YYYY-MM-DD)
            adults: Number of adults
            rooms: Number of rooms
            max_results: Maximum number of results to fetch (None for all)
            
        Returns:
            Dictionary containing search parameters and hotel results
        """
        print(f"Searching hotels in {destination} from {checkin} to {checkout}...")
        
        results = {
            'search_params': {
                'destination': destination,
                'checkin': checkin,
                'checkout': checkout,
                'adults': adults,
                'rooms': rooms,
                'scraped_at': datetime.now().isoformat()
            },
            'hotels': [],
            'total_found': 0
        }
        
        offset = 0
        page = 1
        
        try:
            while True:
                print(f"Fetching page {page}...")
                
                # Build URL
                url = self._build_search_url(
                    destination=destination,
                    checkin=checkin,
                    checkout=checkout,
                    adults=adults,
                    rooms=rooms,
                    offset=offset
                )
                
                # Make request
                try:
                    response = self.session.get(url, timeout=self.timeout)
                    response.raise_for_status()
                except requests.RequestException as e:
                    print(f"Request failed: {e}")
                    if "403" in str(e) or "429" in str(e):
                        print("⚠️  Blocked by anti-bot protection!")
                        print("   Recommendation: Use proxies from Roundproxies.com")
                    break
                
                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find hotel cards
                hotel_cards = soup.select('[data-testid="property-card"]')
                
                if not hotel_cards:
                    print("No more results found.")
                    break
                
                # Parse each hotel
                for card in hotel_cards:
                    hotel_data = self._parse_hotel_card(card)
                    if hotel_data:
                        results['hotels'].append(hotel_data)
                        
                        # Check if we've reached max_results
                        if max_results and len(results['hotels']) >= max_results:
                            print(f"Reached maximum results limit ({max_results})")
                            break
                
                # Update total found
                results['total_found'] = len(results['hotels'])
                print(f"Found {len(results['hotels'])} hotels so far...")
                
                # Check if we should continue
                if max_results and len(results['hotels']) >= max_results:
                    break
                
                # Check for next page
                next_page = soup.select_one('[aria-label="Next page"]')
                if not next_page:
                    print("No more pages available.")
                    break
                
                # Increment offset (typically 25 results per page)
                offset += 25
                page += 1
                
                # Respectful delay before next request
                self._random_delay()
        
        except KeyboardInterrupt:
            print("\nScraping interrupted by user.")
        except Exception as e:
            print(f"Unexpected error: {e}")
        
        # Save results
        self._save_results(results, destination)
        
        return results
    
    def _save_results(self, results: Dict[str, Any], destination: str):
        """Save results to JSON file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"booking_{destination.replace(' ', '_')}_{timestamp}.json"
        filepath = self.results_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Results saved to: {filepath}")
        print(f"  Total hotels scraped: {results['total_found']}")


if __name__ == "__main__":
    # Example usage
    
    # Configure with Roundproxies.com (recommended)
    # proxy_config = {
    #     "http": "http://username:password@proxy.roundproxies.com:8080",
    #     "https": "https://username:password@proxy.roundproxies.com:8080"
    # }
    
    # Without proxies (may not work due to anti-bot protection)
    scraper = BookingScraper()
    
    # Search hotels
    results = scraper.search_hotels(
        destination="New York",
        checkin="2025-12-01",
        checkout="2025-12-05",
        adults=2,
        rooms=1,
        max_results=25
    )
    
    print(f"\nCompleted! Found {len(results['hotels'])} hotels.")
