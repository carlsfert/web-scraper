"""
SeatGeek Web Scraper
Provided by Roundproxies.com
https://github.com/carlsfert/web-scraper/tree/main/websites/seatgeek-scraper
"""

import requests
import json
import time
import random
from datetime import datetime
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote


class SeatGeekScraper:
    """
    Web scraper for SeatGeek event data
    """
    
    BASE_URL = "https://seatgeek.com"
    API_URL = "https://api.seatgeek.com/2"
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the SeatGeek scraper
        
        Args:
            config: Configuration dictionary with scraper settings
        """
        self.config = config or {}
        self.proxy_enabled = self.config.get('proxy_enabled', False)
        self.proxy_list = self.config.get('proxy_list', [])
        self.delay_min = self.config.get('delay_min', 3)
        self.delay_max = self.config.get('delay_max', 7)
        self.user_agents = self._load_user_agents()
        self.session = requests.Session()
        self.results = []
        
    def _load_user_agents(self) -> List[str]:
        """Load a list of user agents for rotation"""
        return [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
    
    def _get_random_user_agent(self) -> str:
        """Get a random user agent from the list"""
        return random.choice(self.user_agents)
    
    def _get_proxy(self) -> Optional[Dict]:
        """Get a random proxy from the proxy list"""
        if self.proxy_enabled and self.proxy_list:
            proxy = random.choice(self.proxy_list)
            return {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
        return None
    
    def _delay(self):
        """Add random delay between requests"""
        delay = random.uniform(self.delay_min, self.delay_max)
        time.sleep(delay)
    
    def _make_request(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        """
        Make HTTP request with error handling and retry logic
        
        Args:
            url: URL to request
            method: HTTP method (GET, POST, etc.)
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object or None if failed
        """
        headers = kwargs.pop('headers', {})
        headers['User-Agent'] = self._get_random_user_agent()
        
        proxies = self._get_proxy()
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    proxies=proxies,
                    timeout=30,
                    **kwargs
                )
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:
                    print(f"Rate limited. Waiting before retry...")
                    time.sleep(60)
                elif response.status_code in [403, 401]:
                    print(f"Access denied (status {response.status_code}). Rotating proxy...")
                    proxies = self._get_proxy()
                else:
                    print(f"Request failed with status {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"Request error (attempt {attempt + 1}/{max_retries}): {e}")
                
            if attempt < max_retries - 1:
                self._delay()
        
        return None
    
    def scrape_events(self, 
                     category: Optional[str] = None,
                     location: Optional[str] = None,
                     date_from: Optional[str] = None,
                     date_to: Optional[str] = None,
                     limit: int = 50) -> List[Dict]:
        """
        Scrape events from SeatGeek
        
        Args:
            category: Event category (concerts, sports, theater, etc.)
            location: City or venue location
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            limit: Maximum number of events to scrape
            
        Returns:
            List of event dictionaries
        """
        print(f"Starting SeatGeek scraper...")
        print(f"Category: {category}, Location: {location}, Limit: {limit}")
        
        events = []
        
        # Build search URL
        search_url = self._build_search_url(category, location, date_from, date_to)
        
        # Scrape events
        page = 1
        while len(events) < limit:
            print(f"Scraping page {page}...")
            
            page_url = f"{search_url}&page={page}"
            response = self._make_request(page_url)
            
            if not response:
                print("Failed to fetch page. Stopping.")
                break
            
            page_events = self._parse_events_page(response.text)
            
            if not page_events:
                print("No more events found.")
                break
            
            events.extend(page_events)
            print(f"Found {len(page_events)} events on page {page}. Total: {len(events)}")
            
            if len(events) >= limit:
                events = events[:limit]
                break
            
            page += 1
            self._delay()
        
        self.results = events
        print(f"Scraping complete. Total events: {len(events)}")
        return events
    
    def _build_search_url(self, category: Optional[str], location: Optional[str],
                         date_from: Optional[str], date_to: Optional[str]) -> str:
        """Build search URL with parameters"""
        url = f"{self.BASE_URL}/browse"
        
        params = []
        if category:
            params.append(f"type={quote(category)}")
        if location:
            params.append(f"location={quote(location)}")
        if date_from:
            params.append(f"datetime_utc.gte={date_from}")
        if date_to:
            params.append(f"datetime_utc.lte={date_to}")
        
        if params:
            url += "?" + "&".join(params)
        
        return url
    
    def _parse_events_page(self, html: str) -> List[Dict]:
        """
        Parse events from HTML page
        
        Args:
            html: HTML content
            
        Returns:
            List of parsed event dictionaries
        """
        events = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Note: This is a simplified parser. SeatGeek uses heavy JavaScript
        # and dynamic content loading, so a headless browser (Selenium/Playwright)
        # would be more reliable for production use.
        
        # Example selectors (these may need to be updated based on actual HTML structure)
        event_cards = soup.find_all('div', class_=['event-card', 'EventCard'])
        
        for card in event_cards:
            try:
                event = self._parse_event_card(card)
                if event:
                    events.append(event)
            except Exception as e:
                print(f"Error parsing event card: {e}")
                continue
        
        return events
    
    def _parse_event_card(self, card) -> Optional[Dict]:
        """
        Parse individual event card
        
        Args:
            card: BeautifulSoup element for event card
            
        Returns:
            Event dictionary or None
        """
        try:
            # Extract event details (selectors are examples and may need adjustment)
            title_elem = card.find(['h2', 'h3', 'a'], class_=['event-title', 'title'])
            title = title_elem.text.strip() if title_elem else None
            
            venue_elem = card.find(['span', 'div'], class_=['venue', 'location'])
            venue = venue_elem.text.strip() if venue_elem else None
            
            date_elem = card.find(['time', 'span'], class_=['date', 'datetime'])
            date = date_elem.get('datetime', date_elem.text.strip()) if date_elem else None
            
            price_elem = card.find(['span', 'div'], class_=['price', 'ticket-price'])
            price = price_elem.text.strip() if price_elem else None
            
            link_elem = card.find('a', href=True)
            url = urljoin(self.BASE_URL, link_elem['href']) if link_elem else None
            
            event = {
                'title': title,
                'venue': venue,
                'date': date,
                'price': price,
                'url': url,
                'scraped_at': datetime.now().isoformat()
            }
            
            return event if title else None
            
        except Exception as e:
            print(f"Error parsing event card: {e}")
            return None
    
    def save_results(self, events: Optional[List[Dict]] = None, 
                    output_path: str = "results/seatgeek_events.json"):
        """
        Save scraped results to JSON file
        
        Args:
            events: List of events to save (uses self.results if None)
            output_path: Output file path
        """
        events = events or self.results
        
        output_data = {
            'scrape_date': datetime.now().isoformat(),
            'total_events': len(events),
            'source': 'SeatGeek',
            'scraped_by': 'Roundproxies.com Scraper',
            'events': events
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"Results saved to {output_path}")
    
    def get_event_details(self, event_url: str) -> Optional[Dict]:
        """
        Get detailed information for a specific event
        
        Args:
            event_url: URL of the event page
            
        Returns:
            Detailed event dictionary
        """
        response = self._make_request(event_url)
        
        if not response:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Parse detailed event information
        # This would need to be implemented based on SeatGeek's actual page structure
        
        details = {
            'url': event_url,
            'scraped_at': datetime.now().isoformat()
        }
        
        return details


def main():
    """Example usage"""
    scraper = SeatGeekScraper(config={
        'proxy_enabled': False,  # Set to True and add proxies for production
        'delay_min': 3,
        'delay_max': 5
    })
    
    # Scrape concerts in New York
    events = scraper.scrape_events(
        category='concerts',
        location='New York',
        limit=20
    )
    
    # Save results
    scraper.save_results(events, 'results/seatgeek_concerts_ny.json')


if __name__ == '__main__':
    main()
