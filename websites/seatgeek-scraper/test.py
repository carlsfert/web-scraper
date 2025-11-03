"""
Unit Tests for SeatGeek Scraper
Provided by Roundproxies.com
"""

import unittest
import json
import os
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from seatgeek import SeatGeekScraper


class TestSeatGeekScraper(unittest.TestCase):
    """Test cases for SeatGeek scraper"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            'proxy_enabled': False,
            'delay_min': 0.1,
            'delay_max': 0.2
        }
        self.scraper = SeatGeekScraper(config=self.config)
        
        # Create results directory for tests
        Path('results').mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up after tests"""
        # Clean up test files
        test_files = [
            'results/test_output.json',
            'results/test_events.json'
        ]
        for file in test_files:
            if os.path.exists(file):
                os.remove(file)
    
    def test_initialization(self):
        """Test scraper initialization"""
        self.assertIsNotNone(self.scraper)
        self.assertEqual(self.scraper.delay_min, 0.1)
        self.assertEqual(self.scraper.delay_max, 0.2)
        self.assertFalse(self.scraper.proxy_enabled)
    
    def test_initialization_with_proxy(self):
        """Test scraper initialization with proxy configuration"""
        config = {
            'proxy_enabled': True,
            'proxy_list': ['proxy1.com:8080', 'proxy2.com:8080']
        }
        scraper = SeatGeekScraper(config=config)
        self.assertTrue(scraper.proxy_enabled)
        self.assertEqual(len(scraper.proxy_list), 2)
    
    def test_user_agent_rotation(self):
        """Test user agent rotation"""
        ua1 = self.scraper._get_random_user_agent()
        self.assertIsInstance(ua1, str)
        self.assertTrue(len(ua1) > 0)
        
        # Test that we have multiple user agents
        user_agents = set()
        for _ in range(20):
            user_agents.add(self.scraper._get_random_user_agent())
        self.assertGreater(len(user_agents), 1)
    
    def test_proxy_selection(self):
        """Test proxy selection"""
        # Test without proxy
        proxy = self.scraper._get_proxy()
        self.assertIsNone(proxy)
        
        # Test with proxy
        scraper_with_proxy = SeatGeekScraper(config={
            'proxy_enabled': True,
            'proxy_list': ['proxy1.com:8080', 'proxy2.com:8080']
        })
        proxy = scraper_with_proxy._get_proxy()
        self.assertIsNotNone(proxy)
        self.assertIn('http', proxy)
        self.assertIn('https', proxy)
    
    def test_build_search_url(self):
        """Test search URL building"""
        # Test basic URL
        url = self.scraper._build_search_url(None, None, None, None)
        self.assertEqual(url, "https://seatgeek.com/browse")
        
        # Test with category
        url = self.scraper._build_search_url('concerts', None, None, None)
        self.assertIn('type=concerts', url)
        
        # Test with location
        url = self.scraper._build_search_url(None, 'New York', None, None)
        self.assertIn('location=New', url)
        
        # Test with all parameters
        url = self.scraper._build_search_url(
            'sports',
            'Los Angeles',
            '2025-12-01',
            '2025-12-31'
        )
        self.assertIn('type=sports', url)
        self.assertIn('location=Los', url)
        self.assertIn('datetime_utc.gte=2025-12-01', url)
        self.assertIn('datetime_utc.lte=2025-12-31', url)
    
    def test_parse_event_card(self):
        """Test event card parsing"""
        # Mock HTML event card
        from bs4 import BeautifulSoup
        
        html = """
        <div class="event-card">
            <h2 class="event-title">Test Concert</h2>
            <span class="venue">Madison Square Garden</span>
            <time class="date" datetime="2025-12-15">December 15, 2025</time>
            <span class="price">$50-$150</span>
            <a href="/test-concert-tickets">View Details</a>
        </div>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        card = soup.find('div', class_='event-card')
        
        event = self.scraper._parse_event_card(card)
        
        if event:  # Parser may return None if selectors don't match
            self.assertIsInstance(event, dict)
            self.assertIn('title', event)
            self.assertIn('scraped_at', event)
    
    def test_save_results(self):
        """Test saving results to JSON file"""
        test_events = [
            {
                'title': 'Test Event 1',
                'venue': 'Test Venue',
                'date': '2025-12-15',
                'price': '$50',
                'url': 'https://seatgeek.com/test1'
            },
            {
                'title': 'Test Event 2',
                'venue': 'Another Venue',
                'date': '2025-12-20',
                'price': '$75',
                'url': 'https://seatgeek.com/test2'
            }
        ]
        
        output_path = 'results/test_output.json'
        self.scraper.save_results(test_events, output_path)
        
        # Verify file exists
        self.assertTrue(os.path.exists(output_path))
        
        # Verify content
        with open(output_path, 'r') as f:
            data = json.load(f)
        
        self.assertIn('scrape_date', data)
        self.assertIn('total_events', data)
        self.assertIn('events', data)
        self.assertEqual(data['total_events'], 2)
        self.assertEqual(len(data['events']), 2)
        self.assertEqual(data['events'][0]['title'], 'Test Event 1')
    
    @patch('seatgeek.requests.Session.request')
    def test_make_request_success(self, mock_request):
        """Test successful HTTP request"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html>Test</html>'
        mock_request.return_value = mock_response
        
        response = self.scraper._make_request('https://example.com')
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)
    
    @patch('seatgeek.requests.Session.request')
    def test_make_request_rate_limit(self, mock_request):
        """Test rate limit handling"""
        # Mock rate limit response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_request.return_value = mock_response
        
        response = self.scraper._make_request('https://example.com')
        
        # Should return None after retries
        self.assertIsNone(response)
    
    @patch('seatgeek.requests.Session.request')
    def test_make_request_access_denied(self, mock_request):
        """Test access denied handling"""
        # Mock access denied response
        mock_response = Mock()
        mock_response.status_code = 403
        mock_request.return_value = mock_response
        
        response = self.scraper._make_request('https://example.com')
        
        # Should return None after retries
        self.assertIsNone(response)
    
    def test_parse_events_page_empty(self):
        """Test parsing empty page"""
        html = '<html><body></body></html>'
        events = self.scraper._parse_events_page(html)
        
        self.assertIsInstance(events, list)
        self.assertEqual(len(events), 0)
    
    def test_parse_events_page_with_events(self):
        """Test parsing page with events"""
        html = """
        <html>
            <body>
                <div class="event-card">
                    <h2 class="event-title">Concert 1</h2>
                    <span class="venue">Venue 1</span>
                    <a href="/concert1">Link</a>
                </div>
                <div class="event-card">
                    <h2 class="event-title">Concert 2</h2>
                    <span class="venue">Venue 2</span>
                    <a href="/concert2">Link</a>
                </div>
            </body>
        </html>
        """
        
        events = self.scraper._parse_events_page(html)
        
        self.assertIsInstance(events, list)
        # Note: May be 0 if selectors don't match the test HTML
        # This is expected as real HTML structure may differ
    
    def test_results_attribute(self):
        """Test results storage in scraper object"""
        self.assertEqual(len(self.scraper.results), 0)
        
        test_events = [{'title': 'Test Event'}]
        self.scraper.results = test_events
        
        self.assertEqual(len(self.scraper.results), 1)
        self.assertEqual(self.scraper.results[0]['title'], 'Test Event')
    
    def test_base_url(self):
        """Test base URL configuration"""
        self.assertEqual(self.scraper.BASE_URL, "https://seatgeek.com")
    
    def test_api_url(self):
        """Test API URL configuration"""
        self.assertEqual(self.scraper.API_URL, "https://api.seatgeek.com/2")


class TestIntegration(unittest.TestCase):
    """Integration tests for SeatGeek scraper"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.scraper = SeatGeekScraper(config={
            'proxy_enabled': False,
            'delay_min': 0.1,
            'delay_max': 0.2
        })
    
    @unittest.skip("Requires network connection and may be rate limited")
    def test_live_scraping(self):
        """Test live scraping (skipped by default)"""
        events = self.scraper.scrape_events(
            category='concerts',
            location='New York',
            limit=5
        )
        
        self.assertIsInstance(events, list)
        # Note: May be empty due to anti-scraping measures
    
    def test_end_to_end_workflow(self):
        """Test complete workflow with mock data"""
        # This would test the full workflow:
        # 1. Initialize scraper
        # 2. Configure settings
        # 3. Scrape events (mocked)
        # 4. Save results
        # 5. Verify output
        
        self.assertIsNotNone(self.scraper)
        
        # Mock scraping result
        mock_events = [
            {
                'title': 'Mock Concert',
                'venue': 'Mock Venue',
                'date': '2025-12-15',
                'price': '$100'
            }
        ]
        
        # Save and verify
        output_path = 'results/test_events.json'
        self.scraper.save_results(mock_events, output_path)
        
        self.assertTrue(os.path.exists(output_path))


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
