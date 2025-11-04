"""
Test suite for Booking.com scraper.

Run tests with: python test.py
Or with pytest: pytest test.py -v
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from booking import BookingScraper


class TestBookingScraper(unittest.TestCase):
    """Test cases for BookingScraper class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scraper = BookingScraper(delay=0.1)  # Reduced delay for testing
        self.test_destination = "Paris"
        self.test_checkin = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        self.test_checkout = (datetime.now() + timedelta(days=35)).strftime('%Y-%m-%d')
    
    def test_initialization(self):
        """Test scraper initialization."""
        scraper = BookingScraper()
        self.assertIsNotNone(scraper.session)
        self.assertEqual(scraper.delay, 2.0)
        self.assertEqual(scraper.timeout, 30)
        self.assertIsNone(scraper.proxies)
    
    def test_initialization_with_proxies(self):
        """Test scraper initialization with proxies."""
        proxy_config = {
            "http": "http://proxy.example.com:8080",
            "https": "https://proxy.example.com:8080"
        }
        scraper = BookingScraper(proxies=proxy_config)
        self.assertEqual(scraper.proxies, proxy_config)
        self.assertEqual(scraper.session.proxies, proxy_config)
    
    def test_build_search_url(self):
        """Test URL building with parameters."""
        url = self.scraper._build_search_url(
            destination="New York",
            checkin="2025-12-01",
            checkout="2025-12-05",
            adults=2,
            rooms=1,
            offset=0
        )
        
        self.assertIn("booking.com/searchresults.html", url)
        self.assertIn("ss=New+York", url)
        self.assertIn("checkin=2025-12-01", url)
        self.assertIn("checkout=2025-12-05", url)
        self.assertIn("group_adults=2", url)
        self.assertIn("no_rooms=1", url)
    
    def test_build_search_url_with_offset(self):
        """Test URL building with pagination offset."""
        url = self.scraper._build_search_url(
            destination="London",
            checkin="2025-12-01",
            checkout="2025-12-05",
            offset=25
        )
        
        self.assertIn("offset=25", url)
    
    def test_session_headers(self):
        """Test that session has proper browser-like headers."""
        headers = self.scraper.session.headers
        
        self.assertIn('User-Agent', headers)
        self.assertIn('Accept', headers)
        self.assertIn('Accept-Language', headers)
        self.assertTrue(headers['User-Agent'].startswith('Mozilla'))
    
    def test_parse_hotel_card_valid(self):
        """Test parsing a valid hotel card."""
        from bs4 import BeautifulSoup
        
        # Mock HTML for a hotel card
        mock_html = """
        <div data-testid="property-card">
            <a data-testid="title-link" href="/hotel/test.html">
                <div data-testid="title">Test Hotel</div>
            </a>
            <div data-testid="address">123 Test St, Paris</div>
            <div data-testid="distance">2 km from center</div>
            <div data-testid="price-and-discounted-price">$150</div>
            <div data-testid="review-score">
                <div>8.5</div>
                <div>1,250 reviews</div>
            </div>
            <div data-testid="facility">WiFi</div>
            <div data-testid="facility">Pool</div>
        </div>
        """
        
        soup = BeautifulSoup(mock_html, 'html.parser')
        card = soup.find('div', {'data-testid': 'property-card'})
        
        result = self.scraper._parse_hotel_card(card)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'Test Hotel')
        self.assertEqual(result['address'], '123 Test St, Paris')
        self.assertEqual(result['price'], '$150')
        self.assertEqual(result['rating'], '8.5')
        self.assertIn('WiFi', result['amenities'])
        self.assertIn('Pool', result['amenities'])
    
    def test_parse_hotel_card_invalid(self):
        """Test parsing an invalid hotel card."""
        from bs4 import BeautifulSoup
        
        mock_html = "<div>Invalid card</div>"
        soup = BeautifulSoup(mock_html, 'html.parser')
        card = soup.find('div')
        
        result = self.scraper._parse_hotel_card(card)
        self.assertIsNone(result)
    
    @patch('booking.BookingScraper._random_delay')
    @patch('booking.requests.Session.get')
    def test_search_hotels_success(self, mock_get, mock_delay):
        """Test successful hotel search."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <div data-testid="property-card">
                <a data-testid="title-link" href="/hotel/test.html">
                    <div data-testid="title">Test Hotel</div>
                </a>
                <div data-testid="price-and-discounted-price">$150</div>
            </div>
        </html>
        """
        mock_get.return_value = mock_response
        
        results = self.scraper.search_hotels(
            destination="Paris",
            checkin=self.test_checkin,
            checkout=self.test_checkout,
            max_results=1
        )
        
        self.assertIn('search_params', results)
        self.assertIn('hotels', results)
        self.assertEqual(results['search_params']['destination'], 'Paris')
        self.assertGreaterEqual(len(results['hotels']), 0)
    
    @patch('booking.requests.Session.get')
    def test_search_hotels_blocked(self, mock_get):
        """Test handling of blocked requests (403 error)."""
        mock_get.side_effect = Exception("403 Forbidden")
        
        results = self.scraper.search_hotels(
            destination="Paris",
            checkin=self.test_checkin,
            checkout=self.test_checkout,
            max_results=1
        )
        
        self.assertEqual(len(results['hotels']), 0)
    
    def test_results_directory_creation(self):
        """Test that results directory is created."""
        import shutil
        
        # Clean up first
        if self.scraper.results_dir.exists():
            shutil.rmtree(self.scraper.results_dir)
        
        # Create new scraper (should create directory)
        new_scraper = BookingScraper()
        self.assertTrue(new_scraper.results_dir.exists())
    
    def test_save_results(self):
        """Test saving results to file."""
        import json
        
        test_results = {
            'search_params': {
                'destination': 'Test City',
                'checkin': '2025-12-01',
                'checkout': '2025-12-05'
            },
            'hotels': [
                {'name': 'Test Hotel', 'price': '$100'}
            ],
            'total_found': 1
        }
        
        self.scraper._save_results(test_results, 'Test_City')
        
        # Check that file was created
        files = list(self.scraper.results_dir.glob('booking_Test_City_*.json'))
        self.assertGreater(len(files), 0)
        
        # Verify content
        with open(files[0], 'r') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data['search_params']['destination'], 'Test City')
        self.assertEqual(len(saved_data['hotels']), 1)


class TestProxyIntegration(unittest.TestCase):
    """Test proxy integration (requires actual proxy to run)."""
    
    @unittest.skip("Requires actual proxy credentials")
    def test_with_real_proxy(self):
        """Test scraper with real proxy from Roundproxies.com."""
        proxy_config = {
            "http": "http://username:password@proxy.roundproxies.com:8080",
            "https": "https://username:password@proxy.roundproxies.com:8080"
        }
        
        scraper = BookingScraper(proxies=proxy_config)
        results = scraper.search_hotels(
            destination="Paris",
            checkin="2025-12-01",
            checkout="2025-12-05",
            max_results=5
        )
        
        self.assertGreater(len(results['hotels']), 0)


def run_tests():
    """Run all tests."""
    print("=" * 60)
    print("Booking.com Scraper - Test Suite")
    print("=" * 60)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestBookingScraper))
    suite.addTests(loader.loadTestsFromTestCase(TestProxyIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print()
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
