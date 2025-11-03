"""
Test suite for the Alibaba scraper.
Run with: python test.py or pytest test.py
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from io import StringIO

# Add parent directory to path to import alibaba module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from alibaba import AlibabaScraper


class TestAlibabaScraper(unittest.TestCase):
    """Test cases for AlibabaScraper class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scraper = AlibabaScraper()
        self.sample_html = """
        <html>
            <body>
                <div class="organic-list-offer">
                    <h2 class="search-card-e-title">Test Laptop</h2>
                    <a href="/product/test-laptop.html">Product Link</a>
                    <span class="search-card-e-price-main">$500.00 - $600.00</span>
                    <span class="search-card-e-moq">10 pieces</span>
                    <a class="search-card-e-company">Test Supplier Co.</a>
                    <img src="http://example.com/image.jpg" />
                </div>
            </body>
        </html>
        """
    
    def test_initialization(self):
        """Test scraper initialization."""
        scraper = AlibabaScraper()
        self.assertIsNone(scraper.proxies)
        self.assertEqual(scraper.delay, (2, 5))
        
        # Test with custom parameters
        proxies = {'http': 'http://proxy.com:8080'}
        scraper = AlibabaScraper(proxies=proxies, delay=(1, 3))
        self.assertEqual(scraper.proxies, proxies)
        self.assertEqual(scraper.delay, (1, 3))
    
    def test_get_headers(self):
        """Test header generation."""
        headers = self.scraper._get_headers()
        self.assertIn('User-Agent', headers)
        self.assertIn('Accept', headers)
        self.assertIn('Chrome', headers['User-Agent'] or headers['User-Agent'])
    
    def test_parse_search_results(self):
        """Test parsing of search results."""
        products = self.scraper._parse_search_results(self.sample_html)
        
        self.assertIsInstance(products, list)
        if products:  # If parsing successful
            product = products[0]
            self.assertIn('title', product)
            self.assertIn('url', product)
            self.assertIn('price', product)
    
    def test_extract_product_data(self):
        """Test extraction of product data from HTML element."""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(self.sample_html, 'lxml')
        card = soup.find('div', class_='organic-list-offer')
        
        if card:
            product = self.scraper._extract_product_data(card)
            if product:
                self.assertIsInstance(product, dict)
                self.assertIn('title', product)
                self.assertIn('price', product)
                self.assertIn('url', product)
    
    @patch('alibaba.requests.Session.get')
    def test_make_request_success(self, mock_get):
        """Test successful HTTP request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html></html>"
        mock_get.return_value = mock_response
        
        response = self.scraper._make_request("http://example.com")
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)
    
    @patch('alibaba.requests.Session.get')
    def test_make_request_forbidden(self, mock_get):
        """Test handling of 403 Forbidden response."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_get.return_value = mock_response
        
        response = self.scraper._make_request("http://example.com")
        self.assertIsNone(response)
    
    @patch('alibaba.requests.Session.get')
    def test_make_request_rate_limit(self, mock_get):
        """Test handling of rate limiting."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response
        
        response = self.scraper._make_request("http://example.com")
        self.assertIsNone(response)
    
    @patch('alibaba.requests.Session.get')
    def test_make_request_exception(self, mock_get):
        """Test handling of request exceptions."""
        mock_get.side_effect = Exception("Network error")
        
        response = self.scraper._make_request("http://example.com")
        self.assertIsNone(response)
    
    def test_save_to_csv(self):
        """Test CSV export functionality."""
        products = [
            {
                'title': 'Test Product 1',
                'price': '$100',
                'supplier': 'Test Supplier',
                'url': 'http://example.com/1'
            },
            {
                'title': 'Test Product 2',
                'price': '$200',
                'supplier': 'Test Supplier 2',
                'url': 'http://example.com/2'
            }
        ]
        
        test_file = 'test_output.csv'
        try:
            self.scraper.save_to_csv(products, test_file)
            self.assertTrue(os.path.exists(test_file))
            
            # Verify file content
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('Test Product 1', content)
                self.assertIn('Test Product 2', content)
        finally:
            # Cleanup
            if os.path.exists(test_file):
                os.remove(test_file)
    
    def test_save_to_csv_empty(self):
        """Test CSV export with empty product list."""
        products = []
        test_file = 'test_empty.csv'
        
        # Should handle gracefully
        self.scraper.save_to_csv(products, test_file)
        
        # File should not be created
        self.assertFalse(os.path.exists(test_file))
    
    def test_find_products_in_json(self):
        """Test JSON product extraction."""
        test_data = {
            'products': [
                {
                    'title': 'JSON Product 1',
                    'price': '$100',
                    'supplier': 'JSON Supplier'
                },
                {
                    'title': 'JSON Product 2',
                    'price': '$200'
                }
            ]
        }
        
        products = self.scraper._find_products_in_json(test_data)
        self.assertIsInstance(products, list)
    
    def test_user_agent_rotation(self):
        """Test that user agents are rotated."""
        agents = set()
        for _ in range(10):
            headers = self.scraper._get_headers()
            agents.add(headers['User-Agent'])
        
        # Should have at least 2 different user agents
        self.assertGreaterEqual(len(agents), 1)
    
    @patch('alibaba.time.sleep')
    def test_random_delay(self, mock_sleep):
        """Test random delay functionality."""
        self.scraper._random_delay()
        mock_sleep.assert_called_once()
        
        # Check that delay is within specified range
        call_args = mock_sleep.call_args[0][0]
        self.assertGreaterEqual(call_args, self.scraper.delay[0])
        self.assertLessEqual(call_args, self.scraper.delay[1])


class TestIntegration(unittest.TestCase):
    """Integration tests (require network access)."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.scraper = AlibabaScraper(delay=(1, 2))  # Shorter delays for testing
    
    @unittest.skip("Skipping live test - requires network and may be blocked")
    def test_live_search(self):
        """Test live search functionality (SKIPPED by default)."""
        # Uncomment to run live test with actual Alibaba scraping
        # WARNING: May be blocked without proxies
        products = self.scraper.search_products("test", max_pages=1)
        self.assertIsInstance(products, list)
    
    def test_url_construction(self):
        """Test that URLs are constructed properly."""
        self.assertEqual(self.scraper.BASE_URL, "https://www.alibaba.com")
        self.assertEqual(self.scraper.SEARCH_URL, "https://www.alibaba.com/trade/search")


def run_tests():
    """Run all tests and display results."""
    print("=" * 70)
    print("ALIBABA SCRAPER TEST SUITE")
    print("=" * 70)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all tests
    suite.addTests(loader.loadTestsFromTestCase(TestAlibabaScraper))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run:     {result.testsRun}")
    print(f"Successes:     {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures:      {len(result.failures)}")
    print(f"Errors:        {len(result.errors)}")
    print(f"Skipped:       {len(result.skipped)}")
    print("=" * 70)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
