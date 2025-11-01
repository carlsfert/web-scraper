"""
eBay Scraper Test Suite
Tests for the eBay scraper functionality.
"""

import unittest
import json
import os
from unittest.mock import Mock, patch, MagicMock
from ebay import EbayScraper


class TestEbayScraper(unittest.TestCase):
    """Test cases for EbayScraper class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scraper = EbayScraper()
        self.test_query = "test laptop"
        
    def tearDown(self):
        """Clean up after tests."""
        # Clean up any test result files
        if os.path.exists('results'):
            for file in os.listdir('results'):
                if file.startswith('ebay_test_'):
                    os.remove(os.path.join('results', file))
    
    def test_initialization(self):
        """Test scraper initialization."""
        self.assertIsNotNone(self.scraper)
        self.assertEqual(self.scraper.delay, 2.0)
        self.assertEqual(self.scraper.timeout, 30)
        self.assertEqual(self.scraper.base_url, "https://www.ebay.com")
    
    def test_initialization_with_proxies(self):
        """Test scraper initialization with proxy configuration."""
        proxy_config = {
            'http': 'http://user:pass@proxy.roundproxies.com:8080',
            'https': 'http://user:pass@proxy.roundproxies.com:8080'
        }
        scraper = EbayScraper(proxies=proxy_config)
        self.assertEqual(scraper.proxies, proxy_config)
    
    def test_build_search_url_basic(self):
        """Test basic search URL construction."""
        url = self.scraper._build_search_url("laptop", 1, None, None, None)
        self.assertIn("laptop", url)
        self.assertIn("ebay.com/sch", url)
    
    def test_build_search_url_with_pagination(self):
        """Test search URL with pagination."""
        url = self.scraper._build_search_url("laptop", 2, None, None, None)
        self.assertIn("_pgn=2", url)
    
    def test_build_search_url_with_condition(self):
        """Test search URL with condition filter."""
        url = self.scraper._build_search_url("laptop", 1, "new", None, None)
        self.assertIn("LH_ItemCondition=1000", url)
        
        url = self.scraper._build_search_url("laptop", 1, "used", None, None)
        self.assertIn("LH_ItemCondition=3000", url)
    
    def test_build_search_url_with_price_filters(self):
        """Test search URL with price filters."""
        url = self.scraper._build_search_url("laptop", 1, None, 100, 500)
        self.assertIn("_udlo=100", url)
        self.assertIn("_udhi=500", url)
    
    def test_extract_product_data_valid(self):
        """Test product data extraction from valid HTML."""
        from bs4 import BeautifulSoup
        
        # Mock HTML structure
        html = """
        <div class="s-item__info">
            <div class="s-item__title">Test Laptop</div>
            <span class="s-item__price">$499.99</span>
            <span class="SECONDARY_INFO">New</span>
            <span class="s-item__shipping">Free shipping</span>
            <span class="s-item__location">United States</span>
            <span class="s-item__seller-info-text">seller123</span>
        </div>
        """
        
        soup = BeautifulSoup(html, 'lxml')
        item = soup.find('div', {'class': 's-item__info'})
        
        product = self.scraper._extract_product_data(item)
        
        self.assertIsNotNone(product)
        self.assertEqual(product['title'], 'Test Laptop')
        self.assertEqual(product['price'], '$499.99')
        self.assertEqual(product['condition'], 'New')
        self.assertEqual(product['shipping'], 'Free shipping')
    
    def test_extract_product_data_invalid(self):
        """Test product data extraction from invalid HTML."""
        from bs4 import BeautifulSoup
        
        # Mock HTML with shop header
        html = """
        <div class="s-item__info">
            <div class="s-item__title">Shop on eBay</div>
        </div>
        """
        
        soup = BeautifulSoup(html, 'lxml')
        item = soup.find('div', {'class': 's-item__info'})
        
        product = self.scraper._extract_product_data(item)
        
        # Should return None for header items
        self.assertIsNone(product)
    
    def test_safe_extract(self):
        """Test safe HTML element extraction."""
        from bs4 import BeautifulSoup
        
        html = '<div><span class="test">Hello World</span></div>'
        soup = BeautifulSoup(html, 'lxml')
        
        result = self.scraper._safe_extract(soup, 'span', {'class': 'test'})
        self.assertEqual(result, 'Hello World')
        
        # Test missing element
        result = self.scraper._safe_extract(soup, 'span', {'class': 'missing'})
        self.assertIsNone(result)
    
    @patch('ebay.requests.get')
    def test_make_request_success(self, mock_get):
        """Test successful HTTP request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html>test</html>'
        mock_get.return_value = mock_response
        
        response = self.scraper._make_request("https://www.ebay.com/test")
        
        self.assertEqual(response.status_code, 200)
        mock_get.assert_called_once()
    
    @patch('ebay.requests.get')
    def test_make_request_with_proxy(self, mock_get):
        """Test HTTP request with proxy."""
        proxy_config = {
            'http': 'http://proxy.roundproxies.com:8080',
            'https': 'http://proxy.roundproxies.com:8080'
        }
        scraper = EbayScraper(proxies=proxy_config)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        scraper._make_request("https://www.ebay.com/test")
        
        # Verify proxy was used
        call_args = mock_get.call_args
        self.assertEqual(call_args[1]['proxies'], proxy_config)
    
    @patch('ebay.requests.get')
    def test_make_request_timeout(self, mock_get):
        """Test HTTP request timeout handling."""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        with self.assertRaises(requests.exceptions.RequestException):
            self.scraper._make_request("https://www.ebay.com/test")
    
    def test_results_directory_creation(self):
        """Test that results directory is created."""
        self.assertTrue(os.path.exists('results'))
        self.assertTrue(os.path.isdir('results'))
    
    @patch('ebay.EbayScraper._make_request')
    @patch('ebay.EbayScraper._parse_search_results')
    def test_search_basic(self, mock_parse, mock_request):
        """Test basic search functionality."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html>mock</html>'
        mock_request.return_value = mock_response
        
        mock_parse.return_value = [
            {'title': 'Product 1', 'price': '$100'},
            {'title': 'Product 2', 'price': '$200'}
        ]
        
        results = self.scraper.search("test", max_pages=1)
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], 'Product 1')
        mock_request.assert_called_once()
        mock_parse.assert_called_once()
    
    @patch('ebay.EbayScraper._make_request')
    def test_search_multiple_pages(self, mock_request):
        """Test search with multiple pages."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><div class="s-item__info"></div></html>'
        mock_request.return_value = mock_response
        
        with patch('time.sleep'):  # Skip actual delays in tests
            self.scraper.search("test", max_pages=3)
        
        # Should make 3 requests for 3 pages
        self.assertEqual(mock_request.call_count, 3)
    
    @patch('ebay.EbayScraper._make_request')
    def test_search_error_handling(self, mock_request):
        """Test search error handling."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_request.return_value = mock_response
        
        results = self.scraper.search("test", max_pages=1)
        
        # Should return empty list on error
        self.assertEqual(len(results), 0)
    
    def test_save_results(self):
        """Test saving results to JSON file."""
        test_results = [
            {'title': 'Test Product', 'price': '$100'},
            {'title': 'Another Product', 'price': '$200'}
        ]
        
        self.scraper._save_results(test_results, "test")
        
        # Check if file was created
        files = [f for f in os.listdir('results') if f.startswith('ebay_test_')]
        self.assertTrue(len(files) > 0)
        
        # Verify file content
        with open(f'results/{files[0]}', 'r') as f:
            saved_data = json.load(f)
        
        self.assertEqual(len(saved_data), 2)
        self.assertEqual(saved_data[0]['title'], 'Test Product')


class TestIntegration(unittest.TestCase):
    """Integration tests (require network access)."""
    
    @unittest.skip("Skipping integration test - requires network")
    def test_real_search(self):
        """Test actual eBay search (requires network)."""
        scraper = EbayScraper(delay=3.0)
        results = scraper.search("laptop", max_pages=1)
        
        self.assertIsInstance(results, list)
        if len(results) > 0:
            self.assertIn('title', results[0])
            self.assertIn('price', results[0])


class TestProxyConfiguration(unittest.TestCase):
    """Test proxy configuration scenarios."""
    
    def test_proxy_format_validation(self):
        """Test different proxy format configurations."""
        # Valid proxy configurations
        valid_configs = [
            {
                'http': 'http://user:pass@proxy.roundproxies.com:8080',
                'https': 'http://user:pass@proxy.roundproxies.com:8080'
            },
            {
                'http': 'http://10.0.0.1:8080',
                'https': 'http://10.0.0.1:8080'
            }
        ]
        
        for config in valid_configs:
            scraper = EbayScraper(proxies=config)
            self.assertEqual(scraper.proxies, config)


def run_tests():
    """Run all tests with verbose output."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestEbayScraper))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestProxyConfiguration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
